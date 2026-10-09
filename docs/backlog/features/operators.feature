# Imprana Commons backlog: Operators
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Operators

  Rule: US-OP-01 Advisor case queue by stage and next action
    As an Imprana Advisor, I want a case queue showing each organisation's stage and next action, so that I can manage many clients.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-OP-01 @R1-Pilot @Must
    Scenario: Case queue shows stage and next action
      Given an Imprana Advisor managing several organisations
      When they open the case queue
      Then each organisation's stage and next action are shown

    @US-OP-01 @R1-Pilot @Must
    Scenario: Filter the queue
      Given the case queue
      When the Imprana Advisor filters by stage, cohort or urgency
      Then only matching organisations are shown

    @US-OP-01 @R1-Pilot @Must
    Scenario: Reject non-matching results
      Given a filter applied to the case queue
      When the queue is shown
      Then no organisation that does not match the filter is listed

  Rule: US-OP-02 Advisor time logging per stage
    As an Imprana Advisor, I want to log time spent per stage, so that we know where expert effort goes and what to automate next.
    Release: R1 Pilot · Priority: Should · Built today: Absent

    @US-OP-02 @R1-Pilot @Should
    Scenario: Log time per stage
      Given an Imprana Advisor working with an organisation
      When they log time
      Then the time is recorded against a stage

    @US-OP-02 @R1-Pilot @Should
    Scenario: Monthly report
      Given time logged during a month
      When the monthly report is produced
      Then it shows the time spent per stage

    @US-OP-02 @R1-Pilot @Should
    Scenario: Reject time without a stage
      Given an Imprana Advisor logging time
      When no stage is chosen
      Then the entry is refused
