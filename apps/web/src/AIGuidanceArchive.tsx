import { useEffect, useRef, useState } from "react";
import type { Catalog } from "./AIEnablement";

type Revision = {
  revision_id: string;
  revision_number: number;
  saved_at: string;
  title: string;
  historical_snapshots_available: boolean;
};
type History = {
  object_id: string;
  items: Revision[];
  next_cursor: string | null;
};
type Archived<T> =
  | { status: "AVAILABLE"; content_version: string; payload: T }
  | { status: "UNAVAILABLE"; content_version: string | null; payload: null };
type ArchivedCatalog = Omit<Catalog, "advisory_available" | "use_cases"> & {
  provenance: {
    source_concept: string;
    note: string;
    status: string;
    validated_demand: boolean;
  };
  use_cases: (Catalog["use_cases"][number] & {
    sectors: string[];
    kind: string;
    data_requirement: string;
    sensitivity: string;
    content_status: string;
  })[];
};
type Solution = {
  id: string;
  name: string;
  provider: string;
  description: string;
  commercial_model: string;
  category: string;
  deployment: string;
  api_available: string;
  nonprofit_offer: string;
  source_urls: { label: string; url: string }[];
  verification_notes: string[];
  data_review_questions: string[];
};
type Practice = {
  content_version: string;
  templates: {
    id: string;
    title: string;
    purpose: string;
    input_guidance: string[];
    example_brief: string;
    allowed_inputs: string[];
    prompt_framework: string[];
    prohibited_inputs: string[];
    review_steps: { id: string; label: string }[];
  }[];
  disclaimer: string;
};
type Guidance = {
  object_id: string;
  revision_id: string;
  status: "COMPLETE" | "PARTIAL" | "UNAVAILABLE";
  captured_at: string | null;
  snapshot_sha256: string | null;
  catalog: Archived<ArchivedCatalog>;
  solutions: Archived<{
    content_version: string;
    checked_on: string;
    explanation: string;
    solutions: Solution[];
    comparison_criteria: { id: string; label: string; prompt: string }[];
  }>;
  practice: Archived<Practice>;
  disclaimer: string;
};
type Props = {
  base: string;
  objectId: string;
  currentRevision: string;
  request: (path: string, options?: RequestInit) => Promise<unknown>;
  explain: (error: unknown) => string;
};
const when = (value: string) => new Date(value).toLocaleString();
function Items({ values }: { values: string[] }) {
  return (
    <ul>
      {values.map((value, index) => (
        <li key={index}>{value}</li>
      ))}
    </ul>
  );
}

