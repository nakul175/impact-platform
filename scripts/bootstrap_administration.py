"""Explicit synthetic fixture provisioning, not a runtime authority inference mechanism."""

from types import SimpleNamespace
from uuid import NAMESPACE_URL, uuid5
from impact_api.contracts import OPERATIONS
from impact_api.service import READ_ROUTES, WRITE_ROUTES, ACTIONS
from impact_api.administration_contracts import ADMIN_READS, COMMANDS
from impact_api.measurement_contracts import SPECIAL_READS
from impact_api.reporting_contracts import SPECIAL_READS as REPORTING_READS
from impact_api.identity_profile import email_hash, masked_email
from impact_api.store import Context, write
from fixture_support import FIXTURE_EXPIRES_AT as EXPIRY, FIXTURE_STARTS_AT

ISSUER = "http://127.0.0.1:8080/realms/impact-dev"


def deterministic(value):
    return str(uuid5(NAMESPACE_URL, "impact-access-v1:" + value))


def provision(c, fixture):
    actual = {verb + "_" + route.replace("-", "_") for route in READ_ROUTES for verb in ["get", "list"]}
    actual |= {verb + "_" + route.replace("-", "_") for route in WRITE_ROUTES for verb in ["create", "patch"]}
    actual |= {
        "action_" + route.replace("-", "_") + "_" + action
        for route, actions in ACTIONS.items()
        for action in actions
    }
    actual |= {entry[0] for entry in SPECIAL_READS.values()}
    actual |= {entry[0] for entry in REPORTING_READS.values()}
    administrative = {
        definition[0] for definition in COMMANDS.values() if definition[0] != "accept_invitation"
    } | {"list_" + route.replace("-", "_") for route in ADMIN_READS}
    templates = {}
    for role in ["AUTHOR", "REVIEWER", "PROGRAMME_MANAGER", "ANALYST", "EXTERNAL", "TENANT_ADMIN"]:
        operations = administrative if role == "TENANT_ADMIN" else actual
        templates[role] = sorted(
            {
                OPERATIONS[op]["capability"]
                for op in operations
                if op in OPERATIONS
                and role in OPERATIONS[op]["role_templates"]
                and not OPERATIONS[op].get("purpose_required")
            }
        )
    for name, actor in fixture["actors"].items():
        email = name + "@example.test"
        c.execute(
            "INSERT INTO impact.identity_profile VALUES(%s,%s,%s,%s,now()) ON CONFLICT(identity_id) DO NOTHING",
            (actor["identity_id"], name.replace("_", " ").title(), email_hash(email), masked_email(email)),
        )
        c.execute(
            "INSERT INTO impact.member_profile VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING",
            (actor["tenant_id"], actor["membership_id"], name.replace("_", " ").title(), masked_email(email)),
        )
    for tenant in [fixture["tenant_a"], fixture["tenant_b"]]:
        owner = fixture["actors"]["owner" if tenant == fixture["tenant_a"] else "other_tenant"]
        ctx = Context(
            tenant,
            owner["principal_id"],
            owner["membership_id"],
            SimpleNamespace(natural_identity_id=owner["natural_identity_id"]),
            0,
            0,
            [],
        )
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute(
            "INSERT INTO impact.tenant_custody VALUES(%s,%s) ON CONFLICT DO NOTHING",
            (tenant, owner["membership_id"]),
        )
        scope = str(
            c.execute(
                "SELECT scope_id FROM impact.scope_definition WHERE tenant_id=%s AND scope_type='TENANT' LIMIT 1",
                (tenant,),
            ).fetchone()["scope_id"]
        )
        for name, caps in templates.items():
            obj = deterministic(tenant + ":role:" + name)
            previous = c.execute(
                "SELECT r.*,v.payload,v.revision_number FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=%s",
                (tenant, obj),
            ).fetchone()
            if not previous or (
                previous["lifecycle_state"] == "Active" and previous["payload"]["capabilities"] != caps
            ):
                write(
                    c,
                    ctx,
                    "RoleTemplate",
                    {
                        "managed_by": "impact-access-v1",
                        "name": name,
                        "capabilities": caps,
                        "administrative": name == "TENANT_ADMIN",
                    },
                    "Active",
                    previous=previous,
                    object_id=obj,
                    track_author=False,
                )
        if tenant != fixture["tenant_a"]:
            continue
        for name in ["owner", "admin"]:
            actor = fixture["actors"][name]
            ctx = Context(
                tenant,
                actor["principal_id"],
                actor["membership_id"],
                SimpleNamespace(natural_identity_id=actor["natural_identity_id"]),
                0,
                0,
                [],
            )
            for cap in sorted({OPERATIONS[op]["capability"] for op in administrative}):
                existing = c.execute(
                    "SELECT 1 FROM impact.grant_current g WHERE g.tenant_id=%s AND g.subject_id=%s AND g.capability=%s AND g.purpose IS NULL",
                    (tenant, actor["principal_id"], cap),
                ).fetchone()
                obj = deterministic(name + ":grant:" + cap)
                # An original OR additive fixture grant prevents re-provisioning, even if revoked.
                if (
                    not existing
                    and not c.execute(
                        "SELECT 1 FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                        (tenant, obj),
                    ).fetchone()
                ):
                    write(
                        c,
                        ctx,
                        "Grant",
                        {
                            "subject_id": actor["principal_id"],
                            "capability": cap,
                            "scope_id": scope,
                            "starts_at": FIXTURE_STARTS_AT,
                            "expires_at": EXPIRY,
                            "issuer_id": actor["principal_id"],
                        },
                        "Active",
                        object_id=obj,
                        track_author=False,
                    )
            for cap in sorted(set().union(*map(set, templates.values()))):
                c.execute(
                    "INSERT INTO impact.grant_authority VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                    (
                        tenant,
                        deterministic(name + ":authority:" + cap),
                        actor["principal_id"],
                        cap,
                        scope,
                        EXPIRY,
                    ),
                )
        for name, actor in fixture["actors"].items():
            if actor["tenant_id"] != tenant:
                continue
            for role in actor["roles"]:
                if role not in templates:
                    continue
                template = deterministic(tenant + ":role:" + role)
                row = c.execute(
                    "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                    (tenant, template),
                ).fetchone()
                grants = c.execute(
                    "SELECT object_id FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s AND capability=ANY(%s) AND purpose IS NULL",
                    (tenant, actor["principal_id"], templates[role]),
                ).fetchall()
                c.execute(
                    "INSERT INTO impact.member_role_assignment VALUES(%s,%s,%s,%s,%s,%s,%s,%s::uuid[]) ON CONFLICT DO NOTHING",
                    (
                        tenant,
                        deterministic(name + ":assignment:" + role),
                        actor["membership_id"],
                        template,
                        row["head_revision"],
                        scope,
                        EXPIRY,
                        [str(g["object_id"]) for g in grants],
                    ),
                )
    invitee = {
        "identity_id": deterministic("invitee"),
        "natural_identity_id": deterministic("invitee-natural"),
    }
    c.execute(
        "INSERT INTO impact.auth_identity VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING",
        (invitee["identity_id"], ISSUER, invitee["identity_id"], invitee["natural_identity_id"]),
    )
    c.execute(
        "INSERT INTO impact.identity_profile VALUES(%s,%s,%s,%s,now()) ON CONFLICT DO NOTHING",
        (
            invitee["identity_id"],
            "Invited colleague",
            email_hash("invitee@example.test"),
            masked_email("invitee@example.test"),
        ),
    )
    return {"invitee": invitee}
