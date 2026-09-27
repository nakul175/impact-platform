"""Synthetic control-plane authority, called only inside guarded fixture bootstrap."""

import os
from uuid import NAMESPACE_URL, uuid5


def provision_platform(c, fixture):
    for name in ["admin", "owner"]:
        c.execute(
            "INSERT INTO impact.platform_operator VALUES(%s,true,'2026-12-01T00:00:00Z','Synthetic local fixture only') ON CONFLICT DO NOTHING",
            (fixture["actors"][name]["identity_id"],),
        )
    c.execute(
        "INSERT INTO impact.deployment_qualification VALUES(%s,%s,%s,'LOCAL_ONLY','http://127.0.0.1:8080/realms/impact-dev','','local-development-privacy','Synthetic recovery fixture; not production evidence',3650,'2026-12-01T00:00:00Z',true) ON CONFLICT DO NOTHING",
        (
            str(uuid5(NAMESPACE_URL, "impact-local-qualification")),
            str(uuid5(NAMESPACE_URL, "impact-local-qualification-v1")),
            os.environ.get("IMPACT_ENVIRONMENT", "development"),
        ),
    )
