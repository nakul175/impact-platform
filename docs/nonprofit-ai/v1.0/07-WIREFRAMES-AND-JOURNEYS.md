# Nonprofit AI Enablement Wireframes and Journeys

Edition 1.0   5 October 2026   Proposed design baseline

This document connects the BRD and FSD to twelve reviewable screen concepts. The standalone clickable wireframe is wireframes/index.html. It shows an organisation-specific nonprofit enablement hub with readiness, comparison, learning, procurement, advice, delivery and operation. Its temporary working name AI for Good is a concept, not an approved brand.

## Status and review boundary

The persistent yellow banner states that the wireframes are proposed, not deployed, and use synthetic data. R1 labels identify capabilities in the build 0.30.0 review branch at commit 36073f1; layouts are proposed rather than screenshots of that product. R2 labels identify future operated services. Purchasing and payments remain conditional R3 and have no form or executable action.

All organisations, people, suppliers and directory entries in the prototype are invented. Fictional entries deliberately carry no actual vendor claims, links, prices, discounts or certifications. The current product's separate eight-product source-backed catalogue remains described in the release baseline. No prototype message, booking, purchase, publication, export, provider generation or connection is real.

Interactive state lives only in browser memory and disappears on reload or Reset demo. The prototype uses no API, provider call, analytics, external font or local/browser storage. A simulated save demonstrates receipt and conflict behaviour; it does not persist to the platform. Fixed demonstration output in the workbench is explicitly labelled as not generated.

## Information architecture

The organisation workspace presents twelve areas in one navigation shell. The current organisation is explicit, actions use plain language, each screen names its phase and screen identifier, and every meaningful decision retains a responsible human. In the product implementation, capability-filtered navigation and independent server authorisation must replace the prototype's illustrative role control.

The journey moves from Describe to Assess, Compare, Learn and Pilot. Target operation adds coordinated capacity, human advisory, supplier offers, independent decisions, delivery acceptance, connections, incidents and outcomes. People can return to a shared draft without having to finish every step in one session. Readiness, directory and lessons remain usable when AI generation is unavailable.

| Screen ID | Area and principal objects | Baseline and target distinction | Functional links |
|---|---|---|---|
| WF-NPA-001 | Organisation profile, readiness and use cases | R1 deterministic self-report guidance; proposed layout; no numeric readiness score | FR-NPA-001, FR-NPA-002, FR-NPA-003, FR-NPA-028, FR-NPA-035, FR-NPA-037 |
| WF-NPA-002 | Tool discovery, comparison and shortlist | R1 current directory/comparison capabilities; fictional prototype entries; future verified supplier evidence separate | FR-NPA-004, FR-NPA-005, FR-NPA-018, FR-NPA-028, FR-NPA-031, FR-NPA-038 |
| WF-NPA-003 | Shared AIAdoptionPlan draft and revision recovery | R1 shared server plans exist; prototype save is temporary; history/export/archive/delete UI absent | FR-NPA-006, FR-NPA-025, FR-NPA-027, FR-NPA-029, FR-NPA-037, FR-NPA-039 |
| WF-NPA-004 | Lessons, exercises and self-checks | R1 twelve lessons in product; three sample lessons in prototype; completion not competency | FR-NPA-007, FR-NPA-028, FR-NPA-031, FR-NPA-038 |
| WF-NPA-005 | LearningProgramme, Cohort, LearningAssignment, CompetencyAssessment | R2 coordinator and assessor workflow; proposed rubric, privacy and independence policy | FR-NPA-008, FR-NPA-009, FR-NPA-025, FR-NPA-026 |
| WF-NPA-006 | Editable procurement notes in AIAdoptionPlan | R1 draft requirements, boundary, budget notes and questions; no send or award | FR-NPA-013, FR-NPA-026, FR-NPA-035, FR-NPA-037 |
| WF-NPA-007 | ProcurementRequest, SupplierQuote, CostComparison, ProcurementDecision | R2 RFQ and independent decisions; all costs unknown; no financial instruction | FR-NPA-014, FR-NPA-015, FR-NPA-016, FR-NPA-018, FR-NPA-019, FR-NPA-035 |
| WF-NPA-008 | HumanAdvisoryCase and separate AI advisory availability | R2 human service; R1 AI draft consent/current authority pattern; live generation currently blocked by credits | FR-NPA-010, FR-NPA-011, FR-NPA-023, FR-NPA-026, FR-NPA-029, FR-NPA-035 |
| WF-NPA-009 | TaskTemplate and TaskRun | R2 approved templates, input boundary and draft review; fixed missing-fact illustration only | FR-NPA-012, FR-NPA-023, FR-NPA-026, FR-NPA-035 |
| WF-NPA-010 | Pilot actions, DeliveryMilestone, Engagement, AdoptionOutcome | R1 self-recorded actions; R2 exact delivery evidence and independent acceptance; no fabricated savings | FR-NPA-019, FR-NPA-021, FR-NPA-024, FR-NPA-034, FR-NPA-035 |
| WF-NPA-011 | SupplierSubmission and PublishedSupplierSnapshot | R2 private onboarding and separately approved public projection; unpublished synthetic entry | FR-NPA-017, FR-NPA-018, FR-NPA-025, FR-NPA-026, FR-NPA-031 |
| WF-NPA-012 | SupportCase, ConnectorBinding, export and financial gate | R2 support/connection/portability; R3 payments unavailable; operations/release remain separately qualified | FR-NPA-020, FR-NPA-022, FR-NPA-025, FR-NPA-026, FR-NPA-030, FR-NPA-032, FR-NPA-033, FR-NPA-034, FR-NPA-036, FR-NPA-040 |

