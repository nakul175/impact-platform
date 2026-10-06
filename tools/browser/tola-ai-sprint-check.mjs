import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { approveRecoveryContact } from "./recovery-fixture.mjs";

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
    "Use scripts/run.py tola-ai-sprint-browser on a disposable fixture",
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
  path.join(root, "docs/evidence/sprint-0.32-browser-tests.json");
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
const requestCounts = { planWrites: 0, accessWrites: 0, advisory: 0 };
const startedAt = new Date().toISOString();
const sourcePaths = [
  "tools/browser/tola-ai-sprint-check.mjs",
  "scripts/run.py",
  "VERSION.json",
  "apps/web/src/AccessUpgrade.tsx",
  "apps/web/src/AIGuidanceArchive.tsx",
  "apps/web/src/AIAdoptionWorkspace.tsx",
  "apps/web/src/ai-enablement.css",
  "apps/api/impact_api/access_upgrade.py",
  "apps/api/impact_api/ai_content_archives.py",
  "apps/api/impact_api/ai_adoption_plans.py",
  "infrastructure/migrations/0036_reviewed_ceiling_widening.sql",
  "infrastructure/migrations/0037_ai_content_snapshots.sql",
];
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
const name = "Synthetic Tola AI access " + Date.now();
const DAY = 86400000;
const command = (data, revision) => ({
  operation_id: crypto.randomUUID(),
  ...(revision ? { expected_revision: revision } : {}),
  data,
});

