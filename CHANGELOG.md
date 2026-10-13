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


## Linked Evidence selector native browser — 11 October2026

Actual native PostgreSQL/Chrome browser qualification now includes linked saved Evidence selection: changed source version refuses rather than silently repinning; keyboard selection of the fresh version, save/readback/reload, completion and correction retain exact selectors. Current and historical API reads refuse404 after the fresh object-only synthetic source-read fixture grant narrows; the subsequent browser refusal clears diagnosis/source details with no domain effects. This is synthetic fixture preparation, not governed grant-flow, default permission widening or human signoff.

Final10 groups passed/316 assertions, zero failed/not-run;9 automated axe scans zero violations/incomplete findings. All360 source pins, served assets and46 applied migration bytes stable; cleanup succeeded and all3 clusters stopped. Two new-test failures remain raw: expected200 versus actual create201; then browser listener caught an earlier authorised correction readback200 while both fresh API reads already refused404. Corrected the new contract assertion and waited for actual readback before observing narrowing; no product authority weakening or old test changed. Intentional transport/refusal failures remain recorded.

Positive selector browser/HTTP duty is locally qualified. Typed-linkage lifecycle/registered upgrade/recovery, source privacy/retention races, integrated full refresh and required external/financial/hosted/container/human/operational release gates remain. Build0.40/domain1.30/schema46;0/50 delivered/deployed, no next feature or remote action. Code/evidence reviews are separate self-review phases. Evidence: `docs/evidence/candidate-0.40/evidence-selector-browser-native-20261011/POSITIVE-SELECTOR-RECEIPT.json`.


## Populated linkage candidate upgrade — 11 October2026

Actual restricted impact_migrator qualification against populated schema46 now proves the sealed unregistered linkage candidate preserves valid two-tenant Draft/Completed/correction JSON/hash/metadata/head, worker fences and ledger, and creates exact per-version typed links. Six malformed current/older-history cases each refuse twice: duplicate current selectors, extra field in older Completed, missing older revision, wrong current object, wrong older kind and actual foreign-tenant older source. Every failed transaction leaves no candidate table/functions/triggers/CHECK and keeps history/ledger byte-exact. No historical row rewritten; synthetic invalid payloads are seeded before application.

Native10 passed, zero failures/errors/skips:7 added candidate-upgrade cases plus3 retained actual registered45-to46 upgrade cases. All281 executable pins and sealed SQL exact; disposable databases dropped with absence assertions and cluster stopped. Valid candidate reapply refuses DuplicateFunction without history changes; this is explicitly not registered checksum-ledger no-op retry. Source/evidence self-review phases do not supply independent human approval.

Unregistered populated rollback gate is locally qualified. Positive supported diagnosis-removal cleanup, active registration/checksum/retry/recovery, source privacy/retention races, integrated refresh and actual external/financial/hosted/container/human/operational release gates remain. Build0.40/domain1.30/schema46;0/50 delivered/deployed, no next feature or remote action. Evidence: `docs/evidence/candidate-0.40/linkage-populated-upgrade-20261011/POPULATED-UPGRADE-RECEIPT.json`.


## Actual source-erasure lock qualification — 11 October2026

US-DX-01a / APL-361 remains the sole active story. New native case wraps the unchanged existing independent member Evidence erasure test: subject-active refusal, plan/hash, seven-store execution, blob removal, audit and official-number assertions remain intact. A restricted-migrator disposable delay-only trigger pauses removal of one fresh Evidence source while the real API holds the tenant lock. PostgreSQL observes8 actual APP advisory waits: the erasure plus seven diagnosis routes. After actual erasure commits, current/named/history/create/complete/exact retry refuse404 RESOURCE_UNAVAILABLE; listing filters the linked diagnosis. Source-read fixture grant remains active throughout, so removal causes denial. Exact diagnosis JSON/bindings persist; no diagnosis registry/revision/receipt effects.

Two actual affected native runs each124 passed, zero failures/errors/skips; one new case plus123 retained cases, not seven stories. Final run strengthens no-effects and temporary delay-function absence assertions. All281 executable pins, sealed linkage candidate and46 applied migration bytes stable. Temporary trigger/function and linkage candidate removed; clusters/API stopped. Receipt: `docs/evidence/candidate-0.40/source-erasure-race-20261011/ERASURE-RACE-RECEIPT.json`. Distinct root self code/evidence review; IR-0.40-14 remains unconfirmed and release passed=false.

