"""Which capabilities can be issued as purpose-bound grants, and for which purposes (v0.26a, gap A4).

Exactly the capabilities of implemented, purpose-required operations: the privacy-case capabilities
for the purposes their policy rows list (DATA_SUBJECT_REQUEST) and the audit export for the purposes
its request accepts. A purpose-less capability is never issued here (it travels in role bundles), and
a capability of an operation this build does not serve is never issued at all.
"""

from .audit_export_contracts import PURPOSES as AUDIT_PURPOSES
from .contracts import IMPLEMENTED_OPERATIONS, OPERATIONS


def purpose_capabilities():
    result = {}
    for row in OPERATIONS.values():
        if row["operation_id"] not in IMPLEMENTED_OPERATIONS or not row.get("purpose_required"):
            continue
        purposes = row.get("purposes") or (AUDIT_PURPOSES if row["capability"] == "audit.export" else [])
        if purposes:
            result.setdefault(row["capability"], set()).update(purposes)
    return {capability: frozenset(purposes) for capability, purposes in result.items()}


PURPOSE_CAPABILITIES = purpose_capabilities()
