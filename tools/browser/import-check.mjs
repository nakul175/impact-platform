// import-browser: a CSV import batch in the Imports area (v0.21). The programme, an approved
// count indicator and six approved prior values (the anomaly history) are prepared through the
// API; upload, column mapping, preview, warning acceptance, commit and the independent review of
// a produced observation are exercised in the browser.
import assert from "node:assert/strict";
import {
  harness,
  ok,
  read,
  approveCandidate,
  receipt,
  nav,
  noHorizontalScroll,
  loadUntil,
  fixture,
  records,
  evidencePath,
} from "./qa-harness.mjs";

const { as, test, finish, errors } = await harness("import-browser");
const unique = Date.now().toString(),
  programmeTitle = "Import programme " + unique,
  indicatorLabel = "Households reached " + unique,
  prefix = "U" + unique.slice(-7),
  period = records.period.object_id;
let instance, workflowVersion, batchId, committed;

async function setup() {
  const calendar = (await read("reporting-calendars")).items[0];
  const geography = (await read("geographies")).items[0];
  const programme = await ok("author", "programmes", {
    code: "IMP",
    title: programmeTitle,
    programme_type: "Health",
    starts_at: "2026-01-01T00:00:00Z",
    ends_at: "2027-01-01T00:00:00Z",
    reporting_calendar_id: calendar.object_id,
    geography_id: geography.object_id,
  });
  const definition = await ok("author", "indicator-definitions", {
    code: "HHI",
    name: "Households " + unique,
    measurement_type: "COUNT",
    unit: "households",
    population: "Resident households",
    inclusion: "Registered",
    exclusion: "Duplicates",
    method: "Register count",
    source_mode: "MANUAL",
    time_semantic: "FLOW",
    combination_rule: "SUM",
    display_decimals: 0,
  });
  workflowVersion = (await read("workflow-templates")).items[0].revision_id;
  await ok(
    "author",
    "indicator-definitions/" + definition.object_id + "/actions/submit",
    { workflow_version: workflowVersion },
    "POST",
    definition.revision_id,
  );
  await approveCandidate(definition.object_id);
  const approved = await read("indicator-definitions/" + definition.object_id);
  instance = await ok("author", "indicator-instances", {
    programme_id: programme.object_id,
    definition_version: approved.revision_id,
    local_applicability: indicatorLabel,
    collector_id: fixture.actors.author.principal_id,
    reviewer_id: fixture.actors.reviewer.principal_id,
  });
  const plan = await ok("author", "collection-plans", {
    title: "Household register",
    indicator_id: instance.object_id,
    period_id: period,
    obligations: [
      {
        label: prefix + "-planned",
        source_namespace: "FORM",
        source_key: prefix + "-planned/" + instance.object_id,
        due_at: "2026-09-01T00:00:00Z",
      },
    ],
  });
  const drafted = await read("collection-plans/" + plan.object_id);
  await ok(
    "author",
    "collection-plans/" + plan.object_id + "/actions/submit",
    { workflow_version: workflowVersion },
    "POST",
    drafted.revision_id,
  );
  await approveCandidate(plan.object_id);
  const draftInstance = await read("indicator-instances/" + instance.object_id);
  await ok(
    "author",
    "indicator-instances/" + instance.object_id + "/actions/activate",
    {},
    "POST",
    draftInstance.revision_id,
  );
  for (const verb of ["ready", "activate"]) {
    const current = await read("programmes/" + programme.object_id);
    await ok(
      "author",
      "programmes/" + programme.object_id + "/actions/" + verb,
      {},
      "POST",
      current.revision_id,
    );
  }
  // Six approved values (median 10.5) give the robust outlier check its minimum history.
  const history = await ok("author", "imports", {
    format: "CSV",
    file_name: "history.csv",
    content:
      "unit,households\n" +
      [10, 11, 12, 9, 10, 11].map((v, i) => `${prefix}-H${i},${v}\n`).join(""),
    programme_id: programme.object_id,
    period_id: period,
    mode: "APPEND",
    atomic: true,
    mapping: {
      unit_column: "unit",
      columns: [
        {
          column: "households",
          indicator_id: instance.object_id,
          value_role: "VALUE",
          unit: "households",
        },
      ],
    },
  });
  let staged = await read("imports/" + history.object_id);
  await ok(
    "author",
    "imports/" + history.object_id + "/actions/preview",
    {},
    "POST",
    staged.revision_id,
  );
  staged = await read("imports/" + history.object_id);
  await ok(
    "author",
    "imports/" + history.object_id + "/actions/commit",
    {
      preview_hash: staged.data.preview.preview_hash,
      workflow_version: workflowVersion,
    },
    "POST",
    staged.revision_id,
  );
  const done = await read("imports/" + history.object_id);
  for (const id of done.data.committed.observation_ids)
    await approveCandidate(id, "Approved history for the anomaly check");
}

