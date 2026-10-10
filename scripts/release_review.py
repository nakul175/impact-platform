"""Release security review check (FR-SEC-001): threat register v2, chains, open threats, impact reviews.

    .venv/bin/python scripts/release_review.py --check                 base: merge-base with origin/main (or main)
    .venv/bin/python scripts/release_review.py --check --base HEAD^1   what CI runs (first parent of the merge)
    .venv/bin/python scripts/release_review.py --init --prepared-by "<name>"   start the current build's review
    .venv/bin/python scripts/release_review.py --open                  print the open lists as review JSON

Deterministic and offline for --check: it reads repository files and the local git history only, never
the network, the clock or a database, and finishes in about a second. It fails (exit 1) when:

- the register (docs/current/threat-register.json) does not match its JSON schema; the preserved version 1
  baseline (specification/contracts/threat-register.json, never edited) no longer matches its independent
  hash record (docs/verification/application-v0.12-original-sha256.json) or a baseline threat is not
  carried over with its title, impact and owner role; a control, owner role or category is unknown;
- a test reference does not resolve: a pytest node ID must name a test function (or Class::method) in
  qualification/, with a [suffix] only when the id is derivable from literal parametrize decorators; a
  browser check must name a test("...") declared in that tools/browser/*.mjs file;
- an implemented control listed for a threat has no test mapped to it in "coverage", or a TESTED threat
  lists a control that is not built;
- a chain lacks two independent implemented controls with resolvable evidence (independent: different
  layers and no shared control in their depends_on closures), or is less strict than its threats (a chain
  with a BLOCK threat must be BLOCK);
- compared with the register at the base of the change set, a threat or chain was removed, an impact was
  lowered, or a decision or verification status was loosened without confirmed_by;
- the release review of the current build (docs/release-reviews/release-review-<build>.json) is missing,
  does not list exactly the unresolved threats and chains, or is marked passed (or gate G11 Pass) while a
  critical threat or a chain is unresolved or a decision or impact review is unconfirmed;
- the change set touches a migration, a *_contracts.py module, packages/contracts/access-policy.json or
  apps/api/impact_api/ai_*.py without modifying the release review with a new impact_reviews entry naming
  that path (entries already at the base do not count and must not change);
- the register or the review contains something that looks like a credential.

A threat is resolved only when its decision is ACCEPT or MITIGATE and its verification is TESTED (every
listed control is built and has a mapped test that exists); BLOCK, PARTIAL and PENDING stay open. A chain
is resolved only when its decision is ACCEPT or MITIGATE and every threat on its path is resolved.
"""

import argparse
import ast
import datetime
import fnmatch
import hashlib
import itertools
import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REGISTER = "docs/current/threat-register.json"
REGISTER_SCHEMA = "docs/current/threat-register.schema.json"
REVIEW_SCHEMA = "docs/current/release-review.schema.json"
BASELINE = "specification/contracts/threat-register.json"
# The independent hash record of the preserved package, written when the package was received.
BASELINE_RECORD = "docs/verification/application-v0.12-original-sha256.json"
REVIEW = "docs/release-reviews/release-review-{build}.json"
REVIEW_FILE = re.compile(r"^docs/release-reviews/release-review-(\d+\.\d+\.\d+)\.json$")
CATEGORIES = (
    "identity",
    "tenant boundary",
    "source data",
    "files",
    "offline devices",
    "publication",
    "AI",
    "support",
)
REPOSITORY_OWNER = "Nakul Jain (owner)"
RESOLVED_DECISIONS = {"ACCEPT", "MITIGATE"}
IMPACT_RANK = {"Medium": 1, "High": 2, "Critical": 3}
# Larger is looser: further from "open".
DECISION_RANK = {"BLOCK": 0, "MITIGATE": 1, "ACCEPT": 2}
VERIFICATION_RANK = {"PENDING": 0, "PARTIAL": 1, "TESTED": 2}
# Path-to-area map: a change set touching any of these needs a new impact-review entry naming the path.
# fnmatch semantics: "*" also matches "/".
MATERIAL_AREAS = (
    ("migration", "infrastructure/migrations/*"),
    ("contracts", "apps/*_contracts.py"),
    ("contracts", "scripts/*_contracts.py"),
    ("access-policy", "packages/contracts/access-policy.json"),
    ("ai-module", "apps/api/impact_api/ai_*.py"),
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"postgres(?:ql)?://[^\s:/@]+:[^\s@]+@"),
    re.compile(
        r"(?i)\b(?:password|passwd|secret|api[_-]?key)\b[\"']?\s*[=:]\s*\\?[\"']?[A-Za-z0-9+/_\-]{12,}"
    ),
)
PYTEST_REF = re.compile(
    r"^(qualification/test_[a-z0-9_]+\.py)::([A-Za-z_][A-Za-z0-9_]*)(?:::([A-Za-z_][A-Za-z0-9_]*))?"
    r"(?:\[([^\]]+)\])?$"
)
BROWSER_REF = re.compile(r"^(tools/browser/[a-z0-9-]+\.mjs)::(\S.*)$")
BROWSER_TEST = re.compile(r"\btest\(\s*\"((?:[^\"\\]|\\.)*)\"")


