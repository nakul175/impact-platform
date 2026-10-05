"""Offline reuse feasibility checks; synthetic data, no database or upstream dependencies.

Scenario inspiration: mercycorps/toladata at 7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d,
indicators/tests/iptt_tests/scenarios.py and indicators/queries/targets_queries.py.
Newly authored checks use Impact Platform semantics, not upstream arithmetic or permissions.
Run from the repository root: python3 tools/reuse/toladata_probe.py
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps/api"))

from impact_api.domain import calculate  # noqa: E402


def definition(rule="SUM", semantic="FLOW", kind="DECIMAL"):
    return {
        "combination_rule": rule,
        "time_semantic": semantic,
        "measurement_type": kind,
        "unit": "synthetic units",
        "display_decimals": 2,
    }


def row(value, day=1, approval="APPROVED", state="PRESENT", **extra):
    return {
        "value": value,
        "event_at": f"2026-08-{day:02d}T00:00:00Z",
        "approval_state": approval,
        "value_state": state,
        **extra,
    }


class TolaDataReuseProbe(unittest.TestCase):
    """Exercise scenario families seen upstream against the actual local domain functions."""

    def test_no_results_is_undefined(self):
        result = calculate(definition(), [])
        self.assertEqual((result["value"], result["reason_code"]), (None, "NO_APPROVED_VALUES"))

    def test_one_result(self):
        self.assertEqual(calculate(definition(), [row("12.5")])["value"], "12.5")

    def test_multiple_flow_results_are_summed(self):
        self.assertEqual(calculate(definition(), [row("12.5"), row("7.5", 2)])["value"], "20")

    def test_explicit_zero_is_a_result(self):
        result = calculate(definition(), [row("0")])
        self.assertEqual((result["value_state"], result["value"]), ("PRESENT", "0"))

    def test_blank_does_not_become_zero(self):
        result = calculate(definition(), [row(None, state="MISSING")])
        self.assertEqual(result["value_state"], "UNDEFINED")

    def test_pending_and_returned_results_do_not_contribute(self):
        rows = [row("12"), row("100", 2, "SUBMITTED"), row("200", 3, "RETURNED")]
        self.assertEqual(calculate(definition(), rows)["value"], "12")

    def test_cumulative_positions_are_not_summed(self):
        rows = [row("10", 1), row("25", 2), row("40", 3)]
        self.assertEqual(calculate(definition("LAST_VALID", "CUMULATIVE"), rows)["value"], "40")

    def test_cumulative_decline_is_withheld(self):
        result = calculate(definition("LAST_VALID", "CUMULATIVE"), [row("40"), row("25", 2)])
        self.assertEqual((result["value"], result["reason_code"]), (None, "CUMULATIVE_DECLINE"))

    def test_latest_is_event_order_not_input_order(self):
        rows = [row("40", 3), row("10", 1), row("25", 2)]
        self.assertEqual(calculate(definition("LAST_VALID", "CUMULATIVE"), rows)["value"], "40")

    def test_conflicting_latest_positions_are_withheld(self):
        result = calculate(definition("LAST_VALID", "STOCK"), [row("10"), row("20")])
        self.assertEqual((result["value"], result["reason_code"]), (None, "TIED_LATEST_VALUES"))

    def test_percentage_is_pooled_not_latest_or_average(self):
        rows = [
            row("50", numerator="50", denominator="100"),
            row("10", 2, numerator="1", denominator="10"),
        ]
        result = calculate(definition("POOLED_RATIO", "FLOW", "PERCENTAGE"), rows)
        self.assertEqual((result["numerator"], result["denominator"]), ("51", "110"))
        self.assertEqual(result["displayed_value"], "46.36")

    def test_zero_denominator_is_undefined(self):
        result = calculate(
            definition("POOLED_RATIO", "FLOW", "PERCENTAGE"),
            [row("0", numerator="0", denominator="0")],
        )
        self.assertEqual((result["value"], result["reason_code"]), (None, "ZERO_DENOMINATOR"))

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TolaDataReuseProbe)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({
        "scope": "offline calculation compatibility probe; no API, database, staging or acceptance evidence",
        "upstream_commit": "7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "successful": result.wasSuccessful(),
    }, indent=2))
    sys.exit(0 if result.wasSuccessful() else 1)