Public privacy build_plan targets owned Evidence/ImportJob and member/invitation stores, with no AIDiagnosis target. This source-erasure proof does not qualify positive diagnosis-removal cleanup or invent an approved plan entry. Supported diagnosis-removal scope/contract, linkage registration/checksum retry/recovery, current-head full integration and external/financial/hosted/container/human/operational/owner release gates remain.0/50 delivered/deployed; no next feature, remote export, deployment or spending.


## Unregistered linkage actual backup/restore — 11 October2026

US-DX-01a only. Actual custom pg_dump/pg_restore now runs with the sealed typed-linkage candidate table/functions/triggers active. Existing restore drill verifies golden official results, row counts, owner/RLS/policy/functions/grants and restricted APP fences. Exact diagnosis Draft/Completed/correction JSON/hash/registry/history/head and per-version links survive. Restored actual APP login is non-superuser/NOBYPASSRLS: own tenant sees exact links, unset/foreign tenant sees none. Population trigger creates one exact binding in a forced-rollback probe; wrong-kind reference refuses FK. Actual worker/platform/identity login-role table SELECT refuses InsufficientPrivilege. Restored database dropped with absence assertion; candidate hooks removed; cluster/API stopped.

Final125 native passed, no failures/errors/skips:1 new case plus124 retained affected cases.282 executable pins and sealed candidate/all46 migration bytes stable. Initial124 passed/1 new test-instrumentation failure retained: explicit rollback inside a transaction context corrected to force_rollback=True without weakening old assertions. Receipt: `docs/evidence/candidate-0.40/linkage-native-restore-20261011/NATIVE-RESTORE-RECEIPT.json`. Separate root self code/evidence review, IR-0.40-15 unconfirmed.

This locally qualifies unregistered candidate database backup/restore; registered schema remains46. Existing46 checksum/no-op verification is not candidate registration/checksum retry. No replacement restored API, uncertain-command replay, diagnosis-removal cleanup, full current-head suite, hosted/container/human/operational acceptance or deployment is claimed. Positive supported cleanup/contract, promotion and API recovery/release gates remain.0/50 delivered/deployed; no next feature, remote export or spending.


## Replacement restored linked API — 11 October2026

US-DX-01a only. Actual custom pg_dump/pg_restore now qualifies a replacement uvicorn API with the sealed unregistered linkage candidate active. Only restored APP/IDENTITY/PLATFORM DSNs in a private0600 config and a minimal sanitized environment reach the API; fixture/migrator/worker DSNs, login passwords, PG overrides and provider keys do not. Existing unchanged capture/verify diagnosis recovery assertions run with linked synthetic Evidence input: exact Draft/Completed/correction reads/history/named versions and create/complete/revise receipt replay,3revisions/3receipts/3audits, changed-body same-operation409 and no extra effects. They pass both before and after an actual API process restart.

Only copied fresh object-source grant narrows under tenant lock; restored current/history/named reads and all3 original exact receipt retries refuse404 RESOURCE_UNAVAILABLE with no diagnosis revision/receipt/audit effects. Original API still passes the unchanged exact recovery assertions, establishing restored-copy isolation. This is synthetic purpose narrowing, not governed revocation or live-provider identity proof. Both replacement processes shut down cleanly; copy drops with absence assertion; candidate hooks removed and clusters stopped.

Two affected native runs each126 passed, zero failures/errors/skips:1 new case plus125 retained. Final283 pins match the exact formatted test and all46 applied migrations/sealed SQL unchanged. Separate root self code/evidence review; IR-0.40-16 unconfirmed. Receipt: `docs/evidence/candidate-0.40/linkage-restored-api-20261011/RESTORED-API-RECEIPT.json`. Candidate remains unregistered at schema46; this closes bounded restored API/restart/retry qualification, not candidate checksum registration/recovery after promotion, supported diagnosis-removal cleanup, current-head full suite, hosted/container/human/operational acceptance or deployment. Those gates remain;0/50 delivered/deployed, no next feature, external export or spending.


## Current executable full native integration — 11 October2026

