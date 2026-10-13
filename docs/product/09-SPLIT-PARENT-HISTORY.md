# Imprana Commons retained split-parent history

These two source records are retained for traceability with original status Split. They are historical planning records, not additional active stories or native Linear issues. Their original fields remain in [import-plan.json](linear/import-plan.json).

<!-- imprana:historical:FR-AI-016 -->

As a MEL Manager, I want AI requests to reserve budget and show progress, timeout and cancellation, so that AI work stays within its limits and running out of AI budget never stops period close or reporting.

### Acceptance and rejection criteria
```gherkin
Scenario: Request reserves budget and shows progress
  Given an AI request
  When it starts
  Then its job class and usage are estimated and permitted budget is reserved
  And progress, timeout and cancellation are shown
  And ordinary question answering follows the BRD latency target

Scenario: Default timeouts keep partial drafts labelled
  Given the proposed default timeouts
  When a standard extraction runs beyond 15 minutes or a report draft runs beyond 20 minutes
  Then the job times out
  And any partial draft remains labelled incomplete

Scenario: Budget exhausted during close
  Given the AI budget is exhausted during period close
  When the MEL Manager continues close
  Then they can still approve data, calculate results and generate a non-AI report

Scenario: Reject lost input and uncontrolled continuation
  Given the AI budget is exhausted or a job is cancelled
  When the user submits or cancels an AI request
  Then a clear limit state is returned without losing user input
  And cancellation stops new model and tool calls where controllable
  And provider work already accepted is accounted separately
```

### Rejection summary
Reject if budget exhaustion loses user input or blocks approving data, calculating results or generating a non-AI report, partial drafts are not labelled incomplete, or cancellation lets new controllable model and tool calls continue.

### Original requirement
AI requests estimate job class and usage, reserve permitted budget and expose progress, timeout and cancellation. Proposed defaults: standard extraction timeout 15 minutes and report draft timeout 20 minutes; partial drafts remain labelled incomplete. Ordinary QA follows the BRD latency target. Budget exhaustion returns a clear limit state without losing user input. Cancellation stops new model and tool calls where controllable; provider work already accepted is accounted separately.

### Original acceptance
Exhaust the AI budget during close; the user can still approve data, calculate results and generate a non-AI report.

### Source and planning context
Source: Impact Platform ledger
Persona: MEL Manager
Release: R1 Pilot · Epic: AI capabilities
Release goal: RG-R1
Proposed strategic objectives: STR-01, STR-02, STR-03, STR-04
Priority: Must · Type: Functional
Original status: Split
Retained implementation snapshot (Built today): Absent
Acceptance is governed by docs/agile/WORKING-AGREEMENT.md; the implementation snapshot is separate from story acceptance.

### Refinement history
Retained split parent. Active replacement stories: FR-AI-016a, FR-AI-016b

Source commit: `8a1e405f0086033dfb25ad834689a08bfe9f1eea`
CSV data record: 14 · CSV record SHA-256: `8915bc56c0afc59cb7a8d309b5447a615e931c31ac082bb02a9c7f7b72fb280f`
Gherkin UTF-8 SHA-256: `392afb91caed2a21f3ffa47ce81a42957a2a2c0a375fbf81a647bb4e1cb0ef26`

<!-- imprana:historical:US-DX-01 -->

As an Executive Director, I want a guided, plain-language problem-discovery conversation, so that we can define our problems without hiring a consultant.

### Acceptance and rejection criteria
```gherkin
Scenario: Complete a guided problem-discovery conversation
  Given an Executive Director starting problem discovery
  When they answer the guided, plain-language questions
  Then the conversation completes in under 60 minutes

Scenario: Output lists prioritised problems with evidence
  Given a completed problem-discovery conversation
  When the Executive Director views the output
  Then it lists the organisation's problems in priority order
  And each problem shows its supporting evidence

Scenario: Reject an overlong or unsupported discovery
  Given a problem-discovery conversation
  When it takes 60 minutes or more, or a listed problem has no priority or no supporting evidence
  Then the discovery is not accepted as complete
```

### Rejection summary
Reject if discovery takes 60 minutes or more, or any listed problem lacks a priority or supporting evidence.

### Original acceptance
Completes in under 60 minutes; output lists prioritised problems with supporting evidence

### Source and planning context
Source: Imprana BRD
Persona: Executive Director
Release: R1 Pilot · Epic: Adoption: Diagnose
Release goal: RG-R1
Proposed strategic objectives: STR-02
Priority: Must · Type: Functional
Original status: Split
Retained implementation snapshot (Built today): Partial
Acceptance is governed by docs/agile/WORKING-AGREEMENT.md; the implementation snapshot is separate from story acceptance.

### Refinement history
Retained split parent. Active replacement stories: US-DX-01a, US-DX-01b

Source commit: `8a1e405f0086033dfb25ad834689a08bfe9f1eea`
CSV data record: 31 · CSV record SHA-256: `00b27e2ef1ae8ae4529ba245a5fe7d33575590182bb86521c3dbd3eb8acd644b`
Gherkin UTF-8 SHA-256: `8d8583df3ffc923e8dd8439057778cce93d170af4812f072455b1c9668220dd7`
