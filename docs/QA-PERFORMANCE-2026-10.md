# QA 2026-10 — performance measurement harness

Build 0.25.0 (no version change) · schema 27 (no migration) · branch `qa/2026-10-performance` from `integration/0.25` (645e825) · measured 1 October 2026.

This pass adds a reproducible way to measure the platform's latency and records one run. It is measurement, not a performance claim: the run is a single sample on a shared, contended 2-CPU sandbox with a small synthetic workload, and the FSD's "standard workload", peak and soak profiles are not defined in rows or users anywhere in the specification, so no requirement below is accepted.

## Delivered

- `scripts/perf.py` and `make perf` (`PERF_ARGS="--scale sandbox --recreate"`). It needs `IMPACT_FIXTURE_DSN` (superuser) to a disposable `impact_test_<x>` database, like `make native`; `--recreate` drops and creates that database (it refuses any other name). It calls `scripts/run.py test --native --perf`, which provisions the four login roles, migrates as `impact_migrator`, starts the API on the provisioned logins with `IMPACT_REQUIRE_UNPRIVILEGED_DB=1` and runs `qualification/perf_harness.py` with `IMPACT_PERF=1`. `--perf` keeps the JUnit file in the run directory and writes no qualification evidence, so `native-application-tests.xml` and `native-qualification.json` are untouched. The harness file does not match `test_*.py` and skips without `IMPACT_PERF=1`, so no suite collects it and no recorded count changes.
- `qualification/perf_harness.py`: seeds the workload **through the governed API only** (no direct inserts) and times every request client-side (loopback HTTP wall time; no browser rendering) with per-actor RS256 bearer tokens minted as `qualification/conftest.py` does. Concurrency is an `httpx.AsyncClient` with a semaphore. Errors are counted per class and never dropped.
- `qualification/perf_support.py` (pure): workload scales, deterministic value generators (seeded `random.Random`), nearest-rank percentiles, summaries, the FSD target table and the verdict rule, and the markdown summary. `qualification/test_perf_unit.py` (6 tests, added to `make unit`) checks the statistics, the verdict rule and seed determinism.
- Evidence: `docs/evidence/performance-2026-10-01.json` (hardware, PostgreSQL version and settings, workload, per-scenario wall time and load average, every class summary and every raw sample in ms) and `docs/evidence/performance-2026-10-01.md` (generated table).

## Workload (scale `sandbox`, seed 20261001, concurrency 4)

All data is synthetic. Values come from the seed; identifiers are random UUIDs (they do not affect timing).

| Step | What is created / measured |
|---|---|
| seed (concurrency 1) | 3 programmes x 10 PERCENTAGE/POOLED_RATIO indicators, each with an independently approved definition and a 2-obligation plan; 60 ratio observations created, submitted and independently approved |
| calculate + cold dashboard | 30 provisional calculations; first dashboard read per programme (10 cards each) |
| interactive reads (concurrency 4) | 200 each of `GET observations?limit=100`, `GET programmes?limit=100`, `GET indicator-instances/{id}`; 50 warm dashboard reads |
| import (maximum bounded batch) | one 500-row CSV (`MAX_ROWS = MAX_OBSERVATIONS = 500`): create, preview, commit; tenant B reads continuously |
| approve imported (concurrency 4) | 500 independent approvals of the imported observations (GET workflow + POST approve); tenant B reads continuously |
| large calculation | one indicator with the maximum 500-obligation plan; 500 observations created, submitted and approved at concurrency 4; calculated 5 times (51,751 pooled denominator) |
| freshness | 20 x: new approved source, recalculation, poll the dashboard until the card shows the new `result_revision` |
| period close | 4 closes (3 x 10 indicators, 1 x 500 sources): request (preview + workflow) and independent approval (lock) |
| report export | 3 approved fixture report packages x PDF/XLSX/DOCX: request acknowledgement, then in-process worker render (no queue wait) |

Hardware and environment: 2 vCPU x86_64, 7.8 GiB RAM, kernel 6.18; PostgreSQL 16.13 single node on loopback, default settings (`shared_buffers` 128 MB, `fsync` and `synchronous_commit` on), no pooler; one uvicorn process; Python 3.12. Load average rose from 1.7 to 4.1 during the run: **two other engineers' suites shared the same 2 CPUs**, so absolute numbers include unknown contention.

## Results against the FSD targets

Verdict rule (`perf_support.verdict`): NOT MET if any error or the p95/p99 bound is exceeded; MET only with no errors, within bounds and at least 20 samples; otherwise NOT MEASURED. A MET class is not an accepted requirement (see Limits).

