"""scripts/release_review.py (FR-SEC-001): the release security review check, without a database.

Synthetic registers are checked against a small throwaway repository (one pytest file, one browser
check, one baseline) so every rule is exercised in isolation; the last tests run the check on the real
register and release review, and guard the attack surfaces the register records as BLOCK.
"""

import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import release_review as check  # noqa: E402

DATE = "2026-10-09"
OK_TEST = "qualification/test_alpha.py::test_one"
CLASS_TEST = "qualification/test_alpha.py::TestGroup::test_two"
BROWSER = "tools/browser/alpha-check.mjs::Opens the page"
BASELINE = [
    {"id": "TH01", "title": "Cross tenant object access", "impact": "Critical"},
    {"id": "TH02", "title": "Scope escalation within a tenant", "impact": "High"},
]


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "qualification").mkdir()
    (tmp_path / "qualification/test_alpha.py").write_text(
        "import pytest\n\n\ndef test_one():\n    pass\n\n\n@pytest.mark.parametrize('n', [1])\n"
        "def test_param(n):\n    pass\n\n\nclass TestGroup:\n    def test_two(self):\n        pass\n\n\n"
        "def helper():\n    pass\n"
    )
    (tmp_path / "tools/browser").mkdir(parents=True)
    (tmp_path / "tools/browser/alpha-check.mjs").write_text(
        'await test("Opens the page", async () => {});\nawait test(\n  "Says \\"hello\\" twice",\n'
        '  async () => {},\n);\nconst label = "Not a test";\n'
    )
    (tmp_path / "apps/api").mkdir(parents=True)
    (tmp_path / "apps/api/module.py").write_text("")
    (tmp_path / "specification/contracts").mkdir(parents=True)
    (tmp_path / "specification/contracts/threat-register.json").write_text(json.dumps(BASELINE))
    return tmp_path


def control(cid, layer, depends_on=(), implemented=True):
    return {
        "id": cid,
        "name": "Control " + cid,
        "layer": layer,
        "implemented": implemented,
        "implemented_in": ["apps/api/module.py"] if implemented else [],
        "depends_on": list(depends_on),
        "description": "A synthetic control.",
    }


def decision(kind="MITIGATE", confirmed_by=None):
    return {
        "decision": kind,
        "decided_by": "Claude (agent), proposal for Nakul Jain (owner)",
        "decided_on": DATE,
        "confirmed_by": confirmed_by,
        "rationale": "Synthetic.",
    }


def threat(base, status="TESTED", kind="MITIGATE", tests=(OK_TEST,)):
    return {
        "id": base["id"],
        "origin": "v1",
        "title": base["title"],
        "impact": base["impact"],
        "category": "tenant boundary",
        "asset": "Synthetic asset",
        "attack": "Synthetic attack.",
        "requirements": ["FR-SEC-003"],
        "owner": "Security lead",
        "target_control": "Synthetic target control.",
        "required_verification": "Synthetic verification.",
        "control_refs": ["C-APP", "C-DB"],
        "test_refs": list(tests),
        "verification": {
            "status": status,
            "summary": "Synthetic summary.",
            "gaps": [] if status == "TESTED" else ["A synthetic gap."],
        },
        "residual_decision": decision(kind),
    }


def register(repo):
    return {
        "schema_version": 2,
        "register_id": "impact-platform-threat-register",
        "updated_on": DATE,
        "baseline": {
            "path": "specification/contracts/threat-register.json",
            "schema_version": 1,
            "sha256": hashlib.sha256((repo / check.BASELINE).read_bytes()).hexdigest(),
            "note": "Synthetic baseline.",
        },
        "role_assignment": "Synthetic.",
        "owner_roles": ["Access lead", "Security lead"],
        "categories": [{"id": name, "covers": "Synthetic."} for name in check.CATEGORIES],
        "verification_statuses": {"TESTED": "t", "PARTIAL": "p", "PENDING": "n"},
        "controls": [
            control("C-APP", "application"),
            control("C-DB", "database"),
            control("C-APP-2", "application"),
            control("C-API", "authorization", ["C-APP"]),
            control("C-IDP", "identity"),
            control("C-ON-IDP", "contract", ["C-IDP"]),
            control("C-ALSO-ON-IDP", "database", ["C-IDP"]),
            control("C-TARGET", "process", implemented=False),
        ],
        "threats": [threat(BASELINE[0]), threat(BASELINE[1], tests=(CLASS_TEST, BROWSER))],
        "chains": [
            {
                "id": "CH01",
                "title": "Synthetic chain",
                "path": ["TH01", "TH02"],
                "narrative": "Synthetic.",
                "controls": [
                    {"control_ref": "C-APP", "breaks": "TH01", "evidence": [OK_TEST]},
                    {"control_ref": "C-DB", "breaks": "TH02", "evidence": [CLASS_TEST, BROWSER]},
                ],
                "residual_decision": decision(),
            }
        ],
    }


