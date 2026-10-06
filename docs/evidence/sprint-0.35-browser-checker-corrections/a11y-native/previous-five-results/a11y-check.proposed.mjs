// Accessibility qualification (VF-UX-001, bounded subset): axe-core scans of every workspace
// area at the WCAG 2.0/2.1/2.2 A and AA rule tags, and a keyboard-only walk-through of one core
// flow (submit an observation, then an independent review). Chromium only; no screen reader, no
// zoom or reflow at 400 %, no manual audit — see docs/current/ACCESSIBILITY-STATEMENT.md.
import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py a11y-browser");
const tenant = JSON.parse(
  await fs.readFile(
    path.join(root, "specification/fixtures/api-fixture.json"),
    "utf8",
  ),
).tenant_a;
const passwords = JSON.parse(
  await fs.readFile(path.join(local, "passwords.json"), "utf8"),
);
const axePath = require.resolve("axe-core/axe.min.js");
const axeSource = await fs.readFile(axePath, "utf8");
const axeVersion = JSON.parse(
  await fs.readFile(path.join(path.dirname(axePath), "package.json"), "utf8"),
).version;
// Rules are selected by tag; a violation fails the group when its impact is serious or critical
// and it carries a WCAG tag. Best-practice findings are recorded as advisory only.
const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
const FAILING_IMPACTS = ["serious", "critical"];
// Accepted exceptions: a failing violation is accepted only when its rule and page match and
// every node's target matches the selector pattern. Each carries its justification.
const EXCEPTIONS = [];
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
  pages = [],
  errors = [];
