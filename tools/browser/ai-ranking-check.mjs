// ai-ranking-browser: US-MP-03 rank opportunities with the organisation's weights (build 0.38.0).
// The real client in the AI enablement area: a Programme Manager (the fixture author) ranks the
// opportunities of a brief with the default weights and sees rank, four scores and the weighted
// total; changes the weights in the editor (four labelled inputs, the sum shown) and the ranking is
// recalculated citing the new weights revision; weights that do not add up to 100 are refused with
// an alert and nothing is sent; a save against weights another administrator changed meanwhile gets
// the 409 alert and the weights in force reload; a reader without ai.enablement.manage (tenant B's
// AUTHOR) ranks with the defaults and has no editor; and the "Not ranked: scores incomplete" list
// renders what the server returns. The scores and totals are computed by the server
// (test_ai_ranking.py qualifies them); the client only shows them.
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
const { as, test, finish, errors } = await harness("ai-ranking-browser");
const weightsPath = "/v1/tenants/" + tenant + "/ai-enablement/ranking-weights";
const rankingPath = "/v1/tenants/" + tenant + "/ai-enablement/ranking";
const DEFAULT = { impact: 25, effort: 25, cost: 25, readiness: 25 };
const IMPACT_FIRST = { impact: 70, effort: 10, cost: 10, readiness: 10 };
const PROFILE = {
  sector: "GENERAL",
  team_size: 8,
  goal: "Improve impact reporting",
  data_readiness: "STRUCTURED",
  ai_experience: "EXPERIMENTING",
  sensitive_data: false,
};
// Server-computed from the editorial scores (qualified in test_ai_ranking.py).
const DEFAULT_ORDER = [
  ["communications", "87.50"],
  ["data_foundation", "81.25"],
  ["mel_narratives", "75.00"],
  ["knowledge_search", "56.25"],
];
const IMPACT_FIRST_ORDER = [
  ["data_foundation", "77.50"],
  ["mel_narratives", "75.00"],
  ["communications", "65.00"],
  ["knowledge_search", "52.50"],
];
const LABELS = [
  "Impact weight",
  "Effort weight",
  "Cost weight",
  "Readiness weight",
];

// Suite-start bearer tokens of the fixture actors (minted by the runner): setup and independent
// assertions only.
async function api(actor, path, method = "GET", data) {
  const response = await fetch(base + path, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + process.env[fixture.actors[actor].token_env],
    },
    body: data ? JSON.stringify(data) : undefined,
  });
  return { status: response.status, body: await response.json() };
}
async function weightsNow(actor = "admin") {
  const current = await api(actor, weightsPath);
  assert.equal(current.status, 200, JSON.stringify(current.body));
  return current.body;
}
async function saveWeights(actor, data, expected) {
  const saved = await api(actor, weightsPath, "PUT", {
    operation_id: crypto.randomUUID(),
    expected_revision: expected,
    data,
  });
  assert.equal(saved.status, 200, JSON.stringify(saved.body));
  return saved.body;
}
const panel = (page) =>
  page.getByRole("region", { name: "Rank opportunities", exact: true });
const rankButton = (page) =>
  panel(page).getByRole("button", { name: "Rank opportunities", exact: true });
const saveButton = (page) =>
  panel(page).getByRole("button", { name: "Save weights", exact: true });

