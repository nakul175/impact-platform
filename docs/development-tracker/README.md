# Live Tola + AI development tracker

This is a local development-support dashboard for the authorised eight-hour session, **5 October 2026, 08:27:26–16:27:26 UTC / 13:57:26–21:57:26 IST**. It extends the existing repository's documentation tooling; it is not a tenant-facing feature, deployment, acceptance register or complete-platform delivery promise.

The server reads the actual saved source files at every request. The browser polls every five seconds. The countdown measures time only: it never changes a workstream's state, adds a deliverable or increases an increment count. Source timestamps, a 15-minute stale indicator and expired forecast warnings remain visible. A failed poll retains the last successfully read snapshot with an explicit warning. Missing/invalid stream files are unavailable, rather than completed.

## Start and inspect

From the repository root:

```sh
.venv/bin/python tools/development-tracker/tracker.py --port 8170
```

Open `http://127.0.0.1:8170`. `GET /api/status` returns the same actual state as the dashboard. The server binds only to loopback and accepts exactly one Host header naming `127.0.0.1` or `localhost` with its actual port. Wrong, missing and duplicate hosts are refused before loading repository status, which prevents a rebound external hostname from reading the local source. It supports no write endpoint, serves exactly its three static assets and status endpoint, and applies no-store, same-origin content security and anti-framing headers. It has no product database, provider, account or credential integration. Do not expose it publicly or place secrets, tokens, personal records or raw logs in its files.

## Ownership and atomic updates

The integrator owns `sprint.json`, including the stream inventory, bounded increment counts and true active-agent count. Each stream has one writer:

| File                           | Writer                 |
| ------------------------------ | ---------------------- |
| `streams/tracker.json`         | `/root/sprint_tracker` |
| `streams/access-ceilings.json` | `/root/sprint_access`  |
| `streams/content-archive.json` | `/root/sprint_content` |
| `streams/integration-qa.json`  | `/root`                |
| `streams/ops-portability.json` | `/root/sprint_tracker` |
| `streams/impact-references.json` | `/root/sprint_content` |
| `streams/human-advice.json` | `/root/sprint_access` |

Ownership is an agent coordination convention, not operating-system authentication. Keep one writer per file. New streams must be registered explicitly in `sprint.json` before using the updater, and need a complete closed stream record. The source schema is implemented in `tracker.py` (`STREAM_FIELDS`, `SPRINT_FIELDS`, `validate_stream`, `validate_sprint`).

Write a JSON patch file, then use:

```sh
.venv/bin/python tools/development-tracker/update.py --stream access-ceilings --file /tmp/access-progress.json
.venv/bin/python tools/development-tracker/update.py --sprint --file /tmp/integration-rollup.json
```

The optional `--expect-updated-at <exact-source-timestamp>` refuses a stale edit. `--file -` accepts structured JSON on stdin. Unknown fields, duplicate keys, unsupported IDs, non-finite JSON, oversized data and invalid timestamps/ranges are refused. The updater merges top-level patch fields; replace an entire nested `eta` or `rollup` object, rather than a fragment. Lists are replaced rather than appended. It preserves the previous complete file until an atomic rename succeeds, stamps `updated_at` and retains the latest 100 meaningful stream changes. A heartbeat-only patch does not fabricate a progress history entry.

Example stream patch:

```json
{
  "status": "TESTING",
  "summary": "The bounded backend implementation is under independent review.",
  "next_step": "Resolve findings and run the named local regression checks.",
  "eta": {
    "earliest": "2026-10-05T10:30:00Z",
    "latest": "2026-10-05T11:30:00Z",
    "confidence": "LOW",
    "basis": "Backend forecast only; integration and hosted gates remain separate."
  },
  "blockers": []
}
```

States are `QUEUED`, `INSPECTING`, `BUILDING`, `REVIEWING`, `TESTING`, `BLOCKED`, `COMPLETE`. ETA confidence is `UNESTIMATED`, `LOW`, `MEDIUM`, `HIGH`; `UNESTIMATED` requires both date fields to be `null`. Complete slices require named `delivered` items and evidence. Evidence records are closed objects with `title`, existing repository-relative `path`, `result`, bounded `scope` and UTC `recorded_at`. They state precisely what ran or was inspected; file existence is not proof that a declared result is true. Test results must come from actual recorded execution.

`verified_increments ≤ integrated_increments ≤ planned_increments` and `active_agents ≤ active_agent_limit` are enforced. There is no global completion-percent field. A workstream may finish a bounded local slice while hosted/native/UAT qualification of the combined product remains pending; say so in its summary/evidence and the integrator's rollup.

## Consolidated backlog

`backlog.json` groups every one of the 307 impact requirements and 40 nonprofit AI requirements exactly once into 14 editorial domains. Shared identity, governance, evidence, privacy, interoperability and operations appear once. Domain groups have different sizes and complexity; their counts are not effort weights, remaining person-hours or a completion percentage.

The derived `docs/COMPLETION-LEDGER.json` now records build 0.32 and bounded supporting evidence; all 307 original requirement acceptance statuses remain unchanged. The proposed `docs/nonprofit-ai/v1.0/requirements.json` remains unchanged. Their build, assessment date, proposed status and source SHA-256 fingerprints are retained so the scope index cannot present development support as acceptance. Current summaries point to the 0.32 saved checkpoint and the 0.33 candidate appendage/workstreams. The saved commit is recorded; the tentative candidate build comes from VERSION.json. Integrated programme links and internal advice are labelled pending their application/native/browser gates, not accepted.

Regenerate only this scope index after reviewing changed source records:

```sh
.venv/bin/python tools/development-tracker/build_backlog.py
```

## Qualification

```sh
.venv/bin/python -m pytest tools/development-tracker/test_tracker.py -q --junitxml=docs/development-tracker/tracker-unit-tests.xml
```

The offline record contains **42 passing checks**. It covers source reload, no time-based completion, exact scope coverage/deduplication, atomic failure preservation, bounded history and counts, stale edits, closed inputs, unsafe paths, missing/corrupt sources, strict Host-header refusal and security headers. It is supporting tracker evidence, not a new application-suite count.

With the loopback server running and the existing browser dependencies available:

```sh
IMPACT_TRACKER_URL=http://127.0.0.1:8170 node tools/development-tracker/browser_check.mjs
```

`browser-evidence.json` records **15 passing groups, zero failed groups, zero uncaught JavaScript errors and two axe scans with zero violations/incomplete findings** in local Chrome. Actual desktop/mobile rendering and endpoint reads are included. Explicitly synthetic intercepted source snapshots test stale/unavailable sources, changed poll responses, inert markup and keyboard-state preservation. They do not rewrite live workstream files. `tracker-desktop.png`, `tracker-mobile.png` and `tracker-mobile-workstreams.png` capture the actual tracker. Zero automated accessibility violations is not complete accessibility conformance.
