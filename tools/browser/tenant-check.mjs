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
// v0.27: the change form is a modal dialog opened from the card, not a panel at the foot of
// the page below the operators, workers and deliveries panels.
async function confirm(p) {
  const dialog = p.getByRole("dialog");
  await dialog.waitFor();
  await dialog
    .getByLabel("Reason", { exact: true })
    .fill("Browser lifecycle qualification");
  await dialog
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
  // The dialog names the action and the organisation, and holds the focus.
  const dialog = p.getByRole("dialog");
  await dialog
    .getByRole("heading", { name: action + ": " + name, exact: true })
    .waitFor();
  assert.ok(
    await p.evaluate(() =>
      Boolean(document.activeElement?.closest("dialog[open]")),
    ),
    "focus moved into the change dialog",
  );
  await confirm(p);
  await p.getByRole("status").filter({ hasText: "Change saved." }).waitFor();
  await dialog.waitFor({ state: "detached" });
}
let admin, nominated;
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
  nominated = await user("author");
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
    const opener = admin
      .getByRole("article", { name, exact: true })
      .getByRole("button", { name: "Activate tenant", exact: true });
    await opener.click();
    await confirm(admin);
    // The refusal is shown inside the open dialog, next to the form that caused it.
    await admin
      .getByRole("dialog")
      .getByRole("alert")
      .filter({ hasText: /independent/i })
      .waitFor();
    await admin.getByRole("button", { name: "Cancel", exact: true }).click();
    await admin.getByRole("dialog").waitFor({ state: "detached" });
    // Cancelling returns focus to the card button that opened the dialog.
    assert.equal(
      await admin.evaluate(() => document.activeElement?.textContent),
      "Activate tenant",
    );
    await opener.waitFor();
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
  await test("Owner awaiting initial access sees what happens next, not a permission error", async () => {
    // v0.27: custody opens no data. Before, the owner landed on the portfolio with "The action
    // is not permitted" and a sidebar full of areas they could not use.
    await nominated
      .getByRole("button", { name: "Back to workspace", exact: true })
      .click();
    const picker = nominated.getByLabel("Workspace", { exact: true });
    await picker
      .locator("option", { hasText: name })
      .waitFor({ state: "attached" });
    // The owner's own view of their access in the new organisation: a custody membership and
    // not one capability.
    const access = await nominated.evaluate(
      async (id) => (await fetch("/v1/tenants/" + id + "/me/access")).json(),
      tenant.tenant_id,
    );
    assert.equal(access.custody, true, JSON.stringify(access));
    assert.deepEqual(access.capabilities, []);
    await picker.selectOption(tenant.tenant_id);
    await nominated
      .getByRole("heading", {
        name: "Your administrator access is being set up",
        exact: true,
      })
      .waitFor();
    const text = await nominated.getByRole("main").innerText();
    assert.match(text, /second administrator accepts/);
    assert.match(text, /platform operator approves/);
    assert.doesNotMatch(text, /not permitted/i);
    assert.equal(await nominated.getByRole("alert").count(), 0);
    const entries = nominated.locator(".sidebar nav button");
    assert.equal(await entries.count(), 2);
    for (const entry of ["My account", "Tenant lifecycle"])
      assert.equal(
        await entries.filter({ hasText: entry }).count(),
        1,
        entry + " stays listed",
      );
    // Back in the fixture workspace every area is listed again.
    const fixtureWorkspace = (await picker.locator("option").allInnerTexts())
      .map((t) => t.trim())
      .find((t) => t !== name);
    await picker.selectOption({ label: fixtureWorkspace });
    await nominated
      .getByRole("heading", { name: "Programme portfolio", exact: true })
      .waitFor();
    assert.ok((await entries.count()) >= 10);
    await nominated
      .getByRole("button", { name: "Tenant lifecycle", exact: true })
      .click();
    await nominated
      .getByRole("heading", { name: "Tenant lifecycle", exact: true })
      .waitFor();
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
    // The author holds capabilities for most areas, so their navigation is the tallest
    // (v0.27 lists only the areas a person can use; an administrator's list is short).
    await p.getByLabel("Username", { exact: true }).fill("author");
    await p.getByLabel("Password", { exact: true }).fill(passwords.author);
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
  await test("Signing out of the console starts the next person in their own workspace", async () => {
    // v0.27: sign-out resets every per-person state in the tab. Before, the next sign-in on
    // the same tab reopened the previous person's Tenant lifecycle console.
    await admin
      .getByRole("heading", { name: "Tenant lifecycle", exact: true })
      .waitFor();
    await admin.getByRole("button", { name: "Sign out", exact: true }).click();
    await admin.getByRole("heading", { name: "Welcome back" }).waitFor();
    await admin.getByLabel("Username", { exact: true }).fill("reviewer");
    await admin
      .getByLabel("Password", { exact: true })
      .fill(passwords.reviewer);
    await admin.getByRole("button", { name: "Sign in →", exact: true }).click();
    await admin
      .getByRole("heading", { name: "Programme portfolio", exact: true })
      .waitFor();
    assert.equal(
      await admin
        .getByRole("heading", { name: "Tenant lifecycle", exact: true })
        .count(),
      0,
    );
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
  if (nominated)
    await nominated
      .screenshot({
        path: path.join(local, "owner-failure.png"),
        fullPage: true,
      })
      .catch(() => {});
  throw e;
} finally {
  await browser.close();
}
