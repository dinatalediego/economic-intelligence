from __future__ import annotations

import argparse
import csv
from datetime import date, datetime
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "db" / "migrations" / "001_macro_foundation.sql"
SOURCE_PROJECT = "project-starter-kit/pilots/economic-intelligence-peru"
MONTHLY_COLUMNS = {"period_start", "provider_code", "series", "domain", "value", "status", "unit", "source"}
SNAPSHOT_COLUMNS = {
    "provider_code", "series", "domain", "title", "frequency", "unit",
    "display_unit", "nature", "primary_signal", "source", "observation_count",
    "latest_period", "latest_value", "previous_month_period", "previous_month_value",
    "previous_year_period", "previous_year_value", "mom_delta", "mom_pct",
    "mom_delta_pp", "yoy_delta", "yoy_pct", "yoy_delta_pp", "staleness_months",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Required EIP export not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")
        return list(reader)


def as_float(raw: str | None, field: str) -> float | None:
    if raw is None or raw.strip() == "":
        return None
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"{field} must be a finite number")
    return value


def as_date(raw: str | None, field: str) -> date | None:
    if raw is None or raw.strip() == "":
        return None
    parsed = date.fromisoformat(raw.strip())
    if field.endswith("period") and parsed.day != 1:
        raise ValueError(f"{field} must be the first day of a monthly period: {raw}")
    return parsed


def as_int(raw: str | None, field: str) -> int | None:
    if raw is None or raw.strip() == "":
        return None
    value = int(raw)
    if value < 0:
        raise ValueError(f"{field} cannot be negative")
    return value


def load_inputs(eip_root: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], dict]:
    config = eip_root / "config" / "series_registry.csv"
    exports = eip_root / "data" / "exports"
    registry = read_csv(
        config,
        {"provider_code", "canonical_slug", "domain", "expected_frequency", "unit",
         "authoring_source", "source_page_url"},
    )
    monthly = read_csv(exports / "macro_monthly_long.csv", MONTHLY_COLUMNS)
    snapshots = read_csv(exports / "validation_summary.csv", SNAPSHOT_COLUMNS)

    gate_path = exports / "freshness_gate.json"
    if not gate_path.is_file():
        raise FileNotFoundError(f"Freshness gate not found: {gate_path}. Run EIP refresh first.")
    gate_doc = json.loads(gate_path.read_text(encoding="utf-8"))
    gate = gate_doc.get("freshness_gate", gate_doc)
    if gate.get("decision") != "PUBLISH":
        raise ValueError(
            "EIP freshness gate is not PUBLISH; refusing to update certified local data. "
            f"Decision={gate.get('decision')!r}, status={gate.get('status')!r}"
        )

    summary_path = exports / "run_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
    return registry, monthly, snapshots, {"gate": gate, "run_summary": summary, "paths": {
        "registry": config,
        "monthly": exports / "macro_monthly_long.csv",
        "snapshots": exports / "validation_summary.csv",
    }}


