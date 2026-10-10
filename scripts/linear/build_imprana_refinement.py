#!/usr/bin/env python3
"""Build and validate the owner's requested complete backlog refinement proposal.

Preserves the original 446-issue import and 24-task baseline. This builder has no
external writes. Native import must reconcile current issue contents first.
"""

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/product/linear/import-plan.json"
ORIGINAL_TASKS = ROOT / "docs/product/technical-tasks.json"
FOLDER = ROOT / "docs/product/refinement"
SHARDS = [
    "backlog-refinement-000-123.json",
    "backlog-refinement-124-247.json",
    "backlog-refinement-248-367.json",
]
LEVELS = {"unit", "integration", "native", "browser", "smoke", "regression", "manual"}
KINDS = {"design", "implementation", "interface", "qualification", "governance"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def scenario_name(value):
    return value.removeprefix("Scenario: ")


def existing_path(value):
    require(isinstance(value, str) and value.strip(), "Empty anchor path")
    path = (ROOT / value).resolve()
    require(
        path.is_relative_to(ROOT)
        and path != ROOT
        and (path.is_file() or path.is_dir())
        and not {".local", ".git", "secrets.env"}.intersection(path.relative_to(ROOT).parts),
        "Missing/outside/private code anchor: " + value,
    )


def acyclic(graph):
    pending = {key: set(value) for key, value in graph.items()}
    while pending:
        ready = {key for key, value in pending.items() if not value}
        if not ready:
            return False
        pending = {key: value - ready for key, value in pending.items() if key not in ready}
    return True


def build():
    baseline = json.loads(BASE.read_text())
    source = baseline["source"]
    require(digest(ROOT / source["path"]) == source["sha256"], "Original CSV changed")
    expected = [item for item in baseline["issues"] if item["kind"] == "story"]
    by_id = {item["canonical_id"]: item for item in expected}
    original_tasks = json.loads(ORIGINAL_TASKS.read_text())["tasks"]
    preserved = {task["id"]: task for task in original_tasks}
    records = []
    shard_refs = []
    for name, limits in zip(SHARDS, [(0, 124), (124, 248), (248, 368)], strict=True):
        path = FOLDER / name
        data = json.loads(path.read_text())
        require(data["source_commit"] == source["commit"], name + ": incorrect source commit")
        require(data["story_offsets"] == list(limits), name + ": incorrect range")
        want = {item["canonical_id"] for item in expected[limits[0] : limits[1]]}
        ids = [item["story_id"] for item in data["stories"]]
        require(len(ids) == len(set(ids)) and set(ids) == want, name + ": incomplete/duplicate coverage")
        records.extend(data["stories"])
        shard_refs.append(
            {"path": "docs/product/refinement/" + name, "sha256": digest(path), "stories": len(ids)}
        )
    require(len(records) == 368, "Expected all 368 active stories")
    record_by_id = {item["story_id"]: item for item in records}
    records = [record_by_id[item["canonical_id"]] for item in expected]
    all_tasks = []
    native_new_tasks = []
    tests_by_level = Counter()
    total_scenarios = 0
    for record in records:
        sid = record["story_id"]
        story = by_id[sid]
        require(
            record["source_gherkin_sha256"] == story["source"]["gherkin_sha256"],
            sid + ": Gherkin hash mismatch",
        )
        require(record["release_goal_id"] == story["release_goal_id"], sid + ": release mismatch")
        require(
            record["strategic_objective_ids"] == story["strategic_objective_ids"], sid + ": strategy mismatch"
        )
        require(
            isinstance(record["scope"], str) and len(record["scope"].strip()) >= 30,
            sid + ": missing bounded scope",
        )
        require(isinstance(record["open_decisions"], list), sid + ": decisions must be explicit")
        require(record["current_code"], sid + ": missing inspected reuse anchors")
        for anchor in record["current_code"]:
            existing_path(anchor["path"])
            require(len(anchor["reuse_note"].strip()) >= 15, sid + ": missing reuse observation")
        for dep in record["dependencies"]:
            require(dep["story_id"] in by_id and dep["story_id"] != sid, sid + ": invalid dependency")
            require(dep["kind"] in {"prerequisite", "related"}, sid + ": unknown dependency kind")
            require(len(dep["rationale"].strip()) >= 10, sid + ": missing dependency rationale")
        headers = re.findall(
            r"^Scenario: (.+)$", story["source_record"]["Acceptance and rejection criteria (Gherkin)"], re.M
        )
        covered = []
        for test in record["test_plan"]:
            name = scenario_name(test["source_scenario"])
            require(name in headers, sid + ": invented/changed scenario name: " + name)
            require(test["level"] in LEVELS, sid + ": unknown test level")
            require(
                test["assertions"]
                and all(isinstance(item, str) and item.strip() for item in test["assertions"]),
                sid + ": missing observable assertions",
            )
            require(
                isinstance(test["proposed_evidence"], str) and test["proposed_evidence"].strip(),
                sid + ": missing planned evidence",
            )
            covered.append(name)
            tests_by_level[test["level"]] += 1
        require(set(covered) == set(headers), sid + ": incomplete original scenario coverage")
        total_scenarios += len(headers)
        tasks = record["tasks"]
        existing = [task for task in original_tasks if task["story_id"] == sid]
        if existing:
            require(
                {task["id"] for task in tasks} == {task["id"] for task in existing},
                sid + ": existing task IDs changed",
            )
        else:
            require(3 <= len(tasks) <= 5, sid + ": expected 3-5 meaningful tasks")
        for task in tasks:
            tid = task["id"]
            require(
                task["story_id"] == sid and re.fullmatch("TASK-" + re.escape(sid) + r"-\d{2}", tid),
                sid + ": invalid child task identity",
            )
            require(
                isinstance(task["title"], str) and len(task["title"].strip()) >= 12,
                tid + ": missing specific title",
            )
            require(
                isinstance(task["description"], str) and len(task["description"].strip()) >= 40,
                tid + ": missing concrete deliverable",
            )
            require(
                isinstance(task["acceptance_criteria"], list) and len(task["acceptance_criteria"]) >= 2,
                tid + ": missing task criteria",
            )
            require(
                all(
                    isinstance(value, str) and len(value.strip()) >= 15
                    for value in task["acceptance_criteria"]
                ),
                tid + ": incomplete criterion",
            )
            require(task["kind"] in KINDS, tid + ": invalid task kind")
            for path in task["code_paths"]:
                existing_path(path)
            if tid in preserved:
                require(
                    all(task[key] == value for key, value in preserved[tid].items()),
                    tid + ": original 24-task core changed",
                )
            else:
                require(
                    all(dep in {other["id"] for other in tasks} for dep in task["depends_on"]),
                    tid + ": new hard dependency outside own reviewed task slice",
                )
                position = [other["id"] for other in tasks].index(tid)
                require(
                    set(task["depends_on"]) <= {other["id"] for other in tasks[:position]},
                    tid + ": prerequisite must precede its dependent for recoverable creation",
                )
                native_new_tasks.append(
                    {
                        **task,
                        "canonical_id": tid,
                        "parent_id": sid,
                        "epic_id": story["epic_id"],
                        "milestone_id": story["milestone_id"],
                        "release_goal_id": story["release_goal_id"],
                        "strategic_objective_ids": story["strategic_objective_ids"],
                        "status": "Backlog",
                    }
                )
            all_tasks.append(task)
        record["planning_state"] = (
            "Refined proposal; owner/engineer Ready review and sprint commitment pending"
        )
        record["source_story_title"] = story["source_record"]["Title"]
        record["epic_id"] = story["epic_id"]
    task_ids = [task["id"] for task in all_tasks]
    require(len(set(task_ids)) == len(task_ids), "Duplicate task identity")
    graph = {task["id"]: task["depends_on"] for task in all_tasks}
    require(all(dep in graph for deps in graph.values() for dep in deps), "Unknown task prerequisite")
    require(acyclic(graph), "Technical task dependency cycle")
    edge_count = sum(len(value) for value in graph.values())
    document = {
        "schema_version": "imprana-complete-refinement/v1",
        "source": source,
        "baseline_import_plan_sha256": digest(BASE),
        "original_technical_tasks_sha256": digest(ORIGINAL_TASKS),
        "planning_state": "Refined proposal; no Ready, sprint commitment, implementation, test run or product acceptance implied",
        "shards": shard_refs,
        "counts": {
            "stories": len(records),
            "epics": len({record["epic_id"] for record in records}),
            "original_scenarios_covered": total_scenarios,
            "test_plan_entries": sum(tests_by_level.values()),
            "test_entries_by_level": dict(tests_by_level),
            "existing_tasks_preserved": len(preserved),
            "new_tasks": len(native_new_tasks),
            "total_technical_tasks": len(all_tasks),
            "task_dependency_edges": edge_count,
        },
        "stories": records,
    }
    plan = {
        "schema_version": "imprana-refinement-native-plan/v1",
        "source_commit": source["commit"],
        "baseline_checkpoint": "docs/product/linear/checkpoint.json",
        "planning_commit": "4cee364036d937c6ce0cff6d009f3d79c83b9cd2",
        "counts": document["counts"],
        "new_tasks": native_new_tasks,
    }
    return document, plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        document, plan = build()
        outputs = {FOLDER / "backlog-refinement.json": document, FOLDER / "native-task-plan.json": plan}
        for path, data in outputs.items():
            body = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            if args.check:
                require(
                    path.exists() and path.read_text() == body, "Out of date: " + str(path.relative_to(ROOT))
                )
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body, encoding="utf-8")
        print(json.dumps({"status": "PASS", **document["counts"]}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "FAIL", "reason": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
