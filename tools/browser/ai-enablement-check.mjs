import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
const root = process.cwd();
const local = process.env.IMPACT_TEST_LOCAL;
const base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py ai-enablement-browser");
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
page.setDefaultTimeout(15000);
const results = [],
  errors = [];
let advisoryRequests = 0;
page.on("request", (request) => {
  if (
    request.method() === "POST" &&
    request.url().endsWith("/ai-enablement/advisory")
  )
    advisoryRequests += 1;
});
page.on("pageerror", (e) => errors.push(e.message));
const button = (name) => page.getByRole("button", { name, exact: true });
const label = (name) => page.getByLabel(name, { exact: true });
async function test(name, fn) {
  await fn();
  results.push({ name, status: "passed" });
  console.log("PASS " + name);
}
try {
  await page.goto(base);
  await label("Username").fill("author");
  await label("Password").fill(passwords.author);
  await button("Sign in →").click();
  await button("AI enablement").waitFor();
  await test("Open the nonprofit AI guide with honest marketplace limits", async () => {
    await button("AI enablement").click();
    await page
      .getByRole("heading", {
        name: "AI enablement for nonprofits",
        exact: true,
      })
      .waitFor();
    await page
      .getByRole("heading", { name: "Your adoption journey", exact: true })
      .waitFor();
    await page
      .getByRole("heading", { name: "Explore potential pilots", exact: true })
      .waitFor();
    await page
      .getByText(
        "Supplier registration and transactions are not yet available.",
        { exact: false },
      )
      .waitFor();
    await page
      .getByText("These are editorial starting points", { exact: false })
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
    const payload = await received.json();
    assert.equal(payload.assessment.method, "DETERMINISTIC_RULES");
    await page
      .getByRole("heading", { name: /^Readiness assessment/ })
      .waitFor();
    await page
      .getByRole("heading", { name: "Next steps", exact: true })
      .waitFor();
    await label("AI goal").fill("Prepare a synthetic staff training pilot.");
    assert.equal(
      await page
        .getByRole("heading", { name: /^Readiness assessment/ })
        .count(),
      0,
    );
  });
  await test("Learning and fair procurement guidance remain available with AI generation disabled", async () => {
    await page
      .getByRole("heading", { name: "Build team capacity", exact: true })
      .waitFor();
    await page
      .getByRole("heading", { name: "Procurement and comparison", exact: true })
      .waitFor();
    await page
      .getByText("Use the same questions for every supplier.", { exact: false })
      .waitFor();
    await page
      .getByText("AI advisory is not configured for this workspace.", {
        exact: false,
      })
      .waitFor();
    assert(await button("Request AI advisory draft").isDisabled());
    assert.equal(
      advisoryRequests,
      0,
      "Disabled advisory must make no provider requests",
    );
    assert.equal(
      await label("I consent to sending this brief to OpenAI").count(),
      0,
    );
    assert.equal(
      await page
        .getByRole("heading", { name: "AI advisory draft", exact: true })
        .count(),
      0,
    );
  });
  await test("The AI workspace remains within a 390 px mobile width", async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page
      .getByRole("heading", { name: "Build team capacity", exact: true })
      .scrollIntoViewIfNeeded();
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
      "AI workspace overflows at 390 px",
    );
    await page.screenshot({
      path: path.join(root, "docs/evidence/ai-enablement-mobile.png"),
      fullPage: true,
    });
    assert.deepEqual(errors, []);
  });
} catch (e) {
  results.push({
    name: "AI enablement browser run",
    status: "failed",
    message: e.message,
  });
  await page.screenshot({
    path: path.join(root, "docs/evidence/ai-enablement-browser-failure.png"),
    fullPage: true,
  });
  console.error(e.message);
  process.exitCode = 1;
} finally {
  await fs.writeFile(
    path.join(root, "docs/evidence/ai-enablement-browser-tests.json"),
    JSON.stringify(
      { engine: "Chromium 153", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
  await browser.close();
}
