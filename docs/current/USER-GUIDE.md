# Impact Platform user guide

Documentation 1.1 applies to application 0.12.0; build 0.13.0 added the administrator-only authority renewal described in the administrator guide, build 0.14.0 (native PostgreSQL qualification) changes no user workflow in this guide, build 0.15.0 qualifies sign-in, step-up and sign-out through a live identity provider (below), and build 0.16.0 adds background delivery: notices reach the work centre through the worker, invitations are also emailed, and a nominated recovery contact can confirm their email address with a code (below), and build 0.18.0 adds the results framework, targets and the targets-versus-actuals view (below). This guide covers the implemented development application. It does not describe a production-approved service. Screens show only actions permitted by current server authority; having a visible record does not authorize its approval, export or publication.

## Sign in and select a workspace

1. In the local environment, use the generated account credentials supplied by the authorized developer. The development sign-in is limited to loopback and uses synthetic identities.
2. Select the intended workspace from the tenant selector. Confirm the workspace before entering or approving data.
3. If a workspace or action is missing, ask its authorized administrator to review your membership and explicit grants. Switching roles or knowing a URL does not create authority.
4. Use Account settings to view preferences and your sessions. Sign out when finished. Session revocation requires fresh configured assurance. With a live identity provider, signing out also ends your provider session: the browser visits the provider and returns to the front page.

Local sign-in proves the development workflow only. With a live identity provider (qualified since build 0.15.0 against a test Keycloak), Sign in sends you to the provider for your password and then a one-time code from your authenticator app; actions that need fresh assurance are accepted for five minutes after that sign-in, after which the platform asks you to sign in again. If your account has no second factor the provider asks you to set one up first. The provider your organisation will use, MFA enrolment and unavailable-account recovery remain release gates.

## Establish a programme and measurement plan

1. Obtain explicit programme-management authority through the reviewed access flow. Tenant ownership alone does not provide it.
2. Create the programme with the fields shown in the setup form. Save and wait for the server's successful-save confirmation.
3. Create the manual indicator definition, including unit, calculation method and precision. Current support is bounded to FLOW measures with SUM or pooled ratio/percentage calculations.
4. Submit the definition for independent review. The material author cannot approve it through another account belonging to the same natural person.
5. Create the measurement plan and its collection obligations and responsibility assignments. Review the intended period and source requirements before submission.
6. An eligible independent reviewer approves the exact candidate revision. Activate only when readiness checks pass.

The source's definition, unit, period and precision govern interpretation. Missing data is different from a present zero. A later definition or plan change follows a reviewed amendment; it does not silently rewrite prior approved data.

## Build the results framework and set targets

Open **Results framework** and choose the programme. You need the framework and target draft capabilities to edit, a separate reviewer to approve, and `targets.read` to see progress.

1. On **Framework**, create the draft: add impact, outcome, output and activity nodes, give each a title, description and owner, place a parent at the same or a higher level, and place each programme indicator on one node. Renaming a node keeps its identity and its indicators.
2. Saving refuses a structure that cannot be valid — a cycle, a parent that is not in the framework, a child above its parent, an indicator placed twice or from another programme. Correct the named node; these cannot be excepted.
3. Read the **Completeness review**. Each issue shows severity, rule, object and the person assigned to resolve it. Resolve errors. A warning (for example an output with no indicator, or a programme indicator not placed) can be accepted with **Document exception**: give a reason and a review date that is not in the past. The platform records who documented it and when.
4. Submit when nothing is unresolved. An eligible reviewer who is a different person opens **Reviews**, re-reads the exact candidate with its completeness report, and approves, returns or rejects it. Approval freezes baseline 1; its exceptions stay visible in it.
5. To change an approved framework, create a new draft from it with an effective date after the previous one. The review shows what changed; the earlier baseline keeps its approved wording and governs the periods before the new date.
6. On **Targets**, create per indicator and period a target (a value, a range, or a milestone with a label and due date), a baseline, or both, with the direction (higher, lower, within range, milestone) and a value state — a blank target is recorded as missing, never as zero. Submit it for independent review. To change an approved target or correct a baseline, create a revised one that names the approved one and gives a reason; the original stays on record.
7. **Targets vs actuals** shows each target, baseline and milestone beside the actual and its source. An official actual appears only from this programme's own locked snapshot; before close the actual is provisional. Attainment is not capped, a lower-is-better target shows its signed deviation, and a zero target or a zero or negative baseline shows Undefined rather than a percentage. Use **Load more** for further indicators.

