import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py planning-browser");
const passwords = JSON.parse(
  await fs.readFile(path.join(local, "passwords.json"), "utf8"),
);
const fixture = JSON.parse(
  await fs.readFile(
    path.join(root, "specification/fixtures/api-fixture.json"),
    "utf8",
  ),
);
const tenant = fixture.tenant_a;
const browserDir = path.join(root, ".local/browser");
const browser = await chromium.launch({
  executablePath: path.join(browserDir, "chromium"),
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
const pages = {};
const results = [],
  errors = [];
function watch(candidate) {
  candidate.setDefaultTimeout(15000);
  candidate.on("pageerror", (e) => errors.push(e.message));
}
watch(page);
async function test(name, fn) {
  await fn();
  results.push({ name, status: "passed" });
  console.log("PASS " + name);
}
const button = (name) => page.getByRole("button", { name, exact: true });
const label = (name) => page.getByLabel(name, { exact: true });
const dialog = () => page.getByRole("dialog");
async function login(user) {
  await label("Username").fill(user);
  await label("Password").fill(passwords[user]);
  await button("Sign in →").click();
  await page
    .getByRole("heading", { name: "Programme portfolio", exact: true })
    .waitFor();
  pages[user] = page;
}
async function switchUser(user) {
  if (pages[user]) {
    page = pages[user];
    await page.reload();
    await page
      .getByRole("heading", { name: "Programme portfolio", exact: true })
      .waitFor();
    return;
  }
  page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
  watch(page);
  await page.goto(base);
  await login(user);
}
// Programme, approved definition and draft indicator are prepared through the API with the
// suite-start bearer tokens; the planning features themselves are exercised in the browser.
async function api(actor, route, data, method = "POST", revision) {
  const response = await fetch(base + "/v1/tenants/" + tenant + "/" + route, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + process.env[fixture.actors[actor].token_env],
    },
    body:
      method === "GET"
        ? undefined
        : JSON.stringify({
            operation_id: crypto.randomUUID(),
            ...(revision ? { expected_revision: revision } : {}),
            data,
          }),
  });
  const body = await response.json();
  assert(response.ok, JSON.stringify(body));
  return body;
}
const read = (route) => api("author", route, null, "GET");
async function saveReceipt(click, suffix) {
  const pending = page.waitForResponse(
    (r) => r.request().method() === "POST" && r.url().endsWith(suffix),
  );
  await click();
  const response = await pending;
  assert(response.ok(), await response.text());
  return response.json();
}
// The first POST ending in `suffix` is applied but its response is dropped; the retry must
// repeat the exact command and receive the original receipt (one server-side effect).
async function lostResponseThenRetry(click, suffix) {
  const sent = [];
  let original = null,
    active = true;
  await page.route(
    (url) => url.pathname.endsWith(suffix),
    async (route) => {
      const request = route.request();
      if (!active || request.method() !== "POST") return route.fallback();
      sent.push(request.postDataJSON());
      if (sent.length === 1) {
        const response = await route.fetch();
        assert(response.ok(), await response.text());
        original = await response.json();
        return route.abort("connectionreset");
      }
      return route.fallback();
    },
  );
  try {
    await click();
    await dialog().getByRole("alert").first().waitFor();
    assert(original, "the first attempt reached the server");
    const retried = await saveReceipt(click, suffix);
    assert.equal(sent.length, 2);
    assert.deepEqual(sent[1], sent[0]);
    assert.deepEqual(retried, original);
    return retried;
  } finally {
    active = false;
  }
}
async function openPlanning(programme, tab) {
  await button("Results framework").click();
  await page
    .getByRole("heading", { name: "Results framework", exact: true })
    .first()
    .waitFor();
  await label("Programme").selectOption({ label: programme });
  await page.getByRole("tab", { name: tab, exact: false }).click();
}
async function reviewAndApprove(programme) {
  await switchUser("reviewer");
  await openPlanning(programme, "Reviews");
  await page
    .getByRole("button", { name: /^Review · / })
    .first()
    .click();
  await dialog().getByText("Decision reason").waitFor();
  await label("Decision reason").fill(
    "Checked the exact hierarchy, placements and values.",
  );
  await button("Approve").click();
  await dialog().waitFor({ state: "hidden" });
}
const unique = Date.now().toString(),
  programme = "Planning programme " + unique,
  indicatorLabel = "Village register " + unique;