def load_json(root, relative):
    return json.loads((Path(root) / relative).read_text(encoding="utf-8"))


def schema_errors(document, schema, label):
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda error: list(map(str, error.absolute_path)))
    return [
        f"{label}: {'/'.join(map(str, error.absolute_path)) or '(root)'}: {error.message}" for error in errors
    ]


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def secret_problems(document, label, raw=None):
    """Credential-like text in the file as written (raw) or in any decoded string of the document."""
    texts = [raw if raw is not None else json.dumps(document, indent=2, ensure_ascii=False)]
    texts += list(_strings(document))
    return [
        f"{label}: contains text that looks like a credential ({pattern.pattern})"
        for pattern in SECRET_PATTERNS
        if any(pattern.search(text) for text in texts)
    ]


def missing_review_message(build):
    return (
        f"release review missing: {REVIEW.format(build=build)}. Every build in VERSION.json needs one. Create it "
        f'with `.venv/bin/python scripts/release_review.py --init --prepared-by "<name>"`, then add an '
        "impact_reviews entry for each material change (see docs/RELEASE-0.37-threat-register.md)."
    )


# Test references


def _literal_id(node, argname, index):
    """pytest's id for one literal parameter value; None when it cannot be derived statically."""
    if (
        isinstance(node, ast.UnaryOp)
        and isinstance(node.op, ast.USub)
        and isinstance(node.operand, ast.Constant)
    ):
        node = ast.Constant(-node.operand.value) if isinstance(node.operand.value, (int, float)) else node
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, str):
            return value if value and value.isascii() else None
        if value is None or isinstance(value, (bool, int, float)):
            return str(value)
        return None
    if isinstance(node, (ast.Dict, ast.List, ast.Set)):
        return f"{argname}{index}"
    return None


def _parametrize_ids(call):
    """The ids one literal @pytest.mark.parametrize decorator generates, or None."""
    if not call.args or len(call.args) < 2:
        return None
    names_node, values_node = call.args[0], call.args[1]
    # pytest unpacks each value into the names unless the names are one comma-free string.
    if isinstance(names_node, ast.Constant) and isinstance(names_node.value, str):
        names = [name.strip() for name in names_node.value.split(",") if name.strip()]
        unpack = len(names) > 1
    elif isinstance(names_node, (ast.List, ast.Tuple)) and all(
        isinstance(item, ast.Constant) and isinstance(item.value, str) for item in names_node.elts
    ):
        names = [item.value for item in names_node.elts]
        unpack = True
    else:
        return None
    if not isinstance(values_node, (ast.List, ast.Tuple)):
        return None
    explicit = next((keyword.value for keyword in call.keywords if keyword.arg == "ids"), None)
    if explicit is not None:
        if not isinstance(explicit, (ast.List, ast.Tuple)) or not all(
            isinstance(item, ast.Constant) and isinstance(item.value, str) for item in explicit.elts
        ):
            return None
        return [item.value for item in explicit.elts]
    ids = []
    for index, value in enumerate(values_node.elts):
        if isinstance(value, ast.Call):  # pytest.param(...): only an explicit literal id is derivable
            given = next((keyword.value for keyword in value.keywords if keyword.arg == "id"), None)
            if isinstance(given, ast.Constant) and isinstance(given.value, str):
                ids.append(given.value)
                continue
            return None
        if not unpack:
            parts = [_literal_id(value, names[0], index)]
        elif isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == len(names):
            parts = [_literal_id(item, name, index) for item, name in zip(value.elts, names)]
        else:
            return None
        if any(part is None for part in parts):
            return None
        ids.append("-".join(parts))
    if len(set(ids)) != len(ids):
        return None  # pytest disambiguates duplicates with suffixes; do not guess
    return ids


def parametrize_ids(function):
    """The set of pytest ids of a test function's literal parametrize decorators (empty when it has none);
    None when any decorator is not statically derivable."""
    calls = [
        decorator
        for decorator in function.decorator_list
        if isinstance(decorator, ast.Call)
        and isinstance(decorator.func, ast.Attribute)
        and decorator.func.attr == "parametrize"
    ]
    if not calls:
        return set()
    per_decorator = []
    for call in reversed(calls):  # pytest joins the decorator nearest the function first
        ids = _parametrize_ids(call)
        if ids is None:
            return None
        per_decorator.append(ids)
    return {"-".join(combination) for combination in itertools.product(*per_decorator)}


