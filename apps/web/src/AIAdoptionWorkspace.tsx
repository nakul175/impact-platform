import React, { useEffect, useRef, useState } from "react";
import type { Catalog, Profile } from "./AIEnablement";

type Solution = {
  id: string;
  name: string;
  provider: string;
  category: string;
  use_case_ids: string[];
  description: string;
  deployment: string;
  commercial_model: string;
  nonprofit_offer: string;
  api_available: string;
  source_urls: { label: string; url: string }[];
  verification_notes: string[];
  data_review_questions: string[];
};
type Solutions = {
  content_version: string;
  checked_on: string;
  explanation: string;
  solutions: Solution[];
  comparison_criteria: { id: string; label: string; prompt: string }[];
};
type PlanDraft = {
  title: string;
  solution_ids: string[];
  learning_completed: string[];
  procurement: {
    requirements: string;
    data_boundary: string;
    budget_notes: string;
    vendor_questions: string;
  };
  pilot: { success_measure: string; completed_actions: string[] };
};
type PlanData = PlanDraft & { profile: Profile };
type Plan = {
  object_id: string;
  revision_id: string;
  business_state: string;
  data: PlanData & {
    content_versions?: { catalog: string; solutions: string };
  };
};
type Props = {
  base: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
  capabilities: string[];
  profile: Profile;
  catalog: Catalog;
  onLoadProfile: (value: Profile) => void;
  Dialog: React.ComponentType<{
    title: string;
    close: () => void;
    children: React.ReactNode;
  }>;
};
const blankDraft = (): PlanDraft => ({
  title: "",
  solution_ids: [],
  learning_completed: [],
  procurement: {
    requirements: "",
    data_boundary: "",
    budget_notes: "",
    vendor_questions: "",
  },
  pilot: { success_measure: "", completed_actions: [] },
});
const pilotActions = [
  ["DEFINE_GOAL", "Define the goal and a measurable success criterion"],
  ["SYNTHETIC_TRIAL", "Test with synthetic or approved non-sensitive material"],
  ["HUMAN_REVIEW", "Have a person review accuracy, fairness and usefulness"],
  ["TRAIN_STAFF", "Train the colleagues who will use and review the tool"],
  ["REVIEW_OUTCOME", "Review the outcome and decide whether to continue"],
];
const tabs = [
  ["tools", "Find and compare tools"],
  ["learning", "Build team capacity"],
  ["procurement", "Procurement brief"],
  ["pilot", "Pilot tracker"],
] as const;
const categoryLabel = (value: string) =>
  value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/^./, (character) => character.toUpperCase());
function extractDraft(data: PlanData): PlanDraft {
  return {
    title: data.title,
    solution_ids: [...data.solution_ids],
    learning_completed: [...data.learning_completed],
    procurement: { ...data.procurement },
    pilot: {
      ...data.pilot,
      completed_actions: [...data.pilot.completed_actions],
    },
  };
}
function Sources({ solution }: { solution: Solution }) {
  return (
    <ul className="ai-sources">
      {solution.source_urls
        .filter((source) => source.url.startsWith("https://"))
        .map((source) => (
          <li key={source.url}>
            <a href={source.url} target="_blank" rel="noopener noreferrer">
              {source.label} ↗
            </a>
          </li>
        ))}
    </ul>
  );
}
function Lesson({
  lesson,
}: {
  lesson: NonNullable<Catalog["learning_paths"][number]["lessons"]>[number];
}) {
  const [answer, setAnswer] = useState<number | null>(null);
  return (
    <details className="ai-lesson">
      <summary>Lesson: {lesson.title}</summary>
      <p>{lesson.lesson}</p>
      <p>
        <strong>Try it:</strong> {lesson.exercise}
      </p>
      <fieldset>
        <legend>{lesson.check.question}</legend>
        {lesson.check.options.map((option, index) => (
          <label className="ai-checkbox" key={index}>
            <input
              type="radio"
              name={"lesson-" + lesson.key}
              checked={answer === index}
              onChange={() => setAnswer(index)}
            />
            {option}
          </label>
        ))}
      </fieldset>
      {answer !== null && (
        <p role="status" className="ai-notice">
          {answer === lesson.check.answer ? "Correct. " : "Try again. "}
          {lesson.check.explanation}
        </p>
      )}
    </details>
  );
}