async function test(name, fn) {
  try {
    await fn();
    results.push({ name, status: "passed" });
    console.log("PASS " + name);
  } catch (e) {
    results.push({ name, status: "failed", message: e.message });
    for (const c of browser.contexts())
      for (const pg of c.pages())
        await pg
          .screenshot({
            path: path.join(root, "docs/evidence/a11y-browser-failure.png"),
            fullPage: true,
          })
          .catch(() => {});
    console.error("FAIL " + name + ": " + e.message);
    process.exitCode = 1;
  }
}
async function user(name, viewport = { width: 1440, height: 1000 }) {
  const context = await browser.newContext({ viewport, locale: "en-US" });
  const p = await context.newPage();
  p.setDefaultTimeout(15000);
  p.on("pageerror", (e) => errors.push(e.message));
  await p.goto(base);
  if (name) {
    await p.getByLabel("Username", { exact: true }).fill(name);
    await p.getByLabel("Password", { exact: true }).fill(passwords[name]);
    await p.getByRole("button", { name: "Sign in →", exact: true }).click();
    await p.locator("main h1").first().waitFor();
  }
  return p;
}
async function settle(p) {
  await p.waitForLoadState("networkidle").catch(() => {});
  await p.waitForTimeout(250);
}
function excepted(page, violation) {
  return EXCEPTIONS.find(
    (x) =>
      x.rule === violation.id &&
      (x.pages === "*" || x.pages.includes(page)) &&
      violation.nodes.every((n) =>
        new RegExp(x.target).test(n.target.join(" ")),
      ),
  );
}
// Scan the current document with axe-core. page.evaluate goes through the DevTools protocol, so
// the injected engine is not subject to the application's Content-Security-Policy.
async function scan(p, name, actor) {
  await settle(p);
  if (!(await p.evaluate(() => Boolean(window.axe))))
    await p.evaluate(axeSource);
  const raw = await p.evaluate(
    (tags) =>
      window.axe.run(document, {
        runOnly: { type: "tag", values: [...tags, "best-practice"] },
        resultTypes: ["violations", "incomplete"],
      }),
    WCAG_TAGS,
  );
  const shape = (v) => ({
    rule: v.id,
    impact: v.impact,
    tags: v.tags.filter((t) => t.startsWith("wcag")),
    help: v.help,
    nodes: v.nodes.map((n) => ({
      target: n.target.join(" "),
      summary: (n.failureSummary || "").split("\n").slice(0, 3).join(" "),
    })),
  });
  const wcag = raw.violations.filter((v) =>
    v.tags.some((t) => WCAG_TAGS.includes(t)),
  );
  const failing = [],
    accepted = [],
    other = [];
  for (const v of wcag) {
    if (!FAILING_IMPACTS.includes(v.impact)) other.push(shape(v));
    else {
      const x = excepted(name, v);
      if (x) accepted.push({ ...shape(v), exception: x.id });
      else failing.push(shape(v));
    }
  }
  const advisory = raw.violations
    .filter((v) => !v.tags.some((t) => WCAG_TAGS.includes(t)))
    .map(shape);
  pages.push({
    page: name,
    actor,
    url: new URL(p.url()).pathname,
    viewport: p.viewportSize(),
    failing,
    accepted,
    minor_wcag: other,
    advisory_best_practice: advisory,
    // axe could not decide these (for example text over a gradient or an overlapping
    // element); they are not passes and need a manual check.
    needs_manual_review: raw.incomplete
      .filter((v) => v.tags.some((t) => WCAG_TAGS.includes(t)))
      .map((v) => ({
        rule: v.id,
        impact: v.impact,
        nodes: v.nodes.length,
        examples: v.nodes.slice(0, 3).map((n) => ({
          target: n.target.join(" "),
          reason: (n.any[0] || n.all[0] || n.none[0] || {}).message || "",
        })),
      })),
  });
  console.log(
    `SCAN ${name}: ${failing.length} failing, ${accepted.length} accepted, ${other.length} minor, ${advisory.length} advisory`,
  );
  for (const v of failing)
    console.log(
      `  ${v.impact} ${v.rule}: ${v.help} :: ${v.nodes
        .slice(0, 4)
        .map((n) => n.target)
        .join(" | ")}`,
    );
  return failing;
}
const button = (p, name) => p.getByRole("button", { name, exact: true });
async function area(p, navName, heading) {
  await button(p, navName).click();
  await p
    .getByRole("heading", { name: heading, exact: true, level: 1 })
    .waitFor();
}
async function closeDialog(p) {
  await button(p, "Close dialog").click();
  await p.getByRole("dialog").waitFor({ state: "detached" });
}
const failures = [];
const slugify = (t) =>
  t
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
// Scan every tab of a role="tablist" (or every button of a navigation used as tabs).
async function eachTab(p, container, prefix, actor) {
  const tabs = container.getByRole(prefix.tabRole || "tab");
  const n = await tabs.count();
  for (let i = 0; i < n; i++) {
    const name = (await tabs.nth(i).innerText()).trim();
    await tabs.nth(i).click();
    await check(p, prefix.slug + "/" + slugify(name), actor);
  }
}
async function check(p, name, actor) {
  const f = await scan(p, name, actor);
  if (f.length) failures.push(name);
}
// The keyboard helpers move focus only with the Tab key and act only with Enter, Space, arrow
// keys and typing; no pointer events are sent.
async function isFocused(locator) {
  return locator
    .evaluate((el) => el === document.activeElement)
    .catch(() => false);
}
const focusTrail = [];
const keyboardWidgetObservations = [];
// Native headless widget gestures vary by platform. Keep every action keyboard
// only and require the exact visible first option rather than assigning a value.
async function selectWithKeyboard(p, field, what) {
  assert(await isFocused(field), what + " must have keyboard focus");
  const option = field.locator("option:not([disabled])").first();
  await option.waitFor({ state: "attached" });
  const expected = await option.getAttribute("value");
  const text = (await option.textContent()).trim();
  assert(expected && text, what + " needs an actual nonempty visible option");
  await p.keyboard.press("ArrowDown");
  let gesture = "ArrowDown";
  if ((await field.inputValue()) === "") {
    await p.keyboard.type(text);
    gesture += " then visible-label keyboard typeahead";
  }
  assert(await isFocused(field), what + " must retain keyboard focus");
  assert.equal(
    await field.inputValue(),
    expected,
    what + " exact option chosen by keyboard",
  );
  keyboardWidgetObservations.push({
    control: what,
    gesture,
    option_label: text,
    selected_value: expected,
  });
}

