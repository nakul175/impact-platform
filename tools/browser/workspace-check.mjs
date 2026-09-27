import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";

const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py workspace-browser");
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
const results = [],
  errors = [],
  pages = [];
async function user(name) {
  const context = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
    }),
    p = await context.newPage();
  pages.push(p);
  p.setDefaultTimeout(15000);
  p.on("pageerror", (e) => errors.push(e.message));
  let releaseAccess;
  if (name === "admin") {
    const accessReady = new Promise((resolve) => {
      releaseAccess = resolve;
    });
    await context.route("**/me/access", async (route) => {
      await accessReady;
      await route.continue();
    });
  }
  await p.goto(base);
  await p.getByLabel("Username", { exact: true }).fill(name);
  await p.getByLabel("Password", { exact: true }).fill(passwords[name]);
  await p.getByRole("button", { name: "Sign in →", exact: true }).click();
  await p
    .getByRole("button", { name: "Workspace settings", exact: false })
    .click();
  await p
    .getByRole("heading", { name: "Workspace settings", exact: true })
    .waitFor();
  releaseAccess?.();
  return p;
}
async function test(name, fn) {
  await fn();
  results.push({ name, status: "passed" });
  console.log("PASS " + name);
}
async function tab(p, name) {
  await p
    .getByRole("navigation", { name: "Workspace administration" })
    .getByRole("button", { name, exact: true })
    .click();
}
async function save(p, name = "Save change") {
  await p
    .getByLabel("Reason", { exact: true })
    .fill("Browser qualification: " + name);
  await p
    .getByRole("dialog")
    .getByRole("button", { name, exact: true })
    .click();
  await p.getByRole("dialog").waitFor({ state: "hidden" });
}
const findRow = (p, name) =>
  p.locator("tbody tr").filter({ has: p.getByText(name, { exact: true }) });
