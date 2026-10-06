"""Offline composition of the hosted checker from the reviewed local workflow assertions.

The output is standalone, reviewable JavaScript; this composer is not used at launch.
No browser, server or network starts here.
"""

from pathlib import Path
import hashlib

REPO = Path(
    "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform"
)
original = (REPO / "tools/browser/ai-walkthrough-check.mjs").read_text()
start = original.index('  await test("separate static entrypoint')
end = original.index("\n} finally {", start)
tests = original[start:end]
tests = tests.replace(
    "        scans.push({\n",
    "        scans.push({\n          incomplete: a.incomplete.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.map((n) => n.target) })),\n          inapplicable_count: a.inapplicable.length,\n          passed_rule_count: a.passes.length,\n",
)
tests = tests.replace(
    '    assert.deepEqual(await hashes(), before);\n    for (const [route, expected] of Object.entries(assets))\n      assert.equal(await hash("dist" + route), expected);\n',
    "    assert.deepEqual(await hashes(), before);\n",
)
tests = tests.replace("new URL(r.url).origin === origin", "r.origin === origin")
tests = tests.replace(
    'reply.path === "/ai-walkthrough.html"\n          ? await hash("dist/ai-walkthrough.html")\n          : assets[reply.path]',
    "expectedAsset(reply.path)",
)
prelude = r"""// Private root-gated hosted verifier, composed offline from reviewed workflow tests.
// No database/login/fixture runner code is included. Only static public GETs are allowed.
import { createRequire } from "node:module";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
const manifestPath = process.argv[2];
assert(manifestPath?.startsWith("/private/tmp/"), "Root-issued private manifest required");
const m = JSON.parse(await fs.readFile(manifestPath, "utf8"));
assert.equal(m.root_gate_passed, true, "Python approval/CI/static gates must pass first");
assert(/^[0-9a-f]{40}$/.test(m.expected_commit));
assert(/^https:\/\/[^/?#@]+$/.test(m.origin));
const repository = m.repo, origin = m.origin;
const require = createRequire(path.join(repository, "tools/browser/package.json"));
const { chromium } = require("playwright-core");
const sha = (bytes) => createHash("sha256").update(bytes).digest("hex");
assert.equal(sha(await fs.readFile(fileURLToPath(import.meta.url))), m.browser_source_sha256);
const hash = async (name) => sha(await fs.readFile(path.join(repository, "apps/web", name)));
const hashes = async () => Object.fromEntries(await Promise.all(Object.keys(m.sources).map(async (name) => [name, sha(await fs.readFile(path.join(repository, name)))])));
const before = await hashes();
assert.deepEqual(before, m.sources);
assert.equal(sha(await fs.readFile(m.build_proof)), m.build_proof_sha256);
const assets = Object.fromEntries(Object.entries(m.assets).filter(([name]) => name.startsWith("assets/")).map(([name, value]) => ["/" + name, value]));
for (const [name, value] of Object.entries(m.assets)) assert.equal(await hash("dist/" + name), value);
const allowed = new Set(["/ai-walkthrough.html", ...m.tour_asset_paths]);
assert.equal(allowed.size, 5, "Exact separate tour graph expected");
for (const route of m.tour_asset_paths) assert(assets[route] && /\/(?:walkthrough|ai-enablement)-/.test(route));
const expectedAsset = (route) => route === "/ai-walkthrough.html" ? m.assets["ai-walkthrough.html"] : assets[route];
const evidenceFile = path.join(m.output, "walkthrough-browser.json"), captureDir = path.join(m.output, "captures");
await fs.mkdir(captureDir, { recursive: false, mode: 0o700 });
const guidance = JSON.parse(await fs.readFile(path.join(repository, "apps/web/src/walkthrough-guidance.json"), "utf8"));
const axe = await fs.readFile(require.resolve("axe-core/axe.min.js"), "utf8");
const results = [], errors = [], consoleErrors = [], requests = [], blocked = [], scans = [], shots = [], staticResponses = [];
const browser = await chromium.launch({
  executablePath: m.browser_executable, headless: true,
  args: ["--disable-background-networking", "--disable-component-update", "--disable-sync", "--no-first-run", "--disable-default-apps"],
  env: Object.fromEntries(Object.entries(process.env).filter(([key]) => ["HOME", "PATH", "TMPDIR", "TEMP", "TMP", "LANG", "LC_ALL", "SYSTEMROOT"].includes(key))),
});
const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, ignoreHTTPSErrors: false, serviceWorkers: "block", acceptDownloads: false });
assert.deepEqual(await context.cookies(), []);
await context.addInitScript(() => {
  window.__walkthroughCalls = [];
  const deny = (name) => function () { window.__walkthroughCalls.push(name); throw new Error("Public fictional walkthrough refuses " + name); };
  window.fetch = deny("fetch"); window.XMLHttpRequest = deny("XMLHttpRequest"); window.WebSocket = deny("WebSocket"); window.EventSource = deny("EventSource");
  navigator.sendBeacon = deny("sendBeacon");
  for (const name of ["getItem", "setItem", "removeItem", "clear"]) Storage.prototype[name] = deny("Storage." + name);
  for (const name of ["localStorage", "sessionStorage", "indexedDB"]) Object.defineProperty(window, name, { get: deny(name) });
  Object.defineProperty(document, "cookie", { get: deny("cookie.read"), set: deny("cookie.write") });
});
await context.route("**/*", async (route) => {
  const request = route.request(), url = new URL(request.url());
  const clean = { method: request.method(), origin: url.origin, path: url.pathname, resource: request.resourceType(), has_query: Boolean(url.search), has_authorization: "authorization" in request.headers(), has_cookie: "cookie" in request.headers() };
  requests.push(clean);
  if (clean.method === "GET" && url.origin === origin && allowed.has(url.pathname) && !url.search && !url.hash && !clean.has_authorization && !clean.has_cookie && ["document", "script", "stylesheet"].includes(clean.resource)) await route.continue();
  else { blocked.push(clean); await route.abort(); }
});
const page = await context.newPage(); page.setDefaultTimeout(15000);
page.on("response", (r) => {
  const url = new URL(r.url());
  staticResponses.push((async () => {
    let observed = null, body_error = null;
    try { const bytes = await r.body(); assert(bytes.length <= 8 * 1024 * 1024); observed = sha(bytes); } catch (e) { body_error = e.name; }
    return { path: url.pathname, origin: url.origin, status: r.status(), sha256: observed, expected_sha256: expectedAsset(url.pathname) ?? null, matches: observed === expectedAsset(url.pathname), body_error, sets_cookie: Boolean(r.headers()["set-cookie"]), content_type: r.headers()["content-type"] ?? null, csp: r.headers()["content-security-policy"] ?? null };
  })());
});
page.on("pageerror", (e) => errors.push(e.message));
page.on("console", (m) => { if (m.type() === "error") consoleErrors.push(m.text()); });
const btn = (name) => page.getByRole("button", { name, exact: true });
const field = (name) => page.getByRole("textbox", { name: new RegExp("^" + name) });
async function open() { await page.goto(origin + "/ai-walkthrough.html"); await page.getByRole("heading", { name: "A first AI pilot, with people in control", exact: true }).waitFor(); }
async function practice() { await btn("Try a manual task").click(); await btn("Preview the invented brief for this task").waitFor(); }
async function test(name, run) { try { await run(); results.push({ name, status: "passed" }); } catch (e) { results.push({ name, status: "failed", error_type: e.name, detail: e.message.slice(0, 500) }); throw e; } }
const started = new Date().toISOString(); let failure = null;
try {
"""
finally_code = r"""
} catch (e) { failure = { error_type: e.name, detail: e.message.slice(0, 500) }; }
finally {
  const calls = await page.evaluate(() => window.__walkthroughCalls).catch(() => ["page unavailable"]);
  const cookies = await context.cookies();
  const replies = await Promise.all(staticResponses);
  const current = await hashes();
  const mismatches = replies.filter((row) => !row.matches || row.status !== 200 || row.sets_cookie || row.body_error || !(row.path.endsWith(".html") ? /^text\/html(?:;|$)/i : row.path.endsWith(".css") ? /^text\/css(?:;|$)/i : /^(?:text|application)\/javascript(?:;|$)/i).test(row.content_type ?? ""));
  const sourcesUnchanged = JSON.stringify(before) === JSON.stringify(current);
  const observedPaths = new Set(replies.map((row) => row.path));
  const completeGraph = [...allowed].every((route) => observedPaths.has(route));
  let builtUnchanged = true;
  for (const [name, value] of Object.entries(m.assets)) if (await hash("dist/" + name) !== value) builtUnchanged = false;
  await browser.close();
  const pass = !failure && results.length === 16 && results.every((row) => row.status === "passed") && mismatches.length === 0 && blocked.length === 0 && calls.length === 0 && cookies.length === 0 && errors.length === 0 && consoleErrors.length === 0 && sourcesUnchanged && builtUnchanged && completeGraph;
  const document = {
    status: pass ? "PASS" : "FAIL", started_at: started, finished_at: new Date().toISOString(), expected_commit: m.expected_commit, origin,
    scope: "Actual anonymous hosted five-step fictional walkthrough, static-only GET graph with denied API/auth/provider/storage operations, local reset, keyboard and desktop/mobile checks. No database state observation or authenticated product acceptance.",
    composed_from_local_checker_sha256: "__ORIGINAL_SHA__",
    cookie_boundary: "Fresh anonymous context sends no credentials/cookies and traps JS cookie access. Existing user browsers can carry ambient same-origin cookies; this scope does not claim otherwise.",
    manual_limits: ["Screen reader and real assistive-device usability not executed", "Axe incompletes retained; absence of automated violations is not an accessibility certification", "Browser-internal background traffic is reduced with flags but this page routing scope is not a whole-OS packet capture", "No real nonprofit onboarding, data, provider, certification, approval, procurement or business save"],
    failure, results, accessibility_scans: scans, screenshots: shots, static_responses: replies, served_asset_mismatches: mismatches, network_requests: requests, blocked_network_attempts: blocked, ambient_calls: calls, cookie_count: cookies.length, page_errors: errors, console_errors: consoleErrors,
    sources_unchanged: sourcesUnchanged, built_bytes_unchanged: builtUnchanged, complete_static_graph_observed: completeGraph, qualified_sources: before, current_sources: current,
  };
  const text = JSON.stringify(document, null, 2) + "\n";
  // Raw proof is private0600; recognizable secret patterns block successful
  // publication and keep the attempted proof distinct for root inspection.
  const suspicious = /bearer\s+\S+|postgres(?:ql)?:\/\/[^\s]+|-----BEGIN [^-]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/i.test(text);
  if (suspicious) {
    await fs.writeFile(path.join(m.output, "walkthrough-refused-raw.private.json"), text, { flag: "wx", mode: 0o600 });
    await fs.writeFile(evidenceFile, JSON.stringify({ status: "FAIL", results: [], reason: "Recognizable secret pattern in proof; raw bytes private and not publishable" }) + "\n", { flag: "wx", mode: 0o600 });
  } else await fs.writeFile(evidenceFile, text, { flag: "wx", mode: 0o600 });
  if (!pass || suspicious) process.exitCode = 1;
}
"""
original_hash = hashlib.sha256(original.encode()).hexdigest()
target = Path(__file__).with_name("verify_walkthrough.mjs")
target.write_text((prelude + tests + finally_code).replace("__ORIGINAL_SHA__", original_hash))
print("Composed private checker; no browser or network started")
