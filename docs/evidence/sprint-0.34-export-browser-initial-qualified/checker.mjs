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
    "Use scripts/run.py ai-plan-export-browser on a disposable fixture.",
  );
const evidenceFile =
  process.env.IMPACT_BROWSER_EVIDENCE_FILE ||
  path.join(root, "docs/evidence/sprint-0.34-export-browser-tests.json");
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
const name = "Synthetic exact saved copy " + Date.now();
let browser,
  activePage,
  tenant,
  plan,
  currentRevision,
  olderRevision,
  qualifiedSources,
  qualifiedAssets,
  runtime,
  currentSources,
  currentAssets;
const expectedNegativeConsole = [];
const fixedSources = [
  "VERSION.json",
  "tools/browser/ai-plan-export-check.mjs",
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
const manifestKeys = [
  "plan_id",
  "revision_id",
  "title",
  "saved_at",
  "generated_at",
  "schema",
  "renderer",
  "filename",
  "media_type",
  "content_sha256",
  "size_bytes",
  "replay_expires_at",
  "guidance_status",
].sort();
const receiptKeys = [
  "object_id",
  "revision_id",
  "business_state",
  "operation_id",
  "correlation_id",
  "saved_at",
  "content_sha256",
  "byte_count",
  "replay_until",
].sort();
function verifyReply(reply, operation, revision) {
  assert.deepEqual(Object.keys(reply).sort(), [
    "content",
    "manifest",
    "receipt",
  ]);
  assert.deepEqual(Object.keys(reply.manifest).sort(), manifestKeys);
  assert.deepEqual(Object.keys(reply.receipt).sort(), receiptKeys);
  assert.equal(reply.manifest.plan_id, plan.object_id);
  assert.equal(reply.manifest.revision_id, revision);
  assert.equal(reply.receipt.operation_id, operation);
  assert.equal(reply.receipt.business_state, "Issued");
  assert.equal(reply.receipt.saved_at, reply.manifest.generated_at);
  assert.equal(reply.receipt.replay_until, reply.manifest.replay_expires_at);
  const bytes = Buffer.from(reply.content, "utf8"),
    digest = createHash("sha256").update(bytes).digest("hex");
  assert.equal(bytes.length, reply.manifest.size_bytes);
  assert.equal(bytes.length, reply.receipt.byte_count);
  assert.equal(digest, reply.manifest.content_sha256);
  assert.equal(digest, reply.receipt.content_sha256);
  assert.equal(reply.manifest.media_type, "application/json");
  assert.match(reply.manifest.filename, /^impact-ai-plan-[a-f0-9-]+\.json$/);
  const doc = JSON.parse(reply.content);
  assert.equal(doc.record_status, "Draft");
  assert.equal(doc.restriction, "INTERNAL_SELF");
  assert.deepEqual(doc.declared_components, [
    "PUBLIC_PLAN",
    "ARCHIVED_GUIDANCE",
  ]);
  assert.equal(doc.plan.object_id, plan.object_id);
  assert.equal(doc.plan.revision_id, revision);
  assert.equal(doc.guidance.status, reply.manifest.guidance_status);
  for (const forbidden of [
    "impact_reference",
    "human_advice",
    "provider_configuration",
    "requester_auth_time",
    "problem_sha256",
    "omitted_count",
    "linked_badge",
  ])
    assert(
      !JSON.stringify(doc).includes('"' + forbidden + '"'),
      "Public copy excludes private field " + forbidden,
    );
  return { bytes, digest, doc };
}

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
                if op in ('session-narrow','session-restore'):
                    identity=client.fixture['actors'][args['actor']]['identity_id']
                    if op=='session-narrow':
                        row=c.execute('SELECT session_id,auth_time FROM impact.web_session WHERE session_hash=%s AND identity_id=%s AND revoked_at IS NULL',
                          (bytes.fromhex(args['session_hash']),identity)).fetchone();assert row
                        c.execute("UPDATE impact.web_session SET auth_time=statement_timestamp()-interval '601 seconds' WHERE session_id=%s AND identity_id=%s",
                          (row['session_id'],identity))
                        answer={'actor':args['actor'],'tenant':tenant,'session_id':str(row['session_id']),'auth_time':row['auth_time'].isoformat()}
                    else:
                        changed=c.execute('UPDATE impact.web_session SET auth_time=%s WHERE session_id=%s AND identity_id=%s RETURNING session_id',
                          (args['auth_time'],args['session_id'],identity)).fetchone();assert changed
                        answer={'restored':True}
                elif op in ('narrow','restore'):
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
                elif op=='issuance':
                    row=c.execute('SELECT e.issuance_id,e.audit_revision_id,e.operation_id,e.plan_object_id,e.plan_revision_id,e.content_sha256,e.byte_count,b.body '
                      'FROM impact.ai_plan_export_issuance e JOIN impact.ai_plan_export_bytes b USING(tenant_id,issuance_id) WHERE e.tenant_id=%s AND e.operation_id=%s',
                      (tenant,args['operation_id'])).fetchone();assert row
                    raw=bytes(row['body']); answer={key:str(row[key])for key in ('issuance_id','audit_revision_id','operation_id','plan_object_id','plan_revision_id')}
                    answer.update(content_sha256=bytes(row['content_sha256']).hex(),body_sha256=hashlib.sha256(raw).hexdigest(),byte_count=row['byte_count'],body_byte_count=len(raw),
                      issuance_count=c.execute('SELECT count(*) AS n FROM impact.ai_plan_export_issuance WHERE tenant_id=%s AND operation_id=%s',(tenant,args['operation_id'])).fetchone()['n'],
                      audit_count=c.execute('SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_id=%s AND revision_id=%s',(tenant,row['issuance_id'],row['audit_revision_id'])).fetchone()['n'],
                      receipt_count=c.execute("SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND command_type='issue_ai_plan_export' AND operation_id=%s",(tenant,args['operation_id'])).fetchone()['n'])
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
async function openPlan(page) {
  await page
    .getByLabel("Saved adoption plans", { exact: true })
    .selectOption(plan.object_id);
  const response = page.waitForResponse(
    (r) =>
      r.request().method() === "GET" &&
      new URL(r.url()).pathname === planPath(),
  );
  await button(page, "Open saved plan").click();
  assert((await response).ok());
  await panel(page)
    .getByRole("heading", {
      name: "Internal copy of your saved plan",
      exact: true,
    })
    .waitFor();
}
async function options(page) {
  if (await button(page, "Prepare an internal saved copy").count())
    await button(page, "Prepare an internal saved copy").click();
  await panel(page)
    .getByLabel("Copy saved revision", { exact: true })
    .waitFor();
}
async function issue(page) {
  await options(page);
  await panel(page).getByRole("checkbox").check();
  const response = page.waitForResponse(
    (r) =>
      r.request().method() === "POST" &&
      new URL(r.url()).pathname.endsWith("/exports"),
  );
  await button(page, "Confirm and issue internal JSON copy").click();
  const result = await response;
  assert.equal(result.status(), 200);
  const reply = await result.json();
  await panel(page)
    .getByRole("group", { name: "Verified issued copy" })
    .waitFor();
  verifyReply(
    reply,
    result.request().postDataJSON().operation_id,
    new URL(result.url()).pathname.split("/").at(-2),
  );
  return reply;
}
async function download(page, expected) {
  const response = page.waitForResponse(
    (r) =>
      r.request().method() === "POST" &&
      new URL(r.url()).pathname.endsWith("/exports"),
  );
  const event = page.waitForEvent("download");
  await button(page, "Download issued copy").click();
  const result = await response;
  assert.equal(result.status(), 200);
  const replay = await result.json();
  assert.deepEqual(replay, expected);
  const copy = await event;
  assert.equal(copy.suggestedFilename(), expected.manifest.filename);
  const file = path.join(
    local,
    `ai-plan-export-download-${downloads.length + 1}.json`,
  );
  await copy.saveAs(file);
  const bytes = await fs.readFile(file);
  assert.deepEqual(bytes, Buffer.from(expected.content, "utf8"));
  const digest = createHash("sha256").update(bytes).digest("hex");
  assert.equal(digest, expected.manifest.content_sha256);
  downloads.push({
    file,
    filename: copy.suggestedFilename(),
    content_sha256: digest,
    byte_count: bytes.length,
    operation_id: expected.receipt.operation_id,
    revision_id: expected.manifest.revision_id,
  });
}
async function loseOneResponse(page, route) {
  let handled = false;
  const handler = async (intercepted) => {
    if (handled) return intercepted.continue();
    handled = true;
    try {
      const response = await intercepted.fetch();
      assert.equal(response.status(), 200);
      const result = await response.json();
      verifyReply(
        result,
        intercepted.request().postDataJSON().operation_id,
        new URL(route).pathname.split("/").at(-2),
      );
      injected.push({
        route: new URL(route).pathname,
        scope:
          "Actual export API committed; only its response was aborted to model ambiguous transport",
      });
      await intercepted.abort("failed");
    } catch (error) {
      errors.push("Response-loss handler: " + error.message);
      try {
        await intercepted.abort("failed");
      } catch {}
    } finally {
      await page.unroute(route, handler);
    }
  };
  await page.route(route, handler);
}
async function mobile(page, width) {
  await page.setViewportSize({ width, height: 900 });
  await button(page, "Download issued copy").focus();
  assert.equal(
    await button(page, "Download issued copy").evaluate(
      (el) => el === document.activeElement,
    ),
    true,
  );
  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth > innerWidth,
    ),
    false,
  );
  await page.evaluate(axeSource);
  const scan = await page.evaluate(async () =>
    window.axe.run({ include: [[".ai-plan-portability"]] }),
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
  scans.push({
    width,
    violations: scan.violations.map(shape),
    incomplete: scan.incomplete.map(shape),
  });
  assert.deepEqual(scan.violations, []);
  assert.deepEqual(scan.incomplete, []);
  const file = path.join(local, `ai-plan-export-${width}.png`);
  await page.screenshot({ path: file });
  const bytes = await fs.readFile(file);
  captures.push({
    width,
    file,
    sha256: createHash("sha256").update(bytes).digest("hex"),
    synthetic: true,
    realProduct: true,
  });
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
try {
  qualifiedSources = await hashes();
  qualifiedAssets = await servedHashes();
  await test(
    "Actual runtime and applied migrations match the frozen export source",
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
    "Fresh tenant and explicit manager export access require actual independent HTTP reviews",
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
          reason: "Synthetic export browser organisation",
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
          reason: "Reviewed manager export scope",
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
      for (const cap of [
        "ai.enablement.read",
        "ai.enablement.manage",
        "ai.enablement.export",
      ])
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
  activePage = await user("reviewer");
  await test("Unopened drafts have no export panel or export request", async () => {
    assert.equal(await panel(activePage).count(), 0);
    assert.equal(
      commands.filter((row) => row.path.endsWith("/exports")).length,
      0,
    );
    await openPlan(activePage);
    assert.equal(
      commands.filter((row) => row.path.endsWith("/exports")).length,
      0,
    );
  });
  let firstCopy, baseline;
  await test("Deliberate acknowledgement issues a saved draft copy and changes no plan head", async () => {
    baseline = setup("plan-heads", { tenant: tenant.tenant_id });
    const before = downloadEvents.length;
    firstCopy = await issue(activePage);
    assert.equal(firstCopy.manifest.guidance_status, "COMPLETE");
    assert.equal(downloadEvents.length, before);
    assert.deepEqual(
      setup("plan-heads", { tenant: tenant.tenant_id }),
      baseline,
    );
    const proof = setup("issuance", {
      tenant: tenant.tenant_id,
      operation_id: firstCopy.receipt.operation_id,
    });
    for (const key of ["issuance_count", "audit_count", "receipt_count"])
      assert.equal(proof[key], 1);
    assert.equal(proof.body_sha256, firstCopy.manifest.content_sha256);
    assert.equal(proof.body_byte_count, firstCopy.manifest.size_bytes);
  });
  await test("Actual browser download freshly replays the same issuance and matches retained database bytes", async () => {
    const before = commands.filter((row) => row.path.endsWith("/exports"));
    await download(activePage, firstCopy);
    const posts = commands.filter((row) => row.path.endsWith("/exports"));
    assert.equal(posts.length, before.length + 1);
    assert.deepEqual(posts.at(-1).body, before.at(-1).body);
    assert.deepEqual(
      setup("plan-heads", { tenant: tenant.tenant_id }),
      baseline,
    );
  });
  await test("Bounded authorised history selection preserves the parent draft and exact older guidance", async () => {
    const field = activePage.getByLabel("Plan name", { exact: true });
    const title = await field.inputValue();
    const before = commands.length;
    const history = activePage.waitForResponse(
      (r) =>
        r.request().method() === "GET" &&
        new URL(r.url()).pathname === planPath() + "/revisions",
    );
    await button(activePage, "Load authorised saved revisions").click();
    const page = await (await history).json();
    assert.equal(page.object_id, plan.object_id);
    assert(page.items.length <= 50);
    await panel(activePage)
      .getByLabel("Copy saved revision", { exact: true })
      .selectOption(olderRevision);
    assert.equal(
      await panel(activePage).getByRole("checkbox").isChecked(),
      false,
    );
    assert.equal(
      await panel(activePage)
        .getByRole("group", { name: "Verified issued copy" })
        .count(),
      0,
    );
    assert.equal(await field.inputValue(), title);
    assert.equal(commands.length, before);
    const older = await issue(activePage);
    assert.equal(older.manifest.revision_id, olderRevision);
    const archived = await api(
      "reviewer",
      planPath() + "/revisions/" + olderRevision + "/guidance",
    );
    assert.equal(older.manifest.guidance_status, archived.status);
    assert.deepEqual(JSON.parse(older.content).guidance, archived);
    assert.equal("planning" in JSON.parse(older.content).plan.data, false);
    await download(activePage, older);
    assert.deepEqual(
      setup("plan-heads", { tenant: tenant.tenant_id }),
      baseline,
    );
    await panel(activePage)
      .getByLabel("Copy saved revision", { exact: true })
      .selectOption(currentRevision);
    assert.equal(
      await panel(activePage).getByRole("checkbox").isChecked(),
      false,
    );
    assert.equal(await field.inputValue(), title);
  });
  await test("Lost actual download response retries the same issued manifest, receipt and operation", async () => {
    const copy = await issue(activePage);
    const original = commands
      .filter((row) => row.path.endsWith("/exports"))
      .at(-1);
    const before = downloadEvents.length;
    await loseOneResponse(activePage, base + exportPath());
    await button(activePage, "Download issued copy").click();
    await enabled(activePage, "Retry previous copy request");
    assert.equal(downloadEvents.length, before);
    assert.equal(
      await button(activePage, "Open saved plan").isDisabled(),
      true,
    );
    const response = activePage.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        new URL(r.url()).pathname === exportPath(),
    );
    const event = activePage.waitForEvent("download");
    await button(activePage, "Retry previous copy request").click();
    const result = await response;
    assert.equal(result.status(), 200);
    assert.deepEqual(await result.json(), copy);
    const file = path.join(
      local,
      `ai-plan-export-download-${downloads.length + 1}.json`,
    );
    const saved = await event;
    await saved.saveAs(file);
    const bytes = await fs.readFile(file);
    assert.deepEqual(bytes, Buffer.from(copy.content, "utf8"));
    downloads.push({
      file,
      filename: saved.suggestedFilename(),
      content_sha256: createHash("sha256").update(bytes).digest("hex"),
      byte_count: bytes.length,
      operation_id: copy.receipt.operation_id,
      revision_id: copy.manifest.revision_id,
    });
    const requests = commands.filter((row) => row.path.endsWith("/exports"));
    assert.deepEqual(requests.at(-1).body, original.body);
    assert.deepEqual(requests.at(-2).body, original.body);
    const proof = setup("issuance", {
      tenant: tenant.tenant_id,
      operation_id: original.body.operation_id,
    });
    for (const key of ["issuance_count", "audit_count", "receipt_count"])
      assert.equal(proof[key], 1);
  });
  await test("Lost actual issue response preserves the exact operation and local parent draft", async () => {
    await openPlan(activePage);
    await options(activePage);
    await panel(activePage).getByRole("checkbox").check();
    await loseOneResponse(activePage, base + exportPath());
    await button(activePage, "Confirm and issue internal JSON copy").click();
    await enabled(activePage, "Retry previous copy request");
    const original = commands
      .filter((row) => row.path.endsWith("/exports"))
      .at(-1);
    assert.equal(
      await button(activePage, "Open saved plan").isDisabled(),
      true,
    );
    assert.equal(
      await button(activePage, "New adoption plan").isDisabled(),
      true,
    );
    await activePage
      .getByLabel("Plan name", { exact: true })
      .fill(name + " local draft survives copy retry");
    const response = activePage.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        new URL(r.url()).pathname === exportPath(),
    );
    await button(activePage, "Retry previous copy request").click();
    const result = await response;
    assert.equal(result.status(), 200);
    const reply = await result.json();
    verifyReply(reply, original.body.operation_id, currentRevision);
    await panel(activePage)
      .getByRole("group", { name: "Verified issued copy" })
      .waitFor();
    assert.deepEqual(
      commands.filter((row) => row.path.endsWith("/exports")).at(-1).body,
      original.body,
    );
    assert.equal(
      await activePage.getByLabel("Plan name", { exact: true }).inputValue(),
      name + " local draft survives copy retry",
    );
    assert.equal(
      await button(activePage, "Download issued copy").isDisabled(),
      true,
    );
    assert.equal(
      setup("issuance", {
        tenant: tenant.tenant_id,
        operation_id: original.body.operation_id,
      }).issuance_count,
      1,
    );
  });
  await test("Actual stale browser authentication refuses replay and clears prior private state before deliberate reprepare", async () => {
    const stale = await user("reviewer");
    activePage = stale;
    await openPlan(stale);
    const issued = await issue(stale);
    const history = stale.waitForResponse(
      (r) =>
        r.request().method() === "GET" &&
        new URL(r.url()).pathname === planPath() + "/revisions",
    );
    await button(stale, "Load authorised saved revisions").click();
    assert.equal((await history).status(), 200);
    await panel(stale)
      .getByRole("option", { name: /Revision 1/ })
      .waitFor({ state: "attached" });
    const cookie = (await stale.context().cookies(base)).find(
      (row) => row.name === "impact_dev_session",
    );
    assert(cookie);
    const sessionHash = createHash("sha256").update(cookie.value).digest("hex");
    const narrowed = setup("session-narrow", {
      tenant: tenant.tenant_id,
      actor: "reviewer",
      session_hash: sessionHash,
    });
    narrowedSessions.push(narrowed);
    expectedNegativeConsole.push({ route: exportPath(), status: 403 });
    const before = downloadEvents.length;
    const response = stale.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        new URL(r.url()).pathname === exportPath(),
    );
    await button(stale, "Download issued copy").click();
    const refusal = await response;
    assert.equal(refusal.status(), 403);
    const problem = await refusal.json();
    assert.equal(problem.code, "ASSURANCE_REQUIRED");
    assert.equal(problem.reason_code, "FRESH_AUTHENTICATION_REQUIRED");
    await panel(stale)
      .getByRole("alert")
      .filter({ hasText: "unavailable with your current access" })
      .waitFor();
    assert.equal(
      await panel(stale)
        .getByRole("group", { name: "Verified issued copy" })
        .count(),
      0,
    );
    assert.equal(await button(stale, "Retry previous copy request").count(), 0);
    assert.equal(
      await panel(stale)
        .getByRole("option", { name: /Revision 1/ })
        .count(),
      0,
    );
    assert.equal(await panel(stale).getByRole("checkbox").isChecked(), false);
    assert.equal(
      await button(stale, "Confirm and issue internal JSON copy").isDisabled(),
      true,
    );
    assert.equal(await button(stale, "Open saved plan").isDisabled(), false);
    assert.equal(downloadEvents.length, before);
    assert.equal(
      setup("issuance", {
        tenant: tenant.tenant_id,
        operation_id: issued.receipt.operation_id,
      }).issuance_count,
      1,
    );
    restoreLatest(narrowedSessions, "session-restore");
    const fresh = await user("reviewer");
    activePage = fresh;
    await openPlan(fresh);
    await options(fresh);
    assert.equal(await panel(fresh).getByRole("checkbox").isChecked(), false);
    const copy = await issue(fresh);
    assert.notEqual(copy.receipt.operation_id, issued.receipt.operation_id);
    assert.equal(downloadEvents.length, before);
  });
  await test("Current server export authority loss clears earlier issued metadata despite the prior positive client hint", async () => {
    const fresh = await user("reviewer");
    activePage = fresh;
    await openPlan(fresh);
    const reply = await issue(fresh);
    const changed = setup("narrow", {
      tenant: tenant.tenant_id,
      actor: "reviewer",
      capability: "ai.enablement.export",
    });
    narrowed.push(changed);
    expectedNegativeConsole.push({ route: exportPath(), status: 404 });
    const before = downloadEvents.length;
    const response = fresh.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        new URL(r.url()).pathname.endsWith("/exports"),
    );
    await button(fresh, "Download issued copy").click();
    const denied = await response;
    assert.equal(denied.status(), 404);
    assert.equal((await denied.json()).code, "RESOURCE_UNAVAILABLE");
    await panel(fresh)
      .getByRole("alert")
      .filter({ hasText: "unavailable with your current access" })
      .waitFor();
    assert.equal(
      await panel(fresh)
        .getByRole("group", { name: "Verified issued copy" })
        .count(),
      0,
    );
    assert.equal(await button(fresh, "Retry previous copy request").count(), 0);
    assert.equal(downloadEvents.length, before);
    await api(
      "reviewer",
      exportPath(),
      {
        operation_id: reply.receipt.operation_id,
        data: {
          format: "JSON",
          restriction: "INTERNAL_SELF",
          acknowledged: true,
        },
      },
      404,
    );
    restoreLatest(narrowed);
  });
  await test("Separate current export permission can download with plan management narrowed", async () => {
    const changed = setup("narrow", {
      tenant: tenant.tenant_id,
      actor: "reviewer",
      capability: "ai.enablement.manage",
    });
    narrowed.push(changed);
    const access = await api("reviewer", tenantPath() + "me/access");
    assert(!access.capabilities.includes("ai.enablement.manage"));
    assert(access.capabilities.includes("ai.enablement.export"));
    const reader = await user("reviewer");
    activePage = reader;
    await openPlan(reader);
    assert.equal(await button(reader, "Save plan changes").count(), 0);
    const reply = await issue(reader);
    await download(reader, reply);
    restoreLatest(narrowed);
  });
  activePage = await user("reviewer");
  await openPlan(activePage);
  const displayCopy = await issue(activePage);
  for (const width of [1440, 390, 320])
    await test(`Actual saved-copy keyboard/mobile/accessibility ${width}px`, () =>
      mobile(activePage, width));
  await test("Qualified sources and served assets stayed fixed with no external or provider request", async () => {
    assert.equal(external.length, 0);
    assert.equal(errors.length, 0);
    assert.equal(
      downloadEvents.length,
      downloads.length,
      "Every offered browser file must be deliberately requested and byte-verified",
    );
    assert.equal(
      commands.filter((row) => row.path.endsWith("/advisory")).length,
      0,
    );
    assert.deepEqual(consoleErrors.filter(unexpectedConsole), []);
    currentSources = await hashes();
    currentAssets = await servedHashes();
    assert.deepEqual(currentSources, qualifiedSources);
    assert.deepEqual(currentAssets, qualifiedAssets);
    assert(displayCopy);
  });
} catch (error) {
  errors.push(error.stack || String(error));
  process.exitCode = 1;
  if (activePage)
    try {
      await activePage.screenshot({
        path: path.join(local, "ai-plan-export-failure.png"),
        fullPage: true,
      });
    } catch {}
} finally {
  for (const change of narrowedSessions)
    try {
      setup("session-restore", change);
    } catch (error) {
      errors.push("Fixture session restoration failed: " + error.message);
      process.exitCode = 1;
    }
  for (const change of narrowed)
    try {
      setup("restore", change);
    } catch (error) {
      errors.push("Fixture restoration failed: " + error.message);
      process.exitCode = 1;
    }
  if (!currentSources)
    try {
      currentSources = await hashes();
    } catch (error) {
      errors.push("Final source proof unavailable: " + error.message);
    }
  if (!currentAssets)
    try {
      currentAssets = await servedHashes();
    } catch (error) {
      errors.push("Final served proof unavailable: " + error.message);
    }
  await fs.mkdir(path.dirname(evidenceFile), { recursive: true });
  await fs.writeFile(
    evidenceFile,
    JSON.stringify(
      {
        scope:
          "Actual local Chrome/API/application database with synthetic internal-self bytes and independently reviewed fresh manager authority. Lost responses and grant narrowing are explicitly labelled. Passing local checks are development evidence, not production or nonprofit UAT acceptance.",
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
        downloads,
        browser_download_events: downloadEvents,
        screenshots: captures,
        accessibility_scans: scans,
        injected_failures: injected,
        fixture_setup: setupEvidence,
        runtime_qualification: runtime,
        write_requests: commands,
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
          "No hosted deployment, provider execution or nonprofit acceptance claim",
          "Read-only database observations use the explicitly privileged disposable fixture connection; API authority is the real application path, not a direct-login RLS claim",
          "Exposed principal/human identity reset is not a unique same-identity reauthentication generation",
          "Archived guidance unavailable/complete variants, expired storage-valid artifacts and broader native role/retention coverage remain separate backend or labelled fixture checks",
        ],
      },
      null,
      2,
    ) + "\n",
  );
  if (browser) await browser.close();
}