def review(reg, **changes):
    critical, other = check.split_open(reg)
    document = {
        "schema_version": 1,
        "release": "0.37.0",
        "register": "docs/current/threat-register.json",
        "prepared_by": "Claude (agent), for Nakul Jain (owner)",
        "prepared_on": DATE,
        "passed": False,
        "gates": {
            "G11": {"status": "Not passed", "reason": "Synthetic."},
            "G12": {"status": "Not run", "reason": "Synthetic."},
        },
        "open_critical": critical,
        "open_other": other,
        "impact_reviews": [],
        "evidence": ["apps/api/module.py"],
        "notes": [],
    }
    document.update(changes)
    return document


def problems_of(reg, repo):
    return check.check_register(reg, repo, check.References(repo))


def impact(paths, areas, confirmed_by=None):
    return {
        "id": "IR-0.37-01",
        "change": "Synthetic change.",
        "paths": paths,
        "areas": areas,
        "threats": ["TH01"],
        "summary": "Synthetic.",
        "prepared_by": "Claude (agent), for Nakul Jain (owner)",
        "prepared_on": DATE,
        "confirmed_by": confirmed_by,
    }


# Scenario: Every threat is categorised and linked (passing case)


def test_a_sound_register_and_release_review_pass(repo):
    reg = register(repo)
    assert problems_of(reg, repo) == []
    changed = ["infrastructure/migrations/0042_synthetic.sql", "docs/notes.md"]
    document = review(
        reg, impact_reviews=[impact(["infrastructure/migrations/0042_synthetic.sql"], ["migration"])]
    )
    assert check.check_review(document, reg, changed, repo) == []
    assert check.open_threats(reg) == []


@pytest.mark.parametrize(
    "field", ["category", "control_refs", "owner", "test_refs", "residual_decision", "verification"]
)
def test_a_threat_missing_a_required_field_fails(repo, field):
    reg = register(repo)
    del reg["threats"][0][field]
    problems = problems_of(reg, repo)
    assert any(f"'{field}' is a required property" in problem for problem in problems), problems


def test_empty_links_unknown_category_invented_owner_and_unknown_control_fail(repo):
    for change, expected in [
        ({"control_refs": []}, "control_refs: [] should be non-empty"),
        ({"test_refs": []}, "test_refs: [] should be non-empty"),
        ({"category": "networking"}, "category: 'networking' is not one of"),
        ({"residual_decision": {**decision(), "decision": "IGNORE"}}, "'IGNORE' is not one of"),
        ({"residual_decision": {**decision(), "decided_by": ""}}, "decided_by"),
    ]:
        reg = register(repo)
        reg["threats"][0].update(change)
        problems = problems_of(reg, repo)
        assert any(expected in problem for problem in problems), (change, problems)
    reg = register(repo)
    reg["threats"][0]["owner"] = "Jane Example"
    assert problems_of(reg, repo) == [
        "threat TH01: owner 'Jane Example' is neither a declared owner role nor 'Nakul Jain (owner)'"
    ]
    reg["threats"][0]["owner"] = "Nakul Jain (owner)"
    reg["threats"][0]["control_refs"] = ["C-APP", "C-MISSING"]
    assert problems_of(reg, repo) == ["threat TH01: unknown control C-MISSING"]


def test_acceptance_needs_a_person_and_tested_needs_an_implemented_control(repo):
    reg = register(repo)
    reg["threats"][0]["residual_decision"] = decision("ACCEPT")
    assert problems_of(reg, repo) == [
        "threat TH01: ACCEPT is a risk acceptance and needs confirmed_by (a person)"
    ]
    reg["threats"][0]["residual_decision"] = decision("ACCEPT", confirmed_by="Nakul Jain (owner)")
    assert problems_of(reg, repo) == []
    reg["threats"][0]["control_refs"] = ["C-TARGET"]
    assert problems_of(reg, repo) == [
        "threat TH01: TESTED verification needs at least one implemented control"
    ]
    reg["threats"][0]["verification"] = {"status": "PENDING", "summary": "s", "gaps": []}
    assert any("gaps: [] should be non-empty" in problem for problem in problems_of(reg, repo))


