import { useEffect, useRef, useState } from "react";
import {
  provisionalCopyAdapter,
  verifyCopy,
  type CopyAdapter,
  type CopyIntent,
  type CopyManifest,
  type CopyReceipt,
} from "./export-adapter";

type Request = (path: string, options?: RequestInit) => Promise<unknown>;
type Revision = {
  revision_id: string;
  revision_number: number;
  saved_at: string;
};
type History = {
  object_id: string;
  items: Revision[];
  next_cursor: string | null;
};
type Issued = {
  context: string;
  command: CopyIntent;
  manifest: CopyManifest;
  receipt: CopyReceipt;
};
type Props = {
  base: string;
  objectId: string;
  currentRevision: string;
  planTitle: string;
  principalId?: string;
  // Existing exposed identity only; no unique-session-generation claim.
  sessionIdentity?: string;
  canExport: boolean;
  hasUnsavedChanges: boolean;
  hasConflictingMutation: boolean;
  request: Request;
  explain(cause: unknown): string;
  onMutationStateChange?(pending: boolean): void;
  adapter?: CopyAdapter;
};
function authorityFailure(cause: unknown) {
  const code = (cause as { code?: string })?.code;
  return [
    "POLICY_DENIED",
    "RESOURCE_UNAVAILABLE",
    "AUTH_REQUIRED",
    "AUTH_ASSURANCE",
    "IDENTITY_UNAVAILABLE",
    "TENANT_UNAVAILABLE",
    "AUTHORIZATION_FAILED",
  ].includes(code || "");
}
function historyPage(value: unknown, planId: string): History {
  const page = value as History;
  if (
    !page ||
    page.object_id !== planId ||
    !Array.isArray(page.items) ||
    page.items.length > 50 ||
    (page.next_cursor !== null &&
      (typeof page.next_cursor !== "string" || page.next_cursor.length > 4096))
  )
    throw new Error("Saved revision history could not be verified.");
  const ids = new Set<string>();
  for (const item of page.items) {
    if (
      !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
        item.revision_id,
      ) ||
      ids.has(item.revision_id) ||
      !Number.isSafeInteger(item.revision_number) ||
      item.revision_number < 1 ||
      !Number.isFinite(Date.parse(item.saved_at))
    )
      throw new Error("Saved revision history could not be verified.");
    ids.add(item.revision_id);
  }
  return page;
}
const when = (value: string) => new Date(value).toLocaleString();

