# Dependency inventory and SBOM

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: any change to `requirements.lock`, `requirements.txt`, `apps/web/package-lock.json`, `tools/*/package-lock.json`, or image tags in `deploy/`.

Generated 2026-10-08 from the lock files at the head of `main` (build 0.36.0). CycloneDX 1.5 JSON, in [`sbom/`](sbom/). These list declared, locked components; they are not a scan of a built image and were not checked against a vulnerability database.

| File | Source | Components | Tool |
|---|---|---|---|
| `sbom/python-requirements-lock.cdx.json` | `requirements.lock` (pinned `name==version`; hashes are in `deploy/requirements.runtime.txt`) | 41 | `cyclonedx-py requirements` (cyclonedx-bom, `--output-reproducible`) |
| `sbom/npm-apps-web.cdx.json` | `apps/web/package-lock.json` (lockfile v3, includes dev tooling such as the build chain) | 69 | `npx @cyclonedx/cyclonedx-npm --package-lock-only` |
| `sbom/npm-tools-browser.cdx.json` | `tools/browser/package-lock.json` (Playwright, axe-core: test tooling) | 20 | same |
| `sbom/npm-tools-dev-db.cdx.json` | `tools/dev-db/package-lock.json` (PGlite dev database) | 2 | same |

Regenerate:

```
cd apps/web && npx --yes @cyclonedx/cyclonedx-npm --package-lock-only --output-format JSON --spec-version 1.5 --output-file ../../docs/governance/sbom/npm-apps-web.cdx.json
# same for tools/browser and tools/dev-db
python3 -m venv /tmp/sb && /tmp/sb/bin/pip install cyclonedx-bom
/tmp/sb/bin/cyclonedx-py requirements requirements.lock --sv 1.5 --of JSON --output-reproducible -o docs/governance/sbom/python-requirements-lock.cdx.json
```

## Known gaps (stated plainly)

- The Python SBOM has no licence data and no hashes (the lock file carries none; `deploy/requirements.runtime.txt` does). The container image's operating-system packages and base images are not inventoried.
- Pinned in code, not in an SBOM: Keycloak 26.7.4 with a SHA-256 check in `scripts/idp.py`; the PostgreSQL 17, Caddy 2 and base-image tags follow their tags and are "refreshed at each build" (DEPLOYMENT-GUIDE section 9). No image digest pinning: TBD (owner: Nakul Jain).
- `requirements.lock` includes test tooling (pytest and plugins) that `deploy/requirements.runtime.txt` leaves out, so the Python SBOM over-states the runtime set.
- No vulnerability scan, licence-policy check or SBOM publication step runs in CI (`.github/workflows/qualification.yml`). Adding one changes CI and needs the owner's decision.
- The one source-embedded third-party code is covered in [THIRD-PARTY-LICENCES.md](THIRD-PARTY-LICENCES.md).
