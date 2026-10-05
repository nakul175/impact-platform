import { useEffect, useRef, useState, type FormEvent } from "react";

type Receipt = {
  operation_id: string;
  object_id: string;
  revision_id: string;
  business_state: string;
  saved_at: string;
  correlation_id: string;
};
type ReferenceInput = {
  programme_id: string;
  indicator_id: string;
  period_id: string;
  interpretation_note: string;
};
type Reference = ReferenceInput & {
  snapshot_id: string | null;
  snapshot_revision: string | null;
  snapshot_version: number | null;
};
type Value = {
  value_state: string;
  displayed_value: string | null;
  numerator: string | null;
  denominator: string | null;
  calculated_at: string | null;
  reason_code: string | null;
};
type Target = {
  value_state: string;
  target_kind: string;
  displayed_value?: string | null;
  displayed_low?: string | null;
  displayed_high?: string | null;
};
type Coverage = {
  source: "CLOSE_SNAPSHOT" | "COLLECTION_PLAN";
  applicability: "APPLICABLE" | "NOT_APPLICABLE" | "UNAVAILABLE";
  approval_percent: string | null;
  expected_count: number | null;
  required_count: number | null;
  received_count?: number | null;
  approved_count?: number | null;
  pending_count?: number | null;
  missing_count?: number | null;
  complete?: boolean;
  reason_code: string | null;
};
type Indicator = {
  indicator_id: string;
  indicator_label?: string;
  unit?: string | null;
  official: Value | null;
  provisional: Value | null;
  target: Target | null;
  baseline: Target | null;
  status: {
    status: string;
    compared_with: "OFFICIAL" | "PROVISIONAL" | null;
    attainment_percent: string | null;
    displayed_deviation?: string | null;
    reason_code: string | null;
  } | null;
  coverage: Coverage;
  freshness: {
    stale: boolean | null;
    stale_reasons: string[];
    source_check: "CHECKED" | "NOT_PERMITTED" | "NO_VALUE";
    checked_at: string;
  };
};
type Evidence = {
  object_id: string;
  revision_id: string;
  status: "LINKED";
  reference: Reference;
  reference_status: Record<string, "CURRENT" | "CHANGED" | "ABSENT">;
  programme_title: string | null;
  period: {
    period_code?: string | null;
    starts_at?: string | null;
    ends_at?: string | null;
    period_state: string;
  };
  indicator: Indicator;
  stale_rule: string;
  disclaimer: string;
};
type Row = {
  object_id: string;
  revision_id: string;
  data: {
    title?: string;
    code?: string;
    starts_at?: string;
    ends_at?: string;
  };
};
type Page<T> = { items: T[]; next_cursor: string | null };
type IndicatorPage = { indicators: Indicator[]; next_cursor: string | null };
type WriteCommand = {
  operation_id: string;
  expected_revision: string;
  data: ReferenceInput | null;
};
export type AIImpactEvidenceProps = {
  base: string;
  path: string;
  objectId: string;
  currentRevision: string;
  canManage: boolean;
  hasUnsavedChanges: boolean;
  request: (path: string, options?: RequestInit) => Promise<unknown>;
  explain: (error: unknown) => string;
  onSaved: (receipt: Receipt) => void | Promise<void>;
  onMutationStateChange?: (blocked: boolean) => void;
};
const words = (value: string | null | undefined) =>
  (value || "Unavailable").replaceAll("_", " ").toLowerCase();
const when = (value: string | null | undefined) =>
  value ? new Date(value).toLocaleString() : "Not supplied";
