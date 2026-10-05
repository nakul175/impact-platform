import { chromium } from "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/tools/browser/node_modules/playwright-core/index.mjs";
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import assert from "node:assert/strict";
const directory = "/private/tmp/tola-ai-portability-draft";
const sourceFiles = [
  "AIPlanPortability.tsx",
  "export-adapter.ts",
  "ui-fixture.tsx",
  "ui-fixture.css",
  "ui-fixture-check.mjs",
];
const hashes = () =>
  Object.fromEntries(
    sourceFiles.map((file) => [
      file,
      createHash("sha256")
        .update(readFileSync(`${directory}/${file}`))
        .digest("hex"),
    ]),
  );
const sources = hashes(),
  results = [],
  errors = [],
  external = [],
  downloads = [],
  scans = [],
  screenshots = [];
const browser = await chromium.launch({
  executablePath:
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
  args: ["--no-sandbox"],
});
const context = await browser.newContext({ acceptDownloads: true });
await context.route("**/*", (route) => {
  if (new URL(route.request().url()).origin !== "http://127.0.0.1:8190") {
    external.push(route.request().url());
    return route.abort();
  }
  return route.continue();
});
const page = await context.newPage();
page.setDefaultTimeout(8000);
page.on("pageerror", (error) => errors.push(error.message));
page.on("download", (download) => downloads.push(download));
const f = (method, value) =>
  page.evaluate(({ method, value }) => window.fixture[method](value), {
    method,
    value,
  });
async function reset() {
  await page.goto("http://127.0.0.1:8190");
  await page
    .getByRole("heading", { name: "Internal copy of your saved plan" })
    .waitFor();
}
const open = () =>
  page.getByRole("button", { name: "Prepare an internal saved copy" }).click();
const issue = () =>
  page
    .getByRole("button", { name: "Confirm and issue internal JSON copy" })
    .click();
const download = () =>
  page.getByRole("button", { name: "Download issued copy" }).click();
const retry = () =>
  page.getByRole("button", { name: "Retry previous copy request" }).click();
