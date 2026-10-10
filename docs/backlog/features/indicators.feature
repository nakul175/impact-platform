# Imprana Commons backlog: Indicators
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Indicators

  Rule: FR-IND-001 Complete indicator definition
    As a MEL Manager, I want the indicator designer to require a complete measurement definition before approval, so that every approved indicator has an unambiguous meaning rather than just a label.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IND-001 @R1-Pilot @Must
    Scenario: Complete measurement contract shown for review
      Given a MEL Manager defining an indicator
      When they provide code, name, type, unit, population, inclusion and exclusion rules, method, source mode, time semantic, frequency, owner and limitations
      And the numerator, denominator, multiplier, direction and aggregation rule required by the type
      Then review displays a complete measurement contract

    @FR-IND-001 @R1-Pilot @Must
    Scenario: Missing denominator blocks approval
      Given a percentage indicator with a numerator but no eligible denominator
      When the MEL Manager validates it
      Then validation links directly to the missing denominator meaning
      And approval remains unavailable

    @FR-IND-001 @R1-Pilot @Must
    Scenario: Reject a label-only or defaulted definition
      Given an indicator with only a label, missing conditional fields, or an undefined population or unit
      When it is submitted
      Then submission is blocked
      And no undocumented default is supplied for the population or unit

  Rule: FR-IND-002 Supported measurement types
    As a MEL Manager, I want each measurement type to constrain the values and operations it allows, so that counts, percentages, rates, ordinal labels and imported scores are never combined in invalid ways.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IND-002 @R1-Pilot @Must
    Scenario: Measurement type constrains inputs
      Given a MEL Manager who selects a measurement type
      When values and operators are configured
      Then counts accept integral eligible quantities
      And percentages use compatible quantities and a multiplier of 100
      And rates declare their multiplier
      And ordinal labels retain ordered codes

    @FR-IND-002 @R1-Pilot @Must
    Scenario: Import a reviewed external score
      Given a reviewed external composite score with external method metadata
      When it is imported
      Then its stated calculation source is retained

    @FR-IND-002 @R1-Pilot @Must
    Scenario: Reject ordinal codes in an additive aggregate
      Given an ordinal indicator
      When a user enters an ordinal code into an additive aggregate
      Then the incompatibility is shown
      And the ordinal labels are not summed

    @FR-IND-002 @R1-Pilot @Must
    Scenario: Reject out-of-range bounded percentages
      Given a bounded percentage without an approved alternative interpretation
      When a value outside zero to 100 is entered
      Then the value is rejected

    @FR-IND-002 @R1-Pilot @Must
    Scenario: Reject composite scores without method metadata
      Given an imported composite score in R1 with no external method metadata
      When it is imported
      Then the import is refused

  Rule: FR-IND-003 Baselines and targets
    As a MEL Manager, I want to set versioned baselines and targets with a declared direction and interpretation, so that progress is calculated correctly for higher, lower, range and milestone targets.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IND-003 @R1-Pilot @Must
    Scenario: Record a baseline or target
      Given a MEL Manager defining a target
      When they set measurement date or period, target kind, value, unit, direction and version
      And choose higher, lower, within range or milestone interpretation
      Then progress uses the declared formula
      And shows whether the original or revised target is selected

    @FR-IND-003 @R1-Pilot @Must
    Scenario: Overachievement against a higher target
      Given a higher target of 100
      When the actual is 120
      Then attainment displays 120 percent
      And it is not capped

    @FR-IND-003 @R1-Pilot @Must
    Scenario: Lower target achieved
      Given a lower target of 10
      When the actual is 8
      Then the result shows achieved and the defined deviation

    @FR-IND-003 @R1-Pilot @Must
    Scenario: Reject dividing by a zero target
      Given a zero target
      When progress is calculated
      Then milestone or reviewed difference logic is used rather than dividing by zero
      And an undefined target ratio displays as undefined

  Rule: FR-IND-004 Target amendments
    As a MEL Manager, I want to amend targets through reviewed versions with reason, effective date and affected periods, so that targets can change without rewriting reports that are already frozen.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IND-004 @R1-Pilot @Must
    Scenario: Review a target amendment
      Given a proposed target amendment with reason, effective date and affected periods
      When a Reviewer opens it
      Then the review compares original, currently effective and proposed values
      And approval retains all earlier versions and identifies any explicit restatement request

    @FR-IND-004 @R1-Pilot @Must
    Scenario: Amend a target after lock
      Given a quarter target of 1000 and a locked report for that quarter
      When the target is changed to 800 and approved
      Then the original report remains against 1000
      And a restated comparison is distinctly labelled

    @FR-IND-004 @R1-Pilot @Must
    Scenario: Reject retrospective changes to a frozen report
      Given a target amendment effective after a locked quarter
      When it is approved without a separately approved restatement
      Then it applies only prospectively
      And the frozen report is unchanged

  Rule: FR-IND-005 Reporting periods
    As a MEL Manager, I want observations assigned to reporting periods by event date and reporting zone, so that late uploads land in the correct period and are flagged rather than misplaced.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IND-005 @R1-Pilot @Must
    Scenario: Boundary event belongs to the new quarter
      Given quarters with inclusive start and exclusive end in the reporting zone
      When an event occurs exactly at midnight on the new quarter boundary and is uploaded two days later
      Then it belongs only to the new quarter

    @FR-IND-005 @R1-Pilot @Must
    Scenario: Receipt time sets timeliness only
      Given a measurement contract that does not use receipt time
      When an observation is received late
      Then period membership follows the event date
      And the late entry is flagged

    @FR-IND-005 @R1-Pilot @Must
    Scenario: Late entry for a locked period
      Given a locked period
      When a late observation for that period arrives
      Then it is routed to restatement review

    @FR-IND-005 @R1-Pilot @Must
    Scenario: Reject summing overlapping windows as official periods
      Given overlapping analytical windows that reuse observations
      When a user sums them as disjoint official periods
      Then the sum is refused

  Rule: FR-IND-006 Disaggregation dimensions
    As a MEL Manager, I want to define versioned disaggregation dimensions with explicit missing, unknown and declined codes, so that breakdowns are accurate and overlapping categories never distort unique reach.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IND-006 @R1-Pilot @Must
    Scenario: Define a dimension
      Given a MEL Manager setting up a dimension
      When they define codes, labels, applicability, exclusivity and exhaustiveness
      Then missing, unknown and declined are available as explicit codes where appropriate
      And submissions store the dimension version and codes

    @FR-IND-006 @R1-Pilot @Must
    Scenario: Multiselect categories keep unique totals
      Given one participant who selects two service types
      When results are aggregated
      Then both categories count the event as defined
      And the unique participant total remains one
      And the category sum is labelled nonadditive

    @FR-IND-006 @R1-Pilot @Must
    Scenario: Changed scheme uses a crosswalk
      Given a category scheme that has changed
      When data across scheme versions is aligned
      Then a reviewed crosswalk is used

    @FR-IND-006 @R1-Pilot @Must
    Scenario: Reject forcing overlapping categories to reconcile
      Given multiselect categories
      When a view tries to reconcile the category sum to unique reach
      Then the reconciliation is refused

  Rule: FR-IND-007 Missing and exceptional values
    As a Data Author, I want to record why a value is missing, not collected or not applicable separately from its number and status, so that blanks are never treated as zeros and every state is reported clearly.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IND-007 @R1-Pilot @Must
    Scenario: Record a reason for a non-numeric state
      Given a Data Author entering or importing a value
      When they mark it not collected or not applicable
      Then they must choose a reason
      And the value state is stored separately from numeric value, workflow status and disclosure status
      And eligibility rules govern whether it is removed from the denominator

    @FR-IND-007 @R1-Pilot @Must
    Scenario: Export distinct value states
      Given rows that are zero, missing, not applicable, invalid and pending
      When they are exported
      Then each has a distinct machine code and matching human label
      And views apply the value state matrix in section 4.2

    @FR-IND-007 @R1-Pilot @Must
    Scenario: Reject blanks as zero
      Given a blank cell in entry or import
      When it is saved
      Then it does not become zero

    @FR-IND-007 @R1-Pilot @Must
    Scenario: Reject suppressed or pending values in results
      Given a suppressed value and a value pending approval
      When results are disclosed and official totals computed
      Then the suppressed numeric payload is removed from the disclosed result
      And the pending value is excluded from official totals

  Rule: FR-IND-008 Definition versioning
    As a MEL Manager, I want material definition edits to create a new version with a comparison report and a comparability decision, so that trends and totals are never combined across incompatible definitions.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IND-008 @R1-Pilot @Must
    Scenario: Material edit creates a child version
      Given an approved indicator definition
      When the MEL Manager makes a material edit
      Then a child version is created
      And a comparison report identifies unit, population, source, method, dimensions and aggregation changes
      And the Reviewer marks comparability as compatible, transformed by approved rule or broken

    @FR-IND-008 @R1-Pilot @Must
    Scenario: Cosmetic label correction
      Given an indicator label with a cosmetic error
      When it is corrected
      Then semantic identity may be retained
      And the change is audited

    @FR-IND-008 @R1-Pilot @Must
    Scenario: Reject combining broken versions
      Given a definition changed from households to people
      When a user requests a combined total
      Then the combined total is blocked until a justified conversion or separate series is selected
      And no continuous trend line or portfolio pool spans the broken versions without explicit qualified treatment

  Rule: FR-IND-010 Manual and calculated results
    As a MEL Manager, I want each result to declare whether it is entered, imported, calculated or aggregated, and manual overrides to keep the computed value beside the approved replacement, so that official figures stay transparent and traceable.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IND-010 @R1-Pilot @Must
    Scenario: Change of actual mode requires approval
      Given an indicator whose actual mode is calculated
      When a user changes it to entered
      Then a new approved measurement version or amendment is required

    @FR-IND-010 @R1-Pilot @Must
    Scenario: Override a computed value
      Given a computed value of 94
      When an override to 90 is proposed with period and reason and approved by an independent Reviewer
      Then the report records the override and explanation
      And retains the calculation of 94
      And views show both values with the official selection

    @FR-IND-010 @R1-Pilot @Must
    Scenario: Remove an override
      Given an approved override
      When it is removed through another attributable decision
      Then the approved calculation is restored

    @FR-IND-010 @R1-Pilot @Must
    Scenario: Reject import or API overwrite of calculated results
      Given a calculated result field
      When an import or API client sends a value for it
      Then the write is refused

  Rule: FR-IND-012 Responsibility and collection schedule
    As a Programme Manager, I want indicator schedules to create assigned obligations with a collector, independent reviewer, due time and escalation owner, so that collection never silently stalls when people change roles or leave.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IND-012 @R1-Pilot @Must
    Scenario: Schedule creates assigned obligations
      Given an indicator schedule with an active date range
      When it is instantiated
      Then obligations are created with a collector, independent reviewer, due time and escalation owner

    @FR-IND-012 @R1-Pilot @Must
    Scenario: Preview an assignment change
      Given a collector with open work and future obligations
      When the Programme Manager changes the assignment
      Then the preview shows open work and future obligations separately

    @FR-IND-012 @R1-Pilot @Must
    Scenario: Suspended collector creates reassignment work
      Given a collector suspended one day before due
      When the Programme Manager views the obligation
      Then it shows as unassigned
      And they can appoint an eligible replacement

    @FR-IND-012 @R1-Pilot @Must
    Scenario: Reject silent routing on departure
      Given a collector whose account has been revoked
      When their obligations come due
      Then no task is sent to the revoked account
      And no obligation is marked complete
      And historic owners remain attributed

  Rule: FR-IND-009 Indicator library reuse
    As a MEL Manager, I want projects to pin a library indicator version and preview the impact before adopting a new version, so that portfolio comparisons stay honest when projects use different versions.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-IND-009 @R2-Scale @Should
    Scenario: Instantiate a library indicator
      Given a library indicator
      When the MEL Manager instantiates it in a project
      Then the parent definition version is pinned
      And local applicability, collection roles and permitted overrides are recorded

    @FR-IND-009 @R2-Scale @Should
    Scenario: Mixed versions are flagged
      Given two projects pinned to version 1
      When only one adopts version 2 with a changed denominator after previewing comparability and reporting impact
      Then the portfolio flags the mixed comparison

    @FR-IND-009 @R2-Scale @Should
    Scenario: Reject local changes that claim exact equivalence
      Given a project instance of a library indicator
      When a locked semantic field is changed locally
      Then a distinct reviewed definition is created
      And the instance does not claim exact standard equivalence

  Rule: FR-IND-011 Evidence requirements
    As a Reviewer, I want approval to check that required evidence has been received, is safe, verified and still available, so that achievements are approved only on trustworthy evidence.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-IND-011 @R2-Scale @Must
    Scenario: Evidence checks at submission and approval
      Given an evidence rule with permitted types, minimum count, source qualification and verification
      When a Data Author submits an achievement
      Then submission checks attachment receipt and scan state
      And approval checks provenance and current availability
      And external evidence shows last checked status and version reference

    @FR-IND-011 @R2-Scale @Must
    Scenario: Quarantined evidence blocks approval
      Given an achievement submitted with one required survey file still quarantined
      When the submission is received
      Then source receipt succeeds
      But approval stays blocked until the evidence is safe and verified

    @FR-IND-011 @R2-Scale @Must
    Scenario: Reject dead or quarantined evidence
      Given a mandatory evidence rule
      When the evidence is a dead URL or quarantined file
      Then the rule is not satisfied
      And approval proceeds only under a policy permitted evidence exception with an independent decision and a visible caveat

  Rule: FR-IND-013 Status and thresholds
    As a Programme Manager, I want indicator status to evaluate data freshness and coverage before thresholds, so that stale or partial results are never shown as success.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-IND-013 @R2-Scale @Should
    Scenario: Status rules evaluate adequacy first
      Given status rules declaring direction, thresholds, tolerance, target reference and minimum freshness and coverage
      When status is evaluated
      Then data adequacy is evaluated first
      And boundary equality follows the published rule

    @FR-IND-013 @R2-Scale @Should
    Scenario: Achieved but stale
      Given a lower-is-better measure at 8 against target 10 with a missed refresh
      When status is evaluated
      Then it is achieved
      And it also displays stale
      And it cannot trigger an unqualified success alert

    @FR-IND-013 @R2-Scale @Should
    Scenario: Qualitative status needs a reviewer assessment
      Given a qualitative indicator
      When its status is set
      Then a recorded Reviewer assessment is required

    @FR-IND-013 @R2-Scale @Should
    Scenario: Reject green for missing results
      Given a missing result
      When status is displayed
      Then it is not coloured green

    @FR-IND-013 @R2-Scale @Should
    Scenario: Reject status detail for unauthorised viewers
      Given a viewer not authorised for the full result
      When they view status
      Then they receive only the permitted status context

  Rule: FR-IND-014 Retirement and replacement
    As a MEL Manager, I want to retire an indicator with an effective date, replacement and continuity statement after previewing its dependencies, so that new obligations stop without breaking historical results or silently breaking future calculations.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-IND-014 @R2-Scale @Must
    Scenario: Preview retirement impact
      Given an indicator proposed for retirement with an effective date, replacement and continuity statement
      When the MEL Manager previews it
      Then future obligations, calculations, dashboard bindings and report templates are identified

    @FR-IND-014 @R2-Scale @Must
    Scenario: Approved retirement stops new obligations
      Given an approved retirement
      When the effective date passes
      Then no new obligations are created
      And historical results remain available for lookup

    @FR-IND-014 @R2-Scale @Must
    Scenario: Retire an indicator feeding a portfolio total
      Given an indicator feeding a portfolio total
      When it is retired
      Then the next period calculation blocks until its replacement rule is reviewed
      And last year's report remains intact

    @FR-IND-014 @R2-Scale @Must
    Scenario: Reject hard deletion and unmanaged dependants
      Given a used indicator definition with dependent future formulas
      When retirement is processed
      Then the definition is not hard deleted
      And each dependent future formula is migrated or explicitly left unavailable with an accountable remediation item

  Rule: FR-IND-015 Reference sheets and dictionary export
    As a MEL Manager, I want to export indicator reference sheets and a machine readable data dictionary for selected versions, so that evaluators can understand each measure without access to our private settings.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-IND-015 @R2-Scale @Should
    Scenario: Export reference sheets
      Given selected indicator versions
      When the MEL Manager exports reference sheets
      Then the export includes human readable definitions and a machine readable dictionary
      And it covers units, eligibility, dimensions, time semantic, formula, source, roles, missingness rules and version references

    @FR-IND-015 @R2-Scale @Should
    Scenario: Evaluator understands a ratio
      Given an evaluator who receives a ratio reference sheet
      When they read it
      Then they can identify numerator population, denominator, multiplier and period without consulting the application's private settings

    @FR-IND-015 @R2-Scale @Should
    Scenario: Reject leaking restricted content or losing precision
      Given an export scope that excludes restricted definitions or source names
      When the export is produced
      Then those items are redacted and marked withheld
      And display rounding does not replace calculation precision metadata
