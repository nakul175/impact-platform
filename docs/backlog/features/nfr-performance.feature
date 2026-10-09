# Imprana Commons backlog: NFR performance
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR performance

  Rule: VF-PER-001 Interactive response
    As a Data Author, I want ordinary reads, list views, saves and approvals to respond quickly under normal load, so that I can work without waiting.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @VF-PER-001 @R1-Pilot @Must
    Scenario: Interactive actions meet response targets
      Given the standard workload with concurrent background work
      And action start, usable response and durable confirmation are instrumented separately for reads, 100-row lists, saves and approvals
      When the complete peak and soak profile is run
      Then each action class completes at p95 within 2 seconds and p99 within 5 seconds from user action to usable confirmed response
      And per-tenant p95, p99, timeout and error counts are reported

    @VF-PER-001 @R1-Pilot @Must
    Scenario: Long jobs are excluded only when asynchronous
      Given a long job
      When it is excluded from the interactive targets
      Then it is explicitly routed asynchronously

    @VF-PER-001 @R1-Pilot @Must
    Scenario: Reject any action class or tenant cohort outside its bound
      Given the measured results
      When any action class or material tenant cohort exceeds p95 2 seconds or p99 5 seconds
      Then the verification fails
      But fast reads are not combined with slow approvals to hide a failure

  Rule: VF-PER-006 Data freshness
    As a Programme Manager, I want live dashboards to show newly approved results quickly, with collection and review delays shown separately, so that I can trust I am seeing current figures.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @VF-PER-006 @R1-Pilot @Must
    Scenario: Dashboard reflects a new approved result within 60 seconds at p95
      Given a submission has been approved
      And its bounded calculation has finished
      When the Programme Manager views the live dashboard
      Then the new approved result is shown within 60 seconds at p95 of calculation completion
      And version identifiers prove the new result is the one displayed

    @VF-PER-006 @R1-Pilot @Must
    Scenario: Collection and review delays are shown separately
      Given source receipt, validation, approval and calculation completion times are recorded
      When data freshness is reported
      Then external source cadence and human review delay are displayed separately from the 60-second propagation metric

    @VF-PER-006 @R1-Pilot @Must
    Scenario: Reject hidden delays or slow propagation
      Given a data freshness measurement
      When collection or human review delay is hidden inside the propagation metric
      Then the measurement is rejected
      And propagation taking longer than 60 seconds at p95 from calculation completion fails the target

  Rule: VF-PER-002 Dashboard response
    As an Analyst, I want standard dashboards to become usable quickly while showing freshness and calculation status, so that I can explore results without waiting or misreading stale data.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @VF-PER-002 @R2-Scale @Should
    Scenario: Ten-widget dashboard meets response targets
      Given a standard dashboard of up to ten widgets with approved bounded calculations
      And imports and report jobs are running
      When initial opening, filter change and drill down are measured with cold and warm caches as separate populations
      Then the dashboard becomes usable at p95 within 5 seconds and p99 within 10 seconds
      And cached and uncached results are reported separately
      And data bindings, freshness and calculation status remain visible and correct

    @VF-PER-002 @R2-Scale @Should
    Scenario: Reject placeholders as usable completion
      Given a widget showing a placeholder or partially loaded chart
      When completion is timed
      Then it is not counted as usable completion
      And failed widgets are recorded rather than excluded from the samples

    @VF-PER-002 @R2-Scale @Should
    Scenario: Reject dashboards outside the bound
      Given the measured results
      When p95 exceeds 5 seconds or p99 exceeds 10 seconds
      Then the verification fails

  Rule: VF-PER-003 Search response
    As a Data Author, I want searches to return the first page of permitted results quickly without revealing restricted information, so that I can find what I need safely.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @VF-PER-003 @R2-Scale @Should
    Scenario: Search meets response targets
      Given a synthetic corpus under the standard profile
      When permission-filtered metadata and indexed document searches retrieve the first 50 permitted results
      Then results return at p95 within 3 seconds and p99 within 8 seconds
      And timing covers the complete first usable page including policy filtering

    @VF-PER-003 @R2-Scale @Should
    Scenario: Restricted, multilingual and empty searches stay confidential
      Given restricted, multilingual and empty-result queries
      When counts, suggestions and snippets are inspected
      Then no hidden marker appears

    @VF-PER-003 @R2-Scale @Should
    Scenario: Reject permission leakage regardless of latency
      Given a search that meets its latency targets
      When any count, suggestion or snippet reveals a hidden marker
      Then the verification fails

    @VF-PER-003 @R2-Scale @Should
    Scenario: Reject searches outside the bound
      Given the measured results including policy filtering
      When p95 exceeds 3 seconds or p99 exceeds 8 seconds
      Then the verification fails

  Rule: VF-PER-004 Import and recalculation throughput
    As a Data Steward, I want large imports and the recalculations they trigger to complete quickly and predictably, so that new data is validated, ingested and reflected in indicators without long waits.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @VF-PER-004 @R2-Scale @Should
    Scenario: Standard import completes validation and ingestion within 10 minutes at p95
      Given a standard import of 100000 rows and 30 simple fields with configured deterministic checks
      And the import contains updates, duplicates and rejected rows
      When the import is run repeatedly
      Then validation and ingestion complete within 10 minutes at p95
      And human approval and external source transfer time are excluded from the measurement

    @VF-PER-004 @R2-Scale @Should
    Scenario: Resulting recalculation completes within 5 additional minutes at p95
      Given eligible ingestion of the standard import has finished
      When the resulting bounded 1000-indicator recalculation runs
      Then it completes within 5 additional minutes at p95
      And the duration of each stage is recorded separately

    @VF-PER-004 @R2-Scale @Should
    Scenario: Reject a throughput result that excludes queuing or retries
      Given a standard 100000-row, 30-field import run
      When throughput results are reported
      Then human approval and external transfer are reported separately as exclusions
      But validation, internal queuing and ordinary retries are not excluded from the measured time
      And the target fails if measured validation and ingestion exceed 10 minutes at p95

  Rule: VF-PER-005 Export and report generation
    As an Analyst, I want large data exports and reports to generate quickly with visible progress and the option to cancel, so that I can produce outputs without waiting blindly or tying up work.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @VF-PER-005 @R2-Scale @Should
    Scenario: Standard export or report completes within 5 minutes at p95
      Given the service is under mixed load
      When an Analyst requests a 100000-row data export or a 50-page report with up to 20 charts
      Then the finished artifact is available within 5 minutes at p95
      And its content is validated as complete

    @VF-PER-005 @R2-Scale @Should
    Scenario: Job acknowledges receipt, shows progress and can be cancelled
      Given an Analyst has submitted an export or report job
      When the job is received
      Then receipt is acknowledged within 2 seconds
      And progress is visible while the job runs
      And the Analyst can cancel the job at any stage

    @VF-PER-005 @R2-Scale @Should
    Scenario: Larger jobs show estimated class and explicit limits
      Given a job larger than the standard export or report
      When the Analyst requests it
      Then the estimated class and explicit limits are shown

    @VF-PER-005 @R2-Scale @Should
    Scenario: Reject a ready link to an incomplete artifact
      Given an export or report job whose artifact is incomplete
      When the job status is shown
      Then no ready link is offered
      And a ready link to an incomplete artifact counts as a failure

    @VF-PER-005 @R2-Scale @Should
    Scenario: Reject download after permission revocation
      Given an export completed within the performance targets
      And the Analyst's permission is revoked before download
      When the Analyst tries to retrieve the artifact
      Then retrieval is refused

  Rule: VF-PER-007 AI responsiveness
    As a MEL Manager, I want AI evidence questions to be acknowledged quickly and answered within predictable times, with long tasks run as visible jobs I can cancel, so that I can rely on the assistant during interactive work.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @VF-PER-007 @R2-Scale @Should
    Scenario: Interactive evidence question meets response targets
      Given a representative supported question set for a use case and model configuration
      When the MEL Manager asks an interactive evidence question
      Then the question is acknowledged within 2 seconds
      And a first useful response arrives within 15 seconds at p95
      And a completed standard answer arrives within 45 seconds at p95, including policy checks and numeric tools

    @VF-PER-007 @R2-Scale @Should
    Scenario: Long tasks run as visible asynchronous jobs
      Given a long extraction or reporting task
      When the MEL Manager starts it
      Then it runs as a visible asynchronous job
      And the job can be cancelled and has a declared timeout

    @VF-PER-007 @R2-Scale @Should
    Scenario: Reject a generic waiting message as a useful response
      Given an interactive evidence question is in progress
      When only a generic waiting message is shown
      Then it does not count as a first useful response

    @VF-PER-007 @R2-Scale @Should
    Scenario: Reject losing the question or an unapproved fallback on provider timeout
      Given the AI provider times out on a question
      When the failure is handled
      Then the question is preserved and the manual route is offered
      But no unapproved fallback is used