Cross-cutting FR-NPA-025 through FR-NPA-029 and FR-NPA-035, FR-NPA-037 through FR-NPA-040 also constrain every applicable screen. A screen mapping does not prove that access, encryption, release or database controls are implemented. FR-NPA-036 reuse and FR-NPA-040 release evidence have no dedicated user decision screen; they constrain the whole package and its release review.

## Journey A Organisation first pilot

An adoption lead begins at WF-NPA-001 with a sector, team size, bounded goal, data readiness, AI experience and sensitive-data flag. Required fields have visible labels and limits. Editing the profile clears the prior readiness interpretation. Assessment shows reasons and next responsible steps, with a foundation step or data review when relevant, rather than promising readiness certification or savings.

At WF-NPA-002 the lead searches and filters the dated directory, adds up to four tools and reads common comparison attributes. Unknown costs, terms, API entitlements and eligibility remain visible. The organisation adopts no endorsed ranking. If nothing matches, the screen gives a recoverable empty state without disclosing hidden-record counts.

The lead practises at WF-NPA-004, reads a short lesson, completes a synthetic exercise and checks an answer. Recording completion changes self-reported progress only. The organisation prepares a common brief at WF-NPA-006, defines a success measure and pilot actions at WF-NPA-010, then saves one named shared draft at WF-NPA-003. Real server plans reopen with the profile, shortlist, progress, brief and pilot notes; the prototype explicitly simulates this in memory.

A read-only staff member can inspect the plan and editorial guidance but cannot change shared completion, procurement notes or a plan. UI restrictions support clarity; the API independently rechecks the current capabilities and scope.

## Journey B Recover a save safely

A successful current product save returns the exact committed revision and operation receipt. While a save is pending, the UI preserves the original request and operation ID. If the response is lost, an exact retry replays the original result after current authority checks. Newer edits remain unsaved rather than being discarded by that replay.

The prototype provides Simulate lost response in WF-NPA-003. Change the title after the simulated unknown outcome, then choose Simulate draft save: the original demo revision is reconciled while the newer title remains. This models the user-facing interpretation only; it does not prove SQL idempotency or concurrency.

A stale revision shows a clear conflict and preserves the edits. A native dialog describes the recovery; Escape closes it and returns focus. The user reviews the latest version and reconciles a new operation rather than silently overwriting. Service failure also preserves input. An in-flight AI claim is a separate outcome requiring investigation; it must not offer an automatic second generation that could spend again.

## Journey C Operated capacity building

WF-NPA-005 adds a coordinator-defined LearningProgramme and Cohort, scoped LearningAssignments and a CompetencyAssessment. The learner sees their own work and approved sharing boundaries. The assessor receives exact evidence and a versioned rubric and may assess or request remediation. Competency state is distinct from lesson completion.

