import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { createHash } from "node:crypto";

const require = createRequire(import.meta.url);
const axeSource = await fs.readFile(
  require.resolve("axe-core/axe.min.js"),
  "utf8",
);
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
    "Use scripts/run.py ai-planning-browser with a disposable loopback fixture",
  );
const evidenceFile =
  process.env.IMPACT_BROWSER_EVIDENCE_FILE ||
  path.join(root, "docs/evidence/nonprofit-ai-planning-browser-tests.json");
const captureDirectory =
  process.env.IMPACT_BROWSER_CAPTURE_DIRECTORY ||
  path.join(local, "ai-planning-captures");
await fs.mkdir(captureDirectory, { recursive: true });
const fixture = JSON.parse(
  await fs.readFile(
    path.join(root, "specification/fixtures/api-fixture.json"),
    "utf8",
  ),
);
const sourceDirectories = [
  "apps/api/impact_api",
  "apps/web/src",
  "packages/contracts",
  "infrastructure/migrations",
  "qualification",
];
const fixedSources = [
  "VERSION.json",
  "tools/browser/ai-planning-check.mjs",
  "scripts/run.py",
  "scripts/fixture_support.py",
  "specification/fixtures/api-fixture.json",
  "specification/fixtures/records.json",
  "apps/web/dist/index.html",
];
async function sourceHashes() {
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
  assert.equal(
    html,
    await fs.readFile(path.join(root, "apps/web/dist/index.html"), "utf8"),
  );
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
const canonical = (value) =>
  JSON.stringify(value, (key, item) =>
    item && typeof item === "object" && !Array.isArray(item)
      ? Object.fromEntries(
          Object.keys(item)
            .sort()
            .map((key) => [key, item[key]]),
        )
      : item,
  );
let qualifiedSources, currentSources, qualifiedAssets, currentAssets, runtime;
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
  coverageLayouts = [],
  screenshots = [],
  externalRequests = [],
  deliberateRefusals = [];
let advisoryRequests = 0,
  planWrites = 0,
  costRequests = 0,
  planReads = 0,
  guidedBefore,
  expectedGuidedPractice,
  catalogue,
  templates,
  planId,
  planRoute,
  savedPlan;
const startedAt = new Date().toISOString();
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
    if (
      request.method() === "GET" &&
      /\/ai-enablement\/plans\/[^/?]+$/.test(route)
    )
      planReads++;
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
await observe(page);
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
  const deliberate = deliberateRefusals.find(
    (item) =>
      item.path === route &&
      record.message ===
        `Failed to load resource: the server responded with a status of ${item.status} (Not Found)`,
  );
  if (deliberate) return deliberate.scope;
  return null;
}
const button = (name) => page.getByRole("button", { name, exact: true });
const label = (name) => page.getByLabel(name, { exact: true });
const select = (name) => page.getByRole("combobox", { name, exact: true });
const practiceField = (name) =>
  page.getByRole("textbox", { name: new RegExp("^" + name) });
const costResult = () =>
  page.getByRole("region", { name: "Supplied cost results", exact: true });
const coverage = () =>
  page.getByRole("region", { name: "Cost category coverage", exact: true });
const coverageRow = (category) =>
  coverage()
    .getByRole("row")
    .filter({
      has: page.getByRole("rowheader", { name: category, exact: true }),
    });
