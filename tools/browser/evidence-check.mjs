// evidence-browser: evidence files on an observation (v0.22). A draft observation is prepared
// through the API; upload, scan verdict, attachment, mediated download, the EICAR refusal and
// the tenant boundary are exercised in the browser (and its own cookie sessions).
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { createHash } from "node:crypto";
import {
  harness,
  ok,
  api,
  read,
  receipt,
  nav,
  loadUntil,
  noHorizontalScroll,
  records,
  tenant,
  base,
  evidencePath,
} from "./qa-harness.mjs";

const { as, test, finish, errors } = await harness("evidence-browser");
const unique = Date.now().toString(),
  source = "EVD-" + unique,
  marker = Buffer.from("#" + unique + "\n");
// Synthetic files, distinct per run (blobs are content-addressed per tenant).
const png = Buffer.concat([
    Buffer.from("89504e470d0a1a0a0000000d49484452", "hex"),
    Buffer.alloc(17),
    marker,
  ]),
  pdf = Buffer.concat([
    Buffer.from(
      "%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\ntrailer << /Root 1 0 R >>\n%%EOF\n",
    ),
    marker,
  ]),
  // The EICAR anti-virus test file, kept encoded so that the source tree carries no copy.
  eicar = Buffer.concat([
    Buffer.from(
      "WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo=",
      "base64",
    ),
    Buffer.from("\n"),
    marker,
  ]);
let observation, items;