async function prepared() {
  await reset();
  await open();
  await page.getByRole("checkbox").check();
  await issue();
  await page.getByLabel("Verified issued copy").waitFor();
}
async function check(name, work) {
  await work();
  results.push({
    name,
    status: "passed",
    scope:
      "Temporary component and in-memory request-function fixture only; no actual API/backend authorisation evidence",
  });
  console.log(`PASS ${name}`);
}
try {
  await check(
    "Lazy options and separate export hint do not call the request fixture",
    async () => {
      await reset();
      assert.equal((await f("calls")).length, 0);
      await f("patch", { canExport: false });
      await page
        .getByText(
          "An internal copy is unavailable with your current access.",
          { exact: true },
        )
        .waitFor();
      assert.equal((await f("calls")).length, 0);
      assert.equal(
        await page
          .getByRole("button", { name: "Prepare an internal saved copy" })
          .isDisabled(),
        true,
      );
    },
  );
  await check(
    "Bounded authorised history selection is deliberate and never saves the parent draft",
    async () => {
      await reset();
      await open();
      await page
        .getByRole("button", { name: "Load authorised saved revisions" })
        .click();
      await page
        .getByRole("option", { name: /Revision 1/ })
        .waitFor({ state: "attached" });
      await page
        .getByLabel("Copy saved revision")
        .selectOption("77777777-7777-4777-8777-777777777777");
      assert.equal(
        (await f("calls")).filter((x) => x.method === "POST").length,
        0,
      );
      assert.equal(downloads.length, 0);
      await page.getByRole("checkbox").check();
      await issue();
      await page.getByLabel("Verified issued copy").waitFor();
      const calls = (await f("calls")).filter((x) => x.method === "POST");
      assert.equal(calls.length, 1);
      assert.match(
        calls[0].path,
        /77777777-7777-4777-8777-777777777777\/exports$/,
      );
      assert.equal(downloads.length, 0);
    },
  );
  await check(
    "Explicit download freshly replays the exact operation and preserves UTF-8 content byte-for-byte",
    async () => {
      const issued = (await f("issued"))[0],
        original = (await f("calls")).find((x) => x.method === "POST");
      const event = page.waitForEvent("download");
      await download();
      const file = await event;
      const path = `${directory}/synthetic-download.json`;
      await file.saveAs(path);
      const bytes = readFileSync(path);
      assert.equal(bytes.toString("utf8"), issued.content);
      assert.equal(
        createHash("sha256").update(bytes).digest("hex"),
        issued.manifest.content_sha256,
      );
      const posts = (await f("calls")).filter((x) => x.method === "POST");
      assert.equal(posts.at(-1).body, original.body);
      assert.equal(posts.length, 2);
    },
  );
  await check(
    "Lost prepare response keeps one exact issuance command and parent mutual-write lock",
    async () => {
      await reset();
      await open();
      await page.getByRole("checkbox").check();
      await f("mode", "lost");
      await issue();
      await page.getByRole("alert").waitFor();
      assert.equal(await f("pending"), true);
      const original = (await f("calls")).find((x) => x.method === "POST");
      await retry();
      await page.getByLabel("Verified issued copy").waitFor();
      assert.equal(
        (await f("calls")).filter((x) => x.method === "POST").at(-1).body,
        original.body,
      );
      assert.equal((await f("issued")).length, 1);
      assert.equal(await f("pending"), false);
    },
  );
  await check(
    "Lost download response retains the verified manifest and exact original command",
    async () => {
      await prepared();
      await f("mode", "lost");
      const before = downloads.length;
      await download();
      await page.getByRole("alert").waitFor();
      assert.equal(downloads.length, before);
      const posts = (await f("calls")).filter((x) => x.method === "POST");
      const event = page.waitForEvent("download");
      await retry();
      await event;
      assert.equal(
        (await f("calls")).filter((x) => x.method === "POST").at(-1).body,
        posts[0].body,
      );
      assert.equal((await f("issued")).length, 1);
    },
  );
  await check(
    "A tampered issuance receipt after response loss cannot replace the pinned copy",
    async () => {
      await prepared();
      await f("mode", "lost");
      await download();
      await page.getByRole("alert").waitFor();
      const before = downloads.length;
      await f("tamperReceipt");
      await retry();
      await page
        .getByRole("alert")
        .filter({ hasText: "immutable issuance receipt changed" })
        .waitFor();
      assert.equal(downloads.length, before);
      assert.equal(await f("pending"), true);
    },
  );
  await check(
    "A fresh server authority refusal clears issued metadata and uncertain intent",
    async () => {
      await prepared();
      await f("mode", "authority");
      await download();
      await page
        .getByRole("alert")
        .filter({ hasText: "unavailable with your current access" })
        .waitFor();
      assert.equal(await page.getByLabel("Verified issued copy").count(), 0);
      assert.equal(
        await page
          .getByRole("button", { name: "Retry previous copy request" })
          .count(),
        0,
      );
      assert.equal(await f("pending"), false);
    },
  );
  await check(
    "Same-tenant exposed actor change discards a late response and cannot download",
    async () => {
      await prepared();
      await f("mode", "delay");
      const before = downloads.length;
      await download();
      await page.waitForFunction(() => window.fixture.pending());
      await f("patch", {
        principalId: "second-synthetic-author",
        sessionIdentity: "second-human-identity",
      });
      await page
        .getByRole("button", { name: "Prepare an internal saved copy" })
        .waitFor();
      await f("release");
      await page.waitForFunction(() => !window.fixture.pending());
      assert.equal(await page.getByLabel("Verified issued copy").count(), 0);
      assert.equal(downloads.length, before);
    },
  );
  await check(
    "Local draft changes while a download reply is pending prevent latent download",
    async () => {
      await prepared();
      await f("mode", "delay");
      const before = downloads.length;
      await download();
      await page.waitForFunction(() => window.fixture.pending());
      await f("patch", { hasUnsavedChanges: true });
      await page
        .getByText(
          "Save or discard local plan edits before preparing or downloading a copy. An uncertain previous request can still be retried exactly.",
        )
        .waitFor();
      await f("release");
      await page
        .getByRole("status")
        .filter({ hasText: "no download was started" })
        .waitFor();
      assert.equal(downloads.length, before);
      assert.equal(
        await page
          .getByRole("button", { name: "Download issued copy" })
          .isDisabled(),
        true,
      );
    },
  );
  await check(
    "Exact uncertain prepare retry remains possible after local draft edits",
    async () => {
      await reset();
      await open();
      await page.getByRole("checkbox").check();
      await f("mode", "lost");
      await issue();
      await page.getByRole("alert").waitFor();
      const before = downloads.length;
      await f("patch", { hasUnsavedChanges: true });
      assert.equal(
        await page
          .getByRole("button", { name: "Confirm and issue internal JSON copy" })
          .isDisabled(),
        true,
      );
      assert.equal(
        await page
          .getByRole("button", { name: "Retry previous copy request" })
          .isDisabled(),
        false,
      );
      await retry();
      await page.getByLabel("Verified issued copy").waitFor();
      assert.equal(downloads.length, before);
      assert.equal((await f("issued")).length, 1);
    },
  );
  await check(
    "Current saved-head change clears private copy and history without touching any draft",
    async () => {
      await prepared();
      await f("patch", {
        currentRevision: "77777777-7777-4777-8777-777777777777",
      });
      await page
        .getByRole("button", { name: "Prepare an internal saved copy" })
        .waitFor();
      assert.equal(await page.getByLabel("Verified issued copy").count(), 0);
      assert.equal(await f("pending"), false);
    },
  );
  for (const width of [1440, 390, 320])
    await check(
      `Synthetic keyboard/mobile/accessibility ${width}px`,
      async () => {
        await page.setViewportSize({ width, height: 900 });
        await prepared();
        await page
          .getByRole("button", { name: "Download issued copy" })
          .focus();
        assert.equal(
          await page
            .getByRole("button", { name: "Download issued copy" })
            .evaluate((el) => el === document.activeElement),
          true,
        );
        assert.equal(
          await page.evaluate(
            () => document.documentElement.scrollWidth > innerWidth,
          ),
          false,
        );
        await page.addScriptTag({
          path: "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/tools/browser/node_modules/axe-core/axe.min.js",
        });
        const scan = await page.evaluate(async () => window.axe.run(document));
        scans.push({
          width,
          violations: scan.violations,
          incomplete: scan.incomplete,
        });
        assert.equal(scan.violations.length, 0);
        assert.equal(scan.incomplete.length, 0);
        const path = `${directory}/ui-fixture-${width}.png`;
        await page.screenshot({ path });
        screenshots.push({ path, width });
      },
    );
  assert.equal(external.length, 0);
  assert.equal(errors.length, 0);
  assert.deepEqual(hashes(), sources);
} catch (error) {
  errors.push(error.stack || String(error));
  process.exitCode = 1;
} finally {
  writeFileSync(
    `${directory}/ui-fixture-tests.json`,
    JSON.stringify(
      {
        scope:
          "Temporary synthetic component and request-function fixture only; not actual API, PostgreSQL, capability enforcement, audit, release or acceptance evidence",
        actual_api_qualification: "NOT_RUN",
        finished_at: new Date().toISOString(),
        results,
        errors,
        blocked_external_requests: external,
        accessibility_scans: scans,
        screenshots,
        source_hashes: sources,
        current_source_hashes: hashes(),
        sources_unchanged: JSON.stringify(hashes()) === JSON.stringify(sources),
      },
      null,
      2,
    ) + "\n",
  );
  await browser.close();
}