class References:
    """Resolves test references against the files in one repository root, parsing each file once."""

    def __init__(self, root):
        self.root = Path(root)
        self.pytest, self.browser = {}, {}

    def _pytest_functions(self, relative):
        if relative not in self.pytest:
            functions = {}
            path = self.root / relative
            if path.is_file():
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
                kinds = (ast.FunctionDef, ast.AsyncFunctionDef)
                for node in tree.body:
                    if isinstance(node, kinds) and node.name.startswith("test"):
                        functions[node.name] = node
                    elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                        for item in node.body:
                            if isinstance(item, kinds) and item.name.startswith("test"):
                                functions[node.name + "::" + item.name] = item
            self.pytest[relative] = functions
        return self.pytest[relative]

    def _browser_names(self, relative):
        if relative not in self.browser:
            path = self.root / relative
            names = set()
            if path.is_file():
                for raw in BROWSER_TEST.findall(path.read_text(encoding="utf-8")):
                    names.add(json.loads('"' + raw + '"'))
            self.browser[relative] = names
        return self.browser[relative]

    def problem(self, ref):
        """None when the reference resolves, otherwise why it does not."""
        match = PYTEST_REF.match(ref)
        if match:
            relative, first, second, suffix = match.groups()
            if not (self.root / relative).is_file():
                return "no such test file " + relative
            name = first + "::" + second if second else first
            function = self._pytest_functions(relative).get(name)
            if function is None:
                return "no test " + name + " in " + relative
            if suffix is not None:
                ids = parametrize_ids(function)
                if ids is None:
                    return (
                        f"the parameter ids of {name} cannot be derived statically; "
                        "reference the test without a [suffix]"
                    )
                if suffix not in ids:
                    return f"{name} has no parameter id [{suffix}] (ids: {', '.join(sorted(ids)) or 'none'})"
            return None
        match = BROWSER_REF.match(ref)
        if match:
            relative, name = match.groups()
            if not (self.root / relative).is_file():
                return "no such browser check file " + relative
            if name not in self._browser_names(relative):
                return "no browser check named " + json.dumps(name) + " in " + relative
            return None
        return "not a pytest node ID under qualification/ or a tools/browser/*.mjs check name"


# Open threats and chains


def _threat_reason(threat):
    decision = threat["residual_decision"]["decision"]
    status = threat["verification"]["status"]
    if decision not in RESOLVED_DECISIONS:
        return "BLOCKED"
    if status == "PENDING":
        return "VERIFICATION_PENDING"
    if status == "PARTIAL":
        return "VERIFICATION_PARTIAL"
    return None


def open_threats(register):
    """Threats that are not resolved (ACCEPT or MITIGATE with TESTED verification), in register order."""
    result = []
    for threat in register.get("threats", []):
        reason = _threat_reason(threat)
        if reason:
            result.append(
                {
                    "id": threat["id"],
                    "title": threat["title"],
                    "impact": threat["impact"],
                    "decision": threat["residual_decision"]["decision"],
                    "verification": threat["verification"]["status"],
                    "reason": reason,
                }
            )
    return result


def split_open(register):
    items = open_threats(register)
    return (
        [item for item in items if item["impact"] == "Critical"],
        [item for item in items if item["impact"] != "Critical"],
    )


def open_chains(register):
    """Chains that are BLOCK or have an unresolved threat on their path, in register order."""
    unresolved = {item["id"] for item in open_threats(register)}
    result = []
    for chain in register.get("chains", []):
        decision = chain["residual_decision"]["decision"]
        if decision not in RESOLVED_DECISIONS:
            reason = "BLOCKED"
        elif set(chain["path"]) & unresolved:
            reason = "MEMBER_THREAT_OPEN"
        else:
            continue
        result.append({"id": chain["id"], "title": chain["title"], "decision": decision, "reason": reason})
    return result


def open_lists(register):
    critical, other = split_open(register)
    return {"open_critical": critical, "open_other": other, "open_chains": open_chains(register)}


def _closure(control_id, controls):
    seen, stack = set(), list(controls.get(control_id, {}).get("depends_on", []))
    while stack:
        current = stack.pop()
        if current not in seen:
            seen.add(current)
            stack.extend(controls.get(current, {}).get("depends_on", []))
    return seen


def independent(first, second, controls):
    """Different layers and no shared control in their dependency closures (one failure defeats neither)."""
    if first == second or controls[first]["layer"] == controls[second]["layer"]:
        return False
    return not (({first} | _closure(first, controls)) & ({second} | _closure(second, controls)))


# The register


