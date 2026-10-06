"""Synthetic predicate checks; never import or execute assemble/main."""

from pathlib import Path
import ast
import copy
import hashlib
import json
import tempfile
from types import SimpleNamespace
import xml.etree.ElementTree as ET

HERE = Path(__file__).parent
CANDIDATE = HERE / "checkpoint-manifest.proposed.py"
BASELINE = "740f81339acf97ad49d3212dec7f1aa1555139b1"
TRACKER = "docs/evidence/sprint-0.35-tracker-source-proof.json"
INSTRUCTION = "docs/evidence/sprint-0.35-instruction-lead-review.json"
XML = "docs/evidence/sprint-0.35-tracker-tests.xml"
SCOPE = "DOCUMENTATION_ONLY_LEAD_PARAGRAPH_REVIEW_ENGINEERING_RULES_UNCHANGED"
NAMES = [
    "app.js",
    "browser_check.mjs",
    "build_backlog.py",
    "index.html",
    "styles.css",
    "test_tracker.py",
    "tracker.py",
    "update.py",
]
REGISTERS = ["docs/COMPLETION-LEDGER.json", "docs/nonprofit-ai/v1.0/requirements.json"]
HELPERS = {
    "read",
    "sha",
    "require",
    "junit",
    "unchanged",
    "tracker_names",
    "verify_tracker",
    "instruction_parts",
    "verify_instruction_leads",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(root, name, value):
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value))


def xml(root, failed=0, skipped=0, count=42):
    suite = ET.Element("testsuite", tests=str(count), failures=str(failed), errors="0", skipped=str(skipped))
    for i in range(count):
        case = ET.SubElement(suite, "testcase", name=f"synthetic-{i}")
        if i < failed:
            ET.SubElement(case, "failure")
        elif i < failed + skipped:
            ET.SubElement(case, "skipped")
    p = root / XML
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(ET.tostring(suite))


def fixture(root):
    for name in NAMES:
        p = root / "tools/development-tracker" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("synthetic input " + name)
    source = {
        "tools/development-tracker/" + name: sha((root / "tools/development-tracker" / name).read_bytes())
        for name in NAMES
    }
    for name in REGISTERS:
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("synthetic unchanged scope register")
    registers = {name: sha((root / name).read_bytes()) for name in REGISTERS}
    xml(root)
    proof = dict(
        exit_code=0,
        source_sha256_start=source,
        source_sha256_end=copy.deepcopy(source),
        source_changed_during_run=[],
        junit=XML,
        junit_sha256=sha((root / XML).read_bytes()),
        counts=dict(tests=42, failures=0, errors=0, skipped=0),
        source_register_sha256_before=registers,
        source_register_sha256_after=copy.deepcopy(registers),
        source_registers_unchanged=True,
    )
    save(root, TRACKER, proof)
    originals = {}
    rows = {}
    for name in ("AGENTS.md", "CLAUDE.md"):
        title = ("# " + name).encode()
        body = b"Engineering rules:\nNo self-approval.\nFrozen SQL stays unchanged.\n"
        original = title + b"\n\n**Current local candidate, original:** previous saved scope.\n\n" + body
        current = title + b"\n\n**Current local candidate, new:** current documented scope only.\n\n" + body
        originals[name] = original
        (root / name).write_bytes(current)
        rows[name] = dict(
            current_whole_sha256=sha(current),
            baseline_whole_sha256=sha(original),
            current_body_sha256=sha(body),
            baseline_body_sha256=sha(body),
            engineering_rules_unchanged=True,
        )
    save(root, INSTRUCTION, dict(baseline_commit=BASELINE, scope=SCOPE, status="PASS", files=rows))
    return originals


def predicates(root, originals):
    tree = ast.parse(CANDIDATE.read_text())
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in HELPERS]
    assert {node.name for node in selected} == HELPERS

    def git(arguments, cwd):
        assert cwd == root and arguments[:2] == ["git", "show"]
        commit, name = arguments[2].split(":", 1)
        assert commit == BASELINE and name in originals
        return originals[name]

    space = dict(
        ROOT=root, Path=Path, ET=ET, hashlib=hashlib, json=json, subprocess=SimpleNamespace(check_output=git)
    )
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(CANDIDATE), "exec"), space)
    return space


def change(root, name, function):
    p = root / name
    value = json.loads(p.read_text())
    function(value)
    save(root, name, value)


def refresh_document(root, document):
    current = (root / document).read_bytes()
    body = current.split(b"\n\n", 2)[2]
    change(
        root,
        INSTRUCTION,
        lambda p: p["files"][document].update(
            current_whole_sha256=sha(current), current_body_sha256=sha(body)
        ),
    )


cases = []


def check(name, function, kind="tracker", refused=True):
    with tempfile.TemporaryDirectory(prefix="tola-manifest-supplemental-test-") as directory:
        root = Path(directory)
        originals = fixture(root)
        space = predicates(root, originals)
        function(root)
        try:
            sources, metadata = space["verify_tracker" if kind == "tracker" else "verify_instruction_leads"]()
        except (RuntimeError, OSError, KeyError, ValueError, TypeError):
            assert refused, "Positive predicate refused: " + name
        else:
            assert not refused, "Invalid predicate silently accepted: " + name
            assert len(sources) == (8 if kind == "tracker" else 2)
            assert metadata["scope"] in {"SUPPLEMENTAL_TRACKER_ONLY_NOT_PRODUCT_ACCEPTANCE", SCOPE}
        cases.append(dict(name=name, status="passed"))


