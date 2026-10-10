# Imprana Commons backlog: Adoption: Improve
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Adoption: Improve

  Rule: US-IM-01 Track usage and outcomes against baseline
    As an Executive Director, I want usage and outcomes tracked against our baseline, so that we know whether it is working.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-IM-01 @R1-Pilot @Must
    Scenario: Compare current metrics with the locked baseline
      Given an opportunity with a locked baseline and a deployed solution
      When the Executive Director opens the dashboard
      Then current usage and outcome metrics are shown against the locked baseline

    @US-IM-01 @R1-Pilot @Must
    Scenario: Reject comparison against anything but the locked baseline
      Given a locked baseline
      When the dashboard compares current metrics
      Then it does not compare them against any other baseline

  Rule: US-IM-02 Share realised ROI with sponsor by choice
    As an Executive Director, I want to share realised ROI with our sponsor when we choose, so that we can show return.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-IM-02 @R1-Pilot @Must
    Scenario: Organisation controls what is shared
      Given an organisation with realised ROI and a sponsor
      When the Executive Director selects what to share
      Then only the selected items are available to share

    @US-IM-02 @R1-Pilot @Must
    Scenario: Report generated on request
      Given the organisation's sharing choices are set
      When the Executive Director requests a report for the sponsor
      Then the report is generated with only the selected items

    @US-IM-02 @R1-Pilot @Must
    Scenario: Reject sharing without the organisation's choice
      Given the Executive Director has not requested a report
      When the sponsor looks for the organisation's ROI
      Then nothing is shared
      And items the organisation did not select are never shared

  Rule: US-IM-03 Quarterly value reviews
    As an Imprana Advisor, I want to run quarterly value reviews, so that problems are caught early.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @US-IM-03 @R1-Pilot @Must
    Scenario: Run a quarterly value review from a template
      Given an organisation due its quarterly value review
      When the Imprana Advisor starts the review
      Then the review template is used

    @US-IM-03 @R1-Pilot @Must
    Scenario: Actions logged and tracked
      Given a value review in progress
      When the Imprana Advisor records an action
      Then the action is logged
      And its progress is tracked

    @US-IM-03 @R1-Pilot @Must
    Scenario: Reject untracked actions
      Given a completed value review
      When an action agreed in the review is not logged
      Then the review is not accepted as complete

  Rule: US-IM-04 Suggest the next opportunity
    As an Executive Director, I want suggestions for our next opportunity, so that we keep improving.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @US-IM-04 @R2-Scale @Should
    Scenario: Suggest the next opportunity
      Given an organisation in the Improve stage
      When the Executive Director views suggestions for the next opportunity
      Then suggestions are shown

    @US-IM-04 @R2-Scale @Should
    Scenario: A suggestion starts a new Diagnose cycle
      Given a suggested next opportunity
      When the Executive Director takes it up
      Then a new Diagnose cycle starts

    @US-IM-04 @R2-Scale @Should
    Scenario: Reject skipping diagnosis
      Given a suggested next opportunity
      When the Executive Director takes it up
      Then it does not skip the new Diagnose cycle

  Rule: US-IM-05 Anonymised evidence base on what works
    As a Platform Operator, I want anonymised outcomes aggregated, so that recommendations improve over time.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @US-IM-05 @R2-Scale @Should
    Scenario: Aggregate consented outcomes
      Given organisations that have consented to share their outcomes
      When anonymised outcomes are aggregated
      Then only those organisations' outcomes are included

    @US-IM-05 @R2-Scale @Should
    Scenario: Reject outcomes without consent
      Given an organisation that has not consented
      When anonymised outcomes are aggregated
      Then its outcomes are excluded

    @US-IM-05 @R2-Scale @Should
    Scenario: Reject figures from fewer than 5 organisations
      Given an aggregated figure based on fewer than 5 organisations
      When it would be displayed
      Then it is not shown
