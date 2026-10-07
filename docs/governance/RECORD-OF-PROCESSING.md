# Record of processing activities (framework)

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: a new data class, tenant region, recipient, provider, AI use case, export, or the first real-data tenant.

Status: **agent-drafted 2026-10-08 from repository documents; not reviewed by a person or counsel; no certification or legal compliance is claimed.** Structure follows the headings of GDPR Article 30 and the duties of a Data Fiduciary under India's Digital Personal Data Protection Act 2023 as a checklist only. Controller/fiduciary and processor roles are decided per deployment, not by this repository. **Today the only permitted data is synthetic** ([AGENTS.md](../../AGENTS.md) rule 11); this record is the template that must be completed before real data.

Sources: [DATA-GOVERNANCE](../current/DATA-GOVERNANCE.md), [RELEASE-0.25b](../RELEASE-0.25b.md), [KEY-AND-ENCRYPTION-REGISTER](../current/KEY-AND-ENCRYPTION-REGISTER.md), [DEPLOYMENT-GUIDE](../current/DEPLOYMENT-GUIDE.md), [AI-MODEL-CARD](AI-MODEL-CARD.md).

## 1. Parties (to be set per deployment)

| Item | Value |
|---|---|
| Controller / Data Fiduciary | The tenant organisation (proposed allocation); name: TBD (owner: Nakul Jain) |
| Processor / Data Processor | Operator of the platform (APLYD / the owner); legal entity: TBD (owner: Nakul Jain) |
| Contact | nakul.jain@aplyd.com (platform owner). Data-protection officer or grievance officer: TBD |
| Sub-processors | DigitalOcean (hosting, droplet backups; region `do-blr1`, Bangalore, per DEPLOYMENT-GUIDE); Let's Encrypt (certificates; no personal data); OpenAI only if AI advisory is enabled (off by default); e-mail provider: none chosen. Contracts and transfer terms: TBD |

## 2. Processing activities currently implemented

| # | Activity | Purpose | Data subjects | Data categories | Recipients | Store / location | Retention | Security measures |
|---|---|---|---|---|---|---|---|---|
| 1 | Sign-in and sessions | Authenticate users with MFA | Members, operators | Identity subject, verified e-mail (kept as SHA-256 and a mask), session metadata | Keycloak on the same server | PostgreSQL `impact`, Keycloak database | Session: 15 min idle / 8 h absolute; other: see [RETENTION-SCHEDULE](RETENTION-SCHEDULE.md) | Forced row-level security, hashed cookies, MFA assurance |
| 2 | Membership, invitations, grants | Access control | Members | Display name, e-mail mask and hash, role grants | Tenant administrators | PostgreSQL | Not deleted except on an approved erasure | Closed DTOs, separation of duties |
| 3 | Programme measurement | Monitoring and reporting | Programme staff; participants only if the tenant enters them (no participant records exist in this build) | Observations, results, evidence files, review decisions | Named report recipients | PostgreSQL; evidence files on the `objects` volume | Official records are kept; see schedule | Immutable revisions, forced RLS, scan verdicts |
| 4 | Audit and denial records | Accountability | Members | Principal identifiers, actions, refused access | Owners, tenant administrators | PostgreSQL | Denials 365 to 3,650 days (default 2,555) | Append-only |
| 5 | Notices and e-mail delivery | Invitations, reminders | Members | Recipient address (AES-256-GCM sealed), template, reference | E-mail provider (none; loopback capture on staging) | `outbox_delivery` | Address redacted 30 days after final state | Keyring-sealed |
| 6 | Data-subject requests | Rights handling | Members | Case record, export package | Requester via authorised role | PostgreSQL | Export package 7 days | Purpose-bound grant, independent approval |
| 7 | AI advisory draft (optional, off) | Advice for nonprofit AI adoption | Not intended to include personal data; synthetic pilot only | Organisation brief submitted by a user | OpenAI API (`store:false`) when enabled | Sealed result in PostgreSQL | Not scheduled: TBD | See model card |
| 8 | Backups | Recovery | All of the above | Whole databases and evidence | None off-server except DigitalOcean droplet backups | `backups` volume; droplet backups | 7 daily, 4 weekly sets | Not encrypted by the application; provider encryption unverified |

## 3. Transfers and location

Server region `do-blr1` (India). Cross-border transfers: none by design except the optional AI call to OpenAI (provider region and retention terms not established; `IMPACT_MODEL_DESTINATIONS` is an unsupplied release input). Transfer basis: TBD (owner: Nakul Jain; counsel).

## 4. Gaps before real data

Named controller and processor; lawful basis or consent model per tenant; notice texts; processor contracts; provider region and retention confirmation; participants as data subjects (not implemented); deletion not replayed after restore; breach-notification procedure with deadlines ([INCIDENT-PROCESS](INCIDENT-PROCESS.md)); completed [DPIA](DPIA.md).
