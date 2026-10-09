"""Versioned editorial opportunity scores (US-MP-03): impact, effort and cost per editorial use case.

Owned by Imprana editorial and reviewed by an advisor (Sprint 1 decision). The values below are the
first editorial draft; advisor review is pending, which `STATUS` says and every ranking response
repeats. They are kept outside `ai_enablement_catalog.catalog()` on purpose: the catalogue is
archived with every saved adoption plan (`ai_content_archives.py`, `ai_content_schema_v1.json`), and
changing a score must never change that archived guidance.

Scale: every score is an integer from 1 to 5.

- impact: 1 = small expected benefit for a nonprofit team, 5 = large. Higher is better.
- effort: 1 = little staff time and change to start, 5 = a lot. Lower is better (reverse-scored).
- cost: 1 = little or no spending to start, 5 = substantial spending. Lower is better (reverse-scored).

Readiness is not editorial: it is computed for each organisation brief from the capacity gaps
`assess()` finds (`ai_ranking.readiness`). A use case without all three editorial scores is never
ranked; it is listed as "Not ranked: scores incomplete". Changing any value means a new
`SCORE_VERSION`.
"""

from copy import deepcopy

SCORE_VERSION = "imprana-opportunity-scores-2026-10-09.1"
STATUS = "EDITORIAL_DRAFT_PENDING_ADVISOR_REVIEW"
CRITERIA = ("impact", "effort", "cost")
MINIMUM, MAXIMUM = 1, 5

# Keyed by the use-case ID of ai_enablement_catalog._USE_CASES. A missing key, or a criterion
# missing from an entry, means "not scored yet".
_SCORES = {
    "data_foundation": {"impact": 4, "effort": 3, "cost": 1},
    "communications": {"impact": 3, "effort": 1, "cost": 1},
    "knowledge_search": {"impact": 3, "effort": 4, "cost": 3},
    "learning_material": {"impact": 3, "effort": 2, "cost": 2},
    "health_communications": {"impact": 4, "effort": 3, "cost": 2},
    "livelihood_resources": {"impact": 3, "effort": 2, "cost": 2},
    "environment_briefs": {"impact": 2, "effort": 2, "cost": 2},
    "mel_narratives": {"impact": 4, "effort": 3, "cost": 2},
}


def validate_table(table):
    """A score table maps use-case IDs to partial {criterion: integer 1-5}; raises ValueError."""
    if not isinstance(table, dict):
        raise ValueError("The score table must be an object.")
    for use_case, scores in table.items():
        if not isinstance(use_case, str) or not use_case or not isinstance(scores, dict):
            raise ValueError("Each use case needs an object of scores.")
        for criterion, value in scores.items():
            if criterion not in CRITERIA:
                raise ValueError("Unknown score criterion " + repr(criterion) + ".")
            if type(value) is not int or not MINIMUM <= value <= MAXIMUM:
                raise ValueError("Scores are integers from 1 to 5.")
    return table


def scores():
    """An isolated copy of the editorial table; callers cannot change later rankings."""
    return deepcopy(validate_table(_SCORES))
