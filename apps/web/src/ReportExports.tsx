import { useEffect, useState } from "react";
import { usePendingOperations } from "./operations";

type Row = {
  object_id: string;
  revision_id: string;
  lifecycle_state: string;
};
type Export = {
  job_id: string;
  report_revision: string;
  format: "PDF" | "XLSX" | "DOCX";
  state: string;
  attempts: number;
  last_error_class: string | null;
  cancellation_requested: boolean;
  cancellation_outcome?: string | null;
  requested_at: string;
  completed_at: string | null;
  content_sha256: string | null;
  size_bytes?: number | null;
};

const FORMATS = [
  ["PDF", "PDF report"],
  ["XLSX", "XLSX bound values"],
  ["DOCX", "DOCX report"],
] as const;

/**
 * Worker-rendered exports of an approved, frozen report package (v0.23). Requesting one queues a
 * job; the worker renders it; a succeeded export can be downloaded (each download is logged) and
 * offered to named recipients through a new disclosure. Shown only with report.export, which the
 * server checks again on every call.
 */
export function ReportExports({
  base,
  row,
  request,
  explain,
}: {
  base: string;
  row: Row;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
}) {
  const [items, setItems] = useState<Export[] | null>(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [tick, setTick] = useState(0);
  const pending = usePendingOperations();
  const path = base + "reports/" + row.object_id + "/exports";
  useEffect(() => {
    const c = new AbortController();
    request(path, { signal: c.signal })
      .then((x) => {
        if (!c.signal.aborted) setItems(x.items);
      })
      .catch((e) => {
        if (!c.signal.aborted) setError(explain(e));
      });
    return () => c.abort();
  }, [path, row.revision_id, tick]);
  const open = (items || []).some((item) =>
    ["Queued", "Running"].includes(item.state),
  );
  useEffect(() => {
    if (!open) return;
    const timer = window.setTimeout(() => setTick((t) => t + 1), 4000);
    return () => window.clearTimeout(timer);
  }, [open, tick]);
  async function act(action: string, data: Record<string, string>) {
    const key = action + ":" + JSON.stringify(data);
    setBusy(true);
    setError("");
    try {
      await request(base + "reports/" + row.object_id + "/actions/" + action, {
        method: "POST",
        body: JSON.stringify({
          operation_id: pending.id(key, data),
          expected_revision: row.revision_id,
          data,
        }),
      });
      pending.done(key);
      setTick((t) => t + 1);
    } catch (e) {
      setError(
        explain(e),
      ); /* The identifier is kept: a retry repeats the same command. */
    } finally {
      setBusy(false);
    }
  }
  const current = (items || []).filter(
    (item) => item.report_revision === row.revision_id,
  );
  return (
    <section className="readiness" aria-label="Report exports">
      <h3>Rendered exports</h3>
      <p className="muted">
        PDF, XLSX and DOCX renderings of this approved package, produced by the
        background worker from the locked snapshot. Numbers are the stored
        displayed values; nothing is recalculated.
      </p>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      <div className="dialog-actions">
        {FORMATS.map(([format, label]) => (
          <button
            key={format}
            className="secondary"
            disabled={
              busy ||
              current.some(
                (item) =>
                  item.format === format &&
                  !["Failed", "Cancelled"].includes(item.state),
              )
            }
            onClick={() => act("export", { format })}
          >
            Request {label}
          </button>
        ))}
      </div>
      {items === null && !error ? (
        <p>Loading exports…</p>
      ) : current.length === 0 ? (
        <p className="muted">No export has been requested for this revision.</p>
      ) : (
        <table>
          <caption className="sr-only">Exports of this report revision</caption>
          <thead>
            <tr>
              <th scope="col">Format</th>
              <th scope="col">Status</th>
              <th scope="col">SHA-256</th>
              <th scope="col">Action</th>
            </tr>
          </thead>
          <tbody>
            {current.map((item) => (
              <tr key={item.job_id}>
                <td>{item.format}</td>
                <td>
                  {item.state}
                  {item.last_error_class
                    ? " (" + item.last_error_class.replaceAll("_", " ") + ")"
                    : ""}
                  {item.cancellation_requested && item.state !== "Cancelled"
                    ? " · cancellation requested"
                    : ""}
                </td>
                <td>
                  <code>
                    {item.content_sha256
                      ? item.content_sha256.slice(0, 16) + "…"
                      : "—"}
                  </code>
                </td>
                <td>
                  {item.state === "Succeeded" && (
                    <a
                      className="secondary button"
                      href={path + "/" + item.job_id + "/download"}
                    >
                      Download {item.format}
                    </a>
                  )}
                  {item.state === "Queued" && !item.cancellation_requested && (
                    <button
                      className="secondary danger"
                      disabled={busy}
                      onClick={() =>
                        act("cancel-export", { job_id: item.job_id })
                      }
                    >
                      Cancel
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