Closing a period freezes its approved targets and the framework that governed it; a locked period accepts no new or revised target. Status thresholds, disaggregated and cumulative targets, theory-of-change relationships and charts are not available in this build, and a programme without a reporting calendar cannot carry targets.

## Enter and review observations

1. Open the assigned collection obligation in the correct programme and period.
2. Enter the requested value or numerator and denominator as ordinary decimal input. Do not use exponent notation or append a percent sign to a numeric field.
3. Confirm the source reference and contextual fields, then save. A local entry or loading message is not a server receipt.
4. Submit the candidate for review. An eligible independent reviewer inspects its exact content and evidence, then approves, returns or rejects it.
5. Address a returned candidate in a new reviewed revision. Approved values and their earlier lineage remain immutable.

Unplanned sources are visible in coverage but do not silently enter the official denominator or result lineage. A missing obligation requires collection or an explicitly reviewed exception. All obligations cannot be removed through exceptions.

## Calculate and inspect lineage

Run the permitted calculation for the programme, indicator and period. Inspect the source contributions, exclusions, unit, precision and result state. A pooled percentage is calculated from summed numerators divided by summed denominators; it is not an average of displayed percentages. Rounding is applied once at the defined display boundary.

A provisional result may become stale after an approved source or plan changes. The work centre shows the assigned recalculation task and a safe notice. Acknowledging the notice does not complete the task. Recalculation creates a replacement result and resolves the relevant invalidation while preserving prior history. Since build 0.16.0 each notice is delivered to your work centre once by the background worker, and administrators of delegated authority also receive notices 14 and 3 days before it expires; no notice is sent by email, SMS or push.

If you are nominated as a tenant's recovery contact, you can confirm your email address after verifying the nomination: choose **Email me a verification code**, enter the address of your registered account, then **Enter verification code** with the eight-digit code from the email within 15 minutes (five wrong attempts lock the code; at most three codes per hour). The confirmation is recorded as evidence only and gives you no access. In development the email goes to a local file, never to a real mailbox.

## Close a period and restate it

1. Open the close preview and review missing, pending, invalid, rejected or unplanned sources and plan readiness.
2. Resolve blockers through the normal source and review workflows. Recreate the preview if any input changes.
3. An eligible independent reviewer approves the pinned preview. Successful close creates official result revisions and a locked snapshot atomically.
4. A locked period rejects ordinary new submissions, corrections and recalculation.
5. A correction after close requires an independently approved, time-bounded restatement covering named sources from the latest snapshot. Close again to create a superseding snapshot.

Do not edit an old official number to make it agree with a later correction. The earlier snapshot remains historical evidence.

## Prepare an internal report

Choose an approved report template and the intended locked snapshot. Bind numeric narrative placeholders to permitted immutable result revisions. Supply required sections and evidence bindings, then submit for independent approval. Bare unsupported numeric claims are rejected; narrative editing cannot overwrite a bound official value.

The approved package freezes its selected versions. Later live recalculation does not change its numbers. Current output formats are authenticated semantic HTML and spreadsheet-safe CSV. PDF, DOCX and XLSX reporting exports are not implemented.

## Publish to named recipients

1. Propose disclosure of one approved report revision with an explicit purpose, expiry and named active recipients.
2. Set download permission separately for each recipient. Review the exact candidate with an eligible independent approver.
3. Publication rechecks current recipient authority and freezes the approved HTML/CSV artifacts.
4. A recipient must still have current permitted access to view or download. Expired, withdrawn, inactive and unlisted access is unavailable.
5. Withdraw an incorrect disclosure through the authorized action and retain its audit history.

There is no anonymous public link or external message delivery in this build. Withdrawal prevents future controlled access; it cannot recall bytes already downloaded.

## Handle errors without losing evidence

| Outcome | Required action |
| --- | --- |
| Validation error | Correct the named field; retain the rest of the draft |
| Revision conflict | Reload the current record and review the differences before resubmitting |
| Uncertain network outcome | Reconcile the saved operation or retry the identical command; do not duplicate it with a new operation identifier |
| Access unavailable | Check workspace, current membership, grant, scope, purpose and tenant state with the authorized administrator |
| Fresh authentication required | Sign in again through the configured identity flow; a refreshed token issue time alone is insufficient |
| Stale result | Complete the assigned recalculation workflow; acknowledging a notice is insufficient |

## Current exclusions

The full form designer/runtime, Android offline collection, generalized ingestion, evidence-file processing, evaluation, participant case management, finance, rich analytics, live integrations and AI assistance remain incomplete or pending. A placeholder, object read route or proposed wireframe is not an available operational workflow. See the current FSD, implementation profile and requirement ledger for the exact boundary.