async function typeDateWithKeyboard(p, field, what) {
  assert(await isFocused(field), what + " must have keyboard focus");
  assert.equal(await field.count(), 1);
  assert.equal(await field.getAttribute("type"), "date");
  assert.equal(await field.getAttribute("name"), "event_at");
  assert(
    await field.evaluate((element) => {
      const selector = 'dialog[open] input[type="date"][name="event_at"]';
      return (
        document.querySelectorAll(selector).length === 1 &&
        element === document.querySelector(selector)
      );
    }),
    "AX selector must bind to the exact labelled date element",
  );
  const locale = await p.evaluate(() => navigator.language);
  assert.match(
    locale,
    /^en(?:-[A-Za-z0-9]+)*$/,
    "English native date parts required; unknown locale refuses",
  );
  const session = await p.context().newCDPSession(p);
  let order;
  try {
    // Read-only AX lookup is qualified to the one actual open-dialog date
    // element. Never infer this order from OS name or navigator.language alone.
    const document = await session.send("DOM.getDocument");
    const selected = await session.send("DOM.querySelector", {
      nodeId: document.root.nodeId,
      selector: 'dialog[open] input[type="date"][name="event_at"]',
    });
    assert(selected.nodeId, "Actual date element must be available");
    const { node } = await session.send("DOM.describeNode", {
      nodeId: selected.nodeId,
    });
    const { nodes } = await session.send("Accessibility.getFullAXTree");
    const target = nodes.find(
      (row) => row.backendDOMNodeId === node.backendNodeId,
    );
    assert(
      target && target.role?.value === "Date",
      "Exact native Date AX node required",
    );
    const indexed = new Map(nodes.map((row) => [row.nodeId, row]));
    const parts = [];
    function walk(row, seen = new Set()) {
      assert(
        row && !seen.has(row.nodeId),
        "Date AX descendants must be complete and acyclic",
      );
      seen.add(row.nodeId);
      if (row.role?.value === "spinbutton") parts.push(row);
      for (const child of row.childIds || []) walk(indexed.get(child), seen);
    }
    walk(target);
    order = parts.map((row) => {
      const name = row.name?.value;
      const part = ["Day", "Month", "Year"].find(
        (value) => name === value || name === value + " " + value,
      );
      assert(part, "Unknown native date part refuses keyboard qualification");
      return part;
    });
    assert.deepEqual(
      [...order].sort(),
      ["Day", "Month", "Year"],
      "Exactly one Day, Month and Year required",
    );
    assert(
      parts[0].properties?.some(
        (property) =>
          property.name === "focused" && property.value?.value === true,
      ),
      "Keyboard must start at the first observed native date part",
    );
    assert.equal(
      parts.filter((row) =>
        row.properties?.some(
          (property) =>
            property.name === "focused" && property.value?.value === true,
        ),
      ).length,
      1,
    );
  } finally {
    await session.detach();
  }
  const digits = { Day: "15", Month: "08", Year: "2026" };
  await p.keyboard.type(order.map((part) => digits[part]).join(""));
  assert(await isFocused(field), what + " must retain keyboard focus");
  assert.equal(
    await field.inputValue(),
    "2026-08-15",
    "Exact native date chosen by keyboard",
  );
  keyboardWidgetObservations.push({
    control: what,
    gesture: "keyboard digits in observed native AX order",
    locale,
    native_part_order: order,
    chosen_date: "2026-08-15",
  });
}
async function tabTo(p, locator, what, limit = 160) {
  await locator.waitFor();
  for (let i = 0; i < limit; i++) {
    if (await isFocused(locator)) {
      // The outline is drawn outside the control (offset 3 px), so its contrast is measured
      // against the first opaque background behind the control (WCAG 1.4.11, 3:1).
      const visible = await p.evaluate(() => {
        const el = document.activeElement;
        const s = getComputedStyle(el);
        const rgb = (c) => (c.match(/[\d.]+/g) || []).map(Number);
        const lum = ([r, g, b]) => {
          const f = (v) => {
            v /= 255;
            return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
          };
          return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
        };
        let node = el.parentElement,
          behind = "rgb(255, 255, 255)";
        while (node) {
          const bg = getComputedStyle(node).backgroundColor;
          const parts = rgb(bg);
          if (parts.length >= 3 && (parts.length < 4 || parts[3] > 0.5)) {
            behind = bg;
            break;
          }
          node = node.parentElement;
        }
        const a = lum(rgb(s.outlineColor)),
          b = lum(rgb(behind));
        const contrast = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
        const outline =
          s.outlineStyle !== "none" && parseFloat(s.outlineWidth) >= 2;
        return {
          visible: outline,
          matches: el.matches(":focus-visible"),
          outline: s.outlineStyle + " " + s.outlineWidth + " " + s.outlineColor,
          behind,
          contrast: Math.round(contrast * 100) / 100,
        };
      });
      focusTrail.push({ control: what, tab_presses: i, ...visible });
      assert(visible.visible, "No visible focus indicator on " + what);
      assert(
        visible.contrast >= 3,
        "Focus indicator contrast " + visible.contrast + ":1 on " + what,
      );
      return;
    }
    await p.keyboard.press("Tab");
  }
  throw Error("Not reachable with Tab: " + what);
}
async function insideDialog(p) {
  return p.evaluate(() =>
    Boolean(document.activeElement?.closest("dialog[open]")),
  );
}
// While a modal dialog is open no element outside it may receive focus. Tabbing past the last
// control moves focus to the browser itself (document.body is reported), never to the page
// behind the dialog, and the next Tab returns into the dialog; that is not a keyboard trap.
async function focusOutsideDialog(p) {
  return p.evaluate(() => {
    const el = document.activeElement;
    if (!el || el === document.body || el === document.documentElement)
      return null;
    return el.closest("dialog[open]") ? null : el.outerHTML.slice(0, 120);
  });
}
let observationSource;
try {
  await test("Scan: sign-in page", async () => {
    const p = await user(null);
    await p.getByRole("heading", { name: "Welcome back" }).waitFor();
    await check(p, "sign-in", "anonymous");
    await p.context().close();
  });
  await test("Scan: every author workspace area, tab and record dialog", async () => {
    const p = await user("author");
    await check(p, "portfolio", "author");
    await p.locator("tbody .record-link").first().click();
    await p.getByRole("dialog").waitFor();
    await check(p, "portfolio-record-dialog", "author");
    await closeDialog(p);
    await p.getByRole("button", { name: "New programme" }).click();
    await p.getByRole("dialog").waitFor();
    await check(p, "new-programme-dialog", "author");
    await closeDialog(p);
    await area(p, "Measurement", "Measurement");
    await check(p, "measurement", "author");
    await p.locator("tbody .record-link").first().click();
    await p.getByRole("dialog").waitFor();
    await check(p, "observation-record-dialog-evidence", "author");
    await closeDialog(p);
    await p.getByRole("button", { name: "Add observation" }).click();
    await p.getByRole("dialog").waitFor();
    await check(p, "add-observation-dialog", "author");
    await closeDialog(p);
    await area(p, "Measurement setup", "Measurement setup");
    await eachTab(
      p,
      p.getByRole("tablist", { name: "Measurement configuration" }),
      { slug: "measurement-setup" },
      "author",
    );
    await area(p, "Results framework", "Results framework");
    await eachTab(
      p,
      p.getByRole("tablist", { name: "Results planning" }),
      { slug: "results-framework" },
      "author",
    );
    for (const [nav, heading, name] of [
      ["Dashboards", "Dashboards", "dashboards"],
      ["Forms", "Forms", "forms"],
      ["Imports", "Imports", "imports"],
      ["Change requests", "Change requests", "change-requests"],
      ["Period close", "Period close", "period-close"],
      ["My work", "My work", "my-work"],
      ["Results", "Results & learning", "results"],
      ["Reports", "Reports", "reports"],
      ["My account", "My account", "my-account"],
    ])
      await area(p, nav, heading).then(() => check(p, name, "author"));
    await area(p, "Results", "Results & learning");
    await settle(p);
    if (await p.locator("tbody .record-link").count()) {
      await p.locator("tbody .record-link").first().click();
      await p.getByRole("dialog").waitFor();
      await check(p, "result-record-dialog", "author");
      await closeDialog(p);
    }
    await area(p, "Reports", "Reports");
    await settle(p);
    const approved = p.locator("tbody tr").filter({ hasText: "Approved" });
    if (await approved.count()) {
      await approved.first().locator(".record-link").click();
      await p.getByRole("dialog").waitFor();
      await check(p, "report-record-dialog-exports", "author");
      await closeDialog(p);
    }
    await p.context().close();
  });
  await test("Scan: review queue, people and access, workspace settings, tenant lifecycle and workers", async () => {
    const r = await user("reviewer");
    await area(r, "Review queue", "Review queue");
    await check(r, "review-queue", "reviewer");
    await r.context().close();
    const a = await user("admin");
    await area(a, "People & access", "People & access");
    await eachTab(
      a,
      a.getByRole("tablist", { name: "Access administration" }),
      { slug: "people-and-access" },
      "admin",
    );
    await area(a, "Workspace settings", "Workspace settings");
    await eachTab(
      a,
      a.getByRole("navigation", { name: "Workspace administration" }),
      { slug: "workspace-settings", tabRole: "button" },
      "admin",
    );
    await button(a, "Tenant lifecycle").click();
    await a
      .getByRole("heading", { name: "Tenant lifecycle", exact: true })
      .waitFor();
    await a.getByRole("heading", { name: "Workers", exact: true }).waitFor();
    await check(a, "tenant-lifecycle-and-workers", "admin");
    for (const [name, slug] of [
      ["Recovery contacts", "recovery-contacts"],
      ["Initial access", "initial-access"],
      ["Authority renewal", "authority-renewal"],
    ]) {
      await button(a, name).click();
      await a.getByRole("heading", { name, exact: true }).waitFor();
      await check(a, slug, "admin");
      await button(a, "Back to tenant lifecycle").click();
      await a
        .getByRole("heading", { name: "Tenant lifecycle", exact: true })
        .waitFor();
    }
    await a.context().close();
  });
  await test("Keyboard only: arrow keys move between tabs and Enter selects one", async () => {
    const p = await user("author");
    await tabTo(
      p,
      button(p, "Measurement setup"),
      "Measurement setup navigation",
    );
    await p.keyboard.press("Enter");
    const list = p.getByRole("tablist", { name: "Measurement configuration" });
    const tabs = list.getByRole("tab");
    await tabTo(p, tabs.first(), "First configuration tab");
    await p.keyboard.press("ArrowRight");
    assert(await isFocused(tabs.nth(1)), "ArrowRight moves to the next tab");
    await p.keyboard.press("End");
    assert(await isFocused(tabs.last()), "End moves to the last tab");
    await p.keyboard.press("ArrowRight");
    assert(await isFocused(tabs.first()), "ArrowRight wraps to the first tab");
    await p.keyboard.press("ArrowLeft");
    await p.keyboard.press("Enter");
    assert.equal(await tabs.last().getAttribute("aria-selected"), "true");
    // The skip link is the first focusable element and moves focus to the main content.
    await p.reload();
    await p.locator("main h1").first().waitFor();
    await p.keyboard.press("Tab");
    const skip = p.getByRole("link", {
      name: "Skip to main content",
      exact: true,
    });
    assert(await isFocused(skip), "Skip link is the first Tab stop");
    assert(await skip.isVisible(), "Skip link is visible while focused");
    await p.keyboard.press("Enter");
    assert(
      await p.evaluate(() => document.activeElement?.id === "main-content"),
      "Skip link moves focus to the main content",
    );
    await p.context().close();
  });
  await test("Scan: portfolio at 390 px width", async () => {
    const p = await user("author", { width: 390, height: 844 });
    await check(p, "portfolio-390px", "author");
    await p.context().close();
  });
  await test("Keyboard only: author captures and submits an observation", async () => {
    const p = await user("author");
    observationSource = "a11y-keyboard-" + Date.now();
    await tabTo(p, button(p, "Measurement"), "Measurement navigation");
    await p.keyboard.press("Enter");
    await p
      .getByRole("heading", { name: "Measurement", exact: true, level: 1 })
      .waitFor();
    const add = p.getByRole("button", { name: "Add observation" });
    await tabTo(p, add, "Add observation");
    await p.keyboard.press("Enter");
    const dialog = p.getByRole("dialog");
    await dialog.waitFor();
    assert(await insideDialog(p), "Focus did not move into the dialog");
    // Focus stays inside the modal dialog however far the user tabs.
    let wrapped = false;
    for (let i = 0; i < 40; i++) {
      await p.keyboard.press("Tab");
      const outside = await focusOutsideDialog(p);
      assert.equal(
        outside,
        null,
        "Focus reached the page behind the dialog at Tab " + (i + 1),
      );
      if (!(await insideDialog(p))) wrapped = true;
    }
    assert(wrapped, "Tabbing cycled past the last dialog control");
    if (!(await insideDialog(p))) await p.keyboard.press("Tab");
    assert(await insideDialog(p), "Tab returns focus into the dialog");
    const field = (name) => dialog.getByLabel(name, { exact: true });
    await field("Indicator")
      .locator("option")
      .nth(1)
      .waitFor({ state: "attached" });
    await tabTo(p, field("Indicator"), "Indicator");
    await selectWithKeyboard(p, field("Indicator"), "Indicator");
    assert.notEqual(
      await field("Indicator").inputValue(),
      "",
      "Indicator chosen by keyboard",
    );
    await tabTo(p, field("Source key"), "Source key");
    await p.keyboard.type(observationSource);
    await tabTo(p, field("Event date (UTC)"), "Event date (UTC)");
    await typeDateWithKeyboard(
      p,
      field("Event date (UTC)"),
      "Event date (UTC)",
    );
    assert.equal(await field("Event date (UTC)").inputValue(), "2026-08-15");
    await tabTo(p, field("Recorded value"), "Recorded value");
    await p.keyboard.type("80");
    await tabTo(p, field("Numerator"), "Numerator");
    await p.keyboard.type("8");
    await tabTo(p, field("Denominator"), "Denominator");
    await p.keyboard.type("10");
    await tabTo(
      p,
      dialog.getByRole("button", { name: "Save draft", exact: true }),
      "Save draft",
    );
    await p.keyboard.press("Enter");
    await dialog.waitFor({ state: "detached" });
    await p
      .getByRole("status")
      .filter({ hasText: "Saved successfully" })
      .waitFor();
    const record = button(p, observationSource);
    await tabTo(p, record, "Observation record");
    await p.keyboard.press("Enter");
    await dialog.waitFor();
    await tabTo(
      p,
      dialog.getByRole("button", { name: "Submit for review", exact: true }),
      "Submit for review (inspect)",
    );
    await p.keyboard.press("Enter");
    await dialog.getByLabel("Review template", { exact: true }).waitFor();
    const template = dialog.getByLabel("Review template", { exact: true });
    await template.locator("option").nth(1).waitFor({ state: "attached" });
    await tabTo(p, template, "Review template");
    await selectWithKeyboard(p, template, "Review template");
    assert.notEqual(
      await template.inputValue(),
      "",
      "Review template chosen by keyboard",
    );
    await tabTo(
      p,
      dialog.getByRole("button", { name: "Submit for review", exact: true }),
      "Submit for review (confirm)",
    );
    await p.keyboard.press("Enter");
    await dialog.waitFor({ state: "detached" });
    await p
      .getByRole("status")
      .filter({ hasText: "Saved successfully" })
      .waitFor();
    await settle(p);
    // Escape closes a dialog and returns focus to the control that opened it.
    await tabTo(p, record, "Observation record (again)", 400);
    await p.keyboard.press("Enter");
    await dialog.waitFor();
    await p.keyboard.press("Escape");
    await dialog.waitFor({ state: "detached" });
    assert(
      await isFocused(record),
      "Focus returned to the opening control after Escape",
    );
    await p.context().close();
  });
  await test("Keyboard only: independent reviewer approves the submitted observation", async () => {
    const p = await user("reviewer");
    await tabTo(p, button(p, "Review queue"), "Review queue navigation");
    await p.keyboard.press("Enter");
    await p
      .getByRole("heading", { name: "Review queue", exact: true, level: 1 })
      .waitFor();
    await settle(p);
    const dialog = p.getByRole("dialog");
    // The queue row is labelled with the first eight characters of the candidate's object id;
    // the reviewer narrows the loaded queue to it by typing into the search field.
    const observations = await fetch(
      base + "/v1/tenants/" + tenant + "/observations?limit=50",
      {
        headers: { Authorization: "Bearer " + process.env.IMPACT_TOKEN_AUTHOR },
      },
    ).then((r) => r.json());
    const candidate = observations.items.find(
      (o) => o.data.source_key === observationSource,
    );
    assert(candidate, "Submitted observation readable through the API");
    const search = p.getByLabel("Search loaded records", { exact: true });
    await tabTo(p, search, "Search loaded records");
    await p.keyboard.type(candidate.object_id.slice(0, 8));
    const row = p
      .locator("tbody .record-link")
      .filter({ hasText: "Review · " + candidate.object_id.slice(0, 8) });
    await tabTo(p, row.first(), "Review queue row");
    await p.keyboard.press("Enter");
    await dialog.waitFor();
    await tabTo(
      p,
      dialog.getByRole("button", { name: "Review submission", exact: true }),
      "Review submission",
    );
    await p.keyboard.press("Enter");
    await dialog.getByText(observationSource, { exact: true }).waitFor();
    const found = true;
    assert(found, "Submitted observation found in the review queue");
    await check(p, "review-decision-dialog", "reviewer");
    await tabTo(
      p,
      dialog.getByLabel("Decision reason", { exact: true }),
      "Decision reason",
    );
    await p.keyboard.type("Independent keyboard-only accessibility review");
    await tabTo(
      p,
      dialog.getByRole("button", { name: "Approve", exact: true }),
      "Approve",
    );
    await p.keyboard.press("Enter");
    await p
      .getByRole("status")
      .filter({ hasText: "Saved successfully" })
      .waitFor();
    await p.context().close();
  });
  await test("No scanned page has an unaccepted serious or critical WCAG violation", async () => {
    assert.deepEqual(failures, []);
    assert.deepEqual(errors, []);
  });
} catch (e) {
  results.push({
    name: "Accessibility browser run",
    status: "failed",
    message: e.message,
  });
  console.error(e.message);
  process.exitCode = 1;
} finally {
  await fs.writeFile(
    path.join(root, "docs/evidence/a11y-browser-tests.json"),
    JSON.stringify(
      {
        engine: "Chromium " + browser.version(),
        browser_version: browser.version(),
        platform: process.platform,
        axe_core: axeVersion,
        rule_tags: WCAG_TAGS,
        failing_impacts: FAILING_IMPACTS,
        scope_note:
          "Automated axe-core scans and one keyboard-only flow. Not a WCAG 2.2 AA conformance claim: no screen reader, zoom/reflow at 400 %, other browsers or manual audit.",
        results,
        pages,
        keyboard_focus_trail: focusTrail,
        keyboard_widget_observations: keyboardWidgetObservations,
        accepted_exceptions: EXCEPTIONS,
        uncaughtErrors: errors,
      },
      null,
      2,
    ),
  );
  await browser.close();
}
