# 0.30 Mercy Corps reporting regression scenarios

## Delivered

Twelve newly authored, synthetic pure regression tests exercise the existing Impact calculation,
planning comparison and reporting-calendar functions. This brings a useful subset of the earlier
Mercy Corps research into qualification, without importing Django, its models, its permissions or
its arithmetic. No new runtime feature or requirement acceptance is claimed.

The upstream source is Mercy Corps TolaData revision
[`7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d`](https://github.com/mercycorps/toladata/tree/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d):

- `indicators/tests/iptt_tests/scenarios.py`: no, one or multiple results; numeric cumulative,
  noncumulative and percentage families; disaggregated results.
- `indicators/queries/targets_queries.py`: actual and target-percent-met behavior, including zero
  targets and latest percentages. Its cumulative naming and latest-percentage selection cannot be
  mapped directly to Impact's declared FLOW/CUMULATIVE semantics and component-based pooled ratios.
- `indicators/tests/test_generate_periodic_target.py`: monthly, quarterly and annual period names,
  counts and date boundaries. Impact uses reporting-zone UTC instants and exclusive period ends;
  the leap-year, DST and offset assertions are platform-specific translations of this scenario family.

These sources inspire the scenario selection; test code and fixture values are original. No upstream
code, translated messages, branding or participant records were copied.

## Contract and persistence

Unchanged. Tests call `domain.calculate`, `domain.disaggregate`, `planning.progress` and
`reference_data.periods`. No endpoints, capabilities, dependencies or migrations are introduced.

The tests preserve missing versus zero; independent review filtering; flow versus cumulative
positions; pooled percentage components; undefined denominators and zero targets; raw decimal
attainment without a cap; equivalent event instants; nonadditive multiselect categories; leap days,
reporting-zone offsets, DST and contiguous year boundaries.

## Limits

These are deterministic function checks, not evidence of authorization, actual period assignment,
snapshot freezing, concurrency, a hosted CI run, staging deployment or UAT. Calendar tests check
boundaries emitted by the existing generator; they do not introduce partial-programme-period
clipping, semiannual frequencies or life-of-programme target generation. Existing API and browser
qualification remain necessary. All requirement states remain unchanged.

## Reproduction

From the repository root:

```sh
PYTHONPATH=apps/api .venv/bin/python -m pytest -q qualification/test_toladata_reuse_scenarios.py
.venv/bin/ruff check qualification/test_toladata_reuse_scenarios.py
.venv/bin/ruff format --check qualification/test_toladata_reuse_scenarios.py
```

Local result on 5 October 2026: **12 passed**, with lint and formatting clean. No paid CI run was
started by this slice.

## Integration notes

Files owned by this slice: `qualification/test_toladata_reuse_scenarios.py` and this document.
The integrator should add the test file to the pure-unit target and summarize its scope in the
shared release and qualification documents. No versions, contracts, shared documents or ledger
states were edited by this slice. No proposed requirement movement. No runtime changes.

Useful exact tests include `test_percentage_actual_requires_components_and_is_not_latest_or_average`,
`test_period_flow_and_cumulative_position_cannot_share_a_summation_rule`,
`test_monthly_leap_day_and_year_rollover_have_exclusive_contiguous_ends`, and
`test_monthly_dst_boundary_preserves_local_midnight_and_contiguity`.
