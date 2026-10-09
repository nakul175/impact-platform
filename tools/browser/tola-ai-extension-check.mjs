import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";

const root = process.cwd();
const local = process.env.IMPACT_TEST_LOCAL;
const base = process.env.IMPACT_BASE_URL;
if (
  !local ||
  !base ||
  new URL(base).hostname !== "127.0.0.1" ||
  process.env.IMPACT_ENVIRONMENT !== "test" ||
  process.env.IMPACT_ALLOW_FIXTURE_LOAD !== "1"
)
  throw Error(
    "Use scripts/run.py tola-ai-extension-browser on a disposable fixture",
  );
const fixture = JSON.parse(
  await fs.readFile("specification/fixtures/api-fixture.json", "utf8"),
);
const passwords = JSON.parse(
  await fs.readFile(path.join(local, "passwords.json"), "utf8"),
);
const require = createRequire(import.meta.url);
const axeSource = await fs.readFile(
  require.resolve("axe-core/axe.min.js"),
  "utf8",
);
const evidenceFile =
  process.env.IMPACT_BROWSER_EVIDENCE_FILE ||
  path.join(root, "docs/evidence/sprint-0.33-browser-tests.json");
const browserDir = path.join(root, ".local/browser");
const browser = await chromium.launch({
  executablePath:
    process.env.IMPACT_BROWSER_EXECUTABLE || path.join(browserDir, "chromium"),
  headless: true,
  args: [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--no-zygote",
  ],
  env: {
    ...process.env,
    LD_LIBRARY_PATH: browserDir + ":" + path.join(browserDir, "lib"),
    FONTCONFIG_PATH: browserDir,
  },
});
const results = [];
const errors = [];
const consoleErrors = [];
const blockedExternalRequests = [];
const accessibilityScans = [];
const screenshots = [];
const fixtureSetup = [];
const injectedFailures = [];
const pages = [];
const requestCounts = {
  planWrites: 0,
  evidenceWrites: 0,
  adviceWrites: 0,
  advisory: 0,
};
const writeRequests = [];
const expectedNegativeRoutes = new Set();
const startedAt = new Date().toISOString();
const sourcePaths = [
  "tools/browser/tola-ai-extension-check.mjs",
  "scripts/run.py",
  "VERSION.json",
  "apps/web/src/AIHumanAdvice.tsx",
  "apps/web/src/AIImpactEvidence.tsx",
  "apps/web/src/AIAdoptionWorkspace.tsx",
  "apps/web/src/AIEnablement.tsx",
  "apps/web/src/main.tsx",
  "apps/web/src/ai-enablement.css",
  "apps/api/impact_api/human_advice.py",
  "apps/api/impact_api/human_advice_contracts.py",
  "apps/api/impact_api/ai_impact_references.py",
  "apps/api/impact_api/ai_impact_reference_contracts.py",
  "apps/api/impact_api/ai_adoption_plans.py",
  "apps/api/impact_api/main.py",
  "apps/api/impact_api/dashboards.py",
  "apps/api/impact_api/planning.py",
  "apps/api/impact_api/store.py",
  "apps/api/impact_api/service.py",
  "packages/contracts/access-policy.json",
  "packages/contracts/openapi.json",
  "packages/contracts/openapi-implemented.json",
  "apps/web/dist/index.html",
  "infrastructure/migrations/0037_ai_content_snapshots.sql",
  "infrastructure/migrations/0038_human_advice_cases.sql",
  "infrastructure/migrations/0039_human_advice_anchor_availability.sql",
  "infrastructure/migrations/0040_ai_plan_portability.sql",
  "qualification/conftest.py",
  "qualification/test_dashboards.py",
  "qualification/test_measurement.py",
  "qualification/test_ai_adoption_plans.py",
  "qualification/test_ai_adoption_plans_live.py",
  "qualification/human_advice_anchor_fixtures.py",
  "qualification/test_human_advice_anchor_availability.py",
  "qualification/prepared_human_advice_anchor_availability.py",
  "qualification/test_framework_old_pin_visibility.py",
  "qualification/prepared_retained_label_visibility_repro.py",
  "qualification/prepared_dashboard_visibility_repro.py",
  "qualification/test_dashboard_current_visibility.py",
  "qualification/test_retained_label_current_visibility.py",
  "qualification/test_human_advice_unit.py",
  "qualification/test_human_advice_live.py",
  "qualification/test_ai_impact_references.py",
  "qualification/test_ai_impact_references_live.py",
  "qualification/test_live_application.py",
  "qualification/test_listing_visibility_unit.py",
  "qualification/test_listing_visibility_live.py",
  "qualification/test_planning.py",
  "scripts/fixture_support.py",
  "specification/fixtures/api-fixture.json",
  "specification/fixtures/records.json",
];
const owningMigrationPaths = (
  await fs.readdir(path.join(root, "infrastructure/migrations"))
)
  .filter((file) => file.endsWith(".sql"))
  .sort()
  .map((file) => "infrastructure/migrations/" + file);
