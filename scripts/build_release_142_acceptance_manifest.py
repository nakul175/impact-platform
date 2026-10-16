#!/usr/bin/env python3
"""Build the review manifest for the 56-story release 1.42 qualification cohort."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "docs/acceptance/RELEASE-1.42-56-STORY-ACCEPTANCE.json"
OUTPUT_MD = ROOT / "docs/acceptance/RELEASE-1.42-56-STORY-ACCEPTANCE.md"

# Unique first occurrence in the sequential release notes 0.86 through 1.42.
COHORT = [
    ("APL-351", "FR-ACC-004"),
    ("APL-352", "FR-ACC-005"),
    ("APL-353", "FR-ACC-006"),
    ("APL-354", "FR-ACC-011"),
    ("APL-338", "FR-AI-001"),
    ("APL-340", "FR-AI-011"),
    ("APL-341", "FR-AI-012"),
    ("APL-342", "FR-AI-013"),
    ("APL-343", "FR-AI-014"),
    ("APL-344", "FR-AI-015"),
    ("APL-345", "FR-AI-016a"),
    ("APL-346", "FR-AI-016b"),
    ("APL-718", "FR-AI-017"),
    ("APL-347", "FR-AI-018"),
    ("APL-531", "FR-AI-002"),
    ("APL-533", "FR-AI-003"),
    ("APL-535", "FR-AI-004"),
    ("APL-537", "FR-AI-005"),
    ("APL-538", "FR-AI-006"),
    ("APL-339", "FR-AI-007"),
    ("APL-597", "FR-AI-008"),
    ("APL-601", "FR-AI-009"),
    ("APL-541", "FR-AI-010"),
    ("APL-402", "FR-CAL-003"),
    ("APL-405", "FR-CAL-005"),
    ("APL-408", "FR-CAL-008"),
    ("APL-411", "FR-CAL-009"),
    ("APL-415", "FR-CAL-010"),
    ("APL-421", "FR-CAL-011"),
    ("APL-607", "FR-CAL-013"),
    ("APL-424", "FR-CAL-015"),
    ("APL-611", "FR-CAL-016"),
    ("APL-610", "FR-ANA-001"),
    ("APL-434", "FR-ANA-002"),
    ("APL-435", "FR-ANA-003"),
    ("APL-437", "FR-ANA-004"),
    ("APL-613", "FR-ANA-005"),
    ("APL-616", "FR-ANA-006"),
    ("APL-612", "FR-ANA-007"),
    ("APL-614", "FR-ANA-008"),
    ("APL-618", "FR-ANA-009"),
    ("APL-620", "FR-ANA-010"),
    ("APL-623", "FR-DQ-007"),
    ("APL-625", "FR-EVA-001"),
    ("APL-630", "FR-EVA-002"),
    ("APL-632", "FR-EVA-003"),
    ("APL-634", "FR-EVA-006"),
    ("APL-639", "FR-EVA-007"),
    ("APL-641", "FR-EVD-005"),
    ("APL-644", "FR-EVD-006"),
    ("APL-646", "FR-EVD-008"),
    ("APL-648", "FR-FIN-002"),
    ("APL-650", "FR-FIN-003"),
    ("APL-652", "FR-FIN-005"),
    ("APL-364", "US-DX-03"),
    ("APL-350", "FR-ACC-003"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refinement_stories() -> dict[str, dict]:
    stories: dict[str, dict] = {}
    for path in sorted((ROOT / "docs/product/refinement").glob("backlog-refinement-*.json")):
        for story in json.loads(path.read_text())["stories"]:
            stories[story["story_id"]] = story
    return stories


def evidence_candidates(linear_id: str, story_id: str) -> tuple[list[str], list[str]]:
    needles = (linear_id, story_id)
    tests: list[str] = []
    releases: list[str] = []
    for directory, destination in (("qualification", tests), ("tools/browser", tests), ("docs", releases)):
        root = ROOT / directory
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".mjs", ".md"}:
                continue
            try:
                text = path.read_text()
            except UnicodeDecodeError:
                continue
            if any(needle in text for needle in needles):
                destination.append(str(path.relative_to(ROOT)))
    release_records = sorted(
        path
        for path in set(releases)
        if "/RELEASE-" in f"/{path}" and not path.startswith("docs/acceptance/")
    )
    for release in release_records:
        text = (ROOT / release).read_text()
        for candidate in re.findall(r"(?:qualification|tools/browser)/[A-Za-z0-9_./-]+\.(?:py|mjs)", text):
            if (ROOT / candidate).is_file():
                tests.append(candidate)
        for name in re.findall(r"`(test_[A-Za-z0-9_]+\.py)`", text):
            matches = list((ROOT / "qualification").glob(name))
            tests.extend(str(path.relative_to(ROOT)) for path in matches)
    return sorted(set(tests)), release_records


def main() -> None:
    stories = refinement_stories()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    entries = []
    for ordinal, (linear_id, story_id) in enumerate(COHORT, 1):
        source = stories[story_id]
        tests, releases = evidence_candidates(linear_id, story_id)
        scenarios = [
            {
                "source_scenario": item["source_scenario"],
                "level": item["level"],
                "assertions": item["assertions"],
                "acceptance_status": "PENDING_EXACT_EVIDENCE_REVIEW",
                "accepted_by": None,
                "accepted_at": None,
            }
            for item in source["test_plan"]
        ]
        entries.append(
            {
                "ordinal": ordinal,
                "linear_issue": linear_id,
                "story_id": story_id,
                "source_gherkin_sha256": source["source_gherkin_sha256"],
                "scenario_count": len(scenarios),
                "assertion_count": sum(len(item["assertions"]) for item in scenarios),
                "candidate_test_files": tests,
                "release_records": releases,
                "scenarios": scenarios,
                "all_acceptance_criteria_accepted": False,
                "product_owner_acceptance": "PENDING",
            }
        )
    manifest = {
        "schema_version": 1,
        "release": "1.42",
        "candidate_head": head,
        "cohort_definition": "Unique first occurrence in sequential release notes 0.86 through 1.42",
        "cohort_count": len(entries),
        "source_files": {
            "backlog": "docs/backlog/backlog.csv",
            "backlog_sha256": sha256(ROOT / "docs/backlog/backlog.csv"),
            "refinement": "docs/product/refinement/backlog-refinement-000-123.json through backlog-refinement-248-367.json",
        },
        "accepted_story_count": 0,
        "acceptance_state": "PENDING_EXACT_CRITERION_EVIDENCE_AND_PRODUCT_OWNER_ACCEPTANCE",
        "human_gates": [
            "Independent human PR approval",
            "Applicable security/accessibility/manual review",
            "Product owner acceptance for every story at sprint review",
        ],
        "stories": entries,
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(manifest, indent=2) + "\n")
    lines = [
        "# Release 1.42 — 56-story acceptance manifest",
        "",
        f"Candidate source head: `{head}`.",
        "",
        "This file freezes the review cohort and its source criteria. Candidate files are discovery hints, not proof that a criterion passed. A criterion remains pending until an exact assertion/run receipt is reviewed, and product-owner acceptance is recorded separately.",
        "",
        "| # | Story | Linear | Scenarios | Assertions | Candidate tests | Acceptance |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    for item in entries:
        lines.append(
            f"| {item['ordinal']} | {item['story_id']} | {item['linear_issue']} | "
            f"{item['scenario_count']} | {item['assertion_count']} | "
            f"{len(item['candidate_test_files'])} | Pending |"
        )
    lines.extend(
        [
            "",
            "## Current gate",
            "",
            "Accepted: **0/56**. Exact criterion evidence review, independent human review, applicable manual checks and product-owner acceptance remain required.",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
