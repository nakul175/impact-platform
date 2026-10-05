import { chromium } from "../browser/node_modules/playwright-core/index.mjs";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";

const root = process.cwd();
const base = process.env.IMPACT_TRACKER_URL || "http://127.0.0.1:8170";
const output = path.join(root, "docs/development-tracker");
const browser = await chromium.launch({
  executablePath:
    process.env.IMPACT_BROWSER_EXECUTABLE ||
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
});
const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
page.setDefaultTimeout(12000);
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const results = [];
const scans = [];
const startedAt = new Date().toISOString();
const axeSource = await fs.readFile(
  path.join(root, "tools/browser/node_modules/axe-core/axe.min.js"),
  "utf8",
);
async function check(
  name,
  body,
  scope = "Real loopback dashboard reading actual source files",
) {
  try {
    await body();
    results.push({ name, status: "PASS", scope });
  } catch (error) {
    results.push({ name, status: "FAIL", scope, error: String(error.message) });
    throw error;
  }
}
async function axe(name) {
  await page.evaluate(axeSource);
  const result = await page.evaluate(async () =>
    window.axe.run(document, {
      runOnly: {
        type: "tag",
        values: ["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"],
      },
    }),
  );
  scans.push({
    name,
    violations: result.violations,
    incomplete: result.incomplete,
  });
  assert.equal(
    result.violations.length,
    0,
    `${name}: accessibility violations`,
  );
}
let source;
let override = null;
let failing = false;
let requests = 0;
try {
  await check("Actual status endpoint and security headers", async () => {
    const response = await page.request.get(`${base}/api/status`);
    assert.equal(response.status(), 200);
    source = await response.json();
    assert.equal(source.sprint.active_agent_limit, 4);
    assert.equal(source.sprint.deadline, "2026-10-05T16:27:26Z");
    assert.equal(source.backlog.baseline.impact_requirements, 307);
    assert.equal(source.backlog.baseline.ai_requirements, 40);
    assert.equal(response.headers()["cache-control"], "no-store");
    assert.ok(
      response
        .headers()
        ["content-security-policy"].includes("frame-ancestors 'none'"),
    );
    const refusedHost = await page.request.get(`${base}/api/status`, {
      headers: { Host: "rebound.example.test:8170" },
    });
    assert.equal(refusedHost.status(), 421);
    assert.equal(await refusedHost.text(), "Unrecognised local host");
    assert.equal(
      (await page.request.get(`${base}/../../.local/synthetic.json`)).status(),
      404,
    );
    assert.equal(
      (await page.request.post(`${base}/api/status`, { data: {} })).status(),
      501,
    );
  });
  await check(
    "Desktop reads actual bounded counts and workstreams",
    async () => {
      await page.goto(base);
      await page
        .getByRole("heading", { name: "One platform. Visible progress." })
        .waitFor();
      await page.locator(".stream").first().waitFor();
      assert.equal(
        await page.locator(".stream").count(),
        source.streams.length,
      );
      await page
        .getByText(
          "14 consolidated scope domains · no overall completion percentage",
          { exact: true },
        )
        .waitFor();
      await page.screenshot({
        path: path.join(output, "tracker-desktop.png"),
        fullPage: true,
      });
    },
  );
  await check("Deadline countdown only measures time", async () => {
    const old = await page.locator("#countdown").textContent();
    const integrated = await page.locator("#integrated").textContent();
    await page.waitForTimeout(1200);
    assert.notEqual(await page.locator("#countdown").textContent(), old);
    assert.equal(await page.locator("#integrated").textContent(), integrated);
  });
  await check("Desktop accessibility scan", async () => {
    await axe("Actual desktop dashboard");
  });
  await check("Expanded scope stays open across live polls", async () => {
    const details = page.locator(".scope-panel details");
    await details.locator("summary").click();
    await page.waitForTimeout(5300);
    assert.equal(await details.getAttribute("open"), "");
    assert.equal(await page.locator(".domain").count(), 14);
  });
  await check("Mobile reflow at 390 and 320 pixels", async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    assert.ok(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
    await page.screenshot({
      path: path.join(output, "tracker-mobile.png"),
      fullPage: false,
    });
    await page
      .getByRole("heading", { name: "What is happening now" })
      .scrollIntoViewIfNeeded();
    await page.screenshot({
      path: path.join(output, "tracker-mobile-workstreams.png"),
      fullPage: false,
    });
    await page.evaluate(() => scrollTo(0, 0));
    await axe("Actual mobile dashboard");
    await page.setViewportSize({ width: 320, height: 740 });
    assert.ok(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
  });
  await check("Keyboard skip link and visible control focus", async () => {
    await page.reload();
    await page.keyboard.press("Tab");
    assert.equal(
      await page.evaluate(() => document.activeElement.textContent),
      "Skip to development progress",
    );
    await page.keyboard.press("Enter");
    await page.getByRole("button", { name: "Refresh now" }).focus();
    const style = await page
      .getByRole("button", { name: "Refresh now" })
      .evaluate((element) => getComputedStyle(element).outlineStyle);
    assert.notEqual(style, "none");
  });
  await page.setViewportSize({ width: 1440, height: 1050 });
  await page.route("**/api/status?*", async (route) => {
    requests++;
    if (failing)
      await route.fulfill({
        status: 503,
        contentType: "application/json",
        body: '{"error":"Synthetic unavailable source"}',
      });
    else if (override)
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(override),
      });
    else await route.continue();
  });
  const simulated =
    "Dashboard behavior with explicitly synthetic intercepted source snapshots; actual HTTP source reload is separately qualified";
  await check(
    "Live polling consumes a changed source snapshot",
    async () => {
      override = structuredClone(source);
      override.streams[0].summary =
        "Synthetic changed source record for live polling qualification";
      await page
        .getByText(override.streams[0].summary, { exact: true })
        .waitFor();
    },
    simulated,
  );
  await check(
    "Unestimated integration remains explicit",
    async () => {
      override.streams[0].status = "REVIEWING";
      override.streams[0].eta = {
        earliest: null,
        latest: null,
        confidence: "UNESTIMATED",
        basis: "Synthetic unknown scope",
      };
      await page.getByRole("button", { name: "Refresh now" }).click();
      await page
        .getByText("ETA not yet estimated", { exact: true })
        .first()
        .waitFor();
    },
    simulated,
  );
  await check(
    "Stale source and expired forecast stay visible",
    async () => {
      override.streams[0].status = "TESTING";
      override.streams[0].updated_at = "2000-01-01T00:00:00Z";
      override.streams[0].eta = {
        earliest: "2000-01-01T00:00:00Z",
        latest: "2000-01-01T00:10:00Z",
        confidence: "LOW",
        basis: "Synthetic expired range",
      };
      await page.getByRole("button", { name: "Refresh now" }).click();
      await page
        .getByText("No source update in 15 minutes. This state may be stale.", {
          exact: true,
        })
        .first()
        .waitFor();
      await page
        .getByText(
          "The forecast window has passed. A revised estimate is needed.",
          { exact: true },
        )
        .first()
        .waitFor();
      assert.equal(override.streams[0].status, "TESTING");
    },
    simulated,
  );
  await check(
    "Unavailable source retains last known state with warning",
    async () => {
      const before = await page.locator("#integrated").textContent();
      failing = true;
      await page.getByRole("button", { name: "Refresh now" }).click();
      await page
        .getByText(
          "Live update unavailable. Showing the last successfully read snapshot; its source timestamps remain visible.",
          { exact: true },
        )
        .waitFor();
      assert.equal(await page.locator("#integrated").textContent(), before);
      failing = false;
    },
    simulated,
  );
  await check(
    "Plain source text never becomes executable markup",
    async () => {
      override.streams[0].summary =
        '<img src="invalid" onerror="window.syntheticXss=true"> Synthetic inert markup';
      await page.getByRole("button", { name: "Refresh now" }).click();
      await page
        .getByText(override.streams[0].summary, { exact: true })
        .waitFor();
      assert.equal(await page.locator(".stream img").count(), 0);
      assert.equal(await page.evaluate(() => window.syntheticXss), undefined);
    },
    simulated,
  );
  await check(
    "Focused details survive a changed live snapshot",
    async () => {
      const summary = page
        .locator(".stream")
        .first()
        .locator("details summary")
        .first();
      await summary.focus();
      const identity = await summary.evaluate((element) => {
        element.dataset.syntheticIdentity = "preserve";
        return element.dataset.syntheticIdentity;
      });
      assert.equal(identity, "preserve");
      override.streams[0].summary = "Synthetic focus-preservation update";
      await page.waitForTimeout(5300);
      assert.equal(
        await page.evaluate(
          () => document.activeElement.dataset.syntheticIdentity,
        ),
        "preserve",
      );
      await page.locator("#filter").focus();
    },
    simulated,
  );
  await check(
    "Pause stops automatic polling and explicit refresh remains available",
    async () => {
      await page.getByRole("button", { name: "Pause updates" }).click();
      await page.waitForTimeout(300);
      const count = requests;
      await page.waitForTimeout(5300);
      assert.equal(requests, count);
      await page.getByRole("button", { name: "Refresh now" }).click();
      await page.waitForTimeout(400);
      assert.equal(requests, count + 1);
      await page.getByRole("button", { name: "Resume updates" }).click();
    },
    simulated,
  );
  await check(
    "Filters expose blocked reasons without changing rollup",
    async () => {
      override.streams[0].status = "BLOCKED";
      override.streams[0].blockers = [
        "Synthetic dependency is awaiting review",
      ];
      await page.getByRole("button", { name: "Refresh now" }).click();
      await page.getByLabel("Show").selectOption("BLOCKED");
      await page
        .getByText("Synthetic dependency is awaiting review", { exact: true })
        .waitFor();
      assert.equal(await page.locator(".stream").count(), 1);
      await page.getByLabel("Show").selectOption("all");
    },
    simulated,
  );
  override = null;
  await page.unroute("**/api/status?*");
  await page.reload();
  await page.locator(".stream").first().waitFor();
  assert.equal(errors.length, 0);
} finally {
  await fs.writeFile(
    path.join(output, "browser-evidence.json"),
    JSON.stringify(
      {
        started_at: startedAt,
        finished_at: new Date().toISOString(),
        browser: await browser.version(),
        platform: process.platform,
        dashboard: base,
        passed: results.filter((r) => r.status === "PASS").length,
        failed: results.filter((r) => r.status === "FAIL").length,
        uncaught_javascript_errors: errors,
        results,
        accessibility_scans: scans,
        qualification_limits: [
          "Tracker-only supporting tool, not product qualification or acceptance.",
          "Synthetic intercepted snapshots explicitly identify failure, stale-source, polling and keyboard-state simulations.",
          "Axe findings are recorded; zero automated violations is not complete accessibility conformance.",
        ],
      },
      null,
      2,
    ) + "\n",
  );
  await browser.close();
}
console.log(
  JSON.stringify({
    passed: results.length,
    failed: 0,
    axe_scans: scans.length,
    uncaught_javascript_errors: errors.length,
  }),
);
