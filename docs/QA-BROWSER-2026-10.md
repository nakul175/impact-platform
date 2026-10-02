# QA browser coverage — October 2026

Base: build 0.24.0 (`integration/0.21-0.24`, schema 26). Branch `qa/2026-10-browser-checks`. No version change, no migration, no API change.

Build 0.24.0 shipped the Imports area (v0.21), the Evidence section (v0.22), report exports (v0.23) and the operator re-queue panel (quality 2026-10) without any browser check. This work adds four browser groups, 22 checks, that drive those screens end to end in Chromium 153 on fresh in-memory PGlite, and fixes the UI defects the checks found.

## Groups and results

All four groups passed on 1 Oct 2026, each in its own clean run (`IMPACT_PORT=23417 .venv/bin/python scripts/run.py <group>`), one at a time on a 2-CPU machine. The JSON results and screenshots in `docs/evidence/` come from those runs.

| Group | Checks | Result file | Screenshots |
|---|---|---|---|
| `import-browser` | 6 | `import-browser-tests.json` | `import-preview.png`, `import-mobile.png` |
| `evidence-browser` | 6 | `evidence-browser-tests.json` | `evidence-attached.png`, `evidence-infected.png`, `evidence-mobile.png` |
| `export-browser` | 5 | `export-browser-tests.json` | `export-succeeded.png`, `export-mobile.png` |
| `requeue-browser` | 5 | `requeue-browser-tests.json` | `requeue-dead.png`, `requeue-mobile.png` |

What each group exercises:

- **import-browser** (`tools/browser/import-check.mjs`). Setup through the API: a programme, an approved COUNT indicator with an approved collection plan, and six approved prior values that give the anomaly check its minimum history (median 10.5). In the browser, the author uploads a synthetic CSV (in memory, nothing on disk), maps `households` to the indicator by name, clears the atomic option and saves a draft. The preview then shows 4 rows: one DUPLICATE (`DUPLICATE_UNIT_PERIOD`, a unit already imported for the period), one QUARANTINED (`VALUE_NOT_NUMERIC`), one ACCEPTED with `ANOMALY_ROBUST_OUTLIER` (value 100), one ACCEPTED, and the unmapped `remarks` column is ignored. The API confirms the preview wrote nothing. Commit stays disabled until the warnings are accepted. The first commit response is dropped; the retry repeats the exact command and gets the original receipt. The two produced observations show in Measurement as Submitted, IMPORT namespace. The reviewer, a different natural person, approves one of them from the review queue, and the other stays Submitted. The area stays within 390 px.
- **evidence-browser** (`tools/browser/evidence-check.mjs`). Setup through the API: one draft observation. In the browser, a synthetic PNG goes through upload, the scan (CLEAN) and attachment, and the list shows `scan CLEAN` with a Download link. The observation is not revised. Clicking Download returns the exact bytes. The response headers are checked: `image/png`, `attachment; filename=…`, `nosniff`, `no-store`, a CSP containing `sandbox`, and a SHA-256 equal to the upload. A synthetic PDF attaches as a second item and downloads beginning `%PDF-`. The EICAR test file (base64 in the source, like `content_safety.py`) is sealed `INFECTED`. The refusal is announced beside the attach button, nothing new is listed, there are still only two Download links, and the API refuses evidence from that upload (409 `UPLOAD_NOT_CLEAN`). The `other_tenant` cookie session gets 404 `RESOURCE_UNAVAILABLE` for the attachment list, the evidence record and the content, and its own Measurement list does not show the observation. The panel stays within 390 px.
- **export-browser** (`tools/browser/export-check.mjs`). Setup through the API: an approved report package on the fixture snapshot. In the browser, the author requests PDF, XLSX and DOCX. Each row shows Queued, and its request button is disabled while the export is open. The worker runs once (`runWorkerOnce`, as `recovery-browser` does; browser modes start no worker process) and records `exports_succeeded == 3`. The panel's own 4 s poll then moves every row to Succeeded without a reload. Each format is downloaded through its UI link: PDF begins `%PDF-`; XLSX and DOCX begin with the ZIP signature `PK\x03\x04` and contain `xl/workbook.xml` and `word/document.xml`. The bytes hash to the listed `content_sha256`, and the content type, attachment disposition and `nosniff` are checked. The author then requests a disclosure in the UI with the PDF box checked, and the candidate pins exactly that PDF job. After API approval and publication, the partner's session downloads `download.pdf` (same hash), `download.xlsx` and `download.docx` return 404 because they were not disclosed, and the author, who is not a recipient, gets 404. The panel stays within 390 px.
- **requeue-browser** (`tools/browser/requeue-check.mjs`). Setup: one ordinary worker iteration settles the fixture's due rows. An invitation email intent is created through the API. One worker iteration with `MAX_ATTEMPTS=1` and `SYNTHETIC_FAILURES=1000` makes it DEAD (`SYNTHETIC_FAILURE`). In the browser, the platform operator finds it in Tenant lifecycle → Deliveries needing attention (`MEMBER_INVITATION by EMAIL`, `Failed · 1 attempts · SYNTHETIC_FAILURE`, no address shown) and the failing worker's heartbeat in the Workers panel. The opener reports `aria-expanded`, and the reason field is required. The first re-queue response is dropped; the error appears inside the form, and the retry sends the same operation ID and `expected_revision` and gets the original receipt (PENDING, previous DEAD, attempts 0). The row leaves the list. The next ordinary worker iteration sends it exactly once to the synthetic sink, and after Refresh the panel shows "No delivery needs attention.". The `author` session gets 404 from `/v1/platform/deliveries` and sees no delivery panel. The console stays within 390 px.