US-DX-01a only, tested head1a47253d52297e68e61de3124f809e59835b89ea. Full native application/reference suite2609 passed,28 skipped,1 existing configuredIT018 deselection,1 warning;0failures/errors. Every skip reason saved, including separate provider/pooler/historical HTTP/restored-mode/database-restart modes. Two native API restart phases pass separately; real generic pg_dump/pg_restore compares192tables/114470rows with exact security/official golden checks; actual restricted migration45-to46 upgrade passes. Newly added linkage/source-erasure/restored-API cases run within full suite as well as retained focused receipts.

All283 executable pins and46 applied migration bytes stable. Candidate linkage stays unregistered, fixture hooks removed, copy databases removed, API/cluster stopped. Nine generated historical evidence artifacts restored byte-exact; actual new observations saved separately. Receipt: `docs/evidence/candidate-0.40/current-head-native-full-20261011/FULL-NATIVE-RECEIPT.json`. Separate root self code/evidence review, IR-0.40-17 unconfirmed; no accepted requirements or human signoff.

Current code full native integration gate is locally qualified. Supported diagnosis-erasure target/contract and positive relation cleanup, candidate registration/checksum/recovery, current-head browser/live-provider and required container/hosted/export/financial/human/operational/owner release gates remain. No next feature, remote export, deployment or spending;0/50 delivered/deployed. Prior focused/full runs below/above remain their own dated scopes.


### 0.40 local qualification follow-up — 11 October 2026

Registered schema47 diagnosis regression: 2,626 native pass / 28 explicit skips, real restore/upgrade and separate database outage, provider18 and browser10/318 pass at79b2316. Bounded deployment writer stop/probe/fail-closed private checkpoint added for local qualification; external-writer maintenance and actual container/hosted/human gates remain. No deployment or story acceptance.


## 11 October 2026 — locked-ledger deployment refusal qualification

A real surviving native PostgreSQL client held an ACCESS EXCLUSIVE lock on the migration ledger. The previous deployment probe waited for that ledger before refusing the already-observed client; the retained reproduction killed the blocked child after two seconds. The probe now refuses other client/prepared counts before reading the ledger and applies transaction-local 10-second statement and 2-second lock timeouts in its read-only transaction.

Actual source-pinned PostgreSQL qualification verifies prompt locked-client refusal, ledger read after release, real statement-timeout failure with redacted output, and a successful fresh transaction after rollback: four observations; cluster stopped. Actual deployment helper/orchestration and retained deployment regression tests:127 passed, zero failures/skips. Initial sandbox/collection failures remain preserved. Separate supporting code review found no introduced defect; independent evidence review is recorded in the receipt when complete. See `docs/evidence/candidate-0.40/deployment-lock-refusal-20261011/LOCK-REFUSAL-RECEIPT.json`.

These are local candidate checks. External writers still need an accountable maintenance operator to keep them disconnected. Container behavior, exact-head hosted CI, financial/public-export authority and existing release/human gates remain held. Automatic review rejected the earlier public GitHub feature-branch export; the explicit public-export and paid-CI questions remain pending. No remote deployment occurred;0/50 delivered. Earlier receipts and all applied migration bytes remain unchanged.


## 11 October 2026 — diagnosis retained erasure after backup restoration

Actual independent privacy HTTP approval/execution precedes the backup. A real PostgreSQL dump/restore and restricted replacement API preserve three removed payloads, immutable revision metadata, zero diagnosis Evidence bindings, unchanged source Evidence, and scoped deletion ledger/completed actions/audit/receipts. Current/history/three named reads refuse404; the exact privacy execute retry returns the original receipt with unchanged scoped durable rows.193 tables/8,054 rows,47 migration checksums/security/official result checks pass; copied API/database and owned cluster stopped.131 affected native checks pass (one new +130 retained), zero failures/skips, exact working-test pins stable. Separate supporting code review found no concrete defect; evidence review recorded separately.

Receipt: `docs/evidence/candidate-0.40/diagnosis-post-erasure-restore-20261011/POST-ERASURE-RESTORE-RECEIPT.json`. Backup is AFTER erasure: TH27 pre-erasure backup replay remains open. This adds no deployment/human acceptance or new full-head hosted CI credit;0/50 deployed. Earlier receipts, original criteria and all applied SQL remain byte-exact. Public export/spending/release/operator gates remain held.


## 11 October 2026 — erased-target receipt and list guards

