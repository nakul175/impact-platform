import React, { FormEvent, useState } from "react";
type Props = {
  base: string;
  capabilities: string[];
  request: (path: string, options?: RequestInit) => Promise<unknown>;
  explain: (e: unknown) => string;
};
type Row = {
  object_id: string;
  revision_id: string;
  data: {
    evaluation_id: string;
    methodology_revision: string;
    review_state: string;
    sampling_frame: string;
    strata: unknown[];
    amendment?: unknown;
  };
};
type Page = { items: Row[] };
const lines = (s: string) =>
  s
    .split("\n")
    .map((x) => x.trim())
    .filter(Boolean);
export function EvaluationMethodologies({
  base,
  capabilities,
  request,
  explain,
}: Props) {
  const [evaluationId, setEvaluationId] = useState(""),
    [rows, setRows] = useState<Row[]>([]),
    [error, setError] = useState("");
  const [frame, setFrame] = useState(""),
    [eligibility, setEligibility] = useState(""),
    [assignment, setAssignment] = useState(""),
    [nonresponse, setNonresponse] = useState(""),
    [analysis, setAnalysis] = useState(""),
    [strata, setStrata] = useState(""),
    [expansion, setExpansion] = useState("HORVITZ_THOMPSON");
  const [amendments, setAmendments] = useState<Record<string, string>>({});
  async function load() {
    const p = (await request(
      `${base}/evaluation-methodologies?evaluation_id=${encodeURIComponent(evaluationId)}&limit=100`,
    )) as Page;
    setRows(p.items);
  }
  function parsedStrata() {
    return lines(strata).map((line) => {
      const [code, eligible, sampled, nonresponseCount, weight] = line
        .split(",")
        .map((x) => x.trim());
      return {
        code,
        eligible_count: Number(eligible),
        sampled_count: Number(sampled),
        nonresponse_count: Number(nonresponseCount),
        weight: weight || null,
      };
    });
  }
  async function create(e: FormEvent) {
    e.preventDefault();
    try {
      await request(`${base}/evaluation-methodologies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          data: {
            evaluation_id: evaluationId,
            sampling_frame: frame,
            eligibility_rules: eligibility,
            assignment_method: assignment,
            strata: parsedStrata(),
            nonresponse_rules: nonresponse,
            analysis_plan: analysis,
            expansion_method: expansion || null,
          },
        }),
      });
      await load();
    } catch (c) {
      setError(explain(c));
    }
  }
  async function review(row: Row, decision: "APPROVE" | "REJECT") {
    try {
      await request(
        `${base}/evaluation-methodologies/${row.object_id}/actions/review`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            expected_revision: row.revision_id,
            data: { decision, reason: "Recorded methodology review" },
          }),
        },
      );
      await load();
    } catch (c) {
      setError(explain(c));
    }
  }
  async function amend(row: Row) {
    try {
      await request(
        `${base}/evaluation-methodologies/${row.object_id}/actions/amend`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            expected_revision: row.revision_id,
            data: {
              reason: "Methodology amendment after inspection",
              relative_to_data_inspection: "AFTER_INSPECTION",
              changes: { analysis_plan: amendments[row.object_id] },
            },
          }),
        },
      );
      await load();
    } catch (c) {
      setError(explain(c));
    }
  }
  async function exportSample(row: Row) {
    try {
      const result = await request(
        `${base}/evaluation-methodologies/${row.object_id}/sample-export`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ weighted: true, population_estimate: true }),
        },
      );
      setError(JSON.stringify(result));
    } catch (c) {
      setError(explain(c));
    }
  }
  return (
    <section className="panel">
      <h2>Sampling methodologies</h2>
      <p className="muted">
        Weights are explicit. Missing weights never become one, and every new or
        amended method requires independent review.
      </p>
      {error ? <p role="status">{error}</p> : null}
      <label>
        Evaluation ID
        <input
          value={evaluationId}
          onChange={(e) => setEvaluationId(e.target.value)}
        />
      </label>
      <button onClick={() => void load()}>Load methodologies</button>
      {capabilities.includes("evaluations.draft.edit") ? (
        <form className="stack" onSubmit={create}>
          <label>
            Sampling frame
            <textarea
              required
              value={frame}
              onChange={(e) => setFrame(e.target.value)}
            />
          </label>
          <label>
            Eligibility rules
            <textarea
              required
              value={eligibility}
              onChange={(e) => setEligibility(e.target.value)}
            />
          </label>
          <label>
            Assignment method
            <textarea
              required
              value={assignment}
              onChange={(e) => setAssignment(e.target.value)}
            />
          </label>
          <label>
            Strata: code, eligible, sampled, nonresponse, weight
            <textarea
              required
              value={strata}
              onChange={(e) => setStrata(e.target.value)}
            />
          </label>
          <label>
            Nonresponse rules
            <textarea
              required
              value={nonresponse}
              onChange={(e) => setNonresponse(e.target.value)}
            />
          </label>
          <label>
            Analysis plan
            <textarea
              required
              value={analysis}
              onChange={(e) => setAnalysis(e.target.value)}
            />
          </label>
          <label>
            Expansion method
            <select
              value={expansion}
              onChange={(e) => setExpansion(e.target.value)}
            >
              <option>HORVITZ_THOMPSON</option>
              <option>POST_STRATIFIED_WEIGHTED_SUM</option>
              <option value="">No population expansion</option>
            </select>
          </label>
          <button>Create methodology for review</button>
        </form>
      ) : null}
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Revision</th>
              <th>State</th>
              <th>Frame</th>
              <th>Updated analysis plan</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.object_id}>
                <td>{row.data.methodology_revision}</td>
                <td>{row.data.review_state}</td>
                <td>{row.data.sampling_frame}</td>
                <td>
                  <input
                    value={amendments[row.object_id] || ""}
                    onChange={(e) =>
                      setAmendments((old) => ({
                        ...old,
                        [row.object_id]: e.target.value,
                      }))
                    }
                  />
                </td>
                <td>
                  {row.data.review_state === "REVIEWED" ? (
                    <button onClick={() => void amend(row)}>
                      Amend after inspection
                    </button>
                  ) : null}
                  {row.data.review_state === "PENDING" ? (
                    <>
                      <button onClick={() => void review(row, "APPROVE")}>
                        Approve
                      </button>
                      <button onClick={() => void review(row, "REJECT")}>
                        Reject
                      </button>
                    </>
                  ) : null}
                  {row.data.review_state === "REVIEWED" ? (
                    <button onClick={() => void exportSample(row)}>
                      Export weighted sample
                    </button>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
