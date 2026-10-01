# Accessibility statement — Impact Platform web client

Status: **partial evidence, not a conformance claim.** Recorded 1 October 2026 against build 0.24.0 (branch `qa/2026-10-accessibility`, based on `integration/0.21-0.24`). The governing requirement is VF-UX-001 (FSD v1.1, NFR-UX-001): *all supported core journeys shall meet WCAG 2.2 Level AA through automated checks and manual keyboard and assistive technology review*, and its failure rule says *a clean automated scan alone does not pass*. This statement records what was checked, what was fixed and what remains untested. VF-UX-001 is at most PARTIAL on this evidence.

## What was tested

| Check | How | Result |
|---|---|---|
| Automated rule scan | axe-core 4.13.0 (pinned in `tools/browser/package.json`) injected into the running single-page client by `tools/browser/a11y-check.mjs` (`scripts/run.py a11y-browser`, part of `make browser` and the CI browser job). Rule tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa`; best-practice rules recorded as advisory. | 43 page states scanned: sign-in; every workspace area (portfolio, measurement, measurement setup and each of its tabs, results framework and each of its tabs, dashboards, forms, imports, change requests, period close, my work, review queue, results, reports, people and access and each of its tabs, workspace settings and each of its sections, my account); record dialogs for a programme, an observation with its evidence panel, a calculated result, an approved report with its exports panel; the new-programme, add-observation and review-decision dialogs; tenant lifecycle with the operator Workers panel, recovery contacts, initial access and authority renewal; the portfolio at 390 px width. **0 serious or critical WCAG violations, 0 accepted exceptions** (before the fixes: 759 failing nodes, all `color-contrast`, on 39 of the 43 states). |
| Keyboard-only core flow | The same group drives one core journey with the keyboard alone (Tab, Enter, Escape, arrow keys and typing; no pointer events): an author opens Measurement, adds an observation (indicator chosen with the arrow key, date typed), saves it, opens it and submits it for review; an independent reviewer opens the review queue, filters it with the search field, opens the submission and approves it with a reason. | Passed. Every control on the path is reachable in tab order and shows a 3 px focus outline whose contrast against the background behind it is at least 3:1 (measured 5.87–8.87:1, recorded per control in the evidence file). |
| Dialogs | Same check. | Focus moves into the modal dialog when it opens; no element behind it can receive focus while it is open (tabbing past the last control goes to the browser and the next Tab returns into the dialog); Escape closes it and focus returns to the control that opened it. |
| Tabs and skip link | Same check. | Arrow keys, Home and End move between the tabs of a tab list and Enter selects one; the first Tab stop is a visible "Skip to main content" link that moves focus to the main region. |

Evidence: `docs/evidence/a11y-browser-tests.json` (per-page results, focus trail, accepted exceptions, items axe could not decide). Browser: **Chromium 153 only** (headless, `@sparticuz/chromium`, Linux x86_64), viewport 1440 × 1000 and one state at 390 × 844, locale en-US, development sign-in on fresh in-memory PGlite with the synthetic fixture.

## Fixed in this round

- Text colour contrast: 28 text colours that fell below 4.5:1 on at least one surface they appear on were replaced by colour tokens on `:root` in `apps/web/src/styles.css`. `--text-muted` and `--text-eyebrow` reach at least 4.6:1 on white, the page background and the tinted panels (down to `#e5ebde`); each badge and code token reaches at least 5.3:1 on its own background; `--placeholder-text` reaches 4.6:1 on the white field background. Text on the dark sidebar and sign-in panel was already above 4.5:1 and is unchanged.
- Focus visibility: the focus outline was `#82b58c` (about 2.2:1 against the page background, below the 3:1 of WCAG 1.4.11); it is now `--focus-ring` (5.2–6.3:1 on light surfaces) with a light variant on the dark sidebar, and also applies to `summary` and `[tabindex]` elements.
- Skip link to the main content (`#main-content`, focusable without entering the tab order).
- Dialog focus return: the shared `Dialog` returns focus to its opener when it closes.
- Tab lists (access administration, measurement setup, results planning): arrow-key, Home and End movement (`apps/web/src/a11y.ts`).
- Status announcements: the workspace save message is a status region that stays mounted, so each new message is announced; export job states in the report exports table are a polite live region; the evidence attach/scan notice is a mounted status region.
- Structure: the records table has a caption and column scopes; the portfolio note heading and the dashboard indicator cards no longer skip a heading level.
- Reduced motion: the operating-system `prefers-reduced-motion` setting is honoured in addition to the account preference.

## Not tested — do not read this statement as covering it

- **Screen readers**: no NVDA, JAWS, VoiceOver or TalkBack run. Live-region announcements, accessible names and reading order are verified only by markup and axe rules, not by hearing them.
- **Other browsers**: Firefox, Safari, Edge and mobile browsers were not run; no browser matrix is declared.
- **Zoom and reflow**: no 200 % text resize or 400 % zoom (WCAG 1.4.4, 1.4.10) check; only one page state at 390 px width was scanned. Text spacing (1.4.12) and orientation were not checked.
- **Manual audit**: no expert WCAG 2.2 AA review. Criteria axe cannot decide — meaningful sequence, consistent navigation and identification, error suggestion and prevention, timing (the 15-minute idle session), focus not obscured (2.4.11), target size (2.5.8), dragging (2.5.7), accessible authentication (3.3.8), redundant entry (3.3.7) — are untested.
- **Most flows by keyboard**: only the submit-and-review flow, tab lists and dialogs were driven by keyboard. Forms design and publication, imports, evidence upload, period close, report publication, administration, tenant lifecycle and the invalid-field and stale-revision cases of acceptance FT-UX-004 / AT30 were scanned but not walked.
- **Live identity provider pages**: the Keycloak sign-in, TOTP and logout pages (an authentication flow under product control) were not scanned; this group uses the development sign-in.
- **Generated artifacts**: HTML/CSV publications and the PDF, XLSX and DOCX report exports were not checked for tagged structure, headings or table semantics.
- **Charts**: the dashboard trend chart's text alternative and equal table are checked by `dashboard-browser`; no further chart review.
- **Users**: no usability session with people with disabilities (VF-UX-002).

## Known limitations and items for manual review

- After a save that refreshes a list, the list is re-rendered and focus falls back to the document start (the save is announced through the status region). Moving focus to a stable target after such refreshes is not done.
- Most other panels mount their `role="status"` message only when it appears; some screen readers do not announce a status region inserted with its text. Only the workspace save message, the export states and the evidence notice were changed.
- Tab lists keep every tab in the Tab order (no roving `tabindex`) and do not yet link tabs to panels with `aria-controls` / `role="tabpanel"`.
- axe reported as *needs review* (not failures): decorative navigation glyphs hidden from assistive technology, and empty tables whose header row has no data cells (empty states).
- Several very small eyebrow labels (9–11 px) meet contrast but are small; no text-size review was made.

## Feedback

Report accessibility problems to the platform owner through the project's issue tracker. Reports are prioritised by data loss, disclosure and incorrect official result risk first, as the FSD's usability qualification does.
