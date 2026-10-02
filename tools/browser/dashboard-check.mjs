import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py dashboard-browser");
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
const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
page.setDefaultTimeout(15000);
const results = [],
  errors = [];
page.on("pageerror", (e) => errors.push(e.message));
async function test(name, fn) {
  await fn();
  results.push({ name, status: "passed" });
  console.log("PASS " + name);
}
const button = (name) => page.getByRole("button", { name, exact: true });
const label = (name) => page.getByLabel(name, { exact: true });
// Measurement, review, calculation and close are prepared through the API with the suite-start
// bearer tokens; the dashboard itself is exercised in the browser.
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
  assert(response.ok, route + " " + JSON.stringify(body));
  return body;
}
const read = (route) => api("author", route, null, "GET");
let template;
async function approve(route, row) {
  const receipt = await api(
    "author",
    route + "/" + row.object_id + "/actions/submit",
    { workflow_version: template.revision_id },
    "POST",
    row.revision_id,
  );
  await review(receipt.object_id);
}
async function review(workflowId) {
  const pending = await read("workflows/" + workflowId);
  await api(
    "reviewer",
    "workflows/" + workflowId + "/actions/approve",
    {
      candidate_revision: pending.data.candidate_revision,
      reason: "Browser dashboard setup",
    },
    "POST",
    pending.revision_id,
  );
}
const unique = Date.now().toString(),
  programme = "Dashboard programme " + unique,
  name = "Safe water coverage " + unique;
