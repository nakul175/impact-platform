import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
const require = createRequire(import.meta.url);
const axeSource = await fs.readFile(
  require.resolve("axe-core/axe.min.js"),
  "utf8",
);
const root = process.cwd();
const local = process.env.IMPACT_TEST_LOCAL;
const base = process.env.IMPACT_BASE_URL;
const evidenceFile =
  process.env.IMPACT_BROWSER_EVIDENCE_FILE ||
  path.join(root, "docs/evidence/ai-enablement-browser-tests.json");
if (
  !local ||
  !base ||
  new URL(base).hostname !== "127.0.0.1" ||
  process.env.IMPACT_ENVIRONMENT !== "test" ||
  process.env.IMPACT_ALLOW_FIXTURE_LOAD !== "1" ||
  process.env.IMPACT_PROCUREMENT_PREVIEW_QUALIFICATION !== "1" ||
  !process.env.IMPACT_BROWSER_EVIDENCE_FILE
)
  throw Error(
    "Root-gated procurement-preview qualification requires a disposable loopback fixture and named report",
  );
const startedAt = new Date().toISOString();
const fixture = JSON.parse(
  await fs.readFile(
    path.join(root, "specification/fixtures/api-fixture.json"),
    "utf8",
  ),
);
const captureDirectory =
  process.env.IMPACT_BROWSER_CAPTURE_DIRECTORY ||
  path.join(local, "procurement-preview-captures");
await fs.mkdir(captureDirectory, { recursive: true });
async function sourceHashes() {
  const files = new Set([
    "VERSION.json",
    "scripts/run.py",
    "scripts/fixture_support.py",
    "tools/browser/ai-enablement-check.mjs",
    "specification/fixtures/api-fixture.json",
    "specification/fixtures/records.json",
    "apps/web/dist/index.html",
  ]);
  for (const directory of [
    "apps/api/impact_api",
    "apps/web/src",
    "packages/contracts",
    "infrastructure/migrations",
    "qualification",
  ]) {
    const rows = await fs.readdir(path.join(root, directory), {
      withFileTypes: true,
    });
    assert(rows.length <= 1000, "Bounded source inventory");
    for (const row of rows)
      if (row.isFile() && /\.(py|json|tsx?|css|sql)$/.test(row.name))
        files.add(directory + "/" + row.name);
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
  const body = await response.text();
  assert.equal(
    body,
    await fs.readFile(path.join(root, "apps/web/dist/index.html"), "utf8"),
  );
  const assets = [
    ...new Set(
      [
        ...body.matchAll(
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
        const body = Buffer.from(await response.arrayBuffer());
        assert(body.length <= 10 * 1024 * 1024);
        assert.deepEqual(
          body,
          await fs.readFile(path.join(root, "apps/web/dist", asset.slice(1))),
        );
        return [asset, createHash("sha256").update(body).digest("hex")];
      }),
    ),
  );
}
let qualifiedSources, currentSources, qualifiedAssets, currentAssets;
const passwords = JSON.parse(
  await fs.readFile(path.join(local, "passwords.json"), "utf8"),
);
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
let page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
page.setDefaultTimeout(15000);
const results = [],
  errors = [],
  accessibilityScans = [],
  externalRequests = [],
  setupEvidence = [],
  narrowed = [];
let advisoryRequests = 0,
  planWrites = 0,
  catalogue,
  solutionDirectory,
  planId,
  planRoute;
async function observe(target) {
  await target.route("**/*", (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== new URL(base).origin) {
      externalRequests.push({
        method: route.request().method(),
        origin: url.origin,
        path: url.pathname,
      });
      return route.abort();
    }
    return route.continue();
  });
  target.on("request", (request) => {
    if (
      ["POST", "PUT"].includes(request.method()) &&
      /\/ai-enablement\/plans(?:\/[^/?]+)?$/.test(
        new URL(request.url()).pathname,
      )
    )
      planWrites++;
    if (
      request.method() === "POST" &&
      request.url().endsWith("/ai-enablement/advisory")
    )
      advisoryRequests += 1;
  });
  target.on("pageerror", (e) => errors.push(e.message));
}
await observe(page);
const button = (name) => page.getByRole("button", { name, exact: true });
const label = (name) => page.getByLabel(name, { exact: true });
const preview = () =>
  page.getByRole("group", { name: "Procurement draft preview", exact: true });