const unavailable = "No programme evidence is available to show.";
function hidden(error: unknown) {
  return (
    !!error &&
    typeof error === "object" &&
    "code" in error &&
    [
      "RESOURCE_UNAVAILABLE",
      "AUTH_REQUIRED",
      "ACCESS_DENIED",
      "ASSURANCE_REQUIRED",
      "CAPABILITY_REQUIRED",
      "AUTHORIZATION_FAILED",
      "FORBIDDEN",
    ].includes(String(error.code))
  );
}
function Shown({ value, unit }: { value: Value | null; unit?: string | null }) {
  if (!value) return <p>No value is available.</p>;
  return (
    <>
      <p>
        <strong>
          {value.value_state === "PRESENT" && value.displayed_value !== null
            ? value.displayed_value
            : words(value.value_state)}
        </strong>
        {unit ? ` ${unit}` : ""}
      </p>
      {value.reason_code && <p>{words(value.reason_code)}</p>}
      {value.numerator !== null && value.denominator !== null && (
        <p>
          Stored components: {value.numerator} / {value.denominator}.
        </p>
      )}
      <p className="muted">Calculated {when(value.calculated_at)}.</p>
    </>
  );
}
function targetText(value: Target | null) {
  if (!value) return "No approved value";
  if (value.value_state !== "PRESENT") return words(value.value_state);
  return value.target_kind === "RANGE"
    ? `${value.displayed_low ?? "Not supplied"}–${value.displayed_high ?? "Not supplied"}`
    : (value.displayed_value ?? "Not supplied");
}
function GovernedEvidence({ value }: { value: Evidence }) {
  const indicator = value.indicator;
  if (value.status !== "LINKED" || !indicator || !value.reference)
    return <p>{unavailable}</p>;
  const coverage = indicator.coverage;
  const changed = Object.entries(value.reference_status || {})
    .filter(([, state]) => state === "CHANGED")
    .map(([name]) => name);
  return (
    <>
      <h5>{value.programme_title || "Authorised programme"}</h5>
      <p>
        {indicator.indicator_label || "Authorised indicator"}.{" "}
        {value.period?.period_code || "Authorised reporting period"} ·{" "}
        {words(value.period?.period_state)}.
      </p>
      <p>
        Period: {when(value.period?.starts_at)} to {when(value.period?.ends_at)}
        .
      </p>
      {changed.length > 0 && (
        <p className="ai-notice">
          Saved source revisions have changed: {changed.join(", ")}. The
          existing link keeps its original pins. Review the current sources
          before deliberately refreshing.
        </p>
      )}
      <div className="ai-cards">
        <article>
          <h5>Official result · saved locked snapshot</h5>
          {value.reference.snapshot_version === null ? (
            <p>
              No locked snapshot was pinned. A later close does not add an
              official value to this link automatically.
            </p>
          ) : (
            <p>Snapshot edition {value.reference.snapshot_version}.</p>
          )}
          <Shown value={indicator.official} unit={indicator.unit} />
        </article>
        <article>
          <h5>Current provisional result</h5>
          <Shown value={indicator.provisional} unit={indicator.unit} />
          <p className="muted">
            Provisional evidence can change and remains separate from the saved
            official result.
          </p>
        </article>
        <article>
          <h5>Governed comparison status</h5>
          {indicator.status ? (
            <>
              <p>
                {words(indicator.status.status)} · compared with{" "}
                {words(indicator.status.compared_with)}.
              </p>
              {indicator.status.attainment_percent !== null && (
                <p>Attainment: {indicator.status.attainment_percent}%.</p>
              )}
              {indicator.status.displayed_deviation != null && (
                <p>Deviation: {indicator.status.displayed_deviation}.</p>
              )}
              {indicator.status.reason_code && (
                <p>{words(indicator.status.reason_code)}</p>
              )}
            </>
          ) : (
            <p>No comparison status is available.</p>
          )}
          <p>
            Approved target: {targetText(indicator.target)}. Baseline:{" "}
            {targetText(indicator.baseline)}.
          </p>
        </article>
      </div>
      <h5>Source coverage</h5>
      <p>
        {coverage.source === "CLOSE_SNAPSHOT"
          ? "Coverage from the saved close snapshot."
          : "Coverage from the current collection plan."}
      </p>
      {coverage.applicability !== "APPLICABLE" ? (
        <p>
          {coverage.applicability === "NOT_APPLICABLE"
            ? "Not applicable"
            : "Coverage unavailable"}
          {coverage.reason_code ? ` · ${words(coverage.reason_code)}` : ""}.
        </p>
      ) : (
        <>
          <p>
            {coverage.approval_percent === null
              ? "Approval percentage unavailable"
              : `${coverage.approval_percent}% approved`}
            .
          </p>
          <p>
            {coverage.approved_count ?? "Unavailable"} approved of{" "}
            {coverage.required_count ?? "Unavailable"} required;{" "}
            {coverage.expected_count ?? "Unavailable"} expected;{" "}
            {coverage.pending_count ?? "Unavailable"} pending;{" "}
            {coverage.missing_count ?? "Unavailable"} missing.
          </p>
        </>
      )}
      <p>
        Source freshness:{" "}
        {indicator.freshness.stale === null
          ? "unknown"
          : indicator.freshness.stale
            ? "stale"
            : "up to date"}
        . {indicator.freshness.stale_reasons.map(words).join("; ")}
      </p>
      {indicator.freshness.source_check === "NOT_PERMITTED" && (
        <p className="ai-notice">
          Some source checks are outside your current access.
        </p>
      )}
      <p className="muted">
        Checked {when(indicator.freshness.checked_at)}. {value.stale_rule}
      </p>
      {value.reference.interpretation_note && (
        <p>
          <strong>Your interpretation note:</strong>{" "}
          {value.reference.interpretation_note}
        </p>
      )}
      <p className="ai-notice">{value.disclaimer}</p>
    </>
  );
}

