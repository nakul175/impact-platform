# Imprana Commons backlog: NFR portability
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR portability

  Rule: VF-PRT-001 Portability and exit quality
    As an Organisation Administrator, I want a complete, documented export of my organisation's data and attachments, so that we can leave or reuse our data without losing relationships or meaning.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @VF-PRT-001 @R1-Pilot @Must
    Scenario: Standard tenant export is delivered within 24 hours
      Given a standard tenant with up to one million structured rows and 10 GB of attachments
      When the Organisation Administrator requests a tenant export under the agreed service process
      Then a complete asynchronous package with a documented manifest and machine-readable relationships is delivered within 24 hours
      And completeness, integrity, permissions and exclusions are verified within that time

    @VF-PRT-001 @R1-Pilot @Must
    Scenario: Package is usable outside the product
      Given the delivered export package
      When representative relationships and selected reports are reconstructed using only the package documentation
      Then the reconstruction succeeds

    @VF-PRT-001 @R1-Pilot @Must
    Scenario: Larger exports show an estimate and progress
      Given a tenant larger than the standard size
      When an export is requested
      Then a visible estimate and progress are shown

    @VF-PRT-001 @R1-Pilot @Must
    Scenario: Reject a collection of unlabelled files
      Given an export made up of unlabelled CSV files
      When it is assessed
      Then it is not accepted as a complete tenant export
