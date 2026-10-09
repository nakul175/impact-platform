# Imprana Commons backlog: NFR cost
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR cost

  Rule: VF-ECO-001 Cost transparency and sustainability
    As a Platform Operator, I want the cost of running the service measured per tenant, workload, storage, integration run and AI use case, so that product limits and commitments are based on known costs.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @VF-ECO-001 @R3-Ecosystem @Should
    Scenario: Unit costs are measured for the reference load
      Given the reference load
      When resource and model usage are measured
      Then cost per active tenant, approved result workload, storage volume, integration run and AI use case is calculated

    @VF-ECO-001 @R3-Ecosystem @Should
    Scenario: Product limits are costed and budget limits enforced
      Given the qualification profile
      When product limits are reviewed
      Then each limit is costed against the profile
      And the corresponding visible budget limits are exercised

    @VF-ECO-001 @R3-Ecosystem @Should
    Scenario: Cost budget is approved before unbounded commitments
      Given a proposed unbounded or dedicated deployment commitment
      When it is to be offered
      Then an approved cost budget exists first

    @VF-ECO-001 @R3-Ecosystem @Should
    Scenario: Reject unlabelled assumptions or unlimited commitments
      Given cost figures presented at HLD review
      When measured prices or costs are not distinguished from assumptions
      Then the review fails
      And no unlimited commercial commitment is derived from these figures
