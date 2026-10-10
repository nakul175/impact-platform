# Imprana Commons backlog: Finance
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Finance

  Rule: FR-FIN-001 Funding and grant context
    As a Finance Officer, I want to record each funding agreement with its funder, programme links, amount, currency, dates, amendments and reporting obligations, so that grant context is complete while each funder sees only what they are approved to see.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-FIN-001 @R2-Scale @Should
    Scenario: Record a funding agreement
      Given a new funding agreement
      When the Finance Officer records it
      Then it captures agreement identity, funder, programme links, amount, currency, dates, amendments and reporting obligations
      And confidential clauses and attachments use separate field permissions
      And any subgrant relationship preserves its own agreement version

    @FR-FIN-001 @R2-Scale @Should
    Scenario: Two donors linked to one project see only their own view
      Given two donors are linked to one project
      When each donor's external user accesses the project
      Then each sees only their approved report view
      And neither has automatic access to the other's agreement

    @FR-FIN-001 @R2-Scale @Should
    Scenario: Reject access or ownership created by a funder relation
      Given a funder is linked to a project
      When the relation is saved
      Then no user grant or ownership share in outcomes is created

    @FR-FIN-001 @R2-Scale @Should
    Scenario: Reject amount changes without amendment history
      Given a recorded funding agreement
      When its amount is changed without an amendment
      Then the change is refused

  Rule: FR-FIN-004 Currency treatment
    As a Finance Officer, I want currency conversions to record source and reporting currency, rate, rate source, effective date and direction and to be pinned in report snapshots, so that historical publications never change when rates change.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-FIN-004 @R2-Scale @Must
    Scenario: Convert and pin a rate
      Given a transaction of USD 100 and a rate of 83 INR per USD
      When the Finance Officer converts it to INR
      Then the converted value is INR 8300
      And the report snapshot pins the rate, source, effective date and rate direction
      And the original transaction remains in USD

    @FR-FIN-004 @R2-Scale @Must
    Scenario: A later rate creates a new view
      Given a published report shows INR 8300 converted at 83
      When a later rate of 84 is applied
      Then a new analytical view or restatement is created
      And the published historical value remains 8300

    @FR-FIN-004 @R2-Scale @Must
    Scenario: Reject silent current-rate conversion of history
      Given a historical publication with pinned conversion values
      When the current rate changes
      Then the publication is not silently converted at the current rate

    @FR-FIN-004 @R2-Scale @Must
    Scenario: Reject zero or parity for missing rates
      Given no rate exists for the required currency pair and date
      When conversion is requested
      Then the converted value is unavailable
      But it is not shown as zero or assumed parity

  Rule: FR-FIN-008 Finance permissions and audit
    As a Finance Officer, I want separate permission checks for financial lines, attachments, approval and export with audited access, so that others can see approved summaries while transaction details and confidential terms stay restricted.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-FIN-008 @R2-Scale @Must
    Scenario: Programme viewer sees the approved summary
      Given a published budget total on a programme dashboard
      When a programme viewer opens it
      Then the approved summary disclosure is visible
      And the audit record identifies the financial read without logging secret values

    @FR-FIN-008 @R2-Scale @Must
    Scenario: Reject retrieving restricted financial detail
      Given a programme viewer who can see a published budget total
      When they attempt to retrieve transaction rows or confidential clauses through drill down, API or export
      Then the request is refused

    @FR-FIN-008 @R2-Scale @Must
    Scenario: Reject self-approval of a budget revision
      Given a finance approver who authored a budget revision
      When they attempt to approve it
      Then the approval is blocked

    @FR-FIN-008 @R2-Scale @Must
    Scenario: Reject ledger access through connection administration
      Given a user with connection administration rights only
      When they attempt to access ledger fields
      Then access to every ledger field is not granted

  Rule: FR-FIN-002 Budget planning
    As a Finance Officer, I want versioned budgets by activity, category, partner and period with an approval route, so that revisions can be compared and approved without altering actual spending or previously reported variance.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-FIN-002 @R3-Ecosystem @Should
    Scenario: Raise an approved budget
      Given an approved budget of 100
      When the Finance Officer revises it to 120 and the revision is approved
      Then the original comparison remains available
      And imported actual spending stays unchanged

    @FR-FIN-002 @R3-Ecosystem @Should
    Scenario: Draft revisions compare against baselines
      Given a draft budget revision with lines by activity, category, partner and period with currency
      When the Finance Officer reviews it
      Then it is compared against the original and current baseline
      And approval pins the budget and its rate assumptions

    @FR-FIN-002 @R3-Ecosystem @Should
    Scenario: Reject budget changes that alter actuals or history
      Given an approved budget with imported actual expenditure and previously reported variance
      When the budget is changed
      Then transaction amounts are not altered
      And historically reported variance is not altered

  Rule: FR-FIN-003 Expenditure ingestion
    As a Finance Officer, I want expenditure imported with stable transaction keys, control totals and explicit correction handling, so that repeated or amended files never double count spending.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-FIN-003 @R3-Ecosystem @Should
    Scenario: Import an amended transaction file twice
      Given an amended transaction file
      When the Finance Officer imports it twice
      Then only the intended corrected expenditure balance contributes to analysis
      And unchanged records are reconciled rather than duplicated

    @FR-FIN-003 @R3-Ecosystem @Should
    Scenario: Mapping validates control totals and adjustments
      Given an expenditure file with source transaction key, posting and event dates, amount, currency, category and funding allocation
      When it is mapped
      Then control totals and adjustment semantics are validated
      And reversals and replacements are treated as separate transaction semantics

    @FR-FIN-003 @R3-Ecosystem @Should
    Scenario: Reject counting the same expense again
      Given a file has already been imported
      When the same file is uploaded again
      Then the same expense is not counted again

    @FR-FIN-003 @R3-Ecosystem @Should
    Scenario: Reject approval of unbalanced source totals
      Given a source file whose totals do not balance
      When approval is requested
      Then approval is blocked unless an explicit permitted exception is recorded

  Rule: FR-FIN-005 Variance and forecast
    As a Finance Officer, I want variance views showing remaining budget with a labelled sign convention and forecasts kept separate from actuals, so that I can report the spending position and expected overrun accurately.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-FIN-005 @R3-Ecosystem @Should
    Scenario: Show unspent budget and forecast overrun as separate facts
      Given a budget of 100, recorded spending of 60 and a forecast total of 110
      When the Finance Officer opens the variance view
      Then it shows 40 currently unspent
      And it shows a forecast overrun of ten as a separate fact
      And the sign convention is labelled

    @FR-FIN-005 @R3-Ecosystem @Should
    Scenario: Forecast assumptions recorded separately
      Given a variance view with a selected budget version, actual cutoff, commitments and forecast method
      When a forecast is saved
      Then its assumptions and author or method version are recorded separately from actuals

    @FR-FIN-005 @R3-Ecosystem @Should
    Scenario: Reject treating missing spending as underspend
      Given spending data is missing for a period
      When variance is calculated
      Then the missing data is not shown as underspend

    @FR-FIN-005 @R3-Ecosystem @Should
    Scenario: Reject forecasts entering actual expenditure
      Given a forecast exists
      When actual expenditure is displayed or reported
      Then the forecast does not enter the actual expenditure series
      And it does not imply programme impact success

  Rule: FR-FIN-006 Shared costs and allocations
    As a Finance Officer, I want to allocate shared costs to projects or donors using versioned rules with stated weights and rounding, so that allocated amounts reconcile to the source cost and are never charged twice.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-FIN-006 @R3-Ecosystem @Should
    Scenario: Allocate 100 at 60 and 40 percent
      Given a shared cost of 100 and an allocation rule of 60 and 40 percent
      When the Finance Officer previews and approves the allocation
      Then the two outputs sum to 100
      And the approved rule is fixed for the relevant snapshot

    @FR-FIN-006 @R3-Ecosystem @Should
    Scenario: Rounding remainder assigned deterministically
      Given an allocation that leaves a residual rounding unit
      When the allocation is previewed
      Then the remainder is reconciled and assigned by a deterministic stated rule

    @FR-FIN-006 @R3-Ecosystem @Should
    Scenario: Reject weights that do not reconcile
      Given an allocation rule whose weights do not reconcile to the declared total
      When the Finance Officer attempts to approve it
      Then approval is refused

    @FR-FIN-006 @R3-Ecosystem @Should
    Scenario: Reject repeated or double allocation
      Given an allocation has been made for an imported cost
      When the same import is repeated
      Then no additional allocation is created
      And no cost is double charged across overlapping views

  Rule: FR-FIN-007 Cost effectiveness
    As a Finance Officer, I want to calculate cost effectiveness from a defined cost scope, currency and rate basis, eligible outcome denominator, matched period and exclusions, so that cost-per-outcome figures are reproducible and their limitations are clear.
    Release: Later · Priority: Could · Built today: Absent

    @FR-FIN-007 @Later @Could
    Scenario: Calculate cost per participant
      Given an approved cost of 900 and 180 unique participants
      When the Finance Officer calculates cost effectiveness
      Then the cost per participant is five
      And shared-cost exclusions are explicitly listed
      And the ratio is returned with its limitations and source lineage

    @FR-FIN-007 @Later @Could
    Scenario: Reject a zero or incompatible denominator
      Given a denominator that is zero or incompatible
      When cost effectiveness is calculated
      Then the result is undefined

    @FR-FIN-007 @Later @Could
    Scenario: Reject unauthorised deduplication and causal labelling
      Given the denominator is unique participants
      When deduplication has not been authorised
      Then the unique participant count is not used
      And the ratio is never automatically labelled as causal return on investment
