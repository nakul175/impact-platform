"""Release security review check (FR-SEC-001): threat register v2, chains, open critical threats, impact reviews.

    .venv/bin/python scripts/release_review.py --check                 base: merge-base with origin/main (or main)
    .venv/bin/python scripts/release_review.py --check --base HEAD^1   what CI runs (first parent of the merge)
    .venv/bin/python scripts/release_review.py --open                  print the open threats as review JSON

Deterministic and offline: it reads repository files and the local git history only, never the network,
the clock or a database, and finishes in seconds. It fails (exit 1) when:

- the register (docs/current/threat-register.json) does not match its JSON schema, loses or renames a
  threat of the preserved version 1 baseline (specification/contracts/threat-register.json, never edited),
  or references an unknown control, owner role or category;
- a test reference does not resolve: a pytest node ID must name a test function (or Class::method) in
  qualification/, a browser check must name a test("...") declared in that tools/browser/*.mjs file;
- a chain lacks two independent implemented controls with resolvable evidence (independent: different
  layers and no shared control in their depends_on closures);
- the release review of the current build (docs/evidence/release-review-<build>.json) does not list
  exactly the unresolved threats, or is marked passed (or gate G11 Pass) while a critical threat is
  unresolved or a decision or impact review is unconfirmed;
- the change set touches a migration, a *_contracts.py module, packages/contracts/access-policy.json or
  apps/api/impact_api/ai_*.py without an impact-review entry naming that path in the release review;
- the register or the review contains something that looks like a credential.

A threat is resolved only when its residual decision is ACCEPT or MITIGATE and its verification status is
TESTED (named automated tests exist for every listed control); BLOCK, PARTIAL and PENDING stay open.
"""

import argparse
import ast
import fnmatch
import hashlib
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
REVIEW = "docs/evidence/release-review-{build}.json"
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
# Path-to-area map: a change set touching any of these needs an impact-review entry naming the path.
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
    re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key)\b\s*[=:]\s*['\"]?[A-Za-z0-9+/_\-]{12,}"),
)
PYTEST_REF = re.compile(
    r"^(qualification/test_[a-z0-9_]+\.py)::([A-Za-z_][A-Za-z0-9_]*)(?:::([A-Za-z_][A-Za-z0-9_]*))?(?:\[[^\]]+\])?$"
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


class References:
    """Resolves test references against the files in one repository root, parsing each file once."""

    def __init__(self, root):
        self.root = Path(root)
        self.pytest, self.browser = {}, {}

    def _pytest_names(self, relative):
        if relative not in self.pytest:
            names = set()
            path = self.root / relative
            if path.is_file():
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
                        "test"
                    ):
                        names.add(node.name)
                    elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                        for item in node.body:
                            if isinstance(
                                item, (ast.FunctionDef, ast.AsyncFunctionDef)
                            ) and item.name.startswith("test"):
                                names.add(node.name + "::" + item.name)
            self.pytest[relative] = names
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
            relative, first, second = match.groups()
            if not (self.root / relative).is_file():
                return "no such test file " + relative
            name = first + "::" + second if second else first
            if name not in self._pytest_names(relative):
                return "no test " + name + " in " + relative
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