# Scenario: Reject an unresolvable test reference


def test_test_references_resolve_to_real_tests_and_browser_checks(repo):
    references = check.References(repo)
    for ref in [OK_TEST, CLASS_TEST, BROWSER, "qualification/test_alpha.py::test_param[1]"]:
        assert references.problem(ref) is None, ref
    assert references.problem('tools/browser/alpha-check.mjs::Says "hello" twice') is None
    for ref, reason in [
        ("qualification/test_alpha.py::test_missing", "no test test_missing in qualification/test_alpha.py"),
        ("qualification/test_alpha.py::helper", "no test helper in qualification/test_alpha.py"),
        ("qualification/test_alpha.py::TestGroup::test_one", "no test TestGroup::test_one"),
        ("qualification/test_beta.py::test_one", "no such test file qualification/test_beta.py"),
        ("tools/browser/alpha-check.mjs::Not a test", "no browser check named"),
        ("tools/browser/beta-check.mjs::Opens the page", "no such browser check file"),
        ("scripts/run.py::main", "not a pytest node ID"),
    ]:
        assert reason in references.problem(ref), ref


def test_an_unresolvable_test_reference_fails_the_check(repo):
    reg = register(repo)
    reg["threats"][1]["test_refs"] = [CLASS_TEST, "qualification/test_alpha.py::test_renamed"]
    assert problems_of(reg, repo) == [
        "threat TH02: unresolvable test reference qualification/test_alpha.py::test_renamed "
        "(no test test_renamed in qualification/test_alpha.py)"
    ]
    reg = register(repo)
    reg["threats"][0]["test_refs"] = ["tools/browser/alpha-check.mjs::Opens the pages"]
    [problem] = problems_of(reg, repo)
    assert problem.startswith("threat TH01: unresolvable test reference tools/browser/alpha-check.mjs::Opens")


# Scenario: Reject a release review that hides a critical path


@pytest.mark.parametrize(
    "status,kind,reason",
    [
        ("PARTIAL", "MITIGATE", "VERIFICATION_PARTIAL"),
        ("PENDING", "MITIGATE", "VERIFICATION_PENDING"),
        ("TESTED", "BLOCK", "BLOCKED"),
        ("PENDING", "ACCEPT", "VERIFICATION_PENDING"),
    ],
)
def test_an_unresolved_critical_threat_cannot_be_hidden_or_passed(repo, status, kind, reason):
    reg = register(repo)
    reg["threats"][0] = threat(BASELINE[0], status=status, kind=kind)
    if kind == "ACCEPT":
        reg["threats"][0]["residual_decision"]["confirmed_by"] = "Nakul Jain (owner)"
    assert problems_of(reg, repo) == []
    expected = {
        "id": "TH01",
        "title": "Cross tenant object access",
        "impact": "Critical",
        "decision": kind,
        "verification": status,
        "reason": reason,
    }
    assert check.split_open(reg) == ([expected], [])
    # Hidden: the review leaves the open critical threat out.
    hidden = review(reg, open_critical=[])
    assert check.check_review(hidden, reg, (), repo) == [
        f"release review: open_critical hides TH01 'Cross tenant object access' ({reason}); list every unresolved threat"
    ]
    # Listed honestly, but marked passed (or gate G11 Pass): the check fails and names the threat.
    for marked in (
        review(reg, passed=True),
        review(
            reg, gates={"G11": {"status": "Pass", "reason": "x"}, "G12": {"status": "Not run", "reason": "x"}}
        ),
    ):
        problems = check.check_review(marked, reg, (), repo)
        assert (
            f"release review: marked passed while critical threat TH01 'Cross tenant object access' is open ({reason})"
            in problems
        ), problems
    # Not marked passed and listed honestly: the review is accepted as a truthful record.
    assert check.check_review(review(reg), reg, (), repo) == []


def test_review_lists_must_match_the_register_exactly(repo):
    reg = register(repo)
    reg["threats"][1] = threat(BASELINE[1], status="PARTIAL", tests=(CLASS_TEST,))
    honest = review(reg)
    assert [item["id"] for item in honest["open_other"]] == ["TH02"]
    assert check.check_review(honest, reg, (), repo) == []
    stale = copy.deepcopy(honest)
    stale["open_other"][0]["reason"] = "BLOCKED"
    assert (
        "release review: open_other entry TH02 differs from the register"
        in check.check_review(stale, reg, (), repo)[0]
    )
    extra = review(reg, open_critical=[{**honest["open_other"][0], "id": "TH01", "impact": "Critical"}])
    assert any("open_critical lists TH01" in problem for problem in check.check_review(extra, reg, (), repo))


