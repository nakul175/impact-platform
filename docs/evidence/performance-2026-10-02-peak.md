# Performance measurement 2026-10-02

Hardware: 2 CPU, 7.8 GiB RAM (x86_64), load average before [1.41, 1.55, 1.11]. Database: PostgreSQL 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1) on x86_64-pc-linux-gnu, single node, loopback, four provisioned login roles, no pooler. Scale `smoke` (seed 20261001, concurrency 4): 1 programmes x 3 indicators x 2 approved observations, one 50-row import. Profile `peak`: multiplier 4, 40 s closed loop.

Shared, contended 2-CPU sandbox: these numbers are not representative of production hardware.

| Class | Requirement | n | errors | p50 ms | p95 ms | p99 ms | target p95/p99 ms | verdict |
|---|---|---|---|---|---|---|---|---|
| calculate.indicator | - | 3 | 0 | 65.1 | 67.4 | 67.4 | - | NOT MEASURED |
| dashboard.cold | VF-PER-002 | 1 | 0 | 72.8 | 72.8 | 72.8 | 5000/10000 | NOT MEASURED |
| dashboard.warm | VF-PER-002 | 45 | 0 | 201.3 | 1967.0 | 2513.0 | 5000/10000 | MET |
| read.list100 | VF-PER-001 | 125 | 0 | 124.3 | 252.1 | 1594.7 | 2000/5000 | MET |
| read.record | VF-PER-001 | 349 | 0 | 112.2 | 198.0 | 287.9 | 2000/5000 | MET |
| write.approval | VF-PER-001 | 138 | 0 | 1452.3 | 2119.6 | 2295.7 | 2000/5000 | NOT MET |
| write.save | VF-PER-001 | 285 | 0 | 1369.5 | 1991.3 | 2236.4 | 2000/5000 | MET |

Scenarios:

- `seed`: wall_seconds=4.62, loadavg_after=[1.45, 1.56, 1.12], concurrency=1, programmes=1, indicators=3, observations=6
- `calculate_and_cold_dashboard`: wall_seconds=0.42, loadavg_after=[1.45, 1.56, 1.12], concurrency=1
- `profile_peak`: wall_seconds=41.43, loadavg_after=[5.04, 2.48, 1.45], profile={'name': 'peak', 'multiplier': 4, 'duration': 40, 'window': 30}, concurrency=16, iterations=365, windows={'read.list100': [{'window': 0, 'from_seconds': 0, 'count': 97, 'p50_ms': 124.7, 'p95_ms': 270.5}, {'window': 1, 'from_seconds': 30, 'count': 28, 'p50_ms': 124.0, 'p95_ms': 252.1}], 'read.record': [{'window': 0, 'from_seconds': 0, 'count': 233, 'p50_ms': 109.3, 'p95_ms': 198.7}, {'window': 1, 'from_seconds': 30, 'count': 116, 'p50_ms': 120.3, 'p95_ms': 198.0}], 'dashboard.warm': [{'window': 0, 'from_seconds': 0, 'count': 40, 'p50_ms': 196.7, 'p95_ms': 1967.0}, {'window': 1, 'from_seconds': 30, 'count': 5, 'p50_ms': 228.9, 'p95_ms': 276.6}], 'write.save': [{'window': 0, 'from_seconds': 0, 'count': 188, 'p50_ms': 1276.0, 'p95_ms': 1859.7}, {'window': 1, 'from_seconds': 30, 'count': 97, 'p50_ms': 1638.2, 'p95_ms': 2021.3}], 'write.approval': [{'window': 0, 'from_seconds': 0, 'count': 84, 'p50_ms': 1371.4, 'p95_ms': 2246.1}, {'window': 1, 'from_seconds': 30, 'count': 54, 'p50_ms': 1637.0, 'p95_ms': 1991.5}]}