Actual HTTP create/complete/revise receipts were captured and verified before independent privacy erasure. Only the new synthetic object owner_id was attributed to the privacy subject under the tenant lock; all other registry fields and immutable history were unchanged. This is explicit fixture preparation, not a governed ownership-transfer claim. The original author stayed active and authorised, so post-erasure404s test removed-content guards rather than revoked identity.

131 affected native tests pass (one new +130 retained), zero failures/skips: three exact original command retries and three generic operation lookups refuse404, current/history/three named reads refuse404, listing succeeds while filtering the target, changed-body retry remains409, original private receipts and three revision/receipt/audit counts stay exact. Notes-only diagnosis has no bindings; this case does not earn linked-cleanup credit. Existing linked erasure evidence remains separate. Native fixture/cluster stopped; exact source pins stable. Receipt: `docs/evidence/candidate-0.40/diagnosis-erased-receipts-20261011/ERASED-RECEIPTS-RECEIPT.json`. No backup/TH27, hosted CI, human approval or deployment claim;0/50 deployed.


## 11 October 2026 — native pooler queue and restored-clone harness qualification

189 affected native checks pass with one retained database-restart skip;43 separate units pass (25 new,18 retained). The original failed pooler run remains preserved:184 pass/one failure/one skip because a barrier expected eight backend waiters behind a three-server pool. The repaired test proves three real advisory waiters plus five actual queued PgBouncer clients, all eight unfinished, then retains the original privacy outcomes. Five separate direct native regressions pass with zero skips, including the unchanged eight-backend branch.

Restored clone connections now use separately retained direct restricted logins, while the original API/worker stay pooled. Clone-only credentials are stripped from the original API environment; actual process isolation passes. Three real clone cases verify schema47,all47checksums,193 tables each, exact row comparisons/security/official arithmetic and retained history/receipts/source-loss/after-erasure behavior. Restored APIs are direct, not pooled. Backup after erasure does not close TH27. The linkage dump artifact retains its pre-finally dropped:false observation; passing test subsequently checks actual removal.

Both successful native runs stopped safely with298 stable source pins, no historical evidence changes. Separate code review corrected a missing test-only process ID before execution; evidence review remains distinct. Receipt: `docs/evidence/candidate-0.40/diagnosis-pooler-harness-20261011/POOLER-HARNESS-RECEIPT.json`. Application/API/SQL and frozen criteria unchanged. These are affected local checks, not a new full-head suite, required hosted CI, container, human signoff or deployment;0/50deployed. Public GitHub export and paid-CI questions remain pending after automatic approval review rejected the feature-branch export.


## 11 October 2026 — exact committed native pooler regression and recovery

Clean tested head `0ed0c5bdb2fb65aba0b8babe31253c495aa3653b`:2,690 passed,24 skipped,one retained IT_018 deselection and one Starlette/httpx warning;zero failures/errors. Actual PostgreSQL17.10/PgBouncer1.26.0 transaction pool size3. Two separate API restart phases each pass; real backup/restore compares193tables/117,676rows with zero differences,47migration checksums/security/official arithmetic intact and copy dropped. Populated restricted45→47 upgrade passes while preserving509revisions across two tenants. Restored APIs remain direct restricted connections; this is not pooled restored API evidence.

A separate owned pooler database outage case passes with zero skips:12.8s actual downtime; original API/worker remain alive, readiness/read/write refuse retryable503, then recover with old receipt intact and exactly one receipt/revision after the refused write is retried twice. First503 readings took5.3s; no latency acceptance or midtransaction crash claim. Main24skips remain unchanged. Both runs stop safely;298source pins each stable,all9historical evidence files restored byte-exact,distinct supporting evidence review complete. No application/API/SQL/criteria change in this evidence batch.

Receipt: `docs/evidence/candidate-0.40/native-pooler-full-20261011/FULL-POOLER-RECEIPT.json`;raw XML/logs/restore/upgrade/skip inventory and safe API phase XMLs preserved, private cookies/configurations/dumps excluded. This adds local full-selected native pooler evidence, not required hosted CI, container, pooled provider/browser, human acceptance or deployment.0/50deployed; public-export and paid-CI questions pending, current release/human/operator gates unchanged.


## 11 October 2026 — live provider through native transaction pooling

