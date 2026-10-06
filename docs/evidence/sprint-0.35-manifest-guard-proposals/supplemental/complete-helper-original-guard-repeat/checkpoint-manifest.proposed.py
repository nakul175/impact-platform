"""Assemble a reviewable local checkpoint only after every frozen local gate passes."""

from pathlib import Path
from datetime import datetime, timezone
import argparse
import ast
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(
    "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform"
)
EVIDENCE = ROOT / "docs/evidence"


def read(name):
    return json.loads((ROOT / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise RuntimeError(message)


def junit(name):
    root = ET.parse(ROOT / name).getroot()
    suites = [s for s in root.iter("testsuite") if not s.findall("testsuite")]
    require(suites, "No actual JUnit suites: " + name)
    counts = dict.fromkeys(("tests", "failures", "errors", "skipped"), 0)
    for suite in suites:
        cases = suite.findall("testcase")
        actual = dict(
            tests=len(cases),
            failures=sum(c.find("failure") is not None for c in cases),
            errors=sum(c.find("error") is not None for c in cases),
            skipped=sum(c.find("skipped") is not None for c in cases),
        )
        declared = {key: int(suite.attrib[key]) for key in counts}
        require(declared == actual, "JUnit metadata differs from actual testcase children: " + name)
        for key in counts:
            counts[key] += actual[key]
    require(
        counts["tests"] > counts["skipped"] and counts["failures"] == counts["errors"] == 0,
        "Missing or failing suite: " + name,
    )
    return dict(counts, passed=counts["tests"] - counts["skipped"])


def evidence_path(name):
    path = EVIDENCE / name
    require(
        not Path(name).is_absolute()
        and ".." not in Path(name).parts
        and not path.is_symlink()
        and path.resolve().is_relative_to(EVIDENCE.resolve())
        and path.is_file(),
        "Missing/unsafe evidence path: " + name,
    )
    return path


def source_names(browser=False):
    # Reproduce the frozen source inventory, without executing either runner.
    roots = [
        "apps/api/impact_api",
        "apps/web/src",
        "qualification",
        "scripts",
        "deploy",
        "infrastructure",
        "packages/contracts",
        "specification/reference-v1",
        ".github/workflows",
        "tools/browser",
    ]
    suffixes = {".py", ".json", ".sql", ".sh", ".ts", ".tsx", ".css", ".yaml", ".yml", ".mjs"}
    extras = [
        "VERSION.json",
        "Makefile",
        "docs/current/CURRENT-DATA-DICTIONARY.md",
        "apps/web/package.json",
        "apps/web/package-lock.json",
        "apps/web/vite.config.ts",
        "apps/web/index.html",
        "apps/web/ai-walkthrough.html",
        "tools/dev-db/package.json",
        "tools/dev-db/package-lock.json",
    ]
    if browser:
        roots.append("specification/fixtures")
        suffixes.add(".html")
        extras += ["apps/web/tsconfig.json", "tools/dev-db/server.mjs"]
    else:
        roots.append("tools/dev-db")
        extras += ["tools/browser/package.json", "tools/browser/package-lock.json"]
    paths = {ROOT / name for name in extras}
    for name in roots:
        paths.update(
            p
            for p in (ROOT / name).rglob("*")
            if p.is_file()
            and not any(part in {"__pycache__", "node_modules", "dist"} for part in p.parts)
            and p.suffix in suffixes
        )
    require(all(p.is_file() and not p.is_symlink() for p in paths), "Frozen inventory file/symlink failure")
    result = {str(p.relative_to(ROOT)) for p in paths}
    require(len(result) == (423 if browser else 417), "The explicit frozen0.35 source inventory changed")
    return result


def frontend_gate_names(lint=False):
    # Closed build-proof producer boundary: registered frontend source plus the
    # exact integration/entrypoint inputs. Lint adds the actual Makefile MJS glob.
    extras = {
        "Makefile",
        "VERSION.json",
        "apps/api/impact_api/main.py",
        "apps/api/impact_api/ai_enablement_catalog.py",
        "apps/api/impact_api/ai_learning_content.py",
        "apps/api/impact_api/ai_task_practice.py",
        "apps/web/ai-walkthrough.html",
        "apps/web/index.html",
        "apps/web/package.json",
        "apps/web/package-lock.json",
        "apps/web/tsconfig.json",
        "apps/web/vite.config.ts",
        "qualification/test_deploy_unit.py",
        "scripts/run.py",
        "scripts/smoke.py",
    }
    paths = {ROOT / name for name in extras}
    paths.update(
        path
        for path in (ROOT / "apps/web/src").rglob("*")
        if path.is_file()
        and path.suffix in {".ts", ".tsx", ".css", ".json"}
        and not any(part in {"__pycache__", "node_modules", "dist"} for part in path.parts)
    )
    if lint:
        paths.update((ROOT / "tools/browser").glob("*.mjs"))
    require(
        all(path.is_file() and not path.is_symlink() for path in paths),
        "Closed build/lint input file/symlink failure",
    )
    names = {str(path.relative_to(ROOT)) for path in paths}
    require(len(names) == (108 if lint else 72), "Frozen0.35 build/lint input inventory changed")
    return names


def browser_registration():
    tree = ast.parse((ROOT / "scripts/run.py").read_text())
    registered = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "BROWSER_MODES" for target in node.targets)
    )
    block = re.search(r"(?m)^browser:\s*\n((?:\t[^\n]*\n)+)", (ROOT / "Makefile").read_text())
    require(block is not None, "Actual Makefile browser recipe missing")
    modes, pure = [], []
    for command in map(str.strip, block.group(1).splitlines()):
        if command.startswith("node --experimental-strip-types tools/browser/"):
            pure.append(command.split()[-1])
        match = re.search(r"\$\(PY\) scripts/run\.py ([a-z0-9-]+)$", command)
        if match:
            modes.append(match.group(1))
    require(
        len(modes) == len(set(modes)) == 26 and set(modes) == set(registered) - {"idp-browser"},
        "Missing/duplicate actual registered browser modes",
    )
    require(len(pure) == len(set(pure)) == 4, "Missing/duplicate actual pure prerequisites")
    return modes, pure, {name: registered[name] for name in modes}


