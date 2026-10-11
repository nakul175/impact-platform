# Changelog

The change record is [docs/current/CHANGELOG.md](docs/current/CHANGELOG.md) (documentation editions and builds, newest first). Every build also has a release note, `docs/RELEASE-0.N*.md`; the latest is named in the status block at the top of [docs/HANDOVER.md](docs/HANDOVER.md).


### Local schema45 diagnosis worker fence follow-up

See [0.40 release follow-up](docs/RELEASE-0.40-ai-diagnosis.md) and its source-bound receipt: additive0045,88 affected native passes/one existing skip,28 version/access-upgrade unit passes and actual restart/restore/populated44-to45 upgrade. No full-suite, hosted/container/human acceptance or deployed story claim; broader task gaps remain. Earlier source-checkpoint results stay historical.


### Local schema46 diagnosis identity/order follow-up — 11 October2026

Additive0046 enforces canonical unique problem IDs and member priority order; Draft partial order and SQL NULL removal storage shape remain valid. Actual158 focused native passes/one existing skip,28 version/access unit passes and56 recovery passes/one restored-mode skip followed by one restored-only API pass; real restart/restore/generic populated45-to46 upgrade passed. Earlier33 and8 failures preserved, no old test or prior migration changed. This is bounded local qualification, not full schema46 regression, independent human acceptance or deployment. See [candidate handover](docs/engineering/delivery-system-20261011/HANDOVER.md) and [constraint receipt](docs/evidence/candidate-0.40/diagnosis-order-schema46-20261011/CONSTRAINT-RECEIPT.json). Remaining protected-reference/access/hosted/container/human/release gates stay held,0 of50 delivered.


### Full local native schema46 qualification — 11 October2026

Exact a8597a7 source:2,530 passed/28 skipped/zero failures-errors, one unchanged IT_018 deselection and existing TestClient warning. Actual native login/restart/backup restore/generic populated45-to46 upgrade passed;271 source pins exact; historical generated evidence restored. [Current receipt](docs/evidence/candidate-0.40/full-native-schema46-20261011/FULL-NATIVE-RECEIPT.json) records each skip and distinct source/evidence reviews. Earlier provider/browser results stay source-bound; current hosted/container/human/wider-task gates remain held, release passed=false,0/50 delivered, no remote action or spending.


## Protected Evidence API integration — 11 October2026

Active US-DX-01a/APL-361 remains In Progress. Build0.40 unreleased candidate/domain API1.30/schema46: optional closed per-problem `evidence_references` now pins canonical object/revision pairs (up to5). Original supporting notes and completeness criteria remain mandatory; old notes-only payloads are unchanged. Current Evidence authority and source availability are freshly checked under tenant lock before save/edit/completion/correction and current/historical/list/exact-replay disclosure. Replay checks both current diagnosis and original receipt revision. Hidden rows filter; list/history scan at most100 candidate rows plus1 lookahead, fill the requested visible page where possible and use opaque scanned-row continuation without totals. A dense hidden batch can return a sparse/empty page with continuation. Unavailable previous sources block edits, including reference removal; a governed repair flow remains undecided.

Actual affected native run:89 passed, zero failures/errors/skips (8 new HTTP cases,24 resolver/shape cases,57 existing diagnosis HTTP cases). Separate114 unit cases passed, including3 deterministic paging cases. First7 new fixture failures and the later actual pre-existing pagination-test failure are preserved; fixed the cause without weakening tests. Native pins276 stayed exact; all46 migrations unchanged. These are separate source-bound affected scopes, not a new full-regression count or hosted CI. Evidence: `docs/evidence/candidate-0.40/evidence-api-integration-20261011/API-INTEGRATION-RECEIPT.json`.

Default diagnosis admin still lacks Evidence read and linked create refuses404. Positive tests use one fresh disposable synthetic OBJECT_SET read grant for one source, narrowed at teardown; no live identity, default profile/role/ceiling or production permission changes. This is fixture preparation, not a governed grant-flow or human approval pass. References currently persist only in immutable revision JSON: tenant-keyed FK linkage, source privacy/retention concurrency and recovery, accessible selector UI/browser and refreshed integrated regression remain. Separate source/evidence self-review is not independent human signoff; IR-0.40-07 unconfirmed and release passed=false. Runtime stopped and history preserved. Required exact-head hosted/container, external/financial and actual human/operational/owner release gates held;0/50 delivered, no next story/export/deployment.