The proposed rubric illustrates factual accuracy, supporting evidence, allowed data and accessible output. It is not an approved certification standard. DEC-NPA-008 must settle the standard and assessor independence; DEC-NPA-009 must settle learner evidence retention and visibility. Numeric cohort targets, pass scores, certification labels and assessor identities remain unapproved.

## Journey D Comparable offers and independent decisions

WF-NPA-006 provides draft requirements and acceptance tests. R2 WF-NPA-007 binds a ProcurementRequest to the exact reviewed brief and named recipients. An independent disclosure review must authorise the precise contents and audience before issuance. An outbox row is an intent; the screen separately records actual delivery evidence.

SupplierQuote responses retain validity, currency, period, inclusions, exclusions, cost components and evidence. The comparison separates setup, recurring, usage, training, review, support and exit. Missing amounts remain unknown and prevent a complete asserted total. Different currencies without an approved conversion rule are not comparable. The prototype includes no monetary amount, price feed, cheapest-supplier claim or implicit exchange rate.

A ProcurementDecision binds exact quote and comparison revisions. The requester cannot approve through another account linked to the same natural person. The demonstration refuses Person A; Person B passes one illustrative independence check but still receives a message that authority, conflicts, exact evidence and offer completeness remain unresolved. No approval or purchase occurs. DEC-NPA-007 supplies the actual policy and thresholds before implementation.

An Engagement agrees parties, scope, terms, milestones and cancellation policy. External acceptance must be evidence rather than inferred from a booking intent. Payments are conditional R3 after DEC-NPA-004 and DEC-NPA-015; no payment form is present.

## Journey E Human advice and AI assisted work

WF-NPA-008 captures a HumanAdvisoryCase with problem, scope, named material and sharing boundary. Assignment requires a named competent adviser and reviewed conflicts under DEC-NPA-006. The adviser can provide advice and actions but cannot approve the organisation's purchase or disclose unrelated records. Closure records the organisation's decision rather than automatic endorsement.

The separate current AI advisory draft requires current read and advisory capabilities plus explicit consent to send the submitted profile and deterministic assessment. It has bounded claim frequency and sealed replay. The selected provider currently has exhausted credits. The preview unavailable state explains that planning and learning remain usable and makes no provider request.

R2 WF-NPA-009 uses a reviewed TaskTemplate with closed input fields, purpose, output checks and human reviewer. TaskRun remains a draft and cannot send messages, publish outputs, spend money, decide eligibility, deploy an integration or compute official impact numbers. Fixed prototype text demonstrates a clarification when the date or venue is missing. It is visibly not generated content.

## Journey F Delivery outcomes and responsible operation

WF-NPA-010 separates a self-recorded R1 action list from proposed DeliveryMilestone acceptance. A target milestone pins scope, evidence, expected tests and an independent natural person. Approved terms or a completed tick do not establish delivered work. Scope changes create a new version and decision.

AdoptionOutcome records comparable baseline and pilot tasks, period, drafting and review effort, corrections, accessibility evidence and uncertainty. Unknown benefits remain unmeasured. Any official impact result uses approved deterministic source snapshots; narrative drafting does not replace that calculation. Feedback is optional, minimised and consented, and does not silently train private records into recommendations.

WF-NPA-012 introduces scoped support intake, explicit incident ownership, pause/recovery and least-privilege ConnectorBinding review. Credentials are server-side references, never user-entered secrets in business notes. A synthetic trial precedes active integration. Export needs its own current authority, exact version context and audit. Current plan history browsing, export and deletion screens are absent; AI retention/removal, holds and backup limitations need DEC-NPA-009.

## Journey G Private supplier intake to public snapshot

WF-NPA-011 records a private SupplierSubmission with attributable claims, supporting evidence and commercial relationships. Independent review checks the exact material and proposed public fields. PublishedSupplierSnapshot is a separate minimised approved projection with verification scope, date/expiry and placement basis.

Private identity and onboarding documents remain private. Publication cannot query private supplier evidence across tenants. Verification means the stated evidence was checked, not blanket supplier certification. Undeclared conflicts or missing evidence block publication. Operator/revenue/placement policy remains DEC-NPA-004 and verification scope remains DEC-NPA-005.