def verify_browser_entry(entry, directory):
    require(entry.get("exit_code") == 0, "Browser/prerequisite process failed")
    require(
        entry.get("publication_guard", {}).get("status") == "PASSED_KNOWN_VALUE_AND_TEXT_SCAN"
        and entry["publication_guard"].get("refused_outputs") == [],
        "Missing/failed publication guard",
    )
    require(
        entry.get("sanitized_log_guard", {}).get("publication_status") == "SANITIZED_DERIVATIVE",
        "Missing sanitized log evidence",
    )
    require(
        sha(evidence_path(directory + "/sanitized-run.log"))
        == entry["sanitized_log_guard"]["published_sha256"],
        "Sanitized log changed after qualification",
    )
    archived = entry.get("archived_outputs", [])
    require(
        archived and len({row["archived_path"] for row in archived}) == len(archived),
        "Missing/duplicate archived evidence",
    )
    for row in archived:
        require(row["archived_path"].startswith(directory + "/"), "Archive outside its named mode")
        path = evidence_path(row["archived_path"])
        require(
            sha(path) == row["sha256"] and path.stat().st_size == row["size_bytes"],
            "Archived output bytes changed after qualification",
        )
    reports = entry.get("fresh_result_reports", [])
    require(reports, "Missing actual fresh executed reports")
    for summary in reports:
        rows = [row for row in archived if row["archived_path"] == summary["path"]]
        require(
            len(rows) == 1 and rows[0].get("fresh_write_observed") is True,
            "Report is not a fresh observed output",
        )
        document = json.loads(evidence_path(summary["path"]).read_text())
        actual = dict.fromkeys(("passed", "failed", "skipped", "unknown"), 0)
        results = document.get("results")
        require(isinstance(results, list) and results, "Missing actual result cases")
        for row in results:
            status = row.get("status") if isinstance(row, dict) else None
            status = {"pass": "passed", "fail": "failed", "skip": "skipped"}.get(status, status)
            actual[status if status in actual else "unknown"] += 1
        require(
            summary["executed_result_count"] == len(results)
            and summary["result_counts"] == actual
            and actual["passed"] > 0
            and actual["failed"] == actual["unknown"] == 0,
            "Actual report cases differ from claimed passing summary",
        )
        fields = (
            "errors",
            "uncaughtErrors",
            "page_errors",
            "console_errors",
            "consoleErrors",
            "blocked_external_requests",
            "blocked_network_attempts",
            "accepted_exceptions",
            "accessibility_scans",
            "accessibilityScans",
            "scope",
            "scope_note",
            "limitations",
            "sources_unchanged",
            "served_assets_unchanged",
        )
        require(
            summary["reported_fields"] == {key: document[key] for key in fields if key in document},
            "Archived report fields differ from their observed summary",
        )
        for field in ("errors", "uncaughtErrors", "page_errors"):
            require(not document.get(field), "Actual browser report contains unhandled errors")
        for field in ("sources_unchanged", "served_assets_unchanged"):
            require(document.get(field) is not False, "Actual browser report records source/build drift")
    require(
        json.loads(evidence_path(directory + "/qualification.json").read_text()) == entry,
        "Top-level mode entry differs from its exact named qualification",
    )


