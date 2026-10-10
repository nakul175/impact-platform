# Imprana Commons backlog: AI capabilities
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: AI capabilities

  Rule: FR-AI-001 Explicit enablement and policy
    As an Organisation Administrator, I want to enable named AI use cases with their allowed data classes, destinations, language coverage, budget and required review, so that AI only runs where we have approved it and every workflow still works without it.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-AI-001 @R1-Pilot @Must
    Scenario: Enable a named use case with its policy
      Given an Organisation Administrator configuring AI
      When they enable a named use case with allowed data classes, destinations, language coverage, budget and required review
      Then only that use case is enabled
      And users see the active policy before making a request

    @FR-AI-001 @R1-Pilot @Must
    Scenario: Core workflows work with AI disabled
      Given AI is disabled for a tenant
      When users complete programme setup, period close and report generation
      Then each completes using deterministic and manual workflows
      And no provider call is made

    @FR-AI-001 @R1-Pilot @Must
    Scenario: Reject transmission that fails policy
      Given a request for sensitive processing without an approved destination and purpose
      When the request is submitted
      Then it is blocked before content leaves the authorised boundary

    @FR-AI-001 @R1-Pilot @Must
    Scenario: Reject implicit enablement of tools
      Given a chat interface has been enabled
      When a user attempts to use a tool that was not separately enabled
      Then the tool is not available

  Rule: FR-AI-007 Report drafting
    As a MEL Manager, I want AI to draft report sections from an approved snapshot and template with evidence references and metric bindings, so that drafting is faster while official numbers, caveats, evidence gaps and human edits stay intact.
    Release: R1 Pilot · Priority: Should · Built today: Absent

    @FR-AI-007 @R1-Pilot @Should
    Scenario: Draft binds snapshot and template
      Given an approved snapshot and report template
      When the MEL Manager requests a draft
      Then proposed sections include evidence references and metric bindings
      And every official number matches its bound result

    @FR-AI-007 @R1-Pilot @Should
    Scenario: Missing evidence stays visible
      Given an incomplete snapshot
      When a draft is generated
      Then missing sections appear as evidence gaps

    @FR-AI-007 @R1-Pilot @Should
    Scenario: Review tracks AI origin
      Given a draft under review
      When reviewers correct it and finalise wording
      Then AI origin, corrections and final human wording are tracked

    @FR-AI-007 @R1-Pilot @Should
    Scenario: Reject invented results and overwritten edits
      Given a draft with accepted human edits
      When the assistant regenerates it or attempts to create a new official snapshot, invent a result or remove a mandatory caveat
      Then the snapshot, result and caveat changes are refused
      And accepted human edits are not overwritten without an explicit reviewed diff

  Rule: FR-AI-011 Input and tool isolation
    As an Organisation Administrator, I want documents, tool outputs and retrieved pages treated as evidence and never as instructions, so that embedded content cannot expand AI tools, change policy or send our data elsewhere.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-AI-011 @R1-Pilot @Must
    Scenario: Tool catalogue is set independently of model output
      Given an AI task
      When it runs
      Then the allowed tool catalogue and scoped arguments are established independently of model generated instructions
      And external destinations are used only with explicit policy permission

    @FR-AI-011 @R1-Pilot @Must
    Scenario: Embedded instruction is treated as untrusted content
      Given a proposal containing an embedded instruction to export all records
      When extraction runs
      Then the instruction is treated as untrusted content
      And no export is performed

    @FR-AI-011 @R1-Pilot @Must
    Scenario: Reject unsafe actions requested by documents
      Given a document that instructs the model to reveal credentials, retrieve all tenants or send outputs elsewhere
      When the model processes it
      Then the unsafe action attempt is blocked without being executed
      And the attempt is recorded

  Rule: FR-AI-012 Model data handling
    As a Privacy Officer, I want every AI transmission checked against tenant, use case, purpose, classification, region, provider retention and minimisation policy, with training reuse off by default, so that data reaches only approved providers and is never used for training without explicit opt in.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-AI-012 @R1-Pilot @Must
    Scenario: Policy is evaluated before transmission
      Given an AI request containing tenant content
      When it is about to be transmitted
      Then tenant, use case, purpose, classification, region, provider retention and minimisation policy are evaluated
      And prohibited fields are redacted or excluded
      And the approved destination version is recorded

    @FR-AI-012 @R1-Pilot @Must
    Scenario: Primary provider offline for restricted data
      Given restricted data and the primary provider forced offline
      When an AI request is made
      Then no unapproved fallback provider receives the content
      And the manual workflow remains usable

    @FR-AI-012 @R1-Pilot @Must
    Scenario: Reject training reuse without opt in
      Given a tenant that has not explicitly opted in
      When its content is processed by AI
      Then it is not reused for training
      And no implicit opt in is applied

    @FR-AI-012 @R1-Pilot @Must
    Scenario: Reject retention and reuse outside schedule
      Given prompts, answers and diagnostics
      When their retention schedule ends or evaluation datasets are assembled
      Then they are not kept beyond their schedule
      And private content is not automatically copied into broad model evaluation datasets

  Rule: FR-AI-013 Source access and conversation history
    As an Organisation Administrator, I want AI answers and saved conversations to recheck current access to their sources whenever they are opened, shared, summarised or exported, so that revoking a source grant also removes that content from AI history.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-AI-013 @R1-Pilot @Must
    Scenario: Answers record dependencies and audience
      Given an AI answer or saved conversation
      When it is saved
      Then its source dependencies and permitted audience are recorded

    @FR-AI-013 @R1-Pilot @Must
    Scenario: Access is rechecked on reuse
      Given a saved conversation
      When it is opened, shared, summarised or exported
      Then current access to its source dependencies is rechecked
      And inaccessible segments are withheld, or the artifact is withdrawn when redaction cannot be safe

    @FR-AI-013 @R1-Pilot @Must
    Scenario: Reject reintroduction of revoked text
      Given a source grant revoked after a conversation
      When the user requests a summary of the prior conversation, opens a cached answer or writes a new prompt
      Then the now restricted passages are not revealed
      And copying the chat does not create new source rights

  Rule: FR-AI-014 Traceability and reproducibility
    As a Data Steward, I want each AI task to record its requester, scope, source versions, model configuration, tool receipts, proposed changes and review decisions, so that I can trace any AI figure or applied change back to its evidence and reviewer.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-AI-014 @R1-Pilot @Must
    Scenario: Task record captures traceability
      Given an AI task
      When it completes
      Then the task record stores requester, scope, source versions, use case configuration, model identifier, tool receipts, proposed changes, review decisions and applied domain receipts within retention policy
      And the generated output version is preserved where lawful

    @FR-AI-014 @R1-Pilot @Must
    Scenario: Audit an applied mapping suggestion
      Given an applied AI mapping suggestion
      When the Data Steward audits it
      Then they can identify the evidence, model configuration, reviewer and deterministic command
      And concise evidence and decision explanations are shown without requiring private chain of thought

    @FR-AI-014 @R1-Pilot @Must
    Scenario: Reject storage or exposure of hidden reasoning
      Given an AI task record
      When it is stored or inspected
      Then hidden model reasoning is not stored
      And hidden model reasoning is not shown

  Rule: FR-AI-015 Evaluation and release gates
    As a Platform Operator, I want every AI use case to pass owned regression evaluation before any model, prompt, retrieval, tool or policy change reaches users, so that a critical failure blocks release even when average quality improves.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-AI-015 @R1-Pilot @Must
    Scenario: Use case has evaluation assets
      Given an AI use case
      When it is prepared for release
      Then it has an owner, held out dataset, expected judgements, supported language and sector matrix and release report

    @FR-AI-015 @R1-Pilot @Must
    Scenario: Changes run regression before exposure
      Given a change to the model, prompt, retrieval, tools or policy
      When it is proposed
      Then regression runs before controlled exposure

    @FR-AI-015 @R1-Pilot @Must
    Scenario: Reject candidate with a critical failure
      Given a candidate with higher average quality but one cross tenant leak
      When it is evaluated
      Then it cannot replace the approved configuration
      And any critical unsupported claim, leakage or unauthorised action blocks the affected capability

    @FR-AI-015 @R1-Pilot @Must
    Scenario: Reject unjustified evaluation exceptions
      Given a specialist evaluation exception
      When it is requested without recorded justification
      Then it is not granted

  Rule: FR-AI-016 Cost latency and fallback
    As a MEL Manager, I want AI requests to reserve budget and show progress, timeout and cancellation, so that AI work stays within its limits and running out of AI budget never stops period close or reporting.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-AI-016 @R1-Pilot @Must
    Scenario: Request reserves budget and shows progress
      Given an AI request
      When it starts
      Then its job class and usage are estimated and permitted budget is reserved
      And progress, timeout and cancellation are shown
      And ordinary question answering follows the BRD latency target

    @FR-AI-016 @R1-Pilot @Must
    Scenario: Default timeouts keep partial drafts labelled
      Given the proposed default timeouts
      When a standard extraction runs beyond 15 minutes or a report draft runs beyond 20 minutes
      Then the job times out
      And any partial draft remains labelled incomplete

    @FR-AI-016 @R1-Pilot @Must
    Scenario: Budget exhausted during close
      Given the AI budget is exhausted during period close
      When the MEL Manager continues close
      Then they can still approve data, calculate results and generate a non-AI report

    @FR-AI-016 @R1-Pilot @Must
    Scenario: Reject lost input and uncontrolled continuation
      Given the AI budget is exhausted or a job is cancelled
      When the user submits or cancels an AI request
      Then a clear limit state is returned without losing user input
      And cancellation stops new model and tool calls where controllable
      And provider work already accepted is accounted separately

  Rule: FR-AI-018 Safety feedback and shutdown
    As an Organisation Administrator, I want to capture AI safety feedback and immediately disable a use case, configuration or destination, so that harmful output is contained and affected artifacts are reviewed while core workflows continue.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-AI-018 @R1-Pilot @Must
    Scenario: Capture safety feedback
      Given an AI output with a safety concern
      When a user submits feedback
      Then it captures the affected output, category, safe supporting detail and reviewer

    @FR-AI-018 @R1-Pilot @Must
    Scenario: Shut down an affected use case
      Given a simulated exposed sensitive citation
      When the Organisation Administrator disables the use case
      Then new affected jobs stop immediately
      And queued work is identified
      And every affected saved answer and generated artifact is listed for review
      And manual report workflows continue

    @FR-AI-018 @R1-Pilot @Must
    Scenario: Reject reenable without fix evidence
      Given a disabled use case
      When someone attempts to reenable it without fix evidence and regression approval
      Then reenable is refused

    @FR-AI-018 @R1-Pilot @Must
    Scenario: Reject retained payloads and lost core workflows
      Given an AI incident
      When incident evidence is preserved and AI is disabled
      Then prohibited source payloads are not retained
      And independent core workflows are not disabled

  Rule: FR-AI-002 Proposal and logframe extraction
    As a MEL Manager, I want AI to extract proposed programme entities and fields from permitted proposal and logframe files with source references and classification, so that I can selectively accept them without unsupported dates, targets or population commitments entering the results framework.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-AI-002 @R2-Scale @Should
    Scenario: Extraction returns traceable proposals
      Given permitted proposal and logframe files selected for extraction
      When extraction runs
      Then each proposed entity and field shows source version, page or section and evidence span
      And each is classified as extracted, inferred or suggested

    @FR-AI-002 @R2-Scale @Should
    Scenario: Selective acceptance in the review panel
      Given extraction results in the review panel
      When the MEL Manager accepts some proposals
      Then only the accepted proposals are applied
      And unresolved ambiguities are retained

    @FR-AI-002 @R2-Scale @Should
    Scenario: Conflicting and missing values are flagged
      Given a proposal with two end dates and no population
      When it is extracted
      Then both end dates are presented separately and flagged
      And the population field remains missing and flagged
      And activation remains blocked until they are reviewed

    @FR-AI-002 @R2-Scale @Should
    Scenario: Reject unsupported commitments
      Given a date, target or population commitment with no direct source support
      When extraction completes
      Then the value stays missing unless a human adds it explicitly
      And contradictory sources are not merged into a single value

  Rule: FR-AI-003 Indicator design assistance
    As a MEL Manager, I want the assistant to propose a complete draft indicator from approved library definitions and programme context and highlight its gaps, so that I can accept selected fields into a draft that passes the same checks as manual authoring.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-AI-003 @R2-Scale @Should
    Scenario: Assistant proposes a complete draft measurement contract
      Given approved library definitions and the current programme context
      When the MEL Manager asks the assistant for an indicator
      Then it proposes a complete draft measurement contract
      And it highlights missing denominator, unsuitable proxy, population ambiguity and evidence requirements

    @FR-AI-003 @R2-Scale @Should
    Scenario: Completion percentage requires essential fields
      Given the assistant suggests a completion percentage indicator
      When the MEL Manager accepts selected fields into a draft
      Then the draft requires an eligible denominator, reporting period and evidence method before review submission

    @FR-AI-003 @R2-Scale @Should
    Scenario: Reject approval by model confidence
      Given an AI drafted indicator
      When it fails the schema and method checks used for manual authoring, or is supported only by model confidence
      Then it cannot be submitted or approved
      And no unsupported standard mapping is created

  Rule: FR-AI-004 Import and cleaning assistance
    As a Data Steward, I want AI to propose source-to-destination mappings and deterministic transformations with affected sample rows, so that I can accept individual proposals after seeing the exact mapping diff while raw rows, identities and approved actuals stay protected.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-AI-004 @R2-Scale @Should
    Scenario: Review mapping proposals with a diff
      Given an import with mapping assistance enabled
      When the assistant returns proposals
      Then each shows the proposed link or deterministic transformation with affected sample rows
      And the Data Steward sees the exact mapping diff before accepting

    @FR-AI-004 @R2-Scale @Should
    Scenario: Apply only approved deterministic changes
      Given a date normalisation suggestion and a name-based participant merge suggestion
      When the Data Steward accepts the date normalisation and rejects the merge
      Then only the date conversion is applied, as a mapping draft or reviewed transformation version

    @FR-AI-004 @R2-Scale @Should
    Scenario: Reject destructive AI actions
      Given AI mapping assistance
      When it attempts to delete raw rows, merge identities or overwrite approved actuals
      Then the action is refused

    @FR-AI-004 @R2-Scale @Should
    Scenario: Reject auto-selection of ambiguous mappings
      Given a low confidence or ambiguous mapping proposal
      When proposals are presented
      Then it remains unselected until explicitly resolved

  Rule: FR-AI-005 Evidence based questions
    As a Programme Manager, I want to ask questions within my authorised scope and get answers that cite their evidence and show missing or contradictory evidence, so that I can rely on answers without exposing data I cannot access.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-AI-005 @R2-Scale @Should
    Scenario: Supported question returns a cited answer
      Given a Programme Manager asks a question with authorised scope, period and source mode
      When the answer is returned
      Then it uses only permitted evidence and results
      And material claims cite their source locations
      And missing or contradictory evidence is shown

    @FR-AI-005 @R2-Scale @Should
    Scenario: Ambiguous scope asks for clarification
      Given a question with ambiguous scope
      When it is submitted
      Then a clarification state is returned
      And no official number is guessed

    @FR-AI-005 @R2-Scale @Should
    Scenario: Reject inaccessible question without leakage
      Given a question about a partner the Programme Manager cannot access
      When it is submitted
      Then a bounded abstention is returned
      And no hidden record detail is revealed and the protected resource's existence is not confirmed
      And no quotations, citations or document titles are fabricated

  Rule: FR-AI-006 Governed numerical analysis
    As an Analyst, I want numeric questions answered by an authorised deterministic tool following a constrained analysis plan, so that every official number in the answer matches an approved calculation rather than the model's own arithmetic.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-AI-006 @R2-Scale @Must
    Scenario: Numeric question runs as a typed analysis plan
      Given an Analyst asks a numeric question
      When it is processed
      Then it is translated into a plan with measure, compatible sources, filters, period, dimensions and permitted operation
      And an authorised deterministic tool executes the plan
      And the answer embeds the returned values and result references without model recomputation

    @FR-AI-006 @R2-Scale @Must
    Scenario: Pooled percentage uses the approved calculation
      Given results of 50/100 and 1/10
      When the Analyst asks for the pooled value
      Then the answer presents 46.36 percent with 51/110
      And it includes the approved calculation receipt

    @FR-AI-006 @R2-Scale @Must
    Scenario: Reject arbitrary queries
      Given a numeric question
      When answering it would require arbitrary SQL, code execution or an unrestricted user supplied query
      Then the request is refused

    @FR-AI-006 @R2-Scale @Must
    Scenario: Reject mismatched figures
      Given drafted numeric text that does not match the tool value
      When the answer is about to be delivered
      Then delivery of the official claim is blocked

  Rule: FR-AI-010 Action proposal and approval
    As a Programme Manager, I want AI write proposals to show the exact change, scope, before and after values and consequences and to need my separate confirmation, so that no AI change is applied without current authority.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-AI-010 @R2-Scale @Must
    Scenario: Proposal shows the exact change
      Given an AI write proposal
      When the Programme Manager reviews it
      Then it shows the exact domain command, object scope, before and after values, affected versions, policy context and consequences
      And confirmation is a separate step from generation

    @FR-AI-010 @R2-Scale @Must
    Scenario: Confirmed proposal executes through the ordinary command
      Given a confirmed proposal
      When it executes
      Then current authority and revisions are rechecked
      And the ordinary domain command is called

    @FR-AI-010 @R2-Scale @Must
    Scenario: Reject stale proposal after permission is revoked
      Given a proposal generated before the user's permission is revoked
      When it is confirmed after revocation
      Then execution fails
      And no stale changes are applied

    @FR-AI-010 @R2-Scale @Must
    Scenario: Reject protected direct writes
      Given an AI proposal
      When it targets approved results, permission grants, publication, privacy deletion or independent decisions directly
      Then the write is refused
      And a source or policy change marks the proposal stale so that regeneration requires review

  Rule: FR-AI-008 Qualitative assistance
    As an Analyst, I want AI to suggest codes, themes, excerpts and translations from a permitted source set and approved codebook, so that I can review qualitative data faster while keeping minority and contradictory viewpoints traceable to their sources.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-AI-008 @R3-Ecosystem @Should
    Scenario: Suggestions from permitted sources and an approved codebook
      Given a permitted source set and an approved codebook
      When qualitative assistance runs
      Then it returns suggested codes, themes, excerpts and translations
      And the Analyst reviews each suggestion individually
      And accepted edits create normal coded evidence records

    @FR-AI-008 @R3-Ecosystem @Should
    Scenario: Opposing views remain traceable
      Given interviews with opposing views in two languages
      When they are summarised
      Then both perspectives are retained
      And each remains traceable to its original excerpts

    @FR-AI-008 @R3-Ecosystem @Should
    Scenario: Reject fabricated quotations and unlabelled translations
      Given AI qualitative output
      When it contains an invented verbatim quotation or a fabricated speaker identity
      Then the output is rejected
      And machine translation stays labelled until reviewed and does not broaden source permission

  Rule: FR-AI-009 Proactive findings
    As a Programme Manager, I want AI to raise suggested findings for enabled scopes with their evidence, limitations and proposed follow up, so that I can verify, dismiss or assign them without them being treated as confirmed findings.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-AI-009 @R3-Ecosystem @Should
    Scenario: Suggested finding includes context
      Given proactive findings are enabled for a scope with a defined detection task
      When a performance spike is detected
      Then one suggested finding is created
      And it states affected result versions, evidence, limitation and proposed follow up

    @FR-AI-009 @R3-Ecosystem @Should
    Scenario: Dismiss a suggestion
      Given a suggested finding for a performance spike
      When the Programme Manager dismisses it as seasonal
      Then the feedback is recorded
      And no source value changes

    @FR-AI-009 @R3-Ecosystem @Should
    Scenario: Reject unreviewed suggestions as confirmed findings
      Given a suggested finding that has not been reviewed
      When it is displayed or reported
      Then it is not presented as a confirmed fraud, impact or programme risk finding
      And noise controls, cooldown and owner accountability apply
      But no suggestion is generated for a scope or detection task that is not enabled

  Rule: FR-AI-017 Forecasts and scenario assistance
    As a Programme Manager, I want AI forecasts and scenarios built from approved inputs with a stated horizon, method, assumptions and uncertainty, so that I can explore projections for planning without them being mistaken for actuals or overwriting targets.
    Release: Later · Priority: Could · Built today: Absent

    @FR-AI-017 @Later @Could
    Scenario: Forecast records its basis
      Given approved input versions
      When a forecast is created
      Then it records forecast horizon, method, assumptions and validation history
      And outputs include uncertainty and a scenario label

    @FR-AI-017 @Later @Could
    Scenario: Actuals and projections exported together stay distinct
      Given actuals and a projection
      When they are exported together
      Then they appear as distinct series with horizon and uncertainty
      And approved targets are not overwritten automatically

    @FR-AI-017 @Later @Could
    Scenario: Adoption is reviewed and changes are versioned
      Given a forecast scenario
      When it is adopted as a planning assumption, or its model or assumptions change
      Then adoption goes through review
      And a change of model or assumptions creates a new scenario version

    @FR-AI-017 @Later @Could
    Scenario: Reject forecasts on insufficient evidence
      Given insufficient evidence for a forecast
      When a forecast is requested
      Then the forecast is withheld or returned only as explicitly bounded exploratory output

  Rule: FR-AI-016a AI jobs with budget reservation and cancellation
    As a MEL Manager, I want each AI request to run as a job that reserves budget, shows progress and can be cancelled, so that AI work stays within its limits and never blocks close or reporting.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-AI-016a @R1-Pilot @Must
    Scenario: Request reserves budget and runs as a job
      Given an enabled use case with budget remaining
      When a request is submitted
      Then the response is 202 with a job ID
      And the estimated units are reserved in the budget ledger
      And progress and a Cancel action are shown

    @FR-AI-016a @R1-Pilot @Must
    Scenario: Budget exhausted during close
      Given the AI budget is exhausted
      When the MEL Manager approves data, calculates results and generates a report
      Then each completes without AI

    @FR-AI-016a @R1-Pilot @Must
    Scenario: Reject a request beyond the budget
      Given the remaining budget is smaller than the estimate
      When a request is submitted
      Then the response is 429 "AI_BUDGET_EXHAUSTED" and the user's input is kept

  Rule: FR-AI-016b Timeouts and labelled partial drafts
    As a MEL Manager, I want AI jobs to stop at their time limit and keep any partial draft clearly labelled incomplete, so that unfinished AI output is never mistaken for a finished draft.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-AI-016b @R1-Pilot @Must
    Scenario: Long job times out with a labelled partial draft
      Given a report-draft job with a 20-minute limit
      When it runs past 20 minutes
      Then it stops with outcome TIMED_OUT
      And any partial draft is kept and labelled "Incomplete draft"

    @FR-AI-016b @R1-Pilot @Must
    Scenario: Reject an incomplete draft shown as complete
      Given a job that timed out or was cancelled
      When its output is shown or exported
      Then it is labelled incomplete and cannot be published as a final draft
