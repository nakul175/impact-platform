# Imprana Commons backlog: NFR capacity
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR capacity

  Rule: VF-CAP-001 Supported object limits
    As a Data Steward, I want the platform to support large forms, files and imports up to clearly published limits, so that I know before starting work what will be accepted.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @VF-CAP-001 @R2-Scale @Should
    Scenario: Form limits are qualified at their boundaries
      Given forms with 199, 200 and 201 questions and with 99, 100 and 101 repeat entries
      When they are tested
      Then forms with 200 questions and 100 repeat entries are supported
      And existing drafts are preserved

    @VF-CAP-001 @R2-Scale @Should
    Scenario: File and import limits are qualified
      Given source files at the 100 MB boundary, media files at the 25 MB boundary and an import of one million rows
      When they are processed
      Then source files up to 100 MB and media files up to 25 MB are accepted
      And the one million-row import completes through an asynchronous path

    @VF-CAP-001 @R2-Scale @Should
    Scenario: Limits are visible before work begins
      Given a Data Steward is about to start a form, upload or import
      When the work is set up
      Then the limits and supported combinations are visible before work begins

    @VF-CAP-001 @R2-Scale @Should
    Scenario: Reject undocumented units or frontend constraints
      Given the advertised object limits
      When qualification is assessed
      Then it fails if decimal versus binary file size units were not documented beforehand
      And it fails if an undocumented frontend constraint reduces any advertised limit

  Rule: VF-CAP-002 Scaling and workload isolation
    As a Platform Operator, I want the service to admit, queue or limit work predictably as demand rises and keep tenant workloads isolated, so that one tenant's large import or AI job does not degrade service for others.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @VF-CAP-002 @R2-Scale @Must
    Scenario: Burst load is handled predictably and recovers
      Given the baseline workload
      When a five-minute twofold arrival burst is applied
      Then work is admitted, queued or limited predictably
      And queues stay bounded and the service recovers to baseline after the burst

    @VF-CAP-002 @R2-Scale @Must
    Scenario: Noisy tenant does not cause other tenants to miss targets
      Given a noisy tenant running a large bulk import or AI job
      And representative other tenants saving and approving records
      When the workloads run together
      Then the unrelated tenants continue to meet core service targets
      And queue depth, rejections and recovery to baseline are measured

    @VF-CAP-002 @R2-Scale @Must
    Scenario: Reject unbounded queues, starvation or hidden violations
      Given results from the burst and noisy-tenant tests
      When the results are reviewed
      Then unbounded queue growth fails the test
      And unexplained starvation fails the test
      And target violations hidden by service-wide averages fail the test
