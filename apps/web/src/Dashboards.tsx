import React, { useEffect, useState } from "react";

import { PortfolioPanel } from "./Portfolio";
import { tabListKeys } from "./a11y";

type Props = {
  base: string;
  capabilities: string[];
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
};
type Row = {
  object_id: string;
  revision_id: string;
  classification?: string;
  data: Record<string, any>;
};
type Value = {
  mode: "OFFICIAL" | "PROVISIONAL";
  value_state: string;
  value: string | null;
  displayed_value: string | null;
  numerator: string | null;
  denominator: string | null;
  reason_code: string | null;
  calculated_at: string | null;
  disaggregation: any[];
};

async function all(request: Props["request"], path: string) {
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
  } while (cursor && items.length < 500);
  return items;
}

const words = (s: string | null | undefined) =>
  (s || "").replaceAll("_", " ").toLowerCase();
const when = (s: string | null | undefined) =>
  s ? s.replace("T", " ").slice(0, 16) + " UTC" : "—";

// A value is shown only from its own display string; a value that is not PRESENT is named by its
// state and reason, never as zero.
function Shown({ value, unit }: { value: Value | null; unit?: string }) {
  if (!value) return <span className="muted">None</span>;
  if (value.value_state !== "PRESENT" || value.displayed_value === null)
    return (
      <span>
        <strong>{words(value.value_state)}</strong>
        {value.reason_code ? (
          <small className="muted"> · {words(value.reason_code)}</small>
        ) : null}
      </span>
    );
  return (
    <span>
      <strong className="dashboard-number">{value.displayed_value}</strong>
      {unit ? <small className="muted"> {unit}</small> : null}
      {value.numerator !== null && value.denominator !== null ? (
        <small className="muted">
          {" "}
          ({value.numerator} / {value.denominator})
        </small>
      ) : null}
    </span>
  );
}

const spoken = (v: Value | null) =>
  v ? (v.displayed_value ?? words(v.value_state)) : "none";

function targetText(t: any) {
  if (!t) return "No approved target";
  if (t.value_state !== "PRESENT") return words(t.value_state);
  if (t.target_kind === "RANGE")
    return t.displayed_low + "–" + t.displayed_high;
  return t.displayed_value;
}

function targetContext(t: any) {
  if (!t) return null;
  const period = t.applicable_period;
  return [
    t.version_label,
    period?.period_code || period?.period_id?.slice(0, 8),
    period?.starts_at && period?.ends_at
      ? `${period.starts_at.slice(0, 10)} to ${period.ends_at.slice(0, 10)}`
      : null,
    t.time_semantic ? words(t.time_semantic) : null,
  ]
    .filter(Boolean)
    .join(" · ");
}

function Coverage({ c }: { c: any }) {
  if (c.applicability === "UNAVAILABLE")
    return (
      <span className="muted">Not available · {words(c.reason_code)}</span>
    );
  if (c.applicability === "NOT_APPLICABLE")
    return (
      <span>
        Not applicable{" "}
        <small className="muted">
          · {c.expected_count} expected, {c.required_count} required
        </small>
      </span>
    );
  return (
    <span>
      {c.approval_percent}% approved{" "}
      <small className="muted">
        · {c.approved_count} of {c.required_count} required, {c.pending_count}{" "}
        pending, {c.missing_count} missing, {c.received_count} received
        {c.source === "CLOSE_SNAPSHOT" ? " · as locked" : " · current plan"}
      </small>
    </span>
  );
}

function Freshness({ f }: { f: any }) {
  const state = f.stale === null ? "Unknown" : f.stale ? "Stale" : "Up to date";
  return (
    <span>
      <span
        className={
          "badge " +
          (f.stale ? "stale" : f.stale === null ? "draft" : "approved")
        }
      >
        {state}
      </span>
      {f.stale_reasons.length ? (
        <small> {f.stale_reasons.map(words).join("; ")}</small>
      ) : null}
      <small className="muted">
        <br />
        State {words(f.data_state)} · last valid data{" "}
        {when(f.last_valid_data_at)}
        <br />
        Last source success {when(f.last_source_success_at)} · approval cutoff{" "}
        {when(f.approval_cutoff_at)} · calculation {when(f.calculation_at)}
        <br />
        {f.locked_at ? "Locked " + when(f.locked_at) + " · " : ""}
        {f.provisional_calculated_at
          ? "Calculated " + when(f.provisional_calculated_at) + " · "
          : ""}
        Last source change {when(f.last_source_change_at)}
        {f.source_check === "NOT_PERMITTED"
          ? " · some sources are outside your access"
          : ""}
        <br />
        Dashboard fetched {when(f.dashboard_fetched_at)}; fetch success does not
        change freshness.
      </small>
    </span>
  );
}

