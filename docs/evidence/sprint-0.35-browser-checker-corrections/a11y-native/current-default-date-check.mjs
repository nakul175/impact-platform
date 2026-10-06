import { chromium } from "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/tools/browser/node_modules/playwright-core/index.mjs";
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import assert from "node:assert/strict";
import vm from "node:vm";
const folder = "/private/tmp/tola-ai-a11y-checker-correction";
const root =
  "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform";
const candidate = folder + "/a11y-check.proposed.mjs";
const bytes = readFileSync(candidate),
  text = bytes.toString("utf8");
const digest = (path) =>
  createHash("sha256").update(readFileSync(path)).digest("hex");
const candidateSha = digest(candidate),
  sourceSha = digest(root + "/apps/web/src/main.tsx");
const begin = text.indexOf("async function selectWithKeyboard("),
  end = text.indexOf("async function tabTo(", begin);
assert(begin >= 0 && end > begin);
const observations = [],
  focusTrail = [],
  results = [];
const helpers = vm.runInNewContext(
  text.slice(begin, end) + ";({selectWithKeyboard,typeDateWithKeyboard});",
  {
    assert,
    keyboardWidgetObservations: observations,
    isFocused: (field) =>
      field.evaluate((element) => element === document.activeElement),
  },
);
const browser = await chromium.launch({
  executablePath:
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
  env: {
    HOME: process.env.HOME,
    TMPDIR: process.env.TMPDIR,
    PATH: "/usr/bin:/bin:/usr/sbin:/sbin",
  },
  args: [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--no-zygote",
  ],
});
let context;
const startDate = new Date().toISOString().slice(0, 10);
try {
  context = await browser.newContext({ locale: "en-US" });
  await context.route("**/*", (route) => route.abort());
  const page = await context.newPage();
  // Current native markup, field attributes, modal heading/close control and
  // observation-field order. Only record labels/values are invented. This is
  // not an authenticated app or server save fixture.
  await page.setContent(`<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Current native date default check</title></head><body>
    <button id="open" type="button">Add observation</button>
    <dialog aria-labelledby="dialog-title"><div class="dialog-heading"><div><span>IMPACT WORKSPACE</span><h2 id="dialog-title">Add observation</h2></div><button type="button" aria-label="Close dialog">×</button></div>
    <form><label>Indicator<select name="indicator_id" aria-label="Indicator" required><option value="" disabled selected>Choose indicator</option><option value="invented-current-indicator">Invented current indicator</option></select></label>
    <label>Source namespace<input name="source_namespace" required maxlength="64" value="MANUAL"></label>
    <label>Source key<input name="source_key" required maxlength="200" placeholder="e.g. field-visit-2026-001"></label>
    <label>Event date (UTC)<input type="date" name="event_at" required value="${startDate}"></label>
    <label>Recorded value<input name="value" required inputmode="decimal" placeholder="80"></label>
    <div><label>Numerator<input name="numerator" inputmode="decimal" placeholder="8"></label><label>Denominator<input name="denominator" inputmode="decimal" placeholder="10"></label></div>
    <label>Dimension codes (optional)<input name="dimension_values" maxlength="500" placeholder="sex=F; service=A|B"></label><button type="button">Save draft</button></form></dialog></body></html>`);
  await page.evaluate(() =>
    document
      .querySelector("#open")
      .addEventListener("click", () =>
        document.querySelector("dialog").showModal(),
      ),
  );
  async function focus() {
    return page.evaluate(() => ({
      tag: document.activeElement.tagName,
      name: document.activeElement.getAttribute("name"),
      label: document.activeElement.getAttribute("aria-label"),
      type: document.activeElement.getAttribute("type"),
    }));
  }
  async function tabTo(field) {
    for (let i = 0; i < 20; i++) {
      focusTrail.push(await focus());
      if (await field.evaluate((element) => element === document.activeElement))
        return;
      await page.keyboard.press("Tab");
    }
    throw Error("Current native field not reachable through actual tab order");
  }
  await page.keyboard.press("Tab");
  await page.keyboard.press("Enter");
  assert.equal((await focus()).label, "Close dialog");
  const indicator = page.getByLabel("Indicator", { exact: true });
  await tabTo(indicator);
  await helpers.selectWithKeyboard(page, indicator, "Indicator");
  const sourceKey = page.getByLabel("Source key", { exact: true });
  await tabTo(sourceKey);
  await page.keyboard.type("private-current-default-date");
  assert.equal(
    await page.getByLabel("Source namespace", { exact: true }).inputValue(),
    "MANUAL",
  );
  const field = page.getByLabel("Event date (UTC)", { exact: true });
  await tabTo(field);
  assert.equal(
    await field.inputValue(),
    startDate,
    "The untouched initial date must be the actual current UTC ISO default",
  );
  await helpers.typeDateWithKeyboard(page, field, "Event date (UTC)");
  assert.equal(await field.inputValue(), "2026-08-15");
  assert.equal(await sourceKey.inputValue(), "private-current-default-date");
  assert.equal(await indicator.inputValue(), "invented-current-indicator");
  assert(focusTrail.some((item) => item.name === "source_namespace"));
  assert(focusTrail.some((item) => item.name === "source_key"));
  assert(focusTrail.some((item) => item.name === "event_at"));
  results.push({
    name: "Exact unchanged proposed helper overwrites actual current ISO default using current modal and observation tab order with keyboard only",
    status: "passed",
    start_date: startDate,
    final_date: "2026-08-15",
  });
  assert.equal(digest(candidate), candidateSha);
  assert.equal(digest(root + "/apps/web/src/main.tsx"), sourceSha);
} catch (error) {
  results.push({
    name: "Current default-date native check",
    status: "failed",
    message: String(error),
  });
  process.exitCode = 1;
  console.error(error);
} finally {
  await context?.close();
  const report = {
    recorded_at: new Date().toISOString(),
    scope:
      "Private exact proposed helper with current-shaped actual native markup/tab order and dynamic current UTC ISO default; no application/API/save/reviewer qualification",
    browser_version: browser.version(),
    platform: process.platform,
    candidate_sha256: candidateSha,
    main_tsx_sha256: sourceSha,
    sources_unchanged:
      digest(candidate) === candidateSha &&
      digest(root + "/apps/web/src/main.tsx") === sourceSha,
    results,
    focus_trail: focusTrail,
    keyboard_widget_observations: observations,
    actual_full_mode: "NOT_RUN",
    preserved_previous_five: "previous-five-results/native-helper-tests.json",
  };
  writeFileSync(
    folder + "/current-default-date-tests.json",
    JSON.stringify(report, null, 2) + "\n",
  );
  await browser.close();
  console.log(
    JSON.stringify({
      passed: results.filter((row) => row.status === "passed").length,
      failed: results.filter((row) => row.status === "failed").length,
      candidate_sha256: candidateSha,
      start_date: startDate,
    }),
  );
}
