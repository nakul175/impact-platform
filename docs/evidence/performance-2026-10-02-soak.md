# Performance measurement 2026-10-02

Hardware: 2 CPU, 7.8 GiB RAM (x86_64), load average before [4.42, 2.43, 1.44]. Database: PostgreSQL 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1) on x86_64-pc-linux-gnu, single node, loopback, four provisioned login roles, no pooler. Scale `smoke` (seed 20261001, concurrency 4): 1 programmes x 3 indicators x 2 approved observations, one 50-row import. Profile `soak`: multiplier 1, 90 s closed loop.

Shared, contended 2-CPU sandbox: these numbers are not representative of production hardware.

| Class | Requirement | n | errors | p50 ms | p95 ms | p99 ms | target p95/p99 ms | verdict |
|---|---|---|---|---|---|---|---|---|
| calculate.indicator | - | 3 | 0 | 61.2 | 65.4 | 65.4 | - | NOT MEASURED |
| dashboard.cold | VF-PER-002 | 1 | 0 | 65.3 | 65.3 | 65.3 | 5000/10000 | NOT MEASURED |
| dashboard.warm | VF-PER-002 | 116 | 0 | 173.6 | 249.4 | 318.6 | 5000/10000 | MET |
| read.list100 | VF-PER-001 | 476 | 0 | 104.7 | 157.1 | 186.6 | 2000/5000 | MET |
| read.record | VF-PER-001 | 919 | 0 | 89.2 | 130.3 | 153.1 | 2000/5000 | MET |
| write.approval | VF-PER-001 | 355 | 0 | 209.0 | 304.9 | 382.1 | 2000/5000 | MET |
| write.save | VF-PER-001 | 719 | 0 | 179.7 | 276.9 | 315.8 | 2000/5000 | MET |

Scenarios:

- `seed`: wall_seconds=4.98, loadavg_after=[4.31, 2.44, 1.45], concurrency=1, programmes=1, indicators=3, observations=6
- `calculate_and_cold_dashboard`: wall_seconds=0.38, loadavg_after=[4.31, 2.44, 1.45], concurrency=1
- `profile_soak`: wall_seconds=90.61, loadavg_after=[5.1, 3.21, 1.82], profile={'name': 'soak', 'multiplier': 1, 'duration': 90, 'window': 60}, concurrency=4, iterations=1140, windows={'read.list100': [{'window': 0, 'from_seconds': 0, 'count': 343, 'p50_ms': 102.1, 'p95_ms': 151.7}, {'window': 1, 'from_seconds': 60, 'count': 133, 'p50_ms': 109.5, 'p95_ms': 175.1}], 'read.record': [{'window': 0, 'from_seconds': 0, 'count': 582, 'p50_ms': 87.1, 'p95_ms': 124.4}, {'window': 1, 'from_seconds': 60, 'count': 337, 'p50_ms': 94.1, 'p95_ms': 142.6}], 'dashboard.warm': [{'window': 0, 'from_seconds': 0, 'count': 76, 'p50_ms': 160.8, 'p95_ms': 294.3}, {'window': 1, 'from_seconds': 60, 'count': 40, 'p50_ms': 193.7, 'p95_ms': 242.3}], 'write.save': [{'window': 0, 'from_seconds': 0, 'count': 453, 'p50_ms': 176.0, 'p95_ms': 275.1}, {'window': 1, 'from_seconds': 60, 'count': 266, 'p50_ms': 190.1, 'p95_ms': 277.3}], 'write.approval': [{'window': 0, 'from_seconds': 0, 'count': 222, 'p50_ms': 202.2, 'p95_ms': 304.9}, {'window': 1, 'from_seconds': 60, 'count': 133, 'p50_ms': 220.6, 'p95_ms': 299.4}]}
