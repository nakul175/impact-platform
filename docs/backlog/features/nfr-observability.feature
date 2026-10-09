# Imprana Commons backlog: NFR observability
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR observability

  Rule: VF-OBS-001 Operational diagnosability
    As a Platform Operator, I want failures traceable across user actions, jobs and integrations, and critical failures alerted quickly without exposing secrets, so that I can diagnose and fix problems for the right tenant fast.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @VF-OBS-001 @R1-Pilot @Must
    Scenario: Failure is traced with one correlation reference
      Given failures injected at report receipt, calculation, rendering and delivery
      When the Platform Operator traces a failure
      Then one safe correlation reference links the user action, background jobs and integration events across the authorised stages
      And logs support tenant-scoped diagnosis while keeping audit separate

    @VF-OBS-001 @R1-Pilot @Must
    Scenario: Critical failure alert is raised within 5 minutes
      Given a critical service failure meets its defined detection condition
      When the alert is generated
      Then it is created within 5 minutes of the detection condition

    @VF-OBS-001 @R1-Pilot @Must
    Scenario: Reject missing context, secrets or late alerts
      Given diagnostics and alerts from the injected failures
      When they are inspected
      Then missing tenant context fails the gate
      And any secret payload in diagnostics fails the gate
      And a critical alert delayed beyond 5 minutes fails the gate