def verify_browser_fixture(entry, version, migrations, assets, seen):
    observations = entry.get("fixture_observations", [])
    require(
        len(observations) == 2
        and [row.get("phase") for row in observations]
        == ["before_original_browser", "after_original_browser"],
        "Both actual before/after browser fixture observations required",
    )
    first, last = observations
    fixture = Path(first["fixture_directory"])
    require(
        fixture.parent == ROOT / ".local"
        and re.fullmatch(r"test-[a-f0-9]{8}", fixture.name)
        and str(fixture) not in seen
        and first["fixture_directory"] == last["fixture_directory"]
        and first["base_origin"] == last["base_origin"]
        and re.fullmatch(r"http://127\.0\.0\.1:[0-9]+", first["base_origin"]),
        "Each mode must use its own unchanged disposable loopback fixture",
    )
    seen.add(str(fixture))
    for row in observations:
        runtime = row["runtime_manifest"]
        require(
            row["environment"] == "PGLITE"
            and runtime.get("environment") == "test"
            and runtime.get("build_id") == "impact-" + version["build"]
            and runtime.get("api_version") == version["domain_api"]
            and str(runtime.get("schema_version")) == "40"
            and runtime.get("mutation_tests_allowed") is True
            and row["served_assets_sha256"] == assets,
            "Actual authenticated runtime/served bytes differ from the qualified build",
        )
        rows = row["owning_migrations"]
        require(
            [item["version"] for item in rows] == list(range(1, 41))
            and len({item["owning_file"] for item in rows}) == 40
            and {item["owning_file"]: item["sha256"] for item in rows} == migrations,
            "Actual browser fixture migration ledger differs from saved0001..0040 SQL",
        )
    require(
        first["runtime_manifest"] == last["runtime_manifest"]
        and first["owning_migrations"] == last["owning_migrations"],
        "Actual browser runtime/migration ledger changed during the mode",
    )


def verify_ledger(document, local=False):
    rows = document["migrations" if local else "applied_migrations"]
    require([row["version"] for row in rows] == list(range(1, 41)), "Actual migration ledger1..40 required")
    files = sorted((ROOT / "infrastructure/migrations").glob("*.sql"))
    require(len(files) == 40, "Current migration inventory must remain40")
    for row, path in zip(rows, files, strict=True):
        require(int(path.name[:4]) == row["version"], "Migration ordinal differs")
        if local:
            require(
                row["file"] == path.name
                and row["applied_sha256"] == row["current_source_sha256"] == sha(path),
                "Actually applied PGlite migration differs from current SQL",
            )
        else:
            require(row["sha256"] == sha(path), "Actually applied native migration differs from current SQL")


def unchanged(proof, before, after, failures):
    require(
        proof.get(before) and proof[before] == proof.get(after) and proof.get(failures) == [],
        "Unchanged source proof required",
    )
    for name, expected in proof[before].items():
        require(sha(ROOT / name) == expected, "Source differs from qualified bytes: " + name)
    return proof[before]


def tracker_names():
    expected = {
        "tools/development-tracker/app.js",
        "tools/development-tracker/browser_check.mjs",
        "tools/development-tracker/build_backlog.py",
        "tools/development-tracker/index.html",
        "tools/development-tracker/styles.css",
        "tools/development-tracker/test_tracker.py",
        "tools/development-tracker/tracker.py",
        "tools/development-tracker/update.py",
    }
    actual = {
        str(path.relative_to(ROOT))
        for path in (ROOT / "tools/development-tracker").rglob("*")
        if path.is_file()
        and not any(part in {"__pycache__", ".pytest_cache", "node_modules"} for part in path.parts)
    }
    require(actual == expected, "Exact eight registered tracker tool inputs required")
    require(all(not (ROOT / name).is_symlink() for name in expected), "Tracker source symlinks refused")
    return expected


