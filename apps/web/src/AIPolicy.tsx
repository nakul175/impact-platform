import React, { useRef, useState } from "react";

// FR-AI-001: the tenant AI policy. AI runs only when the server switch, the organisation's policy
// in force and the use case are all on. Hidden controls are never security: the server checks
// every rule before any reservation or provider call.
export type UseCasePolicy = {
  use_case: string;
  enabled: boolean;
  data_classes: string[];
  destinations: string[];
  purposes: string[];
  languages: string[];
  review_mode: string;
  budget_units: number;
  tools: string[];
};
export type AIPolicyView = {
  policy_version: number;
  policy_version_id: string | null;
  created_at: string | null;
  created_by: string | null;
  use_cases: UseCasePolicy[];
  server_enabled: boolean;
  advisory_available: boolean;
  destinations: { id: string; provider: string; region: string }[];
  reserved_use_cases: string[];
};
type Revision = Omit<
  AIPolicyView,
  | "server_enabled"
  | "advisory_available"
  | "destinations"
  | "reserved_use_cases"
>;
type Requester = (path: string, options?: RequestInit) => Promise<any>;
type DialogType = React.ComponentType<{
  title: string;
  close: () => void;
  children: React.ReactNode;
}>;

const DATA_CLASSES = ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"];
const USE_CASE_NAMES: Record<string, string> = {
  ADVISORY_DRAFT: "AI advisory drafts",
  EXTRACTION: "extraction",
  REPORT_DRAFT: "report drafting",
  CHAT: "chat",
  INDICATOR_DESIGN: "indicator design",
  IMPORT_CLEANING: "import mapping and cleaning",
  EVIDENCE_QUESTION: "evidence questions",
  NUMERIC_ANALYSIS: "governed numerical analysis",
  QUALITATIVE_ASSISTANCE: "qualitative assistance",
  PROACTIVE_FINDINGS: "proactive finding suggestions",
};
const USE_CASES = Object.keys(USE_CASE_NAMES);
const REVIEW_NAMES: Record<string, string> = {
  HUMAN_REVIEW: "Human review before use",
};
const lower = (value: string) => value.replaceAll("_", " ").toLowerCase();
const list = (items: string[], empty = "None") =>
  items.length ? items.join(", ") : empty;
export const advisoryRule = (policy: AIPolicyView | null) =>
  policy?.use_cases.find((rule) => rule.use_case === "ADVISORY_DRAFT") || null;
