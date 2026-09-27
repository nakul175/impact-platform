import React, { useEffect, useState } from "react";

type Row = {
  object_id: string;
  revision_id: string;
  lifecycle_state: string;
  updated_at: string;
  data: Record<string, any>;
};

type Props = {
  base: string;
  capabilities: string[];
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
};

export function WorkCenterPanel({
  base,
  capabilities,
  request,
  explain,
}: Props) {
  const [tasks, setTasks] = useState<Row[]>([]);
  const [notices, setNotices] = useState<Row[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState("");
  const [epoch, setEpoch] = useState(0);
  const can = (capability: string) => capabilities.includes(capability);

  useEffect(() => {
    const controller = new AbortController();
    async function load(route: string) {
      const rows: Row[] = [];
      let cursor = "";
      do {
        const page = await request(
          base +
            route +
            "?limit=100" +
            (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""),
          { signal: controller.signal },
        );
        rows.push(...page.items);
        cursor = page.next_cursor || "";
        if (rows.length >= 500 && cursor)
          throw new Error(
            "More than 500 personal work records are available. Narrowing and archive controls are still required.",
          );
      } while (cursor);
      return rows.reverse();
    }
    setError("");
    Promise.all([
      can("work-items.read") ? load("work-items") : Promise.resolve([]),
      can("notifications.read") ? load("notifications") : Promise.resolve([]),
    ])
      .then(([work, messages]) => {
        setTasks(work);
        setNotices(messages);
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError(explain(e));
      });
    return () => controller.abort();
  }, [base, epoch]);

  async function recalculate(row: Row) {
    setBusy(row.object_id);
    setError("");
    try {
      await request(
        base + "work-items/" + row.object_id + "/actions/recalculate",
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            expected_revision: row.revision_id,
            data: {},
          }),
        },
      );
      setNotice("Recalculation completed from current approved inputs.");
      setEpoch((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy("");
    }
  }

  async function acknowledge(row: Row) {
    setBusy(row.object_id);
    setError("");
    try {
      await request(
        base + "notifications/" + row.object_id + "/actions/acknowledge",
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            expected_revision: row.revision_id,
            data: {},
          }),
        },
      );
      setNotice(
        "Notice acknowledged. Its underlying task remains independent.",
      );
      setEpoch((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy("");
    }
  }

  return (
    <section aria-label="My work and notifications">
      <p>
        Only work assigned to your current identity is shown. Notices contain a
        safe reference; opening an underlying record always rechecks access.
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
      <section className="panel">
        <div className="panel-toolbar">
          <div>
            <h2>Assigned tasks</h2>
            <small>Current work for your signed-in identity</small>
          </div>
          <button
            className="secondary"
            aria-label="Refresh work centre"
            onClick={() => setEpoch((value) => value + 1)}
          >
            ↻
          </button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Task</th>
                <th>Status</th>
                <th>Due</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((row) => (
                <tr key={row.object_id}>
                  <td>
                    <strong>{row.data.title || "Assigned work"}</strong>
                    {row.data.calculation && (
                      <small className="block">
                        {row.data.calculation.affected_result_count} result
                        {row.data.calculation.affected_result_count === 1
                          ? ""
                          : "s"}{" "}
                        affected ·{" "}
                        {row.data.calculation.reason_codes.join(", ")}
                      </small>
                    )}
                  </td>
                  <td>
                    <span
                      className={"badge " + row.lifecycle_state.toLowerCase()}
                    >
                      {row.lifecycle_state}
                    </span>
                  </td>
                  <td>
                    {row.data.due_at
                      ? new Date(row.data.due_at).toLocaleString()
                      : "—"}
                  </td>
                  <td>
                    {row.lifecycle_state === "Open" &&
                      row.data.calculation?.state === "PENDING" &&
                      can("indicator.calculate") && (
                        <button
                          className="primary"
                          disabled={busy === row.object_id}
                          onClick={() => void recalculate(row)}
                        >
                          Recalculate
                        </button>
                      )}
                    {row.data.calculation?.replacement_result_id && (
                      <small className="block">
                        Result{" "}
                        {row.data.calculation.replacement_result_id.slice(0, 8)}
                      </small>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!tasks.length && <p>No assigned tasks.</p>}
        </div>
      </section>
      <section className="panel">
        <div className="panel-toolbar">
          <div>
            <h2>Notifications</h2>
            <small>Minimal references, separate from task completion</small>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Notice</th>
                <th>Received</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {notices.map((row) => (
                <tr key={row.object_id}>
                  <td>
                    {String(row.data.notice_class || "NOTICE").replaceAll(
                      "_",
                      " ",
                    )}
                    <small className="block">
                      Reference {String(row.data.safe_reference).slice(0, 8)}
                    </small>
                  </td>
                  <td>{new Date(row.updated_at).toLocaleString()}</td>
                  <td>
                    {row.data.acknowledged_at ? (
                      <span className="badge completed">Acknowledged</span>
                    ) : can("notifications.acknowledge") ? (
                      <button
                        disabled={busy === row.object_id}
                        onClick={() => void acknowledge(row)}
                      >
                        Acknowledge
                      </button>
                    ) : (
                      <span className="badge unread">Unread</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!notices.length && <p>No notifications.</p>}
        </div>
      </section>
    </section>
  );
}
