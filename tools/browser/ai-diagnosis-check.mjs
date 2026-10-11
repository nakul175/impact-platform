import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { createHash, randomUUID } from "node:crypto";
import { spawnSync } from "node:child_process";

// US-DX-01a, AC-US-DX-01a-001/002. Running this file, rather than its presence,
// produces the bounded local browser evidence. No provider is used or mocked.
const require = createRequire(import.meta.url);
const root = process.cwd();
const local = process.env.IMPACT_TEST_LOCAL;
const base = process.env.IMPACT_BASE_URL;
if (
  !local ||
  !base ||
  new URL(base).hostname !== "127.0.0.1" ||
  new URL(base).protocol !== "http:" ||
  process.env.IMPACT_ENVIRONMENT !== "test" ||
  process.env.IMPACT_ALLOW_FIXTURE_LOAD !== "1"
)
  throw Error(
    "Use scripts/run.py ai-diagnosis-browser with a disposable loopback test fixture",
  );
const origin = new URL(base).origin;
const startedAt = new Date().toISOString();
const fixture = JSON.parse(
  await fs.readFile(
    path.join(root, "specification/fixtures/api-fixture.json"),
    "utf8",
  ),
);
assert.equal(
  fixture.allow_mutations,
  true,
  "Fixture must explicitly allow synthetic mutations",
);
const evidenceFile =
  process.env.IMPACT_BROWSER_EVIDENCE_FILE ||
  path.join(root, "docs/evidence/ai-diagnosis-browser-tests.json");
const captureDirectory =
  process.env.IMPACT_BROWSER_CAPTURE_DIRECTORY ||
  path.join(local, "ai-diagnosis-captures");
await fs.mkdir(captureDirectory, { recursive: true });
await fs.mkdir(path.dirname(evidenceFile), { recursive: true });
const passwords = JSON.parse(
  await fs.readFile(path.join(local, "passwords.json"), "utf8"),
);
const axeSource = await fs.readFile(
  require.resolve("axe-core/axe.min.js"),
  "utf8",
);
const suite = [
  [
    "DX-B01",
    "Actual loopback runtime, served assets and migration/source pins",
  ],
  [
    "DX-B02",
    "Keyboard priority movement, exact evidence save and reopen",
    "AC-US-DX-01a-001",
  ],
  [
    "DX-B03",
    "Missing evidence and priority name the incomplete problem and do not complete",
    "AC-US-DX-01a-002",
  ],
  [
    "DX-B04",
    "Actual completion is read-only; explicit correction preserves completed history",
  ],
  [
    "DX-B05",
    "A real stale revision preserves local edits until explicit current-version review",
  ],
  [
    "DX-B06",
    "A lost actual committed response retries exact bytes with one set of effects",
  ],
  [
    "DX-B07",
    "Current read-grant loss refuses receipt replay and clears private details",
  ],
  [
    "DX-B08",
    "Sign-out, different-tenant sign-in and a delayed old read reset all diagnosis state",
  ],
  [
    "DX-B09",
    "Responsive diagnosis accessibility and stable final evidence pins",
  ],
];
const results = [],
  accessibilityScans = [],
  externalRequests = [],
  forbiddenRequests = [],
  pageErrors = [],
  requestFailures = [],
  setupEvidence = [],
  commands = [],
  mutations = [],
  narrowed = [];
let activeCase,
  browser,
  page,
  sourceStart,
  sourceEnd,
  assetsStart,
  assetsEnd,
  runtime,
  migrationsStart,
  migrationsEnd,
  providerStart,
  providerEnd,
  created,
  current,
  lastReplay;
