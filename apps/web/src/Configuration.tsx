import React, { useEffect, useRef, useState } from "react";
import { tabListKeys } from "./a11y";

// Mirrors domain.METHODS for form guidance only; the server is authoritative.
const METHODS: Record<string, [string[], string[]]> = {
  SUM: [["COUNT", "DECIMAL"], ["FLOW"]],
  POOLED_RATIO: [["RATIO", "PERCENTAGE"], ["FLOW"]],
  COUNT: [["COUNT"], ["EVENT"]],
  LAST_VALID: [
    ["COUNT", "DECIMAL", "RATIO", "PERCENTAGE"],
    ["STOCK", "CUMULATIVE"],
  ],
  MEAN: [
    ["COUNT", "DECIMAL", "RATIO", "PERCENTAGE"],
    ["FLOW", "STOCK"],
  ],
  MEDIAN: [
    ["COUNT", "DECIMAL"],
    ["FLOW", "STOCK"],
  ],
  MIN: [
    ["COUNT", "DECIMAL"],
    ["FLOW", "STOCK"],
  ],
  MAX: [
    ["COUNT", "DECIMAL"],
    ["FLOW", "STOCK"],
  ],
};
const METHOD_LABELS: Record<string, string> = {
  SUM: "sum of approved values",
  POOLED_RATIO: "pooled numerator / denominator",
  COUNT: "count of approved events",
  LAST_VALID: "latest approved position",
  MEAN: "unweighted mean",
  MEDIAN: "median of approved values",
  MIN: "minimum approved value",
  MAX: "maximum approved value",
};
function parseCategories(text: string | undefined) {
  return (text || "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [code, ...rest] = line.split(/\s+/);
      return { code, label: rest.join(" ") || code };
    });
}

