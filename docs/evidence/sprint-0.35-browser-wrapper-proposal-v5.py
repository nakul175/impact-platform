"""Reviewable, local-only wrapper for the exact current Makefile browser target.

Default is a read-only plan. --execute requires the coordinated frozen source/build
lease; it holds the shared lock and uses only fresh disposable PGlite fixtures.
It never installs/downloads packages, edits registered files, weakens a checker,
rewrites old evidence, or claims native-role/UAT/hosted/manual qualification.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time

ROOT = Path(
    "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform"
)
NODE = Path("/Users/athena/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
LOCK = Path("/private/tmp/tola-ai-shared-qualification.lock")
PREFIX = "sprint-0.35-full-browser"
PORT = "8185"
SOURCE_ROOTS = (
    "apps/api/impact_api",
    "apps/web/src",
    "qualification",
    "scripts",
    "deploy",
    "infrastructure",
    "packages/contracts",
    "specification/fixtures",
    "specification/reference-v1",
    ".github/workflows",
    "tools/browser",
)
SOURCE_SUFFIXES = {".py", ".json", ".sql", ".sh", ".ts", ".tsx", ".css", ".yaml", ".yml", ".mjs", ".html"}
EXTRA_SOURCES = (
    "VERSION.json",
    "Makefile",
    "docs/current/CURRENT-DATA-DICTIONARY.md",
    "apps/web/package.json",
    "apps/web/package-lock.json",
    "apps/web/vite.config.ts",
    "apps/web/index.html",
    "apps/web/ai-walkthrough.html",
    "apps/web/tsconfig.json",
    "tools/dev-db/package.json",
    "tools/dev-db/package-lock.json",
    "tools/dev-db/server.mjs",
)


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for data in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(data)
    return value.hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".pending")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    os.replace(temporary, path)


def make_plan(root=ROOT):
    makefile = (root / "Makefile").read_text()
    block = re.search(r"(?m)^browser:\s*\n((?:\t[^\n]*\n)+)", makefile)
    if not block:
        raise RuntimeError("Exact Makefile browser target was not found")
    commands = [line.strip() for line in block.group(1).splitlines()]
    pure = []
    modes = []
    prepare = []
    install = []
    for command in commands:
        if command == "npm ci --prefix tools/browser":
            install.append(command)
        elif command == "node tools/browser/prepare.mjs":
            prepare.append(command)
        elif re.fullmatch(r"node --experimental-strip-types tools/browser/[a-z0-9-]+\.mjs", command):
            pure.append(command.split()[-1])
        else:
            matched = re.fullmatch(
                r"(?:(IMPACT_OPS_STATUS_FILE=\$\(CURDIR\)/\.local/status-browser/ops-status\.json) )?\$\(PY\) scripts/run\.py ([a-z0-9-]+)",
                command,
            )
            if not matched:
                raise RuntimeError("Unreviewed browser Makefile command: " + command)
            mode = matched.group(2)
            if bool(matched.group(1)) != (mode == "status-browser"):
                raise RuntimeError("The exact status-browser environment contract changed")
            modes.append(mode)
    tree = ast.parse((root / "scripts/run.py").read_text())
    registered = next(
        ast.literal_eval(item.value)
        for item in tree.body
        if isinstance(item, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "BROWSER_MODES" for target in item.targets)
    )
    if len(modes) != 26 or len(set(modes)) != 26 or set(modes) != set(registered) - {"idp-browser"}:
        raise RuntimeError("Refuse omitting/duplicating any of the exact 26 current Makefile modes")
    if len(pure) != 4 or len(set(pure)) != 4 or len(prepare) != 1 or len(install) != 1:
        raise RuntimeError("The four pure prerequisites or packaged preparation changed")
    for file in [
        *pure,
        "tools/browser/prepare.mjs",
        *["tools/browser/" + registered[mode] for mode in modes],
    ]:
        if not (root / file).is_file():
            raise RuntimeError("Missing registered browser prerequisite/checker: " + file)
    return {
        "root": str(root),
        "makefile_sha256": digest(root / "Makefile"),
        "runner_sha256": digest(root / "scripts/run.py"),
        "ordered_makefile_commands": commands,
        "pure_prerequisites": pure,
        "modes": modes,
        "registered_checkers": {mode: registered[mode] for mode in modes},
        "npm_ci": "NOT_RUN: use already installed exact pinned browser dependencies; no install/download",
        "packaged_prepare": prepare[0],
        "port": PORT,
        "shared_lock": str(LOCK),
        "excluded_separate_target": "idp-browser requires the separate live-IdP target",
        "execution_status": "NOT_RUN",
        "wrapper_sha256": digest(__file__),
    }


def source_hashes(root=ROOT):
    paths = {root / name for name in EXTRA_SOURCES}
    for name in SOURCE_ROOTS:
        paths.update(
            path
            for path in (root / name).rglob("*")
            if path.is_file()
            and "node_modules" not in path.parts
            and "__pycache__" not in path.parts
            and path.suffix in SOURCE_SUFFIXES
        )
    if any(path.is_symlink() or not path.is_file() for path in paths):
        raise RuntimeError("Source inventory contains a missing file or symlink")
    return {str(path.relative_to(root)): digest(path) for path in sorted(paths)}


def asset_hashes(root=ROOT):
    paths = sorted((root / "apps/web/dist").rglob("*"))
    files = [path for path in paths if path.is_file()]
    if (
        not files
        or len(files) > 100
        or any(path.is_symlink() or path.stat().st_size > 10 * 1024 * 1024 for path in files)
    ):
        raise RuntimeError("Bounded built asset inventory required")
    if (
        not (root / "apps/web/dist/index.html").is_file()
        or not (root / "apps/web/dist/ai-walkthrough.html").is_file()
    ):
        raise RuntimeError("Both actual built entrypoints are required")
    return {str(path.relative_to(root / "apps/web/dist")): digest(path) for path in files}


def changes(before, after):
    return [name for name in sorted(set(before) | set(after)) if before.get(name) != after.get(name)]


def inventory(directory, excluded=None):
    result = {}
    if not directory.exists():
        return result
    for path in sorted(directory.rglob("*")):
        if excluded and path.is_relative_to(excluded):
            continue
        if path.is_symlink():
            raise RuntimeError("Evidence symlinks are refused before restoration")
        if path.is_file():
            value = path.stat()
            result[str(path.relative_to(directory))] = {
                "sha256": digest(path),
                "size_bytes": value.st_size,
                "mode": stat.S_IMODE(value.st_mode),
                "mtime_ns": value.st_mtime_ns,
                "atime_ns": value.st_atime_ns,
            }
    return result


def snapshot(directory, destination, excluded=None):
    baseline = inventory(directory, excluded)
    destination.mkdir(parents=True, exist_ok=True)
    for name in baseline:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(directory / name, target)
    return baseline


def fresh_outputs(before, after):
    return [
        name
        for name in sorted(after)
        if name not in before
        or any(before[name][key] != after[name][key] for key in ("sha256", "mode", "mtime_ns"))
    ]


def restore_evidence(directory, backup, baseline, excluded=None):
    current = inventory(directory, excluded)
    for name in set(current) - set(baseline):
        (directory / name).unlink()
    for name, metadata in baseline.items():
        target = directory / name
        if not target.is_file() or digest(target) != metadata["sha256"]:
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + ".restore-pending")
            shutil.copyfile(backup / name, temporary)
            os.replace(temporary, target)
        os.chmod(target, metadata["mode"])
        os.utime(target, ns=(metadata["atime_ns"], metadata["mtime_ns"]))
    restored = inventory(directory, excluded)
    if set(restored) != set(baseline) or any(
        any(restored[name][key] != metadata[key] for key in ("sha256", "mode", "mtime_ns"))
        for name, metadata in baseline.items()
    ):
        raise RuntimeError("Historical evidence did not restore exactly")


def evidence_matches(directory, baseline, excluded=None):
    observed = inventory(directory, excluded)
    return set(observed) == set(baseline) and all(
        all(observed[name][key] == value[key] for key in ("sha256", "mode", "mtime_ns"))
        for name, value in baseline.items()
    )


def chrome_environment(environment):
    allowed = {
        name: environment[name]
        for name in ("HOME", "TMPDIR", "USER", "LOGNAME", "LANG", "LC_ALL", "LC_CTYPE")
        if name in environment
    }
    allowed["PATH"] = "/usr/bin:/bin:/usr/sbin:/sbin"
    return allowed


def launcher_text(environment):
    values = " ".join(
        shlex.quote(name + "=" + value) for name, value in chrome_environment(environment).items()
    )
    return "#!/bin/sh\nexec /usr/bin/env -i " + values + " " + shlex.quote(str(CHROME)) + ' "$@"\n'


def scrub(text, private_values=()):
    for value in sorted(
        set(value for value in private_values if isinstance(value, str) and len(value) >= 4),
        key=len,
        reverse=True,
    ):
        text = text.replace(value, "[REDACTED]")
    text = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer [REDACTED]", text)
    text = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", "[REDACTED_JWT]", text)
    text = re.sub(r"postgres(?:ql)?://[^\s\"'<>]+", "[REDACTED_DSN]", text)
    return text


TEXT_SUFFIXES = {
    ".json",
    ".xml",
    ".csv",
    ".tap",
    ".md",
    ".py",
    ".tsx",
    ".ts",
    ".mjs",
    ".html",
    ".css",
    ".patch",
    ".sh",
    ".yaml",
    ".yml",
    ".log",
}
CREDENTIAL_FIELDS = {
    "password",
    "temporary_password",
    "one_time_password",
    "access_token",
    "refresh_token",
    "id_token",
    "client_secret",
    "private_key",
    "csrf_token",
    "cookie",
    "set_cookie",
    "authorization",
    "bearer_token",
}
CREDENTIAL_FORMS = (
    ("JWT_FORM", r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
    ("DSN_FORM", r"postgres(?:ql)?://[^\s\"'<>]+"),
    ("BEARER_FORM", r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}=*"),
    ("PRIVATE_KEY_FORM", r"-----BEGIN(?: [A-Z]+)? PRIVATE KEY-----"),
    ("GENERATED_ONE_TIME_PASSWORD_FORM", r"\b[a-z2-9]{4}(?:-[a-z2-9]{4}){4}\b"),
)


def credential_issue(data, private_values=(), structured=False):
    for value in private_values:
        if isinstance(value, str) and len(value) >= 4 and value.encode() in data:
            return "KNOWN_PRIVATE_FIXTURE_VALUE"
    try:
        text = data.decode("utf-8")
    except UnicodeError:
        return None
    for label, pattern in CREDENTIAL_FORMS:
        if re.search(pattern, text):
            return label
    if structured:
        try:
            value = json.loads(text)
        except ValueError:
            return None

        def contains_secret(node):
            if isinstance(node, dict):
                for key, entry in node.items():
                    normalized = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", str(key)).lower().replace("-", "_")
                    if normalized in CREDENTIAL_FIELDS and entry not in (
                        None,
                        False,
                        "",
                        "[REDACTED]",
                        "[REDACTED_JWT]",
                        "[REDACTED_DSN]",
                        [],
                        {},
                    ):
                        return True
                    if contains_secret(entry):
                        return True
            elif isinstance(node, list):
                return any(contains_secret(entry) for entry in node)
            return False

        if contains_secret(value):
            return "SECRET_VALUED_JSON_FIELD"
    return None


def publish_file(source, target, private_values, quarantine):
    data = source.read_bytes()
    issue = credential_issue(data, private_values, source.suffix == ".json")
    if issue:
        if quarantine is None:
            raise RuntimeError("Private quarantine is required for refused evidence publication")
        quarantine.mkdir(parents=True, exist_ok=True)
        quarantine.chmod(0o700)
        preserved = quarantine / (digest(source) + source.suffix)
        preserved.write_bytes(data)
        preserved.chmod(0o600)
        return {
            "reason": issue,
            "sha256": digest(source),
            "private_raw_copy": str(preserved),
            "publication_status": "REFUSED_ORIGINAL_BYTES_RETAINED_PRIVATELY",
        }
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return None


def publish_log(raw, target, private_values=()):
    raw.chmod(0o600)
    text = scrub(raw.read_text(errors="replace"), private_values)
    # These logs are explicitly transformed derivatives, not edited source reports.
    for label, pattern in CREDENTIAL_FORMS:
        text = re.sub(pattern, "[REDACTED_" + label + "]", text)
    issue = credential_issue(text.encode(), private_values)
    if issue:
        return {"publication_status": "REFUSED", "reason": issue, "private_raw_log": str(raw)}
    target.write_text(text)
    return {
        "publication_status": "SANITIZED_DERIVATIVE",
        "private_raw_log": str(raw),
        "published_sha256": digest(target),
    }


def report_summary(data):
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        return None
    counts = {"passed": 0, "failed": 0, "skipped": 0, "unknown": 0}
    for item in data["results"]:
        status_value = item.get("status") if isinstance(item, dict) else None
        status_value = {"pass": "passed", "fail": "failed", "skip": "skipped"}.get(status_value, status_value)
        counts[status_value if status_value in counts else "unknown"] += 1
    fields = {}
    for name in (
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
    ):
        if name in data:
            fields[name] = data[name]
    return {
        "executed_result_count": len(data["results"]),
        "result_counts": counts,
        "reported_fields": fields,
        "manual_visual_review": "NOT_RUN_BY_WRAPPER",
    }


def summaries_pass(summaries):
    return bool(summaries) and all(
        summary["executed_result_count"] > 0
        and summary["result_counts"]["passed"] > 0
        and summary["result_counts"]["failed"] == 0
        and summary["result_counts"]["unknown"] == 0
        and all(
            not summary["reported_fields"].get(field) for field in ("errors", "uncaughtErrors", "page_errors")
        )
        and summary["reported_fields"].get("sources_unchanged") is not False
        and summary["reported_fields"].get("served_assets_unchanged") is not False
        for summary in summaries
    )


def capture_outputs(evidence, output, before, fixture=None, private_values=(), quarantine=None):
    after = inventory(evidence, output.parent)
    written = fresh_outputs(before, after)
    copied = []
    summaries = []
    refused = []
    referenced = set()
    for name in written:
        source = evidence / name
        target = output / "outputs" / name
        refusal = publish_file(source, target, private_values, quarantine)
        if refusal:
            refused.append({"original_path": name, **refusal})
            continue
        copied.append(
            {
                "original_evidence_path": name,
                "archived_path": str(target.relative_to(evidence)),
                "sha256": digest(target),
                "size_bytes": target.stat().st_size,
                "new_file": name not in before,
                "content_changed": name not in before or before[name]["sha256"] != after[name]["sha256"],
                "fresh_write_observed": True,
            }
        )
        if source.suffix == ".json":
            try:
                data = json.loads(source.read_text())
            except (ValueError, UnicodeError):
                continue
            summary = report_summary(data)
            if summary is not None:
                summaries.append({"path": str(target.relative_to(evidence)), **summary})

            def references(value):
                if isinstance(value, dict):
                    for key, entry in value.items():
                        if key in {"file", "path"} and isinstance(entry, str):
                            candidate = Path(entry)
                            if not candidate.is_absolute():
                                candidate = ROOT / candidate
                            if (
                                fixture
                                and candidate.is_relative_to(fixture)
                                and candidate.is_file()
                                and not candidate.is_symlink()
                                and (
                                    candidate.suffix in {".png", ".pdf", ".xlsx", ".docx", ".csv"}
                                    or candidate.suffix == ".json"
                                    and "download" in candidate.name
                                )
                            ):
                                referenced.add(candidate)
                        references(entry)
                elif isinstance(value, list):
                    for entry in value:
                        references(entry)

            references(data)
    if fixture:
        # A failing checker may have captured a screenshot before it wrote a JSON report.
        referenced.update(
            path for path in fixture.glob("*failure*.png") if path.is_file() and not path.is_symlink()
        )
    for source in sorted(referenced):
        target = output / "fixture-artifacts" / source.relative_to(fixture)
        refusal = publish_file(source, target, private_values, quarantine)
        if refusal:
            refused.append({"original_fixture_path": str(source.relative_to(fixture)), **refusal})
            continue
        copied.append(
            {
                "original_fixture_path": str(source.relative_to(fixture)),
                "archived_path": str(target.relative_to(evidence)),
                "sha256": digest(target),
                "size_bytes": target.stat().st_size,
            }
        )
    return {
        "archived_outputs": copied,
        "fresh_result_reports": summaries,
        "publication_guard": {
            "status": "FAILED" if refused else "PASSED_KNOWN_VALUE_AND_TEXT_SCAN",
            "refused_outputs": refused,
            "limitation": "Unknown generated credentials are also checked by common token/password forms and secret-valued JSON fields. This is not OCR or a manual credential review of image pixels/binary formats.",
        },
        "deleted_evidence_paths": sorted(set(before) - set(after)),
    }


def installed_dependencies():
    expected = json.loads((ROOT / "tools/browser/package.json").read_text())["dependencies"]
    observed = {}
    for name, version in expected.items():
        package = ROOT / "tools/browser/node_modules" / name / "package.json"
        actual = json.loads(package.read_text())["version"]
        if actual != version:
            raise RuntimeError("Installed pinned browser dependency mismatch: " + name)
        observed[name] = {"version": actual, "package_sha256": digest(package)}
    if not NODE.is_file() or not CHROME.is_file() or not os.access(CHROME, os.X_OK):
        raise RuntimeError("Installed Node/Chrome required; downloads are forbidden")
    return observed


def clean_runner_environment(original, launcher):
    # PGlite fixture ownership cannot inherit a native DSN, old token/config, proxy or browser override.
    result = {
        key: value
        for key, value in original.items()
        if not (
            key.startswith(("IMPACT_", "PG", "DYLD_", "LD_", "FONTCONFIG_"))
            or key
            in {
                "HTTP_PROXY",
                "HTTPS_PROXY",
                "ALL_PROXY",
                "http_proxy",
                "https_proxy",
                "all_proxy",
                "NODE_OPTIONS",
            }
        )
    }
    result.update(
        PATH=str(ROOT / ".venv/bin")
        + os.pathsep
        + str(NODE.parent)
        + os.pathsep
        + original.get("PATH", "/usr/bin:/bin"),
        IMPACT_PORT=PORT,
        IMPACT_BROWSER_EXECUTABLE=str(launcher),
        NO_PROXY="127.0.0.1,localhost",
        no_proxy="127.0.0.1,localhost",
    )
    return result


def asset_route(name):
    # The frozen API serves the built app entrypoint at /; all other built paths
    # retain their exact public route and still require equal response bytes.
    return "/" if name == "index.html" else "/" + name


def observe_fixture(environment, expected_assets):
    import httpx
    import psycopg
    from psycopg.conninfo import conninfo_to_dict

    base = environment["IMPACT_BASE_URL"]
    if (
        base != "http://127.0.0.1:" + PORT
        or environment.get("IMPACT_ENVIRONMENT") != "test"
        or environment.get("IMPACT_ALLOW_FIXTURE_LOAD") != "1"
    ):
        raise RuntimeError("Refuse a non-owned/non-local fixture runtime")
    local = Path(environment["IMPACT_TEST_LOCAL"])
    if not local.is_relative_to(ROOT / ".local") or not re.fullmatch(r"test-[a-f0-9]{8}", local.name):
        raise RuntimeError("Fresh disposable fixture directory required")
    params = conninfo_to_dict(environment["IMPACT_FIXTURE_DSN"])
    if (
        params.get("host") != "127.0.0.1"
        or params.get("dbname") != "impact_dev"
        or params.get("user") != "postgres"
        or not params.get("port", "").isdigit()
        or params.get("port") == "55437"
    ):
        raise RuntimeError("Refuse native/foreign database observation")
    with psycopg.connect(
        environment["IMPACT_FIXTURE_DSN"], autocommit=True, prepare_threshold=None
    ) as connection:
        rows = [
            {"version": version, "sha256": checksum, "applied_at": stamp.isoformat()}
            for version, checksum, stamp in connection.execute(
                "SELECT version,sha256,applied_at FROM impact.schema_migration ORDER BY version"
            ).fetchall()
        ]
    migrations = sorted((ROOT / "infrastructure/migrations").glob("*.sql"))
    if len(rows) != 40 or len(migrations) != 40:
        raise RuntimeError("Exact current 40 owning migrations required")
    for row, migration in zip(rows, migrations, strict=True):
        if row["version"] != int(migration.name[:4]) or row["sha256"] != digest(migration):
            raise RuntimeError("Actual owning migration checksum mismatch")
        row["owning_file"] = str(migration.relative_to(ROOT))
    fixture = json.loads((ROOT / "specification/fixtures/api-fixture.json").read_text())
    token = environment[fixture["actors"]["author"]["token_env"]]
    with httpx.Client(trust_env=False, timeout=15) as client:
        response = client.get(base + "/v1/runtime-manifest", headers={"Authorization": "Bearer " + token})
        response.raise_for_status()
        manifest = response.json()
        version = json.loads((ROOT / "VERSION.json").read_text())
        if (
            manifest.get("environment") != "test"
            or manifest.get("build_id") != "impact-" + version["build"]
            or manifest.get("api_version") != version["domain_api"]
            or str(manifest.get("schema_version")) != "40"
            or manifest.get("mutation_tests_allowed") is not True
        ):
            raise RuntimeError("Actual authenticated runtime does not match current tuple")
        served = {}
        for name, checksum in expected_assets.items():
            response = client.get(base + asset_route(name))
            response.raise_for_status()
            served[name] = hashlib.sha256(response.content).hexdigest()
            if served[name] != checksum:
                raise RuntimeError("Actual served asset checksum mismatch: " + name)
    return {
        "recorded_at": now(),
        "environment": "PGLITE",
        "fixture_directory": str(local),
        "base_origin": base,
        "observer_scope": "Privileged disposable read-only migration ledger; authenticated HTTP runtime and both entrypoint built bytes. Not native-login RLS evidence.",
        "runtime_manifest": manifest,
        "owning_migrations": rows,
        "served_assets_sha256": served,
    }


def self_test():
    groups = []
    with tempfile.TemporaryDirectory(prefix="tola-browser-wrapper-selftest-") as name:
        root = Path(name)
        evidence = root / "evidence"
        evidence.mkdir()
        (evidence / "untracked035.png").write_bytes(b"old capture")
        (evidence / "generic.json").write_text('{"results":[{"name":"synthetic","status":"passed"}]}')
        (evidence / "deleted.xml").write_bytes(b"old generic junit")
        backup = root / "backup"
        baseline = snapshot(evidence, backup)
        identical = evidence / "generic.json"
        identical.write_bytes(identical.read_bytes())
        os.utime(
            identical,
            ns=(baseline["generic.json"]["atime_ns"], baseline["generic.json"]["mtime_ns"] + 1000000),
        )
        (evidence / "untracked035.png").write_bytes(b"new capture")
        (evidence / "deleted.xml").unlink()
        (evidence / "new.png").write_bytes(b"new")
        assert set(fresh_outputs(baseline, inventory(evidence))) == {
            "generic.json",
            "untracked035.png",
            "new.png",
        }
        groups.append("Identical rewritten report is fresh; new/untracked image changes are retained")
        output = evidence / PREFIX / "synthetic-mode"
        output.mkdir(parents=True)
        captured = capture_outputs(evidence, output, baseline)
        assert len(captured["archived_outputs"]) == 3 and len(captured["fresh_result_reports"]) == 1
        assert (output / "outputs/generic.json").read_bytes() == identical.read_bytes()
        groups.append(
            "Fresh fixed-name reports/captures are archived without recursively copying wrapper evidence"
        )
        restore_evidence(evidence, backup, baseline, evidence / PREFIX)
        assert evidence_matches(evidence, baseline, evidence / PREFIX)
        groups.append(
            "Deleted/changed/untracked historical bytes, modes and nanosecond times restore; new outputs removed"
        )
        (evidence / "escape").symlink_to(root)
        try:
            inventory(evidence)
            raise AssertionError("Symlink accepted")
        except RuntimeError:
            groups.append("Evidence path escapes through symlinks are refused")
    secret = "synthetic-private-value"
    assert secret not in scrub("Bearer " + secret + " postgresql://user:pass@host/db", [secret])
    groups.append("Known private values and bearer/DSN forms are redacted")
    assert credential_issue(secret.encode(), [secret]) == "KNOWN_PRIVATE_FIXTURE_VALUE"
    assert (
        credential_issue(b'{"temporaryPassword":"new synthetic secret"}', structured=True)
        == "SECRET_VALUED_JSON_FIELD"
    )
    assert credential_issue(b"abcd-efgh-jkmn-pqrs-tuvw") == "GENERATED_ONE_TIME_PASSWORD_FORM"
    groups.append(
        "Known runtime private values, secret-valued JSON and unknown one-time password forms refuse publication"
    )
    with tempfile.TemporaryDirectory(prefix="tola-browser-secret-refusal-") as name:
        root = Path(name)
        evidence = root / "evidence"
        evidence.mkdir()
        source = evidence / "report.json"
        source.write_text('{"results":[{"status":"passed"}]}')
        baseline = snapshot(evidence, root / "backup")
        original = source.read_bytes()
        secret_report = json.dumps({"results": [{"status": "passed"}], "observed": secret}).encode()
        source.write_bytes(secret_report)
        out = evidence / PREFIX / "synthetic-refusal"
        out.mkdir(parents=True)
        captured = capture_outputs(
            evidence, out, baseline, private_values=[secret], quarantine=root / "quarantine"
        )
        assert captured["publication_guard"]["status"] == "FAILED" and not captured["fresh_result_reports"]
        raw = Path(captured["publication_guard"]["refused_outputs"][0]["private_raw_copy"])
        assert raw.read_bytes() == secret_report and stat.S_IMODE(raw.stat().st_mode) == 0o600
        assert not (out / "outputs/report.json").exists() and source.read_bytes() == secret_report
        restore_evidence(evidence, root / "backup", baseline, evidence / PREFIX)
        assert source.read_bytes() == original and evidence_matches(evidence, baseline, evidence / PREFIX)
        groups.append(
            "Secret report is preserved exactly privately0600, never silently rewritten/published, and historical evidence restores"
        )
    minimal = chrome_environment(
        {
            "HOME": "/synthetic",
            "IMPACT_TOKEN_AUTHOR": secret,
            "LD_LIBRARY_PATH": secret,
            "DYLD_INSERT_LIBRARIES": secret,
            "FONTCONFIG_PATH": secret,
            "PGPASSWORD": secret,
            "HTTP_PROXY": secret,
        }
    )
    assert set(minimal) == {"HOME", "PATH"} and secret not in launcher_text(
        {"HOME": "/synthetic", "IMPACT_TOKEN_AUTHOR": secret}
    )
    groups.append("Chrome allowlist removes credentials, database/proxy/library/font overrides")
    runner_environment = clean_runner_environment(
        {"PATH": "/usr/bin:/bin", "IMPACT_FIXTURE_DSN": secret}, ROOT / ".local/browser/chromium"
    )
    assert runner_environment["PATH"].split(os.pathsep)[:2] == [str(ROOT / ".venv/bin"), str(NODE.parent)]
    assert "IMPACT_FIXTURE_DSN" not in runner_environment
    python_probe = subprocess.run(
        [
            "python3",
            "-c",
            "import inspect,json,sys,tarfile;print(json.dumps({'version':list(sys.version_info[:2]),'safe_extract_filter':'filter' in inspect.signature(tarfile.TarFile.extractall).parameters}))",
        ],
        env=runner_environment,
        capture_output=True,
        text=True,
        check=True,
    )
    probe = json.loads(python_probe.stdout)
    assert probe["version"] >= [3, 12] and probe["safe_extract_filter"] is True
    groups.append(
        "Original package preparation resolves installed Python3.12 safe extraction, not incompatible system Python"
    )
    plan = make_plan()
    assert len(plan["modes"]) == 26 and len(plan["pure_prerequisites"]) == 4
    groups.append("Exact current Makefile 26-mode order and four registered pure prerequisites are derived")
    assert asset_route("index.html") == "/"
    assert asset_route("ai-walkthrough.html") == "/ai-walkthrough.html"
    built_assets = asset_hashes()
    assert len(built_assets) == 8 and len([name for name in built_assets if name.startswith("assets/")]) == 6
    assert all(asset_route(name) == "/" + name for name in built_assets if name != "index.html")
    groups.append(
        "Exact built app bytes use / while walkthrough and six static asset routes remain unchanged"
    )
    summary = report_summary(
        {
            "results": [
                {"status": "passed"},
                {"status": "failed"},
                {"status": "skipped"},
                {"status": "other"},
            ],
            "accessibility_scans": [{"violations": [], "incomplete": []}],
            "consoleErrors": [],
            "accessibilityScans": [{"violations": []}],
        }
    )
    assert (
        summary["result_counts"] == {"passed": 1, "failed": 1, "skipped": 1, "unknown": 1}
        and summary["manual_visual_review"] == "NOT_RUN_BY_WRAPPER"
    )
    assert summary["reported_fields"]["consoleErrors"] == [] and summary["reported_fields"][
        "accessibilityScans"
    ] == [{"violations": []}]
    groups.append(
        "Executed counts/skips/unknown and snake/camel-case axe/console evidence stay distinct from manual review"
    )
    assert not summaries_pass([])
    assert not summaries_pass([report_summary({"results": [{"status": "skipped"}]})])
    assert not summaries_pass([report_summary({"results": []})])
    assert not summaries_pass(
        [report_summary({"results": [{"status": "passed"}], "sources_unchanged": False})]
    )
    assert not summaries_pass(
        [report_summary({"results": [{"status": "passed"}], "uncaughtErrors": ["synthetic"]})]
    )
    assert summaries_pass([report_summary({"results": [{"status": "passed"}, {"status": "skipped"}]})])
    groups.append(
        "Missing/empty/error/source-drift reports cannot silently pass; explicit skips retain their count"
    )
    assert changes({"a": "one", "deleted": "same"}, {"a": "two", "new": "same"}) == ["a", "deleted", "new"]
    groups.append("Source changes/additions/deletions cannot silently retain a frozen proof")
    print(
        json.dumps(
            {
                "scope": "Offline wrapper orchestration checks only; no API/database/browser run",
                "passed_groups": len(groups),
                "groups": groups,
                "wrapper_sha256": digest(__file__),
            },
            indent=2,
        )
    )


def execute(plan):
    if Path.cwd().resolve() != ROOT or sys.platform != "darwin":
        raise RuntimeError("This reviewed wrapper is scoped to the owned local Mac checkout")
    dependencies = installed_dependencies()
    original_environment = dict(os.environ)
    original_argv = list(sys.argv)
    evidence = ROOT / "docs/evidence"
    output = evidence / PREFIX
    if output.exists():
        raise RuntimeError("Preserve prior attempts: target evidence directory already exists")
    # One shared writer lease for the entire run; no native/full/Python report collision.
    lock = LOCK.open("a+")
    print("Waiting for coordinated shared qualification lock", flush=True)
    fcntl.flock(lock, fcntl.LOCK_EX)
    if make_plan() != plan:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
        raise RuntimeError(
            "Makefile/runner/wrapper changed while awaiting the lease; re-review the current plan"
        )
    started = now()
    tick = time.monotonic()
    work = Path(tempfile.mkdtemp(prefix="tola-ai-035-browser-", dir="/private/tmp"))
    os.chmod(work, 0o700)
    backup = work / "evidence-before"
    baseline = snapshot(evidence, backup)
    source_start = source_hashes()
    assets_start = asset_hashes()
    output.mkdir(parents=True)
    browser_directory = ROOT / ".local/browser"
    browser_binary = browser_directory / "chromium"
    existing_binary = browser_binary.exists()
    if browser_binary.is_symlink():
        raise RuntimeError("Refuse replacing a symlink browser executable")
    if existing_binary:
        shutil.copy2(browser_binary, work / "chromium-original")
    browser_restore = work / "chromium-original" if existing_binary else None
    mode_results = []
    prereq_results = []
    preparation = {}
    suite_errors = []
    result = 1
    original_call = subprocess.call
    original_sigterm = signal.getsignal(signal.SIGTERM)

    def interrupted(*_):
        raise KeyboardInterrupt("Coordinated wrapper interrupted")

    signal.signal(signal.SIGTERM, interrupted)
    runner = None
    run_environment = None
    try:
        run_environment = clean_runner_environment(original_environment, browser_binary)
        preparation["dependency_install"] = plan["npm_ci"]
        preparation["installed_pinned_dependencies"] = dependencies
        preparation["node_version"] = subprocess.check_output(
            [str(NODE), "--version"], env=run_environment, text=True
        ).strip()
        preparation["actual_chrome_version"] = subprocess.check_output(
            [str(CHROME), "--version"], env=chrome_environment(original_environment), text=True
        ).strip()
        # This is the original Makefile preparation with installed pinned Brotli assets only.
        prepared = subprocess.run(
            [str(NODE), "tools/browser/prepare.mjs"],
            cwd=ROOT,
            env=run_environment,
            capture_output=True,
            text=True,
        )
        preparation["prepare_exit_code"] = prepared.returncode
        preparation["prepare_output"] = scrub(prepared.stdout + prepared.stderr)
        if prepared.returncode or not browser_binary.is_file() or browser_binary.is_symlink():
            raise RuntimeError("Original packaged browser preparation failed")
        shutil.copy2(browser_binary, work / "chromium-packaged")
        preparation["packaged_linux_sha256"] = digest(browser_binary)
        if browser_restore is None:
            browser_restore = work / "chromium-packaged"
        temporary = browser_binary.with_name("chromium.mac-launcher-pending")
        temporary.write_text(launcher_text(original_environment))
        temporary.chmod(0o755)
        os.replace(temporary, browser_binary)
        preparation["local_mac_launcher_sha256"] = digest(browser_binary)
        preparation["chrome_environment_names"] = sorted(chrome_environment(original_environment))
        preparation["restoration_target"] = (
            "original pre-existing executable" if existing_binary else "prepared packaged Linux executable"
        )
        os.environ.clear()
        os.environ.update(run_environment)
        for index, checker in enumerate(plan["pure_prerequisites"], 1):
            name = f"prerequisite-{index:02d}-" + Path(checker).stem
            destination = output / name
            destination.mkdir()
            before = inventory(evidence, output)
            completed = subprocess.run(
                [str(NODE), "--experimental-strip-types", checker],
                cwd=ROOT,
                env=run_environment,
                capture_output=True,
                text=True,
            )
            raw_prerequisite = work / (name + ".log")
            raw_prerequisite.write_text(completed.stdout + completed.stderr)
            log_guard = publish_log(raw_prerequisite, destination / "sanitized-run.log")
            captured = capture_outputs(
                evidence, destination, before, quarantine=work / name / "refused-publication"
            )
            entry = {
                "name": name,
                "checker": checker,
                "exit_code": completed.returncode,
                "scope": "Original registered pure Makefile prerequisite; no actual API/browser qualification",
                "sanitized_log_guard": log_guard,
                **captured,
            }
            prereq_results.append(entry)
            atomic_json(destination / "qualification.json", entry)
            restore_evidence(evidence, backup, baseline, output)
        sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "apps/api")]
        import run as actual_runner

        runner = actual_runner
        fixture_directories = set()
        for mode in plan["modes"]:
            if changes(source_start, source_hashes()) or changes(assets_start, asset_hashes()):
                suite_errors.append("Source/build changed; remaining modes are honestly NOT_RUN")
                break
            destination = output / mode
            destination.mkdir()
            raw = work / (mode + ".log")
            before = inventory(evidence, output)
            observations = []
            private_values = []
            fixture = None
            intercepted = 0
            entry = {
                "mode": mode,
                "checker": plan["registered_checkers"][mode],
                "started_at": now(),
                "scope": "Original unmodified Makefile mode on a fresh actual local Chrome/API/PGlite synthetic fixture; not native/UAT/hosted/manual qualification",
            }

            def browser_call(arguments, *positional, **keywords):
                nonlocal fixture, intercepted
                if arguments != ["node", "tools/browser/" + plan["registered_checkers"][mode]]:
                    return original_call(arguments, *positional, **keywords)
                intercepted += 1
                if intercepted != 1:
                    raise RuntimeError("More than one browser launch in one registered mode")
                environment = keywords["env"]
                fixture = Path(environment["IMPACT_TEST_LOCAL"])
                if fixture in fixture_directories:
                    raise RuntimeError("Refuse fixture reuse across modes")
                fixture_directories.add(fixture)
                private_values.extend(
                    value
                    for key, value in environment.items()
                    if key.startswith(("IMPACT_TOKEN_", "IMPACT_LOGIN_PASSWORD_")) or key.endswith("_DSN")
                )
                passwords = fixture / "passwords.json"
                if passwords.is_file():
                    private_values.extend(json.loads(passwords.read_text()).values())
                observations.append(
                    {"phase": "before_original_browser", **observe_fixture(environment, assets_start)}
                )
                keywords.update(stdout=log, stderr=subprocess.STDOUT)
                code = original_call(arguments, *positional, **keywords)
                observations.append(
                    {"phase": "after_original_browser", **observe_fixture(environment, assets_start)}
                )
                return code

            try:
                subprocess.call = browser_call
                os.environ.clear()
                os.environ.update(run_environment)
                if mode == "status-browser":
                    os.environ["IMPACT_OPS_STATUS_FILE"] = str(ROOT / ".local/status-browser/ops-status.json")
                sys.argv = ["run.py", mode]
                with raw.open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                    os.fchmod(log.fileno(), 0o600)
                    try:
                        code = runner.main() or 0
                    except SystemExit as error:
                        code = error.code or 0
                entry["exit_code"] = int(code)
                if int(code) in {130, 143}:
                    suite_errors.append("Interrupted; later modes NOT_RUN")
            except BaseException as error:
                entry["exit_code"] = 1
                entry["wrapper_error"] = scrub(type(error).__name__ + ": " + str(error), private_values)
                if isinstance(error, (KeyboardInterrupt, SystemExit)):
                    suite_errors.append("Interrupted; later modes NOT_RUN")
            finally:
                subprocess.call = original_call
                signal.signal(signal.SIGTERM, interrupted)
                if raw.is_file():
                    entry["sanitized_log_guard"] = publish_log(
                        raw, destination / "sanitized-run.log", private_values
                    )
                entry.update(
                    capture_outputs(
                        evidence,
                        destination,
                        before,
                        fixture,
                        private_values,
                        work / mode / "refused-publication",
                    )
                )
                entry["fixture_observations"] = observations
                entry["source_changes"] = changes(source_start, source_hashes())
                entry["build_asset_changes"] = changes(assets_start, asset_hashes())
                entry["finished_at"] = now()
                entry["complete_fixture_observation"] = intercepted == 1 and len(observations) == 2
                entry["honest_local_result"] = (
                    "PASS"
                    if entry.get("exit_code") == 0
                    and entry["complete_fixture_observation"]
                    and summaries_pass(entry["fresh_result_reports"])
                    and entry["publication_guard"]["status"] != "FAILED"
                    and entry.get("sanitized_log_guard", {}).get("publication_status")
                    == "SANITIZED_DERIVATIVE"
                    and not entry["source_changes"]
                    and not entry["build_asset_changes"]
                    else "FAILED_OR_INCOMPLETE"
                )
                mode_results.append(entry)
                atomic_json(destination / "qualification.json", entry)
                restore_evidence(evidence, backup, baseline, output)
                print(mode + ": " + entry["honest_local_result"], flush=True)
            if suite_errors or entry["source_changes"] or entry["build_asset_changes"]:
                break
        result = (
            0
            if not suite_errors
            and len(mode_results) == 26
            and all(entry["honest_local_result"] == "PASS" for entry in mode_results)
            and all(
                entry["exit_code"] == 0
                and summaries_pass(entry["fresh_result_reports"])
                and entry["publication_guard"]["status"] != "FAILED"
                and entry.get("sanitized_log_guard", {}).get("publication_status") == "SANITIZED_DERIVATIVE"
                for entry in prereq_results
            )
            else 1
        )
    except BaseException as error:
        suite_errors.append(type(error).__name__ + ": " + scrub(str(error)))
        result = 1
    finally:
        subprocess.call = original_call
        sys.argv = original_argv
        os.environ.clear()
        os.environ.update(original_environment)
        try:
            restore_evidence(evidence, backup, baseline, output)
        except BaseException as error:
            suite_errors.append("Historical restoration failure: " + str(error))
            result = 1
        try:
            if browser_restore and browser_restore.is_file():
                temporary = browser_binary.with_name("chromium.restore-pending")
                shutil.copy2(browser_restore, temporary)
                os.replace(temporary, browser_binary)
                preparation["restored_browser_sha256"] = digest(browser_binary)
                preparation["browser_restored_exactly"] = digest(browser_binary) == digest(
                    browser_restore
                ) and stat.S_IMODE(browser_binary.stat().st_mode) == stat.S_IMODE(
                    browser_restore.stat().st_mode
                )
                if not preparation["browser_restored_exactly"]:
                    result = 1
            else:
                preparation["browser_restoration"] = "No executable replaced before preparation failure"
        except BaseException as error:
            suite_errors.append("Browser restoration failure: " + str(error))
            result = 1
        source_end = source_hashes()
        assets_end = asset_hashes()
        source_changes = changes(source_start, source_end)
        asset_changes = changes(assets_start, assets_end)
        if source_changes or asset_changes:
            result = 1
        completed = {entry["mode"] for entry in mode_results}
        proof = {
            "scope": "Serialized exact current Makefile browser target on local Mac using installed pinned dependencies, original checker semantics, isolated synthetic fixtures and independently observed owning migrations. No native-role, live-IdP, paid-provider, hosted deployment, nonprofit acceptance or manual visual/conformance claim.",
            "started_at": started,
            "finished_at": now(),
            "duration_seconds": round(time.monotonic() - tick, 3),
            "exit_code": result,
            "plan": plan,
            "preparation": preparation,
            "pure_prerequisites": prereq_results,
            "modes": mode_results,
            "not_run_modes": [mode for mode in plan["modes"] if mode not in completed],
            "errors": suite_errors,
            "source_sha256_before": source_start,
            "source_sha256_after": source_end,
            "source_changes": source_changes,
            "build_asset_sha256_before": assets_start,
            "build_asset_sha256_after": assets_end,
            "build_asset_changes": asset_changes,
            "historical_evidence_file_count": len(baseline),
            "historical_evidence_sha256": {name: item["sha256"] for name, item in baseline.items()},
            "historical_evidence_restored": evidence_matches(evidence, baseline, output),
            "private_work_directory": str(work),
            "wrapper_sha256": digest(__file__),
            "limitations": [
                "No package installation; installed exact pinned browser dependency manifests are verified and the original local packaged preparation runs",
                "Older reports' hardcoded Chromium153 engine labels are preserved; preparation records the actually used installed Google Chrome version",
                "Per-mode reported result counts/explicit skips/axe fields are retained per report; they are not interchangeable with requirement completion or native/UAT evidence",
                "Manual screenshot review, screen reader/400%zoom/other browser conformance is NOT_RUN by this wrapper",
                "No live IdP target is part of the Makefile browser target; absence of external requests is asserted only by original checkers that record it",
                "Actual ledger observation uses a privileged disposable read-only connection; it is not direct native-login/RLS qualification",
            ],
        }
        atomic_json(output / "qualification.json", proof)
        signal.signal(signal.SIGTERM, original_sigterm)
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
    print(
        json.dumps(
            {
                "exit_code": result,
                "executed_modes": len(mode_results),
                "registered_modes": 26,
                "pure_prerequisites": len(prereq_results),
                "proof": str(output / "qualification.json"),
            }
        )
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--execute",
        action="store_true",
        help="Requires explicit root-coordinated frozen source/build and shared writer lease",
    )
    group.add_argument(
        "--self-test", action="store_true", help="Offline orchestration checks, no application or browser"
    )
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    plan = make_plan()
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return 0
    return execute(plan)


if __name__ == "__main__":
    raise SystemExit(main())
