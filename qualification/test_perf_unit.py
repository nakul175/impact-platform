"""Pure checks of the performance harness (QA 2026-10): statistics, verdicts and seed determinism.
No database or API; runs in `make unit` and every suite."""

import pytest

from perf_support import (
    MINIMUM_SAMPLES,
    PROFILES,
    import_csv,
    markdown,
    percentile,
    profile,
    ratio_values,
    summarize,
    verdict,
    windows,
    workload,
)


def test_nearest_rank_percentiles():
    samples = list(range(1, 101))  # 1..100
    assert percentile(samples, 50) == 50
    assert percentile(samples, 95) == 95
    assert percentile(samples, 99) == 99
    assert percentile(samples, 100) == 100
    # Order does not matter and nothing is interpolated.
    assert percentile([30, 10, 20], 50) == 20
    assert percentile([10, 20], 95) == 20
    assert percentile([7], 99) == 7
    assert percentile([], 95) is None
    with pytest.raises(ValueError):
        percentile([1], 0)


def test_summary_counts_errors_instead_of_dropping_them():
    s = summarize([10.0, 20.0, 30.0, 40.0], errors=1)
    assert (s["count"], s["errors"], s["error_rate"]) == (4, 1, 0.2)
    assert (s["min_ms"], s["p50_ms"], s["max_ms"], s["mean_ms"]) == (10.0, 20.0, 40.0, 25.0)
    empty = summarize([], errors=0)
    assert empty["count"] == 0 and empty["p95_ms"] is None and empty["error_rate"] is None


def test_verdicts_are_honest():
    fast = summarize([100.0] * MINIMUM_SAMPLES)
    assert verdict("read.record", fast) == "MET"
    # Too few samples cannot support a p95/p99 claim, even when every sample is fast.
    assert verdict("read.record", summarize([100.0] * (MINIMUM_SAMPLES - 1))) == "NOT MEASURED"
    # But a single sample beyond the bound already fails.
    assert verdict("read.record", summarize([6000.0])) == "NOT MET"
    # p99 beyond 5 s fails even when p95 is within 2 s.
    tail = summarize([100.0] * 98 + [6000.0] * 2)
    assert tail["p95_ms"] == 100.0 and verdict("write.approval", tail) == "NOT MET"
    # Any error fails the class (failure rules count errors); unknown classes have no target.
    assert verdict("write.save", summarize([100.0] * 50, errors=1)) == "NOT MET"
    assert verdict("calculate.large", fast) == "NOT MEASURED"
    assert verdict("read.record", summarize([])) == "NOT MEASURED"


def test_seed_is_deterministic_and_synthetic():
    assert ratio_values(7, 50) == ratio_values(7, 50)
    assert ratio_values(7, 50) != ratio_values(8, 50)
    for n, d in ratio_values(7, 200):
        assert 10 <= int(d) <= 200 and 0 <= int(n) <= int(d)
    csv = import_csv(3, 500, "U")
    assert csv == import_csv(3, 500, "U")
    lines = csv.splitlines()
    assert lines[0] == "district,households" and len(lines) == 501
    assert lines[1].startswith("U-00000,") and lines[-1].startswith("U-00499,")


def test_workload_scales_and_validation():
    w = workload("sandbox", seed=1, concurrency=4)
    assert w.describe()["manual_observations"] == w.programmes * w.indicators * w.obligations
    # The import batch stays within the bounded maximum (MAX_ROWS = MAX_OBSERVATIONS = 500).
    assert all(workload(s).import_rows <= 500 for s in ["smoke", "sandbox", "standard"])
    with pytest.raises(ValueError):
        workload("huge")
    with pytest.raises(ValueError):
        workload("smoke", concurrency=0)


def test_markdown_summary_lists_every_class():
    report = {
        "started_at": "2026-10-01T00:00:00Z",
        "hardware": {"cpu_count": 2, "memory_gib": 7.8, "machine": "x86_64"},
        "loadavg_before": [0.1, 0.1, 0.1],
        "database": {"server_version": "PostgreSQL 16.13, compiled", "topology": "single node"},
        "workload": workload("smoke").describe(),
        "classes": {
            "read.record": {
                **summarize([1.0] * 20),
                "requirement": "VF-PER-001",
                "target_p95_ms": 2000,
                "target_p99_ms": 5000,
                "verdict": "MET",
            }
        },
        "scenarios": {"seed": {"wall_seconds": 1.0}},
    }
    text = markdown(report)
    assert "| read.record | VF-PER-001 | 20 | 0 |" in text and "not representative" in text


def test_profiles_scale_concurrency_and_bound_durations():
    assert set(PROFILES) == {"base", "peak", "soak", "cohorts"}
    assert profile().name == "base" and profile().concurrency(4) == 4
    peak = profile("peak")
    assert (peak.multiplier, peak.duration, peak.window) == (4, 120, 30) and peak.concurrency(4) == 16
    assert profile("soak").duration == 600
    # A shortened smoke run keeps a window no longer than the run and at least five seconds.
    short = profile("soak", 20)
    assert (short.duration, short.window) == (20, 20)
    assert profile("peak", 3).window == 5
    with pytest.raises(ValueError):
        profile("burst")
    with pytest.raises(ValueError):
        profile("peak", 0)


def test_windows_group_stamped_samples_in_order():
    stamped = [(0.0, 10.0), (1.0, 30.0), (31.0, 20.0), (59.0, 40.0), (61.0, 50.0)]
    out = windows(stamped, 30)
    assert [(w["window"], w["from_seconds"], w["count"]) for w in out] == [(0, 0, 2), (1, 30, 2), (2, 60, 1)]
    assert out[0]["p95_ms"] == 30.0 and out[1]["p50_ms"] == 20.0 and out[2]["p95_ms"] == 50.0
    assert windows([], 30) == [] and windows(stamped, 0) == []
