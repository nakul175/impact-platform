# Impact Platform user guide

**Added in build 0.33:** open a saved AI adoption plan to use **Programme evidence** and **Internal advice**. Save or discard ordinary draft edits before linking a programme, indicator and reporting period. Official evidence stays pinned until an explicit refresh; it remains separate from current provisional figures. For advice, invite an eligible existing member with synthetic/public text, agree scope and conflict declaration, then explicitly assign and consent before sharing the private problem. A requester acknowledges the exact advice/actions to close the case. Current permissions control every view and action; terminal cases end adviser access. [Candidate workflows and limits](../RELEASE-0.33-tola-ai-extension.md). Application/browser qualification remains in progress; this candidate is not deployed.

**Build 0.32 review update:** saved AI plans now offer **View saved guidance**. Select an actual saved revision to inspect the guide wording retained for that revision. This leaves your editable draft and learning progress unchanged. Older revisions may have partial or unavailable guidance; missing wording is not reconstructed. Confirm current supplier terms directly before acting on historical tool information. [Release and limits](../RELEASE-0.32-tola-ai-sprint.md). Not merged/deployed or accepted.

**Build 0.31.0 review update:** supplied cost comparisons, self-reported pilot measurements including review time, four manual task-practice worksheets and saved source inputs now extend the nonprofit adoption plan. Stable learning progress and guide-version warnings preserve earlier saves. Domain API 1.22.0, schema 35. Local tests and new workflow checks are recorded; seven unchanged Mac operations failures and remaining release gates prevent approval. Not merged, deployed or accepted. See [release record](../RELEASE-0.31-nonprofit-ai-planning.md). Historical build notes below retain their original context.

Build 0.30.0 review update: save named AI adoption drafts, search and compare eight source-backed tools, record practical learning progress, draft procurement questions and track a pilot checklist. Schema 35/domain API 1.21.0, 240 implemented operations. Not merged or deployed; live advisory needs funded API credits. See `RELEASE-0.30-ai-adoption-tool.md`.

**Proposed local 0.30.0 (5 October 2026):** nonprofit AI enablement, with readiness/capacity/procurement guidance and separately authorised advisory drafts. Three domain operations (1.20.0), schema 34. Not merged or deployed. See [release note](../RELEASE-0.30-nonprofit-ai-enablement.md). Marketplace transactions remain unavailable.

## Proposed logframe export (build 0.29.0, local branch)

In Results framework, select a programme with an approved baseline. If you have export permission, choose **Download logframe CSV** or **Download logframe Excel**. The file names its exact approved framework version and includes its hierarchy, assumptions, relationships and exceptions. It contains indicator identifiers, not current measurement figures. This feature is not yet deployed.

This guide describes build 0.26.0 of the development and staging application, refreshed for the v0.27 usability work (`docs/RELEASE-0.27-ux.md`). It is written by task. Each section names the release note that describes the feature in full and its exact limits; where this guide and a release note disagree, the release note is right. Nothing here describes a production-approved service: Release 1 is in progress and no requirement is accepted (`docs/COMPLETION-LEDGER.md`).

Two rules explain most of what you will see. First, the screen shows only the actions your current permissions allow, and the server checks every request again: seeing a record never means you may approve, export or publish it. Second, nothing is overwritten. A change is a new revision, an approval is tied to the exact revision that was submitted, and official numbers come only from a closed period.

## Sign in

*Release notes: `docs/RELEASE-0.15.md` (live identity provider), `docs/RELEASE-0.26a.md` (start page and sign-in accounts).*

1. Open the platform address. In a development environment you enter the username and password generated for you; on staging you choose **Continue with your organisation**, which sends you to the organisation's sign-in service for your password and a one-time code from your authenticator app. On your first staging sign-in the service asks you to set your own password and to add the authenticator.
2. If you belong to more than one workspace, choose the right one in the **Workspace** list at the top of the page before you enter or approve anything.
3. If you belong to no workspace yet, you see **No active workspace**. It tells you what happens next for your situation: an invitation link to open, a nomination to accept, or an ownership request to review in the Tenant lifecycle console. Your identity reference is shown there with a **Copy** button; an administrator may ask you for it.
4. If you are a member but have no permission yet, you see **Your access is being set up** (for a workspace owner: **Your administrator access is being set up**). The page explains the steps that are still outstanding. Choose **Check again** once the approval has been recorded.
5. Actions that change who may do what, close a period, publish a report or touch personal data require that you signed in within the last five minutes. If such an action answers "Sign out and sign in again", do exactly that; the time your session was issued does not count, only the moment you authenticated.
6. **My account** shows your display name, a reduced-motion preference and your signed-in sessions. **Sign out** ends the platform session and, on staging, the sign-in service's session too. After fifteen minutes without activity, or eight hours in all, you are signed out automatically.

