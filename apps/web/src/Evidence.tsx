import React, { useEffect, useRef, useState } from "react";

// Evidence cited by an observation or a calculated result (v0.22): list the cited evidence
// revisions, download a CLEAN file through the API, and attach a new file. Buttons follow
// /me/access; the server re-checks every capability, owner and scan verdict.
type Attachment = {
  attachment_id: string;
  evidence_id: string;
  evidence_revision: string;
  evidence_revision_number?: number;
  evidence_head_revision?: string;
  target_revision: string;
  target_is_current?: boolean;
  evidence_type?: string | null;
  filename?: string | null;
  media_type?: string | null;
  byte_size?: number | null;
  external_reference?: string | null;
  scan_state?: string | null;
  downloadable?: boolean;
  reason?: string;
  attached_at?: string;
};
type Target = { object_id: string; revision_id: string };
const MEDIA: Record<string, string> = {
  pdf: "application/pdf",
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  txt: "text/plain",
  csv: "text/csv",
};
const REASONS: Record<string, string> = {
  MEDIA_TYPE_NOT_ALLOWED:
    "Only PDF, PNG, JPEG, plain text and CSV files can be attached.",
  FILE_EXTENSION_MISMATCH:
    "The file name's extension does not match a permitted type.",
  FILENAME_INVALID:
    "Rename the file: the name contains unsupported characters.",
  FILE_TOO_LARGE: "Files are limited to 25 MB.",
  CONTENT_TYPE_MISMATCH:
    "The file's content does not match its type. It was not stored.",
  EXECUTABLE_REFUSED: "Executable content is not accepted.",
  ACTIVE_CONTENT_REFUSED:
    "PDFs with scripts, actions or embedded files are not accepted.",
  HASH_MISMATCH: "The file changed while uploading. Try again.",
  UPLOAD_NOT_CLEAN:
    "The file did not pass the safety scan and cannot be used as evidence.",
  EVIDENCE_ALREADY_ATTACHED: "This evidence version is already attached.",
  TARGET_REVISION_CHANGED:
    "This record changed since you opened it. Reload it before attaching.",
  OBJECT_STORE_NOT_CONFIGURED:
    "Evidence storage is not configured for this workspace.",
};

async function call(
  path: string,
  token: () => string,
  init: RequestInit = {},
): Promise<any> {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...init,
    headers: {
      Accept: "application/json",
      ...(init.method && init.method !== "GET"
        ? { "X-CSRF-Token": token() }
        : {}),
      ...(init.headers || {}),
    },
  });
  const data = await response.json();
  if (!response.ok) {
    const reason = data.reason_code || "";
    throw new Error(
      REASONS[reason] ||
        (data.code === "POLICY_DENIED" || data.code === "RESOURCE_UNAVAILABLE"
          ? "You do not have access to do this."
          : data.message || "The request could not be completed."),
    );
  }
  return data;
}

function json(body: unknown): RequestInit {
  return {
    method: "POST",
    body: JSON.stringify(body),
    headers: { "Content-Type": "application/json" },
  };
}

