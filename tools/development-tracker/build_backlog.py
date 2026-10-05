"""Group source requirements once per shared platform domain; never rescore them."""

from __future__ import annotations

import hashlib
import json
from collections import Counter

from tracker import DATA, ROOT, utc_now
from update import atomic_json

# Domain grouping is an editorial scope index, not an effort or acceptance score.
GROUPS = [
    (
        "access",
        "Organisation, identity and access",
        "TEN IAM ACC",
        [25, 39],
        "Tenant lifecycle, current capability checks, scoped workspaces and reviewed registered-profile upgrades exist locally.",
        "Complete first-organisation onboarding, hosted access-upgrade qualification and acceptance.",
    ),
    (
        "impact-planning",
        "Programmes, results frameworks and indicators",
        "PRG PLN IND",
        [],
        "Governed definitions, results hierarchies, targets and baselines exist.",
        "Workplans and activities, standard indicator libraries and fuller planning semantics.",
    ),
    (
        "collection",
        "Collection, imports and data quality",
        "FRM DAT DQ OFF MIG",
        [],
        "Forms, collection rounds, assignments and bounded spreadsheet imports exist.",
        "Offline collection, reviewed mappings, corrected re-imports and fuller quality controls.",
    ),
    (
        "measurement",
        "Deterministic measurement and evaluation",
        "CAL DIN EVA",
        [],
        "Official arithmetic and frozen period snapshots use governed revisions.",
        "Complete methodological metadata, acceptance scenarios and native contention evidence.",
    ),
    (
        "reporting",
        "Analytics, portfolios and reporting",
        "ANA RPT",
        [],
        "Frozen report packages, dashboard drill-down and bounded portfolio aggregation exist.",
        "Saved views, dashboard authoring, Unicode PDF and broader governed exports.",
    ),
    (
        "evidence",
        "Evidence, revisions and audit",
        "EVD AUD",
        [27],
        "Insert-only revisions and atomic audit/outbox/receipt records are shared by impact and AI plans.",
        "Full repository search, knowledge retrieval and durable provenance/disclosure coverage.",
    ),
    (
        "decisions",
        "Review and consequential decisions",
        "WFL",
        [35],
        "Natural-person independence and immutable approved decisions are existing shared rules.",
        "Full workflow configurability and independent review of future AI/procurement outcomes.",
    ),
    (
        "interoperability",
        "Connectors, portability and reuse",
        "INT PRT",
        [22, 30, 36],
        "Application executor and bounded logframe export are documented current increments.",
        "Kobo and Google connectors, deployment support and complete portability/exit workflows.",
    ),
    (
        "adoption",
        "Nonprofit AI adoption and pilot planning",
        "",
        [1, 2, 3, 6, 21, 24, 34, 37],
        "Readiness assessment, shared adoption drafts and self-reported pilot comparisons exist locally.",
        "Verified quality/evidence, independent pilot acceptance, official impact links and feedback workflows.",
    ),
    (
        "learning",
        "Capacity building and maintained content",
        "",
        [7, 8, 9, 12, 31, 38],
        "Twelve stable lessons, four manual practice worksheets and exact saved-guidance archives exist locally.",
        "Content governance, complete retention, competence evidence, cohorts and governed generated task runs.",
    ),
    (
        "marketplace",
        "Marketplace, procurement and costs",
        "FIN ECO",
        [4, 5, 13, 14, 15, 16, 17, 18, 19, 20],
        "Eight-tool discovery, procurement briefs and deterministic whole-cost comparisons exist locally.",
        "Supplier verification, quote provenance, RFQs, awards, bookings and conditional purchasing/payments policy.",
    ),
    (
        "advisory",
        "AI and human advisory",
        "AI AIQ",
        [10, 11, 23],
        "Consented advisory orchestration has mocked provider qualification and bounded I/O.",
        "Funded live evaluation, money/token controls, human advisory cases and hard process-wide recovery policy.",
    ),
    (
        "privacy",
        "Privacy, participant protection and security",
        "PRV PAR SEC",
        [26],
        "Tenant isolation, sensitive controls, erasure/retention machinery and key rotation have bounded support.",
        "Independent security assessment, restored privacy-erasure replay and complete provider/data-lifecycle policy.",
    ),
    (
        "delivery",
        "Experience, reliability and service operations",
        "UX CMP L10 CAP PER AVL DR OBS OPS MNT SUP",
        [28, 29, 32, 33, 40],
        "Shared web navigation, actual local native recovery checks, Mac operations portability and live ETA tracking are documented.",
        "Hosted/container/live identity-provider qualification, UAT, language UI, off-server backups and support readiness.",
    ),
]


