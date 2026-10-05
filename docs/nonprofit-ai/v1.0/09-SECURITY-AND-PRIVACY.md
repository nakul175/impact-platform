# Nonprofit AI Enablement Security and Privacy

Edition 1.0 · 5 October 2026 · Proposed baseline for review

## Scope and authority

This threat model covers the BRD and the functional requirements in requirements.json. It supplements the existing impact-platform security model and does not replace its controls. Current implementation statements refer to commit 36073f1, build 0.30.0 and schema 35. Proposed controls need implementation and qualification before the affected journey is enabled. A document does not approve a data use, certify a supplier or establish legal compliance.

The first pilot uses synthetic information. Beneficiary personal data, credentials and confidential attachments are outside that pilot's permitted input. The profile's sensitive_data flag is self-reported and is not a detector or a permission to send sensitive information. Free text can contain prohibited information despite a warning; the pilot needs trained staff, an agreed boundary and human review. Future personal-data uses require a separately reviewed purpose, lawful handling basis, recipients, retention and evidence under DEC-NPA-003 and DEC-NPA-009.

## Assets and trust boundaries

Protected assets include organisation profiles and plans, identity and current grants, procurement and advisory records, immutable revision history, provider credentials, sealed advisory outputs and any future evidence attachments. Public catalogue descriptions remain editorial claims with provenance. A public listing must not expose private supplier onboarding or organisation records.

The browser is an untrusted client. Identity assertions are verified server-side; client IDs select a record but do not prove access. The API enters tenant-bound transactions on non-owner runtime roles. PostgreSQL enforces forced row-level security in addition to application authority. The provider receives only the explicit submitted profile and deterministic assessment for the existing advisory request. It has no platform query tool. Future suppliers and advisers receive only an approved disclosure scope, not general tenant access. Operators maintain service custody without automatic private business-data access.

Current catalogue versions are application code. Proposed content curation is a separate reviewed publication workflow, with a deliberately public snapshot. A worker's outbox entry proves intent; an external acknowledgement or reconciled result is needed to establish delivery.

## Threat register

| Threat | Required control and verification | Baseline or gap |
|---|---|---|
| T-NPA-001 Cross organisation record selection | Tenant context before table access, tenant-qualified keys, forced RLS, current scoped read and action checks. Test another tenant and a revoked user, including replay and list cursors. FR-NPA-025 and 039. | Current plan/advisory controls exist locally; real database roles and concurrency require native qualification. |
| T-NPA-002 Forged server metadata or ambiguous input | Closed DTOs reject unknown fields and duplicate JSON keys. Server determines author, revision, state and content versions. Test injected approver/state and boundary lengths. FR-NPA-037. | Current profile and draft validation exists. Every future DTO must repeat the control. |
| T-NPA-003 Prompt injection or misleading generated advice | Treat input as reference data; no tool execution; bound outputs; label drafts; require human review. Exercise hostile instructions and unsupported claims without asserting that a prompt guarantees safety. FR-NPA-010, 012 and 035. | Current advisory instructions and no-tool adapter exist. Workbench and systematic output evaluation are target work. |
| T-NPA-004 Excess spending and repeated generation | Reserve a bounded attempt under the tenant lock before the call; exact replay uses the original result; timeout and response limits; explicit provider availability. Monetary reservations and usage reconciliation are proposed. FR-NPA-023 and 029. | Three attempts per rolling 24 hours currently include failures. There is no currency budget ledger or persisted token accounting. |
| T-NPA-005 Unsafe disclosure through text or attachments | Action-specific consent, minimum submitted data, reviewed sharing scope, independent disclosure decision where required, no secrets in logs. Test denial and consent withdrawal before disclosure. FR-NPA-026 and 035. | Current advisory consent concerns the submitted brief only. No general DLP system or attachment review is claimed. |
| T-NPA-006 Replay after authority loss | Recheck membership, tenant state, read/action capabilities and original visibility before replay; changed payload under the same operation conflicts. FR-NPA-027 and 039. | Current plan and advisory implementation. Do not return a cached result before authority. |
| T-NPA-007 Output tampering or plaintext exposure | Authenticated encryption binds sealed output to tenant and request; key-ring access stays server-side; verify tamper, wrong tenant and unreadable-key errors. FR-NPA-010 and 026. | Current advisory AES GCM sealing uses the delivery key ring. Its lifecycle must be reviewed before broader AI workloads. |
| T-NPA-008 Stale or self approved procurement | Pin quote revisions and request fingerprint; separate requester and approver by natural person; recheck authority and required recent authentication at decision time. FR-NPA-016 and 035. | Procurement approvals are target work. Existing platform independence must be preserved. |
| T-NPA-009 Malicious supplier content and unjustified verification claims | Restricted onboarding; review evidence and conflict declarations; publish only an approved public snapshot; escape descriptions and treat supplier URLs as untrusted. FR-NPA-017, 018 and 031. | Current directory is editorial and source-backed. Supplier verification is not implemented. |
| T-NPA-010 Credential exfiltration and connector abuse | Server-side secrets, scope minimisation, destination validation and SSRF controls, revocation, safe error handling, synthetic qualification. FR-NPA-022. | Future integration design. The current fixed provider URL is not a general connector framework. |
| T-NPA-011 Lost or double service and financial actions | Atomic revision/audit/outbox/receipt; no external call in a database transaction; external idempotency, acknowledgement and reconciliation before claiming success. FR-NPA-014, 019, 020 and 027. | Existing infrastructure is reusable; supplier dispatch, bookings and payments require new adapters and qualification. |
| T-NPA-012 False competency or inflated impact | Distinguish self-completion from assessed competence and accepted delivery. Pin rubrics and evidence. Preserve deterministic official arithmetic and approval boundaries. FR-NPA-008, 021 and 024. | Current progress is self-recorded; competency and outcome evidence are target work. |
| T-NPA-013 Retention failure and unsafe export | Separate export permission, minimised versioned scope, expiry and audit; authorised privacy workflow for removal, including retained history and backup limits. FR-NPA-026 and 030. | Adoption export and its retention application are target work. No deletion UI or plan-specific history UI is claimed. |
| T-NPA-014 Invisible access widening | Review capability ceilings and grants; recompute pending profile proposals; do not widen already applied organisation access without the governed path. FR-NPA-025 and 033. | New capability profile exists; widening existing approved ceilings remains a dependency. |