async function settleCoverageScroll() {
  assert(
    await coverage().evaluate(async (element) => {
      let previous = element.scrollLeft,
        stable = 0;
      for (let frame = 0; frame < 90; frame++) {
        await new Promise((resolve) => requestAnimationFrame(resolve));
        const current = element.scrollLeft;
        stable = current === previous ? stable + 1 : 0;
        previous = current;
        if (stable >= 10) return true;
      }
      return false;
    }),
    "Coverage scrolling did not settle within its bounded animation wait",
  );
}
async function coverageLayout(edge) {
  const geometry = await coverage().evaluate((element) => {
    const table = element.querySelector("table"),
      title = document.getElementById(table.getAttribute("aria-labelledby")),
      rows = [...table.querySelectorAll("tbody tr")],
      row = rows[0],
      cells = row.querySelectorAll("td"),
      rect = (node) => {
        const { left, right, width } = node.getBoundingClientRect();
        return { left, right, width };
      },
      textRects = (node) => {
        const range = document.createRange();
        range.selectNodeContents(node);
        return [...range.getClientRects()].map(({ left, right }) => ({
          left,
          right,
        }));
      };
    return {
      viewport: innerWidth,
      clientWidth: element.clientWidth,
      scrollWidth: element.scrollWidth,
      integerScrollRange: element.scrollWidth - element.clientWidth,
      documentHasFocus: document.hasFocus(),
      visibilityState: document.visibilityState,
      scrollLeft: element.scrollLeft,
      region: rect(element),
      category: rect(row.querySelector("th")),
      firstOffer: rect(cells[0]),
      lastOffer: rect(cells[cells.length - 1]),
      firstText: rows.flatMap((row) => textRects(row.querySelector("td"))),
      lastText: rows.flatMap((row) =>
        textRects(row.querySelector("td:last-child")),
      ),
      title: rect(title),
      titleText: textRects(title),
      titleOutsideScroller: !element.contains(title),
    };
  });
  assert(geometry.titleOutsideScroller);
  assert(geometry.title.left >= 0 && geometry.title.right <= geometry.viewport);
  assert(
    geometry.titleText.every(
      (rect) => rect.left >= 0 && rect.right <= geometry.viewport + 1,
    ),
  );
  assert(geometry.category.left >= geometry.region.left - 1);
  assert(geometry.category.width <= geometry.region.width / 2);
  const cell = edge === "first" ? geometry.firstOffer : geometry.lastOffer,
    texts = edge === "first" ? geometry.firstText : geometry.lastText;
  assert(cell.left >= geometry.category.right - 1);
  assert(cell.right <= geometry.region.right + 1);
  assert(
    cell.width >= 90,
    "An offer needs usable room for complete status text",
  );
  assert(
    texts.length > 0 &&
      texts.every(
        (rect) =>
          rect.left >= geometry.category.right - 1 &&
          rect.right <= geometry.region.right + 1,
      ),
    "Every line of the visible offer status must fit beside the sticky category",
  );
  coverageLayouts.push({ edge, ...geometry });
  return geometry;
}
const openedSource =
  "Calculation source: the opened saved plan inputs. Results remain temporary.";
const localSource =
  "Calculation source: local plan inputs. Reopen the saved plan to check its saved revision.";
