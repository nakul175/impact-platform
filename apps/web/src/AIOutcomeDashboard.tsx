import React, { useRef, useState } from "react";

type Measure = {
  value: string;
  unit: string;
  basis: string;
  observed_from: string;
  observed_to: string;
};
type Metric = "usage" | "time" | "cost" | "quality" | "reach";
type Comparison = {
  metric: Metric;
  baseline: Measure | null;
  current: Measure | null;
  status:
    | "COMPARABLE"
    | "INCOMPATIBLE"
    | "NOT_RECORDED"
    | "BASELINE_NOT_RECORDED";
  delta: string | null;
};
type Dashboard = {
  plan_id: string;
  plan_revision: string;
  deployment_attestation_id: string;
  baseline_object_id: string;
  baseline_revision: string;
  opportunity_id: string;
  reporting_basis: "SELF_REPORTED";
  comparisons: Comparison[];
  disclaimer: string;
};
type Props = {
  base: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
  capabilities: string[];
};
const metrics: Metric[] = ["usage", "time", "cost", "quality", "reach"];
const blank = (): Measure => ({
  value: "",
  unit: "",
  basis: "",
  observed_from: "",
  observed_to: "",
});

function renderMeasure(value: Measure | null, fallback: string) {
  return value
    ? `${value.value} ${value.unit}; ${value.basis}; ${value.observed_from} to ${value.observed_to}`
    : fallback;
}