Clean tested head `c7a55b18ee33d7df095c7a193b53e146c6c62fec`:actual local Keycloak26.7.4/native PostgreSQL17.10/PgBouncer1.26.0 qualification passes18tests with zero skips/failures/errors. Real provider authentication/token validation, no authority from provider role claims, diagnosis create exact retry/changed-body conflict/completion/history, tenant/capability refusal and captured old-cookie logout refusal pass. Separate review verifies actual transaction pooler size3/API runtime ports and297stable source pins. Services stopped;two historical IdP evidence files restored byte-exact. Generated metadata's older PGlite edition stays historical.

First preparation failed before services/tests due a wrong helper source filename; exact failed wrapper/observation retained,generated newly owned private bootstrap file removed,older unrelated file unchanged. Receipt: `docs/evidence/candidate-0.40/provider-pooler-20261011/PROVIDER-POOLER-RECEIPT.json`. HTTP cookie/provider flow is not Chrome/TLS/human acceptance. API intentionally retains narrow provider provisioning configuration; no blanket no-provider-credential claim.

Separately reviewed runner change permits transaction pooling only for native test or native ai-diagnosis-browser; development,other browser and nonnative modes stay refused. Eight actual CLI tests plus43retained units pass (51total), no runtime from unit checks. Browser mode starts no worker. Actual pooled Chrome check remains next, not passed. Application/API/SQL/criteria unchanged; earlier full native2690pass24skip stays pinned0ed0c5b. No hostedCI/container/publicexport/paidCI/humanacceptance/deployment;0/50delivered.


## 11 October 2026 — actual diagnosis browser through transaction pooling

Clean tested head `37de5a1800e897bf1a7d8041296ca8bdd24732de`:Chrome154.0.8037.98/native PostgreSQL17.10/PgBouncer1.26.0 passes10groups/318assertions. Real keyboard save/reopen,completion/correction/history,stale edits,actual committed-response loss/exact-byte retry without duplicate effects,current access loss/delayed-response clearing,signout/tenant/session isolation,and actual Evidence picker/version conflict/pinned history/source-purpose loss all pass.395external/375browser source pins,5servedasset hashes and47migration checksums stable; separate reviewer verifies actual pooler mode3/API ports.

Nine scoped automated axe scans record zero violations/incomplete findings. Uncaught errors/external requests/forbidden requests/cleanup failures are empty;47recorded transport failures remain in raw evidence (46aborted requests,one intentional connection failure). Never claim zero network failures. All owned services stopped;no historical evidence changed. Receipt: `docs/evidence/candidate-0.40/browser-pooler-20261011/BROWSER-POOLER-RECEIPT.json`,rawJSON/logs and four synthetic PNGs. Source review and evidence review distinct; no code/assertion changes in this preservation batch.

Browser uses development fixture authentication,not actual Keycloak UI;provider18-case integration remains separately pinnedc7a55b1. Browser starts no worker;outbox is intent. Source-grant narrowing is not privacy erasure. Private-response headers/cache behavior are not proven by this browser run. No human/accessibility acceptance,hostedCI/container/publicexport/paidCI/deployment;0/50delivered. Original fullnative2690pass24skip pinned0ed0c5b remains unchanged.


## Diagnosis private HTTP headers — 11 October 2026

One additional actual native PostgreSQL/PgBouncer HTTP case passed with zero skips/failures/errors. It retains real response objects for create, current/list/history/named revision, exact retry, changed-operation409, current read-grant loss404, unauthenticated401 and missing404: no-store, nosniff, no-referrer, permissions restrictions, three CSP directives and valid/echoed correlation UUIDs pass; refusal bodies omit private title/notes and domain counts stay unchanged. Tested base `7b75d265c7c1c95887dfa939b2787b495ae97ae5` plus the new test bytes pinned in the [private-header receipt](docs/evidence/candidate-0.40/private-headers-native-20261011/PRIVATE-HEADERS-RECEIPT.json); 300 source pins stable, runtime exit/cluster stop0, historical evidence unchanged. The first sandbox bind refusal occurred before any tests/services and remains separate evidence. Notes-only development bearer authentication and fixture grant narrowing: no linked-source/erased-target headers, browser cache eviction, TLS/HSTS, actual provider session, governed revocation or deployed-header claim. Earlier full/provider/browser runs retain their separate source heads. No next feature, hosted/container/human acceptance, remote export or deployment; 0/50 delivered.