// The source: one unit already imported for this period (duplicate), one non-numeric value
// (quarantined), one spike (anomaly warning) and one ordinary value.
const csv =
  "unit,households,remarks\n" +
  `${prefix}-H0,9,already imported\n` +
  `${prefix}-Q1,abc,not a number\n` +
  `${prefix}-S1,100,spike\n` +
  `${prefix}-A1,10,ordinary\n`;

await finish(async () => {
  await setup();
  let page = await as("author");
  const label = (name) => page.getByLabel(name, { exact: true });
  const button = (name) => page.getByRole("button", { name, exact: true });
  const batchRow = () =>
    page
      .getByRole("table", { name: "Import batches" })
      .locator("tr")
      .filter({ hasText: "districts-" + unique + ".csv" });

  await test("Upload a CSV and map its value column by name", async () => {
    await nav(page, "Imports");
    await page.getByRole("heading", { name: "Import batches" }).waitFor();
    await label("Programme").selectOption({ label: programmeTitle });
    await label("Period").selectOption(period);
    await label("Source file").setInputFiles({
      name: "districts-" + unique + ".csv",
      mimeType: "text/csv",
      buffer: Buffer.from(csv),
    });
    await button("Map a column").click();
    await label("Column 1").fill("households");
    await label("Indicator 1").selectOption({ label: indicatorLabel });
    await label("Role 1").selectOption("VALUE");
    await label("Unit 1").fill("households");
    await page
      .getByRole("checkbox", { name: "All rows or nothing (atomic)" })
      .uncheck();
    const saved = await receipt(
      page,
      () => button("Save draft").click(),
      "/imports",
    );
    batchId = saved.object_id;
    await page
      .getByRole("status")
      .filter({ hasText: "saved as a draft" })
      .waitFor();
    await batchRow().getByText("Draft", { exact: true }).waitFor();
    await batchRow().getByText("Not previewed", { exact: true }).waitFor();
  });

  await test("Preview classifies a quarantined row, a duplicate and an anomaly warning", async () => {
    await receipt(
      page,
      () => batchRow().getByRole("button", { name: "Preview" }).click(),
      "/actions/preview",
    );
    await batchRow().getByText("Previewed", { exact: true }).waitFor();
    await page
      .getByText(
        "4 rows: 2 accepted, 1 quarantined, 1 duplicate; 1 with warnings.",
        { exact: false },
      )
      .waitFor();
    await page
      .getByText("Unmapped columns ignored: remarks.", { exact: false })
      .waitFor();
    const outcomes = page.getByRole("table", { name: "Row outcomes" });
    const row = (unit) => outcomes.locator("tr").filter({ hasText: unit });
    assert.match(
      await row(prefix + "-H0").innerText(),
      /DUPLICATE[\s\S]*DUPLICATE_UNIT_PERIOD/,
    );
    assert.match(
      await row(prefix + "-Q1").innerText(),
      /QUARANTINED[\s\S]*VALUE_NOT_NUMERIC/,
    );
    assert.match(
      await row(prefix + "-S1").innerText(),
      /ACCEPTED[\s\S]*PRESENT 100[\s\S]*ANOMALY_ROBUST_OUTLIER/,
    );
    assert.match(await row(prefix + "-A1").innerText(), /ACCEPTED/);
    // Nothing is written by a preview.
    const batch = await read("imports/" + batchId);
    assert.equal(batch.lifecycle_state, "Previewed");
    assert.equal(batch.data.committed ?? null, null);
    await page.screenshot({
      path: evidencePath("import-preview.png"),
      fullPage: true,
    });
  });

  await test("Commit waits for the warnings to be accepted; a lost response retries exactly", async () => {
    const commit = button("Commit 2 accepted rows");
    // The flagged value is committed only after an explicit acceptance.
    assert.equal(await commit.isDisabled(), true);
    await page
      .getByRole("checkbox", {
        name: "I have reviewed the warnings; commit the flagged values unchanged",
      })
      .check();
    const sent = [];
    let original = null,
      active = true;
    await page.route(
      (url) => url.pathname.endsWith("/imports/" + batchId + "/actions/commit"),
      async (route) => {
        if (!active) return route.fallback();
        sent.push(route.request().postDataJSON());
        if (sent.length === 1) {
          const response = await route.fetch();
          assert(response.ok(), await response.text());
          original = await response.json();
          return route.abort("connectionreset");
        }
        return route.fallback();
      },
    );
    try {
      await commit.click();
      await page.getByRole("alert").first().waitFor();
      assert(original, "the first commit reached the server");
      const retried = await receipt(
        page,
        () => commit.click(),
        "/actions/commit",
      );
      assert.equal(sent.length, 2);
      assert.deepEqual(sent[1], sent[0]);
      assert.deepEqual(retried, original);
    } finally {
      active = false;
    }
    await page
      .getByRole("status")
      .filter({ hasText: "committed and sent for independent review" })
      .waitFor();
    await batchRow().getByText("Committed", { exact: true }).waitFor();
    const batch = await read("imports/" + batchId);
    assert.equal(batch.lifecycle_state, "Committed");
    assert.equal(batch.data.committed.accepted_warnings, true);
    committed = batch.data.committed.observation_ids;
    assert.equal(committed.length, 2);
  });

  await test("Committed rows appear in Measurement as observations pending review", async () => {
    await nav(page, "Measurement");
    for (const unit of [prefix + "-S1", prefix + "-A1"]) {
      const entry = await loadUntil(
        page,
        page.getByRole("button", { name: new RegExp(batchId + "/" + unit) }),
      );
      await entry.click();
      const detail = page.getByRole("dialog");
      await detail.getByText("Submitted", { exact: true }).first().waitFor();
      await detail.getByText("IMPORT", { exact: true }).first().waitFor();
      await page.keyboard.press("Escape");
      await detail.waitFor({ state: "hidden" });
    }
    for (const id of committed) {
      const observation = await read("observations/" + id);
      assert.equal(observation.lifecycle_state, "Submitted");
      assert.equal(observation.data.source_namespace, "IMPORT");
    }
    const spike = await read("observations/" + committed[0]);
    assert.equal(spike.data.value, "100");
  });

  await test("A second actor reviews and approves an imported observation", async () => {
    const workflows = (await read("workflows?limit=100", "reviewer")).items;
    const workflow = workflows.find(
      (w) =>
        w.lifecycle_state === "InReview" &&
        w.data.candidate_id === committed[1],
    );
    assert(workflow, "review of the imported observation");
    page = await as("reviewer");
    await nav(page, "Review queue");
    await page
      .locator("tr")
      .filter({ hasText: workflow.object_id.slice(0, 8) })
      .getByRole("button")
      .first()
      .click();
    await page
      .getByRole("button", { name: "Review submission", exact: true })
      .click();
    await page
      .getByText(prefix + "-A1", { exact: false })
      .first()
      .waitFor();
    await page
      .getByLabel("Decision reason", { exact: true })
      .fill("Checked the imported row against the source file.");
    await receipt(
      page,
      () => page.getByRole("button", { name: "Approve", exact: true }).click(),
      "/actions/approve",
    );
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    const approved = await read("observations/" + committed[1]);
    assert.equal(approved.data.approval_state, "APPROVED");
    // The spike is still pending its own independent review.
    assert.equal(
      (await read("observations/" + committed[0])).lifecycle_state,
      "Submitted",
    );
  });

  await test("Imports stay within a 390 px mobile width", async () => {
    page = await as("author");
    await page.setViewportSize({ width: 390, height: 844 });
    await nav(page, "Imports");
    await page.getByRole("heading", { name: "Import batches" }).waitFor();
    assert(await noHorizontalScroll(page), "imports overflow at 390 px");
    await page.screenshot({
      path: evidencePath("import-mobile.png"),
      fullPage: true,
    });
    assert.deepEqual(errors, []);
  });
}, "Import browser run");
