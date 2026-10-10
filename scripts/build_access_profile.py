"""Generate the onboarding access profile apps/api/impact_api/bootstrap_profile.json (initial-access-v2).

Each role bundle is derived from the generated access policy rather than written by hand: a role holds
exactly the capabilities of the implemented, non-purpose operations whose policy row names its role
template (packages/contracts/access-policy.json `role_templates`). The purpose-required capabilities
of implemented operations (audit export, privacy cases) are listed separately under `purpose_bound`:
they enter the reviewed delegation ceiling (migration 0028 `apply_initial_authority`) but no role
template, so they can be held only as purpose-bound grants issued through an independently reviewed
purpose-grant request. Run after scripts/build_contracts.py and export_implemented_api.py; the unit
test qualification/test_usable_staging_unit.py fails when the checked-in profile differs.

    python scripts/build_access_profile.py [--check]
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "apps/api/impact_api/bootstrap_profile.json"
VERSION = "initial-access-v2"
# Profile role -> the policy role template it is derived from. TENANT_ADMIN is always granted to the
# two reviewed administrators; the others become role templates the administrators may assign through
# independently reviewed access requests. AUDIT_READER is the policy's tenant OPERATOR template
# (audit-event reading), renamed so that it is never confused with a platform operator.
ROLES = {
    "TENANT_ADMIN": "TENANT_ADMIN",
    "MEL_ADMIN": "MEL_ADMIN",
    "AUTHOR": "AUTHOR",
    "REVIEWER": "REVIEWER",
    "PROGRAMME_MANAGER": "PROGRAMME_MANAGER",
    "DATA_STEWARD": "DATA_STEWARD",
    "ENUMERATOR": "ENUMERATOR",
    "ANALYST": "ANALYST",
    "PRIVACY": "PRIVACY",
    "AUDIT_READER": "OPERATOR",
    "EXTERNAL": "EXTERNAL",
    # US-MP-03 (0.38.0): the Operations Head persona; read-only capabilities of implemented operations.
    "FINANCE": "FINANCE",
}


def implemented_operations():
    spec = json.loads((ROOT / "packages/contracts/openapi-implemented.json").read_text())
    return {
        operation["operationId"]
        for node in spec["paths"].values()
        for operation in node.values()
        if isinstance(operation, dict) and "operationId" in operation
    }


def build():
    policy = json.loads((ROOT / "packages/contracts/access-policy.json").read_text())
    implemented = implemented_operations()
    rows = [row for row in policy["operations"] if row["operation_id"] in implemented]
    roles = {
        name: sorted(
            {
                row["capability"]
                for row in rows
                if not row.get("purpose_required") and template in row["role_templates"]
            }
        )
        for name, template in ROLES.items()
    }
    purpose_bound = sorted({row["capability"] for row in rows if row.get("purpose_required")})
    return {"version": VERSION, "roles": roles, "purpose_bound": purpose_bound}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 when the checked-in profile differs")
    args = parser.parse_args()
    text = json.dumps(build(), indent=2) + "\n"
    if args.check:
        if PROFILE.read_text() != text:
            print("bootstrap_profile.json is stale: run scripts/build_access_profile.py")
            return 1
        return 0
    PROFILE.write_text(text)
    print("Wrote " + str(PROFILE.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