assert.equal(
  owningMigrationPaths.length,
  43,
  "The current registered checkpoint has exactly 43 owning migrations",
);
for (const [index, file] of owningMigrationPaths.entries()) {
  assert.match(file, /^infrastructure\/migrations\/\d{4}_[a-z0-9_]+\.sql$/);
  assert.equal(
    Number(
      file.slice(
        "infrastructure/migrations/".length,
        "infrastructure/migrations/".length + 4,
      ),
    ),
    index + 1,
    "Owning migrations are contiguous and ordered",
  );
  if (!sourcePaths.includes(file)) sourcePaths.push(file);
}
function assertCurrentMigrationLedger(
  applied,
  migrationPaths,
  sourceFingerprints,
) {
  assert.equal(
    migrationPaths.length,
    43,
    "Current owning file inventory remains exact",
  );
  assert.equal(
    applied.length,
    migrationPaths.length,
    "The actual applied ledger has the exact owning file count",
  );
  assert.deepEqual(
    applied.map((row) => row.version),
    migrationPaths.map((_, index) => index + 1),
    "Every owning migration is applied once, in order",
  );
  for (const [index, file] of migrationPaths.entries()) {
    assert.match(sourceFingerprints[file], /^[a-f0-9]{64}$/);
    assert.equal(
      applied[index].sha256,
      sourceFingerprints[file],
      "Actual applied checksum matches owning file: " + file,
    );
  }
}
async function hashes() {
  return Object.fromEntries(
    await Promise.all(
      sourcePaths.map(async (file) => [
        file,
        createHash("sha256")
          .update(await fs.readFile(path.join(root, file)))
          .digest("hex"),
      ]),
    ),
  );
}
const qualifiedSources = await hashes();
async function servedHashes() {
  const response = await fetch(base);
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.equal(
    html,
    await fs.readFile(path.join(root, "apps/web/dist/index.html"), "utf8"),
    "The running application serves this workspace's compiled entry point",
  );
  const assets = [
    ...new Set(
      [
        ...html.matchAll(
          /(?:src|href)="(\/assets\/[A-Za-z0-9._/-]+\.(?:js|css))"/g,
        ),
      ].map((match) => match[1]),
    ),
  ];
  assert(
    assets.length > 0 && assets.length <= 32,
    "Served compiled assets are bounded and present",
  );
  return Object.fromEntries(
    await Promise.all(
      assets.map(async (asset) => {
        assert(!asset.includes(".."));
        const result = await fetch(new URL(asset, base));
        assert.equal(result.status, 200);
        const bytes = Buffer.from(await result.arrayBuffer());
        assert(bytes.length <= 10 * 1024 * 1024);
        assert.deepEqual(
          bytes,
          await fs.readFile(path.join(root, "apps/web/dist", asset.slice(1))),
          "Served compiled assets match this workspace's build",
        );
        return [asset, createHash("sha256").update(bytes).digest("hex")];
      }),
    ),
  );
}
const qualifiedServedAssets = await servedHashes();
const name = "Synthetic Tola AI extension " + Date.now();
const DAY = 86400000;
const command = (data, revision) => ({
  operation_id: crypto.randomUUID(),
  ...(revision ? { expected_revision: revision } : {}),
  data,
});

function expectedConsoleEvent(record) {
  let route;
  try {
    route = new URL(record.location.url).pathname;
  } catch {
    return null;
  }
  if (route === "/auth/me" && /status of 401/.test(record.message))
    return "Anonymous session probe before synthetic sign-in";
  if (
    expectedNegativeRoutes.has(route) &&
    /status of (404|403)/.test(record.message)
  )
    return "Actual current-authority or absent-reference refusal";
  if (
    /net::ERR_(FAILED|CONNECTION_FAILED)/.test(record.message) &&
    injectedFailures.some((item) => item.route === route)
  )
    return injectedFailures.find((item) => item.route === route).scope;
  return null;
}
async function api(actor, route, body, status = 200, method) {
  assert(route.startsWith("/"));
  const response = await fetch(base + route, {
    method: method || (body ? "POST" : "GET"),
    headers: {
      Authorization: "Bearer " + process.env[fixture.actors[actor].token_env],
      "Content-Type": "application/json",
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const result = await response.json();
  assert.equal(response.status, status, JSON.stringify(result));
  return result;
}
async function test(title, run, scope = "Real UI and actual local backend") {
  await run();
  results.push({ name: title, status: "passed", scope });
  console.log("PASS " + title);
}
async function oneControlledRequest(page, url, handler) {
  let handled = false;
  const intercept = async (route) => {
    if (handled) return route.continue();
    handled = true;
    try {
      await handler(route);
    } catch (error) {
      errors.push("Controlled request failed: " + error.message);
      console.error("Controlled request failed: " + error.message);
      try {
        await route.abort("failed");
      } catch {
        // The original handler error is retained even if the request ended.
      }
    } finally {
      // Finish the intercepted request first. Removing a live handler can
      // continue the request and turn intended response loss into success.
      try {
        await page.unroute(url, intercept);
      } catch (error) {
        errors.push("Controlled request cleanup failed: " + error.message);
      }
    }
  };
  await page.route(url, intercept);
}
const button = (page, text) =>
  page.getByRole("button", { name: text, exact: true });
const label = (page, text) =>
  text === "Saved revision"
    ? page.getByRole("combobox", { name: /^Saved revision/ })
    : page.getByLabel(text, { exact: true });
async function user(actor, area) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1050 },
  });
  await context.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (
      url.origin === new URL(base).origin ||
      ["data:", "blob:"].includes(url.protocol)
    )
      await route.continue();
    else {
      blockedExternalRequests.push({
        origin: url.origin,
        method: route.request().method(),
      });
      await route.abort();
    }
  });
  const page = await context.newPage();
  pages.push(page);
  page.setDefaultTimeout(15000);
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (event) => {
    if (event.type() === "error")
      consoleErrors.push({ message: event.text(), location: event.location() });
  });
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (
      request.method() === "POST" &&
      url.pathname.endsWith("/ai-enablement/advisory")
    )
      requestCounts.advisory++;
    if (
      ["POST", "PUT"].includes(request.method()) &&
      /\/ai-enablement\/plans(?:\/[^/]+)?$/.test(url.pathname)
    )
      requestCounts.planWrites++;
    if (
      ["POST", "PUT"].includes(request.method()) &&
      url.pathname.endsWith("/impact-reference")
    )
      requestCounts.evidenceWrites++;
    if (request.method() === "POST" && url.pathname.includes("/human-advice"))
      requestCounts.adviceWrites++;
    if (
      ["POST", "PUT"].includes(request.method()) &&
      url.pathname.includes("/ai-enablement/")
    )
      writeRequests.push({
        actor,
        path: url.pathname,
        method: request.method(),
        body: request.postDataJSON(),
      });
  });
  await page.goto(base);
  await label(page, "Username").fill(actor);
  await label(page, "Password").fill(passwords[actor]);
  await button(page, "Sign in →").click();
  if (area !== "Tenant lifecycle")
    await label(page, "Workspace").selectOption(fixture.tenant_a);
  await button(page, area).click();
  if (area === "Tenant lifecycle") {
    await button(page, "Extend organisation access").click();
    await page
      .getByRole("heading", { name: "Extend organisation access", exact: true })
      .waitFor();
  } else {
    await page
      .getByRole("heading", { name: "Your AI adoption plan", exact: true })
      .waitFor();
    await label(page, "Saved adoption plans").waitFor();
  }
  return page;
}
async function openPlan(page, id) {
  await label(page, "Saved adoption plans").selectOption(id);
  const pending = page.waitForResponse(
    (r) =>
      r.request().method() === "GET" &&
      new URL(r.url()).pathname.endsWith("/ai-enablement/plans/" + id),
  );
  await button(page, "Open saved plan").click();
  assert((await pending).ok());
  await button(page, "View saved guidance").waitFor();
}
async function scan(page, name, selector) {
  await page.evaluate(axeSource);
  const result = await page.evaluate(
    async (selector) =>
      window.axe.run(
        { include: [[selector]] },
        {
          runOnly: {
            type: "tag",
            values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"],
          },
          resultTypes: ["violations", "incomplete"],
        },
      ),
    selector,
  );
  const shape = (item) => ({
    id: item.id,
    impact: item.impact,
    help: item.help,
    nodes: item.nodes.map((node) => ({
      target: node.target,
      summary: node.failureSummary,
    })),
  });
  accessibilityScans.push({
    name,
    violations: result.violations.map(shape),
    incomplete: result.incomplete.map(shape),
  });
  assert.deepEqual(
    result.violations.map(shape),
    [],
    "Automated WCAG violations",
  );
  assert.deepEqual(
    result.incomplete.map(shape),
    [],
    "Accessibility findings need manual review",
  );
}
async function mobile(page, width, name, selector) {
  await page.setViewportSize({ width, height: 900 });
  assert(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth + 1,
    ),
    "Screen expands the mobile viewport",
  );
  const escaping = await page
    .locator(
      selector +
        " input, " +
        selector +
        " select, " +
        selector +
        " textarea, " +
        selector +
        " button",
    )
    .evaluateAll((controls) =>
      controls
        .filter((control) => {
          const bounds = control.getBoundingClientRect();
          return (
            bounds.width > 0 &&
            (bounds.left < -1 || bounds.right > innerWidth + 1)
          );
        })
        .map((control) => control.outerHTML),
    );
  assert.deepEqual(escaping, [], "Mobile controls escape the viewport");
  await scan(page, `${name} ${width}px`, selector);
  const focus = page.locator(selector).first();
  await focus.evaluate((element) => element.scrollIntoView({ block: "start" }));
  const file = path.join(local, `tola-ai-extension-${name}-${width}.png`);
  await page.screenshot({ path: file, fullPage: false });
  screenshots.push({
    name: `${name} ${width}px`,
    file,
    synthetic: true,
    realProduct: true,
  });
  await page.setViewportSize({ width: 1440, height: 1050 });
}

