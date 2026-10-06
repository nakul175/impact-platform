import { chromium } from "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/tools/browser/node_modules/playwright-core/index.mjs";
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { createHash } from "node:crypto";
import assert from "node:assert/strict";
import { plan } from "./fixtures.ts";
const directory = "/private/tmp/tola-ai-plan-review-draft";
const repo =
  "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform";
const files = [
  ...readdirSync(directory).filter((file) =>
    /\.(?:ts|tsx|mjs|css|html|patch)$/.test(file),
  ),
  "BASELINE-SOURCE.json",
  ...readdirSync(repo + "/apps/web/src")
    .filter((file) => /\.(?:ts|tsx|css)$/.test(file))
    .map((file) => repo + "/apps/web/src/" + file),
  repo + "/apps/api/impact_api/ai_plan_public_export_schema_v1.json",
  repo + "/packages/contracts/openapi-implemented.json",
];
const hashes = () =>
  Object.fromEntries(
    files.map((file) => [
      file,
      createHash("sha256")
        .update(
          readFileSync(file.startsWith("/") ? file : directory + "/" + file),
        )
        .digest("hex"),
    ]),
  );
const before = hashes(),
  results = [],
  errors = [],
  external = [],
  requests = [],
  scans = [],
  captures = [];
const browser = await chromium.launch({
  executablePath:
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
  args: ["--no-sandbox"],
});
const browserContext = await browser.newContext();
await browserContext.route("**/*", (route) => {
  const url = new URL(route.request().url());
  if (url.origin !== "http://127.0.0.1:8193") {
    external.push(url.origin);
    return route.abort();
  }
  if (url.pathname.includes("/v1/")) requests.push(url.pathname);
  return route.continue();
});
const page = await browserContext.newPage();
page.setDefaultTimeout(8000);
page.on("pageerror", (e) => errors.push(e.message));
const f = (method, value) =>
  page.evaluate(({ method, value }) => window.fixture[method](value), {
    method,
    value,
  });
const region = () =>
  page.getByRole("region", { name: "Review of the opened saved AI plan" });
const view = () =>
  region().getByRole("button", { name: "View saved-plan review" }).click();
