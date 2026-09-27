#!/usr/bin/env bash
set -euo pipefail
mode="${1:-static}"
python_bin="${IMPACT_PYTHON:-python3}"
case "$mode" in
  static)
    "$python_bin" -m unittest discover -s tests -p 'test_contracts.py'
    "$python_bin" -m unittest discover -s tests -p 'test_controls.py'
    "$python_bin" reference-v1/run_tests.py reference --report reports/reference.json
    ;;
  database)
    "$python_bin" database/migrate.py
    "$python_bin" fixtures/load.py
    "$python_bin" tests/run_database.py
    ;;
  application)
    "$python_bin" reference-v1/run_tests.py integration --report reports/integration.json
    "$python_bin" reference-v1/run_tests.py smoke --report reports/smoke.json
    ;;
  release)
    bash environment/ci.sh static
    bash environment/ci.sh database
    bash environment/ci.sh application
    "$python_bin" environment/check_release_inputs.py
    ;;
  *) echo 'Use static, database, application or release'; exit 2 ;;
esac