check(
    "Exactly42 genuine synthetic JUnit cases plus exact8 current source hashes qualify tracker-only",
    lambda _: None,
    refused=False,
)
check("Missing tracker proof refuses", lambda r: (r / TRACKER).unlink())
check("Failed tracker process refuses", lambda r: change(r, TRACKER, lambda p: p.update(exit_code=1)))
check(
    "Shrunk equal tracker maps refuse",
    lambda r: change(
        r,
        TRACKER,
        lambda p: [
            p[k].pop("tools/development-tracker/app.js") for k in ("source_sha256_start", "source_sha256_end")
        ],
    ),
)
check(
    "Extra tracker map input refuses",
    lambda r: change(
        r,
        TRACKER,
        lambda p: [p[k].update(extra="synthetic") for k in ("source_sha256_start", "source_sha256_end")],
    ),
)
check(
    "Start/end source drift refuses",
    lambda r: change(
        r, TRACKER, lambda p: p["source_sha256_end"].update({"tools/development-tracker/app.js": "different"})
    ),
)
check(
    "Actually changed tracker source refuses stale proof",
    lambda r: (r / "tools/development-tracker/app.js").write_text("changed current source"),
)
check(
    "Reported source change refuses even equal maps",
    lambda r: change(r, TRACKER, lambda p: p.update(source_changed_during_run=["synthetic"])),
)
check(
    "Unregistered ninth tracker tool input refuses",
    lambda r: (r / "tools/development-tracker/new.py").write_text("extra"),
)
check("Missing actual tracker JUnit refuses", lambda r: (r / XML).unlink())
check("Wrong JUnit selector refuses", lambda r: change(r, TRACKER, lambda p: p.update(junit="other.xml")))
check(
    "Wrong JUnit byte digest refuses", lambda r: change(r, TRACKER, lambda p: p.update(junit_sha256="stale"))
)
check(
    "Claimed43 cases with actual42 refuses",
    lambda r: change(r, TRACKER, lambda p: p["counts"].update(tests=43)),
)


def bad_case(root, failed=0, skipped=0, count=42):
    xml(root, failed=failed, skipped=skipped, count=count)
    change(
        root,
        TRACKER,
        lambda p: p.update(
            junit_sha256=sha((root / XML).read_bytes()),
            counts=dict(tests=count, failures=failed, errors=0, skipped=skipped),
        ),
    )


check("Actual failed JUnit case refuses matching metadata", lambda r: bad_case(r, failed=1))
check("All skipped matching JUnit refuses", lambda r: bad_case(r, skipped=42))
check("Extra actual43rd case refuses matching metadata", lambda r: bad_case(r, count=43))
check("Tracker register source changed refuses", lambda r: (r / REGISTERS[0]).write_text("changed"))
check(
    "Claimed register movement refuses",
    lambda r: change(r, TRACKER, lambda p: p.update(source_registers_unchanged=False)),
)
check(
    "Explicit current whole hashes and exact fixed-baseline title/body qualify documentation-only",
    lambda _: None,
    kind="instruction",
    refused=False,
)
check("Missing instruction review refuses", lambda r: (r / INSTRUCTION).unlink(), kind="instruction")
check(
    "Different baseline commit refuses",
    lambda r: change(r, INSTRUCTION, lambda p: p.update(baseline_commit="HEAD")),
    kind="instruction",
)
check(
    "Instruction review not explicitly PASS refuses",
    lambda r: change(r, INSTRUCTION, lambda p: p.update(status="PENDING")),
    kind="instruction",
)
check(
    "Wrong documentation-only scope refuses",
    lambda r: change(r, INSTRUCTION, lambda p: p.update(scope="PRODUCT_PASS")),
    kind="instruction",
)
check(
    "Missing second instruction document refuses",
    lambda r: change(r, INSTRUCTION, lambda p: p["files"].pop("CLAUDE.md")),
    kind="instruction",
)


def altered(root, old, new):
    p = root / "AGENTS.md"
    p.write_bytes(p.read_bytes().replace(old, new))
    refresh_document(root, "AGENTS.md")


check(
    "Changed instruction title refuses despite refreshed whole/body hashes",
    lambda r: altered(r, b"# AGENTS.md", b"# Changed title"),
    kind="instruction",
)
check(
    "Changed engineering body refuses despite refreshed current hashes",
    lambda r: altered(r, b"No self-approval.", b"Self-approval allowed."),
    kind="instruction",
)
check(
    "Body whitespace change refuses", lambda r: altered(r, b"Frozen SQL", b"Frozen  SQL"), kind="instruction"
)
check(
    "Unrecognised lead boundary refuses",
    lambda r: altered(r, b"**Current local candidate,", b"**New engineering rules,"),
    kind="instruction",
)
check(
    "Stale whole instruction hash refuses",
    lambda r: change(r, INSTRUCTION, lambda p: p["files"]["AGENTS.md"].update(current_whole_sha256="stale")),
    kind="instruction",
)
check(
    "Stale recorded baseline body hash refuses",
    lambda r: change(r, INSTRUCTION, lambda p: p["files"]["CLAUDE.md"].update(baseline_body_sha256="stale")),
    kind="instruction",
)
check(
    "Engineering rules reviewed false refuses",
    lambda r: change(
        r, INSTRUCTION, lambda p: p["files"]["AGENTS.md"].update(engineering_rules_unchanged=False)
    ),
    kind="instruction",
)
report = dict(
    scope="Private synthetic helper predicates only. AST extracts nine pure guards; assemble/main never imported or executed. No repository writes/API/database/browser/checkpoint.",
    assembler_sha256=sha(CANDIDATE.read_bytes()),
    checker_sha256=sha(Path(__file__).read_bytes()),
    results=cases,
)
with (HERE / "supplemental-guard-tests.json").open("x") as output:
    json.dump(report, output, indent=2)
    output.write("\n")
print(json.dumps(dict(passed=len(cases), failed=0, skipped=0, assembler_sha256=report["assembler_sha256"])))
