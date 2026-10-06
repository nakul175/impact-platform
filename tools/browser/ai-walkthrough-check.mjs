import { chromium } from "playwright-core";
import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";
import fs from "node:fs/promises";
import { pathToFileURL } from "node:url";
import path from "node:path";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
const repository = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL;
if (
  !local ||
  !process.env.IMPACT_BASE_URL ||
  process.env.IMPACT_ENVIRONMENT !== "test" ||
  process.env.IMPACT_ALLOW_FIXTURE_LOAD !== "1"
)
  throw Error(
    "Use scripts/run.py ai-walkthrough-browser on its own disposable fixture",
  );
const root = pathToFileURL(path.join(repository, "apps/web") + path.sep),
  origin = process.env.IMPACT_BASE_URL;
if (!/^http:\/\/127\.0\.0\.1:[0-9]+$/.test(origin))
  throw Error("Only authorized disposable loopback runtime");
const evidenceFile =
  process.env.IMPACT_BROWSER_EVIDENCE_FILE ||
  path.join(
    repository,
    "docs/evidence/sprint-0.35-walkthrough-browser-tests.json",
  );
const captureDir = evidenceFile.replace(/\.json$/, "-captures");
await fs.mkdir(captureDir, { recursive: true });
const require = createRequire(import.meta.url);
const names = [
  "src/AIFictionalWalkthrough.tsx",
  "src/AIFictionalWalkthroughAdapter.ts",
  "src/AILearningLesson.tsx",
  "src/AIToolComparison.tsx",
  "src/AIProcurementBrief.tsx",
  "src/AITaskPractice.tsx",
  "src/AIPracticeStarter.tsx",
  "src/AIPracticeStarterModel.ts",
  "src/walkthrough-guidance.json",
  "src/ai-walkthrough.css",
  "src/styles.css",
  "src/ai-enablement.css",
  "src/ai-planning-tools.css",
  "ai-walkthrough.html",
  "vite.config.ts",
];
const hash = async (name) =>
  createHash("sha256")
    .update(await fs.readFile(new URL(name, root)))
    .digest("hex");
const extraSources = [
  "VERSION.json",
  "apps/api/impact_api/main.py",
  "scripts/run.py",
  "tools/browser/ai-walkthrough-check.mjs",
];
const hashes = async () => ({
  ...Object.fromEntries(
    await Promise.all(
      names.map(async (name) => ["apps/web/" + name, await hash(name)]),
    ),
  ),
  ...Object.fromEntries(
    await Promise.all(
      extraSources.map(async (name) => [
        name,
        createHash("sha256")
          .update(await fs.readFile(path.join(repository, name)))
          .digest("hex"),
      ]),
    ),
  ),
});
const fixturePython = String.raw`
import os,json,psycopg
from pathlib import Path
from psycopg import sql
try:
 assert os.environ.get('IMPACT_ENVIRONMENT')=='test' and os.environ.get('IMPACT_ALLOW_FIXTURE_LOAD')=='1'
 local=Path(os.environ['IMPACT_TEST_LOCAL']).resolve(); root=Path.cwd().resolve()
 assert local.parent==root/'.local' and local.name.startswith('test-')
 dsn=os.environ.get('IMPACT_ADMIN_DSN') or os.environ['IMPACT_FIXTURE_DSN']
 with psycopg.connect(dsn) as c:
  c.execute('SET TRANSACTION READ ONLY')
  tables=[r[0] for r in c.execute("SELECT tablename FROM pg_tables WHERE schemaname='impact' ORDER BY tablename")]
  assert 1<=len(tables)<=300
  result={}
  for name in tables:
   row=c.execute(sql.SQL("SELECT count(*),md5(coalesce(string_agg(md5(to_jsonb(t)::text),'' ORDER BY md5(to_jsonb(t)::text)),'')) FROM impact.{} t").format(sql.Identifier(name))).fetchone()
   result[name]={'rows':row[0],'row_fingerprint_md5':row[1]}
  ledger=[{'version':r[0],'sha256':r[1]} for r in c.execute('SELECT version,sha256 FROM impact.schema_migration ORDER BY version')]
 print(json.dumps({'tables':result,'applied_migrations':ledger}))
except Exception as error:
 print(json.dumps({'error_type':type(error).__name__,'sqlstate':getattr(error,'sqlstate',None)}))
 raise SystemExit(1)
`;
function applicationSnapshot() {
  const result = spawnSync(
    path.join(repository, ".venv/bin/python"),
    ["-c", fixturePython],
    { cwd: repository, env: process.env, encoding: "utf8", timeout: 60000 },
  );
  if (result.status !== 0)
    throw Error(
      "Read-only disposable fixture observation refused; raw diagnostics withheld",
    );
  return JSON.parse(result.stdout);
}
const applicationBefore = applicationSnapshot();
assert.equal(applicationBefore.applied_migrations.length, 40);
for (const row of applicationBefore.applied_migrations) {
  const migration = (
    await fs.readdir(path.join(repository, "infrastructure/migrations"))
  ).filter((name) =>
    name.startsWith(String(row.version).padStart(4, "0") + "_"),
  );
  assert.equal(migration.length, 1);
  const bytes = await fs.readFile(
    path.join(repository, "infrastructure/migrations", migration[0]),
  );
  assert.equal(createHash("sha256").update(bytes).digest("hex"), row.sha256);
}
const before = await hashes(),
  results = [],
  errors = [],
  consoleErrors = [],
  requests = [],
  blocked = [],
  scans = [],
  shots = [],
  staticResponses = [];
