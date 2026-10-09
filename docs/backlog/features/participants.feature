# Imprana Commons backlog: Participants
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Participants

  Rule: FR-PAR-001 Optional registries
    As a Programme Manager, I want to set up a programme as aggregate-only or registry-enabled and configure only the entity types and attributes it needs, so that personal records exist only where the programme genuinely requires them.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-PAR-001 @R2-Scale @Should
    Scenario: Only the registry-enabled programme exposes a registry workspace
      Given a Programme Manager creates an aggregate-only education programme
      And creates a registry-enabled participant programme
      When they open each programme
      Then only the participant programme exposes the configured registry workspace

    @FR-PAR-001 @R2-Scale @Should
    Scenario: Configure registry entities without national identifiers
      Given a registry-enabled programme
      When the Programme Manager selects entity types and necessary attributes
      Then the system issues a programme pseudonym
      And participants, households, groups, institutions, facilities and sites can be registered without mandatory national identifiers
      And entity types and relationships are explicit

    @FR-PAR-001 @R2-Scale @Should
    Scenario: Reject switching to a registry without privacy review
      Given an aggregate-only programme
      When a switch to registry-enabled mode is attempted without privacy review and field configuration
      Then the switch is refused
      And no empty personal records are created

  Rule: FR-PAR-002 Purpose limited identity
    As a Privacy Officer, I want direct identity fields controlled separately from analytical attributes and pseudonyms scoped to an approved programme or matching agreement, so that analysts can follow participants over time without seeing names or linking across programmes.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-PAR-002 @R2-Scale @Must
    Scenario: Analyst joins visits by pseudonym without seeing identity
      Given an Analyst without direct identity capability
      When they join two visits for one participant using the programme pseudonym
      Then the join succeeds
      But they cannot resolve the person's name
      And they cannot resolve the person's participation in another programme

    @FR-PAR-002 @R2-Scale @Must
    Scenario: Reject cross-project linkage without separate approval
      Given participant records in two projects
      When a user attempts to link them without a separately approved purpose, a matching contract and authority to both scopes
      Then the linkage is refused

    @FR-PAR-002 @R2-Scale @Must
    Scenario: Reject using a pseudonym as a universal identifier
      Given a pseudonym scoped to one approved programme
      When it is used to identify the person outside that programme or matching agreement
      Then it does not resolve to the person

  Rule: FR-PAR-003 Notice consent and lawful handling
    As a Privacy Officer, I want collection to present the applicable notice and record its version, language, purpose, handling basis, recorder and consent decisions, with optional purposes chosen independently, so that each use of participant data follows its own lawful basis.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-PAR-003 @R2-Scale @Must
    Scenario: Record notice and consent at collection
      Given a Field Data Collector collecting participant data
      When the applicable notice is presented
      Then the notice version, language, purpose, handling basis, recorder and consent decision are recorded where relevant
      And optional purposes such as photography are selected independently

    @FR-PAR-003 @R2-Scale @Must
    Scenario: Withdraw public image permission
      Given a participant has given public image permission and is under lawful service monitoring
      When they withdraw public image permission
      Then photo publication is blocked
      And lawful service monitoring is retained
      And eligible analytic observations remain governed by their own basis
      And downstream review is triggered

    @FR-PAR-003 @R2-Scale @Must
    Scenario: Reject blocking a service record when optional media is refused
      Given a participant refuses optional photography
      When a service record is created for them
      Then the service record is not blocked unless policy justifies that dependency

    @FR-PAR-003 @R2-Scale @Must
    Scenario: Reject treating consent as blanket authorisation
      Given a participant's recorded consent
      When their data is requested for research, model training or public disclosure
      Then the consent is not assumed to authorise that use

  Rule: FR-PAR-004 Service and participation events
    As a MEL Manager, I want service events recorded with stable identity, subject, type, date, provider or site and evidence, so that reports count services or distinct people correctly according to each indicator definition.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-PAR-004 @R2-Scale @Should
    Scenario: Count services and unique people
      Given three distinct visits recorded for one participant
      When indicators are reported
      Then the service count is three
      And the approved unique person count is one

    @FR-PAR-004 @R2-Scale @Should
    Scenario: Corrections create revisions
      Given a recorded service event
      When a Data Author corrects it
      Then a new revision of the event is created

    @FR-PAR-004 @R2-Scale @Should
    Scenario: Reject duplicate ingestion of the same event
      Given a service event that is already recorded
      When the same event is ingested again
      Then no additional visit is added

    @FR-PAR-004 @R2-Scale @Should
    Scenario: Reject silent removal on cancellation or reversal
      Given a recorded service event
      When it is cancelled or reversed
      Then the cancellation or reversal is recorded explicitly
      But the original receipt is not removed

  Rule: FR-PAR-007 Safeguarding and vulnerable people
    As a Programme Manager, I want sensitive programmes configured with guardian and notice rules, safe contact channels, restricted fields and evidence policy, and safeguarding concerns routed only to designated staff, so that vulnerable people are protected.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-PAR-007 @R2-Scale @Must
    Scenario: Configure a sensitive programme
      Given a Programme Manager setting up a sensitive programme
      When they complete the programme setup
      Then guardian and notice rules, safe contact channels, restricted fields and evidence policy are selected

    @FR-PAR-007 @R2-Scale @Must
    Scenario: Safeguarding concern routed only to designated staff
      Given a Field Data Collector flags a safeguarding concern
      When the restricted case is created
      Then only the assigned safeguarding officer can open its content
      And the Programme Manager sees only a restricted follow up status
      And ordinary workspaces show only a minimal reference

    @FR-PAR-007 @R2-Scale @Must
    Scenario: Reject sensitive details in general notifications
      Given a safeguarding concern has been raised
      When general notifications about it are sent
      Then they do not include the concern narrative, precise location or the child's identity

    @FR-PAR-007 @R2-Scale @Must
    Scenario: Reject access through ordinary programme membership
      Given a user who is an ordinary programme member but not designated safeguarding staff
      When they try to open the safeguarding case
      Then access is refused

  Rule: FR-PAR-008 Participant requests and corrections
    As a Privacy Officer, I want verified participant correction requests handled as scoped cases in which the reviewer previews downstream effects before applying a resolution, so that participants' records are corrected without exposing other people's information.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-PAR-008 @R2-Scale @Must
    Scenario: Open and resolve a scoped correction case
      Given a correction request from a Programme Participant
      When the subject is verified through permitted evidence
      Then a scoped case is opened
      And the Reviewer can resolve it as wrong identity, attribute correction, restriction or merge
      And the downstream effects are previewed before the resolution is applied

    @FR-PAR-008 @R2-Scale @Must
    Scenario: Correct a wrongly linked visit
      Given a visit wrongly linked to a participant
      When the Reviewer applies the correction
      Then both participants' histories are recalculated
      And the erroneous private association is not retained in ordinary views
      And minimal attribution is preserved while disallowed personal values are deleted where required

    @FR-PAR-008 @R2-Scale @Must
    Scenario: Reject exposing household members' information
      Given a correction request from a participant who belongs to a household
      When the request is verified and responded to
      Then no household member's information is exposed

  Rule: FR-PAR-005 Household and group membership
    As a Data Steward, I want household and group membership recorded as dated relationships that survey submissions pin to, so that historic observations keep the household or group that applied at the time.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-PAR-005 @R3-Ecosystem @Should
    Scenario: Move a person between households
      Given a person who is a member of household A
      When they move to household B on 1 June
      Then the membership in household A is closed and a membership in household B is opened after overlap validation
      And May observations retain household A
      And July observations resolve to household B

    @FR-PAR-005 @R3-Ecosystem @Should
    Scenario: Record a membership and pin it to surveys
      Given a household or group
      When a membership is recorded
      Then it records the entity pair, role, effective start and optional end
      And survey submissions pin the relevant relationship version

    @FR-PAR-005 @R3-Ecosystem @Should
    Scenario: Reject retrospective application of current membership
      Given historic surveys pinned to an earlier membership
      When the person's current membership changes
      Then the historic surveys are not updated to the current membership

    @FR-PAR-005 @R3-Ecosystem @Should
    Scenario: Reject guardian details bypassing their own controls
      Given a user permitted to view household membership
      But not permitted under the guardian field's separate sensitivity and purpose controls
      When they view the membership
      Then the guardian field is not shown to them

  Rule: FR-PAR-006 Cohorts and follow up
    As a MEL Manager, I want cohorts that pin eligibility rules, index date, observation windows and denominator policy and record each follow-up outcome, so that attrition and exclusions are explicit rather than hidden in results.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-PAR-006 @R3-Ecosystem @Should
    Scenario: Missing follow ups appear as attrition
      Given a cohort of ten enrolled participants with a declared denominator policy
      And two participants have missing follow ups
      When the cohort outcomes are analysed
      Then the results use the declared denominator
      And the two missing follow ups appear as explicit attrition
      But they are not reported as eight automatically successful outcomes

    @FR-PAR-006 @R3-Ecosystem @Should
    Scenario: Record follow up outcomes and show exclusions
      Given a cohort under follow up
      When follow up outcomes are recorded
      Then each can be recorded as completed, missing, withdrawn, ineligible, deceased or lost to follow up where appropriate
      And the analysis displays exclusions and their reasons

    @FR-PAR-006 @R3-Ecosystem @Should
    Scenario: Reject an unapproved denominator change
      Given a cohort with a pinned denominator policy
      When the denominator is changed without an approved rule
      Then the change is refused

    @FR-PAR-006 @R3-Ecosystem @Should
    Scenario: Reject an outside-window observation substituting for the intended visit
      Given an observation recorded outside the follow up window
      When the cohort is analysed
      Then the observation is separately flagged
      And it does not silently substitute for the intended visit
