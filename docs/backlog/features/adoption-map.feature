# Imprana Commons backlog: Adoption: Map
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Adoption: Map

  Rule: US-MP-01 Problems mapped to AI/tech opportunities
    As an Executive Director, I want each problem translated into candidate AI or tech opportunities, so that I understand what is possible.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-MP-01 @R1-Pilot @Must
    Scenario: Each problem mapped to opportunities
      Given a diagnosis with priority problems
      When the problems are mapped to opportunities
      Then each problem has at least one candidate AI or tech opportunity from the pattern library
      And each opportunity includes a real-world example

    @US-MP-01 @R1-Pilot @Must
    Scenario: Reject an unmapped problem
      Given a mapped diagnosis
      When any problem has no opportunity, or an opportunity is not from the pattern library or has no real-world example
      Then the mapping is not accepted as complete

  Rule: US-MP-02 Recommend process fixes when tech is not the answer
    As an Executive Director, I want to be told when a process fix beats tech, so that we don't spend on the wrong thing.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-MP-02 @R1-Pilot @Must
    Scenario: Show a no-tech option when the pattern library flags one
      Given a problem whose pattern library entry flags a no-tech option
      When the Executive Director views the opportunities for that problem
      Then the no-tech process fix is shown

    @US-MP-02 @R1-Pilot @Must
    Scenario: Reject hiding a flagged no-tech option
      Given a problem whose pattern library entry flags a no-tech option
      When the opportunities for that problem are shown
      Then they are not limited to tech options

  Rule: US-MP-03 Rank opportunities with adjustable weights
    As an Operations Head, I want opportunities ranked by impact, effort, cost and readiness, so that we tackle the right one first.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @US-MP-03 @R1-Pilot @Must
    Scenario: Opportunities ranked with scores
      Given an organisation with mapped opportunities
      When the Operations Head views the ranking
      Then the opportunities are listed in rank order
      And each shows its scores for impact, effort, cost and readiness

    @US-MP-03 @R1-Pilot @Must
    Scenario: Adjust the ranking weights
      Given the ranked list of opportunities
      When the Operations Head changes the weights for impact, effort, cost and readiness
      Then the ranking is recalculated using the organisation's weights

    @US-MP-03 @R1-Pilot @Must
    Scenario: Reject a ranking that ignores the organisation's weights
      Given the organisation has adjusted the weights
      When the ranking is shown
      Then it does not use any weights other than the organisation's
      And no opportunity is ranked without its scores shown

  Rule: US-MP-04 Explain each recommendation
    As an Executive Director, I want to see why each opportunity is recommended, so that I can trust and explain it.
    Release: R1 Pilot · Priority: Must · Built today: Exists

    @US-MP-04 @R1-Pilot @Must
    Scenario: Show why an opportunity is recommended
      Given a recommended opportunity
      When the Executive Director views it
      Then a plain-language rationale is shown
      And the rationale links to the diagnosis inputs it is based on

    @US-MP-04 @R1-Pilot @Must
    Scenario: Reject an unexplained recommendation
      Given a recommended opportunity
      When it has no rationale, or its rationale is not linked to the diagnosis inputs
      Then it is not presented as a recommendation
