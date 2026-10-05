import React, { useEffect, useRef, useState } from "react";
import { AIAdoptionWorkspace } from "./AIAdoptionWorkspace";
import "./ai-enablement.css";

export type Profile = {
  sector: string;
  team_size: number;
  goal: string;
  data_readiness: string;
  ai_experience: string;
  sensitive_data: boolean;
};
type UseCase = {
  id: string;
  title: string;
  description: string;
  prerequisites: string[];
  acceptance_checks: string[];
  human_approval_needs: string[];
};
export type Catalog = {
  content_version: string;
  advisory_available: boolean;
  journey: {
    id: string;
    title: string;
    purpose: string;
    human_owner: string;
  }[];
  use_cases: UseCase[];
  learning_paths: {
    id: string;
    title: string;
    steps: string[];
    lessons?: {
      key: string;
      title: string;
      lesson: string;
      exercise: string;
      check: {
        question: string;
        options: string[];
        answer: number;
        explanation: string;
      };
    }[];
  }[];
  procurement_criteria: { id: string; title: string; questions: string[] }[];
  marketplace_status: { status: string; explanation: string };
};
type Assessment = {
  readiness: { stage: string; reasons: string[] };
  recommendations: {
    use_case_id: string;
    priority: string;
    status: string;
    reasons: string[];
    capacity_gaps: string[];
    human_approval_needs: string[];
  }[];
  capacity_gaps: string[];
  learning_path_ids: string[];
  next_steps: string[];
  human_approval_needs: string[];
  limitations: string[];
};
type Props = {
  base: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
  capabilities: string[];
  Dialog: React.ComponentType<{
    title: string;
    close: () => void;
    children: React.ReactNode;
  }>;
};
const initialProfile: Profile = {
  sector: "GENERAL",
  team_size: 5,
  goal: "",
  data_readiness: "BASIC",
  ai_experience: "NONE",
  sensitive_data: false,
};
const label = (value: string) => value.replaceAll("_", " ").toLowerCase();
function Items({ items }: { items: string[] }) {
  return items.length ? (
    <ul>
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  ) : (
    <p className="muted">None identified from this brief.</p>
  );
}