Signing out also clears the page for the next person: whoever signs in on the same browser tab starts at their own landing page.

## Find your way around

The sidebar narrows to the areas you can use as soon as your access has been checked. **Portfolio** holds programmes. **Measurement** holds observations. **Measurement setup** holds indicator definitions, indicator assignments and collection plans. **Results framework**, **Dashboards**, **Forms**, **Imports**, **Change requests**, **Period close**, **My work**, **Review queue**, **Results** and **Reports** are described below. **People & access** and **Workspace settings** are for administrators (`docs/current/ADMINISTRATOR-GUIDE.md`). **Tenant lifecycle** opens the operators' console, in which you see only the requests addressed to you.

Every list shows the records you are permitted to read, fifty at a time; use **Load more** for the rest and the search box to filter what is loaded. Opening a record shows its current revision, its state and the fields the server stores. Record identifiers are shown short (the first eight characters) only where no name exists.

## Set up a programme and its measurements

*Release notes: `docs/RELEASE-0.19.md` (calculation methods and disaggregation), `docs/RELEASE-0.26a.md` (reference data).*

A programme needs a reporting calendar and a geography before it can be activated. Both come from the workspace's reference data, which an administrator sets up under People & access (the standard set creates a yearly calendar with its periods, a review template, a report template and a geography).

1. In **Portfolio**, choose **New programme**: title, code, dates, type, reporting calendar and geography. Open the saved programme to see its readiness checks; **Mark ready** and then **Activate programme** become available when they pass.
2. In **Measurement setup**, create an indicator **definition**: unit, measurement type, calculation method (sum, pooled ratio, count, last valid value, mean, median, minimum, maximum — each allowed only for the measurement types and time semantics it suits), display precision and, where needed, a disaggregation scheme of dimensions and category codes. Submit it for review; approved versions never change, a later change is a new version.
3. Create an **indicator** (an indicator assignment): it pins one approved definition version to a programme, names the collector and an independent reviewer, and sets the schedule. Activate it.
4. Create the **collection plan** for a period: which sources are expected from whom. The plan is reviewed like everything else and its approved obligations become the denominator of coverage; a period with no obligations shows coverage as not applicable, never as 100 %.

## Build the results framework and set targets

*Release note: `docs/RELEASE-0.18.md`.*

Open **Results framework** and choose the programme.

1. On **Framework**, create the draft: impact, outcome, output and activity nodes with a title, description and owner, each placed under a parent at the same or a higher level, and each programme indicator placed on one node. Saving refuses a structure that cannot be valid (a cycle, a child above its parent, an indicator placed twice) and names the node to correct.
2. Read the **Completeness review**. Resolve errors. A warning can be accepted with **Document exception**, with a reason and a review date that is not in the past.
3. Submit. A different person approves, returns or rejects the exact candidate in **Reviews**. Approval freezes baseline 1. A later change is a new draft with a later effective date; earlier baselines keep governing the periods before it.
4. On **Targets**, create per indicator and period a target (value, range or milestone), a baseline, or both, with the direction and a value state; a blank is recorded as missing, never as zero. Submit for review. A change to an approved target is a revised target that names the one it replaces, with a reason.
5. **Targets vs actuals** shows targets, baselines and milestones beside the actual and its source. An official actual appears only from this programme's locked snapshot; before close the actual is provisional.

Status thresholds, disaggregated and cumulative targets, theory-of-change relationships and charts are not available. A programme without a reporting calendar cannot carry targets.

## Enter data

You can record a value in three ways. Whichever you use, the result is an **observation** in the ordinary review, with an explicit value state: present, missing, not collected, not applicable, invalid or undefined. A blank is never a zero.

### By hand

*Release notes: `docs/RELEASE-0.19.md`; the original workflow is in `docs/IMPLEMENTATION.md`.*

1. In **Measurement**, choose **Add observation**: the indicator, a source namespace and key (the stable identity of the record you are entering; `FORM` and `IMPORT` are reserved for the other two routes), the event date, the value and, for a ratio or percentage, the numerator and denominator. Enter ordinary decimals, without exponent notation or a percent sign. Dimension codes must belong to the indicator's approved scheme.
2. Open the saved observation and choose **Submit for review**, picking the review template. The submitted revision is locked while it is reviewed.
3. A returned observation is corrected in a new revision and submitted again. Approved values never change.

