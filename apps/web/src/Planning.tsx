import React, { useEffect, useState } from "react";
import { usePendingOperations } from "./operations";
import { tabListKeys } from "./a11y";

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
type Relationship = {
  relationship_id: string;
  from_node_id: string;
  to_node_id: string;
  relationship_type: string;
  rationale: string;
  evidence_strength: string;
  assumption_ids: string[];
  external_context: string | null;
};
type Assumption = {
  assumption_id: string;
  kind: string;
  node_ids: string[];
  statement: string;
  expected_condition: string | null;
  evidence: string | null;
  owner_id: string | null;
  review_date: string;
  status: string;
  assessed_by?: string;
  assessed_at?: string;
};
const LEVELS = ["IMPACT", "OUTCOME", "OUTPUT", "ACTIVITY"];
const RELATIONSHIP_TYPES: Record<string, string> = {
  CONTRIBUTES_TO: "contributes to",
  DEPENDS_ON: "depends on",
};
const EVIDENCE = ["STRONG", "MODERATE", "WEAK", "UNTESTED"];
const ASSUMPTION_KINDS = ["ASSUMPTION", "RISK", "CONTEXT"];
const ASSUMPTION_STATUSES = ["UNTESTED", "HOLDS", "AT_RISK", "INVALID"];
const BAND_LABELS: Record<string, string> = {
  ON_TRACK: "On track",
  AT_RISK: "At risk",
  OFF_TRACK: "Off track",
};
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