const safeMessage = (value) =>
  String(value)
    .replace(/Bearer\s+[^\s"']+/g, "Bearer [withheld]")
    .replace(
      /(?:postgres(?:ql)?:\/\/)[^\s"']+/g,
      "[database connection withheld]",
    );
const tick = () => {
  if (activeCase) activeCase.assertions += 1;
};
const eq = (actual, expected, message) => {
  tick();
  assert.equal(actual, expected, message);
};
const same = (actual, expected, message) => {
  tick();
  assert.deepEqual(actual, expected, message);
};
const truth = (value, message) => {
  tick();
  assert(value, message);
};
const sha = (bytes) => createHash("sha256").update(bytes).digest("hex");
const copy = (value) => JSON.parse(JSON.stringify(value));
const diagnosisRoute = `/v1/tenants/${fixture.tenant_a}/ai-enablement/diagnoses`;
const objectRoute = () => diagnosisRoute + "/" + created.object_id;
const region = () => page.locator(".ai-diagnosis");
const button = (name) => page.getByRole("button", { name, exact: true });
const label = (name) => page.getByLabel(name, { exact: true });
const diagnosisButton = (name) =>
  region().getByRole("button", { name, exact: true });
const diagnosisLabel = (name) => region().getByLabel(name, { exact: true });

async function sourceHashes() {
  const files = new Set([
    "VERSION.json",
    "scripts/run.py",
    "scripts/fixture_support.py",
    "tools/browser/ai-diagnosis-check.mjs",
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
      [...files]
        .sort()
        .map(async (file) => [
          file,
          sha(await fs.readFile(path.join(root, file))),
        ]),
    ),
  );
}
async function servedHashes() {
  const response = await fetch(base, { redirect: "error" });
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
  assert(assets.length && assets.length <= 32);
  const hashes = { "/": sha(body) };
  for (const asset of assets) {
    assert(!asset.includes(".."));
    const response = await fetch(new URL(asset, base), { redirect: "error" });
    assert.equal(response.status, 200);
    const body = Buffer.from(await response.arrayBuffer());
    assert(body.length <= 10 * 1024 * 1024);
    assert.deepEqual(
      body,
      await fs.readFile(path.join(root, "apps/web/dist", asset.slice(1))),
    );
    hashes[asset] = sha(body);
  }
  return hashes;
}

// Only disposable fixture reads, real fresh-auth local HTTP and temporary purpose
// narrowing/restoration of exact preexisting read grants are available here.
// No identity, role, grant, ceiling, RLS or immutable-row creation/alteration.
const fixturePython = String.raw`
import json,os,re,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'qualification'))
from conftest import live
assert os.environ.get('IMPACT_ENVIRONMENT')=='test' and os.environ.get('IMPACT_ALLOW_FIXTURE_LOAD')=='1'
args=json.load(sys.stdin);generator=live.__wrapped__();client=next(generator)
try:
 assert client.fixture['allow_mutations'] is True
 tenant=client.fixture['tenant_a'];op=args['operation']
 if op=='api':
  actor=args.get('actor','admin');method=args.get('method','GET');route=args['path']
  selected=client.fixture['tenant_b'] if actor=='other_tenant' else tenant
  allowed='/v1/tenants/'+selected+'/ai-enablement/diagnoses'
  suffix=route[len(allowed):] if route.startswith(allowed) else '!'
  uuid=r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
  assert actor in ('admin','other_tenant') and method in ('GET','POST','PUT')
  assert re.fullmatch(r'(?:/'+uuid+r'(?:/revisions(?:/'+uuid+r')?|/actions/(?:complete|revise))?)?',suffix)
  assert actor=='admin' or method=='GET'
  response=client.request(route,actor=actor,method=method,body=args.get('body'))
  answer={'status':response.status_code,'body':response.json()}
 else:
  with client.db() as c:
   c.execute("SELECT set_config('impact.tenant_id',%s,true)",(tenant,))
   if op=='runtime':answer={'migrations':c.execute('SELECT version,sha256 FROM impact.schema_migration ORDER BY version').fetchall()}
   elif op=='provider_counts':
    answer={table:c.execute('SELECT count(*) AS n FROM impact.'+table+' WHERE tenant_id=%s',(tenant,)).fetchone()['n'] for table in ('ai_advisory_request','ai_advisory_result')}
   elif op=='narrow_read':
    rows=c.execute("SELECT object_id,purpose FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s AND capability='ai.diagnosis.read' AND purpose IS NULL",(tenant,client.fixture['actors']['admin']['principal_id'])).fetchall();assert rows
    c.execute("UPDATE impact.grant_current SET purpose='SYNTHETIC_BROWSER_NARROWED' WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",(tenant,[str(row['object_id']) for row in rows]))
    answer={'grants':[{'object_id':str(row['object_id']),'purpose':row['purpose']} for row in rows]}
   elif op=='restore':
    for row in args['grants']:c.execute('UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s',(row['purpose'],tenant,row['object_id']))
    answer={'restored':len(args['grants'])}
   elif op=='state':
    obj=args['object_id'];row=c.execute('SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s',(tenant,obj)).fetchone();assert row
    actions=('create_ai_diagnosis','update_ai_diagnosis','complete_ai_diagnosis','revise_ai_diagnosis')
    answer={'head_revision':str(row['head_revision']),
     'revisions':c.execute('SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s',(tenant,obj)).fetchone()['n'],
     'audits':c.execute('SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s AND action_type=ANY(%s::text[])',(tenant,obj,list(actions))).fetchone()['n'],
     'outbox':c.execute("SELECT count(*) AS n FROM impact.outbox_event WHERE tenant_id=%s AND payload->>'aggregate_id'=%s",(tenant,obj)).fetchone()['n'],
     'receipts':c.execute("SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND command_type=ANY(%s::text[]) AND outcome->>'object_id'=%s",(tenant,list(actions),obj)).fetchone()['n']}
   else:raise ValueError('Unknown bounded fixture operation')
 print(json.dumps(answer,default=str))
finally:generator.close()
`;
function setup(operation, args = {}) {
  const result = spawnSync(
    process.env.IMPACT_QUALIFICATION_PYTHON ||
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
    scope:
      operation === "api"
        ? "Real loopback HTTP using a freshly signed existing fixture actor; no manufactured response"
        : ["narrow_read", "restore"].includes(operation)
          ? "Temporary narrowing/restoration of exact preexisting disposable diagnosis read grants; no role/ceiling/RLS/history change"
          : "Read-only actual disposable migration, diagnosis effects or advisory-row counts",
  });
  return JSON.parse(result.stdout);
}
function api(route = objectRoute(), method = "GET", body, actor = "admin") {
  const answer = setup("api", { path: route, method, body, actor });
  if (method !== "GET")
    mutations.push({
      method,
      path: route,
      actor,
      request_sha256: sha(JSON.stringify(body)),
      operation_id: body.operation_id,
      status: answer.status,
      response: answer.body,
    });
  return answer;
}
function readCurrent() {
  const answer = api();
  eq(answer.status, 200, "Actual saved diagnosis can be read");
  return answer.body;
}
const state = () => setup("state", { object_id: created.object_id });
function observeEffects(before, after, changes, message) {
  eq(after.revisions - before.revisions, changes, message + ": revision count");
  eq(after.audits - before.audits, changes, message + ": domain audit count");
  eq(after.outbox - before.outbox, changes, message + ": outbox intent count");
  eq(after.receipts - before.receipts, changes, message + ": receipt count");
  if (!changes)
    eq(after.head_revision, before.head_revision, message + ": head revision");
  activeCase.observations.push({
    message,
    before,
    after,
    expected_sets_of_effects: changes,
  });
}
async function test(index, fn) {
  const [id, name, criterion] = suite[index];
  activeCase = {
    id,
    name,
    criterion: criterion || null,
    status: "running",
    assertions: 0,
    observations: [],
    started_at: new Date().toISOString(),
  };
  try {
    await fn();
    activeCase.status = "passed";
    console.log("PASS " + id + " " + name);
  } catch (error) {
    activeCase.status = "failed";
    activeCase.message = safeMessage(error.message);
    throw error;
  } finally {
    activeCase.finished_at = new Date().toISOString();
    results.push(activeCase);
    activeCase = null;
  }
}
async function bounded(promise, message) {
  let timer;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(Error(message)), 20000);
      }),
    ]);
  } finally {
    clearTimeout(timer);
  }
}
function deferred() {
  let resolve;
  const promise = new Promise((done) => {
    resolve = done;
  });
  return { promise, resolve };
}
async function observe(target) {
  await target.route("**/*", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.origin !== origin) {
      externalRequests.push({
        method: request.method(),
        origin: url.origin,
        path: url.pathname,
      });
      return route.abort("blockedbyclient");
    }
    if (
      /\/(?:advisory|providers?)(?:\/|$)/.test(url.pathname) ||
      (request.method() !== "GET" &&
        /\/ai-(?:jobs|requests)(?:\/|$)/.test(url.pathname))
    ) {
      forbiddenRequests.push({ method: request.method(), path: url.pathname });
      return route.abort("blockedbyclient");
    }
    return route.continue();
  });
  target.on("request", (request) => {
    const route = new URL(request.url()).pathname;
    if (
      ["POST", "PUT"].includes(request.method()) &&
      route.startsWith(diagnosisRoute)
    )
      commands.push({
        method: request.method(),
        path: route,
        body: request.postData(),
        body_sha256: sha(request.postData() || ""),
      });
  });
  target.on("pageerror", (error) =>
    pageErrors.push(safeMessage(error.message)),
  );
  target.on("requestfailed", (request) =>
    requestFailures.push({
      method: request.method(),
      path: new URL(request.url()).pathname,
      error: request.failure()?.errorText,
    }),
  );
}
async function openWorkspace() {
  await button("AI enablement").waitFor();
  await button("AI enablement").click();
  await region()
    .getByRole("heading", {
      name: "Your organisation's priorities",
      exact: true,
    })
    .waitFor();
  await diagnosisLabel("Saved diagnoses").waitFor();
  await page.waitForFunction(
    () =>
      !document
        .querySelector(".ai-diagnosis")
        ?.textContent.includes("Loading saved diagnoses…"),
  );
}
async function login(username, diagnosis = true) {
  await page.goto(base);
  await label("Username").fill(username);
  await label("Password").fill(passwords[username]);
  await button("Sign in →").click();
  await label("Workspace").waitFor();
  if (diagnosis) await openWorkspace();
  else {
    await button("AI enablement").waitFor();
    await button("AI enablement").click();
  }
}
async function logout() {
  await button("Sign out").click();
  await label("Username").waitFor();
}
async function openSaved() {
  const expected = page.waitForResponse(
    (response) =>
      response.request().method() === "GET" &&
      new URL(response.url()).pathname === objectRoute(),
  );
  await diagnosisLabel("Saved diagnoses").selectOption(created.object_id);
  const response = await expected;
  eq(response.status(), 200, "Browser opens the actual current saved object");
  const value = await response.json();
  await page.waitForFunction(
    (revision) =>
      document
        .querySelector(".ai-diagnosis")
        ?.getAttribute("data-diagnosis-revision") === revision,
    value.revision_id,
  );
  return value;
}
async function writeFromUI(
  name,
  route = objectRoute(),
  method = "PUT",
  expected = 200,
) {
  const ready = page.waitForResponse(
    (response) =>
      response.request().method() === method &&
      new URL(response.url()).pathname === route,
  );
  await diagnosisButton(name).click();
  const response = await ready;
  eq(response.status(), expected, "Actual browser command outcome");
  const answer = await response.json();
  if (expected < 300)
    await page.waitForFunction(
      (revision) =>
        document
          .querySelector(".ai-diagnosis")
          ?.getAttribute("data-diagnosis-revision") === revision,
      answer.revision_id,
    );
  return answer;
}
async function scan(name) {
  if (!(await page.evaluate(() => Boolean(window.axe))))
    await page.evaluate(axeSource);
  const answer = await page.evaluate(async () =>
    window.axe.run(
      { include: [[".ai-diagnosis"]] },
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
    engine: answer.testEngine,
    violations: answer.violations.map(shape),
    incomplete: answer.incomplete.map(shape),
  });
  eq(
    answer.violations.filter((issue) =>
      ["serious", "critical"].includes(issue.impact),
    ).length,
    0,
    name + ": no serious/critical automated WCAG findings",
  );
}

