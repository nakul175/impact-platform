import React, { useEffect, useState } from "react";

// Portfolio view (v0.27): one indicator definition across every programme of the workspace for a
// chosen period. Official values come from each programme's own locked snapshot; a pooled total
// appears per definition version only where the method pools (SUM, COUNT, POOLED_RATIO), from the
// stored numerators and denominators, and only over a complete, fully official set.

type Props = {
  base: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
  periods: { object_id: string; data: Record<string, any> }[];
  period: string;
  setPeriod: (id: string) => void;
};
type Row = { object_id: string; data: Record<string, any> };

const words = (s: string | null | undefined) =>
  (s || "").replaceAll("_", " ").toLowerCase();
const when = (s: string | null | undefined) =>
  s ? s.replace("T", " ").slice(0, 16) + " UTC" : "—";

async function definitions(request: Props["request"], base: string) {
  let items: Row[] = [],
    cursor: string | null = null;
  do {
    const page: any = await request(
      base +
        "indicator-definitions?limit=100" +
        (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""),
    );
    items = [...items, ...page.items];
    cursor = page.next_cursor;
  } while (cursor && items.length < 500);
  return items;
}

function Pooled({ p, unit }: { p: any; unit: string | null }) {
  if (p.value_state === "PRESENT" && p.displayed_value !== null)
    return (
      <span>
        <strong className="dashboard-number">{p.displayed_value}</strong>
        {unit ? <small className="muted"> {unit}</small> : null}
        {p.numerator !== null && p.denominator !== null ? (
          <small className="muted">
            {" "}
            ({p.numerator}/{p.denominator})
          </small>
        ) : null}
        <small className="muted">
          {" "}
          · {words(p.method)} over {p.contributing_count} of {p.instance_count}
        </small>
      </span>
    );
  return (
    <span>
      <strong>No pooled total</strong>
      <small className="muted">
        {" "}
        · {words(p.reason_code) || words(p.value_state)} ·{" "}
        {p.contributing_count} of {p.instance_count} instances official
      </small>
    </span>
  );
}

export function PortfolioPanel({
  base,
  request,
  explain,
  periods,
  period,
  setPeriod,
}: Props) {
  const [items, setItems] = useState<Row[]>([]),
    [definition, setDefinition] = useState(""),
    [view, setView] = useState<any>(null),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(false);
  useEffect(() => {
    definitions(request, base)
      .then((d) => {
        setItems(d);
        setDefinition((c) => c || d[0]?.object_id || "");
      })
      .catch((e) => setError(explain(e)));
  }, [base]);
  useEffect(() => {
    if (!definition || !period) return;
    let live = true;
    setLoading(true);
    setError("");
    request(
      base +
        "indicator-definitions/" +
        definition +
        "/portfolio?limit=100&period_id=" +
        period,
    )
      .then((v) => live && setView(v))
      .catch((e) => live && setError(explain(e)))
      .finally(() => live && setLoading(false));
    return () => {
      live = false;
    };
  }, [definition, period, base]);
  return (
    <section className="portfolio" aria-label="Portfolio">
      <div className="planning-toolbar">
        <label>
          Indicator definition
          <select
            aria-label="Portfolio definition"
            value={definition}
            onChange={(e) => setDefinition(e.target.value)}
          >
            {!items.length && <option value="">No definitions</option>}
            {items.map((d) => (
              <option key={d.object_id} value={d.object_id}>
                {d.data.name || d.data.code || d.object_id.slice(0, 8)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Period
          <select
            aria-label="Portfolio period"
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
      </div>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {loading && !view ? <p className="muted">Loading portfolio…</p> : null}
      {view && (
        <>
          <p className="dashboard-context" role="status">
            {view.definition_name || "Definition"} ·{" "}
            {words(view.combination_rule)} ·{" "}
            {view.scope === "COMPLETE"
              ? "every instance in the workspace is listed"
              : "some instances are withheld by your access: totals are not shown"}
          </p>
          <h2 className="sr-only">Pooled totals</h2>
          <dl className="portfolio-totals">
            {view.versions.map((v: any) => (
              <React.Fragment key={v.definition_revision || "none"}>
                <dt>
                  Definition version{" "}
                  {v.version_number ??
                    (v.definition_revision || "").slice(0, 8)}
                </dt>
                <dd>
                  <Pooled p={v.pooled} unit={view.unit} />
                </dd>
              </React.Fragment>
            ))}
            {!view.versions.length ? (
              <>
                <dt>Instances</dt>
                <dd className="muted">None you can read.</dd>
              </>
            ) : null}
          </dl>
          <div className="table-scroll">
            <table aria-label="Portfolio programmes">
              <thead>
                <tr>
                  <th>Programme</th>
                  <th>Indicator</th>
                  <th>Period</th>
                  <th>Official</th>
                  <th>Coverage</th>
                  <th>Snapshot</th>
                </tr>
              </thead>
              <tbody>
                {!view.programmes.length ? (
                  <tr>
                    <td colSpan={6} className="muted">
                      No programme instance of this definition you can read.
                    </td>
                  </tr>
                ) : null}
                {view.programmes.map((p: any) => (
                  <tr key={p.indicator_id}>
                    <td>{p.programme_title || p.programme_id.slice(0, 8)}</td>
                    <td>{p.indicator_label}</td>
                    <td>{p.period_state}</td>
                    <td>
                      {p.official ? (
                        p.official.value_state === "PRESENT" &&
                        p.official.displayed_value !== null ? (
                          <span>
                            <strong className="dashboard-number">
                              {p.official.displayed_value}
                            </strong>
                            {p.unit ? (
                              <small className="muted"> {p.unit}</small>
                            ) : null}
                            {p.official.numerator !== null &&
                            p.official.denominator !== null ? (
                              <small className="muted">
                                {" "}
                                ({p.official.numerator}/{p.official.denominator}
                                )
                              </small>
                            ) : null}
                          </span>
                        ) : (
                          <span>
                            <strong>{words(p.official.value_state)}</strong>
                            {p.official.reason_code ? (
                              <small className="muted">
                                {" "}
                                · {words(p.official.reason_code)}
                              </small>
                            ) : null}
                          </span>
                        )
                      ) : (
                        <span className="muted">No official value</span>
                      )}
                    </td>
                    <td>
                      {p.coverage.applicability === "APPLICABLE"
                        ? p.coverage.approved_count +
                          "/" +
                          p.coverage.required_count +
                          " approved · " +
                          p.coverage.approval_percent +
                          "%"
                        : words(p.coverage.applicability) +
                          (p.coverage.reason_code
                            ? " · " + words(p.coverage.reason_code)
                            : "")}
                    </td>
                    <td>
                      {p.snapshot_version
                        ? "v" + p.snapshot_version + " · " + when(p.locked_at)
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {view.next_cursor ? (
            <p className="muted">
              Only the first 100 programme instances are shown.
            </p>
          ) : null}
        </>
      )}
    </section>
  );
}
