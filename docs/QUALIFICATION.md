# Qualification record · v0.13.0

Executed on 28 September 2026 against the source on the release branch. These are development qualification results, not full product acceptance or production certification.

## Results

| Suite | Executed | Outcome | Evidence |
|---|---:|---|---|
| Application unit, contract and change tests | 119 | Passed | `evidence/application-tests.xml` |
| Core application live integration/security tests | 23 | Passed | `evidence/application-tests.xml` |
| Access administration live integration/security tests | 34 | Passed | `evidence/application-tests.xml` |
| Measurement configuration live integration/security tests | 21 | Passed | `evidence/application-tests.xml` |
| Period-governance live integration/security tests | 5 | Passed | `evidence/application-tests.xml` |
| Frozen-reporting live integration/security tests | 4 | Passed | `evidence/application-tests.xml` |
| Reviewed-exclusion/work-centre integration/security tests | 3 | Passed | `evidence/application-tests.xml` |
| Controlled-publication integration/security tests | 4 | Passed | `evidence/application-tests.xml` |
| Workspace administration and account integration/security tests | 15 | Passed | `evidence/application-tests.xml` |
| Tenant lifecycle integration/security tests | 14 | Passed | `evidence/application-tests.xml` |
| Reviewed initial access integration/security tests | 25 | Passed | `evidence/application-tests.xml` |
| Recovery-contact integration/security tests | 29 | Passed | `evidence/application-tests.xml` |
| Authority-renewal integration/security tests | 28 | Passed | `evidence/application-tests.xml` |
| Preserved API integration assertions | 17 | Passed | `evidence/application-tests.xml` |
| Preserved smoke assertions | 12 | Passed | `evidence/application-tests.xml` |
| Preserved design/reference tests | 143 | Passed | `evidence/reference-tests.json` |
| Rendered core browser workflows | 8 | Passed | `evidence/browser-tests.json` |
| Rendered access-administration browser workflows | 12 | Passed | `evidence/admin-browser-tests.json` |
| Rendered configuration, collection and work-centre browser workflows | 17 | Passed | `evidence/measurement-browser-tests.json` |
| Rendered period/reporting/publication browser workflows | 10 | Passed | `evidence/reporting-browser-tests.json` |
| Rendered workspace and account browser workflows | 10 | Passed | `evidence/workspace-browser-tests.json` |
| Rendered tenant lifecycle workflows | 7 | Passed | `evidence/tenant-browser-tests.json` |
| Rendered initial-access and first-programme workflows | 8 | Passed | `evidence/bootstrap-browser-tests.json` |
| Rendered recovery-contact workflows | 9 | Passed | `evidence/recovery-browser-tests.json` |
| Rendered authority-renewal workflows | 10 | Passed | `evidence/renewal-browser-tests.json` |
| Python lint/format, client formatting, TypeScript and Vite build | — | Passed | Reproduce with `make lint build` |
| Native PostgreSQL CI | — | Passed on GitHub Actions (first recorded native run) | `.github/workflows/qualification.yml`, run 36453508807 |
| Live external identity provider | — | Not executed | Required release gate |

The 353 application/API checks, 143 reference checks and 91 browser checks are distinct groups. Reference checks exercise the saved reference implementation, including future product concepts; passing does not imply those concepts are delivered. Counts are tests, not percentage requirement coverage.

One preserved test, **IT_018 (expired offline grant)**, is explicitly deselected because offline sync is not implemented. It is not counted as passed. The broader specification's unimplemented features and NFRs remain pending.

## Environment and limits

Application checks ran against a real HTTP FastAPI service backed by PGlite's PostgreSQL 17.5 engine and sixteen SQL migrations. Checks execute SQL, constraints, database roles, RLS, immutable revisions and transaction rollbacks. Final qualification uses fresh in-memory PGlite. Filesystem-backed runs in this managed filesystem intermittently produced EOF/page-consistency errors and were not counted as passing evidence. PGlite is a single-backend embedded engine. The runner serializes transactions; passing concurrent-request tests here does not qualify native PostgreSQL scheduling or production concurrency.