def validate_inputs(registry, monthly, snapshots) -> None:
    by_code = {row["provider_code"].strip(): row for row in registry}
    if not by_code or len(by_code) != len(registry):
        raise ValueError("Registry is empty or contains duplicate provider_code values.")
    slugs = [row["canonical_slug"].strip() for row in registry]
    if len(slugs) != len(set(slugs)):
        raise ValueError("Registry contains duplicate canonical_slug values.")

    seen: set[tuple[str, str]] = set()
    monthly_codes: set[str] = set()
    for row in monthly:
        code = row["provider_code"].strip()
        spec = by_code.get(code)
        if spec is None:
            raise ValueError(f"Monthly export contains unregistered provider_code {code!r}.")
        if row["series"].strip() != spec["canonical_slug"].strip():
            raise ValueError(f"Series slug mismatch for provider_code {code}.")
        if row["domain"].strip() != spec["domain"].strip() or row["unit"].strip() != spec["unit"].strip():
            raise ValueError(f"Domain or unit mismatch for provider_code {code}.")
        period = as_date(row["period_start"], "period_start")
        key = (code, period.isoformat())
        if key in seen:
            raise ValueError(f"Duplicate monthly observation: {key}")
        seen.add(key)
        monthly_codes.add(code)
        status = row["status"].strip()
        value = as_float(row["value"], "value")
        if status not in {"ok", "missing"}:
            raise ValueError(f"Unsupported observation status {status!r}.")
        if (status == "ok" and value is None) or (status == "missing" and value is not None):
            raise ValueError(f"Value/status mismatch for {key}.")

    if monthly_codes != set(by_code):
        raise ValueError(
            "Monthly export does not cover every registered series. "
            f"Missing={sorted(set(by_code) - monthly_codes)}; extra={sorted(monthly_codes - set(by_code))}"
        )

    snapshot_by_code = {row["provider_code"].strip(): row for row in snapshots}
    if len(snapshot_by_code) != len(snapshots) or set(snapshot_by_code) != set(by_code):
        raise ValueError("Snapshot export must contain exactly one row for every registered series.")
    for code, row in snapshot_by_code.items():
        spec = by_code[code]
        if row["series"].strip() != spec["canonical_slug"].strip():
            raise ValueError(f"Snapshot slug mismatch for provider_code {code}.")
        if row["domain"].strip() != spec["domain"].strip() or row["unit"].strip() != spec["unit"].strip():
            raise ValueError(f"Snapshot domain/unit mismatch for provider_code {code}.")
        as_int(row["observation_count"], "observation_count")
        as_date(row["latest_period"], "latest_period")
        for field in (
            "latest_value", "previous_month_value", "previous_year_value", "mom_delta",
            "mom_pct", "mom_delta_pp", "yoy_delta", "yoy_pct", "yoy_delta_pp",
        ):
            as_float(row[field], field)
        as_date(row["previous_month_period"], "previous_month_period")
        as_date(row["previous_year_period"], "previous_year_period")
        as_int(row["staleness_months"], "staleness_months")