def _baseline_problems(register, root, baseline):
    problems = []
    if baseline is not None:
        return problems, baseline
    path = root / BASELINE
    if not path.is_file():
        return [f"register: baseline {BASELINE} is missing"], []
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    record_path = root / BASELINE_RECORD
    recorded = None
    if record_path.is_file():
        recorded = json.loads(record_path.read_text(encoding="utf-8")).get(BASELINE)
    if recorded is None:
        problems.append(f"register: {BASELINE_RECORD} has no hash for {BASELINE}")
    elif actual != recorded:
        problems.append(
            f"register: {BASELINE} does not match its independent hash record in {BASELINE_RECORD}; "
            "the version 1 baseline must never be edited"
        )
    if register["baseline"]["sha256"] != (recorded or actual):
        problems.append(f"register: baseline.sha256 differs from the hash recorded in {BASELINE_RECORD}")
    return problems, json.loads(path.read_text(encoding="utf-8"))


def check_register(register, root=ROOT, references=None, schema=None, baseline=None, raw=None):
    """Every problem with the register as a list of messages (empty when it is sound)."""
    root = Path(root)
    references = references or References(root)
    schema = schema if schema is not None else load_json(ROOT, REGISTER_SCHEMA)
    problems = schema_errors(register, schema, "register")
    if problems:
        return problems
    problems += secret_problems(register, "register", raw)
    if [category["id"] for category in register["categories"]] != list(CATEGORIES):
        problems.append("register: categories must be exactly, in order: " + ", ".join(CATEGORIES))

    controls = {}
    for control in register["controls"]:
        if control["id"] in controls:
            problems.append(f"control {control['id']}: duplicate id")
        controls[control["id"]] = control
    for control in register["controls"]:
        for path in control["implemented_in"]:
            if not (root / path).exists():
                problems.append(f"control {control['id']}: implemented_in path {path} does not exist")
        for dependency in control["depends_on"]:
            if dependency not in controls:
                problems.append(f"control {control['id']}: depends on unknown control {dependency}")
        if control["id"] in _closure(control["id"], controls):
            problems.append(f"control {control['id']}: depends on itself")

    owners = set(register["owner_roles"]) | {REPOSITORY_OWNER}
    threats = {}
    for threat in register["threats"]:
        tid = threat["id"]
        if tid in threats:
            problems.append(f"threat {tid}: duplicate id")
        threats[tid] = threat
        if threat["owner"] not in owners:
            problems.append(
                f"threat {tid}: owner {threat['owner']!r} is neither a declared owner role nor {REPOSITORY_OWNER!r}"
            )
        for ref in threat["control_refs"]:
            if ref not in controls:
                problems.append(f"threat {tid}: unknown control {ref}")
        for ref in threat["test_refs"]:
            reason = references.problem(ref)
            if reason:
                problems.append(f"threat {tid}: unresolvable test reference {ref} ({reason})")
        coverage = threat["coverage"]
        for ref, tests in coverage.items():
            if ref not in threat["control_refs"]:
                problems.append(f"threat {tid}: coverage names {ref}, which is not in control_refs")
            elif not controls.get(ref, {}).get("implemented"):
                problems.append(f"threat {tid}: coverage names {ref}, which is not built")
            for test in tests:
                if test not in threat["test_refs"]:
                    problems.append(f"threat {tid}: coverage of {ref} uses {test}, which is not in test_refs")
        for ref in threat["control_refs"]:
            control = controls.get(ref)
            if control and control["implemented"] and ref not in coverage:
                problems.append(
                    f"threat {tid}: implemented control {ref} has no test mapped to it in coverage"
                )
            if control and not control["implemented"] and threat["verification"]["status"] == "TESTED":
                problems.append(f"threat {tid}: TESTED, but its control {ref} is not built")
        decision = threat["residual_decision"]
        if decision["decision"] == "ACCEPT" and not decision["confirmed_by"]:
            problems.append(f"threat {tid}: ACCEPT is a risk acceptance and needs confirmed_by (a person)")

    # The preserved version 1 baseline: unchanged, and every threat carried with title, impact and owner.
    found, baseline = _baseline_problems(register, root, baseline)
    problems += found
    for old in baseline:
        new = threats.get(old["id"])
        if not new:
            problems.append(f"threat {old['id']}: baseline threat missing from the register")
            continue
        if (new["title"], new["impact"], new["origin"]) != (old["title"], old["impact"], "v1"):
            problems.append(
                f"threat {old['id']}: title, impact or origin differs from the version 1 baseline"
            )
        if "owner_role" in old and new["owner"] != old["owner_role"]:
            problems.append(
                f"threat {old['id']}: owner {new['owner']!r} differs from the baseline owner role {old['owner_role']!r}"
            )
    baseline_ids = {old["id"] for old in baseline}
    for tid, threat in threats.items():
        if threat["origin"] == "v1" and tid not in baseline_ids:
            problems.append(f"threat {tid}: origin v1 but not in the version 1 baseline")

    seen_chains = set()
    for chain in register["chains"]:
        cid = chain["id"]
        if cid in seen_chains:
            problems.append(f"chain {cid}: duplicate id")
        seen_chains.add(cid)
        for tid in chain["path"]:
            if tid not in threats:
                problems.append(f"chain {cid}: unknown threat {tid} in path")
        blocked = [
            tid
            for tid in chain["path"]
            if threats.get(tid, {}).get("residual_decision", {}).get("decision") == "BLOCK"
        ]
        decision = chain["residual_decision"]
        if blocked and decision["decision"] != "BLOCK":
            problems.append(
                f"chain {cid}: decision {decision['decision']} while {', '.join(blocked)} on its path is BLOCK; "
                "a chain is no looser than its threats"
            )
        if decision["decision"] == "ACCEPT" and not decision["confirmed_by"]:
            problems.append(f"chain {cid}: ACCEPT is a risk acceptance and needs confirmed_by (a person)")
        evidenced = []
        for entry in chain["controls"]:
            ref = entry["control_ref"]
            if ref not in controls:
                problems.append(f"chain {cid}: unknown control {ref}")
                continue
            if entry["breaks"] not in chain["path"]:
                problems.append(
                    f"chain {cid}: control {ref} breaks {entry['breaks']}, which is not in the path"
                )
            if not controls[ref]["implemented"]:
                problems.append(f"chain {cid}: control {ref} is not implemented and cannot count as evidence")
                continue
            unresolved = [(item, references.problem(item)) for item in entry["evidence"]]
            unresolved = [(item, reason) for item, reason in unresolved if reason]
            for item, reason in unresolved:
                problems.append(f"chain {cid}: unresolvable evidence {item} for {ref} ({reason})")
            if not unresolved:
                evidenced.append(ref)
        evidenced = sorted(set(evidenced))
        if len(evidenced) < 2:
            problems.append(
                f"chain {cid}: needs at least two implemented controls with evidence, has {len(evidenced)}"
            )
        elif not any(
            independent(first, second, controls)
            for index, first in enumerate(evidenced)
            for second in evidenced[index + 1 :]
        ):
            problems.append(
                f"chain {cid}: no two of its evidenced controls are independent (they share a layer or a dependency)"
            )
    return problems


