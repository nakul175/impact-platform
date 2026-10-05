"""Pure closed-contract and additive-profile checks; no database or live identity."""

from copy import deepcopy
import json
import re
from uuid import uuid4

import pytest

from impact_api.access_upgrade import capabilities, compatible, profile_manifest
from impact_api.access_upgrade_contracts import validate_body
from impact_api.domain import DomainError
from impact_api.config import ROOT
from impact_api.access_bootstrap import PROFILE, PROFILE_HASH


def body():
    return {
        "operation_id": str(uuid4()),
        "expected_revision": str(uuid4()),
        "data": {
            "second_identity_id": str(uuid4()),
            "authority_hash": "a" * 64,
            "profile_hash": "b" * 64,
            "reason": "Reviewed addition of new capabilities",
        },
    }


def test_closed_request_accepts_only_profile_and_current_authority_selectors():
    validate_body(body(), create=True)
    validate_body(
        {
            "operation_id": str(uuid4()),
            "expected_revision": str(uuid4()),
            "data": {"reason": "Independent consent"},
        }
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("capabilities", ["*"]),
        ("approved_by", str(uuid4())),
        ("owner_auth_time", "2026-10-05T08:00:00Z"),
        ("force", True),
    ],
)
@pytest.mark.parametrize("nested", [False, True])
def test_server_owned_authority_and_waivers_are_rejected(field, value, nested):
    request = body()
    (request["data"] if nested else request)[field] = value
    with pytest.raises(DomainError) as error:
        validate_body(request, create=True)
    assert error.value.code == "VALIDATION_FAILED"


@pytest.mark.parametrize(
    "change",
    [
        {"reason": " "},
        {"authority_hash": "0" * 63},
        {"profile_hash": "Z" * 64},
        {"second_identity_id": "unknown"},
    ],
)
def test_invalid_selectors_and_blank_reason_fail_closed(change):
    request = body()
    request["data"].update(change)
    with pytest.raises(DomainError):
        validate_body(request, create=True)


def test_profile_delta_uses_historical_reviewed_manifest_not_current_ceilings():
    source = {
        "version": "synthetic-v1",
        "roles": {"TENANT_ADMIN": ["roles.manage", "old.revoked"]},
        "purpose_bound": ["audit.export"],
    }
    target = deepcopy(source)
    target["roles"]["TENANT_ADMIN"].append("ai.adoption-plans.manage")
    assert capabilities(target) - capabilities(source) == {"ai.adoption-plans.manage"}
    assert compatible(source, target)
    assert "old.revoked" not in capabilities(target) - capabilities(source)


@pytest.mark.parametrize("change", ["remove_capability", "remove_role", "move_admin_capability"])
def test_widening_does_not_silently_remove_previously_reviewed_bundles(change):
    source = {
        "version": "synthetic-v1",
        "roles": {"TENANT_ADMIN": ["roles.manage"], "AUTHOR": ["programme.create"]},
    }
    target = deepcopy(source)
    if change == "remove_capability":
        target["roles"]["AUTHOR"] = []
    elif change == "remove_role":
        target["roles"].pop("AUTHOR")
    else:
        target["roles"]["TENANT_ADMIN"] = []
        target["roles"]["AUTHOR"].append("roles.manage")
    assert not compatible(source, target)


def test_purpose_bound_capability_cannot_be_moved_into_an_ordinary_role():
    source = {
        "version": "synthetic-v1",
        "roles": {"TENANT_ADMIN": ["roles.manage"]},
        "purpose_bound": ["audit.export"],
    }
    target = deepcopy(source)
    target["purpose_bound"] = []
    target["roles"]["TENANT_ADMIN"].append("audit.export")
    assert capabilities(source) == capabilities(target)
    assert not compatible(source, target)


def test_target_manifest_remains_closed_and_contains_no_fabricated_authority():
    target = profile_manifest()
    assert set(target) <= {"version", "roles", "purpose_bound"}
    assert "TENANT_ADMIN" in target["roles"]
    assert all("*" not in caps for caps in target["roles"].values())


def test_additive_migration_registers_the_exact_current_generated_profile():
    sql = (ROOT / "infrastructure/migrations/0036_reviewed_ceiling_widening.sql").read_text()
    seed = re.search(r"VALUES\('([a-f0-9]{64})',\$profile_0036\$(.*?)\$profile_0036\$::jsonb", sql)
    assert seed is not None
    assert seed.group(1) == PROFILE_HASH
    assert json.loads(seed.group(2)) == PROFILE
