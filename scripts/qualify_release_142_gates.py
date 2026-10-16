"""Bind the reviewed 56-story gate map to actual JUnit results, preserving skips as unpassed."""

import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", type=Path, required=True)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    path = ROOT / "docs/acceptance/RELEASE-1.42-THREE-GATE-TEST-MAP.json"
    mapping = json.loads(path.read_text())
    root = ET.parse(args.junit).getroot()
    cases = list(root.iter("testcase"))

    def passed(case):
        return not any(case.find(kind) is not None for kind in ("failure", "error", "skipped"))

    results = []
    for issue, story in mapping["stories"].items():
        module = story["test_file"].removesuffix(".py").replace("/", ".")
        evidence, missing = [], []
        for name in story["nodes"]:
            found = [
                case
                for case in cases
                if case.get("classname") == module and case.get("name", "").split("[")[0] == name
            ]
            if not found:
                missing.append(f"{story['test_file']}::{name}")
            evidence.extend(found)
        for suite in story.get("supplemental_gate_suites", []):
            module = suite["test_file"].removesuffix(".py").replace("/", ".")
            found = [
                case
                for case in cases
                if case.get("classname") == module and suite["parameter_id_contains"] in case.get("name", "")
            ]
            if not found:
                missing.append(f"{suite['test_file']}::*[{suite['parameter_id_contains']}]")
            evidence.extend(found)
        results.append(
            {
                "issue": issue,
                "bounded_three_gate_evidence_passed": bool(evidence)
                and not missing
                and all(map(passed, evidence)),
                "executed_nodes": [f"{case.get('classname')}::{case.get('name')}" for case in evidence],
                "missing_nodes": missing,
                "unpassed_nodes": [
                    f"{case.get('classname')}::{case.get('name')}" for case in evidence if not passed(case)
                ],
            }
        )
    total = sum(row["bounded_three_gate_evidence_passed"] for row in results)
    report = {
        "source_head": args.source_head,
        "scope": mapping["scope"],
        "map_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "junit_sha256": hashlib.sha256(args.junit.read_bytes()).hexdigest(),
        "full_run": {
            "passed": sum(map(passed, cases)),
            "failed": sum(case.find("failure") is not None for case in cases),
            "errors": sum(case.find("error") is not None for case in cases),
            "skipped": sum(case.find("skipped") is not None for case in cases),
        },
        "cohort_size": 56,
        "bounded_local_gates": {
            gate: total for gate in ("positive_journey", "authorization_refusal", "error_recovery")
        },
        "runtime_blocked": mapping["blocked_reserved_use_cases"],
        "owner_acceptance_count": 0,
        "stories": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"bounded_gate_pass_count": total, "cohort": 56, "full_run": report["full_run"]}))


if __name__ == "__main__":
    main()
