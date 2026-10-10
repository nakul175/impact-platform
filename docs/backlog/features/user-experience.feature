# Imprana Commons backlog: User experience
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: User experience

  Rule: FR-UX-001 Role relevant workspaces
    As a Field Data Collector, I want to land in a workspace matched to my role and recent permitted context and switch among my permitted workspaces, so that I can reach my assigned work quickly without dealing with technical administration.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-UX-001 @R1-Pilot @Must
    Scenario: New enumerator opens an assigned form
      Given a new Field Data Collector with an assigned form
      When they open their landing workspace
      Then they can open the assigned form in two primary navigation actions
      And they see its due time, save status and sync requirement

    @FR-UX-001 @R1-Pilot @Must
    Scenario: Landing workspace follows effective role
      Given users with different effective roles
      When each user signs in
      Then collectors see assignments, reviewers see queues, managers see obligations and viewers see disclosed results
      And each user can switch among their permitted workspaces

    @FR-UX-001 @R1-Pilot @Must
    Scenario: Reject technical administration as a prerequisite for collection
      Given a Field Data Collector with an assigned form
      When they start collecting data
      Then no technical administration step is required or shown as a prerequisite

    @FR-UX-001 @R1-Pilot @Must
    Scenario: Reject stale private links after a role change
      Given a user whose role has changed
      When navigation is recomposed
      Then no stale private links from the previous role remain

  Rule: FR-UX-003 Error recovery and work preservation
    As a Data Author, I want errors to explain what failed, what was saved and what I can do next, with drafts and operation IDs kept across recoverable failures, so that I never lose work or repeat an action by accident.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-UX-003 @R1-Pilot @Must
    Scenario: Recover an import receipt after a timeout
      Given an import confirmation that timed out
      When the Data Author reconnects
      Then the existing job receipt is recovered
      And no additional load is created

    @FR-UX-003 @R1-Pilot @Must
    Scenario: Destructive actions preview and reversible changes offer an inverse
      Given a destructive action
      When the Data Author starts it
      Then the affected objects are previewed
      And reversible changes offer an explicit inverse operation where business semantics support it

    @FR-UX-003 @R1-Pilot @Must
    Scenario: Reject undo that rewrites history
      Given a change that was audited, downloaded externally or lawfully deleted
      When undo is used
      Then the audit is not erased
      And externally downloaded copies are not treated as unpublished
      And lawfully deleted data is not restored

    @FR-UX-003 @R1-Pilot @Must
    Scenario: Reject repeating a request with an unknown outcome
      Given a request whose outcome is unknown
      When the Data Author tries to repeat it
      Then receipt reconciliation is required before the repeat proceeds

  Rule: FR-UX-004 Accessible interaction
    As a Data Author, I want every supported control to work with keyboard and screen reader, with labels, visible focus, understandable errors and announced status changes, so that I can complete my work regardless of disability.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-UX-004 @R1-Pilot @Must
    Scenario: Complete core work with keyboard and screen reader
      Given a Data Author using a keyboard and a qualified screen reader
      When they complete collection, correction and approval
      And they encounter an invalid field and a stale revision conflict
      Then every step is completed with accessible labels, visible focus and understandable errors

    @FR-UX-004 @R1-Pilot @Must
    Scenario: Alternatives for drag actions, charts and async changes
      Given a drag action, a chart and an asynchronous state change
      When they are used without a mouse or sight
      Then the drag action offers buttons or ordered lists
      And the chart offers a table
      And the state change is announced without unexpectedly moving focus

    @FR-UX-004 @R1-Pilot @Must
    Scenario: Reject inaccessible authentication
      Given a Data Author signing in
      When authentication presents a challenge
      Then password managers are supported
      And an accessible alternative to the challenge is available

    @FR-UX-004 @R1-Pilot @Must
    Scenario: Reject waiving conformance because of user content
      Given user-supplied content with accessibility limitations
      When conformance is assessed
      Then the limitations are reported
      But product process conformance is not waived

  Rule: FR-UX-005 Responsive operation
    As a Field Data Collector, I want core screens to work on a 360 CSS pixel wide mobile display with readable fields and reachable actions, so that I can complete my work from a phone in the field.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-UX-005 @R1-Pilot @Must
    Scenario: Complete core tasks on the supported mobile profile
      Given the supported mobile profile at 360 CSS pixel width
      When a user completes a form, reviews evidence and returns a submission
      Then ordinary fields do not depend on horizontal scrolling

    @FR-UX-005 @R1-Pilot @Must
    Scenario: Wide tables and dense configuration on mobile
      Given a wide analysis table and a dense configuration screen
      When they are opened on mobile
      Then the table offers labelled scrolling or a simplified view without hiding critical meaning
      And the configuration screen declares its desktop requirement before editing begins

    @FR-UX-005 @R1-Pilot @Must
    Scenario: Reject hover-only or clipped actions
      Given any core mobile screen
      When it is used on the supported mobile profile
      Then no essential action is hover-only
      And no submit button is clipped

    @FR-UX-005 @R1-Pilot @Must
    Scenario: Reject state loss on orientation change
      Given a draft in progress with a pending confirmation
      When the device orientation changes
      Then the draft, focus context and confirmation state are preserved

  Rule: FR-UX-006 Language and locale
    As a Data Author, I want to work in my own display language and locale while source locale and programme reporting zone govern interpretation, so that changing language never changes the meaning of dates, amounts or periods.
    Release: R1 Pilot · Priority: Should · Built today: Absent

    @FR-UX-006 @R1-Pilot @Should
    Scenario: Decimal-comma value survives locale changes
      Given an import of 1,25 under a decimal-comma locale
      When it is viewed in a decimal-point locale and then exported
      Then the underlying value stays 1.25

    @FR-UX-006 @R1-Pilot @Should
    Scenario: Unicode content survives export and search
      Given Unicode labels, names and codes
      When they are exported and searched
      Then they are preserved unchanged

    @FR-UX-006 @R1-Pilot @Should
    Scenario: Reject ambiguous imports without explicit handling
      Given an import with ambiguous date or decimal formats
      When no explicit handling has been chosen
      Then the import does not proceed

    @FR-UX-006 @R1-Pilot @Should
    Scenario: Reject recalculation on display language change
      Given recorded dates, amounts and period membership
      When the Data Author changes display language
      Then none of them is recalculated
      And stable codes remain separate from translated labels

  Rule: FR-UX-009 Status and trust cues
    As a Data Author, I want consistent status labels distinguishing local save, received, validating, approved, published, stale, partial, suppressed and AI proposed, so that I always know the true state of my work.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-UX-009 @R1-Pilot @Must
    Scenario: Large file shows separate processing stages
      Given a Data Author submits a large file
      When it is processed
      Then separate receipt, validation, review and calculation stages are shown
      And no published result appears prematurely

    @FR-UX-009 @R1-Pilot @Must
    Scenario: Job receipt shows the current stage
      Given a background job in progress
      When the Data Author views its receipt
      Then the receipt names the current stage
      And it shows complete only after the actual completion event

    @FR-UX-009 @R1-Pilot @Must
    Scenario: Reject success cues that overstate status
      Given an action that was saved but not approved or externally delivered
      When its outcome is shown
      Then a generic green success banner does not imply approval or external delivery
      And numeric badges include text equivalents and uncertainty states

  Rule: VF-UX-001 Accessibility conformance
    As a Data Author, I want all core journeys to be fully accessible, so that I can complete my work using a keyboard or assistive technology.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @VF-UX-001 @R1-Pilot @Must
    Scenario: Core journeys meet WCAG 2.2 Level AA
      Given a supported core journey, including complete processes, third-party authentication flows under product control and generated standard templates
      When it is reviewed with automated checks and manual keyboard, screen reader, focus and error tests
      Then it meets WCAG 2.2 Level AA

    @VF-UX-001 @R1-Pilot @Must
    Scenario: Material issues are recorded with evidence
      Given a material accessibility issue is found
      When it is recorded
      Then the environment, user-content boundaries and remediation evidence are captured

    @VF-UX-001 @R1-Pilot @Must
    Scenario: Reject a clean automated scan alone
      Given a journey passes automated accessibility checks
      When manual keyboard and assistive technology review has not been completed
      Then the journey does not pass

  Rule: FR-UX-002 Progressive configuration
    As a Programme Manager, I want to set up a programme from a simple template with advanced settings revealed only in relevant steps and all defaults shown for review before submission, so that I know exactly how results will be calculated and shared.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-UX-002 @R2-Scale @Should
    Scenario: Template programme shows its rules
      Given a simple programme created from a template
      When the Programme Manager inspects it
      Then the exact sum rule and reporting calendar that produce its first result are shown

    @FR-UX-002 @R2-Scale @Should
    Scenario: Defaults are visible and editable before submission
      Given the Programme Manager reaches the final setup summary
      When they review it
      Then defaults for units, periods, aggregation, consent and audience are visible
      And each can be edited before submission

    @FR-UX-002 @R2-Scale @Should
    Scenario: Reject hidden defaults
      Given a programme created from a template
      When its settings are applied
      Then there is no hidden automatic unique reach, broad sharing or assumed consent

    @FR-UX-002 @R2-Scale @Should
    Scenario: Reject progression with invalid defaults
      Given a setup step containing an invalid default
      When the Programme Manager tries to continue
      Then progression is blocked
      And no superficially complete programme is created

  Rule: FR-UX-008 Discoverability and help
    As a Data Author, I want permission-aware search, recent work, saved views and context help explaining measurement states, approval blockers and recovery actions, so that I can find and fix my work without administrator help.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-UX-008 @R2-Scale @Should
    Scenario: Resolve a pending approval without help from an administrator
      Given an indicator assigned to the Data Author with approval pending
      When they search for it
      Then they find it, identify why approval is pending and reach the required evidence task without administrator intervention

    @FR-UX-008 @R2-Scale @Should
    Scenario: Notification leads to the exact issue
      Given a safe task notification
      When the Data Author follows it
      Then they reach the exact permitted object and issue
      And help examples use synthetic data without revealing implementation secrets

    @FR-UX-008 @R2-Scale @Should
    Scenario: Reject results beyond current permissions
      Given an item the Data Author is no longer permitted to see
      When they use search, recent work or saved views
      Then the item does not appear

    @FR-UX-008 @R2-Scale @Should
    Scenario: Reject silent rebinding of a saved view
      Given a saved view bound to a retired definition
      When it is opened
      Then a reviewed rebinding is prompted
      But its meaning is not silently changed

  Rule: FR-UX-010 Usability evidence
    As a Product Owner, I want usability qualification with representative roles and accessibility needs that measures completion, time and consequential errors, so that failures are prioritised by data loss, disclosure and incorrect official result risk.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-UX-010 @R2-Scale @Should
    Scenario: Run the BRD core tasks with representative participants
      Given at least fifteen representative participants covering roles and accessibility needs
      When they perform the six BRD core tasks after standard onboarding
      Then completion, time and consequential errors are measured
      And the completion threshold and every critical error resolution are documented

    @FR-UX-010 @R2-Scale @Should
    Scenario: Failures are prioritised by risk
      Given failures observed during qualification
      When they are triaged
      Then they are prioritised by data loss, disclosure and incorrect official result risk

    @FR-UX-010 @R2-Scale @Should
    Scenario: Reject downgrading critical defects or counting facilitated completion
      Given a critical workflow defect and a task completed with facilitation
      When results are recorded
      Then the critical defect is not accepted as cosmetic
      And the facilitation is recorded and not counted as unaided completion

  Rule: VF-UX-002 Usability qualification
    As a Programme Manager, I want core tasks to be completable without help after standard onboarding, so that my team can set up, collect, correct, approve, explain and report without relying on facilitators.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @VF-UX-002 @R2-Scale @Should
    Scenario: At least 90 percent of users complete core tasks unaided
      Given at least 15 representative users who have completed standard onboarding
      When they attempt programme setup, assigned collection, correction, approval, result explanation and report generation
      Then at least 90 percent complete the tasks without facilitator intervention
      And role, completion, facilitator intervention, elapsed time and consequential errors are recorded

    @VF-UX-002 @R2-Scale @Should
    Scenario: Reject readiness below threshold or with critical errors
      Given the usability session results
      When unaided completion is below 90 percent
      Then readiness is not granted
      And any observed critical disclosure, data loss or incorrect official result blocks readiness

  Rule: FR-UX-007 Expanded localisation
    As a Data Author, I want each released language to cover navigation, help, validation, notifications, standard reports and critical consent text with professional review, so that I can complete core workflows fully in my language.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-UX-007 @R3-Ecosystem @Should
    Scenario: Core workflow works in each released language
      Given each released language
      When a Data Author completes the same core workflow in it
      Then no untranslated blocking message or reversed layout obscures an action
      And right-to-left presentation is qualified where relevant

    @FR-UX-007 @R3-Ecosystem @Should
    Scenario: Reject release with incomplete translation
      Given a language whose core workflow translation is incomplete
      When release is requested
      Then release of the affected core workflows is blocked
      And machine translation alone is not accepted as a completed interface qualification

    @FR-UX-007 @R3-Ecosystem @Should
    Scenario: Reject fallback that changes stored meaning
      Given a missing translation
      When fallback language is used
      Then the fallback is explicit
      And stored codes and numeric semantics do not change