// One series as bars from a zero baseline: official values filled, provisional values outlined,
// targets as a horizontal tick. Geometry only; every number shown is the server's display string.
function SeriesChart({ series }: { series: any }) {
  const points = series.points;
  const numbers: number[] = [];
  for (const p of points) {
    for (const v of [p.official, p.provisional])
      if (v && v.value_state === "PRESENT") numbers.push(Number(v.value));
    if (p.target?.value_state === "PRESENT" && p.target.value !== null)
      numbers.push(Number(p.target.value));
  }
  if (!points.length)
    return <p className="muted">No periods with values or targets yet.</p>;
  const top = Math.max(0, ...numbers) || 1,
    bottom = Math.min(0, ...numbers);
  const width = 640,
    height = 220,
    pad = 28,
    slot = (width - pad * 2) / points.length,
    bar = Math.min(48, slot * 0.38);
  const y = (n: number) =>
    pad + ((top - n) / (top - bottom || 1)) * (height - pad * 2);
  const describe = points
    .map(
      (p: any) =>
        (p.period_code || p.period_id.slice(0, 8)) +
        ": official " +
        spoken(p.official) +
        (p.provisional ? ", provisional " + spoken(p.provisional) : "") +
        (p.target ? ", target " + targetText(p.target) : ""),
    )
    .join("; ");
  return (
    <figure className="dashboard-chart">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-labelledby="series-title series-desc"
      >
        <title id="series-title">{series.indicator_label} by period</title>
        <desc id="series-desc">{describe}</desc>
        <line
          x1={pad}
          x2={width - pad}
          y1={y(0)}
          y2={y(0)}
          className="chart-axis"
        />
        {points.map((p: any, i: number) => {
          const x = pad + slot * i + slot / 2;
          const o =
            p.official?.value_state === "PRESENT"
              ? Number(p.official.value)
              : null;
          const v =
            p.provisional?.value_state === "PRESENT"
              ? Number(p.provisional.value)
              : null;
          const t =
            p.target?.value_state === "PRESENT" && p.target.value !== null
              ? Number(p.target.value)
              : null;
          return (
            <g key={p.period_id}>
              {o !== null && (
                <rect
                  className="chart-official"
                  x={x - bar - 2}
                  width={bar}
                  y={Math.min(y(o), y(0))}
                  height={Math.max(1, Math.abs(y(0) - y(o)))}
                  rx={4}
                >
                  <title>
                    {(p.period_code || "") +
                      " official " +
                      p.official.displayed_value}
                  </title>
                </rect>
              )}
              {o !== null && (
                <text
                  className="chart-value"
                  x={x - bar / 2 - 2}
                  y={Math.min(y(o), y(0)) - 6}
                  textAnchor="middle"
                >
                  {p.official.displayed_value}
                </text>
              )}
              {v !== null && (
                <rect
                  className="chart-provisional"
                  x={x + 2}
                  width={bar}
                  y={Math.min(y(v), y(0))}
                  height={Math.max(1, Math.abs(y(0) - y(v)))}
                  rx={4}
                >
                  <title>
                    {(p.period_code || "") +
                      " provisional " +
                      p.provisional.displayed_value}
                  </title>
                </rect>
              )}
              {t !== null && (
                <line
                  className="chart-target"
                  x1={x - bar - 6}
                  x2={x + bar + 6}
                  y1={y(t)}
                  y2={y(t)}
                />
              )}
              <text x={x} y={height - 8} textAnchor="middle">
                {p.period_code || p.period_id.slice(0, 8)}
              </text>
            </g>
          );
        })}
      </svg>
      <figcaption className="chart-legend">
        <span>
          <i className="key official" /> Official (locked snapshot)
        </span>
        <span>
          <i className="key provisional" /> Provisional (not locked)
        </span>
        <span>
          <i className="key target" /> Target
        </span>
      </figcaption>
    </figure>
  );
}

