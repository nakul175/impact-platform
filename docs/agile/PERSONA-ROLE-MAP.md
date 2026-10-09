# Persona to role map

Owner: Nakul Jain · Decided 9 October 2026 (default, revisit at the first sprint review) · Update trigger: a new persona or role template.

Backlog stories are written for 21 personas. The platform's permissions use the 15 role templates in `packages/contracts/access-policy.json`. Until a story says otherwise, a persona's capabilities are those of the role below. A persona with no exact role uses the nearest one; adding roles is its own story.

| Persona | Role template | Note |
| --- | --- | --- |
| Executive Director | TENANT_ADMIN | For working in the platform (owner decision of 9 October 2026, US-DC-04 review): OWNER holds custody without data access in this platform, so stories written for the Executive Director are exercised as TENANT_ADMIN. OWNER applies only to custody actions (accepting custody, ownership transfer, recovery) |
| Organisation Administrator | TENANT_ADMIN | |
| Operations Head | FINANCE | Reads AI enablement (`ai.enablement.read`, read-only, never `ai.enablement.manage`): owner decision of 9 October 2026 for US-MP-03, in the onboarding profile registered by migration 0042; existing tenants get the FINANCE role template only through the reviewed access upgrade. Plus read of AI usage (`ai.usage.read`) once that capability exists |
| MEL Manager | MEL_ADMIN | |
| Programme Manager | PROGRAMME_MANAGER | |
| Data Author | AUTHOR | |
| Reviewer | REVIEWER | Independence by natural person still applies |
| Field Data Collector | ENUMERATOR | |
| Data Steward | DATA_STEWARD | |
| Analyst | ANALYST | |
| Finance Officer | FINANCE | |
| Privacy Officer | PRIVACY | |
| Platform Operator | OPERATOR | Control plane, not tenant data |
| Support Agent | SUPPORT | |
| Integration Developer | SERVICE | Service identity; no human sign-in |
| Funder Portfolio Manager | EXTERNAL | Scoped, reviewed grants only; cross-organisation view is story US-FP-02 |
| Partner Organisation User | EXTERNAL | |
| Imprana Advisor | EXTERNAL | A dedicated ADVISOR role is a future story (needed by US-DX-05, US-OP-01) |
| Solution Partner Manager | — | No tenant access; partner portal is R2 (US-PT-01) |
| Programme Participant | — | Data subject; acts only through privacy requests |
| Product Owner, Athena Leadership | — | Repository and governance work, not platform roles |