def test_a_passed_review_needs_confirmed_decisions_and_impact_reviews(repo):
    reg = register(repo)
    entry = impact(["apps/api/impact_api/ai_policy.py"], ["ai-module"])
    passed = review(reg, passed=True, impact_reviews=[entry])
    problems = check.check_review(passed, reg, (), repo)
    assert problems == [
        "release review: marked passed while the decision on TH01 is unconfirmed",
        "release review: marked passed while impact review IR-0.37-01 is unconfirmed",
    ]
    reg["threats"][0]["residual_decision"]["confirmed_by"] = "Nakul Jain (owner)"
    entry["confirmed_by"] = "Nakul Jain (owner)"
    assert check.check_review(passed, reg, (), repo) == []


# Scenario: Chained abuse paths have independent controls


def chain_with(repo, *controls):
    reg = register(repo)
    reg["chains"][0]["controls"] = [
        {"control_ref": ref, "breaks": "TH01", "evidence": evidence} for ref, evidence in controls
    ]
    return reg


def test_a_chain_without_two_independent_evidenced_controls_fails(repo):
    message = (
        "chain CH01: no two of its evidenced controls are independent (they share a layer or a dependency)"
    )
    # One layer twice is not independence.
    reg = chain_with(repo, ("C-APP", [OK_TEST]), ("C-APP-2", [OK_TEST]))
    assert problems_of(reg, repo) == [message]
    # Different layers, but one control depends on the other.
    reg = chain_with(repo, ("C-APP", [OK_TEST]), ("C-API", [OK_TEST]))
    assert problems_of(reg, repo) == [message]
    # Different layers, but both rest on the same control.
    reg = chain_with(repo, ("C-ON-IDP", [OK_TEST]), ("C-ALSO-ON-IDP", [OK_TEST]))
    assert problems_of(reg, repo) == [message]
    # Only one control has evidence that resolves.
    reg = chain_with(repo, ("C-APP", [OK_TEST]), ("C-DB", ["qualification/test_alpha.py::test_gone"]))
    assert problems_of(reg, repo) == [
        "chain CH01: unresolvable evidence qualification/test_alpha.py::test_gone for C-DB "
        "(no test test_gone in qualification/test_alpha.py)",
        "chain CH01: needs at least two implemented controls with evidence, has 1",
    ]
    # A control that is not built cannot count, and the schema wants two controls at least.
    reg = chain_with(repo, ("C-APP", [OK_TEST]), ("C-TARGET", [OK_TEST]))
    assert problems_of(reg, repo) == [
        "chain CH01: control C-TARGET is not implemented and cannot count as evidence",
        "chain CH01: needs at least two implemented controls with evidence, has 1",
    ]
    reg = chain_with(repo, ("C-APP", [OK_TEST]))
    assert any("controls: [{" in problem and "is too short" in problem for problem in problems_of(reg, repo))
    # A control breaking a threat outside the path, or an unknown threat in the path.
    reg = chain_with(repo, ("C-APP", [OK_TEST]), ("C-DB", [OK_TEST]))
    reg["chains"][0]["controls"][1]["breaks"] = "TH09"
    reg["chains"][0]["path"] = ["TH01", "TH02", "TH08"]
    assert problems_of(reg, repo) == [
        "chain CH01: unknown threat TH08 in path",
        "chain CH01: control C-DB breaks TH09, which is not in the path",
    ]
    # Independent layers with resolvable evidence pass.
    reg = chain_with(repo, ("C-API", [OK_TEST]), ("C-DB", [BROWSER]))
    assert problems_of(reg, repo) == []


# Scenario: A material change requires an impact review


