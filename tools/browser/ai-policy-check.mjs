// ai-policy-browser: FR-AI-001 explicit AI enablement and policy (build 0.37.0). An administrator's
// policy version is set through the API, then the real client is checked for each persona: a
// Programme Manager (the fixture author) and a MEL Manager (the fixture reviewer) see the read-only
// "Policy in force" card before the advisory request button and no editor; the Organisation
// Administrator (the fixture admin) changes the policy through the editor dialog; and a save made
// against a version that changed meanwhile shows the 409 refusal and reloads the policy in force.
// The server AI switch is off in qualification runs, so no request ever reaches a provider.
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { createRequire } from "node:module";
import {
  harness,
  nav,
  noHorizontalScroll,
  base,
  fixture,
  tenant,
  evidencePath,
} from "./qa-harness.mjs";

const require = createRequire(import.meta.url);
const axeSource = await fs.readFile(
  require.resolve("axe-core/axe.min.js"),
  "utf8",
);
const { as, test, finish, errors } = await harness("ai-policy-browser");
const policyPath = "/v1/tenants/" + tenant + "/ai-enablement/policy";
const rule = (changes = {}) => ({
  use_case: "ADVISORY_DRAFT",
  enabled: true,
  data_classes: ["INTERNAL"],
  destinations: ["openai-us"],
  purposes: ["planning advice"],
  languages: ["en"],
  review_mode: "HUMAN_REVIEW",
  budget_units: 100,
  tools: [],
  ...changes,
});
// The administrator's suite-start bearer token (minted within the last 300 seconds by the runner).
async function policyApi(method = "GET", data) {
  const response = await fetch(base + policyPath, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + process.env[fixture.actors.admin.token_env],
    },
    body: data ? JSON.stringify(data) : undefined,
  });
  return { status: response.status, body: await response.json() };
}
async function enact(changes) {
  const current = await policyApi();
  assert.equal(current.status, 200, JSON.stringify(current.body));
  const saved = await policyApi("PUT", {
    operation_id: crypto.randomUUID(),
    expected_version: current.body.policy_version,
    data: { use_cases: [rule(changes)] },
  });
  assert.equal(saved.status, 200, JSON.stringify(saved.body));
  return saved.body;
}
const card = (page) =>
  page.getByRole("region", { name: "Policy in force", exact: true });
const requestButton = (page) =>
  page.getByRole("button", { name: "Request AI advisory draft", exact: true });
const editorButton = (page) =>
  page.getByRole("button", { name: "Change AI policy", exact: true });
async function openArea(page, version) {
  await nav(page, "AI enablement");
  await page
    .getByRole("heading", { name: "AI enablement for nonprofits", exact: true })
    .waitFor();
  // Wait for the loaded card, never read it the moment it exists.
  await card(page)
    .getByText("Version " + version + ",", { exact: false })
    .waitFor();
}
async function cardPrecedesRequestButton(page) {
  const section = await card(page).elementHandle();
  const button = await requestButton(page).elementHandle();
  assert(section && button, "card and request button are rendered");
  return page.evaluate(
    ([a, b]) =>
      Boolean(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING),
    [section, button],
  );
}
async function scanCard(page) {
  if (!(await page.evaluate(() => Boolean(window.axe))))
    await page.evaluate(axeSource);
  return page.evaluate(async () => {
    const result = await window.axe.run(
      { include: [[".ai-policy-card"]] },
      {
        runOnly: {
          type: "tag",
          values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"],
        },
        resultTypes: ["violations"],
      },
    );
    return result.violations.map((v) => v.id + ": " + v.help);
  });
}

