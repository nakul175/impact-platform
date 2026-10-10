# Imprana Commons backlog: Evidence
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Evidence

  Rule: FR-EVD-001 Evidence repository
    As a MEL Manager, I want to upload evidence with its type, source, date, owner, sensitivity and retention and link specific versions to results, findings and decisions, so that every claim cites the exact evidence it relied on.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-EVD-001 @R1-Pilot @Must
    Scenario: Upload evidence with metadata and safety status
      Given a user uploading evidence
      When they provide type, source, date, owner, sensitivity and retention
      Then the evidence is stored and receives a safety status

    @FR-EVD-001 @R1-Pilot @Must
    Scenario: Earlier citation stays on its version
      Given version 1 of a survey is linked to an achievement
      When version 2 of the survey is uploaded
      Then the earlier achievement still cites version 1

    @FR-EVD-001 @R1-Pilot @Must
    Scenario: Search exposes only authorised evidence
      Given evidence with different permissions in the repository
      When a user searches the repository
      Then only authorised metadata and content are exposed

    @FR-EVD-001 @R1-Pilot @Must
    Scenario: Reject overwriting a published citation
      Given a file cited by a published result
      When the file is replaced
      Then a new version is created
      But the published citation is never overwritten

    @FR-EVD-001 @R1-Pilot @Must
    Scenario: Reject presenting a source URL as archived
      Given evidence recorded as a source URL
      When it is displayed
      Then it is shown as an external reference with its last checked status
      But it is not presented as an archived guarantee

  Rule: FR-EVD-002 Evidence verification and provenance
    As a MEL Manager, I want evidence verification recorded with reviewer, method, source checks, limitations and status, and disputes traced to every dependent claim, so that claims rely only on evidence whose credibility has been checked.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-EVD-002 @R2-Scale @Must
    Scenario: Record evidence verification
      Given a Reviewer verifying evidence
      When they complete the verification
      Then the reviewer, method, source checks, limitations and verified or disputed status are recorded
      And integrity identity is displayed separately from authenticity

    @FR-EVD-002 @R2-Scale @Must
    Scenario: Dispute previously verified evidence
      Given a verified attendance sheet supports unpublished claims and published reports
      When it is marked disputed
      Then every dependent claim is identified and review tasks are initiated
      And affected unpublished claims require resolution
      And published reports enter correction review

    @FR-EVD-002 @R2-Scale @Must
    Scenario: Reject treating a scan or hash as proof of truth
      Given evidence with a passed malware scan and a file hash
      When no verification has been recorded
      Then the evidence is not treated as verified

    @FR-EVD-002 @R2-Scale @Must
    Scenario: Reject unqualified publication with disputed mandatory evidence
      Given mandatory evidence with an unresolved dispute
      When unqualified publication of a dependent claim is attempted
      Then publication is blocked

  Rule: FR-EVD-003 Search and knowledge retrieval
    As an Analyst, I want to search evidence by source, type, date and permitted classification with permission and purpose filters applied first, so that I find relevant knowledge without seeing anything I am not authorised to access.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-EVD-003 @R2-Scale @Should
    Scenario: Search with filters
      Given indexed evidence
      When an Analyst searches using source, type, date and permitted classification filters
      Then permission and purpose filters are applied before result counts and snippets are produced
      And indexed text shows its source version and extraction status
      And unsupported content shows metadata only

    @FR-EVD-003 @R2-Scale @Should
    Scenario: Reject revealing restricted content in search
      Given a phrase that appears only in a restricted report
      When an unprivileged user searches for that phrase
      Then they receive no matching snippet or citation
      And no count or facet reveals the restricted report

    @FR-EVD-003 @R2-Scale @Should
    Scenario: Reject access after revocation or deletion
      Given a document whose access was revoked or which was deleted
      When users search, view suggested queries or use AI retrieval
      Then the document is not reachable through the index, snippets, suggested queries or AI retrieval

  Rule: FR-EVD-004 Document versioning and annotations
    As an Analyst, I want annotations anchored to a specific document version and location, with reviewed migration to new versions, so that comments and citations always point to the passage they were made on.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-EVD-004 @R2-Scale @Should
    Scenario: Annotate a document version
      Given a document version
      When an Analyst adds an annotation
      Then it references that version and a stable page, section, timestamp or excerpt anchor
      And later comment edits retain the author and permitted history

    @FR-EVD-004 @R2-Scale @Should
    Scenario: Replace a report where pages shift
      Given a published citation to a page of a report
      When the report is replaced by a new version in which pages shift
      Then the old published citation still resolves to the old page
      And migrating an annotation to the new version requires verified remapping with ambiguities flagged

    @FR-EVD-004 @R2-Scale @Should
    Scenario: Reject attaching an unmatched anchor to a similar passage
      Given an annotation anchor that cannot be matched in the new version
      When anchor migration runs
      Then the annotation is marked unresolved
      But it is not attached to a similar passage

  Rule: FR-EVD-007 Quotations and disclosure
    As a Privacy Officer, I want external quotations and stories checked for permission, audience, consent and identifiers and redacted into a separate previewed artifact before disclosure approval, so that published stories cannot reveal participants' identities.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-EVD-007 @R2-Scale @Must
    Scenario: Prepare an external quotation
      Given a quote prepared for an external story
      When it is prepared for disclosure
      Then source permission, intended audience, consent scope and identifiers are checked
      And redaction produces a separate artifact that removes hidden text and metadata
      And the artifact must be previewed before disclosure approval

    @FR-EVD-007 @R2-Scale @Must
    Scenario: Export a redacted case story
      Given a case story with an approved quote and a redacted participant identity
      When it is exported
      Then copied text, metadata and embedded files cannot reveal the redacted identity
      And source citations may be retained privately while public references omit identifying detail

    @FR-EVD-007 @R2-Scale @Must
    Scenario: Reject visual-only redaction
      Given text covered only by a black rectangle
      When the document is submitted for disclosure approval
      Then it is not accepted as redacted

  Rule: FR-EVD-005 Qualitative coding
    As an Analyst, I want coders to assign excerpts independently against a versioned codebook and an adjudicator to record the final interpretation, so that qualitative findings are rigorous and individual coding decisions are preserved.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-EVD-005 @R3-Ecosystem @Should
    Scenario: Maintain a versioned codebook
      Given a codebook
      When codes are defined
      Then each code has a stable identity, meaning, and inclusion and exclusion examples
      And the codebook has a version

    @FR-EVD-005 @R3-Ecosystem @Should
    Scenario: Adjudicate a coding disagreement
      Given two coders label the same transcript differently
      When the comparison shows the disagreement and an adjudicator records the final interpretation
      Then both coders' assignments remain
      And the adjudication records its rationale and codebook version

    @FR-EVD-005 @R3-Ecosystem @Should
    Scenario: Reject invalid agreement or consensus
      Given coded excerpts from two coders
      When agreement is calculated or consensus is recorded
      Then unmatched units are not used to calculate agreement
      And consensus cannot be claimed by overwriting a coder's work

    @FR-EVD-005 @R3-Ecosystem @Should
    Scenario: Reject excerpts losing source restrictions
      Given a restricted source transcript
      When excerpts and themes are created from it
      Then they inherit the source restrictions

  Rule: FR-EVD-006 Transcription and translation
    As an Analyst, I want to request transcription or translation of a recording through an approved destination and correct the resulting segments, so that I can use accurate, traceable text from recordings in analysis and reports.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-EVD-006 @R3-Ecosystem @Should
    Scenario: Request a transcript or translation
      Given a recording
      When an Analyst requests processing with an approved destination, language and permitted task
      Then the generated transcript or translation is a new labelled artifact
      And it is linked to offsets in the original recording

    @FR-EVD-006 @R3-Ecosystem @Should
    Scenario: Correct a translated segment used in a quotation
      Given a translated phrase at minute 03:12 is used in a report quotation
      When the Analyst corrects the phrase
      Then the quotation resolves to the corrected segment and the original recording
      And the original automated output is retained according to policy
      And quotation use requires review of the original meaning

    @FR-EVD-006 @R3-Ecosystem @Should
    Scenario: Reject inventing speakers or timings
      Given a segment where the speaker or timing is uncertain
      When the transcript is generated
      Then the speaker or timing is marked unknown
      But it is not invented

    @FR-EVD-006 @R3-Ecosystem @Should
    Scenario: Reject fallback to an unapproved provider
      Given a sensitive recording
      When the approved processing destination is unavailable
      Then processing does not fall back to an unapproved provider

  Rule: FR-EVD-008 Findings and triangulation
    As a MEL Manager, I want findings to record their statement, method, supporting and contradictory evidence, confidence rationale, limitations and reviewer, with versioned interpretations, so that conclusions are evidence-based and transparent about contradictions.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-EVD-008 @R3-Ecosystem @Should
    Scenario: Record a triangulated finding
      Given survey evidence shows improvement while interviews describe harm
      When the finding is recorded and reviewed
      Then the finding retains both sources
      And it distinguishes observation from interpretation

    @FR-EVD-008 @R3-Ecosystem @Should
    Scenario: Version an interpretation change
      Given a recorded finding
      When its interpretation is edited
      Then a new version is created
      And the changed evidence set is shown

    @FR-EVD-008 @R3-Ecosystem @Should
    Scenario: Reject AI confidence in place of evidential judgement
      Given a finding with an AI confidence score
      When the finding is reviewed
      Then the AI confidence is not accepted as a substitute for the confidence rationale

    @FR-EVD-008 @R3-Ecosystem @Should
    Scenario: Reject publication that drops contradictory evidence
      Given a contested finding with material contradictory evidence
      When it is published
      Then publication is refused unless the contradictory evidence is preserved or its limitation is disclosed
