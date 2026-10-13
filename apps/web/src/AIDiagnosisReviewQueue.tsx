import React, { useEffect, useState } from "react";

type Request = (path: string, options?: RequestInit) => Promise<any>;
type Event = {
  event_id: string;
  kind: string;
  comment: string | null;
  actor_id: string;
  recorded_at: string;
};
type Review = {
  review_id: string;
  diagnosis_id: string;
  diagnosis_revision: string;
  advisor_membership_id: string;
  requested_at: string;
  status: string;
  events: Event[];
};
type Shared = {
  base: string;
  request: Request;
  explain: (error: unknown) => string;
  capabilities: string[];
};

export function AIDiagnosisReviewQueue(props: Shared) {
  const allowed = props.capabilities.includes("ai.diagnosis.review");
  const [items, setItems] = useState<Review[]>([]);
  const [comment, setComment] = useState<Record<string, string>>({});
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  async function load() {
    if (!allowed) return;
    try {
      const result = await props.request(
        props.base + "ai-enablement/diagnosis-review-queue",
      );
      setItems(Array.isArray(result?.items) ? result.items : []);
    } catch (cause) {
      setMessage(props.explain(cause));
    }
  }
  useEffect(() => {
    void load();
  }, [allowed]);
  async function act(review: Review, suffix: string, text?: string) {
    setBusy(true);
    try {
      await props.request(
        `${props.base}ai-enablement/diagnosis-reviews/${review.review_id}/${suffix}`,
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            expected_diagnosis_revision: review.diagnosis_revision,
            ...(text === undefined ? {} : { comment: text }),
          }),
        },
      );
      setMessage("Review record saved.");
      setComment((value) => ({ ...value, [review.review_id]: "" }));
      await load();
    } catch (cause) {
      setMessage(props.explain(cause));
    } finally {
      setBusy(false);
    }
  }
  if (!allowed) return null;
  return (
    <section className="card" aria-label="Assigned diagnosis reviews">
      <h3>Assigned diagnosis reviews</h3>
      <p className="muted">
        Validation records expert review of this exact revision. It is separate
        from owner acceptance or publication approval.
      </p>
      {message && <p role="status">{message}</p>}
      {!items.length && <p>No diagnosis is assigned for review.</p>}
      {items.map((review) => (
        <article key={review.review_id}>
          <h4>{review.status}</h4>
          <p>
            Diagnosis {review.diagnosis_id} · revision{" "}
            {review.diagnosis_revision}
          </p>
          <ol>
            {review.events.map((event) => (
              <li key={event.event_id}>
                {event.kind}
                {event.comment ? `: ${event.comment}` : ""} ·{" "}
                {new Date(event.recorded_at).toLocaleString()}
              </li>
            ))}
          </ol>
          {review.status === "QUEUED" && (
            <button
              disabled={busy}
              onClick={() => void act(review, "actions/start")}
            >
              Start review
            </button>
          )}
          {review.status === "IN_REVIEW" && (
            <>
              <label>
                Organisation-visible comment
                <textarea
                  maxLength={4000}
                  value={comment[review.review_id] || ""}
                  onChange={(event) =>
                    setComment((value) => ({
                      ...value,
                      [review.review_id]: event.target.value,
                    }))
                  }
                />
              </label>
              <button
                disabled={busy || !(comment[review.review_id] || "").trim()}
                onClick={() =>
                  void act(review, "comments", comment[review.review_id])
                }
              >
                Add comment
              </button>
              <button
                disabled={busy}
                onClick={() => void act(review, "actions/validate")}
              >
                Validate this revision
              </button>
            </>
          )}
        </article>
      ))}
    </section>
  );
}

export function AIDiagnosisReviewStatus(
  props: Shared & {
    diagnosisId: string;
    diagnosisRevision: string;
    completed: boolean;
  },
) {
  const canRead = props.capabilities.includes("ai.diagnosis.read");
  const canManage = props.capabilities.includes("ai.diagnosis.manage");
  const [items, setItems] = useState<Review[]>([]);
  const [advisorMembership, setAdvisorMembership] = useState("");
  const [message, setMessage] = useState("");
  async function load() {
    if (!canRead) return;
    try {
      const result = await props.request(
        `${props.base}ai-enablement/diagnoses/${props.diagnosisId}/advisor-reviews`,
      );
      setItems(Array.isArray(result?.items) ? result.items : []);
    } catch (cause) {
      setMessage(props.explain(cause));
    }
  }
  useEffect(() => {
    void load();
  }, [props.diagnosisId, props.diagnosisRevision]);
  async function requestReview() {
    try {
      await props.request(
        `${props.base}ai-enablement/diagnoses/${props.diagnosisId}/advisor-reviews`,
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            expected_diagnosis_revision: props.diagnosisRevision,
            advisor_membership_id: advisorMembership.toLowerCase(),
          }),
        },
      );
      setAdvisorMembership("");
      setMessage("Advisor review requested for this exact revision.");
      await load();
    } catch (cause) {
      setMessage(props.explain(cause));
    }
  }
  if (!canRead) return null;
  return (
    <section aria-label="Advisor review status">
      <h4>Advisor review</h4>
      {message && <p role="status">{message}</p>}
      {canManage && props.completed && (
        <>
          <label>
            Advisor membership ID
            <input
              value={advisorMembership}
              onChange={(event) => setAdvisorMembership(event.target.value)}
            />
          </label>
          <button
            type="button"
            disabled={!/^[0-9a-f-]{36}$/i.test(advisorMembership)}
            onClick={() => void requestReview()}
          >
            Request review
          </button>
        </>
      )}
      {!items.length ? (
        <p>No advisor review requested for this revision.</p>
      ) : (
        items.map((review) => (
          <article key={review.review_id}>
            <strong>{review.status}</strong>
            {review.events
              .filter((event) => event.kind === "COMMENTED")
              .map((event) => (
                <p key={event.event_id}>{event.comment}</p>
              ))}
          </article>
        ))
      )}
    </section>
  );
}
