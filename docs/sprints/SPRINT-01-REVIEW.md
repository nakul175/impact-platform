# Sprint 1 review

Owner: Nakul Jain · Prepared 9 October 2026 for the sprint review · Update trigger: product owner acceptance or rejection of a story.

**Sprint goal:** an organisation can see and control exactly which AI use is allowed before anything is sent to a provider, and its opportunity shortlist is ranked by its own priorities with every commercial relationship disclosed; release reviews record threats against tests. **Result: all four stories built, independently reviewed, review findings fixed. None is Done yet:** each still needs a human code review and the product owner's acceptance (Definition of Done).

| Story | Points | Branch commits | Build | Status |
| --- | --- | --- | --- | --- |
| FR-AI-001 Explicit AI enablement and policy | 8 | 43297f7, 8bae855 | 0.37.0, migration 0041 | In review |
| FR-SEC-001 Threat assessment in every release review | 8 | ef98bec, 7ced44f | 0.37.0 (no migration) | In review |
| US-MP-03 Rank opportunities with the organisation's weights | 5 | 42f3cb7, deb0b4c, e40f6d9 | 0.38.0, migration 0042 | In review |
| US-DC-04 Disclose commercial relationships on every listing | 5 | ece6548, b11baee | 0.39.0, migration 0043 | In review |

All four sit on one stacked branch, `sprint-1/us-dc-04` (it contains the earlier story branches), on top of `sprint-0/foundation`. Merge order must stay 0041 → 0042 → 0043.

## Evidence (local, synthetic data)

- Every story: `make lint`, `make unit`, `tsc --noEmit`, documentation index, and `scripts/release_review.py --check` clean against that story's own base. The four stories were not checked as one change set before the push: hosted CI on PR #94 then failed the release review check, because the check searched only the 0.39.0 review for new entries. Fixed on 10 October (see `docs/RELEASE-0.37-threat-register.md`, "Correction after hosted CI"); the stacked change set now passes against `main` and against `sprint-0/foundation`, including a simulated test merge commit; story-specific PGlite suites pass; native PostgreSQL 16 focused runs, restart check, restore drill and populated upgrade (to 41, 42 and 43; also from baseline 33 for 43) pass; browser checks in packaged Chromium pass (ai-policy, ai-ranking, ai-disclosure, ai-enablement, ai-plan-export, ai-saved-review, ai-walkthrough, tola-ai-extension, a11y).
- Full PGlite suite: 2,301 passed, 0 failed at ece6548; on the final head b11baee a rerun reached about 85 % with no failure before the 10-minute session limit.
- Hosted CI (first run, 9 to 10 October, pushed by the owner's agent): PR #95 (Sprint 0) `checks` passed; PR #94 (Sprint 1) all four qualification jobs passed and `checks` failed at the release review step (the defect above), so its web type check step did not run there; locally `tsc --noEmit` passes.
- Not run anywhere yet: the live Keycloak suite, the full native suite, the remaining ~19 browser groups.

## Decisions taken during the sprint (owner defaults; change at review if needed)

1. Operations Head (FINANCE role) can read AI enablement (`ai.enablement.read`, never manage). Existing tenants get it only through the reviewed access upgrade.
2. Executive Director works in the platform as TENANT_ADMIN; OWNER is kept for custody actions.
3. A plan export containing guidance v2 is labelled `nonprofit-ai-plan-export-v2`; v1 exports are byte-identical to 0.38.0.
4. Opportunity scores and the eight commercial disclosures are drafts pending Imprana editorial and advisor confirmation, and say so on screen.
5. No AI destination is approved; the server AI switch stays off until the product owner approves a provider and region.

## Open for the product owner

- Approve an AI provider and region for the pilot (blocks switching AI on).
- Confirm or change the residual decisions in the threat register: every decision is a proposal with `confirmed_by` empty; 14 critical threats and both abuse chains are open, so gate G11 cannot pass yet.
- Confirm the draft opportunity scores and disclosures (editorial).
- Human code review of the four stories before merge (the AI reviews do not replace it).

## Next (Sprint 2 candidates)

US-DX-01a record and prioritise problems (5), FR-AI-016a AI jobs with budget reservation and cancellation (8), US-CM-05 AI usage and alerts (5), US-DX-03 locked baseline per problem (8); then FR-AI-016b, FR-UX-006 (language groundwork for Hindi) and US-DX-01b.