### Through a form

*Release note: `docs/RELEASE-0.20.md`.*

1. In **Forms**, a designer creates a form for a programme: coded questions of type text, decimal, whole number, yes/no or single choice, each optionally required, bounded, shown only when an earlier answer has a stated value, and bound to an indicator as its value or as the numerator or denominator of a ratio. A choice question can supply a disaggregation dimension.
2. **Send for review**; a different person approves it in the Review queue; then **Publish**. Published versions are numbered; **New version** starts the next draft while the current version keeps collecting.
3. **Fill in** opens the current version. Enter the reporting unit if the collection plan names one, answer the questions, and give a reason instead of a blank where you cannot answer. **Save draft** stores it on the server. **Submit response** validates every answer against the published version and sends one observation per bound indicator into review. Submitting a bound form also needs the observation-submit permission.
4. A response started on a version that was replaced meanwhile is kept as entered but quarantined: it produces no observation.

Everyone who drafted or submitted a response is an author of its observations and cannot approve them. Repeat groups, photos, locations, translations, collection rounds, assignments, correcting a returned response and offline collection are not available.

### From a spreadsheet

*Release note: `docs/RELEASE-0.21.md`.*

1. In **Imports**, start a **New batch**: choose the programme and period and a CSV or XLSX file (first sheet; at most 500 rows and 40 columns, about 190 KB). The file travels inside the request, so there is no upload step.
2. Map the columns by their header names: the unit column, optionally an event-date column, and for each indicator the column holding its value or the two holding its numerator and denominator. Choose whether a commit is **all rows or nothing** or accepted rows only, then save the batch and **Preview** it.
3. The preview lists every row as accepted, quarantined with a reason code (for example a value that is not a number, or a unit already imported for this indicator and period) or duplicate. Nothing is written yet.
4. **Commit** the accepted rows. The platform recomputes the preview first and refuses to commit if the file or mapping changed. Each accepted row becomes an observation (namespace `IMPORT`) submitted into the ordinary review, and the unit is registered for that indicator and period so it cannot be imported twice.
5. **Cancel** a batch you no longer need.

Preview and commit run while you wait; a large batch takes some seconds, and other people's saves in the workspace wait behind a commit. Imported values are unplanned where a collection plan exists, which matters at period close (see below).

## Attach evidence

*Release note: `docs/RELEASE-0.22.md`.*

Open an observation or a result. If you may read evidence, its **Evidence** section lists the files and references cited against it, with the version that was cited and a download link when you are permitted to download.

1. To add a file, choose it in the Evidence section: PDF, PNG, JPEG, plain text or CSV up to 25 MB, with a plain file name. The browser computes the file's fingerprint, uploads it, and waits for the check. A file whose contents do not match its declared type, an executable, a PDF with active content or a file that fails the scan is refused and cannot be downloaded by anyone.
2. Give the evidence a type, source and date, or cite an `https://` reference instead of a file.
3. **Upload and attach** cites the exact evidence revision against the exact revision of the record you have open. The record itself is not changed, so an approved observation or an official result stays as it was.

The scan recognises only the standard anti-virus test file; it is not malware protection. Treat downloaded evidence as you would any file received from outside.

## Review

*Release notes: `docs/IMPLEMENTATION.md` (the single independent stage); `docs/RELEASE-0.27-ux.md` (readable stages).*

1. **Review queue** lists the reviews you may see. Open one: the **Review stages** section states who may decide (any member with the approval permission, or the named reviewers), that the decision must come from someone who did not author the submitted version, and whether it is still awaiting a decision or has been decided and when.
2. Choose **Review submission**. The dialog re-reads the exact submitted revision; if it changed since you opened the queue, you are told to refresh. For a change request it also shows the currently approved record.
3. Give a reason and **Approve**, **Return for changes** or **Reject**. A return or rejection needs a reason; an approval may carry one.

You cannot approve your own work, and a second account, a group or a delegation does not change that: independence is decided by the natural person. A decision on an older revision never carries over to a newer one.

## Calculate and inspect results

*Release note: `docs/RELEASE-0.19.md`.*

In **Results**, choose **Calculate result** for an indicator and an open period. The result is **provisional** and is calculated only from approved observations: a pooled percentage is the sum of numerators over the sum of denominators (50/100 and 1/10 give 51/110 = 46.36, never 30), a zero denominator gives **undefined**, and rounding happens once, at display. Open a result to see its coverage (expected, received, valid, approved, pending, missing), its contributors and exclusions, and its breakdown by category where the definition is disaggregated. Category values are shown rounded; the total is never the sum of them.