async function qualifyDelayedReadAfterActualCollectionRefusal() {
  const protectedTitle =
    "Synthetic delayed private diagnosis must stay unavailable";
  const initial = state();
  const listSeen = deferred();
  const releaseListToServer = deferred();
  const listFinished = deferred();
  const objectSeen = deferred();
  const releaseObject = deferred();
  const objectFinished = deferred();
  let savedObject;
  let grantChange;
  let activeList = true;
  let activeObject = false;
  const collectionMatch = (url) =>
    url.origin === origin && url.pathname === diagnosisRoute;
  const objectMatch = new URL(objectRoute(), base).href;

  const holdCollection = async (route) => {
    if (!activeList || route.request().method() !== "GET")
      return route.fallback();
    activeList = false;
    listSeen.resolve();
    await releaseListToServer.promise;
    try {
      // The original browser refresh reaches the actual server only after the
      // real preexisting read-grant purpose has been narrowed. No 404 is invented.
      const response = await route.fetch({ maxRedirects: 0, timeout: 20000 });
      const body = await response.json();
      await route.fulfill({ response });
      listFinished.resolve({ status: response.status(), body });
    } catch (error) {
      listFinished.resolve({ error: safeMessage(error.message) });
    }
  };
  const holdObject = async (route) => {
    if (!activeObject || route.request().method() !== "GET")
      return route.fallback();
    activeObject = false;
    try {
      // Capture the actual authorised object read before grant loss. Retain its
      // real response, rather than manufacturing a readable object after denial.
      const response = await route.fetch({ maxRedirects: 0, timeout: 20000 });
      assert.equal(response.status(), 200);
      savedObject = await response.json();
      objectSeen.resolve();
      await releaseObject.promise;
      try {
        await route.fulfill({ response });
        objectFinished.resolve(
          "Authentic old 200 delivered after actual list refusal",
        );
      } catch {
        objectFinished.resolve(
          "Prior object read aborted after actual list refusal",
        );
      }
    } catch (error) {
      objectSeen.resolve({ error: safeMessage(error.message) });
      objectFinished.resolve("Prior object read could not be captured");
    }
  };

  await page.route(collectionMatch, holdCollection);
  await page.route(objectMatch, holdObject);
  try {
    await diagnosisLabel("Diagnosis title").fill(protectedTitle);
    await writeFromUI("Save diagnosis draft");
    current = readCurrent();
    const savedCounts = state();
    observeEffects(
      initial,
      savedCounts,
      1,
      "Race setup uses one actual coherent UI save",
    );
    await bounded(
      listSeen.promise,
      "Automatic actual saved-list refresh did not reach its held request boundary",
    );

    // List refresh sets loading but does not lock the existing saved selector.
    // Capture a concurrent authorised object 200 while that refresh is pending.
    activeObject = true;
    await diagnosisLabel("Saved diagnoses").selectOption(created.object_id);
    const issue = await bounded(
      objectSeen.promise,
      "Concurrent actual object GET did not reach its held response boundary",
    );
    truth(!issue?.error, issue?.error);
    same(
      savedObject,
      current,
      "Held readable object is the actual newly saved server revision",
    );

    grantChange = setup("narrow_read");
    narrowed.push(grantChange);
    const actualDenied = api();
    eq(
      actualDenied.status,
      404,
      "Independent actual current read now refuses this object",
    );
    eq(actualDenied.body.code, "RESOURCE_UNAVAILABLE");
    releaseListToServer.resolve();
    const listOutcome = await bounded(
      listFinished.promise,
      "Held collection refresh did not receive its actual current-authority refusal",
    );
    truth(!listOutcome.error, listOutcome.error);
    eq(
      listOutcome.status,
      404,
      "The browser collection request received a real server refusal",
    );
    eq(listOutcome.body.code, "RESOURCE_UNAVAILABLE");
    await region()
      .getByText(
        "The diagnosis is unavailable. Refresh your access before continuing.",
        { exact: true },
      )
      .waitFor();

    await page.evaluate(() => {
      const element = document.querySelector(".ai-diagnosis");
      const sample = () => ({
        revision: element.getAttribute("data-diagnosis-revision"),
        state: element.getAttribute("data-diagnosis-state"),
      });
      window.__diagnosisAuthorityRaceSamples = [sample()];
      window.__diagnosisAuthorityRaceObserver = new MutationObserver(() => {
        window.__diagnosisAuthorityRaceSamples.push(sample());
      });
      window.__diagnosisAuthorityRaceObserver.observe(element, {
        attributes: true,
        attributeFilter: ["data-diagnosis-revision", "data-diagnosis-state"],
      });
    });
    releaseObject.resolve();
    const delivery = await bounded(
      objectFinished.promise,
      "Old object response was not delivered or cancelled after collection refusal",
    );
    const authoritySamples = await page.evaluate(async () => {
      // Drain response microtasks and two real browser paint opportunities.
      await new Promise(requestAnimationFrame);
      await new Promise(requestAnimationFrame);
      window.__diagnosisAuthorityRaceObserver.disconnect();
      return window.__diagnosisAuthorityRaceSamples;
    });
    truth(
      authoritySamples.every(
        (sample) => sample.revision === "" && sample.state === "Unsaved",
      ),
      "No observed late-response DOM mutation resurrects a private head or state",
    );
    // Await actual late-transport completion, then inspect state as well as
    // content. Hidden controls alone would miss a resurrected private head.
    eq(
      await region().getAttribute("data-diagnosis-revision"),
      "",
      "Delayed authorised 200 cannot restore private revision after actual refusal",
    );
    eq(
      await region().getAttribute("data-diagnosis-state"),
      "Unsaved",
      "Delayed authorised 200 cannot restore private lifecycle state after actual refusal",
    );
    eq(await diagnosisLabel("Diagnosis title").count(), 0);
    eq(await diagnosisLabel("Saved diagnoses").count(), 0);
    eq(await region().locator("li[data-problem-id]").count(), 0);
    eq(
      await diagnosisButton("Load more diagnoses").count(),
      0,
      "No prior pagination cursor remains available after authority loss",
    );
    truth(!(await region().innerText()).includes(protectedTitle));
    truth(
      !(await region().innerText()).includes(
        current.data.problems[0].supporting_evidence,
      ),
    );
    observeEffects(
      savedCounts,
      state(),
      0,
      "Collection refusal and delayed old read cannot save, restore or overwrite history",
    );
    activeCase.observations.push({
      case: "authentic delayed authorised object 200 after actual collection 404",
      captured_revision_id: savedObject.revision_id,
      captured_object_sha256: sha(JSON.stringify(savedObject)),
      actual_collection_status: listOutcome.status,
      late_transport_outcome: delivery,
      authority_dom_samples: authoritySamples,
      observed_revision_after_release: await region().getAttribute(
        "data-diagnosis-revision",
      ),
      observed_state_after_release: await region().getAttribute(
        "data-diagnosis-state",
      ),
    });
  } finally {
    activeList = false;
    activeObject = false;
    releaseListToServer.resolve();
    releaseObject.resolve();
    await page.unroute(collectionMatch, holdCollection);
    await page.unroute(objectMatch, holdObject);
    if (grantChange) {
      setup("restore", grantChange);
      narrowed.splice(narrowed.indexOf(grantChange), 1);
    }
  }
  await page.reload();
  await openWorkspace();
  await openSaved();
  same(
    readCurrent(),
    current,
    "Restoring only original grant purposes and fresh workspace scope leaves the coherent saved object intact",
  );
}