def db_rows(registry, monthly, snapshots, batch_id: str, imported_at: str):
    snapshot_by_code = {row["provider_code"].strip(): row for row in snapshots}
    catalog_rows = []
    for spec in registry:
        code = spec["provider_code"].strip()
        snap = snapshot_by_code[code]
        catalog_rows.append((
            code, spec["canonical_slug"].strip(), spec["domain"].strip(),
            spec["expected_frequency"].strip(), spec["unit"].strip(),
            snap["display_unit"].strip(), snap["nature"].strip(),
            snap["primary_signal"].strip(), snap["title"].strip(),
            spec["authoring_source"].strip(), spec["source_page_url"].strip(),
        ))

    observation_rows = []
    for row in monthly:
        observation_rows.append((
            row["provider_code"].strip(),
            as_date(row["period_start"], "period_start"),
            as_float(row["value"], "value"),
            row["status"].strip(),
            batch_id,
        ))

    snapshot_rows = []
    for row in snapshots:
        snapshot_rows.append((
            batch_id, row["provider_code"].strip(),
            as_int(row["observation_count"], "observation_count"),
            as_date(row["latest_period"], "latest_period"),
            as_float(row["latest_value"], "latest_value"),
            as_date(row["previous_month_period"], "previous_month_period"),
            as_float(row["previous_month_value"], "previous_month_value"),
            as_date(row["previous_year_period"], "previous_year_period"),
            as_float(row["previous_year_value"], "previous_year_value"),
            as_float(row["mom_delta"], "mom_delta"),
            as_float(row["mom_pct"], "mom_pct"),
            as_float(row["mom_delta_pp"], "mom_delta_pp"),
            as_float(row["yoy_delta"], "yoy_delta"),
            as_float(row["yoy_pct"], "yoy_pct"),
            as_float(row["yoy_delta_pp"], "yoy_delta_pp"),
            as_int(row["staleness_months"], "staleness_months"),
        ))
    return catalog_rows, observation_rows, snapshot_rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Load freshness-approved EIP macro exports into local PostgreSQL.")
    parser.add_argument("--eip-root", required=True, type=Path, help="Path to project-starter-kit/pilots/economic-intelligence-peru")
    args = parser.parse_args()

    dsn = os.environ.get("ECONOMIC_INTELLIGENCE_DATABASE_URL")
    if not dsn:
        parser.error("Set ECONOMIC_INTELLIGENCE_DATABASE_URL in the process environment; never commit it.")
    eip_root = args.eip_root.resolve()
    registry, monthly, snapshots, meta = load_inputs(eip_root)
    validate_inputs(registry, monthly, snapshots)

    try:
        import psycopg
    except ImportError:
        print("Missing dependency. Install with: python -m pip install -r requirements.txt", file=sys.stderr)
        return 2

    batch_id = str(uuid4())
    run_summary = meta["run_summary"]
    source_fetched_at = run_summary.get("fetched_at") or None
    imported_at = datetime.now().astimezone().isoformat()
    catalog_rows, observation_rows, snapshot_rows = db_rows(registry, monthly, snapshots, batch_id, imported_at)
    paths = meta["paths"]

    with psycopg.connect(dsn) as conn:
        with conn.transaction():
            conn.execute(MIGRATION.read_text(encoding="utf-8"))
            conn.execute(
                """
                INSERT INTO economic_intelligence.ingest_batch
                    (batch_id, source_project, source_fetched_at, freshness_decision,
                     series_count, observation_count, monthly_sha256, snapshot_sha256, registry_sha256)
                VALUES (%s, %s, %s, 'PUBLISH', %s, %s, %s, %s, %s)
                """,
                (
                    batch_id, SOURCE_PROJECT, source_fetched_at,
                    len(catalog_rows), len(observation_rows),
                    sha256(paths["monthly"]), sha256(paths["snapshots"]), sha256(paths["registry"]),
                ),
            )
            conn.executemany(
                """
                INSERT INTO economic_intelligence.macro_series_catalog
                    (provider_code, series_slug, domain, frequency, unit, display_unit,
                     nature, primary_signal, title, authoring_source, source_page_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (provider_code) DO UPDATE SET
                    series_slug=EXCLUDED.series_slug, domain=EXCLUDED.domain,
                    frequency=EXCLUDED.frequency, unit=EXCLUDED.unit,
                    display_unit=EXCLUDED.display_unit, nature=EXCLUDED.nature,
                    primary_signal=EXCLUDED.primary_signal, title=EXCLUDED.title,
                    authoring_source=EXCLUDED.authoring_source,
                    source_page_url=EXCLUDED.source_page_url, updated_at=now()
                """,
                catalog_rows,
            )
            conn.executemany(
                """
                INSERT INTO economic_intelligence.macro_monthly
                    (provider_code, period_start, value, source_status, batch_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (provider_code, period_start) DO UPDATE SET
                    value=EXCLUDED.value, source_status=EXCLUDED.source_status,
                    batch_id=EXCLUDED.batch_id
                WHERE economic_intelligence.macro_monthly.value IS DISTINCT FROM EXCLUDED.value
                   OR economic_intelligence.macro_monthly.source_status <> EXCLUDED.source_status
                """,
                observation_rows,
            )
            conn.executemany(
                """
                INSERT INTO economic_intelligence.macro_snapshot
                    (batch_id, provider_code, observation_count, latest_period, latest_value,
                     previous_month_period, previous_month_value, previous_year_period,
                     previous_year_value, mom_delta, mom_pct, mom_delta_pp, yoy_delta,
                     yoy_pct, yoy_delta_pp, staleness_months)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                snapshot_rows,
            )

    print(json.dumps({
        "status": "SUCCESS",
        "schema": "economic_intelligence",
        "batch_id": batch_id,
        "series": len(catalog_rows),
        "observations_in_export": len(observation_rows),
        "snapshots": len(snapshot_rows),
        "freshness_gate": "PUBLISH",
        "views": ["v_macro_monthly", "v_macro_latest"],
        "database_url_printed": False,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