def _loosened(old, new):
    """Text describing how the residual state got looser from old to new, or None."""
    changes = []
    old_decision, new_decision = old["residual_decision"]["decision"], new["residual_decision"]["decision"]
    if DECISION_RANK[new_decision] > DECISION_RANK[old_decision]:
        changes.append(f"decision {old_decision} -> {new_decision}")
    if "verification" in old and "verification" in new:
        old_status, new_status = old["verification"]["status"], new["verification"]["status"]
        if VERIFICATION_RANK[new_status] > VERIFICATION_RANK[old_status]:
            changes.append(f"verification {old_status} -> {new_status}")
    return ", ".join(changes) or None


def compare_registers(old, new, label):
    """Problems with the register compared with its earlier version at the base of the change set."""
    problems = []
    new_threats = {threat["id"]: threat for threat in new.get("threats", [])}
    for threat in old.get("threats", []):
        tid = threat["id"]
        current = new_threats.get(tid)
        if current is None:
            problems.append(
                f"threat {tid} {threat['title']!r} was removed since {label}; threats are never removed"
            )
            continue
        if IMPACT_RANK.get(current["impact"], 0) < IMPACT_RANK.get(threat["impact"], 0):
            problems.append(
                f"threat {tid}: impact lowered from {threat['impact']} to {current['impact']} since {label}"
            )
        change = _loosened(threat, current)
        if change and not current["residual_decision"]["confirmed_by"]:
            problems.append(f"threat {tid}: {change} since {label} without confirmed_by (a person)")
    new_chains = {chain["id"]: chain for chain in new.get("chains", [])}
    for chain in old.get("chains", []):
        current = new_chains.get(chain["id"])
        if current is None:
            problems.append(f"chain {chain['id']} {chain['title']!r} was removed since {label}")
            continue
        change = _loosened(chain, current)
        if change and not current["residual_decision"]["confirmed_by"]:
            problems.append(f"chain {chain['id']}: {change} since {label} without confirmed_by (a person)")
    return problems


# The release review


def material(paths):
    """{path: [areas]} for the paths of a change set that need an impact review."""
    result = {}
    for path in paths:
        areas = sorted({area for area, pattern in MATERIAL_AREAS if fnmatch.fnmatchcase(path, pattern)})
        if areas:
            result[path] = areas
    return result