Browser checks used Chromium 153 through Playwright Core on Linux x86_64. They exercised the compiled React client and API across author/reviewer/partner, administrator/invited-member/owner, configuration, close/restatement, report-package, controlled-publication, tenant onboarding, recovery-contact and authority-renewal workflows. No uncaught page errors were recorded in the final runs. Screenshots show synthetic fixtures only; invitation tokens are hidden before capture. Responsive checks use a 390-pixel viewport without document overflow; this is not a complete accessibility audit.

## What the tests establish

- Custom roles are bounded by explicit delegation; system templates cannot be edited; revised/retired templates preserve previously approved assignments.
- Groups require natural-person-independent review, pinned role/member revisions and current delegation. Removal immediately eliminates derived access.
- Organisation reparenting rejects cycles and cross-tenant parents; moving to root clears the projection as well as the revision payload.
- Renewal removes old grants and requires fresh tenant authentication; ownership transfer requires the nominated successor and adds no data permissions.
- Preferences cannot edit identity; stale preference writes conflict. Session IDs do not expose secrets. Foreign-session revocation is hidden; global revocation blocks old bearer and cookie sessions; idle and CSRF checks apply. Exact configured provider assurance is required for fresh-assurance commands.

- Decimal inputs reject exponent notation, non-finite values, invalid precision and numeric JSON types. Pooled percentages use summed numerators/denominators. Storage and display precision are separate, and rounding is applied to the total.
- Tenant references are checked before successful mutation; failed commands produce no operation receipt. Direct app-role SQL cannot read another tenant or update an immutable revision.
- Forged role claims do not grant membership access. Unsigned, wrong-issuer, wrong-audience, expired, wrong-party and invalid authentication-time tokens are rejected.
- Purpose-restricted grants do not authorize general reads. Explicit object scope filters both detail and list queries. Restricted objects are hidden. Revoking the principal blocks replay of a previously successful command.
- Exact retries create one revision, audit record, outbox record and operation receipt. Changed payloads under the same operation ID conflict. Stale revisions cannot overwrite a newer head.
- Source-key collisions and conflicting source-key patches fail atomically. Unsupported disaggregation is explicitly refused.
- Submitted observations require an independent reviewer. Approval is bound to the exact candidate revision and attributed to the reviewer. A calculation after an 8/10 approval produces 59/120 = 49.17 on the fresh seed data, retains lineage, and becomes stale when a source changes.
- A close preview is generated on the server and pins every source, plan and result input. Missing, pending, invalid, rejected or unplanned sources block close; source drift after preview invalidates approval without partial official data. Successful close creates separate OFFICIAL revisions, copied lineage and a locked snapshot atomically.
- A locked programme-period rejects ordinary new submissions, corrections and recalculation. Independently approved restatement opens only named sources that belonged to the latest snapshot, expires within seven days and closes again when a superseding snapshot is created.
- Report submission reconciles the approved template, required sections/bindings, locked snapshot, official result membership, units and precision. Independent approval creates an append-only binding; deterministic export reloads only the pinned revisions, verifies its digest and escapes author text.
- Numeric narrative submission rejects unknown binding placeholders and bare numeric claims. Valid placeholders render from pinned approved results in semantic HTML and deterministic spreadsheet-safe CSV; Chromium confirms the report stylesheet is admitted only by its exact CSP hash.
- A controlled disclosure pins one approved report revision, declared purpose, bounded expiry and unique active recipients. Self approval is denied. Publication revalidates current recipients and authority, freezes immutable HTML/CSV artifacts and records a digest for each.
- Only a named current recipient can view the publication; CSV additionally requires that recipient's download flag. Expired, inactive, cross-tenant, unlisted and withdrawn access is hidden. Successful views/downloads append access events, while the app role cannot read the log or mutate artifacts.
- A reviewed plan exception retains the historical expected denominator, records reason/effective time, excludes the obligation from required completion and remains visible in coverage. All obligations cannot be excepted. A matching observation is excluded from numeric lineage with an explicit reason.
- Approved source/plan drift creates a principal-owned task and safe notice for affected provisional revisions. Another principal cannot enumerate or read them. Acknowledging a notice does not close the task; exact recalculation creates a replacement result, resolves invalidations and completes the task while the earlier result remains immutable and stale.
- Browser cookies are HttpOnly; missing CSRF is denied; logout invalidates the session. Duplicate JSON keys and oversized bodies are rejected. Tampered pagination cursors fail.
- Invitations require the verified intended identity, tenant, current issuer authority, scope and bounded expiry. Replay with a new operation fails; exact retry is stable while current checks pass. Reissue invalidates the earlier link. Raw invitation tokens and plaintext emails are absent from durable receipts.
- Scoped invitation grants filter actual programme reads; another tenant's object cannot be used to create a scope. Delegation expiry is enforced. Merely refreshing token issuance time cannot satisfy recent-authentication requirements.
- Role changes require an independent natural person other than requester and recipient. Another login belonging to the same natural person does not create independence. Changes to target membership invalidate the pending proposal.
- Suspension blocks current tenant access; reactivation requires a fresh sign-in, while old bearer/cookie authentication stays fenced. Revocation removes grants, preserves history and cannot be reversed through reactivation. Ordinary owner removal and owner-grant revocation are denied.
- Queued jobs are cancelled, running jobs are marked for cancellation, and active owned schedules are paused. Reactivation does not resume them. This does not qualify an actual worker or downstream cancellation.
- App-role SQL cannot manufacture custody or delegation ceilings. Generic PATCH cannot invoke administrative creates. Restarting fixture provisioning does not restore a revoked original administrative capability. Accepted cookie sessions immediately obtain the new workspace directory.

