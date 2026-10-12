import React, { useState } from "react";

type Props = {
  base: string;
  policyVersion: number | null;
  canAnalyse: boolean;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
};

type Result = {
  answer: string;
  result_references: {
    object_id: string;
    revision_id: string;
    numerator: string;
    denominator: string;
  }[];
  calculation_receipt: {
    receipt_id: string;
    tool: string;
    rounding_rule: string;
  };
};

export function AINumericAnalysis({
  base,
  policyVersion,
  canAnalyse,
  request,
  explain,
}: Props) {
  const [form, setForm] = useState({
    question: "",
    period_id: "",
    period_revision_id: "",
    first_object_id: "",
    first_revision_id: "",
    second_object_id: "",
    second_revision_id: "",
    drafted_claim: "",
  });
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const update = (name: keyof typeof form, value: string) =>
    setForm((current) => ({ ...current, [name]: value }));
  if (!canAnalyse) return null;
  return (
    <section aria-labelledby="ai-numeric-analysis">
      <h3 id="ai-numeric-analysis">Governed numerical analysis</h3>
      <p className="muted">
        Pool two exact governed percentage results from one period. The closed
        decimal tool returns the claim and calculation receipt; no model
        recomputes the value or runs arbitrary queries.
      </p>
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          setBusy(true);
          setError("");
          setResult(null);
          try {
            setResult(
              await request(base + "ai-enablement/numeric-analysis", {
                method: "POST",
                body: JSON.stringify({
                  question: form.question,
                  plan: {
                    measure: "POOLED_PERCENTAGE",
                    sources: [
                      {
                        object_id: form.first_object_id,
                        revision_id: form.first_revision_id,
                      },
                      {
                        object_id: form.second_object_id,
                        revision_id: form.second_revision_id,
                      },
                    ],
                    filters: {},
                    period_id: form.period_id,
                    period_revision_id: form.period_revision_id,
                    dimensions: [],
                    source_mode: "OFFICIAL",
                    permitted_operation: "POOL_RATIO",
                  },
                  drafted_claim: form.drafted_claim || null,
                  policy_version: policyVersion,
                  language: "en",
                }),
              }),
            );
          } catch (caught) {
            setError(explain(caught));
          } finally {
            setBusy(false);
          }
        }}
      >
        <fieldset disabled={busy || policyVersion === null}>
          <label>
            Numerical question
            <textarea
              required
              maxLength={2000}
              value={form.question}
              onChange={(event) => update("question", event.target.value)}
            />
          </label>
          <div className="form-grid">
            {(
              [
                ["period_id", "Period ID"],
                ["period_revision_id", "Period revision"],
                ["first_object_id", "First result ID"],
                ["first_revision_id", "First result revision"],
                ["second_object_id", "Second result ID"],
                ["second_revision_id", "Second result revision"],
              ] as const
            ).map(([name, text]) => (
              <label key={name}>
                {text}
                <input
                  required
                  value={form[name]}
                  onChange={(event) => update(name, event.target.value)}
                  placeholder="UUID"
                />
              </label>
            ))}
          </div>
          <label>
            Optional drafted claim to verify exactly
            <input
              maxLength={500}
              value={form.drafted_claim}
              onChange={(event) => update("drafted_claim", event.target.value)}
              placeholder="46.36 percent (51/110)"
            />
          </label>
          <button type="submit">Run governed calculation</button>
        </fieldset>
      </form>
      {error && <div className="error">{error}</div>}
      {result && (
        <div aria-live="polite">
          <p className="badge">{result.answer}</p>
          <p>
            Receipt {result.calculation_receipt.receipt_id} ·{" "}
            {result.calculation_receipt.tool} ·{" "}
            {result.calculation_receipt.rounding_rule}
          </p>
          <ul>
            {result.result_references.map((reference) => (
              <li key={reference.revision_id}>
                {reference.object_id} · {reference.revision_id} ·{" "}
                {reference.numerator}/{reference.denominator}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
