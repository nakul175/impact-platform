import React, { useState } from "react";

type Props = {
  base: string;
  policyVersion: number | null;
  canAsk: boolean;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
};

type Answer = {
  state: "ANSWERED" | "CLARIFICATION_REQUIRED" | "ABSTAINED";
  answer: string | null;
  clarification_fields: string[];
  claims: { text: string; citation_numbers: number[] }[];
  citations: {
    number: number;
    object_id: string;
    revision_id: string;
    location: string;
  }[];
  missing_evidence: string[];
  contradictions: { field: string; values: string[] }[];
};

export function AIEvidenceQuestions({
  base,
  policyVersion,
  canAsk,
  request,
  explain,
}: Props) {
  const [form, setForm] = useState({
    question: "",
    programme_id: "",
    programme_revision_id: "",
    period_id: "",
    period_revision_id: "",
    result_id: "",
    result_revision_id: "",
  });
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const update = (name: keyof typeof form, value: string) =>
    setForm((current) => ({ ...current, [name]: value }));
  if (!canAsk) return null;
  return (
    <section aria-labelledby="ai-evidence-question">
      <h3 id="ai-evidence-question">Evidence questions</h3>
      <p className="muted">
        Answers use only the exact governed result revisions you select. Every
        material claim links to its stored field. Ambiguous scope asks for
        clarification; inaccessible sources return the same bounded abstention.
      </p>
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          setBusy(true);
          setError("");
          setAnswer(null);
          try {
            const result = await request(
              base + "ai-enablement/evidence-questions",
              {
                method: "POST",
                body: JSON.stringify({
                  question: form.question,
                  programme_id: form.programme_id || null,
                  programme_revision_id: form.programme_revision_id || null,
                  period_id: form.period_id || null,
                  period_revision_id: form.period_revision_id || null,
                  source_mode: "SELECTED_GOVERNED_RESULTS",
                  sources:
                    form.result_id && form.result_revision_id
                      ? [
                          {
                            object_id: form.result_id,
                            revision_id: form.result_revision_id,
                          },
                        ]
                      : [],
                  policy_version: policyVersion,
                  language: "en",
                }),
              },
            );
            setAnswer(result);
          } catch (caught) {
            setError(explain(caught));
          } finally {
            setBusy(false);
          }
        }}
      >
        <fieldset disabled={busy || policyVersion === null}>
          <label>
            Question
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
                ["programme_id", "Programme ID"],
                ["programme_revision_id", "Programme revision"],
                ["period_id", "Period ID"],
                ["period_revision_id", "Period revision"],
                ["result_id", "Governed result ID"],
                ["result_revision_id", "Result revision"],
              ] as const
            ).map(([name, label]) => (
              <label key={name}>
                {label}
                <input
                  value={form[name]}
                  onChange={(event) => update(name, event.target.value)}
                  placeholder="UUID"
                />
              </label>
            ))}
          </div>
          <button type="submit">Ask from selected evidence</button>
        </fieldset>
      </form>
      {error && <div className="error">{error}</div>}
      {answer && (
        <div aria-live="polite">
          <p className="badge">{answer.state.replaceAll("_", " ")}</p>
          {answer.answer && <p>{answer.answer}</p>}
          {!!answer.clarification_fields.length && (
            <p>Clarify: {answer.clarification_fields.join(", ")}</p>
          )}
          {!!answer.missing_evidence.length && (
            <ul>
              {answer.missing_evidence.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
          {!!answer.contradictions.length && (
            <div>
              <h4>Contradictory evidence</h4>
              <ul>
                {answer.contradictions.map((item) => (
                  <li key={item.field}>
                    {item.field}: {item.values.join(" / ")}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {!!answer.citations.length && (
            <div>
              <h4>Source locations</h4>
              <ol>
                {answer.citations.map((citation) => (
                  <li key={citation.number}>
                    {citation.object_id} · {citation.revision_id} ·{" "}
                    {citation.location}
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
