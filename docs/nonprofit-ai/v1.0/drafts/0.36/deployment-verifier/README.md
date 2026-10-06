# Private 0.36 deployment verifier — prepared, not run

The integrator owns execution. These helpers have made **no hosting requests and started no browser**. Repository source, evidence and deployment configuration are untouched. The reviewed runtime helpers are byte-identical to the 0.35 proposal (Python `ef56bca3…`, JavaScript `44df3cf9…`): build proof and expected main commit are already explicit parameters. Twenty-three offline tests qualify only the verifier's local refusal and comparison logic. No 0.36 build/deployment qualification is inferred from them.

`verify_deployment.py` requires explicit `--execute`, a root-authored approval/CI/merge evidence record, expected full main commit SHA, and the frozen dual-entry build proof. Missing approval, incomplete CI, missing merge evidence or an older/different public commit/schema produces **NOT_RUN**. A failed packaging, health, TLS or browser assertion produces **FAIL**. There is no retry, deploy, merge, workflow, spending or account operation.

## 0.36 preparation and exact source boundary

The expected release contract remains domain API **1.25.0**, platform API **1.10.0** and schema **40**. This proposal requires the future qualified `docs/evidence/sprint-0.36-web-build-source-proof.json`; it does not reuse the predecessor proof for real deployment. That proof must bind the actual current `VERSION.json`, all required source bytes and the final eight built files to the returned main commit `C`. The public status identifies `C` and schema 40; it is not a separate privileged API/profile/migration proof.

The registered tour checker is unchanged at SHA-256 `f5e40df0a16cd36f75ed6d6f55e224128f96aa402166698513a4272b99881ba4`. Its exact sixteen anonymous workflow groups remain the source for `verify_walkthrough.mjs`. The future build must still have two HTML entries/six assets and a tour graph of one HTML/four assets. A changed graph, count, source-checker hash or served byte mismatch requires explicit review and a new source-bound proposal; never relax those assertions merely to pass.

The 0.36 build proof, CI head and main merge commit have not been supplied yet. Actual hosting, public browser, deployment and provider execution remain **NOT_RUN**. Missing financial/human merge authorization or any of the four exact-head successes remains a refusal, with no remote CI lookup or automatic spending approval.

## Required root observations

1. Complete final local qualification and obtain the applicable financial authorization before paid CI. Preserve the exact four executed job successes and their real head/run references.
2. Merge using the authorized exact-head gate. Resolve the returned main commit `C`; observe its automatic main-push CI as specified by the separate release plan. Prefer recording those four successes directly on `C` here.
3. Keep the expected merge object available locally. The verifier does not fetch Git. If a different tested head is supplied, it requires that head to be an actual ancestor of `C` and have an identical complete Git tree. A GitHub synthetic PR checkout `M` must never be relabelled as `C`; a non-ancestor synthetic merge is refused. Use the actual main-push result on `C`.
4. Retain the exact build proof and local `apps/web/dist`. Every recorded source hash must match both the current local bytes and `git show C:path`. All eight built file hashes must match the current local build. No production rebuild is performed here, and a nondeterministic/mismatched bundle is never waived.

Create a private root record using actual evidence, replacing this deliberately non-authorizing template. Do not include tokens, credentials or query-string secrets:

```json
{
  "financial_approval": false,
  "financial_approval_reference": "PENDING — replace only from trusted owner instruction",
  "merge_authorized": false,
  "main_merge_commit": "PENDING",
  "ci": {
    "head_sha": "PENDING",
    "run_url": "PENDING",
    "jobs": {
      "local-reference-and-browser": "NOT_RUN",
      "live-identity-provider": "NOT_RUN",
      "native-postgresql-gate": "NOT_RUN",
      "container-stack": "NOT_RUN"
    }
  }
}
```

The helper validates this record's contents and local commit relationship. **It does not independently query GitHub, establish human authorization or approve spending.** Root must supply the trusted records. The template cannot authorize execution.

## Source and deployment expectations

