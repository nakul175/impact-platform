# Imprana Commons backlog: Adoption: Deploy
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Adoption: Deploy

  Rule: US-DP-02 Deploy inside existing workflows
    As a Data Author, I want the new solution inside our existing workflow, so that I don't have to learn another separate tool.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @US-DP-02 @R1-Pilot @Must
    Scenario: Deployment plan names the workflow touchpoints
      Given a deployment plan for a new solution
      When the Data Author views it
      Then it names the touchpoints in the existing workflow where the solution is used

    @US-DP-02 @R1-Pilot @Must
    Scenario: Reject duplicate data entry
      Given a solution deployed inside the existing workflow
      When a Data Author records data in the existing workflow
      Then they are not asked to enter the same data again in the new solution
      And a deployment plan that names no workflow touchpoints is not accepted

  Rule: US-DP-03 Deployment plan with owners, milestones, acceptance
    As an Operations Head, I want a deployment plan with owners, milestones and acceptance criteria, so that rollout is accountable.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-DP-03 @R1-Pilot @Must
    Scenario: Generate a deployment plan from a template
      Given a solution to deploy
      When the Operations Head generates a deployment plan
      Then the plan is created from a template with owners, milestones and acceptance criteria

    @US-DP-03 @R1-Pilot @Must
    Scenario: Track progress in the platform
      Given a deployment plan
      When an owner updates a milestone
      Then the progress is tracked in the platform

    @US-DP-03 @R1-Pilot @Must
    Scenario: Reject an unaccountable plan
      Given a deployment plan
      When a milestone has no owner or no acceptance criteria
      Then the plan is not accepted as complete

  Rule: US-DP-04 Reusable workflow templates
    As a MEL Manager, I want reusable workflow templates for common use cases, so that setup is faster.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @US-DP-04 @R2-Scale @Should
    Scenario: Choose from reusable workflow templates
      Given a MEL Manager setting up a workflow
      When they browse the workflow templates
      Then at least 5 templates are available
      And one of them covers donor reporting

    @US-DP-04 @R2-Scale @Should
    Scenario: Reject too few templates or no donor reporting
      Given the workflow template library
      When fewer than 5 templates are available or none covers donor reporting
      Then the template library is not accepted
