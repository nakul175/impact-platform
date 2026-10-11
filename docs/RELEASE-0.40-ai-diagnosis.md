# v0.40 — Manual organisation diagnosis (US-DX-01a)

Local candidate: build0.40.0, domainAPI1.29.0, platformAPI1.11.0, schema44. No requirement acceptance, merge or deployment. Frozen307-requirement baseline remains unaccepted.

## Delivered

A separate tenant diagnosis screen and eight API operations record up to20 named problems, affected areas, manual evidence notes and explicit stable-ID priority order. Drafts may be incomplete. Completion refuses every missing field/priority with the incomplete problem named; a completed diagnosis is read-only until an explicit reason-bound correction creates a later draft. Exact historic content/state remains readable under current authority.

Original source: [APL-361](https://linear.app/aplyd-sandbox/issue/APL-361/us-dx-01a-record-and-prioritise-the-organisations-problems). Its two original criteria and case versions remain unchanged; task01–06 are supported by implementation/qualification work, not marked Done. Scope and bundle application are in [implementation contract](engineering/delivery-system-20261011/US-DX-01a-IMPLEMENTATION.md).

## Contract and persistence

`/v1/tenants/{tenant}/ai-enablement/diagnoses`: GET/POST; GET/PUT `/{id}`; POST `/{id}/actions/complete` and `/{id}/actions/revise`; GET `/{id}/revisions` and `/{id}/revisions/{revision_id}`. Closed request/result schemas; current separate TENANT read/manage grants; completion/correction fresh authentication; signed cursor bounds. Migration0044 registers `AIDiagnosis` and its TENANT_ADMIN-only onboarding capabilities in existing forced-RLS registry/revision storage. No historic migration, row, adoption-plan/archive/export format or existing delegation ceiling changes.

## Limits

Evidence is text supplied by the user; no attachment, protected-object selector, verification of its factual truth, model call or official impact calculation. Candidate includes a20-problem and1000-diagnosis-per-tenant bound. Four native PostgreSQL tests are present but unrun; no native concurrency, role fence, populated upgrade, restart/restore, full hosted CI, manual accessibility, security human confirmation or release acceptance is claimed. Existing tenants need the governed access upgrade before using new capabilities.

## Reproduction and observed checks

Final local results: **1,522 unit cases passed (62 skipped), 136 affected API cases passed (12 skipped), all 57 new diagnosis API cases passed, nine actual Chrome browser groups passed, three bounded component-adapter cases passed, and 143 independent reference checks passed**. Unit/API skips are existing mode-dependent cases, not qualified native results; the four added native tests were not run. Full TypeScript/build and lint passed. Vite retains a large-bundle warning. Exact outcomes, failed attempts, advisory fixes, source hashes, served asset/runtime/migration pins and pending gates are in [qualification receipt](evidence/candidate-0.40/QUALIFICATION-RECEIPT.json). Browser start/end source and asset hashes are unchanged; no external/provider request or new advisory row was observed. Automated desktop/mobile axe scans found no serious/critical violation; incomplete findings and manual accessibility limitations remain in the raw receipt.

The original two criteria have explicit source case markers and locators in a distinct [local binding supplement](engineering/delivery-system-20261011/LOCAL-CASE-BINDINGS.json). The original all-active planning edition remains frozen, unbound and unqualified. Fifty-seven API and nine browser execution rows are appended to the current execution register; no previous rows or original criteria changed. Current story traceability lives in a separate story supplement, preserving the original 307-FSD requirement register.

Reproduce API checks with `IMPACT_PORT=8237 .venv/bin/python -B scripts/run.py test --perf --pytest-path qualification/test_ai_diagnosis_live.py --pytest-path qualification/test_ai_diagnosis_faults_live.py --pytest-path qualification/test_ai_diagnosis_visibility_live.py`. Add the affected existing adoption-plan/archive/ranking/policy/access-upgrade targets listed in the receipt's JUnit. `--perf` places runner JUnit in the disposable directory; this is not a performance benchmark. One existing archive test writes the historic migration-observation file despite this flag; its new observation is preserved separately and the historic bytes restored before committing.

Browser: `IMPACT_PORT=8238 IMPACT_BROWSER_EXECUTABLE='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' IMPACT_BROWSER_EVIDENCE_FILE=<new-output-path> .venv/bin/python -B scripts/run.py ai-diagnosis-browser` on a Mac with that installed executable; the repository's prepared Linux Chromium is the default elsewhere. Component adapter: `node tools/browser/ai-diagnosis-uncertain-command-check.cjs`; it uses declared in-memory hooks/request errors and never claims HTTP expiry or native/browser qualification. All records and demos are synthetic and loopback-only.

Independent advisory review caught and corrected the named Error reader mismatch, terminal authority/late-response metadata race, uncertain expired/conflicting replay recovery, and test fixture/counting assumptions. Earlier failure receipts remain immutable alongside final passing results; no test was removed or weakened.

## Integration notes

Root is sole canonical writer; supporting agents submit isolated proposals and independent advisory reviews. Local branch `feat/imprana-diagnosis-20261011` starts at documentation checkpoint92341d6; source profile and old migrations are pinned. Only US-DX-01a is active. Security review0.40 remains passed=false and its impact review unconfirmed. No next feature starts before this story's actual delivery gates. No paid CI, remote export, main merge or deployment authority is inferred. The attached delivery bundle is sealed reference; its workflow/engineering profiles and CI enforcement are not installed or certified.

## Native qualification follow-up — 11 October 2026

This follow-up supersedes the earlier native-not-run observation, preserving that historical receipt. Private native PostgreSQL 17.10 qualification passed **2,484 tests, 26 skipped, one existing IT_018 runner deselection and one deprecation warning; zero failures/errors**. All four original diagnosis native cases and six added queued-create/edit/exact-replay cases passed under withdrawn read/manage authority. The queued cases observe an actual advisory-lock wait before synthetic current-grant narrowing and verify a refusal with unchanged domain writes and immutable history/receipt. This does not claim the governed revocation workflow itself was exercised.

The existing real API restart phases both passed; the generic restore drill passed across 192 tables / 111,751 compared rows with all 44 migration checksums and restored RLS/functions/grants matching. Populated schema40-to44 upgrade passed with the existing seeded rows preserved. The generic restore drill proves counts/security and the pinned golden result, not exact diagnosis payload/replay through a restored API. [Exact new native receipt](evidence/candidate-0.40/native-20261011/NATIVE-QUALIFICATION-RECEIPT.json) retains source/runtime pins, actual per-case outcomes, raw reports and the separate source/evidence review phases; these are root-agent reviews, not independent human acceptance. Nine historic output files were restored byte-exact after their new observations were saved separately.

The official checksum-verified source was built into a private project output directory; no system package, cloud resource, production data or paid action was involved. The disposable UTF8/C cluster is stopped. Local build excludes ICU/readline/TLS and does not qualify the deployment configuration. Live identity provider, container stack, required exact-head hosted CI and human security/accessibility/owner gates remain pending; current release review stays passed=false. No next feature, remote push/PR, merge or deployment has started.