## Real-provider Chrome diagnosis — 11 October 2026

Optional combined local integration qualification passed: one native pytest case, three actual Chrome groups and45assertions, zero failures/errors/skips. Baseline `d2cb26f932bb96dc3264ca50ec2c6202f4461468` plus exact two new test/checker source hashes;398pins stable. Actual cached Keycloak26.7.4 password/TOTP, Chrome154.0.8037.98, PostgreSQL17.10 andPgBouncer1.26.0 transactionpool3; development authentication disabled. Realadmin UI save/reopen/complete preserves notes/order; logout endsprovider session (`prompt=none` returnslogin_required), oldcapturedcookie read/exactcreate retry return401, and authentic delayed200 actually delivered afterlogout cannotrestore privateDOM/storage. Realowner login obtains no diagnosis access fromcustody: UI absent and GET/POST404. Independent read-only native target counts remain2revisions/2receipts/2audit with exactDraft/Completed payloads.

[Actual provider-browser receipt](docs/evidence/candidate-0.40/provider-browser-native-20261011/PROVIDER-BROWSER-RECEIPT.json) separates rawJUnit/JSON/logs/sourcehashes and distinct supporting code/evidence review. Owned API/provider/pooler/cluster stopped;one historical IdP JSON restored byte-exact. No runtime, API, UI, SQL, existingchecker, originalcriterion, grant/profile or productionaccount change. The new optionalcase is explicitly gated/skipped in default modes; a skip is not pass. This does not rerun earlier18provider cases/318browserassertions/fullnative2690, or supply Evidence/erasure/axe/TLS/human/container/hosted/deployment acceptance. No nextstory or remoteexport/merge;0/50delivered.


## 12 October 2026 — staging CI browser schema-oracle repair

PR96 candidate `d165ef0` passed checks, live identity provider and fresh container-stack; its browser job failed on an obsolete schema43 expectation against actual schema47. Native qualification was still running at this repair checkpoint. Three affected browser checkers now require the exact registered migration count, contiguous applied version sequence and every source checksum, retaining runtime/build/authority and start/end unchanged-source assertions. No product/API/migration/criterion changes.

Actual local Chrome/PGlite runs pass all14 enablement,16 saved-review and16 plan-export groups, separately source-pinned. Initial local attempt failed because the helper required checkout-local `.venv`; a temporary link to the existing installed environment was used for the retry and removed afterward. Historical evidence unchanged; no installation or paid local resource. Separate code/evidence review is not human signoff. Receipt and raw synthetic browser JSONs: `docs/evidence/candidate-0.40/browser-schema-repair-20261012/`. Revised bytes require fresh exact-head hosted qualification; previous job results do not qualify the repair. Staging not deployed; current human/operational/populated-promotion gates remain held.


## 12 October 2026 — remaining walkthrough and extension schema-oracle repair

Hosted PR96 at `a3d96a6` passed the first repaired browser modes, then stopped at a separate walkthrough schema43 assertion. Full browser-source search identified walkthrough and extension as the remaining stale owning-schema43 checks. Both now verify the bounded exact current source inventory, contiguous applied versions, every SQL checksum and unchanged inventory at completion. Walkthrough additionally includes every SQL byte in its start/end source pins. No product/API/migration/criterion change.

Two actual local Chrome/PGlite runs pass16 walkthrough and28 extension groups with stable checker hashes and unchanged historical evidence. Temporary existing-environment link removed after execution. Separate code/evidence reviews do not constitute human acceptance. Receipt/rawJSONs: `docs/evidence/candidate-0.40/browser-schema-repair-second-20261012/`. Prior failed hosted result remains preserved; revised bytes need fresh exact-head required CI. No merge/deployment or next story; populated promotion and human/operator gates remain held.


## 12 October 2026 — native CI setup and lease-takeover qualification

PR96 at `e020eeb` passed checks, browser/reference, live identity provider and container-stack. Its native full suite retained four failures:2691passed/29skipped/one deselection/one warning. Three diagnosis clone restore tests required `IMPACT_PG_BIN` before the suite, but the workflow installed matching PostgreSQL17 clients afterward. The existing fingerprint-verified client step now precedes the suite and the native job exposes its matching binary directory. No restore test skipped.

