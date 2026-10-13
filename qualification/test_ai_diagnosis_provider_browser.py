"""Optional combined real-provider/Chrome diagnosis qualification.

Uses existing native test --idp keycloak --pooler pgbouncer infrastructure.
No development bearer helpers, production identities, provider resources or
workflow activation. The default suites skip this separately opted-in browser
case; a skip is not a pass or an original-criterion waiver.
"""

import hashlib
import json
import os
from pathlib import Path
import subprocess
from uuid import UUID

import pytest

from test_live_idp import db
from test_live_idp import idp as idp

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_IDP") != "keycloak"
    or os.environ.get("IMPACT_NATIVE_TEST") != "1"
    or os.environ.get("IMPACT_DIAGNOSIS_PROVIDER_BROWSER") != "1",
    reason="Optional real-provider Chrome check needs explicit owned native/pooler browser qualification",
)


def test_real_provider_chrome_diagnosis_logout_and_custody_have_no_extra_domain_effects(idp):
    assert idp["config"]["dev_auth"] is False
    assert os.environ.get("IMPACT_DB_POOLER") == "pgbouncer-transaction"
    local = Path(os.environ["IMPACT_TEST_LOCAL"])
    output = local / "diagnosis-provider-browser.json"
    script = ROOT / "tools/browser/ai-diagnosis-provider-check.mjs"
    before = hashlib.sha256(script.read_bytes()).hexdigest()
    # The browser driver needs only private synthetic provider details and loopback
    # origin. Do not inherit privileged fixture/login connections or libpq hints.
    permitted = {
        "PATH",
        "HOME",
        "TMPDIR",
        "LANG",
        "NODE_PATH",
        "IMPACT_TEST_LOCAL",
        "IMPACT_BASE_URL",
        "IMPACT_IDP_FILE",
        "IMPACT_BROWSER_EXECUTABLE",
        "IMPACT_ENVIRONMENT",
        "IMPACT_NATIVE_TEST",
        "IMPACT_IDP",
        "IMPACT_DB_POOLER",
        "IMPACT_POOLER_POOL_SIZE",
        "IMPACT_ALLOW_FIXTURE_LOAD",
    }
    env = {key: value for key, value in os.environ.items() if key in permitted}
    env["IMPACT_BROWSER_EVIDENCE_FILE"] = str(output)
    log = local / "diagnosis-provider-browser.log"
    with log.open("w") as stream:
        result = subprocess.run(
            ["node", str(script)],
            cwd=ROOT,
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            timeout=180,
            check=False,
        )
    assert result.returncode == 0, "Combined provider browser failed; preserve its safe local report"
    report = json.loads(output.read_text())
    assert report["dev_auth"] is False
    assert len(report["results"]) == 3
    assert all(row["status"] == "passed" and row["assertions"] > 0 for row in report["results"])
    assert report["forbidden_requests"] == []
    assert report["uncaught_error_names"] == []
    assert report["cleanup_failures"] == []
    assert hashlib.sha256(script.read_bytes()).hexdigest() == before
    assert str(UUID(report["object_id"])) == report["object_id"]
    operations = report["operation_ids"]
    assert len(operations) == len(set(operations)) == 2
    assert all(str(UUID(operation)) == operation for operation in operations)
    with db() as connection:
        tenant = idp["fixture"]["tenant_a"]
        versions = connection.execute(
            "SELECT revision_id,payload FROM impact.object_revision "
            "WHERE tenant_id=%s AND object_id=%s ORDER BY revision_number",
            (tenant, report["object_id"]),
        ).fetchall()
        assert [row["payload"]["diagnosis_state"] for row in versions] == ["Draft", "Completed"]
        assert [str(row["revision_id"]) for row in versions] == [
            report["draft_revision_id"],
            report["completed_revision_id"],
        ]
        assert all(row["payload"]["title"] == report["title"] for row in versions)
        assert all(
            row["payload"]["problems"][0]["supporting_evidence"] == report["supporting_evidence"]
            for row in versions
        )
        assert (
            connection.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND operation_id=ANY(%s::uuid[])",
                (tenant, operations),
            ).fetchone()["n"]
            == 2
        )
        assert (
            connection.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current "
                "WHERE tenant_id=%s AND object_reference=%s",
                (tenant, report["object_id"]),
            ).fetchone()["n"]
            == 2
        )
    report["readonly_native_counts"] = {"revisions": 2, "receipts": 2, "audit": 2}
    report["checker_sha256"] = before
    output.write_text(json.dumps(report, indent=2) + "\n")
