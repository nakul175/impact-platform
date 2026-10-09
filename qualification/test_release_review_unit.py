"""scripts/release_review.py (FR-SEC-001): the release security review check, without a database.

Synthetic registers are checked against a small throwaway repository (one pytest file, one browser
check, one baseline with its independent hash record), and against a throwaway git repository for the
change-set rules, so every rule is exercised in isolation; the last tests run the check on the real
register and release review, and guard the attack surfaces the register records as BLOCK.
"""

import ast
import copy
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import release_review as check  # noqa: E402

DATE = "2026-10-09"
OK_TEST = "qualification/test_alpha.py::test_one"
CLASS_TEST = "qualification/test_alpha.py::TestGroup::test_two"
BROWSER = "tools/browser/alpha-check.mjs::Opens the page"
REVIEW_PATH = "docs/release-reviews/release-review-0.37.0.json"
BASELINE = [
    {
        "id": "TH01",
        "title": "Cross tenant object access",
        "impact": "Critical",
        "owner_role": "Security lead",
    },
    {
        "id": "TH02",
        "title": "Scope escalation within a tenant",
        "impact": "High",
        "owner_role": "Access lead",
    },
]
ALPHA = """import pytest


def test_one():
    pass


@pytest.mark.parametrize("n", [1, 2])
def test_param(n):
    pass


@pytest.mark.parametrize("n", [VALUES])
def test_opaque(n):
    pass


class TestGroup:
    def test_two(self):
        pass


def helper():
    pass
"""


def write_baseline(root, baseline=BASELINE, record=True):
    path = root / check.BASELINE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(baseline))
    if record:
        (root / "docs/verification").mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        (root / check.BASELINE_RECORD).write_text(json.dumps({check.BASELINE: digest, "Makefile": "0" * 64}))


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "qualification").mkdir()
    (tmp_path / "qualification/test_alpha.py").write_text(ALPHA)
    (tmp_path / "tools/browser").mkdir(parents=True)
    (tmp_path / "tools/browser/alpha-check.mjs").write_text(
        'await test("Opens the page", async () => {});\nawait test(\n  "Says \\"hello\\" twice",\n'
        '  async () => {},\n);\nconst label = "Not a test";\n'
    )
    (tmp_path / "apps/api").mkdir(parents=True)
    (tmp_path / "apps/api/module.py").write_text("")
    write_baseline(tmp_path)
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
        "owner": base["owner_role"],
        "target_control": "Synthetic target control.",
        "required_verification": "Synthetic verification.",
        "control_refs": ["C-APP", "C-DB"],
        "test_refs": list(tests),
        "coverage": {"C-APP": [tests[0]], "C-DB": [tests[-1]]},
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
        **check.open_lists(reg),
        "impact_reviews": [],
        "evidence": ["apps/api/module.py"],
        "notes": [],
    }
    document.update(changes)
    return document


def problems_of(reg, repo):
    return check.check_register(reg, repo, check.References(repo))