def verify_tracker():
    name = "docs/evidence/sprint-0.35-tracker-source-proof.json"
    proof = read(name)
    require(proof.get("exit_code") == 0, "Supplemental tracker qualification did not pass")
    names = tracker_names()
    require(
        set(proof.get("source_sha256_start", {})) == names
        and set(proof.get("source_sha256_end", {})) == names,
        "Supplemental tracker proof must include the exact eight inputs",
    )
    qualified = unchanged(proof, "source_sha256_start", "source_sha256_end", "source_changed_during_run")
    report = "docs/evidence/sprint-0.35-tracker-tests.xml"
    require(
        proof.get("junit") == report and proof.get("junit_sha256") == sha(ROOT / report),
        "Supplemental tracker JUnit must be the exact recorded bytes",
    )
    counts = junit(report)
    require(
        counts == dict(tests=42, failures=0, errors=0, skipped=0, passed=42)
        and proof.get("counts") == {key: counts[key] for key in ("tests", "failures", "errors", "skipped")},
        "Exactly42 genuine passing tracker cases without skips required",
    )
    registers = {"docs/COMPLETION-LEDGER.json", "docs/nonprofit-ai/v1.0/requirements.json"}
    require(
        proof.get("source_registers_unchanged") is True
        and set(proof.get("source_register_sha256_before", {})) == registers
        and proof["source_register_sha256_before"] == proof.get("source_register_sha256_after")
        and all(sha(ROOT / key) == value for key, value in proof["source_register_sha256_before"].items()),
        "Tracker source registers must remain unchanged from recorded bytes",
    )
    return qualified, {
        "proof": name,
        "scope": "SUPPLEMENTAL_TRACKER_ONLY_NOT_PRODUCT_ACCEPTANCE",
        "counts": counts,
        "junit": report,
        "source_count": 8,
        "source_registers_unchanged": True,
    }


def instruction_parts(data):
    parts = data.split(b"\n\n", 2)
    require(
        len(parts) == 3 and parts[0].startswith(b"# ") and parts[1].startswith(b"**Current local candidate,"),
        "Instruction title/current-candidate lead/body boundary required",
    )
    return parts


def verify_instruction_leads():
    name = "docs/evidence/sprint-0.35-instruction-lead-review.json"
    proof = read(name)
    baseline = "740f81339acf97ad49d3212dec7f1aa1555139b1"
    require(
        proof.get("baseline_commit") == baseline
        and proof.get("scope") == "DOCUMENTATION_ONLY_LEAD_PARAGRAPH_REVIEW_ENGINEERING_RULES_UNCHANGED"
        and proof.get("status") == "PASS"
        and set(proof.get("files", {})) == {"AGENTS.md", "CLAUDE.md"},
        "Explicit fixed-baseline two-document lead review required",
    )
    qualified = {}
    for document in ("AGENTS.md", "CLAUDE.md"):
        path = ROOT / document
        require(path.is_file() and not path.is_symlink(), "Instruction file/symlink failure")
        current = path.read_bytes()
        original = subprocess.check_output(["git", "show", baseline + ":" + document], cwd=ROOT)
        current_parts, baseline_parts = instruction_parts(current), instruction_parts(original)
        row = proof["files"][document]
        require(
            current_parts[0] == baseline_parts[0]
            and current_parts[2] == baseline_parts[2]
            and row.get("current_whole_sha256") == hashlib.sha256(current).hexdigest()
            and row.get("baseline_whole_sha256") == hashlib.sha256(original).hexdigest()
            and row.get("current_body_sha256") == hashlib.sha256(current_parts[2]).hexdigest()
            and row.get("baseline_body_sha256") == hashlib.sha256(baseline_parts[2]).hexdigest()
            and row.get("engineering_rules_unchanged") is True,
            "Instruction changes must be only the reviewed lead; title/body/rules and hashes must match",
        )
        qualified[document] = row["current_whole_sha256"]
    return qualified, {
        "proof": name,
        "scope": proof["scope"],
        "baseline_commit": baseline,
        "documents": ["AGENTS.md", "CLAUDE.md"],
        "title_and_engineering_body_unchanged": True,
    }


