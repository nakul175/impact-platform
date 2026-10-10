#!/usr/bin/env python3
"""Build or verify the local Imprana Commons Linear import plan.

This deterministic planner reads the preserved CSV with the standard CSV parser.
It makes no external requests and requires no credentials or paid services.

    python3 scripts/linear/build_imprana_import.py
    python3 scripts/linear/build_imprana_import.py --check

The 370 source records remain intact in source_record, including the two Split
parents retained as historical documents. Active records become 368 story issues
under 54 epic issues. Optional proposed technical tasks become story subissues.
"""

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path
from tempfile import NamedTemporaryFile

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "8a1e405f0086033dfb25ad834689a08bfe9f1eea"
SOURCE_CSV_SHA256 = "6cd4d418dbaf3ec09675947bce0f7840ccc97c3ede9ab3d882202dd6b6ceacbd"
DEFAULT_CSV = ROOT / "docs/backlog/backlog.csv"
DEFAULT_TASKS = ROOT / "docs/product/technical-tasks.json"
DEFAULT_OUTPUT = ROOT / "docs/product/linear/import-plan.json"
DEFAULT_VERIFICATION = ROOT / "docs/product/linear/manifest-verification.json"
GHERKIN = "Acceptance and rejection criteria (Gherkin)"
COLUMNS = [
    "ID",
    "Title",
    "Release",
    "Epic / area",
    "Type",
    "Priority",
    "Built today",
    "Persona",
    "User story",
    GHERKIN,
    "Rejection summary",
    "Source",
    "Merged BRD stories",
    "Related",
    "Original requirement",
    "Original acceptance",
    "Story points",
    "Sprint",
    "Status",
]
RELEASE_GOALS = {
    "Foundation": "RG-FOUNDATION",
    "R1 Pilot": "RG-R1",
    "R2 Scale": "RG-R2",
    "R3 Ecosystem": "RG-R3",
    "Later": "RG-LATER",
}
RELEASE_GOAL_TEXT = {
    "Foundation": "Establish the product and delivery foundation.",
    "R1 Pilot": "Demonstrate a governed pilot journey.",
    "R2 Scale": "Repeat adoption safely at scale.",
    "R3 Ecosystem": "Extend an accountable ecosystem.",
    "Later": "Retain optional scope for evidence-led decisions.",
}
STRATEGIC_OBJECTIVES = {
    "STR-01": "Establish a trusted operating foundation",
    "STR-02": "Help an organisation choose the right problem and intervention",
    "STR-03": "Turn a chosen intervention into adoption with measured value",
    "STR-04": "Make official MEL results and reporting dependable",
    "STR-05": "Grow an accountable service and ecosystem",
}
STRATEGIC_EPIC_GROUPS = {
    "STR-01": [
        "Access control",
        "Identity and accounts",
        "Migration and exit",
        "NFR audit",
        "NFR availability",
        "NFR capacity",
        "NFR compatibility",
        "NFR cost",
        "NFR data integrity",
        "NFR localisation",
        "NFR maintainability",
        "NFR observability",
        "NFR performance",
        "NFR portability",
        "NFR recovery",
        "NFR support",
        "Non-functional",
        "Operators",
        "Platform",
        "Privacy",
        "Security",
        "Service operations",
        "Tenancy and organisation",
        "Transition",
        "User experience",
        "Workflow and review",
        "AI capabilities",
        "NFR AI quality",
    ],
    "STR-02": ["Adoption: Diagnose", "Adoption: Map", "Adoption: Discover", "Adoption: Assess"],
    "STR-03": ["Adoption: Value case", "Adoption: Deploy", "Adoption: Adopt", "Adoption: Improve"],
    "STR-04": [
        "Calculations",
        "Dashboards and analysis",
        "Data import and management",
        "Data quality",
        "Evaluation",
        "Evidence",
        "Finance",
        "Forms and collection",
        "Indicators",
        "Integrations and connectors",
        "Offline collection",
        "Participants",
        "Programmes",
        "Reporting",
        "Results planning",
    ],
    "STR-05": ["Commercial and billing", "Funder portfolio", "Partners"],
}
STATUS_MAP = {"Backlog": "Backlog", "In review": "In Review"}
SPLIT_CHILDREN = {
    "FR-AI-016": ["FR-AI-016a", "FR-AI-016b"],
    "US-DX-01": ["US-DX-01a", "US-DX-01b"],
}
SPRINT_1_IDS = {"FR-AI-001", "FR-SEC-001", "US-DC-04", "US-MP-03"}