def impact(paths, areas, confirmed_by=None, entry_id="IR-0.37-01"):
    return {
        "id": entry_id,
        "change_id": "US-MP-03",
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
    migration = "infrastructure/migrations/0042_synthetic.sql"
    changed = [migration, "docs/notes.md", REVIEW_PATH]
    document = review(reg, impact_reviews=[impact([migration], ["migration"])])
    assert check.check_review(document, reg, changed, repo) == []
    assert check.open_lists(reg) == {"open_critical": [], "open_other": [], "open_chains": []}


@pytest.mark.parametrize(
    "field",
    ["category", "control_refs", "owner", "test_refs", "coverage", "residual_decision", "verification"],
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
        "threat TH01: owner 'Jane Example' is neither a declared owner role nor 'Nakul Jain (owner)'",
        "threat TH01: owner 'Jane Example' differs from the baseline owner role 'Security lead'",
    ]
    reg = register(repo)
    reg["threats"][0]["control_refs"].append("C-MISSING")
    assert problems_of(reg, repo) == ["threat TH01: unknown control C-MISSING"]


def test_the_owner_role_is_carried_over_from_the_baseline(repo):
    reg = register(repo)
    reg["threats"][0]["owner"] = "Access lead"
    assert problems_of(reg, repo) == [
        "threat TH01: owner 'Access lead' differs from the baseline owner role 'Security lead'"
    ]


def test_acceptance_needs_a_person(repo):
    reg = register(repo)
    reg["threats"][0]["residual_decision"] = decision("ACCEPT")
    assert problems_of(reg, repo) == [
        "threat TH01: ACCEPT is a risk acceptance and needs confirmed_by (a person)"
    ]
    reg["threats"][0]["residual_decision"] = decision("ACCEPT", confirmed_by="Nakul Jain (owner)")
    assert problems_of(reg, repo) == []


def test_every_built_control_needs_a_mapped_test_and_tested_needs_only_built_controls(repo):
    reg = register(repo)
    del reg["threats"][0]["coverage"]["C-DB"]
    assert problems_of(reg, repo) == [
        "threat TH01: implemented control C-DB has no test mapped to it in coverage"
    ]
    reg = register(repo)
    reg["threats"][0]["coverage"]["C-APP-2"] = [OK_TEST]
    reg["threats"][0]["coverage"]["C-APP"] = [CLASS_TEST]
    assert problems_of(reg, repo) == [
        "threat TH01: coverage of C-APP uses qualification/test_alpha.py::TestGroup::test_two, which is not in test_refs",
        "threat TH01: coverage names C-APP-2, which is not in control_refs",
    ]
    # A target-design control: a TESTED threat cannot list it, an open one may (it has no test yet).
    reg = register(repo)
    reg["threats"][0]["control_refs"].append("C-TARGET")
    assert problems_of(reg, repo) == ["threat TH01: TESTED, but its control C-TARGET is not built"]
    reg["threats"][0]["verification"] = {"status": "PARTIAL", "summary": "s", "gaps": ["g"]}
    assert problems_of(reg, repo) == []
    reg["threats"][0]["coverage"]["C-TARGET"] = [OK_TEST]
    assert problems_of(reg, repo) == ["threat TH01: coverage names C-TARGET, which is not built"]
    reg = register(repo)
    reg["threats"][0]["verification"] = {"status": "PENDING", "summary": "s", "gaps": []}
    assert any("gaps: [] should be non-empty" in problem for problem in problems_of(reg, repo))


# Scenario: Reject an unresolvable test reference


def test_test_references_resolve_to_real_tests_and_browser_checks(repo):
    references = check.References(repo)
    for ref in [OK_TEST, CLASS_TEST, BROWSER, "qualification/test_alpha.py::test_param[2]"]:
        assert references.problem(ref) is None, ref
    assert references.problem('tools/browser/alpha-check.mjs::Says "hello" twice') is None
    for ref, reason in [
        ("qualification/test_alpha.py::test_missing", "no test test_missing in qualification/test_alpha.py"),
        ("qualification/test_alpha.py::helper", "no test helper in qualification/test_alpha.py"),
        ("qualification/test_alpha.py::TestGroup::test_one", "no test TestGroup::test_one"),
        ("qualification/test_beta.py::test_one", "no such test file qualification/test_beta.py"),
        ("qualification/test_alpha.py::test_param[3]", "test_param has no parameter id [3] (ids: 1, 2)"),
        ("qualification/test_alpha.py::test_one[1]", "test_one has no parameter id [1] (ids: none)"),
        ("qualification/test_alpha.py::test_opaque[1]", "cannot be derived statically"),
        ("tools/browser/alpha-check.mjs::Not a test", "no browser check named"),
        ("tools/browser/beta-check.mjs::Opens the page", "no such browser check file"),
        ("scripts/run.py::main", "not a pytest node ID"),
    ]:
        assert reason in references.problem(ref), ref


def test_derived_parameter_ids_match_what_pytest_collects(tmp_path):
    source = """import pytest


@pytest.mark.parametrize("status", [302, 401, -1, 2.5, True, None, "plain", {"a": 1}])
def test_single(status):
    pass


@pytest.mark.parametrize("left,right", [("a", 1), ("b", 2)])
def test_pairs(left, right):
    pass


@pytest.mark.parametrize(["x"], [[1], [2]])
def test_list_names(x):
    pass


@pytest.mark.parametrize("value", ["one", "two"], ids=["first", "second"])
def test_explicit(value):
    pass


@pytest.mark.parametrize("value", [pytest.param(1, id="named"), pytest.param(2, id="other")])
def test_param_ids(value):
    pass


@pytest.mark.parametrize("outer", [1, 2])
@pytest.mark.parametrize("inner", ["a", "b"])
def test_stacked(outer, inner):
    pass
"""
    (tmp_path / "test_ids.py").write_text(source)
    collected = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "test_ids.py"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    ).stdout
    expected = {}
    for line in collected.splitlines():
        match = re.match(r"^test_ids\.py::(\w+)\[(.+)\]$", line.strip())
        if match:
            expected.setdefault(match.group(1), set()).add(match.group(2))
    functions = {node.name: node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)}
    assert set(expected) == set(functions)
    for name, node in functions.items():
        assert check.parametrize_ids(node) == expected[name], name


