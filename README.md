# Medallio Economic Intelligence

Personal macro intelligence layer for the Medallio founder.

This repository defines and builds the **macro of Medallio Company OS**: a personal system that reads the economic environment, connects it to Medallio's own operating evidence, and helps the founder make traceable decisions with measured outcomes.

It is designed to run locally first and to synchronize selected, non-sensitive data with a personal Supabase project. Power BI is a visualization and analysis client; it is not the source of business logic.

## Strategic fit

Medallio Company OS is the operating system of the company. This repository is a founder-facing intelligence product that supports its strategy:

> Turn governed evidence into traceable decisions and verified economic outcomes.

The operating loop is:

`External evidence + Medallio operating evidence → signal → prediction/scenario → founder decision → action → outcome → economic value`

The first user is Diego. A later sanitized view may be shared with Medallio collaborators or design partners after a deliberate review. This repo is not the Cygnus production data environment and must never contain customer raw data, credentials, or production exports.

## Architecture decisions

- **Personal-first, shareable by design:** keep founder-only data separate from any explicitly approved shareable dataset.
- **Local-first, cloud-capable:** local PostgreSQL is the development and resilient working copy; hosted Supabase is the authenticated online sync and app backend.
- **Evidence before recommendation:** every material signal carries provenance, freshness, quality, and confidence.
- **Decision value over dashboard volume:** connect insights to recorded decisions, actions, outcomes, and economic value.
- **Core before verticals:** keep Peru macro and Medallio-company intelligence reusable; treat real estate/Cygnus as an optional reference adapter.

See [Architecture](docs/ARCHITECTURE.md), [Product charter](docs/PRODUCT_CHARTER.md), [Data governance](docs/DATA_GOVERNANCE.md), and [Roadmap](docs/ROADMAP.md).

## Current state

Architecture v0.1 is being established. No production connection, Supabase project, migrations, or live data sync is implied by these documents.
