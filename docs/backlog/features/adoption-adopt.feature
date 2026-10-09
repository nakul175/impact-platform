# Imprana Commons backlog: Adoption: Adopt
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Adoption: Adopt

  Rule: US-AD-01 Role-based training per deployed solution
    As a Data Author, I want role-based training for each deployed solution, so that I learn only what I need.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-AD-01 @R1-Pilot @Must
    Scenario: Training modules for the user's role
      Given a deployed solution with training modules per role
      When a Data Author opens the training
      Then they see the modules for their role

    @US-AD-01 @R1-Pilot @Must
    Scenario: Completion tracked
      Given a Data Author taking a training module
      When they finish it
      Then their completion is recorded

    @US-AD-01 @R1-Pilot @Must
    Scenario: Reject training for other roles
      Given a Data Author
      When they open the training for a deployed solution
      Then they are not required to complete modules for other roles

  Rule: US-AD-02 Internal champions with guide and check-ins
    As an Executive Director, I want to appoint and support internal champions, so that adoption continues after the advisor steps back.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @US-AD-02 @R1-Pilot @Must
    Scenario: Appoint an internal champion
      Given an Executive Director
      When they appoint a colleague as a champion
      Then the colleague is given the champion role
      And they can open the champion guide

    @US-AD-02 @R1-Pilot @Must
    Scenario: Scheduled check-ins
      Given an appointed champion
      When the appointment is confirmed
      Then check-ins with the champion are scheduled

    @US-AD-02 @R1-Pilot @Must
    Scenario: Reject a champion without support
      Given a colleague appointed as a champion
      When they have no access to the guide or no scheduled check-ins
      Then the appointment is not complete

  Rule: US-AD-03 Short mobile lessons in local language
    As a Field Data Collector, I want short, mobile-friendly lessons in my language, so that I can learn on the go.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @US-AD-03 @R2-Scale @Should
    Scenario: Short lessons in my language on mobile
      Given a Field Data Collector on a mobile device
      When they open a lesson
      Then the lesson takes 5 minutes or less
      And it is in their language

    @US-AD-03 @R2-Scale @Should
    Scenario: Usable on low bandwidth
      Given a Field Data Collector on a low-bandwidth connection
      When they open and complete a lesson
      Then the lesson is usable

    @US-AD-03 @R2-Scale @Should
    Scenario: Reject long or bandwidth-heavy lessons
      Given a lesson
      When it takes more than 5 minutes or cannot be used on low bandwidth
      Then it is not published to Field Data Collectors

  Rule: US-AD-04 Nudges when usage drops
    As a Programme Manager, I want colleagues nudged when their usage drops, so that new habits form.
    Release: R2 Scale · Priority: Could · Built today: Absent

    @US-AD-04 @R2-Scale @Could
    Scenario: Configure nudge rules
      Given a Programme Manager
      When they configure a nudge rule for when usage drops
      Then the rule is saved

    @US-AD-04 @R2-Scale @Could
    Scenario: Colleague nudged when usage drops
      Given a nudge rule
      When a colleague's usage drops and matches the rule
      Then the colleague receives a nudge

    @US-AD-04 @R2-Scale @Could
    Scenario: Reject nudging a user who opted out
      Given a colleague who has opted out of nudges
      When their usage drops and matches a nudge rule
      Then they receive no nudge