def test_an_unresolvable_test_reference_fails_the_check(repo):
    reg = register(repo)
    reg["threats"][1]["test_refs"] = [CLASS_TEST, BROWSER, "qualification/test_alpha.py::test_renamed"]
    assert problems_of(reg, repo) == [
        "threat TH02: unresolvable test reference qualification/test_alpha.py::test_renamed "
        "(no test test_renamed in qualification/test_alpha.py)"
    ]
    reg = register(repo)
    reg["threats"][0]["test_refs"] = ["tools/browser/alpha-check.mjs::Opens the pages"]
    reg["threats"][0]["coverage"] = {name: list(reg["threats"][0]["test_refs"]) for name in ("C-APP", "C-DB")}
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
    if kind == "BLOCK":
        reg["chains"][0]["residual_decision"] = decision("BLOCK")
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
        f"release review: open_critical hides TH01 'Cross tenant object access' ({reason}); list everything unresolved"
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


def test_a_passed_review_needs_confirmed_decisions_chains_and_impact_reviews(repo):
    reg = register(repo)
    entry = impact(["apps/api/impact_api/ai_policy.py"], ["ai-module"])
    passed = review(reg, passed=True, impact_reviews=[entry])
    problems = check.check_review(passed, reg, (), repo)
    assert problems == [
        "release review: marked passed while the decision on TH01 is unconfirmed",
        "release review: marked passed while the decision on chain CH01 is unconfirmed",
        "release review: marked passed while impact review IR-0.37-01 is unconfirmed",
    ]
    reg["threats"][0]["residual_decision"]["confirmed_by"] = "Nakul Jain (owner)"
    reg["chains"][0]["residual_decision"]["confirmed_by"] = "Nakul Jain (owner)"
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


def test_a_chain_is_no_looser_than_its_threats_and_counts_as_open(repo):
    reg = register(repo)
    reg["threats"][1]["residual_decision"] = decision("BLOCK")
    assert problems_of(reg, repo) == [
        "chain CH01: decision MITIGATE while TH02 on its path is BLOCK; a chain is no looser than its threats"
    ]
    reg["chains"][0]["residual_decision"] = decision("BLOCK")
    assert problems_of(reg, repo) == []
    chain = {"id": "CH01", "title": "Synthetic chain", "decision": "BLOCK", "reason": "BLOCKED"}
    assert check.open_chains(reg) == [chain]
    assert check.check_review(review(reg, open_chains=[]), reg, (), repo) == [
        "release review: open_chains hides CH01 'Synthetic chain' (BLOCKED); list everything unresolved"
    ]
    assert (
        "release review: marked passed while chain CH01 'Synthetic chain' is open (BLOCKED)"
        in check.check_review(review(reg, passed=True), reg, (), repo)
    )
    # A MITIGATE chain with an open threat on its path is open too.
    reg = register(repo)
    reg["threats"][1] = threat(BASELINE[1], status="PARTIAL", tests=(CLASS_TEST, BROWSER))
    assert check.open_chains(reg) == [{**chain, "decision": "MITIGATE", "reason": "MEMBER_THREAT_OPEN"}]
    reg["chains"][0]["residual_decision"] = decision("ACCEPT")
    assert problems_of(reg, repo) == [
        "chain CH01: ACCEPT is a risk acceptance and needs confirmed_by (a person)"
    ]


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


