"""Separate the implemented domain API from the larger design contract."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/api"))
from impact_api.contracts import SPEC  # noqa: E402
from impact_api.ai_enablement_contracts import IMPLEMENTED as AI_ENABLEMENT_ROUTES  # noqa: E402
from impact_api.ai_adoption_contracts import IMPLEMENTED as AI_ADOPTION_ROUTES  # noqa: E402
from impact_api.ai_planning_contracts import IMPLEMENTED as AI_PLANNING_ROUTES  # noqa: E402
from impact_api.service import READ_ROUTES, WRITE_ROUTES, ACTIONS  # noqa: E402
from impact_api.administration_contracts import COMMANDS, ADMIN_READS  # noqa: E402
from impact_api.measurement_contracts import SPECIAL_READS  # noqa: E402
from impact_api.reporting_contracts import SPECIAL_READS as REPORTING_READS  # noqa: E402
from impact_api.planning_contracts import SPECIAL_READS as PLANNING_READS  # noqa: E402
from impact_api.planning_contracts import LOGFRAME_READS  # noqa: E402
from impact_api.forms_contracts import SPECIAL_READS as FORMS_READS  # noqa: E402
from impact_api.evidence_contracts import (  # noqa: E402
    SPECIAL_READS as EVIDENCE_READS,
    IMPLEMENTED as EVIDENCE_ROUTES,
)
from impact_api.export_contracts import SPECIAL_READS as EXPORT_READS  # noqa: E402
from impact_api.dashboard_contracts import SPECIAL_READS as DASHBOARD_READS  # noqa: E402
from impact_api.audit_export_contracts import IMPLEMENTED as AUDIT_EXPORT_ROUTES  # noqa: E402
from impact_api.privacy_contracts import IMPLEMENTED as PRIVACY_ROUTES  # noqa: E402
from impact_api.retention_contracts import IMPLEMENTED as RETENTION_ROUTES  # noqa: E402
from impact_api.publication_contracts import (  # noqa: E402
    SPECIAL_READS as PUBLICATION_READS,
    DIRECTORY_READS as PUBLICATION_DIRECTORIES,
)

allowed = set()
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in SPECIAL_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in REPORTING_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in PLANNING_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in LOGFRAME_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in FORMS_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in EXPORT_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in DASHBOARD_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in PUBLICATION_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in PUBLICATION_DIRECTORIES)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in EVIDENCE_READS)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in EVIDENCE_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in PRIVACY_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in RETENTION_ROUTES)
allowed.add(("post", "/v1/tenants/{tenant_id}/disclosure-requests"))
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AUDIT_EXPORT_ROUTES)
for route in READ_ROUTES:
    allowed.update(
        {
            ("get", "/v1/tenants/{tenant_id}/" + route),
            ("get", "/v1/tenants/{tenant_id}/" + route + "/{object_id}"),
        }
    )
for route in WRITE_ROUTES:
    allowed.update(
        {
            ("post", "/v1/tenants/{tenant_id}/" + route),
            ("patch", "/v1/tenants/{tenant_id}/" + route + "/{object_id}"),
        }
    )
for route, actions in ACTIONS.items():
    for action in actions:
        allowed.add(("post", "/v1/tenants/{tenant_id}/" + route + "/{object_id}/actions/" + action))
for route in ADMIN_READS:
    allowed.add(("get", "/v1/tenants/{tenant_id}/" + route))
for route, action in COMMANDS:
    allowed.add(
        ("post", "/v1/tenants/{tenant_id}/" + route + ("/{object_id}/actions/" + action if action else ""))
    )
spec = json.loads(json.dumps(SPEC))
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_ENABLEMENT_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_ADOPTION_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_PLANNING_ROUTES)
spec["info"]["title"] = "Impact Platform — implemented domain API"
spec["info"]["description"] = (
    "Implemented domain subset only. Support, authentication and health routes are documented in docs/IMPLEMENTATION.md."
)
spec["paths"] = {
    path: {k: v for k, v in node.items() if (k, path) in allowed or k == "parameters"}
    for path, node in spec["paths"].items()
    if any(p == path for _, p in allowed)
}
(ROOT / "packages/contracts/openapi-implemented.json").write_text(json.dumps(spec, indent=2) + "\n")
lines = ["# Implemented domain operations", "", "| Method | Path | Capability |", "|---|---|---|"]
for method, path in sorted(allowed, key=lambda x: (x[1], x[0])):
    entry = spec["paths"][path][method]
    lines.append("| " + method.upper() + " | `" + path + "` | `" + entry["x-capability"] + "` |")
(ROOT / "docs/API-INVENTORY.md").write_text("\n".join(lines) + "\n")
print("Exported", len(allowed), "domain operations")
