// export-browser: worker-rendered PDF/XLSX/DOCX exports of an approved report package (v0.23).
// The approved package is prepared through the API. The browser requests each format and
// watches the job status, which the panel polls, move from Queued to Succeeded after one worker
// iteration (browser modes start no worker process: `python -m impact_api.worker --once` runs
// against this run's worker.json); downloads go through the UI, and a disclosure that includes
// the PDF reaches the named recipient.
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { createHash } from "node:crypto";
import { runWorkerOnce } from "./worker-run.mjs";
import {
  harness,
  ok,
  read,
  receipt,
  nav,
  loadUntil,
  noHorizontalScroll,
  approveCandidate,
  fixture,
  records,
  tenant,
  base,
  local,
  evidencePath,
} from "./qa-harness.mjs";

const { as, test, finish, errors, quietly } = await harness("export-browser");
const unique = Date.now().toString(),
  heading = "Export package " + unique;
const FORMATS = [
  ["PDF", "PDF report", "application/pdf"],
  [
    "XLSX",
    "XLSX bound values",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  ],
  [
    "DOCX",
    "DOCX report",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ],
];
const ZIP = Buffer.from("504b0304", "hex");
let report, jobs, disclosureId;

async function approvedReport() {
  const created = await ok("author", "reports", {
    template_version: records.report_template.revision_id,
    snapshot_id: records.snapshot.object_id,
    language: "en",
    audience_class: "INTERNAL",
    sections: [
      {
        section_code: "results",
        heading,
        narrative: "The verified result is {{water}}.",
        bindings: [
          {
            binding_code: "water",
            result_revision: records.pooled_result.revision_id,
            display_decimals: 2,
            unit: "PERCENT",
          },
        ],
        evidence_revisions: [records.evidence_a.revision_id],
      },
    ],
  });
  const template = (await read("workflow-templates")).items[0];
  await ok(
    "author",
    "reports/" + created.object_id + "/actions/submit",
    { workflow_version: template.revision_id },
    "POST",
    created.revision_id,
  );
  await approveCandidate(created.object_id, "Approved package for exports");
  return read("reports/" + created.object_id);
}

