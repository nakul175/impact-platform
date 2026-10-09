# Imprana Commons backlog: Calculations
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Calculations

  Rule: FR-CAL-001 Deterministic calculation
    As an Analyst, I want calculations to run deterministically from approved rules and sources with a recorded input manifest and explanation, so that every official result can be reproduced and traced to its source.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-CAL-001 @R1-Pilot @Must
    Scenario: Run a calculation
      Given approved rule and source versions
      When a calculation run executes
      Then an input manifest is created and the deterministic dependency graph is evaluated
      And the result stores value state, precision, filters, coverage and execution identity
      And explanations resolve each contributing result to its original source

    @FR-CAL-001 @R1-Pilot @Must
    Scenario: Reproduce a frozen ratio
      Given a frozen ratio with exported inputs and the recorded formula
      When the Analyst recomputes it
      Then the raw decimal and displayed rounded output match exactly

    @FR-CAL-001 @R1-Pilot @Must
    Scenario: Reject AI-supplied values
      Given a calculation result
      When an AI message proposes a value
      Then it is not used as the authoritative value

    @FR-CAL-001 @R1-Pilot @Must
    Scenario: Reject zero after a failed run
      Given a prior calculation result
      When a new run fails
      Then the prior result is labelled stale
      And the failure is exposed
      And the result is not overwritten with zero

  Rule: FR-CAL-002 Type and unit compatibility
    As an Analyst, I want calculations to check type, unit, population, period and dimension compatibility before running, so that only genuinely compatible values are combined.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-CAL-002 @R1-Pilot @Must
    Scenario: Type checking before execution
      Given a calculation ready to run
      When execution starts
      Then measurement types, units, populations, period semantics, definitions and dimensions are compared first

    @FR-CAL-002 @R1-Pilot @Must
    Scenario: Combine with an approved conversion
      Given values of 1 hectare and 1 acre and an approved conversion
      When the Analyst combines them
      Then the conversion references an approved version, direction and precision
      And the preview shows original and converted inputs

    @FR-CAL-002 @R1-Pilot @Must
    Scenario: Reject people plus households
      Given a people measure and a household measure with no justified conversion
      When the Analyst combines them
      Then the total is rejected

    @FR-CAL-002 @R1-Pilot @Must
    Scenario: Reject compatibility from similar labels
      Given two measures with similar labels but no established compatibility
      When they are combined
      Then the labels are not accepted as establishing compatibility

  Rule: FR-CAL-003 Ratios rates and percentages
    As an Analyst, I want pooled ratios, rates and percentages to be calculated from the underlying numerators and denominators, so that combined percentages are correctly weighted.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-CAL-003 @R1-Pilot @Must
    Scenario: Pool two ratios
      Given components of 50 of 100 and 1 of 10
      When the Analyst pools them
      Then the result is 51 of 110
      And it displays 46.36 percent under two decimal rounding
      And the weighting basis is disclosed

    @FR-CAL-003 @R1-Pilot @Must
    Scenario: Unweighted mean is a separate statistic
      Given an explicitly requested unweighted mean
      When it is calculated
      Then it is labelled as a different statistic from the pooled percentage

    @FR-CAL-003 @R1-Pilot @Must
    Scenario: Reject averaging percentages
      Given components of 50 of 100 and 1 of 10
      When a pooled percentage is produced
      Then it is never 30 percent
      And a component lacking the necessary quantities does not contribute as if its percentage were sufficient

    @FR-CAL-003 @R1-Pilot @Must
    Scenario: Reject a number for a zero denominator
      Given a pooled denominator of zero
      When the ratio is calculated
      Then the result is UNDEFINED

  Rule: FR-CAL-005 Time aggregation semantics
    As an Analyst, I want each indicator's time semantic to control how values aggregate over time, so that stocks, flows, events and cumulative totals are never added up wrongly.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-CAL-005 @R1-Pilot @Must
    Scenario: Aggregate by time semantic
      Given an indicator
      When the Analyst selects flow sum, latest eligible stock, event count or approved cumulative difference
      Then aggregation follows that semantic
      And snapshots specify maximum permissible age and tie resolution

    @FR-CAL-005 @R1-Pilot @Must
    Scenario: Cumulative positions
      Given cumulative positions of 10, 15 and 20
      When they are aggregated
      Then the end value reported is 20
      And increments of 10, 5 and 5 are reported only when a zero starting baseline is established

    @FR-CAL-005 @R1-Pilot @Must
    Scenario: Cumulative decline needs a correction or reset
      Given a cumulative series that declines
      When it is processed
      Then a correction or reset event with defined treatment is required

    @FR-CAL-005 @R1-Pilot @Must
    Scenario: Reject summing cumulative totals
      Given monthly cumulative totals
      When they are aggregated by default
      Then they are not summed

    @FR-CAL-005 @R1-Pilot @Must
    Scenario: Reject exact increments without a starting value
      Given a missing starting cumulative value
      When an exact period increment is requested
      Then it is not produced unless the approved method supplies a justified baseline

  Rule: FR-CAL-008 Missingness and coverage
    As a MEL Manager, I want each period's results to count received, valid and approved contributors against the expected contributor set separately, so that official sums use only approved eligible values and are marked partial when mandatory contributors are absent.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-CAL-008 @R1-Pilot @Must
    Scenario: Coverage distinguishes approved, pending and missing contributors
      Given the obligation snapshot for the period expects five partners
      And three partners have approved values, one is pending and one is missing
      When the result is calculated
      Then approval coverage is 60 percent
      And the pending count and the missing count are shown separately

    @FR-CAL-008 @R1-Pilot @Must
    Scenario: Official sum is partial when a mandatory contributor is absent
      Given a mandatory contributor has no approved value for the period
      When the official sum is calculated
      Then it uses only approved eligible values
      And the result carries partial status

    @FR-CAL-008 @R1-Pilot @Must
    Scenario: Reject removing an expected contributor without approved eligibility evidence
      Given a partner retired today whose obligation was active in a prior period
      When the prior period result is calculated
      Then the partner remains in the expected contributor set for that period
      And an attempt to mark its obligation not applicable without approved eligibility evidence is refused

  Rule: FR-CAL-009 Precision and rounding
    As an Analyst, I want calculation rules to declare input scale, precision, rounding mode and display decimals and to round only at the output boundary, so that reported figures are accurate and exports carry the raw decimal alongside display metadata.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-CAL-009 @R1-Pilot @Must
    Scenario: Round only at the output boundary
      Given a rule that rounds half up to two decimals at output
      And three input values of 0.335
      When the values are summed
      Then the unrounded total is 1.005
      And the displayed result is 1.01
      And the rule documentation explains why summing the rounded components would give a different total

    @FR-CAL-009 @R1-Pilot @Must
    Scenario: Export carries the raw decimal and display metadata
      Given a rounded result
      When it is exported
      Then the export contains the raw decimal string
      And display metadata where applicable

    @FR-CAL-009 @R1-Pilot @Must
    Scenario: Reject rounded inputs and unsafe numeric conversion
      Given a display-rounded value, a large identifier and a count beyond the qualified numeric range
      When each is submitted to a calculation
      Then the display-rounded value is refused as a new source input
      And the large identifier is kept as text and never converted to a number
      And the out-of-range count produces an explicit limit error

  Rule: FR-CAL-010 Zero denominators and invalid inputs
    As a MEL Manager, I want invalid inputs rejected before calculation and zero-denominator ratios returned as undefined with a reason, so that impossible or meaningless values are never reported as successful results.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-CAL-010 @R1-Pilot @Must
    Scenario: Zero denominator returns undefined with a reason
      Given a ratio indicator
      When 5 is divided by 0
      Then the result is UNDEFINED with a stated reason
      And it is not displayed as a successful zero

    @FR-CAL-010 @R1-Pilot @Must
    Scenario: Negative adjustment through an approved measure
      Given an approved adjustment measure or correction contract
      When a negative adjustment is submitted under it
      Then the adjustment is accepted for calculation

    @FR-CAL-010 @R1-Pilot @Must
    Scenario: Reject invalid inputs before calculation
      Given a submission of negative two participants
      When validation runs before calculation
      Then the value is rejected as invalid and not displayed as a successful zero
      And nonfinite inputs, impossible dates and incompatible sign conventions are also rejected

    @FR-CAL-010 @R1-Pilot @Must
    Scenario: Reject negative counts and automatic clipping
      Given a spreadsheet containing a refund-like negative value for an eligible count
      And no approved adjustment measure or correction contract applies
      When the data is calculated
      Then the eligible count does not become negative
      And a percentage outside its bounds is not automatically clipped without explicit valid semantics

  Rule: FR-CAL-011 Corrections and recalculation
    As a Data Steward, I want an approved source correction to recalculate affected downstream results while published snapshots stay bound to their original version, so that live figures reflect the correction without silently altering what was already published.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-CAL-011 @R1-Pilot @Must
    Scenario: Correction updates live results but not published snapshots
      Given a ratio whose numerator comes from an imported value
      And a quarterly PDF report has been published from it
      When a correction to that numerator is approved
      Then the affected definitions, result periods, dashboards and unpublished reports are identified
      And recalculation creates a new result version and the current ratio updates
      And the published quarterly PDF remains the original version until restated

    @FR-CAL-011 @R1-Pilot @Must
    Scenario: Retry creates one new result per input version
      Given a recalculation is retried after an interruption
      When it completes
      Then exactly one intended new result exists per input version

    @FR-CAL-011 @R1-Pilot @Must
    Scenario: Reject a mixed official snapshot after a failed run
      Given a downstream recalculation run fails
      When affected results are viewed
      Then they show stale status
      And no partially recalculated mixed official snapshot is presented
      But the published report is not restated without a separate approved restatement

  Rule: FR-CAL-015 Reconciliation and explainability
    As an Analyst, I want an explanation view for each result and a run comparison that classifies differences by cause, so that I can reconcile changes in figures before reports are approved.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-CAL-015 @R1-Pilot @Must
    Scenario: Explanation view shows how a result was produced
      Given a calculated result
      When the Analyst opens its explanation view
      Then it shows the rule version, source set, included and excluded counts, adjustments, coverage and approval

    @FR-CAL-015 @R1-Pilot @Must
    Scenario: Run comparison separates the effect of each change
      Given one source value and one filter have changed between two runs
      When the runs are compared
      Then the effect of the source change and the effect of the filter change are identified and classified separately
      And no single unexplained total difference is reported

    @FR-CAL-015 @R1-Pilot @Must
    Scenario: Reject inspection of restricted excluded records
      Given a viewer without access to some excluded records
      When they use reconciliation
      Then only permitted aggregates or withheld references are shown
      And the restricted excluded records cannot be inspected

    @FR-CAL-015 @R1-Pilot @Must
    Scenario: Reject report approval with unreconciled differences
      Given numerical differences that do not reconcile to stated causes
      When report approval is requested
      Then approval is blocked

  Rule: FR-CAL-004 Population overlap
    As an Analyst, I want unique reach computed from permitted identity matches with the overlap recorded, so that reach is not overstated and aggregate-only figures are clearly shown as gross.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-CAL-004 @R2-Scale @Must
    Scenario: Unique reach with matched identities
      Given a unique reach definition declaring entity type, population, time window and approved identity matching scope
      And two approved sets of 100 with 20 shared authorised identities
      When unique reach is computed
      Then the result is 180
      And the matched overlap is recorded

    @FR-CAL-004 @R2-Scale @Must
    Scenario: Aggregate-only inputs
      Given the same totals as aggregate-only inputs with no valid external deduplication method
      When reach is computed
      Then the result is gross 200 with unknown overlap

    @FR-CAL-004 @R2-Scale @Must
    Scenario: Reject matching by similar names
      Given records in different projects or tenants with similar names
      When unique reach is computed
      Then they are not matched

    @FR-CAL-004 @R2-Scale @Must
    Scenario: Reject unreviewed fuzzy resolution
      Given a fuzzy match candidate without reviewed evidence and permission
      When unique reach is computed
      Then unique counts do not change

  Rule: FR-CAL-006 Hierarchical aggregation
    As an Analyst, I want hierarchical aggregation to follow declared edge rules and detect cycles and repeated sources, so that parent totals count each contribution correctly across many reporting levels.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-CAL-006 @R2-Scale @Must
    Scenario: Edges declare their rules
      Given an aggregation hierarchy
      When an edge is defined
      Then it identifies contribution, combination rule and attribution scope
      And aggregation is qualified across at least ten reporting levels

    @FR-CAL-006 @R2-Scale @Must
    Scenario: Deduplicate a repeated source
      Given a source contributing 7 through two intermediate totals
      When a unique parent is evaluated
      Then 7 is included once

    @FR-CAL-006 @R2-Scale @Must
    Scenario: Reject a cyclic edge
      Given the existing hierarchy
      When a reverse edge is added
      Then it is rejected as cyclic

    @FR-CAL-006 @R2-Scale @Must
    Scenario: Reject ambiguous duplication
      Given a repeated path where the contract does not define a unique union
      When the parent is evaluated
      Then additive duplication is blocked
      And the value is not silently halved
      And weighted allocations require explicit weights and reconciliation

  Rule: FR-CAL-007 Dimension alignment
    As a Data Steward, I want category crosswalks that record versions, mapping type and information loss, so that data aligned across dimension schemes never claims more precision than it has.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-CAL-007 @R2-Scale @Must
    Scenario: Record a crosswalk
      Given source and target dimension versions
      When the Data Steward creates a crosswalk
      Then it records source and target versions, mapping type and information loss
      And exact mapping, many to one pooling and approved proportional allocation are distinct

    @FR-CAL-007 @R2-Scale @Must
    Scenario: Preview shows gaps
      Given a crosswalk
      When the Data Steward previews it
      Then unmapped and suppressed contributions are reported

    @FR-CAL-007 @R2-Scale @Must
    Scenario: Reject splitting a broad band without data
      Given one aggregate for ages 0 to 17
      When a user attempts to convert it into 0 to 14
      Then exact transformation is blocked
      And the unresolved coverage remains visible

    @FR-CAL-007 @R2-Scale @Must
    Scenario: Reject silently remapping unknown
      Given values coded unknown
      When a crosswalk is applied
      Then unknown is not silently mapped to another category

  Rule: FR-CAL-012 Formula authoring and validation
    As a MEL Manager, I want to author indicator formulas from typed references and a bounded function catalogue and preview them for permissions, cycles, units and sample outputs, so that only safe, valid formulas reach review and activation.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-CAL-012 @R2-Scale @Must
    Scenario: Preview validates a formula before review
      Given a formula using typed references and catalogue functions such as sum and ratio
      When the MEL Manager previews it
      Then permissions, dependency cycles and units are validated
      And sample outputs are shown before it is submitted for review

    @FR-CAL-012 @R2-Scale @Must
    Scenario: Reject inaccessible, circular and external references
      Given formulas that reference an inaccessible field, a circular indicator and an external URL call
      When each is validated
      Then each is rejected before activation

    @FR-CAL-012 @R2-Scale @Must
    Scenario: Reject scripts and unsupported functions
      Given a formula containing an unsupported function, an arbitrary script, a filesystem reference or a dynamically broadened query
      When it is validated
      Then it fails validation

  Rule: FR-CAL-014 Cross portfolio attribution
    As a Funder Portfolio Manager, I want projects to appear in every portfolio they belong to while organisation-wide totals count each unique project once, with attribution shares applied only in approved allocation views, so that results are never double counted or over-attributed.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-CAL-014 @R2-Scale @Must
    Scenario: Project in multiple portfolios is counted once organisation-wide
      Given project P belongs to the health and education portfolios
      When each portfolio and the organisation-wide count are viewed
      Then each portfolio may show P
      And the organisation unique project count stays one

    @FR-CAL-014 @R2-Scale @Must
    Scenario: Allocation view applies approved attribution shares
      Given separately approved attribution shares with a declared basis and remainder policy
      When the allocation view is displayed
      Then results are allocated according to those shares

    @FR-CAL-014 @R2-Scale @Must
    Scenario: Reject shares exceeding the source total
      Given attribution shares that exceed the source total
      When the allocation view is saved
      Then it is rejected unless the view is explicitly nonadditive and labelled
      And a funding share is never presented as causal impact ownership

  Rule: FR-CAL-013 Weighted and composite indicators
    As a MEL Manager, I want to configure weighted composite indicators with components, normalisation, weights and a missing-component policy, preview each component's contribution, and pin approved versions, so that composite scores are transparent and reproducible.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-CAL-013 @R3-Ecosystem @Should
    Scenario: Weighted composite score is calculated
      Given a normalised weighted mean with component scores 60 and 80
      And weights 0.4 and 0.6
      When the composite is calculated
      Then the score is 72
      And the preview shows each component's contribution and sensitivity to proposed weights

    @FR-CAL-013 @R3-Ecosystem @Should
    Scenario: Changing weights creates a new version
      Given an approved composite configuration pinned with its source versions
      When the weights are changed
      Then a new version is created
      And the old score remains reproducible

    @FR-CAL-013 @R3-Ecosystem @Should
    Scenario: Reject invalid weights or missing required components
      Given a normalised weighted mean whose weights do not sum to one
      When the configuration is validated
      Then it is rejected
      And a missing required component blocks the score or returns an explicitly incomplete score
      But renormalisation is applied only when the approved rule declares it

  Rule: FR-CAL-016 Statistical interpretation
    As an Analyst, I want statistical outputs to declare method, sample basis, weights, uncertainty and limitations and to pool only from compatible raw values or valid sufficient statistics, so that statistics are never misrepresented.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-CAL-016 @R3-Ecosystem @Should
    Scenario: Pooled median from raw values
      Given one group with raw values 1, 2 and 100 and another with raw values 3 and 4
      When a pooled median is calculated
      Then the result is 3
      And the result package contains calculation metadata and limitations

    @FR-CAL-016 @R3-Ecosystem @Should
    Scenario: Reject a pooled median from subgroup medians alone
      Given only subgroup medians are available
      When a pooled median is requested
      Then no pooled median claim is produced
      And any mean of medians is labelled as a mean of medians, never a pooled median

    @FR-CAL-016 @R3-Ecosystem @Should
    Scenario: Reject sample estimates as population counts
      Given a sample estimate without a reviewed expansion method
      When it is reported
      Then it is not presented as a population count
