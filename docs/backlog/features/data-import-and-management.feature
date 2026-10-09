# Imprana Commons backlog: Data import and management
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Data import and management

  Rule: FR-DAT-001 File ingestion
    As a Data Steward, I want an import wizard where I choose file, sheet, encoding, delimiter, header row, locale, date pattern and source key and preview raw against interpreted values, so that data is interpreted exactly as intended before commit.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-DAT-001 @R1-Pilot @Must
    Scenario: Preview exact interpretation before commit
      Given a file containing 00123, a 20 digit ID, 03/04/2026 and a quoted comma
      When the Data Steward previews the import with an explicit date pattern
      Then raw and interpreted values are shown side by side for each value
      And 00123 and the 20 digit ID are kept as text with all digits and leading zeros preserved
      And the quoted comma remains within one field

    @FR-DAT-001 @R1-Pilot @Must
    Scenario: Formulas follow the declared mode
      Given a file containing formulas
      When it is imported
      Then formulas are imported as permitted values or rejected according to the declared mode

    @FR-DAT-001 @R1-Pilot @Must
    Scenario: Reject ambiguous or unsafe input
      Given a date such as 03/04/2026 with no explicit date pattern
      When the import is previewed
      Then an explicit pattern is required before commit
      And mixed-type values produce row errors
      And file safety checks run before any parsing

  Rule: FR-DAT-002 Mapping and preview
    As a Data Steward, I want versioned mappings that bind source fields to destination fields, types, units and transformations, with a preview of gaps and errors, so that imports map correctly even when source columns move or change.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-DAT-002 @R1-Pilot @Must
    Scenario: Preview shows mapping issues
      Given a mapping version
      When the import is previewed
      Then unmatched required fields, dropped columns, conversion errors and sample outcomes are shown
      And AI suggestions remain unchecked proposals until individually accepted or edited

    @FR-DAT-002 @R1-Pilot @Must
    Scenario: Reordered columns keep known bindings
      Given a recurring source with an approved mapping
      When its columns are reordered and one numeric field is renamed
      Then known bindings are preserved
      And the unknown mapping is paused instead of shifting values

    @FR-DAT-002 @R1-Pilot @Must
    Scenario: Reject positional identity and stale previews
      Given a source column is renamed or changes type
      When the import runs
      Then reviewed remapping is required
      And column position alone is never used as stable identity
      And any existing preview expires when the source or mapping changes

  Rule: FR-DAT-004 Validation and quarantine
    As a Data Steward, I want every imported row classified with an exact outcome under an atomic or partial mode chosen before execution, so that I can reconcile all rows and retry only those that failed.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-DAT-004 @R1-Pilot @Must
    Scenario: Partial mode reconciles all rows
      Given 100 rows with 90 valid, five duplicates and five invalid
      And partial mode was selected before execution
      When the import runs
      Then eligible rows are committed and the exact manifest is returned
      And all 100 outcomes reconcile as accepted insert, accepted update, unchanged duplicate, rejected, quarantined or unprocessed
      And only the five corrected rows are retried

    @FR-DAT-004 @R1-Pilot @Must
    Scenario: Atomic mode commits nothing on a blocking failure
      Given atomic mode was selected before execution
      When any blocking row fails
      Then no rows are committed

    @FR-DAT-004 @R1-Pilot @Must
    Scenario: Reject altered raw input or false rollback claims
      Given an import with rejected rows that is later cancelled
      When the results are reviewed
      Then rejected rows carry safe field errors and the raw input remains unchanged
      And the cancelled job identifies committed rows and never claims full rollback
      And an import cannot execute until its mode is selected

  Rule: FR-DAT-009 Data editing and amendments
    As a Data Steward, I want amendments with reason and scope to create reviewed new revisions that keep earlier values where lawful, so that corrections are controlled, traceable and correctly reflected in indicators.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-DAT-009 @R1-Pilot @Must
    Scenario: Unit correction recalculates impacted indicators
      Given an approved value recorded in kilograms
      When an amendment correcting the unit to tonnes is approved
      Then a new revision is created and earlier values are retained where lawful
      And impacted indicators are recalculated under reviewed semantics
      And old reports remain frozen

    @FR-DAT-009 @R1-Pilot @Must
    Scenario: Bulk correction with itemised preview
      Given a bulk correction
      When it is previewed and applied
      Then an itemised preview and outcome receipts are produced

    @FR-DAT-009 @R1-Pilot @Must
    Scenario: Reject editing calculated actuals
      Given a calculated actual
      When a user tries to edit it through dataset correction
      Then the edit is refused
      And where deletion or minimisation policy applies, only a permitted change marker is kept instead of sensitive before and after values

  Rule: FR-DAT-003 Import mode and identity
    As a Data Steward, I want to choose append, keyed update or controlled replacement with a declared source namespace and stable key and preview every effect, so that repeated imports update data without duplicating achievements or deleting records unintentionally.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-DAT-003 @R2-Scale @Must
    Scenario: Keyed reloads do not duplicate achievements
      Given a keyed file
      When it is loaded twice and then loaded a third time with one row revised
      Then the second run creates no new achievement
      And the third run creates one correction revision

    @FR-DAT-003 @R2-Scale @Must
    Scenario: Preview and commit record every effect
      Given an import mode, source namespace and stable key are selected
      When the import is previewed and committed
      Then the preview computes inserts, revisions, unchanged duplicates and removals
      And commit records original and resulting revision references for every effect

    @FR-DAT-003 @R2-Scale @Must
    Scenario: Reject unsafe append and implied deletion
      Given an append without reliable keys or a replacement without explicit scope
      When it is previewed
      Then the append warns that deduplication cannot establish entity uniqueness
      And the replacement is refused until explicit scope and deletion impact are approved
      And records absent from a partial file are not deleted

  Rule: FR-DAT-005 Immutable raw source
    As a Data Steward, I want raw source values kept separately from derived values, with receipt details and lineage to file, sheet or payload and row key, so that every result can be traced back to its unchanged source.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-DAT-005 @R2-Scale @Must
    Scenario: Trace a corrected date to its raw source
      Given an imported date whose interpretation was corrected
      When the Data Steward traces the result
      Then lineage resolves to the source file, sheet and row key with the unchanged raw text
      And the mapping version that produced each interpretation is shown

    @FR-DAT-005 @R2-Scale @Must
    Scenario: Receipt records source details
      Given a source file
      When it is received
      Then its integrity reference, receipt time, source owner and import settings are recorded

    @FR-DAT-005 @R2-Scale @Must
    Scenario: Reject broad access or retention exemptions for raw data
      Given raw values subject to privacy deletion or retention
      When the policy applies
      Then raw storage is not exempt
      And restricted previews inherit the source classification and access
      And original files are not broadly downloadable

  Rule: FR-DAT-006 Governed transformations
    As a Data Steward, I want to author bounded, typed recode, derive, filter, join and reshape transformations with previews of counts, unmatched keys, duplicates and join cardinality, so that transformations do not silently inflate or distort results.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-DAT-006 @R2-Scale @Should
    Scenario: Join preview prevents reach inflation
      Given one participant linked to three visits
      When a one to many join is previewed
      Then the preview shows three output rows and a distinct participant count of one
      And it reports input and output counts, unmatched keys and duplicates

    @FR-DAT-006 @R2-Scale @Should
    Scenario: Publishing pins versions
      Given a previewed transformation
      When it is published
      Then its rule and source versions are pinned

    @FR-DAT-006 @R2-Scale @Should
    Scenario: Reject undeclared joins and code execution
      Given a join without declared one to one, one to many or many to one intent
      When it is saved
      Then it is rejected
      And a many to many join without explicit reviewed justification is rejected
      And expressions cannot execute unrestricted code

  Rule: FR-DAT-007 Schema drift
    As a Data Steward, I want recurring loads compared against the approved source contract and paused for review when fields go missing or change, so that incompatible source changes never silently corrupt results.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-DAT-007 @R2-Scale @Must
    Scenario: Added optional field is ignored with notice
      Given a recurring load with an added optional field
      When it is compared with the approved source contract
      Then the field may be ignored and a notice is shown

    @FR-DAT-007 @R2-Scale @Must
    Scenario: Type change pauses dependent processing
      Given a numerator column changes from decimal to free text
      When the recurring load runs
      Then affected processing pauses for review
      And dependent result freshness becomes failed or stale until a reviewed mapping resolves it

    @FR-DAT-007 @R2-Scale @Must
    Scenario: Reject silent coercion
      Given a load with missing required, renamed, type changed or unit changed fields
      When it is processed
      Then incompatible text is not treated as zero
      And a new date locale is not silently inferred
      And unaffected validated data proceeds only when partial mode was approved

  Rule: FR-DAT-008 Data catalogue and lineage
    As a Data Steward, I want a catalogue showing each permitted dataset's owner, purpose, schema, coverage, classification, quality and freshness, with authorised lineage traversal, so that I can assess impact before correcting or retiring data.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-DAT-008 @R2-Scale @Should
    Scenario: Identify affected reports for a stale dataset
      Given a stale dataset consumed by authorised reports and by a restricted programme
      When the Data Steward inspects its impact
      Then the affected authorised reports are identified
      And the restricted programme is not exposed

    @FR-DAT-008 @R2-Scale @Should
    Scenario: Catalogue entries show permitted metadata
      Given a dataset the user may access
      When it appears in catalogue results
      Then its permitted name, owner, purpose, schema, coverage, classification, quality and freshness are shown

    @FR-DAT-008 @R2-Scale @Should
    Scenario: Reject disclosure through lineage edges
      Given a hidden source in a lineage path
      When lineage is traversed
      Then the hidden source name and counts are not revealed
      But a permitted derivative may show a withheld source reference under its disclosure contract

  Rule: FR-DAT-010 Refresh scheduling and freshness
    As a Data Steward, I want each source to record its cadence and when data was last received, validated and approved, with dashboards showing the relevant freshness stage, so that a successful fetch is never mistaken for usable data.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-DAT-010 @R2-Scale @Should
    Scenario: Source records schedule and freshness stages
      Given a scheduled source
      When its health is viewed
      Then cadence, zone, next run, last received, last validated and last approved data times are shown
      And schedule changes preview the affected runs

    @FR-DAT-010 @R2-Scale @Should
    Scenario: Fetch succeeds but validation fails
      Given a refresh where the fetch succeeds and validation fails
      When source health and dependent dashboards are viewed
      Then source health distinguishes the successful fetch from the failed validation
      And dependent dashboards do not show a fresh approved result

    @FR-DAT-010 @R2-Scale @Should
    Scenario: Reject clearing the last known result on failure
      Given a missed or failed refresh
      When dependent results are viewed
      Then the last known result is not cleared
      And it is labelled stale with a link to the authorised failure owner
      And overlapping scheduled runs follow one declared checkpoint sequence

  Rule: FR-DAT-011 Data exports and portability
    As an Analyst, I want to export authorised rows and fields with their semantic metadata in a safe format, so that exported data stays accurate, portable and secure when opened in other tools.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-DAT-011 @R2-Scale @Must
    Scenario: Export includes semantic metadata
      Given authorised rows and fields are selected
      When the Analyst exports them
      Then the export includes stable IDs, type dictionary, code lists, units, time zone, source versions and value states
      And large exports follow job and revocation controls

    @FR-DAT-011 @R2-Scale @Must
    Scenario: Formula-like text and leading-zero IDs are safe
      Given data containing text beginning with an equals sign and a leading-zero ID
      When the exported file is opened
      Then no formula executes
      And the ID remains text
      And the safe export encoding is documented

    @FR-DAT-011 @R2-Scale @Must
    Scenario: Reject leaking unselected or private data
      Given an export of selected columns
      When the file and its metadata are inspected
      Then no hidden unselected columns or private raw values are present
      And formula-like text is neutralised without silently changing its represented meaning

  Rule: FR-DAT-012 Data retention and dependency review
    As a Privacy Officer, I want dataset archival or deletion to start with a dependency and retention review and produce an itemised manifest, so that deleted data cannot be recovered from any copy while lawful holds remain controlled.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-DAT-012 @R2-Scale @Must
    Scenario: Review dependencies before deletion
      Given a dataset selected for archival or deletion
      When the review preview opens
      Then it separates live inputs, retained snapshots, indexes, AI references and external disclosures

    @FR-DAT-012 @R2-Scale @Must
    Scenario: Deletion produces an itemised manifest
      Given an eligible source is deleted
      When execution completes
      Then an itemised restriction or deletion manifest lists holds and retryable failures
      And search, AI and generated private exports cannot recover the source
      And held evidence appears only in the authorised hold inventory

    @FR-DAT-012 @R2-Scale @Must
    Scenario: Reject orphaned or unlabelled retained artifacts
      Given deletion has executed
      When remaining artifacts are checked
      Then no readable orphan artifacts remain
      And any lawful retained snapshot is explicitly restricted and labelled
      And a historical publication whose continued exposure is no longer permitted can be withdrawn
