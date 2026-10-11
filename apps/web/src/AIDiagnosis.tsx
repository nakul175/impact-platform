import React, { useEffect, useId, useRef, useState } from "react";
import "./ai-diagnosis.css";

type EvidenceReference = { object_id: string; revision_id: string };
type EvidenceChoice = EvidenceReference & {
  data: {
    filename?: string;
    evidence_type?: string;
    upload_id?: string;
    scan_state?: string;
    external_reference?: string;
  };
};
export type DiagnosisProblem = {
  problem_id: string;
  description: string;
  affected_area: string;
  supporting_evidence: string;
  evidence_references?: EvidenceReference[];
};
export type DiagnosisDraft = {
  title: string;
  problems: DiagnosisProblem[];
  priority_order: string[];
};
export type Diagnosis = {
  object_id: string;
  revision_id: string;
  business_state: "Draft" | "Completed";
  data: DiagnosisDraft & {
    completed_at?: string;
    completed_by?: string;
    correction_reason?: string;
  };
};
type Receipt = {
  object_id: string;
  revision_id: string;
  business_state: "Draft" | "Completed";
  saved_at: string;
  operation_id: string;
  correlation_id: string;
};
type Props = {
  base: string;
  principalId: string;
  sessionIdentity: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
  capabilities: string[];
};
type PendingCommand = {
  kind: "save" | "complete" | "revise";
  path: string;
  method: "POST" | "PUT";
  body: string;
  data: DiagnosisDraft;
  objectId: string | null;
};
type SwitchRequest = { kind: "new" } | { kind: "select"; id: string };
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const copy = <T,>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const blank = (): DiagnosisDraft => ({
  title: "Organisation diagnosis",
  problems: [],
  priority_order: [],
});
const draftOf = (value: Diagnosis): DiagnosisDraft => ({
  title: value.data.title,
  problems: copy(value.data.problems),
  priority_order: [...value.data.priority_order],
});
const codeOf = (error: unknown) =>
  error && typeof error === "object" && "code" in error
    ? String(error.code)
    : "";
const refusalCodes = new Set([
  "AUTH_REQUIRED",
  "POLICY_DENIED",
  "RESOURCE_UNAVAILABLE",
  "VALIDATION_FAILED",
  "CONFLICT_VERSION",
  "STATE_TRANSITION_DENIED",
  "LIMIT_EXCEEDED",
  "ASSURANCE_REQUIRED",
]);
function validReferences(value: unknown): value is EvidenceReference[] {
  return (
    Array.isArray(value) &&
    value.length <= 5 &&
    value.every(
      (item) =>
        item &&
        typeof item === "object" &&
        Object.keys(item).sort().join(",") === "object_id,revision_id" &&
        typeof item.object_id === "string" &&
        UUID.test(item.object_id) &&
        item.object_id === item.object_id.toLowerCase() &&
        typeof item.revision_id === "string" &&
        UUID.test(item.revision_id) &&
        item.revision_id === item.revision_id.toLowerCase(),
    ) &&
    new Set(value.map((item) => item.object_id + ":" + item.revision_id))
      .size === value.length
  );
}
function isEvidenceChoice(value: unknown): value is EvidenceChoice {
  if (!value || typeof value !== "object") return false;
  const item = value as EvidenceChoice;
  return (
    validReferences([
      { object_id: item.object_id, revision_id: item.revision_id },
    ]) &&
    !!item.data &&
    typeof item.data === "object" &&
    !Array.isArray(item.data) &&
    [
      "filename",
      "evidence_type",
      "upload_id",
      "scan_state",
      "external_reference",
    ].every(
      (key) =>
        item.data[key as keyof EvidenceChoice["data"]] === undefined ||
        typeof item.data[key as keyof EvidenceChoice["data"]] === "string",
    )
  );
}
function selectableEvidence(item: EvidenceChoice) {
  return item.data.upload_id
    ? item.data.scan_state === "CLEAN"
    : !!item.data.external_reference?.trim();
}
function isDraft(value: unknown): value is DiagnosisDraft {
  if (!value || typeof value !== "object") return false;
  const data = value as DiagnosisDraft;
  if (
    typeof data.title !== "string" ||
    data.title.length > 150 ||
    !Array.isArray(data.problems) ||
    data.problems.length > 20 ||
    !Array.isArray(data.priority_order) ||
    data.priority_order.length > 20 ||
    data.priority_order.some(
      (id) => typeof id !== "string" || !UUID.test(id),
    ) ||
    new Set(data.priority_order).size !== data.priority_order.length
  )
    return false;
  const seen = new Set<string>();
  for (const problem of data.problems) {
    if (
      !problem ||
      typeof problem !== "object" ||
      typeof problem.problem_id !== "string" ||
      !UUID.test(problem.problem_id) ||
      seen.has(problem.problem_id) ||
      typeof problem.description !== "string" ||
      problem.description.length > 1000 ||
      typeof problem.affected_area !== "string" ||
      problem.affected_area.length > 150 ||
      typeof problem.supporting_evidence !== "string" ||
      problem.supporting_evidence.length > 4000 ||
      (problem.evidence_references !== undefined &&
        !validReferences(problem.evidence_references))
    )
      return false;
    seen.add(problem.problem_id);
  }
  return data.priority_order.every((id) => seen.has(id));
}
function isDiagnosis(value: unknown): value is Diagnosis {
  if (!value || typeof value !== "object") return false;
  const result = value as Diagnosis;
  return (
    typeof result.object_id === "string" &&
    UUID.test(result.object_id) &&
    typeof result.revision_id === "string" &&
    UUID.test(result.revision_id) &&
    ["Draft", "Completed"].includes(result.business_state) &&
    isDraft(result.data) &&
    (result.data.completed_at === undefined ||
      (typeof result.data.completed_at === "string" &&
        !Number.isNaN(Date.parse(result.data.completed_at)))) &&
    (result.data.completed_by === undefined ||
      (typeof result.data.completed_by === "string" &&
        UUID.test(result.data.completed_by))) &&
    (result.data.correction_reason === undefined ||
      (typeof result.data.correction_reason === "string" &&
        result.data.correction_reason.length <= 1000))
  );
}
function isReceipt(value: unknown, operationId: string): value is Receipt {
  if (!value || typeof value !== "object") return false;
  const result = value as Receipt;
  return (
    typeof result.object_id === "string" &&
    UUID.test(result.object_id) &&
    typeof result.revision_id === "string" &&
    UUID.test(result.revision_id) &&
    ["Draft", "Completed"].includes(result.business_state) &&
    result.operation_id === operationId &&
    typeof result.saved_at === "string" &&
    !Number.isNaN(Date.parse(result.saved_at)) &&
    typeof result.correlation_id === "string" &&
    UUID.test(result.correlation_id)
  );
}
function completionErrors(data: DiagnosisDraft): string[] {
  const errors: string[] = [];
  if (!data.title.trim()) errors.push("Enter a diagnosis title.");
  if (!data.problems.length) errors.push("Add at least one problem.");
  data.problems.forEach((problem, index) => {
    const name = problem.description.trim() || `Problem ${index + 1}`;
    const missing: string[] = [];
    if (!problem.description.trim()) missing.push("a description");
    if (!problem.affected_area.trim()) missing.push("an affected area");
    if (!problem.supporting_evidence.trim())
      missing.push("supporting evidence");
    if (!data.priority_order.includes(problem.problem_id))
      missing.push("a place in the priority order");
    if (missing.length) errors.push(`${name}: add ${missing.join(", ")}.`);
  });
  return errors;
}

