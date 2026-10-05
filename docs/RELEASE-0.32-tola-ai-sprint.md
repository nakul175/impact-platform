# Tola + AI sprint: access extension and saved guidance

5 October 2026 · Build 0.32.0 · domain API 1.23.0 · platform API 1.10.0 · schema 37.

**Qualified as a bounded local review checkpoint.** Final source and verification fingerprints are recorded in [the local summary](evidence/sprint-0.32-local-summary.json). It does not record a merge, deployment, owner acceptance or production qualification. The starting review source is build 0.31.0 at `5c6c761bf670b371a2d360f6c6e08ec727395568`. The eight-hour development window is 08:27:26–16:27:26 UTC / 13:57:26–21:57:26 IST; it is a work window rather than a complete-platform delivery promise.

## Resulting behaviour

An existing organisation can propose an extension from its last applied access profile to the currently registered profile. The owner proposes the exact extension, the named second administrator accepts it, and a current platform operator who is a different natural person from both approves it. The new console shows additional capabilities, the target role templates, the current expiry and the review deadline. No organisation is upgraded automatically.

Every newly saved AI adoption-plan revision retains the exact available learning/adoption guide, tool directory and manual-practice guide. A read-only saved-guidance viewer lists actual saved revisions and opens the wording captured for one exact revision. Changing the displayed revision leaves the editable plan and learning progress unchanged. Historical supplier terms remain historical; users must confirm current terms directly with the supplier.

The local sprint dashboard polls actual saved workstream files every five seconds. It shows ETA ranges and confidence, actual deliverables, evidence, blockers, stale-source warnings and the remaining work window. It does not turn elapsed time or partial requirements into a completion percentage. Its consolidated index assigns the existing 307 core requirements and 40 AI feature areas to 14 shared domains without changing the original registers.

## Access and database boundaries

Migration `0036_reviewed_ceiling_widening.sql` adds tenant-fenced review records, a one-use applied marker and a narrow ceiling applicator. It also registers the exact generated deployment access profile in immutable control-plane metadata. Runtime roles cannot write that profile registry. An unregistered target cannot be applied; later profile changes need an additive migration that registers the reviewed profile.

The proposal pins the exact existing authority rows, grant and membership revisions, managed role heads, organisation/owner revision and target profile hash. Relevant changes invalidate consent. Authority renewal and access extension cannot be pending simultaneously. Approval preserves current expiries, revoked old ceiling capabilities, prior role capability omissions and retired or missing managed templates. Custom roles are not overwritten. Only the newly introduced capability delta is added. The applicator independently checks profile registration, monotonic widening and the source baseline.

The upgrade inbox and scoped directory use signed 15-minute cursors bound to the current identity, route, tenant/global scope and visibility. Current operator authority or current nominated administrator authority is checked on reads, writes and receipt replay. Historical nomination alone cannot authorise a later read or retry. Approval, role/grant revisions, the applied marker, policy epoch, platform event and receipt commit atomically; a failed application rolls the transaction back.

Migration `0037_ai_content_snapshots.sql` adds insert-only guidance bundles and revision bindings with composite tenant keys and forced row security. Application-role access is SELECT/INSERT only. Guidance reads recheck current scoped plan authority before loading the exact available revision. Stored payloads use a retained closed archive schema and verified canonical content digest. A guide edition cannot silently change wording within the tenant; new wording needs a new edition. Non-unique edition lookup indexes support this check under the existing tenant write lock.

Older revisions without an actual archive answer `UNAVAILABLE`. When an older client retains a worksheet from another practice edition, the new revision reuses only a real matching archived practice guide; otherwise that component is explicitly unavailable and the bundle is `PARTIAL`. Current wording is never used to reconstruct missing historical text. Exact receipt replay writes no additional archive, revision, audit event, outbox intent or receipt.

## Supporting local operations

The sprint also addresses existing Mac backup/restore qualification failures caused by differences between GNU and BSD command-line tools. The production backup-set layout, checksums, atomic replacement, disk guard, weekly hard-link retention and UTC scheduling semantics must remain unchanged. All 61 focused operations checks pass, and the complete native and PGlite regressions resolve the seven previously recorded Mac failures. Focused operations checks use synthetic temporary backup sets and stub clients; the separate actual native backup/restored-database drill also passes. No deployed backup or restore is performed.

