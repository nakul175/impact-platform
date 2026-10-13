"""Deny-by-default batch resource checks; denied selectors disclose no outcome row."""

import re
from uuid import UUID

from .domain import DomainError
from .store import authorize, context, load

CAPABILITY = re.compile(r"[a-z][a-z0-9.-]{0,99}")
KIND = re.compile(r"[A-Z][A-Za-z0-9]{0,99}")


def _invalid():
    raise DomainError("VALIDATION_FAILED", 400, reason="RESOURCE_CHECK_INVALID")


class AccessChecks:
    def __init__(self, service):
        self.service = service

    def permitted(self, identity, tenant, body):
        if not isinstance(body, dict) or set(body) != {"selectors"}:
            _invalid()
        selectors = body["selectors"]
        if not isinstance(selectors, list) or not 1 <= len(selectors) <= 100:
            _invalid()
        canonical, seen = [], set()
        for selector in selectors:
            if not isinstance(selector, dict) or set(selector) != {
                "selector_id",
                "object_id",
                "object_type",
                "capability",
            }:
                _invalid()
            try:
                object_id = str(UUID(selector["object_id"]))
            except (TypeError, ValueError, AttributeError):
                _invalid()
            if (
                not isinstance(selector["selector_id"], str)
                or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", selector["selector_id"])
                or not isinstance(selector["object_type"], str)
                or not KIND.fullmatch(selector["object_type"])
                or not isinstance(selector["capability"], str)
                or not CAPABILITY.fullmatch(selector["capability"])
                or selector["selector_id"] in seen
            ):
                _invalid()
            seen.add(selector["selector_id"])
            canonical.append({**selector, "object_id": object_id})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "check_permitted_resources", hidden=True)
            permitted = []
            for selector in canonical:
                try:
                    load(
                        c,
                        ctx,
                        selector["object_id"],
                        selector["object_type"],
                        selector["capability"],
                    )
                except DomainError as error:
                    if error.status != 404:
                        raise
                    continue
                permitted.append({"selector_id": selector["selector_id"], "permitted": True})
            return {"permitted": permitted}
