"""Keep the generated "every document" list in docs/DOCUMENTATION-INDEX.md current.

    python scripts/doc_index.py           rewrite the generated section
    python scripts/doc_index.py --check   exit 1 when it is out of date (CI runs this)

The list covers every git-tracked Markdown file under docs/ except docs/evidence/ (retained run
output). The text above the markers is written by hand and is never touched.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs/DOCUMENTATION-INDEX.md"
BEGIN = "<!-- BEGIN GENERATED INDEX (scripts/doc_index.py; do not edit by hand) -->"
END = "<!-- END GENERATED INDEX -->"


def tracked_documents() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "docs"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return sorted(
        path
        for path in out.splitlines()
        if path.endswith(".md")
        and not path.startswith("docs/evidence/")
        and path != "docs/DOCUMENTATION-INDEX.md"
    )


def title_of(path: str) -> str:
    for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip().replace("|", "/")
    return Path(path).stem


def generated_section() -> str:
    folders: dict[str, list[str]] = {}
    for path in tracked_documents():
        relative = path[len("docs/") :]
        folder = relative.rsplit("/", 1)[0] if "/" in relative else "docs (top level)"
        folders.setdefault(folder, []).append(path)
    lines = [BEGIN, "", "## Every document (generated)", ""]
    for folder in sorted(folders, key=lambda f: (f != "docs (top level)", f)):
        lines += [f"### {folder}", ""]
        for path in folders[folder]:
            lines.append(f"- [{title_of(path)}]({path[len('docs/') :]})")
        lines.append("")
    lines.append(END)
    return "\n".join(lines) + "\n"


def updated_index() -> str:
    text = INDEX.read_text(encoding="utf-8")
    if BEGIN in text:
        head = text[: text.index(BEGIN)]
    else:
        head = text.rstrip("\n") + "\n\n"
    return head + generated_section()


def main() -> int:
    wanted = updated_index()
    if "--check" in sys.argv:
        if INDEX.read_text(encoding="utf-8") != wanted:
            print(
                "docs/DOCUMENTATION-INDEX.md is out of date: run `python scripts/doc_index.py` and commit it."
            )
            return 1
        print("docs/DOCUMENTATION-INDEX.md is current.")
        return 0
    INDEX.write_text(wanted, encoding="utf-8")
    print(f"wrote {INDEX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
