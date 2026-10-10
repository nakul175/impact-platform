#!/usr/bin/env python3
"""Create the Imprana Commons backlog as GitHub issues from backlog.csv.

Requires the GitHub CLI (`gh`) signed in with access to the repository.

  python3 docs/backlog/create_github_issues.py --repo nakul175/impact-platform --dry-run
  python3 docs/backlog/create_github_issues.py --repo nakul175/impact-platform
  python3 docs/backlog/create_github_issues.py --repo nakul175/impact-platform --release "R1 Pilot"

Each issue is titled "[ID] Title" and is skipped if an issue with that title prefix
already exists, so the script is safe to re-run. Labels and milestones are created
when missing: release:<name>, epic:<name>, priority:<name>, type:<name>.
"""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CSV = HERE / "backlog.csv"
COLOURS = {"release": "1F4E79", "epic": "5319E7", "priority": "D93F0B", "type": "0E8A16"}


def gh(args, capture=True):
    result = subprocess.run(["gh", *args], capture_output=capture, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def slug(text):
    return text.replace(":", "").strip()


def body(row):
    parts = [
        f"**{row['User story']}**",
        "",
        "| Release | Priority | Type | Built today | Persona |",
        "| --- | --- | --- | --- | --- |",
        f"| {row['Release']} | {row['Priority']} | {row['Type']} | {row['Built today']} | {row['Persona']} |",
        "",
        "### Acceptance and rejection criteria",
        "```gherkin",
        row["Acceptance and rejection criteria (Gherkin)"],
        "```",
        f"**{row['Rejection summary']}**",
    ]
    if row.get("Original requirement"):
        parts += ["", "### Original requirement", row["Original requirement"]]
    if row.get("Original acceptance"):
        parts += ["", "**Original acceptance:** " + row["Original acceptance"]]
    meta = [f"Source: {row['Source']}"]
    if row.get("Merged BRD stories"):
        meta.append(f"Merged BRD stories: {row['Merged BRD stories']}")
    if row.get("Related"):
        meta.append(f"Related: {row['Related']}")
    parts += ["", "---", " · ".join(meta)]
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--csv", default=str(DEFAULT_CSV))
    ap.add_argument("--release", help="only create items in this release, e.g. 'R1 Pilot'")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.csv, encoding="utf-8")))
    if a.release:
        rows = [r for r in rows if r["Release"] == a.release]
    print(f"{len(rows)} backlog items")

    labels = {}
    for r in rows:
        for kind, value in (
            ("release", r["Release"]),
            ("epic", r["Epic / area"]),
            ("priority", r["Priority"]),
            ("type", r["Type"]),
        ):
            labels[f"{kind}:{slug(value)}"] = COLOURS[kind]
    milestones = sorted({r["Release"] for r in rows})

    if a.dry_run:
        print(f"would ensure {len(labels)} labels and milestones {milestones}")
        print(body(rows[0]))
        return

    existing_labels = {
        lab["name"]
        for lab in json.loads(gh(["label", "list", "--repo", a.repo, "--limit", "500", "--json", "name"]))
    }
    for name, colour in labels.items():
        if name not in existing_labels:
            gh(["label", "create", name, "--repo", a.repo, "--color", colour])
    existing_ms = {
        m["title"] for m in json.loads(gh(["api", f"repos/{a.repo}/milestones?state=all&per_page=100"]))
    }
    for m in milestones:
        if m not in existing_ms:
            gh(["api", f"repos/{a.repo}/milestones", "-f", f"title={m}"])

    existing = json.loads(
        gh(["issue", "list", "--repo", a.repo, "--state", "all", "--limit", "2000", "--json", "title"])
    )
    done = {i["title"].split("]")[0] + "]" for i in existing if i["title"].startswith("[")}
    for r in rows:
        prefix = f"[{r['ID']}]"
        if prefix in done:
            continue
        lbls = [
            f"release:{slug(r['Release'])}",
            f"epic:{slug(r['Epic / area'])}",
            f"priority:{r['Priority']}",
            f"type:{r['Type']}",
        ]
        gh(
            [
                "issue",
                "create",
                "--repo",
                a.repo,
                "--title",
                f"{prefix} {r['Title']}",
                "--body",
                body(r),
                "--milestone",
                r["Release"],
                *sum((["--label", lab] for lab in lbls), []),
            ]
        )
        print("created", prefix)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(str(e))
