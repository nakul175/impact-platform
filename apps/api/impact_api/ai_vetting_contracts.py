"""Public, closed description of solution vetting criteria and listing review states."""

from .measurement_contracts import closed

VERSION = "1.38.0"
PATH = "/v1/public/ai-vetting-criteria"
IMPLEMENTED = [("get", PATH)]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    criterion = closed({"id": {"type": "string"}, "label": {"type": "string"}, "description": {"type": "string"}}, ["id", "label", "description"])
    listing = closed({"solution_id": {"type": "string"}, "status": {"enum": ["EDITORIAL_REVIEW_PENDING", "VETTED_FOR_PILOT", "WITHDRAWN"]}, "last_reviewed_on": {"type": "string", "format": "date"}}, ["solution_id", "status", "last_reviewed_on"])
    schemas["AIVettingPublication"] = closed({"criteria_edition": {"type": "string"}, "meaning": {"type": "string"}, "criteria": {"type": "array", "minItems": 1, "maxItems": 20, "items": criterion}, "listings": {"type": "array", "maxItems": 100, "items": listing}}, ["criteria_edition", "meaning", "criteria", "listings"])
    spec["paths"][PATH] = {"get": {"operationId": "get_public_ai_vetting_criteria", "summary": "Read public solution vetting criteria and listing states", "x-capability": "public", "x-contract-version": VERSION, "responses": {"200": {"description": "Public vetting criteria", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AIVettingPublication"}}}}, "503": {"description": "Publication metadata invalid", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AIDiagnosisError"}}}}}}}