function TheoryOfChange({
  nodes,
  relationships,
  assumptions,
  members,
}: {
  nodes: Node[];
  relationships: Relationship[];
  assumptions: Assumption[];
  members: any[];
}) {
  const title = (id: string) =>
    nodes.find((n) => n.node_id === id)?.title || id.slice(0, 8);
  const name = (id: string | null) =>
    members.find((m) => m.principal_id === id)?.display_name ||
    (id ? id.slice(0, 8) : "not assigned");
  if (!relationships.length && !assumptions.length) return null;
  return (
    <section className="planning-theory" aria-label="Theory of change">
      <h3>Theory of change</h3>
      {relationships.length ? (
        <ul aria-label="Relationships">
          {relationships.map((r) => (
            <li key={r.relationship_id}>
              <strong>{title(r.from_node_id)}</strong>{" "}
              {RELATIONSHIP_TYPES[r.relationship_type] || r.relationship_type}{" "}
              <strong>{title(r.to_node_id)}</strong>
              <small className="muted">
                {" "}
                · {r.evidence_strength.toLowerCase()} evidence · {r.rationale}
                {r.assumption_ids?.length
                  ? " · rests on " + r.assumption_ids.length + " assumption(s)"
                  : ""}
                {r.external_context ? " · context: " + r.external_context : ""}
              </small>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">No relationships recorded.</p>
      )}
      {assumptions.length > 0 && (
        <ul aria-label="Assumptions">
          {assumptions.map((a) => (
            <li key={a.assumption_id}>
              <span className={"badge assumption-" + a.status.toLowerCase()}>
                {a.status.replaceAll("_", " ")}
              </span>{" "}
              <strong>{a.kind.toLowerCase()}</strong>: {a.statement}
              <small className="muted">
                {" "}
                · owner {name(a.owner_id)} · review by {a.review_date}
                {a.node_ids.length
                  ? " · conditions " + a.node_ids.map(title).join(", ")
                  : ""}
                {a.assessed_at
                  ? " · assessed " + a.assessed_at.slice(0, 10)
                  : ""}
              </small>
            </li>
          ))}
        </ul>
      )}
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
      <div
        className="setup-tabs"
        role="tablist"
        aria-label="Results planning"
        onKeyDown={tabListKeys}
      >
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
                {allowed("framework.export") && (
                  <p>
                    <a
                      href={`${base}/frameworks/${approvedBaseline.framework_id}/logframe.csv?revision_id=${approvedBaseline.revision_id}`}
                    >
                      Download logframe CSV
                    </a>
                    {" · "}
                    <a
                      href={`${base}/frameworks/${approvedBaseline.framework_id}/logframe.xlsx?revision_id=${approvedBaseline.revision_id}`}
                    >
                      Download logframe Excel
                    </a>
                  </p>
                )}
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
          <Progress
            view={view}
            framework={approvedBaseline}
            loadMore={() =>
              request(
                base +
                  "programmes/" +
                  programme +
                  "/targets-vs-actuals?cursor=" +
                  encodeURIComponent(view.next_cursor),
              )
                .then((more) =>
                  setData((d) => ({
                    ...d,
                    view: { ...more, rows: [...d.view.rows, ...more.rows] },
                  })),
                )
                .catch((e) => setError(explain(e)))
            }
          />
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

const SOURCES: Record<string, string> = {
  PROGRAMME_SNAPSHOT: "locked snapshot of this programme",
  CALCULATION: "latest calculation",
};

function ProgressCell({ progress }: { progress: any }) {
  return (
    <>
      {progress.status.replaceAll("_", " ")}
      {progress.band && (
        <span className={"badge band-" + progress.band.toLowerCase()}>
          {" "}
          {BAND_LABELS[progress.band]}
        </span>
      )}
      {progress.attainment_percent && (
        <small>
          {" "}
          ·{" "}
          {progress.attainment_percent === "Undefined"
            ? "attainment undefined"
            : progress.attainment_percent + "% of target"}
        </small>
      )}
      {progress.displayed_deviation && (
        <small className="muted">
          {" "}
          · deviation {progress.displayed_deviation}
        </small>
      )}
    </>
  );
}

function Progress({
  view,
  framework,
  loadMore,
}: {
  view: any;
  framework: any;
  loadMore: () => void;
}) {
  if (!view) return <p>You do not have access to targets.</p>;
  const nodeTitle = (id: string) =>
    framework?.nodes.find((n: Node) => n.node_id === id)?.title || id;
  return (
    <>
      <h2>Targets vs actuals</h2>
      <p className="muted">
        An OFFICIAL actual comes only from this programme&apos;s locked snapshot
        for the period; an open period shows this indicator&apos;s own latest
        calculation, labelled PROVISIONAL. Neither is shared between programmes.
        Attainment uses stored decimals and is rounded once for display.
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
                    {(r.assumption_flags || []).map((a: any) => (
                      <small key={a.assumption_id}>
                        <br />
                        <span
                          className={
                            "badge assumption-" + a.status.toLowerCase()
                          }
                        >
                          {a.kind.toLowerCase()} {a.status.replaceAll("_", " ")}
                        </span>{" "}
                        {a.statement}
                      </small>
                    ))}
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
                    {r.amended_after_close && r.amended_target && (
                      <small>
                        <br />
                        <span className="badge amended">
                          Amended after close
                        </span>{" "}
                        {targetValue(r.amended_target)} ·{" "}
                        {r.amended_target.target_basis.toLowerCase()} · applies
                        prospectively
                      </small>
                    )}
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
                        <small className="muted">
                          {" "}
                          · {SOURCES[r.actual.source] || r.actual.source}
                        </small>
                      </>
                    )}
                  </td>
                  <td>
                    <ProgressCell progress={r.progress} />
                    {r.amended_progress && (
                      <small>
                        <br />
                        Against the amended target:{" "}
                        <ProgressCell progress={r.amended_progress} />
                      </small>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {view.next_cursor && (
        <button className="secondary" onClick={loadMore}>
          Load more indicators
        </button>
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
  const source = row?.data || baseline || {};
  const [relationships, setRelationships] = useState<Relationship[]>(
    (source.relationships || []).map((r: Relationship) => ({
      ...r,
      assumption_ids: r.assumption_ids || [],
      external_context: r.external_context || null,
    })),
  );
  const [assumptions, setAssumptions] = useState<Assumption[]>(
    (source.assumptions || []).map((a: Assumption) => ({ ...a })),
  );
  const [label, setLabel] = useState(
    row?.data.version_label || (baseline ? "Revision" : "Baseline"),
  );
  const [effective, setEffective] = useState(
    (row?.data.effective_from || "").slice(0, 10),
  );
  const update = (i: number, change: Partial<Node>) =>
    setNodes(nodes.map((n, j) => (j === i ? { ...n, ...change } : n)));
  const updateLink = (i: number, change: Partial<Relationship>) =>
    setRelationships(
      relationships.map((r, j) => (j === i ? { ...r, ...change } : r)),
    );
  const updateAssumption = (i: number, change: Partial<Assumption>) =>
    setAssumptions(
      assumptions.map((a, j) => (j === i ? { ...a, ...change } : a)),
    );
  const nodeTitle = (n: Node) => n.title || n.node_type.toLowerCase();
  function submit(e: React.FormEvent) {
    e.preventDefault();
    const data: Record<string, any> = {
      version_label: label,
      nodes: nodes.map((n) => ({
        ...n,
        owner_id: n.owner_id || null,
        parent_node_id: n.parent_node_id || null,
      })),
      relationships: relationships.map((r) => ({
        ...r,
        external_context: r.external_context || null,
      })),
      // Who assessed an assumption's status is server-owned; send only its content.
      assumptions: assumptions.map(
        ({ assessed_by: _by, assessed_at: _at, ...a }) => ({
          ...a,
          owner_id: a.owner_id || null,
          expected_condition: a.expected_condition || null,
          evidence: a.evidence || null,
        }),
      ),
      ...(effective
        ? { effective_from: new Date(effective + "T00:00:00Z").toISOString() }
        : {}),
    };
    if (!row) {
      data.programme_id = programme;
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
      <h3>Theory of change</h3>
      <p className="muted">
        A relationship states how one result contributes to another, with its
        rationale and evidence strength. It never creates a numeric rule: the
        parent result stays uncalculated until an approved method exists.
      </p>
      {relationships.map((r, i) => (
        <fieldset key={r.relationship_id} className="planning-node-editor">
          <legend>Relationship {i + 1}</legend>
          <div className="form-grid">
            <label>
              From node {i + 1}
              <select
                aria-label={"Relationship from " + (i + 1)}
                value={r.from_node_id}
                onChange={(e) =>
                  updateLink(i, { from_node_id: e.target.value })
                }
              >
                {nodes.map((n) => (
                  <option key={n.node_id} value={n.node_id}>
                    {nodeTitle(n)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Relationship type {i + 1}
              <select
                aria-label={"Relationship type " + (i + 1)}
                value={r.relationship_type}
                onChange={(e) =>
                  updateLink(i, { relationship_type: e.target.value })
                }
              >
                {Object.entries(RELATIONSHIP_TYPES).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
            </label>
            <label>
              To node {i + 1}
              <select
                aria-label={"Relationship to " + (i + 1)}
                value={r.to_node_id}
                onChange={(e) => updateLink(i, { to_node_id: e.target.value })}
              >
                {nodes.map((n) => (
                  <option key={n.node_id} value={n.node_id}>
                    {nodeTitle(n)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Evidence strength {i + 1}
              <select
                aria-label={"Evidence strength " + (i + 1)}
                value={r.evidence_strength}
                onChange={(e) =>
                  updateLink(i, { evidence_strength: e.target.value })
                }
              >
                {EVIDENCE.map((s) => (
                  <option key={s} value={s}>
                    {s.toLowerCase()}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label>
            Rationale {i + 1}
            <textarea
              required
              maxLength={2000}
              value={r.rationale}
              onChange={(e) => updateLink(i, { rationale: e.target.value })}
            />
          </label>
          <label>
            External context {i + 1}
            <input
              maxLength={2000}
              value={r.external_context || ""}
              onChange={(e) =>
                updateLink(i, { external_context: e.target.value })
              }
            />
          </label>
          {assumptions.length > 0 && (
            <div
              role="group"
              aria-label={"Relationship assumptions " + (i + 1)}
            >
              {assumptions.map((a) => (
                <label key={a.assumption_id} className="checkbox">
                  <input
                    type="checkbox"
                    checked={r.assumption_ids.includes(a.assumption_id)}
                    onChange={(e) =>
                      updateLink(i, {
                        assumption_ids: e.target.checked
                          ? [...r.assumption_ids, a.assumption_id]
                          : r.assumption_ids.filter(
                              (x) => x !== a.assumption_id,
                            ),
                      })
                    }
                  />{" "}
                  Relationship {i + 1} rests on: {a.statement || a.kind}
                </label>
              ))}
            </div>
          )}
          <button
            type="button"
            className="secondary"
            onClick={() =>
              setRelationships(relationships.filter((_, j) => j !== i))
            }
          >
            Remove relationship {i + 1}
          </button>
        </fieldset>
      ))}
      <button
        type="button"
        className="secondary"
        disabled={nodes.length < 2}
        onClick={() =>
          setRelationships([
            ...relationships,
            {
              relationship_id: crypto.randomUUID(),
              from_node_id: nodes[1].node_id,
              to_node_id: nodes[0].node_id,
              relationship_type: "CONTRIBUTES_TO",
              rationale: "",
              evidence_strength: "MODERATE",
              assumption_ids: [],
              external_context: null,
            },
          ])
        }
      >
        Add relationship
      </button>
      <h3>Assumptions and context</h3>
      <p className="muted">
        An assumption, risk or context record conditions the results it is
        linked to. Marking it invalid flags those results for review; it never
        changes a recorded actual.
      </p>
      {assumptions.map((a, i) => (
        <fieldset key={a.assumption_id} className="planning-node-editor">
          <legend>Assumption {i + 1}</legend>
          <div className="form-grid">
            <label>
              Assumption kind {i + 1}
              <select
                aria-label={"Assumption kind " + (i + 1)}
                value={a.kind}
                onChange={(e) => updateAssumption(i, { kind: e.target.value })}
              >
                {ASSUMPTION_KINDS.map((k) => (
                  <option key={k} value={k}>
                    {k.toLowerCase()}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Assumption status {i + 1}
              <select
                aria-label={"Assumption status " + (i + 1)}
                value={a.status}
                onChange={(e) =>
                  updateAssumption(i, { status: e.target.value })
                }
              >
                {ASSUMPTION_STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s.replaceAll("_", " ").toLowerCase()}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Assumption owner {i + 1}
              <select
                aria-label={"Assumption owner " + (i + 1)}
                value={a.owner_id || ""}
                onChange={(e) =>
                  updateAssumption(i, { owner_id: e.target.value || null })
                }
              >
                <option value="">Not assigned</option>
                {members.map((m) => (
                  <option key={m.principal_id} value={m.principal_id}>
                    {m.display_name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Assumption review date {i + 1}
              <input
                type="date"
                required
                value={a.review_date}
                onChange={(e) =>
                  updateAssumption(i, { review_date: e.target.value })
                }
              />
            </label>
          </div>
          <label>
            Assumption statement {i + 1}
            <textarea
              required
              maxLength={2000}
              value={a.statement}
              onChange={(e) =>
                updateAssumption(i, { statement: e.target.value })
              }
            />
          </label>
          <label>
            Expected condition {i + 1}
            <input
              maxLength={2000}
              value={a.expected_condition || ""}
              onChange={(e) =>
                updateAssumption(i, { expected_condition: e.target.value })
              }
            />
          </label>
          <label>
            Assumption evidence {i + 1}
            <input
              maxLength={2000}
              value={a.evidence || ""}
              onChange={(e) =>
                updateAssumption(i, { evidence: e.target.value })
              }
            />
          </label>
          <div role="group" aria-label={"Assumption nodes " + (i + 1)}>
            {nodes.map((n) => (
              <label key={n.node_id} className="checkbox">
                <input
                  type="checkbox"
                  checked={a.node_ids.includes(n.node_id)}
                  onChange={(e) =>
                    updateAssumption(i, {
                      node_ids: e.target.checked
                        ? [...a.node_ids, n.node_id]
                        : a.node_ids.filter((x) => x !== n.node_id),
                    })
                  }
                />{" "}
                Assumption {i + 1} conditions {nodeTitle(n)}
              </label>
            ))}
          </div>
          <button
            type="button"
            className="secondary"
            onClick={() =>
              setAssumptions(assumptions.filter((_, j) => j !== i))
            }
          >
            Remove assumption {i + 1}
          </button>
        </fieldset>
      ))}
      <button
        type="button"
        className="secondary"
        onClick={() =>
          setAssumptions([
            ...assumptions,
            {
              assumption_id: crypto.randomUUID(),
              kind: "ASSUMPTION",
              node_ids: [],
              statement: "",
              expected_condition: null,
              evidence: null,
              owner_id: null,
              review_date: "",
              status: "UNTESTED",
            },
          ])
        }
      >
        Add assumption
      </button>
      <h3>Hierarchy preview</h3>
      <Tree nodes={nodes} indicators={indicators} members={members} />
      <TheoryOfChange
        nodes={nodes}
        relationships={relationships}
        assumptions={assumptions}
        members={members}
      />
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
      <TheoryOfChange
        nodes={row.data.nodes || []}
        relationships={row.data.relationships || []}
        assumptions={row.data.assumptions || []}
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
                      // Who recorded an exception is server-owned; send only its content.
                      ...(row.data.exceptions || []).map((x: any) => ({
                        object_id: x.object_id,
                        rule: x.rule,
                        reason: x.reason,
                        review_date: x.review_date,
                      })),
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
  const [scheme, setScheme] = useState(
    row?.data.status_thresholds?.scheme || "",
  );
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
      status_thresholds:
        kind !== "MILESTONE" && form.scheme
          ? {
              scheme: form.scheme,
              on_track: form.on_track.trim(),
              at_risk: form.at_risk.trim(),
            }
          : null,
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
            onChange={(e) => {
              setKind(e.target.value);
              // An attainment scheme belongs to a higher-is-better value target only.
              setScheme("");
            }}
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
      {kind !== "MILESTONE" && (
        <fieldset>
          <legend>Status thresholds</legend>
          <p className="muted">
            Thresholds are reviewed with the target and shown beside every
            comparison. Attainment bands apply to higher-is-better values; a
            deviation band measures the adverse distance from the target in the
            indicator&apos;s unit. A missing, undefined or stale actual is never
            banded.
          </p>
          <div className="form-grid">
            <label>
              Threshold scheme
              <select
                aria-label="Threshold scheme"
                name="scheme"
                value={scheme}
                onChange={(e) => setScheme(e.target.value)}
              >
                <option value="">No thresholds</option>
                {(kind === "VALUE" ? ["ATTAINMENT_PERCENT"] : [])
                  .concat(["DEVIATION"])
                  .map((s) => (
                    <option key={s} value={s}>
                      {s.replaceAll("_", " ").toLowerCase()}
                    </option>
                  ))}
              </select>
            </label>
            {scheme && (
              <>
                <label>
                  {scheme === "ATTAINMENT_PERCENT"
                    ? "On track at or above (%)"
                    : "On track within (deviation)"}
                  <input
                    name="on_track"
                    required
                    inputMode="decimal"
                    pattern="(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?"
                    defaultValue={
                      row?.data.status_thresholds?.on_track ??
                      (scheme === "ATTAINMENT_PERCENT" ? "100" : "0")
                    }
                  />
                </label>
                <label>
                  {scheme === "ATTAINMENT_PERCENT"
                    ? "At risk at or above (%)"
                    : "At risk within (deviation)"}
                  <input
                    name="at_risk"
                    required
                    inputMode="decimal"
                    pattern="(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?"
                    defaultValue={
                      row?.data.status_thresholds?.at_risk ??
                      (scheme === "ATTAINMENT_PERCENT" ? "80" : "")
                    }
                  />
                </label>
              </>
            )}
          </div>
        </fieldset>
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
          [
            "Status thresholds",
            row.data.status_thresholds
              ? row.data.status_thresholds.scheme
                  .replaceAll("_", " ")
                  .toLowerCase() +
                " · on track " +
                row.data.status_thresholds.on_track +
                " · at risk " +
                row.data.status_thresholds.at_risk
              : "None",
          ],
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
          <TheoryOfChange
            nodes={record.data.nodes}
            relationships={record.data.relationships || []}
            assumptions={record.data.assumptions || []}
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
          <dl className="fields" aria-label="Target amendment comparison">
            {candidate.original && (
              <>
                <dt>Original</dt>
                <dd>{targetValue(candidate.original.data)}</dd>
              </>
            )}
            {candidate.superseded && (
              <>
                <dt>Currently effective</dt>
                <dd>{targetValue(candidate.superseded.data)}</dd>
              </>
            )}
            <dt>Proposed</dt>
            <dd>
              {record.data.target_kind} · {record.data.direction} ·{" "}
              {record.data.target_basis} · {targetValue(record.data)}
              {record.data.status_thresholds
                ? " · thresholds " +
                  record.data.status_thresholds.scheme
                    .replaceAll("_", " ")
                    .toLowerCase() +
                  " " +
                  record.data.status_thresholds.on_track +
                  " / " +
                  record.data.status_thresholds.at_risk
                : ""}
            </dd>
          </dl>
          {record.data.reason && (
            <p className="muted">Reason for revision: {record.data.reason}</p>
          )}
          {candidate.amendment?.prospective_only && (
            <p className="muted" role="note">
              The period is {candidate.amendment.period_state.toLowerCase()}:
              this amendment applies prospectively. The official comparison
              stays against the target pinned at close.
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