When an approved source or plan changes after a calculation, the result is marked stale and **My work** shows the recalculation task and a notice. Acknowledging the notice does not complete the task; recalculating does, and keeps the earlier result in history.

## Close a period

*Release notes: `docs/IMPLEMENTATION.md` (period governance), `docs/RELEASE-0.18.md` (what close pins).*

1. In **Period close**, choose **Preview period close**: the programme (shown by name, with its code in brackets), the open period, a reason and the review policy (shown by its name; the development fixture's unnamed policy appears as "Independent review, 1 approval").
2. The preview lists every blocker: an obligation not yet approved, a pending or invalid source, an unplanned value (`UNPLANNED_VALUES`) and sources changed since the preview. Resolve them through the ordinary workflows and create the preview again; a preview whose inputs changed cannot be approved.
3. An independent reviewer approves the preview in the Review queue. The close creates the **official** result versions and a locked **snapshot** in one step, and pins the approved targets and the governing framework baseline with them.
4. A locked period refuses new submissions, corrections and recalculation. A correction after close goes through **Request scoped restatement**: named sources, a window of at most seven days, independent approval; after the correction you close again and a new snapshot version supersedes the old one, which stays on record.

Imported values and form responses without a planned unit are unplanned, and unplanned values block a close. Until a reviewed way to plan them exists (acceptance gap A5 in `docs/current/RELEASE-1-ACCEPTANCE-GAPS.md`), plan the units in the collection plan before importing, or keep imports out of periods you intend to close.

## Read dashboards

*Release note: `docs/RELEASE-0.24.md`.*

**Dashboards** shows, per programme and period, each indicator's **official** value (only from this programme's locked snapshot), its **provisional** value (never merged into the official one), its status against a target where one exists, its coverage, and a freshness note with the rule that decides when a value is stale. Coverage shows **not applicable** when nothing is required and **unavailable** when you cannot read every source. Values are read live, card by card; a page with many indicators is correct but not quick. There is no dashboard authoring, saving or drill-down.

## Prepare, export and publish a report

*Release notes: `docs/IMPLEMENTATION.md` (packages and publication), `docs/RELEASE-0.23.md` (PDF, XLSX and DOCX).*

1. In **Reports**, choose **Draft report**: an approved report template, a locked snapshot, a section heading and narrative, and the official result to reference. Write every number in the narrative as a placeholder such as `{{RESULT}}`; a bare number is refused.
2. **Submit frozen package for review**. An independent reviewer approves the package, which freezes the exact template, snapshot and result revisions it binds; later recalculation never changes it.
3. An approved report offers **Open approved export** (HTML) and **Download bound values (CSV)** at once. Under **Rendered exports**, request a **PDF**, **XLSX** or **DOCX**: a background worker renders it, the status refreshes while it works, and you download the finished file. Every number in every format is the stored displayed value; nothing is recalculated. A queued export can be cancelled; one that failed names the reason.
4. **Request controlled publication** names one active member as recipient, a purpose, an expiry, whether the recipient may download, and which rendered formats to include; those formats are pinned to the exact files that already exist. An independent reviewer approves the disclosure.
5. **Publish approved disclosure** rechecks that the recipient is still active and creates immutable HTML and CSV artifacts (plus the pinned renderings). The recipient downloads them from their own session; each access is recorded.
6. **Withdraw publications** stops future access and keeps the record. It cannot recall files already downloaded.

There is no public or anonymous link and no email of a report. The PDF uses a Latin typeface; text in other scripts fails the rendering, and the file keeps a fixed metadata date.

## Correct approved data

*Release note: `docs/IMPLEMENTATION.md` (governed amendments).*

**Change requests** corrects an approved observation, collection plan or indicator assignment through a reviewed amendment: choose the approved record, describe the change and the reason, submit, and an independent reviewer approves it against the exact revision you targeted. If the record moved on meanwhile, the request is returned for an update. Approved history stays visible; a correction never rewrites it.

## When something goes wrong

| What you see | What to do |
| --- | --- |
| A field is refused | Correct the named field; the rest of the draft is kept. |
| "Someone changed this record" | Close the dialog, refresh, read the differences, then save again. |
| The connection dropped while saving | Save again from the same dialog. The platform recognises the repeated operation and returns the original receipt rather than saving twice. |
| "Sign out and sign in again" | The action needs authentication within the last five minutes. |
| "The action is not permitted" or a record you expected is missing | Ask your administrator to check your membership, grant, scope and purpose. Knowing a URL creates no access. |
| A result is marked stale | Complete the recalculation task in My work. Acknowledging the notice is not enough. |
| A form response is quarantined | The form version was replaced after you started. Fill in the current version. |
| An import row is quarantined | Read its reason code in the preview, correct the file or the mapping and preview again. |
| An evidence file is refused | Its contents, name or type did not pass the checks. It cannot be made downloadable. |

