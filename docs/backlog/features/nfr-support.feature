# Imprana Commons backlog: NFR support
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR support

  Rule: VF-SUP-001 Support and service readiness
    As an Executive Director, I want published support hours, response targets and escalation channels, with continuous cover for critical incidents, so that my organisation gets timely help when something goes wrong.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @VF-SUP-001 @R1-Pilot @Must
    Scenario: Support terms are published for each service plan
      Given each service plan
      When an Executive Director views its support terms
      Then normal support hours, response targets and escalation channels are published

    @VF-SUP-001 @R1-Pilot @Must
    Scenario: Critical incidents have continuous on-call coverage
      Given a critical incident readiness exercise
      When it is run
      Then continuous on-call ownership responds
      And the runbook and escalation route are verified

    @VF-SUP-001 @R1-Pilot @Must
    Scenario: Every critical capability has an owner, runbook and tested recovery
      Given readiness exercises for critical incident, identity recovery, failed import, privacy deletion and report correction
      When they are completed
      Then each critical capability has an accountable operational owner, a runbook and a rehearsed recovery path

    @VF-SUP-001 @R1-Pilot @Must
    Scenario: Reject production exposure without readiness
      Given a critical capability without an accountable operational owner or a rehearsed recovery path
      When it is proposed for production exposure
      Then the exposure is blocked
