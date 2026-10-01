"""Install explicit development grants and generate local credentials; never runs in production."""

import hashlib
import json
import os
import secrets
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import NAMESPACE_URL, uuid5

import psycopg
from psycopg.rows import dict_row
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/api"))
from impact_api.config import boolean  # noqa: E402
from impact_api.store import Context, write  # noqa: E402
from impact_api.contracts import OPERATIONS  # noqa: E402
from bootstrap_administration import provision  # noqa: E402
from bootstrap_platform import provision_platform  # noqa: E402
from fixture_support import FIXTURE_EXPIRES_AT, FIXTURE_STARTS_AT, fixture_database_allowed  # noqa: E402


# The issuer the fixture's auth_identity rows carry (specification/fixtures/seed.sql).
FIXTURE_ISSUER = "http://127.0.0.1:8080/realms/impact-dev"


def bootstrap(local, idp=None):
    """idp: the details scripts/idp.py start() returned; the API is then configured for that live
    provider (dev_auth off) and the fixture identities whose subjects exist in the qualification
    realm are re-pointed to its issuer, so each Keycloak user signs in as its fixture actor."""
    if os.environ.get("IMPACT_ALLOW_FIXTURE_LOAD") != "1":
        raise RuntimeError("Explicit local fixture flag is required")
    dsn = os.environ.get(
        "IMPACT_FIXTURE_DSN", "postgresql://postgres:development@127.0.0.1:55432/impact_dev?sslmode=disable"
    )
    fixture = json.loads((ROOT / "specification/fixtures/api-fixture.json").read_text())
    with psycopg.connect(dsn, row_factory=dict_row, prepare_threshold=None) as c:
        if not fixture_database_allowed(c.execute("SELECT current_database() AS db").fetchone()["db"]):
            raise RuntimeError("Fixture database refused")
        c.execute("SELECT set_config('impact.allow_fixtures','true',true)")
        # Fixture purpose labels are not general permission. Append revised, explicit grants.
        for name, actor in fixture["actors"].items():
            tenant = actor["tenant_id"]
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            identity = SimpleNamespace(natural_identity_id=actor["natural_identity_id"])
            ctx = Context(tenant, actor["principal_id"], actor["membership_id"], identity, 0, 0, [])
            general = {p["capability"] for p in OPERATIONS.values() if not p.get("purpose_required")}
            grants = c.execute(
                "SELECT r.*,v.payload,v.revision_number FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision JOIN impact.grant_current g ON g.tenant_id=r.tenant_id AND g.object_id=r.object_id WHERE g.tenant_id=%s AND g.subject_id=%s",
                (tenant, actor["principal_id"]),
            ).fetchall()
            for row in grants:
                data = row["payload"]
                if data.get("purpose") and data["capability"] in general:
                    data = {k: v for k, v in data.items() if k != "purpose"}
                    write(c, ctx, "Grant", data, "Active", row, track_author=False)
                    c.execute(
                        "UPDATE impact.grant_current SET purpose=NULL WHERE tenant_id=%s AND object_id=%s",
                        (tenant, row["object_id"]),
                    )
            capabilities = {
                "observation.submit",
                "indicator.calculate",
                "workflow-templates.read",
                "lineage-manifests.read",
                "collection-plans.read",
                "collection-plans.draft.create",
                "collection-plans.draft.edit",
                "collection-plan.submit",
                "reporting-calendars.read",
                "geographies.read",
                "measurement-members.read",
                "indicator.activate",
                "measurement-changes.read",
                "measurement-changes.draft.create",
                "measurement-changes.draft.edit",
                "measurement-changes.submit",
                "snapshots.read",
                "period-closes.read",
                "restatement-requests.read",
                "period.close",
                "period.restate",
                "notifications.acknowledge",
                "disclosures.read",
                "publication.download",
                "form.submit",
                "imports.read",
                "imports.draft.create",
                "imports.draft.edit",
                "import.preview",
                "import.commit",
                "import.cancel",
                "evidence.attach",
                "report.export",
                # v0.25 part A: purpose-required audit export (OWNER and TENANT_ADMIN templates).
                "audit.export",
            }
            scope = c.execute(
                "SELECT scope_id FROM impact.scope_definition WHERE tenant_id=%s AND scope_type='TENANT' LIMIT 1",
                (tenant,),
            ).fetchone()["scope_id"]
            for cap in capabilities:
                policy = next(p for p in OPERATIONS.values() if p["capability"] == cap)
                if not set(actor["roles"]).intersection(policy["role_templates"]):
                    continue
                obj = str(uuid5(NAMESPACE_URL, "impact-dev-grant:" + name + ":" + cap))
                if c.execute(
                    "SELECT 1 FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s", (tenant, obj)
                ).fetchone():
                    continue
                data = {
                    "subject_id": actor["principal_id"],
                    "capability": cap,
                    "scope_id": str(scope),
                    "starts_at": FIXTURE_STARTS_AT,
                    "expires_at": FIXTURE_EXPIRES_AT,
                    "issuer_id": actor["principal_id"],
                }
                write(c, ctx, "Grant", data, "Active", object_id=obj, track_author=False)
        # This milestone captures manual observations. Preserve the baseline DATASET revision,
        # then explicitly append a development-only manual definition and instance revision.
        author = fixture["actors"]["author"]
        tenant = author["tenant_id"]
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        ctx = Context(
            tenant,
            author["principal_id"],
            author["membership_id"],
            SimpleNamespace(natural_identity_id=author["natural_identity_id"]),
            0,
            0,
            [],
        )
        records = {
            r["key"]: r for r in json.loads((ROOT / "specification/fixtures/records.json").read_text())
        }

        def current(obj):
            return c.execute(
                "SELECT r.*,v.payload,v.revision_number FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=%s",
                (tenant, obj),
            ).fetchone()

        definition = current(records["definition"]["object_id"])
        if definition["payload"]["source_mode"] != "MANUAL" or not definition["payload"].get(
            "numerator_meaning"
        ):
            changed = write(
                c,
                ctx,
                "IndicatorDefinition",
                {
                    **definition["payload"],
                    "source_mode": "MANUAL",
                    "numerator_meaning": "Eligible households with safe water",
                    "denominator_meaning": "Eligible households assessed",
                },
                "Approved",
                definition,
                track_author=False,
            )
            instance = current(records["indicator_a"]["object_id"])
            write(
                c,
                ctx,
                "IndicatorInstance",
                {**instance["payload"], "definition_version": changed["revision_id"]},
                "Active",
                instance,
                track_author=False,
            )
        c.execute(
            "INSERT INTO impact.object_natural_author SELECT DISTINCT r.tenant_id,r.object_id,i.natural_identity_id FROM impact.object_revision r JOIN impact.tenant_principal p ON p.tenant_id=r.tenant_id AND p.principal_id=r.author_id JOIN impact.auth_identity i ON i.identity_id=p.identity_id WHERE r.revision_id=ANY(%s::uuid[]) ON CONFLICT DO NOTHING",
            ([r["revision_id"] for r in records.values()],),
        )
        extra_users = provision(c, fixture)
        provision_platform(c, fixture)
        if idp:
            # Keycloak user IDs are the fixture subjects (the realm is derived from the
            # specification realm), so only the issuer changes; identity IDs, natural persons,
            # memberships and grants stay exactly as the fixture defines them.
            subjects = [u["subject"] for u in idp["users"].values()]
            c.execute(
                "UPDATE impact.auth_identity SET issuer=%s WHERE issuer=%s AND provider_subject=ANY(%s)",
                (idp["issuer"], FIXTURE_ISSUER, subjects),
            )
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        geography = str(uuid5(NAMESPACE_URL, "impact-measurement:geography:demonstration"))
        if not current(geography):
            write(
                c,
                ctx,
                "Geography",
                {"title": "Demonstration region", "code": "DEMO"},
                "Active",
                object_id=geography,
                track_author=False,
            )
    local.mkdir(parents=True, exist_ok=True)
    if not (local / "private.pem").exists():
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        (local / "private.pem").write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
            )
        )
        (local / "public.pem").write_bytes(
            key.public_key().public_bytes(
                serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
    users = json.loads((local / "users.json").read_text()) if (local / "users.json").exists() else {}
    passwords = (
        json.loads((local / "passwords.json").read_text()) if (local / "passwords.json").exists() else {}
    )
    for name, actor in {**fixture["actors"], **extra_users}.items():
        if name not in users:
            password = secrets.token_urlsafe(18)
            salt = secrets.token_bytes(24)
            users[name] = {
                "subject": actor["identity_id"],
                "salt": salt.hex(),
                "password_hash": hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000).hex(),
            }
            passwords[name] = password
    (local / "users.json").write_text(json.dumps(users))
    (local / "passwords.json").write_text(json.dumps(passwords, indent=2))
    previous_config = (
        json.loads((local / "config.json").read_text()) if (local / "config.json").exists() else {}
    )
    config = {
        "environment": os.environ.get("IMPACT_ENVIRONMENT", "development"),
        "app_dsn": os.environ.get("IMPACT_APP_DSN", dsn),
        "identity_dsn": os.environ.get("IMPACT_IDENTITY_DSN", dsn),
        "platform_dsn": os.environ.get("IMPACT_PLATFORM_DSN", dsn),
        "public_origin": "http://127.0.0.1:" + os.environ.get("IMPACT_PORT", "8000"),
        "issuer": FIXTURE_ISSUER,
        "client_id": "impact-web",
        "audience": "impact-api",
        "jwks_url": "",
        "authorization_url": "",
        "token_url": "",
        "cookie_secret": previous_config.get("cookie_secret") or secrets.token_urlsafe(64),
        "invitation_secret": previous_config.get("invitation_secret") or secrets.token_urlsafe(64),
        "delivery_secret": previous_config.get("delivery_secret") or secrets.token_urlsafe(64),
        "dev_auth": True,
        "dev_db_serial": os.environ.get("IMPACT_NATIVE_TEST") != "1",
        "require_unprivileged_db": boolean(
            "require_unprivileged_db", os.environ.get("IMPACT_REQUIRE_UNPRIVILEGED_DB", "0")
        ),
        "dev_users_file": str(local / "users.json"),
        "dev_public_key": str(local / "public.pem"),
        "fixture_id": fixture["fixture_id"],
        # Evidence bytes (v0.22): a private directory of this run, scanned by the deterministic
        # signature scanner (EICAR test file only; not an anti-malware engine).
        "object_store_dir": str((local / "objects").resolve()),
        "evidence_scanner": "eicar-signature",
    }
    # Grace secrets and the development signing key set written by scripts/rotate_secrets.py survive a
    # re-run of this bootstrap (v0.25 part A); a fresh run directory has none.
    for name in ["cookie_secret_previous", "invitation_secret_previous", "delivery_secret_previous"]:
        if previous_config.get(name):
            config[name] = previous_config[name]
    if previous_config.get("dev_signing_keys") and config["dev_auth"] and not idp:
        config["dev_signing_keys"] = previous_config["dev_signing_keys"]
    if idp:
        config.update(
            issuer=idp["issuer"],
            client_id=idp["client_id"],
            audience=idp["audience"],
            jwks_url=idp["discovery"]["jwks_uri"],
            authorization_url=idp["discovery"]["authorization_endpoint"],
            token_url=idp["discovery"]["token_endpoint"],
            end_session_url=idp["discovery"]["end_session_endpoint"],
            required_acr=idp["required_acr"],
            dev_auth=False,
            dev_users_file="",
            dev_public_key="",
        )
    (local / "config.json").write_text(json.dumps(config, indent=2))
    # The worker's own configuration (v0.16): its login, the two secrets it shares with the API and
    # the synthetic mail sink; never the API's connection strings or cookie secret.
    worker = {
        "environment": config["environment"],
        "worker_dsn": os.environ.get("IMPACT_LOGIN_DSN_WORKER", dsn),
        "public_origin": config["public_origin"],
        "invitation_secret": config["invitation_secret"],
        "delivery_secret": config["delivery_secret"],
        **{
            name: config[name]
            for name in ["invitation_secret_previous", "delivery_secret_previous"]
            if config.get(name)
        },
        "email_adapter": "synthetic",
        "synthetic_sink": str(local / "synthetic-mail.jsonl"),
        "require_unprivileged_db": config["require_unprivileged_db"],
    }
    (local / "worker.json").write_text(json.dumps(worker, indent=2))
    for path in local.iterdir():
        if path.is_file():
            path.chmod(0o600)
    print("Development configuration ready. Credentials: " + str(local / "passwords.json"))
    return config


if __name__ == "__main__":
    bootstrap(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".local/dev")
