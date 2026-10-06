"""Private guard-predicate tests; never call assemble/main or real runners."""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

PRIVATE = Path(__file__).parent
SAMPLE = PRIVATE / "safe-report-sample"


@pytest.fixture
def guard(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "private_checkpoint_guard_subject", PRIVATE / "checkpoint-manifest.proposed.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "EVIDENCE", tmp_path / "evidence")
    module.EVIDENCE.mkdir()
    return module


def write_xml(guard, body):
    path = guard.ROOT / "tests.xml"
    path.write_text(body)
    return "tests.xml"


def test_real_pass_and_explicit_skip_are_counted_from_children(guard):
    path = write_xml(
        guard,
        '<testsuites><testsuite tests="3" failures="0" errors="0" skipped="1">'
        '<testcase name="positive1"/><testcase name="positive2"/>'
        '<testcase name="explicit-skip"><skipped/></testcase></testsuite></testsuites>',
    )
    assert guard.junit(path) == {
        "tests": 3,
        "failures": 0,
        "errors": 0,
        "skipped": 1,
        "passed": 2,
    }


def test_an_all_skipped_suite_is_not_a_passing_gate(guard):
    path = write_xml(
        guard,
        '<testsuite tests="1" failures="0" errors="0" skipped="1">'
        "<testcase><skipped/></testcase></testsuite>",
    )
    with pytest.raises(RuntimeError, match="Missing or failing suite"):
        guard.junit(path)


def test_claimed_counts_cannot_replace_actual_testcase_children(guard):
    path = write_xml(
        guard,
        '<testsuite tests="99" failures="0" errors="0" skipped="0"><testcase/></testsuite>',
    )
    with pytest.raises(RuntimeError, match="metadata differs"):
        guard.junit(path)


@pytest.mark.parametrize("outcome", ["failure", "error"])
def test_actual_failure_or_error_is_refused_even_with_honest_metadata(guard, outcome):
    path = write_xml(
        guard,
        f'<testsuite tests="1" failures="{int(outcome == "failure")}" '
        f'errors="{int(outcome == "error")}" skipped="0">'
        f"<testcase><{outcome}/></testcase></testsuite>",
    )
    with pytest.raises(RuntimeError, match="Missing or failing suite"):
        guard.junit(path)


def test_nested_junit_suites_are_not_double_counted(guard):
    path = write_xml(
        guard,
        '<testsuites><testsuite tests="2" failures="0" errors="0" skipped="0">'
        '<testsuite tests="1" failures="0" errors="0" skipped="0"><testcase/></testsuite>'
        '<testsuite tests="1" failures="0" errors="0" skipped="0"><testcase/></testsuite>'
        "</testsuite></testsuites>",
    )
    assert guard.junit(path)["passed"] == guard.junit(path)["tests"] == 2


@pytest.mark.parametrize(
    "path", ["../outside.json", "/absolute/outside.json", "missing.json"]
)
def test_unsafe_or_missing_evidence_paths_are_refused(guard, path):
    (guard.ROOT / "outside.json").write_text("{}")
    with pytest.raises(RuntimeError, match="Missing/unsafe"):
        guard.evidence_path(path)


def test_file_and_ancestor_symlink_escape_are_refused(guard):
    outside = guard.ROOT / "outside"
    outside.mkdir()
    (outside / "data.json").write_text("{}")
    (guard.EVIDENCE / "file.json").symlink_to(outside / "data.json")
    (guard.EVIDENCE / "folder").symlink_to(outside, target_is_directory=True)
    for name in ("file.json", "folder/data.json"):
        with pytest.raises(RuntimeError, match="Missing/unsafe"):
            guard.evidence_path(name)


@pytest.fixture
def report(guard):
    directory = "named-predicate-control"
    folder = guard.EVIDENCE / directory
    folder.mkdir()
    entry = copy.deepcopy(json.loads((SAMPLE / "qualification.json").read_text()))
    (folder / "sanitized-run.log").write_bytes(
        (SAMPLE / "sanitized-run.log").read_bytes()
    )
    (folder / "report.json").write_bytes((SAMPLE / "report.json").read_bytes())
    assert len(entry["archived_outputs"]) == len(entry["fresh_result_reports"]) == 1
    entry["archived_outputs"][0]["archived_path"] = directory + "/report.json"
    entry["fresh_result_reports"][0]["path"] = directory + "/report.json"
    (folder / "qualification.json").write_text(json.dumps(entry))
    guard.verify_browser_entry(entry, directory)
    return guard, directory, folder, entry


def verify(report):
    guard, directory, _, entry = report
    guard.verify_browser_entry(entry, directory)


def rewrite_document(report, change):
    guard, _, folder, entry = report
    path = folder / "report.json"
    document = json.loads(path.read_text())
    change(document)
    path.write_text(json.dumps(document))
    entry["archived_outputs"][0].update(
        sha256=guard.sha(path), size_bytes=path.stat().st_size
    )
    return document


def test_copied_actual_safe_report_is_a_positive_guard_control(report):
    verify(report)
    assert report[3]["fresh_result_reports"][0]["executed_result_count"] == 21


@pytest.mark.parametrize("status", [None, "UNKNOWN", "FAILED"])
def test_missing_unknown_or_failed_publication_status_never_passes(report, status):
    report[3]["publication_guard"]["status"] = status
    with pytest.raises(RuntimeError, match="publication guard"):
        verify(report)


def test_refused_publication_outputs_never_pass_even_when_results_pass(report):
    report[3]["publication_guard"]["refused_outputs"] = [
        {"reason": "synthetic refusal"}
    ]
    with pytest.raises(RuntimeError, match="publication guard"):
        verify(report)


def test_process_failure_cannot_use_an_older_passing_report(report):
    report[3]["exit_code"] = 1
    with pytest.raises(RuntimeError, match="process failed"):
        verify(report)


def test_archive_bytes_must_still_match_the_observed_fingerprint(report):
    path = report[2] / "report.json"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(RuntimeError, match="Archived output bytes changed"):
        verify(report)


def test_exact_report_counts_cannot_be_reduced_in_the_claimed_summary(report):
    summary = report[3]["fresh_result_reports"][0]
    summary["executed_result_count"] = 20
    summary["result_counts"]["passed"] = 20
    with pytest.raises(RuntimeError, match="Actual report cases differ"):
        verify(report)


def test_report_freshness_is_required_even_when_bytes_and_cases_pass(report):
    report[3]["archived_outputs"][0]["fresh_write_observed"] = False
    with pytest.raises(RuntimeError, match="not a fresh observed output"):
        verify(report)


@pytest.mark.parametrize(
    "status,count_key", [("failed", "failed"), ("UNKNOWN", "unknown")]
)
def test_actual_failed_or_unknown_case_cannot_be_relabelled_as_a_pass(
    report, status, count_key
):
    rewrite_document(
        report, lambda document: document["results"][0].update(status=status)
    )
    counts = report[3]["fresh_result_reports"][0]["result_counts"]
    counts.update(passed=20, **{count_key: 1})
    with pytest.raises(RuntimeError, match="Actual report cases differ"):
        verify(report)


def test_reported_fields_cannot_hide_an_actual_unhandled_error(report):
    rewrite_document(
        report,
        lambda document: document.update(page_errors=["synthetic unhandled error"]),
    )
    with pytest.raises(RuntimeError, match="report fields differ"):
        verify(report)


def test_unhandled_error_is_refused_even_with_an_honest_summary(report):
    rewrite_document(
        report,
        lambda document: document.update(page_errors=["synthetic unhandled error"]),
    )
    report[3]["fresh_result_reports"][0]["reported_fields"]["page_errors"] = [
        "synthetic unhandled error"
    ]
    with pytest.raises(RuntimeError, match="unhandled errors"):
        verify(report)


def test_actual_source_drift_is_refused_even_with_updated_report_hashes(report):
    rewrite_document(report, lambda document: document.update(sources_unchanged=False))
    report[3]["fresh_result_reports"][0]["reported_fields"]["sources_unchanged"] = False
    with pytest.raises(RuntimeError, match="source/build drift"):
        verify(report)


def test_sanitized_log_bytes_are_bound_independently_from_the_report(report):
    (report[2] / "sanitized-run.log").write_text("different synthetic output")
    with pytest.raises(RuntimeError, match="Sanitized log changed"):
        verify(report)


def test_top_mode_entry_cannot_disagree_with_named_qualification(report):
    entry = json.loads((report[2] / "qualification.json").read_text())
    entry["scope"] = "different claimed scope"
    (report[2] / "qualification.json").write_text(json.dumps(entry))
    with pytest.raises(RuntimeError, match="Top-level mode entry differs"):
        verify(report)


def test_exact_registry_has_twenty_six_modes_and_four_pure_prerequisites(guard):
    (guard.ROOT / "scripts").mkdir()
    (guard.ROOT / "Makefile").write_bytes((SAMPLE / "Makefile").read_bytes())
    (guard.ROOT / "scripts/run.py").write_bytes((SAMPLE / "run.py").read_bytes())
    modes, pure, checkers = guard.browser_registration()
    assert len(modes) == len(checkers) == 26 and len(pure) == 4
    assert modes[0] == "browser" and modes[-1] == "status-browser"
    assert "idp-browser" not in modes


@pytest.mark.parametrize("mutation", ["duplicate-mode", "omit-mode", "omit-pure"])
def test_omitted_or_duplicated_registered_modes_or_pure_gates_are_refused(
    guard, mutation
):
    (guard.ROOT / "scripts").mkdir()
    text = (SAMPLE / "Makefile").read_text()
    line = "\t$(PY) scripts/run.py ai-planning-browser\n"
    if mutation == "duplicate-mode":
        text = text.replace(line, line + line)
    elif mutation == "omit-mode":
        text = text.replace(line, "")
    else:
        text = text.replace(
            "\tnode --experimental-strip-types tools/browser/ai-plan-export-adapter-check.mjs\n",
            "",
        )
    (guard.ROOT / "Makefile").write_text(text)
    (guard.ROOT / "scripts/run.py").write_bytes((SAMPLE / "run.py").read_bytes())
    with pytest.raises(RuntimeError, match="Missing/duplicate"):
        guard.browser_registration()