export function CoverageSummary({ data }: { data: Record<string, any> }) {
  return (
    <section className="coverage-summary" aria-label="Collection coverage">
      <div className="coverage-counts">
        {[
          ["expected_count", "Expected"],
          ["received_count", "Received"],
          ["valid_count", "Valid"],
          ["approved_count", "Approved"],
          ["pending_count", "Pending"],
          ["missing_count", "Missing"],
          ["excluded_count", "Excluded"],
          ["unplanned_count", "Unplanned"],
          ["overdue_count", "Overdue"],
        ]
          .filter(([key]) => data[key] !== undefined)
          .map(([key, title]) => (
            <div key={key}>
              <span>{title}</span>
              <strong>{data[key]}</strong>
            </div>
          ))}
      </div>
      <p>
        <strong>
          {data.approval_percent
            ? data.approval_percent + "% approved"
            : "Coverage not configured"}
        </strong>{" "}
        · {data.complete ? "Complete collection" : "Incomplete collection"}
      </p>
      {data.plan_revision && (
        <p className="muted">
          Approved plan revision {data.plan_revision.slice(0, 8)} · Counts and
          due status at calculation time.
        </p>
      )}
      {data.obligations && (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Expected source</th>
                <th>Status</th>
                <th>Due (UTC)</th>
              </tr>
            </thead>
            <tbody>
              {data.obligations.map((o: any, i: number) => (
                <tr key={i}>
                  <td>
                    {o.label}
                    <small className="muted">
                      {" "}
                      {o.source_namespace} / {o.source_key}
                    </small>
                  </td>
                  <td>
                    {o.status}
                    {o.overdue ? " · overdue" : ""}
                  </td>
                  <td>{o.due_at.slice(0, 16).replace("T", " ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

type Row = {
  object_id: string;
  revision_id: string;
  lifecycle_state: string;
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
const tabs = {
  "indicator-definitions": "Definitions",
  "indicator-instances": "Indicators",
  "collection-plans": "Collection plans",
};
const name = (r: Row) =>
  r.data.name ||
  r.data.title ||
  r.data.code ||
  r.data.local_applicability ||
  r.object_id.slice(0, 8);

async function pages(
  request: Props["request"],
  path: string,
  signal: AbortSignal,
) {
  let items: Row[] = [],
    cursor: string | null = null;
  do {
    const page: any = await request(
      path +
        "?limit=100" +
        (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""),
      { signal },
    );
    items = [...items, ...page.items];
    cursor = page.next_cursor;
    if (cursor && items.length >= 500)
      throw new Error(
        "This setup view supports 500 records per type. Use the paginated API for larger workspaces.",
      );
  } while (cursor);
  return items;
}

export function ConfigurationPanel({
  base,
  capabilities,
  request,
  explain,
  Dialog,
}: Props) {
  const [tab, setTab] = useState<keyof typeof tabs>("indicator-definitions");
  const [resources, setResources] = useState<Record<string, Row[]>>({});
  const [members, setMembers] = useState<any[]>([]);
  const [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [loading, setLoading] = useState(true);
  const [tick, setTick] = useState(0),
    [editor, setEditor] = useState<{
      route: string;
      row?: Row;
      edit: boolean;
    } | null>(null);
  const allowed = (c: string) => capabilities.includes(c);
  useEffect(() => {
    const control = new AbortController();
    setLoading(true);
    setError("");
    setResources({});
    setMembers([]);
    const routes = [
      ...Object.keys(tabs),
      "programmes",
      "periods",
      "workflow-templates",
    ];
    Promise.all(
      routes
        .filter((r) => allowed(r + ".read"))
        .map(
          async (r) =>
            [r, await pages(request, base + r, control.signal)] as const,
        ),
    )
      .then((data) => {
        if (!control.signal.aborted) setResources(Object.fromEntries(data));
      })
      .catch((e) => {
        if (!control.signal.aborted) setError(explain(e));
      })
      .finally(() => {
        if (!control.signal.aborted) setLoading(false);
      });
    if (allowed("measurement-members.read"))
      request(base + "measurement-members", { signal: control.signal })
        .then((data) => {
          if (!control.signal.aborted) setMembers(data.items);
        })
        .catch((e) => {
          if (!control.signal.aborted) setError(explain(e));
        });
    return () => control.abort();
  }, [base, tick, capabilities.join("|")]);
  const rows = resources[tab] || [];
  return (
    <>
      <div
        className="setup-tabs"
        role="tablist"
        aria-label="Measurement configuration"
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
          </button>
        ))}
      </div>
      <section className="panel setup-panel">
        <div className="setup-heading">
          <div>
            <h2>{tabs[tab]}</h2>
            <p className="muted">
              {tab === "indicator-definitions"
                ? "Define the measure, its population and calculation. Approval fixes the version used by indicators."
                : tab === "indicator-instances"
                  ? "Assign an approved definition, a collector and an independent reviewer to a programme."
                  : "Specify every expected source for a reporting period. Independent approval freezes the obligations."}
            </p>
          </div>
          {allowed(tab + ".draft.create") && (
            <button
              className="primary"
              disabled={loading}
              onClick={() => setEditor({ route: tab, edit: true })}
            >
              New{" "}
              {tab === "indicator-definitions"
                ? "definition"
                : tab === "indicator-instances"
                  ? "indicator"
                  : "collection plan"}
            </button>
          )}
        </div>
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
          <p role="status">Loading configuration…</p>
        ) : !allowed(tab + ".read") ? (
          <p>You do not have access to this configuration.</p>
        ) : !rows.length ? (
          <p className="muted">
            No {tabs[tab].toLowerCase()} yet. Create the first draft to begin.
          </p>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Configuration</th>
                  <th>Revision</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.object_id}>
                    <td>
                      <button
                        className="text record-title"
                        onClick={() =>
                          setEditor({ route: tab, row, edit: false })
                        }
                      >
                        {name(row)}
                      </button>
                    </td>
                    <td>
                      <span
                        className={"badge " + row.lifecycle_state.toLowerCase()}
                      >
                        {row.lifecycle_state}
                      </span>
                    </td>
                    <td>
                      {tab === "indicator-definitions"
                        ? row.data.measurement_type +
                          " · " +
                          row.data.combination_rule
                        : tab === "collection-plans"
                          ? `${row.data.obligations?.length || 0} expected sources`
                          : resources.programmes?.find(
                              (p) => p.object_id === row.data.programme_id,
                            )?.data.title || "Programme required"}
                    </td>
                    <td>{row.revision_id.slice(0, 8)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <p className="muted setup-note">
        Setup order: approve a definition → create an indicator → approve its
        collection plan → activate the indicator → check programme readiness in
        Portfolio. Results remain provisional until governed period closing is
        available.
      </p>
      {editor && (
        <Dialog
          title={
            (editor.edit ? (editor.row ? "Edit " : "New ") : "Inspect ") +
            (editor.route === "indicator-definitions"
              ? "definition"
              : editor.route === "indicator-instances"
                ? "indicator"
                : "collection plan")
          }
          close={() => setEditor(null)}
        >
          <ConfigurationEditor
            key={editor.route + (editor.row?.revision_id || "") + editor.edit}
            {...{ base, request, explain, resources, members, allowed }}
            {...editor}
            editRow={() => setEditor({ ...editor, edit: true })}
            complete={() => {
              setEditor(null);
              setMessage(
                "Saved. The version and audit receipt have been recorded.",
              );
              setTick((v) => v + 1);
            }}
          />
        </Dialog>
      )}
    </>
  );
}

function ConfigurationEditor({
  base,
  route,
  row,
  edit,
  resources,
  members,
  request,
  explain,
  allowed,
  editRow,
  complete,
}: {
  base: string;
  route: string;
  row?: Row;
  edit: boolean;
  resources: Record<string, Row[]>;
  members: any[];
  request: Props["request"];
  explain: Props["explain"];
  allowed: (c: string) => boolean;
  editRow: () => void;
  complete: () => void;
}) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [measure, setMeasure] = useState(row?.data.measurement_type || "COUNT"),
    [semantic, setSemantic] = useState(row?.data.time_semantic || "FLOW"),
    [method, setMethod] = useState(row?.data.combination_rule || "SUM"),
    [dimension, setDimension] = useState<any>(
      row?.data.disaggregation?.dimensions?.[0] || null,
    );
  const methodError = METHODS[method]
    ? METHODS[method][0].includes(measure) &&
      METHODS[method][1].includes(semantic)
      ? ""
      : `${METHOD_LABELS[method][0].toUpperCase() + METHOD_LABELS[method].slice(1)} is not available for ${measure.toLowerCase()} values with ${semantic.toLowerCase()} time semantics.`
    : "Choose a calculation method.";
  const [obligations, setObligations] = useState<any[]>(
    row?.data.obligations || [
      { label: "", source_namespace: "MANUAL", source_key: "", due_at: "" },
    ],
  );
  const [workflow, setWorkflow] = useState("");
  const attempt = useRef<{ signature: string; id: string } | null>(null);
  async function send(data: Record<string, any>, action?: string) {
    setBusy(true);
    setError("");
    const target =
      route +
      (row ? "/" + row.object_id : "") +
      (action ? "/actions/" + action : "");
    const signature = JSON.stringify([target, data]);
    if (attempt.current?.signature !== signature)
      attempt.current = { signature, id: crypto.randomUUID() };
    try {
      await request(base + target, {
        method: action || !row ? "POST" : "PATCH",
        body: JSON.stringify({
          operation_id: attempt.current.id,
          ...(row ? { expected_revision: row.revision_id } : {}),
          data,
        }),
      });
      complete();
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  const input = (
    key: string,
    label: string,
    required = true,
    large = false,
  ) => (
    <label key={key}>
      {label}
      {large ? (
        <textarea
          name={key}
          required={required}
          maxLength={2000}
          defaultValue={row?.data[key] || ""}
        />
      ) : (
        <input
          name={key}
          required={required}
          maxLength={key === "code" || key === "unit" ? 64 : 200}
          defaultValue={row?.data[key] || ""}
        />
      )}
    </label>
  );
  const select = (
    key: string,
    label: string,
    records: Row[],
    revision = false,
  ) => (
    <label>
      {label}
      <select
        name={key}
        aria-label={label}
        required
        defaultValue={row?.data[key] || ""}
      >
        <option value="" disabled>
          Choose {label.toLowerCase()}
        </option>
        {records.map((r) => (
          <option
            key={r.object_id}
            value={revision ? r.revision_id : r.object_id}
          >
            {name(r)}
          </option>
        ))}
      </select>
    </label>
  );
  function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.currentTarget));
    if (route === "indicator-definitions")
      Object.assign(data, {
        source_mode: "MANUAL",
        time_semantic: semantic,
        combination_rule: method,
        display_decimals: Number(data.display_decimals),
        ...(dimension
          ? {
              disaggregation: {
                dimensions: [
                  {
                    ...dimension,
                    categories:
                      dimension.categoriesText === undefined
                        ? dimension.categories
                        : parseCategories(dimension.categoriesText),
                  },
                ].map(({ categoriesText, ...d }) => d),
              },
            }
          : {}),
      });
    delete data.dimension_categories;
    if (route === "indicator-definitions" && methodError) {
      setError(methodError);
      return;
    }
    if (route === "collection-plans")
      Object.assign(data, {
        obligations: obligations.map((o) => ({
          ...o,
          due_at: new Date(o.due_at).toISOString(),
        })),
      });
    void send(data);
  }
  const canEdit =
    row &&
    ["Draft", "Returned"].includes(row.lifecycle_state) &&
    allowed(route + ".draft.edit");
  const submitCap =
    route === "collection-plans"
      ? "collection-plan.submit"
      : "indicator.submit";
  return (
    <>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {!edit && row ? (
        <>
          <div className="detail-meta">
            <span className="badge">{row.lifecycle_state}</span>
            <span>Revision {row.revision_id.slice(0, 8)}</span>
          </div>
          <dl className="fields">
            {Object.entries(row.data)
              .filter(([k]) => k !== "obligations")
              .map(([k, v]) => (
                <React.Fragment key={k}>
                  <dt>{k.replaceAll("_", " ")}</dt>
                  <dd>
                    {v !== null && typeof v === "object" ? (
                      <pre>{JSON.stringify(v, null, 2)}</pre>
                    ) : (
                      String(v)
                    )}
                  </dd>
                </React.Fragment>
              ))}
          </dl>
          {row.data.obligations && (
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Expected source</th>
                    <th>Namespace / key</th>
                    <th>Due (UTC)</th>
                  </tr>
                </thead>
                <tbody>
                  {row.data.obligations.map((o: any, i: number) => (
                    <tr key={i}>
                      <td>{o.label}</td>
                      <td>
                        {o.source_namespace} / {o.source_key}
                      </td>
                      <td>{o.due_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {canEdit && (
            <div className="dialog-actions">
              <button className="secondary" disabled={busy} onClick={editRow}>
                Edit draft
              </button>
            </div>
          )}
          {row.lifecycle_state === "Draft" &&
            route === "indicator-instances" &&
            allowed("indicator.activate") && (
              <button
                className="primary"
                disabled={busy}
                onClick={() => send({}, "activate")}
              >
                Activate indicator
              </button>
            )}
          {route !== "indicator-instances" &&
            ["Draft", "Returned"].includes(row.lifecycle_state) &&
            allowed(submitCap) && (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  void send({ workflow_version: workflow }, "submit");
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
                    {(resources["workflow-templates"] || [])
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
            )}
        </>
      ) : (
        <form onSubmit={submit}>
          {route === "indicator-definitions" && (
            <>
              {input("name", "Definition name")}
              {input("code", "Definition code")}
              <div className="form-grid">
                <label>
                  Measurement type
                  <select
                    aria-label="Measurement type"
                    name="measurement_type"
                    value={measure}
                    onChange={(e) => setMeasure(e.target.value)}
                  >
                    {["COUNT", "DECIMAL", "RATIO", "PERCENTAGE"].map((v) => (
                      <option key={v}>{v}</option>
                    ))}
                  </select>
                </label>
                {input("unit", "Unit")}
              </div>
              {input("population", "Population", true, true)}
              {input("inclusion", "Inclusion criteria", true, true)}
              {input("exclusion", "Exclusion criteria", true, true)}
              {input("method", "Collection method", true, true)}
              {["RATIO", "PERCENTAGE"].includes(measure) && (
                <>
                  {input("numerator_meaning", "Numerator meaning", true, true)}
                  {input(
                    "denominator_meaning",
                    "Denominator meaning",
                    true,
                    true,
                  )}
                </>
              )}
              <label>
                Display decimals
                <input
                  type="number"
                  name="display_decimals"
                  min={0}
                  max={6}
                  required
                  defaultValue={row?.data.display_decimals ?? 2}
                />
              </label>
              <div className="form-grid">
                <label>
                  Time semantic
                  <select
                    aria-label="Time semantic"
                    value={semantic}
                    onChange={(e) => setSemantic(e.target.value)}
                  >
                    {["FLOW", "STOCK", "CUMULATIVE", "EVENT"].map((v) => (
                      <option key={v}>{v}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Calculation method
                  <select
                    aria-label="Calculation method"
                    value={method}
                    onChange={(e) => setMethod(e.target.value)}
                  >
                    {Object.keys(METHODS).map((v) => (
                      <option key={v} value={v}>
                        {METHOD_LABELS[v]}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              {methodError ? (
                <p className="error" role="alert">
                  {methodError}
                </p>
              ) : (
                <p className="muted">
                  Manual collection · {semantic.toLowerCase()} ·{" "}
                  {METHOD_LABELS[method]}. Drafts require independent approval
                  before use.
                </p>
              )}
              <label className="checkbox">
                <input
                  type="checkbox"
                  aria-label="Disaggregate results"
                  checked={!!dimension}
                  onChange={(e) =>
                    setDimension(
                      e.target.checked
                        ? {
                            code: "",
                            label: "",
                            version: "1",
                            multiselect: false,
                            exhaustive: true,
                            categoriesText: "",
                          }
                        : null,
                    )
                  }
                />
                Disaggregate results by one dimension
              </label>
              {dimension && (
                <fieldset>
                  <legend>Disaggregation dimension</legend>
                  <div className="form-grid">
                    {(["code", "label", "version"] as const).map((k) => (
                      <label key={k}>
                        {"Dimension " + k}
                        <input
                          aria-label={"Dimension " + k}
                          required
                          value={dimension[k]}
                          onChange={(e) =>
                            setDimension({ ...dimension, [k]: e.target.value })
                          }
                        />
                      </label>
                    ))}
                  </div>
                  <label>
                    Categories (one per line: CODE Label)
                    <textarea
                      aria-label="Categories"
                      name="dimension_categories"
                      required
                      value={
                        dimension.categoriesText ??
                        (dimension.categories || [])
                          .map((c: any) => c.code + " " + c.label)
                          .join("\n")
                      }
                      onChange={(e) =>
                        setDimension({
                          ...dimension,
                          categoriesText: e.target.value,
                        })
                      }
                    />
                  </label>
                  {(["multiselect", "exhaustive"] as const).map((k) => (
                    <label className="checkbox" key={k}>
                      <input
                        type="checkbox"
                        aria-label={
                          k === "multiselect"
                            ? "Several categories per value"
                            : "Every value must have a category"
                        }
                        checked={dimension[k]}
                        onChange={(e) =>
                          setDimension({ ...dimension, [k]: e.target.checked })
                        }
                      />
                      {k === "multiselect"
                        ? "Several categories per value (category results are not additive)"
                        : "Every value must have a category (otherwise uncoded values are shown as UNSPECIFIED)"}
                    </label>
                  ))}
                </fieldset>
              )}
            </>
          )}
          {route === "indicator-instances" && (
            <>
              {select(
                "programme_id",
                "Programme",
                (resources.programmes || []).filter((r) =>
                  ["Draft", "Active"].includes(r.lifecycle_state),
                ),
              )}
              {select(
                "definition_version",
                "Approved definition",
                (resources["indicator-definitions"] || []).filter(
                  (r) => r.lifecycle_state === "Approved",
                ),
                true,
              )}
              {input("local_applicability", "Local applicability", true, true)}
              {["collector", "reviewer"].map((role) => (
                <label key={role}>
                  {role === "collector" ? "Collector" : "Independent reviewer"}
                  <select
                    aria-label={
                      role === "collector"
                        ? "Collector"
                        : "Independent reviewer"
                    }
                    name={role + "_id"}
                    required
                    defaultValue={row?.data[role + "_id"] || ""}
                  >
                    <option value="" disabled>
                      Choose {role}
                    </option>
                    {members
                      .filter((m) => m[role])
                      .map((m) => (
                        <option key={m.principal_id} value={m.principal_id}>
                          {m.display_name}
                        </option>
                      ))}
                  </select>
                </label>
              ))}
              <p className="muted">
                An approved collection plan is required before activation.
                Assignment does not grant access; current permissions are
                checked by the server.
              </p>
            </>
          )}
          {route === "collection-plans" && (
            <>
              {input("title", "Plan title")}
              {select(
                "indicator_id",
                "Indicator",
                resources["indicator-instances"] || [],
              )}
              {select(
                "period_id",
                "Reporting period",
                (resources.periods || []).filter(
                  (r) => r.lifecycle_state === "Open",
                ),
              )}
              <h3>Expected sources ({obligations.length})</h3>
              <p className="muted">
                Use these exact namespace and source keys when recording
                observations. Include the period in each key. Every source
                remains expected until an approved plan amendment is supported.
                For values that will arrive by file import, use the namespace
                IMPORT and the key unit key/indicator id/period id; the import
                preview shows each value&apos;s key.
              </p>
              {obligations.map((o, i) => (
                <fieldset className="obligation" key={i}>
                  <legend>Source {i + 1}</legend>
                  <div className="form-grid">
                    {[
                      ["label", "Source label"],
                      ["source_namespace", "Namespace"],
                      ["source_key", "Source key"],
                      ["due_at", "Due date and time (UTC)"],
                    ].map(([key, label]) => (
                      <label key={key}>
                        {label}
                        <input
                          aria-label={label + " " + (i + 1)}
                          type={key === "due_at" ? "datetime-local" : "text"}
                          required
                          maxLength={key === "source_namespace" ? 64 : 200}
                          value={
                            key === "due_at" ? o[key].slice(0, 16) : o[key]
                          }
                          onChange={(e) =>
                            setObligations((old) =>
                              old.map((item, n) =>
                                n === i
                                  ? {
                                      ...item,
                                      [key]:
                                        key === "due_at" && e.target.value
                                          ? e.target.value + ":00Z"
                                          : e.target.value,
                                    }
                                  : item,
                              ),
                            )
                          }
                        />
                      </label>
                    ))}
                  </div>
                  <button
                    type="button"
                    className="text"
                    disabled={obligations.length === 1}
                    onClick={() =>
                      setObligations((old) => old.filter((_, n) => n !== i))
                    }
                  >
                    Remove source {i + 1}
                  </button>
                </fieldset>
              ))}
              <button
                type="button"
                className="secondary"
                disabled={obligations.length >= 500}
                onClick={() =>
                  setObligations((old) => [
                    ...old,
                    {
                      label: "",
                      source_namespace: "MANUAL",
                      source_key: "",
                      due_at: "",
                    },
                  ])
                }
              >
                Add expected source
              </button>
            </>
          )}
          <div className="dialog-actions">
            <button className="primary" disabled={busy}>
              {busy ? "Saving…" : "Save draft"}
            </button>
          </div>
        </form>
      )}
    </>
  );
}

export function ProgrammeReadiness({
  base,
  row,
  request,
  explain,
  allowed,
  complete,
}: {
  base: string;
  row: Row;
  request: Props["request"];
  explain: Props["explain"];
  allowed: (cap: string) => boolean;
  complete: () => void;
}) {
  const [value, setValue] = useState<any>(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [reason, setReason] = useState("");
  const attempt = useRef<{ action: string; id: string } | null>(null);
  useEffect(() => {
    const c = new AbortController();
    request(base + "programmes/" + row.object_id + "/readiness", {
      signal: c.signal,
    })
      .then((x) => {
        if (!c.signal.aborted) setValue(x);
      })
      .catch((e) => {
        if (!c.signal.aborted) setError(explain(e));
      });
    return () => c.abort();
  }, [base, row.revision_id]);
  async function act(action: string) {
    setBusy(true);
    setError("");
    const signature = action + reason;
    if (attempt.current?.action !== signature)
      attempt.current = { action: signature, id: crypto.randomUUID() };
    try {
      await request(
        base + "programmes/" + row.object_id + "/actions/" + action,
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: attempt.current.id,
            expected_revision: row.revision_id,
            data: action === "revise" ? { reason } : {},
          }),
        },
      );
      complete();
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="readiness">
      <h3>Measurement readiness</h3>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      {!value && !error ? (
        <p>Checking configuration…</p>
      ) : (
        value && (
          <>
            <p className="muted">
              Manual measurement release: programme details, active references,
              approved definitions, independent assignments and collection
              obligations.
            </p>
            <ul>
              {value.checks.map((check: any) => (
                <li key={check.code}>
                  <span aria-label={check.passed ? "Passed" : "Blocked"}>
                    {check.passed ? "✓" : "○"}
                  </span>{" "}
                  {check.message.replaceAll("_", " ")}
                </li>
              ))}
            </ul>
          </>
        )
      )}
      {allowed("programme.activate") && (
        <div className="dialog-actions">
          {row.lifecycle_state === "Draft" && (
            <button
              className="primary"
              disabled={busy || !value?.ready}
              onClick={() => act("ready")}
            >
              Mark ready
            </button>
          )}
          {row.lifecycle_state === "Ready" && (
            <>
              <button
                className="primary"
                disabled={busy || !value?.ready}
                onClick={() => act("activate")}
              >
                Activate programme
              </button>
              <label>
                Revision reason
                <input
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  maxLength={2000}
                />
              </label>
              <button
                className="secondary"
                disabled={busy || !reason.trim()}
                onClick={() => act("revise")}
              >
                Return to draft
              </button>
            </>
          )}
        </div>
      )}
    </section>
  );
}
