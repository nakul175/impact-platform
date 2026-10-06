import React, { useEffect, useId, useRef, useState } from "react";
import { AIPracticeStarter } from "./AIPracticeStarter";

export type TaskPractice = {
  template_id: string;
  brief: string;
  draft: string;
  review_notes: string;
  checked_steps: string[];
};
type TaskTemplate = {
  id: string;
  title: string;
  purpose: string;
  input_guidance: string[];
  example_brief: string;
  allowed_inputs: string[];
  prohibited_inputs: string[];
  prompt_framework: string[];
  review_steps: { id: string; label: string }[];
};
type TemplateGuide = {
  content_version: string;
  templates: TaskTemplate[];
  disclaimer: string;
};
type Props = {
  base: string;
  contextKey: string;
  mutationBlocked?: boolean;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
  value: TaskPractice | null;
  onChange: (value: TaskPractice | null) => void;
  canManage: boolean;
  persistenceNotice?: string;
  sourceVersion?: string | null;
  onUnavailableChange?: (unavailable: boolean) => void;
};
const blank = (templateId: string): TaskPractice => ({
  template_id: templateId,
  brief: "",
  draft: "",
  review_notes: "",
  checked_steps: [],
});
function Items({ items }: { items: string[] }) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

export function AITaskPractice({
  base,
  contextKey,
  mutationBlocked = false,
  request,
  explain,
  value,
  onChange,
  canManage,
  persistenceNotice,
  sourceVersion,
  onUnavailableChange,
}: Props) {
  const id = useId();
  const [guide, setGuide] = useState<{
    base: string;
    data: TemplateGuide;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  const [preview, setPreview] = useState("");
  const [replacement, setReplacement] = useState("");
  const epoch = useRef(0);
  const currentGuide = guide?.base === base ? guide.data : null;

  useEffect(() => {
    const current = ++epoch.current;
    const controller = new AbortController();
    setGuide(null);
    setLoading(true);
    setError("");
    setPreview("");
    setReplacement("");
    request(base + "ai-enablement/task-templates", {
      signal: controller.signal,
    })
      .then((result: TemplateGuide) => {
        if (current === epoch.current) setGuide({ base, data: result });
      })
      .catch((reason) => {
        if (current === epoch.current && !controller.signal.aborted)
          setError(explain(reason));
      })
      .finally(() => {
        if (current === epoch.current) setLoading(false);
      });
    return () => {
      epoch.current += 1;
      controller.abort();
    };
  }, [base, retry]);

  useEffect(() => {
    setPreview("");
    setReplacement("");
  }, [value?.template_id]);

  const savedTemplate = currentGuide?.templates.find(
    (item) => item.id === value?.template_id,
  );
  const unavailable = Boolean(currentGuide && value && !savedTemplate);
  useEffect(() => {
    if (currentGuide || value === null) onUnavailableChange?.(unavailable);
  }, [currentGuide, value, unavailable, onUnavailableChange]);

  const selectedId = preview || value?.template_id;
  const template = unavailable
    ? undefined
    : currentGuide?.templates.find((item) => item.id === selectedId) ||
      currentGuide?.templates[0];
  const worksheet =
    template && value?.template_id === template.id
      ? value
      : template
        ? blank(template.id)
        : null;

  function update(field: "brief" | "draft" | "review_notes", text: string) {
    if (!canManage || !worksheet) return;
    onChange({
      ...worksheet,
      [field]: text,
      checked_steps: [],
    });
  }

  const edition =
    sourceVersion && currentGuide
      ? sourceVersion === currentGuide.content_version
        ? "Current"
        : "Stale"
      : "Unknown";

  return (
    <section aria-labelledby={id + "-title"}>
      <h3 id={id + "-title"}>Practise a useful task</h3>
      <p>
        Study a guided exercise and write your own draft using invented facts or
        permitted non-sensitive public text. This worksheet makes no AI request.
      </p>
      {loading && <p role="status">Loading task practice guidance…</p>}
      {error && (
        <div>
          <p role="alert" className="error">
            {error}
          </p>
          <button
            type="button"
            className="secondary"
            onClick={() => setRetry((previous) => previous + 1)}
          >
            Retry loading task guidance
          </button>
        </div>
      )}
      {currentGuide && value && (
        <div role="status" className="ai-notice">
          <p>
            Saved practice edition: {edition}
            {sourceVersion
              ? " · " + sourceVersion
              : " · no saved edition recorded"}
            .
          </p>
          {edition !== "Current" && (
            <p>
              Current guidance is edition {currentGuide.content_version}. Choose
              View saved guidance to check whether this revision’s original
              wording was retained. This worksheet uses current guidance; review
              your saved draft and self-checks before continuing.
            </p>
          )}
        </div>
      )}
      {currentGuide && unavailable && value && (
        <div>
          <p role="alert" className="ai-notice">
            Saved practice task “{value.template_id}” is unavailable in the
            current guide. Your entered text is preserved below. Choose a
            replacement deliberately or clear the worksheet before saving this
            plan.
          </p>
          <fieldset>
            <legend>Preserved worksheet · unavailable practice task</legend>
            {(
              [
                ["brief", "Your synthetic or public-text brief"],
                ["draft", "Your manually written draft"],
                ["review_notes", "Human review notes and unresolved questions"],
              ] as const
            ).map(([field, label]) => (
              <label key={field}>
                {label}
                <textarea rows={4} readOnly value={value[field]} />
              </label>
            ))}
            <h4>Saved self-check identifiers</h4>
            {value.checked_steps.length ? (
              <Items items={value.checked_steps} />
            ) : (
              <p>No self-checks were recorded.</p>
            )}
            <p className="muted">
              These identifiers are preserved as recorded. Choose View saved
              guidance to check for any retained original wording. They do not
              certify competence.
            </p>
          </fieldset>
          {canManage ? (
            <fieldset>
              <legend>Resolve the unavailable practice task</legend>
              <label>
                Replacement practice task
                <select
                  value={replacement}
                  onChange={(event) => setReplacement(event.target.value)}
                >
                  <option value="">Choose a current task</option>
                  {currentGuide.templates.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.title}
                    </option>
                  ))}
                </select>
              </label>
              <p className="muted">
                Replacement keeps your brief, draft and review notes, and resets
                all self-checks for a fresh review. Clearing removes this
                worksheet from the plan draft.
              </p>
              <div className="ai-actions">
                <button
                  type="button"
                  className="secondary"
                  disabled={!replacement}
                  onClick={() => {
                    if (
                      !currentGuide.templates.some(
                        (item) => item.id === replacement,
                      )
                    )
                      return;
                    onChange({
                      ...value,
                      template_id: replacement,
                      checked_steps: [],
                    });
                  }}
                >
                  Replace missing task and keep text
                </button>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => onChange(null)}
                >
                  Clear saved practice worksheet
                </button>
              </div>
            </fieldset>
          ) : (
            <p className="muted">
              A colleague with adoption-plan management permission can resolve
              this unavailable task. You cannot replace or clear the shared
              worksheet.
            </p>
          )}
        </div>
      )}
      {currentGuide && template && worksheet && (
        <>
          <p className="ai-notice">{currentGuide.disclaimer}</p>
          <label>
            Practice task
            <select
              value={template.id}
              onChange={(event) => {
                const nextId = event.target.value;
                setPreview(nextId);
                if (canManage)
                  onChange({
                    ...(value || blank(nextId)),
                    template_id: nextId,
                    checked_steps: [],
                  });
              }}
            >
              {currentGuide.templates.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.title}
                </option>
              ))}
            </select>
          </label>
          <h4>{template.title}</h4>
          <p>{template.purpose}</p>
          <details>
            <summary>Brief guidance and input boundaries</summary>
            <h5>How to prepare the brief</h5>
            <Items items={template.input_guidance} />
            <h5>Allowed material</h5>
            <Items items={template.allowed_inputs} />
            <h5>Do not include</h5>
            <Items items={template.prohibited_inputs} />
          </details>
          <details>
            <summary>Read a synthetic example brief</summary>
            <p>{template.example_brief}</p>
          </details>
          <details>
            <summary>Study the bounded prompt framework</summary>
            <ol>
              {template.prompt_framework.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
            <p className="muted">
              This is learning guidance. Studying it does not consent to sending
              any information to a provider.
            </p>
          </details>
          <AIPracticeStarter
            context={contextKey}
            guide={currentGuide}
            templateId={template.id}
            value={value}
            canManage={canManage}
            mutationBlocked={mutationBlocked}
            onChange={onChange}
          />
          {!canManage && (
            <p className="muted">
              You can study every exercise. Editing a shared worksheet requires
              permission to manage adoption plans.
            </p>
          )}
          <fieldset disabled={!canManage}>
            <legend>Manual practice worksheet · draft for human review</legend>
            <p className="muted" id={id + "-saving"}>
              {persistenceNotice ??
                "Changes are saved only when you save the adoption plan."}{" "}
              Updating the brief, draft or review notes resets your self-checks.
            </p>
            {(
              [
                ["brief", "Your synthetic or public-text brief"],
                ["draft", "Your manually written draft"],
                ["review_notes", "Human review notes and unresolved questions"],
              ] as const
            ).map(([field, label]) => (
              <label key={field}>
                {label}
                <textarea
                  rows={4}
                  maxLength={2500}
                  aria-describedby={id + "-saving"}
                  value={worksheet[field]}
                  onChange={(event) => update(field, event.target.value)}
                />
                <small>{worksheet[field].length} / 2500 characters</small>
              </label>
            ))}
            <fieldset>
              <legend>Self-checks · these do not certify competence</legend>
              {template.review_steps.map((step) => (
                <label className="ai-checkbox" key={step.id}>
                  <input
                    type="checkbox"
                    checked={worksheet.checked_steps.includes(step.id)}
                    onChange={(event) => {
                      if (!canManage) return;
                      onChange({
                        ...worksheet,
                        checked_steps: event.target.checked
                          ? [...worksheet.checked_steps, step.id]
                          : worksheet.checked_steps.filter(
                              (checked) => checked !== step.id,
                            ),
                      });
                    }}
                  />
                  {step.label}
                </label>
              ))}
            </fieldset>
          </fieldset>
          <p className="muted">
            Task guidance edition {currentGuide.content_version}. No
            certificate, publication, supplier message or purchase is created
            here.
          </p>
        </>
      )}
    </section>
  );
}
