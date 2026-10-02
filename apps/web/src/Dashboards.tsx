import React, { useEffect, useState } from "react";

type Props = {
  base: string;
  capabilities: string[];
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
};
type Row = { object_id: string; data: Record<string, any> };
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
        {f.locked_at ? "Locked " + when(f.locked_at) + " · " : ""}
        {f.provisional_calculated_at
          ? "Calculated " + when(f.provisional_calculated_at) + " · "
          : ""}
        Last source change {when(f.last_source_change_at)}
        {f.source_check === "NOT_PERMITTED"
          ? " · some sources are outside your access"
          : ""}
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
    [error, setError] = useState(""),
    [loading, setLoading] = useState(false),
    [tick, setTick] = useState(0);
  const permitted =
    allowed("dashboards.read") &&
    allowed("programmes.read") &&
    allowed("periods.read");
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
  return (
    <section className="dashboards" aria-label="Dashboards">
      <div className="planning-toolbar">
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
      {loading && !view ? <p className="muted">Loading dashboard…</p> : null}
      {view && (
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
                          {words(c.target.target_basis)}
                        </small>
                      ) : null}
                    </dd>
                    <dt>Baseline</dt>
                    <dd>{c.baseline ? targetText(c.baseline) : "None"}</dd>
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
                </article>
              ))}
            </div>
          )}
          {view.next_cursor && (
            <button className="secondary" onClick={more}>
              Load more indicators
            </button>
          )}
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