Common harness (`tools/browser/qa-harness.mjs`):

- **Separate sessions.** Each actor gets its own browser context, so cookie sessions never mix.
- **Sidebar reached by scrolling.** The viewport is 1440 × 560, so every sidebar entry is reached by scrolling the fixed navigation, as on CI runners whose fonts are taller than local ones.
- **No fixed delays.** Every wait is on a response or an element state.
- **Long lists.** Lists are paged with "Load more" until the record appears; they are ordered oldest first, 50 at a time.
- **API setup.** Setup uses the suite-start bearer tokens.
- **Quiet worker runs.** `quietly(fn)` runs a worker iteration only while every open page's API requests are held and none is in flight; held requests continue afterwards (see "CI finding").
- **Failure capture.** Each group writes `docs/evidence/<group>-tests.json` and, on failure, `<group minus -browser>-failure.png`.

`tools/browser/worker-run.mjs` `runWorkerOnce(local, id, settings)` now accepts optional `IMPACT_<FIELD>` worker settings. Existing callers are unchanged.

## CI finding: worker and API on one PGlite socket

The first CI run of `export-browser` (pull-request run of commit aa1f173) failed, although the push run of the same commit and every local run passed. The worker rendered the PDF and the XLSX. Its next connection was then refused (`server closed the connection unexpectedly`) and the heartbeat raised, so `--once` exited non-zero. The cause is the exports panel's 4 s poll: it reached the API while the worker process was between transactions, and the PGlite socket server serves one connection at a time (CLAUDE.md §11: the worker and the API take turns).

The checks now run every worker iteration through `quietly()`, which holds and drains the pages' API requests first. The panel still moves to Succeeded on its own afterwards, on its next poll.

Two consequences outside the scope of this branch, recorded rather than fixed:

- A refused connection in `run_once`'s heartbeat ends the `--once` process with a traceback instead of a counted tenant failure.
- `make dev` runs a long-lived worker beside the API on the same PGlite socket, so the same refusal can appear there, logged as a failed tenant pass.

## Defects found and fixed

All fixes are small and stay in the files of the feature concerned.

1. **Imports: commit was enabled while warnings were unaccepted** (`apps/web/src/Imports.tsx`). With an anomaly warning in the preview and the acceptance box unchecked, "Commit N accepted rows" stayed enabled and failed with 422 `WARNINGS_NOT_ACCEPTED`. It is now disabled until the warnings are accepted. Covered by the import group, which asserts the disabled state.
2. **Imports: checkboxes were stretched away from their labels** (`apps/web/src/styles.css`, import section only). The global `width: 100%` input rule pushed the "All rows or nothing (atomic)" and "I have reviewed the warnings…" boxes to the middle of the row, far from their text (visible in the first preview screenshot). `.import-new` and `.import-commit` checkbox inputs now use `width: auto; flex: none`.
3. **Evidence: the scan state was never shown** (`apps/web/src/Evidence.tsx`). The attachment list returns `scan_state`, but the UI dropped it, so a user could not see a file's scan verdict. Each item now shows `· scan <STATE>`.
4. **Evidence: upload errors appeared out of view** (`apps/web/src/Evidence.tsx`). The panel sits at the bottom of a scrolling dialog, and its alert and status were rendered above the attachment list. After an EICAR refusal the message was off-screen and nothing visibly happened near the button. When the user may attach, messages now render inside the attach form, just above "Upload and attach"; read-only users still see them at the top of the panel.
5. **Report exports: the table overflowed the dialog** (`apps/web/src/ReportExports.tsx`). With three rows the table ran past the dialog's right edge. It is now wrapped in the existing `.table-scroll` container. Only indentation changed inside the table.
6. **Re-queue: errors appeared away from the form, and the opener was ambiguous** (`apps/web/src/Workers.tsx`). A failed re-queue or release showed its alert at the top of the panel, possibly far above the open form. While a form is open, the alert now renders inside it. The row's opener button ("Re-queue" / "Release hold") has the same name as the submit button, so it now carries `aria-expanded`.

Checked and found correct (no change):

