import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py recovery-browser");
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
const name = "Recovery browser " + Date.now();
const command = (data, revision) => ({
  operation_id: crypto.randomUUID(),
  ...(revision ? { expected_revision: revision } : {}),
  data,
});
async function api(actor, p, body, status = 200) {
  const response = await fetch(base + p, {
    method: body ? "POST" : "GET",
    headers: {
      Authorization: "Bearer " + process.env[fixture.actors[actor].token_env],
      "Content-Type": "application/json",
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const result = await response.json();
  assert.equal(response.status, status, JSON.stringify(result));
  return result;
}
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
  await p
    .getByRole("button", { name: "Recovery contacts", exact: true })
    .click();
  await p
    .getByRole("heading", { name: "Recovery contacts", exact: true })
    .waitFor();
  return p;
}
function card(p, person, state) {
  return p
    .getByRole("article", {
      name: name + " recovery contact " + person,
      exact: true,
    })
    .filter({ has: p.getByText(state, { exact: true }) });
}
async function confirm(p) {
  await p
    .getByLabel("Reason", { exact: true })
    .fill("Browser recovery verification");
  await p
    .getByRole("button", {
      name: "Confirm recovery contact change",
      exact: true,
    })
    .click();
  await p.getByRole("status").filter({ hasText: "Change saved." }).waitFor();
}
async function refresh(p) {
  await p
    .getByRole("button", { name: "Refresh recovery contacts", exact: true })
    .click();
}
async function nominate(p, tenant, person) {
  await refresh(p);
  await p
    .getByRole("button", { name: "Nominate recovery contact", exact: true })
    .click();
  await p.getByLabel("Tenant", { exact: true }).selectOption(tenant.tenant_id);
  await p
    .getByLabel("Nominated contact identity UUID", { exact: true })
    .fill(fixture.actors[person].identity_id);
  await p
    .getByLabel("Contact expiry", { exact: true })
    .fill(new Date(Date.now() + 60 * 86400000).toISOString().slice(0, 16));
  await confirm(p);
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
      reason: "Synthetic browser recovery tenant",
    }),
  );
  tenant = await api(
    "author",
    `/v1/platform/tenants/${tenant.tenant_id}/actions/accept-owner`,
    command({ reason: "Owner consent" }, tenant.revision_id),
  );
  await test("Tenant cannot activate without a verified recovery contact", async () => {
    const denied = await api(
      "owner",
      `/v1/platform/tenants/${tenant.tenant_id}/actions/activate`,
      command({ reason: "Missing contact" }, tenant.revision_id),
      403,
    );
    assert.equal(denied.reason_code, "TENANT_NOT_READY");
  });
  const owner = await user("author");
  await test("Owner nominates a bounded recovery contact in the interface", async () => {
    await nominate(owner, tenant, "partner");
    await card(owner, "Partner", "Nominated").waitFor();
  });
  const stranger = await user("other_tenant");
  await test("Unrelated account cannot enumerate recovery nominations", async () => {
    await stranger
      .getByText("No recovery contacts are available.", { exact: true })
      .waitFor();
  });
  const contact = await user("partner");
  await test("Nominated account verifies consent without gaining access", async () => {
    await card(contact, "Partner", "Nominated")
      .getByRole("button", { name: "Verify my recovery contact", exact: true })
      .click();
    await confirm(contact);
    await card(contact, "Partner", "Verified").waitFor();
    await api(
      "partner",
      `/v1/tenants/${tenant.tenant_id}/me/access`,
      undefined,
      404,
    );
  });
  const operator = await user("admin");
  await test("Independent operator approves and tenant readiness permits activation", async () => {
    await card(operator, "Partner", "Verified")
      .getByRole("button", { name: "Approve recovery contact", exact: true })
      .click();
    await confirm(operator);
    await card(operator, "Partner", "Active")
      .getByText("Eligible for readiness: Yes.", { exact: true })
      .waitFor();
    tenant = await api(
      "owner",
      `/v1/platform/tenants/${tenant.tenant_id}/actions/activate`,
      command(
        { reason: "Verified recovery contact present" },
        tenant.revision_id,
      ),
    );
    assert.equal(tenant.readiness.recovery_contact_verified, true);
    await api(
      "partner",
      `/v1/tenants/${tenant.tenant_id}/me/access`,
      undefined,
      404,
    );
    await operator.screenshot({
      path: "docs/evidence/recovery-contact-verified.png",
      fullPage: true,
    });
  });
  const replacement = await user("reviewer");
  await test("Declining a replacement preserves the approved contact", async () => {
    await nominate(owner, tenant, "reviewer");
    await refresh(replacement);
    await card(replacement, "Reviewer", "Nominated")
      .getByRole("button", { name: "Decline nomination", exact: true })
      .click();
    await confirm(replacement);
    await card(replacement, "Reviewer", "Declined").waitFor();
    const row = (await api("admin", "/v1/platform/tenants")).items.find(
      (t) => t.tenant_id === tenant.tenant_id,
    );
    assert.equal(row.recovery_contact.eligible, true);
  });
  await test("Replacement activates only after fresh consent and independent approval", async () => {
    await nominate(owner, tenant, "reviewer");
    await refresh(replacement);
    await card(replacement, "Reviewer", "Nominated")
      .getByRole("button", { name: "Verify my recovery contact", exact: true })
      .click();
    await confirm(replacement);
    await refresh(operator);
    await card(operator, "Reviewer", "Verified")
      .getByRole("button", { name: "Approve recovery contact", exact: true })
      .click();
    await confirm(operator);
    await card(operator, "Reviewer", "Active").waitFor();
    await refresh(contact);
    await card(contact, "Partner", "Replaced").waitFor();
    assert.equal(
      await contact
        .getByRole("article", {
          name: name + " recovery contact Reviewer",
          exact: true,
        })
        .count(),
      0,
    );
  });
  await test("Contact revocation removes readiness without suspending the tenant", async () => {
    await refresh(replacement);
    await card(replacement, "Reviewer", "Active")
      .getByRole("button", { name: "Revoke recovery contact", exact: true })
      .click();
    await confirm(replacement);
    await card(replacement, "Reviewer", "Revoked").waitFor();
    const row = (await api("admin", "/v1/platform/tenants")).items.find(
      (t) => t.tenant_id === tenant.tenant_id,
    );
    assert.equal(row.state, "Active");
    assert.equal(row.recovery_contact.eligible, false);
    await api("author", `/v1/tenants/${tenant.tenant_id}/me/access`);
  });
  await test("Recovery review and history fit a mobile viewport", async () => {
    await refresh(operator);
    await card(operator, "Reviewer", "Revoked").waitFor();
    await operator.setViewportSize({ width: 390, height: 844 });
    assert.ok(
      await operator.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
    await operator.screenshot({
      path: "docs/evidence/recovery-contact-mobile.png",
      fullPage: true,
    });
  });
  assert.deepEqual(errors, []);
  await fs.writeFile(
    "docs/evidence/recovery-browser-tests.json",
    JSON.stringify(
      { engine: "Chromium", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
} catch (e) {
  for (let i = 0; i < pages.length; i++)
    await pages[i].screenshot({
      path: path.join(local, `recovery-${i}-failure.png`),
      fullPage: true,
    });
  throw e;
} finally {
  await browser.close();
}