try {
  const calendar = (await read("reporting-calendars")).items[0];
  const geography = (await read("geographies")).items[0];
  const created = await api("author", "programmes", {
    code: "PLAN",
    title: programme,
    programme_type: "Health",
    starts_at: "2026-01-01T00:00:00Z",
    ends_at: "2027-01-01T00:00:00Z",
    reporting_calendar_id: calendar.object_id,
    geography_id: geography.object_id,
  });
  const definition = await api("author", "indicator-definitions", {
    code: "HH",
    name: "Households " + unique,
    measurement_type: "COUNT",
    unit: "households",
    population: "Resident households",
    inclusion: "Registered",
    exclusion: "Duplicates",
    method: "Register count",
    source_mode: "MANUAL",
    time_semantic: "FLOW",
    combination_rule: "SUM",
    display_decimals: 0,
  });
  const template = (await read("workflow-templates")).items[0];
  const workflow = await api(
    "author",
    "indicator-definitions/" + definition.object_id + "/actions/submit",
    { workflow_version: template.revision_id },
    "POST",
    definition.revision_id,
  );
  const pending = await read("workflows/" + workflow.object_id);
  await api(
    "reviewer",
    "workflows/" + workflow.object_id + "/actions/approve",
    {
      candidate_revision: pending.data.candidate_revision,
      reason: "Browser planning setup",
    },
    "POST",
    pending.revision_id,
  );
  const approvedDefinition = await read(
    "indicator-definitions/" + definition.object_id,
  );
  await api("author", "indicator-instances", {
    programme_id: created.object_id,
    definition_version: approvedDefinition.revision_id,
    local_applicability: indicatorLabel,
    collector_id: fixture.actors.author.principal_id,
    reviewer_id: fixture.actors.reviewer.principal_id,
  });

  await page.goto(base);
  await login("author");
  await test("Build a logframe with owners and indicator placement", async () => {
    await openPlanning(programme, "Framework");
    await button("New framework").click();
    await label("Version label").fill("Baseline " + unique);
    await label("Effective from").fill("2026-01-01");
    await label("Level 1").selectOption("IMPACT");
    await label("Title 1").fill("Healthier households");
    await label("Description 1").fill("Households have safe water.");
    await label("Owner 1").selectOption({ label: "Author" });
    await button("Add node").click();
    await label("Level 2").selectOption("OUTPUT");
    await label("Parent 2").selectOption({ label: "Healthier households" });
    await label("Title 2").fill("Households registered");
    await label("Description 2").fill("Registered households are counted.");
    await label("Owner 2").selectOption({ label: "Author" });
    await page
      .getByLabel("Measure node 2 with " + indicatorLabel, { exact: true })
      .check();
    await dialog()
      .getByRole("region", { name: "Results hierarchy" })
      .getByText("Households registered")
      .waitFor();
    await button("Save framework draft").click();
    await dialog().waitFor({ state: "hidden" });
    await button("Baseline " + unique).waitFor();
  });
  await test("Completeness flags the unmeasured impact and accepts a documented exception", async () => {
    await button("Baseline " + unique).click();
    const review = dialog().getByRole("region", {
      name: "Completeness review",
    });
    await review.getByText("action required", { exact: false }).waitFor();
    await review.getByText("UNMEASURED RESULT", { exact: false }).waitFor();
    await page
      .getByRole("button", { name: /^Document exception/ })
      .first()
      .click();
    await label("Exception reason").fill(
      "Impact is measured by the end-line evaluation.",
    );
    await label("Exception review date").fill("2026-12-31");
    await button("Save exception").click();
    await dialog().waitFor({ state: "hidden" });
    await button("Baseline " + unique).click();
    await dialog().getByText("ready for review", { exact: false }).waitFor();
  });
  await test("Submit the framework; a lost response retries the exact command", async () => {
    await label("Review policy").selectOption({ index: 1 });
    await lostResponseThenRetry(
      () => button("Submit for review").click(),
      "/actions/submit",
    );
    await dialog().waitFor({ state: "hidden" });
  });
  await test("Independent reviewer re-fetches the candidate and approves the baseline", async () => {
    await reviewAndApprove(programme);
    await switchUser("author");
    await openPlanning(programme, "Framework");
    await page.getByRole("heading", { name: /^Approved baseline 1/ }).waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/planning-framework.png"),
    });
  });
  await test("Create and approve a period target", async () => {
    await page.getByRole("tab", { name: "Targets", exact: true }).click();
    await button("New target").click();
    await label("Target indicator").selectOption({ label: indicatorLabel });
    await label("Target period").selectOption({ index: 1 });
    await label("Target value").fill("40");
    await button("Save target draft").click();
    await dialog().waitFor({ state: "hidden" });
    await page
      .getByRole("button", { name: indicatorLabel + " · original" })
      .click();
    await label("Review policy").selectOption({ index: 1 });
    await saveReceipt(
      () => button("Submit for review").click(),
      "/actions/submit",
    );
    await dialog().waitFor({ state: "hidden" });
    await reviewAndApprove(programme);
  });
  await test("Targets versus actuals labels missing and official results", async () => {
    await switchUser("author");
    await openPlanning(programme, "Targets vs actuals");
    const table = page.getByRole("table", { name: "Targets versus actuals" });
    const row = table.locator("tr").filter({ hasText: indicatorLabel });
    await row.getByText("No result yet", { exact: true }).waitFor();
    await row.getByText("40", { exact: true }).waitFor();
    await label("Programme").selectOption({ label: "Safe Water 2026" });
    const seeded = page
      .getByRole("table", { name: "Targets versus actuals" })
      .locator("tr")
      .filter({ hasText: "46.36" });
    await seeded.getByText("OFFICIAL", { exact: true }).waitFor();
    await seeded.getByText("No approved target", { exact: true }).waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/planning-targets-vs-actuals.png"),
    });
  });
  await test("Planning views stay within a 390 px mobile width", async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    for (const tab of ["Targets vs actuals", "Framework", "Targets"]) {
      await label("Programme").selectOption({ label: programme });
      await page.getByRole("tab", { name: tab, exact: true }).click();
      await page.waitForTimeout(200);
      assert(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth + 1,
        ),
        tab + " overflows at 390 px",
      );
    }
    await page.screenshot({
      path: path.join(root, "docs/evidence/planning-mobile.png"),
      fullPage: true,
    });
    assert.deepEqual(errors, []);
  });
} catch (e) {
  results.push({
    name: "Planning browser run",
    status: "failed",
    message: e.message,
  });
  await page.screenshot({
    path: path.join(root, "docs/evidence/planning-browser-failure.png"),
    fullPage: true,
  });
  console.error(e.message);
  process.exitCode = 1;
} finally {
  await fs.writeFile(
    path.join(root, "docs/evidence/planning-browser-tests.json"),
    JSON.stringify(
      { engine: "Chromium 153", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
  await browser.close();
}
