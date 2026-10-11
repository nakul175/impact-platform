# APLYD QA v1.3 — package audit facts for Imprana Commons

This audit reads the unchanged owner-supplied package and current Imprana documentation baseline. It supplies proposed reconciliation requirements only. It does not install the package, registers, CI, AGENTS rules, CODEOWNERS or repository settings. No Linear write, application/provider/native/browser/production run, spending, new PR, merge or deployment occurred.

## Actual package integrity and checker observations

- ZIP SHA-256: `26c64346226f660f6a648e5cebcaf2ee893750e1fb8fe50b13821aae631b5e5a`.
- All 86 archive files match the extracted reference byte for byte; all 85 self-excluding manifest records match. No reference file changed or new bytecode file appeared.
- The checker and regression sources were read before execution: only local reads/standard-library operations; regression fixtures are copied/mutated in dedicated temporary directories. Python bytecode was disabled.
- Genuine unchanged bundled regression suite on supported Python 3.12.15: **57 tests passed**, exit 0. An earlier observed Python 3.9.6 run is retained separately; this supported-runtime proof governs the final qualification. Raw stdout/stderr are preserved separately. These qualify the bounded package checker, not Imprana features.
- Fictional lifecycle structural check: exit 0, planned 2/2, validated 1/2, authored selected PASS 1 / FAIL 1. Strict release mode exits 1 for incomplete validation and a failed required mapping. These authored observations are teaching data only.
- Empty adoption registers: structural exit 0 with 0/0 and null ratios; release mode exits 1 because source/candidate/evidence population is missing.
- PM mapping against both bundled extracted index and the installed v4.2 archive full catalogue: exit 0. Actual catalogue edition is `3.0-generic`, SHA-256 `cec6bc14f5976dd7e1a48ba9f224e18b1258abb08ed0479a7f080b2dc6245456`. This proves listed field/alias/gate-prefix membership and source pins, not input-schema, semantic, all-tier or approval compatibility.
- Fictional criteria-pin helper output matched the fixture count/identity/source-byte pins; it only emits candidate values, never writes or approves scope.

## Adoption and readiness boundaries

The normative package hierarchy is subordinate to existing product/repository authority (`standards/TESTING-STANDARD.md:3`). Ready/Done, AI assurance, planning structure, observed test evidence, authenticated approval, release readiness, deployment and learning stay separate. Existing Imprana requirements and natural-person/tenant/current-authority/immutable-history/official-arithmetic controls remain intact.

Before real release reliance, the package demands an independent complete canonical AC source export and pins, plus verified external human CODEOWNER/fresh-review/trusted-required-check/bypass protections or independently controlled canonical-source reconciliation (`workflow/CRITERIA-SOURCE-PINNING.md:2–24`, `workflow/SOURCE-PROTECTION.md:2–16`). The template is inactive. This audit does not prove the real repository has or lacks these settings. Mark the adoption control evidence **NOT_VERIFIED**, not as an observed configured pass. A required unverified source-control gate cannot be cleared by offline exit 0.

The 54-row requirements matrix contains exact source file SHA and line ranges, checker boundaries, and proposed Imprana reconciliation actions. The bounded baseline comparison uses documentation statuses **ALIGNED/PARTIAL/MISSING/NOT_VERIFIED**, separate from execution results. Its MISSING claims are exact-path absence at `b01a628`, not absence of the product capability; root’s current additive audit documents are outside that frozen source state.

## What the checker actually evaluates

- Eight exact-schema registers: AC, case, link-only traceability, immutable run, coverage selection, defect event, risk, exception. The separate `data-register.csv` and `threshold-register.csv` are not in the evaluated schema (`standards/register-schema.json`; `checker/qa_lint.py:39`).
- Count/identity/version/source-byte/applicability consistency against the supplied source export; local relative reference existence/containment and symlink resolution; portable evidence roots; explicit selected run/candidate/version/purpose/freshness equality.
- Present required PASS/FAIL evidence fields and timezone-aware chronology, risk minimum scoring, D1–D4 severity predecessor review fields, defect case identity and same-case/current qualification retest/build, stricter full release snapshot, exception expiry.
- AUTO files and marker text under an explicitly supplied repository root, not test discovery/execution/assertions or meaningful attachment of that marker.
- Mechanical coverage uses selected required mappings, not unique test functions; UNKNOWN remains the AC denominator, NO requires rationale/review, and zero denominator returns null.

## What it cannot establish

No evidence/source/owner/approval authentication; no omitted canonical criteria discovery; no enforcement of append-only history against previous Git; no truth/digest validation of an executed deployable artifact; no numerical/statistical threshold evaluation; no domain/specialist adequacy, legal or accessibility certification; no validity of compensation/exception authority; no actual CI configuration/execution or release/deployment permission. Freeform Markdown and all narrative hierarchy links are not parsed. HTTPS/record references warn but are not fetched; local fragments are locators only. Digest strings and CURRENT/approval labels are declarations until externally reconciled. The containment check is point-in-time; immutable stores avoid concurrent directory drift.

Strict release mode deliberately rejects any applicable required mapping that lacks selected PASS/CURRENT qualification evidence, UNKNOWN applicability, no applicable ACs or open D3/D4 defects. It auto-waives no exception. An otherwise clean strict record gate is only one subordinate gate and cannot establish overall READY (`checker/README.md:22–44`, `checker/qa_lint.py:278–292`).

## Integration guidance for this request

Add a compact QA audit and prioritised reconciliation plan only. Preserve historical nonprofit cases/statuses/evidence, original product criteria and hashes; map old case/criterion aliases explicitly. Inventory all existing suites and reuse narrow meaningful checks before proposing new tools. Use documentation states separately from actual checker results. Keep any future full adoption, source-export deployment, register migration, runtime qualification, native publication, repository-setting changes and paid actions behind their actual authorised engineering scope.
