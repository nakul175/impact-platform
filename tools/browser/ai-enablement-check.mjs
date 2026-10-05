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
if (!local || !base) throw Error("Use scripts/run.py ai-enablement-browser");
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
  accessibilityScans = [];
let advisoryRequests = 0,
  catalogue,
  solutionDirectory,
  planId,
  planRoute;
function observe(target) {
  target.on("request", (request) => {
    if (
      request.method() === "POST" &&
      request.url().endsWith("/ai-enablement/advisory")
    )
      advisoryRequests += 1;
  });
  target.on("pageerror", (e) => errors.push(e.message));
}
observe(page);
const button = (name) => page.getByRole("button", { name, exact: true });
const label = (name) => page.getByLabel(name, { exact: true });
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
    await label("Complete learning step " + firstPath.id + ":0").check();
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
    await button("Fill draft from brief and shortlist").click();
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
  await test("A lost save response retries the same operation and keeps newer edits unsaved", async () => {
    const sent = [];
    let active = true;
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
        await route.abort("connectionfailed");
      } else await route.fallback();
    };
    await page.route(match, intercept);
    await button("Save adoption plan").click();
    await button("Retry previous save").waitFor();
    await label("Plan name").fill("Newer unsaved edits remain visible");
    const received = await savedResponse(() =>
      button("Retry previous save").click(),
    );
    assert(received.ok(), await received.text());
    assert.equal(sent.length, 2);
    assert.deepEqual(sent[0], sent[1]);
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
        "Complete learning step " + catalogue.learning_paths[0].id + ":0",
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
      path: path.join(local, "ai-enablement-desktop.png"),
      fullPage: false,
    });
    await page
      .getByRole("heading", { name: "Your tool comparison", exact: true })
      .scrollIntoViewIfNeeded();
    await assertUsableComparison(2);
    await page.screenshot({
      path: path.join(local, "ai-enablement-comparison.png"),
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
      path: path.join(local, "ai-enablement-mobile.png"),
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
    observe(page);
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
        "Complete learning step " + catalogue.learning_paths[0].id + ":0",
      ).isDisabled(),
    );
    await button("Procurement brief").click();
    assert(await label("Pilot requirements").isDisabled());
    assert.deepEqual(errors, []);
  });
} catch (e) {
  results.push({
    name: "AI enablement browser run",
    status: "failed",
    message: e.message,
  });
  await page.screenshot({
    path: path.join(local, "ai-enablement-browser-failure.png"),
    fullPage: true,
  });
  console.error(e.message);
  process.exitCode = 1;
} finally {
  await fs.writeFile(
    path.join(root, "docs/evidence/ai-enablement-browser-tests.json"),
    JSON.stringify(
      {
        engine: process.env.IMPACT_BROWSER_EXECUTABLE
          ? "Configured Chromium browser"
          : "Chromium 153",
        results,
        uncaughtErrors: errors,
        accessibilityScans,
      },
      null,
      2,
    ),
  );
  await browser.close();
}
