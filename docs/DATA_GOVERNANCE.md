# Data governance and sharing boundary

## Purpose
This repository is public. Treat every committed file as visible to anyone. Git holds code, contracts, examples, and non-sensitive configuration templates; local PostgreSQL and personal Supabase hold data.

## Classification

| Class | Examples | Git | Personal Supabase | Share |
|---|---|---:|---:|---:|
| Public | Official economic series and source metadata | Yes, if terms allow | Yes, subject to terms | Yes, cite source |
| Synthetic | Generated sample records | Yes | Yes | Yes, label synthetic |
| Founder-private | Notes, strategy rationale, private decisions | Never | Owner-only if needed | No |
| Internal non-sensitive | Approved company-level measures | No raw exports | Owner-only by default | Only after review |
| Client-confidential / personal data | CRM rows, contact details, contracts, production extracts | Never | Never in personal project | No |
| Secret | Passwords, API keys, tokens, connection strings | Never | Secret store only | Never |

## Publication rule
Sharing is an explicit publication event. A record can be shared only when the business owner and audience are known; it contains no identifiers, raw customer data, or confidential fields; source terms permit redistribution; claims include provenance, date, unit, limits, and confidence; the copy is minimized; and the founder approves publication.

Default access is private. Creating a shareable view does not itself authorize a public site, external distribution, or customer commitment.

## Cygnus/reference boundary
Cygnus may inform reusable real-estate patterns through aggregated, sanitized evidence. This repo must not pull from Cygnus production or store its exports. Any future adapter must run in the authorized source environment, export only a reviewed aggregate contract, omit identifiers and confidential fields, document authority and retention, and receive founder and data-owner approval before first use.

## Technical controls
- Ignore .env, local databases, exports, notebooks with outputs, and credentials.
- Enable RLS on every owner-scoped Supabase table and test owner access and cross-owner denial.
- Keep internal schemas out of PostgREST exposure; allowlist API views.
- Use distinct credentials per environment; rotate credentials if exposed.
- Log sync IDs and metadata, not secrets or sensitive payloads.
- Add secret scanning before implementation expands.
- Keep connection strings out of issues, logs, screenshots, and Power BI query text.

## Incident response
If sensitive data or a credential reaches the wrong audience: revoke or rotate access, restrict the artifact, identify affected copies and exposure window, notify the data owner through an approved channel, and document remediation without reproducing the data.