export function AIEnablementPanel({
  base,
  request,
  explain,
  capabilities,
  Dialog,
}: Props) {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [profile, setProfile] = useState<Profile>(initialProfile);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [advisory, setAdvisory] = useState<{
    text: string;
    model: string;
    disclaimer: string;
  } | null>(null);
  const [busy, setBusy] = useState<"assessment" | "advisory" | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const generation = useRef(0);
  const pendingAdvisory = useRef<string | null>(null);
  const [consent, setConsent] = useState(false);
  const canRead = capabilities.includes("ai.enablement.read");
  const canAdvise = capabilities.includes("ai.advisory.request");
  useEffect(() => {
    let active = true;
    generation.current += 1;
    setCatalog(null);
    setAssessment(null);
    setAdvisory(null);
    setError("");
    setBusy(null);
    setProfile(initialProfile);
    pendingAdvisory.current = null;
    setConsent(false);
    setLoading(canRead);
    if (canRead)
      request(base + "ai-enablement/catalog")
        .then((result) => {
          if (active) setCatalog(result);
        })
        .catch((e) => {
          if (active) setError(explain(e));
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    return () => {
      active = false;
      generation.current += 1;
    };
  }, [base, canRead]);
  const update = <K extends keyof Profile>(key: K, value: Profile[K]) => {
    generation.current += 1;
    setProfile((previous) => ({ ...previous, [key]: value }));
    pendingAdvisory.current = null;
    setConsent(false);
    setAssessment(null);
    setAdvisory(null);
    setError("");
  };
  function loadProfile(value: Profile) {
    generation.current += 1;
    setProfile(value);
    pendingAdvisory.current = null;
    setConsent(false);
    setAssessment(null);
    setAdvisory(null);
    setError("");
    setBusy(null);
  }
  async function send(kind: "assessment" | "advisory") {
    if (
      kind === "advisory" &&
      (!canAdvise || !catalog?.advisory_available || !consent)
    )
      return;
    const currentGeneration = generation.current;
    if (kind === "advisory" && !pendingAdvisory.current) {
      pendingAdvisory.current = JSON.stringify({
        operation_id: crypto.randomUUID(),
        profile,
        consent: true,
      });
    }
    setError("");
    setBusy(kind);
    setAdvisory(null);
    try {
      const result = await request(base + "ai-enablement/" + kind, {
        method: "POST",
        body:
          kind === "advisory"
            ? pendingAdvisory.current!
            : JSON.stringify({ profile }),
      });
      if (currentGeneration !== generation.current) return;
      setAssessment(result.assessment);
      if (kind === "advisory") {
        pendingAdvisory.current = null;
        setAdvisory(result);
      }
    } catch (e) {
      if (currentGeneration === generation.current) setError(explain(e));
    } finally {
      if (currentGeneration === generation.current) setBusy(null);
    }
  }
  if (!canRead)
    return (
      <section className="panel">
        <h2>AI enablement</h2>
        <p>
          Your organisation administrator can grant access to this workspace.
        </p>
      </section>
    );
  return (
    <section
      className="panel ai-enablement"
      aria-label="AI enablement workspace"
    >
      <header className="panel-toolbar">
        <div>
          <h2>AI enablement for nonprofits</h2>
          <p>
            Choose a useful first pilot, build team skills and prepare a fair
            procurement brief.
          </p>
        </div>
        <span className="badge">Development workspace</span>
      </header>
      <div className="ai-content">
        <p className="ai-notice">
          Keep this brief at organisation level. Do not enter names, participant
          records, health details, passwords or other confidential information.
          Plans are drafts for human review; AI never supplies official impact
          results.
        </p>
        {error && (
          <div role="alert" className="error">
            {error}
          </div>
        )}
        {loading && <p role="status">Loading the AI enablement guide…</p>}
        {catalog && (
          <>
            <section aria-labelledby="ai-journey">
              <h3 id="ai-journey">Your adoption journey</h3>
              <div className="ai-cards">
                {catalog.journey.map((step) => (
                  <article key={step.id}>
                    <h4>{step.title}</h4>
                    <p>{step.purpose}</p>
                    <small>Human owner: {step.human_owner}</small>
                  </article>
                ))}
              </div>
            </section>
            <section aria-labelledby="ai-brief">
              <h3 id="ai-brief">Your organisation brief</h3>
              <p className="muted">
                Assess your brief here, then save it in a named adoption plan
                for authorised colleagues in your organisation. Generated
                advisory drafts are stored encrypted for safe retries.
              </p>
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  void send("assessment");
                }}
              >
                <fieldset disabled={busy !== null}>
                  <legend>Readiness and goals</legend>
                  <div className="form-grid">
                    <label>
                      Sector
                      <select
                        aria-label="Sector"
                        value={profile.sector}
                        onChange={(e) => update("sector", e.target.value)}
                      >
                        {[
                          "GENERAL",
                          "EDUCATION",
                          "HEALTH",
                          "LIVELIHOODS",
                          "ENVIRONMENT",
                        ].map((value) => (
                          <option key={value} value={value}>
                            {label(value)}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Team size
                      <input
                        aria-label="Team size"
                        type="number"
                        min="1"
                        max="100000"
                        step="1"
                        required
                        value={profile.team_size}
                        onChange={(e) =>
                          update("team_size", Number(e.target.value))
                        }
                      />
                    </label>
                    <label>
                      Data readiness
                      <select
                        aria-label="Data readiness"
                        value={profile.data_readiness}
                        onChange={(e) =>
                          update("data_readiness", e.target.value)
                        }
                      >
                        {["NONE", "BASIC", "STRUCTURED"].map((value) => (
                          <option key={value} value={value}>
                            {label(value)}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      AI experience
                      <select
                        aria-label="AI experience"
                        value={profile.ai_experience}
                        onChange={(e) =>
                          update("ai_experience", e.target.value)
                        }
                      >
                        {["NONE", "EXPERIMENTING", "REGULAR"].map((value) => (
                          <option key={value} value={value}>
                            {label(value)}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                  <label>
                    What would you like AI to help with?
                    <textarea
                      aria-label="AI goal"
                      required
                      maxLength={1000}
                      rows={3}
                      value={profile.goal}
                      onChange={(e) => update("goal", e.target.value)}
                      placeholder="For example: help our team prepare clearer programme communication."
                    />
                  </label>
                  <label className="ai-checkbox">
                    <input
                      type="checkbox"
                      checked={profile.sensitive_data}
                      onChange={(e) =>
                        update("sensitive_data", e.target.checked)
                      }
                    />
                    Our intended work involves sensitive data (describe no
                    records here).
                  </label>
                  {canAdvise && catalog.advisory_available && (
                    <label className="ai-checkbox">
                      <input
                        type="checkbox"
                        aria-required="true"
                        checked={consent}
                        onChange={(e) => setConsent(e.target.checked)}
                      />
                      I consent to sending this brief to OpenAI
                    </label>
                  )}
                  <div className="ai-actions">
                    <button className="primary" type="submit">
                      Assess readiness
                    </button>
                    {canAdvise && (
                      <button
                        className="secondary"
                        type="button"
                        disabled={!catalog.advisory_available || !consent}
                        onClick={(e) => {
                          const form = e.currentTarget.form;
                          if (form?.reportValidity()) {
                            e.preventDefault();
                            void send("advisory");
                          }
                        }}
                      >
                        Request AI advisory draft
                      </button>
                    )}
                  </div>
                </fieldset>
              </form>
              {canAdvise && !catalog.advisory_available ? (
                <p className="muted">
                  AI advisory is not configured for this workspace. Readiness
                  assessment and learning guidance remain available.
                </p>
              ) : canAdvise ? (
                <p className="muted">
                  Requesting an advisory draft sends this brief to OpenAI and
                  may incur usage charges. Do not include personal or
                  beneficiary data. Review the draft before acting.
                </p>
              ) : (
                <p className="muted">
                  AI advisory requires separate permission from your
                  organisation administrator.
                </p>
              )}
              {busy && (
                <p role="status">
                  {busy === "assessment"
                    ? "Assessing your brief…"
                    : "Preparing an AI advisory draft…"}
                </p>
              )}
            </section>
            {assessment && (
              <section aria-labelledby="ai-assessment" aria-live="polite">
                <h3 id="ai-assessment">
                  Readiness assessment · {label(assessment.readiness.stage)}
                </h3>
                <Items items={assessment.readiness.reasons} />
                <h4>Next steps</h4>
                <Items items={assessment.next_steps} />
                <h4>Capacity gaps</h4>
                <Items items={assessment.capacity_gaps} />
                <div className="ai-cards">
                  {assessment.recommendations.map((recommendation) => (
                    <article key={recommendation.use_case_id}>
                      <h4>
                        {catalog.use_cases.find(
                          (item) => item.id === recommendation.use_case_id,
                        )?.title || recommendation.use_case_id}
                      </h4>
                      <span className="badge">
                        {label(recommendation.status)} ·{" "}
                        {label(String(recommendation.priority))}
                      </span>
                      <Items items={recommendation.reasons} />
                      <h5>People and skills needed</h5>
                      <Items items={recommendation.capacity_gaps} />
                      <h5>Human review</h5>
                      <Items items={recommendation.human_approval_needs} />
                    </article>
                  ))}
                </div>
                <h4>Human approval needs</h4>
                <Items items={assessment.human_approval_needs} />
                <h4>Assessment limitations</h4>
                <Items items={assessment.limitations} />
              </section>
            )}
            {advisory && (
              <section aria-labelledby="ai-advisory">
                <h3 id="ai-advisory">AI advisory draft</h3>
                <p className="ai-notice">{advisory.disclaimer}</p>
                <div className="ai-draft">{advisory.text}</div>
                <p className="muted">
                  Generated with {advisory.model}. No procurement, purchase or
                  programme change has been made.
                </p>
              </section>
            )}
            <AIAdoptionWorkspace
              base={base}
              request={request}
              explain={explain}
              capabilities={capabilities}
              profile={profile}
              catalog={catalog}
              onLoadProfile={loadProfile}
              Dialog={Dialog}
            />
            <section aria-labelledby="ai-use-cases">
              <h3 id="ai-use-cases">Explore potential pilots</h3>
              <p className="muted">
                These are editorial starting points, not validated demand or
                promises of impact.
              </p>
              <div className="ai-cards">
                {catalog.use_cases.map((item) => (
                  <article key={item.id}>
                    <h4>{item.title}</h4>
                    <p>{item.description}</p>
                    <details>
                      <summary>
                        Pilot prerequisites and acceptance checks
                      </summary>
                      <h5>Prerequisites</h5>
                      <Items items={item.prerequisites} />
                      <h5>Acceptance checks</h5>
                      <Items items={item.acceptance_checks} />
                      <h5>Human approval</h5>
                      <Items items={item.human_approval_needs} />
                    </details>
                  </article>
                ))}
              </div>
            </section>
            <p className="muted">Guide edition {catalog.content_version}.</p>
          </>
        )}
      </div>
    </section>
  );
}
