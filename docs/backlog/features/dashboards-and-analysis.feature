# Imprana Commons backlog: Dashboards and analysis
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Dashboards and analysis

  Rule: FR-ANA-002 Filters and drill down
    As an Analyst, I want filters that show their current values and drill down through permitted hierarchy levels and disclosure slices, so that I can explore results without revealing suppressed or restricted data.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-ANA-002 @R1-Pilot @Must
    Scenario: Filter by partner and drill to programme data
      Given a dashboard covering partner A and partner B
      When the Analyst selects partner A and drills down to programme data
      Then the filter shows its current value
      And drill down follows only permitted hierarchy levels and approved disclosure slices
      And the restricted participant level remains unavailable

    @FR-ANA-002 @R1-Pilot @Must
    Scenario: Non-applicable filter is visibly identified
      Given a filter that is not applicable to a widget
      When the filter is applied
      Then the widget is visibly identified as not affected by the filter

    @FR-ANA-002 @R1-Pilot @Must
    Scenario: Saved view handles a changed binding
      Given a saved view whose binding has changed
      When the Analyst opens the saved view
      Then it uses its pinned definitions or displays a reviewed migration notice

    @FR-ANA-002 @R1-Pilot @Must
    Scenario: Reject leakage through filtering and totals
      Given partner A is selected
      When the summary totals are displayed
      Then they do not leak partner B data
      And no suppressed cells or hidden source counts are revealed

  Rule: FR-ANA-003 Actual target and baseline views
    As a Programme Manager, I want comparison views of actual, baseline and target that state direction, target version, period, scales and calculations, so that I can correctly judge whether performance is on track.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-ANA-003 @R1-Pilot @Must
    Scenario: Lower-is-better target shown correctly
      Given an indicator with a lower-is-better target of ten
      And an actual value of eight
      When the comparison widget is displayed
      Then it shows the correct status and declared deviation
      And it does not give an inverted success interpretation

    @FR-ANA-003 @R1-Pilot @Must
    Scenario: Labels, scales and overachievement are explicit
      Given a comparison widget bound to actual, baseline and a selected target version with direction and time semantic
      When it is displayed
      Then labels identify whether the target is original or revised and its applicable period
      And axis scales and percentage calculations are explicit
      And overachievement remains visible

    @FR-ANA-003 @R1-Pilot @Must
    Scenario: Reject comparing incompatible time semantics
      Given a cumulative actual curve and a monthly flow target
      When no approved conversion exists
      Then the comparison is blocked

    @FR-ANA-003 @R1-Pilot @Must
    Scenario: Reject an infinite trend from a zero baseline
      Given a baseline of zero
      When percentage change is calculated
      Then the result is undefined
      But no infinite trend is shown

  Rule: FR-ANA-004 Freshness and approval context
    As an Executive Director, I want every result widget and export to show whether it is live approved, provisional or snapshot and how fresh it is, so that I do not make decisions on stale or unapproved data.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-ANA-004 @R1-Pilot @Must
    Scenario: Widget shows approval state and freshness context
      Given a dashboard with result widgets
      When the Executive Director views it
      Then each widget is labelled live approved, provisional or snapshot
      And its context shows last source success, approval cutoff, calculation time and coverage

    @FR-ANA-004 @R1-Pilot @Must
    Scenario: Failed refresh remains stale in an export
      Given a source refresh has failed
      When the dashboard is exported
      Then the exported result is marked stale with the last valid data time
      And the export embeds a concise version of the material context

    @FR-ANA-004 @R1-Pilot @Must
    Scenario: Reject treating a successful fetch as fresh data
      Given the source refresh has failed
      When the dashboard fetch succeeds
      Then the source is not shown as fresh

    @FR-ANA-004 @R1-Pilot @Must
    Scenario: Reject unlabelled provisional content
      Given a dashboard where some widgets are approved and one is provisional
      When it is viewed or exported
      Then the provisional widget remains labelled provisional

  Rule: FR-ANA-001 Dashboard authoring
    As an Analyst, I want to author dashboards from permitted widgets and preview them on desktop, mobile and as an accessible table before publishing, so that every audience sees the same values with their quality context.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-ANA-001 @R2-Scale @Should
    Scenario: Build and preview a ten-widget dashboard at mobile width
      Given the Analyst has built a dashboard with ten permitted widgets, each declaring binding, view mode, period, dimensions and disclosure context
      When the Analyst opens the preview at mobile width
      Then each chart has a readable labelled tabular equivalent
      And the tabular values are identical to the chart values

    @FR-ANA-001 @R2-Scale @Should
    Scenario: Dashboard copy starts as a private draft
      Given an existing dashboard
      When the Analyst copies it
      Then the copy begins as a private draft

    @FR-ANA-001 @R2-Scale @Should
    Scenario: Reject layout changes that hide quality context
      Given a widget with required quality context
      When the Analyst changes the dashboard layout
      Then the required quality context cannot be hidden

    @FR-ANA-001 @R2-Scale @Should
    Scenario: Reject stale values for unavailable bindings
      Given a widget whose binding is unsupported or has been revoked
      When the dashboard is viewed
      Then the widget shows unavailable
      But no stale private value is displayed

  Rule: FR-ANA-007 Portfolio comparison
    As a Funder Portfolio Manager, I want to compare grantees only on compatible indicator definitions, periods and coverage thresholds, so that comparisons and rankings across my portfolio are fair and not misleading.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-ANA-007 @R2-Scale @Should
    Scenario: Compatible measures grouped and mismatches flagged
      Given the Funder Portfolio Manager selects indicator definitions, periods and coverage thresholds for a portfolio comparison
      When the comparison is displayed
      Then compatible measures are grouped
      And mismatches are flagged

    @FR-ANA-007 @R2-Scale @Should
    Scenario: Reviewed comparability required before a league table
      Given two completion rates with different eligible populations
      When the Funder Portfolio Manager requests a ranking
      Then an unqualified league table is presented only after comparability has been reviewed
      And otherwise the ranking carries a clear qualified comparison method

    @FR-ANA-007 @R2-Scale @Should
    Scenario: Reject a raw ranking of non-equivalent measures
      Given measures with different denominators, currencies or observation windows
      When a ranking is requested without an approved comparable set
      Then no raw ranking treating them as equivalent is produced

    @FR-ANA-007 @R2-Scale @Should
    Scenario: Reject exposing hidden portfolio members
      Given some portfolio members are outside the Funder Portfolio Manager's permissions
      When the results are permission filtered
      Then the visible scope is stated
      But hidden members are not exposed

  Rule: FR-ANA-008 Dashboard governance
    As a MEL Manager, I want dashboard publication to pin layout, bindings, audience and expiry and copies to carry no new data grants, so that shared dashboards only show data each audience is approved to see.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-ANA-008 @R2-Scale @Must
    Scenario: Publication pins dashboard configuration
      Given a dashboard ready for publication
      When the MEL Manager publishes it
      Then its layout, bindings, audience and expiry are pinned
      And any change of owner requires current authority

    @FR-ANA-008 @R2-Scale @Must
    Scenario: Copy to a funder workspace keeps restricted widgets unavailable
      Given an internal dashboard with restricted widgets
      When the MEL Manager copies it to a funder workspace
      Then the copy is a draft with no new data grants
      And the sharing preview calculates the recipient's view and identifies unavailable bindings
      And restricted widgets remain unavailable until explicitly bound to approved disclosed metrics

    @FR-ANA-008 @R2-Scale @Must
    Scenario: Reject public dashboards on live private queries
      Given a public dashboard
      When its widgets are bound
      Then they reference only disclosure-approved artifacts
      But not unrestricted live private queries

    @FR-ANA-008 @R2-Scale @Must
    Scenario: Reject continued publication after a sensitivity change
      Given a published dashboard
      When the sensitivity of one of its sources changes
      Then the affected publication is suspended until revalidated

  Rule: FR-ANA-005 Table analysis and pivots
    As an Analyst, I want to build pivot tables with compatible dimensions, measures and aggregations and correctly recalculated totals, so that I can analyse data without double counting or breaching disclosure rules.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-ANA-005 @R3-Ecosystem @Should
    Scenario: Pivot participants by a multiselect service type
      Given participants have a multiselect service type
      When the Analyst pivots participants by service type
      Then category totals may exceed the distinct grand total
      And that difference is explained
      And the grand total is recalculated from eligible source semantics rather than summed from displayed cells

    @FR-ANA-005 @R3-Ecosystem @Should
    Scenario: Large pivot runs as a cancellable job
      Given a pivot whose preview estimates a large cardinality
      When the Analyst runs it
      Then the request is routed to a cancellable job

    @FR-ANA-005 @R3-Ecosystem @Should
    Scenario: Reject breaching disclosure policy in a pivot
      Given a pivot that includes suppressed cells or nonadditive dimensions
      When the pivot is displayed
      Then the suppressed cells and nonadditive dimensions retain their disclosure policy

    @FR-ANA-005 @R3-Ecosystem @Should
    Scenario: Reject unsupported statistics
      Given the Analyst selects a statistic that is not supported
      When the pivot is requested
      Then the pivot is blocked or a distinctly labelled alternative is required

  Rule: FR-ANA-006 Geographic analysis
    As an Analyst, I want to configure maps with a boundary version, authorised layers, period, legend, missingness treatment and an equivalent table, so that I can publish geographic views without disclosing more location detail than allowed.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-ANA-006 @R3-Ecosystem @Should
    Scenario: Configure a map with an equivalent table
      Given the Analyst configures a map with a boundary version, authorised point or aggregate layer, period, legend and missingness treatment
      When the map is displayed
      Then an equivalent sortable table is available

    @FR-ANA-006 @R3-Ecosystem @Should
    Scenario: District view discloses no household coordinates
      Given only district aggregates are allowed for vulnerable participants
      When the Analyst publishes a district view and the permitted payload is inspected
      Then no household coordinate is disclosed

    @FR-ANA-006 @R3-Ecosystem @Should
    Scenario: Reject precise coordinates hidden in map outputs
      Given only district aggregates are allowed
      When tooltips, downloads or map request payloads are inspected
      Then no precise coordinates are present

    @FR-ANA-006 @R3-Ecosystem @Should
    Scenario: Reject a hidden boundary mismatch
      Given the data and the selected boundary version do not match
      When the map is displayed
      Then the boundary mismatch is visible

  Rule: FR-ANA-009 Alerts and thresholds
    As a Programme Manager, I want alerts that distinguish threshold breaches from missing or stale data and respect a cooldown, so that I respond to the right problem and am not misled by absent values.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-ANA-009 @R3-Ecosystem @Should
    Scenario: Missed monthly submission raises a missingness alert
      Given an alert declaring measure, condition, minimum coverage, freshness, evaluation cadence, recipients and cooldown
      When a monthly submission is missed
      Then a missingness alert is generated

    @FR-ANA-009 @R3-Ecosystem @Should
    Scenario: Approved performance decline raises a separate threshold alert
      Given the same alert configuration
      When an approved result shows a performance decline that meets the condition
      Then a threshold alert is generated separately from any missingness alert
      And the triggered alert records the exact evaluated result version

    @FR-ANA-009 @R3-Ecosystem @Should
    Scenario: Reject treating an absent value as zero
      Given a value is absent for the evaluation period
      When the alert is evaluated
      Then no deterioration alert is raised by treating the absent value as zero

    @FR-ANA-009 @R3-Ecosystem @Should
    Scenario: Reject separate alerts during cooldown
      Given an alert has triggered and is within its cooldown
      When the condition repeats
      Then one incident or digest is updated according to policy

  Rule: FR-ANA-010 External analytics access
    As a Data Steward, I want to give BI tools governed access to selected datasets through a revocable service identity, so that external analysis uses well-defined data and every external extract stays tracked.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-ANA-010 @R3-Ecosystem @Should
    Scenario: Create a governed BI connection
      Given the Data Steward selects governed datasets and field scope
      When a BI connection is created
      Then a service identity is issued
      And the external destination and reuse terms are recorded
      And the data package includes definitions, units, value states and freshness

    @FR-ANA-010 @R3-Ecosystem @Should
    Scenario: Revoked service identity cannot refresh
      Given a BI connection with a successful prior extract
      When the Data Steward revokes the BI service identity
      Then subsequent refresh fails
      And the register identifies the last successful external extract

    @FR-ANA-010 @R3-Ecosystem @Should
    Scenario: Reject refresh without current authority
      Given a refresh request whose credential or object authority is no longer current
      When the refresh runs
      Then no data is retrieved

    @FR-ANA-010 @R3-Ecosystem @Should
    Scenario: Reject claims of remote erasure or unrestricted access
      Given data has already been extracted to an external tool
      When access is revoked
      Then the external copies remain tracked as disclosures
      But they are not represented as remotely erased
      And no unrestricted database connection is implied
