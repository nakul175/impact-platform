"""Closed read contract for source-backed diagnosis opportunity mappings."""

from copy import deepcopy
from .measurement_contracts import closed

VERSION = "1.43.0"
ROOT = "ai-enablement/diagnoses/{object_id}/opportunity-map"
RANK_ROOT = "ai-enablement/diagnoses/{object_id}/opportunity-ranking"
IMPLEMENTED = [("get", ROOT), ("post", RANK_ROOT)]


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
    input_link = {
        "problem_id": deepcopy(uid),
        "field": {"enum": ["description", "affected_area"]},
    }
    schemas["AIDiagnosisInputLink"] = closed(input_link, list(input_link))
    rationale = {
        "plain_language": {"type": "string", "minLength": 1, "maxLength": 1000},
        "diagnosis_input_links": {
            "type": "array",
            "minItems": 1,
            "maxItems": 2,
            "uniqueItems": True,
            "items": {"$ref": "#/components/schemas/AIDiagnosisInputLink"},
        },
    }
    schemas["AIOpportunityRationale"] = closed(rationale, list(rationale))
    opportunity = {
        "pattern_id": {"type": "string", "minLength": 1, "maxLength": 100},
        "kind": {"enum": ["AI_ASSISTED", "TECHNOLOGY", "PROCESS_FIX"]},
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
        "rationale": {"$ref": "#/components/schemas/AIOpportunityRationale"},
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
    rank_request = {
        "revision_id": deepcopy(uid),
        "profile": {"$ref": "#/components/schemas/AIEnablementProfile"},
    }
    schemas["AIMappedOpportunityRankingRequest"] = closed(rank_request, list(rank_request))
    ranked = deepcopy(schemas["AIOpportunityRanking"]["properties"])
    ranked.update(
        diagnosis_id=deepcopy(uid),
        diagnosis_revision=deepcopy(uid),
        pattern_edition={"type": "string", "minLength": 1},
    )
    schemas["AIMappedOpportunityRanking"] = closed(ranked, list(ranked))
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
    rank_path = "/v1/tenants/{tenant_id}/" + RANK_ROOT
    spec["paths"][rank_path] = {
        "parameters": [
            {"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)},
            {"name": "object_id", "in": "path", "required": True, "schema": deepcopy(uid)},
        ],
        "post": {
            "operationId": "rank_mapped_ai_opportunities",
            "summary": "Rank exact mapped opportunities with the organisation weights",
            "x-capability": "ai.enablement.read",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AIMappedOpportunityRankingRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Edition- and revision-pinned ranking",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AIMappedOpportunityRanking"}
                        }
                    },
                }
            },
        },
    }
    policy["operations"].append(
        {
            "operation_id": "rank_mapped_ai_opportunities",
            "method": "POST",
            "path": rank_path,
            "capability": "ai.enablement.read",
            "role_templates": ["TENANT_ADMIN"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
        }
    )
