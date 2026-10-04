# v0.28 — Collection round and assignment screens

UI increment merged as PR #82 (`6712970`) on build 0.28.0; schema 33 and both API versions unchanged. The requirement ledger remains 113 PARTIAL, 194 PENDING, 0 accepted of 307. All four PR jobs passed on its final head, including the browser flow. The subsequent `main` run found an unrelated Sunday backup-test expectation (see [RELEASE-0.28-ci-sunday.md](RELEASE-0.28-ci-sunday.md)); live deployment has not been independently verified from this workspace.

## Delivered

The Collection rounds area lists rounds and their due dates, lets an authorised manager create or edit a round against a published form version and period, and shows the server's fixed-denominator coverage by expected unit. An authorised manager can assign an unassigned unit and reassign an open task with a reason. The assignment list is scoped by the API: collectors see tasks they hold, while managers see tasks in their read scope. A collector can open the form with its unit and assignment pinned; submission passes the assignment ID through the existing independent review path. The form screen refuses to fill an assignment pinned to a version older than the currently published version, instead of silently switching its version.

## Contract and persistence

No route, capability, database table, migration or version changes. This screen uses the existing `collection-rounds`, `assignments`, `forms/{id}/published`, `collection-rounds/{id}/coverage`, `submissions` and `membership-directory` reads and commands. Mutation retries keep the same operation ID for the same payload. Server rules still verify current grants, eligible holders, immutable round and task fields and independent observation review. The UI's navigation appears only to holders of round or assignment capabilities.

## Limits

The screen lists the first 100 visible rounds, assignments, forms and periods. When the manager cannot read the member directory, assignment requires a principal ID; the server checks eligibility. A task pinned to a superseded form version cannot be filled from this screen, because the existing published-form read exposes only the latest form body. There is no offline collection, visit replacement or sampling frame. This sandbox has no Chromium or network sockets; the PR browser check passed in CI. The staging health gate for the Kobo PR remains unresolved.

## Reproduction

`make lint`; `npm run build --prefix apps/web`; `make forms-browser` in a browser-enabled environment. The existing `qualification/test_forms_rounds.py::test_rounds_assignments_my_work_and_coverage` exercises the server-side access, completion, reassignment and fixed denominator. The new `forms-browser` case drives the round and assignment screen and checks completion and coverage. Local lint and web build passed; local `make unit` reported 362 passed, 59 skipped, 15 failed and 2 errors because this sandbox blocks local sockets (mail sink, TLS and fake Keycloak servers). This is an environment limit, not green evidence.

## Not delivered

No Kobo connector, saved dashboard or workplan in this change.
