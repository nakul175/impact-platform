import { useEffect, useState, type FormEvent } from "react";
import { usePendingOperations } from "./operations";

type Manifest = {
  export_id: string;
  window_start: string;
  window_end: string;
  purpose: string;
  page: number;
  first_sequence: number | null;
  event_count: number;
  complete: boolean;
  content_sha256: string;
  chain_start: string;
  chain_end: string;
  generated_at: string;
  seal: { algorithm: string; key_id: string; value: string };
};
type Page = { manifest: Manifest; content: string; next_cursor: string | null };

const PURPOSES = [
  ["SECURITY_REVIEW", "Security review"],
  ["INCIDENT_INVESTIGATION", "Incident investigation"],
  ["REGULATORY_REQUEST", "Regulatory request"],
  ["INTERNAL_AUDIT", "Internal audit"],
] as const;

const day = (offset: number) =>
  new Date(Date.now() + offset * 86400000).toISOString().slice(0, 10);

/**
 * Audit export (v0.25 part A): one bounded page of this workspace's audit events as JSON Lines with
 * a hash chain and a SHA-256 manifest. Shown only with audit.export; the server checks the grant,
 * the stated purpose and a sign-in within the last five minutes on every page, and records each
 * export as an audit event. The files are built in the browser from the response; nothing is kept.
 */
export function AuditExportPanel({
  base,
  request,
  explain,
}: {
  base: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
}) {
  const [from, setFrom] = useState(day(-30)),
    [to, setTo] = useState(day(0)),
    [purpose, setPurpose] = useState<string>(PURPOSES[0][0]),
    [reason, setReason] = useState(""),
    [page, setPage] = useState<Page | null>(null),
    [links, setLinks] = useState<{ content: string; manifest: string } | null>(
      null,
    ),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const pending = usePendingOperations();
  useEffect(
    () => () => {
      if (links) {
        URL.revokeObjectURL(links.content);
        URL.revokeObjectURL(links.manifest);
      }
    },
    [links],
  );
  function windowEnd() {
    // The end of the chosen day, but never in the future (the server refuses a future window).
    const end = new Date(to + "T00:00:00Z").getTime() + 86400000;
    return new Date(Math.min(end, Date.now() - 1000)).toISOString();
  }
  async function run(cursor?: string) {
    const data: Record<string, unknown> = {
      window_start: new Date(from + "T00:00:00Z").toISOString(),
      window_end: cursor && page ? page.manifest.window_end : windowEnd(),
      purpose,
      reason: reason.trim(),
      limit: 500,
      ...(cursor ? { cursor } : {}),
    };
    if (cursor && page) data.window_start = page.manifest.window_start;
    const key = "audit-export:" + (cursor || "first");
    setBusy(true);
    setError("");
    try {
      const result: Page = await request(base + "audit-exports", {
        method: "POST",
        body: JSON.stringify({ operation_id: pending.id(key, data), data }),
      });
      pending.done(key);
      if (links) {
        URL.revokeObjectURL(links.content);
        URL.revokeObjectURL(links.manifest);
      }
      setLinks({
        content: URL.createObjectURL(
          new Blob([result.content], { type: "application/x-ndjson" }),
        ),
        manifest: URL.createObjectURL(
          new Blob([JSON.stringify(result.manifest, null, 2)], {
            type: "application/json",
          }),
        ),
      });
      setPage(result);
    } catch (e) {
      setError(explain(e)); /* The identifier is kept: a retry repeats it. */
    } finally {
      setBusy(false);
    }
  }
  function submit(event: FormEvent) {
    event.preventDefault();
    setPage(null);
    run();
  }
  const name = page
    ? "audit-" +
      page.manifest.window_start.slice(0, 10) +
      "-page-" +
      page.manifest.page
    : "";
  return (
    <section className="readiness" aria-labelledby="audit-export-title">
      <h3 id="audit-export-title">Audit export</h3>
      <p className="muted">
        Exports this workspace's audit events for a period as JSON Lines with a
        hash chain and a manifest (SHA-256 digest, chain start and end, platform
        seal). Identifiers, action codes and digests only. Each page needs a
        sign-in within the last five minutes, states a purpose and is itself
        recorded in the audit trail.
      </p>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      <form onSubmit={submit} className="form-grid">
        <label>
          From (UTC)
          <input
            type="date"
            value={from}
            max={to}
            onChange={(e) => setFrom(e.target.value)}
            required
          />
        </label>
        <label>
          To (UTC, inclusive)
          <input
            type="date"
            value={to}
            min={from}
            max={day(0)}
            onChange={(e) => setTo(e.target.value)}
            required
          />
        </label>
        <label>
          Export purpose
          <select value={purpose} onChange={(e) => setPurpose(e.target.value)}>
            {PURPOSES.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Export reason
          <input
            value={reason}
            maxLength={2000}
            onChange={(e) => setReason(e.target.value)}
            required
          />
        </label>
        <div className="dialog-actions">
          <button className="primary" disabled={busy || !reason.trim()}>
            Export audit events
          </button>
        </div>
      </form>
      {page && links && (
        <div aria-live="polite">
          <p>
            Page {page.manifest.page}: {page.manifest.event_count} events
            {page.manifest.first_sequence
              ? " (from event " + page.manifest.first_sequence + ")"
              : ""}
            .{" "}
            {page.manifest.complete ? "Export complete." : "More pages remain."}
          </p>
          <p className="muted">
            SHA-256 <code>{page.manifest.content_sha256}</code>, chain end{" "}
            <code>{page.manifest.chain_end}</code>, sealed with key{" "}
            <code>{page.manifest.seal.key_id}</code>.
          </p>
          <div className="dialog-actions">
            <a
              className="secondary"
              href={links.content}
              download={name + ".jsonl"}
            >
              Download events (.jsonl)
            </a>
            <a
              className="secondary"
              href={links.manifest}
              download={name + ".manifest.json"}
            >
              Download manifest
            </a>
            {page.next_cursor && (
              <button
                className="secondary"
                disabled={busy}
                onClick={() => run(page.next_cursor || undefined)}
              >
                Next page
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
