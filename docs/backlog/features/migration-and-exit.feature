# Imprana Commons backlog: Migration and exit
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Migration and exit

  Rule: FR-MIG-007 Full tenant export
    As an Executive Director, I want a full machine-readable export of our tenant's records, relationships, files, dictionaries, versions, permitted decisions and configuration with a manifest, so that we own our data and can rebuild it outside the platform.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-MIG-007 @R1-Pilot @Must
    Scenario: Reconstruct relationships outside the application
      Given a full tenant export package
      When it is used outside the application
      Then programme-to-indicator-to-result-to-report relationships can be reconstructed
      And sample file integrity is verified

    @FR-MIG-007 @R1-Pilot @Must
    Scenario: Manifest describes the export
      Given a completed tenant export
      When the manifest is inspected
      Then it records counts, integrity references, exclusions and restoration instructions independent of internal infrastructure

    @FR-MIG-007 @R1-Pilot @Must
    Scenario: Reject silent omission of secrets
      Given configuration containing secret values
      When the export is built
      Then secret values are excluded
      And they are listed in the manifest as requiring reconfiguration

    @FR-MIG-007 @R1-Pilot @Must
    Scenario: Reject bypassing sensitive content policy on exit
      Given an owner initiates exit
      When the export reaches sensitive content
      Then access to that content remains policy governed

  Rule: FR-MIG-001 Source discovery and mapping
    As a Data Steward, I want to inventory a source system and classify every element as preserved, transformed, excluded or unavailable with owner, method and expected reconciliation, so that migration limitations are explicit before production load.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-MIG-001 @R2-Scale @Must
    Scenario: Discovery inventories the source
      Given a source system to migrate
      When discovery runs
      Then source entities, keys, volumes, semantics, attachments, users, grants and reports are inventoried

    @FR-MIG-001 @R2-Scale @Must
    Scenario: Unknown historic formula is recorded as a limitation
      Given an indicator with an unknown historic formula
      When the Data Steward maps it
      Then the limitation is identified explicitly
      But no deterministic approval history is invented

    @FR-MIG-001 @R2-Scale @Must
    Scenario: Reject production load with undocumented unsupported semantics
      Given a source element with unsupported semantics and no documented decision
      When production load is requested
      Then the load is blocked until the decision is documented
      And mapping does not assume TolaData export provides every historical event or field

  Rule: FR-MIG-002 Trial migrations
    As a Data Steward, I want to run repeatable trial migrations in an isolated tenant with external side effects disabled, so that I can compare outcomes safely before the production migration.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-MIG-002 @R2-Scale @Must
    Scenario: Two identical trials are compared
      Given the same source snapshot and mapping version
      When the Data Steward runs two identical trials into a clean or keyed trial
      Then intended records, errors and totals are compared
      And no duplicate achievements occur
      And no real recipient receives a message

    @FR-MIG-002 @R2-Scale @Must
    Scenario: Reject side effects from trial data
      Given a trial migration in an isolated tenant context
      When trial data would trigger a live notification, payment action, connector write or public report
      Then the action is blocked

    @FR-MIG-002 @R2-Scale @Must
    Scenario: Reject trial credentials in production
      Given credentials issued for a trial
      When they are used against production
      Then access is refused

  Rule: FR-MIG-003 Semantic reconciliation
    As a Data Steward, I want migration reconciliation to compare counts, keys, units, periods, targets, ratios, overlap, attachments and representative reports and record each variance with a decision, so that cutover happens only when results mean the same thing.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-MIG-003 @R2-Scale @Must
    Scenario: Pooled percentage and cumulative series are recomputed
      Given a migrated pooled percentage and a migrated cumulative series
      When both are independently recomputed
      Then semantic differences are resolved before signoff

    @FR-MIG-003 @R2-Scale @Must
    Scenario: Each variance is recorded with a decision
      Given a variance found during reconciliation
      When it is recorded
      Then it captures source value, destination value, cause, severity and decision
      And accepted differences remain visible in migration metadata and, where material, in user-facing limitations

    @FR-MIG-003 @R2-Scale @Must
    Scenario: Reject cutover with critical unexplained differences
      Given a critical unexplained result difference
      When cutover is requested
      Then cutover is blocked
      But record count agreement alone does not satisfy reconciliation

  Rule: FR-MIG-004 Historical provenance
    As a Data Steward, I want imported history to keep original event values, source origin, available evidence and migration receipt separately and label unverified decisions as imported assertions, so that migrated records never pass off reconstructed history as real.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-MIG-004 @R2-Scale @Must
    Scenario: Identify the nature of a migrated approval
      Given a migrated report approval
      When the Data Steward inspects it
      Then it is identified as a preserved source record, verified evidence or a new destination decision

    @FR-MIG-004 @R2-Scale @Must
    Scenario: Destination decisions carry real actors
      Given a decision made in the destination after migration
      When it is recorded
      Then it carries the real current actor and timestamp
      And unverified source decisions are labelled imported assertions

    @FR-MIG-004 @R2-Scale @Must
    Scenario: Reject fabricated history
      Given source history with a missing approval
      When it is migrated
      Then no approval is fabricated
      And migration time is not used as the original event date
      And the missing history is represented as unavailable

  Rule: FR-MIG-005 Cutover and rollback
    As a Data Steward, I want a cutover runbook that sets the authoritative system, freeze instant or delta method, final reconciliation, owners and rollback trigger, so that late source changes are captured and only one system publishes official results.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-MIG-005 @R2-Scale @Must
    Scenario: Late source update is captured
      Given the final transfer is in progress
      When one source record is updated
      Then the update receives a stable key
      And it is captured in the final delta or reported as a controlled exclusion requiring resolution

    @FR-MIG-005 @R2-Scale @Must
    Scenario: Rollback identifies destination writes
      Given destination writes have begun after authority switched
      When the rollback trigger fires
      Then destination writes needing safe replay or reconciliation are identified

    @FR-MIG-005 @R2-Scale @Must
    Scenario: Reject destination writes before the authority switch
      Given authority has not yet switched to the destination
      When a destination write is attempted
      Then the write is refused

    @FR-MIG-005 @R2-Scale @Must
    Scenario: Reject both systems publishing the same period
      Given the source and destination systems during cutover
      When both attempt to publish the same official period independently
      Then the duplicate publication is prevented

  Rule: FR-MIG-006 User enablement
    As an Organisation Administrator, I want onboarding to assign role-specific practice tasks on safe sample programmes and record task outcomes, so that staff are ready for their roles without training granting production access.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-MIG-006 @R2-Scale @Should
    Scenario: Enumerator and reviewer complete practice tasks
      Given a Field Data Collector and a Reviewer enrolled in onboarding with safe sample programmes
      When the Field Data Collector completes offline practice
      And the Reviewer returns and then approves a correction
      Then each task outcome is recorded as completion evidence
      And neither can access real participant records in training

    @FR-MIG-006 @R2-Scale @Should
    Scenario: Administrators verify scopes and help explains concepts
      Given role-specific practice tasks assigned to users
      When the Organisation Administrator verifies their scopes
      Then each user completes setup, collection, correction, review or viewing tasks relevant to their role
      And help links explain both actions and measurement concepts

    @FR-MIG-006 @R2-Scale @Should
    Scenario: Reject training that grants access or counts attendance
      Given a user who has finished training
      When their access and completion are evaluated
      Then no production access is granted by default
      And attendance alone is not recorded as completion evidence

  Rule: FR-MIG-008 Closure and deletion evidence
    As an Executive Director, I want tenant closure to confirm retrieval window, export status, integrations, credentials, jobs, holds and deletion schedule and give me an outcome record, so that I have evidence of what was terminated, deleted and lawfully retained.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-MIG-008 @R2-Scale @Must
    Scenario: Close a tenant after confirmed export
      Given a tenant with a confirmed export and one held item
      When the tenant is closed
      Then live credentials and deliveries stop
      And the outcome record identifies the held item and its review date

    @FR-MIG-008 @R2-Scale @Must
    Scenario: Outcome record shows closure evidence
      Given a closed tenant
      When the Executive Director opens the outcome record
      Then it shows access termination, completed deletion, backup expiry and outstanding lawful retention

    @FR-MIG-008 @R2-Scale @Must
    Scenario: Reject a closure shortcut that bypasses holds or the window
      Given a tenant with a hold or unexported data within the agreed retrieval window
      When a closure shortcut is attempted
      Then the hold is not bypassed
      And unexported data is not erased before the agreed window ends

    @FR-MIG-008 @R2-Scale @Must
    Scenario: Reject ordinary reopen after irreversible deletion
      Given irreversible deletion has completed for a closed tenant
      When reactivation is requested
      Then it is not offered as an ordinary reopen
