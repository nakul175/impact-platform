// Optional actual qualification: actual local Keycloak cookies, native transaction pooler,
// synthetic notes-only diagnosis; no development-minted bearer or grant changes.
import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import assert from "node:assert/strict";

const root = process.cwd();
const local = process.env.IMPACT_TEST_LOCAL;
const base = process.env.IMPACT_BASE_URL;
const evidenceFile = process.env.IMPACT_BROWSER_EVIDENCE_FILE;
let browser,
  context,
  peer,
  page,
  idp,
  config,
  fixture,
  current,
  created,
  command;
let active, csrf, heldRelease, completed, browserVersion, delayedOutcome;
const operationIds = [];
const title = "Synthetic provider browser diagnosis";
const notes =
  "Synthetic evidence notes preserved through actual provider cookies.";
const results = [],
  blocked = [],
  pageErrors = [],
  cleanupFailures = [];
const groups = ["DX-IDP-B01", "DX-IDP-B02", "DX-IDP-B03"];
const names = [
  "Actual admin password/TOTP session and diagnosis UI save/reopen/completion",
  "Actual provider logout, stale cookie refusal and delayed private read clearing",
  "Actual owner provider session cannot gain diagnosis access from custody",
];
const usedSteps = new Map();
const eq = (a, b) => {
  active.assertions++;
  assert.deepEqual(a, b);
};
const truth = (v) => {
  active.assertions++;
  assert.ok(v);
};
const region = () => page.locator(".ai-diagnosis");
const button = (name) => page.getByRole("button", { name, exact: true });
const dbutton = (name) => region().getByRole("button", { name, exact: true });
const dlabel = (name) => region().getByLabel(name, { exact: true });
const deferred = () => {
  let resolve;
  const promise = new Promise((r) => {
    resolve = r;
  });
  return { promise, resolve };
};
async function bounded(promise) {
  let timer;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(Error("bounded-timeout")), 20000);
      }),
    ]);
  } finally {
    clearTimeout(timer);
  }
}
async function test(index, fn) {
  active = {
    id: groups[index],
    name: names[index],
    status: "running",
    assertions: 0,
  };
  try {
    await fn();
    active.status = "passed";
    console.log("PASS " + active.id);
  } catch {
    active.status = "failed";
    active.failure_code = "CHECK_FAILED_DETAILS_WITHHELD";
    throw Error("group-failed");
  } finally {
    results.push(active);
    active = null;
  }
}
async function totp(user) {
  const used = usedSteps.get(user.username) || new Set();
  usedSteps.set(user.username, used);
  for (;;) {
    const now = Math.floor(Date.now() / 30000);
    const step = [now, now + 1].find((s) => !used.has(s));
    if (step !== undefined) {
      used.add(step);
      const counter = Buffer.alloc(8);
      counter.writeBigUInt64BE(BigInt(step));
      const mac = crypto
        .createHmac("sha1", Buffer.from(user.totp_secret, "utf8"))
        .update(counter)
        .digest();
      const offset = mac[mac.length - 1] & 15;
      return String((mac.readUInt32BE(offset) & 0x7fffffff) % 1000000).padStart(
        6,
        "0",
      );
    }
    await new Promise((r) => setTimeout(r, 30000 - (Date.now() % 30000) + 500));
  }
}
async function login(actor) {
  const user = idp.users[actor];
  truth(Boolean(user?.username && user?.password && user?.totp_secret));
  await page.goto(base);
  await page
    .getByRole("link", {
      name: "Continue with your organisation →",
      exact: true,
    })
    .click();
  await page.waitForURL((u) => u.origin === new URL(idp.base_url).origin);
  await page.locator("#username").fill(user.username);
  await page.locator("#password").fill(user.password);
  await page.locator("#kc-login").click();
  await page.locator("#otp").fill(await totp(user));
  await page.locator("#kc-login").click();
  await page.waitForURL((u) => u.origin === new URL(base).origin);
  await button("Sign out").first().waitFor();
  const me = await page.evaluate(async () => {
    const response = await fetch("/auth/me");
    return { status: response.status, body: await response.json() };
  });
  eq(me.status, 200);
  eq(me.body.identity_id, fixture.actors[actor].identity_id);
  csrf = me.body.csrf_token;
  truth(typeof csrf === "string" && csrf.length > 0);
}
async function workspace() {
  await button("AI enablement").click();
  await dlabel("Saved diagnoses").waitFor();
  await page.waitForFunction(
    () =>
      !document
        .querySelector(".ai-diagnosis")
        ?.textContent.includes("Loading saved diagnoses…"),
  );
}
async function api(
  route,
  method = "GET",
  body,
  target = context,
  token = csrf,
) {
  const response = await target.request.fetch(new URL(route, base).href, {
    method,
    data: body,
    headers:
      method === "GET"
        ? {}
        : { Origin: new URL(base).origin, "X-CSRF-Token": token },
    maxRedirects: 0,
  });
  return { status: response.status(), body: await response.json() };
}
async function write(name, route, method, status) {
  const pending = page
    .waitForResponse(
      (r) =>
        new URL(r.url()).pathname === route && r.request().method() === method,
    )
    .catch(() => null);
  await dbutton(name).click();
  const response = await pending;
  eq(response.status(), status);
  const receipt = await response.json();
  await page.waitForFunction(
    (rev) =>
      document
        .querySelector(".ai-diagnosis")
        ?.getAttribute("data-diagnosis-revision") === rev,
    receipt.revision_id,
  );
  return receipt;
}
try {
  assert(local && base && evidenceFile && process.env.IMPACT_IDP_FILE);
  assert(
    process.env.IMPACT_ENVIRONMENT === "test" &&
      process.env.IMPACT_NATIVE_TEST === "1",
  );
  assert(
    process.env.IMPACT_ALLOW_FIXTURE_LOAD === "1" &&
      process.env.IMPACT_DB_POOLER === "pgbouncer-transaction",
  );
  config = JSON.parse(
    await fs.readFile(path.join(local, "config.json"), "utf8"),
  );
  assert.equal(config.dev_auth, false);
  idp = JSON.parse(await fs.readFile(process.env.IMPACT_IDP_FILE, "utf8"));
  fixture = JSON.parse(
    await fs.readFile(
      path.join(root, "specification/fixtures/api-fixture.json"),
      "utf8",
    ),
  );
  assert.equal(fixture.allow_mutations, true);
  const origins = new Set([new URL(base).origin, new URL(idp.base_url).origin]);
  for (const origin of origins) {
    const url = new URL(origin);
    assert.equal(url.hostname, "127.0.0.1");
    assert.equal(url.protocol, "http:");
  }
  browser = await chromium.launch({
    executablePath:
      process.env.IMPACT_BROWSER_EXECUTABLE ||
      path.join(root, ".local/browser/chromium"),
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--no-zygote",
    ],
  });
  browserVersion = browser.version();
  context = await browser.newContext({
    viewport: { width: 1440, height: 1050 },
  });
  await context.route("**/*", async (route) => {
    const request = route.request(),
      url = new URL(request.url());
    if (
      !origins.has(url.origin) ||
      (url.origin === new URL(base).origin &&
        /\/(?:advisory|providers?|ai-jobs|ai-requests)(?:\/|$)/.test(
          url.pathname,
        ))
    ) {
      blocked.push({
        origin: url.origin,
        path: url.pathname,
        method: request.method(),
      });
      await route.abort("blockedbyclient");
      return;
    }
    await route.continue();
  });
  page = await context.newPage();
  page.setDefaultTimeout(20000);
  page.on("pageerror", () => pageErrors.push("BROWSER_ERROR_DETAILS_WITHHELD"));
  const route = `/v1/tenants/${fixture.tenant_a}/ai-enablement/diagnoses`;
  await test(0, async () => {
    await login("admin");
    await workspace();
    await dlabel("Diagnosis title").fill(title);
    await dbutton("Add problem").click();
    await dlabel("Description for priority 1").fill(
      "Synthetic staff capacity gap",
    );
    await dlabel("Area affected for Synthetic staff capacity gap").fill(
      "Delivery",
    );
    await dlabel("Supporting evidence for Synthetic staff capacity gap").fill(
      notes,
    );
    const submitted = page
      .waitForRequest(
        (r) => new URL(r.url()).pathname === route && r.method() === "POST",
      )
      .catch(() => null);
    created = await write("Save diagnosis draft", route, "POST", 201);
    const initialRequest = await submitted;
    command = JSON.parse(initialRequest.postData());
    const requestHeaders = await initialRequest.allHeaders();
    eq(requestHeaders["x-csrf-token"], csrf);
    truth(!requestHeaders.authorization);
    const read = await api(route + "/" + created.object_id);
    eq(read.status, 200);
    current = read.body;
    eq(current.data.title, title);
    eq(current.data.problems[0].supporting_evidence, notes);
    eq(current.data.priority_order, [current.data.problems[0].problem_id]);
    operationIds.push(command.operation_id);
    await page.reload();
    await workspace();
    await dlabel("Saved diagnoses").selectOption(created.object_id);
    await page.waitForFunction(
      (rev) =>
        document
          .querySelector(".ai-diagnosis")
          ?.getAttribute("data-diagnosis-revision") === rev,
      created.revision_id,
    );
    eq(await dlabel("Diagnosis title").inputValue(), title);
    eq(
      await dlabel(
        "Supporting evidence for Synthetic staff capacity gap",
      ).inputValue(),
      notes,
    );
    const completionRoute =
      route + "/" + created.object_id + "/actions/complete";
    const completionRequest = page
      .waitForRequest(
        (r) =>
          new URL(r.url()).pathname === completionRoute &&
          r.method() === "POST",
      )
      .catch(() => null);
    completed = await write("Complete diagnosis", completionRoute, "POST", 200);
    operationIds.push(
      JSON.parse((await completionRequest).postData()).operation_id,
    );
    const final = await api(route + "/" + created.object_id);
    eq(final.status, 200);
    current = final.body;
    eq(current.business_state, "Completed");
    eq(current.revision_id, completed.revision_id);
    eq(current.data.completed_by, fixture.actors.admin.principal_id);
    truth(await dlabel("Diagnosis title").evaluate((e) => e.readOnly));
    eq(new Set(operationIds).size, 2);
  });
  await test(1, async () => {
    await dbutton("New diagnosis").click();
    const oldCsrf = csrf;
    peer = await browser.newContext({
      storageState: await context.storageState(),
    }); // Memory only.
    const captured = deferred(),
      release = deferred(),
      finished = deferred();
    heldRelease = release;
    const target = new URL(route + "/" + created.object_id, base).href;
    let first = true;
    const intercept = async (requestRoute) => {
      if (!first || requestRoute.request().method() !== "GET")
        return requestRoute.fallback();
      first = false;
      try {
        const response = await requestRoute.fetch({
          maxRedirects: 0,
          timeout: 20000,
        });
        assert.equal(response.status(), 200);
        assert.deepEqual(await response.json(), current);
        captured.resolve(true);
        await release.promise;
        try {
          await requestRoute.fulfill({ response });
          finished.resolve("delivered");
        } catch {
          finished.resolve("aborted-after-logout");
        }
      } catch {
        captured.resolve(false);
        finished.resolve("capture-failed");
      }
    };
    await page.route(target, intercept);
    try {
      await dlabel("Saved diagnoses").selectOption(created.object_id);
      truth(await bounded(captured.promise));
      const logoutVisit = page
        .waitForRequest((r) =>
          r.url().startsWith(idp.discovery.end_session_endpoint + "?"),
        )
        .catch(() => null);
      await button("Sign out").first().click();
      const logoutUrl = new URL((await logoutVisit).url());
      truth(Boolean(logoutUrl.searchParams.get("id_token_hint")));
      eq(logoutUrl.searchParams.get("post_logout_redirect_uri"), base + "/");
      await page.waitForURL((u) => u.toString() === base + "/");
      await page
        .getByRole("link", {
          name: "Continue with your organisation →",
          exact: true,
        })
        .waitFor();
      eq(
        await page.evaluate(async () => (await fetch("/auth/me")).status),
        401,
      );
      eq(
        (
          await api(
            route + "/" + created.object_id,
            "GET",
            undefined,
            peer,
            oldCsrf,
          )
        ).status,
        401,
      );
      eq((await api(route, "POST", command, peer, oldCsrf)).status, 401);
      release.resolve();
      delayedOutcome = await bounded(finished.promise);
      truth(["delivered", "aborted-after-logout"].includes(delayedOutcome));
      await page.evaluate(async () => {
        await new Promise(requestAnimationFrame);
        await new Promise(requestAnimationFrame);
      });
      eq(await region().count(), 0);
      truth(!(await page.locator("body").innerText()).includes(title));
      const storage = await page.evaluate(() =>
        JSON.stringify([
          Object.values(localStorage),
          Object.values(sessionStorage),
        ]),
      );
      truth(!storage.includes(title) && !storage.includes(notes));
      // Provider silent auth proves logout beyond a visit to its end-session URL.
      const callback = page
        .waitForRequest((r) => r.url().startsWith(base + "/auth/callback?"))
        .catch(() => null);
      const silent = new URL(idp.discovery.authorization_endpoint);
      silent.search = new URLSearchParams({
        response_type: "code",
        client_id: idp.client_id,
        redirect_uri: base + "/auth/callback",
        scope: "openid",
        prompt: "none",
        state: "synthetic-silent-check",
        code_challenge: "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM",
        code_challenge_method: "S256",
      }).toString();
      await page.goto(silent.href);
      const outcome = new URL((await callback).url());
      eq(outcome.searchParams.get("error"), "login_required");
      eq(outcome.searchParams.get("code"), null);
    } finally {
      release.resolve();
      await page.unroute(target, intercept);
      heldRelease = null;
    }
  });
  await test(2, async () => {
    await login("owner");
    if (await button("AI enablement").count())
      await button("AI enablement").click();
    eq(await region().count(), 0);
    const hidden = await api(route + "/" + created.object_id);
    eq(hidden.status, 404);
    eq(hidden.body.code, "RESOURCE_UNAVAILABLE");
    const denied = await api(route, "POST", command);
    eq(denied.status, 404);
    eq(denied.body.code, "RESOURCE_UNAVAILABLE");
    truth(!JSON.stringify([hidden.body, denied.body]).includes(title));
    truth(!(await page.locator("body").innerText()).includes(title));
    eq(blocked, []);
    eq(pageErrors, []);
  });
} catch {
  process.exitCode = 1;
  console.error(
    "Provider diagnosis qualification failed; private diagnostics withheld.",
  );
} finally {
  heldRelease?.resolve();
  for (const [index, id] of groups.entries())
    if (!results.some((r) => r.id === id))
      results.push({
        id,
        name: names[index],
        status: "not_run",
        assertions: 0,
      });
  for (const resource of [peer, context, browser]) {
    try {
      await resource?.close();
    } catch {
      cleanupFailures.push("BROWSER_CLOSE_FAILED_DETAILS_WITHHELD");
      process.exitCode = 1;
    }
  }
  if (evidenceFile) {
    await fs.mkdir(path.dirname(evidenceFile), { recursive: true });
    await fs.writeFile(
      evidenceFile,
      JSON.stringify(
        {
          suite: "Actual local provider-cookie diagnosis browser",
          browser_version: browserVersion || null,
          delayed_response_outcome: delayedOutcome || null,
          status: process.exitCode ? "failed" : "passed",
          results,
          counts: {
            groups: groups.length,
            passed: results.filter((r) => r.status === "passed").length,
            assertions: results.reduce((n, r) => n + r.assertions, 0),
          },
          runtime: {
            dev_auth: config?.dev_auth ?? null,
            native: process.env.IMPACT_NATIVE_TEST === "1",
            pooler: process.env.IMPACT_DB_POOLER || null,
            pool_size: process.env.IMPACT_POOLER_POOL_SIZE || null,
            origins: [base, idp?.base_url]
              .filter(Boolean)
              .map((u) => new URL(u).origin),
          },
          object_id: created?.object_id || null,
          operation_ids: operationIds,
          draft_revision_id: created?.revision_id || null,
          completed_revision_id: completed?.revision_id || null,
          title,
          supporting_evidence: notes,
          dev_auth: config?.dev_auth ?? null,
          forbidden_requests: blocked,
          uncaught_error_names: pageErrors,
          cleanup_failures: cleanupFailures,
          limits: [
            "Synthetic loopback fixture only; no human UX/acceptance/deployment claim.",
            "Real password/TOTP/cookies/CSRF; no development bearer token or grant/account changes.",
            "Effect counts and exact stored payload verification belong to the invoking native pytest wrapper; no delivery claim.",
            "No Evidence selectors, privacy erasure, accessibility/TLS/HSTS or production provider claim.",
            "External source/migration/binary pinning belongs to the invoking reviewed wrapper.",
          ],
        },
        null,
        2,
      ),
    );
  }
}
