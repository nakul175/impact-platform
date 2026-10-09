# Imprana Commons backlog: Evaluation
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Evaluation

  Rule: FR-EVA-004 Causal claims and uncertainty
    As a MEL Manager, I want every finding or report claim classified as observed change, association, contribution or causal claim, so that reports and AI drafts only attribute impact where an approved method and independent review support it.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-EVA-004 @R2-Scale @Must
    Scenario: Classify a claim
      Given a finding or report claim
      When it is authored
      Then it is classified as observed change, association, contribution or causal claim

    @FR-EVA-004 @R2-Scale @Must
    Scenario: Approve a causal claim
      Given a claim classified as causal
      When it is approved
      Then it has an approved method reference and an independent reviewer judgement

    @FR-EVA-004 @R2-Scale @Must
    Scenario: AI response without a reviewed evaluation
      Given no reviewed evaluation supports attribution for an outcome
      When a user asks why the outcome increased after launch
      Then the AI response describes the observed change and the evidence limits
      And it carries the claim's uncertainty

    @FR-EVA-004 @R2-Scale @Must
    Scenario: Reject automatic causal attribution from a trend
      Given a trend or before-after difference
      When a report is drafted
      Then a causal attribution statement is not automatically populated from it
      And unsupported causal language is flagged during report review

  Rule: FR-EVA-001 Evaluation registry
    As a MEL Manager, I want to register evaluations with their questions, design, baseline, period, evaluator, independence, ethics requirements, budget and deliverables, with stage gates before field collection or publication, so that each study is properly documented and controlled.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-EVA-001 @R3-Ecosystem @Should
    Scenario: Register several studies for one programme
      Given one programme
      When baseline, midline and endline studies are registered for it
      Then each study keeps its own method and observation period

    @FR-EVA-001 @R3-Ecosystem @Should
    Scenario: Stage gates check required documents
      Given a registered evaluation
      When it reaches field collection or publication
      Then the stage gate checks the required methodological and policy documents

    @FR-EVA-001 @R3-Ecosystem @Should
    Scenario: Reject an unsupported independence claim
      Given a study marked independent
      When no basis for its independence is identified
      Then the independence claim is not accepted
      And a self declaration is not shown as verified

    @FR-EVA-001 @R3-Ecosystem @Should
    Scenario: Reject treating registration as approval of sensitive processing
      Given a registered evaluation that involves sensitive processing
      When sensitive processing is attempted on the basis of registration alone
      Then the processing is not approved

  Rule: FR-EVA-002 Sampling and methodological metadata
    As an Analyst, I want a versioned methodology record of sampling frame, eligibility, assignment, weights, nonresponse rules and analysis plan, so that estimates are reproducible and amendments are transparent.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-EVA-002 @R3-Ecosystem @Should
    Scenario: Export a stratified sample with methodology metadata
      Given a stratified sample with weights and nonresponse metadata
      When an Analyst exports it
      Then the declared eligible denominator can be reproduced

    @FR-EVA-002 @R3-Ecosystem @Should
    Scenario: Amendments are reviewed and dated relative to data inspection
      Given a methodology record
      When it is amended
      Then the amendment identifies when it occurred relative to data inspection
      And it requires review

    @FR-EVA-002 @R3-Ecosystem @Should
    Scenario: Reject relabelling a sample count as a population
      Given a sample count
      When a population estimate is requested without an explicit valid expansion method
      Then the population estimate is refused
      And the sample count cannot be relabelled as all beneficiaries

    @FR-EVA-002 @R3-Ecosystem @Should
    Scenario: Reject weighted output with missing weights
      Given a sample with missing weights
      When weighted output is requested
      Then the weighted output is blocked
      But the weights are not silently defaulted to one

  Rule: FR-EVA-003 Analysis packages
    As an Analyst, I want to create a frozen analysis extract with selected variables, filters, approved sources, dictionary and integrity manifest, so that submitted results stay reproducible after live data changes.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-EVA-003 @R3-Ecosystem @Should
    Scenario: Create a frozen extract
      Given approved sources
      When an Analyst creates an extract with selected variables, filters, dictionary and integrity manifest
      Then the extract is frozen
      And reviewed scripts and notebooks can be attached as evidence
      And results reference the extract and method versions

    @FR-EVA-003 @R3-Ecosystem @Should
    Scenario: Reproduce a result after live records change
      Given a submitted result based on a pinned extract
      When live records are later corrected
      Then the extract is not altered
      And the result can be reproduced from the pinned extract
      And the original analysis remains reconcilable

    @FR-EVA-003 @R3-Ecosystem @Should
    Scenario: Reject executing uploaded code
      Given a script or notebook uploaded as an ordinary upload
      When it is stored in the product
      Then it is not executed in the product

    @FR-EVA-003 @R3-Ecosystem @Should
    Scenario: Reject export without the export capability
      Given a user with analysis access but without the separate export capability
      When they try to export the extract
      Then the export is refused

  Rule: FR-EVA-006 Learning agenda
    As a MEL Manager, I want learning questions linked to strategic decisions, evidence gaps, planned inquiry, owner and review date, with versioned evidence and conclusions, so that decisions draw on what we have learned and what remains uncertain.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-EVA-006 @R3-Ecosystem @Should
    Scenario: Link a decision to a learning question
      Given a programme redesign decision
      When the MEL Manager links it to a learning question with three sources and one unresolved assumption
      Then the learning question shows the decision, the three sources and the unresolved assumption
      And the assumption is marked as requiring a follow up study

    @FR-EVA-006 @R3-Ecosystem @Should
    Scenario: Close and reopen a learning question
      Given a learning question
      When it is closed
      Then what was learned and the remaining uncertainty are recorded
      And reopening it later preserves the prior reasoning

    @FR-EVA-006 @R3-Ecosystem @Should
    Scenario: Reject automatic transfer of an answer to another context
      Given a question answered in one context
      When it is considered for another context
      Then the answer is not automatically treated as applicable

    @FR-EVA-006 @R3-Ecosystem @Should
    Scenario: Reject restricted evidence in a broad summary without review
      Given restricted evidence linked to a learning question
      When a broad learning summary is produced
      Then the restricted evidence is not copied into it without disclosure review

  Rule: FR-EVA-007 Management responses and actions
    As an Executive Director, I want to respond to each evaluation recommendation with accept, partially accept or reject and a reason, and track accepted actions to evidenced completion, so that my organisation is accountable for acting on evaluations.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-EVA-007 @R3-Ecosystem @Should
    Scenario: Accept a recommendation and create an action
      Given an evaluation recommendation on training
      When the Executive Director accepts it with a reason
      Then an action is created with an owner, due date and required completion evidence

    @FR-EVA-007 @R3-Ecosystem @Should
    Scenario: Separate action completion from outcome evidence
      Given an accepted training recommendation with completed training evidence
      When the action is reviewed
      Then the action is recorded as complete
      But outcome improvement remains pending until follow up measurements support it

    @FR-EVA-007 @R3-Ecosystem @Should
    Scenario: Reject automatic closure of overdue actions
      Given an action past its due date
      When it becomes overdue
      Then it escalates
      But it is not automatically closed

    @FR-EVA-007 @R3-Ecosystem @Should
    Scenario: Reject hiding a rejected recommendation
      Given a recommendation rejected with a reason
      When recommendations are viewed
      Then it remains visible with its accountable response

  Rule: FR-EVA-005 Outcome harvesting and contribution
    As a MEL Manager, I want to harvest outcomes with their observed change, significance, timing, actors, contribution hypothesis, independent substantiation and dissenting views, so that contribution claims are reviewed separately from observed outcomes and attribution limits are clear.
    Release: Later · Priority: Could · Built today: Absent

    @FR-EVA-005 @Later @Could
    Scenario: Two organisations contribute to one policy change
      Given two organisations claim contribution to one policy change
      When the outcome is reviewed and the narrative approved
      Then the approved narrative identifies both organisations
      And it states the limits of attribution
      And the contributions are not forced into shares that total 100 percent

    @FR-EVA-005 @Later @Could
    Scenario: Review separates the outcome from contribution claims
      Given a harvested outcome
      When it is reviewed
      Then the observed outcome is reviewed separately from each organisation's contribution claim

    @FR-EVA-005 @Later @Could
    Scenario: Reject publishing unsubstantiated claims as causation
      Given a contribution claim without independent substantiation
      When publication as established causation is attempted
      Then the claim remains proposed
      And it is not published as established causation

  Rule: FR-EVA-008 Institutional learning library
    As a Programme Manager, I want to reuse published lessons with their source context, method, applicability and limitations and record my adaptation assumptions, so that new programmes learn from past experience without overstating transferability.
    Release: Later · Priority: Could · Built today: Absent

    @FR-EVA-008 @Later @Could
    Scenario: Publish a lesson
      Given a curator preparing a lesson
      When they publish it
      Then it includes source context, method, applicability, limitations, owner, review date and allowed reuse

    @FR-EVA-008 @Later @Could
    Scenario: Apply a lesson in a different context
      Given a published rural implementation lesson
      When a Programme Manager applies it in an urban programme
      Then the contextual differences are recorded as adaptation assumptions
      And the underlying confidential transcripts remain inaccessible

    @FR-EVA-008 @Later @Could
    Scenario: Reject cross tenant sharing without approval
      Given a lesson in one tenant
      When it is shared with another tenant without approved licensing and disclosure
      Then the sharing is refused

    @FR-EVA-008 @Later @Could
    Scenario: Reject copying restricted material on reuse
      Given a lesson based on restricted interviews
      When it is reused in a new programme
      Then the restricted interviews are not copied
      And identical effectiveness is not implied