async function reset(mode = "direct") {
  await page.goto("http://127.0.0.1:8193");
  await page
    .getByRole("heading", { name: "Private saved-plan review prototype" })
    .waitFor();
  await f("patch", { mode });
}
async function openPlan() {
  await page
    .getByLabel("Saved adoption plans")
    .selectOption("11111111-1111-4111-8111-111111111111");
  await page
    .getByRole("button", { name: "Open saved plan", exact: true })
    .click();
  await region()
    .getByRole("button", { name: "View saved-plan review" })
    .waitFor();
}
async function check(name, fn) {
  await fn();
  results.push({
    name,
    status: "passed",
    scope:
      "Unregistered private prototype/proposed parent in an in-memory request-function fixture. Actual API/database authority and integrated product NOT_RUN.",
  });
  console.log("PASS " + name);
}
try {
  await check(
    "Derived saved review is lazy, advisory and makes no requests",
    async () => {
      await reset();
      assert.equal(
        await region().getByText("Saved plan:", { exact: true }).count(),
        0,
      );
      await view();
      await region()
        .getByRole("heading", { name: "Procurement preparation" })
        .waitFor();
      assert.equal((await f("calls")).length, 0);
      assert.match(
        await region().innerText(),
        /not a completion percentage.*procurement approval or official AI impact/,
      );
    },
  );
  await check(
    "Section actions only open existing sections without writes or worksheet starters",
    async () => {
      await reset();
      await view();
      await region()
        .getByRole("button", { name: "Open guided practice" })
        .click();
      assert.deepEqual(await f("navigation"), ["practice"]);
      assert.equal((await f("calls")).length, 0);
    },
  );
  await check(
    "Mutation gates disable navigation until the existing mutation resolves",
    async () => {
      await reset();
      await view();
      await f("patch", { mutation: true });
      await page.waitForFunction(() =>
        Array.from(document.querySelectorAll(".ai-plan-review button"))
          .filter((button) => button.textContent === "Open procurement brief")
          .every((button) => button.disabled),
      );
      assert.equal(
        await region()
          .getByRole("button", { name: "Open procurement brief" })
          .first()
          .isDisabled(),
        true,
      );
      assert.equal((await f("navigation")).length, 0);
    },
  );
  await check(
    "Dirty source immediately hides and clears prior review until fresh capture",
    async () => {
      await reset();
      await view();
      await f("patch", { dirty: true });
      await region()
        .getByText(/working draft has local edits/)
        .waitFor();
      assert.equal(
        await region()
          .getByText(/Synthetic saved team plan/)
          .count(),
        0,
      );
      await f("patch", { dirty: false });
      await region()
        .getByText(/Open the saved plan again/)
        .waitFor();
      assert.equal(
        await region()
          .getByRole("button", { name: "Hide saved-plan review" })
          .count(),
        0,
      );
      await f("capture");
      await region()
        .getByText(/Synthetic saved team plan/)
        .waitFor();
    },
  );
  await check(
    "Context, exact head, read and canonical availability failures hide all prior derived content",
    async () => {
      for (const change of [
        {
          context: {
            base: "/different/",
            principalId: "synthetic-principal",
            sessionIdentity: "synthetic-human",
          },
        },
        {
          head: {
            object_id: "11111111-1111-4111-8111-111111111111",
            revision_id: "different",
          },
        },
        { canRead: false },
        { unavailable: true },
      ]) {
        await reset();
        await view();
        await f("patch", change);
        await page.waitForFunction(
          () =>
            !document
              .querySelector(".ai-plan-review")
              ?.textContent?.includes("Synthetic saved team plan"),
        );
        assert.equal(
          await region()
            .getByText(/Synthetic saved team plan/)
            .count(),
          0,
        );
      }
    },
  );
  await check(
    "Private/future linkage metadata never enters visible review or changes its derived output",
    async () => {
      await reset();
      await view();
      const expected = await region().innerText();
      const p = plan();
      p.data.impact_reference = { private_label: "PRIVATE-SENTINEL" };
      p.data.human_advice_count = 99;
      await f("row", p);
      await f("capture");
      assert.equal(await region().innerText(), expected);
      assert.doesNotMatch(
        await page.locator("body").innerText(),
        /PRIVATE-SENTINEL/,
      );
      assert.match(expected, /Edition identifiers alone do not prove/);
    },
  );
  await check(
    "Proposed parent does not derive a saved review from the plan list",
    async () => {
      await reset("workspace");
      await page.getByLabel("Saved adoption plans").waitFor();
      await page.waitForFunction(
        () =>
          document.querySelector('select[aria-label="Saved adoption plans"]')
            ?.options.length === 2,
      );
      assert.equal(await region().count(), 0);
      assert.equal(
        (await f("calls")).filter((call) =>
          call.path.endsWith("/plans/11111111-1111-4111-8111-111111111111"),
        ).length,
        0,
      );
    },
  );
  await check(
    "Successful canonical Open establishes review tied to exact public source",
    async () => {
      await reset("workspace");
      await openPlan();
      await view();
      await region()
        .getByText(/Synthetic saved team plan/)
        .waitFor();
      assert.equal(
        (await f("calls")).filter((call) =>
          call.path.endsWith("/plans/11111111-1111-4111-8111-111111111111"),
        ).length,
        1,
      );
      await region()
        .locator("article")
        .filter({
          has: page.getByRole("heading", { name: "Procurement preparation" }),
        })
        .getByRole("button", { name: "Open procurement brief" })
        .click();
      await page
        .getByRole("heading", { name: "Procurement brief", exact: true })
        .waitFor();
      assert.equal(
        (await f("calls")).filter((call) => call.method !== "GET").length,
        0,
      );
    },
  );
  await check(
    "Parent dirty edit and manual revert cannot restore review without a fresh Open",
    async () => {
      await reset("workspace");
      await openPlan();
      await view();
      const title = await page
        .getByLabel("Plan name", { exact: true })
        .inputValue();
      await page
        .getByLabel("Plan name", { exact: true })
        .fill("Local changed draft");
      await region()
        .getByText(/working draft has local edits/)
        .waitFor();
      await page.getByLabel("Plan name", { exact: true }).fill(title);
      await region()
        .getByText(/Open the saved plan again/)
        .waitFor();
      assert.equal(
        await region()
          .getByText(/Synthetic saved team plan/)
          .count(),
        0,
      );
      await page
        .getByRole("button", { name: "Open saved plan", exact: true })
        .click();
      await region()
        .getByText(/Synthetic saved team plan/)
        .waitFor();
    },
  );
  await check(
    "Receipt-only save never restores review or interprets plan-list captured draft content",
    async () => {
      await reset("workspace");
      await openPlan();
      await page
        .getByLabel("Plan name", { exact: true })
        .fill("New synthetic saved title");
      await page
        .getByRole("button", { name: "Save plan changes", exact: true })
        .click();
      await page
        .getByText("Plan saved. Any edits made while saving remain unsaved.", {
          exact: true,
        })
        .waitFor();
      await region()
        .getByText(/Open the saved plan again/)
        .waitFor();
      assert.equal(
        await region()
          .getByRole("button", { name: "View saved-plan review" })
          .count(),
        0,
      );
      await page
        .getByRole("button", { name: "Open saved plan", exact: true })
        .click();
      await view();
      await region()
        .getByText(/New synthetic saved title/)
        .waitFor();
      await region()
        .getByText("Saved revision details", { exact: true })
        .click();
      assert.match(
        await region().innerText(),
        /33333333-3333-4333-8333-333333333333/,
      );
    },
  );
  await check(
    "Failed fresh canonical Open clears prior review while preserving working draft",
    async () => {
      await reset("workspace");
      await openPlan();
      await view();
      const title = await page
        .getByLabel("Plan name", { exact: true })
        .inputValue();
      await f("failNext");
      await page
        .getByRole("button", { name: "Open saved plan", exact: true })
        .click();
      await page
        .getByRole("alert")
        .getByText("Saved source unavailable")
        .waitFor();
      await region()
        .getByText(/Open the saved plan again/)
        .waitFor();
      assert.equal(
        await page.getByLabel("Plan name", { exact: true }).inputValue(),
        title,
      );
      assert.equal(
        await region()
          .getByText(/Synthetic saved team plan/)
          .count(),
        0,
      );
    },
  );
  await check(
    "Draft changes during a held canonical read discard its later review response",
    async () => {
      await reset("workspace");
      await openPlan();
      await view();
      await f("holdNext");
      await page
        .getByRole("button", { name: "Open saved plan", exact: true })
        .click();
      await f("profileGoal", "Later local profile edit");
      await region()
        .getByText(/working draft has local edits/)
        .waitFor();
      await f("release");
      await page
        .getByText(/brief or draft changed while the saved plan was opening/)
        .waitFor();
      assert.equal(
        await region()
          .getByText(/Synthetic saved team plan/)
          .count(),
        0,
      );
    },
  );
  await check(
    "Read hint lost during held canonical reply cannot restore review on later hint return",
    async () => {
      await reset("workspace");
      await openPlan();
      await view();
      await f("holdNext");
      await page
        .getByRole("button", { name: "Open saved plan", exact: true })
        .click();
      await f("patch", { canRead: false });
      await page.waitForFunction(
        () => !document.querySelector(".ai-plan-review"),
      );
      await f("release");
      await page
        .getByRole("button", { name: "Open saved plan", exact: true })
        .waitFor({ state: "visible" });
      await page.waitForFunction(
        () =>
          Array.from(document.querySelectorAll("button")).find(
            (button) => button.textContent === "Open saved plan",
          )?.disabled === false,
      );
      await f("patch", { canRead: true });
      await region()
        .getByText(/Open the saved plan again/)
        .waitFor();
      assert.equal(
        await region()
          .getByText(/Synthetic saved team plan/)
          .count(),
        0,
      );
    },
  );
  await check(
    "Read loss and return before a held reply cannot resurrect an old review",
    async () => {
      await reset("workspace");
      await openPlan();
      await view();
      await f("holdNext");
      await page
        .getByRole("button", { name: "Open saved plan", exact: true })
        .click();
      await f("patch", { canRead: false });
      await page.waitForFunction(
        () => !document.querySelector(".ai-plan-review"),
      );
      await f("patch", { canRead: true });
      await region()
        .getByText(/Open the saved plan again/)
        .waitFor();
      await f("release");
      await page
        .getByText(/access changed while the saved plan was opening/)
        .waitFor();
      assert.equal(
        await region()
          .getByText(/Synthetic saved team plan/)
          .count(),
        0,
      );
      await page
        .getByRole("button", { name: "Open saved plan", exact: true })
        .click();
      await view();
      await region()
        .getByText(/Synthetic saved team plan/)
        .waitFor();
    },
  );
  await check(
    "An edit and undo during a held reply still require a new deliberate canonical Open",
    async () => {
      await reset("workspace");
      await openPlan();
      await view();
      await f("holdNext");
      await page
        .getByRole("button", { name: "Open saved plan", exact: true })
        .click();
      await f("profileGoal", "Transient local edit");
      await region()
        .getByText(/working draft has local edits/)
        .waitFor();
      await f("profileGoal", "Prepare public training material");
      await region()
        .getByText(/Open the saved plan again/)
        .waitFor();
      await f("release");
      await page
        .getByText(/brief or draft changed while the saved plan was opening/)
        .waitFor();
      assert.equal(
        await region()
          .getByText(/Synthetic saved team plan/)
          .count(),
        0,
      );
      await page
        .getByRole("button", { name: "Open saved plan", exact: true })
        .click();
      await region()
        .getByText(/Synthetic saved team plan/)
        .waitFor();
    },
  );
  await check(
    "New plan and same-tenant actor reset discard saved-review state",
    async () => {
      await reset("workspace");
      await openPlan();
      await view();
      await page
        .getByRole("button", { name: "New adoption plan", exact: true })
        .click();
      await page.waitForFunction(
        () => !document.querySelector(".ai-plan-review"),
      );
      await openPlan();
      await view();
      await f("patch", {
        context: {
          base: "/v1/tenants/synthetic/",
          principalId: "another-synthetic-principal",
          sessionIdentity: "another-synthetic-human",
        },
      });
      await page.waitForFunction(
        () => !document.querySelector(".ai-plan-review"),
      );
      assert.equal(
        await page.getByLabel("Plan name", { exact: true }).inputValue(),
        "",
      );
    },
  );
  for (const width of [1440, 390, 320])
    await check(
      `Private checklist keyboard/mobile/accessibility${width}px`,
      async () => {
        await page.setViewportSize({ width, height: 900 });
        await reset();
        await region()
          .getByRole("button", { name: "View saved-plan review" })
          .focus();
        await page.keyboard.press("Enter");
        await region()
          .getByRole("heading", { name: "Pilot measure and observations" })
          .waitFor();
        assert.equal(
          await page.evaluate(
            () => document.documentElement.scrollWidth > innerWidth + 1,
          ),
          false,
        );
        await page.addScriptTag({
          path: repo + "/tools/browser/node_modules/axe-core/axe.min.js",
        });
        const result = await page.evaluate(() =>
          window.axe.run(document.querySelector(".ai-plan-review"), {
            runOnly: {
              type: "tag",
              values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
            },
          }),
        );
        assert.deepEqual(result.violations, []);
        assert.deepEqual(result.incomplete, []);
        scans.push({ width, violations: [], incomplete: [] });
        const file = directory + `/review-${width}.png`;
        await region().screenshot({ path: file });
        captures.push({
          width,
          file,
          sha256: createHash("sha256").update(readFileSync(file)).digest("hex"),
        });
      },
    );
  await check(
    "Prototype sources stayed fixed and no actual API/provider/external request occurred",
    async () => {
      assert.deepEqual(hashes(), before);
      assert.deepEqual(errors, []);
      assert.deepEqual(external, []);
      assert.deepEqual(requests, []);
    },
  );
} catch (error) {
  results.push({
    name: "Stopped private prototype qualification",
    status: "failed",
    error: String(error),
  });
  process.exitCode = 1;
  console.error(error);
  await page
    .screenshot({ path: directory + "/failed-ui.png", fullPage: true })
    .catch(() => {});
} finally {
  writeFileSync(
    directory + "/ui-tests.json",
    JSON.stringify(
      {
        scope:
          "Private prototype and proposed Workspace in in-memory request-function fixture only; not actual product/API/database authority, accepted requirement or deployment evidence",
        results,
        errors,
        blocked_external_requests: external,
        actual_api_requests: requests,
        accessibility_scans: scans,
        captures,
        qualified_sources: before,
        current_sources: hashes(),
        sources_unchanged: JSON.stringify(before) === JSON.stringify(hashes()),
      },
      null,
      2,
    ) + "\n",
  );
  await browser.close();
}
