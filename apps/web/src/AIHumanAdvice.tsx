import { useEffect, useRef, useState, type FormEvent } from "react";

type State =
  | "Open"
  | "Assigned"
  | "AwaitingInput"
  | "AdviceDraft"
  | "Closed"
  | "Cancelled";
type Action =
  | "declare-scope"
  | "assign"
  | "request-input"
  | "respond"
  | "advise"
  | "close"
  | "cancel";
type Receipt = {
  operation_id: string;
  object_id: string;
  revision_id: string;
  business_state: State;
  saved_at: string;
  correlation_id: string;
};
type AdviceAction = {
  action_id: string;
  description: string;
  responsibility: "REQUESTER" | "ADVISER";
};
type Case = {
  object_id: string;
  revision_id: string;
  business_state: State;
  context_current: boolean;
  problem: string | null;
  data: {
    title: string;
    context_plan_id: string;
    context_plan_revision: string;
    requester_principal_id: string;
    adviser_principal_id: string;
    scope: string;
    data_boundary: string;
    desired_outcome: string;
    declaration: null | {
      conflict: "NONE" | "DECLARED";
      details: string;
      scope_accepted: boolean;
      declared_at: string;
    };
    assignment: null | { assigned_at: string; declaration_revision_id: string };
    notes: {
      note_id: string;
      kind: "QUESTION" | "RESPONSE";
      text: string;
      recorded_at: string;
    }[];
    advice: null | {
      text: string;
      actions: AdviceAction[];
      advised_at: string;
    };
    closure: null | {
      closure_reason: string;
      closed_at: string;
      advice_revision_id: string;
    };
    cancellation: null | { reason: string; cancelled_at: string };
  };
};
type Page<T> = { items: T[]; next_cursor: string | null };
type Peer = {
  membership_id: string;
  display_name: string;
};
type History = {
  revision_id: string;
  revision_number: number;
  saved_at: string;
};
type Data = Record<string, unknown>;
type Command = { operation_id: string; expected_revision?: string; data: Data };
type Pending = {
  endpoint: string;
  command: Command;
  label: string;
  objectId?: string;
};

export type AIHumanAdviceProps = {
  base: string;
  planId: string;
  planRevision: string;
  planTitle: string;
  principalId: string;
  canManage: boolean;
  canReadMemberDirectory: boolean;
  hasUnsavedChanges: boolean;
  hasConflictingMutation?: boolean;
  request: (path: string, options?: RequestInit) => Promise<unknown>;
  explain: (error: unknown) => string;
  onSaved?: (receipt: Receipt) => void | Promise<void>;
  onMutationStateChange?: (blocked: boolean) => void;
};
const unavailable =
  "This advice information is unavailable with your current access.";
const stamp = (value: string) => new Date(value).toLocaleString();
const terminal = (value: Case) =>
  ["Closed", "Cancelled"].includes(value.business_state);
function accessFailure(error: unknown) {
  return (
    !!error &&
    typeof error === "object" &&
    "code" in error &&
    [
      "RESOURCE_UNAVAILABLE",
      "AUTH_REQUIRED",
      "ACCESS_DENIED",
      "FORBIDDEN",
      "CAPABILITY_REQUIRED",
      "AUTHORIZATION_FAILED",
    ].includes(String(error.code))
  );
}
const actionLabels: Record<Action, string> = {
  "declare-scope": "Declare conflict and scope",
  assign: "Confirm assignment and private sharing",
  "request-input": "Request further input",
  respond: "Respond to the question",
  advise: "Record advice and accountable actions",
  close: "Acknowledge advice and close",
  cancel: "Cancel this case",
};

