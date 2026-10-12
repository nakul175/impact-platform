"""Closed read contract for source-backed diagnosis opportunity mappings."""

from copy import deepcopy
from .measurement_contracts import closed

VERSION = "1.40.0"
ROOT = "ai-enablement/diagnoses/{object_id}/opportunity-map"
IMPLEMENTED = [("get", ROOT)]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    example = {
        "example_id": {"type": "string", "minLength": 1, "maxLength": 100},
        "organisation": {"type": "string", "minLength": 1, "maxLength": 150},
        "title": {"type": "string", "minLength": 1, "maxLength": 200},
        "source_url": {"type": "string", "format": "uri", "pattern": "^https://"},
        "checked_on": {"type": "string", "format": "date"},
        "summary": {"type": "string", "minLength": 1, "maxLength": 500},
    }
    schemas["AIOpportunityExample"] = closed(example, list(example))
    opportunity = {
        "pattern_id": {"type": "string", "minLength": 1, "maxLength": 100},
        "kind": {"enum": ["AI_ASSISTED", "TECHNOLOGY"]},
        "title": {"type": "string", "minLength": 1, "maxLength": 200},
        "description": {"type": "string", "minLength": 1, "maxLength": 500},
        "real_world_examples": {
            "type": "array",
            "minItems": 1,
            "maxItems": 10,
            "items": {"$ref": "#/components/schemas/AIOpportunityExample"},
        },
        "match_basis": {
            "type": "array",
            "minItems": 1,
            "maxItems": 20,
            "uniqueItems": True,
            "items": {"type": "string"},
        },
    }
    schemas["AIOpportunity"] = closed(opportunity, list(opportunity))
    problem = {
        "problem_id": deepcopy(uid),
        "opportunities": {
            "type": "array",
            "maxItems": 20,
            "items": {"$ref": "#/components/schemas/AIOpportunity"},
        },
    }
    schemas["AIProblemOpportunityMap"] = closed(problem, list(problem))
    mapping = {
        "diagnosis_id": deepcopy(uid),
        "diagnosis_revision": deepcopy(uid),
        "pattern_edition": {"type": "string"},
        "mapping_rule_version": {"type": "string"},
        "mapping_state": {"enum": ["COMPLETE", "INCOMPLETE"]},
        "problems": {
            "type": "array",
            "maxItems": 20,
            "items": {"$ref": "#/components/schemas/AIProblemOpportunityMap"},
        },
        "unmapped_problem_ids": {
            "type": "array",
            "maxItems": 20,
            "uniqueItems": True,
            "items": deepcopy(uid),
        },
        "disclaimer": {"type": "string", "minLength": 1, "maxLength": 500},
    }
    schemas["AIOpportunityMapping"] = closed(mapping, list(mapping))
    path = "/v1/tenants/{tenant_id}/" + ROOT
    spec["paths"][path] = {
        "parameters": [
            {"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)},
            {"name": "object_id", "in": "path", "required": True, "schema": deepcopy(uid)},
            {"name": "revision_id", "in": "query", "required": False, "schema": deepcopy(uid)},
        ],
        "get": {
            "operationId": "get_ai_opportunity_map",
            "summary": "Map a completed diagnosis to source-backed opportunities",
            "x-capability": "ai.diagnosis.read",
            "responses": {
                "200": {
                    "description": "Current or exact-revision mapping",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIOpportunityMapping"}}
                    },
                }
            },
        },
    }
    policy["operations"].append(
        {
            "operation_id": "get_ai_opportunity_map",
            "method": "GET",
            "path": path,
            "capability": "ai.diagnosis.read",
            "role_templates": ["TENANT_ADMIN"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
        }
    )
