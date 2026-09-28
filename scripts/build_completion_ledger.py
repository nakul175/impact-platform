"""Conservative requirement ledger; API presence alone never qualifies a requirement."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalogue = json.loads((ROOT / "specification/contracts/fsd-requirements.json").read_text())
groups = [
    (
        "FR-TEN-001",
        "v0.10–0.13 implement operator-requested profiles, owner acceptance, independent activation, readiness/impact checks, access fencing and durable work holds. Initial access now requires an owner proposal, separate administrator acceptance and independent operator approval of fixed capability/expiry ceilings; business grants still require separate review. Recovery-contact nomination, registered-account/MFA verification, independent approval, replacement/renewal, revocation and current eligibility now gate activation/reactivation. v0.13 adds reviewed renewal/extension of unexpired delegated authority: the owner pins the exact current ceilings, grants and administrative assignments of both administrators, the second administrator accepts, an independent operator approves within 7 days and within 90 days of expiry, and a database-owned applicator re-dates only the pinned rows. Limits: expired authority is not renewable, tenants without exactly one second administrator are unsupported, and renewal requires current readiness including recovery-contact evidence. Partial: external channel verification/invitations, unavailable-owner recovery, support/exit access, workers, credential rechecks, archival/deletion and native concurrency remain open.",
        [
            "apps/api/impact_api/tenant_lifecycle.py",
            "qualification/test_tenant_lifecycle.py",
            "tools/browser/tenant-check.mjs",
            "docs/RELEASE-0.10.md",
            "apps/api/impact_api/access_bootstrap.py",
            "qualification/test_access_bootstrap.py",
            "tools/browser/bootstrap-check.mjs",
            "docs/RELEASE-0.11.md",
            "apps/api/impact_api/recovery_contacts.py",
            "qualification/test_recovery_contacts.py",
            "tools/browser/recovery-check.mjs",
            "docs/RELEASE-0.12.md",
            "apps/api/impact_api/authority_renewal.py",
            "qualification/test_authority_renewal.py",
            "tools/browser/renewal-check.mjs",
            "docs/RELEASE-0.13.md",
        ],
    ),
    (
        "FR-IAM-009",
        "Provisioned-identity invitations, membership changes, independent role approval, suspension and revocation are implemented. v0.13 adds reviewed renewal/extension of unexpired delegated authority within the existing ceilings: owner proposal, second-administrator consent and independent operator approval, with no capability widening and no resurrection of revoked grants. Federation assurance, recovery, all identity providers, renewal of expired authority, administrator replacement and full departure inventory are not qualified.",
        [
            "apps/api/impact_api/administration.py",
            "qualification/test_administration.py",
            "docs/RELEASE-0.2.md",
            "apps/api/impact_api/authority_renewal.py",
            "qualification/test_authority_renewal.py",
            "tools/browser/renewal-check.mjs",
            "docs/RELEASE-0.13.md",
        ],
    ),
    (
        "FR-TEN-003 FR-IAM-001 FR-IAM-002 FR-IAM-006 FR-IAM-008 FR-IAM-013 FR-IAM-014 FR-ACC-003 FR-ACC-006 FR-ACC-012",
        "Provisioned-identity invitations, membership changes, independent role approval, suspension and revocation are implemented. Federation assurance, recovery, all identity providers and full departure inventory are not qualified.",
        [
            "apps/api/impact_api/administration.py",
            "qualification/test_administration.py",
            "docs/RELEASE-0.2.md",
        ],
    ),
    (
        "FR-ACC-001 FR-ACC-002 FR-ACC-004 FR-ACC-005 FR-ACC-011 FR-SEC-003 FR-SEC-004 FR-SEC-007 FR-SEC-012 FR-INT-004 FR-INT-005",
        "Implemented routes enforce explicit grants, tenant fences, natural-person independence, revisions and retry receipts. Native database concurrency, every future module, audit tamper evidence and production assurance remain open.",
        [
            "apps/api/impact_api/store.py",
            "apps/api/impact_api/auth.py",
            "qualification/test_live_application.py",
        ],
    ),
    (
        "FR-PLN-006 FR-PRG-001 FR-PRG-005 FR-PRG-006 FR-PRG-007 FR-IND-001 FR-IND-002 FR-IND-005 FR-IND-007 FR-IND-008 FR-IND-009 FR-IND-010 FR-IND-012 FR-DQ-006",
        "Manual FLOW measures, independently approved definitions/plans, reviewed obligation exceptions, eligible assignments, reference selection and programme readiness are implemented. Historical expected, required and excepted counts are preserved. Rich planning, reference administration, automated schedules and the other measurement profiles remain open.",
        ["apps/api/impact_api/measurement.py", "qualification/test_work_center.py", "docs/RELEASE-0.7.md"],
    ),
    (
        "FR-CAL-001 FR-CAL-002 FR-CAL-003 FR-CAL-005 FR-CAL-008 FR-CAL-009 FR-CAL-010 FR-CAL-015 FR-DAT-008 FR-ANA-004",
        "Decimal SUM and pooled ratios, revision-bound lineage, explicit contributor coverage and stale-result flags are implemented. Hierarchy, stock, overlap, weighting, dimensions and production workload qualification are not implemented.",
        [
            "apps/api/impact_api/domain.py",
            "apps/api/impact_api/service.py",
            "qualification/test_measurement.py",
        ],
    ),
    (
        "FR-CAL-011 FR-DAT-009 FR-WFL-001 FR-WFL-002 FR-WFL-003 FR-WFL-004 FR-WFL-010",
        "Single-stage independent review and governed source/plan/assignment amendments are implemented. Affected provisional result revisions receive durable invalidations and personal recalculation work; current approved inputs produce a replacement revision while old lineage remains immutable. Cross-period aggregates, dashboards, reports, distributed artifacts, bulk amendments, configurable multistage policies and escalation remain open.",
        ["apps/api/impact_api/work.py", "qualification/test_work_center.py", "docs/RELEASE-0.7.md"],
    ),
    (
        "FR-WFL-006",
        "A personal work centre implements deduplicated recalculation assignments and safe in-app notices with event identity, acknowledgement and exact-retry protection. Due obligations, returned work, preferences, digests, provider delivery attempts and escalations remain open.",
        ["apps/api/impact_api/work.py", "apps/web/src/WorkCenter.tsx", "docs/RELEASE-0.7.md"],
    ),
    (
        "FR-WFL-007 FR-WFL-008",
        "Programme-period close previews pin plans, sources and provisional results; independently reviewed exclusions remain visible but do not block required completion. Approval creates official results and an immutable versioned snapshot. Scoped, time-bounded restatement preserves and supersedes the original. Optional-late-source policy, distributed-artifact impact and multi-period downstream regeneration remain open.",
        [
            "apps/api/impact_api/period_governance.py",
            "qualification/test_period_governance.py",
            "docs/RELEASE-0.5.md",
        ],
    ),
    (
        "FR-RPT-003 FR-RPT-005 FR-RPT-007 FR-RPT-009 FR-RPT-010",
        "Internal reports bind to a locked snapshot, approved template and official result/evidence revisions. Independent approval records an append-only reconciliation digest. Numeric narrative claims must use known binding placeholders; deterministic semantic HTML and CSV artifacts are frozen for an independently reviewed, named-recipient, expiring disclosure and every view/download is logged. Withdrawal closes access without deleting artifacts or history. Charts, PDF/DOCX/XLSX, anonymous publication, delivery, supersession notices and distributed-artifact handling remain open.",
        [
            "apps/api/impact_api/reporting.py",
            "qualification/test_reporting.py",
            "qualification/test_publication.py",
            "docs/RELEASE-0.6.md",
            "docs/RELEASE-0.8.md",
        ],
    ),
    (
        "FR-RPT-004 FR-UX-001 FR-UX-002 FR-UX-003 FR-UX-004 FR-UX-005 FR-UX-009 FR-OPS-005",
        "Browser workspaces, labelled dialogs, bound narrative authoring, controlled-publication actions, explicit status and health endpoints are implemented. Full accessibility/usability qualification, anonymous publication, service monitoring and all remaining screens are open.",
        ["apps/web/src/main.tsx", "tools/browser/reporting-check.mjs", "docs/IMPLEMENTATION.md"],
    ),
    (
        "FR-TEN-002 FR-TEN-010 FR-IAM-003 FR-IAM-006 FR-IAM-008 FR-IAM-010 FR-IAM-013 FR-ACC-002",
        "v0.9 adds versioned custom roles, independently reviewed flat group access, immediate organisation moves with cycle checks, renewal without old-access resurrection, nominated custody transfer, self-service session revocation/preferences and configured ACR enforcement. v0.13 adds reviewed renewal/extension of unexpired delegated authority (owner proposal pinning the exact current ceilings, second-administrator acceptance, independent operator approval, database-owned re-dating of only the pinned rows); expired authority is not renewable and single-administrator tenants are unsupported. Further onboarding acceptance, provider MFA/recovery qualification, action-bound step-up, future-effective organisation impact and full access certification remain open.",
        [
            "apps/api/impact_api/workspace_administration.py",
            "apps/api/impact_api/account.py",
            "qualification/test_workspace_administration.py",
            "tools/browser/workspace-check.mjs",
            "docs/RELEASE-0.9.md",
            "apps/api/impact_api/authority_renewal.py",
            "qualification/test_authority_renewal.py",
            "tools/browser/renewal-check.mjs",
            "docs/RELEASE-0.13.md",
        ],
    ),
]
partial = {key: (description, evidence) for ids, description, evidence in groups for key in ids.split()}
requirements = []
for group in ["functional", "nonfunctional"]:
    for req in catalogue[group]:
        description, evidence = partial.get(
            req["id"],
            (
                "No complete implementation and acceptance evidence mapped. Retain the original acceptance criteria; this requirement remains open.",
                [],
            ),
        )
        requirements.append(
            {
                **req,
                "category": group,
                "status": "PARTIAL" if req["id"] in partial else "PENDING",
                "assessment": description,
                "evidence_paths": evidence,
                "release_gate": "Complete the original acceptance criteria and record passing implementation and qualification evidence.",
            }
        )
assert len(requirements) == 307 and len({r["id"] for r in requirements}) == 307
assert set(partial) <= {r["id"] for r in requirements}
for requirement in requirements:
    for path in requirement["evidence_paths"]:
        assert (ROOT / path).is_file(), path
summary = dict(Counter(r["status"] for r in requirements))
result = {
    "build": "0.13.0",
    "assessment_date": "2026-09-28",
    "enterprise_complete": False,
    "method": "PARTIAL means tested behavior exists for a bounded subset; PENDING does not imply that a scaffold or design contract is an implementation. No enterprise acceptance is inferred from passing subset tests.",
    "summary": summary,
    "requirements": requirements,
}
(ROOT / "docs/COMPLETION-LEDGER.json").write_text(json.dumps(result, indent=2) + "\n")
lines = [
    "# Requirement completion ledger",
    "",
    result["method"],
    "",
    f"Scope: 270 functional requirements and 37 non-functional qualification requirements. Status: {summary}. Enterprise completion: **false**.",
    "",
    "| Requirement | Title | Status | Evidence |",
    "|---|---|---|---|",
]
for req in requirements:
    paths = ", ".join(f"[{Path(p).name}](../{p})" for p in req["evidence_paths"])
    lines.append(f"| {req['id']} | {req['title']} | {req['status']} | {paths or 'Pending'} |")
(ROOT / "docs/COMPLETION-LEDGER.md").write_text("\n".join(lines) + "\n")
print(json.dumps(summary))
