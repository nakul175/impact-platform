# Release 1.41 — Problem baseline qualification repair

## Delivered

- Registers `AIProblemBaseline` as an allowed immutable registry kind through additive migration 0098.
- Keeps problem-baseline registry and revision rows unavailable to the background worker because it has no duty for operational baseline measurements.
- Adds focused application qualification for partial drafts, complete-lock validation, immutable exact replay, tenant isolation and capability isolation.

## Contract and persistence

The API contract is unchanged. Migration 0098 repairs the missing registry-kind declaration required by the already-shipped problem-baseline API. Migrations 0001–0097 remain byte-exact. Existing tenant, revision and insert-only lock protections remain in force.

## Limits

The release security review remains open and no human confirmation or requirement acceptance is claimed. Staging deployment requires the complete exact-candidate qualification and repository checks to pass before merge.

## Reproduction

Run the focused application test:

```text
IMPACT_PORT=8123 .venv/bin/python scripts/run.py test --pytest-path qualification/test_ai_problem_baselines_live.py
```

Then run the repository checks and all four exact-candidate qualification jobs before merge.

## Integration notes

- This repair is for US-DX-03 / APL-364.
- Files touched: migration 0098, focused qualification, version metadata, generated contracts, data dictionary and release security review.
- Risk: the new registry kind must remain tenant-fenced, immutable and unavailable to the worker; focused and native qualification cover those boundaries.
