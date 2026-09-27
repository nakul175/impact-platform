import React, { useEffect, useRef, useState } from "react";

type Row = {
  object_id: string;
  revision_id: string;
  lifecycle_state: string;
  created_at: string;
  updated_at: string;
  data: Record<string, any>;
};
type Props = {
  base: string;
  capabilities: string[];
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
  Dialog: React.ComponentType<{
    title: string;
    close: () => void;
    children: React.ReactNode;
  }>;
};
const label = (row: Row) =>
  row.data.code ||
  row.data.title ||
  row.data.source_key ||
  row.object_id.slice(0, 8);

export function PeriodGovernancePanel({
  base,
  capabilities,
  request,
  explain,
  Dialog,
}: Props) {
  const [data, setData] = useState<Record<string, Row[]>>({}),
    [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const [mode, setMode] = useState<"close" | "restate" | null>(null),
    [programme, setProgramme] = useState<Row | null>(null),
    [period, setPeriod] = useState<Row | null>(null);
  const [reason, setReason] = useState(""),
    [template, setTemplate] = useState(""),
    [sources, setSources] = useState<string[]>([]);
  const [expires, setExpires] = useState(""),
    [busy, setBusy] = useState(false),
    [epoch, setEpoch] = useState(0);
  const operation = useRef(crypto.randomUUID()),
    can = (cap: string) => capabilities.includes(cap);
  useEffect(() => {
    const controller = new AbortController(),
      routes = [
        "programmes",
        "periods",
        "period-closes",
        "restatement-requests",
        "snapshots",
        "workflow-templates",
        "indicator-instances",
        "observations",
      ];
    async function load(route: string) {
      let cursor = "",
        items: Row[] = [];
      do {
        const page = await request(
          base +
            route +
            "?limit=100" +
            (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""),
          { signal: controller.signal },
        );
        items = [...items, ...page.items];
        cursor = page.next_cursor || "";
        if (items.length >= 1000 && cursor)
          throw new Error(
            "This workspace exceeds the 1,000-record close-screen limit.",
          );
      } while (cursor);
      return items;
    }
    Promise.all(
      routes
        .filter((route) => can(route + ".read") || route === "periods")
        .map(async (route) => [route, await load(route)] as const),
    )
      .then((values) => setData(Object.fromEntries(values)))
      .catch((e: any) => {
        if (e.name !== "AbortError") setError(explain(e));
      });
    return () => controller.abort();
  }, [base, epoch]);
  function open(next: "close" | "restate") {
    setMode(next);
    setProgramme(null);
    setPeriod(null);
    setReason("");
    setTemplate("");
    setSources([]);
    setError("");
    operation.current = crypto.randomUUID();
    setExpires(new Date(Date.now() + 2 * 86400000).toISOString().slice(0, 16));
  }
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!programme || !period || !mode) return;
    setBusy(true);
    setError("");
    try {
      const payload: Record<string, any> = {
        workflow_version: template,
        programme_id: programme.object_id,
        reason,
      };
      if (mode === "restate") {
        payload.source_ids = sources;
        payload.expires_at = new Date(expires).toISOString();
      }
      await request(base + "periods/" + period.object_id + "/actions/" + mode, {
        method: "POST",
        body: JSON.stringify({
          operation_id: operation.current,
          expected_revision: period.revision_id,
          data: payload,
        }),
      });
      setMode(null);
      setEpoch((value) => value + 1);
      setNotice(
        mode === "close"
          ? "Close preview submitted for independent review."
          : "Restatement window submitted for independent review.",
      );
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  const snapshots = (programmeId: string, periodId: string) =>
    (data.snapshots || []).filter(
      (row) =>
        row.data.programme_id === programmeId &&
        row.data.period_id === periodId,
    );
  const status = (programmeId: string, periodId: string) => {
    const latest = snapshots(programmeId, periodId).sort((a, b) =>
      String(b.data.locked_at).localeCompare(String(a.data.locked_at)),
    )[0];
    if (!latest) return "Open";
    const restatement = (data["restatement-requests"] || []).some(
      (row) =>
        row.lifecycle_state === "Approved" &&
        row.data.programme_id === programmeId &&
        row.data.period_id === periodId &&
        new Date(row.data.expires_at) > new Date() &&
        new Date(row.updated_at) > new Date(latest.data.locked_at),
    );
    return restatement ? "RestatementOpen" : "Locked";
  };
  const programmePeriods = (data.programmes || []).flatMap((programmeRow) =>
    (data.periods || [])
      .filter(
        (periodRow) =>
          programmeRow.lifecycle_state === "Active" &&
          programmeRow.data.starts_at <= periodRow.data.starts_at &&
          programmeRow.data.ends_at >= periodRow.data.ends_at,
      )
      .map((periodRow) => ({
        programme: programmeRow,
        period: periodRow,
        state: status(programmeRow.object_id, periodRow.object_id),
      })),
  );
  const programmeIndicators = new Set(
    (data["indicator-instances"] || [])
      .filter((row) => row.data.programme_id === programme?.object_id)
      .map((row) => row.object_id),
  );
  const availableSources =
    period && programme
      ? (data.observations || []).filter(
          (row) =>
            row.lifecycle_state === "Approved" &&
            programmeIndicators.has(row.data.indicator_id) &&
            new Date(row.data.event_at) >= new Date(period.data.starts_at) &&
            new Date(row.data.event_at) < new Date(period.data.ends_at),
        )
      : [];
  const selectablePeriods = programme
    ? programmePeriods.filter(
        (row) =>
          row.programme.object_id === programme.object_id &&
          (mode === "close"
            ? ["Open", "RestatementOpen"].includes(row.state)
            : row.state === "Locked"),
      )
    : [];
  return (
    <section aria-label="Period close and restatement">
      <p>
        Close previews pin every source, plan and result. Approval creates
        official result versions and an immutable snapshot. Restatement opens
        only named records for up to seven days.
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
      <div className="actions">
        {can("period.close") && (
          <button className="primary" onClick={() => open("close")}>
            Preview period close
          </button>
        )}
        {can("period.restate") && (
          <button onClick={() => open("restate")}>Request restatement</button>
        )}
      </div>
      <h2>Reporting periods</h2>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Programme</th>
              <th>Period</th>
              <th>Dates</th>
              <th>Status</th>
              <th>Snapshots</th>
            </tr>
          </thead>
          <tbody>
            {programmePeriods.map((row) => (
              <tr key={row.programme.object_id + row.period.object_id}>
                <td>{label(row.programme)}</td>
                <td>{label(row.period)}</td>
                <td>
                  {row.period.data.starts_at?.slice(0, 10)} –{" "}
                  {row.period.data.ends_at?.slice(0, 10)}
                </td>
                <td>{row.state}</td>
                <td>
                  {
                    snapshots(row.programme.object_id, row.period.object_id)
                      .length
                  }
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h2>Close previews</h2>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Programme</th>
              <th>Period</th>
              <th>Status</th>
              <th>Coverage</th>
              <th>Review detail</th>
            </tr>
          </thead>
          <tbody>
            {(data["period-closes"] || []).map((row) => (
              <tr key={row.object_id}>
                <td>
                  {label(
                    (data.programmes || []).find(
                      (p) => p.object_id === row.data.programme_id,
                    ) || row,
                  )}
                </td>
                <td>
                  {label(
                    (data.periods || []).find(
                      (p) => p.object_id === row.data.period_id,
                    ) || row,
                  )}
                </td>
                <td>{row.lifecycle_state}</td>
                <td>
                  {row.data.blockers.length
                    ? row.data.blockers.length + " blocker(s)"
                    : "Ready to lock"}
                </td>
                <td>
                  <details>
                    <summary>Exact preview</summary>
                    <p>{row.data.reason}</p>
                    {row.data.blockers.map((b: any, i: number) => (
                      <p key={i}>
                        {b.code}: {b.message}
                      </p>
                    ))}
                    <pre>{JSON.stringify(row.data.entries, null, 2)}</pre>
                  </details>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!(data["period-closes"] || []).length && <p>No close previews.</p>}
      </div>
      <h2>Locked snapshots</h2>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Snapshot</th>
              <th>Programme</th>
              <th>Period</th>
              <th>Locked</th>
              <th>Official results</th>
            </tr>
          </thead>
          <tbody>
            {(data.snapshots || []).map((row) => (
              <tr key={row.object_id}>
                <td>{row.object_id.slice(0, 8)}</td>
                <td>
                  {label(
                    (data.programmes || []).find(
                      (p) => p.object_id === row.data.programme_id,
                    ) || row,
                  )}
                </td>
                <td>
                  {label(
                    (data.periods || []).find(
                      (p) => p.object_id === row.data.period_id,
                    ) || row,
                  )}
                </td>
                <td>
                  {row.data.locked_at?.replace("T", " ").slice(0, 19)} UTC
                </td>
                <td>{row.data.result_versions?.length || 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!(data.snapshots || []).length && <p>No locked snapshots.</p>}
      </div>
      {mode && (
        <Dialog
          title={
            mode === "close"
              ? "Preview and submit period close"
              : "Request scoped restatement"
          }
          close={() => {
            if (!busy) setMode(null);
          }}
        >
          <form onSubmit={submit}>
            {error && (
              <p className="error" role="alert">
                {error}
              </p>
            )}
            <label>
              Programme
              <select
                aria-label="Programme"
                required
                value={programme?.object_id || ""}
                onChange={(e) => {
                  setProgramme(
                    (data.programmes || []).find(
                      (p) => p.object_id === e.target.value,
                    ) || null,
                  );
                  setPeriod(null);
                  setSources([]);
                }}
              >
                <option value="">Choose programme</option>
                {(data.programmes || [])
                  .filter((p) => p.lifecycle_state === "Active")
                  .map((p) => (
                    <option key={p.object_id} value={p.object_id}>
                      {label(p)}
                    </option>
                  ))}
              </select>
            </label>
            <label>
              Reporting period
              <select
                aria-label="Reporting period"
                required
                value={period?.object_id || ""}
                onChange={(e) => {
                  setPeriod(
                    (data.periods || []).find(
                      (p) => p.object_id === e.target.value,
                    ) || null,
                  );
                  setSources([]);
                }}
              >
                <option value="">Choose period</option>
                {selectablePeriods.map((row) => (
                  <option
                    key={row.period.object_id}
                    value={row.period.object_id}
                  >
                    {label(row.period)} · {row.state}
                  </option>
                ))}
              </select>
            </label>
            {mode === "restate" && period && (
              <fieldset>
                <legend>Sources permitted for correction</legend>
                {availableSources.map((row) => (
                  <label className="check" key={row.object_id}>
                    <input
                      type="checkbox"
                      checked={sources.includes(row.object_id)}
                      onChange={(e) =>
                        setSources(
                          e.target.checked
                            ? [...sources, row.object_id]
                            : sources.filter((id) => id !== row.object_id),
                        )
                      }
                    />
                    {label(row)}
                  </label>
                ))}
                {!availableSources.length && (
                  <p>No approved sources from this period are visible.</p>
                )}
              </fieldset>
            )}
            {mode === "restate" && (
              <label>
                Window expires
                <input
                  aria-label="Window expires"
                  type="datetime-local"
                  required
                  value={expires}
                  onChange={(e) => setExpires(e.target.value)}
                />
              </label>
            )}
            <label>
              Reason
              <textarea
                aria-label="Governance reason"
                required
                maxLength={2000}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </label>
            <label>
              Review policy
              <select
                aria-label="Review policy"
                required
                value={template}
                onChange={(e) => setTemplate(e.target.value)}
              >
                <option value="">Choose policy</option>
                {(data["workflow-templates"] || [])
                  .filter((t) => t.lifecycle_state === "Active")
                  .map((t) => (
                    <option key={t.object_id} value={t.revision_id}>
                      {label(t)}
                    </option>
                  ))}
              </select>
            </label>
            <button
              className="primary"
              disabled={
                busy ||
                !programme ||
                !period ||
                (mode === "restate" && !sources.length)
              }
            >
              {mode === "close"
                ? "Submit close preview"
                : "Submit restatement request"}
            </button>
          </form>
        </Dialog>
      )}
    </section>
  );
}
