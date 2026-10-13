#!/usr/bin/env python3
"""Verify an offline native Linear read-back snapshot against the preserved plan.

The snapshot shape is {"issues": [selected list_issues records],
"task_relations": {"TASK-...": get_issue(includeRelations=True) record}}.
Raw MCP text-result wrappers are also accepted for task relation records.

    python3 scripts/linear/verify_imprana_readback.py --snapshot /tmp/readback.json
    python3 scripts/linear/verify_imprana_readback.py --snapshot /tmp/readback.json --output /tmp/report.json

Required issue fields: id, uuid, title, description, url, labels, status, estimate,
parentId, projectMilestone, projectId, teamId, cycleId, assigneeId and dueDate.
Selected list_issues descriptions can be truncated: replace them with the full
get_issue descriptions while keeping the list projection's explicit null fields.
The report stores identities, URLs, checks and hashes, never description content
or assignee names. A partial snapshot fails; no external calls are made.
"""

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLAN = ROOT / "docs/product/linear/import-plan.json"
DEFAULT_CHECKPOINT = ROOT / "docs/product/linear/checkpoint.json"
GHERKIN = "Acceptance and rejection criteria (Gherkin)"
KIND_GROUPS = {"epic": "epics", "story": "stories", "technical_task": "tasks"}
KIND_LABELS = {"epic": "Imprana Epic", "story": "Imprana Story", "technical_task": "Imprana Technical task"}
REQUIRED_FIELDS = {
    "id",
    "uuid",
    "title",
    "description",
    "url",
    "labels",
    "status",
    "estimate",
    "parentId",
    "projectMilestone",
    "projectId",
    "teamId",
    "cycleId",
    "assigneeId",
    "dueDate",
}
TITLE_ID = re.compile(r"^\[([^\]\r\n]+)\](?:[ \t]+|$)")
FENCES = re.compile(r"^(`{3,}|~{3,})[^\r\n]*\r?\n([\s\S]*?)\r?\n\1[ \t]*$", re.M)
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
NATIVE_ID = re.compile(r"^[A-Z][A-Z0-9]*-[0-9]+$")


def sha256(value):
    return hashlib.sha256(value).hexdigest()


def string_hash(value):
    return sha256(value.encode("utf-8"))


def read_json(path):
    raw = path.read_bytes()
    return json.loads(raw), sha256(raw)


def unwrap(value):
    if isinstance(value, str):
        return unwrap(json.loads(value))
    if isinstance(value, dict) and value.get("isError") is True:
        raise ValueError("MCP error result")
    if isinstance(value, dict) and "content" in value:
        for item in value["content"]:
            if item.get("type") == "text":
                try:
                    return json.loads(item["text"])
                except (ValueError, KeyError):
                    continue
    return value


def reference(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ["issue", "relatedIssue", "node"]:
            if isinstance(value.get(key), dict):
                result = reference(value[key])
                if result:
                    return result
        for key in ["uuid", "identifier", "issueId", "relatedIssueId", "id"]:
            if isinstance(value.get(key), str):
                return value[key]
    return None


def prose_normalize(text):
    """Normalize Markdown presentation outside protected fenced payloads only."""
    text = text.replace("\r\n", "\n")
    text = re.sub(r"(?m)^[ \t]*#{1,6}[ \t]+", "", text)
    text = re.sub(r"(?m)^([ \t]*)[*+-][ \t]+", r"\1- ", text)
    text = re.sub(r"<(https?://[^<>\s]+)>", r"\1", text)
    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!|>~])", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def protected_markdown(text):
    blocks = []
    outside = []
    position = 0
    for match in FENCES.finditer(text):
        outside.append(text[position : match.start()])
        outside.append(f"\x00PROTECTED_CODE_{len(blocks)}\x00")
        blocks.append(match.group(2))
        position = match.end()
    outside.append(text[position:])
    return blocks, prose_normalize("".join(outside))


