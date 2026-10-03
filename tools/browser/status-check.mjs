// status-browser: the service-notice banner (release 0.27, VF-AVL-002). The API of this run reads
// the operations status file named by IMPACT_OPS_STATUS_FILE (the Makefile points it into .local);
// this check writes a degraded document there (the server's alert check would), signs in as a
// member and as a platform operator, and expects the plain-language notices for everyone, the
// detail and the on-call line for the operator only, no banner once the file is healthy again, and
// the client-side database-unavailable notice when the status call itself answers 503.
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import {
  harness,
  nav,
  noHorizontalScroll,
  root,
  evidencePath,
} from "./qa-harness.mjs";

const { as, test, finish, errors } = await harness("status-browser");
const statusFile = process.env.IMPACT_OPS_STATUS_FILE;
assert(
  statusFile && path.isAbsolute(statusFile),
  "IMPACT_OPS_STATUS_FILE must name an absolute path (make browser sets it)",
);
const onCallFile = path.join(path.dirname(statusFile), "on-call.json");
const stamp = () => new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
const degraded = {
  operations: { checked_at: stamp() },
  alerts: [
    {
      code: "WORKER_STALE",
      severity: "critical",
      message:
        "No running worker has reported within 120 seconds (newest beat 900 s ago).",
      target: "",
    },
    {
      code: "CONTAINER_UNHEALTHY",
      severity: "critical",
      message: "mailsink is exited.",
      target: "mailsink",
    },
    {
      code: "DISK_LOW",
      severity: "critical",
      message: "root: 700 MB free (0.9 %).",
      target: "root",
    },
    {
      code: "RESTORE_DRILL_STALE",
      severity: "warning",
      message: "No restore drill in the last 8 days.",
      target: "",
    },
  ],
};
const healthy = { operations: { checked_at: stamp() }, alerts: [] };

async function writeStatus(document) {
  await fs.mkdir(path.dirname(statusFile), { recursive: true });
  await fs.writeFile(statusFile, JSON.stringify(document, null, 2) + "\n");
}

const banner = (page) =>
  page.getByRole("status", { name: "Service notice", exact: true });

await finish(async () => {
  await writeStatus(degraded);
  await fs.copyFile(path.join(root, "deploy/on-call.example.json"), onCallFile);

  const member = await as("author");
  await test("A member sees plain-language notices and no detail", async () => {
    await banner(member).waitFor();
    const text = await banner(member).innerText();
    assert.match(text, /Service notice:/);
    assert.match(text, /Email and in-app notices are delayed/);
    assert.match(
      text,
      /Report files \(PDF, XLSX and DOCX\) are not being produced/,
    );
    assert.match(text, /Email delivery is paused/);
    assert.match(text, /File storage is nearly full/);
    // Closed catalogue only: no alert code, figure, service or rota reaches a member.
    for (const leak of [
      "WORKER_STALE",
      "CONTAINER",
      "DISK_LOW",
      "mailsink",
      "900",
      "On call",
    ])
      assert(!text.includes(leak), "leaked " + leak + " in: " + text);
    assert.equal(
      await banner(member)
        .getByRole("button", { name: "Details for operators" })
        .count(),
      0,
    );
    await noHorizontalScroll(member);
    await member.screenshot({ path: evidencePath("status-member.png") });
  });

  const operator = await as("admin");
  await test("A platform operator opens the detail: alert codes and who is on call", async () => {
    await banner(operator).waitFor();
    await banner(operator)
      .getByRole("button", { name: "Details for operators", exact: true })
      .click();
    // Open, the same button reads "Hide details".
    const toggle = banner(operator).getByRole("button", {
      name: "Hide details",
      exact: true,
    });
    assert.equal(await toggle.getAttribute("aria-expanded"), "true");
    const text = await banner(operator).innerText();
    assert.match(text, /Observed: OPERATIONS_CHECK/);
    assert.match(text, /WORKER_STALE/);
    assert.match(text, /CONTAINER_UNHEALTHY critical · mailsink/);
    assert.match(text, /RESTORE_DRILL_STALE/);
    assert.match(
      text,
      /On call: Server owner \(example\) · \(Engineer on call\)/,
    );
    await operator.screenshot({ path: evidencePath("status-operator.png") });
  });

  await test("The Workers panel of the tenant console shows who is on call", async () => {
    await nav(operator, "Tenant lifecycle");
    await operator
      .getByRole("heading", { name: "Tenant lifecycle", exact: true })
      .waitFor();
    await banner(operator).waitFor();
    const line = operator.getByLabel("Who is on call", { exact: true });
    await line.waitFor();
    // The line says "Reading the on-call rota…" until its own GET /v1/status answers; on PGlite
    // that read shares the single connection with the banner's poll and the panel's other reads,
    // so wait for the placeholder to go before reading the line (it failed once at integration).
    await operator
      .getByText("Reading the on-call rota…", { exact: true })
      .waitFor({ state: "detached" });
    assert.match(await line.innerText(), /^On call: Server owner \(example\)/);
    await noHorizontalScroll(operator);
  });

  await test("A healthy check removes the banner", async () => {
    await writeStatus(healthy);
    const answered = member.waitForResponse(
      (r) => new URL(r.url()).pathname === "/v1/status",
    );
    await member.reload();
    const response = await answered;
    assert.equal((await response.json()).state, "OK");
    await member
      .getByRole("heading", { name: "Programme portfolio", exact: true })
      .waitFor();
    assert.equal(await banner(member).count(), 0);
  });

  await test("When the status call itself fails for the database, the client says so", async () => {
    const statusUrl = (url) => url.pathname === "/v1/status";
    await member.route(statusUrl, (route) =>
      route.fulfill({
        status: 503,
        contentType: "application/json",
        body: JSON.stringify({
          code: "SERVICE_UNAVAILABLE",
          message: "The service is unavailable.",
          retryable: true,
          correlation_id: "00000000-0000-4000-8000-000000000000",
          permitted_actions: [],
          reason_code: "DATABASE_UNAVAILABLE",
        }),
      }),
    );
    try {
      await member.reload();
      await banner(member).waitFor();
      const text = await banner(member).innerText();
      assert.match(
        text,
        /The database is unavailable\. Nothing can be read or saved/,
      );
      assert.equal(await banner(member).getAttribute("data-state"), "OUTAGE");
      await member.screenshot({ path: evidencePath("status-outage.png") });
    } finally {
      await member.unroute(statusUrl);
    }
  });

  assert.deepEqual(errors, []);
}, "status-browser run");