The live tracker is a development-support tool, separate from the organisation-facing product. It binds only to loopback, accepts the exact local host/port, serves a fixed asset/status allowlist and provides no write endpoint or credential/database integration. Atomic local updates follow one writer per workstream. See [tracker operation and evidence](development-tracker/README.md).

## Contract and implementation scope

The domain API adds exact-revision guidance and bounded revision history, increasing implemented domain operations from 243 to 245. These use existing `ai.enablement.read`; plan saves still use `ai.enablement.manage`. The control-plane API adds the global upgrade inbox, per-tenant upgrade list/preview/proposal and four review decisions. The generated onboarding profile is unchanged by these two read operations.

The original proposed edition 1.0 BRD, FSD, HLD, LLD, wireframes, requirement register and 108 specified case statuses remain at their stated baseline. This release is an implementation appendage. No specified case or requirement is promoted to accepted solely because a similar automated check exists.

## Qualification and remaining work

The final actual PostgreSQL 17.11 suite passes **1,689 checks, with 26 explicit skips and one deselection**, using separately provisioned NOINHERIT, non-superuser runtime logins. **API restart (both phases), backup/restored database and populated schema 33→37 upgrade pass**. The focused access/archive suite passes 193 checks with no skips; those checks overlap the full suite. The first four role-activation fixture failures and the first full run's Linux-only restart-inspection failure remain recorded. Their corrections preserve runtime permissions and assertions.

The full PGlite regression passes **1,633 checks, 82 explicit skips and one deselection**, with zero errors/failures. All seven historical Mac operations failures are resolved. PGlite and native counts overlap and must not be added together. Prepared, unwired 0.33 cases are excluded from both checkpoint suites.

Thirteen integrated Chrome workflow groups pass against the final product source. Seven axe scans report zero violations/incomplete findings; no uncaught JavaScript errors, unexpected console errors, external/provider requests or paid calls occur. The tests label their synthetic legacy setup and deliberately dropped/aborted responses. Seven retained desktop/mobile captures have been visually reviewed. Automated scans do not constitute full accessibility conformance or nonprofit UAT.

The supporting live tracker passes **42 offline checks and 15 browser groups**, with two clean automated scans. A refreshed unknown-ETA browser fixture needed to mark its synthetic stream as active after the actual stream completed; its first refresh failure is retained. These tracker checks are separate from product gates.

Named final evidence: `sprint-0.32-full-native-qualification.json`, `sprint-0.32-full-native-tests.xml`, `sprint-0.32-native-restart-phase_1.xml`, `sprint-0.32-native-restart-phase_2.xml`, `sprint-0.32-full-native-restore-drill.json`, `sprint-0.32-full-local-tests.xml`, `sprint-0.32-browser-tests.json` and `development-tracker/qualification-summary.json`. Static Python lint/format, TypeScript and Vite build pass; Vite retains the existing bundle-size advisory. The source/evidence manifest identifies the exact checkpoint contents, not later live workstream updates.

The private PostgreSQL 17.11 environment was built from the verified official source; environment preparation is recorded separately in `evidence/sprint-0.32-native-environment.json`. Local Mac qualification does not replace hosted CI, container qualification, the deployed identity provider, production operations, manual accessibility assessment or nonprofit acceptance. The original 307 core acceptance statuses and 108 proposed AI case statuses are unchanged. A separate next-increment diagnostic has reproduced three dashboard visibility gaps after current object restrictions change (target, collection plan and calculated result). The 0.33 fix is in progress; the green local regression does not establish complete security acceptance.

The operated marketplace, procurement awards, human advisory engagements, approved generated task runs, competency certification, live connectors, monetary/token budgets, AI-specific retention, purchasing and payments remain separate target work. Linking AI adoption outcomes to governed impact measurements is the next bounded development increment. No provider, supplier, spending or official-impact decision is performed by the changes described here. No paid provider request, paid CI run, external message or deployment is part of this local sprint checkpoint.