## Interaction and state specification

| State | Visible response | Required product behaviour |
|---|---|---|
| Initial | Goal/profile labels, guidance, phase banner, no commitment | Current scoped read; no automatic provider call |
| Profile changed | Prior assessment cleared; assess again | Prevent stale assessment/advisory interpretation |
| Empty | No matching tools or no visible records; clear next step | Do not expose hidden rows or total counts |
| Invalid | Specific field/limit message; retain input | Closed typed DTO, no unknown members or duplicate keys |
| Read-only | Explanation and disabled save/completion/brief controls | Current API denies writes independently of buttons |
| Saving / outcome unknown | Original operation and payload retained | Exact retry after current authority; no duplicate revision or spend |
| Stale revision | Conflict explanation; edits preserved | CONFLICT_VERSION; no automatic overwrite |
| Dependency unavailable | Plain error and preserved draft | Planning remains available without generation |
| AI in flight | Explain investigation and prior claim | No blind automatic provider replay |
| Consent absent | Input-specific boundary required | No provider or adviser disclosure |
| Self-approval | Natural-person independence refusal | No alias or second account workaround |
| Missing quote fields | Unknown and incomplete comparison | No invented zero, rate, benefit or complete total |
| Unpublished supplier | Evidence/independent review pending | No public join to private intake |
| Export or payment gate | Separate permission/policy required; unavailable | No read-implies-export; no financial effect from a draft |

## Accessibility and responsive design

Use a skip link, semantic navigation, one current-page indication, meaningful heading order, persistent field labels and native input types. Controls have visible keyboard focus and at least forty-four-pixel intended target height. Labels identify data boundaries before text entry. Status/error messages use live regions, and the dialog uses native modal focus and Escape behaviour. Colour supports meaning and does not carry it alone; phase and state have text labels.

At a narrow viewport the navigation becomes a compact grid and cards stack. Comparison attributes remain readable as per-tool cards. Tables use a contained horizontal region rather than widening the whole page. No global horizontal scrolling or clipped form field is permitted. Input history, error recovery, focus return, screen-reader messages, zoom and intended-user language still need manual product qualification; an automated scan alone is insufficient.

The prototype removed opacity/colour navigation animation after an automated scan exposed transient contrast failures. The stable final design is checked without exemptions. Product implementation must use the existing shared Dialog and root design tokens, preserving accessible behaviour and avoiding a separate component system.

## Prototype verification and limitations

wireframes/wireframe-validation.json records 78 passing local checks in installed headless Chrome on macOS using Playwright 1.58.0. All twelve screens were exercised at widths 1440 and 390 pixels for containment and current navigation. Checks covered local readiness/invalidated assessment, search/filter/empty results, four-tool limit, lesson self-check/progress, demo save/lost-response reconciliation, conflict dialog/Escape, read-only controls, self-approval refusal, consent/no-send, unavailable AI and fixed missing-fact handling. There were zero script errors and zero outbound requests.

Automated axe-core 4.13.0 scans of all twelve concept screens reported no WCAG 2 A/AA or WCAG 2.1 AA violations in the final local run. This is prototype evidence, separate from the production React browser evidence. Desktop/mobile previews are desktop-preview.png and mobile-preview.png; mobile-comparison-preview.png shows the readable comparison stack. These checks do not qualify the API, database, real identity, native concurrency, release gates, full screen-reader support or UAT. They do not promote acceptance.

## Handoff and traceability

Implement only owner-approved scope from the FSD and resolved decisions. Translate screens into existing product components, separate proposed from current capabilities, recheck every boundary on the server and preserve synthetic fixtures. Use the data dictionary for exact current DTO fields and proposed logical entity names. Update screen links, tests and decisions together when a workflow changes.

References: 01-BRD.md; 02-FSD.md; requirements.json; 08-DATA-DICTIONARY.md and data-dictionary.csv; 09-SECURITY-AND-PRIVACY.md; 11-DECISIONS-AND-RISKS.md; the test package; docs/RELEASE-0.30-ai-adoption-tool.md and existing platform instructions. Documents and wireframes are review artefacts, not an approval to disclose, purchase, deploy or process beneficiary personal information.
