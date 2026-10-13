import React, { useEffect, useRef, useState, type FormEvent } from "react";
import { usePendingOperations } from "./operations";

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
  const [indicators, setIndicators] = useState<Row[]>([]);
  const [assignedIndicators, setAssignedIndicators] = useState<Row[]>([]);
  const [savedViews, setSavedViews] = useState<Row[]>([]);
  const [search, setSearch] = useState("");
  const [rebind, setRebind] = useState<Row | null>(null);
  const [selectedIssue, setSelectedIssue] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState("");
  const [epoch, setEpoch] = useState(0);
  const operations = usePendingOperations();
  const taskRows = useRef<Record<string, HTMLTableRowElement | null>>({});
  const can = (capability: string) => capabilities.includes(capability);
  // Capabilities arrive asynchronously after sign-in; the load below must re-run when they do,
  // otherwise a fast navigation renders an empty view until something else changes epoch.
  const capabilityKey = capabilities.join(" ");

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
      can("indicator-definitions.read")
        ? load("indicator-definitions")
        : Promise.resolve([]),
      can("indicator-instances.read")
        ? load("indicator-instances")
        : Promise.resolve([]),
      can("work-items.read") ? load("saved-views") : Promise.resolve([]),
    ])
      .then(([work, messages, definitions, instances, views]) => {
        setTasks(work);
        setNotices(messages);
        setIndicators(definitions);
        setAssignedIndicators(instances);
        setSavedViews(views);
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError(explain(e));
      });
    return () => controller.abort();
  }, [base, epoch, capabilityKey]);

  const term = search.trim().toLowerCase();
  const matches = (row: Row) =>
    !term ||
    [
      row.data.title,
      row.data.name,
      row.data.code,
      row.data.local_applicability,
      row.data.notice_class,
      row.data.safe_reference,
      row.object_id,
    ]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(term));

  async function saveView(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = new FormData(event.currentTarget);
    const definition = indicators.find(
      (row) => row.object_id === form.get("definition_id"),
    );
    if (!definition) {
      setError("Choose a currently permitted approved definition.");
      return;
    }
    try {
      await request(base + "saved-views", {
        method: "POST",
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          data: {
            title: String(form.get("title") || ""),
            search_text: search,
            definition_id: definition.object_id,
            definition_revision: definition.revision_id,
          },
        }),
      });
      setNotice("Saved view bound to the exact current definition revision.");
      setEpoch((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    }
  }

  async function openView(view: Row) {
    setError("");
    try {
      const definition = await request(
        base + "indicator-definitions/" + view.data.definition_id,
      );
      if (
        definition.lifecycle_state !== "Approved" ||
        definition.revision_id !== view.data.definition_revision
      ) {
        setRebind(view);
        return;
      }
      setRebind(null);
      setSearch(view.data.search_text);
      setNotice("Saved meaning restored from its exact approved definition.");
    } catch (_) {
      setRebind(view);
      setNotice(
        "The bound definition is retired or no longer permitted. Review a replacement; nothing was rebound.",
      );
    }
  }

  async function rebindView(view: Row, definitionId: string) {
    const definition = indicators.find((row) => row.object_id === definitionId);
    if (!definition) {
      setError("Choose a currently permitted approved definition.");
      return;
    }
    try {
      await request(base + "saved-views/" + view.object_id, {
        method: "PATCH",
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          expected_revision: view.revision_id,
          data: {
            definition_id: definition.object_id,
            definition_revision: definition.revision_id,
          },
        }),
      });
      setRebind(null);
      setNotice(
        "Reviewed definition rebind saved as a new immutable revision.",
      );
      setEpoch((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    }
  }

  function openIssue(reference: string) {
    const task = tasks.find((row) => row.object_id === reference);
    if (!task) {
      setError(
        "The referenced issue is not available under your current permissions.",
      );
      return;
    }
    setSelectedIssue(reference);
    setSearch(reference);
    requestAnimationFrame(() =>
      taskRows.current[reference]?.scrollIntoView({ block: "center" }),
    );
  }

  async function recalculate(row: Row) {
    setBusy(row.object_id);
    setError("");
    try {
      const action = "recalculate:" + row.object_id;
      const command = { expected_revision: row.revision_id, data: {} };
      await request(
        base + "work-items/" + row.object_id + "/actions/recalculate",
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: operations.id(action, command),
            ...command,
          }),
        },
      );
      operations.done(action);
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
      const action = "acknowledge:" + row.object_id;
      const command = { expected_revision: row.revision_id, data: {} };
      await request(
        base + "notifications/" + row.object_id + "/actions/acknowledge",
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: operations.id(action, command),
            ...command,
          }),
        },
      );
      operations.done(action);
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
      <section className="panel" aria-labelledby="find-work-title">
        <h2 id="find-work-title">Find my work</h2>
        <label>
          Search assigned tasks and permitted definitions
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Title, code or exact reference"
          />
        </label>
        <details>
          <summary>Why is approval pending?</summary>
          <p>
            Open the assigned issue, add the required evidence, then return to
            its review action. A returned item keeps the reviewer’s reason. Only
            synthetic examples are shown here: “Community survey result needs
            its signed source file.”
          </p>
        </details>
        <h3>Permitted definitions</h3>
        <ul>
          {indicators
            .filter(matches)
            .slice(0, 20)
            .map((row) => (
              <li key={row.object_id}>
                <strong>
                  {row.data.name || row.data.code || "Definition"}
                </strong>{" "}
                · {row.lifecycle_state}
              </li>
            ))}
        </ul>
        <h3>Indicators and approval blockers</h3>
        <ul>
          {assignedIndicators
            .filter(matches)
            .slice(0, 20)
            .map((row) => (
              <li key={row.object_id}>
                <strong>{row.data.local_applicability || "Indicator"}</strong> ·{" "}
                {row.lifecycle_state}
                {["Draft", "Returned"].includes(row.lifecycle_state) ? (
                  <span>
                    {" "}
                    · Approval is pending: attach the required source evidence,
                    then submit exact indicator <code>
                      {row.object_id}
                    </code>{" "}
                    from Measurement setup.
                  </span>
                ) : (
                  <span> · No draft approval blocker.</span>
                )}
              </li>
            ))}
        </ul>
        <form onSubmit={saveView}>
          <h3>Save this search meaning</h3>
          <label>
            View name
            <input name="title" required maxLength={200} />
          </label>
          <label>
            Approved definition
            <select name="definition_id" required defaultValue="">
              <option value="" disabled>
                Choose exact definition
              </option>
              {indicators
                .filter((row) => row.lifecycle_state === "Approved")
                .map((row) => (
                  <option key={row.object_id} value={row.object_id}>
                    {row.data.name ||
                      row.data.code ||
                      row.object_id.slice(0, 8)}
                  </option>
                ))}
            </select>
          </label>
          <button className="secondary">Save view</button>
        </form>
        <h3>Saved views</h3>
        {!savedViews.length && <p>No saved views.</p>}
        {savedViews.map((view) => (
          <div key={view.object_id} className="toolbar">
            <button className="secondary" onClick={() => void openView(view)}>
              {view.data.title}
            </button>
            {rebind?.object_id === view.object_id && (
              <>
                <label>
                  Reviewed replacement
                  <select
                    defaultValue=""
                    onChange={(event) =>
                      event.target.value &&
                      void rebindView(view, event.target.value)
                    }
                  >
                    <option value="" disabled>
                      Choose replacement
                    </option>
                    {indicators
                      .filter((row) => row.lifecycle_state === "Approved")
                      .map((row) => (
                        <option key={row.object_id} value={row.object_id}>
                          {row.data.name ||
                            row.data.code ||
                            row.object_id.slice(0, 8)}
                        </option>
                      ))}
                  </select>
                </label>
                <span role="status">
                  Rebind requires your explicit selection.
                </span>
              </>
            )}
          </div>
        ))}
      </section>
      <section className="panel">
        <div className="panel-toolbar">
          <div>
            <h2>Assigned tasks</h2>
            <small>Recent current work for your signed-in identity</small>
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
              {tasks.filter(matches).map((row) => (
                <tr
                  key={row.object_id}
                  ref={(node) => {
                    taskRows.current[row.object_id] = node;
                  }}
                  aria-current={
                    selectedIssue === row.object_id ? "true" : undefined
                  }
                >
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
                        {row.data.calculation.dependency_counts && (
                          <>
                            {" "}
                            · dependencies: result{" "}
                            {row.data.calculation.dependency_counts.RESULT || 0}
                            , live dashboard{" "}
                            {row.data.calculation.dependency_counts
                              .LIVE_DASHBOARD || 0}
                            , unpublished report{" "}
                            {row.data.calculation.dependency_counts
                              .UNPUBLISHED_REPORT || 0}
                          </>
                        )}
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
              {notices.filter(matches).map((row) => (
                <tr key={row.object_id}>
                  <td>
                    {String(row.data.notice_class || "NOTICE").replaceAll(
                      "_",
                      " ",
                    )}
                    <small className="block">
                      Reference {String(row.data.safe_reference).slice(0, 8)}
                    </small>
                    <button
                      className="secondary"
                      onClick={() => openIssue(String(row.data.safe_reference))}
                    >
                      Open exact issue
                    </button>
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
