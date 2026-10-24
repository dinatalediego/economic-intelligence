CREATE SCHEMA IF NOT EXISTS economic_intelligence;

CREATE TABLE IF NOT EXISTS economic_intelligence.ingest_batch (
    batch_id UUID PRIMARY KEY,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_project TEXT NOT NULL,
    source_fetched_at TIMESTAMPTZ,
    freshness_decision TEXT NOT NULL CHECK (freshness_decision IN ('PUBLISH')),
    series_count INTEGER NOT NULL CHECK (series_count >= 0),
    observation_count INTEGER NOT NULL CHECK (observation_count >= 0),
    monthly_sha256 TEXT NOT NULL,
    snapshot_sha256 TEXT NOT NULL,
    registry_sha256 TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS economic_intelligence.macro_series_catalog (
    provider_code TEXT PRIMARY KEY,
    series_slug TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL,
    frequency TEXT NOT NULL,
    unit TEXT NOT NULL,
    display_unit TEXT NOT NULL,
    nature TEXT NOT NULL,
    primary_signal TEXT NOT NULL,
    title TEXT NOT NULL,
    authoring_source TEXT NOT NULL,
    source_page_url TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS economic_intelligence.macro_monthly (
    provider_code TEXT NOT NULL REFERENCES economic_intelligence.macro_series_catalog(provider_code),
    period_start DATE NOT NULL CHECK (EXTRACT(DAY FROM period_start) = 1),
    value DOUBLE PRECISION,
    source_status TEXT NOT NULL CHECK (source_status IN ('ok', 'missing')),
    batch_id UUID NOT NULL REFERENCES economic_intelligence.ingest_batch(batch_id),
    PRIMARY KEY (provider_code, period_start),
    CHECK ((source_status = 'ok' AND value IS NOT NULL) OR (source_status = 'missing' AND value IS NULL))
);

CREATE INDEX IF NOT EXISTS ix_ei_macro_monthly_period
    ON economic_intelligence.macro_monthly (period_start);

CREATE TABLE IF NOT EXISTS economic_intelligence.macro_snapshot (
    batch_id UUID NOT NULL REFERENCES economic_intelligence.ingest_batch(batch_id),
    provider_code TEXT NOT NULL REFERENCES economic_intelligence.macro_series_catalog(provider_code),
    observation_count INTEGER NOT NULL,
    latest_period DATE,
    latest_value DOUBLE PRECISION,
    previous_month_period DATE,
    previous_month_value DOUBLE PRECISION,
    previous_year_period DATE,
    previous_year_value DOUBLE PRECISION,
    mom_delta DOUBLE PRECISION,
    mom_pct DOUBLE PRECISION,
    mom_delta_pp DOUBLE PRECISION,
    yoy_delta DOUBLE PRECISION,
    yoy_pct DOUBLE PRECISION,
    yoy_delta_pp DOUBLE PRECISION,
    staleness_months INTEGER,
    PRIMARY KEY (batch_id, provider_code)
);

CREATE OR REPLACE VIEW economic_intelligence.v_macro_monthly AS
SELECT
    m.period_start,
    c.provider_code,
    c.series_slug,
    c.domain,
    m.value,
    m.source_status,
    c.unit,
    c.display_unit,
    c.nature,
    c.authoring_source AS source,
    c.source_page_url,
    m.batch_id
FROM economic_intelligence.macro_monthly AS m
JOIN economic_intelligence.macro_series_catalog AS c USING (provider_code);

CREATE OR REPLACE VIEW economic_intelligence.v_macro_latest AS
SELECT DISTINCT ON (s.provider_code)
    c.provider_code,
    c.series_slug,
    c.domain,
    c.title,
    c.frequency,
    c.unit,
    c.display_unit,
    c.nature,
    c.primary_signal,
    c.authoring_source AS source,
    c.source_page_url,
    s.observation_count,
    s.latest_period,
    s.latest_value,
    s.previous_month_period,
    s.previous_month_value,
    s.previous_year_period,
    s.previous_year_value,
    s.mom_delta,
    s.mom_pct,
    s.mom_delta_pp,
    s.yoy_delta,
    s.yoy_pct,
    s.yoy_delta_pp,
    s.staleness_months,
    b.imported_at,
    b.source_fetched_at,
    b.batch_id
FROM economic_intelligence.macro_snapshot AS s
JOIN economic_intelligence.macro_series_catalog AS c USING (provider_code)
JOIN economic_intelligence.ingest_batch AS b USING (batch_id)
WHERE b.freshness_decision = 'PUBLISH'
ORDER BY s.provider_code, b.imported_at DESC;
