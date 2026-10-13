import React, { useRef, useState } from "react";

type Props = {
  base: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
  capabilities: string[];
};

type Review = {
  object_id: string;
  revision_id: string;
  business_state: string;
  review: any;
};

export function AIQuarterlyValueReviewPanel(props: Props) {
  const [observationId, setObservationId] = useState("");
  const [observationRevision, setObservationRevision] = useState("");
  const [reviewId, setReviewId] = useState("");
  const [review, setReview] = useState<Review | null>(null);
  const [agreement, setAgreement] = useState("");
  const [action, setAction] = useState({
    agreement_id: "",
    title: "",
    owner_membership_id: "",
    due_on: "",
  });
  const [progress, setProgress] = useState({
    action_id: "",
    status: "IN_PROGRESS",
    note: "",
  });
  const [summary, setSummary] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const pending = useRef<{ key: string; body: string } | null>(null);

  if (!props.capabilities.includes("ai.diagnosis.review")) return null;
  const root = `${props.base}ai-enablement/quarterly-value-reviews`;
  const change = (setter: () => void) => {
    setter();
    pending.current = null;
    setError("");
  };

  async function send(
    key: string,
    path: string,
    value: Record<string, unknown>,
  ) {
    setBusy(true);
    setMessage("");
    setError("");
    if (!pending.current || pending.current.key !== key) {
      pending.current = {
        key,
        body: JSON.stringify({ operation_id: crypto.randomUUID(), ...value }),
      };
    }
    try {
      const result = await props.request(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: pending.current.body,
      });
      pending.current = null;
      setReview(result);
      setReviewId(result.object_id);
      setMessage("Saved from the authoritative review record.");
    } catch (reason) {
      setError(props.explain(reason));
    } finally {
      setBusy(false);
    }
  }

  async function open() {
    setBusy(true);
    setError("");
    try {
      setReview(await props.request(`${root}/${reviewId}`));
    } catch (reason) {
      setError(props.explain(reason));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel" aria-labelledby="quarterly-review-heading">
      <h2 id="quarterly-review-heading">Quarterly value review</h2>
      <p>
        Start from the fixed quarterly template using one current outcome
        observation. Completion records the review; it does not mean tracked
        actions are finished.
      </p>
      {!review && (
        <>
          <label>
            Outcome observation ID
            <input
              value={observationId}
              onChange={(e) => change(() => setObservationId(e.target.value))}
            />
          </label>
          <label>
            Outcome observation revision
            <input
              value={observationRevision}
              onChange={(e) =>
                change(() => setObservationRevision(e.target.value))
              }
            />
          </label>
          <button
            type="button"
            disabled={busy || !observationId || !observationRevision}
            onClick={() =>
              void send("start", root, {
                outcome_observation_id: observationId,
                outcome_observation_revision: observationRevision,
              })
            }
          >
            Start review from template
          </button>
          <h3>Open an existing review</h3>
          <label>
            Review ID
            <input
              value={reviewId}
              onChange={(e) => setReviewId(e.target.value)}
            />
          </label>
          <button
            type="button"
            disabled={busy || !reviewId}
            onClick={() => void open()}
          >
            Open review
          </button>
        </>
      )}
      {review && (
        <>
          <p>
            <strong>{review.review.template.title}</strong> · edition{" "}
            {review.review.template.edition}
          </p>
          <p>
            Period {review.review.period_start} to {review.review.period_end};
            due {review.review.due_on}. Status: {review.business_state}.
          </p>
          <ol>
            {review.review.template.sections.map((section: any) => (
              <li key={section.key}>{section.title}</li>
            ))}
          </ol>
          <h3>Agreements</h3>
          {review.review.agreements.length === 0 ? (
            <p>No agreements recorded.</p>
          ) : (
            <ul>
              {review.review.agreements.map((item: any) => (
                <li key={item.agreement_id}>
                  {item.text} <code>{item.agreement_id}</code>
                </li>
              ))}
            </ul>
          )}
          {review.business_state === "InProgress" && (
            <>
              <label>
                Agreed item
                <textarea
                  value={agreement}
                  maxLength={2000}
                  onChange={(e) => change(() => setAgreement(e.target.value))}
                />
              </label>
              <button
                type="button"
                disabled={busy || !agreement}
                onClick={() =>
                  void send(
                    "agreement",
                    `${root}/${review.object_id}/agreements`,
                    {
                      expected_revision: review.revision_id,
                      agreement_id: crypto.randomUUID(),
                      text: agreement,
                    },
                  )
                }
              >
                Record agreement
              </button>
              <fieldset>
                <legend>Log an agreed action</legend>
                <label>
                  Agreement ID
                  <input
                    value={action.agreement_id}
                    onChange={(e) =>
                      change(() =>
                        setAction({ ...action, agreement_id: e.target.value }),
                      )
                    }
                  />
                </label>
                <label>
                  Action title
                  <input
                    value={action.title}
                    onChange={(e) =>
                      change(() =>
                        setAction({ ...action, title: e.target.value }),
                      )
                    }
                  />
                </label>
                <label>
                  Owner membership ID
                  <input
                    value={action.owner_membership_id}
                    onChange={(e) =>
                      change(() =>
                        setAction({
                          ...action,
                          owner_membership_id: e.target.value,
                        }),
                      )
                    }
                  />
                </label>
                <label>
                  Due date
                  <input
                    type="date"
                    value={action.due_on}
                    onChange={(e) =>
                      change(() =>
                        setAction({ ...action, due_on: e.target.value }),
                      )
                    }
                  />
                </label>
                <button
                  type="button"
                  disabled={
                    busy || Object.values(action).some((value) => !value)
                  }
                  onClick={() =>
                    void send("action", `${root}/${review.object_id}/actions`, {
                      expected_revision: review.revision_id,
                      action_id: crypto.randomUUID(),
                      ...action,
                    })
                  }
                >
                  Log tracked action
                </button>
              </fieldset>
              <fieldset>
                <legend>Track action progress</legend>
                <label>
                  Action ID
                  <input
                    value={progress.action_id}
                    onChange={(e) =>
                      change(() =>
                        setProgress({ ...progress, action_id: e.target.value }),
                      )
                    }
                  />
                </label>
                <label>
                  Status
                  <select
                    value={progress.status}
                    onChange={(e) =>
                      change(() =>
                        setProgress({ ...progress, status: e.target.value }),
                      )
                    }
                  >
                    {["OPEN", "IN_PROGRESS", "BLOCKED", "DONE"].map((value) => (
                      <option key={value}>{value}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Progress note
                  <textarea
                    value={progress.note}
                    maxLength={2000}
                    onChange={(e) =>
                      change(() =>
                        setProgress({ ...progress, note: e.target.value }),
                      )
                    }
                  />
                </label>
                <button
                  type="button"
                  disabled={busy || !progress.action_id || !progress.note}
                  onClick={() =>
                    void send(
                      "progress",
                      `${root}/${review.object_id}/actions/${progress.action_id}/progress`,
                      {
                        expected_revision: review.revision_id,
                        status: progress.status,
                        note: progress.note,
                      },
                    )
                  }
                >
                  Save progress
                </button>
              </fieldset>
              <label>
                Review summary
                <textarea
                  value={summary}
                  maxLength={4000}
                  onChange={(e) => change(() => setSummary(e.target.value))}
                />
              </label>
              <p id="review-completion-help">
                Every recorded agreement must have exactly one logged action
                with a current owner and tracked status. The server refuses
                incomplete reviews.
              </p>
              <button
                type="button"
                aria-describedby="review-completion-help"
                disabled={busy || !summary}
                onClick={() =>
                  void send(
                    "complete",
                    `${root}/${review.object_id}/actions/complete`,
                    { expected_revision: review.revision_id, summary },
                  )
                }
              >
                Check and complete review
              </button>
            </>
          )}
          <h3>Tracked actions</h3>
          {review.review.actions.length === 0 ? (
            <p>No actions logged.</p>
          ) : (
            <table>
              <caption>Agreed actions and current progress</caption>
              <thead>
                <tr>
                  <th scope="col">Action</th>
                  <th scope="col">Owner</th>
                  <th scope="col">Due</th>
                  <th scope="col">Status</th>
                </tr>
              </thead>
              <tbody>
                {review.review.actions.map((item: any) => (
                  <tr key={item.action_id}>
                    <th scope="row">
                      {item.title}
                      <br />
                      <code>{item.action_id}</code>
                    </th>
                    <td>{item.owner_membership_id}</td>
                    <td>{item.due_on}</td>
                    <td>{item.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
      {error && <p role="alert">{error}</p>}
      {message && (
        <p role="status" aria-live="polite">
          {message}
        </p>
      )}
    </section>
  );
}
