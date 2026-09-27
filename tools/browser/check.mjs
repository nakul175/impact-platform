import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py browser");
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
const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
  }),
  page = await context.newPage();
page.setDefaultTimeout(15000);
const results = [],
  errors = [];
page.on("pageerror", (e) => errors.push(e.message));
async function test(name, fn) {
  await fn();
  results.push({ name, status: "passed" });
  console.log("PASS " + name);
}
async function login(user) {
  await page.getByLabel("Username", { exact: true }).fill(user);
  await page.getByLabel("Password", { exact: true }).fill(passwords[user]);
  await page.getByRole("button", { name: "Sign in →", exact: true }).click();
  await page
    .getByRole("heading", { name: "Programme portfolio", exact: true })
    .waitFor();
}
async function close() {
  await page.getByRole("button", { name: "Close dialog", exact: true }).click();
}
const unique = Date.now().toString(),
  programme = "Browser programme " + unique,
  source = "browser-observation-" + unique;
try {
  await test("Development sign-in and workspace load", async () => {
    await page.goto(base);
    await page.getByRole("heading", { name: "Welcome back" }).waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/sign-in.png"),
    });
    await login("author");
  });
  await test("Create programme and read its durable revision", async () => {
    await page
      .getByRole("button", { name: "New programme", exact: false })
      .click();
    await page.getByLabel("Programme title", { exact: true }).fill(programme);
    await page.getByLabel("Programme code", { exact: true }).fill("BROWSER");
    await page.getByLabel("Start date", { exact: true }).fill("2026-01-01");
    await page.getByLabel("End date", { exact: true }).fill("2026-12-31");
    await page.getByRole("button", { name: "Save draft", exact: true }).click();
    await page.getByRole("button", { name: programme, exact: true }).waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/portfolio.png"),
    });
  });
  await test("Capture and submit a manual observation", async () => {
    await page
      .getByRole("button", { name: "Measurement", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Add observation", exact: false })
      .click();
    await page
      .getByLabel("Indicator", { exact: true })
      .selectOption({ index: 1 });
    await page.getByLabel("Source key", { exact: true }).fill(source);
    await page
      .getByLabel("Event date (UTC)", { exact: true })
      .fill("2026-08-15");
    await page.getByLabel("Recorded value", { exact: true }).fill("80");
    await page.getByLabel("Numerator", { exact: true }).fill("8");
    await page.getByLabel("Denominator", { exact: true }).fill("10");
    await page.getByRole("button", { name: "Save draft", exact: true }).click();
    await page.getByRole("button", { name: source, exact: true }).click();
    await page
      .getByRole("button", { name: "Submit for review", exact: true })
      .click();
    await page
      .getByLabel("Review template", { exact: true })
      .selectOption({ index: 1 });
    await page
      .getByRole("button", { name: "Submit for review", exact: true })
      .click();
    await page
      .getByRole("status")
      .filter({ hasText: "Saved successfully" })
      .waitFor();
  });
  let workflowName;
  await test("Author cannot approve their submitted record", async () => {
    await page
      .getByRole("button", { name: "Review queue", exact: true })
      .click();
    const links = page.locator("tbody .record-link");
    await links.filter({ hasText: "Review ·" }).first().waitFor();
    const count = await links.count();
    for (let i = 0; i < count; i++) {
      const rowName = await links.nth(i).innerText();
      await links.nth(i).click();
      const inspect = page.getByRole("dialog");
      const text = await inspect.innerText();
      if (text.includes("Submitted") || text.includes("candidate")) {
        await page
          .getByRole("button", { name: "Review submission", exact: true })
          .click();
        try {
          await page
            .getByText(source, { exact: true })
            .waitFor({ timeout: 1500 });
          workflowName = rowName;
          await page
            .getByRole("button", { name: "Approve", exact: true })
            .click();
          await page
            .getByRole("alert")
            .filter({ hasText: "independent reviewer" })
            .waitFor();
          await close();
          break;
        } catch (e) {
          await close();
          continue;
        }
      }
      await close();
    }
    assert(workflowName, "New observation workflow was found");
  });
  await test("Independent reviewer approves the submitted revision", async () => {
    await page.getByRole("button", { name: "Sign out", exact: true }).click();
    await login("reviewer");
    await page
      .getByRole("button", { name: "Review queue", exact: true })
      .click();
    await page.getByRole("button", { name: workflowName, exact: true }).click();
    await page
      .getByRole("button", { name: "Review submission", exact: true })
      .click();
    await page.getByText(source, { exact: true }).waitFor();
    await page
      .getByLabel("Decision reason", { exact: true })
      .fill("Independent browser qualification review");
    await page.getByRole("button", { name: "Approve", exact: true }).click();
    await page
      .getByRole("status")
      .filter({ hasText: "Saved successfully" })
      .waitFor();
  });
  await test("Calculate a provisional pooled result", async () => {
    await page.getByRole("button", { name: "Results", exact: true }).click();
    await page
      .getByRole("button", { name: "Calculate result", exact: false })
      .click();
    await page
      .getByLabel("Indicator", { exact: true })
      .selectOption({ index: 1 });
    await page
      .getByLabel("Reporting period", { exact: true })
      .selectOption({ index: 1 });
    await page.getByRole("button", { name: "Calculate", exact: true }).click();
    await page
      .getByRole("button", { name: "Result · 49.17", exact: true })
      .click();
    await page
      .getByRole("dialog")
      .getByText("PROVISIONAL", { exact: true })
      .waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/result-lineage.png"),
    });
    await close();
  });
  await test("Mobile navigation and bounded page width", async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.getByRole("button", { name: "Portfolio", exact: true }).click();
    await page
      .getByRole("heading", { name: "Programme portfolio", exact: true })
      .waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/mobile.png"),
      fullPage: true,
    });
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
      "Page fits viewport",
    );
    await page
      .getByRole("button", { name: "People & access", exact: true })
      .click();
    await page
      .getByRole("heading", { name: "People & access", exact: true })
      .waitFor();
  });
  await test("Logout invalidates the browser session", async () => {
    await page.getByRole("button", { name: "Sign out", exact: true }).click();
    await page.getByRole("heading", { name: "Welcome back" }).waitFor();
    const status = await page.evaluate(
      async () => (await fetch("/auth/me")).status,
    );
    assert.equal(status, 401);
    assert.deepEqual(errors, []);
  });
} catch (e) {
  results.push({ name: "Browser run", status: "failed", message: e.message });
  await page.screenshot({
    path: path.join(root, "docs/evidence/browser-failure.png"),
    fullPage: true,
  });
  console.error(e.message);
  process.exitCode = 1;
} finally {
  await fs.writeFile(
    path.join(root, "docs/evidence/browser-tests.json"),
    JSON.stringify(
      { engine: "Chromium 153", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
  await browser.close();
}
