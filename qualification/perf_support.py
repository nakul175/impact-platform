"""Pure helpers of the performance measurement harness (QA 2026-10): the synthetic workload plan,
its deterministic value generator, latency statistics and the comparison with the FSD targets.

Nothing here touches the network or the database, so `qualification/test_perf_unit.py` checks it
in every suite. The harness itself is `qualification/perf_harness.py`, run by `scripts/perf.py`."""

import math
import random
from dataclasses import asdict, dataclass

# Named workload scales. "sandbox" is what fits a shared 2-CPU development machine in a few
# minutes; "standard" is larger but is still far below the FSD "standard workload", which the
# specification does not quantify in rows or users (see docs/QA-PERFORMANCE-2026-10.md).
SCALES = {
    "smoke": dict(programmes=1, indicators=3, obligations=2, import_rows=50, read_samples=40),
    "sandbox": dict(programmes=3, indicators=10, obligations=2, import_rows=500, read_samples=200),
    "standard": dict(programmes=5, indicators=10, obligations=4, import_rows=500, read_samples=500),
}


@dataclass(frozen=True)
class Workload:
    scale: str
    seed: int
    concurrency: int
    programmes: int
    indicators: int
    obligations: int
    import_rows: int
    read_samples: int

    @property
    def manual_observations(self):
        return self.programmes * self.indicators * self.obligations

    def describe(self):
        return {**asdict(self), "manual_observations": self.manual_observations}


def workload(scale="sandbox", seed=20261001, concurrency=4):
    if scale not in SCALES:
        raise ValueError("Unknown scale " + scale)
    if concurrency < 1:
        raise ValueError("Concurrency must be at least 1")
    return Workload(scale=scale, seed=seed, concurrency=concurrency, **SCALES[scale])


def ratio_values(seed, count):
    """Deterministic synthetic numerator/denominator pairs (strings, as the API transports them):
    denominators 10..200, numerators 0..denominator. The same seed always gives the same list."""
    rng = random.Random(seed)
    pairs = []
    for _ in range(count):
        d = rng.randint(10, 200)
        pairs.append((str(rng.randint(0, d)), str(d)))
    return pairs


def import_csv(seed, rows, unit_prefix):
    """A deterministic CSV of `rows` districts with household counts 0..999 (one value column)."""
    rng = random.Random(seed)
    lines = ["district,households"]
    for i in range(rows):
        lines.append(f"{unit_prefix}-{i:05d},{rng.randint(0, 999)}")
    return "\n".join(lines) + "\n"


def percentile(samples, p):
    """Nearest-rank percentile (no interpolation): the smallest sample with at least p % of the
    samples at or below it. None for an empty population."""
    if not samples:
        return None
    if not 0 < p <= 100:
        raise ValueError("p must be in (0, 100]")
    ordered = sorted(samples)
    rank = math.ceil(p / 100 * len(ordered))
    return ordered[rank - 1]


def summarize(samples_ms, errors=0):
    """Latency summary in milliseconds (rounded to 0.1 ms) plus error count and rate. The error
    rate is errors / (samples + errors): failed requests are counted, never dropped."""
    n = len(samples_ms)
    total = n + errors

    def r(v):
        return None if v is None else round(v, 1)

    return {
        "count": n,
        "errors": errors,
        "error_rate": round(errors / total, 4) if total else None,
        "min_ms": r(min(samples_ms)) if n else None,
        "p50_ms": r(percentile(samples_ms, 50)),
        "p95_ms": r(percentile(samples_ms, 95)),
        "p99_ms": r(percentile(samples_ms, 99)),
        "max_ms": r(max(samples_ms)) if n else None,
        "mean_ms": r(sum(samples_ms) / n) if n else None,
    }


# FSD v1.1 bounds (milliseconds) per measured class. Each class is judged on its own (VF-PER-001
# failure rule: fast reads never hide slow approvals).
TARGETS = {
    "read.record": ("VF-PER-001", 2000, 5000),
    "read.list100": ("VF-PER-001", 2000, 5000),
    "write.save": ("VF-PER-001", 2000, 5000),
    "write.approval": ("VF-PER-001", 2000, 5000),
    "dashboard.cold": ("VF-PER-002", 5000, 10000),
    "dashboard.warm": ("VF-PER-002", 5000, 10000),
    "freshness.propagation": ("VF-PER-006", 60000, None),
    "export.acknowledge": ("VF-PER-005", None, 2000),
    "export.render": ("VF-PER-005", 300000, None),
}

# Fewer samples than this cannot support a p95/p99 verdict.
MINIMUM_SAMPLES = 20


def verdict(name, summary):
    """MET / NOT MET / NOT MEASURED for one class. NOT MEASURED when there is no target, no samples,
    any error (the failure rules count errors), or too few samples for a p95/p99 to mean anything."""
    if name not in TARGETS:
        return "NOT MEASURED"
    _, p95, p99 = TARGETS[name]
    if not summary.get("count"):
        return "NOT MEASURED"
    if summary.get("errors"):
        return "NOT MET"
    if p95 is None and p99 is None:
        return "NOT MEASURED"
    if (p95 is not None and summary["p95_ms"] > p95) or (p99 is not None and summary["p99_ms"] > p99):
        return "NOT MET"
    if summary["count"] < MINIMUM_SAMPLES:
        return "NOT MEASURED"
    return "MET"


def markdown(report):
    """A short summary table of one harness report (the JSON stays the record)."""
    hw, w = report["hardware"], report["workload"]
    lines = [
        "# Performance measurement " + report["started_at"][:10],
        "",
        f"Hardware: {hw['cpu_count']} CPU, {hw['memory_gib']} GiB RAM ({hw['machine']}), load average "
        f"before {report['loadavg_before']}. Database: {report['database']['server_version'].split(',')[0]}, "
        f"{report['database']['topology']}. Scale `{w['scale']}` (seed {w['seed']}, concurrency "
        f"{w['concurrency']}): {w['programmes']} programmes x {w['indicators']} indicators x "
        f"{w['obligations']} approved observations, one {w['import_rows']}-row import.",
        "",
        "Shared, contended 2-CPU sandbox: these numbers are not representative of production hardware.",
        "",
        "| Class | Requirement | n | errors | p50 ms | p95 ms | p99 ms | target p95/p99 ms | verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name, c in report["classes"].items():
        target = "/".join("-" if v is None else str(v) for v in (c["target_p95_ms"], c["target_p99_ms"]))
        lines.append(
            f"| {name} | {c['requirement'] or '-'} | {c['count']} | {c['errors']} | {c['p50_ms']} | "
            f"{c['p95_ms']} | {c['p99_ms']} | {target if c['requirement'] else '-'} | {c['verdict']} |"
        )
    lines += ["", "Scenarios:", ""]
    for name, s in report["scenarios"].items():
        lines.append(f"- `{name}`: " + ", ".join(f"{k}={v}" for k, v in s.items()))
    return "\n".join(lines) + "\n"