export function AIAdoptionWorkspace({
  base,
  request,
  explain,
  capabilities,
  profile,
  catalog,
  onLoadProfile,
  Dialog,
}: Props) {
  const canManage = capabilities.includes("ai.enablement.manage");
  const [solutions, setSolutions] = useState<Solutions | null>(null);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [draft, setDraft] = useState<PlanDraft>(blankDraft);
  const [head, setHead] = useState<{
    object_id: string;
    revision_id: string;
  } | null>(null);
  const [savedSnapshot, setSavedSnapshot] = useState("");
  const [planChoice, setPlanChoice] = useState("");
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number][0]>("tools");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [hasPendingSave, setHasPendingSave] = useState(false);
  const [discard, setDiscard] = useState<"open" | "new" | null>(null);
  const epoch = useRef(0);
  const busyRef = useRef(false);
  const pending = useRef<{
    path: string;
    body: string;
    data: PlanData;
    selectedId: string | null;
  } | null>(null);
  const abort = useRef<AbortController | null>(null);
  const latestData = useRef("");
  const data: PlanData = { ...draft, profile };
  const serializedData = JSON.stringify(data);
  latestData.current = serializedData;
  const dirty = savedSnapshot
    ? savedSnapshot !== serializedData
    : draft.title !== "" ||
      draft.solution_ids.length > 0 ||
      draft.learning_completed.length > 0 ||
      Object.values(draft.procurement).some(Boolean) ||
      !!draft.pilot.success_measure ||
      draft.pilot.completed_actions.length > 0;
  const selected = draft.solution_ids
    .map((id) => solutions?.solutions.find((solution) => solution.id === id))
    .filter((value): value is Solution => !!value);

  useEffect(() => {
    const current = ++epoch.current;
    abort.current?.abort();
    const controller = new AbortController();
    abort.current = controller;
    pending.current = null;
    busyRef.current = false;
    setHasPendingSave(false);
    setDiscard(null);
    setBusy(false);
    setSolutions(null);
    setPlans([]);
    setNextCursor(null);
    setDraft(blankDraft());
    setHead(null);
    setSavedSnapshot("");
    setPlanChoice("");
    setError("");
    setNotice("");
    setLoading(true);
    Promise.allSettled([
      request(base + "ai-enablement/solutions", { signal: controller.signal }),
      request(base + "ai-enablement/plans?limit=50", {
        signal: controller.signal,
      }),
    ]).then(([solutionResult, planResult]) => {
      if (current !== epoch.current) return;
      if (solutionResult.status === "fulfilled")
        setSolutions(solutionResult.value);
      else setError(explain(solutionResult.reason));
      if (planResult.status === "fulfilled") {
        setPlans(planResult.value.items);
        setNextCursor(planResult.value.next_cursor || null);
      } else setError(explain(planResult.reason));
      setLoading(false);
    });
    return () => {
      ++epoch.current;
      controller.abort();
    };
  }, [base]);

  function edit(fn: (previous: PlanDraft) => PlanDraft) {
    setDraft(fn);
    setNotice("");
  }
  function toggleSolution(id: string) {
    if (!draft.solution_ids.includes(id) && draft.solution_ids.length >= 4) {
      setNotice("Choose up to four tools. Remove one before adding another.");
      return;
    }
    edit((previous) => ({
      ...previous,
      solution_ids: previous.solution_ids.includes(id)
        ? previous.solution_ids.filter((value) => value !== id)
        : [...previous.solution_ids, id],
    }));
  }
  async function loadPlan(confirmed = false) {
    if (!planChoice || busyRef.current || pending.current) return;
    if (dirty && !confirmed) {
      setDiscard("open");
      return;
    }
    const current = epoch.current;
    const beforeLoad = latestData.current;
    busyRef.current = true;
    setBusy(true);
    setError("");
    try {
      const plan: Plan = await request(
        base + "ai-enablement/plans/" + planChoice,
        { signal: abort.current?.signal },
      );
      if (current !== epoch.current) return;
      const nextDraft = extractDraft(plan.data);
      if (beforeLoad !== latestData.current) {
        setNotice(
          "Your brief or draft changed while the saved plan was opening. Your edits remain here; open it again when ready.",
        );
        return;
      }
      setDraft(nextDraft);
      onLoadProfile(plan.data.profile);
      setHead({ object_id: plan.object_id, revision_id: plan.revision_id });
      setSavedSnapshot(
        JSON.stringify({ ...nextDraft, profile: plan.data.profile }),
      );
      setNotice(
        "Saved plan opened. These are shared draft records for your organisation.",
      );
    } catch (e) {
      if (current === epoch.current) setError(explain(e));
    } finally {
      if (current === epoch.current) {
        busyRef.current = false;
        setBusy(false);
      }
    }
  }
  function newPlan(confirmed = false) {
    if (busyRef.current || pending.current) return;
    if (dirty && !confirmed) {
      setDiscard("new");
      return;
    }
    setDraft(blankDraft());
    setHead(null);
    setSavedSnapshot("");
    setPlanChoice("");
    setError("");
    setNotice(
      "New draft. Complete the organisation brief above before saving.",
    );
  }
  async function savePlan(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canManage || busyRef.current) return;
    if (!pending.current) {
      if (
        !profile.goal.trim() ||
        !Number.isInteger(profile.team_size) ||
        profile.team_size < 1 ||
        profile.team_size > 100000
      ) {
        setError(
          "Complete a valid organisation goal and team size in the brief above before saving.",
        );
        return;
      }
      const capturedData = JSON.parse(serializedData) as PlanData;
      pending.current = {
        path: base + "ai-enablement/plans" + (head ? "/" + head.object_id : ""),
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          ...(head ? { expected_revision: head.revision_id } : {}),
          data: capturedData,
        }),
        data: capturedData,
        selectedId: head?.object_id || null,
      };
      setHasPendingSave(true);
    }
    const captured = pending.current;
    const current = epoch.current;
    busyRef.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const receipt = await request(captured.path, {
        method: captured.selectedId ? "PUT" : "POST",
        body: captured.body,
        signal: abort.current?.signal,
      });
      if (current !== epoch.current) return;
      setHead({
        object_id: receipt.object_id,
        revision_id: receipt.revision_id,
      });
      setPlanChoice(receipt.object_id);
      setSavedSnapshot(JSON.stringify(captured.data));
      pending.current = null;
      setHasPendingSave(false);
      setNotice("Plan saved. Any edits made while saving remain unsaved.");
      setPlans((previous) => {
        const item: Plan = {
          object_id: receipt.object_id,
          revision_id: receipt.revision_id,
          business_state: receipt.business_state,
          data: captured.data,
        };
        return [
          item,
          ...previous.filter((plan) => plan.object_id !== item.object_id),
        ];
      });
    } catch (e) {
      if (current !== epoch.current) return;
      const failure = e as { code?: string; reason?: string };
      if (
        ["CONFLICT", "CONFLICT_VERSION"].includes(failure.code || "") ||
        failure.reason?.includes("STALE") ||
        failure.reason?.includes("REVISION")
      ) {
        pending.current = null;
        setHasPendingSave(false);
        setError(
          "This plan changed since you opened it. Your edits remain here. Open the saved plan to review the latest revision; saving has not overwritten it.",
        );
      } else {
        if (
          failure.code &&
          !["SERVICE_UNAVAILABLE", "INTERNAL_ERROR"].includes(failure.code)
        ) {
          pending.current = null;
          setHasPendingSave(false);
          setError(explain(e));
          return;
        }
        setError(explain(e));
        setNotice(
          "Retry the previous save to resolve its outcome. Newer edits will remain in this view until you save them afterward.",
        );
      }
    } finally {
      if (current === epoch.current) {
        busyRef.current = false;
        setBusy(false);
      }
    }
  }
  async function morePlans() {
    if (!nextCursor || busyRef.current || pending.current) return;
    const current = epoch.current;
    busyRef.current = true;
    setBusy(true);
    try {
      const result = await request(
        base +
          "ai-enablement/plans?limit=50&cursor=" +
          encodeURIComponent(nextCursor),
        { signal: abort.current?.signal },
      );
      if (current !== epoch.current) return;
      setPlans((previous) => [
        ...previous,
        ...result.items.filter(
          (item: Plan) =>
            !previous.some((plan) => plan.object_id === item.object_id),
        ),
      ]);
      setNextCursor(result.next_cursor || null);
    } catch (e) {
      if (current === epoch.current) setError(explain(e));
    } finally {
      if (current === epoch.current) {
        busyRef.current = false;
        setBusy(false);
      }
    }
  }
  function fillProcurement() {
    const supplierNames =
      selected.map((solution) => solution.name).join(", ") ||
      "a supplier to be selected";
    edit((previous) => ({
      ...previous,
      procurement: {
        requirements: (
          "Pilot goal: " +
          profile.goal +
          "\nTeam: " +
          profile.team_size +
          " people.\nShortlist: " +
          supplierNames +
          ".\nRequire human review of every output and a documented exit/export process."
        ).slice(0, 2000),
        data_boundary: profile.sensitive_data
          ? "The intended work involves sensitive information. Begin with synthetic material only. An authorised data steward must approve a specific data boundary, access controls, retention and supplier processing terms before any real data is used."
          : "Use synthetic or approved non-sensitive material in the pilot. Do not send participant identities, confidential records or credentials. Confirm retention, deletion and permissions before wider use.",
        budget_notes:
          "Request the total cost of the bounded pilot, including seats, API usage, onboarding, support, taxes and exit costs. Confirm any nonprofit eligibility and renewal conditions directly with the supplier.",
        vendor_questions: [
          ...catalog.procurement_criteria.flatMap(
            (criterion) => criterion.questions,
          ),
          ...selected.flatMap((solution) => solution.data_review_questions),
        ]
          .join("\n")
          .slice(0, 2000),
      },
    }));
  }
  const filtered =
    solutions?.solutions.filter(
      (solution) =>
        (!category || solution.category === category) &&
        [
          solution.name,
          solution.provider,
          solution.description,
          categoryLabel(solution.category),
        ]
          .join(" ")
          .toLowerCase()
          .includes(search.toLowerCase()),
    ) || [];
  return (
    <section className="ai-adoption" aria-labelledby="ai-adoption-tool">
      <header className="ai-section-title">
        <div>
          <h3 id="ai-adoption-tool">Your AI adoption plan</h3>
          <p>
            Compare real tools, practise skills and keep a shared draft of your
            next pilot.
          </p>
        </div>
        <span className="badge">Draft for human review</span>
      </header>
      <div className="ai-plan-bar">
        <label>
          Saved adoption plans
          <select
            aria-label="Saved adoption plans"
            value={planChoice}
            onChange={(event) => setPlanChoice(event.target.value)}
            disabled={busy || hasPendingSave}
          >
            <option value="">Choose a saved plan</option>
            {plans.map((plan) => (
              <option key={plan.object_id} value={plan.object_id}>
                {plan.data.title}
              </option>
            ))}
          </select>
        </label>
        <div className="ai-actions">
          <button
            type="button"
            className="secondary"
            onClick={() => void loadPlan()}
            disabled={!planChoice || busy || hasPendingSave}
          >
            Open saved plan
          </button>
          {canManage && (
            <button
              type="button"
              className="secondary"
              onClick={() => newPlan()}
              disabled={busy || hasPendingSave}
            >
              New adoption plan
            </button>
          )}
          {nextCursor && (
            <button
              type="button"
              className="secondary"
              onClick={() => void morePlans()}
              disabled={busy || hasPendingSave}
            >
              Load more plans
            </button>
          )}
        </div>
      </div>
      <p className="muted">
        Saved plans are visible to authorised staff in this organisation. Keep
        every field at organisation level; do not include beneficiary or
        personal data.
      </p>
      {!canManage && (
        <p className="ai-notice">
          You can browse tools and read saved plans. Saving an adoption plan
          requires separate permission from your organisation administrator.
        </p>
      )}
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {notice && (
        <p role="status" className="ai-notice">
          {notice}
        </p>
      )}
      {loading && (
        <p role="status">Loading the tool directory and saved plans…</p>
      )}
      <form
        onSubmit={(event) => void savePlan(event)}
        className="ai-plan-form"
        noValidate={hasPendingSave}
      >
        <div className="ai-plan-name">
          <label>
            Plan name
            <input
              aria-label="Plan name"
              value={draft.title}
              onChange={(event) =>
                edit((previous) => ({ ...previous, title: event.target.value }))
              }
              maxLength={150}
              required
              disabled={!canManage}
              placeholder="For example: programme communication pilot"
            />
          </label>
          {canManage && (
            <button
              className="primary"
              type="submit"
              disabled={busy || loading}
            >
              {busy
                ? "Saving or opening…"
                : hasPendingSave
                  ? "Retry previous save"
                  : head
                    ? "Save plan changes"
                    : "Save adoption plan"}
            </button>
          )}
        </div>
        <p className="muted" aria-live="polite">
          {head
            ? dirty
              ? "Unsaved changes to this shared draft."
              : "This shared draft is saved."
            : "New draft — save to share with your organisation."}
        </p>
      </form>
      <nav className="ai-tabs" aria-label="Adoption plan sections">
        {tabs.map(([id, title]) => (
          <button
            key={id}
            type="button"
            aria-current={activeTab === id ? "page" : undefined}
            className={activeTab === id ? "primary" : "secondary"}
            onClick={() => setActiveTab(id)}
          >
            {title}
          </button>
        ))}
      </nav>
      {activeTab === "tools" && (
        <section aria-labelledby="ai-solutions">
          <h4 id="ai-solutions">Find and compare tools</h4>
          {solutions && (
            <>
              <p>{solutions.explanation}</p>
              <p className="muted">
                Source review date: {solutions.checked_on}. Product terms can
                change; verify directly before a decision. This directory does
                not accept orders or book suppliers.
              </p>
              <div className="form-grid">
                <label>
                  Search tools
                  <input
                    aria-label="Search tools"
                    type="search"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search by tool, provider or purpose"
                  />
                </label>
                <label>
                  Tool category
                  <select
                    aria-label="Tool category"
                    value={category}
                    onChange={(event) => setCategory(event.target.value)}
                  >
                    <option value="">All categories</option>
                    {[
                      ...new Set(
                        solutions.solutions.map(
                          (solution) => solution.category,
                        ),
                      ),
                    ].map((value) => (
                      <option key={value} value={value}>
                        {categoryLabel(value)}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              <p aria-live="polite">
                {filtered.length} tools shown · {draft.solution_ids.length} of 4
                selected for comparison.
              </p>
              <div className="ai-cards">
                {filtered.map((solution) => (
                  <article key={solution.id}>
                    <div className="ai-section-title">
                      <h5>{solution.name}</h5>
                      <span className="badge">
                        {categoryLabel(solution.category)}
                      </span>
                    </div>
                    <p className="muted">{solution.provider}</p>
                    <p>{solution.description}</p>
                    <button
                      type="button"
                      className="secondary"
                      aria-pressed={draft.solution_ids.includes(solution.id)}
                      onClick={() => toggleSolution(solution.id)}
                    >
                      {draft.solution_ids.includes(solution.id)
                        ? "Remove "
                        : "Compare "}
                      {solution.name}
                    </button>
                    <Sources solution={solution} />
                    <details>
                      <summary>What to verify before a pilot</summary>
                      <ul>
                        {solution.verification_notes.map((note, index) => (
                          <li key={index}>{note}</li>
                        ))}
                      </ul>
                      <ul>
                        {solution.data_review_questions.map(
                          (question, index) => (
                            <li key={index}>{question}</li>
                          ),
                        )}
                      </ul>
                    </details>
                  </article>
                ))}
              </div>
              {!filtered.length && (
                <p>
                  No tools match this search. Try another purpose or category.
                </p>
              )}
            </>
          )}
          {draft.solution_ids.length > 0 && (
            <section aria-labelledby="ai-tool-comparison">
              <h4 id="ai-tool-comparison">Your tool comparison</h4>
              <p className="muted">
                Attributes from published sources, with unknowns stated
                explicitly. This is a shortlist for investigation, without a
                supplier ranking.
              </p>
              {draft.solution_ids
                .filter(
                  (id) => !selected.some((solution) => solution.id === id),
                )
                .map((id) => (
                  <p key={id}>
                    A saved tool ({id}) is absent from the current directory.{" "}
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => toggleSolution(id)}
                    >
                      Remove unavailable tool
                    </button>
                  </p>
                ))}
              {selected.length > 0 && (
                <div
                  className="ai-comparison-scroll"
                  tabIndex={0}
                  aria-label="Tool comparison table"
                >
                  <table
                    className="ai-comparison"
                    style={{ minWidth: 150 + 240 * selected.length }}
                  >
                    <thead>
                      <tr>
                        <th scope="col">Compare</th>
                        {selected.map((solution) => (
                          <th scope="col" key={solution.id}>
                            {solution.name}
                            <button
                              className="secondary"
                              type="button"
                              onClick={() => toggleSolution(solution.id)}
                              aria-label={
                                "Remove " + solution.name + " from comparison"
                              }
                            >
                              Remove
                            </button>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(
                        [
                          ["Provider", "provider"],
                          ["Category", "category"],
                          ["Deployment", "deployment"],
                          ["Commercial model", "commercial_model"],
                          ["Nonprofit offer", "nonprofit_offer"],
                          ["API availability", "api_available"],
                        ] as const
                      ).map(([title, key]) => (
                        <tr key={key}>
                          <th scope="row">{title}</th>
                          {selected.map((solution) => (
                            <td key={solution.id}>
                              {key === "category"
                                ? categoryLabel(solution.category)
                                : solution[key]}
                            </td>
                          ))}
                        </tr>
                      ))}
                      <tr>
                        <th scope="row">Published sources</th>
                        {selected.map((solution) => (
                          <td key={solution.id}>
                            <Sources solution={solution} />
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <th scope="row">Data questions</th>
                        {selected.map((solution) => (
                          <td key={solution.id}>
                            <ul>
                              {solution.data_review_questions.map(
                                (question, index) => (
                                  <li key={index}>{question}</li>
                                ),
                              )}
                            </ul>
                          </td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}
        </section>
      )}
      {activeTab === "learning" && (
        <section aria-labelledby="ai-learning">
          <h4 id="ai-learning">Build team capacity</h4>
          <p>
            Practise these lessons with synthetic examples. Completion is
            self-recorded team progress, not a qualification or certification.
          </p>
          <div className="ai-cards">
            {catalog.learning_paths.map((path) => (
              <article key={path.id}>
                <h5>{path.title}</h5>
                {path.steps.map((step, index) => {
                  const key = path.id + ":" + index;
                  const lesson = path.lessons?.find(
                    (value) => value.key === key,
                  );
                  return (
                    <div className="ai-learning-step" key={key}>
                      <label className="ai-checkbox">
                        <input
                          type="checkbox"
                          aria-label={"Complete learning step " + key}
                          checked={draft.learning_completed.includes(key)}
                          disabled={!canManage}
                          onChange={() =>
                            edit((previous) => ({
                              ...previous,
                              learning_completed:
                                previous.learning_completed.includes(key)
                                  ? previous.learning_completed.filter(
                                      (value) => value !== key,
                                    )
                                  : [...previous.learning_completed, key],
                            }))
                          }
                        />
                        {step}
                      </label>
                      {lesson && <Lesson lesson={lesson} />}
                    </div>
                  );
                })}
              </article>
            ))}
          </div>
          <p className="muted">
            {draft.learning_completed.length} learning steps recorded complete.
            Save your plan to keep this progress.
          </p>
        </section>
      )}
      {activeTab === "procurement" && (
        <section aria-labelledby="ai-procurement">
          <h4 id="ai-procurement">Procurement brief</h4>
          <p>
            Use the same questions for every supplier. Ask for evidence and
            compare the total pilot cost before committing.
          </p>
          {canManage && (
            <button
              type="button"
              className="secondary"
              onClick={fillProcurement}
              disabled={!profile.goal.trim()}
            >
              Fill draft from brief and shortlist
            </button>
          )}
          <p className="muted">
            Review and edit the draft with your data steward and purchasing
            owner. It does not place an order.
          </p>
          <fieldset disabled={!canManage}>
            <legend>Your requirements</legend>
            {(
              [
                ["requirements", "Pilot requirements", 2000],
                ["data_boundary", "Data boundary", 2000],
                ["budget_notes", "Budget and nonprofit offer checks", 500],
                ["vendor_questions", "Questions for suppliers", 2000],
              ] as const
            ).map(([key, title, limit]) => (
              <label key={key}>
                {title}
                <textarea
                  aria-label={title}
                  maxLength={limit}
                  rows={key === "vendor_questions" ? 6 : 4}
                  value={draft.procurement[key]}
                  onChange={(event) =>
                    edit((previous) => ({
                      ...previous,
                      procurement: {
                        ...previous.procurement,
                        [key]: event.target.value,
                      },
                    }))
                  }
                />
              </label>
            ))}
          </fieldset>
          <div className="ai-cards">
            {catalog.procurement_criteria.map((criterion) => (
              <article key={criterion.id}>
                <h5>{criterion.title}</h5>
                <ul>
                  {criterion.questions.map((question, index) => (
                    <li key={index}>{question}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>
      )}
      {activeTab === "pilot" && (
        <section aria-labelledby="ai-pilot-tracker">
          <h4 id="ai-pilot-tracker">Pilot tracker</h4>
          <p>
            Agree a success measure before the trial. A person records these
            actions; checking them does not approve a programme change.
          </p>
          <fieldset disabled={!canManage}>
            <legend>Measure and review your pilot</legend>
            <label>
              Pilot success measure
              <textarea
                aria-label="Pilot success measure"
                maxLength={1000}
                rows={3}
                value={draft.pilot.success_measure}
                onChange={(event) =>
                  edit((previous) => ({
                    ...previous,
                    pilot: {
                      ...previous.pilot,
                      success_measure: event.target.value,
                    },
                  }))
                }
                placeholder="For example: reduce draft preparation time while a reviewer confirms every statement against the source."
              />
            </label>
            {pilotActions.map(([id, title]) => (
              <label className="ai-checkbox" key={id}>
                <input
                  type="checkbox"
                  aria-label={title}
                  checked={draft.pilot.completed_actions.includes(id)}
                  onChange={() =>
                    edit((previous) => ({
                      ...previous,
                      pilot: {
                        ...previous.pilot,
                        completed_actions:
                          previous.pilot.completed_actions.includes(id)
                            ? previous.pilot.completed_actions.filter(
                                (value) => value !== id,
                              )
                            : [...previous.pilot.completed_actions, id],
                      },
                    }))
                  }
                />
                {title}
              </label>
            ))}
          </fieldset>
          <p className="muted">
            {draft.pilot.completed_actions.length} of {pilotActions.length}{" "}
            pilot actions recorded. Save your plan to keep the tracker.
          </p>
        </section>
      )}
      {discard && (
        <Dialog title="Discard unsaved edits?" close={() => setDiscard(null)}>
          <p>
            Your current brief, shortlist and plan edits have not been saved.
            Opening another plan or starting a new one replaces them in this
            view.
          </p>
          <div className="ai-actions">
            <button
              type="button"
              className="secondary"
              onClick={() => setDiscard(null)}
            >
              Keep editing
            </button>
            <button
              type="button"
              className="primary"
              onClick={() => {
                const action = discard;
                setDiscard(null);
                if (action === "open") void loadPlan(true);
                else newPlan(true);
              }}
            >
              {discard === "open"
                ? "Discard edits and open plan"
                : "Discard edits and start new plan"}
            </button>
          </div>
        </Dialog>
      )}
    </section>
  );
}
