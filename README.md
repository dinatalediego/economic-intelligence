# Medallio Economic Intelligence

Personal macro intelligence layer for the Medallio founder.

This repository builds the macro of Medallio Company OS: a personal system that reads the economic environment, connects it to Medallio's own operating evidence, and helps the founder make traceable decisions with measured outcomes.

It is designed to run locally first and to synchronize selected, non-sensitive data with a personal Supabase project. Power BI is a visualization and analysis client; it is not the source of business logic.

## Strategic fit

Medallio Company OS is the operating system of the company. This repository is a founder-facing intelligence product that supports its strategy:

> Turn governed evidence into traceable decisions and verified economic outcomes.

The operating loop is:

External evidence + Medallio operating evidence → signal → prediction/scenario → founder decision → action → outcome → economic value

The first user is Diego. A later sanitized view may be shared with Medallio collaborators or design partners after a deliberate review. This repo is not the Cygnus production data environment and must never contain customer raw data, credentials, or production exports.

## Current implementation

The first executable slice imports EIP's existing Peru macro exports into a local PostgreSQL schema:

- source registry: EIP config/series_registry.csv;
- monthly facts: EIP data/exports/macro_monthly_long.csv;
- latest comparisons and freshness: EIP data/exports/validation_summary.csv and freshness_gate.json;
- outputs: economic_intelligence.macro_series_catalog, macro_monthly, macro_snapshot, v_macro_monthly, and v_macro_latest.

The loader refuses to update certified data unless EIP's freshness gate says PUBLISH. It validates registry alignment, units, periods, numeric values, duplicate observations, and snapshot coverage before opening a database transaction. The import and migration are transactional.

## Local import

Requirements: Python 3.10+, a reachable personal/local PostgreSQL database, and the EIP refresh outputs.

Install the dependency:

```powershell
python -m pip install -r requirements.txt
```

Set ECONOMIC_INTELLIGENCE_DATABASE_URL in the current process using your local PostgreSQL connection string. Do not commit the value or paste it into the command history. Then run:

```powershell
.\scripts\import_eip_exports.bat "C:\Projects\project-starter-kit\pilots\economic-intelligence-peru"
```

Or call Python directly:

```powershell
python .\scripts\import_eip_exports.py --eip-root "C:\Projects\project-starter-kit\pilots\economic-intelligence-peru"
```

The loader prints counts and a batch ID, never the database URL. It does not connect to Cygnus or Supabase. Use a personal/local database, not a client production database.

## Architecture decisions

- Personal-first, shareable by design: keep founder-only data separate from explicitly approved shareable data.
- Local-first, cloud-capable: local PostgreSQL is the development and recovery copy; hosted Supabase is the authenticated online sync and app backend.
- Evidence before recommendation: every material signal carries provenance, freshness, quality, and confidence.
- Decision value over dashboard volume: connect insights to recorded decisions, actions, outcomes, and economic value.
- Core before verticals: keep Peru macro and Medallio-company intelligence reusable; treat real estate/Cygnus as an optional reference adapter.

See [Architecture](docs/ARCHITECTURE.md), [Product charter](docs/PRODUCT_CHARTER.md), [Data governance](docs/DATA_GOVERNANCE.md), and [Roadmap](docs/ROADMAP.md).

## Current limits

Architecture and local macro import are in review. The loader has not been run against your computer or database. Supabase sync, source ingestion, Medallio company metrics, and Power BI report pages are not implemented yet.
