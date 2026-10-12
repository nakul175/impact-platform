"""US-CM-07 control-plane partner revenue contracts."""

from jsonschema import Draft202012Validator, FormatChecker
from .domain import DomainError
from .tenant_contracts import UUID, obj, text

MONEY = {"type": "string", "pattern": "^(?=.*[1-9])(?:0|[1-9][0-9]{0,25})(?:\\.[0-9]{1,12})?$"}
DECIMAL = {"type": "string", "pattern": "^(?:0|[1-9][0-9]{0,25})(?:\\.[0-9]{1,12})?$"}
DATE = {"type": "string", "format": "date"}
COMMON = {"operation_id": UUID, "reason": text(1000)}
ENTRY = obj(
    {
        **COMMON,
        "partner_id": UUID,
        "tenant_id": UUID,
        "invoice_id": UUID,
        "amount": MONEY,
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
        "occurred_on": DATE,
    }
)
GENERATE = obj(
    {
        **COMMON,
        "partner_id": UUID,
        "month": {"type": "string", "format": "date", "pattern": "^[0-9]{4}-(?:0[1-9]|1[0-2])-01$"},
    }
)
SETTLE = obj(COMMON)
ENTRY_RESULT = obj(
    {
        "entry_id": UUID,
        "partner_id": UUID,
        "tenant_id": UUID,
        "invoice_id": UUID,
        "amount": MONEY,
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
        "occurred_on": DATE,
        "reconciled": {"const": True},
    }
)
STATEMENT_RESULT = obj(
    {
        "statement_id": UUID,
        "partner_id": UUID,
        "month": DATE,
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
        "amount": DECIMAL,
        "entry_ids": {"type": "array", "items": UUID, "minItems": 1, "uniqueItems": True},
        "reconciled": {"type": "boolean"},
        "settled": {"const": False},
    }
)
SETTLE_RESULT = obj(
    {
        "statement_id": UUID,
        "reconciled": {"const": True},
        "settled": {"const": True},
        "settled_at": {"type": "string", "format": "date-time"},
    }
)
SCHEMAS = {
    "PartnerRevenueEntryCreate": ENTRY,
    "PartnerStatementGenerate": GENERATE,
    "PartnerStatementSettle": SETTLE,
}


def validate_body(name, body):
    errors = list(Draft202012Validator(SCHEMAS[name], format_checker=FormatChecker()).iter_errors(body))
    if errors:
        raise DomainError("VALIDATION_FAILED", 400)


def add_paths(paths, operation):
    paths["/v1/platform/partner-revenue-entries"] = {
        "post": operation("record_partner_revenue", ENTRY, ENTRY_RESULT)
    }
    paths["/v1/platform/partner-statements"] = {
        "post": operation("generate_partner_statement", GENERATE, STATEMENT_RESULT)
    }
    paths["/v1/platform/partner-statements/{statement_id}/actions/settle"] = {
        "parameters": [{"name": "statement_id", "in": "path", "required": True, "schema": UUID}],
        "post": operation("settle_partner_statement", SETTLE, SETTLE_RESULT),
    }
