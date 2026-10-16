import React, { FormEvent, useEffect, useState } from "react";

type Props = {
  base: string;
  capabilities: string[];
  request: (path: string, options?: RequestInit) => Promise<unknown>;
  explain: (error: unknown) => string;
};
type Evaluation = {
  object_id: string;
  revision_id: string;
  data: {
    title: string;
    study_type: string;
    stage: string;
    sensitive_processing: boolean;
    sensitive_processing_approved: false;
    independence: { verification: string };
  };
};
type Page<T> = { items: T[]; next_cursor: string | null };
const split = (value: string) =>
  value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);

export function EvaluationRegistry({
  base,
  capabilities,
  request,
  explain,
}: Props) {
  const [items, setItems] = useState<Evaluation[]>([]),
    [error, setError] = useState(""),
    [history, setHistory] = useState<Record<string, unknown[]>>({});
  const [programmeId, setProgrammeId] = useState(""),
    [periodId, setPeriodId] = useState(""),
    [title, setTitle] = useState("");
  const [studyType, setStudyType] = useState("BASELINE"),
    [questions, setQuestions] = useState(""),
    [design, setDesign] = useState(""),
    [evaluator, setEvaluator] = useState("");
  const [budget, setBudget] = useState(""),
    [currency, setCurrency] = useState("USD"),
    [deliverables, setDeliverables] = useState(""),
    [sensitive, setSensitive] = useState(false);
  const [fieldDocs, setFieldDocs] = useState("METHODOLOGY"),
    [publicationDocs, setPublicationDocs] = useState(
      "METHODOLOGY\nDISCLOSURE_REVIEW",
    );
  const [gateDocuments, setGateDocuments] = useState<Record<string, string>>(
    {},
  );
  async function load() {
    const page = (await request(
      `${base}/evaluations?limit=100`,
    )) as Page<Evaluation>;
    setItems(page.items);
  }
  useEffect(() => {
    void load().catch((caught) => setError(explain(caught)));
  }, [base]);
  async function create(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await request(`${base}/evaluations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          data: {
            title,
            study_type: studyType,
            programme_id: programmeId,
            period_id: periodId,
            questions: split(questions),
            study_design: design,
            evaluator,
            independence: { claimed: false },
            ethics_requirements: [],
            budget: { amount: budget, currency },
            deliverables: split(deliverables),
            required_documents: {
              FIELD_COLLECTION: split(fieldDocs),
              PUBLICATION: split(publicationDocs),
            },
            sensitive_processing: sensitive,
          },
        }),
      });
      setTitle("");
      await load();
    } catch (caught) {
      setError(explain(caught));
    }
  }
  async function gate(
    row: Evaluation,
    stage: "FIELD_COLLECTION" | "PUBLICATION",
  ) {
    try {
      const documents = split(gateDocuments[row.object_id] || "").map(
        (line) => {
          const [kind, object_id, revision_id] = line
            .split(",")
            .map((part) => part.trim());
          return { kind, object_id, revision_id };
        },
      );
      await request(`${base}/evaluations/${row.object_id}/actions/stage-gate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          expected_revision: row.revision_id,
          data: { stage, documents },
        }),
      });
      await load();
    } catch (caught) {
      setError(explain(caught));
    }
  }
  async function showHistory(id: string) {
    try {
      const page = (await request(
        `${base}/evaluations/${id}/stage-gates?limit=100`,
      )) as Page<unknown>;
      setHistory((old) => ({ ...old, [id]: page.items }));
    } catch (caught) {
      setError(explain(caught));
    }
  }
  return (
    <section className="panel" aria-labelledby="evaluation-registry-title">
      <h2 id="evaluation-registry-title">Evaluation registry</h2>
      <p className="muted">
        Register an evaluation, pin its method and policy evidence, and review
        every passed or blocked gate. Registration never approves sensitive
        processing or verifies independence.
      </p>
      {error ? <p role="alert">{error}</p> : null}
      {capabilities.includes("evaluations.draft.edit") ? (
        <form onSubmit={create} className="stack">
          <label>
            Title
            <input
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </label>
          <label>
            Study type
            <select
              value={studyType}
              onChange={(e) => setStudyType(e.target.value)}
            >
              <option>BASELINE</option>
              <option>MIDLINE</option>
              <option>ENDLINE</option>
              <option>OTHER</option>
            </select>
          </label>
          <label>
            Programme ID
            <input
              required
              value={programmeId}
              onChange={(e) => setProgrammeId(e.target.value)}
            />
          </label>
          <label>
            Observation period ID
            <input
              required
              value={periodId}
              onChange={(e) => setPeriodId(e.target.value)}
            />
          </label>
          <label>
            Evaluation questions, one per line
            <textarea
              required
              value={questions}
              onChange={(e) => setQuestions(e.target.value)}
            />
          </label>
          <label>
            Study design
            <textarea
              required
              value={design}
              onChange={(e) => setDesign(e.target.value)}
            />
          </label>
          <label>
            Evaluator
            <input
              required
              value={evaluator}
              onChange={(e) => setEvaluator(e.target.value)}
            />
          </label>
          <label>
            Budget amount
            <input
              required
              inputMode="decimal"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            />
          </label>
          <label>
            Currency
            <input
              required
              pattern="[A-Z]{3}"
              value={currency}
              onChange={(e) => setCurrency(e.target.value.toUpperCase())}
            />
          </label>
          <label>
            Deliverables, one per line
            <textarea
              required
              value={deliverables}
              onChange={(e) => setDeliverables(e.target.value)}
            />
          </label>
          <label>
            Field-collection document kinds
            <textarea
              value={fieldDocs}
              onChange={(e) => setFieldDocs(e.target.value)}
            />
          </label>
          <label>
            Publication document kinds
            <textarea
              value={publicationDocs}
              onChange={(e) => setPublicationDocs(e.target.value)}
            />
          </label>
          <label>
            <input
              type="checkbox"
              checked={sensitive}
              onChange={(e) => setSensitive(e.target.checked)}
            />{" "}
            Sensitive processing is proposed; a separate governed approval is
            still required
          </label>
          <button type="submit">Register evaluation</button>
        </form>
      ) : null}
      <div className="table-scroll">
        <table aria-label="Controlled evaluations">
          <thead>
            <tr>
              <th>Evaluation</th>
              <th>Type</th>
              <th>Stage</th>
              <th>Sensitive approval</th>
              <th>Independence</th>
              <th>Gate evidence</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <React.Fragment key={row.object_id}>
                <tr>
                  <td>{row.data.title}</td>
                  <td>{row.data.study_type}</td>
                  <td>{row.data.stage}</td>
                  <td>
                    {row.data.sensitive_processing_approved
                      ? "Approved"
                      : "Not approved"}
                  </td>
                  <td>{row.data.independence.verification}</td>
                  <td>
                    <textarea
                      aria-label={`Gate documents for ${row.data.title}`}
                      placeholder="KIND, object UUID, revision UUID"
                      value={gateDocuments[row.object_id] || ""}
                      onChange={(e) =>
                        setGateDocuments((old) => ({
                          ...old,
                          [row.object_id]: e.target.value,
                        }))
                      }
                    />
                  </td>
                  <td>
                    {capabilities.includes("evaluations.draft.edit") &&
                    row.data.stage === "REGISTERED" ? (
                      <button
                        onClick={() => void gate(row, "FIELD_COLLECTION")}
                      >
                        Check field collection
                      </button>
                    ) : null}
                    {capabilities.includes("evaluations.draft.edit") &&
                    row.data.stage === "FIELD_COLLECTION" ? (
                      <button onClick={() => void gate(row, "PUBLICATION")}>
                        Check publication
                      </button>
                    ) : null}
                    <button onClick={() => void showHistory(row.object_id)}>
                      Gate history
                    </button>
                  </td>
                </tr>
                {history[row.object_id] ? (
                  <tr>
                    <td colSpan={7}>
                      <pre>
                        {JSON.stringify(history[row.object_id], null, 2)}
                      </pre>
                    </td>
                  </tr>
                ) : null}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
