"""Source-bound pure draft qualification; writes only beside this unregistered draft."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).parent
REPO = Path(
    "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform"
)
INPUTS = [
    HERE / "ai_plan_exports.py",
    HERE / "ai_plan_export_contracts.py",
    HERE / "ai_plan_public_export_schema_v1.proposed.json",
    HERE / "test_ai_plan_exports_draft.py",
    REPO / "apps/api/impact_api/ai_content_archives.py",
    REPO / "apps/api/impact_api/ai_content_schema_v1.json",
    REPO / "apps/api/impact_api/store.py",
    REPO / "packages/contracts/event.schema.json",
]


def fingerprints():
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in INPUTS}


before = fingerprints()
checks = []
for args in [
    [str(REPO / ".venv/bin/ruff"), "check", "--config", str(REPO / "pyproject.toml"),
     *[str(path) for path in INPUTS[:4] if path.suffix == ".py"]],
    [
        str(REPO / ".venv/bin/ruff"),
        "format",
        "--config",
        str(REPO / "pyproject.toml"),
        "--check",
        *[str(path) for path in INPUTS[:4] if path.suffix == ".py"],
    ],
    [
        str(REPO / ".venv/bin/pytest"),
        "-c",
        "/dev/null",
        "--rootdir=.",
        "-o",
        "cache_dir=.pytest_cache",
        "test_ai_plan_exports_draft.py",
        "-q",
        "--junitxml=export-draft-unit-tests.xml",
    ],
]:
    run = subprocess.run(
        args,
        cwd=HERE,
        env={**os.environ, "PYTHONPATH": str(REPO / "apps/api")},
        text=True,
        capture_output=True,
    )
    checks.append(
        {
            "tool": Path(args[0]).name,
            "arguments": args[1:],
            "exit_code": run.returncode,
            "output": run.stdout + run.stderr,
        }
    )
    print(run.stdout + run.stderr, end="")
after = fingerprints()
proof = {
    "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "scope": "UNREGISTERED_PURE_BACKEND_DRAFT_ONLY",
    "actual_api": "NOT_RUN",
    "actual_native_database": "NOT_RUN",
    "hosted": "NOT_RUN",
    "source_before": before,
    "source_after": after,
    "source_unchanged": before == after,
    "checks": checks,
    "all_passed": before == after and all(check["exit_code"] == 0 for check in checks),
    "test_report": "export-draft-unit-tests.xml",
    "test_report_sha256": hashlib.sha256((HERE / "export-draft-unit-tests.xml").read_bytes()).hexdigest(),
}
(HERE / "export-draft-unit-source-proof.json").write_text(json.dumps(proof, indent=2) + "\n")
raise SystemExit(0 if proof["all_passed"] else 1)