/** Temporary prototype only: no backend registration, parent integration or release claim. */
export function AIPlanPortability({
  base,
  objectId,
  currentRevision,
  planTitle,
  principalId,
  sessionIdentity,
  canExport,
  hasUnsavedChanges,
  hasConflictingMutation,
  request,
  explain,
  onMutationStateChange,
  adapter = provisionalCopyAdapter,
}: Props) {
  const context = [
    base,
    objectId,
    currentRevision,
    principalId || "",
    sessionIdentity || "",
  ].join("|");
  const current = useRef({
    context,
    canExport,
    hasUnsavedChanges,
    hasConflictingMutation,
  });
  current.current = {
    context,
    canExport,
    hasUnsavedChanges,
    hasConflictingMutation,
  };
  const generation = useRef(0);
  const controller = useRef<AbortController | null>(null);
  const objectUrls = useRef(new Set<string>());
  const timers = useRef(new Set<number>());
  const [activeContext, setActiveContext] = useState(context);
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState(currentRevision);
  const [history, setHistory] = useState<History | null>(null);
  const [acknowledged, setAcknowledged] = useState(false);
  const [busy, setBusy] = useState(false);
  const [pending, setPending] = useState<CopyIntent | null>(null);
  const [issued, setIssued] = useState<Issued | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const visibleIssued =
    issued?.context === context && canExport ? issued : null;
  const visiblePending =
    pending?.context === context && canExport ? pending : null;
  const contextVisible = activeContext === context;
  const visibleHistory = contextVisible && canExport ? history : null;
  const newCommandBlocked =
    !canExport ||
    busy ||
    !!visiblePending ||
    hasUnsavedChanges ||
    hasConflictingMutation;

  function revokeUrls() {
    for (const id of timers.current) window.clearTimeout(id);
    timers.current.clear();
    for (const url of objectUrls.current) URL.revokeObjectURL(url);
    objectUrls.current.clear();
  }
  function clearPrivate() {
    revokeUrls();
    setIssued(null);
    setPending(null);
    setHistory(null);
    setAcknowledged(false);
    setSelected(currentRevision);
  }
  useEffect(() => {
    generation.current++;
    controller.current?.abort();
    clearPrivate();
    setActiveContext(context);
    setOpen(false);
    setBusy(false);
    setError("");
    setNotice("");
    return () => {
      generation.current++;
      controller.current?.abort();
      revokeUrls();
    };
  }, [context, canExport]);
  useEffect(() => {
    onMutationStateChange?.(busy || !!visiblePending);
    return () => onMutationStateChange?.(false);
  }, [busy, !!visiblePending, onMutationStateChange]);
  function stillCurrent(epoch: number, key: string) {
    return (
      generation.current === epoch &&
      current.current.context === key &&
      current.current.canExport
    );
  }
  function fail(cause: unknown) {
    revokeUrls();
    setIssued(null);
    setNotice("");
    if ((cause as { code?: string })?.code === "IDEMPOTENCY_EXPIRED") {
      // A definitive server expiry cannot be replayed. Release the parent
      // lock, clear the old copy, and require a new deliberate acknowledgement.
      clearPrivate();
      setError(
        "This previous copy request can no longer be replayed. Your plan draft was not changed. You may deliberately prepare a new saved copy.",
      );
    } else if (authorityFailure(cause)) {
      clearPrivate();
      setError("An internal copy is unavailable with your current access.");
    } else setError(explain(cause));
  }
  async function readHistory(more = false) {
    if (newCommandBlocked) return;
    const epoch = generation.current;
    const key = context;
    const cursor = more ? history?.next_cursor : null;
    if (more && !cursor) return;
    const active = new AbortController();
    controller.current = active;
    setBusy(true);
    setError("");
    try {
      const result = historyPage(
        await request(
          `${base}ai-enablement/plans/${objectId}/revisions?limit=50${cursor ? "&cursor=" + encodeURIComponent(cursor) : ""}`,
          { signal: active.signal },
        ),
        objectId,
      );
      if (!stillCurrent(epoch, key)) return;
      setHistory((previous) => {
        const rows = more
          ? [...(previous?.items || []), ...result.items]
          : result.items;
        const seen = new Set<string>();
        return {
          object_id: objectId,
          items: rows.filter((item) => {
            if (seen.has(item.revision_id)) return false;
            seen.add(item.revision_id);
            return true;
          }),
          next_cursor: result.next_cursor,
        };
      });
    } catch (cause) {
      if (stillCurrent(epoch, key) && !active.signal.aborted) {
        clearPrivate();
        fail(cause);
      }
    } finally {
      if (generation.current === epoch && current.current.context === key)
        setBusy(false);
    }
  }
  function newIntent(): CopyIntent {
    if (
      selected !== currentRevision &&
      !history?.items.some((row) => row.revision_id === selected)
    )
      throw new Error("Choose an authorised loaded saved revision.");
    const operationId = crypto.randomUUID();
    return {
      context,
      revision: selected,
      path: adapter.path(base, objectId, selected),
      body: JSON.stringify(adapter.command(operationId)),
      operationId,
      action: "PREPARE",
    };
  }
  async function execute(command: CopyIntent, previous?: CopyManifest) {
    if (
      busy ||
      !canExport ||
      command.context !== context ||
      hasConflictingMutation
    )
      return;
    const epoch = generation.current;
    const key = context;
    const active = new AbortController();
    controller.current = active;
    setBusy(true);
    setPending(command);
    setError("");
    setNotice("");
    revokeUrls();
    try {
      const reply = adapter.decode(
        await request(command.path, {
          method: "POST",
          body: command.body,
          signal: active.signal,
        }),
      );
      if (!stillCurrent(epoch, key)) return;
      await verifyCopy(
        reply,
        objectId,
        command.revision,
        previous || command.expectedManifest,
        command.operationId,
        command.expectedReceipt,
      );
      if (!stillCurrent(epoch, key)) return;
      // No content string or Blob is retained between clicks. Every download
      // replays this exact command through the server's current authority gate.
      setIssued({
        context: key,
        command: { ...command, action: "PREPARE" },
        manifest: reply.manifest,
        receipt: reply.receipt,
      });
      setPending(null);
      if (command.action === "DOWNLOAD") {
        if (
          current.current.hasUnsavedChanges ||
          current.current.hasConflictingMutation
        ) {
          setNotice(
            "The saved copy was verified. Your plan changed locally, so no download was started.",
          );
          return;
        }
        const url = URL.createObjectURL(
          new Blob([reply.content], { type: reply.manifest.media_type }),
        );
        objectUrls.current.add(url);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = reply.manifest.filename;
        anchor.hidden = true;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        const timer = window.setTimeout(() => {
          URL.revokeObjectURL(url);
          objectUrls.current.delete(url);
          timers.current.delete(timer);
        }, 1000);
        timers.current.add(timer);
        setNotice(
          "The exact issued JSON copy was offered to your browser. Check your downloads to confirm it was saved.",
        );
      } else
        setNotice(
          "The exact saved copy was verified. Downloading it will recheck your current permission.",
        );
    } catch (cause) {
      if (stillCurrent(epoch, key) && !active.signal.aborted) fail(cause);
      // A transport/verification failure keeps this exact operation and body;
      // it never silently starts a second issuance.
    } finally {
      if (generation.current === epoch && current.current.context === key)
        setBusy(false);
    }
  }
  function prepare() {
    if (newCommandBlocked || !acknowledged) return;
    try {
      void execute(newIntent());
    } catch (cause) {
      fail(cause);
    }
  }
  function choose(value: string) {
    if (newCommandBlocked) return;
    if (
      value !== currentRevision &&
      !history?.items.some((item) => item.revision_id === value)
    )
      return;
    revokeUrls();
    setSelected(value);
    setIssued(null);
    setAcknowledged(false);
    setError("");
    setNotice("");
  }
  return (
    <section
      className="ai-plan-portability card"
      aria-label="Internal copy of this saved AI plan"
    >
      <h3>Internal copy of your saved plan</h3>
      <p>
        Download an exact saved revision as JSON for your own organisation work.
        Local draft edits are excluded.
      </p>
      <p>
        This is a saved draft planning record. It does not approve procurement,
        certify competence or establish official programme impact.
      </p>
      <p>
        Read or manage permission does not grant export permission. A downloaded
        copy cannot be recalled; a server replay expiry does not make a local
        file expire.
      </p>
      {!canExport && (
        <p>An internal copy is unavailable with your current access.</p>
      )}
      <button
        type="button"
        className="secondary"
        disabled={!canExport || busy || !!visiblePending}
        onClick={() => setOpen((value) => !value)}
      >
        {open ? "Hide internal copy options" : "Prepare an internal saved copy"}
      </button>
      {open && canExport && contextVisible && (
        <>
          {error && <p role="alert">{error}</p>}
          {notice && <p role="status">{notice}</p>}
          {hasUnsavedChanges && (
            <p>
              Save or discard local plan edits before preparing or downloading a
              copy. An uncertain previous request can still be retried exactly.
            </p>
          )}
          {hasConflictingMutation && (
            <p>Wait for the other saved-plan change to finish.</p>
          )}
          <p>Opened saved plan: {planTitle}.</p>
          <label>
            Saved revision for this copy
            <select
              aria-label="Copy saved revision"
              value={selected}
              disabled={newCommandBlocked}
              onChange={(event) => choose(event.target.value)}
            >
              <option value={currentRevision}>Opened saved revision</option>
              {visibleHistory?.items
                .filter((row) => row.revision_id !== currentRevision)
                .map((row) => (
                  <option key={row.revision_id} value={row.revision_id}>
                    Revision {row.revision_number} · {when(row.saved_at)}
                  </option>
                ))}
            </select>
          </label>
          <div className="actions">
            <button
              type="button"
              className="secondary"
              disabled={newCommandBlocked}
              onClick={() => void readHistory()}
            >
              Load authorised saved revisions
            </button>
            {visibleHistory?.next_cursor && (
              <button
                type="button"
                className="secondary"
                disabled={newCommandBlocked}
                onClick={() => void readHistory(true)}
              >
                Load more saved revisions
              </button>
            )}
          </div>
          {visibleHistory && (
            <p>
              Only the loaded authorised revisions are shown. Selecting one does
              not save or issue a copy.
            </p>
          )}
          <label className="check">
            <input
              type="checkbox"
              checked={acknowledged}
              disabled={newCommandBlocked}
              onChange={(event) => setAcknowledged(event.target.checked)}
            />
            I understand this is an internal copy for me, and downloaded files
            cannot be recalled.
          </label>
          <button
            type="button"
            disabled={newCommandBlocked || !acknowledged}
            onClick={prepare}
          >
            Confirm and issue internal JSON copy
          </button>
          {visiblePending && (
            <button
              type="button"
              className="secondary"
              disabled={busy || hasConflictingMutation}
              onClick={() =>
                void execute(visiblePending, visibleIssued?.manifest)
              }
            >
              Retry previous copy request
            </button>
          )}
          {visibleIssued && !visiblePending && (
            <div role="group" aria-label="Verified issued copy">
              <h4>{visibleIssued.manifest.title}</h4>
              <p>
                Saved {when(visibleIssued.manifest.saved_at)}. Issued{" "}
                {when(visibleIssued.manifest.generated_at)}.
              </p>
              <p>JSON · {visibleIssued.manifest.size_bytes} bytes.</p>
              <details>
                <summary>Copy format and integrity details</summary>
                <p>Package: {visibleIssued.manifest.schema}.</p>
                <p>Renderer: {visibleIssued.manifest.renderer}.</p>
                <p>SHA-256: {visibleIssued.manifest.content_sha256}.</p>
              </details>
              <p>
                Saved guidance coverage:{" "}
                {visibleIssued.manifest.guidance_status.toLowerCase()}. This
                copy preserves the saved archive; it does not regenerate missing
                guidance.
              </p>
              <p>
                Server replay available until{" "}
                {when(visibleIssued.manifest.replay_expires_at)}. A local copy
                keeps working after this time.
              </p>
              <button
                type="button"
                disabled={
                  newCommandBlocked ||
                  Date.now() >=
                    Date.parse(visibleIssued.manifest.replay_expires_at)
                }
                onClick={() =>
                  void execute({
                    ...visibleIssued.command,
                    action: "DOWNLOAD",
                    expectedManifest: visibleIssued.manifest,
                    expectedReceipt: visibleIssued.receipt,
                  })
                }
              >
                Download issued copy
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}
