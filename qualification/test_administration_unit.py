"""Pure identity normalization, invitation-token and administration-contract checks."""

import json
from types import SimpleNamespace
from urllib.parse import unquote, urlparse
from uuid import uuid4
import pytest
from impact_api.administration import Administration
from impact_api.administration_contracts import COMMANDS
from impact_api.contracts import OPERATIONS, SPEC
from impact_api.domain import DomainError
from impact_api.identity_profile import normalize_email, email_hash, masked_email


@pytest.mark.parametrize(
    "value",
    [
        None,
        42,
        "",
        " a@example.test",
        "a@example.test ",
        ".a@example.test",
        "a..b@example.test",
        "a.@example.test",
        "a@localhost",
        "a@-example.test",
        "a\n@example.test",
        "é@example.test",
        "a" * 65 + "@example.test",
    ],
)
def test_invalid_invitation_email(value):
    with pytest.raises(DomainError):
        normalize_email(value)


def test_verified_email_canonicalization_is_explicit_and_not_provider_specific():
    assert normalize_email("Person+News@Example.TEST") == "person+news@example.test"
    assert email_hash("PERSON@EXAMPLE.TEST") == email_hash("person@example.test")
    assert len(email_hash("person@example.test")) == 32
    assert email_hash("a.b@example.test") != email_hash("ab@example.test")
    assert email_hash("a+tag@example.test") != email_hash("a@example.test")
    assert masked_email("Person@Example.TEST") == "pe***@example.test"


def test_invitation_signature_is_bound_to_tenant_id_generation_and_separate_key():
    service = Administration(
        SimpleNamespace(
            invitation_secret="a" * 64, cookie_secret="b" * 64, public_origin="https://example.test"
        ),
        None,
        None,
    )
    tenant, obj, generation = (str(uuid4()) for _ in range(3))
    token = service.invitation_token(tenant, obj, generation)
    assert token == service.invitation_token(tenant, obj, generation)
    for alternate in [
        (str(uuid4()), obj, generation),
        (tenant, str(uuid4()), generation),
        (tenant, obj, str(uuid4())),
    ]:
        assert token != service.invitation_token(*alternate)
    original = {"object_id": obj, "invitation_generation": generation}
    public = service.present_receipt(tenant, original)
    assert "invitation_url" not in original
    payload = json.loads(unquote(urlparse(public["invitation_url"]).fragment[7:]))
    assert payload == {"tenant_id": tenant, "token": token}
    service.s.cookie_secret = "c" * 64
    assert token == service.invitation_token(tenant, obj, generation)
    service.s.invitation_secret = "d" * 64
    assert token != service.invitation_token(tenant, obj, generation)


@pytest.mark.parametrize("definition", list(COMMANDS.values()), ids=[v[0] for v in COMMANDS.values()])
def test_each_administrative_command_has_closed_schema_exact_capability_and_fresh_assurance(definition):
    operation, capability, schema, expected, fields = definition
    request = SPEC["components"]["schemas"][schema]
    data = SPEC["components"]["schemas"][schema + "Data"]
    assert request["additionalProperties"] is False and data["additionalProperties"] is False
    assert ("expected_revision" in request["required"]) == expected
    assert set(data["required"]) == set(fields)
    policy = OPERATIONS[operation]
    assert policy["capability"] == capability and policy["method"] == "POST"
    assert policy["fresh_assurance_seconds"] == (None if operation == "accept_invitation" else 300)


@pytest.mark.parametrize("secret", ["", "x" * 47, "c" * 64])
def test_production_requires_separate_strong_invitation_key(secret, monkeypatch, tmp_path):
    from impact_api.config import Settings

    for field in Settings.__dataclass_fields__:
        monkeypatch.delenv("IMPACT_" + field.upper(), raising=False)
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
        cookie_secret="c" * 64,
        invitation_secret=secret,
    )
    config_file = tmp_path / "settings.json"
    config_file.write_text(json.dumps(config))
    monkeypatch.setenv("IMPACT_CONFIG_FILE", str(config_file))
    with pytest.raises(ValueError, match="separate invitation"):
        Settings.load()
