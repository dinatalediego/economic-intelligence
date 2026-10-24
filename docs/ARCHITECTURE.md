# Architecture — v0.1

## Design
Build a local-first personal intelligence system with a narrow path to Supabase. Keep ingest, transformations, and semantic definitions reproducible in Git. Store credentials and data outside Git. Publish only curated, non-sensitive products to Power BI or collaborators.

## System flow
Public Peru sources ─┐
                    ├→ Local ingest and validation → Local PostgreSQL → Certified intelligence marts → Power BI
Medallio OS /       ┘                                    │
approved aggregates                                      ├→ Decision → Action → Outcome → Economic Value
                                                         └→ Outbound sync outbox → Personal Supabase → Authenticated app / approved views

Local PostgreSQL is the development and recovery copy. Supabase is the authenticated online backend and selected-data sync target, not an uncontrolled copy of local databases. Power BI may read the local mart or an explicitly exposed Supabase serving view.

## Layers

| Layer | Purpose | Example |
|---|---|---|
| Source registry | Define permitted sources, cadence, units, transformation, terms, and owner | BCRP, INEI, SBS, MEF, SUNAT series |
| Ingest | Capture public evidence and retrieval metadata | Macro observations, fetched-at, source period |
| Staging | Normalize keys, periods, units, revisions, and missingness | Typed observations |
| Analytics | Certified facts and dimensions | Macro monthly, latest snapshot, company monthly |
| Intelligence | Signals, scenarios, implications, and confidence | Signal linked to evidence |
| Decision intelligence | Decisions, actions, outcomes, economic value | Founder decision ledger |
| Sync | Outbox, acknowledgments, retry state, audit | Selected non-sensitive records |
| Presentation | Power BI and future app/API | Read-only consumers |

## Data domains
1. Peru macro: public source series, release calendars, revisions, and source quality.
2. Medallio company: founder operating measures, business assumptions, and approved company-state extracts.
3. Reference vertical: optional real-estate aggregates. Start with synthetic or manually sanitized examples.
4. Founder-private: personal notes, strategy hypotheses, and private decision rationale.
5. Shareable: reviewed, minimized, non-sensitive views explicitly promoted from personal data.

A record in the personal system is not automatically shareable.

## Local PostgreSQL layout
Use a dedicated database such as economic_intelligence with schemas:
- source_registry: source and series catalogs.
- raw_public: immutable public-source captures and retrieval metadata.
- staging: normalized facts and validation results.
- analytics: certified dimensions and fact views.
- intelligence: signals, scenarios, confidence, and evidence references.
- decision_intelligence: decisions, actions, outcomes, and value.
- sync_control: outbox, acknowledgments, retry ledger, sync runs.
- shareable: allowlisted views only, never raw-data landing.

Keep SQL migrations in Git. Use stable keys, UTC event timestamps, explicit business-period dates, and source observation dates separately.

## Supabase layout
Use a separately managed personal project. Keep raw and internal schemas unexposed to the Data API. Expose only a narrow API schema, such as ei_api, and selected tables for the authenticated personal app.

- Every owner-scoped row carries owner_id and has RLS with owner-only policies.
- Shared artifacts use separate tables or views with publication state and minimized fields.
- Do not disable RLS to make BI connect.
- Use a dedicated read-only serving role or scoped views for BI.
- Keep service-role credentials server-side. Never place them in Power BI, browser code, notebook output, or Git.
- Version migrations and apply them consistently to local and hosted environments.
- Back up and test restore before relying on Supabase as the only online copy.

## Data flow and sync
1. Ingest public data locally and save source identity, fetched-at, observation period, revision if available, checksum, and parser version.
2. Validate schema, uniqueness, expected period coverage, units, plausible ranges, and staleness. Quarantine invalid batches and retain the last certified mart.
3. Build analytics and signals deterministically from versioned transformations.
4. Create an outbox row only for records explicitly classified personal-cloud or shareable.
5. Send stable IDs and idempotency keys to Supabase; record acknowledgment and version; retry safely.
6. Require explicit founder promotion to shareable. Promotion creates a minimized copy and never grants access to founder-private records.
7. Reconcile local and cloud counts/hashes. Conflicts require a policy decision; never silently overwrite decisions or outcomes.

Default sync direction is local to Supabase for selected records. Public sources can be re-ingested. Two-way conflict resolution is deferred.

## Power BI contract
- Connect to certified views, not raw_public, staging, or personal tables.
- Use a least-privilege read-only credential. Store credentials in Power BI's credential store, not in PBIX source or M scripts.
- Suggested model: DimDate, DimMacroSeries, FactMacroMonth, FactCompanyMonth, and separate snapshot tables.
- Macro facts have series × period grain. Company facts have their own grain. Do not join and sum both facts at duplicated grain.
- Catalog each metric's grain and unit. State when a relationship is associative, not causal.
- Show observation date, refresh time, source, staleness, and quality status.

## Environments

| Environment | Purpose | Data allowed | Credentials |
|---|---|---|---|
| Local development | Build, explore, recover | Public, synthetic, approved minimized aggregates | Ignored local env or OS secret store |
| Personal Supabase | Online personal app and selected sync | Personal and approved shareable records with RLS | Server-side secret store |
| Shared/demo | Demonstrate or collaborate | Synthetic or explicitly sanitized shareable data | Separate project and credentials |

No client-production credentials or customer raw data may be copied into personal Supabase.

## Reliability
Record each pipeline run's start/end, watermark, counts, validation status, and code version. Failed ingest must not replace the last certified data. Every signal must trace to observation IDs and transformation version. Use idempotent upserts and bounded retries. Keep encrypted local backups and test restore. Alerts report data failures or staleness, not invented business conclusions.

## Evolution path
1. Reproducible local macro and company marts.
2. Personal Power BI model and decision ledger.
3. Supabase migrations, owner-only RLS, and controlled outbox sync.
4. Founder app/API and curated shareable layer.
5. Reusable contract and optional vertical adapters.

Do not add multi-tenancy or customer-production serving claims here. Those belong in medallio-platform and need their own security and product gates.