def build() -> dict:
    ledger_path = ROOT / "docs/COMPLETION-LEDGER.json"
    ai_path = ROOT / "docs/nonprofit-ai/v1.0/requirements.json"
    ledger = json.loads(ledger_path.read_text())
    ai = json.loads(ai_path.read_text())
    core_rows = ledger["requirements"]
    ai_rows = ai["functional_requirements"]
    core_seen, ai_seen, domains = set(), set(), []
    for domain_id, title, prefixes, ai_numbers, current, remaining in GROUPS:
        ids = sorted(row["id"] for row in core_rows if row["id"].split("-")[1] in prefixes.split())
        ai_ids = [f"FR-NPA-{number:03d}" for number in ai_numbers]
        if core_seen.intersection(ids) or ai_seen.intersection(ai_ids):
            raise ValueError("A source requirement is assigned more than once")
        core_seen.update(ids)
        ai_seen.update(ai_ids)
        domains.append(
            {
                "id": domain_id,
                "title": title,
                "impact_requirement_ids": ids,
                "ai_requirement_ids": ai_ids,
                "current": current,
                "remaining": remaining,
                "sources": [
                    "docs/IMPLEMENTATION.md",
                    "docs/handover/BACKLOG.md",
                    "docs/nonprofit-ai/v1.0/DEVELOPMENT-0.31.md",
                    "docs/nonprofit-ai/v1.0/DEVELOPMENT-0.32.md",
                ],
            }
        )
    if core_seen != {row["id"] for row in core_rows} or ai_seen != {row["id"] for row in ai_rows}:
        raise ValueError("Consolidated scope is missing or inventing a source requirement")
    counts = Counter(row["status"] for row in core_rows)
    source_paths = [
        "docs/COMPLETION-LEDGER.json",
        "docs/nonprofit-ai/v1.0/requirements.json",
        "docs/IMPLEMENTATION.md",
        "docs/handover/BACKLOG.md",
        "docs/nonprofit-ai/v1.0/DEVELOPMENT-0.31.md",
    ]
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "method": "Each source requirement belongs to exactly one editorial domain. Shared domains are shown once. Counts do not measure effort, accepted scope, overall percentage or remaining person-hours. Source registers are not rewritten.",
        "baseline": {
            "current_build": "0.31.0",
            "tentative_sprint_build": "0.32.0",
            "impact_ledger_build": ledger["build"],
            "impact_ledger_assessment_date": ledger["assessment_date"],
            "impact_requirements": len(core_rows),
            "impact_partial": counts["PARTIAL"],
            "impact_pending": counts["PENDING"],
            "impact_accepted": counts["ACCEPTED"],
            "ai_requirements": len(ai_rows),
            "ai_design_baseline_build": ai["baseline_build"],
            "ai_design_status": ai["status"],
        },
        "source_fingerprints": [
            {"path": path, "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}
            for path in source_paths
        ],
        "domains": domains,
    }


if __name__ == "__main__":
    result = build()
    atomic_json(DATA / "backlog.json", result)
    print(
        json.dumps(
            {
                "domains": len(result["domains"]),
                "impact_requirements": result["baseline"]["impact_requirements"],
                "ai_requirements": result["baseline"]["ai_requirements"],
            }
        )
    )