AI = "apps/api/impact_api/ai_ranking.py"
MIGRATION = "infrastructure/migrations/0042_ai_ranking_weights.sql"
POLICY = "packages/contracts/access-policy.json"


def test_a_material_change_without_an_impact_review_fails(repo):
    reg = register(repo)
    changed = [AI, "docs/RELEASE-0.38.md", MIGRATION, POLICY]
    problems = check.check_review(review(reg), reg, changed, repo)
    assert problems == [
        f"impact review missing: the change set touches {AI}, {MIGRATION}, {POLICY} but does not modify "
        f"{REVIEW_PATH}; add an impact_reviews entry for this change",
    ] + [
        f"impact review missing: the change set touches {path} ({area}); add an impact_reviews entry naming it "
        f"to {REVIEW_PATH}"
        for path, area in [(AI, "ai-module"), (MIGRATION, "migration"), (POLICY, "access-policy")]
    ]
    changed.append(REVIEW_PATH)
    # An entry covering two of the three paths leaves the third reported.
    partial = impact([AI, POLICY], ["ai-module", "access-policy"])
    problems = check.check_review(review(reg, impact_reviews=[partial]), reg, changed, repo)
    assert [problem.split(" (")[0] for problem in problems] == [
        f"impact review missing: the change set touches {MIGRATION}"
    ]
    # An entry must list the areas of what it covers and name known threats.
    wrong = impact([MIGRATION], ["ai-module"], entry_id="IR-0.37-02")
    wrong["threats"] = ["TH99"]
    problems = check.check_review(review(reg, impact_reviews=[partial, wrong]), reg, changed, repo)
    assert problems == [
        "impact review IR-0.37-02: unknown threat TH99",
        f"impact review IR-0.37-02: {MIGRATION} is in area(s) migration not listed",
    ]
    wrong["threats"], wrong["areas"] = ["TH01"], ["migration"]
    assert check.check_review(review(reg, impact_reviews=[partial, wrong]), reg, changed, repo) == []


def test_only_an_entry_added_by_this_change_set_covers_it_and_entries_are_append_only(repo):
    reg = register(repo)
    earlier = impact([AI], ["ai-module"])
    base = review(reg, impact_reviews=[earlier])
    changed = [AI, REVIEW_PATH]
    # A later change to an already reviewed file is not covered by the earlier entry.
    problems = check.check_review(base, reg, changed, repo, base_review=base)
    assert problems == [
        f"impact review missing: {AI} (ai-module) is named only by IR-0.37-01, which predate this change set; "
        f"add a new impact_reviews entry for this change to {REVIEW_PATH}"
    ]
    # The review file must be part of the change set.
    later = impact([AI], ["ai-module"], entry_id="IR-0.37-02")
    current = review(reg, impact_reviews=[earlier, later])
    assert check.check_review(current, reg, [AI], repo, base_review=base) == [
        f"impact review missing: the change set touches {AI} but does not modify {REVIEW_PATH}; "
        "add an impact_reviews entry for this change"
    ]
    assert check.check_review(current, reg, changed, repo, base_review=base) == []
    # Earlier entries cannot be rewritten or dropped to make room.
    rewritten = review(reg, impact_reviews=[{**earlier, "summary": "Changed."}, later])
    assert check.check_review(rewritten, reg, changed, repo, base_review=base) == [
        "impact review IR-0.37-01 was changed since the base; add a new entry instead"
    ]
    assert check.check_review(review(reg, impact_reviews=[later]), reg, changed, repo, base_review=base) == [
        "impact review IR-0.37-01 was removed since the base; impact reviews are append-only"
    ]


