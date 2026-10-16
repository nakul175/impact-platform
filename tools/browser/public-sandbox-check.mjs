import { chromium } from "playwright-core";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { createHash } from "node:crypto";
const origin = process.env.IMPACT_BASE_URL;
if (
  !origin ||
  !/^http:\/\/127\.0\.0\.1:[0-9]+$/.test(origin) ||
  process.env.IMPACT_ENVIRONMENT !== "test" ||
  process.env.IMPACT_ALLOW_FIXTURE_LOAD !== "1"
)
  throw Error("Use the disposable public-sandbox-browser runner.");
const evidence =
  process.env.IMPACT_BROWSER_EVIDENCE_FILE ||
  "docs/evidence/public-sandbox-browser.json";
const capture = evidence.replace(/\.json$/, "-captures");
await fs.mkdir(capture, { recursive: true });
const sources = [
  "apps/web/src/PublicSandbox.tsx",
  "apps/web/src/PublicSandboxModel.ts",
  "apps/web/src/public-sandbox.css",
  "apps/web/sandbox.html",
  "apps/api/impact_api/main.py",
];
const hashes = async () =>
  Object.fromEntries(
    await Promise.all(
      sources.map(async (p) => [
        p,
        createHash("sha256")
          .update(await fs.readFile(p))
          .digest("hex"),
      ]),
    ),
  );
const before = await hashes(),
  requests = [],
  errors = [],
  checks = [];