- operation IDs are kept for retries in Imports (`usePendingOperations`), Evidence (per-step `useRef` map), ReportExports (`usePendingOperations`) and Workers (`useRef` keyed by path, revision and reason);
- the three lost-response checks above confirm that a retry repeats the exact body;
- accessible names of the file, mapping, evidence and reason fields;
- export request buttons are disabled while an export of that format is open.

## Limits

- PGlite evidence only. One worker iteration is run on demand, so the checks do not show worker contention or timing; those stay native-only.
- **Synthetic files only.** The EICAR check exercises the `eicar-signature` test scanner, not malware protection.
- **Export disclosure covers PDF only.** XLSX and DOCX are checked as undisclosed (404), not as disclosed downloads; the API suite covers both.
- **Import mapping fields have no visible labels.** They use `aria-label` and placeholders only. This is left to the parallel accessibility pass.
- **XLSX source not driven in the browser.** The import group covers CSV only; XLSX import stays API-tested.

## Reproduction

```
npm ci --prefix tools/browser && node tools/browser/prepare.mjs   # once
npm --prefix apps/web run build
IMPACT_PORT=<free port> .venv/bin/python scripts/run.py import-browser
IMPACT_PORT=<free port> .venv/bin/python scripts/run.py evidence-browser
IMPACT_PORT=<free port> .venv/bin/python scripts/run.py export-browser
IMPACT_PORT=<free port> .venv/bin/python scripts/run.py requeue-browser
make lint
```

`make browser` (and therefore the CI job `local-reference-and-browser`) runs all sixteen groups.

## Integration notes

Shared files touched by this branch:

- `Makefile` — four lines in `browser`.
- `scripts/run.py` — four `BROWSER_MODES` entries.
- `tools/browser/worker-run.mjs` — optional settings argument.
- `apps/web/src/Imports.tsx`, `Evidence.tsx`, `ReportExports.tsx`, `Workers.tsx` — the fixes above.
- `apps/web/src/styles.css` — one rule in the import section.

The CI workflow is not edited, because its browser job runs `make browser`. New files: `tools/browser/qa-harness.mjs`, `import-check.mjs`, `evidence-check.mjs`, `export-check.mjs`, `requeue-check.mjs`, this document, and the evidence files listed above. Possible merge overlap with the parallel accessibility pass: `ReportExports.tsx` (re-indented table) and `Workers.tsx`.

Lines for the shared documents (not edited here):

- **QUALIFICATION.md / CLAUDE.md §1 and §7.**
  - Browser totals: **132 checks in sixteen groups** (110 in twelve groups + `import-browser` 6, `evidence-browser` 6, `export-browser` 5, `requeue-browser` 5), Chromium 153, recorded 1 Oct 2026.
  - Results: `docs/evidence/{import,evidence,export,requeue}-browser-tests.json`.
- **IMPLEMENTATION.md / CLAUDE.md §11.** Remove the statements that no browser check covers Imports (v0.21 bullet), the Evidence section (v0.22 bullet) and exports (v0.23 bullet); the operator re-queue panel is now covered by `requeue-browser`. Mention the six UI fixes under the respective features.
- **NEXT-DELIVERY.md.** The QA browser coverage for v0.21–v0.23 and re-queue is delivered; an XLSX import browser check and accessible visible labels for import mapping fields remain open.
- **CHANGELOG.md.** "QA 2026-10: four browser groups (import, evidence, export, requeue; 22 checks); UI fixes: import commit gated on accepted warnings, import checkbox layout, evidence scan state shown, evidence and re-queue errors shown beside their forms, export table scroll container, re-queue opener `aria-expanded`."
- **CURRENT-API-INVENTORY.md.** No change (no API change).
- **SCREEN-COVERAGE.csv.** Add or update these rows (screen, browser group, evidence):
  - Imports — batch list, new batch, preview and commit; `import-browser`; `import-preview.png`, `import-mobile.png`
  - Measurement — observation detail, Evidence panel (attach, scan state, download, infected refusal); `evidence-browser`; `evidence-attached.png`, `evidence-infected.png`, `evidence-mobile.png`
  - Reports — approved report, rendered exports (request, status, download); `export-browser`; `export-succeeded.png`, `export-mobile.png`
  - Reports — disclosure request with rendered export formats; `export-browser`; (no screenshot)
  - Tenant lifecycle — Deliveries needing attention (re-queue) and Workers heartbeat; `requeue-browser`; `requeue-dead.png`, `requeue-mobile.png`
- **EXECUTION-REGISTER.csv.** One row per group with the counts above (passed, 0 failed), date 2026-10-01, PGlite.
- **TRACEABILITY.csv / COMPLETION-LEDGER.**
  - Add the new check files as supporting browser evidence to the existing groups in `scripts/build_completion_ledger.py`: imports `FR-DAT-001/002/004`, `FR-DQ-003/007`; evidence `FR-EVD-001`, `FR-SEC-005`; exports `FR-RPT-*` export rows; re-queue `FR-TEN-001`. Then run `make ledger`.
  - No requirement changes status on browser evidence alone.
