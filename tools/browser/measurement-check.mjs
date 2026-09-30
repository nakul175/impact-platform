import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py measurement-browser");
const passwords = JSON.parse(
  await fs.readFile(path.join(local, "passwords.json"), "utf8"),
);
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
page.setDefaultTimeout(15000);
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
async function close() {
  await button("Close dialog").click();
}
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
async function saveReceipt(click, suffix) {
  const pending = page.waitForResponse(
    (r) => r.request().method() === "POST" && r.url().endsWith(suffix),
  );
  await click();
  const response = await pending;
  assert(response.ok(), await response.text());
  return response.json();
}
// The first POST ending in `suffix` reaches the server, which applies it, but its response is
// dropped (connection reset); the second click must repeat the exact command. Asserts that both
// attempts carried the same operation identifier and payload and that the retry returned the
// server's original receipt, i.e. one server-side effect. The route stays installed and falls
// through once the check is done: unrouting while the page's follow-up reads are in flight can
// leave one of them paused in the interception layer.
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
    await page.getByRole("alert").first().waitFor();
    assert(original, "the first attempt reached the server");
    const retried = await saveReceipt(click, suffix);
    assert.equal(sent.length, 2);
    assert.equal(sent[1].operation_id, sent[0].operation_id);
    assert.deepEqual(sent[1], sent[0]);
    assert.deepEqual(retried, original);
    return retried;
  } finally {
    active = false;
  }
}
async function setupTab(name) {
  await button("Measurement setup").click();
  await page.getByRole("tab", { name, exact: true }).click();
}
async function submitConfig(name) {
  await button(name).click();
  await label("Review policy").selectOption({ index: 1 });
  const receipt = await saveReceipt(
    () => button("Submit for review").click(),
    "/actions/submit",
  );
  await page.getByRole("dialog").waitFor({ state: "hidden" });
  return receipt;
}
async function approve(workflow) {
  await button("Review queue").click();
  await page
    .locator("tr")
    .filter({ hasText: workflow.object_id.slice(0, 8) })
    .getByRole("button")
    .first()
    .click();
  await button("Review submission").click();
  await label("Decision reason").fill(
    "Checked the definition and exact obligations.",
  );
  await button("Approve").click();
  await page.getByRole("dialog").waitFor({ state: "hidden" });
}
const unique = Date.now().toString(),
  programme = "Collection programme " + unique,
  definition = "Households " + unique,
  indicator = "Village register " + unique,
  plan = "Quarterly plan " + unique,
  source = "plan-" + unique + "-1";
