# Imprana Commons backlog: NFR maintainability
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR maintainability

  Rule: VF-MNT-001 Maintainable contracts
    As a Product Owner, I want business rules, APIs, policies and data dictionaries documented, version controlled and traceable, with routine configuration needing no customer-specific code, so that the product stays maintainable as it changes.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @VF-MNT-001 @R2-Scale @Should
    Scenario: Different programmes are configured through supported settings
      Given two different programme templates
      When they are configured
      Then ordinary supported settings are sufficient without a customer-specific code fork

    @VF-MNT-001 @R2-Scale @Should
    Scenario: Rule changes are traceable to requirements and tests
      Given a material rule amendment
      When it is traced
      Then it links through requirements, the data dictionary, the interface contract and regression evidence
      And each of these is documented and version controlled

    @VF-MNT-001 @R2-Scale @Should
    Scenario: Reject code forks and unmanaged breaking changes
      Given a routine tenant configuration need
      When it can only be met by a customer-specific code fork
      Then the requirement is not satisfied
      And a breaking change that bypasses the published compatibility process is rejected
