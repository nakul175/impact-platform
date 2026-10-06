# Review of the interrupted 0.36 producer drafts

6 October 2026. **Source review only: none of these drafts was executed.** They remain preserved proposals exactly as found. This note records what a read-through found so the next engineer does not run them as-is. The review was delegated to a read-only subagent; the two facts the conclusions rest on were re-checked directly: the documented 0.35 checkpoint `be65086636804027a5fe33943478446b557ebff9` is not present in the shallow clone (`git cat-file` fails), and the producers, wrapper and manifest assembler contain `/Users/athena` and `/private/tmp` paths, with the full producer reading a persisted password map at `/private/tmp/tola-ai-native-build/login-passwords-033.json`.

## Verdicts

| Draft | Verdict | Why |
| --- | --- | --- |
| `producer-drafts/tola-ai-036-full-qualification.py`, `-unit.py`, `-lint-final.py`, `-build-final.py` | Run only after edits | They are the 0.35 producers plus a guard requiring a 40-hex baseline commit that is an ancestor of HEAD with VERSION build 0.35.0. Paths, lock files and Node/PATH are Mac-specific. The full producer reads a persisted login-password map and a fixed port/user instead of the governed `IMPACT_FIXTURE_DSN` flow. Lint and build open their raw logs exclusively, so a leftover log aborts the run after the lock is taken. |
| `checkpoint-manifest.proposed.py` | Run last, after edits | It is the 0.35 assembler with 420/426 inventories, 74/111 build/lint inputs and five pure prerequisites. It requires evidence that no draft produces: a tracker run, a reference report, an instruction-lead review, `RELEASE-0.36-procurement-preview.md` and `DEVELOPMENT-0.36.md`. It hard-codes `owner_merge_authorisation: True`, which must come from a recorded gate, not a constant. |
| `browser-qualification.proposed.py` and `browser-wrapper/` | Run only after edits | Requires macOS and a Mac Chrome and swaps the packaged Chromium launcher, which is left in place if the process is killed. On Linux the packaged Chromium works without the swap. No baseline-commit guard. |
| `deployment-verifier/` | Do not run yet | It is post-merge and read-only, and there is no merge, CI run or deployment to verify. Its README still refers to the earlier walkthrough checker hash; the checker changed in 0.36. |
| `prepare_sources.py`, `*.patch`, `preserved035/*`, `frozen-inventories.json`, `*.before.py` | Leave alone | Provenance. |

## Conflicts with committed evidence

None found. Outputs are all `sprint-0.36-*` and keep the 0.35 file layout and keys. The deltas are counts (browser fingerprints 423→426, pure prerequisites 4→5) and extra proof keys. The frozen inventories (application 420, build 74, lint 111, browser 426) match the integrated tree by reading.

## What was done instead

The producers were not ported. The 0.36 results in the release note come from running the repository's own gates (`make lint`, `make unit`, `scripts/run.py` modes and native, the strict build) on the committed tree, with per-step logs and the original overwritten evidence files preserved. That is a legitimate local record but it is **not** a producer-generated, source-bound 0.36 checkpoint manifest, and the release note says so.

## Minimum edits for a producer-generated 0.36 manifest

1. Make ROOT, lock, log, work, Node and PATH constants portable; use `29e40e6` (fetch `be65086` for the complete historical checkpoint) as the baseline.
2. Replace the password-map reads with the repository's governed native setup.
3. Drop the darwin and Mac Chrome requirements and the launcher swap in the wrapper; add a clean-tree and baseline-commit guard.
4. Create the missing inputs the assembler requires and take merge authorisation from a recorded gate.
5. Restore tracked generic evidence files before any baseline snapshot, so modified bytes are not recorded as historical.
6. Preserve any failed result under an archive name before re-running.