def test_material_paths_map_to_areas():
    assert check.material(
        [
            "infrastructure/migrations/0042_ai_ranking_weights.sql",
            "apps/api/impact_api/ai_enablement_contracts.py",
            "apps/api/impact_api/ai_ranking.py",
            "apps/api/impact_api/planning_contracts.py",
            "scripts/build_contracts.py",
            "packages/contracts/access-policy.json",
            "packages/contracts/openapi-implemented.json",
            "apps/api/impact_api/planning.py",
            "docs/nonprofit-ai/v1.0/drafts/0.34/ai_plan_export_contracts.py",
            "qualification/test_ai_policy.py",
        ]
    ) == {
        "infrastructure/migrations/0042_ai_ranking_weights.sql": ["migration"],
        "apps/api/impact_api/ai_enablement_contracts.py": ["ai-module", "contracts"],
        "apps/api/impact_api/ai_ranking.py": ["ai-module"],
        "apps/api/impact_api/planning_contracts.py": ["contracts"],
        "scripts/build_contracts.py": ["contracts"],
        "packages/contracts/access-policy.json": ["access-policy"],
    }


def test_a_material_change_without_an_impact_review_fails(repo):
    reg = register(repo)
    changed = [
        "apps/api/impact_api/ai_ranking.py",
        "docs/RELEASE-0.38.md",
        "infrastructure/migrations/0042_ai_ranking_weights.sql",
        "packages/contracts/access-policy.json",
    ]
    problems = check.check_review(review(reg), reg, changed, repo)
    assert problems == [
        f"impact review missing: the change set touches {path} ({area}); add an impact_reviews entry naming it "
        "to docs/evidence/release-review-0.37.0.json"
        for path, area in [
            ("apps/api/impact_api/ai_ranking.py", "ai-module"),
            ("infrastructure/migrations/0042_ai_ranking_weights.sql", "migration"),
            ("packages/contracts/access-policy.json", "access-policy"),
        ]
    ]
    # An entry covering two of the three paths leaves the third reported.
    partial = impact(
        ["apps/api/impact_api/ai_ranking.py", "packages/contracts/access-policy.json"],
        ["ai-module", "access-policy"],
    )
    problems = check.check_review(review(reg, impact_reviews=[partial]), reg, changed, repo)
    assert [problem.split(" (")[0] for problem in problems] == [
        "impact review missing: the change set touches infrastructure/migrations/0042_ai_ranking_weights.sql"
    ]
    # An entry must list the areas of what it covers and name known threats.
    wrong = impact(["infrastructure/migrations/0042_ai_ranking_weights.sql"], ["ai-module"])
    wrong["threats"] = ["TH99"]
    problems = check.check_review(review(reg, impact_reviews=[partial, wrong]), reg, changed, repo)
    assert problems == [
        "impact review IR-0.37-01: unknown threat TH99",
        "impact review IR-0.37-01: infrastructure/migrations/0042_ai_ranking_weights.sql is in area(s) migration not listed",
    ]
    wrong["threats"], wrong["areas"] = ["TH01"], ["migration"]
    assert check.check_review(review(reg, impact_reviews=[partial, wrong]), reg, changed, repo) == []


def test_the_review_must_be_for_the_current_build_and_cite_existing_evidence(repo):
    reg = register(repo)
    assert check.check_review(review(reg, evidence=["docs/missing.md"]), reg, (), repo, build="0.37.0") == [
        "release review: evidence path docs/missing.md does not exist"
    ]
    assert check.check_review(review(reg), reg, (), repo, build="0.38.0") == [
        "release review: release 0.37.0 is not the current build 0.38.0"
    ]


# The preserved baseline and no secrets


def test_baseline_threats_cannot_be_dropped_or_reworded_and_the_baseline_cannot_change(repo):
    reg = register(repo)
    reg["threats"][1]["title"] = "Scope escalation (renamed)"
    assert problems_of(reg, repo) == [
        "threat TH02: title, impact or origin differs from the version 1 baseline"
    ]
    reg = register(repo)
    reg["threats"][1]["impact"] = "Medium"
    assert problems_of(reg, repo) == [
        "threat TH02: title, impact or origin differs from the version 1 baseline"
    ]
    reg = register(repo)
    reg["threats"] = reg["threats"][:1]
    assert "threat TH02: baseline threat missing from the register" in problems_of(reg, repo)
    reg = register(repo)
    reg["threats"][1]["origin"] = "v2"
    assert problems_of(reg, repo) == [
        "threat TH02: title, impact or origin differs from the version 1 baseline"
    ]
    reg = register(repo)
    reg["threats"].append({**threat(BASELINE[1]), "id": "TH40"})
    assert problems_of(reg, repo) == ["threat TH40: origin v1 but not in the version 1 baseline"]
    reg = register(repo)
    (repo / check.BASELINE).write_text(json.dumps(BASELINE, indent=1))
    assert problems_of(reg, repo) == [
        "register: specification/contracts/threat-register.json changed; the version 1 baseline must never be edited"
    ]