| Class | Requirement / bound | n | errors | p50 ms | p95 ms | p99 ms | Verdict |
|---|---|---|---|---|---|---|---|
| read.record (record GET) | VF-PER-001 p95 2 s / p99 5 s | 2020 | 0 | 66.9 | 97.5 | 111.8 | MET (sandbox) |
| read.list100 (100-row lists) | VF-PER-001 p95 2 s / p99 5 s | 400 | 0 | 85.2 | 112.7 | 125.8 | MET (sandbox) |
| write.save (create, submit, activate) | VF-PER-001 p95 2 s / p99 5 s | 1358 | 0 | 123.4 | 169.0 | 190.1 | MET (sandbox) |
| write.approval (independent approval) | VF-PER-001 p95 2 s / p99 5 s | 1142 | 0 | 143.2 | 192.0 | 217.8 | MET (sandbox) |
| import.commit, 500 rows (synchronous request) | VF-PER-001 if treated as a save; VF-PER-004 | 1 | 0 | 14,388 | — | — | NOT MET as an interactive save; NOT MEASURED for VF-PER-004 |
| dashboard.warm (10 cards, concurrency 4) | VF-PER-002 p95 5 s / p99 10 s | 50 | 0 | 192.8 | 242.0 | 264.9 | MET (sandbox) |
| dashboard.cold (first read after calculation) | VF-PER-002 | 3 | 0 | 71.2 | 74.7 | 74.7 | NOT MEASURED (3 samples; no cache exists, so cold/warm differ only by connection and buffer state) |
| freshness.propagation (calculation done → dashboard shows new revision) | VF-PER-006 p95 60 s | 20 | 0 | 62.6 | 71.5 | 78.1 | MET (sandbox) |
| export.acknowledge | VF-PER-005 acknowledge within 2 s | 9 | 0 | 46.7 | 81.9 | 81.9 | NOT MEASURED (9 samples) |
| export.render (fixture package, per format) | VF-PER-005 p95 5 min for 100,000 rows / 50 pages with 20 charts | 9 | 0 | 49.4 | 142.8 | 142.8 | NOT MEASURED (target workload cannot be produced: no data export, no charts) |
| period.close.request / approve | none stated | 4 / 4 | 0 | 164.9 / 139.5 | 247.7 / 153.0 | — | raw only |
| calculate.indicator / calculate.large (500 sources) | VF-PER-004 recalculation of 1000 indicators | 81 / 5 | 0 | 50.6 / 182.5 | 177.5 / 201.4 | — | NOT MEASURED |
| tenant B list read: idle / during import / during approvals | VF-CAP-002 | 40 / 368 / 385 | 0 | 30.8 / 40.7 / 79.5 | 37.1 / 53.2 / 103.0 | 39.5 / 73.9 / 125.9 | NOT MEASURED (one probe, see below) |

Observations (confidence in brackets):

