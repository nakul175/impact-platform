import json
from functools import lru_cache
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from .config import ROOT
from .domain import DomainError

SPEC = json.loads((ROOT / "packages/contracts/openapi.json").read_text())
BASE = "urn:impact:contract"
REGISTRY = Registry().with_resource(
    BASE, Resource.from_contents({"$schema": "https://json-schema.org/draft/2020-12/schema", **SPEC})
)
ENTITIES = {
    x["route"]: x for x in json.loads((ROOT / "specification/contracts/entity-catalogue.json").read_text())
}
OPERATIONS = {
    x["operation_id"]: x
    for x in json.loads((ROOT / "packages/contracts/access-policy.json").read_text())["operations"]
}
# Operations this build serves (scripts/export_implemented_api.py). Only their capabilities can
# be delegated through custom roles; the rest of the policy describes the design contract.
IMPLEMENTED_OPERATIONS = {
    operation["operationId"]
    for node in json.loads((ROOT / "packages/contracts/openapi-implemented.json").read_text())["paths"].values()
    for operation in node.values()
    if isinstance(operation, dict) and "operationId" in operation
}
DELEGABLE_CAPABILITIES = frozenset(
    p["capability"]
    for p in OPERATIONS.values()
    if p["operation_id"] in IMPLEMENTED_OPERATIONS and not p.get("purpose_required")
)
REFERENCES = json.loads((ROOT / "specification/database/reference-map.json").read_text())


@lru_cache
def validator(name):
    return Draft202012Validator(
        {"$ref": BASE + "#/components/schemas/" + name}, registry=REGISTRY, format_checker=FormatChecker()
    )


def validate(name, value):
    errors = sorted(validator(name).iter_errors(value), key=lambda e: str(list(e.path)))
    if errors:
        raise DomainError(
            "VALIDATION_FAILED",
            fields=[
                {
                    "path": ".".join(map(str, e.path)) or "$",
                    "message": "Value does not satisfy " + str(e.validator) + ".",
                }
                for e in errors[:20]
            ],
        )
    return value
