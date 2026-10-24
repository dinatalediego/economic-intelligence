# ADR-001: Personal-first local system with selected Supabase sync

- Status: Proposed
- Date: 2026-10-24
- Decision owner: Founder
- Scope: Economic Intelligence repository

## Context
Economic Intelligence should help the founder operate and improve Medallio, while allowing selected findings to be shared with collaborators or design partners. It must work on the personal machine and online through Supabase. It may use public Peruvian economic sources and Medallio-level context, but must not turn a client reference implementation into a personal raw-data store.

## Decision
Adopt local-first architecture with local PostgreSQL as reproducible working copy and recovery path. Sync selected, classified records through an explicit outbox to a personally controlled Supabase project. Keep founder-private, client-confidential, and shareable data in distinct domains and access paths. Power BI consumes certified read-only views.

## Consequences

### Benefits
- Analysis remains available and testable without cloud access.
- The founder can use a personal online app without copying a local warehouse.
- A reviewed shareable surface can be created without access to private source records.
- Transformations and schemas can be versioned and reproduced.

### Costs
- Local and cloud schemas need migrations and compatibility checks.
- Sync needs idempotency, audit, retries, and conflict rules.
- RLS, backups, and restore must be tested before relying on the cloud copy.
- Hosted Power BI access needs a least-privilege path.

## Rejected alternatives
- Cloud-only database: weaker local recovery and offline work.
- Full local database replication to Supabase: greater exposure without a clear use case.
- Power BI as semantic layer: duplicated logic and weaker reproducibility.
- Direct Cygnus production connection from this personal project: crosses client/personal boundaries and couples the product to one customer.

## Revisit when
Collaboration extends beyond the founder; volume or refresh needs exceed local pipelines; an approved partner needs a governed view; or the workflow is moved into the tenant-aware Medallio Platform.
