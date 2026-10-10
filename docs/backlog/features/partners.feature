# Imprana Commons backlog: Partners
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Partners

  Rule: US-PT-05 Standard partner terms under the master agreement
    As a Solution Partner Manager, I want standard terms that flow down under the master agreement, so that clients sign one contract.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @US-PT-05 @R1-Pilot @Must
    Scenario: Standard partner agreement
      Given a Solution Partner Manager whose solution is to be listed
      When they review the partner agreement
      Then it is the standard agreement covering data processing and service levels
      And it flows down under the master agreement

    @US-PT-05 @R1-Pilot @Must
    Scenario: Clients sign one contract
      Given an organisation deploying the partner's solution under the master agreement
      When the deployment is contracted
      Then the organisation signs no separate contract with the partner

    @US-PT-05 @R1-Pilot @Must
    Scenario: Reject incomplete partner terms
      Given a partner agreement
      When it does not cover data processing or service levels
      Then it is not accepted as the standard partner agreement

  Rule: US-PT-01 Solution partners apply to be listed
    As a Solution Partner Manager, I want to apply to list our solution, so that we reach qualified organisations.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @US-PT-01 @R2-Scale @Must
    Scenario: Apply to list a solution
      Given a Solution Partner Manager
      When they submit the application form for their solution
      Then the application is recorded for vetting

    @US-PT-01 @R2-Scale @Must
    Scenario: Vetted with a decision within 30 days
      Given a submitted application
      When it is vetted
      Then it is assessed against the published criteria
      And the Solution Partner Manager receives a decision within 30 days of submission

    @US-PT-01 @R2-Scale @Must
    Scenario: Reject listing without vetting or a late decision
      Given a submitted application
      When it has not passed vetting against the published criteria
      Then the solution is not listed
      But no application waits more than 30 days for a decision

  Rule: US-PT-02 Partners integrate once via APIs
    As a Solution Partner Manager, I want to integrate once through Imprana Commons APIs, so that we don't build per-client integrations.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @US-PT-02 @R2-Scale @Should
    Scenario: Read and write through the shared data model
      Given a Solution Partner Manager's integration built against the Imprana Commons APIs
      When it reads and writes data
      Then the data is read from and written to the shared data model

    @US-PT-02 @R2-Scale @Should
    Scenario: Test sandbox
      Given a Solution Partner Manager building an integration
      When they use the test sandbox
      Then they can test reads and writes without touching any organisation's live data

    @US-PT-02 @R2-Scale @Should
    Scenario: Reject per-client integration
      Given an integration built once against the Imprana Commons APIs
      When another organisation deploys the solution
      Then no client-specific integration is required

  Rule: US-PT-03 Qualified referrals with consented context
    As a Solution Partner Manager, I want qualified referrals with context, so that we can respond quickly.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @US-PT-03 @R2-Scale @Should
    Scenario: Qualified referral with a diagnosis summary
      Given an organisation that consents to share its diagnosis summary with a solution partner
      When a referral is sent to the Solution Partner Manager
      Then the referral includes the diagnosis summary

    @US-PT-03 @R2-Scale @Should
    Scenario: Reject sharing without consent
      Given an organisation that has not consented
      When a referral is made
      Then its diagnosis summary is not shared with the Solution Partner Manager

  Rule: US-PT-06 Annual partner review and delisting
    As a Platform Operator, I want to review partners regularly and delist those below standard, so that the catalogue stays trustworthy.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @US-PT-06 @R2-Scale @Must
    Scenario: Annual partner review
      Given a listed partner
      When a year has passed since its last review
      Then the Platform Operator reviews it

    @US-PT-06 @R2-Scale @Must
    Scenario: Delist a partner below standard with notice
      Given a partner found below standard in its review
      When the Platform Operator delists it
      Then organisations affected by the delisting are given notice

    @US-PT-06 @R2-Scale @Must
    Scenario: Reject delisting without notice
      Given a partner being delisted
      When affected organisations have not been given notice
      Then the delisting does not proceed
      And no listed partner goes more than a year without a review

  Rule: US-PT-04 Partners see outcomes of their deployments
    As a Solution Partner Manager, I want to see outcomes of our deployments, so that we can improve.
    Release: R3 Ecosystem · Priority: Could · Built today: Absent

    @US-PT-04 @R3-Ecosystem @Could
    Scenario: See outcomes per deployment
      Given deployments of the partner's solution
      When the Solution Partner Manager views outcomes
      Then adoption and ROI are shown for each deployment
      And the data is anonymised

    @US-PT-04 @R3-Ecosystem @Could
    Scenario: Reject identifiable outcome data
      Given outcomes for a deployment
      When the Solution Partner Manager views them
      Then no organisation can be identified from them
      And no outcomes are shown for other partners' deployments
