#!/usr/bin/env python3
"""Verify expanded native backlog, additive story plans and unchanged baseline.

Requires complete list metadata plus full get_issue descriptions/relations for
every issue. Raw descriptions and personal metadata remain in temporary files;
the saved report contains hashes, issue identities and check results only.
"""

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path

from build_imprana_refinement import build as build_proposal
from render_imprana_refinement import build as render_payload
from verify_imprana_readback import (
    REQUIRED_FIELDS,
    labels,
    protected_markdown,
    read_json,
    reference,
    string_hash,
    task_criteria,
    verify,
)

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "docs/product/refinement"


def canonical(issue):
    return issue["title"].split("]", 1)[0].removeprefix("[")


def run(before, before_hash, after, after_hash):
    base_plan, base_hash = read_json(ROOT / "docs/product/linear/import-plan.json")
    checkpoint, checkpoint_hash = read_json(ROOT / "docs/product/linear/checkpoint.json")
    refinement, refinement_hash = read_json(FOLDER / "backlog-refinement.json")
    native_plan, native_plan_hash = read_json(FOLDER / "native-task-plan.json")
    payload, payload_hash = read_json(FOLDER / "native-payloads.json")
    expected_refinement, expected_plan = build_proposal()
    expected_payload = render_payload()
    failures = []
    records = []
    before_by = {canonical(i): i for i in before["issues"]}
    after_by = {canonical(i): i for i in after["issues"]}
    original_ids = {i["canonical_id"] for i in base_plan["issues"]}
    new_tasks = {i["canonical_id"]: i for i in expected_payload["new_tasks"]}
    appends = {i["canonical_id"]: i for i in expected_payload["story_appends"]}
    receipts = dict(checkpoint["tasks"])
    for path in sorted(FOLDER.glob("task-import-*.json")):
        receipts.update(json.loads(path.read_text()).get("tasks", {}))
    resolver = {}
    for canonical_id, issue in after_by.items():
        for key in ["id", "uuid"]:
            resolver[issue[key]] = canonical_id

    def global_check(name, condition):
        if not condition:
            failures.append({"code": name})

    global_check("before_exact_baseline_coverage", set(before_by) == original_ids)
    global_check("refinement_matches_author_shards", refinement == expected_refinement)
    global_check("native_plan_matches_complete_proposal", native_plan == expected_plan)
    global_check("payload_matches_regeneration", payload == expected_payload)
    global_check("payload_current_native_plan_hash", payload.get("native_plan_sha256") == native_plan_hash)
    global_check(
        "payload_full_story_set",
        len(payload.get("story_appends", [])) == 368
        and {i["canonical_id"] for i in payload.get("story_appends", [])} == set(appends),
    )
    global_check(
        "payload_full_new_task_set",
        len(payload.get("new_tasks", [])) == len(new_tasks)
        and {i["canonical_id"] for i in payload.get("new_tasks", [])} == set(new_tasks),
    )
    global_check("after_exact_expanded_coverage", set(after_by) == original_ids | set(new_tasks))
    global_check("unique_canonical_ids", len(after_by) == len(after["issues"]))
    global_check("unique_native_ids", len({i["id"] for i in after["issues"]}) == len(after["issues"]))
    global_check("unique_native_uuids", len({i["uuid"] for i in after["issues"]}) == len(after["issues"]))
    global_check("pagination_complete", after.get("pagination_complete") is True)
    global_check("payload_matches_refinement", payload["refinement_sha256"] == refinement_hash)
    global_check("task_receipts_complete", set(new_tasks) <= set(receipts))

    baseline_issues = []
    baseline_relations = {}
    protected_fields = [
        "id",
        "uuid",
        "title",
        "status",
        "estimate",
        "parentId",
        "projectMilestone",
        "projectId",
        "teamId",
        "cycleId",
        "assigneeId",
        "dueDate",
    ]
    for sid in sorted(original_ids):
        if sid not in before_by or sid not in after_by:
            continue
        previous, current = before_by[sid], after_by[sid]
        row = {"canonical_id": sid, "native_id": current["id"], "checks": {}}

        def check(name, condition):
            row["checks"][name] = bool(condition)
            if not condition:
                failures.append({"code": name, "canonical_id": sid})

        check("metadata_unchanged", all(previous.get(k) == current.get(k) for k in protected_fields))
        check("labels_unchanged", labels(previous.get("labels")) == labels(current.get("labels")))
        description = current["description"]
        if sid in appends:
            proposal = appends[sid]
            marker = proposal["marker"]
            check("refinement_marker_once", description.count(marker) == 1)
            before_body, separator, added = description.partition(marker)
            check(
                "original_description_preserved",
                protected_markdown(before_body) == protected_markdown(previous["description"]),
            )
            check(
                "refinement_text_matches",
                bool(separator)
                and protected_markdown(marker + added) == protected_markdown(proposal["append"]),
            )
            baseline_description = before_body
        else:
            check(
                "original_description_preserved",
                protected_markdown(description) == protected_markdown(previous["description"]),
            )
            baseline_description = description
        row["native_description_sha256"] = string_hash(description)
        records.append(row)
        baseline_record = copy.deepcopy(current)
        baseline_record["description"] = baseline_description
        baseline_issues.append(baseline_record)
        if sid.startswith("TASK-"):
            baseline_relations[sid] = current
    baseline_snapshot = {
        "issues": baseline_issues,
        "pagination_complete": True,
        "task_relations": baseline_relations,
    }
    baseline_report = verify(baseline_snapshot, after_hash, base_plan, base_hash, checkpoint, checkpoint_hash)
    global_check("original_446_baseline_still_verified", not baseline_report["failures"])
    expected_new_edges = []
    actual_new_edges = []
    for tid, planned in new_tasks.items():
        if tid not in after_by:
            continue
        current = after_by[tid]
        receipt = receipts.get(tid, {})
        row = {"canonical_id": tid, "native_id": current["id"], "checks": {}}

        def check(name, condition):
            row["checks"][name] = bool(condition)
            if not condition:
                failures.append({"code": name, "canonical_id": tid})

        check("all_required_fields_present", REQUIRED_FIELDS <= set(current))
        check("receipt_identity_exact", all(current.get(k) == receipt.get(k) for k in ["id", "uuid", "url"]))
        check("title_exact", current["title"] == planned["title"])
        check("project_exact", current["projectId"] == checkpoint["project"]["uuid"])
        check("team_exact", current["teamId"] == checkpoint["team"]["id"])
        check("parent_exact", resolver.get(reference(current["parentId"])) == planned["story_id"])
        check("release_exact", reference(current["projectMilestone"]) == planned["milestone_uuid"])
        check("status_backlog", current["status"] == "Backlog")
        check(
            "planning_labels",
            {"Imprana Technical task", "Imprana Needs refinement"} <= labels(current["labels"]),
        )
        check(
            "no_estimate_assignment_cycle_date",
            all(current.get(k) is None for k in ["estimate", "assigneeId", "cycleId", "dueDate"]),
        )
        check(
            "description_exact_normalized",
            protected_markdown(current["description"]) == protected_markdown(planned["description"]),
        )
        check(
            "task_criteria_exact_normalized",
            task_criteria(current["description"]) == task_criteria(planned["description"]),
        )
        check("task_marker_once", current["description"].count(f"<!-- imprana:task:{tid} -->") == 1)
        relations = current.get("relations", {}).get("blockedBy", [])
        actual = [resolver.get(reference(r)) for r in relations]
        check(
            "task_dependencies_exact",
            len(actual) == len(planned["depends_on"]) and set(actual) == set(planned["depends_on"]),
        )
        expected_new_edges.extend((tid, prerequisite) for prerequisite in planned["depends_on"])
        actual_new_edges.extend((tid, prerequisite) for prerequisite in actual)
        row["description_sha256"] = string_hash(current["description"])
        row["criteria_count"] = len(task_criteria(current["description"]))
        records.append(row)
    global_check("new_dependency_graph_exact", sorted(expected_new_edges) == sorted(actual_new_edges))
    return {
        "schema_version": "imprana-refinement-readback/v1",
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "result": "PASS" if not failures else "FAIL",
        "scope": "Planning-object and original-criteria verification; no product tests executed",
        "before_snapshot_sha256": before_hash,
        "after_snapshot_sha256": after_hash,
        "refinement_sha256": refinement_hash,
        "payload_sha256": payload_hash,
        "counts": {
            **refinement["counts"],
            "native_issues": len(after_by),
            "baseline_issues_protected": len(original_ids),
            "new_native_dependency_edges": len(actual_new_edges),
        },
        "baseline_report": baseline_report,
        "records": records,
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    before, before_hash = read_json(args.before)
    after, after_hash = read_json(args.after)
    report = run(before, before_hash, after, after_hash)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps({"result": report["result"], "counts": report["counts"], "failures": report["failures"]})
    )
    raise SystemExit(0 if report["result"] == "PASS" else 1)


if __name__ == "__main__":
    main()
