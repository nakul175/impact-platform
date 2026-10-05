"""Validate the nonprofit specification and rebuild its requirement traceability.

Offline documentation QA only; it does not run or accept product tests.
"""

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

ID = re.compile(r"(?:BR|FR|SC|TC|DD|WF|DEC)-NPA-\d{3}")
FR = re.compile(r"FR-NPA-\d{3}")


def read_csv(root, name):
    with (root / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def sections(text, level=2):
    result = []
    title, body = "", []
    for line in text.splitlines():
        if re.match(r"^#{" + str(level) + r"}\s", line):
            if title:
                result.append((title, "\n".join(body)))
            title, body = line[level + 1 :], []
        else:
            body.append(line)
    if title:
        result.append((title, "\n".join(body)))
    return result


def refs(value, pattern=FR):
    return set(pattern.findall(value))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("docs/nonprofit-ai/v1.0"))
    args = parser.parse_args()
    root = args.root
    registry = json.loads((root / "requirements.json").read_text())
    business = {r["id"]: r for r in registry["business_requirements"]}
    functional = {r["id"]: r for r in registry["functional_requirements"]}
    scenarios = read_csv(root, "test-scenarios.csv")
    cases = read_csv(root, "test-cases.csv")
    fields = read_csv(root, "data-dictionary.csv")
    texts = {p.name: p.read_text() for p in root.glob("*.md")}
    errors = []
    checks = []

    def check(ok, message):
        checks.append({"check": message, "passed": bool(ok)})
        if not ok:
            errors.append(message)

    check(
        len(business) == 36 and len(functional) == 40, "Canonical business and functional requirement counts"
    )
    check(
        all(set(r["br_ids"]) <= set(business) for r in functional.values()),
        "Functional parent business IDs exist",
    )
    for name in ("02-FSD.md", "03-HLD.md", "04-LLD.md"):
        check(
            refs(texts[name]) == set(functional),
            name + " covers every functional requirement without unknown IDs",
        )
    check(
        set(re.findall(r"BR-NPA-\d{3}", texts["01-BRD.md"])) == set(business),
        "BRD covers all business requirements",
    )

    known_ids = set(business) | set(functional)
    known_ids |= (
        {r["scenario_id"] for r in scenarios}
        | {r["case_id"] for r in cases}
        | {r["field_id"] for r in fields}
    )
    known_ids |= {f"DEC-NPA-{n:03d}" for n in range(1, 17)}
    known_ids |= set(re.findall(r"WF-NPA-\d{3}", texts["07-WIREFRAMES-AND-JOURNEYS.md"]))
    for name, rows, key in (
        ("scenarios", scenarios, "scenario_id"),
        ("cases", cases, "case_id"),
        ("fields", fields, "field_id"),
    ):
        check(len({r[key] for r in rows}) == len(rows), name + " identifiers are unique")
        for row in rows:
            found = refs(" ".join(row.values()), ID)
            check(found <= known_ids, row[key] + " references known IDs")
    check(all(r["status"] == "SPECIFIED_NOT_RUN" for r in cases), "Specified cases do not claim execution")
    check(
        all(r["status"] == "SPECIFIED_NOT_RUN" for r in scenarios),
        "Specified scenarios do not claim execution",
    )
    case_ids = {r["case_id"] for r in cases}
    scenario_ids = {r["scenario_id"] for r in scenarios}
    check(all(r["scenario_id"] in scenario_ids for r in cases), "Every case belongs to an existing scenario")
    check(
        all(set(re.findall(r"TC-NPA-\d{3}", r["case_ids"])) <= case_ids for r in scenarios),
        "Scenario case references exist",
    )

    fsd_sections = {}
    for title, body in sections(texts["02-FSD.md"], 3):
        for requirement in refs(body):
            if requirement not in fsd_sections:
                fsd_sections[requirement] = title
    components = defaultdict(list)
    for line in texts["03-HLD.md"].splitlines():
        component = re.search(r"C-NPA-\d{3}", line)
        if line.startswith("|") and component:
            for requirement in refs(line):
                components[requirement].append(component[0])
    lld_sections = {}
    for line in texts["04-LLD.md"].splitlines():
        match = re.match(r"\| (FR-NPA-\d{3}) \| ([^|]+) \|", line)
        if match:
            lld_sections[match[1]] = match[2].strip()
    screens = defaultdict(set)
    for line in texts["07-WIREFRAMES-AND-JOURNEYS.md"].splitlines():
        ids = set(re.findall(r"WF-NPA-\d{3}", line))
        if line.startswith("|"):
            for requirement in refs(line):
                screens[requirement] |= ids
    decisions = defaultdict(set)
    for line in texts["11-DECISIONS-AND-RISKS.md"].splitlines():
        ids = set(re.findall(r"DEC-NPA-\d{3}", line))
        for requirement in refs(line):
            decisions[requirement] |= ids
    work = defaultdict(set)
    for title, body in sections(texts["12-DELIVERY-BACKLOG.md"], 3):
        package = re.search(r"WP NPA \d{2}", title)
        if package:
            for requirement in refs(body):
                work[requirement].add(package[0])

    trace = []
    for requirement, item in functional.items():
        matching_cases = [r for r in cases if requirement in refs(r["fr_ids"])]
        matching_scenarios = [r["scenario_id"] for r in scenarios if requirement in refs(r["fr_ids"])]
        matching_fields = [r["field_id"] for r in fields if requirement in refs(r["functional_requirements"])]
        matching_decisions = decisions[requirement] | set(
            re.findall(r"DEC-NPA-\d{3}", " ".join(r["decision_dependencies"] for r in matching_cases))
        )
        check(
            bool(matching_cases)
            and any(r["negative_case"].lower() in ("yes", "true") for r in matching_cases),
            requirement + " has specified cases including negative coverage",
        )
        check(
            bool(fsd_sections.get(requirement))
            and bool(components[requirement])
            and bool(lld_sections.get(requirement)),
            requirement + " has FSD HLD and LLD allocation",
        )
        check(bool(work[requirement]), requirement + " has a delivery work package")
        trace.append(
            {
                "fr_id": requirement,
                "br_ids": ";".join(item["br_ids"]),
                "title": item["title"],
                "phase": item["phase"],
                "current_state": item["current_state"],
                "acceptance_status": "PROPOSED_UNAPPROVED",
                "fsd_section": fsd_sections.get(requirement, ""),
                "hld_components": ";".join(components[requirement]),
                "lld_section": lld_sections.get(requirement, ""),
                "scenario_ids": ";".join(matching_scenarios),
                "case_ids": ";".join(r["case_id"] for r in matching_cases),
                "test_status": "SPECIFIED_NOT_RUN",
                "wireframes": ";".join(sorted(screens[requirement])) or "CROSS_CUTTING_NO_STANDALONE_SCREEN",
                "dictionary_fields": ";".join(matching_fields) or "PROCESS_CONTROL_NO_NEW_FIELD",
                "decision_dependencies": ";".join(sorted(matching_decisions)),
                "work_packages": ";".join(sorted(work[requirement])),
            }
        )

    with (root / "traceability.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(trace[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(trace)

    for name, text in texts.items():
        check(refs(text, ID) <= known_ids, name + " has no unknown scoped identifiers")
        for destination in re.findall(r"!?\[[^\]]+\]\(([^)]+)\)", text):
            if destination.startswith(("http:", "https:", "mailto:", "#")):
                continue
            local = unquote(destination.split("#")[0])
            check(
                (root / local).exists() or local == "documentation-validation.json",
                name + " local link exists: " + local,
            )
    visual_review = None
    review_path = root / "visual-review.json"
    if review_path.exists():
        visual_review = json.loads(review_path.read_text())
        reviewed = visual_review["documents"]
        check(len(reviewed) == 4, "Visual review covers all four editable specifications")
        for item in reviewed:
            word_path = root / item["file"]
            source_path = root / (word_path.stem + ".md")
            check(
                hashlib.sha256(word_path.read_bytes()).hexdigest() == item["sha256"]
                and hashlib.sha256(source_path.read_bytes()).hexdigest() == item["canonical_source_sha256"],
                word_path.stem + " visual review matches current Word and source files",
            )
            check(
                item["all_pages_inspected"]
                and item["status"] == "PASS"
                and item["inspected_pages"] == list(range(1, item["rendered_pages"] + 1)),
                word_path.stem + " records inspection of every rendered page",
            )
    report = {
        "edition": registry["edition"],
        "date": registry["date"],
        "baseline_commit": registry["baseline_commit"],
        "scope": "OFFLINE_DOCUMENTATION_CONSISTENCY_ONLY",
        "product_tests_executed": False,
        "business_requirements": len(business),
        "functional_requirements": len(functional),
        "test_scenarios": len(scenarios),
        "test_cases": len(cases),
        "dictionary_fields": len(fields),
        "wireframe_screens": len(set(re.findall(r"WF-NPA-\d{3}", texts["07-WIREFRAMES-AND-JOURNEYS.md"]))),
        "checks_passed": sum(r["passed"] for r in checks),
        "checks_failed": len(errors),
        "errors": errors,
        "all_cases_status": "SPECIFIED_NOT_RUN",
        "human_acceptance_recorded": False,
        "word_visual_review": {
            "record": "visual-review.json" if visual_review else None,
            "pages_inspected": visual_review["pages_inspected"] if visual_review else 0,
            "scope": "DOCUMENT_LAYOUT_ONLY",
        },
    }
    (root / "documentation-validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