await finish(async () => {
  observation = await ok("author", "observations", {
    source_namespace: "MANUAL",
    source_key: source,
    indicator_id: records.indicator_a.object_id,
    event_at: "2026-08-15T12:00:00Z",
    captured_at: "2026-09-25T10:00:00Z",
    capture_zone: "UTC",
    value_state: "PRESENT",
    value: "80",
    numerator: "8",
    denominator: "10",
    source_version: "1",
    dimension_values: {},
  });
  let page = await as("author");
  const panel = () => page.getByRole("region", { name: "Evidence" });
  const form = () => page.getByRole("form", { name: "Attach evidence" });
  async function open() {
    await nav(page, "Measurement");
    const entry = await loadUntil(
      page,
      page.getByRole("button", { name: source, exact: true }),
    );
    await entry.click();
    await panel().waitFor();
  }
  async function attach(name, mimeType, buffer, type, reason) {
    await form()
      .getByLabel("File (PDF, PNG, JPEG, TXT or CSV, at most 25 MB)")
      .setInputFiles({ name, mimeType, buffer });
    await form().getByLabel("Evidence type").selectOption(type);
    await form().getByLabel("Source").fill("Browser qualification");
    await form().getByLabel("Why it supports this record").fill(reason);
    const completed = page.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        new URL(r.url()).pathname.endsWith("/actions/complete"),
    );
    await form().getByRole("button", { name: "Upload and attach" }).click();
    return (await completed).json();
  }
  const listed = async () =>
    (
      await read(
        "observations/" + observation.object_id + "/evidence",
        "author",
      )
    ).items;

  await test("Attach a PNG: the upload is scanned CLEAN and listed with its scan state", async () => {
    await open();
    await panel()
      .getByText("No evidence is attached to this record.")
      .waitFor();
    const sealed = await attach(
      "photo-" + unique + ".png",
      "image/png",
      png,
      "PHOTOGRAPH",
      "Photograph of the water point",
    );
    assert.equal(sealed.state, "CLEAN");
    assert.equal(sealed.scan_state, "CLEAN");
    await panel()
      .getByRole("status")
      .filter({ hasText: "Evidence attached to this revision." })
      .waitFor();
    const item = panel()
      .getByRole("listitem")
      .filter({ hasText: "photo-" + unique + ".png" });
    await item.getByText("scan CLEAN", { exact: false }).waitFor();
    await item.getByRole("link", { name: "Download" }).waitFor();
    items = await listed();
    assert.equal(items.length, 1);
    assert.equal(items[0].downloadable, true);
    // Attaching does not revise the observation.
    assert.equal(
      (await read("observations/" + observation.object_id)).revision_id,
      observation.revision_id,
    );
    await page.screenshot({ path: evidencePath("evidence-attached.png") });
  });

  await test("Download through the UI returns the exact bytes as a sandboxed attachment", async () => {
    const link = panel()
      .getByRole("listitem")
      .filter({ hasText: "photo-" + unique + ".png" })
      .getByRole("link", { name: "Download" });
    const [download] = await Promise.all([
      page.waitForEvent("download"),
      link.click(),
    ]);
    assert.equal(download.suggestedFilename(), "photo-" + unique + ".png");
    const saved = await fs.readFile(await download.path());
    assert(saved.equals(png), "downloaded bytes differ from the upload");
    const href = await link.getAttribute("href");
    const response = await page.context().request.get(base + href);
    assert.equal(response.status(), 200);
    const headers = response.headers();
    assert.equal(headers["content-type"], "image/png");
    assert(
      headers["content-disposition"].startsWith(
        'attachment; filename="photo-' + unique + '.png"',
      ),
      headers["content-disposition"],
    );
    assert.equal(headers["x-content-type-options"], "nosniff");
    assert.equal(headers["cache-control"], "no-store");
    assert(headers["content-security-policy"].includes("sandbox"));
    assert.equal(
      createHash("sha256")
        .update(await response.body())
        .digest("hex"),
      createHash("sha256").update(png).digest("hex"),
    );
  });

  await test("A PDF is attached as a second evidence item and downloads with its signature", async () => {
    const sealed = await attach(
      "register-" + unique + ".pdf",
      "application/pdf",
      pdf,
      "ATTENDANCE_SHEET",
      "Signed attendance register",
    );
    assert.equal(sealed.scan_state, "CLEAN");
    const item = panel()
      .getByRole("listitem")
      .filter({ hasText: "register-" + unique + ".pdf" });
    await item.getByText("scan CLEAN", { exact: false }).waitFor();
    const href = await item
      .getByRole("link", { name: "Download" })
      .getAttribute("href");
    const response = await page.context().request.get(base + href);
    assert.equal(response.headers()["content-type"], "application/pdf");
    const body = await response.body();
    assert.equal(body.subarray(0, 5).toString(), "%PDF-");
    assert(body.equals(pdf));
  });

  await test("The EICAR test file is INFECTED, refused and never downloadable", async () => {
    const sealed = await attach(
      "eicar-" + unique + ".txt",
      "text/plain",
      eicar,
      "SUPPORTING_DOCUMENT",
      "Anti-virus test file",
    );
    assert.equal(sealed.scan_state, "INFECTED");
    assert.notEqual(sealed.state, "CLEAN");
    await panel()
      .getByRole("alert")
      .filter({ hasText: "flagged by the safety scan" })
      .waitFor();
    assert.equal(
      await panel()
        .getByRole("listitem")
        .filter({ hasText: "eicar-" + unique })
        .count(),
      0,
    );
    assert.equal(
      await panel().getByRole("link", { name: "Download" }).count(),
      2,
    );
    assert.equal((await listed()).length, 2);
    // Neither the UI nor the API can turn the infected upload into evidence.
    const refused = await api("author", "evidence", {
      upload_id: sealed.upload_id,
      evidence_type: "SUPPORTING_DOCUMENT",
      source: "Anti-virus test file",
    });
    assert.equal(refused.status, 409);
    assert.equal(refused.body.reason_code, "UPLOAD_NOT_CLEAN");
    // The refusal is announced beside the button that caused it.
    const alert = form().getByRole("alert");
    await alert.scrollIntoViewIfNeeded();
    const box = await alert.boundingBox();
    assert(box && box.y >= 0 && box.y + box.height <= 560, "alert in view");
    await page.screenshot({ path: evidencePath("evidence-infected.png") });
  });

  await test("Another tenant's session sees nothing of this evidence", async () => {
    const other = await as("other_tenant");
    const path = "/v1/tenants/" + tenant + "/";
    for (const route of [
      "observations/" + observation.object_id + "/evidence",
      "evidence/" + items[0].evidence_id,
      "evidence/" +
        items[0].evidence_id +
        "/content?revision=" +
        items[0].evidence_revision,
    ]) {
      const response = await other.context().request.get(base + path + route);
      assert.equal(response.status(), 404, route);
      assert.equal((await response.json()).code, "RESOURCE_UNAVAILABLE");
    }
    // Its own workspace lists no such observation.
    await nav(other, "Measurement");
    await other
      .getByRole("heading", { name: "Measurement", exact: true })
      .first()
      .waitFor();
    assert.equal(
      await other.getByRole("button", { name: source, exact: true }).count(),
      0,
    );
  });

  await test("The evidence panel stays within a 390 px mobile width", async () => {
    page = await as("author");
    await page.keyboard.press("Escape");
    await page.setViewportSize({ width: 390, height: 844 });
    await open();
    assert(
      await noHorizontalScroll(page),
      "evidence panel overflows at 390 px",
    );
    await page.screenshot({
      path: evidencePath("evidence-mobile.png"),
      fullPage: true,
    });
    assert.deepEqual(errors, []);
  });
}, "Evidence browser run");