const blankRule = (useCase = "ADVISORY_DRAFT"): UseCasePolicy => ({
  use_case: useCase,
  enabled: false,
  data_classes: [],
  destinations: [],
  purposes: [],
  languages: [],
  review_mode: "HUMAN_REVIEW",
  budget_units: 0,
  tools: [],
});
// Allowed data classes are a ceiling (PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED).
function ceilingText(classes: string[]) {
  const highest = [...DATA_CLASSES]
    .reverse()
    .find((item) => classes.includes(item));
  return highest ? "Up to " + lower(highest) + " data" : "None";
}
function when(value: string | null) {
  if (!value) return "";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export function AIPolicyInForce({
  base,
  policy,
  loadError,
  canManage,
  request,
  explain,
  Dialog,
  onChanged,
}: {
  base: string;
  policy: AIPolicyView | null;
  loadError: string;
  canManage: boolean;
  request: Requester;
  explain: (e: unknown) => string;
  Dialog: DialogType;
  onChanged: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [history, setHistory] = useState<Revision[] | null>(null);
  const [historyError, setHistoryError] = useState("");
  const [historyLoading, setHistoryLoading] = useState(false);
  // The outcome of the last change: a saved version (status) or a refusal (alert).
  const [saved, setSaved] = useState("");
  const [notice, setNotice] = useState("");
  async function loadHistory() {
    setHistoryError("");
    setHistoryLoading(true);
    try {
      const page = await request(
        base + "ai-enablement/policy/revisions?limit=20",
      );
      setHistory(page.items);
    } catch (e) {
      setHistoryError(explain(e));
    } finally {
      setHistoryLoading(false);
    }
  }
  return (
    <section
      className="ai-policy-card"
      aria-labelledby="ai-policy-in-force"
      data-policy-version={policy?.policy_version ?? ""}
    >
      <h4 id="ai-policy-in-force">Policy in force</h4>
      {!policy && !loadError && (
        <p role="status">Loading your organisation&apos;s AI policy…</p>
      )}
      {loadError && (
        <>
          <div className="error" role="alert">
            The AI policy could not be loaded. {loadError}
          </div>
          <p className="ai-policy-warning" role="status">
            AI requests stay off until the policy can be read.
          </p>
        </>
      )}
      {notice && (
        <div className="error" role="alert">
          {notice}
        </div>
      )}
      {saved && <p role="status">{saved}</p>}
      {policy && (
        <>
          <p>
            {policy.policy_version === 0
              ? "No AI policy has been set. Every AI use stays off until an organisation administrator enables one."
              : "Version " +
                policy.policy_version +
                (policy.created_at
                  ? ", in force since " + when(policy.created_at)
                  : "") +
                "."}
          </p>
          {USE_CASES.map((useCase) => {
            const active = policy.use_cases.find(
              (item) => item.use_case === useCase,
            );
            return (
              <dl className="ai-policy-terms" key={useCase}>
                <dt>{USE_CASE_NAMES[useCase]}</dt>
                <dd>{active?.enabled ? "On" : "Off"}</dd>
                {active?.enabled && (
                  <>
                    <dt>Data allowed</dt>
                    <dd>{ceilingText(active.data_classes)}</dd>
                    <dt>Destinations</dt>
                    <dd>
                      {list(
                        active.destinations.map((id) => {
                          const known = policy.destinations.find(
                            (item) => item.id === id,
                          );
                          return known
                            ? known.provider + " (" + known.region + ")"
                            : id;
                        }),
                      )}
                    </dd>
                    <dt>Approved purposes</dt>
                    <dd>{list(active.purposes)}</dd>
                    <dt>Languages</dt>
                    <dd>{list(active.languages)}</dd>
                    <dt>Review</dt>
                    <dd>
                      {REVIEW_NAMES[active.review_mode] ||
                        lower(active.review_mode)}
                    </dd>
                    <dt>Budget units</dt>
                    <dd>{active.budget_units}</dd>
                    <dt>Tools</dt>
                    <dd>{list(active.tools)}</dd>
                  </>
                )}
              </dl>
            );
          })}
          <p className="muted">
            {policy.server_enabled
              ? "The platform's AI service is switched on for this deployment."
              : "The platform's AI service is switched off for this deployment, so no AI request is sent whatever this policy says."}{" "}
            Every use case and tool is separately controlled. Enabling chat does
            not enable extraction, report drafting, advisory drafts, or any
            tool.
          </p>
          {canManage && (
            <button
              type="button"
              className="secondary"
              onClick={() => setEditing(true)}
            >
              Change AI policy
            </button>
          )}
          {policy.policy_version > 0 && (
            <details
              onToggle={(event) => {
                if ((event.target as HTMLDetailsElement).open)
                  void loadHistory();
              }}
            >
              <summary>Policy history</summary>
              {historyLoading && <p role="status">Loading policy history…</p>}
              {historyError && (
                <div className="error" role="alert">
                  {historyError}
                </div>
              )}
              {history && (
                <ol className="ai-policy-history">
                  {history.map((item) => {
                    const advisory = item.use_cases.find(
                      (entry) => entry.use_case === "ADVISORY_DRAFT",
                    );
                    return (
                      <li key={item.policy_version_id || item.policy_version}>
                        Version {item.policy_version}
                        {item.created_at ? " · " + when(item.created_at) : ""}
                        {" · AI advisory drafts "}
                        {advisory?.enabled ? "on" : "off"}
                      </li>
                    );
                  })}
                </ol>
              )}
            </details>
          )}
        </>
      )}
      {editing && policy && (
        <AIPolicyEditor
          base={base}
          policy={policy}
          request={request}
          explain={explain}
          Dialog={Dialog}
          close={() => setEditing(false)}
          saved={(version) => {
            setEditing(false);
            setHistory(null);
            setNotice("");
            setSaved("AI policy version " + version + " saved.");
            onChanged();
          }}
          stale={(message) => {
            // Saved against an older version: show the refusal and reload the policy in force.
            setEditing(false);
            setHistory(null);
            setSaved("");
            setNotice(message);
            onChanged();
          }}
        />
      )}
    </section>
  );
}

function AIPolicyEditor({
  base,
  policy,
  request,
  explain,
  Dialog,
  close,
  saved,
  stale,
}: {
  base: string;
  policy: AIPolicyView;
  request: Requester;
  explain: (e: unknown) => string;
  Dialog: DialogType;
  close: () => void;
  saved: (version: number) => void;
  stale: (message: string) => void;
}) {
  const [selectedUseCase, setSelectedUseCase] = useState("ADVISORY_DRAFT");
  const [drafts, setDrafts] = useState<UseCasePolicy[]>(
    USE_CASES.map(
      (useCase) =>
        policy.use_cases.find((item) => item.use_case === useCase) ||
        blankRule(useCase),
    ),
  );
  const [purposeText, setPurposeText] = useState<Record<string, string>>(
    Object.fromEntries(
      USE_CASES.map((useCase) => [
        useCase,
        (
          policy.use_cases.find((item) => item.use_case === useCase) ||
          blankRule(useCase)
        ).purposes.join("\n"),
      ]),
    ),
  );
  const [languageText, setLanguageText] = useState<Record<string, string>>(
    Object.fromEntries(
      USE_CASES.map((useCase) => [
        useCase,
        (
          policy.use_cases.find((item) => item.use_case === useCase) ||
          blankRule(useCase)
        ).languages.join(", "),
      ]),
    ),
  );
  const [toolText, setToolText] = useState<Record<string, string>>(
    Object.fromEntries(
      USE_CASES.map((useCase) => [
        useCase,
        (
          policy.use_cases.find((item) => item.use_case === useCase) ||
          blankRule(useCase)
        ).tools.join(", "),
      ]),
    ),
  );
  const current =
    drafts.find((item) => item.use_case === selectedUseCase) ||
    blankRule(selectedUseCase);
  const reserved = policy.reserved_use_cases.includes(selectedUseCase);
  const update = (change: Partial<UseCasePolicy>) =>
    setDrafts((items) =>
      items.map((item) =>
        item.use_case === selectedUseCase ? { ...item, ...change } : item,
      ),
    );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  // One operation identifier for the life of this dialog, renewed only when the payload changes,
  // so a retry after a lost response repeats the exact command (the server returns its receipt).
  const attempt = useRef<{ payload: string; id: string } | null>(null);
  const toggle = (
    values: string[],
    set: (next: string[]) => void,
    value: string,
    checked: boolean,
  ) =>
    set(
      checked
        ? [...values, value]
        : values.filter((existing) => existing !== value),
    );
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const normalizedDrafts = drafts.map((draft) => ({
      ...draft,
      purposes: purposeText[draft.use_case]
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean),
      languages: languageText[draft.use_case]
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      tools: toolText[draft.use_case]
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
    }));
    const payload = JSON.stringify({
      expected_version: policy.policy_version,
      data: { use_cases: normalizedDrafts },
    });
    if (!attempt.current || attempt.current.payload !== payload)
      attempt.current = { payload, id: crypto.randomUUID() };
    setBusy(true);
    setError("");
    try {
      const receipt = await request(base + "ai-enablement/policy", {
        method: "PUT",
        body: JSON.stringify({
          operation_id: attempt.current.id,
          expected_version: policy.policy_version,
          data: { use_cases: normalizedDrafts },
        }),
      });
      saved(receipt.policy_version);
    } catch (e) {
      if ((e as { reason?: string }).reason === "AI_POLICY_CHANGED")
        stale(explain(e));
      else setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <Dialog title="Change AI policy" close={close}>
      <form onSubmit={submit} className="ai-policy-editor">
        <p className="muted">
          Saving creates policy version {policy.policy_version + 1}; earlier
          versions are kept unchanged. This change requires a sign-in with
          multi-factor authentication within the last five minutes and is
          recorded in the audit log.
        </p>
        {error && (
          <div className="error" role="alert">
            {error}
          </div>
        )}
        <fieldset disabled={busy}>
          <legend>Named AI use case</legend>
          <label>
            Use case
            <select
              value={selectedUseCase}
              onChange={(e) => setSelectedUseCase(e.target.value)}
            >
              {USE_CASES.map((useCase) => (
                <option key={useCase} value={useCase}>
                  {USE_CASE_NAMES[useCase]}
                </option>
              ))}
            </select>
          </label>
          <label className="ai-checkbox">
            <input
              type="checkbox"
              checked={current.enabled}
              disabled={reserved}
              onChange={(e) => update({ enabled: e.target.checked })}
            />
            Allow {USE_CASE_NAMES[selectedUseCase]}
          </label>
          {reserved && (
            <p className="muted">
              Reserved for a later reviewed activation. Its policy remains
              disabled in this candidate.
            </p>
          )}
          <fieldset>
            <legend>Data classes that may be sent</legend>
            <p className="muted">
              The highest class you tick is the ceiling: data at or below it may
              be sent. Advisory drafts need at least internal data.
            </p>
            {DATA_CLASSES.map((item) => (
              <label key={item} className="ai-checkbox">
                <input
                  type="checkbox"
                  checked={current.data_classes.includes(item)}
                  onChange={(e) =>
                    toggle(
                      current.data_classes,
                      (next) => update({ data_classes: next }),
                      item,
                      e.target.checked,
                    )
                  }
                />
                {lower(item)}
              </label>
            ))}
          </fieldset>
          <fieldset>
            <legend>Destinations</legend>
            {policy.destinations.map((item) => (
              <label key={item.id} className="ai-checkbox">
                <input
                  type="checkbox"
                  checked={current.destinations.includes(item.id)}
                  onChange={(e) =>
                    toggle(
                      current.destinations,
                      (next) => update({ destinations: next }),
                      item.id,
                      e.target.checked,
                    )
                  }
                />
                {item.provider} ({item.region})
              </label>
            ))}
          </fieldset>
          <label>
            Approved purposes (one per line)
            <textarea
              rows={3}
              maxLength={2100}
              value={purposeText[selectedUseCase]}
              onChange={(e) =>
                setPurposeText((values) => ({
                  ...values,
                  [selectedUseCase]: e.target.value,
                }))
              }
            />
          </label>
          <label>
            Languages (BCP 47 tags, separated by commas)
            <input
              value={languageText[selectedUseCase]}
              maxLength={400}
              onChange={(e) =>
                setLanguageText((values) => ({
                  ...values,
                  [selectedUseCase]: e.target.value,
                }))
              }
            />
          </label>
          <label>
            Review mode
            <select
              value={current.review_mode}
              onChange={(e) => update({ review_mode: e.target.value })}
            >
              {Object.entries(REVIEW_NAMES).map(([value, name]) => (
                <option key={value} value={value}>
                  {name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Budget units
            <input
              type="number"
              min="0"
              max="1000000"
              step="1"
              required
              value={String(current.budget_units)}
              onChange={(e) => update({ budget_units: Number(e.target.value) })}
            />
          </label>
          <label>
            Permitted tools (reviewed identifiers, separated by commas)
            <input
              value={toolText[selectedUseCase]}
              maxLength={1300}
              placeholder="No tools enabled"
              onChange={(e) =>
                setToolText((values) => ({
                  ...values,
                  [selectedUseCase]: e.target.value,
                }))
              }
            />
          </label>
          <p className="muted">
            Use-case permission does not enable a tool. Each tool must be listed
            explicitly and is checked again before execution.
          </p>
          <div className="dialog-actions">
            <button type="button" className="secondary" onClick={close}>
              Cancel
            </button>
            <button type="submit" className="primary">
              {busy ? "Saving…" : "Save AI policy"}
            </button>
          </div>
        </fieldset>
      </form>
    </Dialog>
  );
}