const procurementFields = [
  ["requirements", "Pilot requirements"],
  ["data_boundary", "Data boundary"],
  ["budget_notes", "Budget and nonprofit offer checks"],
  ["vendor_questions", "Questions for suppliers"],
];
async function readProcurement() {
  return Object.fromEntries(
    await Promise.all(
      procurementFields.map(async ([key, title]) => [
        key,
        await label(title).inputValue(),
      ]),
    ),
  );
}
async function fillProcurement(value) {
  for (const [key, title] of procurementFields)
    await label(title).fill(value[key]);
}
async function hiddenPreview() {
  await page.waitForFunction(
    () =>
      !document.querySelector(
        '[role="group"][aria-label="Procurement draft preview"]',
      ),
  );
  assert.equal(await button("Replace these four draft fields").count(), 0);
}
async function preparePreview() {
  await button("Preview draft from brief and shortlist").click();
  await preview().waitFor();
}
async function boundedWait(promise, title) {
  let timer;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(Error(title)), 20000);
      }),
    ]);
  } finally {
    clearTimeout(timer);
  }
}
async function reopenCurrentPlan() {
  await label("Saved adoption plans").selectOption(planId);
  const dirty =
    (await page
      .getByText("Unsaved changes to this shared draft.", { exact: true })
      .count()) > 0;
  const response = page.waitForResponse(
    (r) =>
      r.request().method() === "GET" && new URL(r.url()).pathname === planRoute,
  );
  await button("Open saved plan").click();
  const dialog = page.getByRole("dialog", {
    name: "Discard unsaved edits?",
    exact: true,
  });
  if (dirty) {
    await dialog.waitFor();
    await button("Discard edits and open plan").click();
  }
  const received = await response;
  assert(received.ok(), await received.text());
  await page.getByText("Saved plan opened.", { exact: false }).waitFor();
  return received.json();
}
async function getPlan() {
  const answer = await page.evaluate(async (route) => {
    const response = await fetch(route);
    return { status: response.status, body: await response.json() };
  }, planRoute);
  assert.equal(answer.status, 200);
  return answer.body;
}
function publicData(data) {
  const { content_versions, ...value } = data;
  return value;
}
function nonProcurement(data) {
  const { procurement, ...value } = publicData(data);
  return value;
}
function expectedProcurement(data) {
  const selected = data.solution_ids.map((id) =>
    solutionDirectory.solutions.find((row) => row.id === id),
  );
  assert(selected.every(Boolean));
  const suppliers =
    selected.map((row) => row.name).join(", ") || "a supplier to be selected";
  return {
    requirements: (
      "Pilot goal: " +
      data.profile.goal +
      "\nTeam: " +
      data.profile.team_size +
      " people.\nShortlist: " +
      suppliers +
      ".\nRequire human review of every output and a documented exit/export process."
    ).slice(0, 2000),
    data_boundary: data.profile.sensitive_data
      ? "The intended work involves sensitive information. Begin with synthetic material only. An authorised data steward must approve a specific data boundary, access controls, retention and supplier processing terms before any real data is used."
      : "Use synthetic or approved non-sensitive material in the pilot. Do not send participant identities, confidential records or credentials. Confirm retention, deletion and permissions before wider use.",
    budget_notes:
      "Request the total cost of the bounded pilot, including seats, API usage, onboarding, support, taxes and exit costs. Confirm any nonprofit eligibility and renewal conditions directly with the supplier.",
    vendor_questions: [
      ...catalogue.procurement_criteria.flatMap((row) => row.questions),
      ...selected.flatMap((row) => row.data_review_questions),
    ]
      .join("\n")
      .slice(0, 2000),
  };
}
// Existing disposable fixture authority helper pattern: narrow only an already
// granted capability and restore exactly those rows; no new grant/ceiling/role.
const fixturePython = String.raw`
import json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'qualification'))
from conftest import live
assert os.environ.get('IMPACT_ENVIRONMENT')=='test' and os.environ.get('IMPACT_ALLOW_FIXTURE_LOAD')=='1'
args=json.load(sys.stdin);generator=live.__wrapped__();client=next(generator)
try:
 with client.db() as c:
  tenant=client.fixture['tenant_a'];c.execute("SELECT set_config('impact.tenant_id',%s,true)",(tenant,))
  op=args['operation']
  if op=='narrow':
   rows=c.execute("SELECT g.object_id,g.purpose FROM impact.grant_current g JOIN impact.tenant_principal p ON p.tenant_id=g.tenant_id AND p.principal_id=g.subject_id WHERE g.tenant_id=%s AND p.identity_id=%s AND g.capability='ai.enablement.manage' AND g.purpose IS NULL",(tenant,client.fixture['actors']['author']['identity_id'])).fetchall();assert rows
   c.execute("UPDATE impact.grant_current SET purpose='SYNTHETIC_BROWSER_NARROWED' WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",(tenant,[str(row['object_id']) for row in rows]))
   answer={'grants':[{'object_id':str(row['object_id']),'purpose':row['purpose']}for row in rows]}
  elif op=='restore':
   for row in args['grants']:c.execute('UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s',(row['purpose'],tenant,row['object_id']))
   answer={'restored':len(args['grants'])}
  elif op=='state':
   obj=args['object_id'];row=c.execute('SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s',(tenant,obj)).fetchone();assert row
   answer={'head_revision':str(row['head_revision']),
    'revisions':c.execute('SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s',(tenant,obj)).fetchone()['n'],
    'audits':c.execute("SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s AND action_type IN ('create_ai_adoption_plan','update_ai_adoption_plan')",(tenant,obj)).fetchone()['n'],
    'outbox':c.execute("SELECT count(*) AS n FROM impact.outbox_event WHERE tenant_id=%s AND payload->>'aggregate_id'=%s",(tenant,obj)).fetchone()['n'],
    'receipts':c.execute("SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND command_type IN ('create_ai_adoption_plan','update_ai_adoption_plan') AND outcome->>'object_id'=%s",(tenant,obj)).fetchone()['n']}
  else:raise ValueError('Unknown bounded fixture operation')
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
    "Bounded synthetic fixture helper failed; raw credential-bearing diagnostic withheld",
  );
  setupEvidence.push({
    operation,
    scope: ["narrow", "restore"].includes(operation)
      ? "Explicit disposable-fixture narrowing/restoration of exact preexisting management grants; no role/profile/ceiling/RLS/immutable change"
      : "Read-only current plan head/revision and its existing audit/outbox/receipt counts",
  });
  return JSON.parse(result.stdout);
}
async function test(name, fn) {
  await fn();
  results.push({ name, status: "passed" });
  console.log("PASS " + name);
}
async function login(username) {
  await page.goto(base);
  await label("Username").fill(username);
  await label("Password").fill(passwords[username]);
  await button("Sign in →").click();
  await button("AI enablement").waitFor();
  const catalogResponse = page.waitForResponse((r) =>
    r.url().endsWith("/ai-enablement/catalog"),
  );
  const solutionResponse = page.waitForResponse((r) =>
    r.url().endsWith("/ai-enablement/solutions"),
  );
  await button("AI enablement").click();
  catalogue = await (await catalogResponse).json();
  solutionDirectory = await (await solutionResponse).json();
  await page.getByText(/tools shown · 0 of 4 selected/).waitFor();
}
async function savedResponse(action) {
  const response = page.waitForResponse(
    (r) =>
      ["POST", "PUT"].includes(r.request().method()) &&
      /\/ai-enablement\/plans(?:\/[^/?]+)?$/.test(new URL(r.url()).pathname),
  );
  await action();
  const received = await response;
  return received;
}
async function assertUsableComparison(products) {
  const columns = await page
    .locator(".ai-comparison thead th:not(:first-child)")
    .evaluateAll((headers) =>
      headers.map((header) => ({
        width: header.getBoundingClientRect().width,
        height: header.getBoundingClientRect().height,
      })),
    );
  assert.equal(columns.length, products);
  assert(
    columns.every((column) => column.width >= 180),
    "A comparison product column collapsed below readable width",
  );
  assert(
    columns.every((column) => column.height < 180),
    "A product heading wraps into an excessively tall column",
  );
  const heights = await page
    .locator(".ai-comparison tbody tr")
    .evaluateAll((rows) =>
      rows.map((row) => row.getBoundingClientRect().height),
    );
  assert(
    heights.every((height) => height < 700),
    "A comparison row becomes excessively tall",
  );
}
async function scanAccessibility(name) {
  if (!(await page.evaluate(() => Boolean(window.axe))))
    await page.evaluate(axeSource);
  const scan = await page.evaluate(async () =>
    window.axe.run(
      { include: [[".ai-enablement"]] },
      {
        runOnly: {
          type: "tag",
          values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"],
        },
        resultTypes: ["violations", "incomplete"],
      },
    ),
  );
  const shape = (issue) => ({
    id: issue.id,
    impact: issue.impact,
    help: issue.help,
    nodes: issue.nodes.map((node) => ({
      target: node.target,
      summary: node.failureSummary,
    })),
  });
  accessibilityScans.push({
    name,
    violations: scan.violations.map(shape),
    incomplete: scan.incomplete.map(shape),
  });
  const failures = scan.violations.filter((issue) =>
    ["serious", "critical"].includes(issue.impact),
  );
  assert.equal(
    failures.length,
    0,
    JSON.stringify(failures.map(shape), null, 2),
  );
}
try {
  qualifiedSources = await sourceHashes();
  qualifiedAssets = await servedHashes();
  await login("author");
  await test("Open the working tool directory with published sources and honest transaction limits", async () => {
    await page
      .getByRole("heading", {
        name: "AI enablement for nonprofits",
        exact: true,
      })
      .waitFor();
    await page
      .getByRole("heading", { name: "Your AI adoption plan", exact: true })
      .waitFor();
    await page.getByText("Source review date:", { exact: false }).waitFor();
    assert(solutionDirectory.solutions.length >= 5);
    assert(
      (await page.locator('.ai-sources a[href^="https://"]').count()) >=
        solutionDirectory.solutions.length,
    );
    await page
      .getByText("This directory does not accept orders or book suppliers.", {
        exact: false,
      })
      .waitFor();
  });
  await test("Assess readiness without a model call and clear stale results when the brief changes", async () => {
    await label("AI goal").fill(
      "Improve our synthetic programme communication drafts.",
    );
    await label("Sector").selectOption("EDUCATION");
    await label("Team size").fill("8");
    const response = page.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        r.url().endsWith("/ai-enablement/assessment"),
    );
    await button("Assess readiness").click();
    const received = await response;
    assert(received.ok(), await received.text());
    assert.equal(
      (await received.json()).assessment.method,
      "DETERMINISTIC_RULES",
    );
    await page
      .getByRole("heading", { name: /^Readiness assessment/ })
      .waitFor();
    await label("AI goal").fill(
      "Prepare a synthetic staff communication pilot.",
    );
    assert.equal(
      await page
        .getByRole("heading", { name: /^Readiness assessment/ })
        .count(),
      0,
    );
  });
  await test("Search and filter published tools, and cap a side-by-side comparison at four", async () => {
    const first = solutionDirectory.solutions[0];
    await label("Search tools").fill(first.name);
    assert.equal(
      await page.locator(".ai-adoption .ai-cards article").count(),
      1,
    );
    await label("Search tools").fill("");
    const category = solutionDirectory.solutions.find(
      (item) => item.category === "TRANSLATION",
    ).category;
    await label("Tool category").selectOption(category);
    assert.equal(
      await page.locator(".ai-adoption .ai-cards article").count(),
      solutionDirectory.solutions.filter((item) => item.category === category)
        .length,
    );
    await label("Tool category").selectOption("");
    await button("Compare " + first.name).click();
    await assertUsableComparison(1);
    await page.setViewportSize({ width: 390, height: 844 });
    await assertUsableComparison(1);
    await page.setViewportSize({ width: 1440, height: 1050 });
    for (const solution of solutionDirectory.solutions.slice(1, 5))
      await button("Compare " + solution.name).click();
    await page
      .getByText("Choose up to four tools.", { exact: false })
      .waitFor();
    assert.equal(await page.locator(".ai-comparison thead th").count(), 5);
    await assertUsableComparison(4);
    await page.setViewportSize({ width: 390, height: 844 });
    await assertUsableComparison(4);
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
      "Four-tool comparison expands the mobile page",
    );
    await page.setViewportSize({ width: 1440, height: 1050 });
    for (const solution of solutionDirectory.solutions.slice(2, 4))
      await button("Remove " + solution.name).click();
    assert.equal(await page.locator(".ai-comparison thead th").count(), 3);
    await page
      .getByRole("rowheader", { name: "Nonprofit offer", exact: true })
      .waitFor();
  });
  await test("Use a practical lesson, self-check, procurement draft and pilot tracker", async () => {
    await label("Plan name").fill("Synthetic nonprofit adoption pilot");
    await button("Build team capacity").click();
    const firstPath = catalogue.learning_paths[0];
    await label("Complete learning step " + firstPath.lessons[0].key).check();
    if (firstPath.lessons?.length) {
      const lesson = firstPath.lessons[0];
      await page.getByText("Lesson: " + lesson.title, { exact: true }).click();
      await page
        .getByRole("radio", {
          name: lesson.check.options[lesson.check.answer],
          exact: true,
        })
        .check();
      await page
        .getByText("Correct. " + lesson.check.explanation, { exact: true })
        .waitFor();
    }
    await button("Procurement brief").click();
    const beforePreview = await readProcurement(),
      beforeWrites = planWrites;
    await preparePreview();
    assert.deepEqual(await readProcurement(), beforePreview);
    assert.equal(planWrites, beforeWrites);
    await button("Replace these four draft fields").click();
    await hiddenPreview();
    assert(
      (await label("Pilot requirements").inputValue()).includes(
        "Prepare a synthetic staff communication pilot.",
      ),
    );
    assert((await label("Questions for suppliers").inputValue()).length > 0);
    await label("Budget and nonprofit offer checks").fill(
      "Confirm a bounded synthetic pilot cost with the purchasing owner.",
    );
    await button("Pilot tracker").click();
    await label("Pilot success measure").fill(
      "Every synthetic draft is checked against its source by a reviewer.",
    );
    await label("Define the goal and a measurable success criterion").check();
  });
  await test("Procurement confirmation is discarded after observed edit and undo, profile change, shortlist change or an empty goal", async () => {
    await button("Procurement brief").click();
    const original = await readProcurement(),
      beforeWrites = planWrites;
    for (const [key, title] of procurementFields) {
      await preparePreview();
      await label(title).fill(original[key] + " — transient synthetic edit");
      await hiddenPreview();
      await label(title).fill(original[key]);
      await hiddenPreview();
    }
    const name = await label("Plan name").inputValue(),
      goal = await label("AI goal").inputValue();
    for (const [title, value] of [
      ["Plan name", name],
      ["AI goal", goal],
    ]) {
      await preparePreview();
      await label(title).fill(value + " — transient edit");
      await hiddenPreview();
      await label(title).fill(value);
      await hiddenPreview();
    }
    await preparePreview();
    await button("Find and compare tools").click();
    await button("Remove " + solutionDirectory.solutions[1].name).click();
    await button("Compare " + solutionDirectory.solutions[1].name).click();
    await button("Procurement brief").click();
    await hiddenPreview();
    assert.deepEqual(await readProcurement(), original);
    await label("AI goal").fill("");
    await page.waitForFunction(() =>
      [...document.querySelectorAll("button")].some(
        (node) =>
          node.textContent.trim() ===
            "Preview draft from brief and shortlist" && node.disabled,
      ),
    );
    await label("AI goal").fill(goal);
    await hiddenPreview();
    assert.equal(planWrites, beforeWrites);
  });
  await test("A lost save response retries the same operation and keeps newer edits unsaved", async () => {
    const sent = [];
    let active = true;
    let notify, release;
    const held = new Promise((resolve) => {
      notify = resolve;
    });
    const released = new Promise((resolve) => {
      release = resolve;
    });
    const match = (url) => url.pathname.endsWith("/ai-enablement/plans");
    const intercept = async (route) => {
      if (!active || route.request().method() !== "POST")
        return route.fallback();
      sent.push(route.request().postDataJSON());
      if (sent.length === 1) {
        const response = await route.fetch();
        assert(response.ok(), await response.text());
        const receipt = await response.json();
        planId = receipt.object_id;
        planRoute = new URL(route.request().url()).pathname + "/" + planId;
        notify();
        await released;
        await route.abort("connectionfailed");
      } else await route.fallback();
    };
    await page.route(match, intercept);
    await button("Procurement brief").click();
    const originalFields = await readProcurement();
    await preparePreview();
    await button("Save adoption plan").click();
    try {
      await boundedWait(
        held,
        "Actual save did not reach its held committed-response boundary",
      );
      await hiddenPreview();
      assert(
        await button("Preview draft from brief and shortlist").isDisabled(),
      );
      assert.deepEqual(await readProcurement(), originalFields);
      const current = await getPlan();
      assert.deepEqual(current.data.procurement, originalFields);
      const state = setup("state", { object_id: planId });
      assert.deepEqual(
        [state.revisions, state.audits, state.outbox, state.receipts],
        [1, 1, 1, 1],
      );
    } finally {
      release();
    }
    await button("Retry previous save").waitFor();
    assert(await button("Preview draft from brief and shortlist").isDisabled());
    await label("Plan name").fill("Newer unsaved edits remain visible");
    const received = await savedResponse(() =>
      button("Retry previous save").click(),
    );
    assert(received.ok(), await received.text());
    assert.equal(sent.length, 2);
    assert.deepEqual(sent[0], sent[1]);
    const state = setup("state", { object_id: planId });
    assert.deepEqual(
      [state.revisions, state.audits, state.outbox, state.receipts],
      [1, 1, 1, 1],
    );
    await page.getByText("Plan saved.", { exact: false }).waitFor();
    assert.equal(
      await label("Plan name").inputValue(),
      "Newer unsaved edits remain visible",
    );
    await page
      .getByText("Unsaved changes to this shared draft.", { exact: true })
      .waitFor();
    active = false;
    await page.unroute(match, intercept);
    const update = await savedResponse(() =>
      button("Save plan changes").click(),
    );
    assert(update.ok(), await update.text());
    await page
      .getByText("This shared draft is saved.", { exact: true })
      .waitFor();
  });
  await test("Reopening a saved plan restores shortlist, readiness, learning, procurement and pilot progress", async () => {
    await page.reload();
    await button("AI enablement").click();
    await label("Saved adoption plans").selectOption(planId);
    await button("Open saved plan").click();
    await page.getByText("Saved plan opened.", { exact: false }).waitFor();
    assert.equal(
      await label("Plan name").inputValue(),
      "Newer unsaved edits remain visible",
    );
    assert.equal(
      await label("AI goal").inputValue(),
      "Prepare a synthetic staff communication pilot.",
    );
    assert.equal(await label("Team size").inputValue(), "8");
    assert.equal(await page.locator(".ai-comparison thead th").count(), 3);
    await button("Build team capacity").click();
    assert(
      await label(
        "Complete learning step " + catalogue.learning_paths[0].lessons[0].key,
      ).isChecked(),
    );
    await button("Procurement brief").click();
    assert.equal(
      await label("Budget and nonprofit offer checks").inputValue(),
      "Confirm a bounded synthetic pilot cost with the purchasing owner.",
    );
    await button("Pilot tracker").click();
    assert(
      await label(
        "Define the goal and a measurable success criterion",
      ).isChecked(),
    );
    assert(
      (await label("Pilot success measure").inputValue()).includes(
        "synthetic draft",
      ),
    );
  });
  await test("Preview and cancel leave exact stored work intact; explicit replacement changes only four fields before normal save and reopen", async () => {
    await button("Procurement brief").click();
    const own = {
      requirements:
        "=Preserve our manually written synthetic requirements — Café समुदाय",
      data_boundary:
        "Preserve our bounded synthetic boundary and human review.",
      budget_notes:
        "Preserve our synthetic budget notes; zero is an entered amount.",
      vendor_questions:
        "Preserve our own synthetic questions, with no supplier contact.",
    };
    await fillProcurement(own);
    const save = await savedResponse(() => button("Save plan changes").click());
    assert(save.ok(), await save.text());
    const baseline = await reopenCurrentPlan();
    assert.deepEqual(baseline.data.procurement, own);
    const beforeWrites = planWrites,
      counts = setup("state", { object_id: planId });
    await preparePreview();
    assert.deepEqual(await readProcurement(), own);
    await page
      .getByText("Your procurement fields already contain work.", {
        exact: false,
      })
      .waitFor();
    for (const [width, height] of [
      [1440, 1050],
      [390, 844],
      [320, 844],
    ]) {
      await page.setViewportSize({ width, height });
      await preview().scrollIntoViewIfNeeded();
      assert(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth + 1,
        ),
        "Procurement preview expands the viewport",
      );
      await button("Preview draft from brief and shortlist").focus();
      await page.keyboard.press("Tab");
      assert(
        await button("Replace these four draft fields").evaluate(
          (node) => node === document.activeElement,
        ),
      );
      await page.keyboard.press("Tab");
      assert(
        await button("Keep my procurement fields unchanged").evaluate(
          (node) => node === document.activeElement,
        ),
      );
      await scanAccessibility(`Procurement replacement preview ${width}px`);
      await page.screenshot({
        path: path.join(captureDirectory, `procurement-preview-${width}.png`),
        fullPage: false,
      });
    }
    await page.setViewportSize({ width: 1440, height: 1050 });
    await button("Keep my procurement fields unchanged").click();
    await hiddenPreview();
    assert.deepEqual(await readProcurement(), own);
    assert.deepEqual(await getPlan(), baseline);
    assert.deepEqual(setup("state", { object_id: planId }), counts);
    assert.equal(planWrites, beforeWrites);
    await preparePreview();
    const expected = expectedProcurement(baseline.data);
    for (const [key, title] of procurementFields) {
      const section = preview()
        .locator("section")
        .filter({
          has: page.getByRole("heading", { name: title, exact: true }),
        });
      assert.equal(
        await section.locator(".ai-draft").textContent(),
        expected[key],
      );
    }
    await button("Replace these four draft fields").click();
    await hiddenPreview();
    assert.deepEqual(await readProcurement(), expected);
    assert.deepEqual(await getPlan(), baseline);
    assert.deepEqual(setup("state", { object_id: planId }), counts);
    assert.equal(planWrites, beforeWrites);
    let submitted;
    const capture = (request) => {
      if (
        request.method() === "PUT" &&
        new URL(request.url()).pathname === planRoute
      )
        submitted = request.postDataJSON();
    };
    page.on("request", capture);
    try {
      const response = await savedResponse(() =>
        button("Save plan changes").click(),
      );
      assert(response.ok(), await response.text());
    } finally {
      page.off("request", capture);
    }
    assert(submitted);
    assert.equal(submitted.expected_revision, baseline.revision_id);
    assert.deepEqual(submitted.data.procurement, expected);
    assert.deepEqual(
      nonProcurement(submitted.data),
      nonProcurement(baseline.data),
    );
    const current = await reopenCurrentPlan();
    assert.notEqual(current.revision_id, baseline.revision_id);
    assert.deepEqual(current.data.procurement, expected);
    assert.deepEqual(
      nonProcurement(current.data),
      nonProcurement(baseline.data),
    );
    const after = setup("state", { object_id: planId });
    assert.deepEqual(
      [after.revisions, after.audits, after.outbox, after.receipts],
      [
        counts.revisions + 1,
        counts.audits + 1,
        counts.outbox + 1,
        counts.receipts + 1,
      ],
    );
    await button("Procurement brief").click();
    assert.deepEqual(await readProcurement(), expected);
  });
  await test("A stale shared-plan save preserves local edits and leaves the current server revision intact", async () => {
    const changedTitle = "Another colleague's synthetic revision";
    const result = await page.evaluate(
      async ({ route, title }) => {
        const me = await (await fetch("/auth/me")).json();
        const plan = await (await fetch(route)).json();
        const { content_versions, ...data } = plan.data;
        const response = await fetch(route, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": me.csrf_token,
          },
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            expected_revision: plan.revision_id,
            data: { ...data, title },
          }),
        });
        return { status: response.status, body: await response.json() };
      },
      { route: planRoute, title: changedTitle },
    );
    assert.equal(result.status, 200, JSON.stringify(result.body));
    await label("Plan name").fill("My synthetic edits survive the conflict");
    const received = await savedResponse(() =>
      button("Save plan changes").click(),
    );
    assert.equal(received.status(), 409);
    await page
      .getByText("This plan changed since you opened it.", { exact: false })
      .waitFor();
    assert.equal(
      await label("Plan name").inputValue(),
      "My synthetic edits survive the conflict",
    );
    assert.equal(await button("Open saved plan").isDisabled(), false);
    const current = await page.evaluate(
      async (route) => (await fetch(route)).json(),
      planRoute,
    );
    assert.equal(current.data.title, changedTitle);
    await button("Open saved plan").click();
    await page
      .getByRole("dialog", { name: "Discard unsaved edits?", exact: true })
      .waitFor();
    await button("Keep editing").click();
    assert.equal(
      await label("Plan name").inputValue(),
      "My synthetic edits survive the conflict",
    );
    await button("Open saved plan").click();
    await button("Discard edits and open plan").click();
    await page.getByText("Saved plan opened.", { exact: false }).waitFor();
    assert.equal(await label("Plan name").inputValue(), changedTitle);
  });
  await test("A freshly opened same-valued server revision invalidates a previous procurement confirmation", async () => {
    await button("Procurement brief").click();
    const baseline = await getPlan(),
      fields = await readProcurement();
    await preparePreview();
    const result = await page.evaluate(async (route) => {
      const me = await (await fetch("/auth/me")).json(),
        current = await (await fetch(route)).json();
      const { content_versions, ...data } = current.data;
      const response = await fetch(route, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": me.csrf_token,
        },
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          expected_revision: current.revision_id,
          data,
        }),
      });
      return { status: response.status, body: await response.json() };
    }, planRoute);
    assert.equal(result.status, 200, JSON.stringify(result.body));
    assert.notEqual(result.body.revision_id, baseline.revision_id);
    const refreshed = await reopenCurrentPlan();
    assert.equal(refreshed.revision_id, result.body.revision_id);
    assert.deepEqual(publicData(refreshed.data), publicData(baseline.data));
    await button("Procurement brief").click();
    await hiddenPreview();
    assert.deepEqual(await readProcurement(), fields);
  });
  await test("Cached positive management hints do not grant saving authority after actual management revocation", async () => {
    await button("Procurement brief").click();
    const baseline = await getPlan(),
      counts = setup("state", { object_id: planId });
    await label("Plan name").fill(
      "Local synthetic draft after a current-management refusal",
    );
    await preparePreview();
    const change = setup("narrow");
    narrowed.push(change);
    try {
      // Local text preparation is deliberately distinct from current server
      // authority. Cached hints can allow a local edit; the real save must refuse.
      await button("Replace these four draft fields").click();
      await hiddenPreview();
      const response = await savedResponse(() =>
        button("Save plan changes").click(),
      );
      assert.equal(response.status(), 404);
      assert.equal((await response.json()).code, "RESOURCE_UNAVAILABLE");
      assert.equal(
        await label("Plan name").inputValue(),
        "Local synthetic draft after a current-management refusal",
      );
      assert.deepEqual(await getPlan(), baseline);
      assert.deepEqual(setup("state", { object_id: planId }), counts);
    } finally {
      setup("restore", change);
      narrowed.pop();
    }
    await reopenCurrentPlan();
    await button("Procurement brief").click();
    assert.deepEqual(await readProcurement(), baseline.data.procurement);
  });
  await test("Disabled advisory sends no requests, and the product fits desktop and 390 px mobile views", async () => {
    await page
      .getByText("AI advisory is not configured for this workspace.", {
        exact: false,
      })
      .waitFor();
    assert(await button("Request AI advisory draft").isDisabled());
    assert.equal(advisoryRequests, 0);
    assert.equal(
      await label("I consent to sending this brief to OpenAI").count(),
      0,
    );
    await button("Find and compare tools").click();
    await page
      .getByRole("heading", { name: "Your AI adoption plan", exact: true })
      .scrollIntoViewIfNeeded();
    await page.screenshot({
      path: path.join(captureDirectory, "ai-enablement-desktop.png"),
      fullPage: false,
    });
    await page
      .getByRole("heading", { name: "Your tool comparison", exact: true })
      .scrollIntoViewIfNeeded();
    await assertUsableComparison(2);
    await page.screenshot({
      path: path.join(captureDirectory, "ai-enablement-comparison.png"),
      fullPage: false,
    });
    await page.setViewportSize({ width: 390, height: 844 });
    await page
      .getByRole("heading", { name: "Your tool comparison", exact: true })
      .scrollIntoViewIfNeeded();
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
      "AI workspace overflows at 390 px",
    );
    assert(
      await page.locator(".ai-cards article").evaluateAll((cards) =>
        cards.every((card) => {
          const bounds = card.getBoundingClientRect();
          return [...card.querySelectorAll("button")].every((button) => {
            const target = button.getBoundingClientRect();
            return target.left >= bounds.left && target.right <= bounds.right;
          });
        }),
      ),
      "A tool button extends outside its card on mobile",
    );
    await page.screenshot({
      path: path.join(captureDirectory, "ai-enablement-mobile.png"),
      fullPage: false,
    });
    assert.deepEqual(errors, []);
  });
  await test("New product sections and discard confirmation have no serious or critical automated WCAG findings", async () => {
    await page.setViewportSize({ width: 1440, height: 1050 });
    for (const name of [
      "Find and compare tools",
      "Build team capacity",
      "Procurement brief",
      "Pilot tracker",
    ]) {
      await button(name).click();
      await scanAccessibility(name);
    }
    await label("Pilot success measure").fill(
      "Synthetic accessibility-check draft remains unsaved.",
    );
    await button("Open saved plan").click();
    await page
      .getByRole("dialog", { name: "Discard unsaved edits?", exact: true })
      .waitFor();
    await scanAccessibility("Discard confirmation");
    await button("Keep editing").click();
  });
  await test("An existing read-only actor can browse tools but cannot save plans or record completion", async () => {
    page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
    page.setDefaultTimeout(15000);
    await observe(page);
    await login("other_tenant");
    await page
      .getByText("Saving an adoption plan requires separate permission", {
        exact: false,
      })
      .waitFor();
    assert.equal(await button("Save adoption plan").count(), 0);
    assert.equal(await button("New adoption plan").count(), 0);
    assert(await label("Plan name").isDisabled());
    await button("Compare " + solutionDirectory.solutions[0].name).click();
    await page
      .getByRole("heading", { name: "Your tool comparison", exact: true })
      .waitFor();
    await button("Build team capacity").click();
    assert(
      await label(
        "Complete learning step " + catalogue.learning_paths[0].lessons[0].key,
      ).isDisabled(),
    );
    await button("Procurement brief").click();
    assert(await label("Pilot requirements").isDisabled());
    assert.equal(
      await button("Preview draft from brief and shortlist").count(),
      0,
    );
    assert.equal(await button("Replace these four draft fields").count(), 0);
    assert.deepEqual(errors, []);
  });
  assert.equal(advisoryRequests, 0);
  assert.deepEqual(externalRequests, []);
  currentSources = await sourceHashes();
  currentAssets = await servedHashes();
  assert.deepEqual(currentSources, qualifiedSources);
  assert.deepEqual(currentAssets, qualifiedAssets);
} catch (e) {
  results.push({
    name: "AI enablement browser run",
    status: "failed",
    message: e.message,
  });
  await page.screenshot({
    path: path.join(captureDirectory, "ai-enablement-browser-failure.png"),
    fullPage: true,
  });
  console.error(e.message);
  process.exitCode = 1;
} finally {
  for (const change of narrowed.reverse()) setup("restore", change);
  currentSources ??= await sourceHashes();
  currentAssets ??= await servedHashes();
  await fs.writeFile(
    evidenceFile,
    JSON.stringify(
      {
        engine: process.env.IMPACT_BROWSER_EXECUTABLE
          ? "Configured Chromium browser"
          : "Chromium 153",
        results,
        uncaughtErrors: errors,
        accessibilityScans,
        scope:
          "Proposed next-release checker; when deliberately executed, actual local Chrome/HTTP with synthetic disposable data, normal plan save, current-authority refusal and exact stored plan audit/outbox/receipt counts. No provider or supplier action.",
        started_at: startedAt,
        finished_at: new Date().toISOString(),
        source_sha256_start: qualifiedSources,
        source_sha256_end: currentSources,
        served_assets_sha256_start: qualifiedAssets,
        served_assets_sha256_end: currentAssets,
        source_changed_during_run: Object.keys(qualifiedSources ?? {}).filter(
          (file) => currentSources?.[file] !== qualifiedSources[file],
        ),
        externalRequests,
        planWrites,
        advisoryRequests,
        setupEvidence,
        limitations: [
          "Historical catalog/criterion mutation and management-hint loss-return cycles remain separate private model/synthetic cases; this checker does not claim an actual live catalog deployment change.",
          "Purpose narrowing/restoration is only an explicit disposable fixture negative, never ordinary product grant creation.",
          "Outbox rows are transaction intents, not supplier messages or deliveries.",
          "No hosted/native-role/nonprofit acceptance or provider execution claim; accessibility incompletes are retained.",
        ],
      },
      null,
      2,
    ),
  );
  await browser.close();
}