let page;
try {
  page = await user("admin");
  const unique = String(Date.now()),
    role = "Field readers " + unique,
    group = "Field team " + unique,
    unit = "North region " + unique;
  await test("Initialize settings after delayed permissions and create a custom role", async () => {
    await page
      .getByRole("button", { name: "Create role", exact: true })
      .click();
    await page.getByLabel("Name", { exact: true }).fill(role);
    await page.getByLabel("groups.read", { exact: true }).check();
    await save(page);
    await findRow(page, role).waitFor();
  });
  await test("Create an organisation unit and preserve its stable code on rename", async () => {
    await tab(page, "Organisation");
    await page
      .getByRole("button", { name: "Create unit", exact: true })
      .click();
    await page.getByLabel("Name", { exact: true }).fill(unit);
    await page
      .getByLabel("Stable code", { exact: true })
      .fill("NORTH_" + unique);
    await save(page);
    await findRow(page, unit)
      .getByRole("button", { name: "Rename unit", exact: true })
      .click();
    await page.getByLabel("Name", { exact: true }).fill(unit + " updated");
    await save(page);
    assert.match(await findRow(page, unit + " updated").innerText(), /NORTH_/);
  });
  await test("Create a group and submit a complete access proposal", async () => {
    await tab(page, "Groups");
    await page
      .getByRole("button", { name: "Create group", exact: true })
      .click();
    await page.getByLabel("Name", { exact: true }).fill(group);
    await save(page);
    await findRow(page, group)
      .getByRole("button", { name: "Propose access", exact: true })
      .click();
    await page.getByLabel("Author", { exact: true }).check();
    await page
      .getByLabel("Role binding", { exact: true })
      .selectOption({ label: role });
    await page
      .getByLabel("Scope", { exact: true })
      .selectOption({ label: "All workspace records" });
    await save(page);
  });
  await test("Reject requester self-approval without applying the proposal", async () => {
    await tab(page, "Group reviews");
    await page
      .getByRole("button", { name: "Review approval", exact: true })
      .click();
    await page
      .getByLabel("Reason", { exact: true })
      .fill("Self approval must fail");
    await page
      .getByRole("button", { name: "Approve reviewed change", exact: true })
      .click();
    await page.getByRole("dialog").getByRole("alert").waitFor();
    await page
      .getByRole("button", { name: "Close dialog", exact: true })
      .click();
  });
  const owner = await user("owner");
  await test("Independent owner reviews scopes and capabilities before group approval", async () => {
    await tab(owner, "Group reviews");
    await owner
      .getByRole("button", { name: "Review approval", exact: true })
      .click();
    await owner
      .getByRole("dialog")
      .getByText("Capabilities: groups.read", { exact: true })
      .waitFor();
    await save(owner, "Approve reviewed change");
    await owner.getByText("Applied", { exact: true }).waitFor();
  });
  await test("Remove group membership through an explicit reviewed action", async () => {
    await tab(page, "Groups");
    await page
      .getByRole("button", { name: "Refresh settings", exact: true })
      .click();
    await findRow(page, group)
      .getByRole("button", { name: "Remove member", exact: true })
      .click();
    await page
      .getByLabel("Member", { exact: true })
      .selectOption({ label: "Author · Active" });
    await save(page);
    await findRow(page, group)
      .getByText("0 members · 1 role bindings", { exact: true })
      .waitFor();
  });
  await test("Nominate an existing administrator and accept custody as the successor", async () => {
    await tab(owner, "Ownership");
    await owner
      .getByRole("button", { name: "Nominate owner", exact: true })
      .click();
    await owner
      .getByLabel("Member", { exact: true })
      .selectOption({ label: "Admin · Active" });
    await save(owner);
    await tab(page, "Ownership");
    await page
      .getByRole("button", { name: "Accept ownership", exact: true })
      .click();
    await save(page);
    await page.getByText("Applied", { exact: true }).waitFor();
  });
  await test("Persist personal preferences and apply reduced motion", async () => {
    await page
      .getByRole("button", { name: "My account", exact: false })
      .click();
    await page
      .getByLabel("Display name", { exact: true })
      .fill("Workspace administrator");
    await page.getByLabel("Time zone", { exact: true }).fill("Asia/Kolkata");
    await page.getByLabel("Reduce motion", { exact: true }).check();
    await page
      .getByRole("button", { name: "Save preferences", exact: true })
      .click();
    await page.getByText("Preferences saved.", { exact: true }).waitFor();
    assert.equal(
      await page.locator("html").getAttribute("data-reduced-motion"),
      "true",
    );
    await page.reload();
    await page
      .getByRole("button", { name: "My account", exact: false })
      .click();
    assert.equal(
      await page.getByLabel("Display name", { exact: true }).inputValue(),
      "Workspace administrator",
    );
  });
  await test("Desktop and mobile account screens remain usable", async () => {
    await page.screenshot({
      path: path.join(root, "docs/evidence/workspace-account-desktop.png"),
      fullPage: true,
    });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForFunction(
      () => document.documentElement.scrollWidth <= window.innerWidth + 1,
    );
    await page.screenshot({
      path: path.join(root, "docs/evidence/workspace-account-mobile.png"),
      fullPage: true,
    });
  });
  await test("Revoke all sessions and return to sign-in", async () => {
    await page
      .getByRole("button", { name: "Sign out all sessions", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Confirm revocation", exact: true })
      .click();
    await page
      .getByRole("heading", { name: "Welcome back", exact: true })
      .waitFor();
  });
  assert.deepEqual(errors, []);
} catch (e) {
  process.exitCode = 1;
  console.error(e.message);
  for (const p of pages)
    console.error(
      "Visible errors:",
      await p
        .getByRole("alert")
        .allTextContents()
        .catch(() => []),
    );
  if (page)
    await page
      .screenshot({
        path: path.join(local, "workspace-browser-failure.png"),
        fullPage: true,
      })
      .catch(() => {});
} finally {
  await fs.writeFile(
    path.join(root, "docs/evidence/workspace-browser-tests.json"),
    JSON.stringify(
      { engine: "Chromium 153", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
  await browser.close();
}
