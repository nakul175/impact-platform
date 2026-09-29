import React, { useEffect, useState } from "react";
import { usePendingOperations } from "./operations";

type Row = {
  object_id: string;
  revision_id: string;
  lifecycle_state: string;
  owner_id?: string;
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
type Node = {
  node_id: string;
  node_type: string;
  title: string;
  definition: string;
  parent_node_id: string | null;
  owner_id: string | null;
  indicator_ids: string[];
};
const LEVELS = ["IMPACT", "OUTCOME", "OUTPUT", "ACTIVITY"];
const tabs = {
  framework: "Framework",
  targets: "Targets",
  progress: "Targets vs actuals",
  reviews: "Reviews",
} as const;

async function pages(request: Props["request"], path: string) {
  let items: Row[] = [],
    cursor: string | null = null;
  do {
    const page: any = await request(
      path +
        "?limit=100" +
        (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""),
    );
    items = [...items, ...page.items];
    cursor = page.next_cursor;
    if (cursor && items.length >= 500)
      throw new Error(
        "This planning view supports 500 records per type. Use the paginated API for larger workspaces.",
      );
  } while (cursor);
  return items;
}

const indicatorName = (r?: Row) =>
  r ? r.data.local_applicability || r.object_id.slice(0, 8) : "Indicator";

function Tree({
  nodes,
  indicators,
  members,
}: {
  nodes: Node[];
  indicators: Row[];
  members: any[];
}) {
  const ids = new Set(nodes.map((n) => n.node_id));
  const children = (parent: string | null) =>
    nodes.filter(
      (n) =>
        (n.parent_node_id || null) === parent ||
        (parent === null && n.parent_node_id && !ids.has(n.parent_node_id)),
    );
  const render = (parent: string | null, depth: number): React.ReactNode => {
    const items = children(parent);
    if (!items.length || depth > 20) return null;
    return (
      <ul>
        {items.map((n) => (
          <li key={n.node_id}>
            <div className="planning-node">
              <span className={"badge level-" + n.node_type.toLowerCase()}>
                {n.node_type}
              </span>{" "}
              <strong>{n.title}</strong>
              <small className="muted">
                {" "}
                · owner{" "}
                {members.find((m) => m.principal_id === n.owner_id)
                  ?.display_name ||
                  (n.owner_id ? n.owner_id.slice(0, 8) : "not assigned")}
              </small>
              {n.indicator_ids?.length ? (
                <small>
                  {" "}
                  · measured by{" "}
                  {n.indicator_ids
                    .map((i) =>
                      indicatorName(indicators.find((x) => x.object_id === i)),
                    )
                    .join(", ")}
                </small>
              ) : null}
            </div>
            {render(n.node_id, depth + 1)}
          </li>
        ))}
      </ul>
    );
  };
  return (
    <section className="planning-tree" aria-label="Results hierarchy">
      {nodes.length ? render(null, 0) : <p className="muted">No nodes yet.</p>}
    </section>
  );
}

function Issues({ report }: { report: any }) {
  if (!report) return <p role="status">Checking completeness…</p>;
  return (
    <section aria-label="Completeness review">
      <h3>
        Completeness review ·{" "}
        {report.ready ? "ready for review" : "action required"}
      </h3>
      {!report.issues.length ? (
        <p className="muted">No issues found.</p>
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Severity</th>
                <th>Rule</th>
                <th>Object</th>
                <th>Resolution</th>
              </tr>
            </thead>
            <tbody>
              {report.issues.map((i: any) => (
                <tr key={i.rule + i.object_id}>
                  <td>{i.severity}</td>
                  <td>
                    {i.rule.replaceAll("_", " ")}
                    <small className="muted"> {i.message}</small>
                  </td>
                  <td>{i.object_id.slice(0, 8)}</td>
                  <td>
                    {i.excepted
                      ? "Exception: " + i.exception.reason
                      : i.exceptable
                        ? "Resolve or document an exception"
                        : "Must be resolved"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {report.comparison && (
        <p className="muted">
          Compared with baseline {report.comparison.base_version}:{" "}
          {report.comparison.added.length} added,{" "}
          {report.comparison.removed.length} removed,{" "}
          {report.comparison.changed.length} changed, affecting{" "}
          {report.comparison.affected_indicator_ids.length} indicator(s).
        </p>
      )}
    </section>
  );
}

export function PlanningPanel({
  base,
  capabilities,
  request,
  explain,
  Dialog,
}: Props) {
  const allowed = (c: string) => capabilities.includes(c);
  const [tab, setTab] = useState<keyof typeof tabs>("framework");
  const [programmes, setProgrammes] = useState<Row[]>([]);
  const [programme, setProgramme] = useState("");
  const [data, setData] = useState<Record<string, any>>({});
  const [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [loading, setLoading] = useState(true),
    [tick, setTick] = useState(0);
  const [dialog, setDialog] = useState<{
    mode: string;
    row?: Row;
  } | null>(null);
  useEffect(() => {
    if (!allowed("programmes.read")) {
      setLoading(false);
      return;
    }
    pages(request, base + "programmes")
      .then((items) => {
        setProgrammes(items);
        setProgramme((current) => current || items[0]?.object_id || "");
      })
      .catch((e) => setError(explain(e)));
  }, [base, capabilities.join("|")]);
  useEffect(() => {
    if (!programme) return;
    let live = true;
    setLoading(true);
    setError("");
    const routes = [
      "frameworks",
      "targets",
      "indicator-instances",
      "periods",
      "workflow-templates",
      "workflows",
    ].filter((r) => allowed(r + ".read"));
    Promise.all([
      ...routes.map(async (r) => [r, await pages(request, base + r)] as const),
      allowed("measurement-members.read")
        ? request(base + "measurement-members").then(
            (m) => ["members", m.items] as const,
          )
        : Promise.resolve(["members", []] as const),
      allowed("targets.read")
        ? request(
            base + "programmes/" + programme + "/targets-vs-actuals",
          ).then((v) => ["view", v] as const)
        : Promise.resolve(["view", null] as const),
    ])
      .then((items) => {
        if (live) setData(Object.fromEntries(items));
      })
      .catch((e) => {
        if (live) setError(explain(e));
      })
      .finally(() => {
        if (live) setLoading(false);
      });
    return () => {
      live = false;
    };
  }, [programme, tick, base, capabilities.join("|")]);
  const indicators: Row[] = (data["indicator-instances"] || []).filter(
    (r: Row) => r.data.programme_id === programme,
  );
  const indicatorIds = new Set(indicators.map((r) => r.object_id));
  const frameworks: Row[] = (data.frameworks || []).filter(
    (r: Row) => r.data.programme_id === programme,
  );
  const targets: Row[] = (data.targets || []).filter((r: Row) =>
    indicatorIds.has(r.data.indicator_id),
  );
  const periods: Row[] = data.periods || [];
  const members: any[] = data.members || [];
  const view = data.view;
  const planningIds = new Set([
    ...frameworks.map((r) => r.object_id),
    ...targets.map((r) => r.object_id),
  ]);
  const reviews: Row[] = (data.workflows || []).filter(
    (w: Row) =>
      w.lifecycle_state === "InReview" && planningIds.has(w.data.candidate_id),
  );
  const approvedBaseline = view?.framework;
  const complete = (text: string) => {
    setDialog(null);
    setMessage(text);
    setTick((t) => t + 1);
  };
  const shared = { base, request, explain, allowed, complete };
  return (
    <>
      <div className="planning-toolbar">
        <label>
          Programme
          <select
            aria-label="Programme"
            value={programme}
            onChange={(e) => {
              setProgramme(e.target.value);
              setMessage("");
            }}
          >
            {!programmes.length && <option value="">No programmes</option>}
            {programmes.map((p) => (
              <option key={p.object_id} value={p.object_id}>
                {p.data.title || p.data.code || p.object_id.slice(0, 8)}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="setup-tabs" role="tablist" aria-label="Results planning">
        {Object.entries(tabs).map(([key, label]) => (
          <button
            key={key}
            role="tab"
            aria-selected={tab === key}
            className={tab === key ? "primary" : "secondary"}
            onClick={() => {
              setTab(key as keyof typeof tabs);
              setMessage("");
            }}
          >
            {label}
            {key === "reviews" && reviews.length ? ` (${reviews.length})` : ""}
          </button>
        ))}
      </div>
      <section className="panel setup-panel">
        {error && (
          <div role="alert" className="error">
            {error}
          </div>
        )}
        {message && (
          <p role="status" className="success">
            {message}
          </p>
        )}
        {loading ? (
          <p role="status">Loading planning records…</p>
        ) : tab === "framework" ? (
          <>
            <div className="setup-heading">
              <div>
                <h2>Results framework</h2>
                <p className="muted">
                  Impact, outcome, output and activity nodes with owners and the
                  indicators that measure them. Independent approval freezes a
                  baseline; later changes start a child draft with an effective
                  date.
                </p>
              </div>
              {allowed("frameworks.draft.create") && (
                <button
                  className="primary"
                  onClick={() => setDialog({ mode: "framework" })}
                >
                  {approvedBaseline ? "Start revision" : "New framework"}
                </button>
              )}
            </div>
            {approvedBaseline ? (
              <>
                <h3>
                  Approved baseline {approvedBaseline.baseline_version} ·{" "}
                  {approvedBaseline.version_label} · effective{" "}
                  {approvedBaseline.effective_from.slice(0, 10)}
                </h3>
                <Tree
                  nodes={approvedBaseline.nodes}
                  indicators={indicators}
                  members={members}
                />
              </>
            ) : (
              <p className="muted">No approved framework baseline yet.</p>
            )}
            <h3>Framework versions</h3>
            {!frameworks.length ? (
              <p className="muted">No framework drafts for this programme.</p>
            ) : (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Version</th>
                      <th>Status</th>
                      <th>Effective from</th>
                      <th>Nodes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {frameworks.map((f) => (
                      <tr key={f.object_id}>
                        <td>
                          <button
                            className="text record-title"
                            onClick={() =>
                              setDialog({ mode: "inspect-framework", row: f })
                            }
                          >
                            {f.data.version_label || f.object_id.slice(0, 8)}
                          </button>
                        </td>
                        <td>
                          <span
                            className={
                              "badge " + f.lifecycle_state.toLowerCase()
                            }
                          >
                            {f.lifecycle_state}
                          </span>
                        </td>
                        <td>{(f.data.effective_from || "—").slice(0, 10)}</td>
                        <td>{f.data.nodes?.length || 0}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        ) : tab === "targets" ? (
          <>
            <div className="setup-heading">
              <div>
                <h2>Targets, baselines and milestones</h2>
                <p className="muted">
                  One governed value per indicator and reporting period. A blank
                  target stays blank; a revision supersedes an approved target
                  and keeps the original.
                </p>
              </div>
              {allowed("targets.draft.create") && (
                <button
                  className="primary"
                  disabled={!indicators.length}
                  onClick={() => setDialog({ mode: "target" })}
                >
                  New target
                </button>
              )}
            </div>
            {!targets.length ? (
              <p className="muted">No targets for this programme.</p>
            ) : (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Indicator</th>
                      <th>Period</th>
                      <th>Kind</th>
                      <th>Value</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {targets.map((t) => (
                      <tr key={t.object_id}>
                        <td>
                          <button
                            className="text record-title"
                            onClick={() =>
                              setDialog({ mode: "inspect-target", row: t })
                            }
                          >
                            {indicatorName(
                              indicators.find(
                                (i) => i.object_id === t.data.indicator_id,
                              ),
                            ) +
                              " · " +
                              (t.data.milestone_label ||
                                (t.data.target_basis || "").toLowerCase())}
                          </button>
                        </td>
                        <td>
                          {periods.find((p) => p.object_id === t.data.period_id)
                            ?.data.code || "—"}
                        </td>
                        <td>
                          {t.data.target_kind} · {t.data.direction}
                        </td>
                        <td>{targetValue(t.data)}</td>
                        <td>
                          <span
                            className={
                              "badge " + t.lifecycle_state.toLowerCase()
                            }
                          >
                            {t.lifecycle_state}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        ) : tab === "progress" ? (
          <Progress view={view} framework={approvedBaseline} />
        ) : (
          <>
            <h2>Planning reviews</h2>
            <p className="muted">
              Decide on the exact submitted framework or target revision.
              Authors cannot approve their own work.
            </p>
            {!reviews.length ? (
              <p className="muted">Nothing awaits a decision.</p>
            ) : (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Submission</th>
                      <th>Status</th>
                      <th>Candidate revision</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reviews.map((w) => (
                      <tr key={w.object_id}>
                        <td>
                          <button
                            className="text record-title"
                            onClick={() =>
                              setDialog({ mode: "review", row: w })
                            }
                          >
                            Review ·{" "}
                            {frameworks.some(
                              (f) => f.object_id === w.data.candidate_id,
                            )
                              ? "framework"
                              : "target"}{" "}
                            {w.object_id.slice(0, 8)}
                          </button>
                        </td>
                        <td>
                          <span className="badge inreview">InReview</span>
                        </td>
                        <td>{w.data.candidate_revision.slice(0, 8)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </section>
      {dialog && (
        <Dialog
          title={
            dialog.mode === "framework"
              ? dialog.row
                ? "Edit framework"
                : approvedBaseline
                  ? "Revise framework"
                  : "New framework"
              : dialog.mode === "inspect-framework"
                ? "Framework " + (dialog.row?.data.version_label || "")
                : dialog.mode === "target"
                  ? dialog.row
                    ? "Edit target"
                    : "New target"
                  : dialog.mode === "inspect-target"
                    ? "Target"
                    : "Review planning submission"
          }
          close={() => setDialog(null)}
        >
          {dialog.mode === "framework" ? (
            <FrameworkEditor
              {...shared}
              row={dialog.row}
              programme={programme}
              baseline={approvedBaseline}
              indicators={indicators}
              members={members}
            />
          ) : dialog.mode === "inspect-framework" ? (
            <FrameworkDetail
              {...shared}
              row={dialog.row!}
              indicators={indicators}
              members={members}
              templates={data["workflow-templates"] || []}
              edit={() => setDialog({ mode: "framework", row: dialog.row })}
            />
          ) : dialog.mode === "target" ? (
            <TargetEditor
              {...shared}
              row={dialog.row}
              indicators={indicators}
              periods={periods}
              targets={targets}
            />
          ) : dialog.mode === "inspect-target" ? (
            <TargetDetail
              {...shared}
              row={dialog.row!}
              templates={data["workflow-templates"] || []}
              edit={() => setDialog({ mode: "target", row: dialog.row })}
            />
          ) : (
            <Review
              {...shared}
              row={dialog.row!}
              indicators={indicators}
              members={members}
            />
          )}
        </Dialog>
      )}
    </>
  );
}

function targetValue(d: Record<string, any>) {
  if (d.value_state !== "PRESENT")
    return "Blank · " + String(d.value_state || "—").replaceAll("_", " ");
  if (d.target_kind === "RANGE") return d.low + " – " + d.high;
  return d.value ?? "—";
}

function Progress({ view, framework }: { view: any; framework: any }) {
  if (!view) return <p>You do not have access to targets.</p>;
  const nodeTitle = (id: string) =>
    framework?.nodes.find((n: Node) => n.node_id === id)?.title || id;
  return (
    <>
      <h2>Targets vs actuals</h2>
      <p className="muted">
        Actuals come from locked snapshots (OFFICIAL) where a period is closed,
        otherwise from the latest calculation (PROVISIONAL). Attainment uses
        stored decimals and is rounded once for display.
      </p>
      {!view.rows.length ? (
        <p className="muted">No targets or results for this programme yet.</p>
      ) : (
        <div className="table-scroll">
          <table aria-label="Targets versus actuals">
            <thead>
              <tr>
                <th>Indicator</th>
                <th>Period</th>
                <th>Baseline</th>
                <th>Target</th>
                <th>Actual</th>
                <th>Progress</th>
              </tr>
            </thead>
            <tbody>
              {view.rows.map((r: any) => (
                <tr key={r.indicator_id + r.period_id}>
                  <td>
                    {r.indicator_label}
                    {r.node_ids.length ? (
                      <small className="muted">
                        {" "}
                        · {r.node_ids.map(nodeTitle).join(", ")}
                      </small>
                    ) : null}
                  </td>
                  <td>
                    {r.period_code || r.period_id.slice(0, 8)}
                    <small className="muted"> · {r.period_state}</small>
                  </td>
                  <td>{r.baseline ? targetValue(r.baseline) : "—"}</td>
                  <td>
                    {r.target ? (
                      <>
                        <span>{targetValue(r.target)}</span>
                        <small className="muted">
                          {" "}
                          · {r.target.direction.toLowerCase()} ·{" "}
                          {r.target.target_basis.toLowerCase()}
                        </small>
                      </>
                    ) : (
                      "No approved target"
                    )}
                    {r.milestones.map((m: any) => (
                      <small key={m.revision_id} className="muted">
                        <br />
                        Milestone {m.milestone_label}: {targetValue(m)} by{" "}
                        {(m.due_at || "").slice(0, 10)}
                      </small>
                    ))}
                  </td>
                  <td>
                    {r.actual.mode === "NONE" ? (
                      "No result yet"
                    ) : (
                      <>
                        {r.actual.value_state === "PRESENT"
                          ? r.actual.displayed_value
                          : r.actual.value_state}{" "}
                        <span
                          className={"badge " + r.actual.mode.toLowerCase()}
                        >
                          {r.actual.mode}
                        </span>
                        {r.actual.stale && (
                          <span className="badge stale">STALE</span>
                        )}
                      </>
                    )}
                  </td>
                  <td>
                    {r.progress.status.replaceAll("_", " ")}
                    {r.progress.attainment_percent && (
                      <small>
                        {" "}
                        ·{" "}
                        {r.progress.attainment_percent === "Undefined"
                          ? "attainment undefined"
                          : r.progress.attainment_percent + "% of target"}
                      </small>
                    )}
                    {r.progress.displayed_deviation && (
                      <small className="muted">
                        {" "}
                        · deviation {r.progress.displayed_deviation}
                      </small>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

type Shared = {
  base: string;
  request: Props["request"];
  explain: Props["explain"];
  allowed: (c: string) => boolean;
  complete: (m: string) => void;
};

function useSender({ base, request, explain, complete }: Shared) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const operations = usePendingOperations();
  async function send(
    path: string,
    data: Record<string, any>,
    method: string,
    expected: string | undefined,
    done: string,
  ) {
    setBusy(true);
    setError("");
    const key = method + " " + path;
    const body = {
      ...(expected ? { expected_revision: expected } : {}),
      data,
    };
    try {
      await request(base + path, {
        method,
        body: JSON.stringify({
          operation_id: operations.id(key, body),
          ...body,
        }),
      });
      operations.done(key);
      complete(done);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return { error, busy, send, setError };
}

function FrameworkEditor(
  props: Shared & {
    row?: Row;
    programme: string;
    baseline: any;
    indicators: Row[];
    members: any[];
  },
) {
  const { row, programme, baseline, indicators, members } = props;
  const { error, busy, send } = useSender(props);
  const seed: Node[] =
    row?.data.nodes ||
    (baseline
      ? baseline.nodes
      : [
          {
            node_id: crypto.randomUUID(),
            node_type: "IMPACT",
            title: "",
            definition: "",
            parent_node_id: null,
            owner_id: null,
            indicator_ids: [],
          },
        ]);
  const [nodes, setNodes] = useState<Node[]>(seed.map((n) => ({ ...n })));
  const [label, setLabel] = useState(
    row?.data.version_label || (baseline ? "Revision" : "Baseline"),
  );
  const [effective, setEffective] = useState(
    (row?.data.effective_from || "").slice(0, 10),
  );
  const update = (i: number, change: Partial<Node>) =>
    setNodes(nodes.map((n, j) => (j === i ? { ...n, ...change } : n)));
  function submit(e: React.FormEvent) {
    e.preventDefault();
    const data: Record<string, any> = {
      version_label: label,
      nodes: nodes.map((n) => ({
        ...n,
        owner_id: n.owner_id || null,
        parent_node_id: n.parent_node_id || null,
      })),
      ...(effective
        ? { effective_from: new Date(effective + "T00:00:00Z").toISOString() }
        : {}),
    };
    if (!row) {
      data.programme_id = programme;
      data.relationships = [];
      if (baseline) data.supersedes_revision = baseline.revision_id;
    }
    void send(
      "frameworks" + (row ? "/" + row.object_id : ""),
      data,
      row ? "PATCH" : "POST",
      row?.revision_id,
      "Framework draft saved. The version and audit receipt have been recorded.",
    );
  }
  return (
    <form onSubmit={submit}>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      {baseline && !row && (
        <p className="muted">
          This draft revises approved baseline {baseline.baseline_version}. It
          keeps every node identity; the baseline stays unchanged until an
          independent reviewer approves the revision.
        </p>
      )}
      <div className="form-grid">
        <label>
          Version label
          <input
            required
            maxLength={64}
            value={label}
            onChange={(e) => setLabel(e.target.value)}
          />
        </label>
        <label>
          Effective from
          <input
            type="date"
            value={effective}
            onChange={(e) => setEffective(e.target.value)}
          />
        </label>
      </div>
      <h3>Logframe</h3>
      {nodes.map((n, i) => (
        <fieldset key={n.node_id} className="planning-node-editor">
          <legend>Node {i + 1}</legend>
          <div className="form-grid">
            <label>
              Level {i + 1}
              <select
                aria-label={"Level " + (i + 1)}
                value={n.node_type}
                onChange={(e) => update(i, { node_type: e.target.value })}
              >
                {LEVELS.map((l) => (
                  <option key={l} value={l}>
                    {l.toLowerCase()}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Parent {i + 1}
              <select
                aria-label={"Parent " + (i + 1)}
                value={n.parent_node_id || ""}
                onChange={(e) =>
                  update(i, { parent_node_id: e.target.value || null })
                }
              >
                <option value="">Top level</option>
                {nodes
                  .filter((p) => p.node_id !== n.node_id)
                  .map((p) => (
                    <option key={p.node_id} value={p.node_id}>
                      {p.title || p.node_type.toLowerCase()}
                    </option>
                  ))}
              </select>
            </label>
          </div>
          <label>
            Title {i + 1}
            <input
              required
              maxLength={200}
              value={n.title}
              onChange={(e) => update(i, { title: e.target.value })}
            />
          </label>
          <label>
            Description {i + 1}
            <textarea
              required
              maxLength={2000}
              value={n.definition}
              onChange={(e) => update(i, { definition: e.target.value })}
            />
          </label>
          <label>
            Owner {i + 1}
            <select
              aria-label={"Owner " + (i + 1)}
              value={n.owner_id || ""}
              onChange={(e) => update(i, { owner_id: e.target.value || null })}
            >
              <option value="">Not assigned</option>
              {members.map((m) => (
                <option key={m.principal_id} value={m.principal_id}>
                  {m.display_name}
                </option>
              ))}
            </select>
          </label>
          {indicators.length > 0 && (
            <div role="group" aria-label={"Indicators " + (i + 1)}>
              {indicators.map((ind) => (
                <label key={ind.object_id} className="checkbox">
                  <input
                    type="checkbox"
                    checked={n.indicator_ids.includes(ind.object_id)}
                    onChange={(e) =>
                      update(i, {
                        indicator_ids: e.target.checked
                          ? [...n.indicator_ids, ind.object_id]
                          : n.indicator_ids.filter((x) => x !== ind.object_id),
                      })
                    }
                  />{" "}
                  Measure node {i + 1} with {indicatorName(ind)}
                </label>
              ))}
            </div>
          )}
          <button
            type="button"
            className="secondary"
            onClick={() => setNodes(nodes.filter((_, j) => j !== i))}
          >
            Remove node {i + 1}
          </button>
        </fieldset>
      ))}
      <button
        type="button"
        className="secondary"
        onClick={() =>
          setNodes([
            ...nodes,
            {
              node_id: crypto.randomUUID(),
              node_type: "OUTPUT",
              title: "",
              definition: "",
              parent_node_id: nodes[nodes.length - 1]?.node_id || null,
              owner_id: null,
              indicator_ids: [],
            },
          ])
        }
      >
        Add node
      </button>
      <h3>Hierarchy preview</h3>
      <Tree nodes={nodes} indicators={indicators} members={members} />
      <div className="dialog-actions">
        <button className="primary" disabled={busy}>
          Save framework draft
        </button>
      </div>
    </form>
  );
}

function SubmitForReview({
  templates,
  busy,
  onSubmit,
}: {
  templates: Row[];
  busy: boolean;
  onSubmit: (workflow: string) => void;
}) {
  const [workflow, setWorkflow] = useState("");
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(workflow);
      }}
    >
      <label>
        Review policy
        <select
          aria-label="Review policy"
          required
          value={workflow}
          onChange={(e) => setWorkflow(e.target.value)}
        >
          <option value="" disabled>
            Choose a review policy
          </option>
          {templates
            .filter((r) => r.lifecycle_state === "Active")
            .map((r) => (
              <option key={r.object_id} value={r.revision_id}>
                {r.data.title || "Independent approval"}
              </option>
            ))}
        </select>
      </label>
      <button className="primary" disabled={busy}>
        Submit for review
      </button>
    </form>
  );
}

function FrameworkDetail(
  props: Shared & {
    row: Row;
    indicators: Row[];
    members: any[];
    templates: Row[];
    edit: () => void;
  },
) {
  const { row, indicators, members, templates, edit, allowed, base, request } =
    props;
  const { error, busy, send, setError } = useSender(props);
  const [report, setReport] = useState<any>(null);
  const [exception, setException] = useState<{
    object_id: string;
    rule: string;
  } | null>(null);
  useEffect(() => {
    request(base + "frameworks/" + row.object_id + "/completeness")
      .then(setReport)
      .catch((e) => setError(props.explain(e)));
  }, [row.revision_id]);
  const editable =
    ["Draft", "Returned"].includes(row.lifecycle_state) &&
    allowed("frameworks.draft.edit");
  return (
    <>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      <div className="detail-meta">
        <span className={"badge " + row.lifecycle_state.toLowerCase()}>
          {row.lifecycle_state}
        </span>{" "}
        Revision {row.revision_id.slice(0, 8)}
      </div>
      <Tree
        nodes={row.data.nodes || []}
        indicators={indicators}
        members={members}
      />
      <Issues report={report} />
      {editable && report && (
        <>
          {report.issues
            .filter((i: any) => i.exceptable && !i.excepted)
            .map((i: any) => (
              <button
                key={i.rule + i.object_id}
                className="secondary"
                onClick={() =>
                  setException({ object_id: i.object_id, rule: i.rule })
                }
              >
                Document exception · {i.rule.replaceAll("_", " ").toLowerCase()}{" "}
                {i.object_id.slice(0, 8)}
              </button>
            ))}
          {exception && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const form = new FormData(e.currentTarget);
                void send(
                  "frameworks/" + row.object_id,
                  {
                    exceptions: [
                      ...(row.data.exceptions || []),
                      {
                        ...exception,
                        reason: String(form.get("reason")),
                        review_date: String(form.get("review_date")),
                      },
                    ],
                  },
                  "PATCH",
                  row.revision_id,
                  "Exception documented. The reviewer will see it in the baseline evidence.",
                );
              }}
            >
              <label>
                Exception reason
                <textarea name="reason" required maxLength={2000} />
              </label>
              <label>
                Exception review date
                <input name="review_date" type="date" required />
              </label>
              <button className="primary" disabled={busy}>
                Save exception
              </button>
            </form>
          )}
          <div className="dialog-actions">
            <button className="secondary" onClick={edit}>
              Edit draft
            </button>
          </div>
        </>
      )}
      {["Draft", "Returned"].includes(row.lifecycle_state) &&
        allowed("framework.submit") && (
          <SubmitForReview
            templates={templates}
            busy={busy}
            onSubmit={(workflow) =>
              void send(
                "frameworks/" + row.object_id + "/actions/submit",
                { workflow_version: workflow },
                "POST",
                row.revision_id,
                "Framework submitted for independent review.",
              )
            }
          />
        )}
    </>
  );
}

function TargetEditor(
  props: Shared & {
    row?: Row;
    indicators: Row[];
    periods: Row[];
    targets: Row[];
  },
) {
  const { row, indicators, periods, targets } = props;
  const { error, busy, send } = useSender(props);
  const [kind, setKind] = useState(row?.data.target_kind || "VALUE");
  const [basis, setBasis] = useState(row?.data.target_basis || "ORIGINAL");
  const [state, setState] = useState(row?.data.value_state || "PRESENT");
  const [indicator, setIndicator] = useState(
    row?.data.indicator_id || indicators[0]?.object_id || "",
  );
  const [period, setPeriod] = useState(row?.data.period_id || "");
  function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = Object.fromEntries(new FormData(e.currentTarget)) as Record<
      string,
      string
    >;
    const present = state === "PRESENT";
    const data: Record<string, any> = {
      indicator_id: indicator,
      period_id: period,
      target_kind: kind,
      target_basis: basis,
      value_state: state,
      direction:
        kind === "RANGE"
          ? "RANGE"
          : kind === "MILESTONE"
            ? "MILESTONE"
            : form.direction,
      value: present && kind !== "RANGE" ? form.value.trim() : null,
      low: present && kind === "RANGE" ? form.low.trim() : null,
      high: present && kind === "RANGE" ? form.high.trim() : null,
      milestone_label: kind === "MILESTONE" ? form.milestone_label : null,
      due_at:
        kind === "MILESTONE" && form.due_at
          ? new Date(form.due_at + "Z").toISOString()
          : null,
      supersedes_revision: basis === "REVISED" ? form.supersedes : null,
      reason: basis === "REVISED" ? form.reason : null,
    };
    void send(
      "targets" + (row ? "/" + row.object_id : ""),
      data,
      row ? "PATCH" : "POST",
      row?.revision_id,
      "Target draft saved. The version and audit receipt have been recorded.",
    );
  }
  const approved = targets.filter(
    (t) =>
      t.lifecycle_state === "Approved" &&
      t.data.indicator_id === indicator &&
      t.data.period_id === period,
  );
  return (
    <form onSubmit={submit}>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      <div className="form-grid">
        <label>
          Target indicator
          <select
            aria-label="Target indicator"
            required
            value={indicator}
            onChange={(e) => setIndicator(e.target.value)}
          >
            {indicators.map((i) => (
              <option key={i.object_id} value={i.object_id}>
                {indicatorName(i)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Target period
          <select
            aria-label="Target period"
            required
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
          >
            <option value="" disabled>
              Choose a period
            </option>
            {periods.map((p) => (
              <option key={p.object_id} value={p.object_id}>
                {p.data.code || p.object_id.slice(0, 8)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Target kind
          <select
            aria-label="Target kind"
            value={kind}
            onChange={(e) => setKind(e.target.value)}
          >
            <option value="VALUE">Value</option>
            <option value="RANGE">Range</option>
            <option value="MILESTONE">Milestone</option>
          </select>
        </label>
        <label>
          Target basis
          <select
            aria-label="Target basis"
            value={basis}
            onChange={(e) => setBasis(e.target.value)}
          >
            <option value="ORIGINAL">Original target</option>
            <option value="BASELINE">Baseline</option>
            <option value="REVISED">Revised target</option>
          </select>
        </label>
        {kind === "VALUE" && (
          <label>
            Direction
            <select
              aria-label="Direction"
              name="direction"
              defaultValue={row?.data.direction || "HIGHER"}
            >
              <option value="HIGHER">Higher is better</option>
              <option value="LOWER">Lower is better</option>
            </select>
          </label>
        )}
        <label>
          Value state
          <select
            aria-label="Value state"
            value={state}
            onChange={(e) => setState(e.target.value)}
          >
            {[
              "PRESENT",
              "MISSING",
              "NOT_COLLECTED",
              "NOT_APPLICABLE",
              "UNDEFINED",
            ].map((s) => (
              <option key={s} value={s}>
                {s.replaceAll("_", " ").toLowerCase()}
              </option>
            ))}
          </select>
        </label>
      </div>
      {state === "PRESENT" &&
        (kind === "RANGE" ? (
          <div className="form-grid">
            <label>
              Lower bound
              <input
                name="low"
                required
                inputMode="decimal"
                defaultValue={row?.data.low || ""}
              />
            </label>
            <label>
              Upper bound
              <input
                name="high"
                required
                inputMode="decimal"
                defaultValue={row?.data.high || ""}
              />
            </label>
          </div>
        ) : (
          <label>
            Target value
            <input
              name="value"
              required
              inputMode="decimal"
              pattern="-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?"
              defaultValue={row?.data.value || ""}
            />
          </label>
        ))}
      {state !== "PRESENT" && (
        <p className="muted">
          A blank target is recorded with its state and no value. It is never
          treated as zero.
        </p>
      )}
      {kind === "MILESTONE" && (
        <div className="form-grid">
          <label>
            Milestone label
            <input
              name="milestone_label"
              required
              maxLength={200}
              defaultValue={row?.data.milestone_label || ""}
            />
          </label>
          <label>
            Milestone due (UTC)
            <input
              name="due_at"
              type="datetime-local"
              required
              defaultValue={(row?.data.due_at || "").slice(0, 16)}
            />
          </label>
        </div>
      )}
      {basis === "REVISED" && (
        <>
          <label>
            Superseded target
            <select
              aria-label="Superseded target"
              name="supersedes"
              required
              defaultValue={row?.data.supersedes_revision || ""}
            >
              <option value="" disabled>
                Choose the approved target
              </option>
              {approved.map((t) => (
                <option key={t.object_id} value={t.revision_id}>
                  {targetValue(t.data)} · {t.data.target_basis}
                </option>
              ))}
            </select>
          </label>
          <label>
            Revision reason
            <textarea
              name="reason"
              required
              maxLength={2000}
              defaultValue={row?.data.reason || ""}
            />
          </label>
        </>
      )}
      <div className="dialog-actions">
        <button className="primary" disabled={busy}>
          Save target draft
        </button>
      </div>
    </form>
  );
}

function TargetDetail(
  props: Shared & { row: Row; templates: Row[]; edit: () => void },
) {
  const { row, templates, edit, allowed } = props;
  const { error, busy, send } = useSender(props);
  const open = ["Draft", "Returned"].includes(row.lifecycle_state);
  return (
    <>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      <div className="detail-meta">
        <span className={"badge " + row.lifecycle_state.toLowerCase()}>
          {row.lifecycle_state}
        </span>{" "}
        Revision {row.revision_id.slice(0, 8)}
      </div>
      <dl className="fields">
        {[
          ["Kind", row.data.target_kind],
          ["Basis", row.data.target_basis],
          ["Direction", row.data.direction],
          ["Value", targetValue(row.data)],
          ["Milestone", row.data.milestone_label || "—"],
          ["Pinned definition", row.data.indicator_version || "At submission"],
        ].map(([k, v]) => (
          <React.Fragment key={k}>
            <dt>{k}</dt>
            <dd>{v}</dd>
          </React.Fragment>
        ))}
      </dl>
      {open && allowed("targets.draft.edit") && (
        <div className="dialog-actions">
          <button className="secondary" onClick={edit}>
            Edit draft
          </button>
        </div>
      )}
      {open && allowed("target.submit") && (
        <SubmitForReview
          templates={templates}
          busy={busy}
          onSubmit={(workflow) =>
            void send(
              "targets/" + row.object_id + "/actions/submit",
              { workflow_version: workflow },
              "POST",
              row.revision_id,
              "Target submitted for independent review.",
            )
          }
        />
      )}
    </>
  );
}

function Review(
  props: Shared & { row: Row; indicators: Row[]; members: any[] },
) {
  const { row, indicators, members, allowed, base, request } = props;
  const { error, busy, send, setError } = useSender(props);
  const [candidate, setCandidate] = useState<any>(null);
  const [reason, setReason] = useState("");
  useEffect(() => {
    request(base + "workflows/" + row.object_id + "/candidate")
      .then((c) => {
        // The decision binds the exact submitted revision; a changed candidate aborts.
        if (c.record.revision_id !== row.data.candidate_revision)
          throw new Error("The candidate has changed. Refresh the queue.");
        setCandidate(c);
      })
      .catch((e) => setError(props.explain(e)));
  }, [row.object_id]);
  const record = candidate?.record;
  return (
    <>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      {!candidate ? (
        <p role="status">Loading the submitted record…</p>
      ) : candidate.kind === "Framework" ? (
        <>
          <h3>Submitted framework · {record.data.version_label}</h3>
          <Tree
            nodes={record.data.nodes}
            indicators={indicators}
            members={members}
          />
          <Issues report={candidate.completeness} />
          {candidate.superseded && (
            <p className="muted">
              Supersedes approved revision{" "}
              {candidate.superseded.revision_id.slice(0, 8)} from{" "}
              {record.data.effective_from?.slice(0, 10)}.
            </p>
          )}
        </>
      ) : (
        <>
          <h3>Submitted target</h3>
          <p>
            {record.data.target_kind} · {record.data.direction} ·{" "}
            {record.data.target_basis} · {targetValue(record.data)}
          </p>
          {candidate.superseded && (
            <p className="muted">
              Currently effective: {targetValue(candidate.superseded.data)} ·
              reason for revision: {record.data.reason}
            </p>
          )}
        </>
      )}
      <label>
        Decision reason
        <textarea
          maxLength={2000}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
      </label>
      <div className="dialog-actions">
        {(["return", "approve"] as const)
          .filter((a) => allowed("workflow." + a))
          .map((a) => (
            <button
              key={a}
              className={a === "approve" ? "primary" : "secondary"}
              disabled={busy || !candidate}
              onClick={() => {
                if (a === "return" && !reason.trim()) {
                  setError("Add a reason for returning this submission.");
                  return;
                }
                void send(
                  "workflows/" + row.object_id + "/actions/" + a,
                  { candidate_revision: row.data.candidate_revision, reason },
                  "POST",
                  row.revision_id,
                  a === "approve"
                    ? "Approved. The baseline register records this exact revision."
                    : "Returned to the author for changes.",
                );
              }}
            >
              {a === "approve" ? "Approve" : "Return for changes"}
            </button>
          ))}
      </div>
    </>
  );
}