def build_key(build):
    """A build such as 0.39.0 as a comparable tuple."""
    return tuple(int(part) for part in build.split("."))


def reviews_in(paths):
    """{path: build} for the release review files among a change set's paths."""
    return {path: match.group(1) for path in paths if (match := REVIEW_FILE.match(path))}


def _entry_problems(review, threat_ids, label="release review"):
    """Problems with the impact_reviews entries of one review on their own: duplicates, threats, areas."""
    problems = []
    ids = [entry["id"] for entry in review["impact_reviews"]]
    if len(set(ids)) != len(ids):
        problems.append(f"{label}: impact_reviews has a duplicate id")
    for entry in review["impact_reviews"]:
        for tid in entry["threats"]:
            if tid not in threat_ids:
                problems.append(f"impact review {entry['id']}: unknown threat {tid}")
        for path, areas in material(entry["paths"]).items():
            missing = sorted(set(areas) - set(entry["areas"]))
            if missing:
                problems.append(
                    f"impact review {entry['id']}: {path} is in area(s) {', '.join(missing)} not listed"
                )
    return problems


def _append_only_problems(earlier, current):
    """Entries at the base may only gain confirmed_by (a person confirming them); nothing else changes."""
    problems = []
    for key, entry in earlier.items():
        if key not in current:
            problems.append(f"impact review {key} was removed since the base; impact reviews are append-only")
            continue
        now = current[key]
        before, after = entry.get("confirmed_by"), now.get("confirmed_by")
        confirming = before is None and bool(after)
        if {**now, "confirmed_by": None} != {**entry, "confirmed_by": None} or (
            after != before and not confirming
        ):
            problems.append(f"impact review {key} was changed since the base; add a new entry instead")
    return problems


def check_earlier_review(path, review, base_review, register, build, base_build=None, schema=None, raw=None):
    """Problems with the review of an earlier build that the change set adds or edits.

    A stacked change set can release several builds at once (0.37.0, 0.38.0 and 0.39.0 in one pull
    request); the review of each earlier build is part of it. Its open lists are a record of the
    register at that build and are not compared with today's register. A review that already existed
    at the base is append-only. It takes new entries only while its build is still the build at the
    base (`base_build`): a change set may review a change in that build's review and bump the build
    later. The review of a build already superseded at the base is closed, because a new change is
    reviewed in a build that has not shipped."""
    schema = schema if schema is not None else load_json(ROOT, REVIEW_SCHEMA)
    label = f"release review {path}"
    problems = schema_errors(review, schema, label)
    if problems:
        return problems
    problems += secret_problems(review, label, raw)
    named = reviews_in([path]).get(path)
    if review["release"] != named:
        problems.append(f"{label}: release {review['release']} does not match its file name")
    if named and build_key(named) > build_key(build):
        problems.append(f"{label}: build {named} is newer than the current build {build}")
    problems += _entry_problems(review, {threat["id"] for threat in register["threats"]}, label)
    if base_review is not None:
        earlier = {entry["id"]: entry for entry in base_review.get("impact_reviews", [])}
        current = {entry["id"]: entry for entry in review["impact_reviews"]}
        problems += _append_only_problems(earlier, current)
        if named != base_build:
            current_path = REVIEW.format(build=build)
            for key in current:
                if key not in earlier:
                    problems.append(
                        f"impact review {key} was added to {path}, the review of build {named}, which was "
                        f"already superseded at the base; add it to {current_path} instead"
                    )
    return problems