## Evidence files

- `application-tests.xml`: 353 passing pytest/unittest checks, zero failures/errors/skips among executed tests; one offline test deselected separately.
- `reference-tests.json`: 143 passing preserved reference assertions; product validation explicitly false.
- `browser-tests.json`: eight passing UI workflows and the uncaught-error list.
- `admin-browser-tests.json`: 12 passing access-administration workflows and the uncaught-error list.
- `measurement-browser-tests.json`: 17 passing configuration, collection, reviewed-exclusion and personal work-centre workflows, with no uncaught errors.
- `reporting-browser-tests.json`: ten passing period-governance, frozen-reporting and controlled-publication workflows, with no uncaught errors.
- `recovery-browser-tests.json`: nine passing nomination, consent, independent approval, replacement, revocation and mobile workflows, with no uncaught errors.
- `renewal-browser-tests.json`: ten passing authority inspection, proposal bounds, proposal, privacy, consent, server-side denial of a non-operator, independent approval, renewed expiry, withdrawal and mobile workflows, with no uncaught errors.
- `authority-renewal.png`, `authority-renewal-mobile.png`: approved renewal and history, visually inspected during this build.
- `recovery-contact-verified.png`, `recovery-contact-mobile.png`: approved contact and replacement/revocation history, visually inspected during this build.
- `measurement-setup.png`, `programme-readiness.png`, `collection-coverage.png`, `work-center.png`, `measurement-mobile.png`: rendered setup, readiness, coverage and recalculation-work evidence.
- `period-close.png`, `reporting-package.png`: programme-period status and independently approved internal package evidence.
- `publication-preview.png`, `controlled-publication.png`: independently reviewed disclosure and named-recipient publication evidence.
- `portfolio.png`, `sign-in.png`, `result-lineage.png`, `mobile.png`: rendered screenshots inspected during this build.
- `access-members.png`, `access-invitations.png`, `access-approval.png`, `access-mobile.png`: administration screenshots, with no invitation tokens displayed.

Reproduce the local evidence with `make test reference browser`. Native qualification requires an empty disposable `impact_test` database and an explicit `IMPACT_FIXTURE_DSN`, then `.venv/bin/python scripts/run.py test --native`. The native runner refuses development mode and the fixture loader refuses non-fixture database names. It does not reset existing databases. The configured CI service is disposable; separate production login-role provisioning and real-provider qualification remain additional gates.