def test_the_review_must_be_for_the_current_build_and_cite_existing_evidence(repo):
    reg = register(repo)
    assert check.check_review(review(reg, evidence=["docs/missing.md"]), reg, (), repo, build="0.37.0") == [
        "release review: evidence path docs/missing.md does not exist"
    ]
    assert check.check_review(review(reg), reg, (), repo, build="0.38.0") == [
        "release review: release 0.37.0 is not the current build 0.38.0"
    ]


# The preserved baseline, the previous register and no secrets


def test_baseline_threats_cannot_be_dropped_or_reworded(repo):
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


def test_the_baseline_must_match_its_independent_hash_record(repo):
    # Editing version 1 and declaring its new hash in the register is still caught by the record.
    weakened = [dict(BASELINE[0]), {**BASELINE[1], "impact": "Medium"}]
    (repo / check.BASELINE).write_text(json.dumps(weakened))
    reg = register(repo)
    reg["threats"][1]["impact"] = "Medium"
    assert problems_of(reg, repo) == [
        f"register: {check.BASELINE} does not match its independent hash record in {check.BASELINE_RECORD}; "
        "the version 1 baseline must never be edited",
        f"register: baseline.sha256 differs from the hash recorded in {check.BASELINE_RECORD}",
    ]
    write_baseline(repo, record=False)
    (repo / check.BASELINE_RECORD).write_text(json.dumps({"Makefile": "0" * 64}))
    assert problems_of(register(repo), repo) == [
        f"register: {check.BASELINE_RECORD} has no hash for {check.BASELINE}"
    ]


def test_the_register_cannot_lose_threats_or_get_looser_than_at_the_base_without_a_person(repo):
    old = register(repo)
    old["threats"][0] = threat(BASELINE[0], status="PARTIAL")
    old["threats"].append({**threat(BASELINE[1]), "id": "TH33", "origin": "v2", "title": "New threat"})
    assert check.compare_registers(old, copy.deepcopy(old), "main") == []
    new = copy.deepcopy(old)
    new["threats"] = new["threats"][:2]
    new["chains"] = []
    assert check.compare_registers(old, new, "main") == [
        "threat TH33 'New threat' was removed since main; threats are never removed",
        "chain CH01 'Synthetic chain' was removed since main",
    ]
    new = copy.deepcopy(old)
    new["threats"][2]["impact"] = "Medium"
    assert check.compare_registers(old, new, "main") == [
        "threat TH33: impact lowered from High to Medium since main"
    ]
    new = copy.deepcopy(old)
    new["threats"][0]["verification"]["status"] = "TESTED"
    new["threats"][1]["residual_decision"]["decision"] = "ACCEPT"
    new["chains"][0]["residual_decision"]["decision"] = "ACCEPT"
    assert check.compare_registers(old, new, "main") == [
        "threat TH01: verification PARTIAL -> TESTED since main without confirmed_by (a person)",
        "threat TH02: decision MITIGATE -> ACCEPT since main without confirmed_by (a person)",
        "chain CH01: decision MITIGATE -> ACCEPT since main without confirmed_by (a person)",
    ]
    for item in (new["threats"][0], new["threats"][1], new["chains"][0]):
        item["residual_decision"]["confirmed_by"] = "Nakul Jain (owner)"
    assert check.compare_registers(old, new, "main") == []
    # Tightening needs no confirmation.
    new = copy.deepcopy(old)
    new["threats"][1]["residual_decision"]["decision"] = "BLOCK"
    new["threats"][2]["impact"] = "Critical"
    assert check.compare_registers(old, new, "main") == []


def test_credentials_in_the_register_or_review_are_refused(repo):
    reg = register(repo)
    reg["threats"][0]["residual_decision"]["rationale"] = "Use postgresql://impact:hunter2hunter2@db/impact"
    [problem] = problems_of(reg, repo)
    assert problem.startswith("register: contains text that looks like a credential")
    reg = register(repo)
    document = review(reg, notes=["api_key = abcdefghijklmnop1234"])
    [problem] = check.check_review(document, reg, (), repo)
    assert problem.startswith("release review: contains text that looks like a credential")
    # Escapes in the file as written cannot hide a credential: the decoded strings are scanned too,
    # and the raw text catches what a re-serialisation would escape.
    escaped = '{"note": "pass\\u0077ord=abcdefghijklmnop"}'
    assert check.secret_problems(json.loads(escaped), "x", raw=escaped)
    quoted = '{"password": "abcdefghijklmnop"}'
    assert check.secret_problems(json.loads(quoted), "x", raw=quoted)
    assert check.secret_problems({"note": "A password is never stored."}, "x") == []