def test_credentials_in_the_register_or_review_are_refused(repo):
    reg = register(repo)
    reg["threats"][0]["residual_decision"]["rationale"] = "Use postgresql://impact:hunter2hunter2@db/impact"
    [problem] = problems_of(reg, repo)
    assert problem.startswith("register: contains text that looks like a credential")
    reg = register(repo)
    document = review(reg, notes=["api_key = abcdefghijklmnop1234"])
    [problem] = check.check_review(document, reg, (), repo)
    assert problem.startswith("release review: contains text that looks like a credential")


# The real register and release review


def material_paths_of_build_0_37():
    entry = check.load_json(ROOT, "docs/evidence/release-review-0.37.0.json")["impact_reviews"][0]
    return list(entry["paths"]) + ["docs/RELEASE-0.37-threat-register.md", "scripts/release_review.py"]


def test_the_repository_register_and_release_review_pass_the_check():
    build = check.load_json(ROOT, "VERSION.json")["build"]
    problems, lines = check.run(ROOT, changed=material_paths_of_build_0_37() if build == "0.37.0" else [])
    assert problems == [], problems
    register_data = check.load_json(ROOT, check.REGISTER)
    assert {threat["category"] for threat in register_data["threats"]} == set(check.CATEGORIES)
    ids = [threat["id"] for threat in register_data["threats"]]
    assert ids[:32] == [f"TH{n:02d}" for n in range(1, 33)]
    assert {"TH33", "TH34", "TH35"} <= set(ids)
    chains = {chain["id"]: chain for chain in register_data["chains"]}
    assert chains["CH01"]["path"] == ["TH21", "TH03", "TH15"]
    assert chains["CH02"]["path"] == ["TH25", "TH02", "TH07"]
    by_id = {threat["id"]: threat for threat in register_data["threats"]}
    assert by_id["TH25"]["residual_decision"]["decision"] == "BLOCK"
    # Nothing in the register claims a person confirmed it.
    assert all(threat["residual_decision"]["confirmed_by"] is None for threat in register_data["threats"])


def test_the_open_lists_printed_by_the_script_match_the_recorded_review():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/release_review.py"), "--open"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    opened = json.loads(result.stdout)
    recorded = check.load_json(
        ROOT, "docs/evidence/release-review-" + check.load_json(ROOT, "VERSION.json")["build"] + ".json"
    )
    assert opened == {"open_critical": recorded["open_critical"], "open_other": recorded["open_other"]}


# The attack surfaces the register records as BLOCK stay absent (TH13, TH17, TH18, TH23, TH25; CH02)

BLOCKED_SEGMENTS = {
    "offline-sync": "TH17/TH18 offline packages",
    "devices": "TH17/TH18 device registration",
    "support-requests": "TH25 support access",
    "support-sessions": "TH25 support access",
    "support": "TH25 support access",
    "connectors": "TH13 tenant-configured outbound requests",
    "webhooks": "TH13 tenant-configured outbound requests",
}


def test_blocked_attack_surfaces_are_absent_from_the_implemented_api():
    contracts = ROOT / "packages/contracts"
    domain = json.loads((contracts / "openapi-implemented.json").read_text())
    platform = json.loads((contracts / "openapi-platform.json").read_text())
    explicit = re.findall(
        r"@app\.(?:get|post|put|patch|delete)\(\s*\"([^\"]+)\"",
        (ROOT / "apps/api/impact_api/main.py").read_text(),
    )
    paths = sorted(set(domain["paths"]) | set(platform["paths"]) | set(explicit))
    assert len(paths) > 200 and "/v1/tenants/{tenant_id}/ai-enablement/advisory" in paths
    for path in paths:
        segments = set(path.strip("/").split("/"))
        hit = segments & set(BLOCKED_SEGMENTS)
        assert not hit, f"{path} opens {BLOCKED_SEGMENTS[sorted(hit)[0]]}; revisit the threat register first"
        if "ai-enablement" in segments:
            assert not segments & {"apply", "proposals", "tools", "retrieval"}, (
                f"{path} applies AI output or gives a model tools or retrieval (TH21, TH23)"
            )
    operations = {
        operation.get("operationId")
        for document in (domain, platform)
        for item in document["paths"].values()
        for operation in item.values()
        if isinstance(operation, dict)
    }
    assert not operations & {
        "offline_sync",
        "request_support",
        "action_support_requests_approve",
        "action_support_requests_revoke",
        "list_devices",
        "create_devices",
    }