async function openArea(page, revision) {
  await nav(page, "AI enablement");
  await page
    .getByRole("heading", { name: "AI enablement for nonprofits", exact: true })
    .waitFor();
  // Wait for the loaded weights, never read the panel the moment it exists.
  await panel(page).locator(".ai-ranking-weights").waitFor();
  await page
    .locator('section.ai-ranking[data-weights-revision="' + revision + '"]')
    .waitFor();
}
async function fillBrief(page) {
  await page
    .getByLabel("Team size", { exact: true })
    .fill(String(PROFILE.team_size));
  await page
    .getByLabel("Data readiness", { exact: true })
    .selectOption(PROFILE.data_readiness);
  await page
    .getByLabel("AI experience", { exact: true })
    .selectOption(PROFILE.ai_experience);
  await page.getByLabel("AI goal", { exact: true }).fill(PROFILE.goal);
}
async function rank(page) {
  const answered = page.waitForResponse(
    (r) =>
      r.request().method() === "POST" &&
      new URL(r.url()).pathname.endsWith("/ai-enablement/ranking"),
  );
  await rankButton(page).click();
  const response = await answered;
  assert.equal(response.status(), 200, await response.text());
  const body = await response.json();
  await page
    .locator(
      '.ai-ranking-result[data-ranking-revision="' +
        (body.weights_revision_id ?? "DEFAULT") +
        '"]',
    )
    .waitFor();
  return body;
}
async function shownRows(page) {
  return page.locator(".ai-ranking-table tbody tr").evaluateAll((rows) =>
    rows.map((row) => ({
      id: row.getAttribute("data-use-case"),
      cells: [...row.children].map((cell) => cell.textContent.trim()),
    })),
  );
}
async function fillWeights(page, values) {
  const order = [values.impact, values.effort, values.cost, values.readiness];
  for (const [index, label] of LABELS.entries())
    await panel(page)
      .getByLabel(label, { exact: true })
      .fill(String(order[index]));
}
async function scanPanel(page) {
  if (!(await page.evaluate(() => Boolean(window.axe))))
    await page.evaluate(axeSource);
  return page.evaluate(async () => {
    const result = await window.axe.run(
      { include: [[".ai-ranking"]] },
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
  const start = await weightsNow();
  assert.equal(start.source, "DEFAULT", "a fresh run starts with the defaults");
  const author = await as("author");
  const catalog = await api(
    "author",
    "/v1/tenants/" + tenant + "/ai-enablement/catalog",
  );
  const titles = Object.fromEntries(
    catalog.body.use_cases.map((item) => [item.id, item.title]),
  );

  await test("A Programme Manager ranks the brief's opportunities with four scores and a total", async () => {
    await openArea(author, "");
    assert.match(
      await panel(author).locator(".ai-ranking-weights").innerText(),
      /the defaults \(Impact 25, Effort 25, Cost 25, Readiness 25\)/,
    );
    // The ranking needs a brief first.
    assert(await rankButton(author).isDisabled());
    await fillBrief(author);
    const body = await rank(author);
    assert.equal(body.weights_source, "DEFAULT");
    assert.equal(body.weights_revision_id, null);
    const rows = await shownRows(author);
    assert.deepEqual(
      rows.map((row) => [row.id, row.cells.at(-1)]),
      DEFAULT_ORDER,
    );
    for (const [index, row] of rows.entries()) {
      assert.equal(row.cells[0], String(index + 1));
      assert.equal(row.cells[1], titles[row.id]);
      for (const cell of row.cells.slice(2, 6))
        assert.match(cell, /^[1-5] of 5$/);
    }
    const result = await panel(author)
      .locator(".ai-ranking-result")
      .innerText();
    assert.match(result, /Ranked with the default weights/);
    assert.match(result, /editorial draft pending advisor review/);
    assert.match(result, /Not ranked: scores incomplete/);
    assert.match(
      result,
      /None: every opportunity for this brief has all four scores/,
    );
    // The client shows exactly what the API returns for the same brief.
    const direct = await api("author", rankingPath, "POST", {
      profile: PROFILE,
    });
    assert.deepEqual(
      direct.body.items.map((item) => [item.use_case_id, item.weighted_total]),
      DEFAULT_ORDER,
    );
    assert.deepEqual(await scanPanel(author), []);
  });

  let changed;
  await test("Changing the weights reorders the ranking and cites the new revision", async () => {
    await fillWeights(author, IMPACT_FIRST);
    await panel(author)
      .getByText("Total: 100 of 100", { exact: true })
      .waitFor();
    const answered = author.waitForResponse(
      (r) =>
        r.request().method() === "PUT" &&
        new URL(r.url()).pathname === weightsPath,
    );
    const reranked = author.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        new URL(r.url()).pathname === rankingPath,
    );
    await saveButton(author).click();
    const response = await answered;
    assert.equal(response.status(), 200, await response.text());
    changed = await response.json();
    await panel(author)
      .getByRole("status")
      .filter({ hasText: "Ranking weights saved." })
      .waitFor();
    // The ranking on screen is recalculated with the new weights.
    assert.equal(
      (await (await reranked).json()).weights_revision_id,
      changed.revision_id,
    );
    await author
      .locator(
        '.ai-ranking-result[data-ranking-revision="' +
          changed.revision_id +
          '"]',
      )
      .waitFor();
    assert.deepEqual(
      (await shownRows(author)).map((row) => [row.id, row.cells.at(-1)]),
      IMPACT_FIRST_ORDER,
    );
    const text = await panel(author).locator(".ai-ranking-result").innerText();
    assert(text.includes("revision " + changed.revision_id), text);
    assert.match(text, /Impact 70, Effort 10, Cost 10, Readiness 10/);
    const stored = await weightsNow("reviewer");
    assert.equal(stored.revision_id, changed.revision_id);
    assert.deepEqual(stored.weights, IMPACT_FIRST);
  });

  await test("Weights that do not add up to 100 are refused with an alert and nothing is sent", async () => {
    let puts = 0;
    const count = (r) => {
      if (r.method() === "PUT" && new URL(r.url()).pathname === weightsPath)
        puts++;
    };
    author.on("request", count);
    try {
      await fillWeights(author, {
        impact: 50,
        effort: 30,
        cost: 30,
        readiness: 10,
      });
      await panel(author)
        .getByText("Total: 120 of 100 (must be exactly 100)", { exact: true })
        .waitFor();
      await saveButton(author).click();
      await panel(author)
        .getByRole("alert")
        .filter({
          hasText: "The four weights must add up to 100; these add up to 120.",
        })
        .waitFor();
      assert.equal(
        await panel(author)
          .getByLabel("Impact weight", { exact: true })
          .getAttribute("aria-invalid"),
        "true",
      );
      assert.deepEqual(await scanPanel(author), []);
    } finally {
      author.off("request", count);
    }
    assert.equal(puts, 0);
    const stored = await weightsNow();
    assert.equal(stored.revision_id, changed.revision_id);
    assert.deepEqual(stored.weights, IMPACT_FIRST);
  });

  await test("A save against weights changed meanwhile is refused and the weights in force reload", async () => {
    const admin = await as("admin");
    await openArea(admin, changed.revision_id);
    await fillWeights(admin, {
      impact: 40,
      effort: 20,
      cost: 20,
      readiness: 20,
    });
    // A MEL Manager saves other weights from the same revision while the editor is open.
    const meanwhile = await saveWeights(
      "reviewer",
      { impact: 10, effort: 30, cost: 30, readiness: 30 },
      changed.revision_id,
    );
    const refused = admin.waitForResponse(
      (r) =>
        r.request().method() === "PUT" &&
        new URL(r.url()).pathname === weightsPath,
    );
    await saveButton(admin).click();
    const response = await refused;
    assert.equal(response.status(), 409);
    assert.equal(
      (await response.json()).reason_code,
      "AI_RANKING_WEIGHTS_CHANGED",
    );
    await panel(admin)
      .getByRole("alert")
      .filter({ hasText: "The ranking weights changed since you opened them." })
      .waitFor();
    await admin
      .locator(
        'section.ai-ranking[data-weights-revision="' +
          meanwhile.revision_id +
          '"]',
      )
      .waitFor();
    // The editor now shows the weights in force; nothing was overwritten.
    assert.equal(
      await panel(admin)
        .getByLabel("Impact weight", { exact: true })
        .inputValue(),
      "10",
    );
    const stored = await weightsNow();
    assert.equal(stored.revision_id, meanwhile.revision_id);
    assert.deepEqual(stored.weights, {
      impact: 10,
      effort: 30,
      cost: 30,
      readiness: 30,
    });
    assert.deepEqual(await scanPanel(admin), []);
    await panel(admin).screenshot({
      path: evidencePath("ai-ranking-stale.png"),
    });
  });

  await test("A reader without ai.enablement.manage ranks with the defaults and has no editor", async () => {
    const reader = await as("other_tenant");
    await nav(reader, "AI enablement");
    await reader
      .getByRole("heading", {
        name: "AI enablement for nonprofits",
        exact: true,
      })
      .waitFor();
    await panel(reader).locator(".ai-ranking-weights").waitFor();
    assert.match(
      await panel(reader).locator(".ai-ranking-weights").innerText(),
      /the defaults/,
    );
    assert.equal(await saveButton(reader).count(), 0);
    assert.equal(await panel(reader).getByLabel("Impact weight").count(), 0);
    await fillBrief(reader);
    const body = await rank(reader);
    assert.equal(body.weights_source, "DEFAULT");
    assert.deepEqual(
      (await shownRows(reader)).map((row) => [row.id, row.cells.at(-1)]),
      DEFAULT_ORDER,
    );
  });

  await test("An opportunity the server leaves unranked is listed only under Not ranked: scores incomplete", async () => {
    // The server decides what is unranked (test_ai_ranking.py qualifies a missing cost score); this
    // checks the client's rendering of such a response by moving one opportunity in the real
    // response to `unranked`.
    const ranking = (url) => url.pathname === rankingPath;
    await author.route(ranking, async (route) => {
      const response = await route.fetch();
      const body = await response.json();
      const items = body.items
        .filter((item) => item.use_case_id !== "communications")
        .map((item, index) => ({ ...item, rank: index + 1 }));
      await route.fulfill({
        response,
        json: {
          ...body,
          items,
          unranked: [
            { use_case_id: "communications", missing_scores: ["cost"] },
          ],
        },
      });
    });
    try {
      await rank(author);
      const unranked = panel(author).getByRole("region", {
        name: "Not ranked: scores incomplete",
        exact: true,
      });
      await unranked
        .getByText(titles.communications + ": missing cost score", {
          exact: true,
        })
        .waitFor();
      const rows = await shownRows(author);
      assert(!rows.some((row) => row.id === "communications"));
      assert.deepEqual(
        rows.map((row) => row.cells[0]),
        rows.map((_, index) => String(index + 1)),
      );
      assert.deepEqual(await scanPanel(author), []);
      await author.setViewportSize({ width: 390, height: 800 });
      assert(
        await noHorizontalScroll(author),
        "ranking panel overflows at 390 px",
      );
      await panel(author).screenshot({
        path: evidencePath("ai-ranking-panel.png"),
      });
      await author.setViewportSize({ width: 1440, height: 560 });
    } finally {
      await author.unroute(ranking);
    }
  });

  assert.deepEqual(errors, []);
}, "ai-ranking-browser run");
