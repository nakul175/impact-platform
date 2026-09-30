import { useEffect, useState } from "react";

type Props = {
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
};
const states: Record<string, string> = {
  RUNNING: "Running",
  STOPPING: "Stopping",
  STOPPED: "Stopped",
};
// Operator-only liveness of the outbox workers (GET /v1/platform/workers). Heartbeats carry no
// tenant data; a running worker that has not beaten within the stale window is flagged.
export function Workers({ request, explain }: Props) {
  const [workers, setWorkers] = useState<any>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function load(signal?: AbortSignal) {
    setBusy(true);
    try {
      const result = await request("/v1/platform/workers", { signal });
      if (!signal?.aborted) {
        setWorkers(result);
        setError("");
      }
    } catch (e) {
      if (!signal?.aborted) setError(explain(e));
    } finally {
      if (!signal?.aborted) setBusy(false);
    }
  }
  useEffect(() => {
    const c = new AbortController();
    load(c.signal);
    return () => c.abort();
  }, []);
  return (
    <section className="panel" aria-label="Workers">
      <h2>Workers</h2>
      <p>
        Background workers deliver notices and emails. A worker whose last
        heartbeat is older than {workers ? workers.stale_after_seconds : 60}{" "}
        seconds while running is shown as stale.
      </p>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      <div className="toolbar">
        <button className="secondary" disabled={busy} onClick={() => load()}>
          Refresh workers
        </button>
      </div>
      {!workers ? (
        !error && <p role="status">Loading workers…</p>
      ) : !workers.items.length ? (
        <p>No worker has reported a heartbeat.</p>
      ) : (
        <ul className="worker-list">
          {workers.items.map((w: any) => (
            <li key={w.worker_id} aria-label={`Worker ${w.worker_id}`}>
              <strong>{w.worker_id}</strong> ·{" "}
              {w.stale ? "Stale" : states[w.state] || w.state} · build {w.build}
              <br />
              Last heartbeat: {new Date(w.beat_at).toLocaleString()}
              {w.stopped_at
                ? "; stopped " + new Date(w.stopped_at).toLocaleString()
                : ""}
              <br />
              {w.iterations} iterations · {w.sent} sent · {w.retried} retried ·{" "}
              {w.dead} failed permanently · {w.failures} tenant errors
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
