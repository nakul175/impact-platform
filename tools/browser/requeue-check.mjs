// requeue-browser: the operator re-queue of a failed (DEAD) delivery in the Workers panel of the
// tenant-lifecycle console (platform API 1.5.0). An invitation email intent is created through the
// API and made DEAD by one worker iteration whose synthetic adapter fails every send with one
// attempt allowed; the platform operator re-queues it in the browser with a reason, and the next
// ordinary worker iteration delivers it to the run's synthetic mail sink.
import assert from "node:assert/strict";
import { runWorkerOnce, sinkMessages } from "./worker-run.mjs";
import {
  harness,
  ok,
  read,
  receipt,
  nav,
  noHorizontalScroll,
  tenant,
  base,
  local,
  evidencePath,
} from "./qa-harness.mjs";

const { as, test, finish, errors } = await harness("requeue-browser");
const unique = Date.now().toString();
const attention = async () =>
  (await read("/v1/platform/deliveries?tenant_id=" + tenant, "admin")).items;
let dead;

async function deadInvitation() {
  // Settle whatever earlier fixture work left due, so the failing iteration sees only this intent.
  runWorkerOnce(local, "requeue-settle");
  const roles = (await read("role-templates?limit=100", "admin")).items;
  const scopes = (await read("access-scopes?limit=100", "admin")).items;
  const days = (n) => new Date(Date.now() + n * 86400000).toISOString();
  await ok("admin", "member-invitations", {
    email: "requeue-" + unique + "@example.test",
    role_template_id: roles.find((r) => r.name === "AUTHOR").object_id,
    scope_ids: [scopes.find((s) => s.scope_type === "TENANT").object_id],
    expires_at: days(5),
    membership_expires_at: days(20),
    external: true,
    reason: "Re-queue browser qualification",
  });
  const failing = runWorkerOnce(local, "requeue-failing", {
    MAX_ATTEMPTS: 1,
    SYNTHETIC_FAILURES: 1000,
  });
  assert(failing.dead >= 1, JSON.stringify(failing));
  const items = (await attention()).filter(
    (i) =>
      i.state === "DEAD" &&
      i.template === "MEMBER_INVITATION" &&
      i.last_error_class === "SYNTHETIC_FAILURE",
  );
  assert.equal(items.length, 1, JSON.stringify(items));
  return items[0];
}

await finish(async () => {
  dead = await deadInvitation();
  assert.deepEqual(dead.permitted_actions, ["requeue"]);
  const page = await as("admin");
  const panel = () =>
    page.getByRole("region", { name: "Deliveries needing attention" });
  const item = () =>
    panel().getByRole("listitem", { name: "Delivery " + dead.event_id });

  await test("The operator sees the failed delivery in the Workers panel", async () => {
    await nav(page, "Tenant lifecycle");
    await page
      .getByRole("heading", { name: "Tenant lifecycle", exact: true })
      .waitFor();
    await item().waitFor();
    const text = await item().innerText();
    assert.match(text, /MEMBER_INVITATION by EMAIL/);
    assert.match(text, /Failed · 1 attempts · SYNTHETIC_FAILURE/);
    // The directory carries no address or reference.
    assert(!text.includes("requeue-" + unique));
    await page
      .getByRole("region", { name: "Workers" })
      .getByRole("listitem", { name: "Worker requeue-failing" })
      .waitFor();
  });

  await test("Re-queue needs a reason; a lost response is retried with the same operation", async () => {
    const opener = item().getByRole("button", {
      name: "Re-queue",
      exact: true,
    });
    await opener.click();
    assert.equal(await opener.first().getAttribute("aria-expanded"), "true");
    const form = item().getByRole("form", { name: "Re-queue" });
    const reason = form.getByLabel("Reason", { exact: true });
    // The browser refuses an empty reason before anything is sent.
    assert.equal(await reason.evaluate((el) => el.required), true);
    await reason.fill("Mailbox restored after the synthetic outage " + unique);
    await item().scrollIntoViewIfNeeded();
    await page.screenshot({ path: evidencePath("requeue-dead.png") });
    const suffix = "/deliveries/" + dead.event_id + "/actions/requeue";
    const sent = [];
    let original = null,
      active = true;
    await page.route(
      (url) => url.pathname.endsWith(suffix),
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
    const submit = form.getByRole("button", { name: "Re-queue", exact: true });
    try {
      await submit.click();
      // The failure is announced inside the open form, beside its button.
      await form.getByRole("alert").waitFor();
      assert(original, "the first attempt reached the server");
      const retried = await receipt(page, () => submit.click(), suffix);
      assert.equal(sent.length, 2);
      assert.deepEqual(sent[1], sent[0]);
      assert.equal(sent[0].expected_revision, dead.revision);
      assert.deepEqual(retried, original);
      assert.equal(retried.state, "PENDING");
      assert.equal(retried.previous_state, "DEAD");
      assert.equal(retried.attempts, 0);
    } finally {
      active = false;
    }
    await panel()
      .getByRole("status")
      .filter({ hasText: "delivery re-queued" })
      .waitFor();
    await item().waitFor({ state: "detached" });
    assert.equal(
      (await attention()).some((i) => i.event_id === dead.event_id),
      false,
    );
  });

  await test("The next worker iteration sends the re-queued delivery", async () => {
    const summary = runWorkerOnce(local, "requeue-worker");
    assert(summary.sent >= 1, JSON.stringify(summary));
    const messages = await sinkMessages(local);
    assert.equal(
      messages.filter((m) => m.event_id === dead.event_id).length,
      1,
    );
    await panel()
      .getByRole("button", { name: "Refresh deliveries", exact: true })
      .click();
    await panel().getByText("No delivery needs attention.").waitFor();
    await page
      .getByRole("region", { name: "Workers" })
      .getByRole("button", { name: "Refresh workers", exact: true })
      .click();
    await page
      .getByRole("region", { name: "Workers" })
      .getByRole("listitem", { name: "Worker requeue-worker" })
      .waitFor();
  });

  await test("Only platform operators can read or re-queue deliveries", async () => {
    const author = await as("author");
    const listing = await author
      .context()
      .request.get(base + "/v1/platform/deliveries");
    assert.equal(listing.status(), 404);
    await nav(author, "Tenant lifecycle");
    await author
      .getByRole("heading", { name: "Tenant lifecycle", exact: true })
      .waitFor();
    assert.equal(
      await author
        .getByRole("region", { name: "Deliveries needing attention" })
        .count(),
      0,
    );
  });

  await test("The operator console stays within a 390 px mobile width", async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    await panel().waitFor();
    assert(await noHorizontalScroll(page), "console overflows at 390 px");
    await page.screenshot({
      path: evidencePath("requeue-mobile.png"),
      fullPage: true,
    });
    assert.deepEqual(errors, []);
  });
}, "Requeue browser run");
