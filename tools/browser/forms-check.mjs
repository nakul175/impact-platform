import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py forms-browser");
const passwords = JSON.parse(
  await fs.readFile(path.join(local, "passwords.json"), "utf8"),
);
const fixture = JSON.parse(
  await fs.readFile(
    path.join(root, "specification/fixtures/api-fixture.json"),
    "utf8",
  ),
);
const tenant = fixture.tenant_a;
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
let page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
const pages = {};
const results = [],
  errors = [];
function watch(candidate) {
  candidate.setDefaultTimeout(15000);
  candidate.on("pageerror", (e) => errors.push(e.message));
}
watch(page);
async function test(name, fn) {
  try {
    await fn();
  } catch (e) {
    // Printed to stdout so that the CI step output names the failing step.
    console.log("FAIL " + name + ": " + e.message);
    throw e;
  }
  results.push({ name, status: "passed" });
  console.log("PASS " + name);
}
const button = (name) => page.getByRole("button", { name, exact: true });
const label = (name) => page.getByLabel(name, { exact: true });
const dialog = () => page.getByRole("dialog");
async function login(user) {
  await label("Username").fill(user);
  await label("Password").fill(passwords[user]);
  await button("Sign in →").click();
  await page
    .getByRole("heading", { name: "Programme portfolio", exact: true })
    .waitFor();
  pages[user] = page;
}
async function switchUser(user) {
  if (pages[user]) {
    page = pages[user];
    await page.reload();
    await page
      .getByRole("heading", { name: "Programme portfolio", exact: true })
      .waitFor();
    return;
  }
  page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
  watch(page);
  await page.goto(base);
  await login(user);
}
// Programme, approved definition, activated indicator and collection plan are prepared through
// the API with the suite-start bearer tokens; form design, publication and collection are
// exercised in the browser.
async function api(actor, route, data, method = "POST", revision) {
  const response = await fetch(base + "/v1/tenants/" + tenant + "/" + route, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + process.env[fixture.actors[actor].token_env],
    },
    body:
      method === "GET"
        ? undefined
        : JSON.stringify({
            operation_id: crypto.randomUUID(),
            ...(revision ? { expected_revision: revision } : {}),
            data,
          }),
  });
  const body = await response.json();
  assert(response.ok, JSON.stringify(body));
  return body;
}
const read = (route) => api("author", route, null, "GET");
async function saveReceipt(click, suffix) {
  const pending = page.waitForResponse(
    (r) => r.request().method() === "POST" && r.url().endsWith(suffix),
  );
  await click();
  const response = await pending;
  assert(response.ok(), await response.text());
  return response.json();
}
// The first POST ending in `suffix` is applied but its response is dropped; the retry must
// repeat the exact command and receive the original receipt (one server-side effect).
async function lostResponseThenRetry(click, suffix) {
  const sent = [];
  let original = null,
    active = true;
  await page.route(
    (url) => url.pathname.endsWith(suffix),
    async (route) => {
      const request = route.request();
      if (!active || request.method() !== "POST") return route.fallback();
      sent.push(request.postDataJSON());
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
    await click();
    await dialog().getByRole("alert").first().waitFor();
    assert(original, "the first attempt reached the server");
    const retried = await saveReceipt(click, suffix);
    assert.equal(sent.length, 2);
    assert.deepEqual(sent[1], sent[0]);
    assert.deepEqual(retried, original);
    return retried;
  } finally {
    active = false;
  }
}

async function openForms(programme) {
  await button("Forms").click();
  await page
    .getByRole("heading", { name: "Forms", exact: true })
    .first()
    .waitFor();
  await label("Programme").selectOption({ label: programme });
}
async function approveCandidate(route) {
  const workflows = await read("workflows?limit=100");
  const target = await read(route);
  const workflow = workflows.items.find(
    (w) =>
      w.lifecycle_state === "InReview" &&
      w.data.candidate_revision === target.revision_id,
  );
  assert(workflow, "workflow for " + route);
  await api(
    "reviewer",
    "workflows/" + workflow.object_id + "/actions/approve",
    {
      candidate_revision: workflow.data.candidate_revision,
      reason: "Browser forms setup",
    },
    "POST",
    workflow.revision_id,
  );
}
const unique = Date.now().toString(),
  programme = "Forms programme " + unique,
  indicatorLabel = "Households visited " + unique,
  formTitle = "Household visit " + unique,
  unit = "unit-" + unique;
try {
  const calendar = (await read("reporting-calendars")).items[0];
  const geography = (await read("geographies")).items[0];
  const created = await api("author", "programmes", {
    code: "FRM",
    title: programme,
    programme_type: "Health",
    starts_at: "2026-01-01T00:00:00Z",
    ends_at: "2027-01-01T00:00:00Z",
    reporting_calendar_id: calendar.object_id,
    geography_id: geography.object_id,
  });
  const definition = await api("author", "indicator-definitions", {
    code: "HH",
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
  const template = (await read("workflow-templates")).items[0];
  await api(
    "author",
    "indicator-definitions/" + definition.object_id + "/actions/submit",
    { workflow_version: template.revision_id },
    "POST",
    definition.revision_id,
  );
  await approveCandidate("indicator-definitions/" + definition.object_id);
  const approvedDefinition = await read(
    "indicator-definitions/" + definition.object_id,
  );
  const instance = await api("author", "indicator-instances", {
    programme_id: created.object_id,
    definition_version: approvedDefinition.revision_id,
    local_applicability: indicatorLabel,
    collector_id: fixture.actors.author.principal_id,
    reviewer_id: fixture.actors.reviewer.principal_id,
  });
  // The approved plan expects this unit to report through the form (FORM/<unit>/<indicator>).
  const records = JSON.parse(
    await fs.readFile(
      path.join(root, "specification/fixtures/records.json"),
      "utf8",
    ),
  );
  const period = records.find((r) => r.key === "period").object_id;
  const plan = await api("author", "collection-plans", {
    title: "Household visits",
    indicator_id: instance.object_id,
    period_id: period,
    obligations: [
      {
        label: unit,
        source_namespace: "FORM",
        source_key: unit + "/" + instance.object_id,
        due_at: "2026-09-01T00:00:00Z",
      },
    ],
  });
  const planned = await read("collection-plans/" + plan.object_id);
  await api(
    "author",
    "collection-plans/" + plan.object_id + "/actions/submit",
    { workflow_version: template.revision_id },
    "POST",
    planned.revision_id,
  );
  await approveCandidate("collection-plans/" + plan.object_id);
  const draftInstance = await read("indicator-instances/" + instance.object_id);
  await api(
    "author",
    "indicator-instances/" + instance.object_id + "/actions/activate",
    {},
    "POST",
    draftInstance.revision_id,
  );
  for (const verb of ["ready", "activate"]) {
    const current = await read("programmes/" + created.object_id);
    await api(
      "author",
      "programmes/" + created.object_id + "/actions/" + verb,
      {},
      "POST",
      current.revision_id,
    );
  }
  await page.goto(base);
  await login("author");
  await test("Design a form bound to an indicator with a relevance rule", async () => {
    await openForms(programme);
    await button("New form").click();
    await label("Form code").fill("HV");
    await label("Form title").fill(formTitle);
    await label("Code 1").fill("consent");
    await label("Question 1 label").fill("Consent given");
    await label("Type 1").selectOption("BOOLEAN");
    await label("Required 1").check();
    await button("Add question").click();
    await label("Code 2").fill("households");
    await label("Question 2 label").fill("Households reached");
    await label("Type 2").selectOption("INTEGER");
    await label("Minimum 2").fill("0");
    await label("Maximum 2").fill("1000");
    await label("Feeds indicator 2").selectOption({ label: indicatorLabel });
    await label("Ask only when 2").selectOption("consent");
    await label("equals 2").fill("true");
    // v0.27: the default language and one complete Hindi language version.
    await label("Default language").fill("en");
    await button("Add language version").click();
    await label("Language code 1").fill("hi");
    await label("Language name 1").fill("हिन्दी");
    await label("hi label for question 1").fill("सहमति दी गई");
    await label("hi label for question 2").fill("पहुँचे हुए परिवार");
    await button("Save draft").click();
    await dialog().waitFor({ state: "hidden" });
    await page.getByRole("cell", { name: new RegExp(formTitle) }).waitFor();
    const forms = await read("forms?limit=100");
    const form = forms.items.find((f) => f.data.title === formTitle);
    assert.equal(form.data.default_language, "en");
    assert.equal(form.data.translation_versions[0].language, "hi");
    const completeness = await read(
      "forms/" + form.object_id + "/completeness",
    );
    assert.equal(completeness.complete, true);
  });
  let formId;
  await test("Send for review; the reviewer approves in the review queue and publishes", async () => {
    await button("Send for review").click();
    await page
      .getByText("sent for independent review", { exact: false })
      .waitFor();
    const forms = await read("forms?limit=100");
    const form = forms.items.find((f) => f.data.title === formTitle);
    formId = form.object_id;
    assert.equal(form.lifecycle_state, "Submitted");
    assert.equal(await button("Publish").count(), 0);
    const workflow = (await read("workflows?limit=100")).items.find(
      (w) => w.lifecycle_state === "InReview" && w.data.candidate_id === formId,
    );
    await switchUser("reviewer");
    // The form version is decided in the ordinary review queue, on the exact submitted revision.
    await button("Review queue").click();
    await page
      .locator("tr")
      .filter({ hasText: workflow.object_id.slice(0, 8) })
      .getByRole("button")
      .first()
      .click();
    await button("Review submission").click();
    await page
      .getByText("Households reached", { exact: false })
      .first()
      .waitFor();
    await label("Decision reason").fill(
      "Checked the questions, rules and indicator binding.",
    );
    await button("Approve").click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await openForms(programme);
    await button("Publish").click();
    await page.getByText("Form version published", { exact: false }).waitFor();
    const published = await read("forms/" + formId + "/published");
    assert.equal(published.version_number, 1);
  });
  await test("Fill in: relevance hides the count, the retry after a lost submit response is exact", async () => {
    await switchUser("author");
    await openForms(programme);
    await button("Fill in").click();
    await dialog().getByText("Version 1", { exact: false }).waitFor();
    await label("Reporting unit").fill(unit);
    // v0.27: switching the language changes the question text, not the stable codes.
    await label("Language").selectOption("hi");
    await dialog().getByText("सहमति दी गई", { exact: false }).first().waitFor();
    await label("Consent given").selectOption("false");
    assert.equal(await label("Households reached").count(), 0);
    await label("Consent given").selectOption("true");
    await dialog()
      .getByText("पहुँचे हुए परिवार", { exact: false })
      .first()
      .waitFor();
    await label("Households reached").fill("12");
    await button("Save draft").click();
    await dialog().getByText("Server draft saved", { exact: false }).waitFor();
    const receipt = await lostResponseThenRetry(
      () => button("Submit response").click(),
      "/actions/submit",
    );
    assert.equal(receipt.business_state, "Submitted");
    await dialog().waitFor({ state: "hidden" });
    const submission = await read("submissions/" + receipt.object_id);
    assert.equal(submission.data.language, "hi");
    assert.equal(submission.data.observation_ids.length, 1);
    const observation = await read(
      "observations/" + submission.data.observation_ids[0],
    );
    assert.equal(observation.data.value, "12");
    assert.equal(observation.data.source_key, unit + "/" + instance.object_id);
    assert.equal(observation.lifecycle_state, "Submitted");
  });
  await test("Round, assignment and coverage are usable through the screen", async () => {
    const assignedUnit = "assigned-" + unique;
    await button("Collection rounds").click();
    await page
      .getByRole("heading", { name: "Collection rounds", exact: true })
      .first()
      .waitFor();
    await button("New round").click();
    await label("Published form").selectOption({ label: formTitle });
    await label("Period").selectOption(period);
    await label("Title").fill("Round " + unique);
    await label("Due date and time").fill("2026-09-01T12:00");
    await label("Expected unit keys, one per line").fill(assignedUnit);
    await button("Save round").click();
    await dialog().waitFor({ state: "hidden" });
    await button("Coverage").click();
    await page.getByText("1 unassigned", { exact: false }).waitFor();
    await button("Assign").click();
    if (
      await label("Member").evaluate((element) => element.tagName === "SELECT")
    )
      await label("Member").selectOption(fixture.actors.author.principal_id);
    else await label("Member").fill(fixture.actors.author.principal_id);
    await button("Assign unit").click();
    await dialog().waitFor({ state: "hidden" });
    await button("Coverage").click();
    await page.getByText("0 unassigned", { exact: false }).waitFor();
    await button("Collect").click();
    await dialog().getByText("Version 1", { exact: false }).waitFor();
    assert.equal(await label("Reporting unit").inputValue(), assignedUnit);
    assert.equal(await label("Reporting unit").isDisabled(), true);
    await label("Consent given").selectOption("false");
    await button("Submit response").click();
    await dialog().waitFor({ state: "hidden" });
    const rounds = await read("collection-rounds?limit=100");
    const round = rounds.items.find((r) => r.data.title === "Round " + unique);
    const report = await read(
      "collection-rounds/" + round.object_id + "/coverage",
    );
    assert.equal(report.received_count, 1);
    assert.equal(report.units[0].assignment_state, "Completed");
  });
  await test("Forms stay within a 390 px mobile width", async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    await openForms(programme);
    await button("Fill in").click();
    await dialog().getByText("Version 1", { exact: false }).waitFor();
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
      "fill dialog overflows at 390 px",
    );
    await page.screenshot({
      path: path.join(root, "docs/evidence/forms-mobile.png"),
      fullPage: true,
    });
    assert.deepEqual(errors, []);
  });
} catch (e) {
  results.push({
    name: "Forms browser run",
    status: "failed",
    message: e.message,
  });
  await page.screenshot({
    path: path.join(root, "docs/evidence/forms-browser-failure.png"),
    fullPage: true,
  });
  console.error(e.message);
  process.exitCode = 1;
} finally {
  await fs.writeFile(
    path.join(root, "docs/evidence/forms-browser-tests.json"),
    JSON.stringify(
      { engine: "Chromium 153", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
  await browser.close();
}