const unsavedSource =
  "Calculation source: unsaved plan inputs. Save the plan to keep these entries.";
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
  await page.screenshot({
    path: path.join(captureDirectory, filename),
    fullPage: false,
  });
  screenshots.push({
    name,
    file: path.join(captureDirectory, filename),
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
  qualifiedSources = await sourceHashes();
  qualifiedAssets = await servedHashes();
  await test("Actual loopback runtime matches the qualified source and served build", async () => {
    const response = await fetch(base + "/v1/runtime-manifest", {
      headers: {
        Authorization: "Bearer " + process.env[fixture.actors.author.token_env],
      },
    });
    assert.equal(response.status, 200);
    runtime = await response.json();
    const version = JSON.parse(
      await fs.readFile(path.join(root, "VERSION.json"), "utf8"),
    );
    assert.equal(runtime.environment, "test");
    assert.equal(runtime.build_id, "impact-" + version.build);
    assert.equal(runtime.api_version, version.domain_api);
    assert.equal(runtime.mutation_tests_allowed, true);
    const migrations = Object.keys(qualifiedSources).filter((file) =>
      /^infrastructure\/migrations\/\d{4}_.*\.sql$/.test(file),
    );
    assert.equal(runtime.schema_version, String(migrations.length));
  });
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
    await coverage().waitFor();
    assert.equal(
      await coverageRow("Training")
        .getByRole("cell", { name: "Not recorded", exact: true })
        .count(),
      2,
    );
    assert.equal(
      await coverageRow("Exit")
        .getByRole("cell", { name: "Not recorded", exact: true })
        .count(),
      2,
    );
    assert.equal(
      await coverageRow("Integration")
        .getByRole("cell", { name: "Contains an unknown amount", exact: true })
        .count(),
      1,
    );
    await page.getByText(unsavedSource, { exact: true }).waitFor();
    await costResult()
      .getByText("Some entered amounts are unknown.", { exact: false })
      .waitFor();
    assert.equal(
      await costResult()
        .getByText(/lowest supplied.*total|Lowest supplied.*total/)
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
    await costResult()
      .getByText(
        "All entered amounts are known. This describes entered lines only; unrecorded cost categories remain unassessed. Totals are not verified quotes or a supplier recommendation.",
        { exact: true },
      )
      .waitFor();
    assert.equal(
      await coverageRow("Training")
        .getByRole("cell", { name: "Not recorded", exact: true })
        .count(),
      2,
    );
    assert.equal(
      await costResult()
        .getByText("Equal lowest supplied entered-line total (tie).", {
          exact: false,
        })
        .count(),
      2,
    );
    await shot("cost-desktop");
  });
  await test("Actual entered-line totals distinguish explicit category zero from omitted and unknown amounts", async () => {
    const writes = planWrites;
    await button("Add line to offer 1").click();
    await fillLine(1, 2, {
      description: "Synthetic training explicitly zero",
      category: "TRAINING",
      quantity: "1",
      amount: "0",
      cadence: "ONE_OFF",
    });
    const zero = await responseFor("cost-comparison", () =>
      button("Calculate supplied costs").click(),
    );
    assert.equal(zero.status, "COMPLETE");
    assert.deepEqual(
      zero.offers.map((offer) => offer.complete_total),
      ["60", "60"],
    );
    assert.equal(
      await coverageRow("Training")
        .getByRole("cell", { name: "Amounts recorded", exact: true })
        .count(),
      1,
    );
    assert.equal(
      await coverageRow("Training")
        .getByRole("cell", { name: "Not recorded", exact: true })
        .count(),
      1,
    );
    await select("Offer 1, line 2 category").selectOption("EXIT");
    await label("Offer 1, line 2 quantity").fill("0");
    await label("Offer 1, line 2 unit amount (USD)").fill("");
    const unknown = await responseFor("cost-comparison", () =>
      button("Calculate supplied costs").click(),
    );
    assert.equal(unknown.status, "INCOMPLETE");
    assert.equal(unknown.offers[0].known_subtotal, "60");
    assert.equal(unknown.offers[0].complete_total, null);
    assert.deepEqual(unknown.cheapest_offer_ids, []);
    assert.equal(
      await coverageRow("Exit")
        .getByRole("cell", { name: "Contains an unknown amount", exact: true })
        .count(),
      1,
    );
    await button("Remove offer 1, line 2").click();
    assert.equal(await costResult().count(), 0);
    assert.equal(planWrites, writes);
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
      "Draft for human review: Join our invented workshop. Registration: Not supplied.\nCafé टीम — invented facts only.",
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
      "Updated synthetic review note; confirm registration and access information.\nCafé समुदाय: use supplied facts only.",
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
  await test("Calculation binds exact opened inputs while a save receipt alone never claims a canonical read", async () => {
    await button("Procurement brief").click();
    await page.getByText(openedSource, { exact: true }).waitFor();
    const requestPromise = page.waitForRequest(
      (request) =>
        request.method() === "POST" &&
        new URL(request.url()).pathname.endsWith(
          "/ai-enablement/cost-comparison",
        ),
    );
    const beforeWrites = planWrites,
      beforeReads = planReads;
    const result = await responseFor("cost-comparison", () =>
      button("Calculate supplied costs").click(),
    );
    const sent = (await requestPromise).postDataJSON();
    assert.deepEqual(Object.keys(sent).sort(), [
      "currency",
      "offers",
      "period_months",
    ]);
    assert.deepEqual(sent, savedPlan.data.planning.cost_comparison);
    assert.equal(planWrites, beforeWrites);
    assert.equal(planReads, beforeReads);
    assert.deepEqual(
      result.offers.map((offer) => offer.complete_total),
      ["66", "60"],
    );
    const saved = await savedResponse(() =>
      button("Save plan changes").click(),
    );
    assert(saved.ok(), await saved.text());
    const receipt = await saved.json();
    assert.notEqual(receipt.revision_id, savedPlan.revision_id);
    await page.getByText(localSource, { exact: true }).waitFor();
    assert.equal(await costResult().count(), 0);
    assert.equal(planReads, beforeReads);
    const current = await getPlan();
    assert.equal(current.status, 200);
    assert.equal(current.body.revision_id, receipt.revision_id);
    assert.deepEqual(current.body.data.planning.cost_comparison, sent);
    await page.getByText(localSource, { exact: true }).waitFor();
    await openSavedPlan();
    await page.getByText(openedSource, { exact: true }).waitFor();
    assert.equal(await costResult().count(), 0);
    savedPlan = current.body;
  });
  await test("A delayed real result cannot cross a same-valued new saved revision", async () => {
    let release, received, finished;
    const ready = new Promise((resolve) => {
        received = resolve;
      }),
      held = new Promise((resolve) => {
        release = resolve;
      }),
      completed = new Promise((resolve) => {
        finished = resolve;
      });
    const match = (url) =>
      url.pathname.endsWith("/ai-enablement/cost-comparison");
    const handler = async (route) => {
      const response = await route.fetch();
      assert(response.ok(), await response.text());
      received();
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
    const saved = await savedResponse(() =>
      button("Save plan changes").click(),
    );
    assert(saved.ok(), await saved.text());
    const receipt = await saved.json();
    assert.notEqual(receipt.revision_id, savedPlan.revision_id);
    release();
    await completed;
    await page.unroute(match, handler);
    assert.equal(await costResult().count(), 0);
    await page.getByText(localSource, { exact: true }).waitFor();
    const current = (await getPlan()).body;
    assert.deepEqual(
      current.data.planning.cost_comparison,
      savedPlan.data.planning.cost_comparison,
    );
    await openSavedPlan();
    await page.getByText(openedSource, { exact: true }).waitFor();
    const result = await responseFor("cost-comparison", () =>
      button("Calculate supplied costs").click(),
    );
    assert.deepEqual(
      result.offers.map((offer) => offer.complete_total),
      ["66", "60"],
    );
    savedPlan = current;
  });
  await test("Saved guide compatibility names current editions and reading leaves the revision unchanged", async () => {
    await page
      .getByRole("heading", { name: "Saved guide compatibility", exact: true })
      .waitFor();
    await page
      .getByText(
        "Use the saved guidance view to read the text captured with a specific revision.",
        {
          exact: false,
        },
      )
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
      true,
    );
    const archived = await page.evaluate(
      async (route) => {
        const response = await fetch(route);
        return { status: response.status, body: await response.json() };
      },
      planRoute + "/revisions/" + current.body.revision_id + "/guidance",
    );
    assert.equal(archived.status, 200);
    assert.equal(archived.body.object_id, planId);
    assert.equal(archived.body.revision_id, current.body.revision_id);
    assert.equal(archived.body.status, "COMPLETE");
    for (const component of ["catalog", "solutions", "practice"]) {
      assert.equal(archived.body[component].status, "AVAILABLE");
      assert.equal(
        archived.body[component].content_version,
        current.body.data.content_versions[component],
      );
    }
    assert.deepEqual(
      archived.body.catalog.payload.provenance,
      catalogue.provenance,
    );
    assert.equal(
      archived.body.catalog.payload.provenance.validated_demand,
      false,
    );
    assert.deepEqual(
      archived.body.catalog.payload.learning_paths,
      catalogue.learning_paths,
    );
    assert.deepEqual(archived.body.practice.payload, templates);
    const bundle = {
      schema_version: archived.body.snapshot_schema_version,
      catalog: archived.body.catalog.payload,
      solutions: archived.body.solutions.payload,
      practice: archived.body.practice.payload,
    };
    assert.equal(
      createHash("sha256").update(canonical(bundle), "utf8").digest("hex"),
      archived.body.snapshot_sha256,
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
  await test("Foundations handoff and starter preview/cancel preserve saved practice and learning progress", async () => {
    guidedBefore = structuredClone((await getPlan()).body);
    const writes = planWrites,
      advisory = advisoryRequests;
    await button("Build team capacity").click();
    const progress = guidedBefore.data.learning_completed;
    for (const key of progress)
      assert(await label("Complete learning step " + key).isChecked());
    const guideResponse = page.waitForResponse((response) =>
      response.url().endsWith("/ai-enablement/task-templates"),
    );
    await button("Open a guided practice worksheet").click();
    templates = await (await guideResponse).json();
    await practiceField("Your manually written draft").waitFor();
    const old = guidedBefore.data.planning.task_practice;
    assert.equal(
      await practiceField("Your synthetic or public-text brief").inputValue(),
      old.brief,
    );
    assert.equal(
      await practiceField("Your manually written draft").inputValue(),
      old.draft,
    );
    assert.equal(
      await practiceField(
        "Human review notes and unresolved questions",
      ).inputValue(),
      old.review_notes,
    );
    await button("Preview the invented brief for this task").click();
    const preview = page.getByRole("group", {
      name: "Invented brief starter preview",
      exact: true,
    });
    await preview.waitFor();
    const template = templates.templates.find(
      (item) => item.id === old.template_id,
    );
    assert(template);
    await preview.getByText(template.example_brief, { exact: true }).waitFor();
    await button("Keep my worksheet unchanged").click();
    assert.equal(await preview.count(), 0);
    assert.equal(
      await practiceField("Your synthetic or public-text brief").inputValue(),
      old.brief,
    );
    assert.equal(
      await practiceField("Your manually written draft").inputValue(),
      old.draft,
    );
    assert.equal(
      await practiceField(
        "Human review notes and unresolved questions",
      ).inputValue(),
      old.review_notes,
    );
    for (const check of template.review_steps)
      assert.equal(
        await label(check.label).isChecked(),
        old.checked_steps.includes(check.id),
      );
    const after = (await getPlan()).body;
    assert.equal(after.revision_id, guidedBefore.revision_id);
    assert.deepEqual(after.data, guidedBefore.data);
    assert.equal(planWrites, writes);
    assert.equal(advisoryRequests, advisory);
  });
  await test("Starter confirmation expires after edits and explicit replacement preserves own draft and review bytes", async () => {
    const old = guidedBefore.data.planning.task_practice,
      template = templates.templates.find(
        (item) => item.id === old.template_id,
      ),
      writes = planWrites;
    await button("Preview the invented brief for this task").click();
    await practiceField("Your manually written draft").fill(
      old.draft + "\nLater local edit",
    );
    assert.equal(
      await page
        .getByRole("group", {
          name: "Invented brief starter preview",
          exact: true,
        })
        .count(),
      0,
    );
    assert.equal(
      await practiceField("Your manually written draft").inputValue(),
      old.draft + "\nLater local edit",
    );
    await practiceField("Your manually written draft").fill(old.draft);
    for (const check of template.review_steps) await label(check.label).check();
    await button("Preview the invented brief for this task").click();
    await button("Replace only my brief and reset self-checks").click();
    expectedGuidedPractice = {
      template_id: template.id,
      brief: template.example_brief,
      draft: old.draft,
      review_notes: old.review_notes,
      checked_steps: [],
    };
    assert.equal(
      await practiceField("Your synthetic or public-text brief").inputValue(),
      expectedGuidedPractice.brief,
    );
    assert.equal(
      await practiceField("Your manually written draft").inputValue(),
      old.draft,
    );
    assert.equal(
      await practiceField(
        "Human review notes and unresolved questions",
      ).inputValue(),
      old.review_notes,
    );
    for (const check of template.review_steps)
      assert.equal(await label(check.label).isChecked(), false);
    assert.equal(planWrites, writes);
    const canonical = (await getPlan()).body;
    assert.deepEqual(canonical.data.planning.task_practice, old);
    assert.deepEqual(
      canonical.data.learning_completed,
      guidedBefore.data.learning_completed,
    );
  });
  await test("Deliberate actual save/reopen retains starter text, original own work and unchanged recorded lessons", async () => {
    const saved = await savedResponse(() =>
      button("Save plan changes").click(),
    );
    assert(saved.ok(), await saved.text());
    const receipt = await saved.json();
    const current = (await getPlan()).body;
    assert.equal(current.revision_id, receipt.revision_id);
    assert.notEqual(current.revision_id, guidedBefore.revision_id);
    assert.deepEqual(
      current.data.planning.task_practice,
      expectedGuidedPractice,
    );
    assert.deepEqual(
      current.data.learning_completed,
      guidedBefore.data.learning_completed,
    );
    await openSavedPlan();
    await button("Practise a useful task").click();
    assert.equal(
      await practiceField("Your synthetic or public-text brief").inputValue(),
      expectedGuidedPractice.brief,
    );
    assert.equal(
      await practiceField("Your manually written draft").inputValue(),
      expectedGuidedPractice.draft,
    );
    assert.equal(
      await practiceField(
        "Human review notes and unresolved questions",
      ).inputValue(),
      expectedGuidedPractice.review_notes,
    );
    await page
      .getByText("Saved practice edition: Current", { exact: false })
      .waitFor();
    await page
      .getByText(
        "Using an example does not complete a lesson or a self-check",
        { exact: false },
      )
      .waitFor();
    assert.equal(advisoryRequests, 0);
    savedPlan = current;
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
      .getByText(
        "For a saved revision, choose View saved guidance to check whether its original wording was retained.",
        {
          exact: false,
        },
      )
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
  await test("Simulated stale practice edition is labelled without assuming historical archive availability", async () => {
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
      .getByText(
        "For a saved revision, choose View saved guidance to check whether its original wording was retained.",
        {
          exact: false,
        },
      )
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
    await button("Practise a useful task").click();
    await button("Preview the invented brief for this task").click();
    assert(
      await button("Use this invented brief in my worksheet").isDisabled(),
    );
    await page
      .getByText(
        "Wait for the pending saved-plan action before changing the brief.",
        { exact: true },
      )
      .waitFor();
    const retry = await savedResponse(() =>
      button("Retry previous save").click(),
    );
    assert(retry.ok(), await retry.text());
    assert.equal(sent.length, 2);
    assert.deepEqual(sent[0], sent[1]);
    assert.equal(
      await page
        .getByRole("group", {
          name: "Invented brief starter preview",
          exact: true,
        })
        .count(),
      0,
    );
    assert.equal(
      (await getPlan()).body.data.planning.task_practice,
      null,
      "Unblocking a save must not apply a queued starter",
    );
    await button("Procurement brief").click();
    await page.getByText(unsavedSource, { exact: true }).waitFor();
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
  await test("New product controls fit desktop, 390 and 320 px views with actual keyboard scrolling and all accessibility findings retained", async () => {
    for (const viewport of [
      { width: 1440, height: 1050 },
      { width: 390, height: 844 },
      { width: 320, height: 844 },
    ]) {
      await page.setViewportSize(viewport);
      for (const name of [
        "Procurement brief",
        "Pilot tracker",
        "Practise a useful task",
      ]) {
        await button(name).click();
        await assertFits();
        if (name === "Procurement brief") {
          if (!(await costResult().count()))
            await responseFor("cost-comparison", () =>
              button("Calculate supplied costs").click(),
            );
          await coverage().waitFor();
          await coverage().focus();
          assert(
            await coverage().evaluate(
              (element) => element === document.activeElement,
            ),
          );
          if (viewport.width <= 390) {
            const initialLayout = await coverageLayout("first");
            // Chromium can round fractional collapsed borders to a 1px range
            // while both offers already fit and native arrow keys cannot move.
            // Use the same 1px tolerance as the full cell/text visibility checks.
            const overflows = await coverage().evaluate(
              (element) => element.scrollWidth - element.clientWidth > 1,
            );
            if (viewport.width === 320) assert(overflows);
            if (overflows) {
              assert(initialLayout.documentHasFocus);
              assert.equal(initialLayout.visibilityState, "visible");
              await page.keyboard.press("ArrowRight");
              await page.waitForFunction(
                () =>
                  document.querySelector(".ai-cost-coverage").scrollLeft > 0,
              );
              await settleCoverageScroll();
              const movedRight = await coverage().evaluate(
                (element) => element.scrollLeft,
              );
              assert(movedRight > 0);
              assert(
                await coverageRow("Subscription")
                  .getByRole("rowheader")
                  .evaluate((element) => {
                    const cell = element.getBoundingClientRect(),
                      parent = element
                        .closest(".ai-cost-coverage")
                        .getBoundingClientRect();
                    return (
                      cell.left >= parent.left - 1 && cell.left < parent.right
                    );
                  }),
              );
              await page.keyboard.press("ArrowLeft");
              await page.waitForFunction(
                (right) =>
                  document.querySelector(".ai-cost-coverage").scrollLeft <
                  right,
                movedRight,
              );
              await settleCoverageScroll();
              assert.equal(
                await coverage().evaluate((element) => element.scrollLeft),
                0,
              );
              await coverage().evaluate((element) =>
                element.scrollTo({
                  left: element.scrollWidth,
                  behavior: "instant",
                }),
              );
              await settleCoverageScroll();
              const finalLayout = await coverageLayout("last");
              assert.equal(finalLayout.title.left, initialLayout.title.left);
              assert.equal(finalLayout.title.right, initialLayout.title.right);
              await scan(
                `Procurement brief: ${viewport.width}px scrolled to last offer`,
              );
            } else {
              const finalLayout = await coverageLayout("last");
              assert.equal(finalLayout.title.left, initialLayout.title.left);
              assert.equal(finalLayout.title.right, initialLayout.title.right);
            }
            await coverage().evaluate((element) =>
              element.scrollTo({ left: 0, behavior: "instant" }),
            );
            await settleCoverageScroll();
            assert.equal(
              await coverage().evaluate((element) => element.scrollLeft),
              0,
            );
            await coverageLayout("first");
          }
        }
        await scan(`${name}: ${viewport.width}px`);
        if (viewport.width === 390)
          await shot(
            name === "Procurement brief"
              ? "cost-mobile"
              : name === "Pilot tracker"
                ? "pilot-mobile"
                : "practice-mobile",
          );
        if (viewport.width === 320 && name === "Procurement brief")
          await shot("cost-320");
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
    await observe(page);
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
    await button("Preview the invented brief for this task").click();
    await page
      .getByRole("group", {
        name: "Invented brief starter preview",
        exact: true,
      })
      .waitFor();
    assert.equal(
      await button("Use this invented brief in my worksheet").count(),
      0,
    );
    assert.equal(
      await button("Replace only my brief and reset self-checks").count(),
      0,
    );
    await page
      .getByText(
        "You can study this example. Plan management permission is needed to change the shared worksheet.",
        { exact: true },
      )
      .waitFor();
    await button("Keep my worksheet unchanged").click();
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
  await test("Actual read-only management refusal creates no plan and leaves preserved canonical work unchanged", async () => {
    const authorHeaders = {
      Authorization: "Bearer " + process.env[fixture.actors.author.token_env],
    };
    const beforeResponse = await fetch(base + planRoute, {
      headers: authorHeaders,
    });
    assert.equal(beforeResponse.status, 200);
    const beforePlan = await beforeResponse.json();
    const beforeWrites = planWrites;
    const answer = await page.evaluate(async (data) => {
      const me = await (await fetch("/auth/me")).json(),
        tenant = me.tenants[0].tenant_id;
      const route = `/v1/tenants/${tenant}/ai-enablement/plans`;
      const before = await fetch(route + "?limit=50");
      const publicData = structuredClone(data);
      delete publicData.content_versions;
      const denied = await fetch(route, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": me.csrf_token,
        },
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          data: publicData,
        }),
      });
      const after = await fetch(route + "?limit=50");
      return {
        path: route,
        status: denied.status,
        error: await denied.json(),
        beforeStatus: before.status,
        afterStatus: after.status,
        before: await before.json(),
        after: await after.json(),
      };
    }, beforePlan.data);
    deliberateRefusals.push({
      path: answer.path,
      status: 404,
      scope:
        "Deliberate current read-only actor create refusal; no management grant or profile widening",
    });
    assert.equal(answer.status, 404);
    assert.equal(answer.error.code, "RESOURCE_UNAVAILABLE");
    assert.equal(answer.beforeStatus, 200);
    assert.equal(answer.afterStatus, 200);
    assert.deepEqual(answer.after, answer.before);
    assert.equal(
      planWrites,
      beforeWrites + 1,
      "Exactly one deliberate refusal request; no automatic starter save",
    );
    const afterResponse = await fetch(base + planRoute, {
      headers: authorHeaders,
    });
    assert.equal(afterResponse.status, 200);
    assert.deepEqual(await afterResponse.json(), beforePlan);
  });
  await test("No advisory/provider request or uncaught browser error occurs across these synthetic workflows", async () => {
    assert.equal(advisoryRequests, 0);
    assert.deepEqual(externalRequests, []);
    assert.deepEqual(errors, []);
    const unexpected = consoleErrors.filter(
      (record) => !expectedConsoleNetworkEvent(record),
    );
    assert.deepEqual(unexpected, [], "Unexpected browser console errors");
    currentSources = await sourceHashes();
    currentAssets = await servedHashes();
    assert.deepEqual(currentSources, qualifiedSources);
    assert.deepEqual(currentAssets, qualifiedAssets);
  });
} catch (error) {
  results.push({
    name: "AI planning browser run",
    status: "failed",
    message: error.message,
  });
  await page.screenshot({
    path: path.join(captureDirectory, "ai-planning-browser-failure.png"),
    fullPage: true,
  });
  console.error(error.stack);
  process.exitCode = 1;
} finally {
  currentSources ??= await sourceHashes().catch(() => null);
  currentAssets ??= await servedHashes().catch(() => null);
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
          "Disposable local database through the real FastAPI service; engine and applied ledger are captured by the owning runner qualification",
        fixture: "Synthetic fixture only",
        results,
        uncaughtErrors: errors,
        consoleErrors,
        accessibilityScans,
        coverageLayouts,
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
        planReads,
        blocked_external_requests: externalRequests,
        deliberate_current_authority_refusals: deliberateRefusals,
        runtime_manifest: runtime,
        qualified_sources: qualifiedSources,
        current_sources: currentSources,
        sources_unchanged:
          !!currentSources &&
          JSON.stringify(qualifiedSources) === JSON.stringify(currentSources),
        qualified_served_assets: qualifiedAssets,
        current_served_assets: currentAssets,
        served_assets_unchanged:
          !!currentAssets &&
          JSON.stringify(qualifiedAssets) === JSON.stringify(currentAssets),
        implementation_scope:
          "Actual local existing HTTP/login/grant browser workflow; category coverage uses exact entered inputs, arithmetic unchanged; guided starters remain deliberate local manual work with normal save.",
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
