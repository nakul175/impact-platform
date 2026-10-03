import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";

const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL;
if (!local || !base) throw Error("Use scripts/run.py reporting-browser");
const passwords = JSON.parse(
    await fs.readFile(path.join(local, "passwords.json"), "utf8"),
  ),
  fixture = JSON.parse(
    await fs.readFile(
      path.join(root, "specification/fixtures/api-fixture.json"),
      "utf8",
    ),
  ),
  browserDir = path.join(root, ".local/browser"),
  browser = await chromium.launch({
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
  }),
  results = [],
  errors = [];
let page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
const pages = {};
function watch(candidate) {
  candidate.setDefaultTimeout(15000);
  candidate.on("pageerror", (error) => errors.push(error.message));
}
watch(page);
const button = (name) => page.getByRole("button", { name, exact: true });
const label = (name) => page.getByLabel(name, { exact: true });
async function test(name, action) {
  await action();
  results.push({ name, status: "passed" });
  console.log("PASS " + name);
}
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
    await page.goto(base);
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
async function receipt(click, suffix) {
  const pending = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" && response.url().endsWith(suffix),
  );
  await click();
  const response = await pending;
  assert(response.ok(), await response.text());
  return response.json();
}

const heading = "Snapshot report " + Date.now();
let report, workflow, disclosureWorkflow, publication;
try {
  await page.goto(base);
  await login("author");
  await test("Period governance workspace shows programme-scoped status", async () => {
    await button("Period close").click();
    await page
      .getByRole("heading", { name: "Reporting periods", exact: true })
      .waitFor();
    await page
      .getByRole("columnheader", { name: "Programme" })
      .first()
      .waitFor();
    await page.screenshot({
      path: path.join(root, "docs/evidence/period-close.png"),
    });
    // v0.27: the close dialog names programmes ("Title (CODE)") and the review policy by what
    // it is, never by a bare code or identifier prefix.
    await button("Preview period close").click();
    const dialog = page.getByRole("dialog");
    await dialog.waitFor();
    // The panel loads its records after the heading renders: wait for the first real option.
    const programmeOptions = dialog
      .getByLabel("Programme", { exact: true })
      .locator("option");
    await programmeOptions.nth(1).waitFor({ state: "attached" });
    const programmes = await programmeOptions.allInnerTexts();
    assert.ok(programmes.length > 1, "an active programme is offered");
    for (const option of programmes.slice(1))
      assert.match(option, /^.+ \(.+\)$/, option);
    const policyOptions = dialog
      .getByLabel("Review policy", { exact: true })
      .locator("option");
    await policyOptions.nth(1).waitFor({ state: "attached" });
    const policies = await policyOptions.allInnerTexts();
    assert.ok(policies.length > 1, "a review policy is offered");
    for (const option of policies.slice(1))
      assert.doesNotMatch(option, /^[0-9a-f]{8}$/, option);
    await page
      .getByRole("button", { name: "Close dialog", exact: true })
      .click();
    await dialog.waitFor({ state: "detached" });
  });
  await test("Author drafts a report from a locked snapshot", async () => {
    await button("Reports").click();
    await page
      .getByRole("button", { name: "Draft report", exact: false })
      .click();
    await label("Approved report template").selectOption({ index: 1 });
    await label("Locked snapshot").selectOption({ index: 1 });
    await label("Section heading").fill(heading);
    await label("Narrative").fill(
      "A frozen, independently reviewed quarterly result.",
    );
    await label("Result to reference").selectOption({ index: 1 });
    report = await receipt(() => button("Save draft").click(), "/reports");
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await button(heading).waitFor();
  });
  await test("Author submits the exact package for independent review", async () => {
    await button(heading).click();
    await button("Submit frozen package for review").click();
    await label("Review template").selectOption({ index: 1 });
    workflow = await receipt(
      () => button("Submit for review").click(),
      "/actions/submit",
    );
    await page.getByRole("dialog").waitFor({ state: "hidden" });
  });
  await test("Independent reviewer approves the frozen package", async () => {
    await switchUser("reviewer");
    await button("Review queue").click();
    await page
      .locator("tr")
      .filter({ hasText: workflow.object_id.slice(0, 8) })
      .getByRole("button")
      .first()
      .click();
    await button("Review submission").click();
    await page.locator("pre").filter({ hasText: heading }).waitFor();
    await label("Decision reason").fill(
      "Checked the snapshot, template and exact numeric binding.",
    );
    await button("Approve").click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
  });
  await test("Approved export renders pinned context and value", async () => {
    await button("Reports").click();
    await button(heading).click();
    const popup = page.waitForEvent("popup");
    await page.getByRole("link", { name: "Open approved export" }).click();
    const exported = await popup;
    await exported
      .getByRole("heading", { name: "Quarterly results" })
      .waitFor();
    await exported.getByText("46.36 PERCENT", { exact: false }).waitFor();
    assert((await exported.content()).includes(report.object_id));
    await exported.screenshot({
      path: path.join(root, "docs/evidence/reporting-package.png"),
      fullPage: true,
    });
    await exported.close();
  });
  await test("Author requests recipient-bounded disclosure review", async () => {
    await switchUser("author");
    await button("Reports").click();
    await button(heading).click();
    await button("Request controlled publication").click();
    await label("Publication recipient").selectOption(fixture.member_partner);
    await label("Publication purpose").selectOption("PARTNER_REPORTING");
    await label("Disclosure review template").selectOption({ index: 1 });
    disclosureWorkflow = await receipt(
      () => button("Request disclosure review").click(),
      "/disclosure-requests",
    );
    await page.getByRole("dialog").waitFor({ state: "hidden" });
  });
  await test("Independent publisher approves and freezes the disclosure", async () => {
    await switchUser("reviewer");
    await button("Review queue").click();
    await page
      .locator("tr")
      .filter({ hasText: disclosureWorkflow.object_id.slice(0, 8) })
      .getByRole("button")
      .first()
      .click();
    await button("Review submission").click();
    await page.getByText("PARTNER_REPORTING", { exact: false }).waitFor();
    await label("Decision reason").fill(
      "Verified recipient, purpose, expiry and download rights.",
    );
    await button("Approve").click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await button("Reports").click();
    await button(heading).click();
    await button("Publish approved disclosure").click();
    await label("Approved disclosure").selectOption({ index: 1 });
    await page.screenshot({
      path: path.join(root, "docs/evidence/publication-preview.png"),
    });
    publication = await receipt(
      () => button("Publish controlled artifact").click(),
      "/actions/publish",
    );
    await page.getByRole("dialog").waitFor({ state: "hidden" });
  });
  await test("Named recipient can view HTML and download exact CSV", async () => {
    await switchUser("partner");
    const artifactBase =
      base +
      "/v1/tenants/" +
      fixture.tenant_a +
      "/publications/" +
      publication.object_id;
    const viewed = await page.goto(artifactBase + "/view");
    assert.equal(viewed.status(), 200);
    await page.getByRole("heading", { name: "Quarterly results" }).waitFor();
    await page.getByText("46.36 PERCENT", { exact: false }).first().waitFor();
    assert.equal(
      await page
        .locator("body")
        .evaluate((node) => getComputedStyle(node).maxWidth),
      "850px",
    );
    await page.screenshot({
      path: path.join(root, "docs/evidence/controlled-publication.png"),
      fullPage: true,
    });
    const csv = await page
      .context()
      .request.get(artifactBase + "/download.csv");
    assert(csv.ok());
    assert((await csv.text()).includes("46.36,PERCENT"));
  });
  await test("Withdrawal closes recipient access without erasing history", async () => {
    await switchUser("reviewer");
    await button("Reports").click();
    await button(heading).click();
    await button("Withdraw publications").click();
    await label("Withdrawal reason").fill(
      "Superseded during controlled publication qualification.",
    );
    await receipt(
      () => button("Withdraw controlled publications").click(),
      "/actions/withdraw",
    );
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    page = pages.partner;
    const unavailable = await page.goto(
      base +
        "/v1/tenants/" +
        fixture.tenant_a +
        "/publications/" +
        publication.object_id +
        "/view",
    );
    assert.equal(unavailable.status(), 404);
  });
  await test("Reporting workspace remains bounded on mobile", async () => {
    await switchUser("reviewer");
    await page.setViewportSize({ width: 390, height: 844 });
    await page.keyboard.press("Escape");
    await button("Reports").click();
    await button(heading).waitFor();
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    );
    assert.deepEqual(errors, []);
  });
} catch (error) {
  results.push({
    name: "Reporting browser run",
    status: "failed",
    message: error.message,
  });
  await page.screenshot({
    path: path.join(root, "docs/evidence/reporting-browser-failure.png"),
    fullPage: true,
  });
  console.error(error.message);
  process.exitCode = 1;
} finally {
  await fs.writeFile(
    path.join(root, "docs/evidence/reporting-browser-tests.json"),
    JSON.stringify(
      { engine: "Chromium 153", results, uncaughtErrors: errors },
      null,
      2,
    ),
  );
  await browser.close();
}
