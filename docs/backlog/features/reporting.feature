# Imprana Commons backlog: Reporting
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Reporting

  Rule: FR-RPT-003 Frozen reporting packages
    As a MEL Manager, I want each report built from a locked snapshot with numeric fields bound to immutable results, so that regenerating an old report reproduces exactly what was authorised and later corrections appear as separate versions.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-RPT-003 @R1-Pilot @Must
    Scenario: Regenerate an old quarter after a live correction
      Given a report for an old quarter was created from a locked snapshot
      And the live source data has since been corrected
      When the MEL Manager regenerates the old quarter report
      Then its authorised numeric content stays unchanged
      And the later correction is a separate report version

    @FR-RPT-003 @R1-Pilot @Must
    Scenario: Regeneration uses the same versions
      Given a report created from a locked snapshot
      When the report is regenerated
      Then it uses the same definition, target, result, evidence and configuration versions
      And the rendering version is recorded separately from the content version

    @FR-RPT-003 @R1-Pilot @Must
    Scenario: Reject reconstructing lawfully deleted evidence
      Given evidence in a report has been lawfully deleted
      When the report is regenerated or accessed
      Then the withheld evidence is disclosed as withheld or the artifact is withdrawn as required
      But the deleted content is not reconstructed to preserve visual identity
      And numeric history is retained only where lawful

  Rule: FR-RPT-007 Publication control
    As a MEL Manager, I want to publish an approved report to a defined audience only after previewing its version, audience, disclosure checks and expiry, so that unpublished content is never exposed and only eligible recipients can access it.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-RPT-007 @R1-Pilot @Must
    Scenario: Publish an approved version to a funder
      Given a report version has been approved and any required privacy review is complete
      And the MEL Manager is an authorised publisher with current assurance
      When the MEL Manager reviews the preview of version, audience, disclosure checks and expiry and confirms publication to a funder
      Then a disclosure record and a stable versioned reference are created
      And only the eligible funder can access the published artifact

    @FR-RPT-007 @R1-Pilot @Must
    Scenario: Reject access to a draft by guessed URL
      Given a draft report that has not been published
      When someone guesses its URL or filename
      Then the draft content is not accessible
      And it is not exposed through search indexing

    @FR-RPT-007 @R1-Pilot @Must
    Scenario: Reject broadening the audience by a link toggle
      Given a report published to a funder
      When a user attempts to make it available to a broader audience by toggling a link
      Then the change is refused until a new disclosure decision is made

  Rule: FR-RPT-009 Amend withdraw and supersede
    As a MEL Manager, I want to withdraw or supersede a published report with a recorded reason, authority and impact review, so that recipients are directed to the correct version while the record of who received the old one is kept.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-RPT-009 @R1-Pilot @Must
    Scenario: Supersede report v1 with v2
      Given report v1 has been published and distributed
      And a separately approved replacement v2 exists
      When the MEL Manager supersedes v1 with v2
      Then old links to v1 expose only the permitted supersession status
      And the distribution log identifies the v1 recipients

    @FR-RPT-009 @R1-Pilot @Must
    Scenario: Withdraw a published report
      Given a published report
      When the MEL Manager withdraws it with a reason, authority and impact review
      Then the live publication becomes unavailable or displays an approved withdrawal notice without protected content

    @FR-RPT-009 @R1-Pilot @Must
    Scenario: Reject withdrawal without reason or authority
      Given a published report
      When a user attempts to withdraw it without a reason, current authority or impact review
      Then the withdrawal is refused

    @FR-RPT-009 @R1-Pilot @Must
    Scenario: Reject claims of recalling downloaded copies
      Given recipients have already downloaded v1
      When v1 is withdrawn or superseded
      Then the downloaded copies remain recorded as external disclosures
      And notices refer to the obsolete version and corrective action
      But the system never claims recall of already downloaded bytes

  Rule: FR-RPT-010 Reporting reconciliation
    As a Reviewer, I want every number in a report candidate reconciled against its snapshot and version changes separated by cause, so that no unexplained official figure passes review.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-RPT-010 @R1-Pilot @Must
    Scenario: Identify every location affected by a metric change
      Given one approved metric used in a report has changed
      When preapproval reconciliation runs on the new report candidate
      Then every affected narrative and chart location is identified before approval

    @FR-RPT-010 @R1-Pilot @Must
    Scenario: Version comparison separates change types
      Given two versions of a report
      When the Reviewer compares them
      Then source, definition, target, calculation, period and narrative changes are shown separately

    @FR-RPT-010 @R1-Pilot @Must
    Scenario: Reject unexplained official numeric differences
      Given a report candidate with an official number that differs from the snapshot without explanation
      When the Reviewer attempts to approve it
      Then approval is blocked

    @FR-RPT-010 @R1-Pilot @Must
    Scenario: Reject unbound manually written numbers
      Given a manually written number in a report candidate
      When it has neither an explicit source binding nor a reviewed non-result classification such as a date or section number
      Then the candidate cannot pass review

  Rule: FR-RPT-001 Report template library
    As a MEL Manager, I want versioned report templates defining sections, metric bindings, tables, charts, narrative limits, evidence slots, language and mandatory caveats, so that donor reports are produced consistently from approved data without altering reports already created.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-RPT-001 @R2-Scale @Should
    Scenario: Two donor reports from one snapshot reconcile
      Given published report templates for donor A and donor B
      When the MEL Manager generates quarterly reports for both from one approved snapshot
      Then shared numeric fields in both reports reconcile to the same result IDs

    @FR-RPT-001 @R2-Scale @Should
    Scenario: Template preview validates against a snapshot
      Given a draft report template
      When the MEL Manager previews it
      Then it is validated against a representative approved snapshot

    @FR-RPT-001 @R2-Scale @Should
    Scenario: Reject zero placeholders for missing bindings
      Given a template with a required metric binding that is missing
      When a report is generated
      Then the missing binding appears as an explicit gap
      But no zero placeholder is inserted

    @FR-RPT-001 @R2-Scale @Should
    Scenario: Reject silent changes to published reports
      Given a report created from a published template version
      When the donor template is changed
      Then a new template version is created
      And the existing report stays pinned to its original template version without being restyled or changed

  Rule: FR-RPT-002 Reporting obligations
    As a Programme Manager, I want each reporting obligation tracked with its recipient, period, due date, owner, required indicators, template and review route, so that every donor deadline is met and no obligation is closed by mistake.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-RPT-002 @R2-Scale @Must
    Scenario: Quarterly and annual obligations tracked separately
      Given a project with a quarterly obligation and an annual obligation
      When the Q4 report is completed
      Then the Q4 obligation is complete
      But the annual obligation is not closed automatically

    @FR-RPT-002 @R2-Scale @Must
    Scenario: Calendar shows dependencies and status
      Given obligations defined for more than one donor
      When the Programme Manager opens the reporting calendar
      Then the donor calendars coexist
      And each instance shows missing dependencies and approval status

    @FR-RPT-002 @R2-Scale @Must
    Scenario: Amendment preserves contractual history
      Given an existing obligation
      When it is amended
      Then the prior due date and contractual reference are preserved

    @FR-RPT-002 @R2-Scale @Must
    Scenario: Reject completion by another donor's report
      Given obligations for donor A and donor B for the same period
      When the report for donor A is sent
      Then donor B's obligation is not marked complete

    @FR-RPT-002 @R2-Scale @Must
    Scenario: Reject leaving an obligation without an owner
      Given an obligation whose owner departs
      When the departure is recorded
      Then reassignment of the obligation is triggered

  Rule: FR-RPT-004 Narrative authoring and review
    As a Data Author, I want to draft, comment on and compare narrative revisions with AI suggestions labelled and factual claims linked to evidence, so that report narratives are accurate and consistent with official figures.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-RPT-004 @R2-Scale @Should
    Scenario: Review AI suggestions before submission
      Given a narrative section containing AI proposed text
      When the Data Author reviews the section
      Then the AI proposed text is labelled until reviewed
      And the Data Author can accept, edit or reject each suggestion before submission
      And material factual claims link to permitted evidence or metric references

    @FR-RPT-004 @R2-Scale @Should
    Scenario: Editing an approved narrative creates a new candidate
      Given an approved narrative
      When the Data Author edits it
      Then a new candidate is created
      And the revision can be compared with the approved version

    @FR-RPT-004 @R2-Scale @Should
    Scenario: Reject a narrative number that conflicts with its metric
      Given a narrative and its bound metric both state 180 participants
      When the Data Author changes the narrative to 200 participants while the metric remains 180
      Then the discrepancy is flagged for resolution
      And reconciliation blocks approval until it is resolved

    @FR-RPT-004 @R2-Scale @Should
    Scenario: Reject deleting required caveats through formatting
      Given a narrative section with a required caveat
      When formatting is applied that would remove the caveat
      Then the required caveat is retained

  Rule: FR-RPT-005 Accessible export formats
    As a MEL Manager, I want to export reports as DOCX or PDF and tables as XLSX or CSV with validated, accessible structure, so that exported artifacts match the approved snapshot exactly and can be read by everyone.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-RPT-005 @R2-Scale @Should
    Scenario: Export a large report faithfully
      Given an approved 50-page report with twenty charts
      When the MEL Manager exports it
      Then no values are clipped
      And no caveats are missing
      And all values agree exactly with the snapshot
      And the artifact receipt identifies the report version, format and access expiry

    @FR-RPT-005 @R2-Scale @Should
    Scenario: Export job validates content and structure
      Given a report export in DOCX or PDF or a table export in XLSX or CSV
      When the export job runs
      Then it validates snapshot, fonts, page breaks, headings, tables, figures, units, caveats and filter context
      And accessible standard templates preserve headings and table structure

    @FR-RPT-005 @R2-Scale @Should
    Scenario: Reject marking a failed rendering as published
      Given an export job encounters a rendering failure
      When the job ends
      Then publication is not marked successful

    @FR-RPT-005 @R2-Scale @Should
    Scenario: Reject unremediated conformance claims
      Given a report containing user supplied inaccessible content
      When it is exported
      Then the inaccessible content is flagged
      But the artifact is not claimed conformant until it is remediated

  Rule: FR-RPT-008 Distribution and scheduled delivery
    As a Programme Manager, I want to schedule report deliveries that recheck each recipient's eligibility at send time, so that reports reach the right people and removed recipients never receive protected content.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-RPT-008 @R2-Scale @Must
    Scenario: Removed recipient receives nothing
      Given a delivery schedule with an artifact version or explicit latest-approved policy, three recipients, a cadence and an owner
      When one recipient is removed after scheduling and the delivery runs
      Then notices are sent to the two eligible recipients
      And the removed recipient receives no protected artifact
      And the removed recipient is skipped with a permitted reason

    @FR-RPT-008 @R2-Scale @Must
    Scenario: Sensitive delivery uses authenticated access
      Given a sensitive artifact is scheduled for delivery
      When the delivery is sent
      Then recipients receive an authenticated access notice rather than an unprotected attachment

    @FR-RPT-008 @R2-Scale @Must
    Scenario: Reject sending to recipients from a cached list
      Given a recipient's access has been revoked
      When the delivery runs
      Then recipient membership, purpose, artifact approval and disclosure are rechecked
      And the revoked recipient is not silently retained from a cached list

    @FR-RPT-008 @R2-Scale @Must
    Scenario: Reject treating an unresolved timeout as delivered
      Given a delivery attempt ended in an unresolved provider timeout
      When the delivery status is checked or the delivery is retried
      Then the attempt is tracked as unknown until reconciled
      And any retry uses the delivery identity

  Rule: FR-RPT-012 Report evidence package
    As a Funder Portfolio Manager, I want an audit package with the report, snapshot manifest, dictionary, lineage, sources, decisions and caveats, so that I can verify published results are complete and reproducible without receiving lawfully withheld private data.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-RPT-012 @R2-Scale @Should
    Scenario: Reconstruct a published pooled ratio from the package
      Given an audit package for a published report within the permitted scope
      When the Funder Portfolio Manager uses its contents
      Then the published pooled ratio can be reconstructed
      And file integrity and the content inventory allow completeness to be verified

    @FR-RPT-012 @R2-Scale @Should
    Scenario: Withheld materials are listed without content
      Given an attachment has been lawfully withheld
      When the package is generated
      Then the withheld attachment is identified in the inventory
      But its private data is not included

    @FR-RPT-012 @R2-Scale @Should
    Scenario: Reject download without current export authority
      Given a user whose export authority was removed after the package was generated
      When they attempt to download the package
      Then the download is refused
      And evidence restrictions remain enforced

  Rule: FR-RPT-006 Presentation and donor format output
    As a MEL Manager, I want to produce slides and donor-format submissions from the approved snapshot through versioned mappings, so that figures stay consistent across formats without retyped numbers or fabricated values.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-RPT-006 @R3-Ecosystem @Should
    Scenario: Presentation and donor submission agree
      Given an approved snapshot and versioned mappings for a presentation and a structured donor submission
      When the MEL Manager produces both outputs
      Then shared result values and periods agree despite the different layouts

    @FR-RPT-006 @R3-Ecosystem @Should
    Scenario: Preview and approve a mapping
      Given a slide or donor format mapping
      When the MEL Manager previews the output
      Then omitted optional content and unsupported mandatory fields are listed
      And approval binds the mapping version and intended audience

    @FR-RPT-006 @R3-Ecosystem @Should
    Scenario: Reject retyped authoritative numbers
      Given an output with editable placeholders
      When authoritative numbers are placed in it
      Then they keep maintained bindings to the snapshot
      But they are not retyped without bindings

    @FR-RPT-006 @R3-Ecosystem @Should
    Scenario: Reject fabricated defaults in donor schemas
      Given a donor schema whose required data is missing
      When the submission is validated
      Then validation fails
      But no fabricated default is supplied

  Rule: FR-RPT-011 Transparency publication
    As a MEL Manager, I want to validate and publish to a specifically qualified IATI standard profile and reconcile the external acknowledgement, so that our transparency publications are valid and traceable.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-RPT-011 @R3-Ecosystem @Should
    Scenario: Validation lists payload issues
      Given a publication workspace with a specifically qualified IATI standard profile, organisation identity and mapping
      When the MEL Manager validates a representative payload containing an invalid code
      Then mandatory fields, code list errors and disclosure issues are listed

    @FR-RPT-011 @R3-Ecosystem @Should
    Scenario: Approved version reconciles to the external acknowledgement
      Given the MEL Manager has fixed the invalid code and approved the exact payload version
      When the payload is exported or published directly and the external acknowledgement is received
      Then the payload version and external acknowledgement are recorded
      And the acknowledgement reconciles to the internal publication record

    @FR-RPT-011 @R3-Ecosystem @Should
    Scenario: Reject unspecified schema versions
      Given a schema version that has not been specifically qualified
      When publication against it is attempted
      Then support for that schema version is not claimed

    @FR-RPT-011 @R3-Ecosystem @Should
    Scenario: Reject treating an external rejection as delivered
      Given a payload has been published
      When the external recipient rejects it
      Then the delivery is left as failed or correction required

    @FR-RPT-011 @R3-Ecosystem @Should
    Scenario: Reject claims of erasing third party copies
      Given a published payload must be removed
      When removal follows the qualified route
      Then the system does not claim that third party copies were erased