await finish(async () => {
  const first = await enact({});
  const author = await as("author");

  await test("A Programme Manager sees the policy in force before the request button", async () => {
    await openArea(author, first.policy_version);
    const text = await card(author).innerText();
    assert.match(text, /AI advisory drafts\s*On/);
    assert.match(text, /Up to internal data/);
    assert.match(text, /OpenAI \(United States\)/);
    assert.match(text, /planning advice/);
    assert.match(text, /Human review before use/);
    assert.match(text, /switched off for this deployment/);
    assert(await cardPrecedesRequestButton(author));
    // The server switch is off: the request stays disabled and nothing is offered for consent.
    assert(await requestButton(author).isDisabled());
    await author
      .getByText("AI advisory is not configured for this workspace.", {
        exact: false,
      })
      .waitFor();
    assert.equal(await editorButton(author).count(), 0);
    assert.deepEqual(await scanCard(author), []);
    await author.setViewportSize({ width: 390, height: 800 });
    assert(
      await noHorizontalScroll(author),
      "AI policy card overflows at 390 px",
    );
    await card(author).screenshot({ path: evidencePath("ai-policy-card.png") });
    await author.setViewportSize({ width: 1440, height: 560 });
  });

  await test("A MEL Manager reads the policy and has no editor", async () => {
    const reviewer = await as("reviewer");
    await openArea(reviewer, first.policy_version);
    assert(await cardPrecedesRequestButton(reviewer));
    assert.equal(await editorButton(reviewer).count(), 0);
  });

  const admin = await as("admin");
  let saved;
  await test("Only the Organisation Administrator gets the editor and saves a new version", async () => {
    await openArea(admin, first.policy_version);
    await editorButton(admin).click();
    const dialog = admin.getByRole("dialog", { name: "Change AI policy" });
    await dialog
      .getByText(
        "Saving creates policy version " + (first.policy_version + 1),
        { exact: false },
      )
      .waitFor();
    await dialog.getByLabel("Budget units", { exact: true }).fill("75");
    await dialog
      .getByRole("checkbox", { name: "confidential", exact: true })
      .check();
    const answered = admin.waitForResponse(
      (r) =>
        r.request().method() === "PUT" &&
        new URL(r.url()).pathname === policyPath,
    );
    await dialog
      .getByRole("button", { name: "Save AI policy", exact: true })
      .click();
    const response = await answered;
    assert.equal(response.status(), 200, await response.text());
    saved = await response.json();
    assert.equal(saved.policy_version, first.policy_version + 1);
    await card(admin)
      .getByRole("status")
      .filter({
        hasText: "AI policy version " + saved.policy_version + " saved.",
      })
      .waitFor();
    await card(admin)
      .getByText("Version " + saved.policy_version + ",", { exact: false })
      .waitFor();
    const text = await card(admin).innerText();
    assert.match(text, /Up to confidential data/);
    assert.match(text, /Budget units\s*75/);
    const stored = await policyApi();
    assert.deepEqual(stored.body.use_cases, [
      rule({ data_classes: ["INTERNAL", "CONFIDENTIAL"], budget_units: 75 }),
    ]);
  });

  await test("A save against a version that changed meanwhile is refused and the policy reloads", async () => {
    await editorButton(admin).click();
    const dialog = admin.getByRole("dialog", { name: "Change AI policy" });
    await dialog.getByLabel("Budget units", { exact: true }).fill("10");
    // Another administrator session creates the next version while the dialog is open.
    const meanwhile = await enact({ budget_units: 50 });
    assert.equal(meanwhile.policy_version, saved.policy_version + 1);
    const refused = admin.waitForResponse(
      (r) =>
        r.request().method() === "PUT" &&
        new URL(r.url()).pathname === policyPath,
    );
    const reloaded = admin.waitForResponse(
      (r) =>
        r.request().method() === "GET" &&
        new URL(r.url()).pathname === policyPath,
    );
    await dialog
      .getByRole("button", { name: "Save AI policy", exact: true })
      .click();
    const response = await refused;
    assert.equal(response.status(), 409);
    assert.equal((await response.json()).reason_code, "AI_POLICY_CHANGED");
    await reloaded;
    await card(admin)
      .getByRole("alert")
      .filter({ hasText: "Your organisation's AI policy changed." })
      .waitFor();
    await card(admin)
      .getByText("Version " + meanwhile.policy_version + ",", { exact: false })
      .waitFor();
    assert.equal(await dialog.count(), 0);
    assert.match(await card(admin).innerText(), /Budget units\s*50/);
    // Nothing was saved from the stale form.
    const stored = await policyApi();
    assert.equal(stored.body.policy_version, meanwhile.policy_version);
    assert.equal(stored.body.use_cases[0].budget_units, 50);
    assert.deepEqual(await scanCard(admin), []);
    await card(admin).screenshot({ path: evidencePath("ai-policy-stale.png") });
  });

  await test("The policy history shows a loading status, then every version", async () => {
    // Hold the history response so the loading status can be observed, then release it.
    let release;
    const gate = new Promise((resolve) => (release = resolve));
    const revisions = (url) => url.pathname === policyPath + "/revisions";
    await admin.route(revisions, async (route) => {
      await gate;
      await route.fallback();
    });
    try {
      await card(admin).getByText("Policy history", { exact: true }).click();
      await card(admin)
        .getByRole("status")
        .filter({ hasText: "Loading policy history…" })
        .waitFor();
      release();
      await card(admin).locator(".ai-policy-history li").first().waitFor();
    } finally {
      release();
      await admin.unroute(revisions);
    }
    const text = await card(admin).locator(".ai-policy-history").innerText();
    for (const version of [
      first.policy_version,
      saved.policy_version,
      saved.policy_version + 1,
    ])
      assert.match(text, new RegExp("Version " + version + "\\b"));
    assert.equal(
      await card(admin).getByText("Loading policy history…").count(),
      0,
    );
  });

  assert.deepEqual(errors, []);
}, "ai-policy-browser run");