def open_threats(register):
    """Threats that are not resolved (ACCEPT or MITIGATE with TESTED verification), in register order."""
    result = []
    for threat in register.get("threats", []):
        decision = threat["residual_decision"]["decision"]
        status = threat["verification"]["status"]
        if decision not in RESOLVED_DECISIONS:
            reason = "BLOCKED"
        elif status == "PENDING":
            reason = "VERIFICATION_PENDING"
        elif status == "PARTIAL":
            reason = "VERIFICATION_PARTIAL"
        else:
            continue
        result.append(
            {
                "id": threat["id"],
                "title": threat["title"],
                "impact": threat["impact"],
                "decision": decision,
                "verification": status,
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


def _secrets(document, label):
    text = json.dumps(document, ensure_ascii=False)
    return [
        f"{label}: contains text that looks like a credential ({pattern.pattern})"
        for pattern in SECRET_PATTERNS
        if pattern.search(text)
    ]


def check_register(register, root=ROOT, references=None, schema=None, baseline=None):
    """Every problem with the register as a list of messages (empty when it is sound)."""
    root = Path(root)
    references = references or References(root)
    schema = schema if schema is not None else load_json(ROOT, REGISTER_SCHEMA)
    problems = schema_errors(register, schema, "register")
    if problems:
        return problems
    problems += _secrets(register, "register")
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
        decision = threat["residual_decision"]
        if decision["decision"] == "ACCEPT" and not decision["confirmed_by"]:
            problems.append(f"threat {tid}: ACCEPT is a risk acceptance and needs confirmed_by (a person)")
        if threat["verification"]["status"] == "TESTED" and not any(
            controls.get(ref, {}).get("implemented") for ref in threat["control_refs"]
        ):
            problems.append(f"threat {tid}: TESTED verification needs at least one implemented control")

    # The preserved version 1 baseline: unchanged, and every threat carried with its title and impact.
    baseline_path = root / BASELINE
    if baseline is None and baseline_path.is_file():
        if hashlib.sha256(baseline_path.read_bytes()).hexdigest() != register["baseline"]["sha256"]:
            problems.append(f"register: {BASELINE} changed; the version 1 baseline must never be edited")
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    if baseline is None:
        problems.append(f"register: baseline {BASELINE} is missing")
        baseline = []
    for old in baseline:
        new = threats.get(old["id"])
        if not new:
            problems.append(f"threat {old['id']}: baseline threat missing from the register")
        elif (new["title"], new["impact"], new["origin"]) != (old["title"], old["impact"], "v1"):
            problems.append(
                f"threat {old['id']}: title, impact or origin differs from the version 1 baseline"
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
            unresolved = [ref_ for ref_ in entry["evidence"] if references.problem(ref_)]
            for ref_ in unresolved:
                problems.append(
                    f"chain {cid}: unresolvable evidence {ref_} for {ref} ({references.problem(ref_)})"
                )
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


def material(paths):
    """{path: [areas]} for the paths of a change set that need an impact review."""
    result = {}
    for path in paths:
        areas = sorted({area for area, pattern in MATERIAL_AREAS if fnmatch.fnmatchcase(path, pattern)})
        if areas:
            result[path] = areas
    return result


def check_review(review, register, changed=(), root=ROOT, schema=None, build=None):
    """Every problem with one release review against the register and the change set."""
    schema = schema if schema is not None else load_json(ROOT, REVIEW_SCHEMA)
    problems = schema_errors(review, schema, "release review")
    if problems:
        return problems
    problems += _secrets(review, "release review")
    if build and review["release"] != build:
        problems.append(f"release review: release {review['release']} is not the current build {build}")
    for path in review["evidence"]:
        if not (Path(root) / path).exists():
            problems.append(f"release review: evidence path {path} does not exist")

    critical, other = split_open(register)
    for label, listed, computed in (
        ("open_critical", review["open_critical"], critical),
        ("open_other", review["open_other"], other),
    ):
        listed_by_id = {item["id"]: item for item in listed}
        computed_by_id = {item["id"]: item for item in computed}
        for tid, item in computed_by_id.items():
            if tid not in listed_by_id:
                problems.append(
                    f"release review: {label} hides {tid} {item['title']!r} ({item['reason']}); list every unresolved threat"
                )
            elif listed_by_id[tid] != item:
                problems.append(
                    f"release review: {label} entry {tid} differs from the register: expected {json.dumps(item)}"
                )
        for tid in listed_by_id:
            if tid not in computed_by_id:
                problems.append(
                    f"release review: {label} lists {tid}, which the register does not leave open there"
                )
        if len(listed_by_id) != len(listed):
            problems.append(f"release review: {label} lists a threat twice")

    marked_passed = review["passed"] or review["gates"]["G11"]["status"] == "Pass"
    if marked_passed:
        for item in critical:
            problems.append(
                f"release review: marked passed while critical threat {item['id']} {item['title']!r} is open ({item['reason']})"
            )
        for threat in register["threats"]:
            if threat["impact"] == "Critical" and not threat["residual_decision"]["confirmed_by"]:
                problems.append(
                    f"release review: marked passed while the decision on {threat['id']} is unconfirmed"
                )
        for entry in review["impact_reviews"]:
            if not entry["confirmed_by"]:
                problems.append(
                    f"release review: marked passed while impact review {entry['id']} is unconfirmed"
                )

    threat_ids = {threat["id"] for threat in register["threats"]}
    covered = {}
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
        for path in entry["paths"]:
            covered.setdefault(path, entry["id"])
    for path, areas in material(changed).items():
        if path not in covered:
            problems.append(
                f"impact review missing: the change set touches {path} ({', '.join(areas)}); "
                f"add an impact_reviews entry naming it to {REVIEW.format(build=review['release'])}"
            )
    return problems


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


def changed_paths(root, base=None):
    """Paths changed between the merge-base of HEAD with the base ref and HEAD (committed changes only)."""
    candidates = [base] if base else ["origin/main", "main"]
    for candidate in candidates:
        try:
            point = _git(root, "merge-base", "HEAD", candidate).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        output = _git(root, "diff", "--name-only", "--no-renames", point, "HEAD")
        return candidate, point, sorted(line for line in output.splitlines() if line)
    raise RuntimeError(
        "cannot find a base for the change set (tried " + ", ".join(candidates) + "); pass --base <ref>"
    )


def run(root=ROOT, base=None, changed=None):
    """(problems, report lines) for the whole repository."""
    root = Path(root)
    lines, problems = [], []
    references = References(root)
    register = load_json(root, REGISTER)
    problems += check_register(register, root, references)
    register_readable = not schema_errors(register, load_json(ROOT, REGISTER_SCHEMA), "register")
    build = load_json(root, "VERSION.json")["build"]
    review_path = REVIEW.format(build=build)
    if changed is None:
        try:
            ref, point, changed = changed_paths(root, base)
            lines.append(f"change set: {len(changed)} paths since {ref} ({point[:12]})")
        except RuntimeError as error:
            problems.append(str(error))
            changed = []
    for path, areas in material(changed).items():
        lines.append(f"  material: {path} ({', '.join(areas)})")
    if not (root / review_path).is_file():
        problems.append(f"release review missing: {review_path} (one per build in VERSION.json)")
    elif register_readable:
        review = load_json(root, review_path)
        problems += check_review(review, register, changed, root, build=build)
    critical, other = split_open(register) if register_readable else ([], [])
    lines.append(
        f"register: {len(register.get('threats', []))} threats, {len(register.get('controls', []))} controls, "
        f"{len(register.get('chains', []))} chains; open: {len(critical)} critical, {len(other)} other"
    )
    lines.append("open critical: " + (", ".join(item["id"] for item in critical) or "none"))
    return problems, lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="validate everything; exit 1 on any problem")
    parser.add_argument(
        "--base", help="git ref the change set is measured from (default origin/main, then main)"
    )
    parser.add_argument("--open", action="store_true", help="print open_critical and open_other as JSON")
    args = parser.parse_args(argv)
    if args.open:
        critical, other = split_open(load_json(ROOT, REGISTER))
        print(json.dumps({"open_critical": critical, "open_other": other}, indent=2, ensure_ascii=False))
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
