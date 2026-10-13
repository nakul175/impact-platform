"""Read-only, bounded Imprana Native evidence review. Not product execution."""
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "outputs/imprana-standards-completion-20261011"
OUT = Path(__file__).resolve().parent
REPO = ROOT / "work/imprana-framework-refinement-20261011"
PINS = {}


def load(relative):
    path = ROOT / relative
    raw = path.read_bytes()
    PINS[relative] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    return json.loads(raw)


def local(relative):
    return load(str((BASE / relative).relative_to(ROOT)))


def unique(rows):
    result = {row["id"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError("duplicate identity")
    return result


def raw_issue(envelope):
    if "description" in envelope:
        return envelope
    for item in envelope.get("content", []):
        if item.get("type") == "text":
            candidate = json.loads(item["text"])
            if "description" in candidate:
                return candidate
    raise ValueError("complete issue unavailable")


def projection_errors(metadata, combined, full, selected):
    errors = []
    try:
        listed, joined, complete = map(unique, (metadata, combined, full))
    except ValueError as exc:
        return [str(exc)]
    if set(listed) != set(joined) or set(complete) != selected:
        errors.append("identity sets differ")
    for identity in set(listed) & set(joined):
        expected = copy.deepcopy(listed[identity])
        if identity in selected:
            expected["description"] = complete.get(identity, {}).get("description")
        if joined[identity] != expected:
            errors.append(identity + ": combined record is not exact list/full projection")
    return errors


def same_literal_markup(markup):
    match = re.fullmatch(r"\[([^\]\n]+)\]\(<(https?://[^>\n]+)>\)", markup)
    if not match:
        return None
    label, url = match.groups()
    parts = urlsplit(url)
    if parts.netloc != label or parts.path or parts.query or parts.fragment:
        return None
    return label


def apply_literal_repairs(text, patches):
    for patch in patches:
        if patch.get("op") != "replace" or patch.get("replace_all") is not True:
            raise ValueError("repair is not a declared all-occurrence literal replacement")
        old, new = patch["old_string"], patch["new_string"]
        label = same_literal_markup(old)
        # Some saved patch envelopes quote a backslash twice. Both forms must
        # decode to precisely the captured identical label; no word waiver.
        plain = re.sub(r"\\+([.!#$%&'()*+,\-/:;<=>?@\[\]^_`{|}~])", r"\1", new)
        if label is None or plain != label or old not in text:
            raise ValueError("repair does not preserve the identical label/host")
        text = text.replace(old, label)
    return text


def main():
    OUT.mkdir(exist_ok=True)
    checks = []

    def check(name, passed, details=None):
        checks.append({"check": name, "passed": bool(passed), "details": details})

    before = local("native-full-target-before.json")
    plan = local("native-story-full-plan.json")
    full_capture = local("native-final-full-targets.json")
    metadata = local("native-final-all-metadata.json")
    combined = local("native-final-combined.json")
    documents = local("native-final-ten-document-fresh.json")
    root_result = local("ACTUAL-FINAL-NATIVE-PUBLICATION-REVIEW.json")
    helper_path = BASE / "review_native_publication.py"
    PINS[str(helper_path.relative_to(ROOT))] = {
        "sha256": hashlib.sha256(helper_path.read_bytes()).hexdigest(),
        "bytes": helper_path.stat().st_size,
    }
    spec = importlib.util.spec_from_file_location("imprana_publication_review", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    canonical = helper.canonical

    prior_helper = OUT / "ACTUAL-HELPER-REVIEW.json"
    if prior_helper.exists():
        history = OUT / "history"
        history.mkdir(exist_ok=True)
        old = history / "first-helper-review.json"
        if not old.exists():
            old.write_bytes(prior_helper.read_bytes())
    command = [sys.executable, str(helper_path), "--before", str(BASE / "native-full-target-before.json"),
               "--after", str(BASE / "native-final-combined.json"), "--plan", str(BASE / "native-story-full-plan.json"),
               "--docs", str(BASE / "native-final-ten-document-fresh.json"), "--out", str(prior_helper)]
    actual = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
    (OUT / "actual-helper.stdout.txt").write_text(actual.stdout)
    (OUT / "actual-helper.stderr.txt").write_text(actual.stderr)
    review = json.loads(prior_helper.read_text())
    check("actual_unchanged_helper_exit_and_13_corruption_guards", actual.returncode == 0 and review["status"] == "PASS"
          and not review["errors"] and len(review["guard_checks"]) == 13 and all(review["guard_checks"].values()),
          {"exit": actual.returncode, "guard_count": len(review["guard_checks"]), "errors": review["errors"]})
    check("root_result_matches_separate_actual_helper_result", review == root_result)
    selected = {row["id"] for row in plan}
    full = unique(full_capture["rows"])
    old = unique(before["issues"])
    check("complete_capture_counts_and_uniqueness", len(plan) == len(selected) == len(full) == 368 and len(old) == 1553
          and len(metadata["issues"]) == 1553 and len(combined["issues"]) == 1553 and not full_capture["errors"]
          and not combined["errors"])
    projection = projection_errors(metadata["issues"], combined["issues"], full_capture["rows"], selected)
    check("all1553_combined_fields_bind_exactly_to_fresh_list_and368_fullGET_descriptions", not projection,
          {"errors": projection, "target_full_descriptions": 368, "unselected_excerpt_only": 1185})
    check("all1553_fresh_estimate_fields_present_and_unchanged", all("estimate" in row and row["estimate"] == old[row["id"]]["estimate"]
          for row in metadata["issues"]), {"explicit_list_estimate_count": sum("estimate" in row for row in metadata["issues"])})
    target_results = []
    for row in plan:
        got = full[row["id"]]
        source = old[row["id"]]["description"]
        target_results.append({"id": row["id"], "prefix_exact": got["description"].startswith(source),
                               "expected_full_append_exact_subject_to_declared_cosmetics": canonical(got["description"]) == canonical(row["expectedDescription"]),
                               "marker_once": got["description"].count("<!-- imprana:qa-v1.3:case-design:20261011 -->") == 1})
    check("all368_full_original_prefixes_appends_markers", all(all(r[k] for k in r if k != "id") for r in target_results),
          {"checked": len(target_results), "failures": [r for r in target_results if not all(r[k] for k in r if k != "id")]})
    raw_old = unique(before["targetFullRows"])
    differences, omissions, field_count = [], [], 0
    for identity, row in raw_old.items():
        for key, value in row.items():
            if key in ("description", "updatedAt"):
                continue
            field_count += 1
            if key not in full[identity]:
                omissions.append({"id": identity, "field": key})
            elif full[identity][key] != value:
                differences.append({"id": identity, "field": key})
    claimed_metadata = local("ACTUAL-TARGET-FULL-METADATA-COMPARISON.json")
    check("all368_additional_observed_fullGET_fields_exact", not differences and not omissions,
          {"field_values": field_count, "differences": differences, "omitted": omissions})
    check("additional_fullGET_count_and_root_receipt_match", field_count == claimed_metadata["compared_field_values"] == 11418
          and differences == claimed_metadata["differences"] and omissions == claimed_metadata["omitted"])
    recovery = local("native-first-target-full-prefix-reconciliation.json")
    prior = load(recovery["priorFullCapturePath"])
    prior_row = unique(prior["issues"])[recovery["id"]]
    check("first_target_recovered_original_matches_exact_retained_prior_capture", recovery["id"] == "APL-332"
          and prior_row["description"] == recovery["currentOriginalPrefix"] == old["APL-332"]["description"]
          and before["firstTargetRecovery"] == recovery,
          {"fresh_presave_fullGET_obtained": False, "authority": "Saved earlier complete publication capture; not a fresh pre-save capture"})
    check("ten_full_document_contents_and_project_exact", len(documents) == len({d["id"] for d in documents}) == 10
          and all(d["verified"] is True and canonical(d["expected"]) == canonical(d["actual"])
                  and d["projectId"] == "2de29065-7bb5-46ca-9b8c-4c4ef66cc046" for d in documents))

    repairs = []
    root_repair = local("native-APL-429-auto-link-repair.json")
    root_bad, root_fixed = root_repair["before"]["result"], root_repair["after"]
    root_patches = []
    for markup in set(re.findall(r"\[[^\]\n]+\]\(<https?://[^>\n]+>\)", root_bad["description"])):
        if markup not in root_fixed["description"]:
            label = same_literal_markup(markup)
            if label is None:
                raise ValueError("Root repair removed a non-identical-label URL")
            root_patches.append({"op": "replace", "old_string": markup, "new_string": label, "replace_all": True})
    root_replaced = apply_literal_repairs(root_bad["description"], root_patches)
    repairs.append({"id": "APL-429", "lane": "root", "preserved_bad_prefix": not root_bad["description"].startswith(old["APL-429"]["description"]),
                    "identical_literal_only": canonical(root_replaced) == canonical(root_fixed["description"]),
                    "restored_original_byte_exact": root_fixed["description"].startswith(old["APL-429"]["description"]),
                    "final_fresh_capture_exact": root_fixed["description"] == full["APL-429"]["description"],
                    "structured_request_available": False, "observed_removed_link_occurrences": sum(root_bad["description"].count(p["old_string"]) for p in root_patches)})
    c = local("native-lane-c/FINAL-JOURNAL.json")
    for row in c["entries"]:
        if not row.get("repairCount"):
            continue
        badpath = "native-lane-c/tool-pre-repair/" + Path(row["beforeFile"]).name
        bad = raw_issue(local(badpath))
        fixed = local("native-lane-c/" + row["afterFile"])
        replaced = apply_literal_repairs(bad["description"], row["repairPatches"])
        repairs.append({"id": row["id"], "lane": "C", "preserved_bad_prefix": not bad["description"].startswith(old[row["id"]]["description"]),
                        "identical_literal_only": canonical(replaced) == canonical(fixed["description"]),
                        "restored_original_byte_exact": fixed["description"].startswith(old[row["id"]]["description"]),
                        "final_fresh_capture_exact": fixed["description"] == full[row["id"]]["description"],
                        "structured_request_available": True})
    d = local("native-lane-d/FINAL-JOURNAL.json")
    for row in d["rows"]:
        if not row["repairs"]:
            continue
        sequential_valid = True
        for repair in row["repairs"]:
            replaced = apply_literal_repairs(repair["before"]["description"], repair["patch"])
            sequential_valid &= canonical(replaced) == canonical(repair["after"]["description"])
        repairs.append({"id": row["id"], "lane": "D", "preserved_bad_prefix": not row["repairs"][0]["before"]["description"].startswith(old[row["id"]]["description"]),
                        "identical_literal_only": sequential_valid,
                        "restored_original_byte_exact": row["after"]["description"].startswith(old[row["id"]]["description"]),
                        "final_fresh_capture_exact": row["after"]["description"] == full[row["id"]]["description"],
                        "structured_request_available": True})
    check("all21_concrete_parser_repair_provenance_retained_and_literal_only", len(repairs) == len({r["id"] for r in repairs}) == 21
          and all(all(r[k] for k in ["preserved_bad_prefix", "identical_literal_only", "restored_original_byte_exact", "final_fresh_capture_exact"]) for r in repairs),
          {"count": len(repairs), "root": sum(r["lane"] == "root" for r in repairs), "C": sum(r["lane"] == "C" for r in repairs), "D": sum(r["lane"] == "D" for r in repairs), "records": repairs})

    overview = local("native-overview-final-append-readback.json")
    content_before, content_after = overview["before"]["content"], overview["after"]["content"]
    check("overview_original_full_content_prefix_and_unique_declared_appendix", overview["originalPrefixByteExact"] is True
          and content_after.startswith(content_before) and overview["expected"] == content_before + overview["addition"]
          and canonical(content_after) == canonical(overview["expected"])
          and content_after.count("<!-- imprana:pm-qa-standards-completion:20261011 -->") == 1
          and overview["markerCount"] == 1 and overview["verified"] is True)
    overview_meta = [k for k in overview["before"] if k not in ("content", "updatedAt", "updatedBy")]
    check("overview_observed_identity_title_project_metadata_preserved", all(k in overview["after"] and overview["before"][k] == overview["after"][k] for k in overview_meta),
          {"fields": overview_meta, "updatedAt_and_updatedBy_not_certified_unchanged": True})

    pm_pins = load(str((REPO / "docs/product/framework-v4-20261011/standards-completion/SOURCE-PINS.json").relative_to(ROOT)))
    pin_checks = []
    for item in pm_pins["files"]:
        raw = (ROOT / item["path"]).read_bytes()
        pin_checks.append({"path": item["path"], "exact": hashlib.sha256(raw).hexdigest() == item["sha256"]})
    check("24_frozen_PM_source_package_adapter_inputs_unchanged", len(pin_checks) == 24 and all(p["exact"] for p in pin_checks),
          {"checked": len(pin_checks), "failures": [p for p in pin_checks if not p["exact"]]})
    qa_prefix = REPO / "docs/qa/standards-completion-20261011"
    source_preserve = load(str((qa_prefix / "source-registers/SOURCE-BASELINE-PRESERVATION-RECEIPT.json").relative_to(ROOT)))
    source_checks = []
    for row in source_preserve["checks"]:
        path = REPO / row["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        source_checks.append({"path": row["path"], "exact": digest == row["baseline_sha256"] == row["current_sha256"]})
    check("protected_primary_QA_source_history_invariants_unchanged", all(s["exact"] for s in source_checks),
          {"checked": len(source_checks), "failures": [s for s in source_checks if not s["exact"]]})
    qa_negative = load(str((qa_prefix / "proposed-registers/negative-release-record.stdout.json").relative_to(ROOT)))
    qa_case = load(str((qa_prefix / "case-design/CASE-DESIGN-MANIFEST.json").relative_to(ROOT)))
    check("overview_unresolved_QA_runtime_and_acceptance_claims_remain_honest", len(qa_negative["errors"]) == 3794
          and qa_negative["unknown_applicability"] == 1328 and qa_negative["selected_unique_runs"] == 0
          and qa_case["product_execution"] is False and qa_case["owner_acceptance_or_selected_release_scope"] is False
          and "completed runs are zero" in overview["addition"] and "not" in qa_case["status"].lower(),
          {"negative_release_errors": len(qa_negative["errors"]), "unknown_applicability": qa_negative["unknown_applicability"], "selected_unique_runs": qa_negative["selected_unique_runs"]})

    guards = {}
    corrupted = copy.deepcopy(combined["issues"])
    target_index = next(i for i, r in enumerate(corrupted) if r["id"] in selected)
    corrupted[target_index]["description"] += "\nUNPLANNED"
    guards["fullGET_description_projection_mutation_rejected"] = bool(projection_errors(metadata["issues"], corrupted, full_capture["rows"], selected))
    corrupted = copy.deepcopy(combined["issues"])
    corrupted[0]["estimate"] = "INVENTED"
    guards["list_estimate_projection_mutation_rejected"] = bool(projection_errors(metadata["issues"], corrupted, full_capture["rows"], selected))
    corrupted = copy.deepcopy(combined["issues"])
    corrupted[0]["uncapturedExtra"] = True
    guards["combined_extra_field_rejected"] = bool(projection_errors(metadata["issues"], corrupted, full_capture["rows"], selected))
    guards["generated_autolink_not_normalized_away"] = canonical("ai.usage.read") != canonical("[ai.usage.read](<http://ai.usage.read>)")
    try:
        apply_literal_repairs("[Original.word](<http://Original.word>)", [{"op": "replace", "old_string": "[Original.word](<http://Original.word>)", "new_string": "CHANGED.word", "replace_all": True}])
        guards["repair_word_mutation_rejected"] = False
    except ValueError:
        guards["repair_word_mutation_rejected"] = True
    check("five_additional_independent_projection_and_literal_repair_corruption_guards", len(guards) == 5 and all(guards.values()), guards)
    for relative, pin in PINS.items():
        check("input_immutable_during_review:" + relative, hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == pin["sha256"])
    result = {
        "record": "IMPRANA-FINAL-NATIVE-INDEPENDENT-EVIDENCE-REVIEW-20261011",
        "reviewed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "PASS" if all(c["passed"] for c in checks) else "FAIL",
        "material_findings": [c for c in checks if not c["passed"]],
        "checks": checks,
        "input_pins": PINS,
        "counts": {"target_full_descriptions": 368, "captured_issue_metadata": 1553, "explicit_estimates": 1553,
                   "unselected_excerpt_only": 1185, "documents": 10, "concrete_repaired_targets": 21,
                   "additional_fullGET_field_values": field_count, "helper_corruption_guards": 13,
                   "additional_independent_guards": 5},
        "scope": "Bounded AI evidence review of actual saved captures and an actual offline publication-helper run; no Native queries/mutations or product tests.",
        "independence": "Reviewer authored PM draft records and published Native lane B (103 targets); separately reviews capture integration, root/helper disposition, lanes C/D repairs and overview. This is not independent human/trust/acceptance approval.",
        "limitations": ["Unselected1185 descriptions are500-character list excerpts, not complete-content proof.",
                        "First target original prefix uses exact saved prior full capture; no fresh pre-save full GET for that target.",
                        "Assignee/cycle fields were not requested and are not inferred from omissions.",
                        "779 source dependency edges are immutable; no new all-live relationship proof or external enforcement proof.",
                        "Root APL429 repair has raw bad/fixed readbacks and a prose patch description, not a structured save request; identical-literal equivalence was independently derived from those raw bytes.",
                        "Native captures establish bounded captured field/content integrity, not runtime tests, Ready/Done, approval, deployment or spending authority.",
                        "PM shared draft assurance groups remain needs_input; QA bindings/applicability/run/adoption and authentic reviews remain unresolved."],
    }
    (OUT / "ACTUAL-INDEPENDENT-EVIDENCE-CHECKS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "check_count": len(checks), "failed": len(result["material_findings"]), "counts": result["counts"]}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