const guidance = JSON.parse(
  await fs.readFile(new URL("src/walkthrough-guidance.json", root), "utf8"),
);
const axe = await fs.readFile(require.resolve("axe-core/axe.min.js"), "utf8");
const assets = Object.fromEntries(
  await Promise.all(
    (await fs.readdir(new URL("dist/assets/", root))).map(async (name) => [
      "/assets/" + name,
      await hash("dist/assets/" + name),
    ]),
  ),
);
const browser = await chromium.launch({
  executablePath:
    process.env.IMPACT_BROWSER_EXECUTABLE ||
    (process.platform === "darwin"
      ? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
      : path.join(repository, ".local/browser/chromium")),
  headless: true,
  args: ["--no-sandbox"],
  env: Object.fromEntries(
    Object.entries(process.env).filter(
      ([key]) => !key.startsWith("IMPACT_") && !key.startsWith("PG"),
    ),
  ),
});
const context = await browser.newContext({
  viewport: { width: 1440, height: 1100 },
});
await context.addInitScript(() => {
  window.__walkthroughCalls = [];
  const deny = (name) =>
    function () {
      window.__walkthroughCalls.push(name);
      throw new Error("Isolated fictional walkthrough refuses " + name);
    };
  window.fetch = deny("fetch");
  window.XMLHttpRequest = deny("XMLHttpRequest");
  window.WebSocket = deny("WebSocket");
  navigator.sendBeacon = deny("sendBeacon");
  for (const name of ["getItem", "setItem", "removeItem", "clear"])
    Storage.prototype[name] = deny("Storage." + name);
  Object.defineProperty(document, "cookie", {
    get: deny("cookie.read"),
    set: deny("cookie.write"),
  });
  Object.defineProperty(window, "indexedDB", { get: deny("indexedDB") });
});
await context.route("**/*", async (route) => {
  const request = route.request(),
    url = new URL(request.url());
  assert(
    !("authorization" in request.headers()),
    "Anonymous request must carry no authorization header",
  );
  assert(
    !("cookie" in request.headers()),
    "Anonymous request must carry no cookie header",
  );
  requests.push({
    method: request.method(),
    url: url.origin + url.pathname,
    resource: request.resourceType(),
  });
  if (
    request.method() === "GET" &&
    url.origin === origin &&
    (url.pathname === "/ai-walkthrough.html" || assets[url.pathname])
  )
    await route.continue();
  else {
    blocked.push({ method: request.method(), url: url.origin + url.pathname });
    await route.abort();
  }
});
const page = await context.newPage();
page.setDefaultTimeout(12000);
page.on("response", (r) => {
  const url = new URL(r.url());
  if (
    url.origin === origin &&
    (url.pathname === "/ai-walkthrough.html" || assets[url.pathname])
  )
    staticResponses.push(
      (async () => ({
        path: url.pathname,
        status: r.status(),
        sha256: createHash("sha256")
          .update(await r.body())
          .digest("hex"),
        sets_cookie: Boolean(r.headers()["set-cookie"]),
        csp: r.headers()["content-security-policy"] ?? null,
      }))(),
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
    console.log("PASS " + name);
  } catch (e) {
    results.push({ name, status: "failed", error: e.stack || String(e) });
    throw e;
  }
}
const started = new Date().toISOString();
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
    assert(
      requests.every(
        (r) => r.method === "GET" && new URL(r.url).origin === origin,
      ),
    );
    assert.deepEqual(await hashes(), before);
    for (const [route, expected] of Object.entries(assets))
      assert.equal(await hash("dist" + route), expected);
    for (const reply of await Promise.all(staticResponses)) {
      assert.equal(reply.status, 200);
      assert.equal(reply.sets_cookie, false);
      assert.equal(
        reply.sha256,
        reply.path === "/ai-walkthrough.html"
          ? await hash("dist/ai-walkthrough.html")
          : assets[reply.path],
      );
    }
  });
} finally {
  const applicationAfter = applicationSnapshot();
  const stateUnchanged =
    JSON.stringify(applicationBefore) === JSON.stringify(applicationAfter);
  const calls = await page
    .evaluate(() => window.__walkthroughCalls)
    .catch(() => ["page unavailable"]);
  await browser.close();
  await fs.writeFile(
    evidenceFile,
    JSON.stringify(
      {
        application_database_state_unchanged: stateUnchanged,
        application_database_before: applicationBefore,
        application_database_after: applicationAfter,
        fixture_observer:
          "Explicit privileged read-only synthetic fixture observation; no query-row/config/credential bytes published and no runtime-login RLS claim",
        cookie_boundary:
          "Fresh anonymous browser: no cookies or cookie reads/writes. Same-origin HTTP can carry pre-existing cookies in other sessions; code does not authenticate or use them.",
        scope:
          "Anonymous actual disposable application serving integrated fictional walkthrough static bytes; no authenticated domain action/provider/approval or nonprofit acceptance proof",
        static_responses: await Promise.all(staticResponses),
        started_at: started,
        finished_at: new Date().toISOString(),
        results,
        page_errors: errors,
        console_errors: consoleErrors,
        network_requests: requests,
        blocked_network_attempts: blocked,
        ambient_calls: calls,
        accessibility_scans: scans,
        screenshots: shots,
        qualified_sources: before,
        current_sources: await hashes(),
        sources_unchanged:
          JSON.stringify(before) === JSON.stringify(await hashes()),
        served_asset_sha256: assets,
      },
      null,
      2,
    ) + "\n",
  );
  assert(
    stateUnchanged,
    "Walkthrough changed application rows/heads/receipts/outbox/bytes",
  );
}