export function AIOutcomeDashboardPanel(props: Props) {
  const [planId, setPlanId] = useState("");
  const [baselineId, setBaselineId] = useState("");
  const [opportunityId, setOpportunityId] = useState("");
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [values, setValues] = useState<Record<Metric, Measure>>({
    usage: blank(),
    time: blank(),
    cost: blank(),
    quality: blank(),
    reach: blank(),
  });
  const [notes, setNotes] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const pendingBody = useRef<string | null>(null);
  const loadEpoch = useRef(0);
  const canRead =
    props.capabilities.includes("ai.enablement.read") &&
    props.capabilities.includes("ai.problem-baseline.read");
  const canManage =
    props.capabilities.includes("ai.enablement.manage") && canRead;

  async function load() {
    const epoch = ++loadEpoch.current;
    setBusy(true);
    setMessage("");
    try {
      const query = new URLSearchParams({
        plan_id: planId,
        baseline_object_id: baselineId,
        opportunity_id: opportunityId,
      });
      const result = (await props.request(
        `${props.base}ai-enablement/outcomes-dashboard?${query}`,
      )) as Dashboard;
      if (epoch === loadEpoch.current) setDashboard(result);
    } catch (error) {
      setMessage(props.explain(error));
    } finally {
      setBusy(false);
    }
  }

  async function save() {
    if (!dashboard) return;
    setBusy(true);
    setMessage("");
    try {
      if (!pendingBody.current) {
        pendingBody.current = JSON.stringify({
          operation_id: crypto.randomUUID(),
          plan_id: dashboard.plan_id,
          plan_revision: dashboard.plan_revision,
          deployment_attestation_id: dashboard.deployment_attestation_id,
          baseline_object_id: dashboard.baseline_object_id,
          baseline_revision: dashboard.baseline_revision,
          opportunity_id: dashboard.opportunity_id,
          metrics: values,
          notes,
        });
      }
      await props.request(`${props.base}ai-enablement/outcome-observations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: pendingBody.current,
      });
      pendingBody.current = null;
      setMessage("Self-reported observation recorded.");
      await load();
    } catch (error) {
      setMessage(props.explain(error));
    } finally {
      setBusy(false);
    }
  }

  if (!canRead) return null;
  return (
    <section className="panel" aria-labelledby="ai-outcome-heading">
      <h2 id="ai-outcome-heading">Usage and outcomes</h2>
      <p>
        Compare self-reported current observations only with an exact locked
        problem baseline.
      </p>
      <div className="form-grid">
        <label>
          Completed adoption plan ID
          <input
            value={planId}
            onChange={(e) => {
              setPlanId(e.target.value);
              loadEpoch.current += 1;
              setDashboard(null);
              pendingBody.current = null;
            }}
          />
        </label>
        <label>
          Locked baseline ID
          <input
            value={baselineId}
            onChange={(e) => {
              setBaselineId(e.target.value);
              loadEpoch.current += 1;
              setDashboard(null);
              pendingBody.current = null;
            }}
          />
        </label>
        <label>
          Mapped opportunity ID
          <input
            value={opportunityId}
            onChange={(e) => {
              setOpportunityId(e.target.value);
              loadEpoch.current += 1;
              setDashboard(null);
              pendingBody.current = null;
            }}
          />
        </label>
      </div>
      <button
        type="button"
        disabled={busy || !planId || !baselineId || !opportunityId}
        onClick={() => void load()}
      >
        {busy ? "Loading…" : "Open comparison"}
      </button>
      {message && (
        <p role="status" aria-live="polite">
          {message}
        </p>
      )}
      {dashboard && (
        <>
          <p>
            <strong>Locked baseline:</strong> {dashboard.baseline_object_id} /{" "}
            {dashboard.baseline_revision}
          </p>
          <div className="table-wrap">
            <table>
              <caption>
                Current observations against the locked baseline
              </caption>
              <thead>
                <tr>
                  <th scope="col">Metric</th>
                  <th scope="col">Locked baseline</th>
                  <th scope="col">Current observation</th>
                  <th scope="col">Comparison</th>
                </tr>
              </thead>
              <tbody>
                {dashboard.comparisons.map((row) => (
                  <tr key={row.metric}>
                    <th scope="row">{row.metric}</th>
                    <td>
                      {renderMeasure(
                        row.baseline,
                        row.metric === "usage"
                          ? "Not recorded in locked baseline"
                          : "Not recorded",
                      )}
                    </td>
                    <td>
                      {renderMeasure(
                        row.current,
                        "No current observation recorded",
                      )}
                    </td>
                    <td>
                      {row.status === "COMPARABLE"
                        ? `Comparable; signed difference ${row.delta}`
                        : row.status.replaceAll("_", " ").toLowerCase()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p>{dashboard.disclaimer}</p>
          {canManage && (
            <>
              <h3>Record current self-reported observations</h3>
              {metrics.map((name) => (
                <fieldset key={name}>
                  <legend>{name}</legend>
                  <label>
                    Value
                    <input
                      inputMode="decimal"
                      value={values[name].value}
                      onChange={(e) =>
                        setValues({
                          ...values,
                          [name]: { ...values[name], value: e.target.value },
                        })
                      }
                    />
                  </label>
                  <label>
                    Unit
                    <input
                      value={values[name].unit}
                      onChange={(e) =>
                        setValues({
                          ...values,
                          [name]: { ...values[name], unit: e.target.value },
                        })
                      }
                    />
                  </label>
                  <label>
                    Basis or denominator
                    <input
                      value={values[name].basis}
                      onChange={(e) =>
                        setValues({
                          ...values,
                          [name]: { ...values[name], basis: e.target.value },
                        })
                      }
                    />
                  </label>
                  <label>
                    Observed from
                    <input
                      type="date"
                      value={values[name].observed_from}
                      onChange={(e) =>
                        setValues({
                          ...values,
                          [name]: {
                            ...values[name],
                            observed_from: e.target.value,
                          },
                        })
                      }
                    />
                  </label>
                  <label>
                    Observed to
                    <input
                      type="date"
                      value={values[name].observed_to}
                      onChange={(e) =>
                        setValues({
                          ...values,
                          [name]: {
                            ...values[name],
                            observed_to: e.target.value,
                          },
                        })
                      }
                    />
                  </label>
                </fieldset>
              ))}
              <label>
                Observation notes
                <textarea
                  maxLength={4000}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </label>
              <button type="button" disabled={busy} onClick={() => void save()}>
                {busy ? "Recording…" : "Record observation"}
              </button>
            </>
          )}
        </>
      )}
    </section>
  );
}