function AdviceRecord({ item }: { item: Case }) {
  return (
    <>
      <h5>{item.data.title}</h5>
      <p>
        Case state: <strong>{item.business_state}</strong>.
      </p>
      <div className="ai-cards">
        <article>
          <h5>Invitation scope</h5>
          <p className="ai-draft">{item.data.scope}</p>
        </article>
        <article>
          <h5>Material boundary</h5>
          <p className="ai-draft">{item.data.data_boundary}</p>
        </article>
        <article>
          <h5>Desired outcome</h5>
          <p className="ai-draft">{item.data.desired_outcome}</p>
        </article>
      </div>
      {item.problem !== null ? (
        <>
          <h5>Private problem brief</h5>
          <p className="ai-draft">{item.problem}</p>
        </>
      ) : (
        <p className="ai-notice">
          The private problem brief is withheld until the requester confirms
          assignment and sharing.
        </p>
      )}
      {item.data.declaration && (
        <section aria-label="Adviser's scope declaration">
          <h5>Adviser declaration</h5>
          <p>
            Conflict:{" "}
            {item.data.declaration.conflict === "NONE"
              ? "No conflict declared"
              : "Conflict declared"}
            . Scope{" "}
            {item.data.declaration.scope_accepted ? "accepted" : "not accepted"}
            .
          </p>
          <p className="ai-draft">{item.data.declaration.details}</p>
          <p className="muted">
            Recorded {stamp(item.data.declaration.declared_at)}.
          </p>
        </section>
      )}
      {item.data.assignment && (
        <p className="muted">
          Requester confirmed assignment and private sharing{" "}
          {stamp(item.data.assignment.assigned_at)}.
        </p>
      )}
      {item.data.notes.length > 0 && (
        <section aria-label="Case questions and responses">
          <h5>Questions and responses</h5>
          {item.data.notes.map((note) => (
            <article key={note.note_id}>
              <h5>
                {note.kind === "QUESTION"
                  ? "Adviser question"
                  : "Requester response"}
              </h5>
              <p className="ai-draft">{note.text}</p>
              <p className="muted">Recorded {stamp(note.recorded_at)}.</p>
            </article>
          ))}
        </section>
      )}
      {item.data.advice && (
        <section aria-label="Recorded advice and accountable actions">
          <h5>Recorded advice</h5>
          <p className="ai-draft">{item.data.advice.text}</p>
          <ul>
            {item.data.advice.actions.map((action) => (
              <li key={action.action_id}>
                <strong>
                  {action.responsibility === "REQUESTER"
                    ? "Requester"
                    : "Adviser"}
                  :
                </strong>{" "}
                {action.description}
              </li>
            ))}
          </ul>
          {item.data.advice.actions.length === 0 && (
            <p>No follow-up actions were recorded.</p>
          )}
          <p className="muted">
            Recorded {stamp(item.data.advice.advised_at)}.
          </p>
        </section>
      )}
      {item.data.closure && (
        <p className="ai-notice">
          Requester closed this case {stamp(item.data.closure.closed_at)}:{" "}
          {item.data.closure.closure_reason}
        </p>
      )}
      {item.data.cancellation && (
        <p className="ai-notice">
          Requester cancelled this case{" "}
          {stamp(item.data.cancellation.cancelled_at)}:{" "}
          {item.data.cancellation.reason}
        </p>
      )}
      <p className="ai-notice">
        Internal peer advice is a human recommendation. It is not official
        programme evidence, approval, causal proof or a procurement decision.
      </p>
    </>
  );
}

