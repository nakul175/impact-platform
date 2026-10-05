# Development increment 0.33: governed evidence and internal advice

5 October 2026 · Build 0.33.0 local checkpoint; known cleanup privacy blocker · domain 1.24.0 · platform 1.10.0 · schema 39.

This appendage extends the original proposed BRD → FSD → HLD → LLD and its test design. Those edition 1.0 reference documents, editable documents, wireframes, 362-field dictionary, 40-requirement baseline and 108 specified case statuses retain their original reference point. The final named [release record](../../RELEASE-0.33-tola-ai-extension.md) owns this increment's qualification and limitations. It is an extension of the same platform, using the shared programme, measurement, authority, history and audit services.

## Support map

| Proposed requirement | Added bounded implementation | Named implementation sources | Remaining scope |
| --- | --- | --- | --- |
| FR-NPA-024 | Explicit saved-plan relationship to current-authorised governed programme/indicator/period; frozen official versus current provisional evidence; manual refresh and no inferred AI causality | `ai_impact_references.py`, `test_ai_impact_references.py`, `test_ai_impact_references_live.py`, `AIImpactEvidence.tsx` | Full specified case execution, attribution design, reporting disclosure, operated KPI service and nonprofit acceptance |
| FR-NPA-011 | Existing-member advice invitation, conflict declaration, explicit assignment/consent, accountable questions, advice/actions and exact closure | `human_advice.py`, `test_human_advice_unit.py`, `test_human_advice_live.py`, `AIHumanAdvice.tsx` | Adviser onboarding, verified qualifications/availability, external engagement, operated advice service, retention/removal |
| FR-NPA-006, FR-NPA-027, FR-NPA-039 | Atomic plan relationship revisions, actual prior guidance inheritance and exact current-authorised replay; private case revisions and projection | Existing plan/archive writer plus focused impact/advice tests | Portable exports, complete retention, formal specified-case execution and acceptance |
| FR-NPA-025, FR-NPA-037, FR-NPA-039 | Current programme authority, uniform absent/hidden response, private advice brief/proofs, current participants and forced tenant row security | Dedicated result routes, frozen migration 0038, current-visibility regressions | Hosted/provider/security acceptance and complete platform access certification |
| FR-NPA-028, FR-NPA-040 | Saved-plan panels, read-only/privacy controls, recovery after uncertain requests, forwarded actor/identity reset and mobile layouts | New UI panels and `tola-ai-extension-check.mjs` | Latest actual browser passes28 groups; same-identity session-generation reset, manual accessibility and nonprofit UAT remain pending |

These are support relationships, not acceptance transitions. TC-NPA-021/022 remain specified cases awaiting their formal execution. Similar implementation tests do not silently execute or accept them. Original core requirement states remain 113 PARTIAL / 194 PENDING / zero accepted.

## Added data and UI dictionary

| Record / DTO / screen | Meaning and authority |
| --- | --- |
| `AIAdoptionPlan.impact_reference` | Optional server-only metadata: exact programme, indicator, definition, period and calendar UUID/revision pairs, nullable snapshot UUID/revision/version, bounded interpretation note and exact reference schema constant. Generic reads project it out; generic writes cannot supply it. No result arithmetic is copied. |
| `AIImpactReferenceResult` | Dedicated current-authorised read model, containing deliberate pins/status and the existing governed dashboard cell. No available evidence is an opaque unavailable response. |
| `human_advice_case_current` | Current tenant/case revision, exact saved plan anchor, immutable requester/adviser principal, membership and private natural-person proofs, and current state. Application role privileges remain RLS-governed. |
| `human_advice_private_brief` | Insert-only bounded problem text, random private nonce and salted integrity digest. Adviser reads require assignment and current authority; terminal adviser reads are refused. |
| `HumanAdvicePublicData` | Closed participant projection. Private natural-person proofs, authentication timestamps, internal schema marker and brief digest are omitted, including nested decision authentication proofs. |
| Programme evidence panel | Current programme/indicator/period selection, explicit link/refresh/clear, independent official/provisional blocks and unavailable states. Unsaved draft edits must be resolved before relationship changes. |
| Internal advice panel | Permission-bounded colleague choice, invitation, declaration, consent/assignment, questions/answers, advice/actions, closure/cancellation and read-only revision history. |

The [current dictionary](../../current/CURRENT-DATA-DICTIONARY.md) records all 19 new database columns and exact frozen SQL. Slice notes provide complete private metadata and state/permission details: [programme evidence](../../RELEASE-0.33-impact-references.md), [internal member advice](../../RELEASE-0.33-human-advice.md).

## Current evidence and remaining checks

The candidate's named pure checks pass: 149 impact/adjacent, 90 human advice and 16 kernel-environment checks. Schema39 retained visibility passes96 focused checks with two native-only skips, covering eleven current/historical restrictions and preserving exact old snapshots and decimal values. Schema39 advice passes122 PGlite checks with six native-only skips; its actual PostgreSQL17.11 qualification passes142 checks with no skips, including executor topology and actual application-login pointer privacy. Counts overlap and are not summed. Final actual native1,929/PGlite1,865/unit1,102 and28 browser groups pass; both actual API restart phases, backup restoration and populated33→39 upgrade pass. Their exact source/evidence hashes and explicit skips are in the release record. A subsequently reproduced private-advice cleanup-definer key disclosure remains unresolved in registered0.33 and blocks deployment/full privacy qualification; its additive correction is being reviewed in next0.34. Scratch PostgreSQL experiments and request-function UI fixtures retain their narrower scope and do not establish production acceptance.

The final source-bound release record identifies executed reports, failed attempts, explicit skips, actual applied migration ledgers and the known cleanup privacy residual. Existing Mercy Corps-derived approved-logframe export conventions and attribution remain in their governed export workflow; this increment reuses the integrated Tola programme/measurement services. It introduces no new claim of importing Mercy Corps code or content.