## Workspace evidence

`workspace-browser-tests.json` records ten passing role, unit, group, independent-review, custody, preference and session workflows. `workspace-account-desktop.png` and `workspace-account-mobile.png` show the compiled client. The core browser test now waits for the successful-save status specifically, because a loading status can appear concurrently; its assertion has not been weakened.

The temporary diagnostic used while tracing the local emulator is not part of the source release or final count. Native PostgreSQL service installation was unavailable here, and no native persistence, concurrency or upgrade result is claimed. See RELEASE-0.9.md and NEXT-DELIVERY.md for provider and remaining Release 1 gates.

## Measurement-specific acceptance

The measurement suite exercises the complete programme/definition/plan activation path, the FR-CAL-008 five-contributor vector, missing and exceptional values, present zero, unplanned source exclusion, source-key reservation, independent approval, competing-plan rollback, returned-plan resubmission, governed correction, additive plan amendment, reviewed obligation exclusion, responsibility reassignment, immutable approved data, server-controlled indicator pins, configuration drift before approval/activation, assignment suspension, revision conflicts, exact retry, same/cross-tenant denial and forced binding RLS. Approval of a plan after an earlier calculation creates a durable stale-result invalidation; source changes do the same. The browser shows historical/required/excepted coverage and each obligation's status, then acknowledges a safe notice and completes the assigned recalculation task.

The period/reporting suites then prove the bounded promotion path from current provisional calculations to immutable official snapshot members, a frozen internal report, and an independently reviewed named-recipient HTML/CSV publication with withdrawal. They do not qualify anonymous/public disclosure, external contacts, PDF/DOCX/XLSX, provider delivery, background-worker execution or native PostgreSQL concurrency.

## v0.10 tenant lifecycle evidence

Fourteen live checks cover operator authority, wrong-owner rejection, independent activation, closed profile validation, expiry and revision drift, exact retries, revoked-operator replay, zero implicit grants, suspension/reauthentication, durable job and schedule holds, tenant isolation and database-role boundaries. Seven browser workflows cover the three identities, confirmation forms, lifecycle transitions and mobile layout. Screenshots: tenant-lifecycle.png and tenant-lifecycle-mobile.png.

Regression found two pre-existing timing bugs: change-request resources loaded before permissions arrived, and a late initial-access response could override a user's chosen navigation. Both were corrected and the affected measurement and workspace workflows passed.

All results are local PGlite development qualification. Native persistence/concurrency, genuine provider assurance/recovery, worker effects, initial new-tenant access provisioning and completed closure remain open. No new requirement is marked fully accepted.

## v0.11 initial access evidence

Twenty-five live checks cover the complete onboarding-to-first-programme path, closed schemas, verified identity and natural-person separation, fresh authentication, nominated inbox visibility, capability and expiry ceilings, exact retries, revoked-grant non-resurrection, stale owner/tenant/profile/deployment pins, consent cutoffs, suspension, withdrawal/rejection, revoked operators and database-role constraints. An injected failure after access provisioning returns a retryable service error and leaves no grants, authority, new membership, scope, assignment, applied marker or receipt; the same operation succeeds once after the injected failure is removed.

Eight browser checks cover owner proposal, private visibility, nominee acceptance without grants, independent operator provision without operator membership, administrative-only access, independently reviewed business grants, first programme creation and mobile layout. Screenshots: `initial-access.png`, `initial-access-mobile.png` and `initial-access-programme.png`. Final screenshots were visually inspected. Browser testing also found and fixed an asynchronous session-refresh reset of the selected workspace, and supplied an explicit accessible name for the tenant selector.

The initial-access workflows remain covered in the current regression run. The historical v0.11 scope and limits are retained in RELEASE-0.11.md.

## v0.12 recovery-contact evidence

