# Current roadmap and next delivery

Roadmap Release 1 is **in progress**. Build v0.12 adds recovery-contact evidence management and readiness gates to the v0.11 initial-access increment. A build number does not mean a roadmap release is accepted. The original 307-requirement ledger has 74 PARTIAL and 233 PENDING requirements; none is declared fully accepted.

## Finish Release 1 before moving to Release 2

| Priority | Remaining work | Acceptance evidence |
|---|---|---|
| 1 | Complete onboarding: authority renewal/extension, external recovery-channel verification/invitations and legacy tenant adoption | New tenant can run a business workflow only through explicitly reviewed grants; verified contacts and provider evidence are recorded |
| 2 | Complete lifecycle: real worker cancellation, source-credential rechecks, support/exit access, closure export/archive/deletion | v0.10 already fences access and holds work; live cancellation boundaries, governed exit and recovery still need acceptance |
| 3 | Live OIDC/MFA/passkeys and provider recovery | PKCE/state/nonce replay and disabled-account tests; actual assurance policy; enrolment/last-factor safeguards; action-bound step-up |
| 4 | Unavailable-owner recovery | Independently verified contacts/evidence, separate approvers and audited fail-closed custody transition |
| 5 | Full account/access acceptance | Expiry notices/jobs, provider logout/refresh tokens, shared-device mode, timeout warning, authority renewal/extension, certification, complete departure inventory and key rotation |
| 6 | Organisation reorganisation acceptance | Future-effective moves, affected-obligation preview, historical context and documented scope semantics |
| 7 | Native persistence and real service roles | v0.8 upgrade, duplicate-code preflight, RLS under separate app/identity roles, simultaneous approval/revocation, restart and backup/restore |

Already delivered: custom role create/revise/retire; independently reviewed flat group access; immediate member removal; organisation create/rename/move; renewal that removes old access; owner nomination/acceptance; own-session inventory/revocation; identity authentication cutoff; preferences; configured ACR enforcement. Extend these capabilities rather than rebuilding them. Exact limits are in RELEASE-0.9.md.

The next coding slice is reviewed delegation-authority renewal and extension. Initial authority expires within 90 days; extend it through an explicit, independently reviewed proposal that rechecks current source authority, recovery readiness, exact capability/scope ceilings and expiry. Preserve existing revocations and the one-time bootstrap marker. v0.12 supplies registered-account recovery-contact nomination, verification, replacement/renewal, revocation and live eligibility checks; it does not deliver account recovery or a new email/SMS challenge. External delivery/provider qualification, unavailable-owner recovery and operational acceptance still require further work.

## Retained release sequence

| Release | Scope | State |
|---|---|---|
| 1 | Tenant and user administration | In progress; v0.12 increment delivered |
| 2 | Security and privacy foundations | Planned |
| 3 | Programme planning | Planned |
| 4 | Advanced measurement | Planned |
| 5 | Forms | Planned |
| 6 | Ingestion | Planned |
| 7 | Offline | Planned |
| 8 | Evidence and evaluation | Planned |
| 9 | Participant and finance | Planned |
| 10 | Analytics | Planned |
| 11 | Automation and integrations | Planned |
| 12 | Reporting | Planned |
| 13 | AI | Planned |
| 14 | Product administration, migration, localisation, help and gaps | Planned |
| 15 | Full qualification | Planned |
| 16 | Production acceptance | Planned |

Earlier builds contain bounded implementation in some later-release areas. Their original acceptance criteria remain open. Track implementation, test evidence and operational acceptance separately. No deployment, real invitations, external messages or infrastructure purchases are implied.