def task_criteria(text):
    """Read the ordered flat acceptance list without keeping its Markdown bullets."""
    lines = text.splitlines()
    active = False
    criteria = []
    for line in lines:
        heading = re.sub(r"^[ \t]*#{1,6}[ \t]+", "", line).strip()
        if heading == "Proposed acceptance criteria":
            active = True
            continue
        if not active:
            continue
        if line.strip().startswith("Parent story:") or re.match(r"^[ \t]*#{1,6}[ \t]+", line):
            break
        match = re.match(r"^[ \t]*[*+-][ \t]+(.*)$", line)
        if match:
            criteria.append(match.group(1))
        elif line.strip() and criteria and line[:1].isspace():
            criteria[-1] += " " + line.strip()
        elif line.strip():
            break
    return [prose_normalize(criterion) for criterion in criteria]


def labels(value):
    if not isinstance(value, list):
        return set()
    return {
        item if isinstance(item, str) else item.get("name") for item in value if isinstance(item, (str, dict))
    }


def estimate_matches(value, expected):
    """Compare only the numeric estimate; Linear's display name is not evidence."""
    if isinstance(value, dict):
        value = value.get("value")
    return type(value) in {int, float} and value == expected


def safe_identity(value, pattern):
    return value if isinstance(value, str) and pattern.fullmatch(value) else None


def safe_url(value):
    if not isinstance(value, str):
        return None
    match = re.match(r"^(https://linear\.app/[^/]+/issue/[A-Z][A-Z0-9]*-[0-9]+)(?:/.*)?$", value)
    return match.group(1) if match else None