def check_review(
    review,
    register,
    changed=(),
    root=ROOT,
    schema=None,
    build=None,
    base_review=None,
    raw=None,
    earlier_reviews=(),
):
    """Every problem with one release review against the register, the change set and the review at its base.

    `earlier_reviews` is [(path, review, review at the base or None)] for the reviews of earlier builds
    that the same change set adds or edits (a stacked pull request); their new entries count as impact
    reviews of this change set too. Check them on their own with check_earlier_review."""
    schema = schema if schema is not None else load_json(ROOT, REVIEW_SCHEMA)
    problems = schema_errors(review, schema, "release review")
    if problems:
        return problems
    problems += secret_problems(review, "release review", raw)
    if build and review["release"] != build:
        problems.append(f"release review: release {review['release']} is not the current build {build}")
    review_path = REVIEW.format(build=review["release"])
    for path in review["evidence"]:
        if not (Path(root) / path).exists():
            problems.append(f"release review: evidence path {path} does not exist")

    computed = open_lists(register)
    for label in ("open_critical", "open_other", "open_chains"):
        listed, expected = review[label], computed[label]
        listed_by_id = {item["id"]: item for item in listed}
        expected_by_id = {item["id"]: item for item in expected}
        for key, item in expected_by_id.items():
            if key not in listed_by_id:
                problems.append(
                    f"release review: {label} hides {key} {item['title']!r} ({item['reason']}); list everything unresolved"
                )
            elif listed_by_id[key] != item:
                problems.append(
                    f"release review: {label} entry {key} differs from the register: expected {json.dumps(item)}"
                )
        for key in listed_by_id:
            if key not in expected_by_id:
                problems.append(
                    f"release review: {label} lists {key}, which the register does not leave open there"
                )
        if len(listed_by_id) != len(listed):
            problems.append(f"release review: {label} lists an entry twice")

    if review["passed"] or review["gates"]["G11"]["status"] == "Pass":
        for item in computed["open_critical"]:
            problems.append(
                f"release review: marked passed while critical threat {item['id']} {item['title']!r} is open ({item['reason']})"
            )
        for item in computed["open_chains"]:
            problems.append(
                f"release review: marked passed while chain {item['id']} {item['title']!r} is open ({item['reason']})"
            )
        for threat in register["threats"]:
            if threat["impact"] == "Critical" and not threat["residual_decision"]["confirmed_by"]:
                problems.append(
                    f"release review: marked passed while the decision on {threat['id']} is unconfirmed"
                )
        for chain in register["chains"]:
            if not chain["residual_decision"]["confirmed_by"]:
                problems.append(
                    f"release review: marked passed while the decision on chain {chain['id']} is unconfirmed"
                )
        for entry in review["impact_reviews"]:
            if not entry["confirmed_by"]:
                problems.append(
                    f"release review: marked passed while impact review {entry['id']} is unconfirmed"
                )

    problems += _entry_problems(review, {threat["id"] for threat in register["threats"]})

    # Impact reviews are append-only, and only an entry added by this change set covers its material
    # paths: an entry new in this build's review, or in the review of an earlier build released by the
    # same (stacked) change set.
    earlier = {entry["id"]: entry for entry in (base_review or {}).get("impact_reviews", [])}
    current = {entry["id"]: entry for entry in review["impact_reviews"]}
    problems += _append_only_problems(earlier, current)
    sources = [(review, earlier)] + [
        (
            other,
            {entry["id"]: entry for entry in (other_base or {}).get("impact_reviews", [])},
        )
        for _, other, other_base in earlier_reviews
    ]
    touched = material(changed)
    if touched and review_path not in set(changed):
        problems.append(
            f"impact review missing: the change set touches {', '.join(touched)} but does not modify {review_path}; "
            "add an impact_reviews entry for this change"
        )
    for path, areas in touched.items():
        naming, fresh = [], []
        for document, before in sources:
            for entry in document["impact_reviews"]:
                if path in entry["paths"]:
                    naming.append(entry["id"])
                    if entry["id"] not in before:
                        fresh.append(entry["id"])
        if not naming:
            problems.append(
                f"impact review missing: the change set touches {path} ({', '.join(areas)}); "
                f"add an impact_reviews entry naming it to {review_path}"
            )
        elif not fresh:
            problems.append(
                f"impact review missing: {path} ({', '.join(areas)}) is named only by {', '.join(naming)}, "
                f"which predate this change set; add a new impact_reviews entry for this change to {review_path}"
            )
    return problems


# Git


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


def merge_point(root, base=None):
    """(ref, commit) of the merge-base of HEAD with the base ref (default origin/main, then main)."""
    candidates = [base] if base else ["origin/main", "main"]
    for candidate in candidates:
        try:
            return candidate, _git(root, "merge-base", "HEAD", candidate).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    raise RuntimeError(
        "cannot find a base for the change set (tried " + ", ".join(candidates) + "); pass --base <ref>"
    )


def changed_paths(root, point):
    """Paths changed between a commit and HEAD (committed changes only; a rename lists both paths)."""
    output = _git(root, "diff", "--name-only", "--no-renames", point, "HEAD")
    return sorted(line for line in output.splitlines() if line)


def file_at(root, point, path):
    """A file's text at a commit, or None when it did not exist there."""
    try:
        return _git(root, "show", f"{point}:{path}")
    except subprocess.CalledProcessError:
        return None


# Running


