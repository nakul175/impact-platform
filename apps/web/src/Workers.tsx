import { useEffect, useRef, useState, type FormEvent } from "react";

type Props = {
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
};
const states: Record<string, string> = {
  RUNNING: "Running",
  STOPPING: "Stopping",
  STOPPED: "Stopped",
};
const actionLabels: Record<string, string> = {
  requeue: "Re-queue",
  release: "Release hold",
};
const deliveryConflicts: Record<string, string> = {
  DELIVERY_NOT_DEAD: "This delivery is no longer failed. Refresh the list.",
  DELIVERY_NOT_HELD: "This delivery is no longer held. Refresh the list.",
  DELIVERY_NOT_PENDING:
    "A worker is holding this delivery. Wait for its lease to end, then refresh.",
  TENANT_NOT_ACTIVE:
    "The tenant must be active again before deliveries resume.",
};
// Operator-only liveness of the outbox workers (GET /v1/platform/workers). Heartbeats carry no
// tenant data; a running worker that has not beaten within the stale window is flagged.
export function Workers({ request, explain }: Props) {
  return (
    <>
      <WorkerHeartbeats request={request} explain={explain} />
      <DeliveryAttention request={request} explain={explain} />
    </>
  );
}

function WorkerHeartbeats({ request, explain }: Props) {
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

// Operator re-queue (platform API 1.5.0): failed (DEAD) deliveries and deliveries held by a
// suspension, without addresses or references. Nothing resumes automatically: each row needs a
// reason, fresh authentication and an Active tenant; the server re-checks every condition.
function DeliveryAttention({ request, explain }: Props) {
  const [list, setList] = useState<any>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState<{ item: any; action: string } | null>(null);
  const retry = useRef({ key: "", operation: "" });
  function describe(e: any) {
    return (e && deliveryConflicts[e.reason]) || explain(e);
  }
  async function load(signal?: AbortSignal) {
    try {
      const result = await request("/v1/platform/deliveries", { signal });
      if (!signal?.aborted) {
        setList(result);
        setError("");
      }
    } catch (e) {
      if (!signal?.aborted) setError(describe(e));
    }
  }
  useEffect(() => {
    const c = new AbortController();
    load(c.signal);
    return () => c.abort();
  }, []);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!open) return;
    const reason = String(new FormData(event.currentTarget).get("reason"));
    const { item, action } = open;
    const path = `/v1/platform/tenants/${item.tenant_id}/deliveries/${item.event_id}/actions/${action}`;
    const key = JSON.stringify([path, item.revision, reason]);
    if (retry.current.key !== key)
      retry.current = { key, operation: crypto.randomUUID() };
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await request(path, {
        method: "POST",
        body: JSON.stringify({
          operation_id: retry.current.operation,
          expected_revision: item.revision,
          data: { reason },
        }),
      });
      retry.current = { key: "", operation: "" };
      setOpen(null);
      setNotice(
        `${item.operating_name}: delivery ${action === "requeue" ? "re-queued" : "released"}. A worker will send it if it is still current.`,
      );
      await load();
    } catch (e) {
      setError(describe(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel" aria-label="Deliveries needing attention">
      <h2>Deliveries needing attention</h2>
      <p>
        Failed deliveries and deliveries held by a suspension are never resent
        automatically. Re-queue or release one only after checking why it
        stopped; the reason is recorded.
      </p>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {notice && (
        <div className="success" role="status">
          {notice}
        </div>
      )}
      <div className="toolbar">
        <button className="secondary" disabled={busy} onClick={() => load()}>
          Refresh deliveries
        </button>
      </div>
      {!list ? (
        !error && <p role="status">Loading deliveries…</p>
      ) : !list.items.length ? (
        <p>No delivery needs attention.</p>
      ) : (
        <ul className="worker-list">
          {list.items.map((d: any) => (
            <li key={d.event_id} aria-label={`Delivery ${d.event_id}`}>
              <strong>{d.operating_name}</strong> ({d.lifecycle_state}) ·{" "}
              {d.template} by {d.channel}
              <br />
              {d.state === "DEAD" ? "Failed" : d.state}
              {d.held ? " · held by suspension" : ""} · {d.attempts} attempts
              {d.last_error_class ? " · " + d.last_error_class : ""}
              {d.last_attempt_at
                ? " · last attempt " +
                  new Date(d.last_attempt_at).toLocaleString()
                : ""}
              <div className="toolbar">
                {d.permitted_actions.map((a: string) => (
                  <button
                    key={a}
                    className="secondary"
                    disabled={busy}
                    onClick={() => {
                      setOpen({ item: d, action: a });
                      setError("");
                    }}
                  >
                    {actionLabels[a]}
                  </button>
                ))}
                {!d.permitted_actions.length && (
                  <span>No action until the tenant is active again.</span>
                )}
              </div>
              {open && open.item.event_id === d.event_id && (
                <form onSubmit={submit} aria-label={actionLabels[open.action]}>
                  <label>
                    Reason
                    <textarea name="reason" required maxLength={1000} />
                  </label>
                  <div className="toolbar">
                    <button className="primary" disabled={busy}>
                      {actionLabels[open.action]}
                    </button>
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => setOpen(null)}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
