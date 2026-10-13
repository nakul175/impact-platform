# Release 1.40 — Qualification repair candidate

## Delivered

- Registers the exact generated current access profile through additive migration 0095.
- Converts the unqualified 0048–0051 access-profile seeds to the static, checksum-verifiable form required by the repository's upgrade checks.
- Repairs invalid foreign-key targets and a reserved identifier in unqualified migrations 0060, 0072 and 0081.
- Restores the solution-vetting publication path and fixes diagnosis-review validation formatting.

## Contract and persistence

The current access manifest is registered for governed bootstrap and later review. Registration does not activate it for an existing tenant or widen current authority. Historical migrations 0001–0047 remain byte-exact. Migration 0095 is additive and the current data dictionary records every changed candidate checksum.

## Limits

This is a local qualification repair candidate. It is not merged or deployed. The first full regression after the repair reported 2,303 passed, 192 failed, 229 skipped and one deselected check. Most remaining failures are compatibility gaps between the 50 newly coded stories and retained qualification expectations; they must be reconciled without weakening security or acceptance criteria.

## Reproduction

Focused profile and catalogue checks:

```text
.venv/bin/pytest -q qualification/test_access_upgrade_unit.py qualification/test_ai_solutions_catalog.py
88 passed
```

Full local qualification:

```text
IMPACT_PORT=8123 make test
192 failed, 2303 passed, 229 skipped, 1 deselected
```

## Integration notes

- Keep the candidate off `main` until the complete local suite and the required four exact-candidate CI jobs pass.
- No requirement moves to accepted, tested, merged or deployed from this checkpoint.
- Remaining failures need code/test contract reconciliation story by story; do not delete or weaken retained tests merely to obtain green status.
