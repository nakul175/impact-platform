"""Reviewed server activation never substitutes tenant policy or weakens production defaults."""

import pytest

from impact_api.ai_policy import validate_policy, require
from impact_api.ai_runtime_activation import REVIEWABLE_USE_CASES, reviewed_use_cases
from impact_api.config import Settings
from impact_api.domain import DomainError
from reviewed_ai_runtime_fixture import rules


@pytest.mark.parametrize(
    "value", ["UNKNOWN", "INDICATOR_DESIGN,INDICATOR_DESIGN", "INDICATOR_DESIGN,", [], True]
)
def test_reviewed_activation_rejects_nonclosed_or_duplicate_identifiers(value):
    with pytest.raises(ValueError):
        reviewed_use_cases(value, "test")


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_hosted_environment_cannot_activate_local_reviewed_cases(environment):
    with pytest.raises(ValueError):
        Settings(
            environment=environment,
            app_dsn="unused",
            identity_dsn="unused",
            public_origin="unused",
            issuer="unused",
            client_id="unused",
            audience="unused",
            jwks_url="unused",
            authorization_url="unused",
            token_url="unused",
            cookie_secret="x" * 64,
            ai_reviewed_use_cases="INDICATOR_DESIGN",
        )


def test_default_is_empty_and_partial_activation_is_exact():
    assert reviewed_use_cases("", "test") == ()
    assert reviewed_use_cases("IMPORT_CLEANING", "development") == ("IMPORT_CLEANING",)


@pytest.mark.parametrize("case", REVIEWABLE_USE_CASES)
def test_policy_and_runtime_both_require_reviewed_activation_and_current_tenant_authority(case):
    rule = next(row for row in rules() if row["use_case"] == case)
    with pytest.raises(DomainError) as blocked:
        validate_policy({"use_cases": [rule]})
    assert blocked.value.reason == "AI_USE_CASE_RESERVED"
    approved = validate_policy({"use_cases": [rule]}, activated_use_cases=(case,))[0]
    policy = {"version": 1, "use_cases": {case: approved}}
    args = (policy, case, 1, "CONFIDENTIAL", "openai-us", "en", tuple(rule["tools"]), rule["purposes"][0])
    assert require(*args, activated_use_cases=(case,)) == approved
    # Config rollback must refuse even a previously persisted enabled tenant policy.
    with pytest.raises(DomainError) as rollback:
        require(*args)
    assert (rollback.value.status, rollback.value.reason) == (503, "AI_USE_CASE_DISABLED")
    with pytest.raises(DomainError) as destination:
        require(
            policy,
            case,
            1,
            "CONFIDENTIAL",
            "unapproved",
            "en",
            purpose=rule["purposes"][0],
            activated_use_cases=(case,),
        )
    assert destination.value.reason == "AI_POLICY_BLOCKED"
    disabled = {"version": 1, "use_cases": {case: {**approved, "enabled": False}}}
    with pytest.raises(DomainError) as tenant:
        require(disabled, *args[1:], activated_use_cases=(case,))
    assert tenant.value.reason == "AI_USE_CASE_DISABLED"
