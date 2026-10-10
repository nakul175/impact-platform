# Imprana Commons backlog: Forms and collection
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Forms and collection

  Rule: FR-FRM-001 Form builder
    As a MEL Manager, I want to build forms with stable field IDs, typed fields, groups and repeat groups, preview them on desktop and mobile, and submit them for review, so that collected data is structured consistently and changes are controlled.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-FRM-001 @R1-Pilot @Must
    Scenario: Build a household form with a repeat group
      Given a household form with a repeat group for members, an optional photo and a calculated age
      When three members are entered and the form is submitted
      Then every child response retains its parent and its stable field code

    @FR-FRM-001 @R1-Pilot @Must
    Scenario: Preview and submit for review
      Given a draft form
      When the MEL Manager previews it on desktop and mobile and submits it for review
      Then the preview displays the effective form version
      And submission locks the schema and starts the approval workflow

    @FR-FRM-001 @R1-Pilot @Must
    Scenario: Qualified form size is supported
      Given a form with 200 questions and a repeat group
      When a submission contains 100 repeat entries
      Then the form previews and the submission is accepted

    @FR-FRM-001 @R1-Pilot @Must
    Scenario: Reject unsupported structures before publishing
      Given a form whose groups are nested deeper than two levels or that uses another unsupported combination
      When it is submitted for publishing
      Then it is rejected before publishing
      And a submission exceeding the declared repeat instance limit is refused

  Rule: FR-FRM-002 Conditional logic and validation
    As a MEL Manager, I want form relevance and required rules to use typed references, recalculate in dependency order and be enforced identically on the server, so that collected answers always respect the approved form logic.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-FRM-002 @R1-Pilot @Must
    Scenario: Newly irrelevant answers clear after confirmation
      Given a form whose pregnancy-dependent fields are relevant only when pregnancy is yes
      And those fields have been answered
      When the pregnancy answer changes from yes to no
      Then downstream state is recalculated in dependency order
      And after a visible confirmation the dependent fields are cleared under the declared policy

    @FR-FRM-002 @R1-Pilot @Must
    Scenario: Retained hidden values are excluded from calculations
      Given the schema explicitly retains a hidden value
      When calculations run
      Then the retained hidden value is excluded unless the approved schema says otherwise

    @FR-FRM-002 @R1-Pilot @Must
    Scenario: Reject a tampered payload
      Given a client payload containing answers the relevance rules disallow, including a hidden required answer
      When it is submitted
      Then the server checks the same versioned rules and rejects the payload

    @FR-FRM-002 @R1-Pilot @Must
    Scenario: Reject cyclic or inaccessible rule references
      Given a relevance or required rule that creates a cycle or references an inaccessible field
      When the rule is saved
      Then it is rejected

  Rule: FR-FRM-003 Form lifecycle and compatibility
    As a MEL Manager, I want forms to move through draft, isolated test, independent review and publication, with each version declaring compatibility and an acceptance cutoff, so that submissions keep the exact version used and incompatible ones are quarantined rather than altered.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-FRM-003 @R1-Pilot @Must
    Scenario: Older offline submission is quarantined after a mandatory change
      Given a form package is offline on an older version
      And a new version adding a mandatory question is published
      When the device reconnects and submits
      Then the original submission is preserved with the exact form and translation version used at capture
      And it is quarantined for reviewed mapping rather than having the answer invented

    @FR-FRM-003 @R1-Pilot @Must
    Scenario: Additive optional change accepts older versions
      Given a new version with only additive optional changes declared compatible with earlier versions
      When a submission on an older version arrives before the acceptance cutoff
      Then it is accepted

    @FR-FRM-003 @R1-Pilot @Must
    Scenario: Reject a revoked unsafe form
      Given a form version revoked as unsafe
      When it is used for live collection
      Then it is rejected as a live collection instrument

  Rule: FR-FRM-005 Collection rounds and assignments
    As a Programme Manager, I want to define collection rounds with an eligible frame, form version, dates and one stable assignment per sampled unit and visit, with tracked reassignment and replacement, so that field work and completion counts stay accurate and auditable.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-FRM-005 @R1-Pilot @Must
    Scenario: Round creates one stable assignment per sampled unit and visit
      Given a round with an eligible frame, form version, dates and expected assignments
      When tasks are created
      Then exactly one stable assignment exists per sampled unit and visit

    @FR-FRM-005 @R1-Pilot @Must
    Scenario: Reassignment keeps history without extra completions
      Given a household visit assigned to collector A
      When it is reassigned to collector B and B submits
      Then the assignee change is recorded in history
      And the old assignment cannot produce an extra eligible completed visit

    @FR-FRM-005 @R1-Pilot @Must
    Scenario: Sample replacement records original and substitute
      Given a sampled unit is replaced
      When the replacement is recorded
      Then the original and substitute are recorded with a reason
      And the original nonresponse remains recorded

    @FR-FRM-005 @R1-Pilot @Must
    Scenario: Reject silent expansion of the sample or denominator
      Given an assigned sample for a round
      When tasks are generated or a unit is replaced
      Then assignments are not automatically expanded to the full registry
      And the intended denominator does not increase silently

  Rule: FR-FRM-006 Save resume and correction
    As a Field Data Collector, I want to save drafts locally or on the server, resume the same submission, and submit with a receipt that survives interruptions, so that I never lose work or create duplicate submissions.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-FRM-006 @R1-Pilot @Must
    Scenario: Save and resume a draft
      Given a Field Data Collector has a form in progress
      When they save a draft and later resume it
      Then they see whether the draft was saved locally or on the server
      And the same submission identity and form version are restored

    @FR-FRM-006 @R1-Pilot @Must
    Scenario: Interrupted final submit resolves to one submission
      Given final submit is interrupted
      When the collector reopens the form and retries
      Then the receipt resolves to one submission
      And the local draft remains until server acceptance is confirmed

    @FR-FRM-006 @R1-Pilot @Must
    Scenario: Returned work starts a linked correction
      Given a submitted form is returned for correction
      When the collector opens it
      Then a linked correction revision is started

    @FR-FRM-006 @R1-Pilot @Must
    Scenario: Reject duplicate submissions and silent loss
      Given the collector taps submit repeatedly or the server times out
      When the submission is processed
      Then repeated taps reuse the same operation identity
      And a timeout enters confirmation pending rather than creating a new submission
      And closing the browser with unsaved changes shows a warning

  Rule: FR-FRM-004 Multilingual instruments
    As a MEL Manager, I want each form field and choice to keep a stable code with separately reviewed language-specific labels, so that responses in any approved language map to the same codes and consent is always shown in an approved translation.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-FRM-004 @R2-Scale @Should
    Scenario: Same choice in different languages maps to one code
      Given a form released with an approved English and Hindi language set
      When the same choice is submitted once in English and once in Hindi
      Then both map to one stable response code
      And each retains the language presented to the respondent

    @FR-FRM-004 @R2-Scale @Should
    Scenario: Translator sees gaps and proposals
      Given a form with untranslated and machine-proposed labels
      When the translator opens a language version
      Then missing and machine-proposed translations are shown
      And the language version is approved through review separately

    @FR-FRM-004 @R2-Scale @Should
    Scenario: Reject collection without approved consent translation
      Given critical consent text lacks an approved translation in the selected collection language
      When collection in that language is started
      Then collection in that language is blocked

    @FR-FRM-004 @R2-Scale @Should
    Scenario: Reject fallback that changes choice codes
      Given fallback text is used for a missing label
      When a response is recorded
      Then the fallback is shown explicitly
      And the choice code is unchanged

  Rule: FR-FRM-007 Media and location evidence
    As a Privacy Officer, I want media and location capture to show necessity, consent and size limits, record GPS refusal, and strip prohibited embedded metadata before disclosure, so that evidence is collected and shared without exposing protected information.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-FRM-007 @R2-Scale @Should
    Scenario: Capture shows necessity, consent and limits
      Given a form field requiring media capture
      When the collector starts recording
      Then necessity, consent and size limits are displayed before recording
      And each attachment shows upload progress, safety state and evidence requirement

    @FR-FRM-007 @R2-Scale @Should
    Scenario: Optional GPS refusal is recorded
      Given an optional GPS field
      When location is unavailable or declined
      Then the field records unavailable or declined
      And mandatory justified GPS follows the explicit exception path

    @FR-FRM-007 @R2-Scale @Should
    Scenario: Reject disclosure of prohibited location metadata
      Given a photo with embedded coordinates and location disclosure is prohibited
      When the photo is disclosed externally
      Then the external artifact contains no recoverable coordinate metadata
      And permitted source provenance is retained

    @FR-FRM-007 @R2-Scale @Should
    Scenario: Reject incomplete or unsafe files as evidence
      Given an attachment whose scanning is incomplete or that is found unsafe
      When evidence completeness or approval is assessed
      Then the evidence is not complete and approval is prevented

  Rule: FR-FRM-010 Instrument testing and reuse
    As a MEL Manager, I want to test forms with synthetic submissions covering branches, boundaries, translations and devices, and reuse pinned question library versions, so that instruments are proven before publication without polluting official data.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-FRM-010 @R2-Scale @Should
    Scenario: Testing reports branch coverage
      Given a form with skip branches and a repeat group
      When two skip branches and one repeat boundary are exercised with synthetic submissions
      Then results identify any unvisited logic branches and validation failures

    @FR-FRM-010 @R2-Scale @Should
    Scenario: Synthetic responses stay out of production after publishing
      Given synthetic test responses exist for a form
      When the form is published
      Then none of the synthetic responses appear in production counts or official datasets
      And no real respondent messages are triggered

    @FR-FRM-010 @R2-Scale @Should
    Scenario: Reuse a pinned question library version
      Given a question library
      When questions are copied into a form
      Then the selected library version is pinned
      And permitted local adaptation is allowed

    @FR-FRM-010 @R2-Scale @Should
    Scenario: Reject publishing without passing checks
      Given mandatory path checks have not passed or independent instrument review is incomplete
      When publishing is attempted
      Then publishing is blocked

  Rule: FR-FRM-008 Respondent and public forms
    As a Programme Participant, I want to complete a public form or a single-response link with clear notice, expiry and resume rules, so that I can respond myself without seeing anyone else's information.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-FRM-008 @R3-Ecosystem @Should
    Scenario: Submit once with a scoped token
      Given a Programme Participant has a single response token with notice and expiry
      When they submit the form
      Then a receipt confirms successful submission
      And the receipt contains no other respondents' details

    @FR-FRM-008 @R3-Ecosystem @Should
    Scenario: Resume a draft before expiry
      Given draft resume is permitted for the token
      When the participant returns before expiry, authenticated or with the bound token
      Then their draft is restored

    @FR-FRM-008 @R3-Ecosystem @Should
    Scenario: Reject token replay and access to other responses
      Given a token already used for a final submission
      When it is replayed and a different response ID is requested
      Then the replay is idempotent or unavailable and creates no duplicate result
      And the other response is never shown

    @FR-FRM-008 @R3-Ecosystem @Should
    Scenario: Reject abuse and directory exposure
      Given submissions arriving beyond the rate limits
      When further requests are made to the form
      Then accessible abuse controls and rate limits are applied
      And no participant directory is exposed

  Rule: FR-FRM-009 Longitudinal and repeat visits
    As a MEL Manager, I want repeat visit templates with entity scope, visit type, baseline reference, expected interval and observation window, recording each visit as a separate event, so that follow-up data is analysed correctly without double counting participants.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-FRM-009 @R3-Ecosystem @Should
    Scenario: Baseline and follow ups analysed in the designated window
      Given one person with a baseline and two follow-up visits
      When the analysis runs
      Then it selects the visit in the designated window
      And the person is not counted as three different participants

    @FR-FRM-009 @R3-Ecosystem @Should
    Scenario: Prior responses shown but not copied
      Given permitted prior responses exist for a person
      When a follow-up visit form is opened
      Then prior responses are shown with their date and source
      And they are not copied as current answers by default

    @FR-FRM-009 @R3-Ecosystem @Should
    Scenario: Reject an outside-window visit without a reason
      Given a visit outside the observation window
      When it is submitted without a reason and an analysis eligibility decision
      Then it is not accepted as eligible for analysis

    @FR-FRM-009 @R3-Ecosystem @Should
    Scenario: Reject treating missing follow up as zero
      Given a participant with missing follow up, withdrawal or death
      When outcomes are calculated
      Then each status remains distinct and is not recorded as a zero outcome