// Reuse the real qualification helpers: measurement, review, calculation, close
// and plan creation all go through application routes with distinct fixture actors.
// Grant narrowing is explicit disposable-fixture maintenance, never a product route.
const fixturePython = String.raw`
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'qualification'))
from conftest import live
from test_dashboards import measure, ratio_source, calculate, target, close
from test_measurement import get
from test_ai_adoption_plans import plan
from test_ai_adoption_plans_live import save
assert os.environ.get('IMPACT_ENVIRONMENT') == 'test'
assert os.environ.get('IMPACT_ALLOW_FIXTURE_LOAD') == '1'
args = json.load(sys.stdin)
generator = live.__wrapped__()
client = next(generator)
try:
    operation = args['operation']
    if operation == 'runtime-schema':
        with client.db() as c:
            answer = {'applied_migrations':c.execute('SELECT version,sha256 FROM impact.schema_migration ORDER BY version').fetchall()}
    elif operation == 'prepare':
        programme, indicator, period, keys = measure(client, keys=2)
        ratio_source(client, indicator, keys[0], '50', '100')
        ratio_source(client, indicator, keys[1], '1', '10')
        calculate(client, indicator, period)
        target(client, indicator, period, '50')
        data = plan()
        data['title'] = args['title']
        receipt = save(client, data)
        answer = {'programme':get(client,'programmes',programme['object_id']),
          'indicator':get(client,'indicator-instances',indicator['object_id']),
          'period':get(client,'periods',period['object_id']), 'plan':receipt}
    elif operation == 'close':
        close(client, get(client,'programmes',args['programme_id']),
          get(client,'periods',args['period_id']))
        answer = {'actual_application_workflow':'independent reviewed programme period close'}
    elif operation in ('narrow','restore'):
        tenant = client.fixture['tenant_a']
        with client.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)",(tenant,))
            if operation == 'narrow':
                principal = client.fixture['actors'][args['actor']]['principal_id']
                rows = c.execute('SELECT object_id,purpose FROM impact.grant_current WHERE tenant_id=%s '
                  'AND subject_id=%s AND capability=%s AND purpose IS NULL',
                  (tenant,principal,args['capability'])).fetchall()
                assert rows, 'Synthetic actor must actually hold the narrowed capability'
                c.execute("UPDATE impact.grant_current SET purpose='SYNTHETIC_BROWSER_NARROWED' WHERE tenant_id=%s "
                  'AND object_id=ANY(%s::uuid[])',(tenant,[str(r['object_id']) for r in rows]))
                answer = {'grants':[{'object_id':str(r['object_id']),'purpose':r['purpose']} for r in rows]}
            else:
                for row in args['grants']:
                    c.execute('UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s',
                      (row['purpose'],tenant,row['object_id']))
                answer = {'restored_grants':len(args['grants'])}
    elif operation == 'core-state':
        tenant = client.fixture['tenant_a']
        with client.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)",(tenant,))
            answer = {'core_heads':c.execute("SELECT object_id,head_revision FROM impact.object_registry WHERE tenant_id=%s "
              "AND object_type NOT IN ('AIAdoptionPlan','HumanAdviceCase','AuditEvent') ORDER BY object_id",(tenant,)).fetchall(),
              'snapshot_bindings':c.execute('SELECT snapshot_id,snapshot_revision,snapshot_version FROM impact.period_snapshot_binding '
                'WHERE tenant_id=%s ORDER BY snapshot_id',(tenant,)).fetchall(),
              'official_results':c.execute('SELECT snapshot_id,indicator_id,result_revision FROM impact.official_result_snapshot '
                'WHERE tenant_id=%s ORDER BY snapshot_id,indicator_id',(tenant,)).fetchall()}
    else:
        raise ValueError('Unknown synthetic fixture operation')
    print(json.dumps(answer,default=str))
finally:
    generator.close()
`;
function setup(operation, data = {}) {
  const result = spawnSync(
    path.join(root, ".venv/bin/python"),
    ["-c", fixturePython],
    {
      cwd: root,
      env: process.env,
      input: JSON.stringify({ operation, ...data }),
      encoding: "utf8",
      timeout: 60000,
    },
  );
  assert.equal(
    result.status,
    0,
    result.stderr || "Synthetic qualification setup failed",
  );
  fixtureSetup.push({
    operation,
    scope:
      operation === "narrow" || operation === "restore"
        ? "Explicit synthetic current-grant narrowing/restoration; immutable triggers and RLS retained"
        : operation === "runtime-schema" || operation === "core-state"
          ? "Read-only applied schema/core-state observation from the disposable qualification database"
          : "Actual local application API workflow using existing qualification helpers",
  });
  return JSON.parse(result.stdout);
}

