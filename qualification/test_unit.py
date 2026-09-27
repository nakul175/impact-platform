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
