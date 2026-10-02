.PHONY: setup dev worker test native idp unit reference browser lint build package ledger perf
PYTHON ?= python3
PY = .venv/bin/python
setup:
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -r requirements.lock
	npm ci --prefix apps/web
	npm ci --prefix tools/dev-db
	$(MAKE) build
build:
	npm run build --prefix apps/web
dev:
	$(PY) scripts/run.py dev
# One more outbox worker for a running `make dev` stack (the dev runner starts one already).
worker:
	IMPACT_WORKER_CONFIG_FILE=.local/dev/worker.json PYTHONPATH=apps/api $(PY) -m impact_api.worker
test:
	$(PY) scripts/run.py test
# Needs IMPACT_FIXTURE_DSN: a superuser connection to an empty disposable impact_test[_suffix] database.
# Runs the suite on the provisioned logins, the API restart check, the backup and restore drill of
# that database, and the schema-15 upgrade check; see scripts/run.py for the --skip-* flags.
native:
	$(PY) scripts/run.py test --native
# Needs Java 21+; downloads the pinned Keycloak into .local/keycloak on first use (scripts/idp.py).
idp:
	$(PY) scripts/run.py test --idp keycloak
	npm ci --prefix tools/browser
	node tools/browser/prepare.mjs
	$(PY) scripts/run.py idp-browser --idp keycloak
unit:
	$(PY) -m pytest qualification/test_unit.py qualification/test_administration_unit.py qualification/test_measurement_unit.py qualification/test_planning_unit.py qualification/test_golden.py qualification/test_deploy_unit.py qualification/test_ops_unit.py qualification/test_version_unit.py qualification/test_evidence_unit.py qualification/test_key_rotation.py qualification/test_audit_export.py qualification/test_perf_unit.py qualification/test_usable_staging_unit.py
# VF-DIN-001: golden corpus through the independent reference, the domain code and the live API;
# writes docs/evidence/golden-reconciliation.json.
# Performance measurement harness (QA 2026-10); needs IMPACT_FIXTURE_DSN like native. PERF_ARGS e.g. --scale smoke --recreate
perf:
	$(PY) scripts/perf.py $(PERF_ARGS)
golden:
	$(PY) scripts/run.py test --pytest-path qualification/test_golden.py
reference:
	$(PY) specification/reference-v1/run_tests.py reference --report docs/evidence/reference-tests.json
browser:
	npm ci --prefix tools/browser
	node tools/browser/prepare.mjs
	$(PY) scripts/run.py browser
	$(PY) scripts/run.py admin-browser
	$(PY) scripts/run.py measurement-browser
	$(PY) scripts/run.py planning-browser
	$(PY) scripts/run.py dashboard-browser
	$(PY) scripts/run.py forms-browser
	$(PY) scripts/run.py reporting-browser
	$(PY) scripts/run.py workspace-browser
	$(PY) scripts/run.py tenant-browser
	$(PY) scripts/run.py bootstrap-browser
	$(PY) scripts/run.py recovery-browser
	$(PY) scripts/run.py renewal-browser
	$(PY) scripts/run.py import-browser
	$(PY) scripts/run.py evidence-browser
	$(PY) scripts/run.py export-browser
	$(PY) scripts/run.py requeue-browser
	$(PY) scripts/run.py a11y-browser
	$(PY) scripts/run.py operators-browser
lint:
	.venv/bin/ruff check apps/api scripts qualification deploy
	.venv/bin/ruff format --check apps/api scripts qualification deploy
	apps/web/node_modules/.bin/prettier --check apps/web/src apps/web/index.html apps/web/vite.config.ts tools/dev-db/server.mjs tools/browser/*.mjs
package:
	$(PY) scripts/package_source.py
ledger:
	$(PY) scripts/build_completion_ledger.py
