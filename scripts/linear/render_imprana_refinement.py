#!/usr/bin/env python3
"""Render separate native refinement payloads; never write to Linear.

The original import is preserved. Re-run after task receipt reconciliation to
include native links. The story body is appended, never substituted for source.
"""

import argparse
import hashlib
import json
import re
import subprocess
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "docs/product/refinement"
REPOSITORY = "https://github.com/nakul175/impact-platform"
SOURCE = "8a1e405f0086033dfb25ad834689a08bfe9f1eea"
PLANNING_BASELINE = "4cee364036d937c6ce0cff6d009f3d79c83b9cd2"
BASE = ROOT / "docs/product/linear/checkpoint.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_prose(value):
    """Prevent Linear from inventing website links for filenames/capabilities.

    Protect intentional Markdown links and URLs; no source Gherkin is rendered
    by this function. Linear returns escaped dots as their original characters.
    """
    protected = []

    def protect(match):
        protected.append(match.group(0))
        return f"\x00PROTECTED{len(protected) - 1}\x00"

    value = re.sub(r"\[[^\]\n]*\]\(https?://[^\s)]+\)|https?://[^\s)]+", protect, value)
    value = re.sub(
        r"(?<![\w\\])(?:[A-Za-z_][\w-]*\.)+[\w-]+",
        lambda match: match.group(0).replace(".", "\\."),
        value,
    )
    for index, original in enumerate(protected):
        value = value.replace(f"\x00PROTECTED{index}\x00", original)
    return value