const tenantPath = `/v1/tenants/${fixture.tenant_a}/`;
const planPath = (id) => tenantPath + "ai-enablement/plans/" + id;
const evidencePath = (id) => planPath(id) + "/impact-reference";
const advicePath = (id = "") =>
  tenantPath + "ai-enablement/human-advice" + (id ? "/" + id : "");
const evidencePanel = (page) => page.locator(".ai-impact-evidence");
const advicePanel = (page) => page.locator(".ai-human-advice");
async function reopen(page, planId) {
  await openPlan(page, planId);
}
async function chooseEvidence(page, records) {
  await button(page, "Choose programme evidence").click();
  await label(page, "Evidence programme").selectOption(
    records.programme.object_id,
  );
  await label(page, "Evidence reporting period").selectOption(
    records.period.object_id,
  );
  await label(page, "Evidence indicator").selectOption(
    records.indicator.object_id,
  );
  await label(page, "Evidence interpretation note").fill(
    "Synthetic governed evidence for human review; no causal attribution to AI.",
  );
}
async function selectedCase(page, title, state) {
  await button(page, `${title} · ${state}`).click();
  await advicePanel(page)
    .getByRole("region", { name: "Selected internal advice case", exact: true })
    .waitFor();
}
async function actionForm(page, title) {
  await button(page, title).click();
  return advicePanel(page).getByRole("form", { name: title, exact: true });
}
async function invitation(page, title) {
  await button(
    page,
    "Choose an internal peer and prepare an invitation",
  ).click();
  await label(page, "Advice internal peer").selectOption(
    fixture.actors.reviewer.membership_id,
  );
  await label(page, "Advice case title").fill(title);
  await label(page, "Advice invitation scope").fill(
    "Review a synthetic AI pilot scope and human acceptance examples.",
  );
  await label(page, "Advice material boundary").fill(
    "Synthetic or public text only; no participant data, credentials or documents.",
  );
  await label(page, "Advice desired outcome").fill(
    "A bounded recommendation with accountable human actions.",
  );
  await label(page, "Advice private problem brief").fill(
    "Synthetic private problem for internal member advice; withheld before requester sharing.",
  );
  await page.getByLabel(/I consent to show the invitation fields/).check();
}

