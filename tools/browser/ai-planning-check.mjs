import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const axeSource = await fs.readFile(
  require.resolve("axe-core/axe.min.js"),
  "utf8",
);
const root = process.cwd();
const local = process.env.IMPACT_TEST_LOCAL;
const base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py ai-planning-browser");
const evidenceFile =
  process.env.IMPACT_BROWSER_EVIDENCE_FILE ||
  path.join(root, "docs/evidence/nonprofit-ai-planning-browser-tests.json");
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
  consoleErrors = [],
  accessibilityScans = [],
  screenshots = [];
let advisoryRequests = 0,
  planWrites = 0,
  costRequests = 0,
  catalogue,
  templates,
  planId,
  planRoute,
  savedPlan;
const startedAt = new Date().toISOString();
function observe(target) {
  target.on("request", (request) => {
    const route = new URL(request.url()).pathname;
    if (
      request.method() === "POST" &&
      route.endsWith("/ai-enablement/advisory")
    )
      advisoryRequests++;
    if (
      ["POST", "PUT"].includes(request.method()) &&
      /\/ai-enablement\/plans(?:\/[^/?]+)?$/.test(route)
    )
      planWrites++;
    if (
      request.method() === "POST" &&
      route.endsWith("/ai-enablement/cost-comparison")
    )
      costRequests++;
  });
  target.on("pageerror", (error) => errors.push(error.message));
  target.on("console", (message) => {
    if (message.type() === "error")
      consoleErrors.push({
        message: message.text(),
        location: message.location(),
      });
  });
}
observe(page);
function expectedConsoleNetworkEvent(record) {
  let route;
  try {
    route = new URL(record.location.url).pathname;
  } catch {
    return null;
  }
  if (
    route === "/auth/me" &&
    record.message ===
      "Failed to load resource: the server responded with a status of 401 (Unauthorized)"
  )
    return "Anonymous session probe before synthetic sign-in";
  if (
    route === "/favicon.ico" &&
    record.message ===
      "Failed to load resource: the server responded with a status of 404 (Not Found)"
  )
    return "Existing missing favicon resource";
  if (
    route === planRoute &&
    record.message ===
      "Failed to load resource: the server responded with a status of 404 (Not Found)"
  )
    return "Deliberate cross-tenant plan refusal";
  if (
    route === planRoute &&
    /^Failed to load resource: net::ERR_(FAILED|CONNECTION_FAILED)$/.test(
      record.message,
    )
  )
    return "Deliberate lost save response after real server commit";
  return null;
}
const button = (name) => page.getByRole("button", { name, exact: true });
const label = (name) => page.getByLabel(name, { exact: true });
const select = (name) => page.getByRole("combobox", { name, exact: true });
const practiceField = (name) =>
  page.getByRole("textbox", { name: new RegExp("^" + name) });
const costResult = () =>
  page.getByRole("region", { name: "Supplied cost results", exact: true });
const pilotResult = () =>
  page.getByRole("region", { name: "Pilot evaluation results", exact: true });
async function test(name, run) {
  await run();
  results.push({ name, status: "passed" });
  console.log("PASS " + name);
}
async function login(username) {
  await page.goto(base);
  await label("Username").fill(username);
  await label("Password").fill(passwords[username]);
  await button("Sign in →").click();
  await button("AI enablement").waitFor();
  const response = page.waitForResponse((r) =>
    r.url().endsWith("/ai-enablement/catalog"),
  );
  await button("AI enablement").click();
  catalogue = await (await response).json();
  await page.getByText(/tools shown · 0 of 4 selected/).waitFor();
}
async function responseFor(route, action) {
  const pending = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      new URL(response.url()).pathname.endsWith("/ai-enablement/" + route),
  );
  await action();
  const response = await pending;
  assert(response.ok(), await response.text());
  return await response.json();
}
async function savedResponse(action) {
  const pending = page.waitForResponse(
    (r) =>
      ["POST", "PUT"].includes(r.request().method()) &&
      /\/ai-enablement\/plans(?:\/[^/?]+)?$/.test(new URL(r.url()).pathname),
  );
  await action();
  return await pending;
}
async function openSavedPlan() {
  const pending = page.waitForResponse(
    (response) =>
      response.request().method() === "GET" &&
      new URL(response.url()).pathname === planRoute,
  );
  await button("Open saved plan").click();
  const response = await pending;
  assert(response.ok(), await response.text());
  await response.json();
  await button("Save plan changes").waitFor();
  await page.getByText("Saved plan opened.", { exact: false }).waitFor();
}
async function getPlan() {
  return await page.evaluate(async (route) => {
    const response = await fetch(route);
    return { status: response.status, body: await response.json() };
  }, planRoute);
}
async function fillLine(offer, line, values) {
  const prefix = `Offer ${offer}, line ${line} `;
  await label(prefix + "description").fill(values.description);
  await select(prefix + "category").selectOption(values.category);
  await label(prefix + "quantity").fill(values.quantity);
  await label(prefix + "unit amount (USD)").fill(values.amount);
  await select(prefix + "cadence").selectOption(values.cadence);
}
async function sample(name, values) {
  await label(name + " sample size (items)").fill(values.size);
  await label(name + " total drafting minutes").fill(values.drafting);
  await label(name + " total human review minutes").fill(values.review);
  await label(name + " factual corrections").fill(values.corrections);
}
const comparable = () =>
  page.getByRole("checkbox", {
    name: "We judge these samples comparable in task type, difficulty and quality expectations.",
    exact: true,
  });
