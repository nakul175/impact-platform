import pytest
from impact_api.contracts import validate, SPEC
from impact_api.domain import calculate, decimal_value, stored, DomainError
from decimal import Decimal

DEFINITION = {
    "combination_rule": "POOLED_RATIO",
    "measurement_type": "PERCENTAGE",
    "unit": "percent",
    "time_semantic": "FLOW",
    "display_decimals": 2,
}


def observation(n, d):
    return {
        "approval_state": "APPROVED",
        "value_state": "PRESENT",
        "value": "0",
        "numerator": n,
        "denominator": d,
    }


def test_pooled_percentage():
    result = calculate(DEFINITION, [observation("50", "100"), observation("1", "10")])
    assert result["numerator"] == "51" and result["denominator"] == "110"
    assert result["value"] == "46.363636363636" and result["displayed_value"] == "46.36"


def test_excludes_unapproved():
    assert (
        calculate(DEFINITION, [{**observation("1", "2"), "approval_state": "DRAFT"}])["reason_code"]
        == "NO_APPROVED_VALUES"
    )


def test_zero_denominator():
    result = calculate(DEFINITION, [observation("0", "0")])
    assert result["value"] is None and result["reason_code"] == "ZERO_DENOMINATOR"


@pytest.mark.parametrize("value", ["1e2", "NaN", "Infinity", 1, None, "01", "1.1234567890123", " 1", "1."])
def test_decimal_input(value):
    with pytest.raises(DomainError):
        decimal_value(value)


@pytest.mark.parametrize("n,d", [("-1", "1"), ("1", "-1"), ("2", "1")])
def test_invalid_components(n, d):
    with pytest.raises(DomainError):
        calculate(DEFINITION, [observation(n, d)])


def test_round_once():
    definition = {**DEFINITION, "combination_rule": "SUM", "measurement_type": "DECIMAL"}
    result = calculate(
        definition, [{**observation("0", "1"), "value": "0.005"}, {**observation("0", "1"), "value": "0.005"}]
    )
    assert result["displayed_value"] == "0.01"


def test_stock_cannot_sum():
    with pytest.raises(DomainError):
        calculate(
            {**DEFINITION, "combination_rule": "SUM", "measurement_type": "COUNT", "time_semantic": "STOCK"},
            [observation("1", "2")],
        )


def test_overflow():
    with pytest.raises(DomainError):
        stored(Decimal("100000000000000000000000000"))


@pytest.mark.parametrize(
    "data",
    [
        {"approval_state": "APPROVED"},
        {"tenant_id": "x"},
        {"created_by": "x"},
        {"lifecycle_state": "Approved"},
    ],
)
def test_server_owned_fields(data):
    with pytest.raises(DomainError):
        validate("ObservationCreate", {"operation_id": "2cc25c88-c8be-4777-9660-b69bc633e5ab", "data": data})


def test_present_requires_value():
    with pytest.raises(DomainError):
        validate("ObservationData", {"value_state": "PRESENT", "value": None})


def test_patch_requires_revision():
    with pytest.raises(DomainError):
        validate(
            "ProgrammePatch",
            {"operation_id": "2cc25c88-c8be-4777-9660-b69bc633e5ab", "data": {"title": "New"}},
        )


def test_additive_contracts():
    assert "/v1/tenants/{tenant_id}/observations/{object_id}/actions/submit" in SPEC["paths"]
    assert "/v1/tenants/{tenant_id}/indicator-instances/{object_id}/actions/calculate" in SPEC["paths"]


def test_canonical_negative_zero():
    assert stored(Decimal("-0")) == "0"


def test_production_refuses_development_identity(monkeypatch, tmp_path):
    import json
    from impact_api.config import Settings

    config = {
        name: "https://example.test"
        for name in ["public_origin", "issuer", "jwks_url", "authorization_url", "token_url"]
    }
    config.update(
        environment="production",
        app_dsn="postgresql://app",
        identity_dsn="postgresql://identity",
        client_id="web",
        audience="api",
        cookie_secret="x" * 64,
        invitation_secret="y" * 64,
        dev_auth=True,
    )
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    monkeypatch.setenv("IMPACT_CONFIG_FILE", str(path))
    monkeypatch.delenv("IMPACT_ENVIRONMENT", raising=False)
    with pytest.raises(ValueError, match="Development settings"):
        Settings.load()


