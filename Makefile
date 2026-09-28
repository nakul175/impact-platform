.PHONY: setup dev test unit reference browser lint build package ledger
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
test:
	$(PY) scripts/run.py test
unit:
	$(PY) -m pytest qualification/test_unit.py qualification/test_administration_unit.py qualification/test_measurement_unit.py
reference:
	$(PY) specification/reference-v1/run_tests.py reference --report docs/evidence/reference-tests.json
browser:
	npm ci --prefix tools/browser
	node tools/browser/prepare.mjs
	$(PY) scripts/run.py browser
	$(PY) scripts/run.py admin-browser
	$(PY) scripts/run.py measurement-browser
	$(PY) scripts/run.py reporting-browser
	$(PY) scripts/run.py workspace-browser
	$(PY) scripts/run.py tenant-browser
	$(PY) scripts/run.py bootstrap-browser
	$(PY) scripts/run.py recovery-browser
	$(PY) scripts/run.py renewal-browser
lint:
	.venv/bin/ruff check apps/api scripts qualification
	.venv/bin/ruff format --check apps/api scripts qualification
	apps/web/node_modules/.bin/prettier --check apps/web/src apps/web/index.html apps/web/vite.config.ts tools/dev-db/server.mjs tools/browser/*.mjs
package:
	$(PY) scripts/package_source.py
ledger:
	$(PY) scripts/build_completion_ledger.py
