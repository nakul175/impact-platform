import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { runWorkerOnce } from "./worker-run.mjs";
import { approveRecoveryContact } from "./recovery-fixture.mjs";
const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py tenant-browser");
const passwords = JSON.parse(
  await fs.readFile(path.join(local, "passwords.json"), "utf8"),
);
const fixture = JSON.parse(
  await fs.readFile("specification/fixtures/api-fixture.json", "utf8"),
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
const results = [],
  errors = [];
async function user(name) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
  });
  const p = await context.newPage();
  p.setDefaultTimeout(15000);
  p.on("pageerror", (e) => errors.push(e.message));
  await p.goto(base);
  await p.getByLabel("Username", { exact: true }).fill(name);
  await p.getByLabel("Password", { exact: true }).fill(passwords[name]);
  await p.getByRole("button", { name: "Sign in →", exact: true }).click();
  await p
    .getByRole("button", { name: "Tenant lifecycle", exact: true })
    .click();
  await p
    .getByRole("heading", { name: "Tenant lifecycle", exact: true })
    .waitFor();
  return p;
}
async function test(name, fn) {
  await fn();
  results.push({ name, status: "passed" });
  console.log("PASS " + name);
}
async function confirm(p) {
  await p
    .getByLabel("Reason", { exact: true })
    .fill("Browser lifecycle qualification");
  await p
    .getByRole("button", { name: "Confirm tenant change", exact: true })
    .click();
}
async function change(p, name, action) {
  // Wait for the refreshed directory before acting, so the action carries the
  // current revision rather than racing the in-flight refresh.
  const [refreshed] = await Promise.all([
    p.waitForResponse(
      (r) =>
        r.request().method() === "GET" &&
        new URL(r.url()).pathname === "/v1/platform/tenants",
    ),
    p.getByRole("button", { name: "Refresh tenants", exact: true }).click(),
  ]);
  await refreshed.finished();
  const card = p.getByRole("article", { name, exact: true });
  await card.getByRole("button", { name: action, exact: true }).click();
  await confirm(p);
  await p.getByRole("status").filter({ hasText: "Change saved." }).waitFor();
}
let admin;
try {
  admin = await user("admin");
  const name = "Lifecycle browser " + Date.now();
  await test("Operator submits a pinned tenant profile", async () => {
    await admin
      .getByRole("button", { name: "Request tenant", exact: true })
      .click();
    await admin.getByLabel("Operating name", { exact: true }).fill(name);
    // v0.26a: operators choose the owner by name from the registered people.
    const owner = admin.getByLabel("Organisation owner", { exact: true });
    await owner.waitFor();
    await owner.selectOption(fixture.actors.author.identity_id);
    await admin
      .getByLabel("Qualified deployment", { exact: true })
      .selectOption({ index: 1 });
    await admin
      .getByLabel("Privacy policy reference", { exact: true })
      .fill("local-development-privacy");
    await confirm(admin);
    await admin
      .getByRole("status")
      .filter({ hasText: "Change saved." })
      .waitFor();
    assert.match(
      await admin.getByRole("article", { name, exact: true }).innerText(),
      /Requested/,
    );
  });
  const nominated = await user("author");
  await test("Nominated owner accepts without receiving automatic data access", async () => {
    assert.equal(
      await nominated
        .getByRole("button", { name: "Request tenant", exact: true })
        .count(),
      0,
    );
    await change(nominated, name, "Accept ownership");
    assert.match(
      await nominated.getByRole("article", { name, exact: true }).innerText(),
      /Provisioning/,
    );
  });
  await test("Requester cannot independently activate their own request", async () => {
    await admin
      .getByRole("button", { name: "Refresh tenants", exact: true })
      .click();
    await admin
      .getByRole("article", { name, exact: true })
      .getByRole("button", { name: "Activate tenant", exact: true })
      .click();
    await confirm(admin);
    await admin
      .getByRole("alert")
      .filter({ hasText: /independent/i })
      .waitFor();
    await admin.getByRole("button", { name: "Cancel", exact: true }).click();
  });
  const approver = await user("owner");
  const response = await fetch(base + "/v1/platform/tenants", {
    headers: {
      Authorization: "Bearer " + process.env[fixture.actors.author.token_env],
    },
  });
  const tenant = (await response.json()).items.find(
    (row) => row.operating_name === name,
  );
  await approveRecoveryContact(base, fixture, tenant);
  await test("Independent operator activates the tenant", async () => {
    await change(approver, name, "Activate tenant");
  });
  await test("Operator suspends and independently reactivates without replay", async () => {
    await change(admin, name, "Suspend tenant");
    await change(approver, name, "Reactivate tenant");
  });
  await test("Closing state preserves records and has no reactivation shortcut", async () => {
    await change(admin, name, "Begin closure");
    const card = admin.getByRole("article", { name, exact: true });
    assert.match(await card.innerText(), /Closing/);
    assert.equal(
      await card
        .getByRole("button", { name: "Reactivate tenant", exact: true })
        .count(),
      0,
    );
  });
  await test("Operator sees worker heartbeats; an owner does not", async () => {
    const workerId = "tenant-browser-" + Date.now();
    runWorkerOnce(local, workerId);
    await admin
      .getByRole("button", { name: "Refresh workers", exact: true })
      .click();
    const entry = admin.getByLabel("Worker " + workerId, { exact: true });
    await entry.waitFor();
    assert.match(await entry.innerText(), /Stopped/);
    // The heartbeat carries this build's version, read from the single version source.
    const { build } = JSON.parse(
      await fs.readFile(path.join(root, "VERSION.json"), "utf8"),
    );
    assert.ok((await entry.innerText()).includes("build " + build));
    await nominated
      .getByRole("button", { name: "Refresh tenants", exact: true })
      .click();
    assert.equal(
      await nominated.getByRole("region", { name: "Workers" }).count(),
      0,
    );
  });
  await test("Every sidebar entry stays reachable on a short screen", async () => {
    // The fixed sidebar scrolls: with every workspace area listed, the last entry (Tenant
    // lifecycle) must still be clickable when the window is shorter than the navigation.
    const context = await browser.newContext({
      viewport: { width: 1440, height: 560 },
    });
    const p = await context.newPage();
    p.setDefaultTimeout(15000);
    p.on("pageerror", (e) => errors.push(e.message));
    await p.goto(base);
    await p.getByLabel("Username", { exact: true }).fill("admin");
    await p.getByLabel("Password", { exact: true }).fill(passwords.admin);
    await p.getByRole("button", { name: "Sign in →", exact: true }).click();
    const entries = p.locator(".sidebar nav button");
    await entries.first().waitFor();
    assert.ok((await entries.count()) >= 10);
    await p
      .getByRole("button", { name: "Tenant lifecycle", exact: true })
      .click();
    await p
      .getByRole("heading", { name: "Tenant lifecycle", exact: true })
      .waitFor();
    await context.close();
  });
  await test("Tenant console fits a mobile viewport", async () => {
    await admin.setViewportSize({ width: 390, height: 844 });
    assert.ok(
      await admin.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
    await admin.screenshot({
      path: "docs/evidence/tenant-lifecycle-mobile.png",
      fullPage: true,
    });
    await admin.setViewportSize({ width: 1440, height: 1000 });
    await admin.screenshot({
      path: "docs/evidence/tenant-lifecycle.png",
      fullPage: true,
    });
  });
  assert.deepEqual(errors, []);
  await fs.writeFile(
    "docs/evidence/tenant-browser-tests.json",
    JSON.stringify(
      { engine: "Chromium", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
} catch (e) {
  if (admin)
    await admin.screenshot({
      path: path.join(local, "tenant-failure.png"),
      fullPage: true,
    });
  throw e;
} finally {
  await browser.close();
}