Twenty-nine live checks cover activation readiness, no implicit membership or grants, private participant inboxes, closed schemas, bounded expiry, natural-person independence, fresh configured assurance, exact retries, atomic replacement, decline/cancel/reject, immediate revocation, pinned owner/tenant/profile/contact drift, account authentication cutoffs, revoked-operator replay and database-role restrictions. A positive repair path renews expired contact evidence while Suspended and permits independent reactivation. An injected failure during replacement leaves the old contact and audit history intact and creates no receipt; a subsequent retry succeeds once.

Nine browser checks exercise readiness refusal, owner nomination, unrelated-account privacy, nominee consent, independent approval, replacement decline, approved replacement, revocation and mobile history. Desktop and mobile screenshots were visually inspected. Verification is through an existing registered account with fresh configured assurance; development proof is synthetic and visibly labelled. These checks do not establish email/SMS delivery, live provider assurance or actual account recovery.

Workspace regression exposed an initialization race when permissions arrived after the settings page mounted. The page now selects the first permitted section once capabilities arrive and retains any valid selection. The browser check holds the initial permissions response until the settings page is open, then creates a role successfully.

All eight browser groups passed with no uncaught page errors. The original 66 specification files and fourteen prior migrations are byte-identical to the saved v0.11 archive; see `evidence/source-preservation.json`. Migration 0015 is additive. Reviewed authority renewal, external-channel verification, unavailable-owner recovery, native PostgreSQL and operational acceptance remain open as detailed in RELEASE-0.12.md and NEXT-DELIVERY.md. No requirement is newly declared fully accepted.

## v0.13 authority-renewal evidence

Twenty-eight live checks cover the end-to-end proposal, confirmation and approval that extend every pinned ceiling, grant, assignment and the second administrator's membership while readiness, epochs and the bootstrap marker are verified; owner-only proposal and closed fields; second-administrator eligibility and natural-person independence; expiry bounds (not after the current ceiling, in the past, beyond 90 days, malformed, without offset); removed ceilings and revoked grants excluded before a proposal and never resurrected by approval or replay; a grant revoked through the ordinary administration path after consent invalidating approval; pinned tenant, owner, qualification and review-deadline drift; owner and second-administrator authentication cutoffs; operator-only review and operator independence; exact retries, operation reuse, fresh assurance and invalid transitions; one live proposal per tenant and closure of an expired pending proposal by withdrawal or rejection; suspension and a revoked recovery contact blocking renewal until evidence is restored; private inboxes and cross-tenant isolation; runtime role boundaries (application and identity roles cannot read the review table, update ceilings or assignments, or execute the applicator; the control-plane role cannot delete proposals or write ceilings directly); and an injected failure after extension that leaves every expiry, revision, epoch and state unchanged with no receipt, followed by one successful exact retry.

Ten browser checks exercise the owner's authority panel, client-side expiry bounds, proposal, an unrelated account's privacy, second-administrator consent, the server's denial of a non-operator whose client gate was bypassed, independent operator approval, the renewed expiry, withdrawal of a later proposal and the mobile layout. Desktop and mobile screenshots were visually inspected. During regression a timing race in the tenant lifecycle browser check (an action clicked before the tenant refresh completed) was corrected by awaiting the refresh; no assertion was weakened.

All nine browser groups passed with no uncaught page errors. Separately, the `native-postgresql-gate` job of `.github/workflows/qualification.yml` ran `scripts/run.py test --native` against a PostgreSQL 17.11 service container for commit cc3c683 and completed successfully (GitHub Actions run 36453508807, job 109033872546, 28 September 2026): the first recorded native execution of the live suite. Its JUnit artifact (`native-postgresql-qualification`) was not inspected from the development environment; the job used the disposable fixture connection, so separate least-privilege login roles, persistence across restarts, upgrades and concurrent approval/revocation under native scheduling remain open. Migrations 0001–0015 and every existing test file are unchanged. Migration 0016 is additive. Renewal of expired authority, administrator replacement, external-channel verification, unavailable-owner recovery, native PostgreSQL and operational acceptance remain open as detailed in RELEASE-0.13.md, NEXT-DELIVERY.md and DELIVERY-PLAN.md. No requirement is newly declared fully accepted.

