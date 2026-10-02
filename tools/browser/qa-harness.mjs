// Shared harness of the October 2026 browser groups (import, evidence, export, requeue): the
// packaged Chromium, sign-in with the run's passwords.json, suite-start bearer tokens for API
// setup, and the result file docs/evidence/<group>-browser-tests.json. Every wait is on a
// response or an element state, never on a fixed delay.
import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";

export const root = process.cwd();
export const local = process.env.IMPACT_TEST_LOCAL;
export const base = process.env.IMPACT_BASE_URL;
export const fixture = JSON.parse(
  await fs.readFile(
    path.join(root, "specification/fixtures/api-fixture.json"),
    "utf8",
  ),
);
export const records = Object.fromEntries(
  JSON.parse(
    await fs.readFile(
      path.join(root, "specification/fixtures/records.json"),
      "utf8",
    ),
  ).map((r) => [r.key, r]),
);
export const tenant = fixture.tenant_a;
export const evidencePath = (name) => path.join(root, "docs/evidence", name);

export async function harness(group) {
  if (!local || !base) throw Error("Use scripts/run.py " + group);
  const passwords = JSON.parse(
    await fs.readFile(path.join(local, "passwords.json"), "utf8"),
  );
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
    errors = [],
    pages = {};
  let last = null;
  const inflight = new Map();
  // PGlite serves one connection at a time: a worker process that connects while the API is
  // answering a browser request (a panel's poll, say) is refused. Run `fn` (a worker iteration)
  // with every open page's API requests held and none in flight; held requests continue after.
  async function quietly(fn) {
    let release;
    const gate = new Promise((resolve) => (release = resolve));
    const held = new Map();
    const hold = async (route) => {
      const page = route.request().frame().page();
      held.set(page, (held.get(page) || 0) + 1);
      await gate;
      await route.fallback();
    };
    const match = (url) => url.pathname.startsWith("/v1/");
    const open = Object.values(pages);
    for (const page of open) await page.route(match, hold);
    try {
      const busy = (p) => inflight.get(p) - (held.get(p) || 0) > 0;
      for (let i = 0; open.some(busy); i++) {
        assert(i < 400, "API requests did not settle");
        await new Promise((resolve) => setTimeout(resolve, 50));
      }
      return fn();
    } finally {
      release();
      for (const page of open) await page.unroute(match, hold);
    }
  }
  // One browser context per actor, so cookie sessions never mix. The 560 px height keeps the
  // fixed, scrolling sidebar honest: every entry must be reached by scrolling, as on CI runners
  // whose fonts are taller than local ones.
  async function as(user, height = 560, password = null) {
    // A sign-in created during the run (v0.26a operators-browser) brings its own one-time password.
    if (password) passwords[user] = password;
    if (pages[user]) {
      last = pages[user];
      return last;
    }
    const context = await browser.newContext({
      viewport: { width: 1440, height },
      acceptDownloads: true,
    });
    const page = await context.newPage();
    page.setDefaultTimeout(20000);
    // API requests in flight, for quietly() below.
    const api = (r) => new URL(r.url()).pathname.startsWith("/v1/");
    inflight.set(page, 0);
    page.on("request", (r) => {
      if (api(r)) inflight.set(page, inflight.get(page) + 1);
    });
    for (const done of ["requestfinished", "requestfailed"])
      page.on(done, (r) => {
        if (api(r)) inflight.set(page, inflight.get(page) - 1);
      });
    page.on("pageerror", (e) => errors.push(user + ": " + e.message));
    await page.goto(base);
    await page.getByLabel("Username", { exact: true }).fill(user);
    await page.getByLabel("Password", { exact: true }).fill(passwords[user]);
    await page.getByRole("button", { name: "Sign in →", exact: true }).click();
    // The landing area depends on the actor's access: a reader of programmes lands on the
    // portfolio, an administrator without programmes.read on People & access (main.tsx). The
    // portfolio heading is also rendered for a moment before /me/access answers, so waiting for it
    // alone passed for the administrator only by winning that race.
    await page
      .getByRole("heading", {
        name: /^(Programme portfolio|People & access|No active workspace)$/,
      })
      .and(page.locator("h1"))
      .waitFor();
    pages[user] = page;
    last = page;
    return page;
  }
  async function test(name, fn) {
    try {
      await fn();
    } catch (e) {
      console.log("FAIL " + name + ": " + e.message);
      throw e;
    }
    results.push({ name, status: "passed" });
    console.log("PASS " + name);
  }
  async function finish(run, failure) {
    try {
      await run();
    } catch (e) {
      results.push({ name: failure, status: "failed", message: e.message });
      if (last)
        await last
          .screenshot({
            path: evidencePath(group.replace("-browser", "") + "-failure.png"),
            fullPage: true,
          })
          .catch(() => {});
      console.error(e.stack || e.message);
      process.exitCode = 1;
    } finally {
      await fs.writeFile(
        evidencePath(group + "-tests.json"),
        JSON.stringify(
          { engine: "Chromium 153", results, uncaughtErrors: errors },
          null,
          2,
        ) + "\n",
      );
      await browser.close();
    }
  }
  return { as, test, finish, errors, quietly };
}

