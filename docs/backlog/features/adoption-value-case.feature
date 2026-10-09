# Imprana Commons backlog: Adoption: Value case
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Adoption: Value case

  Rule: US-VC-01 Cost-benefit, ROI and TCO over 1-3 years
    As an Operations Head, I want cost-benefit, ROI and total cost of ownership over 1-3 years, so that we know whether it is worth it.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-VC-01 @R1-Pilot @Must
    Scenario: Cost-benefit, ROI and TCO from baseline and trial data
      Given an opportunity with a baseline and trial results
      When the Operations Head builds the value case over 1-3 years
      Then cost-benefit, ROI and total cost of ownership are calculated from the baseline and trial data

    @US-VC-01 @R1-Pilot @Must
    Scenario: Costs include all components
      Given a value case
      When the Operations Head views its costs
      Then they include licences, setup, training and staff time

    @US-VC-01 @R1-Pilot @Must
    Scenario: Reject a value case with missing inputs
      Given a value case
      When it does not use the baseline and trial data, or omits licences, setup, training or staff time
      Then it is not accepted as complete

  Rule: US-VC-02 Benefits in sector terms
    As an Executive Director, I want benefits expressed in sector terms, so that they make sense to our board and donors.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @US-VC-02 @R1-Pilot @Must
    Scenario: Benefits in sector terms
      Given a value case
      When the Executive Director views its benefits
      Then staff hours, cost per beneficiary, data quality and reach are shown

    @US-VC-02 @R1-Pilot @Must
    Scenario: Reject benefits not in sector terms
      Given a value case
      When any of staff hours, cost per beneficiary, data quality or reach is missing from the benefits
      Then the value case is not accepted as complete

  Rule: US-VC-03 Board- or funder-ready business case export
    As an Executive Director, I want to export a board- or funder-ready business case, so that we get approval quickly.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-VC-03 @R1-Pilot @Must
    Scenario: Export a board- or funder-ready business case
      Given a completed value case
      When the Executive Director exports it as a PDF or a document
      Then the export contains the business case
      And all assumptions are listed

    @US-VC-03 @R1-Pilot @Must
    Scenario: Reject an export missing assumptions
      Given a value case with assumptions
      When it is exported
      Then an export that omits any assumption is not accepted

  Rule: US-VC-05 Lock the approved value case as baseline
    As an Executive Director, I want to lock the approved value case, so that later ROI is measured against it.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-VC-05 @R1-Pilot @Must
    Scenario: Lock the approved value case
      Given an approved value case
      When the Executive Director locks it
      Then the locked version records the date and the approver

    @US-VC-05 @R1-Pilot @Must
    Scenario: Changes create a new version
      Given a locked value case
      When someone changes it
      Then a new version is created
      And the locked version stays unchanged

    @US-VC-05 @R1-Pilot @Must
    Scenario: Reject overwriting the locked version
      Given a locked value case
      When an edit is saved
      Then the locked version is not overwritten
      And later ROI is still measured against the locked version

  Rule: US-VC-04 Low, expected and high scenarios
    As an Operations Head, I want low, expected and high scenarios, so that we understand the risk.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @US-VC-04 @R2-Scale @Should
    Scenario: Low, expected and high scenarios
      Given a value case
      When the Operations Head views it
      Then low, expected and high scenarios are shown

    @US-VC-04 @R2-Scale @Should
    Scenario: Edit scenario assumptions
      Given the three scenarios
      When the Operations Head edits an assumption in one scenario
      Then that scenario's results are recalculated

    @US-VC-04 @R2-Scale @Should
    Scenario: Reject missing scenarios or fixed assumptions
      Given a value case
      When fewer than three scenarios are shown or their assumptions cannot be edited
      Then the value case is not accepted
