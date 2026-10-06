import { chromium } from "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/tools/browser/node_modules/playwright-core/index.mjs";
import fs from "node:fs";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
const dir = "/private/tmp/tola-ai-profile-preservation-draft",
  repo =
    "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform",
  out = dir + "/baseline-attempt-01";
fs.mkdirSync(out);
const names = [
  ...fs
    .readdirSync(repo + "/apps/web/src")
    .filter((name) => /\.(tsx?|css|json)$/.test(name))
    .map((name) => repo + "/apps/web/src/" + name),
  ...[
    "baseline/AIAdoptionWorkspace.tsx",
    "baseline/fixture.tsx",
    "baseline/index.html",
    "server.mjs",
    "baseline-check.mjs",
  ].map((name) => dir + "/" + name),
];
const hashes = () =>
  Object.fromEntries(
    names.map((name) => [
      name,
      createHash("sha256").update(fs.readFileSync(name)).digest("hex"),
    ]),
  );
const before = hashes(),
  network = [],
  errors = [],
  observations = {};
let browser;
const report = {
  scope:
    "Synthetic actual0.35 React Workspace + mocked parent/profile and in-memory requests only; no API/database/current authority/acceptance claim",
  status: "NOT_RUN",
  observations,
  source_sha256_start: before,
};
try {
  browser = await chromium.launch({
    executablePath:
      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: true,
    args: ["--no-sandbox"],
  });
  report.browser = browser.version();
  report.platform = process.platform;
  const context = await browser.newContext();
  await context.route("**/*", (route) => {
    const u = new URL(route.request().url());
    if (u.origin !== "http://127.0.0.1:8196" || u.pathname.startsWith("/v1/")) {
      network.push(route.request().url());
      return route.abort();
    }
    return route.continue();
  });
  const page = await context.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  page.setDefaultTimeout(10000);
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("http://127.0.0.1:8196/baseline/");
  await page
    .getByRole("combobox", { name: "Saved adoption plans", exact: true })
    .selectOption("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa");
  const original = await page.evaluate(() => window.fixture.row());
  observations.original_stored_profile = original.data.profile;
  const goal = page.getByRole("textbox", { name: "AI goal", exact: true });
  assert.equal(await goal.inputValue(), "");
  await goal.fill("Only-profile unsaved Café goal\nKeep this exact brief");
  observations.entered_goal = await goal.inputValue();
  assert.equal(
    await page
      .getByRole("textbox", { name: "Plan name", exact: true })
      .inputValue(),
    "",
  );
  await page
    .getByRole("button", { name: "Open saved plan", exact: true })
    .click();
  await page
    .getByText(
      "Saved plan opened. These are shared draft records for your organisation.",
      { exact: true },
    )
    .waitFor();
  observations.discard_dialog_count = await page
    .getByRole("dialog", { name: "Discard unsaved edits?", exact: true })
    .count();
  observations.goal_after_open = await goal.inputValue();
  observations.mock_calls = await page.evaluate(() => window.fixture.calls());
  assert.equal(observations.discard_dialog_count, 0);
  assert.equal(observations.goal_after_open, original.data.profile.goal);
  assert.notEqual(observations.goal_after_open, observations.entered_goal);
  assert.equal(
    observations.mock_calls.filter(
      (c) =>
        c.path.endsWith("/plans/" + original.object_id) && c.method === "GET",
    ).length,
    1,
  );
  assert.deepEqual(await page.evaluate(() => window.fixture.row()), original);
  assert.equal(
    observations.mock_calls.filter((c) => c.method !== "GET").length,
    0,
  );
  assert.deepEqual(network, []);
  assert.deepEqual(errors, []);
  await page.screenshot({
    path: out + "/baseline-profile-lost-1440.png",
    fullPage: true,
  });
  report.status = "REPRODUCED";
  report.finding =
    "Existing unsaved profile-only input bypasses discard dialog and is replaced by saved profile on deliberate open";
} catch (error) {
  report.status = "REPRODUCTION_FAILED";
  report.error = String(error.stack || error);
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  report.source_sha256_end = hashes();
  report.source_unchanged =
    JSON.stringify(before) === JSON.stringify(report.source_sha256_end);
  report.network_refusals = network;
  report.page_errors = errors;
  if (!report.source_unchanged) process.exitCode = 1;
  fs.writeFileSync(
    out + "/reproduction.json",
    JSON.stringify(report, null, 2) + "\n",
  );
  console.log(report.status);
}
