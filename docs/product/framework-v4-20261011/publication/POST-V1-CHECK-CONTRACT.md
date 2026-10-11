# One separate post-verification receipt

This checker performs only offline readback verification. It never writes to Linear or Git, reruns application tests, changes acceptance criteria, or replaces the complete v1 publication report. Native v2 publication remains the root integration lane's action.

First copy the actual v1 PASS report, final full issues, final full documents, final project, frozen publication plan, declared formatting policy and exact v1 verifier source into a new immutable v1 evidence directory inside this output root. Preserve all original files and hashes. The PASS report's embedded input hashes must match the copied files. An actual v1 FAIL or incomplete counts cannot qualify.

Create a **new separate** v2 delta plan with exactly these fields:

```json
{
  "kind": "Imprana Commons post-publication overview receipt v2",
  "overview_id": "61b8c340-13f3-4d51-8c6f-bfc23a6660a5",
  "marker": "<!-- imprana:publication-verification:20261011:v2 -->",
  "append": "<exact separately reviewed plain paragraph beginning with two newlines and containing this marker once>",
  "baseline": {
    "report": {"path": "<frozen actual v1 PASS report>", "sha256": "<actual SHA256>"},
    "issues": {"path": "<frozen full issues>", "sha256": "<actual SHA256>"},
    "documents": {"path": "<frozen full documents>", "sha256": "<actual SHA256>"},
    "project": {"path": "<frozen full project>", "sha256": "<actual SHA256>"},
    "publication_plan": {"path": "<frozen v1 publication plan>", "sha256": "<actual SHA256>"},
    "policy": {"path": "<frozen v1 formatting policy>", "sha256": "<actual SHA256>"},
    "verifier": {"path": "<exact frozen v1 verifier source>", "sha256": "<actual SHA256>"}
  },
  "allowed_suffix_normalization": null
}
```

The placeholders above are a schema illustration, not actual evidence or an executable publication plan. Relative paths resolve against this output root; all frozen inputs must remain inside it. Use a plain paragraph with an already explicit blank line after the marker. A new heading/table/autolink transformation receives no implicit formatting allowance. The append should state the actual v1 counts and bounded quality outcome and explicitly retain product testing, owner acceptance and Ready/Done limitations.

After the single authorized root write, collect full overview and full project readbacks into separate v2 files. The checker requires the complete v1 overview content as an exact untouched prefix, exactly one new marker and the exact declared append. All captured overview metadata except intentional updatedAt/updatedBy must stay exact. Resource IDs/count and every full resource member stay exact, except only the overview resource's updatedAt must equal the corresponding before/after full overview updatedAt. The other thirteen resources, all five milestone members and project fields except updatedAt remain exact. No v1 document timestamp exemption applies to v2.

Only if an actual v2 readback demonstrates removal of precisely one final newline from the new append, preserve its actual observation as a hashed file and use a separately declared plan edition with:

```json
{"name":"remove_single_final_lf","actual_observation_pin":{"path":"<actual observed evidence>","sha256":"<actual SHA256>"}}
```

No normalization touches the frozen v1 prefix. Unknown differences fail. Preserve any original failed plan/report/readback edition; do not silently replace it.

Run `verify_post_publication_overview.py` with `--base`, `--plan`, `--after-overview`, `--after-project` and a distinct `--output` report. All actual input hashes and the checker hash are included in that separate report. The five synthetic corruption guard groups are checker tests only; they do not establish Native v2 execution or product acceptance. Other issues and documents are not re-read by this v2 checker, so its scope must remain the one receipt append and fresh project projection.