export function EvidencePanel({
  base,
  route,
  row,
  allowed,
  token,
}: {
  base: string;
  route: "observations" | "calculated-results";
  row: Target;
  allowed: (cap: string) => boolean;
  token: () => string;
}) {
  const [items, setItems] = useState<Attachment[]>([]),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [version, setVersion] = useState(0);
  // One identifier per step for the life of this panel: a retried click repeats the same command.
  const operations = useRef<Record<string, string>>({});
  const op = (key: string) => (operations.current[key] ||= crypto.randomUUID());
  const canRead = allowed("evidence.read");
  const canAttach =
    allowed("upload.create") &&
    allowed("upload.write") &&
    allowed("evidence.draft.create") &&
    allowed("evidence.attach");
  useEffect(() => {
    if (!canRead) return;
    const c = new AbortController();
    call(base + route + "/" + row.object_id + "/evidence", token, {
      signal: c.signal,
    })
      .then((page) => setItems(page.items))
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    return () => c.abort();
  }, [base, route, row.object_id, version, canRead]);
  if (!canRead) return null;

  async function attach(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const file = form.get("file") as File | null;
    if (!file || !file.size) return setError("Choose a file.");
    const extension = file.name.split(".").pop()?.toLowerCase() || "";
    const media = MEDIA[extension];
    if (!media) return setError(REASONS.MEDIA_TYPE_NOT_ALLOWED);
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const bytes = await file.arrayBuffer();
      const digest = Array.from(
        new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)),
      )
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("");
      const key = digest + ":" + file.name;
      const upload = await call(
        base + "uploads",
        token,
        json({
          operation_id: op("upload:" + key),
          data: {
            purpose: "EVIDENCE_MEDIA",
            content_type: media,
            expected_bytes: bytes.byteLength,
            content_sha256: digest,
            mode: "WHOLE",
            filename: file.name,
          },
        }),
      );
      const received = await call(
        base + "uploads/" + upload.upload_id + "/content",
        token,
        {
          method: "PUT",
          body: bytes,
          headers: { "Content-Type": "application/octet-stream" },
        },
      );
      const sealed = await call(
        base + "uploads/" + upload.upload_id + "/actions/complete",
        token,
        json({
          operation_id: op("complete:" + upload.upload_id),
          expected_revision: received.revision_id,
          data: { content_sha256: digest, parts: [] },
        }),
      );
      if (sealed.state !== "CLEAN")
        throw new Error(
          sealed.scan_state === "INFECTED"
            ? "The file was flagged by the safety scan and was not attached."
            : "The file could not be scanned and was not attached.",
        );
      const saved = await call(
        base + "evidence",
        token,
        json({
          operation_id: op("evidence:" + upload.upload_id),
          data: {
            upload_id: upload.upload_id,
            evidence_type: String(form.get("evidence_type")),
            source: String(form.get("source") || file.name),
          },
        }),
      );
      await call(
        base + "evidence/" + saved.object_id + "/actions/attach",
        token,
        json({
          operation_id: op("attach:" + saved.revision_id),
          expected_revision: saved.revision_id,
          data: {
            target_kind:
              route === "observations" ? "Observation" : "CalculatedResult",
            target_id: row.object_id,
            target_revision: row.revision_id,
            reason: String(form.get("reason")),
          },
        }),
      );
      operations.current = {};
      setNotice("Evidence attached to this revision.");
      setVersion((v) => v + 1);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-label="Evidence" className="evidence-panel">
      <h3>Evidence</h3>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {notice && <p role="status">{notice}</p>}
      {items.length === 0 ? (
        <p className="muted">No evidence is attached to this record.</p>
      ) : (
        <ul>
          {items.map((item) => (
            <li key={item.attachment_id}>
              <strong>{item.filename || item.external_reference}</strong>{" "}
              <span className="muted">
                {item.evidence_type} · version{" "}
                {item.evidence_revision_number ?? "?"}
                {item.evidence_head_revision !== item.evidence_revision &&
                  " (a newer version exists)"}
                {!item.target_is_current && " · cited by an earlier revision"}
              </span>
              {item.downloadable && (
                <>
                  {" "}
                  <a
                    href={
                      base +
                      "evidence/" +
                      item.evidence_id +
                      "/content?revision=" +
                      item.evidence_revision
                    }
                  >
                    Download
                  </a>
                </>
              )}
              {item.reason && <div className="muted">{item.reason}</div>}
            </li>
          ))}
        </ul>
      )}
      {canAttach && (
        <form onSubmit={attach} aria-label="Attach evidence">
          <label>
            File (PDF, PNG, JPEG, TXT or CSV, at most 25 MB)
            <input
              name="file"
              type="file"
              required
              accept=".pdf,.png,.jpg,.jpeg,.txt,.csv"
            />
          </label>
          <label>
            Evidence type
            <select name="evidence_type" defaultValue="SUPPORTING_DOCUMENT">
              <option value="SUPPORTING_DOCUMENT">Supporting document</option>
              <option value="ATTENDANCE_SHEET">Attendance sheet</option>
              <option value="PHOTOGRAPH">Photograph</option>
              <option value="DATA_EXTRACT">Data extract</option>
            </select>
          </label>
          <label>
            Source
            <input
              name="source"
              maxLength={2000}
              placeholder="Where it came from"
            />
          </label>
          <label>
            Why it supports this record
            <input name="reason" required maxLength={2000} />
          </label>
          <p className="muted">
            Files are checked for their real type and scanned before anyone can
            download them. The scan in this build recognises only the standard
            anti-virus test file; it is not malware protection.
          </p>
          <button className="primary" disabled={busy}>
            {busy ? "Attaching…" : "Upload and attach"}
          </button>
        </form>
      )}
    </section>
  );
}
