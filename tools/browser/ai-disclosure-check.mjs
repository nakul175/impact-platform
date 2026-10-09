// ai-disclosure-browser: US-DC-04 disclose commercial relationships on every listing (build 0.39.0).
// The real client in the AI enablement area, signed in as the tenant administrator (the Executive
// Director persona where the owner delegates administration): every tool card and every comparison
// column carries a commercial-disclosure label, exposed to assistive technology as a note named
// "Commercial disclosure for <tool>"; the label reads "No commercial relationship known" for every
// listing of the real directory (none is disclosed today). A disclosed relationship (types and
// statement) is rendered from a modified real response, because the real directory has none; the
// server-side rules are qualified in test_ai_solutions_catalog.py. A saved plan's archived guidance
// shows the disclosures captured at save time, and a v1 archive (modified response) says none was
// recorded. axe WCAG 2.2 AA scans of the directory, comparison and archive; no overflow at 390 px.
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { createRequire } from "node:module";
import { harness, nav, noHorizontalScroll, ok, read } from "./qa-harness.mjs";

const require = createRequire(import.meta.url);
const axeSource = await fs.readFile(
  require.resolve("axe-core/axe.min.js"),
  "utf8",
);
const { as, test, finish } = await harness("ai-disclosure-browser");
const NONE_KNOWN = "No commercial relationship known";
const SYNTHETIC = {
  status: "DISCLOSED",
  relationship_types: ["referral_fee", "sponsorship"],
  statement:
    "Synthetic browser check: Imprana receives a referral fee and a sponsorship from this provider.",
  declared_on: "2026-10-09",
};
const solutionsRoute = (url) =>
  url.pathname.endsWith("/ai-enablement/solutions");

const tools = (page) => page.locator('section[aria-labelledby="ai-solutions"]');
const cards = (page) => tools(page).locator(".ai-cards article");
const comparison = (page) => page.locator(".ai-comparison");
const note = (scope, name) =>
  scope.getByRole("note", {
    name: "Commercial disclosure for " + name,
    exact: true,
  });