try {
  await test(0, async () => {
    sourceStart = await sourceHashes();
    assetsStart = await servedHashes();
    const token = process.env[fixture.actors.admin.token_env];
    truth(
      Boolean(token),
      "Existing ephemeral fixture admin bearer must be available",
    );
    const response = await fetch(new URL("/v1/runtime-manifest", base), {
      headers: { Authorization: "Bearer " + token },
      redirect: "error",
    });
    eq(response.status, 200);
    runtime = await response.json();
    const version = JSON.parse(
      await fs.readFile(path.join(root, "VERSION.json"), "utf8"),
    );
    eq(runtime.environment, "test");
    eq(runtime.build_id, "impact-" + version.build);
    eq(runtime.api_version, version.domain_api);
    eq(runtime.mutation_tests_allowed, true);
    migrationsStart = setup("runtime").migrations;
    const migrationFiles = Object.keys(sourceStart).filter((file) =>
      /^infrastructure\/migrations\/\d{4}_.+\.sql$/.test(file),
    );
    eq(migrationsStart.length, migrationFiles.length);
    eq(runtime.schema_version, String(migrationsStart.length));
    same(
      migrationsStart.map((row) => row.version),
      Array.from({ length: migrationsStart.length }, (_, index) => index + 1),
    );
    for (const row of migrationsStart) {
      const files = migrationFiles.filter((file) =>
        file.startsWith(
          `infrastructure/migrations/${String(row.version).padStart(4, "0")}_`,
        ),
      );
      eq(files.length, 1);
      eq(
        row.sha256,
        sourceStart[files[0]],
        "Applied migration equals the pinned source bytes",
      );
    }
    providerStart = setup("provider_counts");
    const browserDir = path.join(root, ".local/browser");
    browser = await chromium.launch({
      executablePath:
        process.env.IMPACT_BROWSER_EXECUTABLE ||
        path.join(browserDir, "chromium"),
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
    page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
    page.setDefaultTimeout(20000);
    await observe(page);
    activeCase.observations.push({
      browser_version: browser.version(),
      source_files: Object.keys(sourceStart).length,
      served_assets: Object.keys(assetsStart),
      migration_count: migrationsStart.length,
    });
  });
  await test(1, async () => {
    await login("admin");
    eq(await label("Workspace").inputValue(), fixture.tenant_a);
    const title = "Synthetic priorities — Café समुदाय";
    const first = {
      description: "Synthetic newsletter preparation is slow",
      affected_area: "Communications",
      supporting_evidence:
        "Synthetic log: five drafts took two staff hours.\nExact Café समुदाय evidence.",
    };
    const second = {
      description: "Synthetic programme definitions need a checklist",
      affected_area: "Monitoring and evaluation",
      supporting_evidence:
        "Synthetic review: three labels differed.\nPreserve punctuation: =sample + notes.",
    };
    await diagnosisLabel("Diagnosis title").fill(title);
    for (const [index, problem] of [first, second].entries()) {
      await diagnosisButton("Add problem").click();
      const description = diagnosisLabel(
        "Description for priority " + (index + 1),
      );
      await page.waitForFunction(
        (id) => document.activeElement?.id === id,
        await description.getAttribute("id"),
      );
      truth(
        await description.evaluate(
          (element) => document.activeElement === element,
        ),
        "Add problem focuses its description",
      );
      await description.fill(problem.description);
      await diagnosisLabel("Area affected for " + problem.description).fill(
        problem.affected_area,
      );
      await diagnosisLabel(
        "Supporting evidence for " + problem.description,
      ).fill(problem.supporting_evidence);
    }
    eq(
      await region()
        .getByRole("button", { name: /Choose saved evidence/ })
        .count(),
      0,
      "Default diagnosis admin has no Evidence selector without evidence.read",
    );
    eq(
      await region()
        .getByText(
          "Evidence read access is needed to choose saved evidence. You can still enter supporting notes.",
          { exact: true },
        )
        .count(),
      2,
      "Notes remain usable without widening Evidence access",
    );
    const ids = await region()
      .locator("li[data-problem-id]")
      .evaluateAll((rows) =>
        rows.map((row) => row.getAttribute("data-problem-id")),
      );
    eq(ids.length, 2);
    const move = diagnosisButton("Move " + second.description + " up");
    await move.focus();
    await move.press("Enter");
    await region()
      .getByText("Problem moved to priority 1.", { exact: true })
      .waitFor();
    same(
      await region()
        .locator("li[data-problem-id]")
        .evaluateAll((rows) =>
          rows.map((row) => row.getAttribute("data-problem-id")),
        ),
      [ids[1], ids[0]],
      "Keyboard movement changes the visible priority order",
    );
    const movedHeading = region().locator(`li[data-problem-id="${ids[1]}"] h4`);
    await page.waitForFunction(
      (id) => document.activeElement?.id === id,
      await movedHeading.getAttribute("id"),
    );
    truth(
      await movedHeading.evaluate(
        (element) => document.activeElement === element,
      ),
      "Movement focuses the moved problem's heading",
    );
    const expected = {
      title,
      problems: [
        { problem_id: ids[0], ...first },
        { problem_id: ids[1], ...second },
      ],
      priority_order: [ids[1], ids[0]],
    };
    created = await writeFromUI(
      "Save diagnosis draft",
      diagnosisRoute,
      "POST",
      201,
    );
    current = readCurrent();
    same(
      current.data,
      expected,
      "Exact saved evidence and stable IDs/order, independently read from the actual server",
    );
    const after = state();
    same(
      [after.revisions, after.audits, after.outbox, after.receipts],
      [1, 1, 1, 1],
      "Create has one atomic set of domain effects",
    );
    await page.reload();
    await openWorkspace();
    same(
      await openSaved(),
      current,
      "Browser reopens exact saved data after a real reload",
    );
    eq(
      await diagnosisLabel(
        "Supporting evidence for " + first.description,
      ).inputValue(),
      first.supporting_evidence,
    );
    eq(
      await diagnosisLabel(
        "Supporting evidence for " + second.description,
      ).inputValue(),
      second.supporting_evidence,
    );
    same(
      await region()
        .locator("li[data-problem-id]")
        .evaluateAll((rows) =>
          rows.map((row) => row.getAttribute("data-problem-id")),
        ),
      expected.priority_order,
    );
    await scan("Saved reordered draft");
    await page.screenshot({
      path: path.join(captureDirectory, "diagnosis-saved-draft.png"),
      fullPage: true,
    });
    activeCase.observations.push({
      object_id: created.object_id,
      revision_id: current.revision_id,
      saved_data: current.data,
      stored_effects: after,
    });
  });
  await test(2, async () => {
    const problem = current.data.problems[0];
    await diagnosisLabel("Supporting evidence for " + problem.description).fill(
      "",
    );
    await diagnosisButton("Remove priority for " + problem.description).click();
    await writeFromUI("Save diagnosis draft");
    current = readCurrent();
    const before = state(),
      sent = commands.length;
    await diagnosisButton("Complete diagnosis").click();
    const errors = region().getByRole("alert");
    await errors
      .getByText(
        "Completion was refused. Fix these problems, then save the draft:",
        { exact: true },
      )
      .waitFor();
    const text = await errors.innerText();
    truth(
      text.includes(problem.description),
      "Local refusal names the incomplete problem",
    );
    truth(text.includes("supporting evidence"));
    truth(text.includes("priority order"));
    eq(
      commands.length,
      sent,
      "Client rejects incomplete completion before sending a write",
    );
    const refused = api(objectRoute() + "/actions/complete", "POST", {
      operation_id: randomUUID(),
      expected_revision: current.revision_id,
    });
    eq(refused.status, 422);
    eq(refused.body.code, "VALIDATION_FAILED");
    eq(refused.body.reason_code, "DIAGNOSIS_INCOMPLETE");
    for (const field of ["supporting_evidence", "priority"]) {
      const actual = refused.body.field_errors.filter(
        (row) => row.path === "problems." + problem.problem_id + "." + field,
      );
      eq(actual.length, 1);
      truth(
        actual[0].message.includes(problem.description),
        "Actual server refusal names this problem for " + field,
      );
    }
    same(
      readCurrent(),
      current,
      "Actual refusal preserves saved Draft and head",
    );
    observeEffects(
      before,
      state(),
      0,
      "Both completion refusals have no domain write",
    );
    await scan("Named incomplete-problem refusal");
    await page.screenshot({
      path: path.join(captureDirectory, "diagnosis-completion-refused.png"),
      fullPage: true,
    });
    await diagnosisLabel("Supporting evidence for " + problem.description).fill(
      "Synthetic follow-up evidence restores this incomplete problem.",
    );
    await diagnosisButton("Set priority for " + problem.description).click();
    await writeFromUI("Save diagnosis draft");
    current = readCurrent();
  });
  await test(3, async () => {
    const before = state(),
      prior = copy(current);
    const completed = await writeFromUI(
      "Complete diagnosis",
      objectRoute() + "/actions/complete",
      "POST",
    );
    current = readCurrent();
    eq(current.business_state, "Completed");
    eq(current.revision_id, completed.revision_id);
    eq(current.data.completed_by, fixture.actors.admin.principal_id);
    truth(!Number.isNaN(Date.parse(current.data.completed_at)));
    same(
      {
        title: current.data.title,
        problems: current.data.problems,
        priority_order: current.data.priority_order,
      },
      prior.data,
    );
    truth(
      await diagnosisLabel("Diagnosis title").evaluate(
        (element) => element.readOnly,
      ),
      "Completed title is read-only",
    );
    truth(
      await region()
        .locator(
          ".ai-diagnosis-problems input, .ai-diagnosis-problems textarea",
        )
        .evaluateAll((elements) =>
          elements.every((element) => element.readOnly),
        ),
      "All completed problem fields are read-only",
    );
    eq(await diagnosisButton("Save diagnosis draft").count(), 0);
    eq(await diagnosisButton("Add problem").count(), 0);
    eq(
      await region()
        .getByRole("button", { name: /^Move / })
        .count(),
      0,
    );
    observeEffects(
      before,
      state(),
      1,
      "Actual completion has one set of effects",
    );
    const immutable = copy(current),
      reason =
        "Synthetic correction: clarify priority evidence without replacing completed history.";
    await scan("Read-only completed diagnosis");
    await page.screenshot({
      path: path.join(captureDirectory, "diagnosis-completed.png"),
      fullPage: true,
    });
    await diagnosisLabel("Reason for diagnosis correction").fill(reason);
    const correction = await writeFromUI(
      "Create correction draft",
      objectRoute() + "/actions/revise",
      "POST",
    );
    current = readCurrent();
    eq(current.business_state, "Draft");
    eq(current.revision_id, correction.revision_id);
    truth(current.revision_id !== immutable.revision_id);
    eq(current.data.correction_reason, reason);
    eq(current.data.completed_at, undefined);
    eq(current.data.completed_by, undefined);
    const historical = api(
      objectRoute() + "/revisions/" + immutable.revision_id,
    );
    eq(historical.status, 200);
    same(
      historical.body,
      immutable,
      "Actual completed historical revision is byte-equivalent in JSON meaning after correction",
    );
    const history = api(objectRoute() + "/revisions");
    eq(history.status, 200);
    truth(
      history.body.items.some(
        (row) =>
          row.revision_id === immutable.revision_id &&
          row.business_state === "Completed",
      ),
    );
    truth(
      !(await diagnosisLabel("Diagnosis title").evaluate(
        (element) => element.readOnly,
      )),
      "Correction is an editable new Draft",
    );
    activeCase.observations.push({
      completed: immutable,
      correction: current,
      reason,
      history_items: history.body.items,
    });
  });
  await test(4, async () => {
    const localTitle = "Synthetic local draft must survive a real conflict";
    const replacement = {
      title: "Synthetic independently saved current version",
      problems: copy(current.data.problems),
      priority_order: [...current.data.priority_order],
    };
    const old = copy(current);
    const saved = api(objectRoute(), "PUT", {
      operation_id: randomUUID(),
      expected_revision: old.revision_id,
      data: replacement,
    });
    eq(saved.status, 200);
    await diagnosisLabel("Diagnosis title").fill(localTitle);
    const before = state();
    const refused = await writeFromUI(
      "Save diagnosis draft",
      objectRoute(),
      "PUT",
      409,
    );
    eq(refused.code, "CONFLICT_VERSION");
    await region()
      .getByRole("group", { name: "Diagnosis version conflict", exact: true })
      .waitFor();
    eq(
      await diagnosisLabel("Diagnosis title").inputValue(),
      localTitle,
      "Stale refusal retains local input",
    );
    observeEffects(
      before,
      state(),
      0,
      "Rejected stale UI write has no domain effects",
    );
    same(
      Object.fromEntries(
        ["title", "problems", "priority_order"].map((key) => [
          key,
          readCurrent().data[key],
        ]),
      ),
      replacement,
      "Real concurrent saved editable data is unchanged by stale write",
    );
    await diagnosisButton("Load current saved version for review").click();
    await diagnosisButton(
      "Replace my local draft with this saved version",
    ).waitFor();
    eq(
      await diagnosisLabel("Diagnosis title").inputValue(),
      localTitle,
      "Loading a review does not replace the local draft",
    );
    truth(
      (await region().innerText()).includes(replacement.title),
      "Review shows actual current title",
    );
    truth(
      (await region().innerText()).includes(
        replacement.problems[0].supporting_evidence,
      ),
      "Review shows actual current evidence",
    );
    await scan("Actual current-version conflict review");
    await diagnosisButton(
      "Replace my local draft with this saved version",
    ).click();
    current = readCurrent();
    eq(
      await diagnosisLabel("Diagnosis title").inputValue(),
      replacement.title,
      "Only explicit replacement adopts the current saved Draft",
    );
    eq(
      await region().getAttribute("data-diagnosis-revision"),
      current.revision_id,
    );
  });
  await test(5, async () => {
    const title = "Synthetic response-loss exact retry";
    await diagnosisLabel("Diagnosis title").fill(title);
    const before = state(),
      sent = [],
      committed = deferred(),
      released = deferred();
    let first = true,
      actualReceipt;
    const intercept = async (route) => {
      if (route.request().method() !== "PUT") return route.fallback();
      sent.push(route.request().postData());
      if (!first) return route.fallback();
      first = false;
      try {
        const response = await route.fetch({ maxRedirects: 0, timeout: 20000 });
        assert.equal(
          response.status(),
          200,
          "The dropped response must come from an actual committed server command",
        );
        actualReceipt = await response.json();
        committed.resolve();
        await released.promise;
        await route.abort("connectionfailed");
      } catch (error) {
        committed.resolve({ error: safeMessage(error.message) });
        throw error;
      }
    };
    const match = new URL(objectRoute(), base).href;
    await page.route(match, intercept);
    try {
      await diagnosisButton("Save diagnosis draft").click();
      const issue = await bounded(
        committed.promise,
        "Actual save did not reach its committed-response boundary",
      );
      truth(!issue?.error, issue?.error);
      truth(Boolean(actualReceipt));
      const stored = readCurrent();
      eq(stored.data.title, title);
      eq(stored.revision_id, actualReceipt.revision_id);
      observeEffects(
        before,
        state(),
        1,
        "Lost response follows one real committed set of effects",
      );
      released.resolve();
      await diagnosisButton("Retry the same request").waitFor();
      truth(
        await diagnosisLabel("Diagnosis title").evaluate(
          (element) => element.readOnly,
        ),
        "Uncertain command freezes input against changed-payload replay",
      );
      truth(await diagnosisButton("Save diagnosis draft").isDisabled());
      truth(await diagnosisButton("New diagnosis").isDisabled());
      await scan("Uncertain committed diagnosis command");
      const storedCounts = state();
      const replay = await writeFromUI("Retry the same request");
      eq(sent.length, 2, "Only initial command and exact retry were submitted");
      eq(
        sent[1],
        sent[0],
        "Replay is the exact same operation ID, expected revision and payload bytes",
      );
      same(
        replay,
        actualReceipt,
        "Actual server returns the original operation receipt",
      );
      observeEffects(
        storedCounts,
        state(),
        0,
        "Actual receipt replay creates no duplicate effects",
      );
      current = readCurrent();
      eq(current.data.title, title);
      lastReplay = {
        route: objectRoute(),
        body: JSON.parse(sent[0]),
        receipt: actualReceipt,
      };
      activeCase.observations.push({
        initial_request_sha256: sha(sent[0]),
        replay_request_sha256: sha(sent[1]),
        actual_receipt: actualReceipt,
        response_transport:
          "First actual committed response deliberately aborted; second request reached the actual server, not a mocked success",
      });
    } finally {
      released.resolve();
      await page.unroute(match, intercept);
    }
  });
  await test(6, async () => {
    // Settle the prior authentic replay readback before observing a new refusal.
    await page.waitForFunction(
      (revision) =>
        document
          .querySelector(".ai-diagnosis")
          ?.getAttribute("data-diagnosis-revision") === revision,
      lastReplay.receipt.revision_id,
    );
    await page.waitForFunction(
      () =>
        !document
          .querySelector(".ai-diagnosis")
          ?.textContent.includes("Loading saved diagnoses…"),
    );
    const before = state();
    const change = setup("narrow_read");
    narrowed.push(change);
    try {
      const denied = api();
      eq(denied.status, 404);
      eq(denied.body.code, "RESOURCE_UNAVAILABLE");
      const replay = api(lastReplay.route, "PUT", lastReplay.body);
      eq(replay.status, 404);
      eq(replay.body.code, "RESOURCE_UNAVAILABLE");
      truth(
        replay.body.object_id === undefined,
        "Receipt replay does not disclose its private prior outcome after actual read-grant loss",
      );
      const pending = page.waitForResponse(
        (response) =>
          response.request().method() === "GET" &&
          new URL(response.url()).pathname === objectRoute(),
      );
      await diagnosisLabel("Saved diagnoses").selectOption(created.object_id);
      const refused = await pending;
      eq(refused.status(), 404);
      await region()
        .getByText(
          "The diagnosis is unavailable. Refresh your access before continuing.",
          { exact: true },
        )
        .waitFor();
      eq(await diagnosisLabel("Diagnosis title").count(), 0);
      eq(await region().locator("li[data-problem-id]").count(), 0);
      eq(await diagnosisLabel("Saved diagnoses").count(), 0);
      truth(
        !(await region().innerText()).includes(current.data.title),
        "Actual read refusal removes saved private title from the DOM",
      );
      truth(
        !(await region().innerText()).includes(
          current.data.problems[0].supporting_evidence,
        ),
        "Actual read refusal removes private evidence from the DOM",
      );
      observeEffects(
        before,
        state(),
        0,
        "Current-authority read and replay refusals have no domain effects",
      );
      await scan("Unavailable after real current read-grant loss");
    } finally {
      setup("restore", change);
      narrowed.splice(narrowed.indexOf(change), 1);
    }
    await page.reload();
    await openWorkspace();
    await openSaved();
    same(
      readCurrent(),
      current,
      "Restoring only original fixture purposes leaves saved diagnosis unchanged",
    );
    await qualifyDelayedReadAfterActualCollectionRefusal();
  });
  await test(7, async () => {
    const marker = "Synthetic unsaved input must leave with its session";
    const before = state();
    await diagnosisLabel("Diagnosis title").fill(marker);
    await logout();
    await login("other_tenant", false);
    eq(
      await label("Workspace").inputValue(),
      fixture.tenant_b,
      "Actual next session belongs to the different synthetic tenant",
    );
    eq(
      await region().count(),
      0,
      "Diagnosis-only private UI is absent without this actor's capability",
    );
    truth(!(await page.locator("body").innerText()).includes(marker));
    truth(
      !(await page.locator("body").innerText()).includes(current.data.title),
    );
    const denied = api(
      `/v1/tenants/${fixture.tenant_b}/ai-enablement/diagnoses/${created.object_id}`,
      "GET",
      undefined,
      "other_tenant",
    );
    eq(denied.status, 404);
    const storage = await page.evaluate(() => ({
      local: Object.values(localStorage),
      session: Object.values(sessionStorage),
    }));
    truth(
      !JSON.stringify(storage).includes(marker) &&
        !JSON.stringify(storage).includes(
          current.data.problems[0].supporting_evidence,
        ),
      "Diagnosis notes are absent from browser local/session storage",
    );
    await logout();
    await login("admin");
    eq(
      await diagnosisLabel("Diagnosis title").inputValue(),
      "Organisation diagnosis",
      "New authenticated scope starts with a blank unsaved worksheet",
    );
    await openSaved();
    const held = deferred(),
      release = deferred(),
      finished = deferred();
    let responseFromServer;
    const match = new URL(objectRoute(), base).href;
    const intercept = async (route) => {
      if (route.request().method() !== "GET") return route.fallback();
      try {
        const response = await route.fetch({ maxRedirects: 0, timeout: 20000 });
        assert.equal(response.status(), 200);
        responseFromServer = await response.json();
        held.resolve();
        await release.promise;
        // Replay only the authentic already-fetched read response; no fabricated
        // server result. A client abort on logout is an expected safe outcome.
        try {
          await route.fulfill({ response });
          finished.resolve("actual old read delivered");
        } catch {
          finished.resolve("old client read aborted after scope change");
        }
      } catch (error) {
        held.resolve({ error: safeMessage(error.message) });
        finished.resolve("held read failed");
      }
    };
    await page.route(match, intercept);
    try {
      await diagnosisLabel("Saved diagnoses").selectOption(created.object_id);
      const issue = await bounded(
        held.promise,
        "Actual prior-session GET did not reach its delayed response boundary",
      );
      truth(!issue?.error, issue?.error);
      same(responseFromServer, current);
      await logout();
      await login("other_tenant", false);
      release.resolve();
      const outcome = await bounded(
        finished.promise,
        "Delayed old response was not released or aborted",
      );
      eq(await region().count(), 0);
      truth(
        !(await page.locator("body").innerText()).includes(current.data.title),
        "Delayed old-scope response never repopulates the new tenant DOM",
      );
      activeCase.observations.push({
        delayed_response_source: "Actual prior-session authorised server GET",
        delayed_response_sha256: sha(JSON.stringify(responseFromServer)),
        delivery_outcome: outcome,
        next_tenant: fixture.tenant_b,
      });
    } finally {
      release.resolve();
      await page.unroute(match, intercept);
    }
    await logout();
    await login("admin");
    await openSaved();
    observeEffects(
      before,
      state(),
      0,
      "Scope transitions and delayed reads do not save or overwrite a diagnosis",
    );
  });
  await test(8, async () => {
    await scan("Desktop correction draft");
    await page.setViewportSize({ width: 390, height: 844 });
    await region().scrollIntoViewIfNeeded();
    truth(
      await region().evaluate((element) => {
        const box = element.getBoundingClientRect();
        return (
          box.left >= -1 &&
          box.right <= innerWidth + 1 &&
          element.scrollWidth <= box.width + 1
        );
      }),
      "Diagnosis content fits the 390px viewport",
    );
    truth(
      await region()
        .locator("button")
        .evaluateAll((elements) =>
          elements.every((element) => {
            const box = element.getBoundingClientRect();
            return box.left >= -1 && box.right <= innerWidth + 1;
          }),
        ),
      "Native keyboard buttons remain inside the mobile viewport",
    );
    await scan("Mobile correction draft");
    await page.screenshot({
      path: path.join(captureDirectory, "diagnosis-mobile.png"),
      fullPage: true,
    });
    await page.setViewportSize({ width: 1440, height: 1050 });
    same(pageErrors, [], "No uncaught browser errors");
    same(externalRequests, [], "No external request was allowed or attempted");
    same(
      forbiddenRequests,
      [],
      "No provider/advisory/job request was attempted",
    );
    providerEnd = setup("provider_counts");
    same(
      providerEnd,
      providerStart,
      "Advisory request/result rows did not change",
    );
    migrationsEnd = setup("runtime").migrations;
    same(
      migrationsEnd,
      migrationsStart,
      "Applied migrations did not change during the test",
    );
    sourceEnd = await sourceHashes();
    assetsEnd = await servedHashes();
    same(
      sourceEnd,
      sourceStart,
      "Qualification sources remained at exact start bytes",
    );
    same(assetsEnd, assetsStart, "Served assets remained at exact start bytes");
    activeCase.observations.push({
      scan_count: accessibilityScans.length,
      advisory_counts: providerEnd,
      actual_browser_commands: commands.length,
      independent_api_mutations: mutations.length,
    });
  });
} catch (error) {
  process.exitCode = 1;
  console.error(safeMessage(error.message));
  if (page) {
    try {
      await page.screenshot({
        path: path.join(captureDirectory, "diagnosis-browser-failure.png"),
        fullPage: true,
        timeout: 10000,
      });
    } catch (captureError) {
      setupEvidence.push({
        operation: "failure_capture",
        failure: safeMessage(captureError.message),
      });
    }
  }
} finally {
  const cleanupFailures = [];
  for (const change of [...narrowed].reverse()) {
    try {
      setup("restore", change);
    } catch (error) {
      cleanupFailures.push(safeMessage(error.message));
      process.exitCode = 1;
    }
  }
  for (const [id, name, criterion] of suite)
    if (!results.some((row) => row.id === id))
      results.push({
        id,
        name,
        criterion: criterion || null,
        status: "not_run",
        assertions: 0,
        observations: [],
        reason:
          "Prerequisite group failed or setup did not complete; no pass is inferred",
      });
  for (const [name, fn] of [
    ["final_sources", sourceHashes],
    ["final_assets", servedHashes],
  ]) {
    try {
      const value = await fn();
      if (name === "final_sources") sourceEnd ??= value;
      else assetsEnd ??= value;
    } catch (error) {
      cleanupFailures.push(name + ": " + safeMessage(error.message));
      process.exitCode = 1;
    }
  }
  const changedSources = Object.keys(sourceStart || {}).filter(
    (file) => sourceEnd?.[file] !== sourceStart[file],
  );
  const changedAssets = Object.keys(assetsStart || {}).filter(
    (file) => assetsEnd?.[file] !== assetsStart[file],
  );
  if (changedSources.length || changedAssets.length) process.exitCode = 1;
  await fs.writeFile(
    evidenceFile,
    JSON.stringify(
      {
        suite: "US-DX-01a actual local browser qualification",
        criteria: ["AC-US-DX-01a-001", "AC-US-DX-01a-002"],
        started_at: startedAt,
        finished_at: new Date().toISOString(),
        status: process.exitCode ? "failed" : "passed",
        counts: {
          cases: suite.length,
          passed: results.filter((row) => row.status === "passed").length,
          failed: results.filter((row) => row.status === "failed").length,
          not_run: results.filter((row) => row.status === "not_run").length,
          assertions: results.reduce((sum, row) => sum + row.assertions, 0),
        },
        results,
        engine: browser?.version() || null,
        playwright_version: require("playwright-core/package.json").version,
        axe_version: require("axe-core/package.json").version,
        platform: process.platform,
        runtime_manifest: runtime || null,
        actual_applied_migrations_start: migrationsStart || null,
        actual_applied_migrations_end: migrationsEnd || null,
        source_sha256_start: sourceStart || null,
        source_sha256_end: sourceEnd || null,
        served_assets_sha256_start: assetsStart || null,
        served_assets_sha256_end: assetsEnd || null,
        source_changed_during_run: changedSources,
        served_assets_changed_during_run: changedAssets,
        browser_commands: commands.map(({ body, ...row }) => ({
          ...row,
          operation_id: JSON.parse(body).operation_id,
        })),
        independent_api_mutations: mutations,
        advisory_rows_start: providerStart || null,
        advisory_rows_end: providerEnd || null,
        accessibilityScans,
        uncaughtErrors: pageErrors,
        requestFailures,
        externalRequests,
        forbiddenRequests,
        setupEvidence,
        cleanupFailures,
        captures_directory: captureDirectory,
        limitations: [
          "Synthetic disposable loopback data only; no nonprofit owner acceptance, production use or deployment claim.",
          "Disposable preexisting read-grant purpose narrowing and restoration qualifies an actual refusal; it is not ordinary grant/role creation.",
          "PGlite fixture runs do not qualify native-role RLS/concurrency. Native qualification remains a separate gate.",
          "Outbox rows are transaction intents, not external messages or provider deliveries.",
          "Automated axe serious/critical results are bounded scans; incomplete findings are retained and manual assistive-technology acceptance is not inferred.",
          "Actual server response transport is deliberately lost or delayed in two groups; server success, conflict, completion, replay and refusal are never fabricated.",
        ],
      },
      null,
      2,
    ),
  );
  await browser?.close();
}