// The API as a fixture actor (suite-start bearer token): setup and independent assertions only.
export async function api(actor, route, data, method = "POST", revision) {
  const url = route.startsWith("/")
    ? base + route
    : base + "/v1/tenants/" + tenant + "/" + route;
  const response = await fetch(url, {
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
  const text = await response.text();
  const body = text ? JSON.parse(text) : null;
  return { status: response.status, body };
}
export async function ok(actor, route, data, method = "POST", revision) {
  const { status, body } = await api(actor, route, data, method, revision);
  assert(status >= 200 && status < 300, route + " " + JSON.stringify(body));
  return body;
}
export const read = (route, actor = "author") => ok(actor, route, null, "GET");

// Approve the open review of `candidateId` as the independent reviewer.
export async function approveCandidate(candidateId, reason = "Browser setup") {
  const workflow = (await read("workflows?limit=100", "reviewer")).items.find(
    (w) =>
      w.lifecycle_state === "InReview" && w.data.candidate_id === candidateId,
  );
  assert(workflow, "no open review for " + candidateId);
  return ok(
    "reviewer",
    "workflows/" + workflow.object_id + "/actions/approve",
    { candidate_revision: workflow.data.candidate_revision, reason },
    "POST",
    workflow.revision_id,
  );
}

// Wait for the POST (or other method) whose path ends with `suffix` caused by `click`.
export async function receipt(page, click, suffix, method = "POST") {
  const pending = page.waitForResponse(
    (r) =>
      r.request().method() === method &&
      new URL(r.url()).pathname.endsWith(suffix),
  );
  await click();
  const response = await pending;
  assert(response.ok(), await response.text());
  return response.json();
}

// The sidebar entry, reached by scrolling the fixed navigation.
export async function nav(page, name) {
  const entry = page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("button", { name, exact: true });
  await entry.scrollIntoViewIfNeeded();
  await entry.click();
}

// Lists are ordered oldest first, 50 at a time: load further pages until `entry` is present.
export async function loadUntil(page, entry) {
  const more = page.getByRole("button", { name: "Load more", exact: true });
  await entry.first().or(more).first().waitFor();
  for (let i = 0; i < 40 && !(await entry.count()); i++) {
    if (!(await more.count())) break;
    const loaded = page.waitForResponse(
      (r) => r.request().method() === "GET" && r.url().includes("cursor="),
    );
    await more.click();
    await (await loaded).finished();
  }
  await entry.first().waitFor();
  return entry.first();
}

export function noHorizontalScroll(page) {
  return page.evaluate(
    () => document.documentElement.scrollWidth <= innerWidth + 1,
  );
}