async function openArea(page, count) {
  await nav(page, "AI enablement");
  await page
    .getByRole("heading", { name: "AI enablement for nonprofits", exact: true })
    .waitFor();
  await page
    .getByRole("heading", { name: "Find and compare tools", exact: true })
    .waitFor();
  // Wait for the loaded directory, never read the cards the moment the section exists.
  await cards(page)
    .nth(count - 1)
    .waitFor();
  assert.equal(await cards(page).count(), count);
}
async function leaveArea(page) {
  await nav(page, "People & access");
  await page
    .getByRole("heading", { name: "People & access", exact: true })
    .and(page.locator("h1"))
    .waitFor();
}
async function scan(page, selector) {
  if (!(await page.evaluate(() => Boolean(window.axe))))
    await page.evaluate(axeSource);
  return page.evaluate(async (selector) => {
    const result = await window.axe.run(
      { include: [[selector]] },
      {
        runOnly: {
          type: "tag",
          values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"],
        },
        resultTypes: ["violations"],
      },
    );
    return result.violations.map(
      (v) => v.id + " (" + v.impact + "): " + v.help,
    );
  }, selector);
}
async function compare(page, name) {
  await tools(page)
    .getByRole("button", { name: "Compare " + name, exact: true })
    .click();
  await comparison(page)
    .getByRole("columnheader", {
      name: new RegExp("^" + name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")),
    })
    .waitFor();
}

await finish(async () => {
  const directory = await read("ai-enablement/solutions", "admin");
  const listings = directory.solutions;
  assert.equal(listings.length, 8);
  assert(listings.every((item) => item.commercial_disclosure));
  const admin = await as("admin", 900);

  await test("Every tool card carries its commercial disclosure label", async () => {
    await openArea(admin, listings.length);
    assert.equal(
      await tools(admin).locator(".ai-cards article .ai-disclosure").count(),
      listings.length,
      "exactly one label per card",
    );
    for (const item of listings) {
      const label = note(tools(admin), item.name);
      assert.equal(await label.count(), 1, item.name);
      const text = await label.innerText();
      assert(text.includes(NONE_KNOWN), item.name + ": " + text);
      assert(text.includes(item.commercial_disclosure.statement), item.name);
      assert(text.includes("Declared 2026-10-09."), item.name);
      assert.equal(
        await label.getAttribute("data-disclosure-status"),
        "NONE_KNOWN",
      );
      // The label sits inside the tool's own card.
      const card = cards(admin).filter({
        has: admin.getByRole("heading", { name: item.name, exact: true }),
      });
      assert.equal(await note(card, item.name).count(), 1, item.name);
    }
  });

  await test("Every comparison column carries the disclosure label", async () => {
    const chosen = listings.slice(0, 4);
    for (const item of chosen) await compare(admin, item.name);
    await comparison(admin)
      .getByRole("rowheader", { name: "Commercial disclosure", exact: true })
      .waitFor();
    assert.equal(
      await comparison(admin).locator(".ai-disclosure").count(),
      chosen.length,
    );
    const headers = await comparison(admin)
      .locator("thead th:not(:first-child)")
      .count();
    assert.equal(headers, chosen.length);
    for (const item of chosen) {
      const cell = note(comparison(admin), item.name);
      assert.equal(await cell.count(), 1, item.name);
      assert((await cell.innerText()).includes(NONE_KNOWN), item.name);
    }
    // Columns follow the header order: the n-th disclosure belongs to the n-th tool.
    const names = await comparison(admin)
      .locator(".ai-disclosure")
      .evaluateAll((nodes) => nodes.map((n) => n.getAttribute("aria-label")));
    assert.deepEqual(
      names,
      chosen.map((item) => "Commercial disclosure for " + item.name),
    );
    assert.deepEqual(
      await scan(admin, 'section[aria-labelledby="ai-solutions"]'),
      [],
    );
    await admin.setViewportSize({ width: 390, height: 844 });
    assert(await noHorizontalScroll(admin), "390 px page overflows");
    assert.deepEqual(
      await scan(admin, 'section[aria-labelledby="ai-solutions"]'),
      [],
    );
    await admin.setViewportSize({ width: 1440, height: 900 });
    for (const item of chosen)
      await tools(admin)
        .getByRole("button", { name: "Remove " + item.name, exact: true })
        .first()
        .click();
    await comparison(admin).waitFor({ state: "detached" });
  });

  await test("A disclosed relationship shows its types and statement on the card and in the comparison (client rendering of a modified real response)", async () => {
    const target = listings[2];
    const handler = async (route) => {
      if (route.request().method() !== "GET") return route.fallback();
      const response = await route.fetch();
      const body = await response.json();
      body.solutions.find(
        (item) => item.id === target.id,
      ).commercial_disclosure = SYNTHETIC;
      await route.fulfill({ response, json: body });
    };
    await admin.route(solutionsRoute, handler);
    try {
      await leaveArea(admin);
      await openArea(admin, listings.length);
      const label = note(tools(admin), target.name);
      await label
        .getByText(
          "Commercial relationship disclosed: Referral fee, Sponsorship",
          {
            exact: true,
          },
        )
        .waitFor();
      assert((await label.innerText()).includes(SYNTHETIC.statement));
      assert.equal(
        await label.getAttribute("data-disclosure-status"),
        "DISCLOSED",
      );
      // Every other card keeps its own label.
      assert.equal(
        await tools(admin)
          .locator(
            '.ai-cards .ai-disclosure[data-disclosure-status="NONE_KNOWN"]',
          )
          .count(),
        listings.length - 1,
      );
      await compare(admin, target.name);
      const cell = note(comparison(admin), target.name);
      assert(
        (await cell.innerText()).includes(
          "Commercial relationship disclosed: Referral fee, Sponsorship",
        ),
      );
      assert((await cell.innerText()).includes(SYNTHETIC.statement));
      assert.deepEqual(
        await scan(admin, 'section[aria-labelledby="ai-solutions"]'),
        [],
      );
      await tools(admin)
        .getByRole("button", { name: "Remove " + target.name, exact: true })
        .first()
        .click();
      await comparison(admin).waitFor({ state: "detached" });
    } finally {
      await admin.unroute(solutionsRoute, handler);
    }
    await leaveArea(admin);
    await openArea(admin, listings.length);
    assert.equal(
      await tools(admin)
        .locator(
          '.ai-cards .ai-disclosure[data-disclosure-status="NONE_KNOWN"]',
        )
        .count(),
      listings.length,
    );
  });

  await test("A saved plan's archived guidance shows the disclosures captured at save time", async () => {
    const title = "Synthetic disclosure archive plan " + crypto.randomUUID();
    const saved = await ok("admin", "ai-enablement/plans", {
      title,
      profile: {
        sector: "GENERAL",
        team_size: 8,
        goal: "Draft a public newsletter",
        data_readiness: "BASIC",
        ai_experience: "EXPERIMENTING",
        sensitive_data: false,
      },
      solution_ids: [listings[0].id],
      learning_completed: [],
      procurement: {
        requirements: "Human review and source links",
        data_boundary: "Synthetic examples only",
        budget_notes: "Ask for a written offer",
        vendor_questions: "How do we export and delete our data?",
      },
      pilot: {
        success_measure: "Every sampled claim verified",
        completed_actions: [],
      },
    });
    const guidance = await read(
      "ai-enablement/plans/" +
        saved.object_id +
        "/revisions/" +
        saved.revision_id +
        "/guidance",
      "admin",
    );
    assert.equal(guidance.snapshot_schema_version, "nonprofit-ai-guidance-v2");
    assert.deepEqual(guidance.solutions.payload, directory);
    // Reopen the area so the saved-plan list includes the new plan.
    await leaveArea(admin);
    await openArea(admin, listings.length);
    const archive = admin.getByRole("region", {
      name: "Saved guidance archive",
      exact: true,
    });
    async function openArchive() {
      await admin
        .getByLabel("Saved adoption plans", { exact: true })
        .selectOption(saved.object_id);
      const pending = admin.waitForResponse(
        (r) =>
          r.request().method() === "GET" &&
          new URL(r.url()).pathname.endsWith(
            "/ai-enablement/plans/" + saved.object_id,
          ),
      );
      await admin
        .getByRole("button", { name: "Open saved plan", exact: true })
        .click();
      assert((await pending).ok());
      const archived = admin.waitForResponse(
        (r) =>
          r.request().method() === "GET" &&
          new URL(r.url()).pathname.endsWith(
            "/revisions/" + saved.revision_id + "/guidance",
          ),
      );
      await admin
        .getByRole("button", { name: "View saved guidance", exact: true })
        .click();
      assert((await archived).ok());
      await archive
        .getByText("All three guides were archived for this revision.", {
          exact: true,
        })
        .waitFor();
      await archive
        .locator("summary")
        .filter({ hasText: "Tool directory" })
        .click();
    }
    await openArchive();
    await archive
      .getByText("archive edition nonprofit-ai-guidance-v2", { exact: false })
      .waitFor();
    for (const item of listings) {
      const label = note(archive, item.name);
      assert.equal(await label.count(), 1, item.name);
      const text = await label.innerText();
      assert(text.includes(NONE_KNOWN), item.name);
      assert(text.includes(item.commercial_disclosure.statement), item.name);
    }
    assert.deepEqual(await scan(admin, ".ai-guidance-archive"), []);
    await admin
      .getByRole("button", { name: "Hide saved guidance", exact: true })
      .click();

    // A revision archived before disclosures existed (edition v1) says none was recorded.
    const guidanceRoute = (url) =>
      url.pathname.endsWith("/revisions/" + saved.revision_id + "/guidance");
    const v1 = async (route) => {
      const response = await route.fetch();
      const body = await response.json();
      body.snapshot_schema_version = "nonprofit-ai-guidance-v1";
      for (const item of body.solutions.payload.solutions)
        delete item.commercial_disclosure;
      await route.fulfill({ response, json: body });
    };
    await admin.route(guidanceRoute, v1);
    try {
      await admin
        .getByRole("button", { name: "View saved guidance", exact: true })
        .click();
      await archive
        .getByText("archive edition nonprofit-ai-guidance-v1", {
          exact: false,
        })
        .waitFor();
      await archive
        .locator("summary")
        .filter({ hasText: "Tool directory" })
        .click();
      for (const item of listings) {
        const label = note(archive, item.name);
        assert.equal(
          await label.getAttribute("data-disclosure-status"),
          "NOT_RECORDED",
        );
        const text = await label.innerText();
        assert(text.includes("Commercial disclosure not recorded"), item.name);
        assert(text.includes("saved before the directory recorded"), item.name);
      }
      assert.deepEqual(await scan(admin, ".ai-guidance-archive"), []);
    } finally {
      await admin.unroute(guidanceRoute, v1);
    }
  });
}, "ai-disclosure-browser run");
