# Imprana Commons backlog: Results planning
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Results planning

  Rule: FR-PLN-001 Results hierarchy
    As a MEL Manager, I want to build the results framework in a table or relationship view that both edit the same nodes, so that I can structure programme results in the way that suits me without creating duplicates or inconsistencies.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-PLN-001 @R1-Pilot @Must
    Scenario: Create framework nodes in either view
      When the MEL Manager creates typed framework nodes in the table or relationship view
      Then both views edit the same stable node identities and version
      And activities may be linked to output nodes
      And relationship links are kept distinct from numeric aggregation links

    @FR-PLN-001 @R1-Pilot @Must
    Scenario: Rename a node in one view
      Given an output with indicator bindings in a draft
      When the MEL Manager renames the output in the table
      Then the graph and indicator bindings update within the same draft
      And no duplicate node is created

    @FR-PLN-001 @R1-Pilot @Must
    Scenario: Validate nodes before review
      When the MEL Manager submits the draft for review
      Then each node is validated for title, description, owner and intended result level

    @FR-PLN-001 @R1-Pilot @Must
    Scenario: Reject invalid structural changes
      When the MEL Manager creates a containment cycle, leaves an orphaned parent reference or deletes a referenced approved node
      Then the change is rejected

  Rule: FR-PLN-003 Framework baselines
    As a MEL Manager, I want to submit a framework for review with its completeness report and change comparison and freeze an approved baseline, so that later changes are dated drafts and past reports keep the framework they were approved under.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-PLN-003 @R1-Pilot @Must
    Scenario: Submit and approve a framework baseline
      When the MEL Manager submits a framework candidate with its completeness report and change comparison
      Then review shows impacted indicators, targets, activities, templates and obligations
      And approval freezes a baseline version

    @FR-PLN-003 @R1-Pilot @Must
    Scenario: Change an approved framework
      Given an approved baseline
      When the MEL Manager revises an outcome in July
      Then a child draft with an effective date is started

    @FR-PLN-003 @R1-Pilot @Must
    Scenario: Reject rewriting historical reports
      Given a March report was approved against the earlier baseline
      When the March report is regenerated after the July revision
      Then it retains its approved hierarchy and language

    @FR-PLN-003 @R1-Pilot @Must
    Scenario: Reject deleting approved history
      Given an obsolete draft
      When it is deleted
      Then approved history and source citations are not deleted

  Rule: FR-PLN-006 Measurement plan
    As a MEL Manager, I want activating a measurement plan to check that every active indicator has its source, method, collector, reviewer, calendar, coverage and evidence rule, so that indicators only go live when they can actually be collected and reviewed.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-PLN-006 @R1-Pilot @Must
    Scenario: Completeness check creates remediation items
      Given a measurement plan in which an active indicator lacks source mode, method, collection owner, reviewer, calendar, coverage or evidence rule
      When the MEL Manager runs activation
      Then the completeness check lists each gap
      And an assigned remediation item is created for each gap

    @FR-PLN-006 @R1-Pilot @Must
    Scenario: Activation shows the exact missing fields
      Given a measurement plan with an unassigned reviewer and a missing denominator method
      When the MEL Manager attempts to move the plan from Ready to Active
      Then both exact fields are shown
      And the plan cannot move from Ready to Active until both are resolved

    @FR-PLN-006 @R1-Pilot @Must
    Scenario: Reject an ineligible or non-independent collector and reviewer
      Given an indicator where collector and reviewer independence is required
      When an ineligible person, or the collector, is assigned as reviewer
      Then the assignment is refused

    @FR-PLN-006 @R1-Pilot @Must
    Scenario: Reject a default zero series for a missing source binding
      Given an active indicator with no source binding
      When activation runs
      Then no default zero series is substituted
      And the missing binding is reported as a gap

  Rule: FR-PLN-010 Framework completeness review
    As a MEL Manager, I want a framework completeness review that lists each issue with severity, rule and an assigned resolver, so that frameworks are approved only when gaps are fixed or covered by permitted documented exceptions.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-PLN-010 @R1-Pilot @Must
    Scenario: Completeness view lists issues
      Given a submitted results framework
      When the MEL Manager opens the completeness view
      Then it checks orphan nodes, unmeasured outcomes, missing owners, invalid sources, unreviewed assumptions and conflicting reporting obligations
      And each issue shows severity, object, rule and assigned resolver

    @FR-PLN-010 @R1-Pilot @Must
    Scenario: Unmeasured output is excepted or blocks approval
      Given a framework submitted with an unmeasured output
      When approval is requested
      Then approval proceeds only with a permitted exception documented with reason and review date
      And otherwise approval remains blocked with an assigned action

    @FR-PLN-010 @R1-Pilot @Must
    Scenario: Reject exceptions for structural invalidity
      Given a framework with a structural invalidity or unsupported official arithmetic
      When a user requests an exception
      Then the exception is refused
      And approval remains blocked

    @FR-PLN-010 @R1-Pilot @Must
    Scenario: Reject warning acceptance by anyone but the named authority
      Given a warning with a named accepting authority
      When another user tries to accept it
      Then the acceptance is refused
      And once accepted by the named authority, the warning remains visible in baseline evidence

  Rule: FR-PLN-004 Reusable libraries
    As a MEL Manager, I want to publish versioned library templates that projects use as pinned copies or managed instances and update only after reviewing the differences, so that approved definitions never change without a deliberate project decision.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-PLN-004 @R2-Scale @Should
    Scenario: Publish a library version with governance details
      Given a MEL Manager curating a reusable library
      When they publish a library version
      Then the version records applicability, owner, review date and permitted override fields

    @FR-PLN-004 @R2-Scale @Should
    Scenario: Consuming projects stay on their version until they adopt a reviewed revision
      Given two projects that consume the same library template
      When the MEL Manager updates the template denominator and publishes a new version
      Then each project receives an update notice showing the semantic differences and affected local changes
      And both projects remain on their existing versions
      And each project moves to the revised version only when it adopts the reviewed revision

    @FR-PLN-004 @R2-Scale @Should
    Scenario: Project declines a library update
      Given a project with a pending library update
      When the Programme Manager rejects the update with a reason
      Then the project stays on its existing version
      And the reason is recorded

    @FR-PLN-004 @R2-Scale @Should
    Scenario: Reject automatic update of approved definitions
      Given a project that consumes a library template as a managed instance with an approved definition
      When a new library version is published
      Then the approved definition is not updated automatically

    @FR-PLN-004 @R2-Scale @Should
    Scenario: Reject new use of a retired library
      Given a library that has been retired
      When a user tries to instantiate it in a project
      Then the instantiation is refused
      But existing reports that used the library remain valid

  Rule: FR-PLN-007 Assumptions and context
    As a Programme Manager, I want to record assumptions and context linked to framework nodes and flag affected plans when an assumption becomes invalid, so that we can reinterpret results without altering what was actually recorded.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-PLN-007 @R2-Scale @Should
    Scenario: Record an assumption linked to a node
      Given a Programme Manager working on a results framework
      When they create an assumption linked to a node
      Then it records expected condition, evidence, owner, review date and status

    @FR-PLN-007 @R2-Scale @Should
    Scenario: Invalidating an assumption flags affected planning
      Given a funding assumption linked to an outcome whose baseline was approved
      When the Programme Manager marks the assumption invalid
      Then a review task is generated
      And the linked outcome is flagged in affected planning views
      And historical results remain unchanged

    @FR-PLN-007 @R2-Scale @Should
    Scenario: Reject changes to recorded actuals
      Given recorded actuals for an outcome linked to an assumption
      When the assumption status changes
      Then the recorded actuals are not altered

    @FR-PLN-007 @R2-Scale @Should
    Scenario: Reject overwriting a past assessment
      Given a past assumption with an existing assessment
      When the assumption is changed
      Then the previous assessment and its effective date are retained

  Rule: FR-PLN-009 Document assisted setup
    As a Programme Manager, I want to set up a programme from a proposal document by reviewing extracted values with their source location and inference labels, so that I can start faster while missing or conflicting facts stay visible.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-PLN-009 @R2-Scale @Should
    Scenario: Choose a setup path
      Given a Programme Manager starting programme setup
      When they choose the manual, library or document assisted path
      Then each path produces the same draft entities

    @FR-PLN-009 @R2-Scale @Should
    Scenario: Review extracted values
      Given a processed proposal document
      When the Programme Manager reviews the extraction
      Then each value shows source location, proposed field, ambiguity and inference label
      And they can accept or edit selected values
      And unresolved fields are shown before submission

    @FR-PLN-009 @R2-Scale @Should
    Scenario: Conflicting end dates block activation
      Given a proposal containing two different end dates
      When the document is processed
      Then setup shows both references
      And the programme cannot be activated until the owner resolves the conflict

    @FR-PLN-009 @R2-Scale @Should
    Scenario: Reject invented facts and embedded commands
      Given a proposal that omits dates, populations or commitments
      When extraction runs
      Then the missing values stay missing
      And AI inferred relationships are not presented as source facts
      And material additions require normal review
      But no source text can execute a product command

  Rule: FR-PLN-002 Theory of change relationships
    As a MEL Manager, I want to add directed contribution links with rationale, assumptions, evidence strength and optional context to the theory of change, so that I can document how results contribute to each other without implying calculations or causal proof.
    Release: R3 Ecosystem · Priority: Should · Built today: Partial

    @FR-PLN-002 @R3-Ecosystem @Should
    Scenario: Add a contribution link
      When the MEL Manager adds a directed contribution link
      Then it records rationale, assumptions, evidence strength and optional external context
      And alternative causal pathways are allowed

    @FR-PLN-002 @R3-Ecosystem @Should
    Scenario: Link across programmes
      When the MEL Manager links to a result in another programme
      Then the link is allowed only with permission to both endpoints or through a separately shared summary endpoint

    @FR-PLN-002 @R3-Ecosystem @Should
    Scenario: Reject implied calculation
      Given two outcomes are linked to one impact
      When the parent result is inspected
      Then it remains uncalculated until an explicit approved numeric rule exists
      And the relationship creates no numeric sum, deduplication rule or causal proof

    @FR-PLN-002 @R3-Ecosystem @Should
    Scenario: Reject containment cycles
      When a link would create a containment cycle
      Then it is rejected

  Rule: FR-PLN-005 Standard mappings
    As a MEL Manager, I want to map local nodes or indicators to versioned external standards with a relation type, rationale and reviewer, so that we can organise reporting against standards such as the SDGs without distorting our own results.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-PLN-005 @R3-Ecosystem @Should
    Scenario: Record a reviewed mapping to an external standard
      Given a MEL Manager in the mapping editor
      When they link a local indicator to an entry in a versioned external standard using a relation type such as related to, contributes to or equivalent by reviewed definition
      Then the mapping records the relation type, rationale and reviewer

    @FR-PLN-005 @R3-Ecosystem @Should
    Scenario: Map one local measure to two SDG entries without double counting
      Given a local measure with an organisational unique result
      When the MEL Manager maps it to two SDG entries
      Then both mappings are available to organise reporting
      And the organisational unique result is still counted once

    @FR-PLN-005 @R3-Ecosystem @Should
    Scenario: Keep mappings to an unavailable standard version
      Given a mapping to a standard version that is no longer available
      When a user views the mapping
      Then it remains as a historical reference

    @FR-PLN-005 @R3-Ecosystem @Should
    Scenario: Reject treating mappings as arithmetic
      Given a local indicator with many to many mappings to an external standard
      When results are reported through those mappings
      Then the mappings do not imply mathematical equivalence, unit conversion or additive attribution

  Rule: FR-PLN-008 Planning scenarios
    As a Programme Manager, I want to model planning scenarios from a pinned baseline and adopt one through normal amendment proposals, so that I can compare options without bypassing approvals or confusing projections with actuals.
    Release: Later · Priority: Could · Built today: Absent

    @FR-PLN-008 @Later @Could
    Scenario: Compare funding scenarios
      Given a programme with a pinned baseline
      When the Programme Manager creates two funding scenarios with altered targets, budgets, timing and assumptions and compares them
      Then the comparison shows the differences
      And calculated projections are shown separately from approved actuals

    @FR-PLN-008 @Later @Could
    Scenario: Adopt a scenario through amendment proposals
      Given two compared funding scenarios
      When the Programme Manager adopts one
      Then an ordinary amendment proposal is created for each governed object
      And the original targets remain official until all required amendment decisions complete

    @FR-PLN-008 @Later @Could
    Scenario: Reject direct promotion of a scenario
      Given a scenario with altered targets and budgets
      When a user attempts to promote it directly to official
      Then the operation is refused
      And target, budget and framework approval are still required

    @FR-PLN-008 @Later @Could
    Scenario: Reject abandoned scenarios in official views
      Given an abandoned scenario
      When an official portfolio view is displayed
      Then the scenario is excluded
      And it remains labelled as abandoned
