"""Bounded Imprana documentation publication review; never a product test."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical(text):
    # Only observed renderer differences; literal code remains exact.
    lines = []
    fence = None
    for line in text.split("\n"):
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            token = match.group(1)
            if fence is None:
                fence = token[0]
            elif token[0] == fence:
                fence = None
            lines.append(line)
            continue
        if fence is None:
            line = re.sub(r"^(\s*)[-*] (?=\S)", r"\1* ", line)
            if re.fullmatch(r"\|[|\s:\-]+\|", line):
                cells = [re.sub(r"-{2,}", "--", c.strip()) for c in line[1:-1].split("|")]
                line = "| " + " | ".join(cells) + " |"
            pieces = re.split(r"(`+[^`]*`+)", line)
            for index in range(0, len(pieces), 2):
                pieces[index] = re.sub(r"\]\(<(https?://[^>\n]+)>\)", r"](\1)", pieces[index])
                pieces[index] = re.sub(r"\\\[(code_source|evidence_artifact)\\\]", r"[\1]", pieces[index])
            line = "".join(pieces)
        lines.append(line)
    return "\n".join(lines).rstrip("\n")


PROTECTED = ["id", "uuid", "title", "projectMilestone", "priority", "estimate", "url", "status", "statusType", "parentId", "projectId"]


def review(before, after, plan, documents):
    errors = []
    original = {row["id"]: row for row in before}
    current = {row["id"]: row for row in after}
    mutations = {row["id"]: row for row in plan}
    if len(original) != len(before) or len(current) != len(after):
        errors.append("duplicate issue identity")
    if set(original) != set(current):
        errors.append("complete issue identity set changed")
    if len(mutations) != len(plan) or not set(mutations) <= set(original):
        errors.append("mutation targets duplicated or absent from original")
    verified = []
    sentinel = object()
    for identity, old in original.items():
        new = current.get(identity)
        if new is None:
            continue
        for field in PROTECTED:
            if old.get(field, sentinel) != new.get(field, sentinel):
                errors.append(f"{identity}: protected {field} changed")
        actual = new.get("description", "")
        if identity in mutations:
            proposed = mutations[identity]
            expected = proposed["expectedDescription"]
            if not actual.startswith(old["description"]):
                errors.append(f"{identity}: original full description prefix changed")
            if canonical(actual) != canonical(expected):
                errors.append(f"{identity}: complete proposed appendix readback mismatch")
            if actual.count("<!-- imprana:qa-v1.3:case-design:20261011 -->") != 1:
                errors.append(f"{identity}: appendix marker missing or duplicated")
            verified.append({"id": identity, "story_id": proposed["storyId"], "expected_sha256": digest(expected), "actual_sha256": digest(actual), "original_prefix_sha256": digest(old["description"])})
        elif actual != old.get("description"):
            errors.append(f"{identity}: unselected description changed")
    document_checks = []
    for doc in documents:
        ok = canonical(doc["expected"]) == canonical(doc["actual"])
        if not ok:
            errors.append(f"document {doc['id']}: full content differs")
        if doc["projectId"] != "2de29065-7bb5-46ca-9b8c-4c4ef66cc046":
            errors.append(f"document {doc['id']}: wrong project")
        document_checks.append({"id": doc["id"], "title": doc["title"], "url": doc["url"], "expected_sha256": digest(doc["expected"]), "actual_sha256": digest(doc["actual"]), "normalized_full_content_exact": ok})
    return {"errors": errors, "issues": len(current), "updated_story_count": len(verified), "unselected_issues": len(original) - len(mutations), "story_readbacks": verified, "documents": document_checks}


def main():
    parser = argparse.ArgumentParser()
    for name in ["before", "after", "plan", "docs", "out"]:
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    before = json.loads(Path(args.before).read_text())["issues"]
    after = json.loads(Path(args.after).read_text())["issues"]
    plan = json.loads(Path(args.plan).read_text())
    documents = json.loads(Path(args.docs).read_text())
    result = review(before, after, plan, documents)
    guards = {}
    bad = copy.deepcopy(after)
    bad[0]["status"] = "UNAUTHORISED-STATUS"
    guards["status_mutation_rejected"] = bool(review(before, bad, plan, documents)["errors"])
    guards["missing_identity_rejected"] = bool(review(before, after[:-1], plan, documents)["errors"])
    guards["duplicate_identity_rejected"] = bool(review(before, after + after[:1], plan, documents)["errors"])
    if plan:
        index = next(i for i, row in enumerate(after) if row["id"] == plan[0]["id"])
        for name, changed in [
            ("old_source_mutation_rejected", "CHANGED-SOURCE\n" + after[index]["description"]),
            ("appendix_truncation_rejected", after[index]["description"][:-40]),
            ("duplicate_appendix_rejected", after[index]["description"] + "\n<!-- imprana:qa-v1.3:case-design:20261011 -->"),
        ]:
            bad = copy.deepcopy(after)
            bad[index]["description"] = changed
            guards[name] = bool(review(before, bad, plan, documents)["errors"])
    if documents:
        bad_docs = copy.deepcopy(documents)
        bad_docs[0]["actual"] += "\nQUALIFICATION PASSED"
        guards["unplanned_claim_rejected"] = bool(review(before, after, plan, bad_docs)["errors"])
        bad_docs = copy.deepcopy(documents)
        bad_docs[0]["projectId"] = "WRONG-PROJECT"
        guards["wrong_project_rejected"] = bool(review(before, after, plan, bad_docs)["errors"])
    guards["literal_code_delimiter_change_not_normalized"] = canonical("```text\n|---|---|\n```") != canonical("```text\n| -- | -- |\n```")
    guards["literal_code_url_change_not_normalized"] = canonical("`[label](<https://example.test/>)`") != canonical("`[label](https://example.test/)`")
    guards["source_class_mutation_not_normalized"] = canonical("[code_source]") != canonical("[evidence_artifact]")
    guards["literal_class_escape_change_not_normalized"] = canonical("`[code_source]`") != canonical("`\\[code_source\\]`")
    guards["literal_code_bullet_change_not_normalized"] = canonical("```text\n- source\n```") != canonical("```text\n* source\n```")
    result.update({"guard_checks": guards, "status": "PASS" if not result["errors"] and all(guards.values()) else "FAIL", "scope": "Complete 368 targeted native story/document readbacks and 1,553 captured identity/metadata fields. Unselected descriptions are list excerpts only; not full-content certified. First target full-prefix recovery uses its separately saved exact prior-capture reconciliation. Not product execution, human review, Ready or deployment", "normalization": "Only Markdown table delimiter spacing/dash lengths, unordered bullet dash/star cosmetics, angle brackets around unchanged HTTP(S) URL destinations and escaped literal code_source/evidence_artifact label brackets outside literal code, terminal newlines. Parser-generated autolinks are never normalized away; actual identical-literal repairs require separate evidence.", "omitted_fields": "Assignee/cycle not requested or certified; do not infer absent fields as backend null.", "relationships": "Only description patches are requested; no relationship mutation. Existing 779 dependency source edges remain immutable; live relations need a separate capture if certified."})
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "errors": result["errors"], "issues": result["issues"], "updated_story_count": result["updated_story_count"], "documents": len(documents), "guard_checks": guards}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
