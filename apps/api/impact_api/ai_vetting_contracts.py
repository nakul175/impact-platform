"""Public, closed description of solution vetting criteria and listing review states."""

from .measurement_contracts import closed

VERSION = "1.39.0"
PATH = "/v1/public/ai-vetting-criteria"
DISCLOSURE_PATH = "/v1/public/ai-solution-disclosures"
IMPLEMENTED = [("get", PATH), ("get", DISCLOSURE_PATH)]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    criterion = closed({"id": {"type": "string"}, "label": {"type": "string"}, "description": {"type": "string"}}, ["id", "label", "description"])
    listing = closed({"solution_id": {"type": "string"}, "status": {"enum": ["EDITORIAL_REVIEW_PENDING", "VETTED_FOR_PILOT", "WITHDRAWN"]}, "last_reviewed_on": {"type": "string", "format": "date"}}, ["solution_id", "status", "last_reviewed_on"])
    schemas["AIVettingPublication"] = closed({"criteria_edition": {"type": "string"}, "meaning": {"type": "string"}, "criteria": {"type": "array", "minItems": 1, "maxItems": 20, "items": criterion}, "listings": {"type": "array", "maxItems": 100, "items": listing}}, ["criteria_edition", "meaning", "criteria", "listings"])
    disclosure = closed({"status": {"enum": ["NONE_KNOWN", "DISCLOSED"]}, "relationship_types": {"type": "array", "uniqueItems": True, "items": {"enum": ["referral_fee", "revenue_share", "reseller", "sponsorship", "ownership"]}}, "statement": {"type": "string", "minLength": 1, "maxLength": 1000}, "declared_on": {"type": "string", "format": "date"}, "editorial_confirmation": {"enum": ["PENDING", "CONFIRMED"]}}, ["status", "relationship_types", "statement", "declared_on", "editorial_confirmation"])
    disclosure_listing = closed({"solution_id": {"type": "string"}, "solution_name": {"type": "string"}, "provider": {"type": "string"}, "commercial_disclosure": disclosure}, ["solution_id", "solution_name", "provider", "commercial_disclosure"])
    schemas["AICommercialDisclosurePublication"] = closed({"content_version": {"type": "string"}, "meaning": {"type": "string"}, "listings": {"type": "array", "maxItems": 100, "items": disclosure_listing}}, ["content_version", "meaning", "listings"])
    spec["paths"][PATH] = {"get": {"operationId": "get_public_ai_vetting_criteria", "summary": "Read public solution vetting criteria and listing states", "x-capability": "public", "x-contract-version": VERSION, "responses": {"200": {"description": "Public vetting criteria", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AIVettingPublication"}}}}, "503": {"description": "Publication metadata invalid", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AIDiagnosisError"}}}}}}}
    spec["paths"][DISCLOSURE_PATH] = {"get": {"operationId": "get_public_ai_solution_disclosures", "summary": "Read commercial disclosure for every published solution", "x-capability": "public", "x-contract-version": VERSION, "responses": {"200": {"description": "Public commercial disclosure directory", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AICommercialDisclosurePublication"}}}}, "503": {"description": "A listing is missing a valid disclosure", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AIDiagnosisError"}}}}}}}
