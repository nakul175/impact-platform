# Third-party licences

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: any new file under `third_party/`, any further literal reuse of upstream code, or a change to the repository's own licence.

Status: **agent-drafted 2026-10-08 from the files named below; not reviewed by a person or counsel. This is a summary of what the files say, not a legal conclusion and not a compliance claim.**

## 1. The repository's own licence

None is chosen. The root [`LICENSE.md`](../../LICENSE.md) is a placeholder: "All rights reserved, Copyright (c) 2026 Nakul Jain; no licence is granted." **Open owner decision:** choose a licence (or keep proprietary). Whether that choice interacts with the Apache-2.0 component below is for the owner and counsel: TBD (owner: Nakul Jain).

## 2. Embedded third-party code: Mercy Corps TolaData

Sources read: [`third_party/mercycorps-toladata/LICENSE`](../../third_party/mercycorps-toladata/LICENSE), [`NOTICE`](../../third_party/mercycorps-toladata/NOTICE), [`docs/handover/MERCYCORPS-REUSE.md`](../handover/MERCYCORPS-REUSE.md), the header of `apps/api/impact_api/logframe.py`, and [`docs/RELEASE-0.29-logframe-reuse.md`](../RELEASE-0.29-logframe-reuse.md).

| Fact | Where recorded |
|---|---|
| Upstream: `github.com/mercycorps/toladata`, revision `7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d` (3 November 2022) | NOTICE; MERCYCORPS-REUSE.md |
| Licence: Apache License, Version 2.0 (file is the standard text; its appendix placeholder `Copyright {yyyy} {name of copyright owner}` is unfilled, and the NOTICE carries no named copyright holder) | LICENSE; NOTICE |
| What is embedded: `apps/api/impact_api/logframe.py` adapts the `apply_label_styling` function from upstream `indicators/xls_export_utils.py`. Changes stated: platform colours instead of Mercy Corps colours; applied inline to workbook headers; no merged-cell workaround | NOTICE; `logframe.py` docstring |
| What is not used: upstream logo, name, theme, dependencies, application permission model | NOTICE |
| Tests are newly authored with scenario inspiration from upstream `test_rf_export.py` and `program.rfLevelOrdering.test.js` | NOTICE |
| The earlier trial (`tools/reuse/toladata_probe.py`) imported no upstream code; any later literal reuse "must retain applicable notices, include the license and mark modified files" and individual files and third-party assets should be checked first | MERCYCORPS-REUSE.md |

### What the Apache-2.0 text in the repository requires (Section 4, "Redistribution")

Quoted in substance from the licence file; applies when the work or derivative works are reproduced or distributed:

- (a) give recipients a copy of the License;
- (b) modified files carry prominent notices that they were changed;
- (c) retain, in Source form of derivative works, copyright, patent, trademark and attribution notices of the Source form;
- (d) if the Work has a NOTICE file, include a readable copy of its attribution notices in a NOTICE file, in documentation, or in a display, as the licence allows. The NOTICE contents are informational and do not modify the License;
- you may add your own copyright statement to your modifications and may provide different terms for them, provided use of the Work otherwise complies.

Other sections, in substance: Section 3 grants a patent licence from contributors, with a termination clause on patent litigation; Section 5 treats submitted contributions as under the same licence unless stated; Section 6 grants no trademark rights; Sections 7 and 8 disclaim warranty and limit liability.

### Present state against those points (observed, not concluded)

| Point | Observed |
|---|---|
| Licence copy shipped | `third_party/mercycorps-toladata/LICENSE` is in the repository. `scripts/package_source.py` excludes only `.venv`, `.local`, `node_modules`, caches, `dist`, `.git`, so the source archive includes `third_party/` |
| Modified-file notice | `logframe.py` docstring states the adaptation and the upstream commit; the NOTICE lists the changes |
| NOTICE carried | `third_party/mercycorps-toladata/NOTICE` exists. No product screen or root-level NOTICE reproduces it: TBD (owner: Nakul Jain) |
| Upstream copyright line | Not present in either file: TBD, check upstream at the pinned revision |
| Trademarks | NOTICE states no upstream name, logo or theme is used |

## 3. Other third-party components

Python, npm and container components are inventoried in [DEPENDENCY-INVENTORY.md](DEPENDENCY-INVENTORY.md) with CycloneDX files under [`sbom/`](sbom/). Licence identifiers present in the npm SBOMs, by count of components: `apps/web` MIT 33, Apache-2.0 22, MPL-2.0 12, ISC 1, BSD-3-Clause 1; `tools/browser` MIT 8, Apache-2.0 9, ISC 2, MPL-2.0 1; `tools/dev-db` Apache-2.0 2. The Python SBOM carries no licence data (the lock file has none). Obligations of those licences (notably MPL-2.0 file-level terms) have not been analysed: TBD (owner: Nakul Jain).

Runtime images and services named in `deploy/compose.yaml` (PostgreSQL 17, Keycloak 26.7.4, Caddy 2, Python 3.12 and Node 24 base images) keep their own licences; none has been reviewed here.
