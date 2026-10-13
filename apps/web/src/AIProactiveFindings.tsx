import React, { useState } from "react";

type Props = {
  base: string;
  policyVersion: number | null;
  canManage: boolean;
  canSuggest: boolean;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
};
type Task = { task_id: string; task_code: string; enabled: boolean };
type Suggestion = {
  suggestion_id: string;
  summary: string;
  limitation: string;
  proposed_follow_up: string;
  status: "SUGGESTED";
  confirmed_finding: false;
};
const selectors = (value: string) =>
  value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => {
      const [object_id, revision_id] = item.split(":");
      return { object_id, revision_id };
    });

export function AIProactiveFindings({
  base,
  policyVersion,
  canManage,
  canSuggest,
  request,
  explain,
}: Props) {
  const [taskForm, setTaskForm] = useState({
    task_code: "",
    scope_object_id: "",
    scope_revision_id: "",
    owner_principal_id: "",
    cooldown_seconds: "3600",
    noise_limit: "5",
  });
  const [findingForm, setFindingForm] = useState({
    task_id: "",
    detection_event_key: "",
    affected_results: "",
    evidence: "",
    summary: "",
    limitation: "",
    proposed_follow_up: "",
  });
  const [task, setTask] = useState<Task | null>(null);
  const [suggestion, setSuggestion] = useState<Suggestion | null>(null);
  const [review, setReview] = useState({
    decision: "DISMISSED",
    reason: "",
    assigned_to: "",
  });
  const [reviewed, setReviewed] = useState(false);
  const [error, setError] = useState("");
  if (!canManage && !canSuggest) return null;
  return (
    <section aria-labelledby="ai-proactive-findings">
      <h3 id="ai-proactive-findings">Proactive finding suggestions</h3>
      <p className="muted">
        Detection runs only for an exact enabled programme scope. Output stays
        visibly suggested until one person verifies, dismisses or assigns it;
        source values are never changed.
      </p>
      {canManage && (
        <form
          onSubmit={async (event) => {
            event.preventDefault();
            setError("");
            try {
              const result = await request(
                base + "ai-enablement/detection-tasks",
                {
                  method: "POST",
                  body: JSON.stringify({
                    operation_id: crypto.randomUUID(),
                    ...taskForm,
                    cooldown_seconds: Number(taskForm.cooldown_seconds),
                    noise_limit: Number(taskForm.noise_limit),
                    enabled: true,
                    policy_version: policyVersion,
                    language: "en",
                  }),
                },
              );
              setTask(result);
              setFindingForm((current) => ({
                ...current,
                task_id: result.task_id,
              }));
            } catch (caught) {
              setError(explain(caught));
            }
          }}
        >
          <h4>Enable a bounded detector</h4>
          {Object.entries(taskForm).map(([name, value]) => (
            <label key={name}>
              {name.replaceAll("_", " ")}
              <input
                required
                value={value}
                onChange={(event) =>
                  setTaskForm({ ...taskForm, [name]: event.target.value })
                }
              />
            </label>
          ))}
          <button disabled={policyVersion === null}>Enable detector</button>
        </form>
      )}
      {task && (
        <p role="status">
          Enabled {task.task_code}: {task.task_id}
        </p>
      )}
      {canSuggest && (
        <form
          onSubmit={async (event) => {
            event.preventDefault();
            setError("");
            try {
              const result = await request(
                base + "ai-enablement/suggested-findings",
                {
                  method: "POST",
                  body: JSON.stringify({
                    operation_id: crypto.randomUUID(),
                    ...findingForm,
                    affected_results: selectors(findingForm.affected_results),
                    evidence: selectors(findingForm.evidence),
                    language: "en",
                  }),
                },
              );
              setSuggestion(result);
              setReviewed(false);
            } catch (caught) {
              setError(explain(caught));
            }
          }}
        >
          <h4>Create a suggestion</h4>
          {Object.entries(findingForm).map(([name, value]) => (
            <label key={name}>
              {name.replaceAll("_", " ")}
              {name === "summary" ||
              name === "limitation" ||
              name === "proposed_follow_up" ? (
                <textarea
                  required
                  value={value}
                  onChange={(event) =>
                    setFindingForm({
                      ...findingForm,
                      [name]: event.target.value,
                    })
                  }
                />
              ) : (
                <input
                  required
                  value={value}
                  onChange={(event) =>
                    setFindingForm({
                      ...findingForm,
                      [name]: event.target.value,
                    })
                  }
                />
              )}
            </label>
          ))}
          <p className="muted">
            Result and evidence sources use object-id:revision-id pairs
            separated by commas.
          </p>
          <button>Create unconfirmed suggestion</button>
        </form>
      )}
      {suggestion && (
        <article className="ai-result-card">
          <h4>{suggestion.summary}</h4>
          <p>
            <strong>Status:</strong> Suggested — not a confirmed fraud, impact
            or programme-risk finding.
          </p>
          <p>
            <strong>Limitation:</strong> {suggestion.limitation}
          </p>
          <p>
            <strong>Follow up:</strong> {suggestion.proposed_follow_up}
          </p>
          {canManage && !reviewed && (
            <form
              onSubmit={async (event) => {
                event.preventDefault();
                setError("");
                try {
                  await request(
                    base +
                      `ai-enablement/suggested-findings/${suggestion.suggestion_id}/actions/review`,
                    {
                      method: "POST",
                      body: JSON.stringify({
                        operation_id: crypto.randomUUID(),
                        decision: review.decision,
                        reason: review.reason,
                        assigned_to:
                          review.decision === "ASSIGNED"
                            ? review.assigned_to
                            : null,
                      }),
                    },
                  );
                  setReviewed(true);
                } catch (caught) {
                  setError(explain(caught));
                }
              }}
            >
              <label>
                Decision
                <select
                  value={review.decision}
                  onChange={(event) =>
                    setReview({ ...review, decision: event.target.value })
                  }
                >
                  <option value="VERIFIED">Verify</option>
                  <option value="DISMISSED">Dismiss</option>
                  <option value="ASSIGNED">Assign</option>
                </select>
              </label>
              <label>
                Reason
                <textarea
                  required
                  value={review.reason}
                  onChange={(event) =>
                    setReview({ ...review, reason: event.target.value })
                  }
                />
              </label>
              {review.decision === "ASSIGNED" && (
                <label>
                  Assignee principal ID
                  <input
                    required
                    value={review.assigned_to}
                    onChange={(event) =>
                      setReview({ ...review, assigned_to: event.target.value })
                    }
                  />
                </label>
              )}
              <button>Save individual review</button>
            </form>
          )}
          {reviewed && (
            <p role="status">Feedback recorded. Source values unchanged.</p>
          )}
        </article>
      )}
      {error && <p role="alert">{error}</p>}
    </section>
  );
}