def assemble():
    version = read("VERSION.json")
    require(version["build"] == "0.35.0", "This helper is bound to build0.35.0")
    native = read("docs/evidence/sprint-0.35-full-native-source-proof.json")
    local = read("docs/evidence/sprint-0.35-full-local-source-proof.json")
    unit = read("docs/evidence/sprint-0.35-unit-summary.json")
    build = read("docs/evidence/sprint-0.35-web-build-source-proof.json")
    lint = read("docs/evidence/sprint-0.35-lint-source-proof.json")
    browser = read("docs/evidence/sprint-0.35-full-browser/qualification.json")
    expected_modes, expected_pure, expected_checkers = browser_registration()
    require(
        all(p.get("exit_code") == 0 for p in [native, local, unit, lint, browser]),
        "One or more gates did not pass",
    )
    require(build.get("exit_codes") == [0, 0], "Exact production build required")
    require(
        browser.get("not_run_modes") == [] and browser.get("errors") == [], "All browser modes must execute"
    )
    require(
        len(browser.get("modes", [])) == 26
        and all(m.get("honest_local_result") == "PASS" for m in browser["modes"]),
        "Twenty-six actual browser modes required",
    )
    require(
        [row["mode"] for row in browser["modes"]] == expected_modes,
        "Actual modes must match the exact unique current Makefile order",
    )
    require(
        browser.get("plan", {}).get("modes") == expected_modes
        and browser["plan"].get("pure_prerequisites") == expected_pure
        and browser["plan"].get("registered_checkers") == expected_checkers
        and browser["plan"].get("makefile_sha256") == sha(ROOT / "Makefile")
        and browser["plan"].get("runner_sha256") == sha(ROOT / "scripts/run.py"),
        "Frozen actual browser registration differs from current recipe/runner",
    )
    require(
        len(browser.get("pure_prerequisites", [])) == 4
        and all(
            p.get("exit_code") == 0
            and p.get("publication_guard", {}).get("status") == "PASSED_KNOWN_VALUE_AND_TEXT_SCAN"
            for p in browser["pure_prerequisites"]
        ),
        "Four passing registered pure prerequisites required",
    )
    require(
        [row["checker"] for row in browser["pure_prerequisites"]] == expected_pure,
        "Actual prerequisites must match the exact registered order",
    )
    for row in browser["pure_prerequisites"]:
        verify_browser_entry(row, "sprint-0.35-full-browser/" + row["name"])
    for row in browser["modes"]:
        require(
            row.get("checker") == expected_checkers[row["mode"]]
            and row.get("complete_fixture_observation") is True
            and row.get("source_changes") == row.get("build_asset_changes") == [],
            "Actual mode lacks its current checker/complete unchanged fixture observations",
        )
        verify_browser_entry(row, "sprint-0.35-full-browser/" + row["mode"])
    require(browser.get("historical_evidence_restored") is True, "Historical evidence restoration required")
    historical = browser.get("historical_evidence_sha256")
    require(
        isinstance(historical, dict)
        and historical
        and browser.get("historical_evidence_file_count") == len(historical),
        "Complete historical restoration fingerprints required",
    )
    for name, expected in historical.items():
        require(
            sha(evidence_path(name)) == expected, "Historical evidence changed after restoration: " + name
        )
    require(browser.get("build_asset_changes") == [], "Browser build assets drifted")
    sources = {}
    names = source_names()
    require(
        all(set(p["source_sha256_start"]) == names for p in [native, local, unit]),
        "Actual417 native/local/unit inventory is incomplete",
    )
    require(
        set(browser["source_sha256_before"]) == source_names(browser=True),
        "Actual423 browser inventory is incomplete",
    )
    require(
        set(build["source_sha256_start"]) == frontend_gate_names()
        and set(lint["source_sha256_start"]) == frontend_gate_names(lint=True),
        "Exact closed frozen build/lint source-name sets required",
    )
    for p in [native, local, unit, build, lint]:
        sources.update(unchanged(p, "source_sha256_start", "source_sha256_end", "source_changed_during_run"))
    sources.update(unchanged(browser, "source_sha256_before", "source_sha256_after", "source_changes"))
    tracker_sources, tracker_scope = verify_tracker()
    instruction_sources, instruction_scope = verify_instruction_leads()
    for supplemental in (tracker_sources, instruction_sources):
        require(
            all(name not in sources or sources[name] == value for name, value in supplemental.items()),
            "Supplemental source proof conflicts with an already qualified source",
        )
        sources.update(supplemental)
    previous = read("docs/evidence/sprint-0.34-local-summary.json")
    saved_previous = json.loads(
        subprocess.check_output(
            [
                "git",
                "show",
                "740f81339acf97ad49d3212dec7f1aa1555139b1:docs/evidence/sprint-0.34-local-summary.json",
            ],
            cwd=ROOT,
            text=True,
        )
    )
    require(previous == saved_previous, "Saved0.34 predecessor manifest changed")
    migrations = {
        str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "infrastructure/migrations").glob("*.sql"))
    }
    migration_names = {Path(name).name: checksum for name, checksum in migrations.items()}
    require(
        len(migrations) == len(migration_names) == 40
        and migration_names == saved_previous["migration_sha256"],
        "Frozen0001..0040 SQL differs from saved0.34 checkpoint",
    )
    for name, expected in previous["source_and_verification_sha256"].items():
        require((ROOT / name).is_file(), "Predecessor verification source disappeared: " + name)
        if name not in sources:
            require(sha(ROOT / name) == expected, "Unqualified predecessor-only source changed: " + name)
            sources[name] = expected
        # Already qualified values are never overwritten with newly read bytes.
    native_run = read("docs/evidence/sprint-0.35-full-native-qualification.json")
    require(native_run["restart_check"]["outcome"] == "PASS", "Both native restart phases must pass")
    restore = read("docs/evidence/sprint-0.35-full-native-restore-drill.json")
    require(native_run["tests"]["exit_code"] == 0, "Native application gate failed")
    native_counts = junit("docs/evidence/sprint-0.35-full-native-tests.xml")
    local_counts = junit("docs/evidence/sprint-0.35-full-local-tests.xml")
    unit_counts = junit("docs/evidence/sprint-0.35-unit-tests.xml")
    for key in ("tests", "failures", "errors", "skipped"):
        require(native_counts[key] == native_run["tests"][key], "Native actual JUnit/count summary mismatch")
        require(unit_counts[key] == unit["counts"][key], "Unit actual JUnit/count summary mismatch")
    restart = native_run["restart_check"]
    for phase in ("phase_1", "phase_2"):
        counts = junit("docs/evidence/sprint-0.35-full-native-restart-" + phase + "-tests.xml")
        require(
            counts == dict(tests=1, failures=0, errors=0, skipped=0, passed=1)
            and restart[phase]["exit_code"] == 0
            and all(restart[phase][key] == counts[key] for key in ("tests", "failures", "errors", "skipped")),
            "Actual independent native restart phase did not pass",
        )
    require(
        restart["first_api"]["clean_shutdown"] is True
        and restart["phase_1"]["api_pid"] == restart["first_api"]["pid"]
        and restart["phase_2"]["api_pid"] == restart["second_api"]["pid"]
        and restart["phase_1"]["api_pid"] != restart["phase_2"]["api_pid"],
        "Two genuinely separate native processes required",
    )
    upgrade = native_run["upgrade_check"]
    require(
        upgrade["baseline"]["schema_version"] == 33
        and upgrade["baseline"]["fixture_loaded_at_schema"] == 33
        and upgrade["baseline"]["fixture_loaded"] is True
        and upgrade["baseline"]["revisions"] > 0
        and upgrade["verification"]["rows"] == upgrade["verification"]["max_version"] == 40
        and upgrade["verification"]["checksum_mismatches"] == []
        and upgrade["verification"]["data_preserved"] is True,
        "Actual populated33 to40 upgrade and unchanged data/checksum evidence required",
    )
    require(
        restore.get("credentials_altered") is False
        and restore["migration"]["schema_version"] == restore["migration"]["checksums_verified"] == 40
        and restore["migration"]["applied"] == restore["migration"]["checksum_mismatches"] == []
        and restore["row_counts"]["differing"] == {}
        and restore["checks"]
        and all(value is True for value in restore["checks"].values())
        and restore["security"]["rls_and_policies_identical"] is True
        and restore["security"]["functions_identical"] is True
        and restore["security"]["grants_identical"] is True
        and restore["security"]["fenced_reads"]["ok"] is True,
        "Actual restore data/SQL/RLS/credentials preservation required",
    )
    for side in ("source", "restored"):
        require(
            restore[side]["golden"]["ok"] is True
            and restore[side]["golden"]["found"]
            == dict(displayed_value="46.36", value="46.363636363636", mode="OFFICIAL"),
            "Original raw official arithmetic must survive restore",
        )
    require(
        restore["source"]["golden"]["payload_sha256"] == restore["restored"]["golden"]["payload_sha256"],
        "Original official payload bytes changed during restore",
    )
    verify_ledger(read("docs/evidence/sprint-0.35-full-native-applied-migrations.json"))
    verify_ledger(read("docs/evidence/sprint-0.35-full-local-applied-migrations.json"), local=True)
    require(
        restore.get("outcome") == "PASS" and native_run.get("upgrade_check", {}).get("outcome") == "PASS",
        "Native restore and deployed-baseline upgrade must pass",
    )
    reference = read("docs/evidence/sprint-0.35-reference-tests.json")
    require(
        reference.get("status") == "Pass"
        and reference.get("executed") == 143
        and reference.get("failures") == reference.get("errors") == reference.get("skipped") == 0
        and reference.get("product_validated") is False,
        "Exact preserved design-reference gate required",
    )
    assets = build["built_assets_sha256"]
    require(
        len(assets) == 8
        and assets == browser["build_asset_sha256_before"] == browser["build_asset_sha256_after"],
        "Exact shared eight-file build required",
    )
    for name, expected in assets.items():
        require(sha(ROOT / "apps/web/dist" / name) == expected, "Current built asset mismatch")
    seen_fixtures = set()
    for row in browser["modes"]:
        verify_browser_fixture(row, version, migrations, assets, seen_fixtures)
    evidence = {
        str(p.relative_to(ROOT)): sha(p)
        for p in sorted(EVIDENCE.glob("sprint-0.35-*"))
        if p.is_file() and p.name != "sprint-0.35-local-summary.json"
    }
    for directory in sorted(EVIDENCE.glob("sprint-0.35-*")):
        if directory.is_dir():
            for p in sorted(directory.rglob("*")):
                if p.is_file():
                    evidence[str(p.relative_to(ROOT))] = sha(p)
    doc_names = list(previous["documentation_sha256"]) + [
        "docs/RELEASE-0.35-practical-ai-workspace.md",
        "docs/nonprofit-ai/v1.0/DEVELOPMENT-0.35.md",
    ]
    docs = {name: sha(ROOT / name) for name in sorted(set(doc_names))}
    return {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "candidate": dict(
            version,
            schema=40,
            branch=subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
            parent_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        ),
        "qualification_status": "LOCAL_FULL_NATIVE_PGLITE_UNIT_REFERENCE_BUILD_BROWSER_PASS_HOSTED_GATES_PENDING",
        "native": native_counts,
        "local": local_counts,
        "unit": unit_counts,
        "reference": {"passed": 143, "scope": "Preserved design reference only; product_validated false"},
        "browser": {
            "modes": 26,
            "pure_prerequisites": 4,
            "proof": "docs/evidence/sprint-0.35-full-browser/qualification.json",
            "source_fingerprints": len(browser["source_sha256_before"]),
            "actual_environment": browser["preparation"],
            "scope": browser["scope"],
            "manual_visual_review": "REQUIRES_SEPARATE_ROOT_RECORD",
        },
        "native_restart": "PASS_BOTH_PHASES",
        "native_restore_report": "docs/evidence/sprint-0.35-full-native-restore-drill.json",
        "native_upgrade": "PASS_POPULATED_SCHEMA33_TO40",
        "supplemental_qualification": {"tracker": tracker_scope, "instruction_leads": instruction_scope},
        "source_and_verification_sha256": sources,
        "evidence_sha256": evidence,
        "documentation_sha256": docs,
        "built_asset_sha256": assets,
        "migration_sha256": migration_names,
        "release": {
            "owner_merge_authorisation": True,
            "financial_permission": "PENDING",
            "required_four_job_CI": "NOT_RUN",
            "merged": False,
            "deployed": False,
        },
        "limits": [
            "Counts overlap and do not establish requirement acceptance.",
            "Original307 core113PARTIAL/194PENDING/zeroaccepted;40nonprofit requirements and108specified cases unchanged.",
            "Installed Mac browser/local fixtures do not replace liveIdP/nativeLinux/container/four-job hosted CI.",
            "Any source correction invalidates affected qualification; this manifest cannot qualify a later build.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = assemble()
    with args.output.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha(args.output),
                "source_count": len(result["source_and_verification_sha256"]),
                "evidence_count": len(result["evidence_sha256"]),
            }
        )
    )


if __name__ == "__main__":
    main()