function ActionForm({
  action,
  item,
  disabled,
  submit,
  cancel,
}: {
  action: Action;
  item: Case;
  disabled: boolean;
  submit: (data: Data) => void;
  cancel: () => void;
}) {
  const [conflict, setConflict] = useState<"" | "NONE" | "DECLARED">("");
  const [scopeAccepted, setScopeAccepted] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [text, setText] = useState("");
  const [checked, setChecked] = useState<string[]>([]);
  const [actions, setActions] = useState<
    {
      key: string;
      description: string;
      responsibility: "REQUESTER" | "ADVISER";
    }[]
  >([]);
  const allAcknowledged =
    !!item.data.advice &&
    checked.length === item.data.advice.actions.length &&
    item.data.advice.actions.every((value) =>
      checked.includes(value.action_id),
    );
  const maximum =
    action === "advise"
      ? 6000
      : action === "respond"
        ? 4000
        : action === "request-input"
          ? 2000
          : 1000;
  function send(event: FormEvent) {
    event.preventDefault();
    if (disabled) return;
    if (action === "declare-scope") {
      if (
        !conflict ||
        !text.trim() ||
        (conflict === "DECLARED" && scopeAccepted)
      )
        return;
      submit({ conflict, details: text, scope_accepted: scopeAccepted });
    } else if (action === "assign") {
      if (!confirmed) return;
      submit({
        declaration_revision_id: item.revision_id,
        sharing_confirmed: true,
      });
    } else if (action === "close") {
      if (!confirmed || !allAcknowledged || !text.trim()) return;
      submit({
        advice_revision_id: item.revision_id,
        acknowledged_action_ids: [...checked],
        closure_reason: text,
      });
    } else if (action === "advise") {
      if (!text.trim() || actions.some((value) => !value.description.trim()))
        return;
      submit({
        advice: text,
        actions: actions.map(({ description, responsibility }) => ({
          description,
          responsibility,
        })),
      });
    } else {
      if (!text.trim()) return;
      submit({
        [action === "cancel"
          ? "reason"
          : action === "respond"
            ? "response"
            : "question"]: text,
      });
    }
  }
  return (
    <form onSubmit={send} aria-label={actionLabels[action]}>
      <fieldset disabled={disabled}>
        <legend>
          {actionLabels[action]} · {item.data.title}
        </legend>
        {action === "declare-scope" && (
          <>
            <label>
              Conflict declaration
              <select
                aria-label="Advice conflict declaration"
                required
                value={conflict}
                onChange={(event) => {
                  setConflict(event.target.value as typeof conflict);
                  setScopeAccepted(false);
                }}
              >
                <option value="">Choose a declaration</option>
                <option value="NONE">I have no conflict to declare</option>
                <option value="DECLARED">I have a conflict to declare</option>
              </select>
            </label>
            <label className="ai-checkbox">
              <input
                type="checkbox"
                checked={scopeAccepted}
                disabled={conflict !== "NONE"}
                onChange={(event) => setScopeAccepted(event.target.checked)}
              />
              I accept the invitation scope and material boundary.
            </label>
            {conflict === "DECLARED" && (
              <p className="ai-notice">
                A declared conflict prevents assignment. The requester can
                cancel and open a new case with another permitted peer.
              </p>
            )}
          </>
        )}
        {action === "assign" && (
          <>
            <p>
              Review the current adviser declaration above. This assignment pins
              that exact declaration and the saved plan revision.
            </p>
            <p>
              The named internal peer will receive the private problem brief. No
              participant or declaration can be replaced after assignment.
            </p>
            <label className="ai-checkbox">
              <input
                type="checkbox"
                required
                checked={confirmed}
                onChange={(event) => setConfirmed(event.target.checked)}
              />
              I confirm the current scope and declaration, and consent to share
              this private brief with the named peer.
            </label>
          </>
        )}
        {action === "close" && (
          <>
            <p>
              Review the exact advice shown above and acknowledge every recorded
              follow-up action. Closing ends the adviser's access to this case
              and its history.
            </p>
            <label className="ai-checkbox">
              <input
                type="checkbox"
                required
                checked={confirmed}
                onChange={(event) => setConfirmed(event.target.checked)}
              />
              I acknowledge the advice in the current saved case revision.
            </label>
            {item.data.advice?.actions.map((value) => (
              <label className="ai-checkbox" key={value.action_id}>
                <input
                  type="checkbox"
                  checked={checked.includes(value.action_id)}
                  onChange={(event) =>
                    setChecked((previous) =>
                      event.target.checked
                        ? [...previous, value.action_id]
                        : previous.filter((id) => id !== value.action_id),
                    )
                  }
                />
                Acknowledge{" "}
                {value.responsibility === "REQUESTER" ? "requester" : "adviser"}{" "}
                action: {value.description}
              </label>
            ))}
          </>
        )}
        {action === "cancel" && (
          <p className="ai-notice">
            Cancellation ends the case and the adviser's access immediately.
            Earlier revisions remain part of the requester's governed case
            history.
          </p>
        )}
        {action !== "assign" && (
          <label>
            {action === "declare-scope"
              ? "Declaration details"
              : action === "request-input"
                ? "Question for the requester"
                : action === "respond"
                  ? "Response to the adviser"
                  : action === "advise"
                    ? "Advice text"
                    : action === "close"
                      ? "Closure reason"
                      : "Cancellation reason"}
            <textarea
              aria-label={`Advice ${action} text`}
              value={text}
              required
              maxLength={maximum}
              onChange={(event) => setText(event.target.value)}
            />
          </label>
        )}
        {action === "advise" && (
          <section aria-label="Advice follow-up actions">
            <h5>Accountable follow-up actions</h5>
            {actions.map((value, index) => (
              <fieldset key={value.key}>
                <legend>Follow-up action {index + 1}</legend>
                <label>
                  Action description
                  <textarea
                    aria-label={`Advice action ${index + 1} description`}
                    required
                    maxLength={1000}
                    value={value.description}
                    onChange={(event) =>
                      setActions((previous) =>
                        previous.map((row) =>
                          row.key === value.key
                            ? { ...row, description: event.target.value }
                            : row,
                        ),
                      )
                    }
                  />
                </label>
                <label>
                  Responsible participant
                  <select
                    aria-label={`Advice action ${index + 1} responsibility`}
                    value={value.responsibility}
                    onChange={(event) =>
                      setActions((previous) =>
                        previous.map((row) =>
                          row.key === value.key
                            ? {
                                ...row,
                                responsibility: event.target.value as
                                  | "REQUESTER"
                                  | "ADVISER",
                              }
                            : row,
                        ),
                      )
                    }
                  >
                    <option value="REQUESTER">Requester</option>
                    <option value="ADVISER">Adviser</option>
                  </select>
                </label>
                <button
                  type="button"
                  className="secondary"
                  onClick={() =>
                    setActions((previous) =>
                      previous.filter((row) => row.key !== value.key),
                    )
                  }
                >
                  Remove follow-up action {index + 1}
                </button>
              </fieldset>
            ))}
            <button
              type="button"
              className="secondary"
              disabled={disabled || actions.length >= 20}
              onClick={() =>
                setActions((previous) => [
                  ...previous,
                  {
                    key: crypto.randomUUID(),
                    description: "",
                    responsibility: "REQUESTER",
                  },
                ])
              }
            >
              Add follow-up action
            </button>
            <p className="muted">
              Record up to 20 actions. The requester must acknowledge the saved
              actions before closing.
            </p>
          </section>
        )}
        <div className="ai-actions">
          <button
            type="submit"
            className="primary"
            disabled={
              disabled ||
              (action === "assign" && !confirmed) ||
              (action === "close" && (!confirmed || !allAcknowledged))
            }
          >
            {actionLabels[action]}
          </button>
          <button
            type="button"
            className="secondary"
            disabled={disabled}
            onClick={cancel}
          >
            Cancel action form
          </button>
        </div>
      </fieldset>
    </form>
  );
}

