# Imprana Commons backlog: Adoption: Assess
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Adoption: Assess

  Rule: US-AS-01 Trial an option on own or sample data
    As a MEL Manager, I want to trial an option on our own or sample data, so that we see it work before committing.
    Release: R1 Pilot · Priority: Should · Built today: Absent

    @US-AS-01 @R1-Pilot @Should
    Scenario: Advisor-led trial in the pilot
      Given a MEL Manager in the pilot who wants to trial an option
      When an Imprana Advisor sets up a trial on the organisation's own or sample data
      Then the advisor-led trial runs for up to 4 weeks

    @US-AS-01 @R1-Pilot @Should
    Scenario: Reject a pilot trial longer than 4 weeks
      Given an advisor-led trial in the pilot
      When it reaches 4 weeks
      Then it is not extended beyond 4 weeks

  Rule: US-AS-03 Record trial results for the value case
    As an Imprana Advisor, I want to record trial results, so that they feed the value case.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-AS-03 @R1-Pilot @Must
    Scenario: Record trial results against the opportunity
      Given a completed trial
      When the Imprana Advisor records the results
      Then they are stored against the opportunity

    @US-AS-03 @R1-Pilot @Must
    Scenario: Trial results pulled into the value case
      Given trial results stored against an opportunity
      When the value case for that opportunity is built
      Then the results are pulled in automatically

    @US-AS-03 @R1-Pilot @Must
    Scenario: Reject manual re-entry
      Given trial results stored against an opportunity
      When the value case is built
      Then no one has to re-enter the results
      And results stored against another opportunity are not pulled in

  Rule: US-AS-02 Side-by-side comparison of options
    As an Operations Head, I want to compare options side by side, so that the choice is transparent.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @US-AS-02 @R2-Scale @Should
    Scenario: Compare options side by side on agreed criteria
      Given options for an opportunity and agreed comparison criteria
      When the Operations Head opens the comparison
      Then the options are shown side by side against the agreed criteria

    @US-AS-02 @R2-Scale @Should
    Scenario: Export the comparison
      Given a side-by-side comparison
      When the Operations Head exports it
      Then the export contains the same options and criteria as the comparison

    @US-AS-02 @R2-Scale @Should
    Scenario: Reject a comparison off the agreed criteria
      Given a side-by-side comparison
      When it omits an agreed criterion or adds one that was not agreed
      Then the comparison is not accepted
