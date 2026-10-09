# Imprana Commons backlog: Non-functional
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Non-functional

  Rule: NFR-08 Recommendations independent of commercial ties
    As an Executive Director, I want recommendations independent of commercial relationships, so that I can trust them.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @NFR-08 @R1-Pilot @Must
    Scenario: Fit-scoring logic documented
      Given the fit scoring used for recommendations
      When the Executive Director looks up how options are scored
      Then the fit-scoring logic is documented

    @NFR-08 @R1-Pilot @Must
    Scenario: Annual independent review
      Given the documented fit-scoring logic
      When a year has passed since the last review
      Then an independent review of the logic has been completed

    @NFR-08 @R1-Pilot @Must
    Scenario: Reject commercial influence on recommendations
      Given a solution with a commercial relationship
      When it is fit-scored and recommended
      Then the commercial relationship does not change its score or recommendation

    @NFR-08 @R1-Pilot @Must
    Scenario: Reject a missed annual review
      Given the fit-scoring logic
      When more than a year passes without an independent review
      Then the recommendations are not treated as independent
