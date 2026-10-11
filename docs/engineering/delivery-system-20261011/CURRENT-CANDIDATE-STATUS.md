# Imprana Commons: current diagnosis candidate

Latest qualification observed 11 October 2026 at 19:39 UTC, against baseline
`d2cb26f932bb96dc3264ca50ec2c6202f4461468` plus the two newly pinned optional
provider-browser test/checker files. This page is a navigation and
release-handoff checkpoint, not acceptance or a deployed-state receipt. Inspect
the actual head and writer record before continuing. Older sections in the
handover, implementation contract and review pack remain chronological evidence;
their original version numbers and pending observations describe their own dates.

## Current work and counting

Only **US-DX-01a / APL-361** is active on `feat/imprana-diagnosis-20261011`.
The original implementation is `2e9f7841175efea3c5fc7572c6402b1dc89ff811`.
`VERSION.json` supplies build **0.40.0 unreleased**, domain API **1.31.0** and
platform API **1.11.0**; the 47 registered migration files supply schema **47**.
Applied SQL, original criteria and saved history remain unchanged.

Manual diagnosis, immutable completion/correction, current-authority checks,
exact operation retries, worker isolation, typed Evidence references and bounded
diagnosis privacy cleanup are implemented and locally qualified. Evidence notes
remain mandatory. Source availability is rechecked for linked revisions; this
does not make the diagnosis an independent approval, official calculation or AI
effectiveness finding. Existing-tenant access is not automatically widened.

**Delivered/deployed: 0/50. Release-ready: no. Owner acceptance: not recorded.**
No next feature has started. Do not count tests, technical tasks, documentation or
local passes as delivered stories. Main/CI/staging observations belong only in
the status block of [the repository handover](../../HANDOVER.md); this page makes
no new remote or deployed-state observation.

## Latest executed qualification, with separate source pins

| Evidence | Actual observed result | Tested source and boundary |
| --- | --- | --- |
| [Full native pooler](../../evidence/candidate-0.40/native-pooler-full-20261011/FULL-POOLER-RECEIPT.json) | 2,690 passed, 24 explicit skips, one deselection; separate API restart phases, real backup/restore and populated 45-to-47 upgrade pass | `0ed0c5b`; 193 tables / 117,676 rows restored with zero differences. No fresh full-suite claim for later runner/test changes. |
| Same full-native receipt: owned database outage | One passed; observed 12.8-second downtime, retryable refusals and exact recovery without duplicate effects | `0ed0c5b`; no latency acceptance, mid-transaction kill or pre-erasure recovery claim. |
| [Actual provider through pooler](../../evidence/candidate-0.40/provider-pooler-20261011/PROVIDER-POOLER-RECEIPT.json) | 18 passed, zero skips/failures/errors; 297 stable pins | `c7a55b1`; real local Keycloak HTTP/cookie authentication and diagnosis behavior. Not a Chrome provider flow or production TLS. |
| [Actual Chrome through pooler](../../evidence/candidate-0.40/browser-pooler-20261011/BROWSER-POOLER-RECEIPT.json) | Ten groups / 318 assertions; nine scoped axe scans with zero violations/incomplete findings | `37de5a1`; synthetic development login. All 47 recorded transport failures remain in raw evidence: 46 aborted requests and one deliberately lost response. No human accessibility or worker delivery claim. |
| Provider receipt: narrow CLI and retained units | 51 passed: eight new CLI cases plus 43 retained cases | Narrow native test/diagnosis-browser allowance; unsupported modes refused before runtime. |
| [Private HTTP headers](../../evidence/candidate-0.40/private-headers-native-20261011/PRIVATE-HEADERS-RECEIPT.json) | One passed, zero skips/failures/errors; 300 stable pins | `7b75d265` plus exact new-test hash: actual success/replay/404/409/401 headers and no extra domain effects. Not browser cache eviction, provider sessions, TLS or deployed headers. |

