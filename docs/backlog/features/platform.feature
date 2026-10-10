# Imprana Commons backlog: Platform
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Platform

  Rule: US-PL-03 Production email provider
    As a Data Author, I want invitations and notices to arrive by real email, so that I don't miss them.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-PL-03 @R1-Pilot @Must
    Scenario: Invitations and notices arrive by real email
      Given a production email provider configured with SPF and DKIM
      When the platform sends a Data Author an invitation or notice
      Then the email arrives in their inbox

    @US-PL-03 @R1-Pilot @Must
    Scenario: Bounces handled and sending limits monitored
      Given email sent through the production provider
      When an email bounces
      Then the bounce is handled
      And sending against the provider's limits is monitored

    @US-PL-03 @R1-Pilot @Must
    Scenario: Reject unauthenticated or unmonitored sending
      Given the production environment
      When email is sent without SPF and DKIM, bounces are not handled, or sending limits are not monitored
      Then the email setup is not accepted for production