export function AIGuidanceArchive({
  base,
  objectId,
  currentRevision,
  request,
  explain,
}: Props) {
  const [open, setOpen] = useState(false);
  const [history, setHistory] = useState<History | null>(null);
  const [choice, setChoice] = useState(currentRevision);
  const [guidance, setGuidance] = useState<Guidance | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const epoch = useRef(0);
  const prefix = base + "ai-enablement/plans/" + objectId + "/revisions";
  useEffect(() => {
    ++epoch.current;
    setHistory(null);
    setChoice(currentRevision);
    setGuidance(null);
    setError("");
    setBusy(false);
    return () => {
      ++epoch.current;
    };
  }, [base, objectId, currentRevision]);
  useEffect(() => {
    if (!open) return;
    const controller = new AbortController();
    setHistory(null);
    setError("");
    (
      request(prefix + "?limit=50", {
        signal: controller.signal,
      }) as Promise<History>
    )
      .then((value) => {
        if (!controller.signal.aborted) setHistory(value);
      })
      .catch((e) => {
        if (!controller.signal.aborted) setError(explain(e));
      });
    return () => controller.abort();
  }, [open, prefix, currentRevision]);
  useEffect(() => {
    setGuidance(null);
    if (!open || !choice) return;
    const controller = new AbortController();
    setError("");
    (
      request(prefix + "/" + choice + "/guidance", {
        signal: controller.signal,
      }) as Promise<Guidance>
    )
      .then((value) => {
        if (!controller.signal.aborted) setGuidance(value);
      })
      .catch((e) => {
        if (!controller.signal.aborted) setError(explain(e));
      });
    return () => controller.abort();
  }, [open, prefix, choice]);
  async function more() {
    if (!history?.next_cursor || busy) return;
    const current = epoch.current;
    setBusy(true);
    setError("");
    try {
      const value = (await request(
        prefix + "?limit=50&cursor=" + encodeURIComponent(history.next_cursor),
      )) as History;
      if (current !== epoch.current) return;
      setHistory((previous) => ({
        ...value,
        items: [
          ...(previous?.items || []),
          ...value.items.filter(
            (item) =>
              !previous?.items.some(
                (old) => old.revision_id === item.revision_id,
              ),
          ),
        ],
      }));
    } catch (e) {
      if (current === epoch.current) setError(explain(e));
    } finally {
      if (current === epoch.current) setBusy(false);
    }
  }
  return (
    <section
      className="ai-guidance-archive"
      aria-label="Saved guidance archive"
    >
      <button
        type="button"
        className="secondary"
        aria-expanded={open}
        onClick={() => {
          ++epoch.current;
          setBusy(false);
          setOpen((value) => !value);
        }}
      >
        {open ? "Hide saved guidance" : "View saved guidance"}
      </button>
      {open && (
        <>
          <h4>Guidance captured with this plan</h4>
          <p>
            This view reads the guide text saved with an exact plan revision.
            Viewing another revision leaves your current draft and learning
            progress unchanged.
          </p>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          {!history ? (
            <p role="status">Loading saved revisions…</p>
          ) : (
            <label>
              Saved revision
              <select
                value={choice}
                onChange={(event) => setChoice(event.target.value)}
              >
                {!history.items.some(
                  (item) => item.revision_id === currentRevision,
                ) && (
                  <option value={currentRevision}>
                    Current saved revision
                  </option>
                )}
                {history.items.map((item) => (
                  <option key={item.revision_id} value={item.revision_id}>
                    Revision {item.revision_number} · {when(item.saved_at)} ·{" "}
                    {item.title}
                    {item.revision_id === currentRevision ? " (current)" : ""}
                  </option>
                ))}
              </select>
            </label>
          )}
          {history?.next_cursor && (
            <button
              type="button"
              className="secondary"
              disabled={busy}
              onClick={() => void more()}
            >
              {busy ? "Loading…" : "Load older revisions"}
            </button>
          )}
          {!guidance && !error && <p role="status">Loading saved guidance…</p>}
          {guidance && (
            <>
              <p className="ai-notice">
                {guidance.status === "COMPLETE"
                  ? "All three guides were archived for this revision."
                  : guidance.status === "PARTIAL"
                    ? "Only some guides were archived for this revision. Each unavailable guide is identified below."
                    : "No guidance archive exists for this revision. Older guide text cannot be reconstructed from today’s guide."}
              </p>
              {guidance.captured_at && (
                <p>Captured {when(guidance.captured_at)}.</p>
              )}
              <details>
                <summary>
                  Learning and adoption guide ·{" "}
                  {guidance.catalog.content_version || "edition unavailable"}
                </summary>
                {guidance.catalog.status === "UNAVAILABLE" ? (
                  <p>This guide was not archived for this revision.</p>
                ) : (
                  <>
                    <p>
                      {guidance.catalog.payload.provenance.source_concept}.{" "}
                      {guidance.catalog.payload.provenance.note}
                    </p>
                    {guidance.catalog.payload.journey.map((item) => (
                      <article key={item.id}>
                        <h5>{item.title}</h5>
                        <p>{item.purpose}</p>
                        <p>
                          <strong>Human owner:</strong> {item.human_owner}
                        </p>
                      </article>
                    ))}
                    {guidance.catalog.payload.use_cases.map((item) => (
                      <article key={item.id}>
                        <h5>{item.title}</h5>
                        <p>{item.description}</p>
                        <p>
                          <strong>Data requirement:</strong>{" "}
                          {item.data_requirement}. <strong>Sensitivity:</strong>{" "}
                          {item.sensitivity}. <strong>Use:</strong> {item.kind}.
                        </p>
                        <p>
                          Applicable sectors: {item.sectors.join(", ")}. Guide
                          status: {item.content_status}.
                        </p>
                        <Items values={item.prerequisites} />
                        <Items values={item.acceptance_checks} />
                        <Items values={item.human_approval_needs} />
                      </article>
                    ))}
                    {guidance.catalog.payload.learning_paths.map((path) => (
                      <article key={path.id}>
                        <h5>{path.title}</h5>
                        <Items values={path.steps} />
                        {path.lessons?.map((lesson) => (
                          <details key={lesson.key}>
                            <summary>{lesson.title}</summary>
                            <p>{lesson.lesson}</p>
                            <p>
                              <strong>Exercise:</strong> {lesson.exercise}
                            </p>
                            <p>{lesson.check.question}</p>
                            <Items values={lesson.check.options} />
                            <p>
                              <strong>Saved answer:</strong>{" "}
                              {lesson.check.options[lesson.check.answer]}.{" "}
                              {lesson.check.explanation}
                            </p>
                          </details>
                        ))}
                      </article>
                    ))}
                    <p>
                      <strong>Marketplace:</strong>{" "}
                      {guidance.catalog.payload.marketplace_status.status}.{" "}
                      {guidance.catalog.payload.marketplace_status.explanation}
                    </p>
                    {guidance.catalog.payload.procurement_criteria.map(
                      (item) => (
                        <article key={item.id}>
                          <h5>{item.title}</h5>
                          <Items values={item.questions} />
                        </article>
                      ),
                    )}
                  </>
                )}
              </details>
              <details>
                <summary>
                  Tool directory ·{" "}
                  {guidance.solutions.content_version || "edition unavailable"}
                </summary>
                {guidance.solutions.status === "UNAVAILABLE" ? (
                  <p>This directory was not archived for this revision.</p>
                ) : (
                  <>
                    <p>{guidance.solutions.payload.explanation}</p>
                    <p>
                      Directory checked on{" "}
                      {guidance.solutions.payload.checked_on}. Confirm today’s
                      terms directly with the supplier.
                    </p>
                    {guidance.solutions.payload.comparison_criteria.map(
                      (item) => (
                        <article key={item.id}>
                          <h5>{item.label}</h5>
                          <p>{item.prompt}</p>
                        </article>
                      ),
                    )}
                    {guidance.solutions.payload.solutions.map((item) => (
                      <article key={item.id}>
                        <h5>
                          {item.name} · {item.provider}
                        </h5>
                        <p>{item.description}</p>
                        <p>
                          Category: {item.category.replaceAll("_", " ")}.
                          Deployment: {item.deployment}. API availability:{" "}
                          {item.api_available}.
                        </p>
                        <p>{item.commercial_model}</p>
                        <p>{item.nonprofit_offer}</p>
                        <Items values={item.verification_notes} />
                        <Items values={item.data_review_questions} />
                        <ul>
                          {item.source_urls
                            .filter((source) =>
                              source.url.startsWith("https://"),
                            )
                            .map((source, index) => (
                              <li key={index}>
                                <a
                                  href={source.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                >
                                  {source.label} ↗
                                </a>
                              </li>
                            ))}
                        </ul>
                      </article>
                    ))}
                  </>
                )}
              </details>
              <details>
                <summary>
                  Manual practice guide ·{" "}
                  {guidance.practice.content_version || "edition unavailable"}
                </summary>
                {guidance.practice.status === "UNAVAILABLE" ? (
                  <p>
                    The original practice guide was not archived for this
                    revision. The saved worksheet remains in the plan.
                  </p>
                ) : (
                  <>
                    <p>{guidance.practice.payload.disclaimer}</p>
                    {guidance.practice.payload.templates.map((item) => (
                      <article key={item.id}>
                        <h5>{item.title}</h5>
                        <p>{item.purpose}</p>
                        <Items values={item.input_guidance} />
                        <p>
                          <strong>Example brief:</strong> {item.example_brief}
                        </p>
                        <h6>Allowed inputs</h6>
                        <Items values={item.allowed_inputs} />
                        <h6>Prompt framework</h6>
                        <Items values={item.prompt_framework} />
                        <h6>Excluded inputs</h6>
                        <Items values={item.prohibited_inputs} />
                        <h6>Review checklist</h6>
                        <Items
                          values={item.review_steps.map((step) => step.label)}
                        />
                      </article>
                    ))}
                  </>
                )}
              </details>
              <p className="muted">{guidance.disclaimer}</p>
              {guidance.snapshot_sha256 && (
                <details>
                  <summary>Archive integrity reference</summary>
                  <code className="ai-archive-hash">
                    {guidance.snapshot_sha256}
                  </code>
                </details>
              )}
            </>
          )}
        </>
      )}
    </section>
  );
}
