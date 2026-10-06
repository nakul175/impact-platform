// Private root-gated hosted verifier, composed offline from reviewed workflow tests.
// No database/login/fixture runner code is included. Only static public GETs are allowed.
import { createRequire } from "node:module";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
const manifestPath = process.argv[2];
assert(
  manifestPath?.startsWith("/private/tmp/"),
  "Root-issued private manifest required",
);
const m = JSON.parse(await fs.readFile(manifestPath, "utf8"));
assert.equal(
  m.root_gate_passed,
  true,
  "Python approval/CI/static gates must pass first",
);
assert(/^[0-9a-f]{40}$/.test(m.expected_commit));
assert(/^https:\/\/[^/?#@]+$/.test(m.origin));
const repository = m.repo,
  origin = m.origin;
const require = createRequire(
  path.join(repository, "tools/browser/package.json"),
);
const { chromium } = require("playwright-core");
const sha = (bytes) => createHash("sha256").update(bytes).digest("hex");
assert.equal(
  sha(await fs.readFile(fileURLToPath(import.meta.url))),
  m.browser_source_sha256,
);
const hash = async (name) =>
  sha(await fs.readFile(path.join(repository, "apps/web", name)));
const hashes = async () =>
  Object.fromEntries(
    await Promise.all(
      Object.keys(m.sources).map(async (name) => [
        name,
        sha(await fs.readFile(path.join(repository, name))),
      ]),
    ),
  );
const before = await hashes();
assert.deepEqual(before, m.sources);
assert.equal(sha(await fs.readFile(m.build_proof)), m.build_proof_sha256);
const assets = Object.fromEntries(
  Object.entries(m.assets)
    .filter(([name]) => name.startsWith("assets/"))
    .map(([name, value]) => ["/" + name, value]),
);
for (const [name, value] of Object.entries(m.assets))
  assert.equal(await hash("dist/" + name), value);
const allowed = new Set(["/ai-walkthrough.html", ...m.tour_asset_paths]);
assert.equal(allowed.size, 5, "Exact separate tour graph expected");
for (const route of m.tour_asset_paths)
  assert(assets[route] && /\/(?:walkthrough|ai-enablement)-/.test(route));
const expectedAsset = (route) =>
  route === "/ai-walkthrough.html"
    ? m.assets["ai-walkthrough.html"]
    : assets[route];
const evidenceFile = path.join(m.output, "walkthrough-browser.json"),
  captureDir = path.join(m.output, "captures");
await fs.mkdir(captureDir, { recursive: false, mode: 0o700 });
const guidance = JSON.parse(
  await fs.readFile(
    path.join(repository, "apps/web/src/walkthrough-guidance.json"),
    "utf8",
  ),
);
const axe = await fs.readFile(require.resolve("axe-core/axe.min.js"), "utf8");
const results = [],
  errors = [],
  consoleErrors = [],
  requests = [],
  blocked = [],
  scans = [],
  shots = [],
  staticResponses = [];
const browser = await chromium.launch({
  executablePath: m.browser_executable,
  headless: true,
  args: [
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-sync",
    "--no-first-run",
    "--disable-default-apps",
  ],
  env: Object.fromEntries(
    Object.entries(process.env).filter(([key]) =>
      [
        "HOME",
        "PATH",
        "TMPDIR",
        "TEMP",
        "TMP",
        "LANG",
        "LC_ALL",
        "SYSTEMROOT",
      ].includes(key),
    ),
  ),
});
const context = await browser.newContext({
  viewport: { width: 1440, height: 1100 },
  ignoreHTTPSErrors: false,
  serviceWorkers: "block",
  acceptDownloads: false,
});
assert.deepEqual(await context.cookies(), []);
await context.addInitScript(() => {
  window.__walkthroughCalls = [];
  const deny = (name) =>
    function () {
      window.__walkthroughCalls.push(name);
      throw new Error("Public fictional walkthrough refuses " + name);
    };
  window.fetch = deny("fetch");
  window.XMLHttpRequest = deny("XMLHttpRequest");
  window.WebSocket = deny("WebSocket");
  window.EventSource = deny("EventSource");
  navigator.sendBeacon = deny("sendBeacon");
  for (const name of ["getItem", "setItem", "removeItem", "clear"])
    Storage.prototype[name] = deny("Storage." + name);
  for (const name of ["localStorage", "sessionStorage", "indexedDB"])
    Object.defineProperty(window, name, { get: deny(name) });
  Object.defineProperty(document, "cookie", {
    get: deny("cookie.read"),
    set: deny("cookie.write"),
  });
});
await context.route("**/*", async (route) => {
  const request = route.request(),
    url = new URL(request.url());
  const clean = {
    method: request.method(),
    origin: url.origin,
    path: url.pathname,
    resource: request.resourceType(),
    has_query: Boolean(url.search),
    has_authorization: "authorization" in request.headers(),
    has_cookie: "cookie" in request.headers(),
  };
  requests.push(clean);
  if (
    clean.method === "GET" &&
    url.origin === origin &&
    allowed.has(url.pathname) &&
    !url.search &&
    !url.hash &&
    !clean.has_authorization &&
    !clean.has_cookie &&
    ["document", "script", "stylesheet"].includes(clean.resource)
  )
    await route.continue();
  else {
    blocked.push(clean);
    await route.abort();
  }
});
const page = await context.newPage();
page.setDefaultTimeout(15000);
page.on("response", (r) => {
  const url = new URL(r.url());
  staticResponses.push(
    (async () => {
      let observed = null,
        body_error = null;
      try {
        const bytes = await r.body();
        assert(bytes.length <= 8 * 1024 * 1024);
        observed = sha(bytes);
      } catch (e) {
        body_error = e.name;
      }
      return {
        path: url.pathname,
        origin: url.origin,
        status: r.status(),
        sha256: observed,
        expected_sha256: expectedAsset(url.pathname) ?? null,
        matches: observed === expectedAsset(url.pathname),
        body_error,
        sets_cookie: Boolean(r.headers()["set-cookie"]),
        content_type: r.headers()["content-type"] ?? null,
        csp: r.headers()["content-security-policy"] ?? null,
      };
    })(),
  );
});
page.on("pageerror", (e) => errors.push(e.message));
page.on("console", (m) => {
  if (m.type() === "error") consoleErrors.push(m.text());
});
const btn = (name) => page.getByRole("button", { name, exact: true });
const field = (name) =>
  page.getByRole("textbox", { name: new RegExp("^" + name) });
async function open() {
  await page.goto(origin + "/ai-walkthrough.html");
  await page
    .getByRole("heading", {
      name: "A first AI pilot, with people in control",
      exact: true,
    })
    .waitFor();
}
async function practice() {
  await btn("Try a manual task").click();
  await btn("Preview the invented brief for this task").waitFor();
}
async function test(name, run) {
  try {
    await run();
    results.push({ name, status: "passed" });
  } catch (e) {
    results.push({
      name,
      status: "failed",
      error_type: e.name,
      detail: e.message.slice(0, 500),
    });
    throw e;
  }
}
const started = new Date().toISOString();
let failure = null;
try {
  await test("separate static entrypoint has a permanent fictional no-persistence boundary and strict CSP", async () => {
    const response = await page.goto(origin + "/ai-walkthrough.html");
    assert.equal(response.status(), 200);
    assert(
      response
        .headers()
        ["content-security-policy"].includes("connect-src 'none'"),
    );
    assert(
      response
        .headers()
        ["content-security-policy"].includes("frame-ancestors 'none'"),
    );
    assert.equal(Boolean(response.headers()["set-cookie"]), false);
    assert.equal(response.headers()["cache-control"], "no-store");
    assert.equal(response.headers()["x-content-type-options"], "nosniff");
    assert.equal(
      createHash("sha256")
        .update(await response.body())
        .digest("hex"),
      await hash("dist/ai-walkthrough.html"),
    );
    await page
      .getByRole("heading", {
        name: "A first AI pilot, with people in control",
        exact: true,
      })
      .waitFor();
    const boundary = page.getByRole("complementary", {
      name: "Fictional walkthrough boundary",
    });
    assert((await boundary.textContent()).includes("no persistence"));
    assert.equal(
      await page
        .getByRole("button", {
          name: /sign in|log in|save|approve|send|download/i,
        })
        .count(),
      0,
    );
    assert.equal(await page.locator('input[type="password"]').count(), 0);
  });
  await test("public lessons provide local feedback without completion or certification", async () => {
    await btn("Build team skills").click();
    const foundation = guidance.catalog.learning_paths.find(
      (p) => p.id === "foundations",
    );
    const lesson = foundation.lessons[0];
    await page.getByText("Lesson: " + lesson.title, { exact: true }).click();
    await page
      .getByRole("radio", {
        name: lesson.check.options[lesson.check.answer],
        exact: true,
      })
      .check();
    assert(
      (await page.getByRole("status").allTextContents())
        .join(" ")
        .includes("Correct."),
    );
    assert.equal(
      await page.getByRole("checkbox", { name: /Complete learning/ }).count(),
      0,
    );
  });
  await test("manual starter preview and cancellation leave a blank local worksheet", async () => {
    await practice();
    await btn("Preview the invented brief for this task").click();
    assert(
      (
        await page
          .getByText(/Temporary local example: reloading clears this worksheet/)
          .textContent()
      ).includes("cannot save an adoption plan"),
    );
    assert(
      (
        await page
          .getByRole("group", {
            name: "Invented brief starter preview",
            exact: true,
          })
          .textContent()
      ).includes(guidance.practice.templates[0].example_brief),
    );
    await btn("Keep my worksheet unchanged").click();
    assert.equal(
      await field("Your synthetic or public-text brief").inputValue(),
      "",
    );
  });
  await test("deliberate starter supplies only the invented brief and no draft or checked action", async () => {
    await btn("Preview the invented brief for this task").click();
    await btn("Use this invented brief in my worksheet").click();
    assert.equal(
      await field("Your synthetic or public-text brief").inputValue(),
      guidance.practice.templates[0].example_brief,
    );
    assert.equal(await field("Your manually written draft").inputValue(), "");
    assert.equal(await field("Human review notes").inputValue(), "");
    assert.equal(
      await page.locator('input[type="checkbox"]:checked').count(),
      0,
    );
  });
  await test("explicit starter replacement preserves manual draft and notes without auto-checks", async () => {
    await field("Your manually written draft").fill(
      "My invented draft Ω.\nSecond line.",
    );
    await field("Human review notes").fill(
      "My own question: missing registration.\n",
    );
    await page
      .getByLabel("I checked every factual claim against the supplied brief.", {
        exact: true,
      })
      .check();
    await btn("Preview the invented brief for this task").click();
    await btn("Replace only my brief and reset self-checks").click();
    assert.equal(
      await field("Your manually written draft").inputValue(),
      "My invented draft Ω.\nSecond line.",
    );
    assert.equal(
      await field("Human review notes").inputValue(),
      "My own question: missing registration.\n",
    );
    assert.equal(
      await page.locator('input[type="checkbox"]:checked').count(),
      0,
    );
  });
  await test("edited brief invalidates the starter notice and old preview confirmation", async () => {
    await btn("Preview the invented brief for this task").click();
    await field("Your synthetic or public-text brief").fill(
      "My later invented brief.",
    );
    assert.equal(
      await btn("Replace only my brief and reset self-checks").count(),
      0,
    );
    assert.equal(
      await page
        .getByRole("status")
        .filter({ hasText: "The invented brief is in your local worksheet" })
        .count(),
      0,
    );
  });
  await test("tool comparison is visibly invented with no provider links or selected winner", async () => {
    await btn("Compare invented tools").click();
    const text = await page
      .getByRole("region", { name: "Current walkthrough step" })
      .textContent();
    assert(text.includes("not entries from the real source-backed directory"));
    assert(text.includes("80 example units"));
    assert(text.includes("setup unknown"));
    assert(text.includes("no winner"));
    assert.equal(await page.locator('a[href^="https:"]').count(), 0);
  });
  await test("procurement edits are local only and cannot send or save", async () => {
    await btn("Prepare questions").click();
    await page
      .getByRole("textbox", { name: "Pilot requirements", exact: true })
      .fill("A locally edited fictional pilot brief.");
    assert.equal(
      await page
        .getByRole("textbox", { name: "Pilot requirements", exact: true })
        .inputValue(),
      "A locally edited fictional pilot brief.",
    );
    assert.equal(await page.locator("form").count(), 0);
    assert.equal(
      await page
        .getByRole("button", { name: /save|send|buy|book|approve/i })
        .count(),
      0,
    );
  });
  await test("switching walkthrough steps preserves only local worksheet edits", async () => {
    await practice();
    assert.equal(
      await field("Your manually written draft").inputValue(),
      "My invented draft Ω.\nSecond line.",
    );
    assert.equal(
      await field("Your synthetic or public-text brief").inputValue(),
      "My later invented brief.",
    );
  });
  await test("reload discards practice procurement and lesson answer state", async () => {
    await page.reload();
    await practice();
    assert.equal(
      await field("Your synthetic or public-text brief").inputValue(),
      "",
    );
    assert.equal(await field("Your manually written draft").inputValue(), "");
    assert.equal(await field("Human review notes").inputValue(), "");
    await btn("Prepare questions").click();
    assert(
      (
        await page
          .getByRole("textbox", { name: "Pilot requirements", exact: true })
          .inputValue()
      ).startsWith("Fictional example:"),
    );
    await btn("Build team skills").click();
    assert.equal(await page.locator('input[type="radio"]:checked').count(), 0);
  });
  await test("reset clears local edits and requires a fresh deliberate starter", async () => {
    await practice();
    await field("Your manually written draft").fill(
      "Discard this invented temporary draft.",
    );
    await btn("Reset this local example").click();
    await practice();
    assert.equal(await field("Your manually written draft").inputValue(), "");
  });
  await test("keyboard navigation reaches step and practice actions without submission", async () => {
    await open();
    await btn("Build team skills").focus();
    await page.keyboard.press("Enter");
    await page
      .getByRole("heading", {
        name: "Build team skills before using real data",
        exact: true,
      })
      .waitFor();
    await btn("Try an invented practice brief").focus();
    await page.keyboard.press("Enter");
    await btn("Preview the invented brief for this task").focus();
    await page.keyboard.press("Enter");
    await btn("Keep my worksheet unchanged").focus();
    await page.keyboard.press("Enter");
    assert.equal(
      await field("Your synthetic or public-text brief").inputValue(),
      "",
    );
  });
  for (const width of [1440, 390, 320])
    await test(`all public steps fit and pass automated accessibility at ${width}px`, async () => {
      await page.setViewportSize({ width, height: 1100 });
      for (const [step, label] of [
        ["start", "Choose a first use"],
        ["learning", "Build team skills"],
        ["practice", "Try a manual task"],
        ["tools", "Compare invented tools"],
        ["procurement", "Prepare questions"],
      ]) {
        await btn(label).click();
        if (step === "practice")
          await btn("Preview the invented brief for this task").waitFor();
        await page.evaluate(axe);
        const a = await page.evaluate(
          async () =>
            await window.axe.run(document, {
              runOnly: {
                type: "tag",
                values: ["wcag2a", "wcag2aa", "wcag21aa"],
              },
            }),
        );
        scans.push({
          incomplete: a.incomplete.map((v) => ({
            id: v.id,
            impact: v.impact,
            nodes: v.nodes.map((n) => n.target),
          })),
          inapplicable_count: a.inapplicable.length,
          passed_rule_count: a.passes.length,
          width,
          step,
          violations: a.violations.map((v) => ({
            id: v.id,
            impact: v.impact,
            nodes: v.nodes.map((n) => n.target),
          })),
        });
        assert.deepEqual(scans.at(-1).violations, []);
        assert(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        );
        if (step === "tools" && width < 700) {
          const scroll = page.getByRole("region", {
            name: "Tool comparison table",
            exact: true,
          });
          assert(
            await scroll.evaluate(
              (el) =>
                el.scrollWidth > el.clientWidth &&
                getComputedStyle(el).overflowX === "auto",
            ),
          );
          await scroll.focus();
          await page.keyboard.press("ArrowRight");
          await scroll.evaluate((el) => {
            el.scrollLeft = el.scrollWidth;
          });
          assert(await scroll.evaluate((el) => el.scrollLeft > 0));
        }
        const name = `walkthrough-${step}-${width}.png`;
        await page.screenshot({
          path: path.join(captureDir, name),
          fullPage: true,
        });
        shots.push(name);
      }
    });
  await test("no network API authentication provider storage cookie or fallback operation occurs", async () => {
    assert.deepEqual(blocked, []);
    assert.deepEqual(await page.evaluate(() => window.__walkthroughCalls), []);
    assert.deepEqual(await context.cookies(), []);
    assert.deepEqual(errors, []);
    assert.deepEqual(consoleErrors, []);
    assert(requests.every((r) => r.method === "GET" && r.origin === origin));
    assert.deepEqual(await hashes(), before);
    for (const reply of await Promise.all(staticResponses)) {
      assert.equal(reply.status, 200);
      assert.equal(reply.sets_cookie, false);
      assert.equal(reply.sha256, expectedAsset(reply.path));
    }
  });
} catch (e) {
  failure = { error_type: e.name, detail: e.message.slice(0, 500) };
} finally {
  const calls = await page
    .evaluate(() => window.__walkthroughCalls)
    .catch(() => ["page unavailable"]);
  const cookies = await context.cookies();
  const replies = await Promise.all(staticResponses);
  const current = await hashes();
  const mismatches = replies.filter(
    (row) =>
      !row.matches ||
      row.status !== 200 ||
      row.sets_cookie ||
      row.body_error ||
      !(
        row.path.endsWith(".html")
          ? /^text\/html(?:;|$)/i
          : row.path.endsWith(".css")
            ? /^text\/css(?:;|$)/i
            : /^(?:text|application)\/javascript(?:;|$)/i
      ).test(row.content_type ?? ""),
  );
  const sourcesUnchanged = JSON.stringify(before) === JSON.stringify(current);
  const observedPaths = new Set(replies.map((row) => row.path));
  const completeGraph = [...allowed].every((route) => observedPaths.has(route));
  let builtUnchanged = true;
  for (const [name, value] of Object.entries(m.assets))
    if ((await hash("dist/" + name)) !== value) builtUnchanged = false;
  await browser.close();
  const pass =
    !failure &&
    results.length === 16 &&
    results.every((row) => row.status === "passed") &&
    mismatches.length === 0 &&
    blocked.length === 0 &&
    calls.length === 0 &&
    cookies.length === 0 &&
    errors.length === 0 &&
    consoleErrors.length === 0 &&
    sourcesUnchanged &&
    builtUnchanged &&
    completeGraph;
  const document = {
    status: pass ? "PASS" : "FAIL",
    started_at: started,
    finished_at: new Date().toISOString(),
    expected_commit: m.expected_commit,
    origin,
    scope:
      "Actual anonymous hosted five-step fictional walkthrough, static-only GET graph with denied API/auth/provider/storage operations, local reset, keyboard and desktop/mobile checks. No database state observation or authenticated product acceptance.",
    composed_from_local_checker_sha256:
      "f5e40df0a16cd36f75ed6d6f55e224128f96aa402166698513a4272b99881ba4",
    cookie_boundary:
      "Fresh anonymous context sends no credentials/cookies and traps JS cookie access. Existing user browsers can carry ambient same-origin cookies; this scope does not claim otherwise.",
    manual_limits: [
      "Screen reader and real assistive-device usability not executed",
      "Axe incompletes retained; absence of automated violations is not an accessibility certification",
      "Browser-internal background traffic is reduced with flags but this page routing scope is not a whole-OS packet capture",
      "No real nonprofit onboarding, data, provider, certification, approval, procurement or business save",
    ],
    failure,
    results,
    accessibility_scans: scans,
    screenshots: shots,
    static_responses: replies,
    served_asset_mismatches: mismatches,
    network_requests: requests,
    blocked_network_attempts: blocked,
    ambient_calls: calls,
    cookie_count: cookies.length,
    page_errors: errors,
    console_errors: consoleErrors,
    sources_unchanged: sourcesUnchanged,
    built_bytes_unchanged: builtUnchanged,
    complete_static_graph_observed: completeGraph,
    qualified_sources: before,
    current_sources: current,
  };
  const text = JSON.stringify(document, null, 2) + "\n";
  // Raw proof is private0600; recognizable secret patterns block successful
  // publication and keep the attempted proof distinct for root inspection.
  const suspicious =
    /bearer\s+\S+|postgres(?:ql)?:\/\/[^\s]+|-----BEGIN [^-]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/i.test(
      text,
    );
  if (suspicious) {
    await fs.writeFile(
      path.join(m.output, "walkthrough-refused-raw.private.json"),
      text,
      { flag: "wx", mode: 0o600 },
    );
    await fs.writeFile(
      evidenceFile,
      JSON.stringify({
        status: "FAIL",
        results: [],
        reason:
          "Recognizable secret pattern in proof; raw bytes private and not publishable",
      }) + "\n",
      { flag: "wx", mode: 0o600 },
    );
  } else await fs.writeFile(evidenceFile, text, { flag: "wx", mode: 0o600 });
  if (!pass || suspicious) process.exitCode = 1;
}
