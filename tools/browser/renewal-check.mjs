import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { approveRecoveryContact } from "./recovery-fixture.mjs";
const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py renewal-browser");
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
const name = "Authority renewal browser " + Date.now();
const DAY = 86400000;
const command = (data, revision) => ({
  operation_id: crypto.randomUUID(),
  ...(revision ? { expected_revision: revision } : {}),
  data,
});
// Same masking as the console: identities are never shown in full.
const mask = (id) => id.slice(0, 8) + "…" + id.slice(-4);
// datetime-local value; the page converts it back with the browser's own clock.
const local_value = (days) =>
  new Date(Date.now() + days * DAY).toISOString().slice(0, 16);
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
    .getByRole("button", { name: "Authority renewal", exact: true })
    .click();
  await p
    .getByRole("heading", { name: "Authority renewal", exact: true })
    .waitFor();
  return p;
}
const panel = (p) =>
  p.getByRole("region", { name: "Delegated authority", exact: true });
const history = (p) =>
  p.getByRole("region", { name: "Authority renewal history", exact: true });
function card(p, state) {
  return p
    .getByRole("article", { name: name + " authority renewal", exact: true })
    .filter({ has: p.getByText(state, { exact: true }) });
}
async function confirm(p, label, reason, state) {
  await p.getByLabel("Reason", { exact: true }).fill(reason);
  await p.getByRole("button", { name: label, exact: true }).click();
  await p
    .getByRole("status")
    .filter({ hasText: `authority renewal ${state}. Change saved.` })
    .waitFor();
}
async function refresh(p) {
  await p
    .getByRole("button", { name: "Refresh authority renewals", exact: true })
    .click();
}
const shown = (p, value) =>
  p.evaluate((v) => new Date(v).toLocaleString(), value);
const authority = (actor, tenant, status = 200) =>
  api(
    actor,
    `/v1/platform/tenants/${tenant.tenant_id}/authority`,
    undefined,
    status,
  );