let activePage;
let prepared;
let requester;
let evidenceReader;
let adviser;
let caseId;
let narrowed;
let runtimeQualification;
const adviceTitle = name + " internal member case";
try {
  await test("Actual runtime and all 43 owning migration checks match frozen source", async () => {
    const manifest = await api("admin", "/v1/runtime-manifest");
    assert.equal(manifest.environment, "test");
    assert.equal(manifest.schema_version, String(owningMigrationPaths.length));
    assert.equal(manifest.mutation_tests_allowed, true);
    const version = JSON.parse(
      await fs.readFile(path.join(root, "VERSION.json"), "utf8"),
    );
    assert.equal(manifest.build_id, "impact-" + version.build);
    assert.equal(manifest.api_version, version.domain_api);
    const applied = setup("runtime-schema").applied_migrations;
    assertCurrentMigrationLedger(
      applied,
      owningMigrationPaths,
      qualifiedSources,
    );
    assert.equal(applied.at(-1).version, owningMigrationPaths.length);
    for (const number of [37, 38, 39]) {
      const file = sourcePaths.find((name) =>
        name.startsWith(
          "infrastructure/migrations/" + String(number).padStart(4, "0") + "_",
        ),
      );
      assert.equal(
        applied.find((row) => row.version === number)?.sha256,
        qualifiedSources[file],
      );
    }
    runtimeQualification = {
      environment: manifest.environment,
      build_id: manifest.build_id,
      schema_version: manifest.schema_version,
      api_version: manifest.api_version,
      mutation_tests_allowed: manifest.mutation_tests_allowed,
      applied_migrations: applied,
      owning_migration_count: owningMigrationPaths.length,
      owning_migration_files: owningMigrationPaths,
    };
  });
  prepared = setup("prepare", { title: name });
  const id = prepared.plan.object_id;
  expectedNegativeRoutes.add(evidencePath(id) + "/result");
  requester = await user("author", "AI enablement");
  evidenceReader = requester;
  activePage = requester;
  await test("Unopened plan panels stay lazy and saved-plan reads expose no private core reference", async () => {
    assert.equal(await button(requester, "View programme evidence").count(), 0);
    assert.equal(
      await button(requester, "View internal peer advice").count(),
      0,
    );
    const current = await api("author", planPath(id));
    assert(!("impact_reference" in current.data));
    for (const hidden of [
      prepared.programme.object_id,
      prepared.indicator.object_id,
      prepared.period.object_id,
    ])
      assert(!JSON.stringify(current).includes(hidden));
    await reopen(requester, id);
    assert.equal(requestCounts.evidenceWrites, 0);
    assert.equal(requestCounts.adviceWrites, 0);
  });
  await test("Actual absent reference returns the neutral evidence view without saving", async () => {
    await button(requester, "View programme evidence").click();
    await evidencePanel(requester)
      .getByRole("alert")
      .filter({ hasText: "No programme evidence is available to show." })
      .waitFor();
    const missing = await api(
      "author",
      evidencePath(id) + "/result",
      undefined,
      404,
    );
    assert.equal(missing.code, "RESOURCE_UNAVAILABLE");
    assert.equal(requestCounts.evidenceWrites, 0);
  });
  await test("Authorized bounded measurement selection never saves before deliberate confirmation", async () => {
    await chooseEvidence(requester, prepared);
    assert.equal(requestCounts.evidenceWrites, 0);
    const title = await label(requester, "Plan name").inputValue();
    await label(requester, "Plan name").fill(title + " local edit");
    assert(
      await button(requester, "Confirm programme evidence link").isDisabled(),
    );
    await label(requester, "Plan name").fill(title);
  });
  await test("A deliberate relationship creates a plan revision without changing governed source heads", async () => {
    const before = setup("core-state");
    await button(requester, "Confirm programme evidence link").click();
    await evidencePanel(requester)
      .getByRole("heading", {
        name: prepared.programme.data.title,
        exact: true,
      })
      .waitFor();
    const linked = await api("author", evidencePath(id) + "/result");
    assert.equal(linked.reference.snapshot_id, null);
    assert.equal(linked.indicator.official, null);
    assert.equal(linked.indicator.provisional.displayed_value, "46.36");
    assert.deepEqual(setup("core-state"), before);
    assert.equal(requestCounts.evidenceWrites, 1);
  });
  await test("A later reviewed period close cannot silently add official evidence to an absent snapshot pin", async () => {
    setup("close", {
      programme_id: prepared.programme.object_id,
      period_id: prepared.period.object_id,
    });
    await button(requester, "Check evidence again").click();
    await evidencePanel(requester)
      .getByText(
        "No locked snapshot was pinned. A later close does not add an official value to this link automatically.",
      )
      .waitFor();
    const current = await api("author", evidencePath(id) + "/result");
    assert.equal(current.indicator.official, null);
    assert.equal(current.reference.snapshot_id, null);
    assert.equal(requestCounts.evidenceWrites, 1);
  });
  await test("Only an explicit saved-pin refresh displays the governed official snapshot", async () => {
    const before = setup("core-state");
    await button(requester, "Review refresh of saved pins").click();
    assert.equal(requestCounts.evidenceWrites, 1);
    await button(requester, "Confirm evidence refresh").click();
    await evidencePanel(requester)
      .getByText("Snapshot edition 1.", { exact: true })
      .waitFor();
    const current = await api("author", evidencePath(id) + "/result");
    assert.equal(current.indicator.official.displayed_value, "46.36");
    assert.equal(current.indicator.provisional, null);
    assert.equal(current.indicator.target.displayed_value, "50.00");
    assert.equal(current.indicator.coverage.approved_count, 2);
    assert.deepEqual(setup("core-state"), before);
    assert(
      (await evidencePanel(requester).innerText()).includes(
        "do not establish that AI caused",
      ),
    );
  });
  await test("Lost actual evidence response retries the exact operation and reopens a newer canonical plan", async () => {
    const beforeHistory = await api(
      "author",
      planPath(id) + "/revisions?limit=100",
    );
    assert.equal(beforeHistory.next_cursor, null);
    const route = base + evidencePath(id);
    await oneControlledRequest(requester, route, async (interception) => {
      const response = await interception.fetch();
      assert.equal(response.status(), 200);
      const receipt = await response.json();
      const current = await api("author", planPath(id));
      const data = structuredClone(current.data);
      delete data.content_versions;
      const later = await api(
        "admin",
        planPath(id),
        command(
          { ...data, title: name + " later canonical revision" },
          receipt.revision_id,
        ),
        200,
        "PUT",
      );
      prepared.later_revision = later.revision_id;
      injectedFailures.push({
        route: evidencePath(id),
        scope:
          "Actual backend committed the evidence command; response deliberately aborted after a later actual plan edit",
      });
      await interception.abort("failed");
    });
    await button(requester, "Review refresh of saved pins").click();
    await button(requester, "Confirm evidence refresh").click();
    await button(requester, "Retry previous evidence change").waitFor();
    assert(await button(requester, "Save plan changes").isDisabled());
    assert(await button(requester, "Open saved plan").isDisabled());
    await label(requester, "Plan name").fill(
      name + " local draft survives actual retry",
    );
    await button(requester, "Retry previous evidence change").click();
    await requester
      .getByText(
        "Evidence relationship saved. The current plan revision was checked; your local draft edits remain unsaved.",
      )
      .waitFor();
    assert.equal(
      await label(requester, "Plan name").inputValue(),
      name + " local draft survives actual retry",
    );
    const requests = writeRequests.filter((r) => r.path === evidencePath(id));
    assert.deepEqual(requests.at(-1).body, requests.at(-2).body);
    await button(requester, "Save plan changes").click();
    await requester
      .getByText("Plan saved. Any edits made while saving remain unsaved.")
      .waitFor();
    const ordinary = writeRequests
      .filter((r) => r.path === planPath(id))
      .at(-1);
    assert.equal(ordinary.body.expected_revision, prepared.later_revision);
    assert.equal(
      (await api("author", planPath(id))).data.title,
      name + " local draft survives actual retry",
    );
    const afterHistory = await api(
      "author",
      planPath(id) + "/revisions?limit=100",
    );
    assert.equal(afterHistory.next_cursor, null);
    assert.equal(
      afterHistory.items.length,
      beforeHistory.items.length + 3,
      "One evidence command, one independent canonical edit and one ordinary plan save; replay adds no revision",
    );
  });
  await test("Current source authority loss clears prior labels and values; missing and hidden results remain opaque", async () => {
    narrowed = setup("narrow", {
      actor: "author",
      capability: "programmes.read",
    });
    await button(requester, "Check evidence again").click();
    await evidencePanel(requester)
      .getByRole("alert")
      .filter({ hasText: "No programme evidence is available to show." })
      .waitFor();
    assert.equal(
      await evidencePanel(requester)
        .getByText(prepared.programme.data.title, { exact: true })
        .count(),
      0,
    );
    assert.equal(
      await evidencePanel(requester)
        .getByText("46.36", { exact: true })
        .count(),
      0,
    );
    const hidden = await api(
      "author",
      evidencePath(id) + "/result",
      undefined,
      404,
    );
    await button(requester, "Review clearing of evidence relationship").click();
    await button(requester, "Confirm link removal").click();
    await requester
      .getByText(
        "Evidence relationship saved. The current plan revision has been reopened.",
      )
      .waitFor();
    const absent = await api(
      "author",
      evidencePath(id) + "/result",
      undefined,
      404,
    );
    assert.equal(hidden.code, absent.code);
    assert.equal(hidden.message, absent.message);
    setup("restore", narrowed);
    narrowed = null;
  });
  await chooseEvidence(requester, prepared);
  await button(requester, "Confirm programme evidence link").click();
  await evidencePanel(requester)
    .getByText("Snapshot edition 1.", { exact: true })
    .waitFor();
  for (const width of [1440, 390, 320])
    await test(`Actual evidence keyboard/mobile/accessibility ${width}px`, async () => {
      await mobile(requester, width, "evidence", ".ai-impact-evidence");
      await button(requester, "Check evidence again").focus();
      assert(
        await button(requester, "Check evidence again").evaluate(
          (e) => e === document.activeElement,
        ),
      );
    });
  await test("Eligible internal-member selection uses the separately authorized minimal bounded lookup", async () => {
    requester = await user("admin", "AI enablement");
    activePage = requester;
    await reopen(requester, id);
    // Directory/AI authority does not imply programme authority: the actual
    // tenant administrator sees the same opaque evidence-unavailable result.
    await button(requester, "View programme evidence").click();
    await evidencePanel(requester)
      .getByRole("alert")
      .filter({ hasText: "No programme evidence is available to show." })
      .waitFor();
    await button(requester, "View internal peer advice").click();
    await invitation(requester, adviceTitle);
    assert.equal(requestCounts.adviceWrites, 0);
    const peers = await api(
      "admin",
      advicePath() + "/eligible-peers?context_plan_id=" + id + "&limit=50",
    );
    assert(
      peers.items.some(
        (p) => p.membership_id === fixture.actors.reviewer.membership_id,
      ),
    );
    assert(
      peers.items.every(
        (p) => Object.keys(p).sort().join(",") === "display_name,membership_id",
      ),
    );
    const count = requestCounts.adviceWrites;
    for (const width of [1440, 390, 320])
      await mobile(requester, width, "advice-invitation", ".ai-human-advice");
    assert.equal(requestCounts.adviceWrites, count);
  });
  await test("Lost actual invitation response repeats one exact command and preserves parent draft edits", async () => {
    const route = base + advicePath();
    await oneControlledRequest(requester, route, async (interception) => {
      const response = await interception.fetch();
      assert.equal(response.status(), 201);
      const receipt = await response.json();
      caseId = receipt.object_id;
      injectedFailures.push({
        route: advicePath(),
        scope:
          "Actual backend created the invitation; only its response was deliberately aborted",
      });
      await interception.abort("failed");
    });
    await button(requester, "Create internal advice invitation").click();
    await button(requester, "Retry previous advice change").waitFor();
    assert(await button(requester, "Save plan changes").isDisabled());
    assert(await button(requester, "Choose programme evidence").isDisabled());
    const title = await label(requester, "Plan name").inputValue();
    await label(requester, "Plan name").fill(title + " remains a local draft");
    await button(requester, "Retry previous advice change").click();
    await advicePanel(requester)
      .getByRole("heading", { name: adviceTitle, exact: true })
      .waitFor();
    const requests = writeRequests.filter((r) => r.path === advicePath());
    assert.equal(requests.length, 2);
    assert.deepEqual(requests[0].body, requests[1].body);
    assert.equal(
      await label(requester, "Plan name").inputValue(),
      title + " remains a local draft",
    );
    await label(requester, "Plan name").fill(title);
    const current = await api("admin", advicePath(caseId));
    const history = await api(
      "admin",
      advicePath(caseId) + "/revisions?limit=50",
    );
    assert.equal(
      history.items.length,
      1,
      "Invitation replay must not append another case revision",
    );
    const listed = await api("admin", advicePath() + "?limit=50");
    assert.equal(
      listed.items.filter((row) => row.object_id === caseId).length,
      1,
    );
    assert.equal(current.data.context_plan_id, id);
    assert.equal(
      current.data.context_plan_revision,
      (await api("admin", planPath(id))).revision_id,
    );
  });
  adviser = await user("reviewer", "AI enablement");
  activePage = adviser;
  await reopen(adviser, id);
  await button(adviser, "View internal peer advice").click();
  await test("An invited ordinary member discovers the case while Open private material and directory remain unavailable", async () => {
    await selectedCase(adviser, adviceTitle, "Open");
    assert(
      await button(
        adviser,
        "Choose an internal peer and prepare an invitation",
      ).isDisabled(),
    );
    assert.equal(
      await advicePanel(adviser)
        .getByText(
          "Synthetic private problem for internal member advice; withheld before requester sharing.",
          { exact: true },
        )
        .count(),
      0,
    );
    await advicePanel(adviser)
      .getByText(
        "The private problem brief is withheld until the requester confirms assignment and sharing.",
      )
      .waitFor();
    const invite = await api("reviewer", advicePath(caseId));
    assert.equal(invite.problem, null);
    expectedNegativeRoutes.add(advicePath() + "/eligible-peers");
    await api(
      "reviewer",
      advicePath() + "/eligible-peers?context_plan_id=" + id + "&limit=50",
      undefined,
      404,
    );
  });
  await test("A declared conflict prevents sharing until the current member accepts scope with no conflict", async () => {
    let form = await actionForm(adviser, "Declare conflict and scope");
    await label(adviser, "Advice conflict declaration").selectOption(
      "DECLARED",
    );
    assert(
      await adviser
        .getByLabel("I accept the invitation scope and material boundary.")
        .isDisabled(),
    );
    await label(adviser, "Advice declare-scope text").fill(
      "Synthetic declared conflict within this scope",
    );
    await form
      .getByRole("button", { name: "Declare conflict and scope", exact: true })
      .click();
    await advicePanel(adviser)
      .getByText("Conflict: Conflict declared. Scope not accepted.")
      .waitFor();
    await button(requester, "Reload currently authorised advice cases").click();
    await selectedCase(requester, adviceTitle, "Open");
    assert.equal(
      await button(requester, "Confirm assignment and private sharing").count(),
      0,
    );
    form = await actionForm(adviser, "Declare conflict and scope");
    await label(adviser, "Advice conflict declaration").selectOption("NONE");
    await adviser
      .getByLabel("I accept the invitation scope and material boundary.")
      .check();
    await label(adviser, "Advice declare-scope text").fill(
      "Synthetic no conflict after reviewing current invitation scope",
    );
    await form
      .getByRole("button", { name: "Declare conflict and scope", exact: true })
      .click();
    await advicePanel(adviser)
      .getByText("Conflict: No conflict declared. Scope accepted.")
      .waitFor();
  });
  activePage = requester;
  await test("Requester assignment is deliberate, pins the exact declaration and enables private sharing", async () => {
    await button(requester, "Reload currently authorised advice cases").click();
    await selectedCase(requester, adviceTitle, "Open");
    const declaration = await api("admin", advicePath(caseId));
    const form = await actionForm(
      requester,
      "Confirm assignment and private sharing",
    );
    assert(
      await form
        .getByRole("button", {
          name: "Confirm assignment and private sharing",
          exact: true,
        })
        .isDisabled(),
    );
    await requester
      .getByLabel(/I confirm the current scope and declaration/)
      .check();
    await form
      .getByRole("button", {
        name: "Confirm assignment and private sharing",
        exact: true,
      })
      .click();
    await advicePanel(requester).getByText("Case state: Assigned.").waitFor();
    const body = writeRequests
      .filter((r) => r.path.endsWith("/actions/assign"))
      .at(-1).body;
    assert.equal(body.data.declaration_revision_id, declaration.revision_id);
    assert.equal(body.data.sharing_confirmed, true);
    const item = await api("reviewer", advicePath(caseId));
    assert.equal(
      item.problem,
      "Synthetic private problem for internal member advice; withheld before requester sharing.",
    );
  });
  activePage = adviser;
  await test("Current participant authority failure removes previously shared private material", async () => {
    await button(adviser, "Reload currently authorised advice cases").click();
    await selectedCase(adviser, adviceTitle, "Assigned");
    await advicePanel(adviser)
      .getByText(
        "Synthetic private problem for internal member advice; withheld before requester sharing.",
        { exact: true },
      )
      .waitFor();
    narrowed = setup("narrow", {
      actor: "reviewer",
      capability: "ai.enablement.read",
    });
    expectedNegativeRoutes.add(advicePath());
    await button(adviser, "Reload currently authorised advice cases").click();
    await advicePanel(adviser)
      .getByRole("alert")
      .filter({
        hasText:
          "This advice information is unavailable with your current access.",
      })
      .waitFor();
    assert.equal(
      await advicePanel(adviser)
        .getByText(
          "Synthetic private problem for internal member advice; withheld before requester sharing.",
          { exact: true },
        )
        .count(),
      0,
    );
    assert.equal(
      await advicePanel(adviser)
        .getByRole("region", {
          name: "Selected internal advice case",
          exact: true,
        })
        .count(),
      0,
    );
    setup("restore", narrowed);
    narrowed = null;
    await button(adviser, "Reload currently authorised advice cases").click();
    await selectedCase(adviser, adviceTitle, "Assigned");
  });
  await test("Human advice records distinct accountable actions without provider calls", async () => {
    const form = await actionForm(
      adviser,
      "Record advice and accountable actions",
    );
    await label(adviser, "Advice advise text").fill(
      "Use only synthetic examples, verify every source and retain a person as the accountable reviewer.",
    );
    await button(adviser, "Add follow-up action").click();
    await label(adviser, "Advice action 1 description").fill(
      "Prepare synthetic acceptance examples and verify each claim.",
    );
    await button(adviser, "Add follow-up action").click();
    await label(adviser, "Advice action 2 description").fill(
      "Review trial findings with the requester.",
    );
    await label(adviser, "Advice action 2 responsibility").selectOption(
      "ADVISER",
    );
    await form
      .getByRole("button", {
        name: "Record advice and accountable actions",
        exact: true,
      })
      .click();
    await advicePanel(adviser).getByText("Case state: AdviceDraft.").waitFor();
    const body = writeRequests
      .filter((r) => r.path.endsWith("/actions/advise"))
      .at(-1).body;
    assert(body.data.actions.every((a) => !("action_id" in a)));
    assert.equal(requestCounts.advisory, 0);
  });
  activePage = requester;
  await test("Historical case reads keep the current parent draft unchanged and never submit a command", async () => {
    await button(requester, "Reload currently authorised advice cases").click();
    await selectedCase(requester, adviceTitle, "AdviceDraft");
    const title = await label(requester, "Plan name").inputValue();
    await label(requester, "Plan name").fill(
      title + " historical viewing local draft",
    );
    const count = writeRequests.length;
    await button(requester, "View case revision history").click();
    await requester.getByRole("button", { name: /Case revision 1 ·/ }).click();
    await advicePanel(requester)
      .getByText(
        "You are reading a saved historical revision. Case actions require the current revision.",
      )
      .waitFor();
    assert.equal(
      await button(requester, "Acknowledge advice and close").count(),
      0,
    );
    assert.equal(writeRequests.length, count);
    assert.equal(
      await label(requester, "Plan name").inputValue(),
      title + " historical viewing local draft",
    );
    await button(requester, "Return to current case revision").click();
    await label(requester, "Plan name").fill(title);
  });
  await test("Requester closure pins exact saved advice and every server-issued action before ending adviser access", async () => {
    const item = await api("admin", advicePath(caseId));
    const form = await actionForm(requester, "Acknowledge advice and close");
    await requester
      .getByLabel(
        "I acknowledge the advice in the current saved case revision.",
      )
      .check();
    await label(requester, "Advice close text").fill(
      "Synthetic requester reviewed the exact saved recommendation and all accountable actions.",
    );
    assert(
      await form
        .getByRole("button", {
          name: "Acknowledge advice and close",
          exact: true,
        })
        .isDisabled(),
    );
    await requester.getByLabel(/Acknowledge requester action:/).check();
    assert(
      await form
        .getByRole("button", {
          name: "Acknowledge advice and close",
          exact: true,
        })
        .isDisabled(),
    );
    await requester.getByLabel(/Acknowledge adviser action:/).check();
    await form
      .getByRole("button", {
        name: "Acknowledge advice and close",
        exact: true,
      })
      .click();
    await advicePanel(requester).getByText("Case state: Closed.").waitFor();
    const body = writeRequests
      .filter((r) => r.path.endsWith("/actions/close"))
      .at(-1).body;
    assert.equal(body.expected_revision, item.revision_id);
    assert.equal(body.data.advice_revision_id, item.revision_id);
    assert.deepEqual(
      body.data.acknowledged_action_ids.sort(),
      item.data.advice.actions.map((a) => a.action_id).sort(),
    );
    expectedNegativeRoutes.add(advicePath(caseId));
    await api("reviewer", advicePath(caseId), undefined, 404);
    await api("reviewer", advicePath(caseId) + "/revisions", undefined, 404);
    await button(adviser, "Reload currently authorised advice cases").click();
    await adviser.waitForFunction(
      (title) =>
        ![...document.querySelectorAll(".ai-human-advice button")].some(
          (b) => b.textContent === title + " · Closed",
        ),
      adviceTitle,
    );
    assert.equal(
      await advicePanel(adviser)
        .getByText(
          "Synthetic private problem for internal member advice; withheld before requester sharing.",
          { exact: true },
        )
        .count(),
      0,
    );
  });
  for (const width of [1440, 390, 320])
    await test(`Actual member advice keyboard/mobile/accessibility ${width}px`, async () => {
      await mobile(requester, width, "advice-closed", ".ai-human-advice");
      await button(requester, "View case revision history").focus();
      assert(
        await button(requester, "View case revision history").evaluate(
          (e) => e === document.activeElement,
        ),
      );
    });
  await test("Nonparticipants cannot recover case content through generic AI reads or case history", async () => {
    await api("author", advicePath(caseId), undefined, 404);
    await api("author", advicePath(caseId) + "/revisions", undefined, 404);
    const current = await api("author", planPath(id));
    assert(!JSON.stringify(current).includes(caseId));
    assert(
      !JSON.stringify(current).includes(
        "Synthetic private problem for internal member advice",
      ),
    );
  });
  await test("A failed evidence read clears prior values and an explicit retry reads the actual backend", async () => {
    activePage = evidenceReader;
    const openEvidence = button(evidenceReader, "View programme evidence");
    if (await openEvidence.count()) await openEvidence.click();
    else await button(evidenceReader, "Check evidence again").click();
    await evidencePanel(evidenceReader)
      .getByText("Snapshot edition 1.", { exact: true })
      .waitFor();
    const route = base + evidencePath(id) + "/result";
    await oneControlledRequest(evidenceReader, route, async (interception) => {
      injectedFailures.push({
        route: evidencePath(id) + "/result",
        scope:
          "One evidence GET was deliberately aborted before reaching the application; retry reads the actual backend",
      });
      await interception.abort("failed");
    });
    await button(evidenceReader, "Check evidence again").click();
    await evidencePanel(evidenceReader).getByRole("alert").waitFor();
    assert.equal(
      await evidencePanel(evidenceReader)
        .getByText(prepared.programme.data.title, { exact: true })
        .count(),
      0,
    );
    await button(evidenceReader, "Check evidence again").click();
    await evidencePanel(evidenceReader)
      .getByText("Snapshot edition 1.", { exact: true })
      .waitFor();
  });
  await test("Actual read-only AI permission retains authorized evidence and denies relationship writes", async () => {
    narrowed = setup("narrow", {
      actor: "reviewer",
      capability: "ai.enablement.manage",
    });
    const reader = await user("reviewer", "AI enablement");
    activePage = reader;
    await reopen(reader, id);
    await button(reader, "View programme evidence").click();
    await evidencePanel(reader)
      .getByText("Snapshot edition 1.", { exact: true })
      .waitFor();
    assert.equal(await button(reader, "Choose programme evidence").count(), 0);
    assert.equal(
      await button(reader, "Review clearing of evidence relationship").count(),
      0,
    );
    assert.equal(await button(reader, "Save plan changes").count(), 0);
    const current = await api("reviewer", planPath(id));
    await api(
      "reviewer",
      evidencePath(id),
      command(
        {
          programme_id: prepared.programme.object_id,
          indicator_id: prepared.indicator.object_id,
          period_id: prepared.period.object_id,
          interpretation_note: "Synthetic denied reader command",
        },
        current.revision_id,
      ),
      404,
      "PUT",
    );
    setup("restore", narrowed);
    narrowed = null;
  });
  await test("All qualified sources remained unchanged and no external/provider request occurred", async () => {
    assert.deepEqual(await hashes(), qualifiedSources);
    assert.deepEqual(await servedHashes(), qualifiedServedAssets);
    assert.deepEqual(errors, []);
    assert.deepEqual(blockedExternalRequests, []);
    assert.equal(requestCounts.advisory, 0);
    const unexpected = consoleErrors.filter((r) => !expectedConsoleEvent(r));
    assert.deepEqual(unexpected, []);
  });
} catch (error) {
  console.error(error.stack);
  results.push({
    name: "Real Tola AI extension browser qualification",
    status: "failed",
    message: error.message,
  });
  if (activePage) {
    const file = path.join(local, "tola-ai-extension-failure.png");
    await activePage.screenshot({ path: file, fullPage: true });
    screenshots.push({
      name: "Failure",
      file,
      synthetic: true,
      realProduct: true,
    });
  }
  process.exitCode = 1;
} finally {
  if (narrowed) {
    try {
      setup("restore", narrowed);
    } catch (error) {
      errors.push("Synthetic grant restoration failed: " + error.message);
      process.exitCode = 1;
    }
  }
  const currentSources = await hashes();
  const currentServedAssets = await servedHashes();
  const report = {
    scope:
      "Real Chrome UI and actual local API/application database using disposable synthetic facts; explicit response-loss injection and grant narrowing are labelled",
    started_at: startedAt,
    finished_at: new Date().toISOString(),
    browser_version: browser.version(),
    base_origin: new URL(base).origin,
    fixture_directory: local,
    results,
    request_counts: requestCounts,
    accessibility_scans: accessibilityScans,
    screenshots,
    errors,
    console_errors: consoleErrors.map((r) => ({
      ...r,
      expected_reason: expectedConsoleEvent(r),
    })),
    blocked_external_requests: blockedExternalRequests,
    injected_failures: injectedFailures,
    fixture_setup: fixtureSetup,
    runtime_qualification: runtimeQualification,
    actor_workflow: {
      evidence_reader_and_manager: "author",
      internal_advice_requester_with_directory_authority: "admin",
      invited_organisation_member: "reviewer",
      independent_later_plan_editor: "admin",
      authority: "Existing fixture grants; no capability or role widening",
    },
    qualified_sources: qualifiedSources,
    current_sources: currentSources,
    qualified_served_assets: qualifiedServedAssets,
    current_served_assets: currentServedAssets,
    served_assets_unchanged:
      JSON.stringify(currentServedAssets) ===
      JSON.stringify(qualifiedServedAssets),
    sources_unchanged:
      JSON.stringify(currentSources) === JSON.stringify(qualifiedSources),
  };
  await fs.mkdir(path.dirname(evidenceFile), { recursive: true });
  await fs.writeFile(evidenceFile, JSON.stringify(report, null, 2) + "\n");
  await browser.close();
}
