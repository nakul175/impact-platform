# Performance measurement 2026-10-02

Hardware: 2 CPU, 7.8 GiB RAM (x86_64), load average before [4.69, 3.19, 1.83]. Database: PostgreSQL 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1) on x86_64-pc-linux-gnu, single node, loopback, four provisioned login roles, no pooler. Scale `smoke` (seed 20261001, concurrency 4): 1 programmes x 3 indicators x 2 approved observations, one 50-row import. Profile `cohorts`: multiplier 1, 60 s closed loop.

Shared, contended 2-CPU sandbox: these numbers are not representative of production hardware.

| Class | Requirement | n | errors | p50 ms | p95 ms | p99 ms | target p95/p99 ms | verdict |
|---|---|---|---|---|---|---|---|---|
| calculate.indicator | - | 3 | 0 | 68.9 | 70.0 | 70.0 | - | NOT MEASURED |
| dashboard.cold | VF-PER-002 | 1 | 0 | 92.1 | 92.1 | 92.1 | 5000/10000 | NOT MEASURED |
| dashboard.warm | VF-PER-002 | 60 | 0 | 263.2 | 390.9 | 666.9 | 5000/10000 | MET |
| isolation.tenant_b.during_cohorts | - | 435 | 0 | 131.1 | 199.9 | 232.0 | - | NOT MEASURED |
| isolation.tenant_b.idle | - | 157 | 0 | 62.9 | 80.3 | 89.3 | - | NOT MEASURED |
| isolation.tenant_c.during_cohorts | - | 465 | 0 | 124.4 | 183.7 | 209.2 | - | NOT MEASURED |
| isolation.tenant_c.idle | - | 167 | 0 | 58.0 | 76.0 | 83.7 | - | NOT MEASURED |
| read.list100 | VF-PER-001 | 220 | 0 | 153.5 | 216.0 | 277.4 | 2000/5000 | MET |
| read.record | VF-PER-001 | 416 | 0 | 136.7 | 191.6 | 220.7 | 2000/5000 | MET |
| write.approval | VF-PER-001 | 155 | 0 | 328.7 | 455.1 | 524.4 | 2000/5000 | MET |
| write.save | VF-PER-001 | 319 | 0 | 276.8 | 437.6 | 492.9 | 2000/5000 | MET |

Scenarios:

- `seed`: wall_seconds=5.37, loadavg_after=[4.4, 3.15, 1.83], concurrency=1, programmes=1, indicators=3, observations=6
- `calculate_and_cold_dashboard`: wall_seconds=0.46, loadavg_after=[4.4, 3.15, 1.83], concurrency=1
- `profile_cohorts`: wall_seconds=71.56, loadavg_after=[5.77, 3.8, 2.15], profile={'name': 'cohorts', 'multiplier': 1, 'duration': 60, 'window': 30}, concurrency=4, tenant_c=8ae4e99e-409a-445e-bd5f-a618bc24ae67, noisy_iterations=525, isolation.tenant_b_p95_ratio=2.49, isolation.tenant_c_p95_ratio=2.42