// A scope or capability change remounts all ephemeral data immediately, before an effect can run.
// The server still resolves current authority for every read, write and receipt replay.
export function AIDiagnosisPanel(props: Props) {
  const canRead = props.capabilities.includes("ai.diagnosis.read");
  const canManage = props.capabilities.includes("ai.diagnosis.manage");
  if (!canRead && !canManage) return null;
  return (
    <DiagnosisWorkspace
      key={JSON.stringify([
        props.base,
        props.principalId,
        props.sessionIdentity,
        canRead,
        canManage,
        props.capabilities.includes("evidence.read"),
      ])}
      {...props}
      canRead={canRead}
      canManage={canManage}
    />
  );
}

function DiagnosisWorkspace({
  base,
  request,
  explain,
  canRead,
  canManage,
  capabilities,
}: Props & { canRead: boolean; canManage: boolean }) {
  const canReadEvidence = capabilities.includes("evidence.read");
  const [evidenceProblem, setEvidenceProblem] = useState<string | null>(null);
  const [evidenceChoices, setEvidenceChoices] = useState<EvidenceChoice[]>([]);
  const [evidenceCursor, setEvidenceCursor] = useState<string | null>(null);
  const [evidenceError, setEvidenceError] = useState("");
  const [evidenceBusy, setEvidenceBusy] = useState(false);
  const evidenceReads = useRef(0);
  const evidenceSending = useRef(false);
  const evidenceTarget = useRef<string | null>(null);
  const id = useId();
  const headingId = id + "-diagnosis-heading";
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [head, setHead] = useState<Diagnosis | null>(null);
  const [draft, setDraft] = useState<DiagnosisDraft>(blank);
  const [savedData, setSavedData] = useState(() => JSON.stringify(blank()));
  const [loading, setLoading] = useState(canRead);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [missing, setMissing] = useState<string[]>([]);
  const [pending, setPending] = useState<PendingCommand | null>(null);
  const [conflict, setConflict] = useState(false);
  const [currentVersion, setCurrentVersion] = useState<Diagnosis | null>(null);
  const [switchRequest, setSwitchRequest] = useState<SwitchRequest | null>(
    null,
  );
  const [correctionReason, setCorrectionReason] = useState("");
  const [needsReadback, setNeedsReadback] = useState(false);
  const [unavailable, setUnavailable] = useState(false);
  const alive = useRef(true);
  // Read loss is terminal for this keyed workspace, including requests already in flight.
  const authorityInvalidated = useRef(false);
  const active = () => alive.current && !authorityInvalidated.current;
  const reads = useRef(0);
  const sending = useRef(false);
  const pendingRef = useRef<PendingCommand | null>(null);
  const requests = useRef(request);
  requests.current = request;
  const controllers = useRef(new Set<AbortController>());
  const serialized = JSON.stringify(draft);
  const dirty = serialized !== savedData;
  const completed = head?.business_state === "Completed";
  const editingBlocked = busy || !!pending || conflict || needsReadback;
  const canEdit = canRead && canManage && !completed && !unavailable;
  const endpoint = base + "ai-enablement/diagnoses";

  async function guardedRequest(path: string, options?: RequestInit) {
    const controller = new AbortController();
    controllers.current.add(controller);
    try {
      if (!active())
        throw new Error("Diagnosis access is no longer available.");
      const value = await requests.current(path, {
        ...options,
        signal: controller.signal,
      });
      if (!active())
        throw new Error("Diagnosis access is no longer available.");
      return value;
    } finally {
      controllers.current.delete(controller);
    }
  }
  function clearEvidence() {
    ++evidenceReads.current;
    evidenceTarget.current = null;
    evidenceSending.current = false;
    setEvidenceProblem(null);
    setEvidenceChoices([]);
    setEvidenceCursor(null);
    setEvidenceError("");
    setEvidenceBusy(false);
  }
  async function loadEvidence(problemId: string, cursor?: string) {
    if (
      !active() ||
      !canEdit ||
      editingBlocked ||
      !canReadEvidence ||
      evidenceSending.current
    )
      return;
    const generation = ++evidenceReads.current;
    evidenceSending.current = true;
    evidenceTarget.current = problemId;
    setEvidenceProblem(problemId);
    setEvidenceBusy(true);
    setEvidenceError("");
    if (!cursor) {
      setEvidenceChoices([]);
      setEvidenceCursor(null);
    }
    try {
      const page = await guardedRequest(
        base +
          "evidence?limit=20" +
          (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""),
      );
      if (!active() || generation !== evidenceReads.current) return;
      if (
        !page ||
        !Array.isArray(page.items) ||
        page.items.length > 20 ||
        !page.items.every(isEvidenceChoice) ||
        (page.next_cursor !== null && typeof page.next_cursor !== "string")
      )
        throw new Error("Evidence choices could not be read safely.");
      // Replace each bounded page: no unbounded accumulation of protected metadata.
      setEvidenceChoices(page.items.filter(selectableEvidence));
      setEvidenceCursor(page.next_cursor);
    } catch {
      if (!active() || generation !== evidenceReads.current) return;
      setEvidenceChoices([]);
      setEvidenceCursor(null);
      setEvidenceError(
        "Evidence is unavailable. Check your access and try again.",
      );
    } finally {
      if (active() && generation === evidenceReads.current) {
        evidenceSending.current = false;
        setEvidenceBusy(false);
      }
    }
  }
  async function chooseEvidence(problemId: string, item: EvidenceChoice) {
    if (
      !active() ||
      !canEdit ||
      editingBlocked ||
      !canReadEvidence ||
      evidenceSending.current ||
      evidenceTarget.current !== problemId
    )
      return;
    const generation = ++evidenceReads.current;
    evidenceSending.current = true;
    setEvidenceBusy(true);
    setEvidenceError("");
    try {
      const current = await guardedRequest(base + "evidence/" + item.object_id);
      if (!active() || generation !== evidenceReads.current) return;
      if (
        !isEvidenceChoice(current) ||
        current.object_id !== item.object_id ||
        !selectableEvidence(current)
      )
        throw new Error("Evidence unavailable");
      if (current.revision_id !== item.revision_id) {
        setEvidenceChoices([]);
        setEvidenceCursor(null);
        setEvidenceError(
          "This evidence changed. Reload the choices before selecting its new version.",
        );
        return;
      }
      // A concurrent edit or pending command invalidates this picker before its response arrives.
      const problem = draft.problems.find(
        (value) => value.problem_id === problemId,
      );
      if (!problem || (problem.evidence_references?.length || 0) >= 5) return;
      const refs = problem.evidence_references || [];
      if (
        refs.some(
          (value) =>
            value.object_id === item.object_id &&
            value.revision_id === item.revision_id,
        )
      )
        return;
      changeProblem(problemId, {
        evidence_references: [
          ...refs,
          { object_id: item.object_id, revision_id: item.revision_id },
        ],
      });
      clearEvidence();
      setNotice(
        "Evidence version selected. Save the diagnosis to keep this link.",
      );
    } catch {
      if (!active() || generation !== evidenceReads.current) return;
      setEvidenceChoices([]);
      setEvidenceCursor(null);
      setEvidenceError("Evidence is unavailable. No link was added.");
    } finally {
      if (active() && generation === evidenceReads.current) {
        evidenceSending.current = false;
        setEvidenceBusy(false);
      }
    }
  }
  function hideUnavailable() {
    clearEvidence();
    authorityInvalidated.current = true;
    reads.current += 1;
    for (const controller of controllers.current) controller.abort();
    controllers.current.clear();
    sending.current = false;
    setBusy(false);
    setLoading(false);
    setNextCursor(null);
    setUnavailable(true);
    setDiagnoses([]);
    setHead(null);
    setDraft(blank());
    setSavedData(JSON.stringify(blank()));
    setCurrentVersion(null);
    setMissing([]);
    setCorrectionReason("");
    pendingRef.current = null;
    setPending(null);
    setConflict(false);
    setNeedsReadback(false);
    setSwitchRequest(null);
  }
  async function readList(cursor?: string) {
    if (!active() || !canRead || unavailable) return;
    const current = ++reads.current;
    setLoading(true);
    try {
      const page = await guardedRequest(
        endpoint +
          "?limit=20" +
          (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""),
      );
      if (!active() || current !== reads.current) return;
      if (
        !page ||
        !Array.isArray(page.items) ||
        page.items.length > 100 ||
        !page.items.every(isDiagnosis) ||
        (page.next_cursor !== null && typeof page.next_cursor !== "string")
      )
        throw new Error("The saved diagnosis list could not be read safely.");
      setDiagnoses((previous) => {
        const items: Diagnosis[] = cursor ? [...previous] : [];
        for (const item of page.items as Diagnosis[]) {
          const index = items.findIndex(
            (value) => value.object_id === item.object_id,
          );
          if (index < 0) items.push(item);
          else items[index] = item;
        }
        return items;
      });
      setNextCursor(page.next_cursor);
    } catch (cause) {
      if (!active() || current !== reads.current) return;
      if (
        ["AUTH_REQUIRED", "POLICY_DENIED", "RESOURCE_UNAVAILABLE"].includes(
          codeOf(cause),
        )
      )
        hideUnavailable();
      setError(explain(cause));
    } finally {
      if (active() && current === reads.current) setLoading(false);
    }
  }
  useEffect(() => {
    alive.current = true;
    if (canRead) void readList();
    return () => {
      alive.current = false;
      reads.current += 1;
      for (const controller of controllers.current) controller.abort();
      controllers.current.clear();
    };
  }, []);

  function install(value: Diagnosis) {
    if (!active()) return;
    clearEvidence();
    const data = draftOf(value);
    setHead(value);
    setDraft(data);
    setSavedData(JSON.stringify(data));
    setMissing([]);
    setConflict(false);
    setCurrentVersion(null);
    setCorrectionReason("");
    setNeedsReadback(false);
    setError("");
  }
  async function selectDiagnosis(objectId: string, compare = false) {
    if (
      !active() ||
      sending.current ||
      pendingRef.current ||
      !canRead ||
      unavailable
    )
      return;
    sending.current = true;
    setBusy(true);
    setError("");
    try {
      const value = await guardedRequest(endpoint + "/" + objectId);
      if (!active()) return;
      if (!isDiagnosis(value) || value.object_id !== objectId)
        throw new Error("The saved diagnosis could not be read safely.");
      if (compare) setCurrentVersion(value);
      else install(value);
    } catch (cause) {
      if (!active()) return;
      if (
        ["AUTH_REQUIRED", "POLICY_DENIED", "RESOURCE_UNAVAILABLE"].includes(
          codeOf(cause),
        )
      )
        hideUnavailable();
      setError(explain(cause));
    } finally {
      if (active()) {
        sending.current = false;
        setBusy(false);
      }
    }
  }
  function switchTo(value: SwitchRequest, confirmed = false) {
    if (!active() || sending.current || pendingRef.current || unavailable)
      return;
    if (dirty && !confirmed) {
      setSwitchRequest(value);
      return;
    }
    clearEvidence();
    setSwitchRequest(null);
    setNotice("");
    if (value.kind === "select") void selectDiagnosis(value.id);
    else {
      setHead(null);
      setDraft(blank());
      setSavedData(JSON.stringify(blank()));
      setMissing([]);
      setError("");
      setConflict(false);
      setCurrentVersion(null);
      setCorrectionReason("");
      setNeedsReadback(false);
    }
  }
  function change(next: DiagnosisDraft) {
    if (!active() || !canEdit || editingBlocked) return;
    clearEvidence();
    setDraft(next);
    setNotice("");
    setMissing([]);
    setError("");
  }
  function changeProblem(problemId: string, fields: Partial<DiagnosisProblem>) {
    change({
      ...draft,
      problems: draft.problems.map((problem) =>
        problem.problem_id === problemId ? { ...problem, ...fields } : problem,
      ),
    });
  }
  function move(problemId: string, direction: -1 | 1) {
    if (!active()) return;
    const order = [...draft.priority_order];
    const index = order.indexOf(problemId);
    const destination = index + direction;
    if (index < 0 || destination < 0 || destination >= order.length) return;
    [order[index], order[destination]] = [order[destination], order[index]];
    change({ ...draft, priority_order: order });
    setNotice(`Problem moved to priority ${destination + 1}.`);
    requestAnimationFrame(() => {
      if (active())
        document.getElementById(id + "-problem-" + problemId)?.focus();
    });
  }
  async function send(command: PendingCommand) {
    if (!active() || sending.current || !canRead || !canManage || unavailable)
      return;
    if (pendingRef.current && pendingRef.current !== command) return;
    clearEvidence();
    sending.current = true;
    pendingRef.current = command;
    setPending(command);
    setBusy(true);
    setError("");
    setNotice("");
    const operationId = JSON.parse(command.body).operation_id as string;
    try {
      const receipt = await guardedRequest(command.path, {
        method: command.method,
        body: command.body,
      });
      if (!active()) return;
      if (
        !isReceipt(receipt, operationId) ||
        (command.objectId !== null && receipt.object_id !== command.objectId) ||
        receipt.business_state !==
          (command.kind === "complete" ? "Completed" : "Draft")
      )
        throw new Error(
          "The save response was unreadable; its outcome is uncertain.",
        );
      pendingRef.current = null;
      setPending(null);
      // The durable receipt proves a save. A fresh readable head is required before another write.
      const provisional: Diagnosis = {
        object_id: receipt.object_id,
        revision_id: receipt.revision_id,
        business_state: receipt.business_state,
        data: copy(command.data),
      };
      setHead(provisional);
      setSavedData(JSON.stringify(command.data));
      setNeedsReadback(true);
      setNotice(
        command.kind === "complete"
          ? "Diagnosis completed. Loading its saved version…"
          : command.kind === "revise"
            ? "A new correction draft was saved. Loading its saved version…"
            : "Diagnosis draft saved. Loading its saved version…",
      );
      try {
        const value = await guardedRequest(endpoint + "/" + receipt.object_id);
        if (!active()) return;
        if (!isDiagnosis(value) || value.object_id !== receipt.object_id)
          throw new Error("The saved diagnosis could not be read safely.");
        if (value.revision_id !== receipt.revision_id) {
          setCurrentVersion(value);
          setConflict(true);
          setNeedsReadback(false);
          setNotice(
            "Your change was saved. Another change is now current; review it below.",
          );
        } else {
          install(value);
          setNotice(
            value.business_state === "Completed"
              ? "Diagnosis completed and read back. Corrections create a new draft."
              : "Diagnosis draft saved and read back.",
          );
        }
        void readList();
      } catch (cause) {
        if (!active()) return;
        if (
          ["AUTH_REQUIRED", "POLICY_DENIED", "RESOURCE_UNAVAILABLE"].includes(
            codeOf(cause),
          )
        )
          hideUnavailable();
        setError(
          "The change was saved, but its current version could not be loaded. " +
            explain(cause),
        );
      }
    } catch (cause) {
      if (!active()) return;
      const code = codeOf(cause);
      if (refusalCodes.has(code)) {
        pendingRef.current = null;
        setPending(null);
        if (["CONFLICT_VERSION", "STATE_TRANSITION_DENIED"].includes(code))
          setConflict(true);
        if (["AUTH_REQUIRED", "RESOURCE_UNAVAILABLE"].includes(code))
          hideUnavailable();
        if (code === "POLICY_DENIED" && head) {
          // Write denial does not imply read access. Verify the latter without replacing local input.
          try {
            const readable = await guardedRequest(
              endpoint + "/" + head.object_id,
            );
            if (!active()) return;
            if (
              !isDiagnosis(readable) ||
              readable.object_id !== head.object_id
            ) {
              hideUnavailable();
            } else if (readable.revision_id !== head.revision_id) {
              setCurrentVersion(readable);
              setConflict(true);
            }
          } catch {
            if (!active()) return;
            hideUnavailable();
          }
        }
        setError(explain(cause));
      } else {
        setError(
          "The outcome is uncertain. Your input and this exact request are kept here. Retry the same request before making another change. " +
            explain(cause),
        );
      }
    } finally {
      if (active()) {
        sending.current = false;
        setBusy(false);
      }
    }
  }
  function command(kind: PendingCommand["kind"]) {
    if (!active() || editingBlocked || !canManage || !canRead || unavailable)
      return;
    if (
      kind === "save" &&
      (completed || !isDraft(draft) || !draft.title.trim())
    ) {
      setError("Enter a title and keep each problem within the stated limits.");
      return;
    }
    if (kind === "complete") {
      if (!head || dirty || completed) return;
      const errors = completionErrors(draft);
      if (errors.length) {
        setMissing(errors);
        return;
      }
    }
    if (
      kind === "revise" &&
      (!head || !completed || !correctionReason.trim())
    ) {
      setError("Enter a reason for this correction.");
      return;
    }
    const body =
      kind === "save"
        ? {
            operation_id: crypto.randomUUID(),
            ...(head ? { expected_revision: head.revision_id } : {}),
            data: copy(draft),
          }
        : {
            operation_id: crypto.randomUUID(),
            expected_revision: head!.revision_id,
            ...(kind === "revise" ? { reason: correctionReason } : {}),
          };
    void send({
      kind,
      method: kind === "save" && head ? "PUT" : "POST",
      path:
        endpoint +
        (head ? "/" + head.object_id : "") +
        (kind === "save" ? "" : "/actions/" + kind),
      body: JSON.stringify(body),
      data: copy(draft),
      objectId: head?.object_id || null,
    });
  }
  const ordered = [
    ...draft.priority_order.map(
      (problemId) =>
        draft.problems.find((problem) => problem.problem_id === problemId)!,
    ),
    ...draft.problems.filter(
      (problem) => !draft.priority_order.includes(problem.problem_id),
    ),
  ];
  return (
    <section
      className="ai-diagnosis"
      aria-labelledby={headingId}
      data-diagnosis-state={head?.business_state || "Unsaved"}
      data-diagnosis-revision={head?.revision_id || ""}
    >
      <h3 id={headingId}>Your organisation&apos;s priorities</h3>
      <p>
        Record the problems your organisation wants to solve, the area affected
        and the evidence behind them. Put the most important problem first. This
        works with AI switched off.
      </p>
      <p className="muted">
        Use organisation-level notes. Keep names, participant details, passwords
        and confidential records out of this worksheet.
      </p>
      <p className="muted">
        Save before leaving this page. Reloading or leaving discards unsaved
        input.
      </p>
      {notice && <p role="status">{notice}</p>}
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {missing.length > 0 && (
        <div className="error" role="alert">
          <p>
            Completion was refused. Fix these problems, then save the draft:
          </p>
          <ul>
            {missing.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
      )}
      {!canRead && (
        <p>Your administrator needs to grant diagnosis read access.</p>
      )}
      {unavailable && (
        <p>
          The diagnosis is unavailable. Refresh your access before continuing.
        </p>
      )}
      {canRead && !unavailable && (
        <>
          <div className="ai-diagnosis-selector">
            <label>
              Saved diagnoses
              <select
                aria-label="Saved diagnoses"
                value={head?.object_id || ""}
                disabled={busy || !!pending || conflict || needsReadback}
                onChange={(event) => {
                  if (event.target.value)
                    switchTo({ kind: "select", id: event.target.value });
                }}
              >
                <option value="">Choose a saved diagnosis</option>
                {diagnoses.map((value) => (
                  <option key={value.object_id} value={value.object_id}>
                    {value.data.title} · {value.business_state}
                  </option>
                ))}
              </select>
            </label>
            {canManage && (
              <button
                type="button"
                disabled={editingBlocked}
                onClick={() => switchTo({ kind: "new" })}
              >
                New diagnosis
              </button>
            )}
          </div>
          {loading && <p role="status">Loading saved diagnoses…</p>}
          {nextCursor && (
            <button
              type="button"
              disabled={loading || busy || !!pending}
              onClick={() => void readList(nextCursor)}
            >
              Load more diagnoses
            </button>
          )}
          {switchRequest && (
            <div
              className="ai-diagnosis-confirm"
              role="group"
              aria-label="Unsaved diagnosis changes"
            >
              <p>
                Your changes are unsaved. Keep this draft or discard it to
                continue.
              </p>
              <div className="ai-actions">
                <button type="button" onClick={() => setSwitchRequest(null)}>
                  Keep my draft
                </button>
                <button
                  type="button"
                  onClick={() => switchTo(switchRequest, true)}
                >
                  Discard my changes and continue
                </button>
              </div>
            </div>
          )}
          {pending && (
            <div
              className="ai-diagnosis-confirm"
              role="group"
              aria-label="Uncertain diagnosis request"
            >
              <p>
                Resolve this request before editing, leaving this draft or
                starting another save.
              </p>
              <button
                type="button"
                disabled={busy}
                onClick={() => void send(pending)}
              >
                Retry the same request
              </button>
            </div>
          )}
          {conflict && (
            <div
              className="ai-diagnosis-confirm"
              role="group"
              aria-label="Diagnosis version conflict"
            >
              <p>
                Your local input is kept below. A saved version changed; load it
                for review before saving again.
              </p>
              {head && (
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => void selectDiagnosis(head.object_id, true)}
                >
                  Load current saved version for review
                </button>
              )}
              {currentVersion && (
                <>
                  <h4>Current saved diagnosis: {currentVersion.data.title}</h4>
                  <p>{currentVersion.business_state}</p>
                  <ol>
                    {[
                      ...currentVersion.data.priority_order,
                      ...currentVersion.data.problems
                        .filter(
                          (problem) =>
                            !currentVersion.data.priority_order.includes(
                              problem.problem_id,
                            ),
                        )
                        .map((problem) => problem.problem_id),
                    ].map((problemId) => {
                      const problem = currentVersion.data.problems.find(
                        (value) => value.problem_id === problemId,
                      )!;
                      return (
                        <li key={problemId}>
                          <strong>
                            {problem.description ||
                              "Problem without a description"}
                          </strong>
                          <p>
                            Affected area:{" "}
                            {problem.affected_area || "Not recorded"}
                          </p>
                          <p className="ai-diagnosis-text">
                            Evidence:{" "}
                            {problem.supporting_evidence || "Not recorded"}
                          </p>
                        </li>
                      );
                    })}
                  </ol>
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => {
                      install(currentVersion);
                      setNotice(
                        "Current saved version loaded. Review it before making new changes.",
                      );
                    }}
                  >
                    Replace my local draft with this saved version
                  </button>
                </>
              )}
            </div>
          )}
          {needsReadback && head && !pending && (
            <button
              type="button"
              disabled={busy}
              onClick={() => void selectDiagnosis(head.object_id)}
            >
              Load the saved diagnosis
            </button>
          )}
          {head && (
            <p className="muted">
              {head.business_state}
              {head.data.completed_at
                ? " · completed " +
                  new Date(head.data.completed_at).toLocaleString()
                : ""}
              {dirty ? " · unsaved changes" : ""}
            </p>
          )}
          {(canManage || head) && (
            <>
              <fieldset disabled={busy}>
                <legend>Diagnosis details</legend>
                <label>
                  Diagnosis title
                  <input
                    aria-label="Diagnosis title"
                    value={draft.title}
                    readOnly={!canEdit || editingBlocked}
                    maxLength={150}
                    onChange={(event) =>
                      change({ ...draft, title: event.target.value })
                    }
                  />
                </label>
                <p className="muted">
                  Up to 20 problems. Drafts may be incomplete; completion
                  requires every field and a priority for each problem.
                </p>
                <ol className="ai-diagnosis-problems">
                  {ordered.map((problem) => {
                    const position = draft.priority_order.indexOf(
                      problem.problem_id,
                    );
                    const name = problem.description.trim() || "this problem";
                    return (
                      <li
                        key={problem.problem_id}
                        data-problem-id={problem.problem_id}
                        data-priority={position < 0 ? "" : position + 1}
                      >
                        <div className="ai-diagnosis-problem">
                          <h4
                            id={id + "-problem-" + problem.problem_id}
                            tabIndex={-1}
                          >
                            {position < 0
                              ? "Priority not set"
                              : `Priority ${position + 1}`}
                          </h4>
                          <label>
                            Description
                            <textarea
                              id={id + "-description-" + problem.problem_id}
                              aria-label={`Description for ${position < 0 ? "unprioritised problem" : "priority " + (position + 1)}`}
                              value={problem.description}
                              readOnly={!canEdit || editingBlocked}
                              maxLength={1000}
                              rows={3}
                              onChange={(event) =>
                                changeProblem(problem.problem_id, {
                                  description: event.target.value,
                                })
                              }
                            />
                          </label>
                          <label>
                            Area affected
                            <input
                              aria-label={`Area affected for ${name}`}
                              value={problem.affected_area}
                              readOnly={!canEdit || editingBlocked}
                              maxLength={150}
                              onChange={(event) =>
                                changeProblem(problem.problem_id, {
                                  affected_area: event.target.value,
                                })
                              }
                            />
                          </label>
                          <label>
                            Supporting evidence
                            <textarea
                              aria-label={`Supporting evidence for ${name}`}
                              value={problem.supporting_evidence}
                              readOnly={!canEdit || editingBlocked}
                              maxLength={4000}
                              rows={4}
                              onChange={(event) =>
                                changeProblem(problem.problem_id, {
                                  supporting_evidence: event.target.value,
                                })
                              }
                            />
                          </label>
                          <section aria-label={`Evidence links for ${name}`}>
                            <p className="muted">
                              Optional saved evidence links supplement your
                              notes. A link is not verification or approval.
                            </p>
                            {!!problem.evidence_references?.length && (
                              <ul>
                                {problem.evidence_references.map(
                                  (ref, index) => (
                                    <li key={ref.object_id + ref.revision_id}>
                                      <span>
                                        Evidence link {index + 1}:{" "}
                                        {ref.object_id} · version{" "}
                                        {ref.revision_id}
                                      </span>
                                      {canEdit && !editingBlocked && (
                                        <button
                                          type="button"
                                          aria-label={`Remove evidence link ${index + 1} for ${name}`}
                                          onClick={() =>
                                            changeProblem(problem.problem_id, {
                                              evidence_references:
                                                problem.evidence_references!.filter(
                                                  (_, position) =>
                                                    position !== index,
                                                ),
                                            })
                                          }
                                        >
                                          Remove link
                                        </button>
                                      )}
                                    </li>
                                  ),
                                )}
                              </ul>
                            )}
                            {canEdit && !editingBlocked && canReadEvidence && (
                              <button
                                type="button"
                                disabled={
                                  (problem.evidence_references?.length || 0) >=
                                    5 || evidenceBusy
                                }
                                onClick={() =>
                                  void loadEvidence(problem.problem_id)
                                }
                              >
                                Choose saved evidence for {name}
                              </button>
                            )}
                            {canEdit && !canReadEvidence && (
                              <p className="muted">
                                Evidence read access is needed to choose saved
                                evidence. You can still enter supporting notes.
                              </p>
                            )}
                            {evidenceProblem === problem.problem_id && (
                              <fieldset
                                aria-label={`Choose evidence for ${name}`}
                                disabled={evidenceBusy || editingBlocked}
                              >
                                <legend>
                                  Choose one saved evidence version
                                </legend>
                                {evidenceBusy && (
                                  <p role="status">Checking evidence access…</p>
                                )}
                                {evidenceError && (
                                  <p role="alert">{evidenceError}</p>
                                )}
                                {!evidenceBusy &&
                                  !evidenceError &&
                                  !evidenceChoices.length && (
                                    <p>No selectable evidence on this page.</p>
                                  )}
                                <ul>
                                  {evidenceChoices.map((item, index) => (
                                    <li key={item.object_id + item.revision_id}>
                                      <button
                                        type="button"
                                        disabled={
                                          !!problem.evidence_references?.some(
                                            (ref) =>
                                              ref.object_id ===
                                                item.object_id &&
                                              ref.revision_id ===
                                                item.revision_id,
                                          )
                                        }
                                        onClick={() =>
                                          void chooseEvidence(
                                            problem.problem_id,
                                            item,
                                          )
                                        }
                                      >
                                        Select{" "}
                                        {item.data.filename ||
                                          item.data.evidence_type ||
                                          `evidence ${index + 1}`}{" "}
                                        · version {item.revision_id}
                                      </button>
                                    </li>
                                  ))}
                                </ul>
                                {evidenceCursor && (
                                  <button
                                    type="button"
                                    onClick={() =>
                                      void loadEvidence(
                                        problem.problem_id,
                                        evidenceCursor,
                                      )
                                    }
                                  >
                                    Next evidence page
                                  </button>
                                )}
                                <button
                                  type="button"
                                  onClick={() =>
                                    void loadEvidence(problem.problem_id)
                                  }
                                >
                                  Reload evidence choices
                                </button>
                                <button type="button" onClick={clearEvidence}>
                                  Close evidence choices
                                </button>
                              </fieldset>
                            )}
                          </section>
                          {canEdit && !editingBlocked && (
                            <div className="ai-actions">
                              {position < 0 ? (
                                <button
                                  type="button"
                                  aria-label={`Set priority for ${name}`}
                                  onClick={() =>
                                    change({
                                      ...draft,
                                      priority_order: [
                                        ...draft.priority_order,
                                        problem.problem_id,
                                      ],
                                    })
                                  }
                                >
                                  Add to priority order
                                </button>
                              ) : (
                                <>
                                  <button
                                    type="button"
                                    aria-label={`Move ${name} up`}
                                    disabled={position === 0}
                                    onClick={() => move(problem.problem_id, -1)}
                                  >
                                    Move up
                                  </button>
                                  <button
                                    type="button"
                                    aria-label={`Move ${name} down`}
                                    disabled={
                                      position ===
                                      draft.priority_order.length - 1
                                    }
                                    onClick={() => move(problem.problem_id, 1)}
                                  >
                                    Move down
                                  </button>
                                  <button
                                    type="button"
                                    aria-label={`Remove priority for ${name}`}
                                    onClick={() =>
                                      change({
                                        ...draft,
                                        priority_order:
                                          draft.priority_order.filter(
                                            (problemId) =>
                                              problemId !== problem.problem_id,
                                          ),
                                      })
                                    }
                                  >
                                    Remove priority
                                  </button>
                                </>
                              )}
                              <button
                                type="button"
                                aria-label={`Remove ${name}`}
                                onClick={() =>
                                  change({
                                    ...draft,
                                    problems: draft.problems.filter(
                                      (value) =>
                                        value.problem_id !== problem.problem_id,
                                    ),
                                    priority_order: draft.priority_order.filter(
                                      (problemId) =>
                                        problemId !== problem.problem_id,
                                    ),
                                  })
                                }
                              >
                                Remove problem
                              </button>
                            </div>
                          )}
                        </div>
                      </li>
                    );
                  })}
                </ol>
                {canEdit && (
                  <button
                    type="button"
                    disabled={draft.problems.length >= 20 || editingBlocked}
                    onClick={() => {
                      const problemId = crypto.randomUUID();
                      change({
                        ...draft,
                        problems: [
                          ...draft.problems,
                          {
                            problem_id: problemId,
                            description: "",
                            affected_area: "",
                            supporting_evidence: "",
                          },
                        ],
                        priority_order: [...draft.priority_order, problemId],
                      });
                      requestAnimationFrame(() => {
                        if (active())
                          document
                            .getElementById(id + "-description-" + problemId)
                            ?.focus();
                      });
                    }}
                  >
                    Add problem
                  </button>
                )}
              </fieldset>
              {canEdit && (
                <div className="ai-actions">
                  <button
                    type="button"
                    disabled={editingBlocked}
                    onClick={() => command("save")}
                  >
                    {busy ? "Saving…" : "Save diagnosis draft"}
                  </button>
                  <button
                    type="button"
                    disabled={editingBlocked || !head || dirty}
                    onClick={() => command("complete")}
                  >
                    Complete diagnosis
                  </button>
                  {dirty && head && (
                    <p className="muted">
                      Save your changes before completing the diagnosis.
                    </p>
                  )}
                </div>
              )}
              {completed && (
                <>
                  <p>
                    Completed diagnoses are read-only. A correction creates a
                    new draft and keeps the completed revision unchanged.
                  </p>
                  {head?.data.correction_reason && (
                    <p className="ai-diagnosis-text">
                      Previous correction reason: {head.data.correction_reason}
                    </p>
                  )}
                  {canManage && (
                    <fieldset disabled={editingBlocked}>
                      <legend>Start a correction</legend>
                      <label>
                        Reason for correction
                        <textarea
                          aria-label="Reason for diagnosis correction"
                          maxLength={1000}
                          rows={3}
                          value={correctionReason}
                          onChange={(event) =>
                            setCorrectionReason(event.target.value)
                          }
                        />
                      </label>
                      <button
                        type="button"
                        disabled={!correctionReason.trim()}
                        onClick={() => command("revise")}
                      >
                        Create correction draft
                      </button>
                    </fieldset>
                  )}
                </>
              )}
              {!canManage && (
                <p>
                  You can read saved diagnoses. Your administrator can grant
                  diagnosis management permission.
                </p>
              )}
            </>
          )}
        </>
      )}
    </section>
  );
}
