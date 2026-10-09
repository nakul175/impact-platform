# Imprana Commons backlog: Programmes
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Programmes

  Rule: FR-PRG-001 Programme and project registry
    As a Programme Manager, I want a programme and project registry with unique identities and dated portfolio memberships, so that a project can appear in several portfolios without being duplicated.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-PRG-001 @R1-Pilot @Must
    Scenario: Create a programme with validated details
      Given a Programme Manager creating a programme
      When they enter a code, title, dates, owner, geography and reporting calendar
      Then the code is validated as unique within the tenant
      And the programme is created

    @FR-PRG-001 @R1-Pilot @Must
    Scenario: One project in two portfolios
      Given project P
      When it is added to two thematic portfolios with effective dates
      Then the organisation registry contains one project identity and two memberships

    @FR-PRG-001 @R1-Pilot @Must
    Scenario: Registry respects access
      Given a user with access to only some projects
      When they filter the registry
      Then access is applied before counts are shown
      And archive or reopen is available only through lifecycle actions

    @FR-PRG-001 @R1-Pilot @Must
    Scenario: Reject a duplicate code
      Given an existing programme code in the tenant
      When another programme is created with the same code
      Then creation is refused

    @FR-PRG-001 @R1-Pilot @Must
    Scenario: Reject ordinary submissions to an archived project
      Given an archived project
      When a user attempts an ordinary new submission
      Then the submission is refused
      But authorised auditors can still find the project in search

  Rule: FR-PRG-006 Partner responsibilities
    As a Programme Manager, I want to assign partners explicit collection, activity or reporting responsibilities and preview transfers between partners, so that work moves cleanly without exposing unrelated records or reattributing past submissions.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-PRG-006 @R1-Pilot @Must
    Scenario: Assign and accept a responsibility
      Given a Programme Manager assigning a partner
      When they assign collection, activity or reporting responsibility with dates, acceptance and explicit scope
      Then the Partner Organisation User can accept it or request correction

    @FR-PRG-006 @R1-Pilot @Must
    Scenario: Transfer reporting between partners
      Given partner X holds reporting responsibility and has an approved quarter
      When the Programme Manager transfers next quarter's reporting from X to Y
      Then the preview lists open tasks, historic submissions and new access needs
      And X's approved quarter stays intact and attributed to X
      And Y sees only the assignments and evidence needed for future work

    @FR-PRG-006 @R1-Pilot @Must
    Scenario: Reject access to unrelated historical records
      Given partner Y has received a new responsibility
      When Y tries to open unrelated historical participant records
      Then access is denied

    @FR-PRG-006 @R1-Pilot @Must
    Scenario: Reject reattribution of approved submissions
      Given approved submissions by the original partner
      When responsibility is transferred
      Then the submissions remain attributed to the original contributor

  Rule: FR-PRG-002 Activities and milestones
    As a Programme Manager, I want to define activities and milestones with assignees, dates, dependencies and required evidence, so that I can track delivery and see dependency risk without changing official results or approved dates.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-PRG-002 @R2-Scale @Should
    Scenario: Define an activity
      Given a Programme Manager planning work
      When they create an activity with assignee, start, due date, predecessor links, milestone evidence and framework reference
      Then the activity is saved
      And blocked and cancelled are available as explicit states

    @FR-PRG-002 @R2-Scale @Should
    Scenario: Complete an activity with evidence
      Given an activity with declared deliverable evidence
      When the assignee marks it complete
      Then completion requires the declared evidence or an authorised exception

    @FR-PRG-002 @R2-Scale @Should
    Scenario: Predecessor delay flags downstream risk
      Given activity A precedes activity B
      When activity A is delayed
      Then B shows dependency risk
      And B's approved due date is retained
      And no indicator achievement is invented

    @FR-PRG-002 @R2-Scale @Should
    Scenario: Reject a dependency cycle
      Given activity A precedes activity B
      When a user makes B a predecessor of A
      Then the link is rejected

    @FR-PRG-002 @R2-Scale @Should
    Scenario: Reject a due date before start
      Given an activity with a start date
      When a user sets a due date before the start
      Then the date is rejected

  Rule: FR-PRG-003 Workplans and calendars
    As a Programme Manager, I want a workplan calendar that shows tasks in my time zone, creates recurring obligations once and previews reschedules, so that deadlines shift predictably without altering locked history.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-PRG-003 @R2-Scale @Should
    Scenario: View tasks in the viewer's zone
      Given programme and reporting tasks with a governing deadline zone
      When a Programme Manager opens the calendar
      Then tasks are shown in the viewer's zone
      And the governing deadline zone is available

    @FR-PRG-003 @R2-Scale @Should
    Scenario: Preview and apply a reschedule
      Given a programme with future tasks and a locked quarterly deadline
      When the Programme Manager moves the programme end by one month
      Then the preview lists future tasks and affected recipients
      And only eligible future tasks shift
      And the locked quarterly deadline stays unchanged

    @FR-PRG-003 @R2-Scale @Should
    Scenario: Recurrence uses the working calendar
      Given a recurring obligation
      When instances are generated across a daylight saving change
      Then stable obligation instances are created using the working calendar
      And each deadline resolves to one declared instant

    @FR-PRG-003 @R2-Scale @Should
    Scenario: Reject duplicate tasks
      Given an obligation instance that already exists
      When recurrence generation runs again
      Then no duplicate task is created for that obligation identity

    @FR-PRG-003 @R2-Scale @Should
    Scenario: Reject changes to locked deadlines
      Given a locked period deadline
      When a reschedule is applied
      Then the locked deadline remains unchanged in history

  Rule: FR-PRG-004 Risks issues and dependencies
    As a Programme Manager, I want to record risks and issues with owners, scored by a configured matrix, and to validate automated detections, so that escalations are reliable and auditable.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-PRG-004 @R2-Scale @Should
    Scenario: Record a scored risk
      Given a configured risk matrix
      When the Programme Manager records a risk with category, likelihood, impact, owner, mitigation and review date
      Then the score is calculated from the configured matrix

    @FR-PRG-004 @R2-Scale @Should
    Scenario: Automated detections await validation
      Given an automated detection of a possible issue
      When it is created
      Then it stays in suggested state until a manager validates it

    @FR-PRG-004 @R2-Scale @Should
    Scenario: Escalate an overdue high impact issue
      Given a high impact issue past its due date with restricted evidence
      When escalation runs
      Then it identifies the responsible manager and linked obligations
      And the escalation email does not expose the restricted evidence

    @FR-PRG-004 @R2-Scale @Should
    Scenario: Reject AI certainty as the risk score
      Given an automated detection with an AI certainty value
      When the risk score is calculated
      Then the score comes only from the configured matrix

    @FR-PRG-004 @R2-Scale @Should
    Scenario: Reject closure without resolution evidence
      Given an open issue with earlier escalation events
      When a user tries to close it without resolution evidence
      Then closure is refused
      And earlier escalation events are never removed

  Rule: FR-PRG-005 Geography and sites
    As a Data Steward, I want to manage versioned geography hierarchies and bind projects and observations to a boundary version, so that boundary changes never rewrite history and locations are disclosed only at the permitted level.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-PRG-005 @R2-Scale @Should
    Scenario: Bind data to a boundary version
      Given a Data Steward in the geography editor
      When they import or select a versioned hierarchy with optional permitted coordinates
      Then project and observation bindings record boundary version and effective date

    @FR-PRG-005 @R2-Scale @Should
    Scenario: Report on the old boundary after a split
      Given a district that is split into two new districts
      When a report on the old boundary is reproduced
      Then it uses the old boundary codes
      And future data uses the new codes

    @FR-PRG-005 @R2-Scale @Should
    Scenario: Maps follow the viewer's disclosure level
      Given a viewer without exact coordinate permission
      When they view a map
      Then locations are shown at the disclosure level allowed for them
      And generalisation uses a documented mapping

    @FR-PRG-005 @R2-Scale @Should
    Scenario: Reject rewriting old observation codes
      Given observations coded to an old boundary
      When the boundaries change
      Then the old observation codes are not rewritten

    @FR-PRG-005 @R2-Scale @Should
    Scenario: Reject exposing or faking exact locations
      Given a viewer without separate exact coordinate permission
      When they view locations
      Then exact coordinates are not shown
      And arbitrary jitter is not presented as an exact location

  Rule: FR-PRG-007 Programme change control
    As a Programme Manager, I want to propose programme amendments as complete packages with reason, effective date and impact, so that approved changes apply consistently and never leave a hidden mix of old and new commitments.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-PRG-007 @R2-Scale @Should
    Scenario: Approve and apply an amendment package
      Given an amendment with proposed changes, reason, effective date and impact on targets, activities, budgets and obligations
      When a Reviewer approves the exact amendment package
      Then application creates the corresponding new object versions and receipts

    @FR-PRG-007 @R2-Scale @Should
    Scenario: Shorten a programme with future obligations
      Given a programme with future obligations
      When the Programme Manager submits an amendment shortening the programme
      Then approval requires resolving or explicitly retaining every affected obligation

    @FR-PRG-007 @R2-Scale @Should
    Scenario: Reject applying an amendment with a failed child change
      Given an approved amendment where a required child change fails validation
      When the amendment is applied
      Then the amendment remains unapplied
      But it may be explicitly partially applied only under a declared approved mode

  Rule: FR-PRG-008 Closure and archival
    As a Programme Manager, I want a close wizard that lists outstanding work and blocks closure until mandatory items are resolved, so that archived programmes are complete, protected from ordinary edits and still exportable.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-PRG-008 @R2-Scale @Must
    Scenario: Close wizard lists outstanding items
      Given a project being closed
      When the Programme Manager opens the close wizard
      Then it lists incomplete submissions, unresolved quality issues, open approvals, deliverables and retention duties
      And mandatory blockers must be resolved before closure

    @FR-PRG-008 @R2-Scale @Must
    Scenario: Archive with a permitted warning
      Given a project with one permitted warning
      When the Programme Manager archives it with the exception attached to the closure decision
      Then its approved export still works
      And new ordinary data entry is denied
      And ordinary schedules stop

    @FR-PRG-008 @R2-Scale @Must
    Scenario: Reject corrections without an approved reopen or amendment
      Given a closed project
      When a user attempts a correction without an approved reopen or governed amendment with scope
      Then the correction is refused

    @FR-PRG-008 @R2-Scale @Must
    Scenario: Reject reopening locked periods with the programme
      Given a closed programme with locked reporting periods
      When the programme is reopened
      Then the locked reporting periods stay locked

  Rule: FR-PRG-009 Cross project dependencies
    As a Programme Manager, I want to link an authorised prerequisite from another project with a shared status contract, so that dependent teams can track it without seeing confidential details of the source project.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-PRG-009 @R3-Ecosystem @Should
    Scenario: Link a cross project prerequisite
      Given a Programme Manager authorised for a prerequisite in another project
      When they link it with a shared status contract
      Then receiving users see either the full permitted dependency or a disclosed status summary with owner contact and freshness

    @FR-PRG-009 @R3-Ecosystem @Should
    Scenario: Partner sees only the status summary
      Given a Partner Organisation User with a delayed prerequisite from another project
      When they view the dependency
      Then they see that it is delayed and its due date
      But they cannot drill into the originating project's confidential grant agreement

    @FR-PRG-009 @R3-Ecosystem @Should
    Scenario: Reject exposure of restricted details
      Given a prerequisite with a restricted title, budget or task comments
      When a receiving user views the dependency label
      Then none of the restricted details are shown

    @FR-PRG-009 @R3-Ecosystem @Should
    Scenario: Reject copying hidden source on a broken grant
      Given a dependency whose access grant is broken
      When a receiving user views the link
      Then the link shows as unavailable
      And no hidden source content is copied

  Rule: FR-PRG-010 Bulk administration
    As an Organisation Administrator, I want to apply one operation, such as owner reassignment or template instantiation, to many objects with a validated preview and an item manifest, so that bulk changes are safe, scoped and repeatable.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-PRG-010 @R3-Ecosystem @Should
    Scenario: Preview a bulk operation
      Given an Organisation Administrator who selects a set of objects and one operation
      When the preview runs
      Then every object's current revision and scope are validated
      And candidates are shown as valid, skipped or blocked

    @FR-PRG-010 @R3-Ecosystem @Should
    Scenario: Execute with mixed candidates
      Given ten projects selected for reassignment, with two outside scope and one at a stale revision
      When the Organisation Administrator executes the operation
      Then seven commit
      And three report safe reasons
      And an item manifest is returned

    @FR-PRG-010 @R3-Ecosystem @Should
    Scenario: Retry has no new effect
      Given a completed bulk template instantiation
      When it is retried with the same operation identity
      Then no duplicate template instances are created

    @FR-PRG-010 @R3-Ecosystem @Should
    Scenario: Reject mass approval
      Given items awaiting approval
      When a user tries to approve them through bulk administration
      Then the operation is refused

    @FR-PRG-010 @R3-Ecosystem @Should
    Scenario: Reject changed candidates without refreshed review
      Given a candidate that changed after the preview
      When execution runs
      Then it is not committed until a refreshed review