// Historical setup is explicit synthetic maintenance, never an application route.
// It follows the existing governed-store fixtures, keeps RLS and immutable triggers
// enabled, and prints only synthetic receipt IDs or counts, never connection strings.
const fixturePython = String.raw`
import json, os, sys
from copy import deepcopy
from uuid import uuid4
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
sys.path.insert(0, str(Path.cwd() / 'qualification'))
from impact_api.auth import Auth, Identity
from impact_api.config import Settings
from impact_api.store import Database, Context, context, authorize, load, write, audit
from impact_api.tenant_lifecycle import now
from impact_api.ai_adoption_plans import KIND
from starlette.requests import Request
from test_ai_adoption_plans import plan
from test_ai_planning_inputs import planning_plan
assert os.environ.get('IMPACT_ENVIRONMENT') == 'test'
assert os.environ.get('IMPACT_ALLOW_FIXTURE_LOAD') == '1'
args = json.load(sys.stdin)
fixture = json.loads(Path('specification/fixtures/api-fixture.json').read_text())
operation = args['operation']
tenant = args.get('tenant', fixture['tenant_a'])
if operation == 'legacy-plan':
    settings = Settings(**json.loads((Path(os.environ['IMPACT_TEST_LOCAL']) / 'config.json').read_text()))
    db = Database(settings)
    token = os.environ[fixture['actors']['admin']['token_env']]
    identity = Auth(settings, db).resolve(Request({'type':'http', 'method':'POST',
      'headers':[(b'authorization', ('Bearer ' + token).encode())]}))
    data = planning_plan() if args['practice'] else plan()
    data['title'] = args['title']
    data['content_versions'] = {'catalog':'synthetic-before-archive', 'solutions':'synthetic-before-archive'}
    if args['practice']:
        data['content_versions']['practice'] = 'synthetic-unavailable-practice'
    with db.transaction(tenant) as c:
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        ctx = context(c, identity, tenant, write=True)
        authorize(c, ctx, 'create_ai_adoption_plan', hidden=True)
        authorize(c, ctx, 'get_ai_adoption_plan', hidden=True)
        receipt = write(c, ctx, KIND, deepcopy(data), 'Draft')
        audit(c, ctx, 'create_ai_adoption_plan', receipt, str(uuid4()))
    print(json.dumps({'receipt':receipt, 'data':data}))
else:
    with psycopg.connect(os.environ['IMPACT_FIXTURE_DSN'], row_factory=dict_row, prepare_threshold=None) as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        if operation == 'pre-ai-profile':
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            access = args['access']
            old = deepcopy(access['manifest'])
            old['version'] = 'synthetic-pre-ai-profile'
            for role, caps in old['roles'].items():
                old['roles'][role] = [cap for cap in caps if not cap.startswith('ai.')]
            c.execute('UPDATE impact.tenant_access_bootstrap SET manifest=%s WHERE tenant_id=%s AND request_id=%s',
              (Jsonb(old), tenant, access['request_id']))
            c.execute("DELETE FROM impact.grant_authority WHERE tenant_id=%s AND capability LIKE 'ai.%%'", (tenant,))
            c.execute("UPDATE impact.object_registry r SET lifecycle_state='Revoked' FROM impact.grant_current g "
              "WHERE g.tenant_id=r.tenant_id AND g.object_id=r.object_id AND g.tenant_id=%s AND g.capability LIKE 'ai.%%'", (tenant,))
            actor = fixture['actors']['author']
            person = Identity(actor['identity_id'], actor['natural_identity_id'], actor['identity_id'], now())
            principal = c.execute('SELECT principal_id FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s',
              (tenant, actor['identity_id'])).fetchone()['principal_id']
            ctx = Context(tenant, str(principal), '', person, 0, 0, [])
            rows = c.execute("SELECT r.object_id FROM impact.object_registry r JOIN impact.object_revision v "
              "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s "
              "AND r.object_type='RoleTemplate' AND v.payload->>'managed_by'='impact-access-v1'", (tenant,)).fetchall()
            for row in rows:
                previous = load(c, ctx, str(row['object_id']), 'RoleTemplate')
                data = {**previous['payload'], 'capabilities':[cap for cap in previous['payload']['capabilities'] if not cap.startswith('ai.')]}
                write(c, ctx, 'RoleTemplate', data, 'Active', previous, track_author=False)
            print(json.dumps({'synthetic_maintenance':'pre-AI applied profile', 'managed_roles':len(rows)}))
        elif operation == 'readonly':
            principal = fixture['actors']['reviewer']['principal_id']
            rows = c.execute("UPDATE impact.grant_current SET purpose='QUALIFICATION' WHERE tenant_id=%s "
              "AND subject_id=%s AND capability='ai.enablement.manage' AND purpose IS NULL RETURNING object_id", (tenant, principal)).fetchall()
            assert rows
            print(json.dumps({'narrowed_synthetic_grants':len(rows)}))
        elif operation == 'counts':
            tables = ['object_registry','object_revision','audit_event_current','outbox_event','operation_receipt',
              'ai_content_snapshot','ai_plan_content_binding','ai_advisory_request','ai_advisory_result']
            print(json.dumps({table:c.execute('SELECT count(*) AS n FROM impact.' + table + ' WHERE tenant_id=%s',
              (tenant,)).fetchone()['n'] for table in tables}))
        elif operation == 'authority':
            rows = c.execute('SELECT authority_id,capability,expires_at FROM impact.grant_authority WHERE tenant_id=%s ORDER BY authority_id', (tenant,)).fetchall()
            print(json.dumps({str(row['authority_id']):{'capability':row['capability'], 'expires_at':row['expires_at'].isoformat()} for row in rows}))
        elif operation == 'access-events':
            rows = c.execute("SELECT action FROM impact.platform_event WHERE tenant_id=%s AND action LIKE 'access-upgrade-%%' ORDER BY created_at", (tenant,)).fetchall()
            print(json.dumps([row['action'] for row in rows]))
        else:
            raise ValueError('Unknown synthetic fixture operation')
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
    result.stderr || "Synthetic fixture setup failed",
  );
  if (["legacy-plan", "pre-ai-profile", "readonly"].includes(operation))
    fixtureSetup.push({
      operation,
      scope:
        "Explicit synthetic setup; RLS and immutable triggers remain enabled",
    });
  return JSON.parse(result.stdout);
}
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
      // Synchronous fixture setup can idle a pooled socket past the API's keep-alive
      // timeout; the next request would then be written to an already closed socket.
      Connection: "close",
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
      request.method() === "POST" &&
      /\/access-upgrade(?:s\/[^/]+\/actions\/[^/]+)?$/.test(url.pathname)
    )
      requestCounts.accessWrites++;
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
const card = (page) =>
  page.getByRole("article", { name: name + " access proposal", exact: true });
async function confirm(page, reason, state) {
  await label(page, "Reason").fill(reason);
  await button(page, "Confirm decision").click();
  await page
    .getByRole("status")
    .filter({ hasText: `access proposal ${state}. Change saved.` })
    .waitFor();
  await card(page).getByText(state, { exact: true }).waitFor();
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
const archive = (page) =>
  page.getByRole("region", { name: "Saved guidance archive", exact: true });
async function showArchive(page, text) {
  await button(page, "View saved guidance").click();
  await archive(page).getByText(text, { exact: false }).waitFor();
  await label(page, "Saved revision").waitFor();
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
  const focus = name.includes("archive") ? archive(page) : card(page);
  await focus.evaluate((element) => element.scrollIntoView({ block: "start" }));
  const file = path.join(local, `tola-ai-sprint-${name}-${width}.png`);
  await page.screenshot({ path: file, fullPage: false });
  screenshots.push({
    name: `${name} ${width}px`,
    file,
    synthetic: true,
    realProduct: true,
  });
  await page.setViewportSize({ width: 1440, height: 1050 });
}

let activePage;
let tenant;
let complete;
let firstRevision;
let secondRevision;
try {
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
      reason: "Synthetic browser access extension tenant",
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
    command({ reason: "Independent synthetic activation" }, tenant.revision_id),
  );
  const profile = await api("author", "/v1/platform/access-bootstraps");
  let initial = await api(
    "author",
    `/v1/platform/tenants/${tenant.tenant_id}/access-bootstrap`,
    command(
      {
        second_identity_id: fixture.actors.reviewer.identity_id,
        profile_hash: profile.profile_hash,
        role_names: ["PROGRAMME_MANAGER"],
        expires_at: new Date(Date.now() + 30 * DAY).toISOString(),
        reason: "Synthetic initial authority",
      },
      tenant.revision_id,
    ),
  );
  const bootstrap = `/v1/platform/access-bootstraps/${initial.request_id}/actions/`;
  initial = await api(
    "reviewer",
    bootstrap + "accept",
    command({ reason: "Synthetic second acceptance" }, initial.revision_id),
  );
  initial = await api(
    "admin",
    bootstrap + "approve",
    command({ reason: "Independent synthetic approval" }, initial.revision_id),
  );
  assert.equal(initial.state, "Applied");
  setup("pre-ai-profile", { tenant: tenant.tenant_id, access: initial });
  const before = setup("authority", { tenant: tenant.tenant_id });
  const previewPath = `/v1/platform/tenants/${tenant.tenant_id}/access-upgrade-preview`;
  const proposalPath = `/v1/platform/tenants/${tenant.tenant_id}/access-upgrade`;
  const aiRoute = `/v1/tenants/${tenant.tenant_id}/ai-enablement/catalog`;
  let proposed;
  const owner = await user("author", "Tenant lifecycle");
  activePage = owner;
  await test("Owner sees the real proposed AI capability delta; no authority applies on inspection", async () => {
    await owner
      .getByRole("combobox", { name: /^Organisation/ })
      .selectOption(tenant.tenant_id);
    await button(owner, "Propose access extension").waitFor();
    const preview = await api("author", previewPath);
    assert(preview.upgradable);
    assert(preview.new_capabilities.includes("ai.enablement.read"));
    await owner
      .getByRole("region", { name: "Available access extension", exact: true })
      .getByText("Review the additional capabilities", { exact: true })
      .click();
    for (const cap of preview.new_capabilities)
      await owner
        .getByRole("region", {
          name: "Available access extension",
          exact: true,
        })
        .locator("details")
        .first()
        .getByText(cap, { exact: true })
        .waitFor();
    await api("reviewer", aiRoute, undefined, 404);
    assert.deepEqual(setup("authority", { tenant: tenant.tenant_id }), before);
  });
  await test(
    "A lost real proposal response retries its exact operation and creates one request",
    async () => {
      await button(owner, "Propose access extension").click();
      await label(owner, "Reason").fill(
        "Synthetic reviewed AI access extension",
      );
      let requestBody;
      const handler = async (route) => {
        requestBody = route.request().postDataJSON();
        const response = await route.fetch();
        assert(response.ok(), await response.text());
        proposed = await response.json();
        injectedFailures.push({
          route: proposalPath,
          scope:
            "Actual proposal POST committed before its browser response was deliberately dropped",
        });
        await route.abort("failed");
      };
      await owner.route((url) => url.pathname === proposalPath, handler);
      await button(owner, "Confirm decision").click();
      await owner.getByRole("alert").waitFor();
      assert.equal(proposed.state, "Requested");
      await owner.unroute((url) => url.pathname === proposalPath, handler);
      // Remove all page-scoped handlers for this matcher; the context origin guard remains.
      await owner.unrouteAll({ behavior: "wait" });
      const pending = owner.waitForRequest(
        (r) =>
          new URL(r.url()).pathname === proposalPath && r.method() === "POST",
      );
      await button(owner, "Confirm decision").click();
      assert.deepEqual((await pending).postDataJSON(), requestBody);
      await card(owner).getByText("Requested", { exact: true }).waitFor();
      const rows = (
        await api("author", "/v1/platform/access-upgrades")
      ).items.filter((r) => r.tenant_id === tenant.tenant_id);
      assert.equal(rows.length, 1);
      assert.equal(rows[0].request_id, proposed.request_id);
      assert.deepEqual(setup("access-events", { tenant: tenant.tenant_id }), [
        "access-upgrade-request",
      ]);
      assert.deepEqual(
        setup("authority", { tenant: tenant.tenant_id }),
        before,
      );
    },
    "Actual POST committed; browser response deliberately dropped, then actual exact receipt retry",
  );
  const second = await user("reviewer", "Tenant lifecycle");
  activePage = second;
  await test("Named second administrator accepts the proposal without applying capabilities", async () => {
    await card(second).getByText("Requested", { exact: true }).waitFor();
    assert.equal(
      await card(second)
        .getByRole("button", { name: "Approve access extension", exact: true })
        .count(),
      0,
    );
    await card(second)
      .getByRole("button", { name: "Accept access proposal", exact: true })
      .click();
    await confirm(
      second,
      "Accept the exact synthetic capability proposal",
      "Accepted",
    );
    assert.deepEqual(setup("authority", { tenant: tenant.tenant_id }), before);
    await api("reviewer", aiRoute, undefined, 404);
    await mobile(second, 320, "access-accepted", ".tenant-console");
  });
  const operator = await user("admin", "Tenant lifecycle");
  activePage = operator;
  await test("Switching approval and rejection clears the reason and keeps the exact proposal explicit", async () => {
    const writes = requestCounts.accessWrites;
    const decision = operator.getByRole("region", {
      name: "Access extension decision",
      exact: true,
    });
    const proposalLabel =
      proposed.request_id.slice(0, 8) + "…" + proposed.request_id.slice(-4);
    await card(operator)
      .getByRole("button", { name: "Approve access extension", exact: true })
      .click();
    await label(operator, "Reason").fill("Synthetic reason only for approval");
    assert((await decision.innerText()).includes(name));
    assert((await decision.innerText()).includes(proposalLabel));
    await card(operator)
      .getByRole("button", { name: "Reject access proposal", exact: true })
      .click();
    await decision
      .getByRole("heading", { name: "Reject access proposal", exact: true })
      .waitFor();
    assert.equal(await label(operator, "Reason").inputValue(), "");
    assert((await decision.innerText()).includes(name));
    assert((await decision.innerText()).includes(proposalLabel));
    await label(operator, "Reason").fill("Synthetic reason only for rejection");
    await card(operator)
      .getByRole("button", { name: "Approve access extension", exact: true })
      .click();
    await decision
      .getByRole("heading", { name: "Approve access extension", exact: true })
      .waitFor();
    assert.equal(await label(operator, "Reason").inputValue(), "");
    assert((await decision.innerText()).includes(name));
    assert((await decision.innerText()).includes(proposalLabel));
    assert.equal(requestCounts.accessWrites, writes);
    assert.deepEqual(setup("authority", { tenant: tenant.tenant_id }), before);
    const row = (await api("admin", "/v1/platform/access-upgrades")).items.find(
      (item) => item.request_id === proposed.request_id,
    );
    assert.equal(row.state, "Accepted");
  });
  await test("Independent operator approval applies only the reviewed capabilities and keeps expiry", async () => {
    await card(operator)
      .getByRole("button", { name: "Approve access extension", exact: true })
      .click();
    await confirm(
      operator,
      "Independent synthetic capability review",
      "Applied",
    );
    const after = setup("authority", { tenant: tenant.tenant_id });
    assert(Object.keys(after).length > Object.keys(before).length);
    for (const [id, value] of Object.entries(before))
      assert.deepEqual(after[id], value);
    assert.deepEqual(
      [...new Set(Object.values(after).map((row) => row.expires_at))].sort(),
      [...new Set(Object.values(before).map((row) => row.expires_at))].sort(),
    );
    await api("reviewer", aiRoute);
    assert.deepEqual(setup("access-events", { tenant: tenant.tenant_id }), [
      "access-upgrade-request",
      "access-upgrade-accept",
      "access-upgrade-approve",
    ]);
    await scan(operator, "Applied access review desktop", ".tenant-console");
    await card(operator).evaluate((element) =>
      element.scrollIntoView({ block: "start" }),
    );
    const desktop = path.join(local, "tola-ai-sprint-access-desktop.png");
    await operator.screenshot({ path: desktop, fullPage: false });
    screenshots.push({
      name: "Applied access review desktop",
      file: desktop,
      synthetic: true,
      realProduct: true,
    });
    await mobile(operator, 390, "access-applied", ".tenant-console");
  });
  await test("Applied extension is unavailable for repeat proposal and an unrelated person sees no review", async () => {
    await button(owner, "Refresh access proposals").click();
    await owner
      .getByText(
        "The organisation already holds the available access profile.",
        { exact: true },
      )
      .waitFor();
    assert.equal(await button(owner, "Propose access extension").count(), 0);
    const other = await api("partner", "/v1/platform/access-upgrades");
    assert(!other.items.some((row) => row.request_id === proposed.request_id));
    await api("partner", previewPath, undefined, 404);
  });

  const author = await user("author", "AI enablement");
  activePage = author;
  const plansRoute = `/v1/tenants/${fixture.tenant_a}/ai-enablement/plans`;
  await test("Saving through the real workspace captures complete guidance for two immutable revisions", async () => {
    await label(author, "Plan name").fill("Synthetic archived guidance one");
    await label(author, "AI goal").fill(
      "Practise invented public workshop communication with human review.",
    );
    const first = author.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        new URL(r.url()).pathname === plansRoute,
    );
    await button(author, "Save adoption plan").click();
    const response = await first;
    assert.equal(response.status(), 201, await response.text());
    complete = await response.json();
    firstRevision = complete.revision_id;
    await button(author, "Save plan changes").waitFor();
    await label(author, "Plan name").fill("Synthetic archived guidance two");
    const second = author.waitForResponse(
      (r) =>
        r.request().method() === "PUT" &&
        new URL(r.url()).pathname === plansRoute + "/" + complete.object_id,
    );
    await button(author, "Save plan changes").click();
    const saved = await second;
    assert(saved.ok(), await saved.text());
    complete = await saved.json();
    secondRevision = complete.revision_id;
    assert.notEqual(firstRevision, secondRevision);
    await showArchive(
      author,
      "All three guides were archived for this revision.",
    );
    const history = await api(
      "author",
      plansRoute + "/" + complete.object_id + "/revisions",
    );
    assert.deepEqual(
      history.items.map((row) => row.revision_id),
      [secondRevision, firstRevision],
    );
  });
  await test("Real archived revision switching leaves unsaved draft and learning progress untouched", async () => {
    await label(author, "Plan name").fill("Unsaved synthetic working title");
    await button(author, "Build team capacity").click();
    const learning = author
      .getByRole("checkbox", { name: /^Complete learning step / })
      .first();
    const initialCheck = await learning.isChecked();
    await learning.setChecked(!initialCheck);
    const goal = await label(author, "AI goal").inputValue();
    const current = await api("author", plansRoute + "/" + complete.object_id);
    const counts = setup("counts");
    const writes = requestCounts.planWrites;
    const pending = author.waitForResponse(
      (r) =>
        r.request().method() === "GET" &&
        new URL(r.url()).pathname.endsWith(
          "/revisions/" + firstRevision + "/guidance",
        ),
    );
    await label(author, "Saved revision").selectOption(firstRevision);
    assert((await pending).ok());
    await archive(author)
      .getByText("All three guides were archived for this revision.", {
        exact: true,
      })
      .waitFor();
    await archive(author)
      .getByText(/^Learning and adoption guide ·/)
      .click();
    assert((await archive(author).getByRole("heading").count()) > 5);
    await label(author, "Saved revision").selectOption(secondRevision);
    await archive(author)
      .getByText("All three guides were archived for this revision.", {
        exact: true,
      })
      .waitFor();
    assert.equal(
      await label(author, "Plan name").inputValue(),
      "Unsaved synthetic working title",
    );
    assert.equal(await label(author, "AI goal").inputValue(), goal);
    assert.equal(await learning.isChecked(), !initialCheck);
    assert.equal(requestCounts.planWrites, writes);
    assert.deepEqual(
      await api("author", plansRoute + "/" + complete.object_id),
      current,
    );
    assert.deepEqual(setup("counts"), counts);
    await archive(author).evaluate((element) =>
      element.scrollIntoView({ block: "start" }),
    );
    const desktop = path.join(local, "tola-ai-sprint-archive-desktop.png");
    await author.screenshot({ path: desktop, fullPage: false });
    screenshots.push({
      name: "Complete guidance archive desktop",
      file: desktop,
      synthetic: true,
      realProduct: true,
    });
    await mobile(author, 320, "complete-archive", ".ai-adoption");
    await mobile(author, 390, "complete-archive", ".ai-adoption");
  });
  await test(
    "A failed archive read retries against the real backend without changing the draft",
    async () => {
      await button(author, "Hide saved guidance").click();
      let failed = 0;
      const matcher = (url) =>
        url.pathname.endsWith("/revisions/" + secondRevision + "/guidance");
      await author.route(matcher, async (route) => {
        failed++;
        injectedFailures.push({
          route: new URL(route.request().url()).pathname,
          scope:
            "One archive GET deliberately aborted for UI recovery; retry uses the actual backend",
        });
        await route.abort("failed");
      });
      await button(author, "View saved guidance").click();
      await archive(author).getByRole("alert").waitFor();
      assert.equal(failed, 1);
      await author.unroute(matcher);
      await button(author, "Hide saved guidance").click();
      await showArchive(
        author,
        "All three guides were archived for this revision.",
      );
      assert.equal(
        await label(author, "Plan name").inputValue(),
        "Unsaved synthetic working title",
      );
    },
    "Browser read failure deliberately injected; recovery fetch returns actual archived guidance",
  );

  const legacy = setup("legacy-plan", {
    title: "Synthetic pre-archive guidance",
    practice: false,
  });
  const oldPractice = setup("legacy-plan", {
    title: "Synthetic original practice retained",
    practice: true,
  });
  const update = structuredClone(oldPractice.data);
  delete update.content_versions;
  delete update.planning;
  update.title = "Synthetic partial archived guidance";
  const partial = await api(
    "admin",
    plansRoute + "/" + oldPractice.receipt.object_id,
    command(update, oldPractice.receipt.revision_id),
    200,
    "PUT",
  );
  setup("readonly");
  const reader = await user("reviewer", "AI enablement");
  activePage = reader;
  await test("A real read-only person reads complete history without save controls or writes", async () => {
    await openPlan(reader, complete.object_id);
    assert(await label(reader, "Plan name").isDisabled());
    assert.equal(await button(reader, "Save plan changes").count(), 0);
    assert.equal(await button(reader, "Save adoption plan").count(), 0);
    const beforeReads = setup("counts");
    const writes = requestCounts.planWrites;
    await showArchive(
      reader,
      "All three guides were archived for this revision.",
    );
    await label(reader, "Saved revision").selectOption(firstRevision);
    await archive(reader)
      .getByText("All three guides were archived for this revision.", {
        exact: true,
      })
      .waitFor();
    assert.equal(requestCounts.planWrites, writes);
    assert.deepEqual(setup("counts"), beforeReads);
    await scan(reader, "Read-only archive desktop", ".ai-adoption");
  });
  await test("Actual legacy revision reports unavailable guidance instead of reconstructing current wording", async () => {
    await openPlan(reader, legacy.receipt.object_id);
    await showArchive(reader, "No guidance archive exists for this revision.");
    const guidance = await api(
      "reviewer",
      plansRoute +
        "/" +
        legacy.receipt.object_id +
        "/revisions/" +
        legacy.receipt.revision_id +
        "/guidance",
    );
    assert.equal(guidance.status, "UNAVAILABLE");
    assert.equal(guidance.snapshot_sha256, null);
    await archive(reader)
      .getByText(/^Learning and adoption guide ·/)
      .click();
    await archive(reader)
      .getByText("This guide was not archived for this revision.", {
        exact: true,
      })
      .waitFor();
  });
  await test("Actual partial archive marks missing practice and preserves the original saved worksheet", async () => {
    await openPlan(reader, partial.object_id);
    await showArchive(
      reader,
      "Only some guides were archived for this revision.",
    );
    const guidance = await api(
      "reviewer",
      plansRoute +
        "/" +
        partial.object_id +
        "/revisions/" +
        partial.revision_id +
        "/guidance",
    );
    assert.equal(guidance.status, "PARTIAL");
    assert.equal(guidance.catalog.status, "AVAILABLE");
    assert.equal(guidance.solutions.status, "AVAILABLE");
    assert.equal(guidance.practice.status, "UNAVAILABLE");
    await archive(reader)
      .getByText(/^Manual practice guide ·/)
      .click();
    await archive(reader)
      .getByText(
        "The original practice guide was not archived for this revision.",
        { exact: false },
      )
      .waitFor();
    const current = await api("reviewer", plansRoute + "/" + partial.object_id);
    assert.deepEqual(current.data.planning, oldPractice.data.planning);
    assert.equal(
      current.data.content_versions.practice,
      "synthetic-unavailable-practice",
    );
    await label(reader, "Saved revision").selectOption(
      oldPractice.receipt.revision_id,
    );
    await archive(reader)
      .getByText("No guidance archive exists for this revision.", {
        exact: false,
      })
      .waitFor();
    await label(reader, "Saved revision").selectOption(partial.revision_id);
    await archive(reader)
      .getByText("Only some guides were archived for this revision.", {
        exact: false,
      })
      .waitFor();
    await mobile(reader, 320, "partial-archive", ".ai-adoption");
  });
  await test("Archive and access qualification makes no external or provider requests and has no uncaught errors", async () => {
    assert.deepEqual(blockedExternalRequests, []);
    assert.equal(requestCounts.advisory, 0);
    assert.deepEqual(errors, []);
    assert.deepEqual(
      consoleErrors.filter((record) => !expectedConsoleEvent(record)),
      [],
      "Unexpected browser console errors",
    );
    assert.deepEqual(
      await hashes(),
      qualifiedSources,
      "Product source changed during qualification",
    );
  });
} catch (error) {
  results.push({
    name: "Tola AI sprint browser run",
    status: "failed",
    message: error.message,
  });
  if (activePage && !activePage.isClosed())
    await activePage.screenshot({
      path: path.join(local, "tola-ai-sprint-browser-failure.png"),
      fullPage: true,
    });
  console.error(error.stack);
  process.exitCode = 1;
} finally {
  await fs.writeFile(
    evidenceFile,
    JSON.stringify(
      {
        build: JSON.parse(
          await fs.readFile(path.join(root, "VERSION.json"), "utf8"),
        ),
        started_at: startedAt,
        completed_at: new Date().toISOString(),
        browser_version: browser.version(),
        database:
          process.env.IMPACT_NATIVE_TEST === "1"
            ? "Disposable native PostgreSQL with provisioned logins through real FastAPI"
            : "Disposable in-memory PGlite through real FastAPI; this does not establish native-login security",
        fixture: "Synthetic identities and invented nonprofit facts only",
        qualification:
          "Dirty working tree development candidate; bounded evidence only",
        source_sha256: qualifiedSources,
        fixtureSetup,
        injectedFailures,
        results,
        accessibilityScans,
        screenshots,
        uncaughtErrors: errors,
        consoleErrors,
        expectedConsoleNetworkEvents: consoleErrors
          .map((record) => ({
            ...record,
            reason: expectedConsoleEvent(record),
          }))
          .filter((record) => record.reason),
        unexpectedConsoleErrors: consoleErrors.filter(
          (record) => !expectedConsoleEvent(record),
        ),
        blockedExternalRequests,
        requestCounts,
        limitations: [
          "Development sign-in fixture; live identity provider and deployment gates remain separate",
          "Passing local checks are development evidence, not production or nonprofit UAT acceptance",
        ],
      },
      null,
      2,
    ) + "\n",
  );
  await browser.close();
}