@lru_cache(maxsize=None)
def code_link(path):
    kind = "tree" if (ROOT / path).is_dir() else "blob"
    for revision in [SOURCE, PLANNING_BASELINE]:
        found = subprocess.run(
            ["git", "cat-file", "-e", f"{revision}:{path}"],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        if found.returncode == 0:
            return f"[{path}]({REPOSITORY}/{kind}/{revision}/{path})"
    raise ValueError("Inspected anchor has no preserved Git baseline: " + path)


def bullets(items):
    return "\n".join("- " + item for item in items)


def task_description(task, story, checkpoint):
    parent = checkpoint["stories"][story["story_id"]]["url"]
    body = (
        f"<!-- imprana:task:{task['id']} -->\n\n"
        f"{task['description']}\n\n"
        "## Proposed acceptance criteria\n\n"
        + bullets(task["acceptance_criteria"])
        + f"\n\nParent story: [{story['story_id']}]({parent})\n\n"
        f"Release goal: {story['release_goal_id']}\n\n"
        f"Strategic objectives: {', '.join(story['strategic_objective_ids'])}\n\n"
        f"Task kind: {task['kind']}\n\n"
        "## Existing implementation anchors\n\n"
        + bullets([code_link(path) for path in task["code_paths"]])
        + "\n\nProposed prerequisites: "
        + (", ".join(task["depends_on"]) or "None within this proposed task slice")
        + "\n\nPlanning state: proposed Backlog task. Owner/engineer review, Ready decision, "
        "sprint selection and implementation are pending. Criteria and planned evidence "
        "are not executed test results. Recheck code and migration ledger before building."
    )
    return safe_prose(body)


def story_append(story, task_receipts):
    sid = story["story_id"]
    lines = [
        f"<!-- imprana:refinement:v1:{sid} -->",
        "## Complete backlog refinement proposal",
        "Prepared 10 October 2026 at Nakul's request. This is an additive planning proposal; "
        "the original acceptance/rejection criteria above remain the preserved baseline.",
        "### Bounded scope",
        story["scope"],
        "### Inspected implementation and reuse",
        bullets([code_link(a["path"]) + " — " + a["reuse_note"] for a in story["current_code"]]),
        "### Decisions before Ready",
        bullets(story["open_decisions"])
        if story["open_decisions"]
        else "No additional product decision identified in this proposal; engineer/owner review is still required.",
        "### Proposed story dependencies",
        bullets([f"{d['story_id']} ({d['kind']}): {d['rationale']}" for d in story["dependencies"]])
        if story["dependencies"]
        else "No additional cross-story dependency identified in this proposal.",
    ]
    if story.get("tooling_override"):
        value = story["tooling_override"]
        lines.extend(
            [
                "### Authorised tooling decision",
                value if isinstance(value, str) else json.dumps(value, ensure_ascii=False),
            ]
        )
    lines.append("### Proposed technical tasks")
    for task in story["tasks"]:
        receipt = task_receipts.get(task["id"])
        label = f"[{task['id']}]({receipt['url']})" if receipt else task["id"]
        lines.extend(
            [
                f"#### {label}: {task['title']}",
                task["description"],
                "Proposed task criteria:\n\n" + bullets(task["acceptance_criteria"]),
                "Proposed prerequisites: " + (", ".join(task["depends_on"]) or "None within this task slice"),
            ]
        )
    lines.extend(["### Scenario test plan", "Every entry below is proposed and unrun."])
    for test in story["test_plan"]:
        lines.extend(
            [
                "#### " + test["source_scenario"].removeprefix("Scenario: "),
                "Proposed level: " + test["level"],
                bullets(test["assertions"]),
                "Proposed evidence (unrun): " + test["proposed_evidence"],
            ]
        )
    lines.append(
        "Planning state: refined proposal. Ready, estimates, owners, sprint commitments, "
        "implementation evidence and product acceptance remain separate decisions. "
        "Cross-story dependency proposals are informational; only reviewed task prerequisites "
        "are represented as native blocking relationships."
    )
    return "\n\n" + safe_prose("\n\n".join(lines))


def build():
    document = json.loads((FOLDER / "backlog-refinement.json").read_text())
    plan = json.loads((FOLDER / "native-task-plan.json").read_text())
    checkpoint = json.loads(BASE.read_text())
    task_receipts = dict(checkpoint["tasks"])
    for path in sorted(FOLDER.glob("task-import-*.json")):
        data = json.loads(path.read_text())
        for canonical, receipt in data.get("tasks", {}).items():
            if canonical in task_receipts and receipt != task_receipts[canonical]:
                raise ValueError("Conflicting task receipt: " + canonical)
            task_receipts[canonical] = receipt
    stories = {s["story_id"]: s for s in document["stories"]}
    tasks = []
    for task in plan["new_tasks"]:
        story = stories[task["story_id"]]
        tasks.append(
            {
                "canonical_id": task["id"],
                "story_id": task["story_id"],
                "title": f"[{task['id']}] {task['title']}",
                "description": task_description(task, story, checkpoint),
                "parent_uuid": checkpoint["stories"][task["story_id"]]["uuid"],
                "milestone_uuid": checkpoint["milestones"][story["release_goal_id"]]["id"],
                "depends_on": task["depends_on"],
            }
        )
    return {
        "schema_version": "imprana-refinement-native-payload/v1",
        "refinement_sha256": digest(FOLDER / "backlog-refinement.json"),
        "native_plan_sha256": digest(FOLDER / "native-task-plan.json"),
        "counts": document["counts"],
        "new_tasks": tasks,
        "story_appends": [
            {
                "canonical_id": sid,
                "uuid": checkpoint["stories"][sid]["uuid"],
                "marker": f"<!-- imprana:refinement:v1:{sid} -->",
                "append": story_append(story, task_receipts),
                "source_gherkin_sha256": story["source_gherkin_sha256"],
            }
            for sid, story in stories.items()
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    output = FOLDER / "native-payloads.json"
    content = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not output.exists() or output.read_text() != content:
            raise SystemExit("Refinement native payloads are missing or stale")
    else:
        output.write_text(content)
    print(json.dumps({"mode": "check" if args.check else "build", "counts": payload["counts"]}))


if __name__ == "__main__":
    main()