try {
  // Fixture: an Active managed tenant with applied initial access
  // (owner = author, second administrator = reviewer, operator = admin).
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
      reason: "Synthetic browser renewal tenant",
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
  const profile = await api("author", "/v1/platform/access-bootstraps");
  let access = await api(
    "author",
    `/v1/platform/tenants/${tenant.tenant_id}/access-bootstrap`,
    command(
      {
        second_identity_id: fixture.actors.reviewer.identity_id,
        profile_hash: profile.profile_hash,
        role_names: ["PROGRAMME_MANAGER"],
        expires_at: new Date(Date.now() + 30 * DAY).toISOString(),
        reason: "Synthetic initial access",
      },
      tenant.revision_id,
    ),
  );
  const bootstraps = `/v1/platform/access-bootstraps/${access.request_id}/actions/`;
  access = await api(
    "reviewer",
    bootstraps + "accept",
    command({ reason: "Accept administrator role" }, access.revision_id),
  );
  access = await api(
    "admin",
    bootstraps + "approve",
    command(
      { reason: "Independent initial access review" },
      access.revision_id,
    ),
  );
  assert.equal(access.state, "Applied");
  const initial = await authority("author", tenant);
  assert.equal(initial.renewable, true);
  assert.equal(initial.second_identity_id, fixture.actors.reviewer.identity_id);
  const owner = await user("author");
  await test("Owner inspects the pinned delegated authority of both administrators", async () => {
    const region = panel(owner);
    await region.getByText("Renewable", { exact: true }).waitFor();
    const text = await region.innerText();
    for (const principal of initial.principals) {
      assert.ok(text.includes(mask(principal.identity_id)));
      assert.ok(text.includes(`${principal.capabilities.length} capabilities`));
      assert.ok(text.includes(await shown(owner, principal.expires_at)));
    }
    assert.ok(text.includes(await shown(owner, initial.earliest_expires_at)));
    assert.equal(
      await region
        .getByText(initial.principals[0].capabilities[0], { exact: true })
        .first()
        .isVisible(),
      false,
    );
    await region.locator("details").first().locator("summary").click();
    await region
      .locator("details")
      .first()
      .getByText(initial.principals[0].capabilities[0], { exact: true })
      .waitFor();
  });
  await test("Proposal form pins the second administrator and rejects an expiry inside the current ceiling", async () => {
    await owner
      .getByRole("button", { name: "Propose authority renewal", exact: true })
      .click();
    const second = owner.getByLabel("Second administrator identity UUID", {
      exact: true,
    });
    assert.equal(await second.inputValue(), initial.second_identity_id);
    assert.equal(await second.evaluate((el) => el.readOnly), true);
    await owner.getByLabel("New expiry", { exact: true }).fill(local_value(1));
    await owner.getByLabel("Reason", { exact: true }).fill("Too early");
    await owner
      .getByRole("button", { name: "Confirm renewal proposal", exact: true })
      .click();
    await owner
      .getByRole("alert")
      .filter({ hasText: "after the current expiry" })
      .waitFor();
    assert.equal(
      (await api("author", "/v1/platform/authority-renewals")).items.length,
      0,
    );
  });
  const proposed = local_value(60);
  const expected = await owner.evaluate(
    (v) => new Date(v).toISOString(),
    proposed,
  );
  await test("Owner proposes a bounded renewal pinned to the current authority", async () => {
    await owner.getByLabel("New expiry", { exact: true }).fill(proposed);
    await confirm(
      owner,
      "Confirm renewal proposal",
      "Browser reviewed authority renewal",
      "Requested",
    );
    await card(owner, "Requested").waitFor();
    const text = await card(owner, "Requested").innerText();
    assert.ok(text.includes(await shown(owner, initial.earliest_expires_at)));
    assert.ok(text.includes(await shown(owner, expected)));
    await panel(owner).getByText("Not renewable", { exact: true }).waitFor();
    assert.match(await panel(owner).innerText(), /already pending review/);
    const [row] = (await api("author", "/v1/platform/authority-renewals"))
      .items;
    assert.equal(row.state, "Requested");
    assert.equal(row.authority_hash, initial.authority_hash);
    assert.equal(Date.parse(row.expires_at), Date.parse(expected));
  });
  const stranger = await user("partner");
  await test("Unrelated account sees neither delegated authority nor the proposal", async () => {
    await stranger
      .getByText("No authority renewals are available.", { exact: true })
      .waitFor();
    await stranger
      .getByText("No managed tenants are available to you", { exact: false })
      .waitFor();
    await authority("partner", tenant, 404);
  });
  const second = await user("reviewer");
  await test("Second administrator accepts the exact proposal without a proposal form", async () => {
    assert.equal(
      await second
        .getByRole("button", { name: "Propose authority renewal", exact: true })
        .count(),
      0,
    );
    await card(second, "Requested")
      .getByRole("button", { name: "Accept renewal", exact: true })
      .click();
    await confirm(
      second,
      "Confirm acceptance",
      "Browser reviewed authority renewal",
      "Accepted",
    );
    await card(second, "Accepted").waitFor();
    assert.equal(await card(second, "Accepted").getByRole("button").count(), 0);
  });
  await test("Tenant owner cannot approve: the operator-only denial is enforced and explained", async () => {
    assert.equal(
      await card(owner, "Accepted")
        .getByRole("button", { name: "Approve renewal", exact: true })
        .count(),
      0,
    );
    // Hidden buttons are never security: bypass the client gate and let the server decide.
    await owner.route(
      (url) => url.pathname === "/v1/platform/authority-renewals",
      async (route) => {
        const response = await route.fetch();
        const json = await response.json();
        await route.fulfill({ response, json: { ...json, operator: true } });
      },
    );
    await refresh(owner);
    await card(owner, "Accepted")
      .getByRole("button", { name: "Approve renewal", exact: true })
      .click();
    await owner
      .getByLabel("Reason", { exact: true })
      .fill("Owner attempts approval");
    await owner
      .getByRole("button", { name: "Confirm approval", exact: true })
      .click();
    await owner
      .getByRole("alert")
      .filter({
        hasText:
          "Only an independent platform operator can perform this review",
      })
      .waitFor();
    await owner.unrouteAll({ behavior: "ignoreErrors" });
    await owner.getByRole("button", { name: "Cancel", exact: true }).click();
    await refresh(owner);
    // The untampered directory no longer offers the operator action.
    await card(owner, "Accepted")
      .getByRole("button", { name: "Approve renewal", exact: true })
      .waitFor({ state: "detached" });
    await card(owner, "Accepted")
      .getByRole("button", { name: "Withdraw proposal", exact: true })
      .waitFor();
    const [row] = (await api("author", "/v1/platform/authority-renewals"))
      .items;
    assert.equal(row.state, "Accepted");
    assert.equal(row.applied_at, null);
  });
  const operator = await user("owner");
  let renewed;
  await test("Independent operator approves and every pinned ceiling extends to the renewed expiry", async () => {
    await card(operator, "Accepted")
      .getByRole("button", { name: "Approve renewal", exact: true })
      .click();
    await confirm(
      operator,
      "Confirm approval",
      "Independent operator review",
      "Applied",
    );
    await history(operator)
      .getByRole("row")
      .filter({ hasText: "Applied" })
      .waitFor();
    assert.equal(await card(operator, "Accepted").count(), 0);
    renewed = await authority("author", tenant);
    assert.equal(renewed.renewable, true);
    assert.notEqual(renewed.authority_hash, initial.authority_hash);
    assert.equal(Date.parse(renewed.earliest_expires_at), Date.parse(expected));
    for (const principal of renewed.principals)
      assert.equal(Date.parse(principal.expires_at), Date.parse(expected));
    const [row] = (await api("owner", "/v1/platform/authority-renewals")).items;
    assert.equal(row.state, "Applied");
    assert.equal(row.approved_by, fixture.actors.owner.identity_id);
    const view = await api(
      "reviewer",
      `/v1/tenants/${tenant.tenant_id}/me/access`,
    );
    assert.ok(view.capabilities.includes("roles.manage"));
    await operator.screenshot({
      path: "docs/evidence/authority-renewal.png",
      fullPage: true,
    });
  });
  await test("Owner’s authority panel shows the renewed expiry", async () => {
    await refresh(owner);
    const region = panel(owner);
    await region.getByText("Renewable", { exact: true }).waitFor();
    const text = await region.innerText();
    assert.ok(text.includes(await shown(owner, renewed.earliest_expires_at)));
    assert.ok(!text.includes(await shown(owner, initial.earliest_expires_at)));
  });
  await test("A later proposal is withdrawn by the owner and kept in history", async () => {
    await owner
      .getByRole("button", { name: "Propose authority renewal", exact: true })
      .click();
    await owner.getByLabel("New expiry", { exact: true }).fill(local_value(80));
    await confirm(
      owner,
      "Confirm renewal proposal",
      "Second bounded extension",
      "Requested",
    );
    await card(owner, "Requested")
      .getByRole("button", { name: "Withdraw proposal", exact: true })
      .click();
    await confirm(
      owner,
      "Confirm withdrawal",
      "Withdrawn before review",
      "Cancelled",
    );
    assert.equal(await card(owner, "Requested").count(), 0);
    await history(owner)
      .getByRole("row")
      .filter({ hasText: "Cancelled" })
      .waitFor();
    const later = await authority("author", tenant);
    assert.equal(later.renewable, true);
    assert.equal(later.authority_hash, renewed.authority_hash);
    assert.equal(Date.parse(later.earliest_expires_at), Date.parse(expected));
  });
  await test("Authority renewal review and history fit a mobile viewport", async () => {
    await refresh(operator);
    await history(operator)
      .getByRole("row")
      .filter({ hasText: "Cancelled" })
      .waitFor();
    await operator.setViewportSize({ width: 390, height: 844 });
    assert.ok(
      await operator.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
    await operator.screenshot({
      path: "docs/evidence/authority-renewal-mobile.png",
      fullPage: true,
    });
  });
  assert.deepEqual(errors, []);
  await fs.writeFile(
    "docs/evidence/renewal-browser-tests.json",
    JSON.stringify(
      { engine: "Chromium", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
} catch (e) {
  for (let i = 0; i < pages.length; i++)
    await pages[i].screenshot({
      path: path.join(local, `renewal-${i}-failure.png`),
      fullPage: true,
    });
  throw e;
} finally {
  await browser.close();
}