const browser = await chromium.launch({
  executablePath:
    process.env.IMPACT_BROWSER_EXECUTABLE ||
    (process.platform === "darwin"
      ? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
      : path.join(process.cwd(), ".local/browser/chromium")),
  env: Object.fromEntries(
    Object.entries(process.env).filter(
      ([key]) => !key.startsWith("IMPACT_") && !key.startsWith("PG"),
    ),
  ),
  headless: true,
  args: ["--no-sandbox"],
});
try {
  const context = await browser.newContext();
  const page = await context.newPage();
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("request", (r) =>
    requests.push({
      url: r.url(),
      method: r.method(),
      resource: r.resourceType(),
    }),
  );
  const response = await page.goto(origin + "/sandbox.html");
  assert.equal(response.status(), 200);
  assert.match(
    response.headers()["content-security-policy"],
    /connect-src 'none'/,
  );
  assert.match(
    response.headers()["content-security-policy"],
    /form-action 'none'/,
  );
  assert.equal(response.headers()["set-cookie"], undefined);
  await page.getByRole("heading", { name: "Portfolio", exact: true }).waitFor();
  const names = await page
    .getByRole("navigation", { name: "Demo sections" })
    .getByRole("button")
    .allTextContents();
  assert.equal(names.length, 20);
  for (const name of names) {
    await page
      .getByRole("navigation", { name: "Demo sections" })
      .getByRole("button", { name, exact: true })
      .click();
    await page.getByRole("heading", { name, exact: true }).waitFor();
  }
  checks.push("All 20 sections render without sign-in");
  await page.getByRole("button", { name: "Portfolio", exact: true }).click();
  await page
    .getByRole("button", { name: "New programme", exact: true })
    .click();
  await page
    .getByLabel("Title", { exact: true })
    .fill("Synthetic demo programme");
  await page
    .getByLabel("Notes", { exact: true })
    .fill("<script>window.shouldNeverRun=true</script>");
  await page.getByRole("button", { name: "Save local draft" }).click();
  const row = page.getByRole("article").filter({
    has: page.getByRole("heading", {
      name: "Synthetic demo programme",
      exact: true,
    }),
  });
  await row.waitFor();
  assert.equal(await row.locator("script").count(), 0);
  await row.getByRole("button", { name: "Simulate submission" }).click();
  await row
    .getByRole("button", { name: "Simulate review", exact: true })
    .click();
  await row.getByText("Reviewed (simulation)", { exact: true }).waitFor();
  await row.getByRole("button", { name: "Edit draft" }).click();
  await page
    .getByLabel("Notes", { exact: true })
    .fill("Revised invented notes");
  await page.getByRole("button", { name: "Save local draft" }).click();
  await row.getByText("Draft", { exact: true }).waitFor();
  checks.push(
    "Create, edit, simulated review and invalidation run locally; text is escaped",
  );
  await page.getByLabel("Search this section").fill("no-match-at-all");
  await page.getByText("No matching samples.", { exact: false }).waitFor();
  await page.getByLabel("Search this section").fill("");
  await page.getByRole("button", { name: "Reset demo", exact: true }).click();
  await page.getByRole("button", { name: "Keep my changes" }).click();
  await row.waitFor();
  await page.getByRole("button", { name: "Reset demo", exact: true }).click();
  await page.getByRole("button", { name: "Discard changes and reset" }).click();
  assert.equal(
    await page
      .getByRole("heading", { name: "Synthetic demo programme", exact: true })
      .count(),
    0,
  );
  checks.push("Search, reset confirmation and discard behave correctly");
  await page
    .getByRole("button", { name: "New programme", exact: true })
    .click();
  await page.getByLabel("Title", { exact: true }).fill("Private to this tab");
  await page.getByRole("button", { name: "Save local draft" }).click();
  const second = await context.newPage();
  await second.goto(origin + "/sandbox.html");
  await second
    .getByRole("heading", { name: "Portfolio", exact: true })
    .waitFor();
  assert.equal(
    await second
      .getByRole("heading", { name: "Private to this tab", exact: true })
      .count(),
    0,
  );
  await page.reload();
  await page.getByRole("heading", { name: "Portfolio", exact: true }).waitFor();
  assert.equal(
    await page
      .getByRole("heading", { name: "Private to this tab", exact: true })
      .count(),
    0,
  );
  assert.deepEqual(await context.cookies(), []);
  assert.equal(
    await page.evaluate(() => localStorage.length + sessionStorage.length),
    0,
  );
  assert(
    requests.every(
      (r) =>
        r.method === "GET" &&
        (new URL(r.url).pathname === "/sandbox.html" ||
          new URL(r.url).pathname.startsWith("/assets/")),
    ),
  );
  checks.push(
    "Fresh tabs and reload reset data; no cookies, storage or API requests",
  );
  const landing = await context.newPage();
  await landing.goto(origin + "/");
  await landing
    .getByRole("link", { name: "Explore demo without login →" })
    .waitFor();
  assert.equal(
    await landing
      .getByRole("link", { name: "Explore demo without login →" })
      .getAttribute("href"),
    "/sandbox.html",
  );
  checks.push("Shared landing page offers an explicit no-login demo entry");
  const auth = await context.request.get(origin + "/auth/me");
  assert.equal(auth.status(), 401);
  const platform = await context.request.get(origin + "/v1/platform/tenants");
  assert.equal(platform.status(), 401);
  checks.push("Shared account and platform APIs remain authenticated");
  await page.setViewportSize({ width: 390, height: 844 });
  assert(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  );
  await page.screenshot({
    path: path.join(capture, "mobile.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.screenshot({
    path: path.join(capture, "desktop.png"),
    fullPage: true,
  });
  checks.push(
    "Mobile and desktop views captured; no mobile horizontal overflow",
  );
  assert.deepEqual(errors, []);
} finally {
  await browser.close();
  const after = await hashes();
  await fs.writeFile(
    evidence,
    JSON.stringify(
      {
        checks,
        passed: checks.length === 7 && errors.length === 0,
        expected_checks: 7,
        page_errors: errors,
        requests,
        source_before: before,
        source_after: after,
        sources_unchanged: JSON.stringify(before) === JSON.stringify(after),
        scope:
          "Anonymous browser-only fictional simulation, not domain API acceptance; intentional separate anonymous API refusal checks",
      },
      null,
      2,
    ) + "\n",
  );
  assert.deepEqual(after, before);
}
assert.equal(checks.length, 7);
console.log("PASS public sandbox: " + checks.join("; "));