await finish(async () => {
  report = await approvedReport();
  assert.equal(report.lifecycle_state, "Approved");
  let page = await as("author");
  const exportsPanel = () =>
    page.getByRole("region", { name: "Report exports" });
  const row = (format) =>
    exportsPanel()
      .locator("tbody tr")
      .filter({ has: page.getByRole("cell", { name: format, exact: true }) });
  async function open() {
    await nav(page, "Reports");
    const entry = await loadUntil(
      page,
      page.getByRole("button", { name: heading, exact: true }),
    );
    await entry.click();
    await exportsPanel().waitFor();
  }

  await test("Request PDF, XLSX and DOCX renderings of the approved package", async () => {
    await open();
    await exportsPanel()
      .getByText("No export has been requested for this revision.")
      .waitFor();
    jobs = {};
    for (const [format, name] of FORMATS) {
      const button = exportsPanel().getByRole("button", {
        name: "Request " + name,
        exact: true,
      });
      const queued = await receipt(
        page,
        () => button.click(),
        "/actions/export",
      );
      jobs[format] = queued;
      await row(format).getByText("Queued", { exact: false }).waitFor();
      // One open export per format: the request button is disabled while it is open.
      assert.equal(await button.isDisabled(), true);
    }
    const listed = (await read("reports/" + report.object_id + "/exports"))
      .items;
    assert.deepEqual(listed.map((item) => item.state).sort(), [
      "Queued",
      "Queued",
      "Queued",
    ]);
  });

  await test("One worker iteration renders them; the panel moves to Succeeded on its own", async () => {
    const summary = await quietly(() =>
      runWorkerOnce(local, "export-browser-worker"),
    );
    assert.equal(summary.exports_succeeded, 3, JSON.stringify(summary));
    // No reload: the panel polls while an export is open.
    for (const [format] of FORMATS)
      await row(format)
        .getByRole("link", { name: "Download " + format, exact: true })
        .waitFor({ timeout: 30000 });
    for (const [format] of FORMATS)
      await row(format).getByText("Succeeded", { exact: false }).waitFor();
    await exportsPanel().scrollIntoViewIfNeeded();
    await page.screenshot({ path: evidencePath("export-succeeded.png") });
  });

  await test("Each rendering downloads through the UI with its signature and media type", async () => {
    const listed = (await read("reports/" + report.object_id + "/exports"))
      .items;
    for (const [format, , media] of FORMATS) {
      const link = row(format).getByRole("link", {
        name: "Download " + format,
        exact: true,
      });
      const [download] = await Promise.all([
        page.waitForEvent("download"),
        link.click(),
      ]);
      const extension = format.toLowerCase();
      assert(
        download.suggestedFilename().endsWith("." + extension),
        download.suggestedFilename(),
      );
      const bytes = await fs.readFile(await download.path());
      if (format === "PDF")
        assert.equal(bytes.subarray(0, 5).toString(), "%PDF-");
      else assert(bytes.subarray(0, 4).equals(ZIP), format + " is a zip");
      if (format === "XLSX") assert(bytes.includes("xl/workbook.xml"));
      if (format === "DOCX") assert(bytes.includes("word/document.xml"));
      const item = listed.find((x) => x.format === format);
      assert.equal(
        createHash("sha256").update(bytes).digest("hex"),
        item.content_sha256,
      );
      const response = await page
        .context()
        .request.get(base + (await link.getAttribute("href")));
      const headers = response.headers();
      assert(
        headers["content-type"].startsWith(media),
        headers["content-type"],
      );
      assert(headers["content-disposition"].startsWith("attachment"));
      assert.equal(headers["x-content-type-options"], "nosniff");
    }
  });

  await test("Include the PDF in a disclosure; the named recipient downloads it", async () => {
    await page
      .getByRole("button", {
        name: "Request controlled publication",
        exact: true,
      })
      .click();
    const label = (name) => page.getByLabel(name, { exact: true });
    await label("Publication recipient").selectOption(fixture.member_partner);
    await label("Publication purpose").selectOption("PARTNER_REPORTING");
    await page
      .getByRole("checkbox", {
        name: "PDF (must already be rendered for this revision)",
      })
      .check();
    await label("Disclosure review template").selectOption({ index: 1 });
    const requested = await receipt(
      page,
      () =>
        page
          .getByRole("button", {
            name: "Request disclosure review",
            exact: true,
          })
          .click(),
      "/disclosure-requests",
    );
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    const workflow = await read("workflows/" + requested.object_id, "reviewer");
    disclosureId = workflow.data.candidate_id;
    const candidate = await read(
      "workflows/" + workflow.object_id + "/candidate",
      "reviewer",
    );
    const pinned = candidate.record.data.export_artifacts;
    assert.deepEqual(
      pinned.map((p) => [p.format, p.job_id]),
      [["PDF", jobs.PDF.job_id]],
    );
    await approveCandidate(disclosureId, "Recipient, purpose and PDF checked");
    await ok(
      "reviewer",
      "reports/" + report.object_id + "/actions/publish",
      {
        approved_candidate_revision: report.revision_id,
        disclosure_id: disclosureId,
      },
      "POST",
      report.revision_id,
    );
    const partner = await as("partner");
    const publication =
      base + "/v1/tenants/" + tenant + "/publications/" + disclosureId;
    const pdf = await partner
      .context()
      .request.get(publication + "/download.pdf");
    assert.equal(pdf.status(), 200);
    const body = await pdf.body();
    assert.equal(body.subarray(0, 5).toString(), "%PDF-");
    assert.equal(
      createHash("sha256").update(body).digest("hex"),
      pinned[0].content_sha256,
    );
    assert(pdf.headers()["content-disposition"].startsWith("attachment"));
    // Formats that were not disclosed stay unavailable, and the author is not a recipient.
    for (const extension of ["xlsx", "docx"])
      assert.equal(
        (
          await partner
            .context()
            .request.get(publication + "/download." + extension)
        ).status(),
        404,
      );
    assert.equal(
      (
        await page.context().request.get(publication + "/download.pdf")
      ).status(),
      404,
    );
  });

  await test("The exports panel stays within a 390 px mobile width", async () => {
    page = await as("author");
    await page.keyboard.press("Escape");
    await page.setViewportSize({ width: 390, height: 844 });
    await open();
    assert(await noHorizontalScroll(page), "exports panel overflows at 390 px");
    await page.screenshot({
      path: evidencePath("export-mobile.png"),
      fullPage: true,
    });
    assert.deepEqual(errors, []);
  });
}, "Export browser run");
