import { chromium } from "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/tools/browser/node_modules/playwright-core/index.mjs";
import fs from "node:fs";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
const dir = "/private/tmp/tola-ai-profile-preservation-draft",
  repo =
    "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform",
  out =
    dir + "/" + (process.env.PRIVATE_PROFILE_ATTEMPT || "proposed-attempt-01");
fs.mkdirSync(out);
const require = createRequire(repo + "/tools/browser/package.json"),
  axe = fs.readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");
const names = [
  ...fs
    .readdirSync(repo + "/apps/web/src")
    .filter((name) => /\.(tsx?|css|json)$/.test(name))
    .map((name) => repo + "/apps/web/src/" + name),
  ...[
    "proposed/AIAdoptionWorkspace.tsx",
    "proposed/AIProcurementPreview.tsx",
    "proposed/AIProcurementPreviewModel.ts",
    "proposed/fixture.tsx",
    "proposed/index.html",
    "server.mjs",
    "proposed-check.mjs",
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
  results = [],
  network = [],
  errors = [],
  scans = [],
  captures = [];
let browser, page, active;
const report = {
  scope:
    "Private036 candidate actual React Workspace + mocked parent/profile and in-memory requests; no actual API/current authority/database/acceptance claim",
  status: "NOT_RUN",
  results,
  source_sha256_start: before,
};
const button = (name) => page.getByRole("button", { name, exact: true }),
  goal = () => page.getByRole("textbox", { name: "AI goal", exact: true }),
  planName = () =>
    page.getByRole("textbox", { name: "Plan name", exact: true }),
  dialog = () =>
    page.getByRole("dialog", { name: "Discard unsaved edits?", exact: true });
const fixture = (method, value) =>
  page.evaluate(({ method, value }) => window.fixture[method](value), {
    method,
    value,
  });
const planGets = async () =>
  (await fixture("calls")).filter(
    (c) =>
      c.method === "GET" &&
      c.path.endsWith("/plans/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
  ).length;
const writes = async () =>
  (await fixture("calls")).filter((c) => c.method !== "GET");
async function fresh() {
  await page.goto("http://127.0.0.1:8196/proposed/");
  await page
    .getByRole("combobox", { name: "Saved adoption plans", exact: true })
    .selectOption("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa");
  assert.equal(await goal().inputValue(), "");
  assert.equal(await planName().inputValue(), "");
}
async function opened() {
  await fresh();
  await button("Open saved plan").click();
  await page
    .getByText(
      "Saved plan opened. These are shared draft records for your organisation.",
      { exact: true },
    )
    .waitFor();
  assert.equal(await goal().inputValue(), "Saved canonical Café goal");
}
async function test(name, work) {
  active = name;
  await work();
  results.push({
    name,
    status: "passed",
    scope: "Synthetic mocked request/authority hints only",
  });
  console.log("PASS " + name);
  active = null;
}
async function scan(name) {
  await page.evaluate(axe);
  const r = await page.evaluate(
    async () =>
      await window.axe.run(document, {
        runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa"] },
      }),
  );
  scans.push({
    name,
    violations: r.violations,
    incomplete: r.incomplete.map((v) => ({
      id: v.id,
      impact: v.impact,
      nodes: v.nodes.map((n) => ({
        target: n.target,
        failureSummary: n.failureSummary,
      })),
    })),
  });
  assert.equal(r.violations.length, 0);
}
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
  page = await context.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(10000);
  page.on("pageerror", (e) => errors.push(e.message));
  await test("Fresh initial unchanged brief opens without a false discard prompt", async () => {
    await opened();
    assert.equal(await dialog().count(), 0);
    assert.equal(await planGets(), 1);
    assert.deepEqual(await writes(), []);
  });
  await test("Only-goal Unicode edits require confirmation; Cancel preserves exact profile and makes no canonical GET", async () => {
    await fresh();
    await goal().fill("Only-profile unsaved Café goal\nKeep this exact brief");
    const beforeProfile = await fixture("profile");
    await button("Open saved plan").click();
    await dialog().waitFor();
    assert.equal(await planGets(), 0);
    await button("Keep editing").click();
    assert.deepEqual(await fixture("profile"), beforeProfile);
    assert.equal(await planName().inputValue(), "");
    assert.equal(await planGets(), 0);
    assert.deepEqual(await writes(), []);
    await scan("Profile-only cancel desktop");
    await page.screenshot({
      path: out + "/profile-only-cancel-1440.png",
      fullPage: true,
    });
    captures.push("profile-only-cancel-1440.png");
  });
  await test("Only-team-size edits are protected even with empty goal and all plan fields blank", async () => {
    await fresh();
    await page
      .getByRole("spinbutton", { name: "Team size", exact: true })
      .fill("31");
    const beforeProfile = await fixture("profile");
    await button("Open saved plan").click();
    await dialog().waitFor();
    await button("Keep editing").click();
    assert.equal(await goal().inputValue(), "");
    assert.deepEqual(await fixture("profile"), beforeProfile);
    assert.equal(await planGets(), 0);
  });
  await test("Deliberate Discard performs one canonical GET and applies the exact saved profile and plan", async () => {
    await fresh();
    await goal().fill("Own unsaved draft");
    await button("Open saved plan").click();
    await dialog().waitFor();
    assert.equal(await planGets(), 0);
    await button("Discard edits and open plan").click();
    await page
      .getByText(
        "Saved plan opened. These are shared draft records for your organisation.",
        { exact: true },
      )
      .waitFor();
    assert.equal(await planGets(), 1);
    assert.deepEqual(
      await fixture("profile"),
      (await fixture("row")).data.profile,
    );
    assert.equal(await planName().inputValue(), "Private procurement source");
  });
  await test("Ordinary saved-plan profile edits retain the existing full-data discard protection", async () => {
    await opened();
    await goal().fill("Saved-plan local Café edit");
    const profile = await fixture("profile"),
      gets = await planGets();
    await button("Open saved plan").click();
    await dialog().waitFor();
    await button("Keep editing").click();
    assert.deepEqual(await fixture("profile"), profile);
    assert.equal(await planGets(), gets);
    assert.equal(await planName().inputValue(), "Private procurement source");
  });
  await test("Fresh exact edit then undo returns to the deliberate clean baseline", async () => {
    await fresh();
    await goal().fill("Temporary change");
    await goal().fill("");
    await button("Open saved plan").click();
    await page
      .getByText(
        "Saved plan opened. These are shared draft records for your organisation.",
        { exact: true },
      )
      .waitFor();
    assert.equal(await dialog().count(), 0);
    assert.equal(await planGets(), 1);
  });
  await test("New from a clean saved plan preserves the intended profile and establishes a fresh baseline", async () => {
    await opened();
    const profile = await fixture("profile");
    await button("New adoption plan").click();
    assert.equal(await planName().inputValue(), "");
    assert.deepEqual(await fixture("profile"), profile);
    await page
      .getByRole("combobox", { name: "Saved adoption plans", exact: true })
      .selectOption("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa");
    await button("Open saved plan").click();
    await page
      .getByText(
        "Saved plan opened. These are shared draft records for your organisation.",
        { exact: true },
      )
      .waitFor();
    assert.equal(await dialog().count(), 0);
    assert.equal(await planGets(), 2);
  });
  await test("Dirty new-plan Cancel preserves the existing head, exact edited profile and no new GET", async () => {
    await opened();
    await goal().fill("Own kept new-plan choice");
    const profile = await fixture("profile");
    await button("New adoption plan").click();
    await dialog().waitFor();
    await button("Keep editing").click();
    assert.deepEqual(await fixture("profile"), profile);
    assert.equal(await planName().inputValue(), "Private procurement source");
    assert.equal(await planGets(), 1);
  });
  await test("Explicit dirty New retains the intended profile and rebases only at that deliberate transition", async () => {
    await opened();
    await goal().fill("Own intended new Café brief");
    const profile = await fixture("profile");
    await button("New adoption plan").click();
    await dialog().waitFor();
    await button("Discard edits and start new plan").click();
    assert.equal(await planName().inputValue(), "");
    assert.deepEqual(await fixture("profile"), profile);
    await page
      .getByRole("combobox", { name: "Saved adoption plans", exact: true })
      .selectOption("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa");
    await button("Open saved plan").click();
    await page
      .getByText(
        "Saved plan opened. These are shared draft records for your organisation.",
        { exact: true },
      )
      .waitFor();
    assert.equal(await dialog().count(), 0);
    assert.equal(await planGets(), 2);
  });
  await test("A later edit to the newly accepted brief is protected; the baseline never follows every prop change", async () => {
    await opened();
    await button("New adoption plan").click();
    await goal().fill("Later fresh-brief edit");
    await page
      .getByRole("combobox", { name: "Saved adoption plans", exact: true })
      .selectOption("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa");
    await button("Open saved plan").click();
    await dialog().waitFor();
    await button("Keep editing").click();
    assert.equal(await goal().inputValue(), "Later fresh-brief edit");
    assert.equal(await planGets(), 1);
  });
  await test("Context transition clears the old draft and accepts only the incoming context baseline", async () => {
    await fresh();
    await goal().fill("Old context only goal");
    await fixture("newContext");
    await page.getByText("2 tools shown", { exact: false }).waitFor();
    await page
      .getByRole("combobox", { name: "Saved adoption plans", exact: true })
      .selectOption("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa");
    assert.equal(await goal().inputValue(), "Clean new context brief");
    await button("Open saved plan").click();
    await page
      .getByText(
        "Saved plan opened. These are shared draft records for your organisation.",
        { exact: true },
      )
      .waitFor();
    assert.equal(await dialog().count(), 0);
    const calls = await fixture("calls");
    assert.equal(
      calls.filter(
        (c) =>
          c.method === "GET" &&
          c.path.endsWith("/plans/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
      ).length,
      1,
    );
    assert(
      calls.some((c) => c.path.startsWith("/v1/tenants/another-invented/")),
    );
  });
  await test("Held canonical GET cannot replace an edited then exactly undone fresh brief", async () => {
    await fresh();
    await fixture("holdRead");
    await button("Open saved plan").click();
    await page.waitForFunction(() => window.fixture.readHeld());
    await goal().fill("Edit while read is held");
    await goal().fill("");
    await fixture("releaseRead");
    await page
      .getByText(
        "Your brief or draft changed while the saved plan was opening.",
        { exact: false },
      )
      .waitFor();
    assert.equal(await goal().inputValue(), "");
    assert.equal(await planName().inputValue(), "");
    assert.equal(await button("View saved-plan review").count(), 0);
    assert.equal(await planGets(), 1);
  });
  await test("Held canonical GET cannot apply after read-hint loss and return", async () => {
    await fresh();
    await fixture("holdRead");
    await button("Open saved plan").click();
    await page.waitForFunction(() => window.fixture.readHeld());
    await fixture("canRead", false);
    await page.waitForTimeout(50);
    await fixture("canRead", true);
    await page.waitForTimeout(50);
    await fixture("releaseRead");
    await page
      .getByText("Your access changed while the saved plan was opening.", {
        exact: false,
      })
      .waitFor();
    assert.equal(await goal().inputValue(), "");
    assert.equal(await planName().inputValue(), "");
    assert.equal(await button("View saved-plan review").count(), 0);
  });
  await test("Held canonical GET preserves a newer profile edit without replacing the fresh baseline", async () => {
    await fresh();
    await fixture("holdRead");
    await button("Open saved plan").click();
    await page.waitForFunction(() => window.fixture.readHeld());
    await goal().fill("Newer own brief while opening");
    await fixture("releaseRead");
    await page
      .getByText(
        "Your brief or draft changed while the saved plan was opening.",
        { exact: false },
      )
      .waitFor();
    assert.equal(await goal().inputValue(), "Newer own brief while opening");
    await button("Open saved plan").click();
    await dialog().waitFor();
    assert.equal(await planGets(), 1);
    await button("Keep editing").click();
  });
  await test("A committed save receipt does not erase newer profile edits or turn them into clean saved input", async () => {
    await opened();
    await fixture("holdSave");
    await button("Save plan changes").click();
    await page.waitForFunction(() => window.fixture.saveHeld());
    await goal().fill("Newer goal during captured save");
    await fixture("releaseSave");
    await page
      .getByText("Plan saved. Any edits made while saving remain unsaved.", {
        exact: true,
      })
      .waitFor();
    const ws = await writes();
    assert.equal(ws.length, 1);
    assert.equal(ws[0].body.data.profile.goal, "Saved canonical Café goal");
    assert.equal(await goal().inputValue(), "Newer goal during captured save");
    await button("Open saved plan").click();
    await dialog().waitFor();
    assert.equal(await planGets(), 1);
    await button("Keep editing").click();
  });
  await test("Narrow mobile confirmation is readable and retains exact local goal on Cancel", async () => {
    await page.setViewportSize({ width: 320, height: 900 });
    await fresh();
    await goal().fill("Mobile Café brief kept");
    await button("Open saved plan").click();
    await dialog().waitFor();
    await scan("Profile-only confirmation320");
    await page.screenshot({
      path: out + "/profile-only-confirmation-320.png",
      fullPage: true,
    });
    captures.push("profile-only-confirmation-320.png");
    await button("Keep editing").click();
    assert.equal(await goal().inputValue(), "Mobile Café brief kept");
    assert.equal(await planGets(), 0);
  });
  assert.deepEqual(network, []);
  assert.deepEqual(errors, []);
  assert.equal(results.length, 16);
  report.status = "PASS";
} catch (error) {
  report.status = "FAIL";
  report.failure = { name: active, error: String(error.stack || error) };
  results.push({ name: active, status: "failed", error: String(error) });
  if (page)
    await page
      .screenshot({ path: out + "/failure.png", fullPage: true })
      .catch(() => {});
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  report.source_sha256_end = hashes();
  report.source_unchanged =
    JSON.stringify(before) === JSON.stringify(report.source_sha256_end);
  report.scans = scans;
  report.captures = captures;
  report.network_refusals = network;
  report.page_errors = errors;
  if (!report.source_unchanged) process.exitCode = 1;
  fs.writeFileSync(
    out + "/qualification.json",
    JSON.stringify(report, null, 2) + "\n",
  );
  console.log(
    report.status + " " + results.filter((r) => r.status === "passed").length,
  );
}
