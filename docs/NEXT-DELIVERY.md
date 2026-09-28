# Current roadmap and next delivery

Release 1 — **Usable core** — is **in progress**. Build v0.13 added reviewed renewal of unexpired delegated authority to the v0.11 initial-access and v0.12 recovery-contact increments. On 28 September 2026 scope decision SD-01 reorganised the delivery sequence into three releases so that the first one is usable on its own by one organisation; the sequenced increments, the decision record and the quality backlog are in [DELIVERY-PLAN.md](DELIVERY-PLAN.md). A build number does not mean a release is accepted. The original 307-requirement ledger has 74 PARTIAL and 233 PENDING requirements; none is declared fully accepted, and the ledger's own R1/R2/R3 requirement tags are unchanged by SD-01.

## Release 1 — Usable core

Definition: one organisation runs its real MEL cycle end to end on hosted infrastructure with real logins — results framework, governed indicators, web forms and imports, independent review, calculation, period close, PDF/XLSX exports, dashboards — with the P0 security, privacy, backup and monitoring safeguards.

| Priority | Remaining work | Acceptance evidence |
|---|---|---|
| 1 | Deployable base: native PostgreSQL with separate login roles, upgrade path, concurrency and restore drill (v0.14); live identity provider with MFA, logout and revocation (v0.15); worker, outbox dispatcher and email adapter (v0.16); deployment package, secrets, logs, metrics, backups, first staging deployment (v0.17) | Native and provider evidence recorded per run; a staging deployment operated with a restore drill |
| 2 | Programme design and measurement: results framework and planning (v0.18); indicator and calculation completion with golden corpus (v0.19) | P0 PLN/IND/CAL requirements at PARTIAL with executed evidence; calculation reconciliation against the corpus |
| 3 | Data collection: web forms (v0.20); CSV/XLSX import and data quality (v0.21); object store and evidence attachments (v0.22) | Submissions become observations with value states; imports staged and quarantined; attachments scanned and mediated |
| 4 | Outputs: PDF/XLSX/DOCX exports of frozen packages (v0.23); dashboards from official snapshots (v0.24) | Rendered artifacts bound to locked snapshots; freshness shown |
| 5 | Safeguards and acceptance: security and privacy P0 (v0.25); non-functional qualification, accessibility, UAT pack, penetration-test remediation (v0.26) | Release acceptance procedure with named approvers |

Already delivered: custom role create/revise/retire; independently reviewed flat group access; immediate member removal; organisation create/rename/move; renewal that removes old access; owner nomination/acceptance; own-session inventory/revocation; identity authentication cutoff; preferences; configured ACR enforcement; reviewed extension of unexpired delegated authority (v0.13). Extend these capabilities rather than rebuilding them. Exact limits are in RELEASE-0.9.md and RELEASE-0.13.md.

The next coding slice is **v0.14, native PostgreSQL qualification**: separate app, identity and platform login roles provisioned by script and refused by the runtime guard when privileged; upgrade of a populated schema-15 database to schema 16; native-only concurrency tests (simultaneous approvals of one candidate, revocation racing a renewal approval, simultaneous period close); API restart persistence; a backup and restore drill with measured timing; one migration runner; per-test signed fixture tokens; and a regenerated fixture ahead of its 2026-12-01 expiry. Administrator replacement and renewal of expired authority, previously planned as v0.14, move to Release 2 under SD-01; the v0.13 renewal path keeps unexpired authority alive meanwhile.

## Releases 2 and 3

| Release | Scope | State |
|---|---|---|
| 1 | Usable core (above) | In progress; v0.13 delivered |
| 2 | Field and partners: offline and Android, participants, evaluation, remaining evidence, integrations and connectors, migration tooling, tenant-administration completion (administrator replacement, legacy adoption, unavailable-owner recovery, lifecycle closure, access certification, organisation reorganisation) | Planned |
| 3 | Intelligence: AI, advanced analytics, finance, remaining reporting and delivery, localisation and help completion | Planned |

The former 16-stage sequence (tenant administration; security and privacy; programme planning; advanced measurement; forms; ingestion; offline; evidence and evaluation; participant and finance; analytics; automation and integrations; reporting; AI; product administration, migration, localisation, help; full qualification; production acceptance) is retained in the engineering implementation plan for traceability and is no longer used for scheduling.

Earlier builds contain bounded implementation in some later-release areas. Their original acceptance criteria remain open. Track implementation, test evidence and operational acceptance separately. No deployment, real invitations, external messages or infrastructure purchases are implied by this record; hosting, identity-provider and email-provider decisions are the owner's and are listed in DELIVERY-PLAN.md §2.
