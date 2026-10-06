import { captureReviewSnapshot } from "../../apps/web/src/AIPlanReviewModel.ts";
import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";
import { approveRecoveryContact } from "./recovery-fixture.mjs";

const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (
  !local ||
  !base ||
  new URL(base).hostname !== "127.0.0.1" ||
  process.env.IMPACT_ENVIRONMENT !== "test" ||
  process.env.IMPACT_ALLOW_FIXTURE_LOAD !== "1"
)
  throw Error(
    "Use scripts/run.py ai-saved-review-browser on a disposable fixture.",
  );
const evidenceFile =
  process.env.IMPACT_BROWSER_EVIDENCE_FILE ||
  path.join(root, "docs/evidence/sprint-0.35-saved-review-browser-tests.json");
const fixture = JSON.parse(
  await fs.readFile("specification/fixtures/api-fixture.json", "utf8"),
);
const passwords = JSON.parse(
  await fs.readFile(path.join(local, "passwords.json"), "utf8"),
);
const require = createRequire(import.meta.url),
  axeSource = await fs.readFile(require.resolve("axe-core/axe.min.js"), "utf8");
const results = [],
  errors = [],
  consoleErrors = [],
  external = [],
  captures = [],
  scans = [],
  injected = [],
  setupEvidence = [],
  downloads = [],
  downloadEvents = [],
  commands = [],
  pages = [],
  narrowed = [],
  narrowedSessions = [];
const startedAt = new Date().toISOString(),
  DAY = 86400000;
const name = "Synthetic saved plan review " + Date.now();
let browser,
  activePage,
  tenant,
  plan,
  currentRevision,
  olderRevision,
  missingPlan,
  qualifiedSources,
  qualifiedAssets,
  runtime,
  currentSources,
  currentAssets;
