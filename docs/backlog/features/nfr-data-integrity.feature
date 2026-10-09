# Imprana Commons backlog: NFR data integrity
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR data integrity

  Rule: VF-DIN-001 Calculation correctness
    As a MEL Manager, I want every official calculation to match independently prepared expected results exactly, so that published results can be trusted.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @VF-DIN-001 @R1-Pilot @Must
    Scenario: Golden corpus passes exactly before release
      Given the approved deterministic golden corpus CAL01 through CAL20 with version, correction, missingness and permission variants
      When it is run against independently prepared expected results
      Then every case passes exactly at the defined precision
      And raw and displayed decimals and report bindings match

    @VF-DIN-001 @R1-Pilot @Must
    Scenario: Corpus covers the required calculation semantics
      Given the approved golden corpus
      When its coverage is reviewed
      Then it covers pooled ratios, distinct counts, period semantics, dimensions, corrections, rounding, missingness, cycles and permissions

    @VF-DIN-001 @R1-Pilot @Must
    Scenario: Reject release with an unexplained discrepancy
      Given an unexplained difference between an official result and its expected result
      When the release gate is evaluated
      Then the release is blocked
      But a numerical tolerance is applied only where the approved calculation contract defines it

  Rule: VF-DIN-002 Concurrent change integrity
    As a Data Author, I want concurrent edits, approvals and retries to be handled safely, so that no update is silently lost, no achievement is duplicated and no stale version is approved.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @VF-DIN-002 @R1-Pilot @Must
    Scenario: Concurrent edits do not silently overwrite each other
      Given two Data Authors edit the same record at the same time
      When both save
      Then one save completes with recorded effects
      And the stale save is rejected explicitly rather than silently overwriting the other

    @VF-DIN-002 @R1-Pilot @Must
    Scenario: Repeated commands and interrupted jobs do not duplicate results
      Given an import command is repeated or a bulk job is interrupted
      When processing finishes
      Then no achievement is duplicated
      And the operation either completes with recorded effects or returns an explicit recoverable partial outcome with complete per-item receipts

    @VF-DIN-002 @R1-Pilot @Must
    Scenario: Approvals apply only to the reviewed version
      Given a Reviewer approved an earlier version of a record
      And a new candidate version has since been submitted
      When approval is applied
      Then the earlier decision is not used to approve the new candidate

    @VF-DIN-002 @R1-Pilot @Must
    Scenario: Reject silent overwrite, duplicate result or stale approval
      Given racing edits, racing approvals, repeated imports and interrupted bulk jobs
      When outcomes are verified
      Then any silent last-write overwrite fails
      And any duplicate intended result fails
      And any approval of a new candidate using an old decision fails
