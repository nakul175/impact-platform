# Imprana Commons backlog: NFR audit
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR audit

  Rule: VF-AUD-001 Audit coverage and retention
    As an Organisation Administrator, I want all security and business audit events captured, searchable and retained without secrets or unnecessary personal data, so that I can investigate activity and demonstrate accountability.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @VF-AUD-001 @R1-Pilot @Must
    Scenario: Every audit event class is captured and searchable
      Given every defined audit event class is executed, including denied operations, restricted reads and privileged actions
      When an authorised reviewer searches the audit log
      Then each event is found
      And command receipts reconcile to immutable events and a permitted audit export

    @VF-AUD-001 @R1-Pilot @Must
    Scenario: Retention defaults are applied and verified separately
      Given security event metadata and business audit events
      When retention is applied
      Then security event metadata expires by default after 365 days
      And longer business audit retention follows tenant policy and is verified separately

    @VF-AUD-001 @R1-Pilot @Must
    Scenario: Reject secrets or unnecessary personal payloads in audit events
      Given captured audit events
      When they are inspected
      Then any secret value fails the check
      And any unnecessary personal payload fails the check
