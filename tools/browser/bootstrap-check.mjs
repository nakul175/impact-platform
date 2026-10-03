import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { approveRecoveryContact } from "./recovery-fixture.mjs";
const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py bootstrap-browser");
const fixture = JSON.parse(
  await fs.readFile("specification/fixtures/api-fixture.json", "utf8"),
);
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
const name = "Initial access browser " + Date.now();
async function api(actor, p, body) {
  const response = await fetch(base + p, {
    method: body ? "POST" : "GET",
    headers: {
      Authorization: "Bearer " + process.env[fixture.actors[actor].token_env],
      "Content-Type": "application/json",
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const result = await response.json();
  assert.equal(response.status, 200, JSON.stringify(result));
  return result;
}
const command = (data, revision) => ({
  operation_id: crypto.randomUUID(),
  ...(revision ? { expected_revision: revision } : {}),
  data,
});
async function test(label, fn) {
  await fn();
  results.push({ name: label, status: "passed" });
  console.log("PASS " + label);
}
async function user(actor) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
  });
  const p = await context.newPage();
  pages.push(p);
  p.setDefaultTimeout(15000);
  p.on("pageerror", (e) => errors.push(e.message));
  await p.goto(base);
  await p.getByLabel("Username", { exact: true }).fill(actor);
  await p.getByLabel("Password", { exact: true }).fill(passwords[actor]);
  await p.getByRole("button", { name: "Sign in →", exact: true }).click();
  await p
    .getByRole("button", { name: "Tenant lifecycle", exact: true })
    .click();
  await p.getByRole("button", { name: "Initial access", exact: true }).click();
  await p
    .getByRole("heading", { name: "Initial access", exact: true })
    .waitFor();
  return p;
}
async function confirm(p) {
  await p
    .getByLabel("Reason", { exact: true })
    .fill("Browser reviewed initial access");
  await p
    .getByRole("button", { name: "Confirm initial access change", exact: true })
    .click();
  await p.getByRole("status").filter({ hasText: "Change saved." }).waitFor();
}
async function workspace(p, tenant) {
  await p
    .getByRole("button", { name: "Back to tenant lifecycle", exact: true })
    .click();
  await p
    .getByRole("button", { name: "Back to workspace", exact: true })
    .click();
  await p.getByLabel("Workspace", { exact: true }).selectOption(tenant);
  await p.getByRole("button", { name: "People & access", exact: true }).click();
  await p
    .getByRole("heading", { name: "People & access", exact: true })
    .waitFor();
}
try {
  const q = (await api("admin", "/v1/platform/tenants")).qualifications[0];
  let tenant = await api(
    "admin",
    "/v1/platform/tenants",
    command({
      owner_identity_id: fixture.actors.author.identity_id,
      qualification_id: q.qualification_id,
      operating_name: name,
      reporting_zone: "UTC",
      retention_days: 365,
      privacy_reference: q.privacy_reference,
      reason: "Synthetic browser qualification",
    }),
  );
  tenant = await api(
    "author",
    `/v1/platform/tenants/${tenant.tenant_id}/actions/accept-owner`,
    command({ reason: "Owner acceptance" }, tenant.revision_id),
  );
  await approveRecoveryContact(base, fixture, tenant);
  tenant = await api(
    "owner",
    `/v1/platform/tenants/${tenant.tenant_id}/actions/activate`,
    command({ reason: "Independent activation" }, tenant.revision_id),
  );
  const owner = await user("author");
  await test("Owner proposes explicit administration and selected business delegation", async () => {
    await owner
      .getByRole("button", { name: "Propose initial access", exact: true })
      .click();
    await owner
      .getByLabel("Tenant", { exact: true })
      .selectOption(tenant.tenant_id);
    await owner
      .getByLabel("Second administrator identity UUID", { exact: true })
      .fill(fixture.actors.reviewer.identity_id);
    await owner
      .getByLabel("Access expiry", { exact: true })
      .fill(new Date(Date.now() + 60 * 86400000).toISOString().slice(0, 16));
    assert.equal(
      await owner.getByLabel("PROGRAMME MANAGER", { exact: true }).isChecked(),
      true,
    );
    await confirm(owner);
    assert.match(
      await owner
        .getByRole("article", { name: name + " initial access", exact: true })
        .innerText(),
      /Requested/,
    );
  });
  const stranger = await user("other_tenant");
  await test("Unrelated identity cannot see the access review", async () => {
    await stranger
      .getByText("No initial access reviews are available.", { exact: true })
      .waitFor();
  });
  const second = await user("reviewer");
  await test("Nominated administrator accepts without receiving tenant access", async () => {
    await second
      .getByRole("button", { name: "Accept administrator role", exact: true })
      .click();
    await confirm(second);
    assert.equal(
      await second.evaluate(
        async (t) => (await fetch(`/v1/tenants/${t}/me/access`)).status,
        tenant.tenant_id,
      ),
      404,
    );
  });
  const operator = await user("admin");
  await test("Independent operator reviews and provisions the exact package", async () => {
    await operator
      .getByRole("button", { name: "Approve initial access", exact: true })
      .click();
    await confirm(operator);
    await operator
      .getByRole("article", { name: name + " initial access", exact: true })
      .getByText("Applied", { exact: true })
      .waitFor();
    assert.equal(
      await operator.evaluate(
        async (t) => (await fetch(`/v1/tenants/${t}/me/access`)).status,
        tenant.tenant_id,
      ),
      404,
    );
    await operator.screenshot({
      path: "docs/evidence/initial-access.png",
      fullPage: true,
    });
  });
  await test("New administrators can manage access but cannot read programmes", async () => {
    for (const p of [owner, second])
      assert.equal(
        await p.evaluate(
          async (t) => (await fetch(`/v1/tenants/${t}/programmes`)).status,
          tenant.tenant_id,
        ),
        403,
      );
    await workspace(second, tenant.tenant_id);
    await second
      .locator("tbody")
      .getByText("Reviewer", { exact: true })
      .waitFor();
  });
  await test("Second administrator requests business access and owner approves", async () => {
    await second
      .locator("tbody tr")
      .filter({ has: second.getByText("Reviewer", { exact: true }) })
      .getByRole("button", { name: "View member", exact: true })
      .click();
    await second
      .getByRole("button", { name: "Request role change", exact: true })
      .click();
    await second
      .getByLabel("Role template", { exact: true })
      .selectOption({ label: "PROGRAMME_MANAGER" });
    await second
      .getByLabel("Access scope", { exact: true })
      .selectOption({ label: "All workspace records" });
    // Scoped to the dialog: since build 0.27.0 People & access also carries the
    // retention-policy and retention-hold forms, each with its own "Reason" field.
    await second
      .getByRole("dialog")
      .getByLabel("Reason", { exact: true })
      .fill("Create first programme");
    await second
      .getByRole("button", { name: "Submit access request", exact: true })
      .click();
    await second.getByRole("dialog").waitFor({ state: "hidden" });
    await workspace(owner, tenant.tenant_id);
    await owner
      .getByRole("tab", { name: "Access requests", exact: true })
      .click();
    await owner
      .getByRole("button", { name: "View details", exact: true })
      .click();
    await owner
      .getByRole("button", { name: "Approve request", exact: true })
      .click();
    await owner
      .getByRole("dialog")
      .getByLabel("Reason", { exact: true })
      .fill("Independent business review");
    await owner
      .getByRole("button", { name: "Confirm approval", exact: true })
      .click();
    await owner.getByRole("dialog").waitFor({ state: "hidden" });
    await owner.getByText("Applied", { exact: true }).waitFor();
  });
  await test("Reviewed programme manager creates the first programme in the new tenant", async () => {
    // Re-enter the chosen tenant to refresh newly granted capabilities.
    await second.reload();
    await second
      .getByLabel("Workspace", { exact: true })
      .selectOption(tenant.tenant_id);
    await second
      .getByRole("button", { name: "Portfolio", exact: true })
      .click();
    await second
      .getByRole("button", { name: "New programme", exact: false })
      .click();
    await second.getByLabel("Programme code", { exact: true }).fill("FIRST-UI");
    await second
      .getByLabel("Programme title", { exact: true })
      .fill("First reviewed programme");
    await second.getByLabel("Start date", { exact: true }).fill("2026-01-01");
    await second.getByLabel("End date", { exact: true }).fill("2026-12-31");
    await second
      .getByRole("button", { name: "Save draft", exact: true })
      .click();
    await second
      .getByText("First reviewed programme", { exact: true })
      .first()
      .waitFor();
    await second.screenshot({
      path: "docs/evidence/initial-access-programme.png",
      fullPage: true,
    });
  });
  await test("Initial access review fits a mobile viewport", async () => {
    await operator.setViewportSize({ width: 390, height: 844 });
    assert.ok(
      await operator.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
    await operator.screenshot({
      path: "docs/evidence/initial-access-mobile.png",
      fullPage: true,
    });
  });
  assert.deepEqual(errors, []);
  await fs.writeFile(
    "docs/evidence/bootstrap-browser-tests.json",
    JSON.stringify(
      { engine: "Chromium", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
} catch (e) {
  for (let i = 0; i < pages.length; i++)
    await pages[i].screenshot({
      path: path.join(local, `bootstrap-${i}-failure.png`),
      fullPage: true,
    });
  throw e;
} finally {
  await browser.close();
}