# The change set from git


def git(root, *args):
    return subprocess.run(
        [
            "git",
            "-c",
            "user.name=Synthetic",
            "-c",
            "user.email=synthetic@example.test",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def commit(root, message):
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)


def test_the_change_set_and_base_files_come_from_git(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/old.md").write_text("old\n")
    (tmp_path / "docs/keep.md").write_text("keep\n")
    commit(tmp_path, "base")
    git(tmp_path, "checkout", "-q", "-b", "feature")
    git(tmp_path, "mv", "docs/old.md", "docs/new.md")
    (tmp_path / "infrastructure/migrations").mkdir(parents=True)
    (tmp_path / "infrastructure/migrations/0042_x.sql").write_text("SELECT 1;\n")
    commit(tmp_path, "change")
    (tmp_path / "docs/keep.md").write_text("uncommitted\n")
    # Default base: origin/main is absent here, so main is used; a rename lists both paths; uncommitted
    # edits are not part of the change set.
    ref, point = check.merge_point(tmp_path)
    assert ref == "main" and point == git(tmp_path, "rev-parse", "main").strip()
    assert check.changed_paths(tmp_path, point) == [
        "docs/new.md",
        "docs/old.md",
        "infrastructure/migrations/0042_x.sql",
    ]
    assert check.merge_point(tmp_path, "HEAD^1") == ("HEAD^1", point)
    assert check.file_at(tmp_path, point, "docs/old.md") == "old\n"
    assert check.file_at(tmp_path, point, "docs/new.md") is None
    with pytest.raises(RuntimeError, match="cannot find a base for the change set \\(tried nope\\)"):
        check.merge_point(tmp_path, "nope")


def synthetic_repository(repo):
    """A git repository with a sound register, release review 0.37.0 and one reviewed AI module on main."""
    git(repo, "init", "-q", "-b", "main")
    reg = register(repo)
    (repo / "docs/current").mkdir(parents=True, exist_ok=True)
    (repo / "docs/release-reviews").mkdir(parents=True, exist_ok=True)
    (repo / "apps/api/impact_api").mkdir(parents=True, exist_ok=True)
    (repo / "apps/api/impact_api/ai_policy.py").write_text("RULES = 1\n")
    (repo / "VERSION.json").write_text(json.dumps({"build": "0.37.0"}))
    write(repo, check.REGISTER, reg)
    path = "apps/api/impact_api/ai_policy.py"
    write(repo, REVIEW_PATH, review(reg, impact_reviews=[impact([path], ["ai-module"])]))
    commit(repo, "main")
    git(repo, "checkout", "-q", "-b", "feature")
    return reg


def write(repo, relative, document):
    (repo / relative).write_text(json.dumps(document, indent=2) + "\n")


def test_a_later_edit_to_a_reviewed_ai_module_needs_a_new_impact_review(repo):
    synthetic_repository(repo)
    problems, _ = check.run(repo, base="main")
    assert problems == []  # nothing changed yet
    (repo / "apps/api/impact_api/ai_policy.py").write_text("RULES = 2\n")
    commit(repo, "edit the AI policy module")
    problems, lines = check.run(repo, base="main")
    assert "  material: apps/api/impact_api/ai_policy.py (ai-module)" in lines
    assert problems == [
        "impact review missing: the change set touches apps/api/impact_api/ai_policy.py but does not modify "
        f"{REVIEW_PATH}; add an impact_reviews entry for this change",
        "impact review missing: apps/api/impact_api/ai_policy.py (ai-module) is named only by IR-0.37-01, "
        f"which predate this change set; add a new impact_reviews entry for this change to {REVIEW_PATH}",
    ]
    document = json.loads((repo / REVIEW_PATH).read_text())
    document["impact_reviews"].append(
        impact(["apps/api/impact_api/ai_policy.py"], ["ai-module"], entry_id="IR-0.37-02")
    )
    write(repo, REVIEW_PATH, document)
    commit(repo, "review the edit")
    assert check.run(repo, base="main")[0] == []
    assert check.run(repo, base="HEAD^1")[0] == []  # the second commit alone touches no material path


def test_the_register_is_compared_with_its_version_at_the_base(repo):
    reg = synthetic_repository(repo)
    loosened = copy.deepcopy(reg)
    loosened["threats"][1]["residual_decision"]["decision"] = "ACCEPT"
    loosened["threats"][1]["residual_decision"]["confirmed_by"] = None
    write(repo, check.REGISTER, loosened)
    commit(repo, "loosen TH02")
    problems, _ = check.run(repo, base="main")
    assert "threat TH02: ACCEPT is a risk acceptance and needs confirmed_by (a person)" in problems
    assert any(
        problem.startswith("threat TH02: decision MITIGATE -> ACCEPT since main (") for problem in problems
    ), problems
    git(repo, "reset", "-q", "--hard", "main")
    lowered = copy.deepcopy(reg)
    lowered["threats"].append({**threat(BASELINE[1]), "id": "TH33", "origin": "v2", "title": "New threat"})
    write(repo, check.REGISTER, lowered)
    git(repo, "checkout", "-q", "main")
    commit(repo, "add TH33 on main")
    git(repo, "checkout", "-q", "-b", "drop")
    write(repo, check.REGISTER, reg)
    commit(repo, "drop TH33")
    problems, _ = check.run(repo, base="main")
    assert [problem.split(" since ")[0] for problem in problems] == ["threat TH33 'New threat' was removed"]


def test_init_starts_a_review_that_the_check_accepts(repo):
    synthetic_repository(repo)
    (repo / REVIEW_PATH).unlink()
    commit(repo, "no review")
    problems, _ = check.run(repo, base="HEAD")
    assert problems == [check.missing_review_message("0.37.0")]
    assert "--init" in problems[0] and REVIEW_PATH in problems[0]
    path = check.init_review(repo, "Synthetic Person", today=date(2026, 10, 9))
    assert path == repo / REVIEW_PATH
    created = json.loads(path.read_text())
    assert created["prepared_by"] == "Synthetic Person" and created["impact_reviews"] == []
    assert created["passed"] is False and created["open_chains"] == []
    with pytest.raises(FileExistsError):
        check.init_review(repo, "Synthetic Person")
    commit(repo, "review again")
    assert check.run(repo, base="HEAD^1")[0] == []


# The real register and release review


def material_paths_of_build_0_37():
    entry = check.load_json(ROOT, REVIEW_PATH)["impact_reviews"][0]
    return list(entry["paths"]) + [
        REVIEW_PATH,
        "docs/RELEASE-0.37-threat-register.md",
        "scripts/release_review.py",
    ]


def current_review():
    build = check.load_json(ROOT, "VERSION.json")["build"]
    path = ROOT / check.REVIEW.format(build=build)
    if not path.is_file():
        pytest.fail(check.missing_review_message(build))
    return build, json.loads(path.read_text())


def test_the_repository_register_and_release_review_pass_the_check():
    build, _ = current_review()
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
    assert chains["CH02"]["residual_decision"]["decision"] == "BLOCK"
    # Nothing in the register claims a person confirmed it.
    assert all(threat["residual_decision"]["confirmed_by"] is None for threat in register_data["threats"])


def test_the_open_lists_printed_by_the_script_match_the_recorded_review():
    _, recorded = current_review()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/release_review.py"), "--open"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    assert json.loads(result.stdout) == {
        name: recorded[name] for name in ("open_critical", "open_other", "open_chains")
    }


# The attack surfaces the register records as BLOCK stay absent (TH13, TH17, TH18, TH21, TH23, TH25; CH02)

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