- **The synchronous 500-row import commit takes about 14 s** (high: one sample, but 29 ms per produced observation agrees with the smoke run's 1.3 s for 50 rows). The commit runs inside one request and one transaction under tenant A's advisory lock, writing each observation and its review workflow (revision, projection, audit, outbox, receipt). It is not routed asynchronously, so under VF-PER-001's wording it is an interactive save outside its bound, and every other tenant A write waits behind it. Linear extrapolation to VF-PER-004's 100,000 rows gives about 48 minutes against a 10-minute bound — but the batch is bounded at 500, so VF-PER-004 is not measurable at all in this build. This is a design limit, not an isolated defect: no N+1 query or missing index was found (the per-row cost is the governed write itself), so no product code was changed.
- **Tenant B kept its latency during tenant A's import** (medium): p95 53 ms against 37 ms idle. During the 500 concurrent approvals it rose to 103 ms, which is CPU sharing on 2 cores rather than lock interference (tenants share no advisory lock). This is one probe, not VF-CAP-002's admission, queueing and burst-recovery qualification.
- **Freshness is bounded by one dashboard read** (high): dashboards are computed on read with no cache, so the new provisional revision is visible on the first poll after the calculation returns. The collection and human-review delays VF-PER-006 asks to expose separately were not recorded.
- Warm dashboard p50 (193 ms) is higher than cold (71 ms) because warm reads ran at concurrency 4 and cold reads at 1 (high).

## Limits

- One run, 2 shared vCPUs under load from other suites, loopback only, single API process, default PostgreSQL settings, no TLS, no proxy, no pooler: **not representative of production hardware** (the droplet) and not a capacity statement.
- The FSD "standard workload", "peak and soak profile" and "material tenant cohort" are not quantified; this workload is a few thousand objects in one tenant (plus fixture tenant B). No soak, no peak ramp, no per-tenant cohort report, no timeout budget, no concurrent background imports or report jobs during the interactive read phase.
- Times are server round trips measured by the client, not "user action to usable confirmed response" in a browser (VF-PER-001) or a fully rendered dashboard (VF-PER-002); filter change and drill-down were not measured.
- Report export render excludes queue wait (the worker drains immediately in-process) and covers only the small fixture package; no 100,000-row data export exists; cancellation and progress were not timed.
- Search (VF-PER-003), AI (VF-PER-007) and object limits (VF-CAP-001) are out of scope.

## Reproduce

```
# a private UTF8 PostgreSQL 16 cluster, e.g. initdb -E UTF8 under /var/lib/postgresql/<name>
export IMPACT_FIXTURE_DSN=postgresql://postgres:<pw>@127.0.0.1:<port>/impact_test_perf
IMPACT_PORT=8471 make perf PERF_ARGS="--scale sandbox --recreate"     # ~4 minutes on 2 CPUs
.venv/bin/python scripts/perf.py --scale smoke --recreate --output /tmp/perf-smoke.json   # ~40 s
.venv/bin/python -m pytest qualification/test_perf_unit.py
```

## Integration notes

Proposed requirement statuses (for the integrator; nothing promoted in this branch):

| Requirement | Proposed | Exact evidence |
|---|---|---|
| VF-PER-001 | PENDING → PARTIAL (bounded subset measured: record reads, 100-row lists, saves, approvals within bounds at sandbox scale; failure rule not exercised under peak/soak; the synchronous 500-row import commit, ~14 s, is outside the bound if counted as a save) | `docs/evidence/performance-2026-10-01.json` classes `read.record`, `read.list100`, `write.save`, `write.approval`, `import.commit`; `qualification/perf_harness.py::test_performance_workload`; `qualification/test_perf_unit.py` |
| VF-PER-002 | stays PENDING, related evidence recorded (warm 10-card dashboard read within bounds; no cold-cache population, filter change, drill-down or concurrent imports/report jobs) | same JSON, `dashboard.warm`, `dashboard.cold` |
| VF-PER-005 | stays PENDING (acknowledgement and render of the fixture package only; no 100,000-row export or 50-page/20-chart report exists) | same JSON, `export.acknowledge`, `export.render` |
| VF-PER-006 | PENDING → PARTIAL (propagation from calculation completion to the dashboard showing the new `result_revision`, 20 samples, p95 72 ms; collection and review delays not separately exposed) | same JSON, `freshness.propagation`, scenario `freshness` |
| VF-CAP-002 | stays PENDING, related evidence recorded (one cross-tenant probe during a 500-row import and 500 concurrent approvals; no admission control, queue limits or burst recovery) | same JSON, `isolation.tenant_b.*` |
| VF-PER-004 | stays PENDING; record the measured 29 ms per imported observation and the 500-row bound | same JSON, scenario `import_max_batch` |

Lines for shared documents:

- `docs/QUALIFICATION.md`: "QA 2026-10 performance harness: `make perf` (scripts/perf.py, native, provisioned logins); one sandbox run 1 Oct 2026 on 2 shared vCPUs, PostgreSQL 16.13 — record p95 97.5 ms, 100-row list p95 112.7 ms, save p95 169.0 ms, approval p95 192.0 ms, warm dashboard p95 242.0 ms, freshness p95 71.5 ms, 500-row import commit 14.4 s; `docs/evidence/performance-2026-10-01.json`; `make unit` gains `test_perf_unit.py` (6 passed)."
- `docs/IMPLEMENTATION.md` (limits): "Import commit is synchronous: a 500-row batch took ~14 s in one request under the tenant advisory lock (QA 2026-10 performance run)."
- `docs/NEXT-DELIVERY.md` (v0.26): "Performance harness exists (`make perf`); still needed: a quantified standard workload, peak/soak profiles, per-tenant cohorts, a run on the staging droplet, browser-side timing, an asynchronous import path."
- `docs/current/CHANGELOG.md`: "QA 2026-10 performance: scripts/perf.py, make perf, qualification/perf_harness.py, perf_support.py, test_perf_unit.py; run.py --perf."
- `CLAUDE.md` §7: add `make perf` (needs `IMPACT_FIXTURE_DSN`; `PERF_ARGS`), and to `make unit` the count change (+6 from `test_perf_unit.py`).
- `scripts/build_completion_ledger.py`: add `docs/evidence/performance-2026-10-01.json` to the VF-PER-001/002/005/006 and VF-CAP-002 evidence groups, then `make ledger`.

Shared files touched: `Makefile` (`perf` target, `.PHONY`, `test_perf_unit.py` in `unit`), `scripts/run.py` (new `--perf` flag: JUnit to the run directory and early return in native mode; no change without the flag). Recorded counts: `make unit` +6 passed; `make test`/`make native` +6 passed (the unit file is collected under `qualification/`), no new skips (`perf_harness.py` is never collected by name). No migration (0028 unused), no version bump, no product code change.