export function AIImpactEvidence({
  base,
  path,
  objectId,
  currentRevision,
  canManage,
  hasUnsavedChanges,
  request,
  explain,
  onSaved,
  onMutationStateChange,
}: AIImpactEvidenceProps) {
  const [open, setOpen] = useState(false);
  const [evidence, setEvidence] = useState<Evidence | null>(null);
  const [programmes, setProgrammes] = useState<Page<Row> | null>(null);
  const [periods, setPeriods] = useState<Page<Row> | null>(null);
  const [indicators, setIndicators] = useState<IndicatorPage | null>(null);
  const [programme, setProgramme] = useState("");
  const [period, setPeriod] = useState("");
  const [indicator, setIndicator] = useState("");
  const [note, setNote] = useState("");
  const [editing, setEditing] = useState(false);
  const [confirmation, setConfirmation] = useState<"refresh" | "clear" | null>(
    null,
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [tick, setTick] = useState(0);
  const [ambiguous, setAmbiguous] = useState<WriteCommand | null>(null);
  const generation = useRef(0);
  const evidenceGeneration = useRef(0);
  const indicatorGeneration = useRef(0);
  const previousCommand = useRef<{ key: string; command: WriteCommand } | null>(
    null,
  );
  const busyRef = useRef(false);
  const endpoint = path.replace(/\/$/, "") + "/impact-reference";
  const prefix = base.endsWith("/") ? base : base + "/";
  const headChanged =
    evidence !== null && evidence.revision_id !== currentRevision;
  const blocked =
    busy || hasUnsavedChanges || headChanged || ambiguous !== null;
  useEffect(() => {
    onMutationStateChange?.(busy || ambiguous !== null);
  }, [busy, ambiguous, onMutationStateChange]);
  useEffect(
    () => () => onMutationStateChange?.(false),
    [onMutationStateChange],
  );
  function clearPrivate() {
    ++evidenceGeneration.current;
    setEvidence(null);
    setProgrammes(null);
    setPeriods(null);
    setIndicators(null);
    setProgramme("");
    setPeriod("");
    setIndicator("");
    setNote("");
    setEditing(false);
    setConfirmation(null);
    ++indicatorGeneration.current;
  }
  function failure(cause: unknown) {
    clearPrivate();
    setError(hidden(cause) ? unavailable : explain(cause));
  }
  useEffect(() => {
    ++generation.current;
    previousCommand.current = null;
    busyRef.current = false;
    clearPrivate();
    setAmbiguous(null);
    setBusy(false);
    setError("");
    setNotice("");
    return () => {
      ++generation.current;
      ++indicatorGeneration.current;
    };
  }, [base, path, objectId, canManage]);
  useEffect(() => {
    clearPrivate();
    setError("");
    setNotice("");
  }, [currentRevision]);
  useEffect(() => {
    if (!open) return;
    const current = ++evidenceGeneration.current;
    const controller = new AbortController();
    setEvidence(null);
    setError("");
    (
      request(endpoint + "/result", {
        signal: controller.signal,
      }) as Promise<Evidence>
    )
      .then((value) => {
        if (
          !controller.signal.aborted &&
          current === evidenceGeneration.current
        )
          setEvidence(value);
      })
      .catch((cause) => {
        if (
          !controller.signal.aborted &&
          current === evidenceGeneration.current
        )
          failure(cause);
      });
    return () => controller.abort();
  }, [open, endpoint, currentRevision, canManage, tick]);
  useEffect(() => {
    ++indicatorGeneration.current;
    setIndicators(null);
    setIndicator("");
    if (!editing || !programme || !period) return;
    const current = indicatorGeneration.current;
    const controller = new AbortController();
    (
      request(
        `${prefix}programmes/${programme}/dashboard?period_id=${encodeURIComponent(period)}&limit=100`,
        { signal: controller.signal },
      ) as Promise<IndicatorPage>
    )
      .then((value) => {
        if (
          !controller.signal.aborted &&
          current === indicatorGeneration.current
        )
          setIndicators(value);
      })
      .catch((cause) => {
        if (
          !controller.signal.aborted &&
          current === indicatorGeneration.current
        )
          failure(cause);
      });
    return () => controller.abort();
  }, [editing, programme, period, prefix]);
  async function editLink() {
    if (blocked || !canManage || busyRef.current) return;
    const current = generation.current;
    busyRef.current = true;
    setBusy(true);
    setError("");
    try {
      const [p, d] = await Promise.all([
        request(prefix + "programmes?limit=100") as Promise<Page<Row>>,
        request(prefix + "periods?limit=100") as Promise<Page<Row>>,
      ]);
      if (current !== generation.current) return;
      setProgrammes(p);
      setPeriods(d);
      setEditing(true);
      setConfirmation(null);
      setProgramme("");
      setPeriod("");
      setIndicator("");
      setNote(evidence?.reference?.interpretation_note || "");
    } catch (cause) {
      if (current === generation.current) failure(cause);
    } finally {
      if (current === generation.current) {
        busyRef.current = false;
        setBusy(false);
      }
    }
  }
  async function more(kind: "programmes" | "periods" | "indicators") {
    if (busyRef.current || blocked) return;
    const cursor =
      kind === "programmes"
        ? programmes?.next_cursor
        : kind === "periods"
          ? periods?.next_cursor
          : indicators?.next_cursor;
    if (!cursor) return;
    const current = generation.current;
    const indicatorEpoch = indicatorGeneration.current;
    busyRef.current = true;
    setBusy(true);
    setError("");
    try {
      const route =
        kind === "indicators"
          ? `${prefix}programmes/${programme}/dashboard?period_id=${encodeURIComponent(period)}&limit=100&cursor=`
          : `${prefix}${kind}?limit=100&cursor=`;
      const page = await request(route + encodeURIComponent(cursor));
      if (
        current !== generation.current ||
        (kind === "indicators" &&
          indicatorEpoch !== indicatorGeneration.current)
      )
        return;
      if (kind === "indicators") {
        const value = page as IndicatorPage;
        setIndicators((previous) => ({
          ...value,
          indicators: [
            ...(previous?.indicators || []),
            ...value.indicators.filter(
              (item) =>
                !previous?.indicators.some(
                  (old) => old.indicator_id === item.indicator_id,
                ),
            ),
          ],
        }));
      } else {
        const value = page as Page<Row>;
        const merge = (previous: Page<Row> | null) => ({
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
        });
        if (kind === "programmes") setProgrammes(merge);
        else setPeriods(merge);
      }
    } catch (cause) {
      if (
        current === generation.current &&
        (kind !== "indicators" ||
          indicatorEpoch === indicatorGeneration.current)
      )
        failure(cause);
    } finally {
      if (current === generation.current) {
        busyRef.current = false;
        setBusy(false);
      }
    }
  }
  async function save(data: ReferenceInput | null, exact?: WriteCommand) {
    if (
      !canManage ||
      (hasUnsavedChanges && !exact) ||
      (headChanged && !exact) ||
      busyRef.current ||
      (!exact && ambiguous)
    )
      return;
    const key = JSON.stringify([endpoint, currentRevision, data]);
    const body =
      exact ||
      (previousCommand.current?.key === key
        ? previousCommand.current.command
        : {
            operation_id: crypto.randomUUID(),
            expected_revision: currentRevision,
            data,
          });
    previousCommand.current = { key, command: body };
    const current = generation.current;
    busyRef.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    let receipt: Receipt;
    try {
      receipt = (await request(endpoint, {
        method: "PUT",
        body: JSON.stringify(body),
      })) as Receipt;
    } catch (cause) {
      if (current === generation.current) {
        failure(cause);
        if (!(cause && typeof cause === "object" && "code" in cause))
          setAmbiguous(body);
        busyRef.current = false;
        setBusy(false);
      }
      return;
    }
    if (current !== generation.current) return;
    previousCommand.current = null;
    setAmbiguous(null);
    setEditing(false);
    setConfirmation(null);
    clearPrivate();
    busyRef.current = false;
    setBusy(false);
    setNotice("Evidence relationship saved as a new plan revision.");
    try {
      await onSaved(receipt);
    } catch {
      if (current === generation.current)
        setNotice(
          "Evidence relationship saved. Reopen the plan to view its new revision.",
        );
    }
    if (current === generation.current) setTick((value) => value + 1);
  }
  function submit(event: FormEvent) {
    event.preventDefault();
    if (programme && period && indicator && !blocked)
      void save({
        programme_id: programme,
        indicator_id: indicator,
        period_id: period,
        interpretation_note: note,
      });
  }
  const chosenProgramme = programmes?.items.find(
    (item) => item.object_id === programme,
  );
  const availablePeriods =
    periods?.items.filter((item) => {
      if (
        !chosenProgramme?.data.starts_at ||
        !chosenProgramme.data.ends_at ||
        !item.data.starts_at ||
        !item.data.ends_at
      )
        return true;
      return (
        Date.parse(item.data.starts_at) >=
          Date.parse(chosenProgramme.data.starts_at) &&
        Date.parse(item.data.ends_at) <=
          Date.parse(chosenProgramme.data.ends_at)
      );
    }) || [];
  const currentInput = evidence?.reference
    ? {
        programme_id: evidence.reference.programme_id,
        indicator_id: evidence.reference.indicator_id,
        period_id: evidence.reference.period_id,
        interpretation_note: evidence.reference.interpretation_note,
      }
    : null;
  return (
    <section
      className="ai-impact-evidence ai-guidance-archive"
      aria-label="Programme evidence for this AI plan"
    >
      <button
        type="button"
        className="secondary"
        aria-expanded={open}
        disabled={busy || ambiguous !== null}
        onClick={() => {
          ++generation.current;
          ++indicatorGeneration.current;
          setOpen((value) => !value);
          clearPrivate();
          setError("");
          setNotice("");
        }}
      >
        {open ? "Hide programme evidence" : "View programme evidence"}
      </button>
      {open && (
        <>
          <h4>Programme evidence for this AI plan</h4>
          <p>
            A deliberate link keeps the governed source revisions separate from
            your AI pilot notes. It does not establish that AI caused an impact
            result.
          </p>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          {notice && (
            <p role="status" className="ai-notice">
              {notice}
            </p>
          )}
          {!evidence && !error && (
            <p role="status">Loading currently authorised evidence…</p>
          )}
          <button
            type="button"
            className="secondary"
            disabled={busy || ambiguous !== null}
            onClick={() => {
              ++generation.current;
              clearPrivate();
              setTick((value) => value + 1);
            }}
          >
            Check evidence again
          </button>
          {evidence && <GovernedEvidence value={evidence} />}
          {hasUnsavedChanges && (
            <p className="ai-notice">
              Save or discard your plan draft changes before linking, refreshing
              or clearing programme evidence.
            </p>
          )}
          {headChanged && (
            <p className="ai-notice">
              The saved plan changed. Reopen its current revision before
              changing this relationship.
            </p>
          )}
          {ambiguous && (
            <div role="status" className="ai-notice">
              <p>
                The response was lost. The change may already be saved. Retry
                the same change to confirm its outcome before editing.
              </p>
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={() => void save(ambiguous.data, ambiguous)}
              >
                Retry previous evidence change
              </button>
            </div>
          )}
          {canManage && !ambiguous && (
            <div className="ai-actions">
              <button
                type="button"
                className="secondary"
                disabled={blocked}
                onClick={() => void editLink()}
              >
                Choose programme evidence
              </button>
              {evidence && (
                <>
                  <button
                    type="button"
                    className="secondary"
                    disabled={blocked}
                    onClick={() => {
                      setEditing(false);
                      setConfirmation("refresh");
                    }}
                  >
                    Review refresh of saved pins
                  </button>
                </>
              )}
              <button
                type="button"
                className="secondary"
                disabled={blocked}
                onClick={() => {
                  setEditing(false);
                  setConfirmation("clear");
                }}
              >
                Review clearing of evidence relationship
              </button>
            </div>
          )}
          {confirmation && (confirmation === "clear" || evidence) && (
            <section aria-label="Confirm evidence relationship change">
              <h5>
                {confirmation === "refresh"
                  ? "Refresh the saved source pins"
                  : "Clear the evidence relationship"}
              </h5>
              <p>
                {evidence ? (
                  <>
                    {evidence.programme_title || "Authorised programme"} ·{" "}
                    {evidence.indicator?.indicator_label ||
                      "Authorised indicator"}{" "}
                    · {evidence.period?.period_code || "Authorised period"}.
                  </>
                ) : (
                  "This saved AI adoption plan."
                )}
              </p>
              <p>
                {confirmation === "refresh"
                  ? "This creates a new plan revision and pins the currently authorised source revisions and latest locked snapshot, when available. Review changes in the programme workspace first."
                  : "This creates a new plan revision with no evidence relationship. Earlier plan revisions remain unchanged."}
              </p>
              <div className="ai-actions">
                <button
                  type="button"
                  className="primary"
                  disabled={blocked}
                  onClick={() =>
                    void save(confirmation === "clear" ? null : currentInput)
                  }
                >
                  {confirmation === "refresh"
                    ? "Confirm evidence refresh"
                    : "Confirm link removal"}
                </button>
                <button
                  type="button"
                  className="secondary"
                  disabled={busy}
                  onClick={() => setConfirmation(null)}
                >
                  Cancel relationship change
                </button>
              </div>
            </section>
          )}
          {editing && programmes && periods && (
            <form onSubmit={submit}>
              <fieldset disabled={blocked}>
                <legend>Choose currently authorised programme evidence</legend>
                <p>
                  Each list shows one bounded page. Load more explicitly when
                  needed. Period and calendar compatibility is checked again
                  when you confirm the link.
                </p>
                <div className="form-grid">
                  <label>
                    Programme
                    <select
                      aria-label="Evidence programme"
                      value={programme}
                      required
                      onChange={(event) => {
                        setProgramme(event.target.value);
                        setPeriod("");
                        setIndicator("");
                      }}
                    >
                      <option value="">Choose a programme</option>
                      {programmes.items.map((item) => (
                        <option key={item.object_id} value={item.object_id}>
                          {item.data.title ||
                            item.data.code ||
                            "Authorised programme"}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Reporting period
                    <select
                      aria-label="Evidence reporting period"
                      value={period}
                      required
                      disabled={!programme || blocked}
                      onChange={(event) => setPeriod(event.target.value)}
                    >
                      <option value="">Choose a reporting period</option>
                      {availablePeriods.map((item) => (
                        <option key={item.object_id} value={item.object_id}>
                          {item.data.code || "Authorised period"} ·{" "}
                          {when(item.data.starts_at)}–{when(item.data.ends_at)}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Indicator
                    <select
                      aria-label="Evidence indicator"
                      value={indicator}
                      required
                      disabled={!indicators || blocked}
                      onChange={(event) => setIndicator(event.target.value)}
                    >
                      <option value="">Choose an indicator</option>
                      {indicators?.indicators.map((item) => (
                        <option
                          key={item.indicator_id}
                          value={item.indicator_id}
                        >
                          {item.indicator_label || "Authorised indicator"}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Interpretation note
                    <textarea
                      aria-label="Evidence interpretation note"
                      value={note}
                      maxLength={1000}
                      onChange={(event) => setNote(event.target.value)}
                    />
                  </label>
                </div>
                {programme && period && !indicators && (
                  <p role="status">Loading authorised indicator labels…</p>
                )}
                {indicators && indicators.indicators.length === 0 && (
                  <p>No permitted indicator is available on this page.</p>
                )}
                <div className="ai-actions">
                  {programmes.next_cursor && (
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => void more("programmes")}
                    >
                      Load more evidence programmes
                    </button>
                  )}
                  {periods.next_cursor && (
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => void more("periods")}
                    >
                      Load more evidence periods
                    </button>
                  )}
                  {indicators?.next_cursor && (
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => void more("indicators")}
                    >
                      Load more evidence indicators
                    </button>
                  )}
                  <button
                    type="submit"
                    className="primary"
                    disabled={blocked || !programme || !period || !indicator}
                  >
                    Confirm programme evidence link
                  </button>
                  <button
                    type="button"
                    className="secondary"
                    onClick={() => setEditing(false)}
                  >
                    Cancel evidence selection
                  </button>
                </div>
              </fieldset>
            </form>
          )}
        </>
      )}
    </section>
  );
}
