# Imprana Commons backlog: Commercial and billing
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Commercial and billing

  Rule: US-CM-04 Keep data when sponsorship ends
    As an Executive Director, I want to keep all our data when sponsorship ends, so that we never lose our work.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @US-CM-04 @R1-Pilot @Must
    Scenario: Data kept read-only after sponsorship ends
      Given an organisation whose sponsorship has ended
      When the Executive Director opens the workspace within 90 days of the end date
      Then all the organisation's data is available read-only

    @US-CM-04 @R1-Pilot @Must
    Scenario: One-step conversion to a direct subscription
      Given an organisation whose sponsorship has ended
      When the Executive Director converts to a direct subscription
      Then the conversion completes in one step
      And all the organisation's existing data is available under the direct subscription

    @US-CM-04 @R1-Pilot @Must
    Scenario: Reject data loss when sponsorship ends
      Given an organisation whose sponsorship ended fewer than 90 days ago
      When any retention or clean-up process runs
      Then none of the organisation's data is deleted or made unavailable

  Rule: US-CM-05 Visible AI usage credits and limits
    As an Operations Head, I want to see AI usage credits and limits, so that there are no surprise costs.
    Release: R1 Pilot · Priority: Should · Built today: Partial

    @US-CM-05 @R1-Pilot @Should
    Scenario: See AI credit balance and usage by user
      Given an organisation with AI usage credits
      When the Operations Head opens the AI usage view
      Then the remaining credit balance and the limit are shown
      And usage is shown by user

    @US-CM-05 @R1-Pilot @Should
    Scenario: Alerts at 80% and 100% of the limit
      Given an organisation's AI usage is approaching its limit
      When usage reaches 80% of the limit
      Then the Operations Head is alerted
      And when usage reaches 100% of the limit the Operations Head is alerted again

    @US-CM-05 @R1-Pilot @Should
    Scenario: Reject a threshold crossed without an alert
      Given an organisation's AI usage has reached 80% or 100% of its limit
      When the Operations Head has received no alert for that threshold
      Then the usage alerting counts as failed

  Rule: US-CM-09 One contract and DPA for all deployed solutions
    As an Operations Head, I want one contract and data processing agreement for every solution deployed through the platform, so that we avoid separate procurement.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @US-CM-09 @R1-Pilot @Must
    Scenario: Partner terms flow down under the master agreement
      Given an organisation that has signed the master agreement
      When it deploys a partner's solution through the platform
      Then the partner's terms apply under the master agreement

    @US-CM-09 @R1-Pilot @Must
    Scenario: One data processing agreement per organisation
      Given an organisation with several solutions deployed through the platform
      When the Operations Head views its agreements
      Then a single data processing agreement covers all the deployed solutions

    @US-CM-09 @R1-Pilot @Must
    Scenario: Reject separate procurement
      Given an organisation that has signed the master agreement and its data processing agreement
      When another solution is deployed through the platform
      Then the organisation is not asked to sign a separate contract or a second data processing agreement

  Rule: US-CM-02 Funder-sponsored access for a cohort
    As a Funder Portfolio Manager, I want to sponsor access for a named cohort of grantees, so that they can use the platform at no cost to them.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @US-CM-02 @R2-Scale @Must
    Scenario: Funder Portfolio Manager sponsors a named cohort
      Given a Funder Portfolio Manager setting up sponsored access for a named cohort of grantees
      When they enrol the grantee organisations and set the duration and budget
      Then the sponsorship is saved with the enrolled organisations, duration and budget

    @US-CM-02 @R2-Scale @Must
    Scenario: Grantee gets access when it accepts
      Given a grantee organisation enrolled in the sponsored cohort
      When the grantee accepts the sponsorship
      Then the organisation gets access to the platform for the sponsored duration
      And the organisation is not charged for that access

    @US-CM-02 @R2-Scale @Must
    Scenario: Reject access before acceptance or without terms
      Given a grantee organisation enrolled in the sponsored cohort that has not accepted
      When anyone from that organisation tries to use the sponsored access
      Then access is not granted
      But a sponsorship with no duration or no budget cannot be saved

  Rule: US-CM-03 Combine sponsored and direct entitlements
    As an Executive Director, I want sponsored and direct entitlements to combine, so that support from several funders adds up.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @US-CM-03 @R2-Scale @Should
    Scenario: Sponsored and direct entitlements add up
      Given an organisation with a direct subscription and sponsorship from more than one funder
      When the Executive Director views the organisation's entitlements
      Then the entitlements from every source are shown combined
      And the source of each entitlement is visible

    @US-CM-03 @R2-Scale @Should
    Scenario: Reject duplicate charges
      Given an entitlement covered by both a sponsorship and the direct subscription
      When the organisation is invoiced
      Then the same entitlement is not charged twice
      And no entitlement is shown without its source

  Rule: US-CM-06 Fixed-fee service packages on the same invoice
    As an Operations Head, I want to buy fixed-fee service packages alongside the subscription, so that deployment support sits on one contract.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @US-CM-06 @R2-Scale @Must
    Scenario: Service packages listed with scope and price
      Given fixed-fee service packages are offered
      When the Operations Head views the service packages
      Then each package is listed with its scope and price

    @US-CM-06 @R2-Scale @Must
    Scenario: Package added to the subscription invoice
      Given an organisation with a subscription
      When the Operations Head buys a fixed-fee service package
      Then the package is added to the same invoice as the subscription

    @US-CM-06 @R2-Scale @Must
    Scenario: Reject a separate invoice or an unpriced package
      Given an organisation with a subscription
      When a service package is bought
      Then no separate invoice is raised for the package
      But a package without a stated scope or price is not offered

  Rule: US-CM-07 Partner revenue-share tracking
    As a Platform Operator, I want to track revenue sourced through each partner, so that revenue share is settled accurately.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @US-CM-07 @R2-Scale @Should
    Scenario: Monthly statement per partner
      Given revenue was sourced through a partner during a month
      When the monthly statements are produced
      Then a statement is produced for that partner showing the revenue sourced through it that month

    @US-CM-07 @R2-Scale @Should
    Scenario: Statement reconciled to invoices
      Given a partner's monthly statement
      When the Platform Operator reconciles it
      Then every amount on the statement matches the related invoices

    @US-CM-07 @R2-Scale @Should
    Scenario: Reject an unreconciled statement
      Given a partner statement whose amounts do not match the related invoices
      When the Platform Operator tries to settle the revenue share
      Then the statement is not used for settlement until it is reconciled

  Rule: US-CM-08 Local-currency invoices with GST
    As an Operations Head, I want invoices in local currency with the right taxes, so that we can pay and account for them easily.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @US-CM-08 @R2-Scale @Must
    Scenario: Invoice in INR with GST at launch
      Given an organisation invoiced in INR at launch
      When an invoice is issued
      Then the invoice is in INR
      And GST is applied and shown on the invoice

    @US-CM-08 @R2-Scale @Must
    Scenario: Other currencies added per market
      Given a new market has been added with its local currency
      When an invoice is issued to an organisation in that market
      Then the invoice is in that market's local currency

    @US-CM-08 @R2-Scale @Must
    Scenario: Reject an INR invoice without GST
      Given an organisation invoiced in INR
      When an invoice is issued without GST
      Then the invoice is not accepted
      And no invoice is issued in a currency whose market has not been added