def run(root=ROOT, base=None, changed=None, base_files=None):
    """(problems, report lines) for a repository. With `changed` given, `base_files` ({path: text}) stands
    in for the files at the base; otherwise both come from git."""
    root = Path(root)
    lines, problems = [], []
    register_text = (root / REGISTER).read_text(encoding="utf-8")
    register = json.loads(register_text)
    build = load_json(root, "VERSION.json")["build"]
    review_path = REVIEW.format(build=build)
    base_files = dict(base_files or {})
    label = "the base"
    if changed is None:
        try:
            ref, point = merge_point(root, base)
            changed = changed_paths(root, point)
            label = f"{ref} ({point[:12]})"
            for path in (REGISTER, "VERSION.json", review_path, *reviews_in(changed)):
                base_files[path] = file_at(root, point, path)
            lines.append(f"change set: {len(changed)} paths since {label}")
        except RuntimeError as error:
            problems.append(str(error))
            changed = []
    for path, areas in material(changed).items():
        lines.append(f"  material: {path} ({', '.join(areas)})")

    problems += check_register(register, root, References(root), raw=register_text)
    readable = not schema_errors(register, load_json(ROOT, REGISTER_SCHEMA), "register")
    if readable and base_files.get(REGISTER):
        problems += compare_registers(json.loads(base_files[REGISTER]), register, label)
    # Reviews of earlier builds released by the same change set (a stacked pull request).
    base_build = json.loads(base_files["VERSION.json"])["build"] if base_files.get("VERSION.json") else None
    earlier_reviews = []
    for path in sorted(reviews_in(changed)):
        if path == review_path:
            continue
        if not (root / path).is_file():
            problems.append(
                f"release review {path} was deleted since {label}; the review of every build is kept"
            )
            continue
        if not readable:
            continue
        text = (root / path).read_text(encoding="utf-8")
        document = json.loads(text)
        before = json.loads(base_files[path]) if base_files.get(path) else None
        found = check_earlier_review(path, document, before, register, build, base_build, raw=text)
        problems += found
        if not schema_errors(document, load_json(ROOT, REVIEW_SCHEMA), path):
            earlier_reviews.append((path, document, before))
            lines.append(f"  earlier review in the change set: {path}" + ("" if before else " (added)"))
    if not (root / review_path).is_file():
        problems.append(missing_review_message(build))
    elif readable:
        review_text = (root / review_path).read_text(encoding="utf-8")
        base_review = json.loads(base_files[review_path]) if base_files.get(review_path) else None
        problems += check_review(
            json.loads(review_text),
            register,
            changed,
            root,
            build=build,
            base_review=base_review,
            raw=review_text,
            earlier_reviews=earlier_reviews,
        )
    if readable:
        lists = open_lists(register)
        lines.append(
            f"register: {len(register['threats'])} threats, {len(register['controls'])} controls, "
            f"{len(register['chains'])} chains; open: {len(lists['open_critical'])} critical, "
            f"{len(lists['open_other'])} other, {len(lists['open_chains'])} chains"
        )
        lines.append("open critical: " + (", ".join(item["id"] for item in lists["open_critical"]) or "none"))
    return problems, lines


def init_review(root, prepared_by, today=None):
    """Write the current build's review with the register's open lists and no impact reviews yet."""
    root = Path(root)
    build = load_json(root, "VERSION.json")["build"]
    path = root / REVIEW.format(build=build)
    if path.exists():
        raise FileExistsError(f"{path.relative_to(root)} already exists; edit it instead")
    lists = open_lists(load_json(root, REGISTER))
    review = {
        "schema_version": 1,
        "release": build,
        "register": REGISTER,
        "prepared_by": prepared_by,
        "prepared_on": (today or datetime.date.today()).isoformat(),
        "passed": False,
        "gates": {
            "G11": {"status": "Not passed", "reason": "Review started; no independent assessment recorded."},
            "G12": {"status": "Not run", "reason": "No AI evaluation recorded for this build."},
        },
        **lists,
        "impact_reviews": [],
        "evidence": [REGISTER],
        "notes": [],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="validate everything; exit 1 on any problem")
    parser.add_argument(
        "--base", help="git ref the change set is measured from (default origin/main, then main)"
    )
    parser.add_argument("--open", action="store_true", help="print open_critical, open_other and open_chains")
    parser.add_argument("--init", action="store_true", help="create the current build's release review")
    parser.add_argument(
        "--prepared-by", help="with --init: who prepares the review (a person, or an agent for a person)"
    )
    args = parser.parse_args(argv)
    if args.open:
        print(json.dumps(open_lists(load_json(ROOT, REGISTER)), indent=2, ensure_ascii=False))
        return 0
    if args.init:
        if not args.prepared_by:
            parser.error("--init needs --prepared-by")
        try:
            print("wrote " + str(init_review(ROOT, args.prepared_by).relative_to(ROOT)))
        except FileExistsError as error:
            print(error)
            return 1
        return 0
    problems, lines = run(ROOT, args.base)
    for line in lines:
        print(line)
    for problem in problems:
        print("FAIL " + problem)
    print(
        ("release review check failed: " + str(len(problems)) + " problem(s)")
        if problems
        else "release review check passed"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