async function shot(name) {
  const filename = "ai-planning-" + name + ".png";
  let focus = name.startsWith("cost")
    ? costResult()
    : name.startsWith("pilot")
      ? pilotResult()
      : page.getByRole("group", {
          name: "Manual practice worksheet · draft for human review",
          exact: true,
        });
  if (!(await focus.count()) && name.startsWith("cost"))
    focus = page.getByRole("group", {
      name: "Compare supplied costs",
      exact: true,
    });
  if (!(await focus.count()) && name.startsWith("pilot"))
    focus = page.getByRole("group", { name: "Evaluate a pilot", exact: true });
  if (await focus.count())
    await focus.evaluate((element) =>
      element.scrollIntoView({ block: "start" }),
    );
  await page.screenshot({ path: path.join(local, filename), fullPage: false });
  screenshots.push({
    name,
    file: path.join(local, filename),
    synthetic: true,
    realProduct: true,
  });
}
async function assertFits() {
  assert(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth + 1,
    ),
    "Planning workspace expands the viewport",
  );
  const escaping = await page
    .locator(
      ".ai-planning-tool input, .ai-planning-tool textarea, .ai-planning-tool select, .ai-planning-tool button",
    )
    .evaluateAll((controls) =>
      controls
        .filter((control) => {
          const boundary = control.closest("fieldset").getBoundingClientRect();
          const bounds = control.getBoundingClientRect();
          return (
            bounds.width > 0 &&
            (bounds.left < boundary.left - 1 ||
              bounds.right > boundary.right + 1)
          );
        })
        .map((control) => control.outerHTML),
    );
  assert.deepEqual(escaping, [], "A planning control escapes its fieldset");
}
async function scan(name) {
  if (!(await page.evaluate(() => Boolean(window.axe))))
    await page.evaluate(axeSource);
  const findings = await page.evaluate(async () =>
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
  const shape = (finding) => ({
    id: finding.id,
    impact: finding.impact,
    help: finding.help,
    nodes: finding.nodes.map((node) => ({
      target: node.target,
      summary: node.failureSummary,
    })),
  });
  accessibilityScans.push({
    name,
    violations: findings.violations.map(shape),
    incomplete: findings.incomplete.map(shape),
  });
  assert.deepEqual(
    findings.violations.map(shape),
    [],
    "Automated WCAG violations",
  );
}
try {
  await login("author");
  await label("Plan name").fill("Synthetic nonprofit planning comparison");
  await label("AI goal").fill(
    "Practise invented workshop communications with human review.",
  );
  await test("An unfinished cost draft cannot calculate or save, and unknown amounts remain explicit", async () => {
    await button("Procurement brief").click();
    await button("Add cost comparison").click();
    assert(await button("Calculate supplied costs").isDisabled());
    const before = costRequests;
    await label("Cost comparison currency").fill("usd");
    assert.equal(await label("Cost comparison currency").inputValue(), "USD");
    await label("Comparison months").fill("3");
    await label("Offer 1 name").fill("Fictional monthly offer");
    await fillLine(1, 1, {
      description: "Synthetic subscription",
      category: "SUBSCRIPTION",
      quantity: "2",
      amount: "10",
      cadence: "MONTHLY",
    });
    await button("Add cost offer").click();
    await label("Offer 2 name").fill("Fictional integration offer");
    await fillLine(2, 1, {
      description: "Unquoted synthetic integration",
      category: "INTEGRATION",
      quantity: "0",
      amount: "",
      cadence: "ONE_OFF",
    });
    assert.equal(costRequests, before);
    assert.equal(await button("Calculate supplied costs").isDisabled(), false);
    const result = await responseFor("cost-comparison", () =>
      button("Calculate supplied costs").click(),
    );
    assert.deepEqual(
      Object.keys(result).sort(),
      [
        "currency",
        "period_months",
        "status",
        "offers",
        "cheapest_offer_ids",
        "disclaimer",
      ].sort(),
    );
    assert.equal(result.status, "INCOMPLETE");
    assert.equal(result.offers[0].known_subtotal, "60");
    assert.equal(result.offers[1].known_subtotal, "0");
    assert.equal(result.offers[1].complete_total, null);
    assert.equal(result.offers[1].missing_line_ids.length, 1);
    assert.deepEqual(result.cheapest_offer_ids, []);
    await costResult()
      .getByText("Some costs are unknown.", { exact: false })
      .waitFor();
    assert.equal(
      await costResult()
        .getByText(/lowest supplied total|Lowest supplied complete total/)
        .count(),
      0,
    );
  });
  await test("Complete monthly totals retain exact amounts and equally lowest supplied offers remain a tie", async () => {
    await label("Offer 2, line 1 quantity").fill("1");
    await label("Offer 2, line 1 unit amount (USD)").fill("60");
    assert.equal(await costResult().count(), 0);
    const result = await responseFor("cost-comparison", () =>
      button("Calculate supplied costs").click(),
    );
    assert.equal(result.status, "COMPLETE");
    assert.deepEqual(
      result.offers.map((offer) => offer.complete_total),
      ["60", "60"],
    );
    assert.deepEqual(
      result.cheapest_offer_ids,
      result.offers.map((offer) => offer.id),
    );
    await costResult().waitFor();
    assert.equal(
      await costResult()
        .getByText("Equal lowest supplied total (tie).", { exact: false })
        .count(),
      2,
    );
    await shot("cost-desktop");
  });
  await test("Editing clears calculated output and invalid decimal notation makes no calculation request", async () => {
    await label("Offer 1, line 1 quantity").fill("1e3");
    assert.equal(await costResult().count(), 0);
    assert(await button("Calculate supplied costs").isDisabled());
    const writes = planWrites;
    await button("Save adoption plan").click();
    await page
      .getByRole("alert")
      .getByText("Complete the cost comparison before saving", { exact: false })
      .waitFor();
    assert.equal(planWrites, writes);
    await label("Offer 1, line 1 quantity").fill("2");
  });
  await test("A delayed real cost response cannot revive results after a new edit", async () => {
    let release, fetched, finished;
    const completed = new Promise((resolve) => {
      finished = resolve;
    });
    const responseReady = new Promise((resolve) => {
      fetched = resolve;
    });
    const held = new Promise((resolve) => {
      release = resolve;
    });
    const match = (url) =>
      url.pathname.endsWith("/ai-enablement/cost-comparison");
    const handler = async (route) => {
      const response = await route.fetch();
      assert(response.ok(), await response.text());
      fetched();
      await held;
      await route.fulfill({ response }).catch((error) => {
        if (
          !/closed|abort|Target page|interrupted|already handled/i.test(
            error.message,
          )
        )
          throw error;
      });
      finished();
    };
    await page.route(match, handler);
    await button("Calculate supplied costs").click();
    await responseReady;
    await label("Offer 1, line 1 unit amount (USD)").fill("11");
    release();
    await completed;
    await page.unroute(match, handler);
    assert.equal(await costResult().count(), 0);
    assert.equal(
      await label("Offer 1, line 1 unit amount (USD)").inputValue(),
      "11",
    );
    const current = await responseFor("cost-comparison", () =>
      button("Calculate supplied costs").click(),
    );
    assert.deepEqual(
      current.offers.map((offer) => offer.complete_total),
      ["66", "60"],
    );
  });
  await test("Pilot calculations include human review and normalize different sample sizes", async () => {
    await button("Pilot tracker").click();
    await button("Add pilot evaluation").click();
    assert(await button("Calculate pilot comparison").isDisabled());
    await label("Task being compared").fill("Synthetic invitation drafting");
    await sample("Baseline", {
      size: "2",
      drafting: "40",
      review: "20",
      corrections: "1",
    });
    await sample("Pilot", {
      size: "4",
      drafting: "60",
      review: "20",
      corrections: "2",
    });
    await comparable().check();
    await label("Pilot comparison notes").fill(
      "Synthetic observations; review minutes included for both samples.",
    );
    const result = await responseFor("pilot-evaluation", () =>
      button("Calculate pilot comparison").click(),
    );
    assert.deepEqual(
      Object.keys(result).sort(),
      [
        "status",
        "task_label",
        "comparable",
        "notes",
        "source",
        "baseline",
        "pilot",
        "improvement",
        "disclaimer",
      ].sort(),
    );
    assert.equal(result.status, "SELF_REPORTED_DRAFT");
    assert.equal(result.baseline.total_minutes, "60");
    assert.equal(result.baseline.minutes_per_item, "30");
    assert.equal(result.pilot.total_minutes, "80");
    assert.equal(result.pilot.minutes_per_item, "20");
    assert.equal(result.baseline.factual_corrections_per_item, "0.5");
    assert.equal(result.pilot.factual_corrections_per_item, "0.5");
    assert.deepEqual(result.improvement, {
      status: "DEFINED",
      percent: "33.333333",
      reason: "COMPARABLE_SAMPLES",
    });
    await pilotResult()
      .getByText("Relative time improvement: 33.333333%", { exact: false })
      .waitFor();
    await shot("pilot-desktop");
  });
  await test("Zero baseline and incomparable samples produce undefined change rather than a false zero", async () => {
    await label("Baseline total drafting minutes").fill("0");
    await label("Baseline total human review minutes").fill("0");
    assert.equal(await pilotResult().count(), 0);
    const zero = await responseFor("pilot-evaluation", () =>
      button("Calculate pilot comparison").click(),
    );
    assert.deepEqual(zero.improvement, {
      status: "UNDEFINED",
      percent: null,
      reason: "ZERO_BASELINE",
    });
    await pilotResult()
      .getByText("Time change is undefined because baseline time is zero.", {
        exact: true,
      })
      .waitFor();
    await label("Baseline total drafting minutes").fill("40");
    await label("Baseline total human review minutes").fill("20");
    await comparable().uncheck();
    const unknown = await responseFor("pilot-evaluation", () =>
      button("Calculate pilot comparison").click(),
    );
    assert.deepEqual(unknown.improvement, {
      status: "UNDEFINED",
      percent: null,
      reason: "SAMPLES_NOT_COMPARABLE",
    });
    await pilotResult()
      .getByText(
        "Time change is undefined because the samples were reported as not comparable.",
        { exact: true },
      )
      .waitFor();
    await comparable().check();
  });
  await test("A slower pilot shows negative improvement and preserves source values", async () => {
    await label("Pilot total drafting minutes").fill("180");
    const result = await responseFor("pilot-evaluation", () =>
      button("Calculate pilot comparison").click(),
    );
    assert.equal(result.improvement.percent, "-66.666667");
    assert.equal(result.source.pilot.total_drafting_minutes, "180");
    await pilotResult()
      .getByText("Pilot took more staff time per item.", { exact: false })
      .waitFor();
    await label("Pilot total drafting minutes").fill("60");
  });
  await test("Manual task practice exposes five review checks, resets checks after editing and makes no model request", async () => {
    const pending = page.waitForResponse((r) =>
      r.url().endsWith("/ai-enablement/task-templates"),
    );
    await button("Practise a useful task").click();
    templates = await (await pending).json();
    assert.equal(templates.templates.length, 4);
    assert(
      templates.templates.every(
        (template) => template.review_steps.length === 5,
      ),
    );
    await select("Practice task").selectOption(templates.templates[0].id);
    const checks = templates.templates[0].review_steps;
    await practiceField("Your synthetic or public-text brief").fill(
      "Invented workshop at a fictional community hall. Registration not supplied.",
    );
    await practiceField("Your manually written draft").fill(
      "Draft for human review: Join our invented workshop. Registration: Not supplied.",
    );
    await practiceField("Human review notes and unresolved questions").fill(
      "Communications reviewer must confirm registration and access information.",
    );
    for (const check of checks) await label(check.label).check();
    assert.equal(
      await page
        .getByRole("group", {
          name: "Self-checks · these do not certify competence",
          exact: true,
        })
        .locator("input:checked")
        .count(),
      5,
    );
    await practiceField("Human review notes and unresolved questions").fill(
      "Updated synthetic review note; confirm registration and access information.",
    );
    for (const check of checks)
      assert.equal(await label(check.label).isChecked(), false);
    await label(checks[0].label).check();
    await select("Practice task").selectOption(templates.templates[1].id);
    assert.equal(await label(checks[0].label).isChecked(), false);
    assert(
      (
        await practiceField("Your manually written draft").inputValue()
      ).startsWith("Draft for human review"),
    );
    await select("Practice task").selectOption(templates.templates[0].id);
    for (const check of checks) await label(check.label).check();
    await page
      .getByText(
        "No certificate, publication, supplier message or purchase is created",
        { exact: false },
      )
      .waitFor();
    assert.equal(advisoryRequests, 0);
    await shot("practice-desktop");
  });
  await test("Saving and reopening persists actual cost, pilot and practice inputs but no transient calculation result", async () => {
    await button("Build team capacity").click();
    const key = catalogue.learning_paths[0].lessons[0].key;
    assert(!/:\d+$/.test(key), "A lesson still uses a positional identity");
    await label("Complete learning step " + key).check();
    const response = await savedResponse(() =>
      button("Save adoption plan").click(),
    );
    assert(response.ok(), await response.text());
    const receipt = await response.json();
    planId = receipt.object_id;
    planRoute = new URL(response.url()).pathname + "/" + planId;
    savedPlan = (await getPlan()).body;
    assert.equal(
      savedPlan.data.planning.cost_comparison.offers[0].lines[0].unit_amount,
      "11",
    );
    assert.equal(
      savedPlan.data.planning.pilot_evaluation.baseline.total_review_minutes,
      "20",
    );
    assert.equal(savedPlan.data.planning.pilot_evaluation.pilot.sample_size, 4);
    assert.equal(savedPlan.data.planning.task_practice.checked_steps.length, 5);
    assert.deepEqual(Object.keys(savedPlan.data.planning).sort(), [
      "cost_comparison",
      "pilot_evaluation",
      "task_practice",
    ]);
    await page.reload();
    await button("AI enablement").click();
    await label("Saved adoption plans").selectOption(planId);
    await openSavedPlan();
    await page.getByText("Saved plan opened.", { exact: false }).waitFor();
    await button("Procurement brief").click();
    assert.equal(
      await label("Offer 1, line 1 unit amount (USD)").inputValue(),
      "11",
    );
    assert.equal(await label("Comparison months").inputValue(), "3");
    assert.equal(await costResult().count(), 0);
    await button("Pilot tracker").click();
    assert.equal(await label("Pilot sample size (items)").inputValue(), "4");
    assert.equal(
      await label("Baseline total human review minutes").inputValue(),
      "20",
    );
    assert.equal(await pilotResult().count(), 0);
    await button("Practise a useful task").click();
    assert.equal(
      await practiceField("Your synthetic or public-text brief").inputValue(),
      savedPlan.data.planning.task_practice.brief,
    );
    for (const check of templates.templates[0].review_steps)
      assert(await label(check.label).isChecked());
  });
  await test("Saved guide compatibility names current editions and reading leaves the revision unchanged", async () => {
    await page
      .getByRole("heading", { name: "Saved guide compatibility", exact: true })
      .waitFor();
    await page
      .getByText("Older guide text and product terms are not archived here.", {
        exact: false,
      })
      .waitFor();
    const before = planWrites;
    const current = await getPlan();
    assert.equal(current.status, 200);
    assert.deepEqual(
      Object.keys(current.body.content_compatibility).sort(),
      [
        "current_versions",
        "catalog_version_status",
        "solutions_version_status",
        "learning_completed",
        "legacy_learning_keys",
        "unavailable_learning_keys",
        "historical_snapshots_available",
      ].sort(),
    );
    assert.equal(
      current.body.content_compatibility.catalog_version_status,
      "CURRENT",
    );
    assert.equal(
      current.body.content_compatibility.solutions_version_status,
      "CURRENT",
    );
    assert.equal(
      current.body.content_compatibility.historical_snapshots_available,
      false,
    );
    assert.equal(current.body.revision_id, savedPlan.revision_id);
    assert.equal(planWrites, before);
    await button("Build team capacity").click();
    assert(
      await label(
        "Complete learning step " + catalogue.learning_paths[0].lessons[0].key,
      ).isChecked(),
    );
  });
  await test("Simulated retired-guide projection preserves unavailable progress until explicit removal", async () => {
    // Only this historical compatibility projection is simulated. Its original
    // response, current authority, persisted plan and all writes use the real API.
    const retired = "retired:synthetic-lesson";
    const match = (url) => url.pathname === planRoute;
    const handler = async (route) => {
      if (route.request().method() !== "GET") return route.fallback();
      const response = await route.fetch();
      assert(response.ok(), await response.text());
      const projection = await response.json();
      projection.data.learning_completed.push(retired);
      projection.content_compatibility.unavailable_learning_keys.push(retired);
      await route.fulfill({ response, json: projection });
    };
    await page.route(match, handler);
    await openSavedPlan();
    await page.getByText("Saved plan opened.", { exact: false }).waitFor();
    await label("Plan name").fill(
      "Unrelated synthetic name edit preserves historical progress",
    );
    await button("Build team capacity").click();
    await page
      .getByText(`This saved learning entry (${retired}) is unavailable`, {
        exact: false,
      })
      .waitFor();
    const writes = planWrites;
    await button("Save plan changes").click();
    await page
      .getByRole("alert")
      .getByText("Some saved learning progress is unavailable", {
        exact: false,
      })
      .waitFor();
    assert.equal(planWrites, writes);
    assert.equal(
      await button("Remove unavailable progress from this draft").count(),
      1,
    );
    await button("Remove unavailable progress from this draft").click();
    assert.equal(
      await page
        .getByText(`This saved learning entry (${retired}) is unavailable`, {
          exact: false,
        })
        .count(),
      0,
    );
    await page.unroute(match, handler);
    const response = await savedResponse(() =>
      button("Save plan changes").click(),
    );
    assert(response.ok(), await response.text());
    const current = (await getPlan()).body;
    assert.deepEqual(
      current.data.learning_completed,
      savedPlan.data.learning_completed,
    );
    assert.equal(
      current.data.title,
      "Unrelated synthetic name edit preserves historical progress",
    );
    savedPlan = current;
  });
  await test("Simulated unavailable practice keeps entered text and requires deliberate replacement before saving", async () => {
    const original = structuredClone(
      (await getPlan()).body.data.planning.task_practice,
    );
    const match = (url) => url.pathname === planRoute;
    const handler = async (route) => {
      if (route.request().method() !== "GET") return route.fallback();
      const response = await route.fetch();
      const projection = await response.json();
      projection.data.planning.task_practice.template_id =
        "retired_synthetic_practice";
      delete projection.data.content_versions.practice;
      await route.fulfill({ response, json: projection });
    };
    await page.route(match, handler);
    await openSavedPlan();
    await page.getByText("Saved plan opened.", { exact: false }).waitFor();
    await button("Practise a useful task").click();
    await page
      .getByText(
        "Saved practice task “retired_synthetic_practice” is unavailable",
        { exact: false },
      )
      .waitFor();
    await page
      .getByText("Saved practice edition: Unknown", { exact: false })
      .waitFor();
    await page
      .getByText("Historical guidance wording is not available.", {
        exact: false,
      })
      .waitFor();
    assert.equal(
      await practiceField("Your synthetic or public-text brief").inputValue(),
      original.brief,
    );
    assert.equal(
      await practiceField("Your manually written draft").inputValue(),
      original.draft,
    );
    assert.equal(
      await practiceField(
        "Human review notes and unresolved questions",
      ).inputValue(),
      original.review_notes,
    );
    assert.equal(
      await practiceField("Your manually written draft").isEditable(),
      false,
    );
    assert(await button("Replace missing task and keep text").isDisabled());
    const writes = planWrites;
    await button("Save plan changes").click();
    await page
      .getByText("The saved practice exercise is unavailable", { exact: false })
      .waitFor();
    assert.equal(planWrites, writes);
    await select("Replacement practice task").selectOption(
      templates.templates[1].id,
    );
    assert.equal(
      await practiceField("Your manually written draft").isEditable(),
      false,
    );
    await page
      .getByText(
        "Saved practice task “retired_synthetic_practice” is unavailable",
        { exact: false },
      )
      .waitFor();
    await scan("Simulated unavailable practice preservation");
    await button("Replace missing task and keep text").click();
    assert.equal(
      await select("Practice task").inputValue(),
      templates.templates[1].id,
    );
    assert.equal(
      await practiceField("Your manually written draft").inputValue(),
      original.draft,
    );
    assert.equal(
      await page
        .getByRole("group", {
          name: "Self-checks · these do not certify competence",
          exact: true,
        })
        .locator("input:checked")
        .count(),
      0,
    );
    await page.unroute(match, handler);
    const response = await savedResponse(() =>
      button("Save plan changes").click(),
    );
    assert(response.ok(), await response.text());
    savedPlan = (await getPlan()).body;
    assert.deepEqual(savedPlan.data.planning.task_practice, {
      ...original,
      template_id: templates.templates[1].id,
      checked_steps: [],
    });
  });
  await test("Simulated stale practice edition is labelled without claiming historical guide wording", async () => {
    const match = (url) => url.pathname === planRoute;
    const handler = async (route) => {
      if (route.request().method() !== "GET") return route.fallback();
      const response = await route.fetch();
      const projection = await response.json();
      projection.data.content_versions.practice =
        "synthetic-historical-practice-edition";
      await route.fulfill({ response, json: projection });
    };
    await page.route(match, handler);
    await openSavedPlan();
    await page.getByText("Saved plan opened.", { exact: false }).waitFor();
    await button("Practise a useful task").click();
    await page
      .getByText("Saved practice edition: Stale", { exact: false })
      .waitFor();
    await page
      .getByText("Historical guidance wording is not available.", {
        exact: false,
      })
      .waitFor();
    assert.equal(
      await practiceField("Your manually written draft").inputValue(),
      savedPlan.data.planning.task_practice.draft,
    );
    await page.unroute(match, handler);
    await openSavedPlan();
    await page.getByText("Saved plan opened.", { exact: false }).waitFor();
    await page
      .getByText("Saved practice edition: Current", { exact: false })
      .waitFor();
  });
  await test("Simulated unavailable practice is cleared only by the explicit clear action and save", async () => {
    const match = (url) => url.pathname === planRoute;
    const handler = async (route) => {
      if (route.request().method() !== "GET") return route.fallback();
      const response = await route.fetch();
      const projection = await response.json();
      projection.data.planning.task_practice.template_id =
        "retired_synthetic_practice";
      await route.fulfill({ response, json: projection });
    };
    await page.route(match, handler);
    await openSavedPlan();
    await page.getByText("Saved plan opened.", { exact: false }).waitFor();
    await button("Practise a useful task").click();
    await page
      .getByText(
        "Saved practice task “retired_synthetic_practice” is unavailable",
        { exact: false },
      )
      .waitFor();
    const writes = planWrites;
    await button("Clear saved practice worksheet").click();
    assert.equal(planWrites, writes);
    assert.equal(
      await practiceField("Your manually written draft").inputValue(),
      "",
    );
    await page.unroute(match, handler);
    const response = await savedResponse(() =>
      button("Save plan changes").click(),
    );
    assert(response.ok(), await response.text());
    savedPlan = (await getPlan()).body;
    assert.equal(savedPlan.data.planning.task_practice, null);
  });
  await test("Ambiguous save recovery replays exact planning inputs while newer changes remain unsaved", async () => {
    await button("Procurement brief").click();
    await label("Offer 1, line 1 unit amount (USD)").fill("12");
    const sent = [];
    let active = true;
    const match = (url) => url.pathname === planRoute;
    const handler = async (route) => {
      if (!active || route.request().method() !== "PUT")
        return route.fallback();
      sent.push(route.request().postDataJSON());
      if (sent.length === 1) {
        const response = await route.fetch();
        assert(response.ok(), await response.text());
        await route.abort("connectionfailed");
      } else await route.fallback();
    };
    await page.route(match, handler);
    await button("Save plan changes").click();
    await button("Retry previous save").waitFor();
    await label("Offer 1, line 1 unit amount (USD)").fill("13");
    const retry = await savedResponse(() =>
      button("Retry previous save").click(),
    );
    assert(retry.ok(), await retry.text());
    assert.equal(sent.length, 2);
    assert.deepEqual(sent[0], sent[1]);
    assert.equal(
      sent[1].data.planning.cost_comparison.offers[0].lines[0].unit_amount,
      "12",
    );
    assert.equal(
      await label("Offer 1, line 1 unit amount (USD)").inputValue(),
      "13",
    );
    await page
      .getByText("Unsaved changes to this shared draft.", { exact: true })
      .waitFor();
    assert.equal(
      (await getPlan()).body.data.planning.cost_comparison.offers[0].lines[0]
        .unit_amount,
      "12",
    );
    active = false;
    await page.unroute(match, handler);
    const update = await savedResponse(() =>
      button("Save plan changes").click(),
    );
    assert(update.ok(), await update.text());
    assert.equal(
      (await getPlan()).body.data.planning.cost_comparison.offers[0].lines[0]
        .unit_amount,
      "13",
    );
  });
  await test("Navigating away during a real calculation cannot revive the previous section's result on return", async () => {
    let release, fetched, finished;
    const completed = new Promise((resolve) => {
      finished = resolve;
    });
    const ready = new Promise((resolve) => {
      fetched = resolve;
    });
    const held = new Promise((resolve) => {
      release = resolve;
    });
    const match = (url) =>
      url.pathname.endsWith("/ai-enablement/cost-comparison");
    const handler = async (route) => {
      const response = await route.fetch();
      assert(response.ok(), await response.text());
      fetched();
      await held;
      await route.fulfill({ response }).catch((error) => {
        if (
          !/closed|abort|Target page|interrupted|already handled/i.test(
            error.message,
          )
        )
          throw error;
      });
      finished();
    };
    await page.route(match, handler);
    await button("Calculate supplied costs").click();
    await ready;
    await button("Build team capacity").click();
    release();
    await completed;
    await page.unroute(match, handler);
    await button("Procurement brief").click();
    assert.equal(await costResult().count(), 0);
    await responseFor("cost-comparison", () =>
      button("Calculate supplied costs").click(),
    );
    await costResult().waitFor();
  });
  await test("New product controls fit desktop and 390 px views with all automated accessibility findings retained", async () => {
    for (const viewport of [
      { width: 1440, height: 1050 },
      { width: 390, height: 844 },
    ]) {
      await page.setViewportSize(viewport);
      for (const name of [
        "Procurement brief",
        "Pilot tracker",
        "Practise a useful task",
      ]) {
        await button(name).click();
        await assertFits();
        await scan(`${name}: ${viewport.width}px`);
        if (viewport.width === 390)
          await shot(
            name === "Procurement brief"
              ? "cost-mobile"
              : name === "Pilot tracker"
                ? "pilot-mobile"
                : "practice-mobile",
          );
      }
    }
    assert.deepEqual(errors, []);
  });
  await test("A delayed calculation from a previous signed-in tenant cannot appear after changing user and workspace", async () => {
    await page.setViewportSize({ width: 1440, height: 1050 });
    await button("Procurement brief").click();
    let release, fetched, finished;
    const ready = new Promise((resolve) => {
      fetched = resolve;
    });
    const held = new Promise((resolve) => {
      release = resolve;
    });
    const completed = new Promise((resolve) => {
      finished = resolve;
    });
    const match = (url) =>
      url.pathname.endsWith("/ai-enablement/cost-comparison");
    const handler = async (route) => {
      const response = await route.fetch();
      assert(response.ok(), await response.text());
      fetched();
      await held;
      await route.fulfill({ response }).catch((error) => {
        if (
          !/closed|abort|Target page|interrupted|already handled/i.test(
            error.message,
          )
        )
          throw error;
      });
      finished();
    };
    await page.route(match, handler);
    await button("Calculate supplied costs").click();
    await ready;
    const writes = planWrites;
    await button("Sign out").click();
    await label("Username").waitFor();
    await login("other_tenant");
    release();
    await completed;
    await page.unroute(match, handler);
    await button("Procurement brief").click();
    assert.equal(await costResult().count(), 0);
    assert.equal(await label("Offer 1 name").count(), 0);
    assert.equal(await button("Add cost comparison").count(), 0);
    assert.equal(planWrites, writes);
  });
  await test("Read-only staff can study guides and calculate supplied drafts but cannot save or read another tenant's plan", async () => {
    page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
    page.setDefaultTimeout(15000);
    observe(page);
    await login("other_tenant");
    const before = planWrites;
    assert.equal(await button("Save adoption plan").count(), 0);
    assert.equal(await button("New adoption plan").count(), 0);
    await button("Procurement brief").click();
    assert.equal(await button("Add cost comparison").count(), 0);
    assert(await label("Pilot requirements").isDisabled());
    await button("Pilot tracker").click();
    assert.equal(await button("Add pilot evaluation").count(), 0);
    await button("Practise a useful task").click();
    await select("Practice task").waitFor();
    await select("Practice task").selectOption(templates.templates[2].id);
    assert(await practiceField("Your manually written draft").isDisabled());
    assert(
      await label(templates.templates[2].review_steps[0].label).isDisabled(),
    );
    const answer = await page.evaluate(
      async ({ cost, pilot, hiddenPlan }) => {
        const me = await (await fetch("/auth/me")).json();
        const tenant = me.tenants[0].tenant_id;
        const headers = {
          "Content-Type": "application/json",
          "X-CSRF-Token": me.csrf_token,
        };
        const calculation = await fetch(
          `/v1/tenants/${tenant}/ai-enablement/cost-comparison`,
          { method: "POST", headers, body: JSON.stringify(cost) },
        );
        const evaluation = await fetch(
          `/v1/tenants/${tenant}/ai-enablement/pilot-evaluation`,
          { method: "POST", headers, body: JSON.stringify(pilot) },
        );
        const unavailable = await fetch(hiddenPlan);
        return {
          cost: calculation.status,
          pilot: evaluation.status,
          unavailable: unavailable.status,
          hidden: await unavailable.json(),
        };
      },
      {
        cost: savedPlan.data.planning.cost_comparison,
        pilot: savedPlan.data.planning.pilot_evaluation,
        hiddenPlan: planRoute,
      },
    );
    assert.equal(answer.cost, 200);
    assert.equal(answer.pilot, 200);
    assert.equal(answer.unavailable, 404);
    assert.equal(answer.hidden.code, "RESOURCE_UNAVAILABLE");
    assert.equal(planWrites, before);
    await scan("Read-only practice worksheet");
  });
  await test("No advisory/provider request or uncaught browser error occurs across these synthetic workflows", async () => {
    assert.equal(advisoryRequests, 0);
    assert.deepEqual(errors, []);
    const unexpected = consoleErrors.filter(
      (record) => !expectedConsoleNetworkEvent(record),
    );
    assert.deepEqual(unexpected, [], "Unexpected browser console errors");
  });
} catch (error) {
  results.push({
    name: "AI planning browser run",
    status: "failed",
    message: error.message,
  });
  await page.screenshot({
    path: path.join(local, "ai-planning-browser-failure.png"),
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
        engine: process.env.IMPACT_BROWSER_EXECUTABLE
          ? "Configured Chromium browser"
          : "Chromium 153",
        browser_version: browser.version(),
        database:
          "Disposable in-memory PGlite through the real FastAPI service",
        fixture: "Synthetic fixture only",
        results,
        uncaughtErrors: errors,
        consoleErrors,
        accessibilityScans,
        screenshots,
        expectedConsoleNetworkEvents: consoleErrors
          .map((record) => ({
            ...record,
            reason: expectedConsoleNetworkEvent(record),
          }))
          .filter((record) => record.reason),
        advisoryRequests,
        planWrites,
        costRequests,
        limits: [
          "Local browser evidence only; no native concurrency, hosted deployment, manual screen-reader review or user acceptance.",
          "No live provider, supplier message, purchase, competence certification or official impact record was exercised.",
          "Accessibility incomplete findings are retained separately and require manual review.",
          "Four historical content-compatibility projections are explicitly simulated; their surrounding authority, calculations and persisted writes use the real API.",
        ],
      },
      null,
      2,
    ),
  );
  await browser.close();
}
