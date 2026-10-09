# Imprana Commons backlog: Adoption: Diagnose
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Adoption: Diagnose

  Rule: US-DX-01 Guided plain-language problem discovery (intake agent)
    As an Executive Director, I want a guided, plain-language problem-discovery conversation, so that we can define our problems without hiring a consultant.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-DX-01 @R1-Pilot @Must
    Scenario: Complete a guided problem-discovery conversation
      Given an Executive Director starting problem discovery
      When they answer the guided, plain-language questions
      Then the conversation completes in under 60 minutes

    @US-DX-01 @R1-Pilot @Must
    Scenario: Output lists prioritised problems with evidence
      Given a completed problem-discovery conversation
      When the Executive Director views the output
      Then it lists the organisation's problems in priority order
      And each problem shows its supporting evidence

    @US-DX-01 @R1-Pilot @Must
    Scenario: Reject an overlong or unsupported discovery
      Given a problem-discovery conversation
      When it takes 60 minutes or more, or a listed problem has no priority or no supporting evidence
      Then the discovery is not accepted as complete

  Rule: US-DX-02 Digital maturity and data readiness assessment
    As a MEL Manager, I want to assess our digital maturity and data readiness, so that recommendations match what we can handle.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-DX-02 @R1-Pilot @Must
    Scenario: Score digital maturity and data readiness
      Given a MEL Manager completing the digital maturity and data readiness assessment
      When the assessment is submitted
      Then the organisation is scored against a standard framework

    @US-DX-02 @R1-Pilot @Must
    Scenario: Each score explained
      Given a completed assessment
      When the MEL Manager views the results
      Then every score has an explanation

    @US-DX-02 @R1-Pilot @Must
    Scenario: Reject unexplained or non-standard scores
      Given a completed assessment
      When any score has no explanation or is not measured against the standard framework
      Then the results are not accepted

  Rule: US-DX-03 Locked baseline metrics per priority problem
    As an Executive Director, I want to record baseline metrics for each priority problem, so that we can later prove what changed.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-DX-03 @R1-Pilot @Must
    Scenario: Capture baseline metrics per priority problem
      Given a priority problem from the diagnosis
      When the Executive Director records its baseline
      Then time, cost, quality and reach are captured for that problem

    @US-DX-03 @R1-Pilot @Must
    Scenario: Lock the baseline with a date
      Given a priority problem with its baseline metrics captured
      When the Executive Director locks the baseline
      Then the baseline is locked and the lock date is recorded

    @US-DX-03 @R1-Pilot @Must
    Scenario: Reject changes to a locked baseline
      Given a locked baseline
      When anyone tries to edit its metrics
      Then the edit is refused

    @US-DX-03 @R1-Pilot @Must
    Scenario: Reject locking an incomplete baseline
      Given a priority problem missing any of time, cost, quality or reach
      When the Executive Director tries to lock its baseline
      Then the lock is refused

  Rule: US-DX-04 Several staff contribute to one diagnosis
    As an Executive Director, I want to invite colleagues to contribute, so that the diagnosis reflects the whole organisation.
    Release: R1 Pilot · Priority: Should · Built today: Partial

    @US-DX-04 @R1-Pilot @Should
    Scenario: Invite colleagues by email
      Given an Executive Director running a diagnosis
      When they invite a colleague by email
      Then the colleague receives an email invitation to contribute

    @US-DX-04 @R1-Pilot @Should
    Scenario: Role-based contributions merged into one diagnosis
      Given invited colleagues with different roles
      When each completes the sections for their role
      Then their contributions are merged into one diagnosis

    @US-DX-04 @R1-Pilot @Should
    Scenario: Reject split diagnoses or out-of-role edits
      Given a colleague invited to contribute to a diagnosis
      When they submit their contribution
      Then no separate diagnosis is created
      But they cannot edit sections that are not for their role

  Rule: US-DX-05 Advisor review and validation of diagnosis
    As an Imprana Advisor, I want to review, annotate and validate a diagnosis, so that organisations get expert-checked findings.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-DX-05 @R1-Pilot @Must
    Scenario: Diagnosis appears in the advisor queue
      Given an organisation has a diagnosis ready for review
      When the Imprana Advisor opens the advisor queue
      Then the diagnosis is listed for review

    @US-DX-05 @R1-Pilot @Must
    Scenario: Annotate and validate a diagnosis
      Given an Imprana Advisor reviewing a diagnosis
      When they add comments and mark the diagnosis validated
      Then the comments are visible to the organisation
      And the validated status is recorded

    @US-DX-05 @R1-Pilot @Must
    Scenario: Reject validation without advisor review
      Given a diagnosis that has not been reviewed by an Imprana Advisor
      When a member of the organisation tries to mark it validated
      Then the validated status is not recorded

  Rule: US-DX-01a Record and prioritise the organisation's problems
    As an Executive Director, I want to record our organisation's problems in a structured, plain-language form and put them in priority order, so that the rest of the adoption journey starts from agreed priorities.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-DX-01a @R1-Pilot @Must
    Scenario: Record and prioritise problems
      Given an Executive Director starting a diagnosis
      When they record problems with a short description, the area affected and supporting evidence
      And put them in priority order
      Then the problems are saved in that order with their evidence

    @US-DX-01a @R1-Pilot @Must
    Scenario: Reject a problem without evidence or priority
      Given a recorded problem with no supporting evidence or no priority
      When the diagnosis is marked complete
      Then completion is refused and the incomplete problem is named

  Rule: US-DX-01b Conversational intake agent
    As an Executive Director, I want a guided, plain-language conversation that helps me find and describe our problems, so that we can define them without hiring a consultant.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-DX-01b @R1-Pilot @Must
    Scenario: Conversation produces prioritised problems
      Given AI use case CHAT is enabled by policy
      When the Executive Director completes the guided conversation
      Then it finishes in under 60 minutes
      And proposes problems in priority order, each with the evidence quoted from the conversation, for the Executive Director to accept or edit

    @US-DX-01b @R1-Pilot @Must
    Scenario: Reject AI output accepted without review
      Given the agent proposes problems
      When nobody has accepted or edited them
      Then they are not saved as the organisation's problems