## Data handling requirements

Classify public catalogue content separately from internal organisation working data, restricted identity and authority records, and secrets. Every new dictionary field records its owner, permitted purpose, visibility and retention decision. No global analytics may read private organisation payloads merely because an operator can administer tenants. Feedback must be optional, minimised and governed; it must not train rules or models silently from private records.

Application logs must omit credentials, submitted prompts, raw provider responses and personal information. Use safe reason codes, correlation IDs and aggregate operational counters. A provider's store false option is a request setting; it is not evidence of zero retention across the provider's infrastructure. Provider terms, hosting geography and contractual controls require review before any permitted sensitive use.

Current advisory claims and results are insert-only tenant tables. Claim persistence before generation can leave an in-flight request if the process crashes or authority disappears before result finalisation. Such a state requires investigation; changing the operation ID or automatically retrying can spend again. Future recovery must prove that it cannot repeat a completed external action.

## Required security evidence

Use synthetic fixtures with two organisations, two independently attributable people and separately scoped roles. Test denied reads/writes, hidden selectors, revoked membership, wrong capability, modified operation payload, tenant-swapped or expired cursor, stale revisions, forged server fields, hostile prompt text and unavailable provider. Test runtime database roles on native PostgreSQL; in-memory qualification cannot prove production concurrency or role isolation.

For target workflows add same-natural-person identities, supplier disclosure scope, expired evidence, quote changes after preview, connector revocation, SSRF destinations, signed webhook replay and financial reconciliation. Payment evidence is conditional on an approved model. Automated browser results are supporting evidence only; the two incomplete accessibility checks in the recorded browser file need manual investigation.

## Accountability and incident response

Proposed control owners are the product owner for scope and commercial policy, the organisation data owner for disclosure, the security lead for assurance, the procurement owner for approval policy and the operations lead for service incidents. These are role assignments for review, not named appointed people. DEC-NPA-003, 007, 009, 010, 011, 013, 014 and 015 must be resolved before their dependent services proceed.

On suspected leakage, unsafe output, duplicate generation or payment ambiguity: stop the affected action or connector, retain minimised immutable evidence, assess the impacted scope, contact the appointed owner through the agreed process and resume only after an accountable decision. Notification duties and timing depend on the approved operating policy; this document invents no jurisdictional deadline.

## References

Read 01-BRD.md, 02-FSD.md, 03-HLD.md, 04-LLD.md, 05-TEST-STRATEGY.md and 08-DATA-DICTIONARY.md with this document. Local facts are grounded in ai_enablement.py, ai_advisory_provider.py, ai_adoption_plans.py, migrations 0034 and 0035 and docs/RELEASE-0.30-ai-adoption-tool.md. Existing platform invariants remain authoritative in AGENTS.md and CLAUDE.md.
