# Performance measurement 2026-10-01

Hardware: 2 CPU, 7.8 GiB RAM (x86_64), load average before [1.73, 0.92, 0.5]. Database: PostgreSQL 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1) on x86_64-pc-linux-gnu, single node, loopback, four provisioned login roles, no pooler. Scale `sandbox` (seed 20261001, concurrency 4): 3 programmes x 10 indicators x 2 approved observations, one 500-row import.

Shared, contended 2-CPU sandbox: these numbers are not representative of production hardware.

| Class | Requirement | n | errors | p50 ms | p95 ms | p99 ms | target p95/p99 ms | verdict |
|---|---|---|---|---|---|---|---|---|
| calculate.indicator | - | 81 | 0 | 50.6 | 177.5 | 191.5 | - | NOT MEASURED |
| calculate.large | - | 5 | 0 | 182.5 | 201.4 | 201.4 | - | NOT MEASURED |
| dashboard.cold | VF-PER-002 | 3 | 0 | 71.2 | 74.7 | 74.7 | 5000/10000 | NOT MEASURED |
| dashboard.poll | - | 20 | 0 | 62.5 | 71.4 | 78.0 | - | NOT MEASURED |
| dashboard.warm | VF-PER-002 | 50 | 0 | 192.8 | 242.0 | 264.9 | 5000/10000 | MET |
| export.acknowledge | VF-PER-005 | 9 | 0 | 46.7 | 81.9 | 81.9 | -/2000 | NOT MEASURED |
| export.render | VF-PER-005 | 9 | 0 | 49.4 | 142.8 | 142.8 | 300000/- | NOT MEASURED |
| freshness.propagation | VF-PER-006 | 20 | 0 | 62.6 | 71.5 | 78.1 | 60000/- | MET |
| import.commit | - | 1 | 0 | 14388.4 | 14388.4 | 14388.4 | - | NOT MEASURED |
| import.create | - | 1 | 0 | 59.5 | 59.5 | 59.5 | - | NOT MEASURED |
| import.preview | - | 1 | 0 | 627.4 | 627.4 | 627.4 | - | NOT MEASURED |
| isolation.tenant_b.during_approvals | - | 385 | 0 | 79.5 | 103.0 | 125.9 | - | NOT MEASURED |
| isolation.tenant_b.during_import | - | 368 | 0 | 40.7 | 53.2 | 73.9 | - | NOT MEASURED |
| isolation.tenant_b.idle | - | 40 | 0 | 30.8 | 37.1 | 39.5 | - | NOT MEASURED |
| period.close.approve | - | 4 | 0 | 139.5 | 153.0 | 153.0 | - | NOT MEASURED |
| period.close.request | - | 4 | 0 | 164.9 | 247.7 | 247.7 | - | NOT MEASURED |
| read.list100 | VF-PER-001 | 400 | 0 | 85.2 | 112.7 | 125.8 | 2000/5000 | MET |
| read.record | VF-PER-001 | 2020 | 0 | 66.9 | 97.5 | 111.8 | 2000/5000 | MET |
| write.approval | VF-PER-001 | 1142 | 0 | 143.2 | 192.0 | 217.8 | 2000/5000 | MET |
| write.save | VF-PER-001 | 1358 | 0 | 123.4 | 169.0 | 190.1 | 2000/5000 | MET |

Scenarios:

- `seed`: wall_seconds=30.05, loadavg_after=[1.64, 0.97, 0.53], concurrency=1, programmes=3, indicators=30, observations=60
- `calculate_and_cold_dashboard`: wall_seconds=2.74, loadavg_after=[1.59, 0.97, 0.54], concurrency=1
- `interactive_reads`: wall_seconds=16.63, loadavg_after=[2.19, 1.14, 0.6], concurrency=4, requests_per_class=200
- `import_max_batch`: wall_seconds=15.34, loadavg_after=[2.22, 1.2, 0.63], rows=500, observations=500, preview_ms=627.4, preview_counts={'rows': 500, 'accepted': 500, 'warnings': 0, 'duplicate': 0, 'quarantined': 0, 'observations': 500}, commit_ms=14388.5
- `approve_imported`: wall_seconds=30.94, loadavg_after=[3.46, 1.61, 0.78], concurrency=4, workflows=500
- `seed_large`: wall_seconds=68.4, loadavg_after=[4.08, 2.17, 1.04], concurrency=4, observations=500
- `calculate_large`: wall_seconds=1.37, loadavg_after=[4.08, 2.17, 1.04], value=46.733396456107, numerator=24185, denominator=51751, reason_code=CALCULATED
- `freshness`: wall_seconds=11.35, loadavg_after=[3.4, 2.12, 1.04]
- `period_close`: wall_seconds=5.3, loadavg_after=[3.12, 2.08, 1.03], closes=[{'indicators': 10, 'request_ms': 186.0, 'approve_ms': 147.2}, {'indicators': 10, 'request_ms': 154.7, 'approve_ms': 125.4}, {'indicators': 10, 'request_ms': 164.9, 'approve_ms': 153.0}, {'indicators': 1, 'request_ms': 247.7, 'approve_ms': 139.5}]
- `report_export`: wall_seconds=1.92, loadavg_after=[3.12, 2.08, 1.03], formats=['PDF', 'XLSX', 'DOCX'], repetitions=3
