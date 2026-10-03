# v0.28 — Application executor and asynchronous import commits

Proposed build 0.28.0; schema 33; domain API 1.18.0 (230 operations); platform API 1.9.0 (44 operations). Ledger: no requirement promoted or accepted. This PR is not merged or deployed.

## Delivered

A commit of more than 50 staged rows queues an `IMPORT_COMMIT` application job. A separate process handles it through the existing observation write, audit and independent review path. Smaller batches stay synchronous. The import screen shows Queued, Running, Committed or Failed, a closed error class and refresh. The operator Workers panel shows the executor heartbeat.

The executor has its own `impact_executor_login`, a member of exactly `impact_app`, without `impact_worker` membership or changed worker grants. Compose places it on the backend network only. Every run reconstructs the requesting person's identity and current grants. Authority loss fails `AUTHORITY_CHANGED`; that person's natural identity authors every observation and cannot approve it.

Claims take the tenant advisory lock and a 60-second database-clock lease. Generation and owner fence outcomes. Observation writes, import register entries, review submissions, audits and successful outcome share one transaction. A stale holder cannot complete twice. A failed commit rolls back data writes and records a closed error class separately. Preview outcome is recomputed before writing.

## Contract and persistence

The existing commit route keeps its body and capability. Above threshold the receipt has `business_state: Queued` and `job_id`; reads include `data.processing` with job ID, state, attempts, error and completion time. The server-owned `commit_request` pins the requester, workflow version, hash and warning choice, but is never returned. Migration 0033 adds `import_job_current.commit_request`, tenant-fenced `import_commit`, a due-tenant directory and an operational heartbeat. No credential is stored.

## Limits

The 500-row bound and all-or-nothing tenant lock remain; latency moves off the HTTP request but the work is not faster. `CONNECTOR_SYNC` and Kobo belong to PR 2 after this PR is merged and healthy on staging. Local PGlite does not prove native PostgreSQL login boundaries or deployed networking. No requirement is accepted.

## Reproduction and evidence

`make lint`, `make unit`, `IMPACT_PORT=8132 .venv/bin/python scripts/run.py test --pytest-path qualification/test_import.py`, `npm --prefix apps/web run build`; native: `IMPACT_UPGRADE_BASELINE=32 make native`. Focused PGlite imports: 14 passed, 1 native-only skipped, including a 51-row queued commit, takeover and stale-holder refusal, independent review, and authority loss after queueing. Focused worker suite: 34 passed. Native login, full CI, live provider, browser and container stack remain to be proved by the pull request.