export function DashboardsPanel({
  base,
  capabilities,
  request,
  explain,
}: Props) {
  const allowed = (c: string) => capabilities.includes(c);
  const [programmes, setProgrammes] = useState<Row[]>([]),
    [periods, setPeriods] = useState<Row[]>([]),
    [programme, setProgramme] = useState(""),
    [period, setPeriod] = useState(""),
    [view, setView] = useState<any>(null),
    [indicator, setIndicator] = useState(""),
    [series, setSeries] = useState<any>(null),
    [mode, setMode] = useState<"programme" | "portfolio" | "authored">(
      "programme",
    ),
    [savedDashboards, setSavedDashboards] = useState<Row[]>([]),
    [calculatedResults, setCalculatedResults] = useState<Row[]>([]),
    [savedDashboard, setSavedDashboard] = useState(""),
    [authoredPreview, setAuthoredPreview] = useState<any>(null),
    [viewport, setViewport] = useState<"DESKTOP" | "MOBILE" | "TABLE">(
      "DESKTOP",
    ),
    [drillLevel, setDrillLevel] = useState(""),
    [filterField, setFilterField] = useState("programme"),
    [filterValue, setFilterValue] = useState(""),
    [pivotDimension, setPivotDimension] = useState("service_type"),
    [pivotStatistic, setPivotStatistic] = useState("DISTINCT_COUNT"),
    [pivotResult, setPivotResult] = useState<any>(null),
    [geographicPreview, setGeographicPreview] = useState<any>(null),
    [recipientId, setRecipientId] = useState(""),
    [sharingPreview, setSharingPreview] = useState<any>(null),
    [publicationId, setPublicationId] = useState(""),
    [publicationStatus, setPublicationStatus] = useState<any>(null),
    [publicationAudience, setPublicationAudience] = useState<
      "INTERNAL" | "PUBLIC"
    >("INTERNAL"),
    [publicationExpiry, setPublicationExpiry] = useState(() => {
      const value = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
      return value.toISOString().slice(0, 16);
    }),
    [publicationMessage, setPublicationMessage] = useState(""),
    [alertRule, setAlertRule] = useState(""),
    [alertRules, setAlertRules] = useState<any[]>([]),
    [alertIncidents, setAlertIncidents] = useState<any[]>([]),
    [alertResult, setAlertResult] = useState(""),
    [alertOperator, setAlertOperator] = useState<"LT" | "GT">("LT"),
    [alertThreshold, setAlertThreshold] = useState("0"),
    [alertCoverage, setAlertCoverage] = useState(75),
    [alertFreshness, setAlertFreshness] = useState(2678400),
    [alertCadence, setAlertCadence] = useState<"DAILY" | "WEEKLY" | "MONTHLY">(
      "MONTHLY",
    ),
    [alertCooldown, setAlertCooldown] = useState(86400),
    [alertOutcome, setAlertOutcome] = useState<any>(null),
    [sourcesFor, setSourcesFor] = useState(""),
    [sources, setSources] = useState<any>(null),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(false),
    [tick, setTick] = useState(0);
  const permitted =
    allowed("dashboards.read") &&
    allowed("programmes.read") &&
    allowed("periods.read");
  const canAuthor =
    allowed("dashboards.read") &&
    allowed("dashboards.draft.create") &&
    allowed("calculated-results.read");
  const canCopy =
    allowed("dashboards.read") && allowed("dashboards.draft.create");
  const canPublish =
    allowed("dashboards.read") && allowed("dashboards.draft.edit");
  useEffect(() => {
    if (!permitted) return;
    Promise.all([
      all(request, base + "programmes"),
      all(request, base + "periods"),
    ])
      .then(([p, q]) => {
        setProgrammes(p);
        setPeriods(q);
        setProgramme((c) => c || p[0]?.object_id || "");
        setPeriod((c) => c || q[0]?.object_id || "");
      })
      .catch((e) => setError(explain(e)));
  }, [base, permitted]);
  useEffect(() => {
    if (!programme || !period) return;
    let live = true;
    setLoading(true);
    setError("");
    request(
      base +
        "programmes/" +
        programme +
        "/dashboard?limit=50&period_id=" +
        period,
    )
      .then((v) => {
        if (!live) return;
        setView(v);
        setIndicator((c) =>
          v.indicators.some((x: any) => x.indicator_id === c)
            ? c
            : v.indicators[0]?.indicator_id || "",
        );
      })
      .catch((e) => live && setError(explain(e)))
      .finally(() => live && setLoading(false));
    return () => {
      live = false;
    };
  }, [programme, period, tick, base]);
  useEffect(() => {
    if (!indicator) {
      setSeries(null);
      return;
    }
    let live = true;
    request(
      base + "indicator-instances/" + indicator + "/dashboard-series?limit=24",
    )
      .then((s) => live && setSeries(s))
      .catch((e) => live && setError(explain(e)));
    return () => {
      live = false;
    };
  }, [indicator, tick, base]);
  // Drill-down (v0.27): the source observations behind the value a card shows, as this reader
  // may see them; a PARTIAL set says rows are withheld, never how many.
  useEffect(() => {
    if (!sourcesFor || !period) {
      setSources(null);
      return;
    }
    let live = true;
    request(
      base +
        "indicator-instances/" +
        sourcesFor +
        "/dashboard-sources?limit=100&period_id=" +
        period,
    )
      .then((s) => live && setSources(s))
      .catch((e) => live && setError(explain(e)));
    return () => {
      live = false;
    };
  }, [sourcesFor, period, tick, base]);
  useEffect(() => {
    if (mode !== "authored" || !canAuthor) return;
    Promise.all([
      all(request, base + "dashboards"),
      all(request, base + "calculated-results"),
      all(request, base + "dashboard-alert-rules"),
    ])
      .then(([dashboards, results, rules]) => {
        setSavedDashboards(dashboards);
        setCalculatedResults(results);
        setAlertRules(rules);
        setAlertRule((current) =>
          rules.some((row: any) => row.object_id === current)
            ? current
            : rules[0]?.object_id || "",
        );
        setSavedDashboard(
          (current) => current || dashboards[0]?.object_id || "",
        );
      })
      .catch((e) => setError(explain(e)));
  }, [mode, canAuthor, base, tick]);
  useEffect(() => {
    if (mode !== "authored" || !alertRule) {
      setAlertIncidents([]);
      return;
    }
    all(request, `${base}dashboard-alert-rules/${alertRule}/incidents`)
      .then(setAlertIncidents)
      .catch((e) => setError(explain(e)));
  }, [mode, alertRule, base, tick]);
  useEffect(() => {
    if (mode !== "authored" || !savedDashboard) {
      setAuthoredPreview(null);
      return;
    }
    request(
      `${base}dashboards/${savedDashboard}/preview?viewport=${viewport}${drillLevel ? `&drill_level=${drillLevel}` : ""}`,
    )
      .then(setAuthoredPreview)
      .catch((e) => setError(explain(e)));
  }, [mode, savedDashboard, viewport, drillLevel, base, tick]);
  const widgetFor = (result: Row, position: number) => ({
    widget_id: crypto.randomUUID(),
    type: "METRIC",
    title: `Result ${result.object_id.slice(0, 8)}`,
    binding: {
      resource_type: "CALCULATED_RESULT",
      object_id: result.object_id,
      revision_id: result.revision_id,
    },
    view_mode: result.data.mode || "PROVISIONAL",
    period_id: result.data.period_id,
    dimensions: [],
    disclosure_context: {
      classification: result.classification || "INTERNAL",
      quality_context_required: true,
    },
    position,
    width: 6,
    compatible_filters: ["programme", "period", "indicator"],
    drilldown_levels: ["PORTFOLIO", "PARTNER", "PROGRAMME"],
    approved_slices: [],
  });
  async function createAuthoredDashboard() {
    const result = calculatedResults[0];
    if (!result) return setError("A permitted calculated result is required.");
    try {
      const receipt = await request(base + "dashboards", {
        method: "POST",
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          data: {
            title: "New private dashboard",
            mode: "PRIVATE_DRAFT",
            widgets: [widgetFor(result, 0)],
            filters: { terms: [] },
          },
        }),
      });
      setSavedDashboard(receipt.object_id);
      setTick((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    }
  }
  async function addWidget() {
    const dashboard = savedDashboards.find(
      (row) => row.object_id === savedDashboard,
    );
    if (!dashboard || dashboard.data.widgets.length >= 10) return;
    const used = new Set(
      dashboard.data.widgets.map((widget: any) => widget.binding.object_id),
    );
    const result = calculatedResults.find((row) => !used.has(row.object_id));
    if (!result)
      return setError("No additional permitted result is available.");
    try {
      await request(base + "dashboards/" + dashboard.object_id, {
        method: "PATCH",
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          expected_revision: dashboard.revision_id,
          data: {
            widgets: [
              ...dashboard.data.widgets,
              widgetFor(result, dashboard.data.widgets.length),
            ],
          },
        }),
      });
      setTick((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    }
  }
  async function addMapWidget() {
    const dashboard = savedDashboards.find(
      (row) => row.object_id === savedDashboard,
    );
    const result = calculatedResults.find((row) =>
      row.data.disaggregation?.some(
        (entry: any) => entry.dimension && entry.dimension_version,
      ),
    );
    const geographic = result?.data.disaggregation?.find(
      (entry: any) => entry.dimension && entry.dimension_version,
    );
    if (!dashboard || !result || !geographic)
      return setError("A versioned geographic result is required.");
    if (dashboard.data.widgets.length >= 10) return;
    const widget = {
      ...widgetFor(result, dashboard.data.widgets.length),
      type: "MAP",
      title: `Map ${result.object_id.slice(0, 8)}`,
      geographic_config: {
        dimension: geographic.dimension,
        boundary_version: geographic.dimension_version,
        layer: "AGGREGATE",
        granularity: "DISTRICT",
        legend: "Approved result by district",
        missingness: "SHOW_MISSING",
        external_map: false,
      },
    };
    try {
      await request(base + "dashboards/" + dashboard.object_id, {
        method: "PATCH",
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          expected_revision: dashboard.revision_id,
          data: { widgets: [...dashboard.data.widgets, widget] },
        }),
      });
      setTick((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    }
  }
  async function previewMap() {
    const dashboard = savedDashboards.find(
      (row) => row.object_id === savedDashboard,
    );
    const widget = dashboard?.data.widgets.find(
      (item: any) => item.type === "MAP",
    );
    if (!dashboard || !widget)
      return setError("A configured map widget is required.");
    try {
      setGeographicPreview(
        await request(
          `${base}dashboards/${dashboard.object_id}/geographic-preview?widget_id=${encodeURIComponent(widget.widget_id)}`,
        ),
      );
    } catch (e) {
      setError(explain(e));
    }
  }
  async function copyDashboard() {
    if (!savedDashboard) return;
    try {
      setError("");
      setPublicationMessage("");
      const receipt = await request(
        `${base}dashboards/${savedDashboard}/actions/copy`,
        {
          method: "POST",
          body: JSON.stringify({ operation_id: crypto.randomUUID(), data: {} }),
        },
      );
      setSavedDashboard(receipt.object_id);
      setSharingPreview(null);
      setPublicationId("");
      setPublicationStatus(null);
      setPublicationMessage("Private draft created. No access was granted.");
      setTick((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    }
  }
  async function previewSharing() {
    if (!savedDashboard || !recipientId) return;
    try {
      setError("");
      setSharingPreview(null);
      setSharingPreview(
        await request(
          base +
            "dashboards/" +
            savedDashboard +
            "/sharing-preview?recipient_id=" +
            encodeURIComponent(recipientId),
        ),
      );
    } catch (e) {
      setError(explain(e));
    }
  }
  async function publishDashboard() {
    if (!savedDashboard) return;
    const dashboard = savedDashboards.find(
      (row) => row.object_id === savedDashboard,
    );
    if (!dashboard) return setError("Select a current dashboard draft.");
    const expires = new Date(publicationExpiry);
    if (!Number.isFinite(expires.getTime()) || expires <= new Date()) {
      return setError("Choose a publication expiry in the future.");
    }
    try {
      setError("");
      setPublicationMessage("");
      const receipt = await request(
        base + "dashboards/" + savedDashboard + "/actions/publish",
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            expected_revision: dashboard.revision_id,
            data: {
              audience: publicationAudience,
              expires_at: expires.toISOString(),
            },
          }),
        },
      );
      setPublicationId(receipt.object_id);
      setPublicationMessage("Pinned publication created.");
      setPublicationStatus(
        await request(
          `${base}dashboards/${savedDashboard}/publications/${receipt.object_id}`,
        ),
      );
    } catch (e) {
      setError(explain(e));
    }
  }
  async function refreshPublicationStatus() {
    if (!savedDashboard || !publicationId) return;
    try {
      setError("");
      setPublicationStatus(
        await request(
          `${base}dashboards/${savedDashboard}/publications/${publicationId}`,
        ),
      );
    } catch (e) {
      setError(explain(e));
    }
  }
  async function createAlertRule() {
    if (!indicator || !recipientId) return;
    try {
      const receipt = await request(base + "dashboard-alert-rules", {
        method: "POST",
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          data: {
            measure_id: indicator,
            operator: alertOperator,
            threshold: alertThreshold,
            minimum_coverage: alertCoverage,
            max_freshness_seconds: alertFreshness,
            evaluation_cadence: alertCadence,
            recipient_ids: [recipientId],
            cooldown_seconds: alertCooldown,
          },
        }),
      });
      setAlertRule(receipt.object_id);
      setTick((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    }
  }
  async function evaluateAlert() {
    if (!alertRule || !period) return;
    try {
      setAlertOutcome(
        await request(
          base + "dashboard-alert-rules/" + alertRule + "/actions/evaluate",
          {
            method: "POST",
            body: JSON.stringify({
              operation_id: crypto.randomUUID(),
              data: {
                period_id: period,
                ...(alertResult ? { result_id: alertResult } : {}),
              },
            }),
          },
        ),
      );
      setTick((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    }
  }
  async function applyDashboardFilter() {
    const dashboard = savedDashboards.find(
      (row) => row.object_id === savedDashboard,
    );
    if (!dashboard) return;
    try {
      await request(base + "dashboards/" + dashboard.object_id, {
        method: "PATCH",
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          expected_revision: dashboard.revision_id,
          data: {
            filters: {
              terms: filterValue
                ? [
                    {
                      field: filterField,
                      operator: "EQ",
                      values: [filterValue],
                    },
                  ]
                : [],
            },
          },
        }),
      });
      setTick((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    }
  }
  async function runPivot(preview: boolean) {
    const dashboard = savedDashboards.find(
      (row) => row.object_id === savedDashboard,
    );
    const widget = dashboard?.data.widgets[0];
    if (!dashboard || !widget)
      return setError("A dashboard result widget is required.");
    const data = {
      widget_id: widget.widget_id,
      row_dimension: pivotDimension,
      statistic: pivotStatistic,
    };
    try {
      const result = await request(
        `${base}dashboards/${dashboard.object_id}/${preview ? "pivot-preview" : "actions/run-pivot"}`,
        {
          method: "POST",
          body: JSON.stringify(
            preview ? data : { operation_id: crypto.randomUUID(), data },
          ),
        },
      );
      setPivotResult(result);
    } catch (e) {
      setError(explain(e));
    }
  }
  async function cancelPivot() {
    if (!savedDashboard || !pivotResult?.job_id) return;
    try {
      setPivotResult(
        await request(
          `${base}dashboards/${savedDashboard}/pivot-jobs/${pivotResult.job_id}/actions/cancel`,
          {
            method: "POST",
            body: JSON.stringify({ operation_id: crypto.randomUUID() }),
          },
        ),
      );
    } catch (e) {
      setError(explain(e));
    }
  }
  async function more() {
    try {
      const next = await request(
        base +
          "programmes/" +
          programme +
          "/dashboard?limit=50&period_id=" +
          period +
          "&cursor=" +
          encodeURIComponent(view.next_cursor),
      );
      setView({
        ...next,
        indicators: [...view.indicators, ...next.indicators],
      });
    } catch (e) {
      setError(explain(e));
    }
  }
  if (!permitted)
    return (
      <section className="panel">
        <p className="muted">
          Dashboards need dashboard, programme and period read access in this
          workspace.
        </p>
      </section>
    );
  const portfolioAllowed = allowed("indicator-definitions.read");
  return (
    <section className="dashboards" aria-label="Dashboards">
      {portfolioAllowed ? (
        <div
          className="setup-tabs"
          role="tablist"
          aria-label="Dashboard view"
          onKeyDown={tabListKeys}
        >
          {(
            [
              "programme",
              "portfolio",
              ...(canAuthor ? ["authored"] : []),
            ] as const
          ).map((m) => (
            <button
              key={m}
              role="tab"
              type="button"
              aria-selected={mode === m}
              className={mode === m ? "primary" : "secondary"}
              onClick={() => setMode(m as typeof mode)}
            >
              {m === "programme"
                ? "Programme dashboard"
                : m === "portfolio"
                  ? "Portfolio"
                  : "Authored dashboards"}
            </button>
          ))}
        </div>
      ) : null}
      {mode === "portfolio" ? (
        <PortfolioPanel
          base={base}
          request={request}
          explain={explain}
          periods={periods}
          period={period}
          setPeriod={setPeriod}
        />
      ) : null}
      {mode === "authored" ? (
        <section className="panel" aria-label="Authored dashboard preview">
          <div className="planning-toolbar">
            <label>
              Private dashboard
              <select
                value={savedDashboard}
                onChange={(event) => setSavedDashboard(event.target.value)}
              >
                {!savedDashboards.length && <option value="">No drafts</option>}
                {savedDashboards.map((row) => (
                  <option key={row.object_id} value={row.object_id}>
                    {row.data.title}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Preview
              <select
                value={viewport}
                onChange={(event) =>
                  setViewport(event.target.value as typeof viewport)
                }
              >
                <option>DESKTOP</option>
                <option>MOBILE</option>
                <option>TABLE</option>
              </select>
            </label>
            <label>
              Drill level
              <select
                value={drillLevel}
                onChange={(event) => setDrillLevel(event.target.value)}
              >
                <option value="">No drill</option>
                <option>PORTFOLIO</option>
                <option>PARTNER</option>
                <option>PROGRAMME</option>
              </select>
            </label>
            <button type="button" onClick={createAuthoredDashboard}>
              New draft
            </button>
            <button type="button" className="secondary" onClick={addWidget}>
              Add result widget
            </button>
            <button type="button" className="secondary" onClick={addMapWidget}>
              Add district map
            </button>
            <button type="button" className="secondary" onClick={previewMap}>
              Preview safe map
            </button>
          </div>
          <fieldset aria-label="Dashboard alerts">
            <legend>Dashboard alerts</legend>
            <div className="planning-toolbar">
              <label>
                Existing rule
                <select
                  value={alertRule}
                  onChange={(event) => setAlertRule(event.target.value)}
                >
                  <option value="">Select rule</option>
                  {alertRules.map((row) => (
                    <option key={row.object_id} value={row.object_id}>
                      {words(row.data.evaluation_cadence)} · {row.data.operator}{" "}
                      {row.data.threshold}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Condition
                <select
                  value={alertOperator}
                  onChange={(event) =>
                    setAlertOperator(event.target.value as "LT" | "GT")
                  }
                >
                  <option value="LT">Below</option>
                  <option value="GT">Above</option>
                </select>
              </label>
              <label>
                Threshold
                <input
                  value={alertThreshold}
                  onChange={(event) => setAlertThreshold(event.target.value)}
                />
              </label>
              <label>
                Minimum coverage %
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={alertCoverage}
                  onChange={(event) =>
                    setAlertCoverage(Number(event.target.value))
                  }
                />
              </label>
              <label>
                Maximum freshness seconds
                <input
                  type="number"
                  min="60"
                  value={alertFreshness}
                  onChange={(event) =>
                    setAlertFreshness(Number(event.target.value))
                  }
                />
              </label>
              <label>
                Cadence
                <select
                  value={alertCadence}
                  onChange={(event) =>
                    setAlertCadence(event.target.value as typeof alertCadence)
                  }
                >
                  <option>DAILY</option>
                  <option>WEEKLY</option>
                  <option>MONTHLY</option>
                </select>
              </label>
              <label>
                Cooldown seconds
                <input
                  type="number"
                  min="60"
                  value={alertCooldown}
                  onChange={(event) =>
                    setAlertCooldown(Number(event.target.value))
                  }
                />
              </label>
              <button
                type="button"
                className="secondary"
                disabled={!indicator || !recipientId}
                onClick={createAlertRule}
              >
                Create alert rule
              </button>
              <label>
                Evaluation result
                <select
                  value={alertResult}
                  onChange={(event) => setAlertResult(event.target.value)}
                >
                  <option value="">Missed or absent result</option>
                  {calculatedResults.map((row) => (
                    <option key={row.object_id} value={row.object_id}>
                      {row.object_id}
                    </option>
                  ))}
                </select>
              </label>
              <button
                type="button"
                className="secondary"
                disabled={!alertRule || !period}
                onClick={evaluateAlert}
              >
                Evaluate due period
              </button>
            </div>
            {alertRules.find((row) => row.object_id === alertRule) ? (
              <p className="muted">
                Next due{" "}
                {when(
                  alertRules.find((row) => row.object_id === alertRule).data
                    .next_evaluation_at,
                )}
                . The selected period and exact result revision are retained
                with every incident.
              </p>
            ) : null}
          </fieldset>
          <fieldset aria-label="Sharing and publication">
            <legend>Sharing and publication</legend>
            <div className="planning-toolbar">
              {canCopy ? (
                <button
                  type="button"
                  className="secondary"
                  disabled={!savedDashboard}
                  onClick={copyDashboard}
                >
                  Copy privately
                </button>
              ) : null}
              <label>
                Recipient principal ID
                <input
                  value={recipientId}
                  onChange={(event) => setRecipientId(event.target.value)}
                  placeholder="UUID"
                />
              </label>
              <button
                type="button"
                className="secondary"
                disabled={!savedDashboard || !recipientId}
                onClick={previewSharing}
              >
                Preview recipient view
              </button>
              {canPublish ? (
                <>
                  <label>
                    Audience
                    <select
                      value={publicationAudience}
                      onChange={(event) =>
                        setPublicationAudience(
                          event.target.value as typeof publicationAudience,
                        )
                      }
                    >
                      <option>INTERNAL</option>
                      <option>PUBLIC</option>
                    </select>
                  </label>
                  <label>
                    Expires
                    <input
                      type="datetime-local"
                      value={publicationExpiry}
                      onChange={(event) =>
                        setPublicationExpiry(event.target.value)
                      }
                    />
                  </label>
                  <button
                    type="button"
                    disabled={!savedDashboard || !publicationExpiry}
                    onClick={publishDashboard}
                  >
                    Publish pinned dashboard
                  </button>
                </>
              ) : null}
              {publicationId ? (
                <button
                  type="button"
                  className="secondary"
                  onClick={refreshPublicationStatus}
                >
                  Refresh publication status
                </button>
              ) : null}
            </div>
            {publicationAudience === "PUBLIC" && canPublish ? (
              <p className="muted">
                Public publication is permitted only when every pinned binding
                is an approved public disclosure artifact.
              </p>
            ) : null}
            {publicationMessage ? (
              <p role="status" className="muted">
                {publicationMessage}
              </p>
            ) : null}
          </fieldset>
          {sharingPreview ? (
            <section aria-label="Recipient sharing preview">
              <p role="status" className="muted">
                Recipient preview:{" "}
                {sharingPreview.unavailable_binding_count === 0
                  ? "all bindings available"
                  : sharingPreview.unavailable_binding_count +
                    " bindings unavailable"}
                . No grants were created.
              </p>
              <table>
                <thead>
                  <tr>
                    <th>Widget</th>
                    <th>Source</th>
                    <th>Pinned revision</th>
                    <th>Classification</th>
                    <th>Availability</th>
                  </tr>
                </thead>
                <tbody>
                  {sharingPreview.widgets.map((widget: any) => (
                    <tr key={widget.widget_id}>
                      <td>{widget.widget_id}</td>
                      <td>
                        {words(widget.binding.resource_type)} ·{" "}
                        {widget.binding.object_id}
                      </td>
                      <td>{widget.binding.revision_id}</td>
                      <td>{words(widget.classification || "Unavailable")}</td>
                      <td>{words(widget.availability)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          ) : null}
          {publicationStatus ? (
            <section aria-label="Publication status" className="callout">
              <h3>Publication status</h3>
              <p>
                <strong>{words(publicationStatus.status)}</strong> ·{" "}
                {words(publicationStatus.audience)} · expires{" "}
                {when(publicationStatus.expires_at)}
              </p>
              <p className="muted">
                Publication {publicationStatus.publication_id} pins dashboard
                revision {publicationStatus.dashboard_revision}.
              </p>
              {publicationStatus.status === "SUSPENDED" ? (
                <p role="alert">
                  This publication is unavailable:{" "}
                  {words(publicationStatus.reason_code)}. Rebind or review the
                  sources, then publish a successor.
                </p>
              ) : null}
            </section>
          ) : null}
          {alertOutcome ? (
            <p role="status" className="muted">
              Alert outcome: {words(alertOutcome.outcome)} ·{" "}
              {words(alertOutcome.reason_code)}
              {alertOutcome.coalesced ? " · cooldown incident updated" : ""}
              {alertOutcome.incident_id
                ? ` · incident ${alertOutcome.incident_id}`
                : ""}
              {alertOutcome.result_revision
                ? ` · result revision ${alertOutcome.result_revision}`
                : ""}
              {alertOutcome.occurrence_count
                ? ` · occurrence ${alertOutcome.occurrence_count}`
                : ""}
            </p>
          ) : null}
          {alertIncidents.length ? (
            <section aria-label="Alert incident history">
              <h3>Alert incident history</h3>
              <table>
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Reason</th>
                    <th>Period</th>
                    <th>Result revision</th>
                    <th>Occurrences</th>
                    <th>Last evaluated</th>
                  </tr>
                </thead>
                <tbody>
                  {alertIncidents.map((row) => (
                    <tr key={row.object_id}>
                      <td>{words(row.data.alert_type)}</td>
                      <td>{words(row.data.reason_code)}</td>
                      <td>{row.data.evaluation_period_id}</td>
                      <td>{row.data.result_revision || "No result"}</td>
                      <td>{row.data.occurrence_count}</td>
                      <td>{when(row.data.last_evaluated_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          ) : null}
          <div className="planning-toolbar" aria-label="Pivot analysis">
            <label>
              Pivot dimension
              <input
                value={pivotDimension}
                onChange={(event) => setPivotDimension(event.target.value)}
              />
            </label>
            <label>
              Statistic
              <select
                value={pivotStatistic}
                onChange={(event) => setPivotStatistic(event.target.value)}
              >
                <option>DISTINCT_COUNT</option>
                <option>SUM</option>
                <option>MEAN</option>
              </select>
            </label>
            <button
              type="button"
              className="secondary"
              onClick={() => runPivot(true)}
            >
              Preview pivot
            </button>
            <button
              type="button"
              className="secondary"
              onClick={() => runPivot(false)}
            >
              Run pivot
            </button>
          </div>
          {pivotResult ? (
            <section className="dashboard-card" aria-label="Pivot result">
              <h3>Pivot result</h3>
              <p role="status">
                {words(pivotResult.execution)} · estimated{" "}
                {pivotResult.estimated_cardinality} cells
              </p>
              <p>{pivotResult.explanation}</p>
              {pivotResult.job_id ? (
                <p>
                  Queued cancellable job {pivotResult.job_id}{" "}
                  <button
                    type="button"
                    className="secondary"
                    onClick={cancelPivot}
                  >
                    Cancel queued pivot
                  </button>
                </p>
              ) : null}
              {!pivotResult.job_id ? (
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Category</th>
                        <th>Value</th>
                        <th>Disclosure</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pivotResult.cells.map((cell: any, index: number) => (
                        <tr key={`${cell.category}-${index}`}>
                          <td>{cell.category ?? "—"}</td>
                          <td>
                            {cell.displayed_value ??
                              cell.value ??
                              words(cell.value_state)}
                          </td>
                          <td>
                            {words(cell.disclosure)} · {words(cell.additivity)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr>
                        <th>Grand total</th>
                        <td>{pivotResult.grand_total ?? "—"}</td>
                        <td>{words(pivotResult.grand_total_basis)}</td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              ) : null}
            </section>
          ) : null}
          {geographicPreview ? (
            <section
              className="dashboard-card"
              aria-label="Geographic map and equivalent table"
            >
              <h3>{geographicPreview.legend}</h3>
              <p role="status">
                Boundary {words(geographicPreview.boundary_status)} ·{" "}
                {words(geographicPreview.granularity)} ·{" "}
                {words(geographicPreview.coordinate_delivery)}
              </p>
              <div
                className="geographic-map"
                role="img"
                aria-label={`${geographicPreview.legend}; ${geographicPreview.map_request.length} permitted geographic features`}
              >
                {geographicPreview.map_request.map(
                  (feature: any, index: number) => (
                    <span
                      key={`${feature.geography_key}-${index}`}
                      title={`${feature.tooltip.label}: ${feature.tooltip.displayed_value ?? words(feature.tooltip.value_state)}`}
                    >
                      {feature.geography_key ?? "Missing"}:{" "}
                      {feature.displayed_value ?? words(feature.value_state)}
                    </span>
                  ),
                )}
              </div>
              <div className="table-scroll">
                <table>
                  <caption>Sortable equivalent table</caption>
                  <thead>
                    <tr>
                      <th>Geography</th>
                      <th>Value</th>
                      <th>State</th>
                      <th>Disclosure</th>
                    </tr>
                  </thead>
                  <tbody>
                    {geographicPreview.equivalent_table.map(
                      (row: any, index: number) => (
                        <tr key={`${row.geography_key}-${index}`}>
                          <td>{row.geography_key ?? "—"}</td>
                          <td>{row.displayed_value ?? row.value ?? "—"}</td>
                          <td>{words(row.value_state)}</td>
                          <td>{words(row.disclosure)}</td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          ) : null}
          <div className="planning-toolbar">
            <label>
              Filter field
              <select
                value={filterField}
                onChange={(event) => setFilterField(event.target.value)}
              >
                <option value="programme">Programme</option>
                <option value="period">Period</option>
                <option value="indicator">Indicator</option>
                <option value="geography">Geography</option>
                <option value="dimension">Dimension</option>
                <option value="approval">Approval</option>
              </select>
            </label>
            <label>
              Current filter value
              <input
                value={filterValue}
                onChange={(event) => setFilterValue(event.target.value)}
              />
            </label>
            <button
              type="button"
              className="secondary"
              onClick={applyDashboardFilter}
            >
              Apply visible filter
            </button>
          </div>
          {authoredPreview?.current_filters?.terms?.length ? (
            <p role="status">
              Current filters:{" "}
              {authoredPreview.current_filters.terms
                .map(
                  (term: any) =>
                    `${words(term.field)} = ${term.values.join(", ")}`,
                )
                .join("; ")}
            </p>
          ) : (
            <p className="muted">No filters applied.</p>
          )}
          {authoredPreview?.widgets.map((widget: any) => (
            <article className="dashboard-card" key={widget.widget_id}>
              <h3>{widget.title}</h3>
              {widget.availability === "UNAVAILABLE" ? (
                <p role="status">
                  Unavailable — no saved private value is shown.
                </p>
              ) : (
                <div className="table-scroll">
                  <table aria-label={`${widget.title} tabular equivalent`}>
                    <thead>
                      <tr>
                        <th>Measure</th>
                        <th>Value</th>
                        <th>State</th>
                      </tr>
                    </thead>
                    <tbody>
                      {widget.table_rows.map((row: any) => (
                        <tr key={row.label}>
                          <td>{row.label}</td>
                          <td>{row.displayed_value ?? "—"}</td>
                          <td>{words(row.value_state)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              <p className="muted">
                Quality context is always visible · {words(widget.view_mode)}
              </p>
              {widget.non_applicable_filters.length ? (
                <p role="status">
                  Not affected by:{" "}
                  {widget.non_applicable_filters.map(words).join(", ")}
                </p>
              ) : null}
            </article>
          ))}
        </section>
      ) : null}
      <div
        className="planning-toolbar"
        style={mode !== "programme" ? { display: "none" } : undefined}
      >
        <label>
          Programme
          <select
            aria-label="Dashboard programme"
            value={programme}
            onChange={(e) => setProgramme(e.target.value)}
          >
            {!programmes.length && <option value="">No programmes</option>}
            {programmes.map((p) => (
              <option key={p.object_id} value={p.object_id}>
                {p.data.title || p.data.code || p.object_id.slice(0, 8)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Period
          <select
            aria-label="Dashboard period"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
          >
            {!periods.length && <option value="">No periods</option>}
            {periods.map((p) => (
              <option key={p.object_id} value={p.object_id}>
                {p.data.code || p.object_id.slice(0, 8)}
              </option>
            ))}
          </select>
        </label>
        <button className="secondary" onClick={() => setTick((t) => t + 1)}>
          Refresh
        </button>
      </div>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {loading && !view && mode === "programme" ? (
        <p className="muted">Loading dashboard…</p>
      ) : null}
      {view && mode === "programme" && (
        <>
          <p className="dashboard-context" role="status">
            {view.snapshot ? (
              <>
                Official values from locked snapshot version{" "}
                {view.snapshot.snapshot_version} · locked{" "}
                {when(view.snapshot.locked_at)} · period{" "}
                {view.period.period_state}
              </>
            ) : (
              <>
                No locked snapshot for this programme and period yet · period{" "}
                {view.period.period_state} · values shown are provisional
              </>
            )}
          </p>
          <details className="dashboard-rule">
            <summary>When is a value stale?</summary>
            <p>{view.stale_rule}</p>
          </details>
          <button
            type="button"
            className="secondary dashboard-print-control"
            onClick={() => window.print()}
          >
            Print or save dashboard with context
          </button>
          {!view.indicators.length ? (
            <p className="muted">No indicators in this programme yet.</p>
          ) : (
            <div className="dashboard-grid">
              <h2 className="sr-only">Indicators</h2>
              {view.indicators.map((c: any) => (
                <article
                  key={c.indicator_id}
                  className="dashboard-card"
                  aria-label={c.indicator_label}
                >
                  <h3>{c.indicator_label}</h3>
                  <dl>
                    <dt>
                      <span className="badge official">OFFICIAL</span>
                    </dt>
                    <dd>
                      <Shown value={c.official} unit={c.unit} />
                    </dd>
                    <dt>
                      <span className="badge provisional">PROVISIONAL</span>
                    </dt>
                    <dd>
                      <Shown value={c.provisional} unit={c.unit} />
                    </dd>
                    <dt>Target</dt>
                    <dd>
                      {targetText(c.target)}
                      {c.target ? (
                        <small className="muted">
                          {" "}
                          · {words(c.target.direction)} ·{" "}
                          {targetContext(c.target)}
                        </small>
                      ) : null}
                    </dd>
                    <dt>Baseline</dt>
                    <dd>
                      {c.baseline ? targetText(c.baseline) : "None"}
                      {c.baseline ? (
                        <small className="muted">
                          {" "}
                          · {targetContext(c.baseline)}
                        </small>
                      ) : null}
                    </dd>
                    {c.status ? (
                      <>
                        <dt>Status</dt>
                        <dd>
                          {words(c.status.status)}
                          {c.status.attainment_percent
                            ? " · " + c.status.attainment_percent + "%"
                            : ""}
                          {c.status.compared_with ? (
                            <small className="muted">
                              {" "}
                              · against {words(c.status.compared_with)}
                            </small>
                          ) : null}
                          <small className="muted">
                            <br />
                            Deviation{" "}
                            {c.status.displayed_deviation ?? "undefined"} ·
                            formula: {c.status.deviation_formula}
                            <br />
                            Attainment formula: {c.status.attainment_formula} ·
                            scale is uncapped
                            <br />
                            Baseline change{" "}
                            {c.status.change_from_baseline_percent === null
                              ? "not available"
                              : c.status.change_from_baseline_percent ===
                                  "Undefined"
                                ? "undefined"
                                : c.status.change_from_baseline_percent +
                                  "%"}{" "}
                            · {c.status.baseline_change_formula}
                            <br />
                            Time semantic: {words(c.status.time_semantic)} (
                            {words(c.status.time_semantic_compatibility)})
                          </small>
                        </dd>
                      </>
                    ) : null}
                    <dt>Coverage</dt>
                    <dd>
                      <Coverage c={c.coverage} />
                    </dd>
                    <dt>Freshness</dt>
                    <dd>
                      <Freshness f={c.freshness} />
                    </dd>
                  </dl>
                  <button
                    className="secondary"
                    aria-expanded={sourcesFor === c.indicator_id}
                    onClick={() =>
                      setSourcesFor((s) =>
                        s === c.indicator_id ? "" : c.indicator_id,
                      )
                    }
                  >
                    {sourcesFor === c.indicator_id
                      ? "Hide sources"
                      : "Show sources"}
                  </button>
                </article>
              ))}
            </div>
          )}
          {view.next_cursor && (
            <button className="secondary" onClick={more}>
              Load more indicators
            </button>
          )}
          {sourcesFor && sources ? (
            <section
              className="panel dashboard-sources"
              aria-label="Source observations"
            >
              <h2>Sources behind {sources.indicator_label}</h2>
              <p className="muted" role="status">
                {sources.value.mode
                  ? "Dispositions refer to the " +
                    sources.value.mode.toLowerCase() +
                    " value shown on the card"
                  : "No calculated value yet: rows carry no disposition"}
                {" · "}
                {sources.source_check === "COMPLETE"
                  ? "every source row of the period is listed"
                  : "some rows are withheld by your access (the set is partial)"}
              </p>
              <div className="table-scroll">
                <table aria-label="Source observations">
                  <thead>
                    <tr>
                      <th>Source</th>
                      <th>Event time</th>
                      <th>Value</th>
                      <th>Value state</th>
                      <th>Approval</th>
                      <th>In shown value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {!sources.items.length ? (
                      <tr>
                        <td colSpan={6} className="muted">
                          No source observations you can read in this period.
                        </td>
                      </tr>
                    ) : null}
                    {sources.items.map((o: any) => (
                      <tr key={o.observation_id}>
                        <td>
                          {o.source_namespace}/{o.source_key}
                        </td>
                        <td>{when(o.event_at)}</td>
                        <td>
                          {o.displayed_value ?? "—"}
                          {o.numerator !== null && o.denominator !== null ? (
                            <small className="muted">
                              {" "}
                              ({o.numerator}/{o.denominator})
                            </small>
                          ) : null}
                        </td>
                        <td>{words(o.value_state)}</td>
                        <td>
                          {words(o.approval_state) || "—"}
                          <small className="muted">
                            {" "}
                            · {o.lifecycle_state}
                          </small>
                        </td>
                        <td>
                          {o.contribution ? words(o.contribution) : "—"}
                          {o.contribution_reason ? (
                            <small className="muted">
                              {" "}
                              · {words(o.contribution_reason)}
                            </small>
                          ) : null}
                          {o.changed_since_calculation ? (
                            <small className="muted"> · changed since</small>
                          ) : null}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {sources.next_cursor ? (
                <p className="muted">Only the first 100 rows are shown here.</p>
              ) : null}
            </section>
          ) : null}
          {view.indicators.length ? (
            <section className="panel dashboard-series">
              <label>
                Indicator trend
                <select
                  aria-label="Trend indicator"
                  value={indicator}
                  onChange={(e) => setIndicator(e.target.value)}
                >
                  {view.indicators.map((c: any) => (
                    <option key={c.indicator_id} value={c.indicator_id}>
                      {c.indicator_label}
                    </option>
                  ))}
                </select>
              </label>
              {series && (
                <>
                  <SeriesChart series={series} />
                  <div className="table-scroll">
                    <table aria-label="Indicator series">
                      <thead>
                        <tr>
                          <th>Period</th>
                          <th>Official</th>
                          <th>Provisional</th>
                          <th>Target</th>
                          <th>Breakdown (official)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {series.points.map((p: any) => (
                          <tr key={p.period_id}>
                            <td>
                              {p.period_code || p.period_id.slice(0, 8)}
                              <small className="muted">
                                {" "}
                                · {p.period_state}
                              </small>
                            </td>
                            <td>
                              <Shown value={p.official} />
                            </td>
                            <td>
                              <Shown value={p.provisional} />
                            </td>
                            <td>{targetText(p.target)}</td>
                            <td>
                              {p.official?.disaggregation?.length
                                ? p.official.disaggregation
                                    .map(
                                      (d: any) =>
                                        d.category +
                                        ": " +
                                        (d.displayed_value ??
                                          words(d.value_state)),
                                    )
                                    .join(", ")
                                : "—"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </section>
          ) : null}
        </>
      )}
    </section>
  );
}