try {
  template = (await read("workflow-templates")).items[0];
  const calendar = (await read("reporting-calendars")).items[0];
  const geography = (await read("geographies")).items[0];
  const records = JSON.parse(
    await fs.readFile(
      path.join(root, "specification/fixtures/records.json"),
      "utf8",
    ),
  );
  const period = await read(
    "periods/" + records.find((r) => r.key === "period").object_id,
  );
  let created = await api("author", "programmes", {
    code: "DASH",
    title: programme,
    programme_type: "Health",
    starts_at: "2026-01-01T00:00:00Z",
    ends_at: "2027-01-01T00:00:00Z",
    reporting_calendar_id: calendar.object_id,
    geography_id: geography.object_id,
  });
  let definition = await api("author", "indicator-definitions", {
    code: "SW",
    name,
    measurement_type: "PERCENTAGE",
    unit: "percent",
    population: "Visited households",
    inclusion: "Visited",
    exclusion: "Duplicates",
    method: "Pooled ratio",
    source_mode: "MANUAL",
    time_semantic: "FLOW",
    combination_rule: "POOLED_RATIO",
    numerator_meaning: "Households with safe water",
    denominator_meaning: "Households visited",
    display_decimals: 2,
  });
  await approve(
    "indicator-definitions",
    await read("indicator-definitions/" + definition.object_id),
  );
  definition = await read("indicator-definitions/" + definition.object_id);
  let indicator = await api("author", "indicator-instances", {
    programme_id: created.object_id,
    definition_version: definition.revision_id,
    local_applicability: "Districts",
    collector_id: fixture.actors.author.principal_id,
    reviewer_id: fixture.actors.reviewer.principal_id,
  });
  const keys = [crypto.randomUUID(), crypto.randomUUID()];
  const plan = await api("author", "collection-plans", {
    title: "Dashboard collection",
    indicator_id: indicator.object_id,
    period_id: period.object_id,
    obligations: keys.map((k, i) => ({
      label: "Site " + (i + 1),
      source_namespace: "MANUAL",
      source_key: k,
      due_at: "2026-09-01T00:00:00Z",
    })),
  });
  await approve(
    "collection-plans",
    await read("collection-plans/" + plan.object_id),
  );
  indicator = await read("indicator-instances/" + indicator.object_id);
  await api(
    "author",
    "indicator-instances/" + indicator.object_id + "/actions/activate",
    {},
    "POST",
    indicator.revision_id,
  );
  for (const verb of ["ready", "activate"]) {
    created = await read("programmes/" + created.object_id);
    await api(
      "author",
      "programmes/" + created.object_id + "/actions/" + verb,
      {},
      "POST",
      created.revision_id,
    );
  }
  for (const [key, n, d] of [
    [keys[0], "50", "100"],
    [keys[1], "1", "10"],
  ]) {
    const row = await api("author", "observations", {
      source_namespace: "MANUAL",
      source_key: key,
      indicator_id: indicator.object_id,
      event_at: "2026-08-15T12:00:00Z",
      captured_at: "2026-08-15T13:00:00Z",
      capture_zone: "UTC",
      value_state: "PRESENT",
      value: "0",
      numerator: n,
      denominator: d,
      source_version: "1",
      dimension_values: {},
    });
    await approve("observations", await read("observations/" + row.object_id));
  }
  indicator = await read("indicator-instances/" + indicator.object_id);
  await api(
    "author",
    "indicator-instances/" + indicator.object_id + "/actions/calculate",
    { period_id: period.object_id },
    "POST",
    indicator.revision_id,
  );

  await page.goto(base);
  await label("Username").fill("author");
  await label("Password").fill(passwords.author);
  await button("Sign in →").click();
  await page
    .getByRole("heading", { name: "Programme portfolio", exact: true })
    .waitFor();
  const card = () => page.getByRole("article", { name: name + " · Districts" });
  async function open() {
    await button("Dashboards").click();
    await page
      .getByRole("heading", { name: "Dashboards", exact: true })
      .first()
      .waitFor();
    await label("Dashboard programme").selectOption({ label: programme });
    await label("Dashboard period").selectOption({
      label: period.data.code,
    });
  }
  await test("Provisional 51/110 is labelled provisional before any close", async () => {
    await open();
    await page
      .getByText("No locked snapshot for this programme and period yet", {
        exact: false,
      })
      .waitFor();
    await card().getByText("46.36", { exact: true }).waitFor();
    await card().getByText("(51 / 110)", { exact: false }).waitFor();
    await card().getByText("Up to date", { exact: true }).waitFor();
    await card().getByText("100.00% approved", { exact: false }).waitFor();
    // The official slot says None: nothing is promoted without a close.
    const official = card().locator("dd").first();
    assert.equal((await official.innerText()).trim(), "None");
  });
  await test("The trend chart has a text alternative and an equal table", async () => {
    const chart = page.getByRole("img", {
      name: name + " · Districts by period",
    });
    await chart.waitFor();
    const description = await page.locator("#series-desc").textContent();
    assert.match(description, /official none, provisional 46\.36/);
    const table = page.getByRole("table", { name: "Indicator series" });
    await table.getByText("46.36", { exact: true }).waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/dashboard-provisional.png"),
    });
  });
  await test("After the independent close the value is official from the snapshot", async () => {
    const receipt = await api(
      "author",
      "periods/" + period.object_id + "/actions/close",
      {
        workflow_version: template.revision_id,
        programme_id: created.object_id,
        reason: "Quarterly source and quality review complete.",
      },
      "POST",
      (await read("periods/" + period.object_id)).revision_id,
    );
    await review(receipt.object_id);
    await button("Refresh").click();
    await page
      .getByText("Official values from locked snapshot version 1", {
        exact: false,
      })
      .waitFor();
    const official = card().locator("dd").first();
    await official.getByText("46.36", { exact: true }).waitFor();
    assert.equal(
      (await card().locator("dd").nth(1).innerText()).trim(),
      "None",
    );
    await card().getByText("as locked", { exact: false }).waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/dashboard-official.png"),
      fullPage: true,
    });
  });
  await test("Drill-down lists the official value's source rows with their disposition", async () => {
    await card()
      .getByRole("button", { name: "Show sources", exact: true })
      .click();
    const sources = page.getByRole("region", { name: "Source observations" });
    await sources.waitFor();
    await sources
      .getByText("Dispositions refer to the official value shown on the card", {
        exact: false,
      })
      .waitFor();
    await sources
      .getByText("every source row of the period is listed", { exact: false })
      .waitFor();
    const table = sources.getByRole("table", { name: "Source observations" });
    await table.getByText("included", { exact: true }).first().waitFor();
    assert.equal(await table.locator("tbody tr").count(), 2);
    await table.getByText("(50/100)", { exact: false }).waitFor();
    await table.getByText("(1/10)", { exact: false }).waitFor();
    await card()
      .getByRole("button", { name: "Hide sources", exact: true })
      .click();
    await sources.waitFor({ state: "detached" });
  });
  await test("The portfolio pools the official value across programmes from stored components", async () => {
    await page.getByRole("tab", { name: "Portfolio", exact: true }).click();
    await label("Portfolio definition").selectOption({ label: name });
    await label("Portfolio period").selectOption({ label: period.data.code });
    const totals = page.locator(".portfolio-totals");
    await totals.getByText("46.36", { exact: true }).waitFor();
    await totals.getByText("(51/110)", { exact: false }).waitFor();
    await totals
      .getByText("pooled ratio over 1 of 1", { exact: false })
      .waitFor();
    const rows = page.getByRole("table", { name: "Portfolio programmes" });
    await rows.getByText(programme, { exact: true }).waitFor();
    await rows.getByText("Locked", { exact: true }).waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/dashboard-portfolio.png"),
      fullPage: true,
    });
    await page
      .getByRole("tab", { name: "Programme dashboard", exact: true })
      .click();
    await card().waitFor();
  });
  await test("The seeded fixture 46.36 is never attributed to a programme", async () => {
    await label("Dashboard programme").selectOption({
      label: "Safe Water 2026",
    });
    await page
      .getByText("No locked snapshot for this programme and period yet", {
        exact: false,
      })
      .waitFor();
    await page.waitForTimeout(300);
    assert.equal(
      await page.locator(".dashboard-grid").getByText("46.36").count(),
      0,
    );
  });
  await test("Dashboards stay within a 390 px mobile width", async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    await label("Dashboard programme").selectOption({ label: programme });
    await card().waitFor();
    await page.waitForTimeout(200);
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
      "dashboard overflows at 390 px",
    );
    await page.screenshot({
      path: path.join(root, "docs/evidence/dashboard-mobile.png"),
      fullPage: true,
    });
    assert.deepEqual(errors, []);
  });
} catch (e) {
  results.push({
    name: "Dashboard browser run",
    status: "failed",
    message: e.message,
  });
  await page.screenshot({
    path: path.join(root, "docs/evidence/dashboard-browser-failure.png"),
    fullPage: true,
  });
  console.error(e.message);
  process.exitCode = 1;
} finally {
  await fs.writeFile(
    path.join(root, "docs/evidence/dashboard-browser-tests.json"),
    JSON.stringify(
      { engine: "Chromium 153", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
  await browser.close();
}