- Frozen proof: `docs/evidence/sprint-0.36-web-build-source-proof.json`; successful strict TypeScript and dual-entry Vite exits `[0,0]`, identical before/after source maps, exact eight built files.
- Actual public `deploy-status.json`: full expected commit, schema string/number `40`, result `ok`, empty alerts, exact application origin, `tls: "acme"` (the current deploy script's public-certificate label), and running postgres/keycloak/api/worker/executor/mailsink/caddy/backup. An explicit unhealthy status fails. Missing health probes can remain null as in the current deployment format; readiness is checked independently.
- HTTPS must validate the public certificate chain and hostname. Neither Python nor Chrome can disable verification. HTTP redirect is additionally checked by the existing smoke. No proxy or credential environment is passed into the smoke/Chrome processes.
- Both initial and final public status are streamed within 128 KiB with no-cookie checks before decoding; each health body is streamed within 4 KiB. Status is scanned for secret-looking field names and recognizable bearer/JWT/DSN/PEM/password assignment patterns. Only its safe health/identity projection is retained; full `log_tail`, configuration and status body are never saved. This pattern scan cannot certify the absence of arbitrary unknown secrets.
- `/health/live` and `/health/ready` return their exact public state documents, without cookies. Public schema status plus readiness is **not** a privileged live migration-ledger proof.
- The normal `/` entry is downloaded and inspected, never executed. Its compiled graph and the separate tour graph must exactly cover all six asset paths in the eight-file proof. HTML is at most 128 KiB; each script/style at most 8 MiB. Same-origin bounded `/assets/` references only; no external/dev/query/fragment/traversal/redirect/cookie asset is accepted. Every response hash is recorded, including a mismatch before refusal.
- The existing default `scripts/smoke.py` is run with its sole `--no-provider` switch: TLS, redirect, live, ready, normal headers/root, default public tour and deploy status remain active. Its four auth/provider probes are explicitly skipped, so this creates no sign-in state and contacts no provider.
- `verify_walkthrough.mjs` is derived offline from the exact registered 16-group local workflow checker. The frozen source checker hash is recorded. Fixture/login/database observers are removed; nothing creates or selects a real identity.

The browser uses a **fresh anonymous context**, TLS verification, blocked service workers/downloads, and only GETs for `/ai-walkthrough.html` plus its four exact compiled assets. API/auth/provider/other-origin/query/header-credential requests are aborted and fail the result. Fetch/XHR/WebSocket/EventSource/beacon, local/session storage, IndexedDB and cookie APIs are trapped. Only visibly fictional/synthetic text is entered. The five real steps, deliberate brief preview/replacement, cancellation, manual notes, local procurement editing, reload/reset, and keyboard reachability are checked. Fifteen captures/scans cover 1440/390/320 widths; axe incompletes and manual assistive-technology limitations are preserved. Each served asset hash, source stability and reset outcome remains in the named report.

Fresh-context cookie refusal does not claim that existing user browsers lack ambient same-origin cookies. Reduced browser background traffic is not a whole-OS packet capture. Static GETs can change ordinary access logs/metrics; no domain action or application DB observation is requested. This verifier does not qualify authenticated use, real onboarding, current grants, a provider, procurement, human review/approval, certification or official impact.

## Offline checks (safe during qualification)

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python /private/tmp/tola-ai-036-deployment-verifier/run_offline_no_sockets.py
```

The copied twenty-three baseline checks use in-process MockTransport or local byte/Git stubs, without sockets, an HTTP server, a browser or hosting. Their local eight-file/build controls deliberately still read the saved 0.35 proof as an offline comparison fixture; those controls are not 0.36 build evidence. The runtime launch below must receive the future qualified 0.36 proof. A socket-denying private runner adds a fail-closed boundary for this preparation run. A default-command test proves NOT_RUN without network/subprocess calls. `compose_browser.py` was used only to prepare the reviewable JavaScript; it is not run during deployment verification.

## Root-only launch after the gates

Replace the three `ACTUAL_*` placeholders with already observed public origin, returned full main commit and the private evidence-record path. Use a **new** output directory; existing reports cannot be overwritten.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python /private/tmp/tola-ai-036-deployment-verifier/verify_deployment.py \
  --repo /Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform \
  --origin https://ACTUAL_PUBLIC_HOST \
  --expected-commit ACTUAL_FULL_MAIN_SHA \
  --build-proof docs/evidence/sprint-0.36-web-build-source-proof.json \
  --gate /private/tmp/ACTUAL_ROOT_GATE.json \
  --output /private/tmp/tola-ai-036-deployment-actual-attempt-01 \
  --node /Users/athena/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
  --browser-executable '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --execute
```

Omit `--execute` to produce a private NOT_RUN plan without reading a gate record or contacting any origin. Exit codes: `0 PASS`, `1 FAIL`, `2 NOT_RUN`. Output is mode0700, JSON reports mode0600; captures are inside that private directory. Root should review desktop/mobile captures and all incomplete/manual findings before copying sanitized evidence or sharing a verified tour link. This helper never writes repository evidence.