def require(condition, message):
    """Keep validation effective even when Python runs with optimization."""
    if not condition:
        raise ValueError(message)


def sha256(value):
    return hashlib.sha256(value).hexdigest()


def relative_path(path):
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def canonical_epic(area):
    return "EPIC-" + re.sub(r"[^A-Z0-9]+", "-", area.upper()).strip("-")


def strategic_objectives(area, story_id=None):
    if story_id in {"FR-AI-016a", "US-CM-05"}:
        return ["STR-01", "STR-03"]
    if story_id == "US-DX-03":
        return ["STR-02", "STR-03"]
    if area in {"AI capabilities", "NFR AI quality"}:
        return ["STR-01", "STR-02", "STR-03", "STR-04"]
    return [objective for objective, areas in STRATEGIC_EPIC_GROUPS.items() if area in areas]


def marker(kind, canonical_id):
    return f"<!-- imprana:{kind}:{canonical_id} -->"


def read_source(path):
    raw = path.read_bytes()
    require(sha256(raw) == SOURCE_CSV_SHA256, "CSV differs from the pinned 370-row source snapshot")
    stream = io.StringIO(raw.decode("utf-8"), newline="")
    reader = csv.DictReader(stream)
    require(reader.fieldnames == COLUMNS, "CSV header differs from the preserved source schema")
    previous_offset = stream.tell()
    previous_line = reader.line_num
    records = []
    for number, fields in enumerate(reader, start=1):
        offset = stream.tell()
        require(set(fields) == set(COLUMNS), f"Malformed CSV record {number}")
        require(all(isinstance(value, str) for value in fields.values()), f"Missing field at record {number}")
        for key in COLUMNS:
            if key not in {
                "Merged BRD stories",
                "Related",
                "Original requirement",
                "Original acceptance",
                "Story points",
                "Sprint",
            }:
                require(bool(fields[key]), f"Required {key} missing at record {number}")
        require(fields["Release"] in RELEASE_GOALS, f"Unknown release at record {number}")
        require(fields["Status"] in {*STATUS_MAP, "Split"}, f"Unknown status at record {number}")
        require("Scenario:" in fields[GHERKIN], f"Missing Gherkin scenario at record {number}")
        require("Then " in fields[GHERKIN], f"Missing Gherkin result at record {number}")
        record_bytes = stream.getvalue()[previous_offset:offset].encode("utf-8")
        records.append(
            {
                "fields": fields,
                "source": {
                    "path": relative_path(path),
                    "commit": SOURCE_COMMIT,
                    "row": number,
                    "physical_start_line": previous_line + 1,
                    "physical_end_line": reader.line_num,
                    "csv_record_sha256": sha256(record_bytes),
                    "fields_sha256": sha256(
                        json.dumps(fields, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                    ),
                    "gherkin_sha256": sha256(fields[GHERKIN].encode("utf-8")),
                },
            }
        )
        previous_offset = offset
        previous_line = reader.line_num
    require(len(records) == 370, "Expected exactly 370 source records")
    ids = [record["fields"]["ID"] for record in records]
    require(len(set(ids)) == 370, "Source IDs must be unique")
    split_ids = {record["fields"]["ID"] for record in records if record["fields"]["Status"] == "Split"}
    require(split_ids == set(SPLIT_CHILDREN), "Split history differs from the pinned source")
    for split_id, children in SPLIT_CHILDREN.items():
        for child in children:
            row = next(record["fields"] for record in records if record["fields"]["ID"] == child)
            require(row["Related"] == split_id, f"Split child {child} lost its parent link")
    return raw, records


def story_description(record, historical=False):
    row = record["fields"]
    kind = "historical" if historical else "story"
    parts = [marker(kind, row["ID"]), "", row["User story"], "", "### Acceptance and rejection criteria"]
    parts.extend(["```gherkin", row[GHERKIN], "```", "", "### Rejection summary", row["Rejection summary"]])
    if row["Original requirement"]:
        parts.extend(["", "### Original requirement", row["Original requirement"]])
    if row["Original acceptance"]:
        parts.extend(["", "### Original acceptance", row["Original acceptance"]])
    parts.extend(
        [
            "",
            "### Source and planning context",
            f"Source: {row['Source']}",
            f"Persona: {row['Persona']}",
            f"Release: {row['Release']} · Epic: {row['Epic / area']}",
            f"Release goal: {RELEASE_GOALS[row['Release']]}",
            "Proposed strategic objectives: "
            + ", ".join(strategic_objectives(row["Epic / area"], row["ID"])),
            f"Priority: {row['Priority']} · Type: {row['Type']}",
            f"Original status: {row['Status']}",
            f"Retained implementation snapshot (Built today): {row['Built today']}",
            "Acceptance is governed by docs/agile/WORKING-AGREEMENT.md; "
            "the implementation snapshot is separate from story acceptance.",
        ]
    )
    for key in ["Merged BRD stories", "Related", "Story points", "Sprint"]:
        if row[key]:
            parts.append(f"{key}: {row[key]}")
    if historical:
        parts.extend(
            [
                "",
                "### Refinement history",
                "Retained split parent. Active replacement stories: " + ", ".join(SPLIT_CHILDREN[row["ID"]]),
            ]
        )
    source = record["source"]
    parts.extend(
        [
            "",
            f"Source commit: `{source['commit']}`",
            f"CSV data record: {source['row']} · CSV record SHA-256: `{source['csv_record_sha256']}`",
            f"Gherkin UTF-8 SHA-256: `{source['gherkin_sha256']}`",
        ]
    )
    return "\n".join(parts)


def read_tasks(path, active_ids):
    if not path.exists():
        return None, []
    raw = path.read_bytes()
    payload = json.loads(raw)
    require(payload.get("source_commit") == SOURCE_COMMIT, "Technical task source commit differs")
    tasks = payload.get("tasks")
    require(isinstance(tasks, list), "Technical tasks must be a list")
    require(all(isinstance(task, dict) for task in tasks), "Technical tasks must be objects")
    ids = [task.get("id") for task in tasks]
    require(all(isinstance(item, str) and item.startswith("TASK-") for item in ids), "Invalid task IDs")
    require(len(ids) == len(set(ids)), "Technical task IDs must be unique")
    for task in tasks:
        require(task.get("story_id") in active_ids, f"Task {task['id']} needs an active parent story")
        for key in ["title", "description"]:
            require(isinstance(task.get(key), str) and bool(task[key]), f"Task {task['id']} lacks {key}")
        criteria = task.get("acceptance_criteria")
        require(isinstance(criteria, list) and bool(criteria), f"Task {task['id']} lacks criteria")
        require(all(isinstance(value, str) and bool(value) for value in criteria), "Invalid task criteria")
        dependencies = task.get("depends_on", [])
        require(isinstance(dependencies, list), f"Task {task['id']} dependencies must be a list")
        require(all(dependency in ids for dependency in dependencies), f"Unknown dependency in {task['id']}")
        require(task["id"] not in dependencies, f"Task {task['id']} depends on itself")
    tasks_by_id = {task["id"]: task for task in tasks}
    visiting = set()
    visited = set()

    def visit(task_id):
        require(task_id not in visiting, f"Dependency cycle at {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in tasks_by_id[task_id].get("depends_on", []):
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in ids:
        visit(task_id)
    return {
        "path": relative_path(path),
        "sha256": sha256(raw),
        "source_commit": SOURCE_COMMIT,
        "planning_status": payload.get("planning_status"),
        "version": payload.get("version"),
    }, tasks


def build_manifest(csv_path, tasks_path):
    raw, records = read_source(csv_path)
    active = [record for record in records if record["fields"]["Status"] != "Split"]
    active_by_id = {record["fields"]["ID"]: record for record in active}
    areas = sorted({record["fields"]["Epic / area"] for record in active})
    require(len(areas) == 54, "Expected 54 active epics")
    require(len({canonical_epic(area) for area in areas}) == len(areas), "Epic canonical IDs collide")
    proposed_areas = [area for group in STRATEGIC_EPIC_GROUPS.values() for area in group]
    require(len(proposed_areas) == len(set(proposed_areas)), "Primary strategic epic mappings overlap")
    require(set(proposed_areas) == set(areas), "Strategic mapping differs from the 54 source epics")
    tasks_source, tasks = read_tasks(tasks_path, set(active_by_id))
    issues = []
    for area in areas:
        children = [record for record in active if record["fields"]["Epic / area"] == area]
        epic_id = canonical_epic(area)
        release_counts = Counter(record["fields"]["Release"] for record in children)
        issues.append(
            {
                "canonical_id": epic_id,
                "kind": "epic",
                "title": f"[{epic_id}] {area}",
                "description": "\n".join(
                    [
                        marker("epic", epic_id),
                        "",
                        f"{area}: {len(children)} active source stories in Imprana Commons.",
                        "The epic retains one parent across releases. "
                        "Each story carries its release milestone.",
                        "Proposed strategic objectives: " + ", ".join(strategic_objectives(area)),
                        "",
                        "Release scope: "
                        + "; ".join(
                            f"{release}: {release_counts[release]}"
                            for release in RELEASE_GOALS
                            if release_counts[release]
                        ),
                        "",
                        "Source stories: " + ", ".join(record["fields"]["ID"] for record in children),
                        "",
                        f"Source: docs/backlog/backlog.csv at `{SOURCE_COMMIT}`",
                        f"CSV SHA-256: `{sha256(raw)}`",
                    ]
                ),
                "epic_id": epic_id,
                "parent_id": None,
                "release": None,
                "milestone_id": None,
                "source_id": area,
                "source_story_ids": [record["fields"]["ID"] for record in children],
                "release_counts": dict(release_counts),
                "strategic_objective_ids": strategic_objectives(area),
                "status": "Backlog",
            }
        )
    for record in active:
        row = record["fields"]
        issue = {
            "canonical_id": row["ID"],
            "kind": "story",
            "title": f"[{row['ID']}] {row['Title']}",
            "description": story_description(record),
            "epic_id": canonical_epic(row["Epic / area"]),
            "parent_id": canonical_epic(row["Epic / area"]),
            "release": row["Release"],
            "milestone_id": RELEASE_GOALS[row["Release"]],
            "release_goal_id": RELEASE_GOALS[row["Release"]],
            "strategic_objective_ids": strategic_objectives(row["Epic / area"], row["ID"]),
            "source_id": row["ID"],
            "status": STATUS_MAP[row["Status"]],
            "source": record["source"],
            "source_record": row,
        }
        if row["Story points"]:
            require(row["Story points"].isdigit(), f"Invalid source estimate for {row['ID']}")
            issue["estimate"] = int(row["Story points"])
        issues.append(issue)
    for task in tasks:
        row = active_by_id[task["story_id"]]["fields"]
        task_id = task["id"]
        description = [
            marker("task", task_id),
            "",
            task["description"],
            "",
            "### Proposed acceptance criteria",
        ]
        description.extend(f"- {criterion}" for criterion in task["acceptance_criteria"])
        description.extend(
            [
                "",
                f"Parent story: {task['story_id']}",
                f"Release goal: {RELEASE_GOALS[row['Release']]}",
                "Proposed strategic objectives: "
                + ", ".join(strategic_objectives(row["Epic / area"], row["ID"])),
                "Planning state: Proposed — Backlog; Sprint 2 not committed.",
                f"Source: {relative_path(tasks_path)} · source commit `{SOURCE_COMMIT}`",
                f"Technical task source SHA-256: `{tasks_source['sha256']}`",
            ]
        )
        if task.get("depends_on"):
            description.extend(["", "Depends on: " + ", ".join(task["depends_on"])])
        issues.append(
            {
                "canonical_id": task_id,
                "kind": "technical_task",
                "title": f"[{task_id}] {task['title']}",
                "description": "\n".join(description),
                "epic_id": canonical_epic(row["Epic / area"]),
                "parent_id": task["story_id"],
                "release": row["Release"],
                "milestone_id": RELEASE_GOALS[row["Release"]],
                "release_goal_id": RELEASE_GOALS[row["Release"]],
                "strategic_objective_ids": strategic_objectives(row["Epic / area"], row["ID"]),
                "source_id": task_id,
                "status": "Backlog",
                "depends_on": task.get("depends_on", []),
                "source_record": task,
            }
        )
    history = [
        {
            "canonical_id": f"HISTORY-{record['fields']['ID']}",
            "kind": "historical_split_document",
            "title": f"[{record['fields']['ID']}] {record['fields']['Title']} — split history",
            "description": story_description(record, historical=True),
            "source_id": record["fields"]["ID"],
            "replacement_story_ids": SPLIT_CHILDREN[record["fields"]["ID"]],
            "source": record["source"],
            "source_record": record["fields"],
        }
        for record in records
        if record["fields"]["Status"] == "Split"
    ]
    manifest = {
        "schema_version": "imprana-linear-import-plan/v1",
        "source": {
            "path": relative_path(csv_path),
            "commit": SOURCE_COMMIT,
            "sha256": sha256(raw),
            "encoding": "utf-8",
            "columns": COLUMNS,
            "row_numbering": "1-based CSV data records, excluding header; "
            "quoted multiline fields remain one record",
            "field_preservation": "All decoded original fields retained verbatim; "
            "Gherkin UTF-8 bytes validated",
        },
        "technical_tasks_source": tasks_source,
        "product_hierarchy": {
            "vision_id": "VISION-IMPRANA-01",
            "strategic_objectives": STRATEGIC_OBJECTIVES,
            "strategy_mapping_status": "Proposed taxonomy; "
            "source release assignments and acceptance stay intact",
            "strategy_source": "docs/product/02-STRATEGY.md",
            "release_goals_source": "docs/product/04-RELEASE-GOALS.md",
        },
        "target": {
            "platform": "Linear",
            "workspace_name": "Aplyd Sandbox",
            "team_key": "APL",
            "project_name": "Imprana Commons",
            "project_id": "2de29065-7bb5-46ca-9b8c-4c4ef66cc046",
            "project_url": "https://linear.app/aplyd-sandbox/project/imprana-commons-cf62fc3d7e9d",
        },
        "mapping": {
            "project_count": 1,
            "release_representation": "Five project milestones using stable RG-* canonical IDs",
            "epic_representation": "54 parent issues; release and milestone remain null across releases",
            "story_representation": "368 subissues, each under one epic and assigned its release milestone",
            "technical_task_representation": "Proposed Backlog subissues under their active story parents",
            "split_representation": "Two historical project documents with replacement story links",
            "status_map": STATUS_MAP,
            "estimate_policy": "Only the ten source Story points values are assigned",
            "sprint_policy": "Four original Sprint 1 memberships retained in source context",
            "duplicate_policy": "Match the unique imprana content marker before create; "
            "source checksums detect changed input",
            "native_issue_ids": "Assigned by Linear and retained in the import checkpoint after creation",
        },
        "counts": {
            "source_records": len(records),
            "active_stories": len(active),
            "historical_split_documents": len(history),
            "epic_issues": len(areas),
            "technical_task_issues": len(tasks),
            "active_issues_total": len(issues),
            "source_estimates": sum(bool(record["fields"]["Story points"]) for record in records),
            "source_sprint_1_stories": sum(record["fields"]["Sprint"] == "Sprint 1" for record in records),
            "source_statuses": dict(Counter(record["fields"]["Status"] for record in records)),
            "active_story_statuses": dict(
                Counter(STATUS_MAP[record["fields"]["Status"]] for record in active)
            ),
        },
        "milestones": [
            {
                "canonical_id": goal_id,
                "name": release,
                "description": marker("release", goal_id)
                + f"\n\n{RELEASE_GOAL_TEXT[release]}\n\n"
                + f"{release}: retained release grouping from the source backlog. "
                + f"{sum(record['fields']['Release'] == release for record in active)} active stories.",
                "goal": RELEASE_GOAL_TEXT[release],
                "source_row_count": sum(record["fields"]["Release"] == release for record in records),
                "active_story_count": sum(record["fields"]["Release"] == release for record in active),
                "historical_split_count": sum(
                    record["source_record"]["Release"] == release for record in history
                ),
            }
            for release, goal_id in RELEASE_GOALS.items()
        ],
        "issues": issues,
        "historical_documents": history,
    }
    validate_manifest(manifest, records)
    return manifest


def validate_manifest(manifest, records):
    issues = manifest["issues"]
    stories = {issue["source_id"]: issue for issue in issues if issue["kind"] == "story"}
    historical = {document["source_id"]: document for document in manifest["historical_documents"]}
    require(len(stories) == 368 and len(historical) == 2, "Active and historical source coverage differs")
    canonical_ids = [issue["canonical_id"] for issue in issues]
    canonical_ids.extend(document["canonical_id"] for document in historical.values())
    require(len(canonical_ids) == len(set(canonical_ids)), "Duplicate canonical IDs")
    markers = []
    for item in [*issues, *historical.values()]:
        found = re.findall(r"<!-- imprana:[^>]+ -->", item["description"])
        require(len(found) == 1, f"Expected one content marker for {item['canonical_id']}")
        markers.extend(found)
        require("assignee" not in item and "due_date" not in item, "Assignment or due date was invented")
        require("linear_id" not in item, "Linear issue ID was invented")
    require(len(markers) == len(set(markers)), "Duplicate content markers")
    for record in records:
        row = record["fields"]
        item = historical[row["ID"]] if row["Status"] == "Split" else stories[row["ID"]]
        require(item["source_record"] == row, f"Original fields changed for {row['ID']}")
        require(item["source"] == record["source"], f"Original source identity changed for {row['ID']}")
        for field in COLUMNS:
            require(
                item["source_record"][field].encode("utf-8") == row[field].encode("utf-8"),
                f"Original {field} bytes changed for {row['ID']}",
            )
        embedded_gherkin = item["description"].split("```gherkin\n", 1)[1].split("\n```", 1)[0]
        require(
            embedded_gherkin.encode("utf-8") == row[GHERKIN].encode("utf-8"),
            f"Gherkin changed for {row['ID']}",
        )
        require(row["Rejection summary"] in item["description"], f"Rejection summary lost for {row['ID']}")
        for key in ["User story", "Original requirement", "Original acceptance"]:
            require(row[key] in item["description"], f"Original {key} text lost for {row['ID']}")
        if row["Status"] != "Split":
            require(item["status"] == STATUS_MAP[row["Status"]], f"Status changed for {row['ID']}")
            require(item["parent_id"] == canonical_epic(row["Epic / area"]), f"Epic changed for {row['ID']}")
            require(item["milestone_id"] == RELEASE_GOALS[row["Release"]], f"Release changed for {row['ID']}")
            require(
                item["strategic_objective_ids"] == strategic_objectives(row["Epic / area"], row["ID"]),
                f"Proposed strategic traceability differs for {row['ID']}",
            )
            require(
                item.get("estimate") == (int(row["Story points"]) if row["Story points"] else None),
                f"Estimate changed for {row['ID']}",
            )
    review_ids = {issue["source_id"] for issue in stories.values() if issue["status"] == "In Review"}
    require(review_ids == SPRINT_1_IDS, "The four Sprint 1 review stories changed")
    require(all(issue["status"] in {"Backlog", "In Review"} for issue in issues), "Unsupported import status")
    require(sum("estimate" in issue for issue in issues) == 10, "Expected exactly ten source estimates")
    issue_by_id = {issue["canonical_id"]: issue for issue in issues}
    for issue in issues:
        if issue["kind"] == "epic":
            require(issue["parent_id"] is None and issue["milestone_id"] is None, "Epic has a release parent")
        else:
            require(issue["parent_id"] in issue_by_id, f"Unknown parent for {issue['canonical_id']}")
            expected_kind = "epic" if issue["kind"] == "story" else "story"
            require(issue_by_id[issue["parent_id"]]["kind"] == expected_kind, "Incorrect issue hierarchy")


def verification_report(manifest, serialized, csv_path, tasks_path, output_path):
    """Record reproducible local evidence; make no claim about external imports."""
    _, records = read_source(csv_path)
    validate_manifest(manifest, records)
    issues = manifest["issues"]
    tasks = [issue for issue in issues if issue["kind"] == "technical_task"]
    task_source, original_tasks = read_tasks(
        tasks_path, {issue["source_id"] for issue in issues if issue["kind"] == "story"}
    )
    require(
        {issue["source_id"]: issue["source_record"] for issue in tasks}
        == {task["id"]: task for task in original_tasks},
        "Proposed task source records differ",
    )
    for task in tasks:
        parent = next(issue for issue in issues if issue["canonical_id"] == task["parent_id"])
        require(task["status"] == "Backlog", f"Task {task['canonical_id']} is not proposed Backlog")
        require(task["release"] == parent["release"], f"Task {task['canonical_id']} changed release")
        require(
            task["strategic_objective_ids"] == parent["strategic_objective_ids"],
            f"Task {task['canonical_id']} changed strategic traceability",
        )
        require(
            task["depends_on"] == task["source_record"].get("depends_on", []),
            f"Task {task['canonical_id']} changed dependencies",
        )
        require(task["source_record"]["description"] in task["description"], "Task description lost")
        require(
            all(
                criterion in task["description"] for criterion in task["source_record"]["acceptance_criteria"]
            ),
            f"Task {task['canonical_id']} lost acceptance criteria",
        )
    task_by_id = {task["canonical_id"]: task for task in tasks}
    topological_order = []
    visited = set()

    def visit(task_id):
        if task_id in visited:
            return
        for dependency in task_by_id[task_id]["depends_on"]:
            visit(dependency)
        visited.add(task_id)
        topological_order.append(task_id)

    for task_id in sorted(task_by_id):
        visit(task_id)
    edges = [
        {"task_id": task["canonical_id"], "depends_on": dependency}
        for task in tasks
        for dependency in task["depends_on"]
    ]
    all_items = [*issues, *manifest["historical_documents"], *manifest["milestones"]]
    markers = [
        content_marker
        for item in all_items
        for content_marker in re.findall(r"<!-- imprana:[^>]+ -->", item["description"])
    ]
    require(
        len(markers) == len(all_items), "Expected exactly one marker per issue, history document or milestone"
    )
    require(
        len(markers) == len(set(markers)), "Markers collide across issues, history documents or milestones"
    )
    issue_shapes = {}
    for kind in ["epic", "story", "technical_task"]:
        items = [issue for issue in issues if issue["kind"] == kind]
        required_keys = set.intersection(*(set(item) for item in items)) if items else set()
        all_keys = set.union(*(set(item) for item in items)) if items else set()
        issue_shapes[kind] = {
            "count": len(items),
            "required_keys": sorted(required_keys),
            "optional_keys": sorted(all_keys - required_keys),
        }
    story_estimates = {
        issue["source_id"]: issue["estimate"]
        for issue in issues
        if issue["kind"] == "story" and "estimate" in issue
    }
    return {
        "schema_version": "imprana-manifest-verification/v1",
        "result": "PASS",
        "verification_scope": "Local source preservation, deterministic plan structure and dependency integrity",
        "external_state_verified": False,
        "verifier": {
            "path": relative_path(Path(__file__)),
            "sha256": sha256(Path(__file__).read_bytes()),
            "reproduce": "python3 scripts/linear/build_imprana_import.py --check",
        },
        "artifacts": {
            "source_csv": {
                "path": relative_path(csv_path),
                "sha256": manifest["source"]["sha256"],
                "commit": SOURCE_COMMIT,
            },
            "technical_tasks": task_source,
            "import_manifest": {
                "path": relative_path(output_path),
                "sha256": sha256(serialized),
                "bytes": len(serialized),
            },
        },
        "counts": manifest["counts"],
        "preservation": {
            "original_csv_records_verified": len(records),
            "original_csv_field_count": len(COLUMNS),
            "original_field_utf8_values_verified": len(records) * len(COLUMNS),
            "original_csv_record_checksums_verified": len(records),
            "original_gherkin_utf8_records_verified": len(records),
            "embedded_user_stories_verified": len(records),
            "embedded_rejection_summaries_verified": len(records),
            "proposed_technical_task_records_verified": len(tasks),
            "proposed_task_criteria_verified": sum(
                len(task["source_record"]["acceptance_criteria"]) for task in tasks
            ),
            "preserved_estimates": story_estimates,
            "retained_sprint_context": {
                issue["source_id"]: issue["source_record"]["Sprint"]
                for issue in issues
                if issue["kind"] == "story" and issue["source_record"]["Sprint"]
            },
        },
        "manifest_structure": {
            "top_level_keys": list(manifest),
            "original_csv_columns": COLUMNS,
            "issue_shapes": issue_shapes,
            "milestone_keys": list(manifest["milestones"][0]),
            "historical_document_keys": list(manifest["historical_documents"][0]),
            "reference_fields": {
                "canonical_id": "Stable local identity; never a native Linear issue ID",
                "parent_id": "Epic canonical ID for stories; story canonical ID for technical tasks",
                "epic_id": "The epic canonical ID, including on task grandchildren",
                "milestone_id": "RG-* canonical release milestone; null on cross-release epic parents",
                "depends_on": "Technical task canonical IDs; edge means the task depends on the named task",
                "source_record": "Every original CSV field, or every original proposed task field",
            },
        },
        "hierarchy": {
            "projects_planned": 1,
            "release_milestones_planned": 5,
            "epic_parent_issues": sum(issue["kind"] == "epic" for issue in issues),
            "story_to_epic_links": sum(issue["kind"] == "story" for issue in issues),
            "task_to_story_links": len(tasks),
            "historical_split_replacements": {
                item["source_id"]: item["replacement_story_ids"] for item in manifest["historical_documents"]
            },
        },
        "release_counts": [
            {
                "release": milestone["name"],
                "milestone_id": milestone["canonical_id"],
                "source_rows": milestone["source_row_count"],
                "active_stories": milestone["active_story_count"],
                "historical_split_documents": milestone["historical_split_count"],
                "proposed_technical_tasks": sum(task["release"] == milestone["name"] for task in tasks),
            }
            for milestone in manifest["milestones"]
        ],
        "status_checks": {
            "planned_issue_statuses": dict(Counter(issue["status"] for issue in issues)),
            "source_review_story_ids": sorted(
                issue["source_id"]
                for issue in issues
                if issue["kind"] == "story" and issue["status"] == "In Review"
            ),
            "done_issues": sum(issue["status"] == "Done" for issue in issues),
            "invented_assignments": sum("assignee" in issue for issue in issues),
            "invented_due_dates": sum("due_date" in issue for issue in issues),
            "invented_native_issue_ids": sum("linear_id" in issue for issue in issues),
        },
        "unique_content_markers": {"count": len(markers), "unique_count": len(set(markers))},
        "task_dependency_dag": {
            "acyclic": True,
            "node_count": len(tasks),
            "edge_count": len(edges),
            "edges": edges,
            "topological_order_dependency_first": topological_order,
        },
        "csv_export_decision": {
            "generated": False,
            "primary_documentation": "https://linear.app/docs/cli-importer",
            "reason": "The documented CLI CSV fields omit the project's parent/subissue, "
            "release milestone and dependency relationships. The JSON manifest preserves this hierarchy.",
        },
    }


def write_atomic(path, serialized):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == serialized:
        return
    with NamedTemporaryFile(
        prefix=".imprana-import-", suffix=".json.tmp", dir=path.parent, delete=False
    ) as temporary:
        temporary.write(serialized)
        temporary_path = Path(temporary.name)
    try:
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--technical-tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verification-output", type=Path, default=DEFAULT_VERIFICATION)
    parser.add_argument(
        "--check", action="store_true", help="Validate that the saved plan exactly matches its sources"
    )
    args = parser.parse_args()
    try:
        manifest = build_manifest(args.csv, args.technical_tasks)
        serialized = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        report = verification_report(manifest, serialized, args.csv, args.technical_tasks, args.output)
        report_serialized = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if args.check:
            require(args.output.exists(), "Saved import plan is missing; run the builder first")
            require(
                args.output.read_bytes() == serialized,
                "Saved import plan is stale; regenerate from preserved sources",
            )
            require(
                args.verification_output.exists(),
                "Saved verification report is missing; run the builder first",
            )
            require(
                args.verification_output.read_bytes() == report_serialized,
                "Saved verification report is stale; regenerate from preserved sources",
            )
        else:
            write_atomic(args.output, serialized)
            write_atomic(args.verification_output, report_serialized)
    except (ValueError, OSError, csv.Error) as error:
        print(f"Import plan validation failed: {error}", file=sys.stderr)
        return 1
    action = "Verified" if args.check else "Built"
    counts = manifest["counts"]
    print(
        f"{action} {relative_path(args.output)}: {counts['source_records']} source records, "
        f"{counts['active_stories']} stories, {counts['epic_issues']} epics, "
        f"{counts['historical_split_documents']} historical documents, "
        f"{counts['technical_task_issues']} proposed technical tasks; "
        f"all original field and Gherkin bytes preserved. Verification: {relative_path(args.verification_output)}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
