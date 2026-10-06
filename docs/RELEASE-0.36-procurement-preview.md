# Build 0.36 procurement preview and unsaved-brief protection

6 October 2026 · Integrated local candidate; hosted gates pending · build 0.36.0 · domain API 1.25.0 · platform API 1.10.0 · schema 40 (unchanged) · head on `integration/0.32-tola-ai-sprint`, built from handover commit `29e40e6`.

Three bounded client changes to the existing AI adoption workspace, plus one reporting improvement and three checker/test robustness fixes. No migration, API operation, capability, role, provider call, supplier contact, purchase or automatic save was added. Official arithmetic is untouched.

## Delivered behaviour

1. **Unsaved organisation brief is protected.** In 0.35, editing only organisation-profile fields on a fresh plan left the draft "clean", so opening a saved plan silently replaced the brief. `AIAdoptionWorkspace.tsx` now keeps a `freshProfileSnapshot`, set only at deliberate fresh/context transitions, and the dirty test compares against it while no saved snapshot exists. The discard dialog now says which case applies: opening a plan replaces the organisation brief; starting a new plan clears only plan fields and keeps the brief.
2. **Procurement preview.** The immediate procurement fill is replaced by preview, apply and cancel (`AIProcurementPreview.tsx`, `AIProcurementPreviewModel.ts`). The four generated strings are unchanged; apply replaces only those four local draft fields, and ordinary Save plus current server authority remain required. The interaction-generation guard, stale-response, authority and pending-save protections are retained; `canManage` and `mutationBlocked` are passed through.
3. **Archive-neutral practice copy.** Unknown/Stale edition wording no longer claims archived guidance is unavailable; it points to "View saved guidance", which reports retained or unavailable content from the actual archive lookup.
4. **Walkthrough accessibility reporting.** `ai-walkthrough-check.mjs` now retains axe `incomplete` entries (targets and failure summaries) in its report instead of discarding them.

## Checker and test fixes made during qualification

Each was a measured defect in the check, not in the product; every original failing run is preserved under `docs/evidence/sprint-0.36/`.

- `ai-enablement-check.mjs`: the four procurement text areas are addressed by role and exact name; the label matched more than one element (strict-mode violation, twice).
- `tola-ai-sprint-check.mjs`: `Connection: close` on each API call. Reused keep-alive sockets produced `UND_ERR_SOCKET` (`fetch failed`), reproduced three times.
- `qualification/test_native_worker.py::test_native_lease_takeover_while_the_first_holder_is_sending`: the first holder's send time was 8 s and is now 30 s; the final wait is 60 s. In two full native runs the rival pass took 5.6–6.2 s over a 138-tenant database, longer than the 2.5 s window, so the holder was never superseded in time. Assertions are unchanged.

## Qualification at this edition

All runs are on the committed head `4ecf543` unless stated. Counts overlap and are not summed.

| Executed scope | Observation |
| --- | --- |
| Lint, strict `tsc`, dual-entry production build | Pass. |
| Five pure browser prerequisites | Pass: plan export adapter (21 groups), plan review model (22), practice starter model, walkthrough adapter (starter and walkthrough clean), procurement preview model (35 groups). |
| 26 browser modes | 26 PASS, 285 groups, 0 failed, run on `27622e6` with only the later test-only commit (`4ecf543`) added; client and checker bytes are identical. |
| Accessibility | Walkthrough 15 scans: 0 violations, 0 incomplete. Broad a11y 44 pages: 0 violations, 50 retained incomplete-rule entries. Enablement 8 scans: 0 violations, 0 incomplete. Automated scans are not manual WCAG conformance. |
| Native PostgreSQL 16.15, fresh `impact_test_c036f` | 2,102 passed, 26 explicit skips, 1 deselected, 0 failed. Both restart phases, restore (190 tables, 108,103 rows, 40 checksums) and populated 33→40 upgrade pass. |
| Embedded PGlite | 2,037 passed, 91 explicit skips, 1 deselected, 0 failed. |
| Unit (`make unit`) | 1,242 passed, 62 explicit skips. |
| Inventories and migrations | 420 / 74 / 111 as frozen; all 40 migration hashes unchanged. |

Failed and superseded runs kept: first pure/enablement attempts (`ev/`), 25-of-26 browser run (`browser26-first-run/`), two native runs failing the takeover test (`gates/native-attempt1`, `-attempt2`).

## Limits

- **This is a local record from the repository's own gates, not a producer-generated, source-bound checkpoint manifest.** The interrupted producer drafts are Mac-bound and were reviewed but not run; see [PRODUCER-REVIEW-2026-10-06](nonprofit-ai/v1.0/drafts/0.36/PRODUCER-REVIEW-2026-10-06.md).
- The native gate was run on PostgreSQL 16.15; hosted CI uses a different minor version. Hosted `live-identity-provider`, `container-stack`, the CI native gate and the CI browser job have **not** run on this head.
- No merge, deployment, or hosted demo verification is claimed. Hosted state could not be inspected from this workspace.
- Requirement ledger unchanged: 113 PARTIAL, 194 PENDING, 0 accepted. No test-case or acceptance status moves.
- No supplier certification, procurement award or provider call is implied by the preview.

## Next release step

Owner grants paid-CI permission → open the PR for this exact head → the four required checks (`local-reference-and-browser`, `live-identity-provider`, `native-postgresql-gate`, `container-stack`) must pass on that head → merge → verify the merged commit, schema 40, health and the hosted demo. Do not push to `main` directly.

Development detail: [DEVELOPMENT-0.36](nonprofit-ai/v1.0/DEVELOPMENT-0.36.md).
