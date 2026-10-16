import React, { useEffect, useRef, useState } from "react";

type Props = {
  base: string;
  capabilities: string[];
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
};

export function AnomalyAssistance({
  base,
  capabilities,
  request,
  explain,
}: Props) {
  const allowed = (capability: string) => capabilities.includes(capability);
  const [findings, setFindings] = useState<any[]>([]);
  const [observationIds, setObservationIds] = useState("");
  const [owner, setOwner] = useState("");
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [tick, setTick] = useState(0);
  const operation = useRef(crypto.randomUUID());

  useEffect(() => {
    if (!allowed("dashboards.read")) return;
    request(base + "anomaly-findings?limit=100")
      .then((result) => setFindings(result.items || []))
      .catch((e) => setError(explain(e)));
  }, [base, tick]);

  async function run() {
    const eligible_observations = observationIds
      .split(/\s+/)
      .filter(Boolean)
      .map((pair) => {
        const [object_id, revision_id] = pair.split(":");
        return { object_id, revision_id };
      });
    try {
      await request(base + "anomaly-runs", {
        method: "POST",
        body: JSON.stringify({
          operation_id: operation.current,
          data: {
            method_version: "ROBUST_MAD_1",
            eligible_observations,
            comparison_window: {
              starts_at: new Date(startsAt).toISOString(),
              ends_at: new Date(endsAt).toISOString(),
            },
            owner_id: owner,
          },
        }),
      });
      operation.current = crypto.randomUUID();
      setMessage("Anomaly run recorded. Source observations were not changed.");
      setError("");
      setTick((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    }
  }

  async function review(finding: any, decision: string, reason_code?: string) {
    try {
      await request(
        base + "anomaly-findings/" + finding.object_id + "/actions/review",
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            data: { decision, reason_code: reason_code || null },
          }),
        },
      );
      setMessage(
        "Review saved separately from the observation. No data value or person label was changed.",
      );
      setError("");
      setTick((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    }
  }

  return (
    <section className="panel setup-panel">
      <h2>Anomaly review assistance</h2>
      <p className="muted">
        Compare exact observation revisions and create review suggestions. A
        suggestion never changes source data, never labels a person as
        fraudulent, and stays distinct from a confirmed quality defect.
      </p>
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
      {allowed("dashboards.draft.create") && (
        <fieldset>
          <legend>Run a versioned comparison</legend>
          <label>
            Observation and revision pairs
            <textarea
              aria-label="Observation and revision pairs"
              placeholder="observation-id:revision-id (one or more, separated by spaces)"
              value={observationIds}
              onChange={(e) => setObservationIds(e.target.value)}
            />
          </label>
          <label>
            Finding owner ID
            <input value={owner} onChange={(e) => setOwner(e.target.value)} />
          </label>
          <label>
            Window starts
            <input
              type="datetime-local"
              value={startsAt}
              onChange={(e) => setStartsAt(e.target.value)}
            />
          </label>
          <label>
            Window ends
            <input
              type="datetime-local"
              value={endsAt}
              onChange={(e) => setEndsAt(e.target.value)}
            />
          </label>
          <button
            className="primary"
            disabled={!observationIds || !owner || !startsAt || !endsAt}
            onClick={run}
          >
            Run suggestion-only check
          </button>
        </fieldset>
      )}
      {!findings.length ? (
        <p className="muted">No readable anomaly findings.</p>
      ) : (
        <div className="table-scroll">
          <table aria-label="Anomaly findings">
            <thead>
              <tr>
                <th>Finding</th>
                <th>State</th>
                <th>Explanation</th>
                <th>Review</th>
              </tr>
            </thead>
            <tbody>
              {findings.map((finding) => (
                <tr key={finding.object_id}>
                  <td>{finding.object_id.slice(0, 8)}</td>
                  <td>{finding.data.state}</td>
                  <td>{finding.data.explanation}</td>
                  <td>
                    {allowed("dashboards.draft.edit") &&
                    ["SUGGESTED", "DEFERRED"].includes(finding.data.state) ? (
                      <>
                        <button
                          className="secondary"
                          onClick={() => review(finding, "CONFIRMED")}
                        >
                          Confirm issue
                        </button>{" "}
                        <button
                          className="secondary"
                          onClick={() =>
                            review(finding, "DISMISSED", "EXPECTED_SEASONALITY")
                          }
                        >
                          Dismiss: expected seasonality
                        </button>{" "}
                        <button
                          className="secondary"
                          onClick={() => review(finding, "DEFERRED")}
                        >
                          Defer
                        </button>
                      </>
                    ) : (
                      finding.data.review?.reason_code || "Reviewed"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