const expectedNegativeConsole = [];
const fixedSources = [
  "VERSION.json",
  "tools/browser/ai-saved-review-check.mjs",
  "tools/browser/ai-plan-review-model-check.mjs",
  "tools/browser/ai-plan-export-adapter-check.mjs",
  "tools/browser/recovery-fixture.mjs",
  "scripts/run.py",
  "scripts/fixture_support.py",
  "specification/fixtures/api-fixture.json",
  "specification/fixtures/records.json",
  "apps/web/dist/index.html",
];
const sourceDirectories = [
  "apps/api/impact_api",
  "apps/web/src",
  "packages/contracts",
  "infrastructure/migrations",
  "qualification",
];
async function hashes() {
  const files = new Set(fixedSources);
  for (const directory of sourceDirectories) {
    const entries = await fs.readdir(path.join(root, directory), {
      withFileTypes: true,
    });
    assert(entries.length <= 1000, "Bounded source inventory");
    for (const entry of entries)
      if (entry.isFile() && /\.(py|json|tsx?|css|sql)$/.test(entry.name))
        files.add(directory + "/" + entry.name);
  }
  return Object.fromEntries(
    await Promise.all(
      [...files].sort().map(async (file) => [
        file,
        createHash("sha256")
          .update(await fs.readFile(path.join(root, file)))
          .digest("hex"),
      ]),
    ),
  );
}
async function servedHashes() {
  const response = await fetch(base);
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.equal(html, await fs.readFile("apps/web/dist/index.html", "utf8"));
  const assets = [
    ...new Set(
      [
        ...html.matchAll(
          /(?:src|href)="(\/assets\/[A-Za-z0-9._/-]+\.(?:js|css))"/g,
        ),
      ].map((match) => match[1]),
    ),
  ];
  assert(assets.length > 0 && assets.length <= 32);
  return Object.fromEntries(
    await Promise.all(
      assets.map(async (asset) => {
        assert(!asset.includes(".."));
        const response = await fetch(new URL(asset, base));
        assert.equal(response.status, 200);
        const bytes = Buffer.from(await response.arrayBuffer());
        assert(bytes.length <= 10 * 1024 * 1024);
        assert.deepEqual(
          bytes,
          await fs.readFile(path.join(root, "apps/web/dist", asset.slice(1))),
        );
        return [asset, createHash("sha256").update(bytes).digest("hex")];
      }),
    ),
  );
}
const command = (data, revision) => ({
  operation_id: crypto.randomUUID(),
  ...(revision ? { expected_revision: revision } : {}),
  data,
});
async function api(actor, route, body, expected = 200, method) {
  const response = await fetch(base + route, {
    method: method || (body ? "POST" : "GET"),
    headers: {
      Authorization: "Bearer " + process.env[fixture.actors[actor].token_env],
      "Content-Type": "application/json",
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const result = await response.json();
  assert.equal(response.status, expected, JSON.stringify(result));
  return result;
}
async function test(
  title,
  run,
  scope = "Real Chrome and actual local application API/database with synthetic facts",
) {
  await run();
  results.push({ name: title, status: "passed", scope });
  console.log("PASS " + title);
}
const button = (page, title) =>
  page.getByRole("button", { name: title, exact: true });
async function enabled(page, title) {
  const target = button(page, title);
  await target.waitFor();
  const handle = await target.elementHandle();
  assert(handle);
  await page.waitForFunction((node) => !node.disabled, handle);
  await handle.dispose();
}
const panel = (page) => page.locator(".ai-plan-portability");
const tenantPath = () => `/v1/tenants/${tenant.tenant_id}/`;
const planPath = () => tenantPath() + "ai-enablement/plans/" + plan.object_id;
const exportPath = (revision = currentRevision) =>
  planPath() + "/revisions/" + revision + "/exports";
// These helpers use the existing disposable qualification connection. Authority
// changes only narrow already granted capabilities and restore those exact rows.
// They do not add grants, rewrite role/profile ceilings, or disable RLS/triggers.
const fixturePython = String.raw`
import hashlib,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'qualification'))
from conftest import live
from test_ai_adoption_plans import plan
from test_ai_task_practice import practice
assert os.environ.get('IMPACT_ENVIRONMENT')=='test' and os.environ.get('IMPACT_ALLOW_FIXTURE_LOAD')=='1'
args=json.load(sys.stdin); generator=live.__wrapped__(); client=next(generator)
try:
    op=args['operation']; answer={}
    if op=='plan-input':
        answer=plan();answer['title']=args['title'];answer['procurement']['requirements']='=Preserve exact synthetic wording — Café समुदाय'
        if args.get('complete'):answer['planning']={'cost_comparison':None,'pilot_evaluation':None,'task_practice':practice()}
    else:
        with client.db() as c:
            if op=='runtime':answer={'migrations':c.execute('SELECT version,sha256 FROM impact.schema_migration ORDER BY version').fetchall()}
            else:
                tenant=args['tenant']; c.execute("SELECT set_config('impact.tenant_id',%s,true)",(tenant,))
                if op in ('narrow','restore'):
                    if op=='narrow':
                        rows=c.execute('SELECT g.object_id,g.purpose FROM impact.grant_current g JOIN impact.tenant_principal p '
                          'ON p.tenant_id=g.tenant_id AND p.principal_id=g.subject_id WHERE g.tenant_id=%s AND p.identity_id=%s '
                          'AND g.capability=%s AND g.purpose IS NULL',(tenant,client.fixture['actors'][args['actor']]['identity_id'],args['capability'])).fetchall()
                        assert rows,'Actor must hold the actual narrowed capability'
                        c.execute("UPDATE impact.grant_current SET purpose='SYNTHETIC_BROWSER_NARROWED' WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
                          (tenant,[str(row['object_id']) for row in rows]))
                        answer={'tenant':tenant,'grants':[{'object_id':str(row['object_id']),'purpose':row['purpose']}for row in rows]}
                    else:
                        for row in args['grants']:c.execute('UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s',(row['purpose'],tenant,row['object_id']))
                        answer={'restored':len(args['grants'])}
                elif op=='plan-heads':answer={'heads':c.execute("SELECT object_id,head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_type='AIAdoptionPlan' ORDER BY object_id",(tenant,)).fetchall()}
                elif op=='plan-counts':
                    answer={'revisions':c.execute("SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",(tenant,args['object_id'])).fetchone()['n'],
                      'receipts':c.execute("SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND command_type='update_ai_adoption_plan' AND operation_id=%s",(tenant,args['operation_id'])).fetchone()['n']}
                else:raise ValueError('Unknown fixture operation')
    print(json.dumps(answer,default=str))
finally:generator.close()
`;
function setup(operation, args = {}) {
  const result = spawnSync(
    path.join(root, ".venv/bin/python"),
    ["-c", fixturePython],
    {
      cwd: root,
      env: process.env,
      input: JSON.stringify({ operation, ...args }),
      encoding: "utf8",
      timeout: 60000,
    },
  );
  assert.equal(
    result.status,
    0,
    result.stderr || "Synthetic fixture helper failed",
  );
  setupEvidence.push({
    operation,
    scope: ["narrow", "restore"].includes(operation)
      ? "Explicit disposable-fixture narrowing/restoration only; current RLS and immutable guards remain active"
      : ["session-narrow", "session-restore"].includes(operation)
        ? "Disposable negative fixture narrows/restores only the exact expected synthetic identity browser session auth_time; no capability, immutable data, RLS or ceiling changes; no cookie/hash/token is recorded"
        : operation === "plan-input"
          ? "Pure synthetic input from existing qualification helpers; product writes use actual HTTP"
          : "Read-only observation of actual disposable application database",
  });
  return JSON.parse(result.stdout);
}
function restoreLatest(items, operation = "restore") {
  const change = items.at(-1);
  assert(change);
  setup(operation, change);
  items.pop();
}
async function user(actor) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1050 },
    acceptDownloads: true,
  });
  await context.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (
      url.origin === new URL(base).origin ||
      ["data:", "blob:"].includes(url.protocol)
    )
      await route.continue();
    else {
      external.push({ origin: url.origin, method: route.request().method() });
      await route.abort();
    }
  });
  const page = await context.newPage();
  pages.push(page);
  page.setDefaultTimeout(15000);
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("download", (download) =>
    downloadEvents.push({
      actor,
      filename: download.suggestedFilename(),
      at: new Date().toISOString(),
    }),
  );
  page.on("console", (event) => {
    if (event.type() === "error")
      consoleErrors.push({ message: event.text(), location: event.location() });
  });
  page.on("request", (request) => {
    const pathname = new URL(request.url()).pathname;
    if (
      ["POST", "PUT"].includes(request.method()) &&
      pathname.includes("/ai-enablement/")
    )
      commands.push({
        actor,
        path: pathname,
        method: request.method(),
        body: request.postDataJSON(),
      });
  });
  await page.goto(base);
  await page.getByLabel("Username", { exact: true }).fill(actor);
  await page.getByLabel("Password", { exact: true }).fill(passwords[actor]);
  await button(page, "Sign in →").click();
  await page
    .getByLabel("Workspace", { exact: true })
    .selectOption(tenant.tenant_id);
  await button(page, "AI enablement").click();
  await page
    .getByRole("heading", { name: "Your AI adoption plan", exact: true })
    .waitFor();
  return page;
}
function unexpectedConsole(record) {
  const url = new URL(record.location?.url || base, base),
    route = url.pathname;
  if (route === "/auth/me" && /status of 401/.test(record.message))
    return false;
  if (
    expectedNegativeConsole.some(
      (item) =>
        item.route === route &&
        record.message.includes("status of " + item.status),
    )
  )
    return false;
  if (
    injected.some((item) => item.route === route) &&
    /net::ERR_(FAILED|CONNECTION_FAILED)/.test(record.message)
  )
    return false;
  return true;
}
async function openPlan(page, selected = plan) {
  await page
    .getByLabel("Saved adoption plans", { exact: true })
    .selectOption(selected.object_id);
  const route = tenantPath() + "ai-enablement/plans/" + selected.object_id;
  const response = page.waitForResponse(
    (r) =>
      r.request().method() === "GET" && new URL(r.url()).pathname === route,
  );
  await button(page, "Open saved plan").click();
  const result = await response;
  assert.equal(result.status(), 200);
  const row = await result.json();
  assert.equal(row.object_id, selected.object_id);
  await review(page)
    .getByRole("heading", { name: "Review your saved plan", exact: true })
    .waitFor();
  return row;
}
const review = (page) => page.locator(".ai-plan-review");
const observed = [];
async function reveal(page, row) {
  const show = review(page).getByRole("button", {
    name: "View saved-plan review",
    exact: true,
  });
  if (await show.count()) await show.click();
  await review(page).getByText(row.data.title, { exact: false }).waitFor();
  const snapshot = captureReviewSnapshot(row, {
    base: tenantPath(),
    principalId: "qualification-only",
    sessionIdentity: "qualification-only",
  });
  assert(snapshot, "Actual closed saved public data must be interpretable");
  const text = await review(page).innerText();
  for (const area of snapshot.areas)
    for (const note of area.notes)
      assert(text.includes(note), "Exact saved public input note: " + area.id);
  assert.equal(await review(page).locator("progress").count(), 0);
  observed.push({
    object_id: row.object_id,
    revision_id: row.revision_id,
    title: row.data.title,
    derived_area_states: snapshot.areas.map((area) => ({
      id: area.id,
      basis: area.basis,
    })),
  });
  return snapshot;
}
async function waitHidden(page) {
  await review(page)
    .getByText(/Open the saved plan again|working draft has local edits/)
    .waitFor();
  assert.equal(await review(page).locator(".ai-cards").count(), 0);
}
async function heldGet(page) {
  let resolveReady, releaseResponse;
  const ready = new Promise((resolve) => {
    resolveReady = resolve;
  });
  const released = new Promise((resolve) => {
    releaseResponse = resolve;
  });
  const route = base + planPath();
  const handler = async (intercepted) => {
    const response = await intercepted.fetch();
    assert.equal(response.status(), 200);
    const row = await response.json();
    assert.equal(row.object_id, plan.object_id);
    resolveReady(row);
    await released;
    try {
      await intercepted.fulfill({ response });
    } catch (error) {
      assert(
        /Target.*closed|already handled|cancelled|disposed|Invalid InterceptionId/.test(
          String(error),
        ),
        String(error),
      );
    }
    await page.unroute(route, handler).catch(() => {});
  };
  await page.route(route, handler);
  injected.push({
    route: planPath(),
    scope:
      "Actual currently authorised canonical GET200 body retained; only browser delivery is delayed, never a mocked server authority outcome",
  });
  return { ready, release: () => releaseResponse() };
}
async function loseSave(page) {
  let resolveCommitted;
  const committed = new Promise((resolve) => {
    resolveCommitted = resolve;
  });
  const route = base + planPath();
  const handler = async (intercepted) => {
    if (intercepted.request().method() !== "PUT") return intercepted.continue();
    const body = intercepted.request().postDataJSON();
    const response = await intercepted.fetch();
    assert.equal(response.status(), 200);
    const receipt = await response.json();
    assert.equal(receipt.operation_id, body.operation_id);
    resolveCommitted({ body, receipt });
    injected.push({
      route: planPath(),
      scope:
        "Actual PUT committed a saved revision; only its response was aborted to exercise the existing exact pending-save recovery",
    });
    await intercepted.abort("failed");
    await page.unroute(route, handler);
  };
  await page.route(route, handler);
  return { committed };
}
async function save(page) {
  const response = page.waitForResponse(
    (r) =>
      r.request().method() === "PUT" &&
      new URL(r.url()).pathname === planPath(),
  );
  await button(page, "Save plan changes").click();
  const result = await response;
  assert.equal(result.status(), 200);
  return result.json();
}
async function mobile(page, width, row) {
  await page.setViewportSize({ width, height: 900 });
  const hide = review(page).getByRole("button", {
    name: "Hide saved-plan review",
    exact: true,
  });
  if (await hide.count()) await hide.click();
  await review(page)
    .getByRole("button", { name: "View saved-plan review", exact: true })
    .focus();
  await page.keyboard.press("Enter");
  await review(page).getByText(row.data.title, { exact: false }).waitFor();
  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth > innerWidth + 1,
    ),
    false,
  );
  await page.evaluate(axeSource);
  const result = await page.evaluate(() =>
    window.axe.run(document.querySelector(".ai-plan-review"), {
      runOnly: {
        type: "tag",
        values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
      },
    }),
  );
  assert.deepEqual(result.violations, []);
  assert.deepEqual(result.incomplete, []);
  scans.push({ width, violations: [], incomplete: [] });
  const file = path.join(local, `ai-plan-review-${width}.png`);
  await review(page).screenshot({ path: file });
  captures.push({
    width,
    file,
    sha256: createHash("sha256")
      .update(await fs.readFile(file))
      .digest("hex"),
    synthetic: true,
    realProduct: true,
    view: "Full actual saved-plan review component",
  });
}
try {
  qualifiedSources = await hashes();
  qualifiedAssets = await servedHashes();
  await test(
    "Actual runtime and applied migrations match the frozen saved-review source",
    async () => {
      const version = JSON.parse(await fs.readFile("VERSION.json", "utf8"));
      const observed = await api("author", "/v1/runtime-manifest");
      assert.equal(observed.environment, "test");
      assert.equal(observed.build_id, "impact-" + version.build);
      assert.equal(observed.api_version, version.domain_api);
      assert.equal(observed.mutation_tests_allowed, true);
      const applied = setup("runtime").migrations;
      assert.equal(applied.at(-1).version, 40);
      assert.equal(observed.schema_version, String(applied.length));
      const migration = Object.keys(qualifiedSources).find((file) =>
        /^infrastructure\/migrations\/0040_.*\.sql$/.test(file),
      );
      assert(migration);
      assert.equal(applied.at(-1).sha256, qualifiedSources[migration]);
      runtime = { ...observed, applied_migrations: applied };
    },
    "Authenticated actual HTTP runtime and read-only applied database ledger before browser creation",
  );
  await test(
    "Fresh tenant and explicit manager read/manage access require actual independent HTTP reviews",
    async () => {
      const qualification = (await api("admin", "/v1/platform/tenants"))
        .qualifications[0];
      tenant = await api(
        "admin",
        "/v1/platform/tenants",
        command({
          owner_identity_id: fixture.actors.author.identity_id,
          qualification_id: qualification.qualification_id,
          operating_name: name,
          reporting_zone: "UTC",
          retention_days: 365,
          privacy_reference: qualification.privacy_reference,
          reason: "Synthetic saved-review organisation",
        }),
      );
      tenant = await api(
        "author",
        `/v1/platform/tenants/${tenant.tenant_id}/actions/accept-owner`,
        command({ reason: "Synthetic owner acceptance" }, tenant.revision_id),
      );
      await approveRecoveryContact(base, fixture, tenant);
      tenant = await api(
        "owner",
        `/v1/platform/tenants/${tenant.tenant_id}/actions/activate`,
        command(
          { reason: "Independent synthetic activation" },
          tenant.revision_id,
        ),
      );
      const profile = await api("author", "/v1/platform/access-bootstraps");
      let bootstrap = await api(
        "author",
        `/v1/platform/tenants/${tenant.tenant_id}/access-bootstrap`,
        command(
          {
            second_identity_id: fixture.actors.reviewer.identity_id,
            profile_hash: profile.profile_hash,
            role_names: ["PROGRAMME_MANAGER"],
            expires_at: new Date(Date.now() + 30 * DAY).toISOString(),
            reason: "Bounded explicit manager ceiling",
          },
          tenant.revision_id,
        ),
      );
      const decisions = `/v1/platform/access-bootstraps/${bootstrap.request_id}/actions/`;
      bootstrap = await api(
        "reviewer",
        decisions + "accept",
        command({ reason: "Named second acceptance" }, bootstrap.revision_id),
      );
      bootstrap = await api(
        "admin",
        decisions + "approve",
        command(
          { reason: "Independent platform review" },
          bootstrap.revision_id,
        ),
      );
      assert.equal(bootstrap.state, "Applied");
      const roles = (await api("reviewer", tenantPath() + "role-templates"))
        .items;
      const role = roles.find((row) => row.name === "PROGRAMME_MANAGER");
      assert(role?.capabilities.includes("ai.enablement.export"));
      const members = (
        await api("reviewer", tenantPath() + "membership-directory")
      ).items;
      const member = members.find(
        (row) => row.object_id === bootstrap.second_membership_id,
      );
      assert(member);
      const request = await api(
        "reviewer",
        tenantPath() + "access-requests",
        command({
          membership_id: member.object_id,
          expected_membership_revision: member.revision_id,
          role_template_id: role.object_id,
          scope_ids: [bootstrap.scope_id],
          expires_at: new Date(Date.now() + 20 * DAY).toISOString(),
          reason: "Reviewed manager plan preparation scope",
        }),
      );
      const decision =
        tenantPath() +
        "access-requests/" +
        request.object_id +
        "/actions/approve";
      await api(
        "reviewer",
        decision,
        command(
          { reason: "Self approval must be refused" },
          request.revision_id,
        ),
        403,
      );
      await api(
        "author",
        decision,
        command(
          { reason: "Independent ordinary manager approval" },
          request.revision_id,
        ),
      );
      const access = await api("reviewer", tenantPath() + "me/access");
      for (const cap of ["ai.enablement.read", "ai.enablement.manage"])
        assert(access.capabilities.includes(cap));
      setupEvidence.push({
        operation: "reviewed-fresh-tenant-manager",
        scope:
          "Actual HTTP custody, independent bootstrap and explicit manager assignment; owner SQL grant shortcut NOT_USED",
        tenant_id: tenant.tenant_id,
        profile_hash: profile.profile_hash,
      });
      const data = setup("plan-input", { title: name + " — Café समुदाय" });
      plan = await api(
        "reviewer",
        tenantPath() + "ai-enablement/plans",
        command(data),
        201,
      );
      olderRevision = plan.revision_id;
      const updated = setup("plan-input", {
        title: name + " complete saved revision — Café समुदाय",
        complete: true,
      });
      plan = await api(
        "reviewer",
        planPath(),
        command(updated, olderRevision),
        200,
        "PUT",
      );
      currentRevision = plan.revision_id;
      const missing = setup("plan-input", {
        title: name + " missing preparation",
      });
      missing.solution_ids = [];
      missing.learning_completed = [];
      missing.procurement = {
        requirements: "",
        data_boundary: "",
        budget_notes: "",
        vendor_questions: "",
      };
      missing.pilot = { success_measure: "", completed_actions: [] };
      missing.planning = {
        cost_comparison: null,
        task_practice: null,
        pilot_evaluation: null,
      };
      missingPlan = await api(
        "reviewer",
        tenantPath() + "ai-enablement/plans",
        command(missing),
        201,
      );
    },
    "Actual independent custody/bootstrap/access-request HTTP decisions and two actual saved plan revisions before browser creation",
  );
  browser = await chromium.launch({
    executablePath:
      process.env.IMPACT_BROWSER_EXECUTABLE ||
      path.join(root, ".local/browser/chromium"),
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--no-zygote",
    ],
  });
  const unopened = await user("reviewer");
  activePage = unopened;
  await test("Plan directory and unopened working drafts never establish a saved review", async () => {
    assert.equal(await review(unopened).count(), 0);
    assert.equal(
      commands.filter((command) => command.path === planPath()).length,
      0,
    );
  });
  let row = await openPlan(activePage);
  await test("Canonical actual GET binds review to the exact saved title and revision", async () => {
    await reveal(activePage, row);
    await review(activePage)
      .getByText("Saved revision details", { exact: true })
      .click();
    assert((await review(activePage).innerText()).includes(row.object_id));
    assert((await review(activePage).innerText()).includes(row.revision_id));
    await review(activePage)
      .getByText("Saved revision details", { exact: true })
      .click();
    assert.equal(Object.hasOwn(row.data, "impact_reference"), false);
    assert.equal(Object.hasOwn(row.data, "human_advice"), false);
  });
  await test("Review toggles and existing-section navigation do not write or auto-start an exercise", async () => {
    const before = commands.length,
      heads = setup("plan-heads", { tenant: tenant.tenant_id });
    await button(activePage, "Hide saved-plan review").click();
    await button(activePage, "View saved-plan review").click();
    for (const [title, target] of [
      ["Open tool comparison", "Find and compare tools"],
      ["Open team learning", "Build team capacity"],
      ["Open guided practice", "Practise a useful task"],
      ["Open procurement brief", "Procurement brief"],
      ["Open pilot tracker", "Pilot tracker"],
    ]) {
      await review(activePage)
        .getByRole("button", { name: title, exact: true })
        .first()
        .click();
      await activePage
        .getByRole("heading", { name: target, exact: true })
        .waitFor();
    }
    assert.equal(commands.length, before);
    assert.deepEqual(setup("plan-heads", { tenant: tenant.tenant_id }), heads);
  });
  await test("Missing saved public preparation produces follow-up without a completion or private-linkage count", async () => {
    const empty = await openPlan(activePage, missingPlan);
    await reveal(activePage, empty);
    const text = await review(activePage).innerText();
    assert(text.includes("Follow-up suggested"));
    assert(text.includes("A tool shortlist is not recorded"));
    assert(text.includes("Record a pilot success measure"));
    assert(text.includes("not recorded in this saved plan"));
    assert.equal(await review(activePage).locator("progress").count(), 0);
    assert(!/advice case|linked programme|reference count/i.test(text));
    row = await openPlan(activePage);
    await reveal(activePage, row);
  });
  await test("Local edit and undo cannot restore review until another actual canonical Open", async () => {
    const title = await activePage
      .getByLabel("Plan name", { exact: true })
      .inputValue();
    const heads = setup("plan-heads", { tenant: tenant.tenant_id });
    await activePage
      .getByLabel("Plan name", { exact: true })
      .fill(title + " local edit");
    await waitHidden(activePage);
    await activePage.getByLabel("Plan name", { exact: true }).fill(title);
    await waitHidden(activePage);
    assert.deepEqual(setup("plan-heads", { tenant: tenant.tenant_id }), heads);
    row = await openPlan(activePage);
    await reveal(activePage, row);
  });
  await test("Actual save receipt creates no review source until the committed revision is reopened", async () => {
    await activePage
      .getByLabel("Plan name", { exact: true })
      .fill(name + " deliberate new saved title — Café समुदाय");
    await waitHidden(activePage);
    const receipt = await save(activePage);
    currentRevision = receipt.revision_id;
    plan = receipt;
    await activePage
      .getByText("Plan saved. Any edits made while saving remain unsaved.", {
        exact: true,
      })
      .waitFor();
    await waitHidden(activePage);
    row = await openPlan(activePage);
    assert.equal(row.revision_id, receipt.revision_id);
    await reveal(activePage, row);
  });
  await test("Lost actual committed save keeps navigation blocked and retries the exact pending operation", async () => {
    const title = name + " lost committed save";
    await activePage.getByLabel("Plan name", { exact: true }).fill(title);
    await waitHidden(activePage);
    const loss = await loseSave(activePage);
    await button(activePage, "Save plan changes").click();
    const result = await loss.committed;
    await enabled(activePage, "Retry previous save");
    assert.equal(
      await button(activePage, "Open saved plan").isDisabled(),
      true,
    );
    await waitHidden(activePage);
    const baseline = setup("plan-counts", {
      tenant: tenant.tenant_id,
      object_id: plan.object_id,
      operation_id: result.body.operation_id,
    });
    const response = activePage.waitForResponse(
      (r) =>
        r.request().method() === "PUT" &&
        new URL(r.url()).pathname === planPath(),
    );
    await button(activePage, "Retry previous save").click();
    const replay = await response;
    assert.equal(replay.status(), 200);
    assert.deepEqual(await replay.json(), result.receipt);
    const sent = commands.filter(
      (command) =>
        command.method === "PUT" &&
        command.body.operation_id === result.body.operation_id,
    );
    assert.equal(sent.length, 2);
    assert.deepEqual(sent[0].body, sent[1].body);
    assert.deepEqual(
      setup("plan-counts", {
        tenant: tenant.tenant_id,
        object_id: plan.object_id,
        operation_id: result.body.operation_id,
      }),
      baseline,
    );
    assert.equal(baseline.receipts, 1);
    currentRevision = result.receipt.revision_id;
    plan = result.receipt;
    await waitHidden(activePage);
    row = await openPlan(activePage);
    await reveal(activePage, row);
  });
  await test("Actual current read refusal clears prior review despite cached positive client permission", async () => {
    const change = setup("narrow", {
      tenant: tenant.tenant_id,
      actor: "reviewer",
      capability: "ai.enablement.read",
    });
    narrowed.push(change);
    expectedNegativeConsole.push({ route: planPath(), status: 404 });
    const denied = activePage.waitForResponse(
      (r) =>
        r.request().method() === "GET" &&
        new URL(r.url()).pathname === planPath(),
    );
    await button(activePage, "Open saved plan").click();
    const result = await denied;
    assert.equal(result.status(), 404);
    assert.equal((await result.json()).code, "RESOURCE_UNAVAILABLE");
    await waitHidden(activePage);
    assert.equal(
      await review(activePage)
        .getByText(row.data.title, { exact: false })
        .count(),
      0,
    );
    await api("reviewer", planPath(), undefined, 404);
    restoreLatest(narrowed);
    row = await openPlan(activePage);
    await reveal(activePage, row);
  });
  await test("Actual200 reply delayed across draft edit and undo cannot restore a stale review", async () => {
    const title = await activePage
        .getByLabel("Plan name", { exact: true })
        .inputValue(),
      heads = setup("plan-heads", { tenant: tenant.tenant_id });
    const held = await heldGet(activePage);
    await button(activePage, "Open saved plan").click();
    const real = await held.ready;
    assert.equal(real.revision_id, row.revision_id);
    await activePage
      .getByLabel("Plan name", { exact: true })
      .fill(title + " transient edit");
    await waitHidden(activePage);
    await activePage.getByLabel("Plan name", { exact: true }).fill(title);
    await waitHidden(activePage);
    held.release();
    await activePage
      .getByText(/brief or draft changed while the saved plan was opening/)
      .waitFor();
    await waitHidden(activePage);
    assert.deepEqual(setup("plan-heads", { tenant: tenant.tenant_id }), heads);
    row = await openPlan(activePage);
    await reveal(activePage, row);
  });
  await test("Actual logout and another actor in the same organisation cannot inherit prior review", async () => {
    const old = activePage;
    await button(old, "Sign out").click();
    await old.getByLabel("Username", { exact: true }).waitFor();
    assert.equal(await review(old).count(), 0);
    await old.getByLabel("Username", { exact: true }).fill("author");
    await old.getByLabel("Password", { exact: true }).fill(passwords.author);
    await button(old, "Sign in →").click();
    await old
      .getByLabel("Workspace", { exact: true })
      .selectOption(tenant.tenant_id);
    await button(old, "AI enablement").click();
    await old
      .getByRole("heading", { name: "Your AI adoption plan", exact: true })
      .waitFor();
    assert.equal(await review(old).count(), 0);
    assert.equal(
      await old.getByLabel("Plan name", { exact: true }).inputValue(),
      "",
    );
    const source = await api("author", planPath());
    row = await openPlan(old);
    assert.equal(row.revision_id, source.revision_id);
    await reveal(old, row);
  });
  for (const width of [1440, 390, 320])
    await test(`Actual saved-review keyboard/mobile/accessibility${width}px`, () =>
      mobile(activePage, width, row));
  await test("Exact sources and served assets stayed fixed with no download or external/provider command", async () => {
    assert.deepEqual(external, []);
    assert.deepEqual(errors, []);
    assert.deepEqual(consoleErrors.filter(unexpectedConsole), []);
    assert.equal(downloadEvents.length, 0);
    assert.equal(
      commands.filter(
        (command) =>
          command.path.endsWith("/advisory") ||
          command.path.endsWith("/exports"),
      ).length,
      0,
    );
    currentSources = await hashes();
    currentAssets = await servedHashes();
    assert.deepEqual(currentSources, qualifiedSources);
    assert.deepEqual(currentAssets, qualifiedAssets);
  });
} catch (error) {
  errors.push(error.stack || String(error));
  process.exitCode = 1;
  if (activePage)
    await activePage
      .screenshot({
        path: path.join(local, "ai-plan-review-failure.png"),
        fullPage: true,
      })
      .catch(() => {});
} finally {
  for (const change of narrowed)
    try {
      setup("restore", change);
    } catch (error) {
      errors.push("Fixture restoration failed: " + error.message);
      process.exitCode = 1;
    }
  if (!currentSources) currentSources = await hashes().catch(() => null);
  if (!currentAssets) currentAssets = await servedHashes().catch(() => null);
  await fs.mkdir(path.dirname(evidenceFile), { recursive: true });
  await fs.writeFile(
    evidenceFile,
    JSON.stringify(
      {
        scope:
          "Actual local Chrome/API/PGlite saved public review with independently reviewed synthetic manager authority. Transport delay/response loss and synthetic grant narrowing are labelled. Not native-role/concurrency, hosted deployment or nonprofit acceptance evidence.",
        actual_api_qualification: errors.length
          ? "FAILED_OR_INCOMPLETE"
          : "PASSED_ON_DISPOSABLE_LOCAL_DATABASE",
        started_at: startedAt,
        finished_at: new Date().toISOString(),
        base_origin: base,
        fixture_directory: local,
        browser_version: browser ? await browser.version() : null,
        results,
        errors,
        console_errors: consoleErrors,
        blocked_external_requests: external,
        screenshots: captures,
        accessibility_scans: scans,
        injected_failures: injected,
        fixture_setup: setupEvidence,
        runtime_qualification: runtime,
        write_requests: commands,
        observed_saved_public_sources: observed,
        qualified_sources: qualifiedSources,
        current_sources: currentSources,
        sources_unchanged:
          !!qualifiedSources &&
          JSON.stringify(qualifiedSources) === JSON.stringify(currentSources),
        qualified_served_assets: qualifiedAssets,
        current_served_assets: currentAssets,
        served_assets_unchanged:
          !!qualifiedAssets &&
          JSON.stringify(qualifiedAssets) === JSON.stringify(currentAssets),
        limitations: [
          "No native-role, hosted deployment, provider execution or nonprofit acceptance claim",
          "Direct fixture database observations/narrowing use a privileged disposable connection; actual API authorisation is the application path, not direct-login RLS evidence",
          "Loss/return of a canRead prop before a held response is separately exercised in the labelled private request-function fixture; the actual shell refresh/logout remount boundary is not an injected backend authority response",
          "Exposed principal/human identity reset is not a unique same-identity reauthentication generation",
          "No private linked impact/advice case is created by this checker; privacy field selection has separate pure/backend/native evidence",
        ],
      },
      null,
      2,
    ) + "\n",
  );
  if (browser) await browser.close();
}
