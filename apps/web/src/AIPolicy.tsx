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
};
const REVIEW_NAMES: Record<string, string> = {
  HUMAN_REVIEW: "Human review before use",
};
const lower = (value: string) => value.replaceAll("_", " ").toLowerCase();
const list = (items: string[], empty = "None") =>
  items.length ? items.join(", ") : empty;
export const advisoryRule = (policy: AIPolicyView | null) =>
  policy?.use_cases.find((rule) => rule.use_case === "ADVISORY_DRAFT") || null;
const blankRule = (): UseCasePolicy => ({
  use_case: "ADVISORY_DRAFT",
  enabled: false,
  data_classes: [],
  destinations: [],
  purposes: [],
  languages: [],
  review_mode: "HUMAN_REVIEW",
  budget_units: 0,
  tools: [],
});
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
  const rule = advisoryRule(policy);
  async function loadHistory() {
    setHistoryError("");
    try {
      const page = await request(
        base + "ai-enablement/policy/revisions?limit=20",
      );
      setHistory(page.items);
    } catch (e) {
      setHistoryError(explain(e));
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
        <p className="ai-policy-warning">
          The AI policy could not be loaded, so AI requests stay off.{" "}
          {loadError}
        </p>
      )}
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
          <dl className="ai-policy-terms">
            <dt>AI advisory drafts</dt>
            <dd>{rule?.enabled ? "On" : "Off"}</dd>
            {rule?.enabled && (
              <>
                <dt>Data allowed</dt>
                <dd>{list(rule.data_classes.map(lower))}</dd>
                <dt>Destinations</dt>
                <dd>
                  {list(
                    rule.destinations.map((id) => {
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
                <dd>{list(rule.purposes)}</dd>
                <dt>Languages</dt>
                <dd>{list(rule.languages)}</dd>
                <dt>Review</dt>
                <dd>
                  {REVIEW_NAMES[rule.review_mode] || lower(rule.review_mode)}
                </dd>
                <dt>Budget units</dt>
                <dd>{rule.budget_units}</dd>
                <dt>Tools</dt>
                <dd>{list(rule.tools)}</dd>
              </>
            )}
          </dl>
          <p className="muted">
            {policy.server_enabled
              ? "The platform's AI service is switched on for this deployment."
              : "The platform's AI service is switched off for this deployment, so no AI request is sent whatever this policy says."}{" "}
            Reserved for later releases and always off:{" "}
            {list(
              policy.reserved_use_cases.map(
                (item) => USE_CASE_NAMES[item] || lower(item),
              ),
            )}
            .
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
              {historyError && (
                <p className="ai-policy-warning">{historyError}</p>
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
          saved={() => {
            setEditing(false);
            setHistory(null);
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
}: {
  base: string;
  policy: AIPolicyView;
  request: Requester;
  explain: (e: unknown) => string;
  Dialog: DialogType;
  close: () => void;
  saved: () => void;
}) {
  const current = advisoryRule(policy) || blankRule();
  const [enabled, setEnabled] = useState(current.enabled);
  const [dataClasses, setDataClasses] = useState<string[]>(
    current.data_classes,
  );
  const [destinations, setDestinations] = useState<string[]>(
    current.destinations,
  );
  const [purposes, setPurposes] = useState(current.purposes.join("\n"));
  const [languages, setLanguages] = useState(current.languages.join(", "));
  const [budget, setBudget] = useState(String(current.budget_units));
  const [reviewMode, setReviewMode] = useState(current.review_mode);
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
    const rule: UseCasePolicy = {
      use_case: "ADVISORY_DRAFT",
      enabled,
      data_classes: DATA_CLASSES.filter((item) => dataClasses.includes(item)),
      destinations: policy.destinations
        .map((item) => item.id)
        .filter((item) => destinations.includes(item)),
      purposes: purposes
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean),
      languages: languages
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      review_mode: reviewMode,
      budget_units: Number(budget),
      tools: [],
    };
    const payload = JSON.stringify({
      expected_version: policy.policy_version,
      data: { use_cases: [rule] },
    });
    if (!attempt.current || attempt.current.payload !== payload)
      attempt.current = { payload, id: crypto.randomUUID() };
    setBusy(true);
    setError("");
    try {
      await request(base + "ai-enablement/policy", {
        method: "PUT",
        body: JSON.stringify({
          operation_id: attempt.current.id,
          expected_version: policy.policy_version,
          data: { use_cases: [rule] },
        }),
      });
      saved();
    } catch (e) {
      setError(explain(e));
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
          <legend>AI advisory drafts</legend>
          <label className="ai-checkbox">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => setEnabled(e.target.checked)}
            />
            Allow AI advisory drafts
          </label>
          <fieldset>
            <legend>Data classes that may be sent</legend>
            {DATA_CLASSES.map((item) => (
              <label key={item} className="ai-checkbox">
                <input
                  type="checkbox"
                  checked={dataClasses.includes(item)}
                  onChange={(e) =>
                    toggle(dataClasses, setDataClasses, item, e.target.checked)
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
                  checked={destinations.includes(item.id)}
                  onChange={(e) =>
                    toggle(
                      destinations,
                      setDestinations,
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
              value={purposes}
              onChange={(e) => setPurposes(e.target.value)}
            />
          </label>
          <label>
            Languages (BCP 47 tags, separated by commas)
            <input
              value={languages}
              maxLength={400}
              onChange={(e) => setLanguages(e.target.value)}
            />
          </label>
          <label>
            Review mode
            <select
              value={reviewMode}
              onChange={(e) => setReviewMode(e.target.value)}
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
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            />
          </label>
          <p className="muted">
            Tools: none. No AI tool can be enabled in this release.
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