The fourth failure sent all six messages once but did not observe fast-worker takeover (all generations1). A bounded private test-only driver pauses the original slow worker BETWEEN committed sends. Parent proves exactly1SENT/5LEASED owned by slow, then the normal fast process takes over through actual database-clock lease expiry. Original no-duplicate, generation, fast-sink and stale-refusal assertions remain; production worker/lease SQL unchanged.

Actual owned PostgreSQL17.10 checks: first12native cases pass (three clone restore cases plus full worker file); after adding a safe takeover report, four exact formerly failed cases pass separately, zero skips/failures/errors. Final report shows1slow/5fast sends,6unique/6total, remaining five generations2 and allSENT.302source pins per run stable, clusters stopped and historical evidence unchanged. These runs retain separate source hashes and are not a new combined full-suite count. Prettier YAML round-trip/syntax check and Ruff pass; optional PyYAML parsing was unavailable and earns no pass credit. Evidence: `docs/evidence/candidate-0.40/native-ci-repair-20261012/`. Fresh exact-head required hosted CI and current human/operator/populated-promotion gates remain pending; no main merge or staging deployment.


## 12 October 2026 — committed-send readiness repair

Hosted PR96 at `6d6faa0` passed checks, browser/reference, live identity provider and container-stack. Native full-suite result:2694passed/1failed/29skipped/one deselection/one warning. All three diagnosis clone restore cases now pass. The remaining worker test announced readiness after a target handler returned without a committed send (zero SENT rows); no underlying handler exception class is claimed.

The test-only barrier now requires the target handler to increment the sent counter, which occurs only after its fenced database transaction commits. A30-second preparation lease accommodates loaded execution; the controlled between-message pause still causes actual database-clock expiry. Exact1SENT/5LEASED before fast start, real takeover generation, fast sink, six unique sends and stale slow-worker refusal remain required. No production worker or migration byte changed.

Actual owned PostgreSQL17.10 execution: all9native worker cases pass, zero failures/errors/skips,302source pins stable. Safe report proves1slow/5fast sends,6unique/6total, five takeover generations2. Owned cluster stopped; historical evidence unchanged. Initial sandbox loopback refusal ran zero tests and is preserved without pass credit. Separate code/evidence review does not supply human signoff. Evidence: `docs/evidence/candidate-0.40/native-committed-send-repair-20261012/`. Revised bytes require fresh exact-head hosted CI. No staging deployment, main merge or next story; human/operator/populated-promotion gates remain held.


## 12 October 2026 — bounded dispatch-only scenario preparation

Hosted PR96 at `d236809` passed checks, browser/reference, live identity provider and container-stack. Native full suite again retained2694passed/1failed/29skipped: committed-send readiness now produced one SENT, but only three target rows were LEASED rather than five. Other target states and exact background cause were not observed. Source inspection shows run_once dispatches before scheduling reminders, so using it as a drain can leave new eligible deliveries.

Before creating the six target invitations, the test now runs bounded original Worker.dispatch calls for the target synthetic tenant, reading the exact real claim predicate until zero eligible deliveries. After creation it requires the eligible event set to equal the six target IDs. No claimed rows, timestamps, retries, reminder/audit/export history, lease SQL or production worker changed. This observation is not a durable future-writer/eligibility fence; unchanged strict readiness/ownership/takeover/unique-send/stale-refusal assertions still catch interference.

Three actual native runs each pass9worker cases, zero failures/errors/skips,302stable pins; run5 predates formatting, run6 precedes the explicit interference fixture, and run7 pins final bytes. Run7 creates two unrelated normal synthetic invitations and requires original dispatch to send both before creating the target six; this exercises the preparation path without inflating the nine-test count. Each run proves1slow/5fast sends,6unique/6total, five generation2 takeovers and stale refusal; owned clusters stopped. Initial format-check failure retained and corrected. A new evidence folder created during run6 was separated by its historical-evidence wrapper and restored from those exact new bytes; original tracked evidence unchanged. Separate code/evidence review is not human signoff. Evidence: `docs/evidence/candidate-0.40/native-dispatch-preparation-20261012/`. Fresh final-head hosted CI remains required. No main merge/staging deployment or nextstory; human/operator/populated-promotion gates remain held.