def verify(snapshot, snapshot_hash, plan, plan_hash, checkpoint, checkpoint_hash):
    failures = []
    records = []

    def fail(code, canonical_id=None, field=None, record=None):
        item = {"code": code}
        if canonical_id is not None:
            item["canonical_id"] = canonical_id
        if field is not None:
            item["field"] = field
        failures.append(item)
        if record is not None:
            record["failures"].append(code + (":" + field if field else ""))

    expected = {issue["canonical_id"]: issue for issue in plan["issues"]}
    if len(expected) != len(plan["issues"]):
        fail("duplicate_plan_canonical_id")
    if len(expected) != 446:
        fail("unexpected_plan_issue_count")
    if checkpoint.get("import_plan_sha256") != plan_hash:
        fail("checkpoint_plan_hash_mismatch")
    if checkpoint.get("source_csv_sha256") != plan["source"]["sha256"]:
        fail("checkpoint_source_csv_hash_mismatch")
    if checkpoint.get("source_commit") != plan["source"]["commit"]:
        fail("checkpoint_source_commit_mismatch")
    if snapshot.get("hasNextPage") is True or snapshot.get("pagination_complete") is False:
        fail("snapshot_pagination_incomplete")
    if snapshot.get("partial") is True:
        fail("snapshot_marked_partial")
    source_path = ROOT / plan["source"]["path"]
    source_rows = []
    if source_path.exists():
        if sha256(source_path.read_bytes()) != plan["source"]["sha256"]:
            fail("local_source_csv_hash_mismatch")
        with source_path.open(encoding="utf-8", newline="") as stream:
            source_rows = list(csv.DictReader(stream))
        original = {row["ID"]: row for row in source_rows}
        if len(source_rows) != 370 or len(original) != 370:
            fail("local_source_csv_record_count")
        preserved = {
            issue["source_id"]: issue["source_record"] for issue in plan["issues"] if issue["kind"] == "story"
        }
        preserved.update({item["source_id"]: item["source_record"] for item in plan["historical_documents"]})
        if preserved != original:
            fail("local_original_source_fields_mismatch")
    else:
        fail("local_source_csv_missing")
    task_source = plan.get("technical_tasks_source", {})
    task_source_path = ROOT / task_source.get("path", "docs/product/technical-tasks.json")
    if task_source_path.is_file():
        source_tasks, source_tasks_hash = read_json(task_source_path)
        if source_tasks_hash != task_source.get("sha256"):
            fail("local_technical_task_source_hash_mismatch")
        if (
            source_tasks.get("source_commit") != plan["source"]["commit"]
            or task_source.get("source_commit") != plan["source"]["commit"]
        ):
            fail("technical_task_source_commit_mismatch")
        task_rows = source_tasks.get("tasks", [])
        original_tasks = {task["id"]: task for task in task_rows}
        preserved_tasks = {
            issue["canonical_id"]: issue["source_record"]
            for issue in plan["issues"]
            if issue["kind"] == "technical_task"
        }
        if len(task_rows) != 24 or len(original_tasks) != 24:
            fail("local_technical_task_source_record_count")
        if preserved_tasks != original_tasks:
            fail("local_original_technical_task_fields_mismatch")
    else:
        fail("local_technical_task_source_missing")
    native_issues = snapshot.get("issues")
    if not isinstance(native_issues, list):
        native_issues = []
        fail("snapshot_issues_not_list")
    native_by_canonical = {}
    seen_native_ids = set()
    seen_uuids = set()
    resolver = {}
    for kind, group in KIND_GROUPS.items():
        entries = checkpoint.get(group, {})
        if set(entries) != {key for key, issue in expected.items() if issue["kind"] == kind}:
            fail("checkpoint_kind_coverage_mismatch", field=group)
        for canonical_id, entry in entries.items():
            if canonical_id not in expected or expected[canonical_id]["kind"] != kind:
                fail("unexpected_checkpoint_canonical_id")
                continue
            for key in ["id", "uuid"]:
                if isinstance(entry.get(key), str):
                    if entry[key] in resolver and resolver[entry[key]] != canonical_id:
                        fail("duplicate_checkpoint_native_identity", canonical_id, key)
                    resolver[entry[key]] = canonical_id
    for index, native in enumerate(native_issues):
        if not isinstance(native, dict):
            fail("native_record_not_object", field=str(index))
            continue
        match = TITLE_ID.match(native.get("title", "")) if isinstance(native.get("title"), str) else None
        canonical_id = match.group(1) if match else None
        if canonical_id not in expected:
            fail("unexpected_native_issue", field=str(index))
            continue
        if canonical_id in native_by_canonical:
            fail("duplicate_native_canonical_id", canonical_id)
        else:
            native_by_canonical[canonical_id] = native
        for key, seen, pattern in [("id", seen_native_ids, NATIVE_ID), ("uuid", seen_uuids, UUID)]:
            value = safe_identity(native.get(key), pattern)
            if value is None:
                fail("invalid_native_identity", canonical_id, key)
            elif value in seen:
                fail("duplicate_native_identity", canonical_id, key)
            else:
                seen.add(value)
                if value in resolver and resolver[value] != canonical_id:
                    fail("native_identity_resolves_to_other_canonical_id", canonical_id, key)
                resolver[value] = canonical_id
    for canonical_id in expected:
        if canonical_id not in native_by_canonical:
            fail("missing_native_issue", canonical_id)
    if len(native_issues) != len(expected):
        fail("native_issue_count_mismatch")
    project_uuid = checkpoint["project"]["uuid"]
    team_uuid = checkpoint["team"]["id"]
    if project_uuid != plan["target"]["project_id"]:
        fail("checkpoint_project_mismatch")
    milestones = checkpoint.get("milestones", {})
    if set(milestones) != {milestone["canonical_id"] for milestone in plan["milestones"]}:
        fail("checkpoint_milestone_coverage_mismatch")
    for canonical_id, planned in expected.items():
        native = native_by_canonical.get(canonical_id)
        if native is None:
            continue
        record = {
            "canonical_id": canonical_id,
            "kind": planned["kind"],
            "native_id": safe_identity(native.get("id"), NATIVE_ID),
            "native_uuid": safe_identity(native.get("uuid"), UUID),
            "url": safe_url(native.get("url")),
            "checks": {},
            "failures": [],
        }
        records.append(record)

        def check(name, condition, code=None):
            record["checks"][name] = bool(condition)
            if not condition:
                fail(code or name, canonical_id, record=record)

        missing_fields = sorted(REQUIRED_FIELDS - set(native))
        check("all_required_fields_present", not missing_fields)
        for field in missing_fields:
            fail("missing_native_field", canonical_id, field, record)
        check("title_exact", native.get("title") == planned["title"])
        check("native_url_valid", safe_url(native.get("url")) is not None)
        check(
            "native_url_identifier_exact",
            safe_url(native.get("url")) is not None
            and safe_url(native["url"]).endswith("/" + str(native.get("id"))),
        )
        check(
            "native_identifier_team_key_exact",
            isinstance(native.get("id"), str) and native["id"].startswith(checkpoint["team"]["key"] + "-"),
        )
        check("project_exact", native.get("projectId") == project_uuid)
        check("team_exact", native.get("teamId") == team_uuid)
        status = native.get("status")
        if isinstance(status, dict):
            status = status.get("name")
        check("status_exact", status == planned["status"])
        for field in ["cycleId", "assigneeId", "dueDate"]:
            check(field + "_unset", field in native and native[field] is None)
        point_value = native.get("estimate")
        if "estimate" in planned:
            check(
                "estimate_exact",
                estimate_matches(point_value, planned["estimate"]),
            )
        else:
            check("estimate_unset", "estimate" in native and point_value is None)
        expected_parent = planned["parent_id"]
        check(
            "parent_exact",
            native.get("parentId") is None
            if expected_parent is None
            else resolver.get(reference(native.get("parentId"))) == expected_parent,
        )
        expected_milestone = planned["milestone_id"]
        if expected_milestone is None:
            check("milestone_unset", "projectMilestone" in native and native["projectMilestone"] is None)
        else:
            milestone_uuid = milestones.get(expected_milestone, {}).get("id")
            check(
                "milestone_exact",
                isinstance(milestone_uuid, str)
                and reference(native.get("projectMilestone")) == milestone_uuid,
            )
        required_labels = {KIND_LABELS[planned["kind"]]}
        if planned["kind"] == "technical_task" or (
            planned["kind"] == "story" and planned["status"] == "Backlog"
        ):
            required_labels.add("Imprana Needs refinement")
        if planned["kind"] == "story" and planned["status"] == "In Review":
            required_labels.add("Imprana Sprint 1 acceptance")
        check("required_labels_present", required_labels <= labels(native.get("labels")))
        entry = checkpoint.get(KIND_GROUPS[planned["kind"]], {}).get(canonical_id)
        check("checkpoint_record_present", isinstance(entry, dict))
        if isinstance(entry, dict):
            check("checkpoint_native_id_exact", native.get("id") == entry.get("id"))
            check("checkpoint_native_uuid_exact", native.get("uuid") == entry.get("uuid"))
            check("checkpoint_url_exact", native.get("url") == entry.get("url"))
        description = native.get("description")
        if not isinstance(description, str):
            check("description_present", False)
            continue
        check(
            "description_not_truncated",
            "(truncated, use `get_issue` for full description)" not in description,
        )
        original_blocks, original_prose = protected_markdown(planned["description"])
        native_blocks, native_prose = protected_markdown(description)
        record["description_sha256"] = string_hash(description)
        record["normalized_outside_fence_sha256"] = string_hash(native_prose)
        record["expected_normalized_outside_fence_sha256"] = string_hash(original_prose)
        check("outside_fence_content_matches_normalized", native_prose == original_prose)
        check("fenced_payloads_exact", native_blocks == original_blocks)
        marker_kind = "task" if planned["kind"] == "technical_task" else planned["kind"]
        content_marker = f"<!-- imprana:{marker_kind}:{canonical_id} -->"
        check("content_marker_exactly_once", description.count(content_marker) == 1)
        if planned["kind"] == "story":
            original_gherkin = planned["source_record"][GHERKIN]
            gherkin_exact = len(native_blocks) == 1 and native_blocks[0].encode(
                "utf-8"
            ) == original_gherkin.encode("utf-8")
            check("original_gherkin_utf8_exact", gherkin_exact)
            native_gherkin_hash = string_hash(native_blocks[0]) if len(native_blocks) == 1 else None
            record["native_gherkin_sha256"] = native_gherkin_hash
            record["expected_gherkin_sha256"] = planned["source"]["gherkin_sha256"]
            check("original_gherkin_sha256_exact", native_gherkin_hash == planned["source"]["gherkin_sha256"])
        elif planned["kind"] == "technical_task":
            native_criteria = task_criteria(description)
            expected_criteria = [
                prose_normalize(text) for text in planned["source_record"]["acceptance_criteria"]
            ]
            check("task_criteria_order_and_text_exact_normalized", native_criteria == expected_criteria)
            record["task_criteria_count"] = len(native_criteria)
            record["task_criteria_sha256"] = [string_hash(text) for text in native_criteria]
    relation_snapshot = snapshot.get("task_relations")
    if not isinstance(relation_snapshot, dict):
        relation_snapshot = {}
        fail("task_relation_snapshot_not_object")
    expected_tasks = {key: item for key, item in expected.items() if item["kind"] == "technical_task"}
    record_by_id = {record["canonical_id"]: record for record in records}
    actual_edges = []
    expected_edges = [
        (key, dependency) for key, item in expected_tasks.items() for dependency in item["depends_on"]
    ]
    for canonical_id in relation_snapshot:
        if canonical_id not in expected_tasks:
            fail("unexpected_task_relation_record")
    for canonical_id, task in expected_tasks.items():
        record = record_by_id.get(canonical_id)
        if canonical_id not in relation_snapshot:
            fail("missing_task_relation_record", canonical_id, record=record)
            continue
        try:
            relation_issue = unwrap(relation_snapshot[canonical_id])
        except ValueError:
            relation_issue = None
        if not isinstance(relation_issue, dict):
            fail("invalid_task_relation_record", canonical_id, record=record)
            continue
        relation_references = [reference(relation_issue)]
        relation_references.extend(relation_issue[key] for key in ["id", "uuid"] if key in relation_issue)
        if not relation_references or any(
            resolver.get(identifier) != canonical_id for identifier in relation_references
        ):
            fail("task_relation_record_identity_mismatch", canonical_id, record=record)
        blocked_by = relation_issue.get("relations", {}).get("blockedBy")
        if not isinstance(blocked_by, list):
            fail("blocked_by_relations_missing", canonical_id, record=record)
            continue
        actual_dependencies = []
        for dependency in blocked_by:
            dependency_id = resolver.get(reference(dependency))
            if dependency_id is None:
                fail("unresolved_blocked_by_reference", canonical_id, record=record)
            else:
                actual_dependencies.append(dependency_id)
                actual_edges.append((canonical_id, dependency_id))
        dependencies_match = set(actual_dependencies) == set(task["depends_on"]) and len(
            actual_dependencies
        ) == len(set(actual_dependencies))
        if record is not None:
            record["checks"]["blocked_by_dependencies_exact"] = dependencies_match
            record["blocked_by_canonical_ids"] = sorted(set(actual_dependencies))
        if not dependencies_match:
            fail("blocked_by_dependencies_mismatch", canonical_id, record=record)
    if len(expected_edges) != 36:
        fail("unexpected_plan_dependency_edge_count")
    if set(actual_edges) != set(expected_edges) or len(actual_edges) != len(expected_edges):
        fail("native_dependency_edge_set_mismatch")
    graph = {task_id: [] for task_id in expected_tasks}
    for task_id, dependency in actual_edges:
        graph.setdefault(task_id, []).append(dependency)
    visiting = set()
    visited = set()

    def visit(task_id):
        if task_id in visiting:
            return False
        if task_id in visited:
            return True
        visiting.add(task_id)
        for dependency in graph.get(task_id, []):
            if not visit(dependency):
                return False
        visiting.remove(task_id)
        visited.add(task_id)
        return True

    acyclic = all(visit(task_id) for task_id in graph)
    if not acyclic:
        fail("native_dependency_graph_cycle")
    expected_counts = Counter(issue["kind"] for issue in expected.values())
    observed_counts = Counter(expected[key]["kind"] for key in native_by_canonical)
    if expected_counts != observed_counts:
        fail("native_kind_counts_mismatch")
    expected_estimates = sum("estimate" in issue for issue in expected.values())
    actual_estimates = sum(native.get("estimate") is not None for native in native_by_canonical.values())
    if expected_estimates != 10 or actual_estimates != expected_estimates:
        fail("native_estimate_count_mismatch")
    return {
        "schema_version": "imprana-linear-readback-verification/v1",
        "status": "PASS" if not failures else "FAIL",
        "complete": not failures,
        "verified_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "scope": "Provided offline native issue snapshot and task relation snapshot",
        "verifier": {
            "path": "scripts/linear/verify_imprana_readback.py",
            "sha256": sha256(Path(__file__).read_bytes()),
        },
        "snapshot_sha256": snapshot_hash,
        "import_plan_sha256": plan_hash,
        "checkpoint_sha256": checkpoint_hash,
        "source_commit": plan["source"]["commit"],
        "source_csv_sha256": plan["source"]["sha256"],
        "technical_tasks_source_sha256": task_source.get("sha256"),
        "counts": {
            "expected_issues": len(expected),
            "snapshot_records": len(native_issues),
            "unique_expected_canonical_ids_observed": len(native_by_canonical),
            "expected_by_kind": dict(expected_counts),
            "observed_by_kind": dict(observed_counts),
            "missing_issues": len(set(expected) - set(native_by_canonical)),
            "expected_source_estimates": expected_estimates,
            "observed_assigned_estimates": actual_estimates,
            "story_gherkin_records_exact": sum(
                record["checks"].get("original_gherkin_utf8_exact", False) for record in records
            ),
            "task_criteria_verified": sum(
                record.get("task_criteria_count", 0)
                for record in records
                if record["checks"].get("task_criteria_order_and_text_exact_normalized", False)
            ),
            "expected_dependency_edges": len(expected_edges),
            "observed_dependency_edges": len(actual_edges),
            "failures": len(failures),
        },
        "dependency_graph_acyclic": acyclic,
        "failure_codes": dict(Counter(failure["code"] for failure in failures)),
        "failures": failures,
        "records": records,
        "verification_method": {
            "criteria": "Extract protected fenced payloads and compare UTF-8 bytes and SHA-256 exactly. "
            "No punctuation, whitespace, indentation, escape or Unicode normalization inside code.",
            "outside_fences": "Compare all outside text and code-position placeholders after only "
            "heading level, bullet marker, URL-angle-bracket, Markdown punctuation escaping and prose whitespace normalization.",
            "tasks": "Compare the ordered acceptance list's normalized presentation and all blockedBy prerequisites.",
            "identity": "Match exact canonical title prefixes and checkpoint native identifiers/UUIDs; "
            "compare parents, milestones, project, team, statuses, labels and estimates.",
            "privacy": "The report omits actual descriptions, titles, names and assignee identifiers.",
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        snapshot, snapshot_hash = read_json(args.snapshot)
        plan, plan_hash = read_json(args.plan)
        checkpoint, checkpoint_hash = read_json(args.checkpoint)
        report = verify(snapshot, snapshot_hash, plan, plan_hash, checkpoint, checkpoint_hash)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        report = {
            "schema_version": "imprana-linear-readback-verification/v1",
            "status": "FAIL",
            "complete": False,
            "failure_codes": {"invalid_input": 1},
            "error_type": type(error).__name__,
        }
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
        print(
            f"Read-back verification: {report['status']}; complete={report['complete']}; report={args.output}"
        )
    else:
        print(serialized, end="")
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
