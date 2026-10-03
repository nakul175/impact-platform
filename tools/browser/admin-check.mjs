import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";

const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py admin-browser");
const passwords = JSON.parse(
  await fs.readFile(path.join(local, "passwords.json"), "utf8"),
);
const fixture = JSON.parse(
  await fs.readFile(
    path.join(root, "specification/fixtures/api-fixture.json"),
    "utf8",
  ),
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
async function newPage() {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
  });
  const p = await context.newPage();
  p.setDefaultTimeout(15000);
  p.on("pageerror", (e) => errors.push(e.message));
  pages.push(p);
  return p;
}
async function test(name, fn) {
  await fn();
  results.push({ name, status: "passed" });
  console.log("PASS " + name);
}
async function login(p, user, heading) {
  await p.getByLabel("Username", { exact: true }).fill(user);
  await p.getByLabel("Password", { exact: true }).fill(passwords[user]);
  await p.getByRole("button", { name: "Sign in →", exact: true }).click();
  await p.getByRole("heading", { name: heading, exact: true }).waitFor();
}
async function close(p) {
  await p.getByRole("button", { name: "Close dialog", exact: true }).click();
}
async function member(p, name) {
  await p.getByRole("tab", { name: "Members", exact: true }).click();
  await p.getByRole("button", { name: "Refresh access", exact: true }).click();
  await p
    .locator("tbody tr")
    .filter({ has: p.getByText(name, { exact: true }) })
    .getByRole("button", { name: "View member", exact: true })
    .click();
}
async function confirm(p, button) {
  await p
    .getByLabel("Reason for access change", { exact: true })
    .fill("Browser qualification: " + button);
  await p
    .getByRole("dialog")
    .getByRole("button", { name: button, exact: true })
    .click();
  await p.getByRole("dialog").waitFor({ state: "hidden" });
}
const page = await newPage();
let invitation, colleague, owner;
try {
  await test("Administrator loads the access-management workspace", async () => {
    await page.goto(base);
    await login(page, "admin", "People & access");
    await page.getByRole("heading", { name: "Members", exact: true }).waitFor();
    await page.locator("tbody").getByText("Owner", { exact: true }).waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/access-members.png"),
    });
  });
  await test("Designated owner has no ordinary offboarding controls", async () => {
    await member(page, "Owner");
    await page
      .getByText("The designated owner cannot be suspended", { exact: false })
      .waitFor();
    assert.equal(
      await page
        .getByRole("button", { name: "Suspend member", exact: true })
        .count(),
      0,
    );
    assert.equal(
      await page
        .getByRole("button", { name: "Revoke member", exact: true })
        .count(),
      0,
    );
    await close(page);
  });
  await test("Create an immutable exact-object access scope", async () => {
    await page.getByRole("tab", { name: "Scopes", exact: true }).click();
    await page
      .getByRole("button", { name: "Create scope", exact: true })
      .click();
    await page
      .getByLabel("Scope name", { exact: true })
      .fill("Browser programme-only scope");
    await page
      .getByLabel("Object identifiers", { exact: true })
      .fill(fixture.programme_a);
    await confirm(page, "Create scope");
    await page
      .getByText("Browser programme-only scope", { exact: true })
      .waitFor();
  });
  await test("Create a time-bounded invitation with explicit manual delivery", async () => {
    await page.getByRole("tab", { name: "Invitations", exact: true }).click();
    await page
      .getByRole("button", { name: "Invite member", exact: true })
      .click();
    await page
      .getByLabel("Verified account email", { exact: true })
      .fill("invitee@example.test");
    await page
      .getByLabel("Role template", { exact: true })
      .selectOption({ label: "AUTHOR" });
    await page
      .getByLabel("Access scope", { exact: true })
      .selectOption({ label: "All workspace records" });
    await confirm(page, "Create invitation");
    await page.getByText("No email has been sent", { exact: false }).waitFor();
    invitation = await page
      .getByLabel("Copy invitation link", { exact: true })
      .inputValue();
    assert(invitation.startsWith(base + "/#invite="));
    // Do not capture a screenshot while the bearer-like invitation link is displayed.
    await page.getByRole("button", { name: "Hide link", exact: true }).click();
    await page.screenshot({
      path: path.join(root, "docs/evidence/access-invitations.png"),
    });
  });
  await test("A forwarded invitation cannot be accepted by the wrong account", async () => {
    const wrong = await page.context().newPage();
    try {
      await wrong.goto(invitation);
      await wrong
        .getByRole("button", { name: "Accept invitation", exact: true })
        .click();
      await wrong
        .getByRole("alert")
        .filter({ hasText: "different verified account" })
        .waitFor();
    } finally {
      await wrong.close();
    }
  });
  await test("Intended account accepts once and receives the granted workspace", async () => {
    colleague = await newPage();
    await colleague.goto(invitation);
    await login(colleague, "invitee", "Join the workspace");
    await colleague
      .getByRole("button", { name: "Accept invitation", exact: true })
      .click();
    await colleague
      .getByRole("heading", { name: "Programme portfolio", exact: true })
      .waitFor();
    assert.equal(new URL(colleague.url()).hash, "");
    await member(page, "Invited colleague");
    await page
      .getByRole("dialog")
      .getByText("AUTHOR", { exact: true })
      .waitFor();
    await close(page);
  });
  await test("Role proposal is recorded and requester self-approval is denied", async () => {
    await member(page, "Invited colleague");
    await page
      .getByRole("button", { name: "Request role change", exact: true })
      .click();
    await page
      .getByLabel("Role template", { exact: true })
      .selectOption({ label: "REVIEWER" });
    await page
      .getByLabel("Access scope", { exact: true })
      .selectOption({ label: "All workspace records" });
    await confirm(page, "Submit access request");
    await page
      .getByRole("tab", { name: "Access requests", exact: true })
      .click();
    await page
      .getByRole("button", { name: "View details", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Approve request", exact: true })
      .click();
    await page
      .getByLabel("Reason for access change", { exact: true })
      .fill("Negative independence test");
    await page
      .getByRole("button", { name: "Confirm approval", exact: true })
      .click();
    await page
      .getByRole("alert")
      .filter({ hasText: "independent reviewer" })
      .waitFor();
    await close(page);
  });
  await test("Independent administrator approves the precise role request", async () => {
    owner = await newPage();
    await owner.goto(base);
    await login(owner, "owner", "People & access");
    await owner
      .getByRole("tab", { name: "Access requests", exact: true })
      .click();
    await owner
      .getByRole("button", { name: "View details", exact: true })
      .click();
    await owner
      .getByRole("button", { name: "Approve request", exact: true })
      .click();
    await confirm(owner, "Confirm approval");
    await owner.getByText("Applied", { exact: true }).waitFor();
    await owner.screenshot({
      path: path.join(root, "docs/evidence/access-approval.png"),
    });
    await member(page, "Invited colleague");
    await page
      .getByRole("dialog")
      .getByText("AUTHOR, REVIEWER", { exact: true })
      .waitFor();
    await close(page);
  });
  await test("Suspension blocks the member's existing browser session", async () => {
    await member(page, "Invited colleague");
    await page
      .getByRole("button", { name: "Suspend member", exact: true })
      .click();
    await confirm(page, "Confirm suspension");
    assert.equal(
      await colleague.evaluate(
        async (tenant) =>
          (await fetch("/v1/tenants/" + tenant + "/programmes")).status,
        fixture.tenant_a,
      ),
      404,
    );
  });
  await test("Reactivation requires a fresh sign-in and clears stale client state", async () => {
    await member(page, "Invited colleague");
    await page
      .getByRole("button", { name: "Reactivate member", exact: true })
      .click();
    await confirm(page, "Confirm reactivation");
    await colleague
      .getByRole("button", { name: "Measurement", exact: true })
      .click();
    await colleague
      .getByRole("heading", { name: "Welcome back", exact: true })
      .waitFor();
    await login(colleague, "invitee", "Programme portfolio");
    assert.equal(
      await colleague.evaluate(
        async (tenant) =>
          (await fetch("/v1/tenants/" + tenant + "/programmes")).status,
        fixture.tenant_a,
      ),
      200,
    );
  });
  await test("Permanent offboarding revokes access and preserves history", async () => {
    await member(page, "Invited colleague");
    await page
      .getByRole("button", { name: "Revoke member", exact: true })
      .click();
    await confirm(page, "Confirm revocation");
    assert.equal(
      await colleague.evaluate(
        async (tenant) =>
          (await fetch("/v1/tenants/" + tenant + "/programmes")).status,
        fixture.tenant_a,
      ),
      404,
    );
    await member(page, "Invited colleague");
    await page
      .getByRole("dialog")
      .getByText("Revoked", { exact: true })
      .waitFor();
    assert.equal(
      await page
        .getByRole("button", { name: "Reactivate member", exact: true })
        .count(),
      0,
    );
    await close(page);
  });
  await test("Access-management page fits a mobile viewport without script errors", async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    );
    await page.screenshot({
      path: path.join(root, "docs/evidence/access-mobile.png"),
      fullPage: true,
    });
    assert.deepEqual(errors, []);
  });
} catch (e) {
  process.exitCode = 1;
  results.push({
    name: "Administration browser run",
    status: "failed",
    message: e.message,
  });
  for (let i = 0; i < pages.length; i++) {
    console.error(
      "PAGE",
      i,
      await pages[i]
        .getByRole("heading")
        .allTextContents()
        .catch(() => []),
      await pages[i]
        .getByRole("alert")
        .allTextContents()
        .catch(() => []),
    );
    console.error(
      "ACCESS STATUS",
      await pages[i]
        .evaluate(async (tenant) => {
          const r = await fetch("/v1/tenants/" + tenant + "/me/access");
          return { status: r.status, code: (await r.json()).code };
        }, fixture.tenant_a)
        .catch(() => null),
    );
    if (i)
      await pages[i]
        .screenshot({
          path: path.join(local, "admin-browser-failure-" + i + ".png"),
          fullPage: true,
        })
        .catch(() => {});
  }
  // Hide invitation secrets before retaining failure evidence.
  await page
    .getByRole("button", { name: "Hide link", exact: true })
    .click({ timeout: 500 })
    .catch(() => {});
  await page
    .screenshot({
      path: path.join(local, "admin-browser-failure.png"),
      fullPage: true,
    })
    .catch(() => {});
  console.error(e.message);
} finally {
  await fs.writeFile(
    path.join(root, "docs/evidence/admin-browser-tests.json"),
    JSON.stringify(
      { engine: "Chromium 153", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
  await browser.close();
}
