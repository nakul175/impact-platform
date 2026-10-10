# Imprana Commons backlog: Workflow and review
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Workflow and review

  Rule: FR-WFL-001 Configurable approvals
    As an Organisation Administrator, I want to design versioned approval workflows with stages, reviewer eligibility, mandatory reviewers, quorum, thresholds and deadlines, so that reviews follow our rules without disrupting work already in progress.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-WFL-001 @R1-Pilot @Must
    Scenario: Publish a workflow version
      Given a workflow defining object type, sequential or parallel stages, reviewer eligibility, mandatory reviewers, quorum, thresholds and deadlines
      When the Organisation Administrator publishes it
      Then the workflow version is pinned
      And new instances use it

    @FR-WFL-001 @R1-Pilot @Must
    Scenario: Running instance keeps its original route
      Given a candidate is underway in a two-stage review
      When the two-stage review is changed
      Then the candidate retains its original route

    @FR-WFL-001 @R1-Pilot @Must
    Scenario: Migrate a running instance
      Given a candidate underway on an earlier workflow version
      When an authorised migration is applied
      Then the affected stages restart
      And affected decisions are invalidated with the impact shown

    @FR-WFL-001 @R1-Pilot @Must
    Scenario: Reject a workflow without an independent reviewer
      Given a workflow being designed
      When it would leave no independent reviewer
      Then publishing the workflow is refused

    @FR-WFL-001 @R1-Pilot @Must
    Scenario: Reject a quorum bypassing mandatory review
      Given a workflow with a mandatory privacy or security review
      When the quorum is reached without that review
      Then the approval does not complete

  Rule: FR-WFL-002 Reviewer independence and authority
    As a Reviewer, I want to approve an immutable candidate with its change summary and evidence, with my authority and independence rechecked at commit, so that approvals apply only to exactly what I reviewed.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-WFL-002 @R1-Pilot @Must
    Scenario: Approve a current candidate
      Given a Reviewer opens an immutable candidate with its change summary and evidence
      When they approve it
      Then the approval submits the candidate revision and the Reviewer's current identity
      And commit rechecks membership, scope, independence, assurance and workflow stage

    @FR-WFL-002 @R1-Pilot @Must
    Scenario: Reject approval of a stale candidate
      Given a Reviewer has opened a submission
      When the submission or its evidence changes before they approve
      Then their old approve command fails
      And a fresh review is required

    @FR-WFL-002 @R1-Pilot @Must
    Scenario: Reject independent approval after a Reviewer edits content
      Given a Reviewer edits content in a candidate
      When they try to approve the resulting revision
      Then the edit is recorded as a new revision authored by them
      And they are not eligible to independently approve that revision

  Rule: FR-WFL-003 Return reject and resubmit
    As a Reviewer, I want to return work with actionable comments or reject it with a permitted final disposition and reason, and see each resubmission as a new compared version, so that every correction cycle is clear and decided afresh.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-WFL-003 @R1-Pilot @Must
    Scenario: Return work with actionable comments
      Given a Reviewer reviewing a submission
      When they return it with actionable comments tied to fields or issues
      Then the submission is returned to its author with those comments

    @FR-WFL-003 @R1-Pilot @Must
    Scenario: Inspect two correction cycles
      Given a submission that has gone through two correction cycles
      When its history is inspected
      Then each cycle shows its distinct reasons, revisions, authors and decision times
      And each resubmission is a new candidate version compared to the returned one with a fresh decision sequence

    @FR-WFL-003 @R1-Pilot @Must
    Scenario: Reject a return or rejection without required reasons
      Given a Reviewer deciding on a submission
      When they return it without actionable comments or reject it without a policy permitted final disposition and reason
      Then the decision is refused

    @FR-WFL-003 @R1-Pilot @Must
    Scenario: Reject reuse of previous approvals
      Given a resubmitted candidate whose earlier version had approvals
      When the new candidate is decided
      Then the previous approvals remain historical
      But they do not satisfy the new candidate unless the workflow explicitly revalidates unchanged independent stages under a qualified rule

  Rule: FR-WFL-007 Period close and lock
    As a MEL Manager, I want to preview a period close and have it independently locked as a fixed snapshot once all required checks pass, so that reported figures stay stable while late data is handled separately.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-WFL-007 @R1-Pilot @Must
    Scenario: Preview a period close
      Given a period ready to close
      When the MEL Manager runs the close preview
      Then the expected obligation set is frozen
      And the preview lists approved values, missing work, quality blockers and proposed exclusions

    @FR-WFL-007 @R1-Pilot @Must
    Scenario: Lock a quarter and receive late data
      Given a quarter with three approved mandatory obligations
      And all required checks pass and source revisions are unchanged
      When an independent decision locks the snapshot
      And a late optional record is then received
      Then the snapshot stays fixed
      And current views label the new data separately

    @FR-WFL-007 @R1-Pilot @Must
    Scenario: Reject a lock after inputs change or with failing checks
      Given a close preview
      When inputs change before the lock or a required check has not passed
      Then the lock is refused
      And a new preview is required if inputs changed

    @FR-WFL-007 @R1-Pilot @Must
    Scenario: Reject ordinary edits to locked results
      Given a locked snapshot
      When a user tries to alter a locked result through ordinary editing
      Then the edit is refused

  Rule: FR-WFL-008 Reopen and restate
    As a MEL Manager, I want to reopen a locked period for a scoped, time-bounded correction and restate it through a reviewed comparison, so that corrected results become a new approved version without overwriting what was previously reported.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-WFL-008 @R1-Pilot @Must
    Scenario: Restate Q1 and regenerate year-to-date
      Given Q1 has a locked snapshot and a distributed report
      When the MEL Manager starts a restatement from the Q1 snapshot with a correction reason, changed sources, affected totals and previously distributed artifacts
      And a Reviewer compares the old and proposed new snapshots and approves
      Then a new locked Q1 version is created
      And correction notices are created for eligible recipients
      And the old Q1 remains available marked as superseded

    @FR-WFL-008 @R1-Pilot @Must
    Scenario: Annual package points to the new approved version
      Given Q1 has been restated and the new version approved
      When year-to-date and annual totals are regenerated
      Then the annual package points to the new approved Q1 version
      And the annual totals identify which Q1 version they use

    @FR-WFL-008 @R1-Pilot @Must
    Scenario: Reject overwriting the original snapshot or report
      Given a restatement of Q1 has been approved
      When the original Q1 snapshot and report are accessed
      Then they are unchanged
      But they are marked as superseded

    @FR-WFL-008 @R1-Pilot @Must
    Scenario: Reject changes outside the reopened scope or time bound
      Given Q1 has been reopened for correction with a defined scope and time bound
      When a user attempts a change outside that scope or after the time bound has passed
      Then the change is refused

  Rule: FR-WFL-010 Decisions and signoff
    As a Reviewer, I want my signoff to record my identity, acting capacity, authority, the exact candidate version, decision, time and evidence, so that approval history is accountable and exportable without overstating its legal standing.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-WFL-010 @R1-Pilot @Must
    Scenario: Signoff records accountable decision details
      Given a Reviewer with current authority approves a report candidate
      When the signoff is recorded
      Then it records the Reviewer's real identity, acting capacity, current authority, candidate version, decision, time and evidence
      And any delegation or emergency context is included explicitly

    @FR-WFL-010 @R1-Pilot @Must
    Scenario: Export decisions for one report
      Given a report has been approved by several reviewers
      When the decision history for that report is exported within scope
      Then the export identifies the exact candidate version approved by each reviewer
      And ordinary approvals are labelled as accountable product decisions

    @FR-WFL-010 @R1-Pilot @Must
    Scenario: Reject unqualified electronic signature claims
      Given no separately qualified electronic signature integration and approved contract exists
      When the approval history is displayed or exported
      Then no approval is attributed to a legally recognised electronic signature standard

  Rule: FR-WFL-004 Delegation escalation and absence
    As a Reviewer, I want to delegate my review work for a defined scope and period and have overdue or orphaned work escalated to an eligible backup, so that reviews continue during absence without compromising independence.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-WFL-004 @R2-Scale @Should
    Scenario: Delegate review work
      Given a Reviewer sets a delegation with scope, start, end, delegate and reason
      When work is routed during the delegation period
      Then the system verifies the delegate's eligibility and independence before routing

    @FR-WFL-004 @R2-Scale @Should
    Scenario: Escalate when the only reviewer is removed
      Given the only assigned reviewer during period close
      When that reviewer is removed
      Then an eligible backup is selected with attribution
      And the original reviewer receives no new protected task

    @FR-WFL-004 @R2-Scale @Should
    Scenario: Escalate on a missed deadline
      Given a review task with a deadline
      When the deadline passes
      Then the task escalates to a named backup or manager

    @FR-WFL-004 @R2-Scale @Should
    Scenario: Reject a delegate approving the delegator's own change
      Given a delegate acting for a Reviewer
      When the delegate tries to approve a change authored by the delegator where independence is lost
      Then the approval is refused

    @FR-WFL-004 @R2-Scale @Should
    Scenario: Reject automatic approval when no replacement exists
      Given no eligible replacement reviewer exists
      When escalation runs
      Then the work is marked Blocked and a management task is created
      But it is never automatically approved

  Rule: FR-WFL-005 Comments mentions and discussions
    As a Data Author, I want to discuss work in threads attached to a specific object version or field and mention eligible collaborators, so that I can collaborate without exposing restricted information.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-WFL-005 @R2-Scale @Should
    Scenario: Discuss in a thread and mention a collaborator
      Given an object version or field
      When a Data Author starts a thread on it and mentions a collaborator
      Then the thread is attached to that version or field reference
      And mention suggestions contain only eligible collaborators
      And the notification links to the object with minimal permitted text and access is rechecked on opening

    @FR-WFL-005 @R2-Scale @Should
    Scenario: Edit or remove a comment
      Given a comment in a thread
      When it is edited or removed
      Then permitted moderation history is retained

    @FR-WFL-005 @R2-Scale @Should
    Scenario: Reject mentioning an external viewer in a restricted discussion
      Given a restricted evidence discussion
      When a Data Author tries to mention an external viewer
      Then the external viewer is not offered in the mention list
      And no outgoing notification discloses the restricted content

    @FR-WFL-005 @R2-Scale @Should
    Scenario: Reject quoting restricted fields into a broader thread
      Given a restricted field
      When a user tries to quote it into a broader thread
      Then the quote is prevented

    @FR-WFL-005 @R2-Scale @Should
    Scenario: Reject treating a resolved thread as resolution or approval
      Given a thread about a quality issue or a record awaiting approval
      When the thread is resolved
      Then the quality issue is not resolved
      And the record is not approved

  Rule: FR-WFL-006 Task and notification centre
    As a Data Author, I want one work centre for my assignments, returned work, due obligations and security notices, with my choice of permitted channels and digests, so that I never miss work that needs my attention.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-WFL-006 @R2-Scale @Should
    Scenario: Use the consolidated work centre
      Given a Data Author with assignments, returned work, due obligations and security notices
      When they open the work centre
      Then all of these items are consolidated in one place
      And they can choose permitted channels and digests
      And deadlines and escalations follow FD12
      And every notification has an event identity and per recipient delivery status

    @FR-WFL-006 @R2-Scale @Should
    Scenario: Retry an overdue reminder after a provider timeout
      Given an overdue reminder whose delivery timed out at the provider
      When the reminder is retried
      Then one logical notice remains with traceable delivery attempts
      And no duplicate task is created

    @FR-WFL-006 @R2-Scale @Should
    Scenario: Reject muting mandatory security notices
      Given a mandatory security notice
      When a Data Author tries to mute it
      Then muting is refused

    @FR-WFL-006 @R2-Scale @Should
    Scenario: Reject revealing content after failed delivery
      Given a notification whose delivery failed
      When contact remediation is flagged
      Then the content is not revealed to unverified alternative contacts

  Rule: FR-WFL-009 Automation rules
    As a Programme Manager, I want to define and preview bounded automation rules with a trigger, conditions, action, owner, scope and retry policy, so that routine follow-ups such as overdue reminders happen reliably without runaway or unauthorised actions.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-WFL-009 @R3-Ecosystem @Should
    Scenario: Overdue reminder rule updates one task
      Given the Programme Manager has created an overdue reminder rule with an event trigger, conditions, a task update action, owner, scope and retry policy
      And the rule has been previewed against synthetic or permitted sample events
      When the same overdue event occurs repeatedly
      Then exactly one task is produced
      And each execution records the input event and action receipt

    @FR-WFL-009 @R3-Ecosystem @Should
    Scenario: Disabling a rule stops future actions
      Given an active automation rule that has already committed actions
      When the Programme Manager disables the rule
      Then no further actions are taken
      And the already committed actions are identified

    @FR-WFL-009 @R3-Ecosystem @Should
    Scenario: Reject recursive unlimited reminders
      Given an automation rule whose action could re-trigger the rule
      When the loop depth or frequency limit is reached
      Then no further reminders are created

    @FR-WFL-009 @R3-Ecosystem @Should
    Scenario: Reject automation acting beyond its authority
      Given an active automation rule
      When it attempts to approve an object it generated, publish without approval or expand permissions
      Then the action is blocked
