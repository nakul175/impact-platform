import { chromium } from "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/tools/browser/node_modules/playwright-core/index.mjs";
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import assert from "node:assert/strict";
import vm from "node:vm";
const folder = "/private/tmp/tola-ai-a11y-checker-correction";
const candidate = folder + "/a11y-check.proposed.mjs";
const text = readFileSync(candidate, "utf8"),
  sha = createHash("sha256").update(text).digest("hex");
const begin = text.indexOf("async function selectWithKeyboard("),
  end = text.indexOf("async function tabTo(", begin);
assert(begin >= 0 && end > begin);
const observations = [];
const helpers = vm.runInNewContext(
  text.slice(begin, end) + ";({selectWithKeyboard,typeDateWithKeyboard});",
  {
    assert,
    keyboardWidgetObservations: observations,
    isFocused: (field) => field.evaluate((el) => el === document.activeElement),
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
const results = [];
async function page() {
  const c = await browser.newContext({ locale: "en-US" });
  await c.route("**/*", (r) => r.abort());
  const p = await c.newPage();
  await p.setContent(`<!doctype html><html lang="en"><head><title>Native widget checker correction</title></head><body><button id="open" type="button">Open synthetic native controls</button><dialog><form>
 <label>Indicator<select name="indicator_id" aria-label="Indicator" required><option value="" disabled selected>Choose indicator</option><option value="invented-first">Invented first indicator</option><option value="invented-second">Invented second indicator</option></select></label>
 <label>Event date (UTC)<input type="date" name="event_at" required value="2026-10-06"></label>
 <label>Review template<select name="workflow_version" aria-label="Review template" required><option value="" disabled selected>Choose review template</option><option value="invented-template">Invented template</option></select></label><button type="button">End diagnostic</button></form></dialog></body></html>`);
  await p.evaluate(() =>
    document
      .querySelector("#open")
      .addEventListener("click", () =>
        document.querySelector("dialog").showModal(),
      ),
  );
  await p.keyboard.press("Tab");
  await p.keyboard.press("Enter");
  async function tabTo(field) {
    for (let i = 0; i < 15; i++) {
      if (await field.evaluate((el) => el === document.activeElement)) return;
      await p.keyboard.press("Tab");
    }
    throw Error("Native field not keyboard reachable");
  }
  return { p, c, tabTo };
}
try {
  const run = await page();
  const indicator = run.p.getByLabel("Indicator", { exact: true }),
    date = run.p.getByLabel("Event date (UTC)", { exact: true }),
    template = run.p.getByLabel("Review template", { exact: true });
  await run.tabTo(indicator);
  await helpers.selectWithKeyboard(run.p, indicator, "Indicator");
  assert.equal(await indicator.inputValue(), "invented-first");
  results.push({
    name: "Exact proposed native helper chooses Indicator using keyboard and exact actual option value",
    status: "passed",
  });
  await run.tabTo(date);
  await helpers.typeDateWithKeyboard(run.p, date, "Event date (UTC)");
  assert.equal(await date.inputValue(), "2026-08-15");
  results.push({
    name: "Exact proposed date helper binds native AX element and types observed order with exact date",
    status: "passed",
  });
  await run.tabTo(template);
  await helpers.selectWithKeyboard(run.p, template, "Review template");
  assert.equal(await template.inputValue(), "invented-template");
  results.push({
    name: "Exact proposed native helper chooses Review template with exact value and retained focus",
    status: "passed",
  });
  await run.c.close();
  for (const [name, mutate] of [
    [
      "Unknown native date part fails before keyboard typing",
      (tree) => {
        const part = tree.nodes.find((n) => n.role?.value === "spinbutton");
        part.name.value = "Unknown part";
      },
    ],
    [
      "Duplicate native date parts fail instead of a guessed order",
      (tree) => {
        const parts = tree.nodes.filter((n) => n.role?.value === "spinbutton");
        parts[1].name.value = parts[0].name.value;
      },
    ],
  ]) {
    const r = await page(),
      field = r.p.getByLabel("Event date (UTC)", { exact: true });
    await r.tabTo(field);
    const before = await field.inputValue();
    let keyboardWrites = 0;
    const proxy = {
      evaluate: r.p.evaluate.bind(r.p),
      keyboard: {
        type: () => {
          keyboardWrites++;
          throw Error("Unexpected keyboard write");
        },
      },
      context: () => ({
        newCDPSession: async () => {
          const session = await r.c.newCDPSession(r.p);
          return {
            detach: () => session.detach(),
            send: async (method, args) => {
              const answer = await session.send(method, args);
              if (method === "Accessibility.getFullAXTree") mutate(answer);
              return answer;
            },
          };
        },
      }),
    };
    await assert.rejects(() =>
      helpers.typeDateWithKeyboard(proxy, field, "Event date (UTC)"),
    );
    assert.equal(keyboardWrites, 0);
    assert.equal(await field.inputValue(), before);
    results.push({
      name,
      status: "passed",
      scope:
        "Validation negative over an observed real native AX tree; not a real alternate system layout",
    });
    await r.c.close();
  }
  assert.equal(
    createHash("sha256").update(readFileSync(candidate)).digest("hex"),
    sha,
  );
} catch (error) {
  results.push({
    name: "Native helper qualification",
    status: "failed",
    message: String(error),
  });
  console.error(error);
  process.exitCode = 1;
} finally {
  writeFileSync(
    folder + "/native-helper-tests.json",
    JSON.stringify(
      {
        recorded_at: new Date().toISOString(),
        scope:
          "Private exact proposed helper on actual installed Chrome native DOM fixture, no real application/API/save/reviewer qualification",
        browser_version: browser.version(),
        platform: process.platform,
        results,
        keyboard_widget_observations: observations,
        candidate_sha256: sha,
        sources_unchanged:
          sha ===
          createHash("sha256").update(readFileSync(candidate)).digest("hex"),
        actual_full_a11y_mode: "NOT_RUN",
      },
      null,
      2,
    ) + "\n",
  );
  await browser.close();
  console.log(
    JSON.stringify({
      passed: results.filter((x) => x.status === "passed").length,
      failed: results.filter((x) => x.status === "failed").length,
      candidate_sha256: sha,
    }),
  );
}
