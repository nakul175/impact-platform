# Imprana Commons backlog: NFR availability
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR availability

  Rule: VF-AVL-001 Core availability
    As a Data Author, I want sign-in, record access, submission, approval and published reports to be reliably available, so that I can do my work whenever I need to.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @VF-AVL-001 @R1-Pilot @Must
    Scenario: Each critical journey meets 99.9 percent monthly availability
      Given synthetic journeys for authentication, read, submission, approval and report access
      When monthly availability is measured
      Then each journey achieves at least 99.9 percent availability for each material tenant cohort

    @VF-AVL-001 @R1-Pilot @Must
    Scenario: Planned maintenance counts against the objective
      Given planned maintenance or a platform-dependent outage affects a critical journey
      When monthly bad minutes are calculated
      Then those minutes count against the 99.9 percent internal objective

    @VF-AVL-001 @R1-Pilot @Must
    Scenario: Reject a single aggregate availability figure
      Given monthly availability results
      When only a single aggregate availability number is reported
      Then the evidence is rejected as insufficient
      And excluding planned maintenance or platform-dependent outages from bad minutes is rejected

  Rule: VF-AVL-002 Dependency degradation
    As a Data Author, I want failures in AI, email, external data collection or BI to be isolated and clearly flagged, so that I can keep doing core manual work and know what is stale or queued.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @VF-AVL-002 @R1-Pilot @Must
    Scenario: Core manual workflows continue when an independent dependency fails
      Given AI, email, the survey connector or BI retrieval has failed independently
      When a Data Author performs manual entry, deterministic calculations and access to existing approved reports
      Then those core workflows remain available

    @VF-AVL-002 @R1-Pilot @Must
    Scenario: Affected function, stale data and queued actions are shown
      Given a dependency has failed
      When a Data Author uses the platform
      Then the affected function is identified
      And stale data and queued actions are labelled

    @VF-AVL-002 @R1-Pilot @Must
    Scenario: Reject false isolation claims
      Given a failed dependency that is actually required for the tested journey
      When isolation results are reported
      Then isolation is not claimed for that journey
      And the dependency is declared and the affected cohort is reported