| [Real-provider Chrome](../../evidence/candidate-0.40/provider-browser-native-20261011/PROVIDER-BROWSER-RECEIPT.json) | One pytest / three browser groups /45assertions, zero skips/failures/errors;398pins stable | `d2cb26f` plus two exact test hashes; actual Keycloak password/TOTP/cookies, UI save/reopen/complete, provider logout/oldcookie401, delivered late200 cannot restore UI, owner404. Independent target2revision/2receipt/2audit storage proof. Optional coverage; no axe/TLS/erasure/human/deployment claim. |

All these are local synthetic qualification. Actual runtime services stopped;
historical evidence restored or unchanged. Initial setup/test failures and skips
are retained. Distinct supporting code and evidence review phases are recorded;
they are not human signoff. These separate scopes must not be summed into an
invented full-suite result or completion percentage.

## External and human gates: concrete action order

1. **Public export authority:** the existing GitHub feature-branch export was
   rejected by automatic approval review because specific public-export permission
   was missing. A direct owner answer remains pending. Review the actual candidate
   diff and export boundary again before any permitted push; no workaround or
   direct main push. No export has occurred under this checkpoint.
2. **Financial authority:** the pending question concerns required hosted CI
   within the existing spending limit. No permission to raise a limit or create a
   paid resource is implied. Public export permission and CI spending permission
   are separate gates.
3. **Exact candidate checks:** after applicable tool/export/financial authority,
   preserve a reviewed feature branch/PR and obtain successful
   `local-reference-and-browser`, `live-identity-provider`,
   `native-postgresql-gate`, `container-stack` and `checks` on the exact release
   candidate. Local results and an advisory pooler step do not replace these jobs.
4. **Human and operational disposition:** independent PR/security/accessibility
   review, requirement/owner acceptance, existing-tenant access review and actual
   release operational gates remain necessary. The release record has `passed=false`,
   G11 not passed and G12 not run; 14 critical threats, 13 other threats and two
   chains remain open. Agents cannot fill `confirmed_by` or invent a disposition.
   These are platform-wide release findings, not 14 newly discovered diagnosis
   bugs. All 21 impact entries remain unconfirmed. The manual diagnosis's lack of
   model calls does not automatically waive G12. After-erasure backup evidence
   does not resolve TH27's pre-erasure-backup replay requirement.
5. **Controlled release:** only completed, reviewed work with all required checks
   and applicable gates may use a reviewed merge. Verify deployed commit/schema,
   health and actual demo behavior before counting this story as deployed.

Container qualification remains **NOT RUN**: no local Docker/Podman/Colima/Lima
runtime was available in the recorded inspection. No new runtime or paid resource
has been provisioned. Current identity/privacy/authority and immutable-history
defects must be resolved on their merits, not waived by the delivery target.

For the container/operator checkpoint, use
[DEPLOYMENT-WRITER-QUIESCENCE.md](DEPLOYMENT-WRITER-QUIESCENCE.md): actual in-flight
API/worker/executor drain, refusal on failed or replacement writers, private
checkpoint capture and matching-image forward recovery remain to be qualified.
The operator must continuously exclude external writers during maintenance;
the read-only client-count probe is not a durable writer fence. Existing database
provisioning and Keycloak realm/bootstrap actions require their actual account
authority; the coding request does not authorize production identity changes.

Separate read-only story and release audits at this checkpoint found no uncovered
mandatory local defect in the two frozen story criteria. The optional combined
real-provider Chrome flow now has the distinct source-pinned local receipt above;
it is not a missing frozen criterion or an automatic release requirement. Resolve the declared release gates before
starting another feature; repeated local checks do not replace them.

## Resume safely

Read `AGENTS.md`, `CLAUDE.md`, the current engineering brief, then the actual
writer/tracker records under the project output directory. Compare HEAD and
working status with the latest checkpoint. One integration writer and one active
story; supporting lanes are read-only unless assigned an exclusive file.
The historical `DIAGNOSIS-WORKER-FENCE-REVIEW.md` describes a pre-registration
draft; current migration 0045 and its integrated/recovery receipts are authoritative
for the executed worker fence. Never apply the saved draft again or edit applied SQL.

The owner window ends **12 October 2026 at 00:51 UTC / 06:21 IST**. At the deadline,
start no new feature, preserve the actual diff/evidence, report actual counts and
remaining gates, and pause the Imprana heartbeat. No guarantee of 50 deliveries is
created by this page.
