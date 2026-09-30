"""Synthetic control-plane authority, called only inside guarded fixture bootstrap."""

import os
from uuid import NAMESPACE_URL, uuid5
from fixture_support import FIXTURE_EXPIRES_AT


def provision_platform(c, fixture):
    for name in ["admin", "owner"]:
        c.execute(
            "INSERT INTO impact.platform_operator VALUES(%s,true,%s,'Synthetic local fixture only') ON CONFLICT DO NOTHING",
            (fixture["actors"][name]["identity_id"], FIXTURE_EXPIRES_AT),
        )
    c.execute(
        "INSERT INTO impact.deployment_qualification VALUES(%s,%s,%s,'LOCAL_ONLY','http://127.0.0.1:8080/realms/impact-dev','','local-development-privacy','Synthetic recovery fixture; not production evidence',3650,%s,true) ON CONFLICT DO NOTHING",
        (
            str(uuid5(NAMESPACE_URL, "impact-local-qualification")),
            str(uuid5(NAMESPACE_URL, "impact-local-qualification-v1")),
            os.environ.get("IMPACT_ENVIRONMENT", "development"),
            FIXTURE_EXPIRES_AT,
        ),
    )