## What this build does not do

Offline and Android collection, participant records, evaluation, finance, AI assistance, integrations, public publication, charts in reports, dashboard authoring, keyed import updates, quality issues and exceptions, a real malware scanner, SMS or push notices, and email through a real provider are not implemented. A visible placeholder is not a feature. The exact boundary is in `docs/IMPLEMENTATION.md` and `docs/COMPLETION-LEDGER.md`.

## Nonprofit AI adoption workspace (build 0.31 in review)

Open **AI enablement**, enter your organisation goal and team readiness, and select **Assess readiness**. In **Find and compare tools**, search or filter products and select up to four for comparison. Inspect source links and the checks needed for your actual subscription.

Use **Build team capacity** to read twelve lessons, try synthetic exercises and answer self-checks. Completion is self-recorded. Older saved progress is matched to stable lesson meanings. When you reopen a plan, **Saved guide compatibility** shows whether its guide and tool-directory editions are current, stale or unknown. You are reading current guidance; older guide text is not archived. Reading a plan does not rewrite its stored revision. Unavailable progress is named rather than counted as completion. Review it and choose **Remove unavailable progress from this draft** before saving a new revision; the historical saved revision remains unchanged.

In **Practise a useful task**, select a community invitation, fictional grant summary, invented meeting actions or fictional supplier questions. Read the input boundary, synthetic example and prompt framework. Write your own brief and draft, then add review notes and check the steps you actually performed. This worksheet makes no AI request; a completed checklist does not certify competence or approve the output. Each text field allows up to 2,500 characters. One worksheet is stored with the plan.

**Saved practice edition** shows Current, Stale or Unknown. Older guidance wording is unavailable, so review your saved work against the current guide. If a saved task has been removed, your exact entered text and checked-step identifiers stay visible read-only. With management permission, choose a replacement and **Replace missing task and keep text**; all three text fields are retained and checks reset for fresh review. Alternatively, **Clear saved practice worksheet** removes it from this draft. Resolve the unavailable task before saving. A read-only colleague can inspect the preserved worksheet but cannot replace or clear it.

In **Procurement brief**, edit requirements, permitted data, budget assumptions and supplier questions. Under **Compare supplied costs**, add a comparison using amounts from your own sources: one currency, a period of 1–60 whole months, up to four offers and up to twenty lines per offer. Add one-off and monthly setup, subscription, usage, integration, training, review, support and exit costs. Leave an unknown unit amount blank; it remains unknown even with a zero quantity. Choose **Calculate supplied costs** to inspect the known subtotal and any missing lines. No complete total or cheapest indication is asserted while an offer is incomplete. Complete equal totals retain ties. The platform supplies no quote or exchange rate and makes no purchasing decision.

In **Pilot tracker**, define a success measure and record practical actions. Under **Evaluate a pilot**, enter the baseline and pilot sample counts, total drafting minutes, total human review minutes and factual corrections. State whether the tasks are comparable and add notes explaining the limits. Choose **Calculate pilot comparison**. Staff time includes review and is normalized per item. Zero baseline time or samples reported incomparable produce an undefined percentage. Results remain self-reported drafts; they do not prove quality, causal benefit, ROI, accepted impact or independent pilot acceptance.

With management permission, name and **Save adoption plan**. The brief, shortlist, learning progress, procurement/pilot notes and optional original planning inputs save together. Calculation results are temporary; reopening restores the source inputs so you can calculate again. Correct an invalid planning input or clear that optional section before saving. A read-only colleague can inspect saved source inputs and calculate them, but cannot save edits or change recorded progress/checks.

Choose a plan from the saved-plan list to reopen it, including after a page reload. A lost save response can be retried as the same pending operation; newer edits remain visible. If someone else changed the plan, review the latest saved version before a new save. Plans are drafts shared with authorised organisation staff. Keep beneficiary information, credentials and private case files out of these working notes.

Buying tools, booking advisers, supplier verification, RFQ dispatch, competency certification, connectors and payments remain future work. AI-generated advisory drafts still require separate permission, explicit consent, server configuration and a funded provider project. Costs, pilot calculations, learning and manual practice work without requesting an AI draft. If advisory is unavailable, these planning tools remain available under your normal permissions.