def test_boolean_environment_flags_accept_spellings_and_refuse_the_rest(monkeypatch, tmp_path):
    """IMPACT_REQUIRE_UNPRIVILEGED_DB (and the other boolean fields) accept 1/true/yes/on and
    0/false/no/off case-insensitively; any other spelling is a configuration error, never a
    silent False."""
    import json
    from impact_api.config import Settings, boolean

    for value in ["1", "true", "YES", "On"]:
        assert boolean("require_unprivileged_db", value) is True, value
    for value in ["0", "false", "No", "off", ""]:
        assert boolean("require_unprivileged_db", value) is False, value
    with pytest.raises(ValueError, match="IMPACT_REQUIRE_UNPRIVILEGED_DB must be one of"):
        boolean("require_unprivileged_db", "yes please")
    config = {
        "environment": "test",
        "app_dsn": "postgresql://app",
        "identity_dsn": "postgresql://identity",
        "public_origin": "http://127.0.0.1:8000",
        "issuer": "http://127.0.0.1:8080/realms/impact-dev",
        "client_id": "web",
        "audience": "api",
        "jwks_url": "",
        "authorization_url": "",
        "token_url": "",
        "cookie_secret": "x" * 64,
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    monkeypatch.setenv("IMPACT_CONFIG_FILE", str(path))
    for name in ["IMPACT_ENVIRONMENT", "IMPACT_DEV_AUTH", "IMPACT_DEV_DB_SERIAL"]:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("IMPACT_REQUIRE_UNPRIVILEGED_DB", "True")
    assert Settings.load().unprivileged_db_required is True
    monkeypatch.setenv("IMPACT_REQUIRE_UNPRIVILEGED_DB", "no")
    assert Settings.load().unprivileged_db_required is False
    monkeypatch.setenv("IMPACT_REQUIRE_UNPRIVILEGED_DB", "enabled")
    with pytest.raises(ValueError, match="IMPACT_REQUIRE_UNPRIVILEGED_DB"):
        Settings.load()
    monkeypatch.delenv("IMPACT_REQUIRE_UNPRIVILEGED_DB")
    path.write_text(json.dumps({**config, "require_unprivileged_db": "1"}))
    with pytest.raises(ValueError, match="must be a JSON boolean"):
        Settings.load()


def test_route_missing_from_contract_is_not_found(monkeypatch):
    """#22: a route present in code but absent from the regenerated contract answers the
    not-found envelope (RESOURCE_UNAVAILABLE 404) before any database work, not a 503."""
    import impact_api.service as service

    path = "/v1/tenants/{tenant_id}/programmes"
    assert "programmes" in service.WRITE_ROUTES and service.request_schema(path, "post")
    monkeypatch.setattr(
        service, "SPEC", {**SPEC, "paths": {k: v for k, v in SPEC["paths"].items() if k != path}}
    )
    assert service.request_schema(path, "post") is None
    # No settings or database: reaching either would raise something other than DomainError.
    unconfigured = service.Service.__new__(service.Service)
    body = {"operation_id": "00000000-0000-4000-8000-000000000000", "data": {}}
    with pytest.raises(DomainError) as refused:
        unconfigured.command(None, "00000000-0000-4000-8000-000000000001", "programmes", body, None)
    assert refused.value.code == "RESOURCE_UNAVAILABLE" and refused.value.status == 404
    action = "/v1/tenants/{tenant_id}/programmes/{object_id}/actions/activate"
    monkeypatch.setattr(
        service, "SPEC", {**SPEC, "paths": {k: v for k, v in SPEC["paths"].items() if k != action}}
    )
    with pytest.raises(DomainError) as refused:
        unconfigured.command(
            None, "00000000-0000-4000-8000-000000000001", "programmes", body, None, obj="x", action="activate"
        )
    assert refused.value.status == 404


def test_production_requires_a_separate_delivery_secret(monkeypatch, tmp_path):
    import json
    from impact_api.config import Settings

    config = {
        name: "https://example.test"
        for name in ["public_origin", "issuer", "jwks_url", "authorization_url", "token_url"]
    }
    config.update(
        environment="production",
        app_dsn="postgresql://app",
        identity_dsn="postgresql://identity",
        client_id="web",
        audience="api",
        cookie_secret="x" * 64,
        invitation_secret="y" * 64,
        required_acr="urn:impact:acr:mfa",
    )
    monkeypatch.delenv("IMPACT_ENVIRONMENT", raising=False)
    monkeypatch.delenv("IMPACT_DELIVERY_SECRET", raising=False)
    for secret in ["", "y" * 64, "short"]:
        path = tmp_path / "config.json"
        path.write_text(json.dumps({**config, "delivery_secret": secret}))
        monkeypatch.setenv("IMPACT_CONFIG_FILE", str(path))
        with pytest.raises(ValueError, match="delivery secret"):
            Settings.load()
    path.write_text(json.dumps({**config, "delivery_secret": "z" * 64}))
    assert Settings.load().delivery_secret == "z" * 64


def test_delivery_sealing_is_bound_to_its_intent_and_codes_are_derived():
    from cryptography.exceptions import InvalidTag
    from impact_api.delivery import channel_code, channel_code_hash, render, seal_recipient, unseal_recipient

    secret = "s" * 64
    sealed = seal_recipient(secret, "tenant-a", "MEMBER_INVITATION", "ref-1", "Person@Example.test")
    assert b"person" not in sealed.lower()
    assert unseal_recipient(secret, "tenant-a", "MEMBER_INVITATION", "ref-1", sealed) == "person@example.test"
    for tenant, template, reference, key in [
        ("tenant-b", "MEMBER_INVITATION", "ref-1", secret),
        ("tenant-a", "RECOVERY_CHANNEL_VERIFICATION", "ref-1", secret),
        ("tenant-a", "MEMBER_INVITATION", "ref-2", secret),
        ("tenant-a", "MEMBER_INVITATION", "ref-1", "t" * 64),
    ]:
        with pytest.raises(InvalidTag):
            unseal_recipient(key, tenant, template, reference, sealed)
    code = channel_code(secret, "challenge-1")
    assert len(code) == 8 and code.isdigit() and code == channel_code(secret, "challenge-1")
    assert code != channel_code("t" * 64, "challenge-1")
    assert channel_code_hash(secret, "challenge-1", code) != channel_code_hash(secret, "challenge-2", code)
    subject, body = render("RECOVERY_CHANNEL_VERIFICATION", code=code, expires_at="2026-09-29 12:00")
    assert code in body and "<" not in body
    for fields in [
        {"code": "<b>1</b>", "expires_at": "x"},
        {"code": "1\r\nBcc: x", "expires_at": "x"},
        {"code": "1"},
    ]:
        with pytest.raises(ValueError):
            render("RECOVERY_CHANNEL_VERIFICATION", **fields)
    with pytest.raises(ValueError):
        render("CUSTOM_HTML", url="x", expires_at="x")