function InvitationForm({
  peers,
  disabled,
  more,
  submit,
  cancel,
}: {
  peers: Page<Peer>;
  disabled: boolean;
  more: () => void;
  submit: (data: Data) => void;
  cancel: () => void;
}) {
  const [peer, setPeer] = useState("");
  const [title, setTitle] = useState("");
  const [problem, setProblem] = useState("");
  const [scope, setScope] = useState("");
  const [boundary, setBoundary] = useState("");
  const [outcome, setOutcome] = useState("");
  const [consent, setConsent] = useState(false);
  const allowed = peers.items;
  function send(event: FormEvent) {
    event.preventDefault();
    if (
      disabled ||
      !consent ||
      !allowed.some((value) => value.membership_id === peer) ||
      [title, problem, scope, boundary, outcome].some((value) => !value.trim())
    )
      return;
    submit({
      title,
      adviser_membership_id: peer,
      problem,
      scope,
      data_boundary: boundary,
      desired_outcome: outcome,
      material_policy: "SYNTHETIC_OR_PUBLIC_TEXT",
      invitation_consent: true,
    });
  }
  return (
    <form onSubmit={send} aria-label="Create internal peer advice case">
      <fieldset disabled={disabled}>
        <legend>Invite a named internal peer</legend>
        <p>
          The case title, invitation scope, material boundary and desired
          outcome are visible to the named peer in the Open state. The separate
          problem brief remains private until you confirm assignment and
          sharing.
        </p>
        <p>
          Use synthetic or public text only. Do not paste participant data,
          credentials or confidential documents.
        </p>
        <div className="form-grid">
          <label>
            Case title
            <input
              aria-label="Advice case title"
              required
              maxLength={150}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
            />
          </label>
          <label>
            Internal peer
            <select
              aria-label="Advice internal peer"
              required
              value={peer}
              onChange={(event) => {
                setPeer(event.target.value);
                setConsent(false);
              }}
            >
              <option value="">Choose a permitted internal member</option>
              {allowed.map((value) => (
                <option key={value.membership_id} value={value.membership_id}>
                  {value.display_name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Invitation scope
            <textarea
              aria-label="Advice invitation scope"
              required
              maxLength={2000}
              value={scope}
              onChange={(event) => setScope(event.target.value)}
            />
          </label>
          <label>
            Material boundary
            <textarea
              aria-label="Advice material boundary"
              required
              maxLength={2000}
              value={boundary}
              onChange={(event) => setBoundary(event.target.value)}
            />
          </label>
          <label>
            Desired outcome
            <textarea
              aria-label="Advice desired outcome"
              required
              maxLength={2000}
              value={outcome}
              onChange={(event) => setOutcome(event.target.value)}
            />
          </label>
          <label>
            Private problem brief
            <textarea
              aria-label="Advice private problem brief"
              required
              maxLength={4000}
              value={problem}
              onChange={(event) => setProblem(event.target.value)}
            />
          </label>
        </div>
        <p className="muted">
          These names come from a separately authorised lookup of colleagues
          with current access to this saved plan. Current scope and a distinct
          natural person are checked again when the invitation is saved.
          Appearing here does not indicate availability, certification or
          adviser consent.
        </p>
        {allowed.length === 0 && (
          <p>
            No permitted internal member is available on these loaded pages.
          </p>
        )}
        <label className="ai-checkbox">
          <input
            type="checkbox"
            checked={consent}
            required
            onChange={(event) => setConsent(event.target.checked)}
          />
          I consent to show the invitation fields to this named internal peer. I
          understand the private brief requires a later, separate sharing
          confirmation.
        </label>
        <div className="ai-actions">
          {peers.next_cursor && (
            <button type="button" className="secondary" onClick={more}>
              Load more permitted internal members
            </button>
          )}
          <button
            type="submit"
            className="primary"
            disabled={disabled || !peer || !consent}
          >
            Create internal advice invitation
          </button>
          <button
            type="button"
            className="secondary"
            disabled={disabled}
            onClick={cancel}
          >
            Cancel invitation form
          </button>
        </div>
      </fieldset>
    </form>
  );
}

export function AIHumanAdvice({
  base,
  planId,
  planRevision,
  planTitle,
  principalId,
  canManage,
  canReadMemberDirectory,
  hasUnsavedChanges,
  hasConflictingMutation = false,
  request,
  explain,
  onSaved,
  onMutationStateChange,
}: AIHumanAdviceProps) {
  const prefix = base.endsWith("/") ? base : base + "/";
  const route = prefix + "ai-enablement/human-advice";
  const [open, setOpen] = useState(false);
  const [cases, setCases] = useState<Page<Case> | null>(null);
  const [current, setCurrent] = useState<Case | null>(null);
  const [shown, setShown] = useState<Case | null>(null);
  const [history, setHistory] = useState<Page<History> | null>(null);
  const [peers, setPeers] = useState<Page<Peer> | null>(null);
  const [peerUnavailable, setPeerUnavailable] = useState(false);
  const [inviting, setInviting] = useState(false);
  const [action, setAction] = useState<Action | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [pending, setPending] = useState<Pending | null>(null);
  const [tick, setTick] = useState(0);
  const [formEpoch, setFormEpoch] = useState(0);
  const generation = useRef(0);
  const readGeneration = useRef(0);
  const busyRef = useRef(false);
  const previous = useRef<{ key: string; pending: Pending } | null>(null);
  useEffect(() => {
    onMutationStateChange?.(busy || pending !== null);
    return () => onMutationStateChange?.(false);
  }, [busy, pending, onMutationStateChange]);
  const historical =
    !!current && !!shown && current.revision_id !== shown.revision_id;
  const actor =
    current?.data.requester_principal_id === principalId
      ? "REQUESTER"
      : current?.data.adviser_principal_id === principalId
        ? "ADVISER"
        : null;
  const privateChanged = () => {
    ++readGeneration.current;
    setCurrent(null);
    setShown(null);
    setHistory(null);
    setPeers(null);
    setInviting(false);
    setAction(null);
    setFormEpoch((value) => value + 1);
  };
  function fail(cause: unknown) {
    privateChanged();
    setCases(null);
    setError(accessFailure(cause) ? unavailable : explain(cause));
  }
  useEffect(() => {
    ++generation.current;
    privateChanged();
    previous.current = null;
    setCases(null);
    setPending(null);
    setPeerUnavailable(false);
    setBusy(false);
    busyRef.current = false;
    setError("");
    setNotice("");
    return () => {
      ++generation.current;
      ++readGeneration.current;
    };
  }, [prefix, planId, principalId, canManage]);
  useEffect(() => {
    privateChanged();
    setPeerUnavailable(false);
  }, [canReadMemberDirectory]);
  useEffect(() => {
    privateChanged();
    setPeerUnavailable(false);
    setError("");
    setNotice("");
  }, [planRevision]);
  useEffect(() => {
    if (!open) return;
    const controller = new AbortController();
    const epoch = ++readGeneration.current;
    setCases(null);
    setError("");
    (
      request(route + "?limit=50", { signal: controller.signal }) as Promise<
        Page<Case>
      >
    )
      .then((value) => {
        if (!controller.signal.aborted && epoch === readGeneration.current)
          setCases(value);
      })
      .catch((cause) => {
        if (!controller.signal.aborted && epoch === readGeneration.current)
          fail(cause);
      });
    return () => controller.abort();
  }, [
    open,
    route,
    planId,
    planRevision,
    principalId,
    canManage,
    canReadMemberDirectory,
    tick,
  ]);
  async function read<T>(path: string, receive: (value: T) => void) {
    if (busyRef.current || pending) return;
    const epoch = readGeneration.current;
    const identity = generation.current;
    busyRef.current = true;
    setBusy(true);
    setError("");
    try {
      const value = (await request(path)) as T;
      if (identity === generation.current && epoch === readGeneration.current)
        receive(value);
    } catch (cause) {
      if (identity === generation.current && epoch === readGeneration.current) {
        if (path.startsWith(route + "/eligible-peers?") && accessFailure(cause))
          setPeerUnavailable(true);
        fail(cause);
      }
    } finally {
      if (identity === generation.current) {
        busyRef.current = false;
        setBusy(false);
      }
    }
  }
  function select(item: Case) {
    privateChanged();
    setNotice("");
    void read<Case>(route + "/" + item.object_id, (value) => {
      setCurrent(value);
      setShown(value);
    });
  }
  function moreCases() {
    if (!cases?.next_cursor) return;
    void read<Page<Case>>(
      route + "?limit=50&cursor=" + encodeURIComponent(cases.next_cursor),
      (value) =>
        setCases((previous) => ({
          ...value,
          items: [
            ...(previous?.items || []),
            ...value.items.filter(
              (item) =>
                !previous?.items.some(
                  (old) => old.object_id === item.object_id,
                ),
            ),
          ],
        })),
    );
  }
  function invite() {
    if (
      !canManage ||
      !canReadMemberDirectory ||
      peerUnavailable ||
      hasUnsavedChanges ||
      hasConflictingMutation ||
      pending ||
      busyRef.current
    )
      return;
    privateChanged();
    void read<Page<Peer>>(
      route +
        "/eligible-peers?context_plan_id=" +
        encodeURIComponent(planId) +
        "&limit=50",
      (value) => {
        setPeers(value);
        setInviting(true);
      },
    );
  }
  function morePeers() {
    if (!peers?.next_cursor) return;
    void read<Page<Peer>>(
      route +
        "/eligible-peers?context_plan_id=" +
        encodeURIComponent(planId) +
        "&limit=50&cursor=" +
        encodeURIComponent(peers.next_cursor),
      (value) =>
        setPeers((previous) => ({
          ...value,
          items: [
            ...(previous?.items || []),
            ...value.items.filter(
              (item) =>
                !previous?.items.some(
                  (old) => old.membership_id === item.membership_id,
                ),
            ),
          ],
        })),
    );
  }
  function getHistory() {
    if (!current) return;
    setAction(null);
    void read<Page<History>>(
      route + "/" + current.object_id + "/revisions?limit=50",
      setHistory,
    );
  }
  function moreHistory() {
    if (!current || !history?.next_cursor) return;
    void read<Page<History>>(
      route +
        "/" +
        current.object_id +
        "/revisions?limit=50&cursor=" +
        encodeURIComponent(history.next_cursor),
      (value) =>
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
        })),
    );
  }
  async function save(data: Data, commandAction?: Action, exact?: Pending) {
    if (
      !canManage ||
      busyRef.current ||
      hasConflictingMutation ||
      (!exact && pending) ||
      (!exact && historical) ||
      (hasUnsavedChanges && commandAction !== "cancel" && !exact) ||
      (!exact &&
        current &&
        commandAction !== "cancel" &&
        !current.context_current)
    )
      return;
    const endpoint =
      commandAction && current
        ? route + "/" + current.object_id + "/actions/" + commandAction
        : route;
    const key = JSON.stringify([
      endpoint,
      current?.revision_id,
      planId,
      planRevision,
      data,
    ]);
    const value =
      exact ||
      (previous.current?.key === key
        ? previous.current.pending
        : {
            endpoint,
            command: {
              operation_id: crypto.randomUUID(),
              ...(commandAction && current
                ? { expected_revision: current.revision_id }
                : {}),
              data: commandAction
                ? data
                : {
                    ...data,
                    context_plan_id: planId,
                    context_plan_revision: planRevision,
                  },
            },
            label: commandAction
              ? actionLabels[commandAction]
              : "Create internal advice invitation",
            objectId: current?.object_id,
          });
    previous.current = { key, pending: value };
    const identity = generation.current;
    ++readGeneration.current;
    busyRef.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    let receipt: Receipt;
    try {
      receipt = (await request(value.endpoint, {
        method: "POST",
        body: JSON.stringify(value.command),
      })) as Receipt;
    } catch (cause) {
      if (identity === generation.current) {
        fail(cause);
        if (!(cause && typeof cause === "object" && "code" in cause))
          setPending(value);
        busyRef.current = false;
        setBusy(false);
      }
      return;
    }
    if (identity !== generation.current) return;
    previous.current = null;
    setPending(null);
    privateChanged();
    setNotice("The internal advice case change was saved.");
    try {
      await onSaved?.(receipt);
    } catch {
      if (identity === generation.current)
        setNotice(
          "The case change was saved. Reload the case to view its current revision.",
        );
    }
    if (identity !== generation.current) return;
    const epoch = readGeneration.current;
    busyRef.current = true;
    setBusy(true);
    try {
      const [page, item] = await Promise.all([
        request(route + "?limit=50") as Promise<Page<Case>>,
        request(route + "/" + receipt.object_id) as Promise<Case>,
      ]);
      if (identity === generation.current && epoch === readGeneration.current) {
        setCases(page);
        setCurrent(item);
        setShown(item);
      }
    } catch (cause) {
      if (identity === generation.current && epoch === readGeneration.current)
        fail(cause);
    } finally {
      if (identity === generation.current) {
        busyRef.current = false;
        setBusy(false);
      }
    }
  }
  const visibleCases =
    cases?.items.filter((value) => value.data.context_plan_id === planId) || [];
  const permitted: Action[] =
    !current ||
    terminal(current) ||
    !actor ||
    !canManage ||
    historical ||
    hasConflictingMutation
      ? []
      : actor === "REQUESTER"
        ? [
            ...(current.context_current &&
            !hasUnsavedChanges &&
            current.business_state === "Open" &&
            current.data.declaration?.conflict === "NONE" &&
            current.data.declaration.scope_accepted
              ? ["assign" as Action]
              : []),
            ...(current.context_current &&
            !hasUnsavedChanges &&
            current.business_state === "AwaitingInput"
              ? ["respond" as Action]
              : []),
            ...(current.context_current &&
            !hasUnsavedChanges &&
            current.business_state === "AdviceDraft" &&
            current.data.advice
              ? ["close" as Action]
              : []),
            "cancel",
          ]
        : !current.context_current || hasUnsavedChanges
          ? []
          : current.business_state === "Open"
            ? ["declare-scope"]
            : ["Assigned", "AdviceDraft"].includes(current.business_state)
              ? ["request-input", "advise"]
              : [];
  return (
    <section
      className="ai-human-advice ai-guidance-archive"
      aria-label="Internal peer advice for this AI plan"
    >
      <button
        type="button"
        className="secondary"
        aria-expanded={open}
        disabled={busy || pending !== null}
        onClick={() => {
          ++generation.current;
          privateChanged();
          setCases(null);
          setError("");
          setNotice("");
          setOpen((value) => !value);
        }}
      >
        {open ? "Hide internal peer advice" : "View internal peer advice"}
      </button>
      {open && (
        <>
          <h4>Internal peer advice · {planTitle}</h4>
          <p>
            Ask a named member of your organisation for scoped human advice
            anchored to this saved plan. The private problem brief is shared
            only after separate adviser scope acceptance and requester sharing
            confirmation.
          </p>
          <p className="muted">
            This workflow sends no external messages, books no consultation, and
            calls no AI provider.
          </p>
          {error && (
            <p role="alert" className="error">
              {error}
            </p>
          )}
          {notice && (
            <p role="status" className="ai-notice">
              {notice}
            </p>
          )}
          {busy && (
            <p role="status">Checking currently authorised case information…</p>
          )}
          {!cases && !error && !busy && (
            <p role="status">Loading currently authorised cases…</p>
          )}
          {pending && (
            <div role="status" className="ai-notice">
              <p>
                The response was lost. The case change may already be saved.
                Retry the exact same change before starting another action.
              </p>
              <button
                type="button"
                className="secondary"
                disabled={busy || !canManage || hasConflictingMutation}
                onClick={() =>
                  void save(pending.command.data, undefined, pending)
                }
              >
                Retry previous advice change
              </button>
            </div>
          )}
          <div className="ai-actions">
            <button
              type="button"
              className="secondary"
              disabled={busy || pending !== null}
              onClick={() => {
                privateChanged();
                setError("");
                setTick((value) => value + 1);
              }}
            >
              Reload currently authorised advice cases
            </button>
            {canManage && (
              <button
                type="button"
                className="secondary"
                disabled={
                  busy ||
                  pending !== null ||
                  hasUnsavedChanges ||
                  hasConflictingMutation ||
                  !canReadMemberDirectory ||
                  peerUnavailable ||
                  !principalId
                }
                onClick={invite}
              >
                Choose an internal peer and prepare an invitation
              </button>
            )}
          </div>
          {canManage && (!canReadMemberDirectory || peerUnavailable) && (
            <p className="ai-notice">
              Internal peer selection is unavailable with your current access.
              Member-directory authority is separate from AI management
              permission. You can still work on currently authorised cases where
              you are already a participant.
            </p>
          )}
          {hasUnsavedChanges && (
            <p className="ai-notice">
              Save or discard your plan draft changes before creating an
              invitation or changing its consent or advice. An existing
              requester case can still be cancelled.
            </p>
          )}
          {cases && (
            <>
              <p>
                Showing cases for this saved plan from the loaded pages. Loading
                or selecting a case does not save any change.
              </p>
              {visibleCases.length === 0 && (
                <p>
                  No advice cases for this plan are available on these loaded
                  pages.
                </p>
              )}
              <div className="ai-actions">
                {visibleCases.map((value) => (
                  <button
                    type="button"
                    className="secondary"
                    key={value.object_id}
                    disabled={busy || pending !== null}
                    onClick={() => select(value)}
                  >
                    {value.data.title} · {value.business_state}
                  </button>
                ))}
                {cases.next_cursor && (
                  <button
                    type="button"
                    className="secondary"
                    disabled={busy || pending !== null}
                    onClick={moreCases}
                  >
                    Load more available advice cases
                  </button>
                )}
              </div>
            </>
          )}
          {inviting && peers && (
            <InvitationForm
              key={`${planId}:${planRevision}:${formEpoch}`}
              peers={peers}
              disabled={
                busy ||
                pending !== null ||
                hasUnsavedChanges ||
                hasConflictingMutation ||
                !canReadMemberDirectory ||
                !canManage
              }
              more={morePeers}
              submit={(data) => void save(data)}
              cancel={() => {
                setInviting(false);
                setPeers(null);
              }}
            />
          )}
          {shown && (
            <section aria-label="Selected internal advice case">
              {historical && (
                <p className="ai-notice">
                  You are reading a saved historical revision. Case actions
                  require the current revision.
                </p>
              )}
              <AdviceRecord item={shown} />
              {!shown.context_current && (
                <p className="ai-notice">
                  The saved plan has changed since this case was opened. This
                  case is read-only except requester cancellation; open a new
                  case against the current plan for further advice.
                </p>
              )}
              {actor && (
                <p>
                  You are the{" "}
                  {actor === "REQUESTER"
                    ? "requester"
                    : "named internal adviser"}{" "}
                  for this case.
                </p>
              )}
              <div className="ai-actions">
                <button
                  type="button"
                  className="secondary"
                  disabled={busy || pending !== null}
                  onClick={getHistory}
                >
                  View case revision history
                </button>
                {historical && current && (
                  <button
                    type="button"
                    className="secondary"
                    disabled={
                      busy || pending !== null || hasConflictingMutation
                    }
                    onClick={() => select(current)}
                  >
                    Return to current case revision
                  </button>
                )}
                {permitted.map((value) => (
                  <button
                    type="button"
                    className="secondary"
                    key={value}
                    disabled={busy || pending !== null}
                    onClick={() => setAction(value)}
                  >
                    {actionLabels[value]}
                  </button>
                ))}
              </div>
              {history && (
                <section aria-label="Internal advice revision history">
                  <h5>Saved case revisions</h5>
                  <div className="ai-actions">
                    {history.items.map((value) => (
                      <button
                        type="button"
                        className="secondary"
                        key={value.revision_id}
                        disabled={busy || pending !== null}
                        onClick={() => {
                          setAction(null);
                          void read<Case>(
                            route +
                              "/" +
                              shown.object_id +
                              "/revisions/" +
                              value.revision_id,
                            setShown,
                          );
                        }}
                      >
                        Case revision {value.revision_number} ·{" "}
                        {stamp(value.saved_at)}
                      </button>
                    ))}
                    {history.next_cursor && (
                      <button
                        type="button"
                        className="secondary"
                        disabled={busy || pending !== null}
                        onClick={moreHistory}
                      >
                        Load more case revisions
                      </button>
                    )}
                  </div>
                </section>
              )}
              {action &&
                current &&
                !historical &&
                permitted.includes(action) && (
                  <ActionForm
                    key={`${current.object_id}:${current.revision_id}:${action}:${formEpoch}`}
                    action={action}
                    item={current}
                    disabled={busy || pending !== null}
                    submit={(data) => void save(data, action)}
                    cancel={() => setAction(null)}
                  />
                )}
            </section>
          )}
        </>
      )}
    </section>
  );
}