## Typed Evidence linkage implementation — 11 October2026

Actual code now exists in `docs/engineering/delivery-system-20261011/diagnosis-evidence-linkage.CANDIDATE.sql`: tenant-keyed typed object/revision/kind FKs; immutable per-problem/position binding; atomic revision insertion trigger; forced RLS with app SELECT/INSERT only and no worker/platform/identity table grants; owner-directory per-tenant historical backfill; guarded diagnosis-removal cleanup hook. This is a complete local candidate, not registered schema47 or deployed linkage. Existing46 migrations and contract/domain1.30 unchanged. Source existence/kind/tenant linkage and current Evidence authority are separate controls.

Final affected native123 passed, zero failures/errors/skips:10 new linkage cases,89 existing diagnosis/resolver,5 existing worker and19 existing privacy/security cases. Save/complete/correction links remain exact; missing/wrong object/kind/actual foreign-tenant source references refuse at real APP SQL. Both synthetic tenants' linked history backfilled through restricted migrator without JSON/hash/metadata change or disabling RLS; ledger remains46. Existing independent synthetic source-erasure API assertions run while table/hooks active and source-read grant still active: source bytes erased, official/audit assertions preserved, diagnosis disclosure404, original links/history retained. Actual reminders and pinned exports run under active candidate. Separate46 release/threat units pass;280 executable pins stable.

Integrated erasure initially failed503 because existing privacy blob discovery cast an unrelated malformed Evidence upload_id directly to UUID. `privacy.py` now validates targeted/shared selectors inside CASE before cast, preserving valid shared-blob logic. Raw failure and parameterised SQL error retained; no malformed-source test weakened or history rewritten. Earlier101 and104 passing scopes remain separate. Receipt: `docs/evidence/candidate-0.40/typed-linkage-candidate-20261011/LINKAGE-CANDIDATE-RECEIPT.json`. Candidate removed after experiment; cluster stopped; historical evidence intact.

Separate self code/evidence review, IR-0.40-10 unconfirmed, no human signoff. Positive supported diagnosis-removal cleanup, invalid populated upgrade/rollback and checksum-ledger registration/retry/recovery remain before migration promotion. No new diagnosis privacy target or approval waiver is supplied by hooks. Source cleanup races, selector UI/browser, integrated full refresh and external/financial/hosted/container/human/operational release gates remain.0/50 delivered; no next feature/export/deploy/spending.


## Optional diagnosis Evidence selector UI — 11 October2026

Optional saved Evidence selection is implemented in the existing diagnosis worksheet. Up to5 canonical exact object/revision pairs supplement mandatory notes; older notes-only payloads keep absent reference fields. Bounded current-authority metadata pages replace one another; source GET before selection refuses changed versions. Picker generations invalidate on edit/switch/install/save/read loss; Evidence capability participates in session/tenant keyed remount. Pending uncertain diagnosis saves retain exact bytes. Default roles/profiles/ceilings unchanged.

Actual component-adapter10 passed separately from rebuilt native PostgreSQL/Chrome browser9 groups/295 assertions and8 automated axe scans. The mounted run adds2 no-Evidence-capability assertions; positive selector browser/HTTP qualification remains pending. First browser served stale built assets and failed new note assertion, retained then fixed by rebuilding without weakening it. Final source/assets stable; runtime stopped; intentional transport faults retained. Separate code/evidence self-review does not supply human approval. Typed-linkage cleanup and registered upgrade/recovery, source races, integrated refresh and external/financial/hosted/container/human/operational release gates remain. Build0.40/domain1.30/schema46 unchanged;0/50 delivered, no next feature/export/deploy/acceptance.

Evidence: `docs/evidence/candidate-0.40/evidence-selector-ui-20261011/UI-RECEIPT.json`.
