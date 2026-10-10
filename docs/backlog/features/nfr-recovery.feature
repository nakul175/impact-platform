# Imprana Commons backlog: NFR recovery
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR recovery

  Rule: VF-DR-001 Disaster recovery
    As a Platform Operator, I want to recover the service from a catastrophic incident with minimal data loss and downtime within permitted regions, so that organisations' records, files and governance are restored intact.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @VF-DR-001 @R1-Pilot @Must
    Scenario: Recovery meets recovery point and recovery time objectives
      Given a simulated regional disaster has been declared for the standard qualified deployment
      When the service is restored
      Then the recovery point is at most 15 minutes
      And service is recovered within 4 hours of incident declaration

    @VF-DR-001 @R1-Pilot @Must
    Scenario: Recovery stays in permitted regions and is complete
      Given a restore is in progress
      When recovery completes
      Then it has occurred only in a permitted region
      And files, configuration and governance state are restored
      And records and attachments are reconciled against the latest accepted receipts

    @VF-DR-001 @R1-Pilot @Must
    Scenario: Reject reopening with mismatched governance
      Given a restored environment with mismatched governance or missing deletion restrictions
      When reopening is requested
      Then the service is not reopened

    @VF-DR-001 @R1-Pilot @Must
    Scenario: Reject a recovery report based only on backup timestamps
      Given recovery is complete
      When the recovery report is produced
      Then it states the actual lost interval and the affected accepted writes
      But a report showing only backup timestamps is rejected

  Rule: VF-DR-002 Ordinary failure durability
    As a Data Author, I want a server-confirmed save to mean my record is durably kept, with offline saves clearly distinct, so that I can trust confirmed work is not lost.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @VF-DR-002 @R1-Pilot @Must
    Scenario: Server acknowledgement survives an ordinary single component failure
      Given a Data Author saves a record and receives a server receipt
      When a qualified individual component is interrupted during or around the write
      Then the recovered record, its child relationships and files match the receipt

    @VF-DR-002 @R1-Pilot @Must
    Scenario: Offline local saves are clearly distinct
      Given a Data Author saves a record while offline
      When the save completes locally
      Then it is clearly shown as a local save, distinct from a server acknowledgement

    @VF-DR-002 @R1-Pilot @Must
    Scenario: Reject silent loss of an acknowledged save
      Given a successful server receipt for a saved record
      When an ordinary qualified single component failure occurs
      Then the record does not silently disappear
      And any uncertain client outcome is reconciled by operation identity

  Rule: VF-DR-003 Recovery testing and backups
    As a Platform Operator, I want backups protected from tampering, restores tested regularly and backup retention kept to the default window, so that recovery works when needed and data is not kept longer than allowed.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @VF-DR-003 @R1-Pilot @Must
    Scenario: Backups are protected against alteration
      Given backups of tenant data
      When unauthorised alteration or use of compromised credentials is attempted
      Then the backups cannot be altered

    @VF-DR-003 @R1-Pilot @Must
    Scenario: Restores and disaster recovery are tested on schedule
      Given the backup schedule
      When the monthly representative restore and quarterly disaster exercise are run
      Then protected backup access, attachment integrity, snapshot consistency, key recovery and deletion replay are tested before reopening

    @VF-DR-003 @R1-Pilot @Must
    Scenario: Default backup retention is no more than 35 days
      Given no approved contract or hold requires a different schedule
      When backups age
      Then they are retained for no more than 35 days

    @VF-DR-003 @R1-Pilot @Must
    Scenario: Reject an archive download as a completed restore
      Given a backup archive has been downloaded successfully
      When the restore test is assessed
      Then it is not recorded as a completed restore

    @VF-DR-003 @R1-Pilot @Must
    Scenario: Reject silent extension of backup retention
      Given a backup retention exception
      When the default window would be extended
      Then the exception and its owner are recorded
      But the default window is never extended silently