let workflow, instance;
try {
  await page.goto(base);
  await login("author");
  await test("Create programme with calendar and geography", async () => {
    await page
      .getByRole("button", { name: "New programme", exact: false })
      .click();
    await label("Programme title").fill(programme);
    await label("Programme code").fill("CONFIG");
    await label("Start date").fill("2026-01-01");
    await label("End date").fill("2026-12-31");
    await label("Programme type").fill("Health");
    await label("Reporting calendar").selectOption({ index: 1 });
    await label("Geography").selectOption({ index: 1 });
    await button("Save draft").click();
    await button(programme).waitFor();
    await button(programme).click();
    await button("Mark ready").waitFor();
    assert(await button("Mark ready").isDisabled());
    await close();
  });
  await test("Create and submit a complete indicator definition", async () => {
    await setupTab("Definitions");
    await button("New definition").click();
    for (const [key, value] of Object.entries({
      "Definition name": definition,
      "Definition code": "HH",
      Unit: "households",
      Population: "Resident households",
      "Inclusion criteria": "Registered households",
      "Exclusion criteria": "Duplicate entries",
      "Collection method": "Count the register",
    }))
      await label(key).fill(value);
    await label("Display decimals").fill("0");
    await label("Calculation method").selectOption("MEDIAN");
    await label("Time semantic").selectOption("EVENT");
    await page
      .getByText("Median of approved values is not available", { exact: false })
      .waitFor();
    await label("Time semantic").selectOption("FLOW");
    await label("Calculation method").selectOption("SUM");
    await label("Disaggregate results").check();
    await label("Dimension code").fill("sex");
    await label("Dimension label").fill("Sex");
    await label("Dimension version").fill("2026-1");
    await label("Categories").fill("F Female\nM Male");
    await button("Save draft").click();
    await button(definition).waitFor();
    workflow = await submitConfig(definition);
  });
  await test("Independent definition review renders the correct candidate", async () => {
    await switchUser("reviewer");
    await approve(workflow);
  });
  await test("Create indicator with approved definition and independent assignments", async () => {
    await switchUser("author");
    await setupTab("Indicators");
    await button("New indicator").click();
    await label("Programme").selectOption({ label: programme });
    await label("Approved definition").selectOption({ label: definition });
    await label("Local applicability").fill(indicator);
    await label("Collector").selectOption({ label: "Author" });
    await label("Independent reviewer").selectOption({ label: "Reviewer" });
    instance = await saveReceipt(
      () => button("Save draft").click(),
      "/indicator-instances",
    );
    await button(indicator).waitFor();
  });
  await test("Create explicit collection obligations and submit the plan", async () => {
    await page
      .getByRole("tab", { name: "Collection plans", exact: true })
      .click();
    await button("New collection plan").click();
    await label("Plan title").fill(plan);
    await label("Indicator").selectOption({ label: indicator });
    await label("Reporting period").selectOption({ index: 1 });
    await label("Source label 1").fill("Village A");
    await label("Source key 1").fill(source);
    await label("Due date and time (UTC) 1").fill("2026-09-01T12:00");
    await button("Add expected source").click();
    await label("Source label 2").fill("Village B");
    await label("Source key 2").fill("plan-" + unique + "-2");
    await label("Due date and time (UTC) 2").fill("2026-09-01T12:00");
    await button("Save draft").click();
    await button(plan).waitFor();
    workflow = await submitConfig(plan);
  });
  await test("Plan approval freezes the reviewed obligations", async () => {
    await switchUser("reviewer");
    await approve(workflow);
  });
  await test("Activate indicator and pass programme readiness", async () => {
    await switchUser("author");
    await setupTab("Indicators");
    await button(indicator).click();
    await button("Activate indicator").click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await page.screenshot({
      path: path.join(root, "docs/evidence/measurement-setup.png"),
    });
    await button("Portfolio").click();
    await button(programme).click();
    await button("Mark ready").click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await button(programme).click();
    await page.screenshot({
      path: path.join(root, "docs/evidence/programme-readiness.png"),
    });
    await button("Activate programme").click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
  });
  await test("Capture a planned observation for the activated indicator", async () => {
    await button("Measurement").click();
    await page
      .getByRole("button", { name: "Add observation", exact: false })
      .click();
    await label("Indicator").selectOption(instance.object_id);
    await label("Source key").fill(source);
    await label("Event date (UTC)").fill("2026-08-15");
    await label("Recorded value").fill("10");
    await label("Dimension codes (optional)").fill("sex=F");
    await button("Save draft").click();
    await button(source).click();
    await button("Submit for review").click();
    await label("Review template").selectOption({ index: 1 });
    workflow = await saveReceipt(
      () => button("Submit for review").click(),
      "/actions/submit",
    );
    await page.getByRole("dialog").waitFor({ state: "hidden" });
  });
  await test("Assigned reviewer approves the planned observation", async () => {
    await switchUser("reviewer");
    await approve(workflow);
  });
  await test("Calculate and inspect approved-versus-missing coverage", async () => {
    await switchUser("author");
    await button("Results").click();
    await page.getByRole("button", { name: "Calculate", exact: false }).click();
    await label("Indicator").selectOption(instance.object_id);
    await label("Reporting period").selectOption({ index: 1 });
    await button("Calculate").click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await button("Result · 10").click();
    await page.getByText("50.00% approved", { exact: true }).waitFor();
    assert(
      await page
        .getByRole("region", { name: "Collection coverage" })
        .getByText("Village B", { exact: false })
        .isVisible(),
    );
    const breakdown = page.getByRole("table", { name: "Category breakdown" });
    await breakdown.waitFor();
    const cells = await breakdown.locator("tbody tr").allInnerTexts();
    assert.equal(cells.length, 2, cells.join(" | "));
    assert.match(cells[0], /sex · v2026-1\s+F\s+10\s+1\s+Adds to total/);
    assert.match(cells[1], /M\s+Undefined \(no approved values\)\s+0/);
    await page.screenshot({
      path: path.join(root, "docs/evidence/collection-coverage.png"),
    });
    await close();
  });
  await test("Submit a governed correction without replacing the approved value", async () => {
    await button("Change requests").click();
    await button("New change request").click();
    await label("Approved record").selectOption({ label: source });
    await label("Corrected value").fill("25");
    await label("Reason for change").fill(
      "Verified source correction " + unique,
    );
    await button("Save change request").click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    const row = page
      .locator("tr")
      .filter({ hasText: "Verified source correction " + unique });
    await row.getByLabel("Review policy").selectOption({ index: 1 });
    workflow = await lostResponseThenRetry(
      () =>
        row
          .getByRole("button", { name: "Submit for review", exact: true })
          .click(),
      "/actions/submit",
    );
    await row.getByText("Submitted", { exact: true }).waitFor();
    await button("Measurement").click();
    await button(source).click();
    await page.getByRole("dialog").getByText("10", { exact: true }).waitFor();
    await close();
  });
  await test("Reviewer sees current and proposed records and approves the correction", async () => {
    await switchUser("reviewer");
    await button("Review queue").click();
    await page
      .locator("tr")
      .filter({ hasText: workflow.object_id.slice(0, 8) })
      .getByRole("button")
      .first()
      .click();
    await button("Review submission").click();
    await page
      .getByRole("region", { name: "Current approved record" })
      .getByText("10", { exact: true })
      .waitFor();
    await page
      .getByRole("heading", { name: "Submitted request", exact: true })
      .waitFor();
    await label("Decision reason").fill(
      "Independently checked corrected source",
    );
    await page.screenshot({
      path: path.join(root, "docs/evidence/correction-review.png"),
    });
    await button("Approve").click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await button("Measurement").click();
    await button(source).click();
    await page.getByRole("dialog").getByText("25", { exact: true }).waitFor();
    await close();
  });
  await test("Author submits an obligation exception for independent review", async () => {
    await switchUser("author");
    await button("Change requests").click();
    await button("New change request").click();
    await label("Change type").selectOption("CollectionPlan");
    await label("Approved record").selectOption({ label: plan });
    await label("Contributor 2 eligibility").selectOption("EXCEPTED");
    await label("Exclusion reason").fill(
      "Partner was outside the eligible reporting frame " + unique,
    );
    await label("Reason for change").fill(
      "Reviewed eligibility exception " + unique,
    );
    await button("Save change request").click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    const row = page
      .locator("tr")
      .filter({ hasText: "Reviewed eligibility exception " + unique });
    await row.getByLabel("Review policy").selectOption({ index: 1 });
    workflow = await saveReceipt(
      () =>
        row
          .getByRole("button", { name: "Submit for review", exact: true })
          .click(),
      "/actions/submit",
    );
    await row.getByText("Submitted", { exact: true }).waitFor();
  });
  await test("Independent review activates the exact eligibility exception", async () => {
    await switchUser("reviewer");
    await approve(workflow);
    await button("Change requests").click();
    await page
      .locator("tr")
      .filter({ hasText: "Reviewed eligibility exception " + unique })
      .getByText("Approved", { exact: true })
      .waitFor();
  });
  await test("Personal work centre acknowledges notice and recalculates current results", async () => {
    await switchUser("author");
    await button("My work").click();
    await page.getByRole("heading", { name: "My work", exact: true }).waitFor();
    const taskRows = page
      .locator("tr")
      .filter({ hasText: "Recalculate " + indicator });
    const openTask = taskRows.filter({ hasText: "Open" }).first();
    await openTask.getByText("Open", { exact: true }).waitFor();
    const noticeRow = page
      .locator("tr")
      .filter({ hasText: "CALCULATION STALE" })
      .first();
    await lostResponseThenRetry(
      () => noticeRow.getByRole("button", { name: "Acknowledge" }).click(),
      "/actions/acknowledge",
    );
    await noticeRow.getByText("Acknowledged", { exact: true }).waitFor();
    await openTask.getByText("Open", { exact: true }).waitFor();
    await lostResponseThenRetry(
      () => openTask.getByRole("button", { name: "Recalculate" }).click(),
      "/actions/recalculate",
    );
    await taskRows
      .filter({ hasText: "Completed" })
      .first()
      .getByText("Completed", { exact: true })
      .waitFor();
    await page
      .getByRole("status")
      .filter({ hasText: "Recalculation completed" })
      .waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/work-center.png"),
    });
  });
  await test("Correction requests remain usable on mobile", async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    await button("Change requests").click();
    await page
      .locator("tr")
      .filter({ hasText: "Verified source correction " + unique })
      .getByText("Approved", { exact: true })
      .waitFor();
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    );
  });
  await test("Setup remains usable on mobile without page overflow", async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    await setupTab("Collection plans");
    await button(plan).waitFor();
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    );
    await page.screenshot({
      path: path.join(root, "docs/evidence/measurement-mobile.png"),
      fullPage: true,
    });
    assert.deepEqual(errors, []);
  });
} catch (e) {
  results.push({
    name: "Measurement browser run",
    status: "failed",
    message: e.message,
  });
  await page.screenshot({
    path: path.join(root, "docs/evidence/measurement-browser-failure.png"),
    fullPage: true,
  });
  console.error(e.message);
  process.exitCode = 1;
} finally {
  await fs.writeFile(
    path.join(root, "docs/evidence/measurement-browser-tests.json"),
    JSON.stringify(
      { engine: "Chromium 153", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
  await browser.close();
}
