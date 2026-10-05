import { createRoot } from "react-dom/client";
import { useState } from "react";
import { AIPlanPortability } from "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/src/AIPlanPortability";
import {
  COPY_SCHEMA,
  COPY_RENDERER,
} from "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/src/AIPlanExportAdapter";
import "./ui-fixture.css";
import "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/src/ai-enablement.css";

const PLAN = "11111111-1111-4111-8111-111111111111",
  REV = "22222222-2222-4222-8222-222222222222",
  OLD = "77777777-7777-4777-8777-777777777777";
type State = {
  canExport: boolean;
  hasUnsavedChanges: boolean;
  hasConflictingMutation: boolean;
  principalId: string;
  sessionIdentity: string;
  currentRevision: string;
};
const calls: { path: string; method: string; body?: string }[] = [];
const issued = new Map<string, any>();
let mode = "normal",
  delayed: (() => void) | null = null;
let parentPending = false;
async function makeReply(path: string, body: string) {
  const command = JSON.parse(body),
    revision = path.split("/").at(-2);
  if (issued.has(command.operation_id))
    return structuredClone(issued.get(command.operation_id));
  const content =
    "\n" +
    JSON.stringify(
      {
        record_status: "Draft",
        restriction: "INTERNAL_SELF",
        title: "Synthetic Café — समुदाय",
        revision,
        archive_status: "PARTIAL",
      },
      null,
      2,
    ) +
    "\n";
  const bytes = new TextEncoder().encode(content),
    digest = await crypto.subtle.digest("SHA-256", bytes),
    sha = [...new Uint8Array(digest)]
      .map((x) => x.toString(16).padStart(2, "0"))
      .join("");
  const generated = new Date().toISOString(),
    until = new Date(Date.now() + 604800000).toISOString();
  const reply = {
    content,
    manifest: {
      plan_id: PLAN,
      revision_id: revision,
      title: "Synthetic Café — समुदाय",
      saved_at: "2026-10-05T08:00:00Z",
      generated_at: generated,
      schema: COPY_SCHEMA,
      renderer: COPY_RENDERER,
      filename: `impact-ai-plan-${PLAN}.json`,
      media_type: "application/json",
      content_sha256: sha,
      size_bytes: bytes.length,
      replay_expires_at: until,
      guidance_status: "PARTIAL",
    },
    receipt: {
      object_id: crypto.randomUUID(),
      revision_id: crypto.randomUUID(),
      business_state: "Issued",
      operation_id: command.operation_id,
      correlation_id: crypto.randomUUID(),
      saved_at: generated,
      content_sha256: sha,
      byte_count: bytes.length,
      replay_until: until,
    },
  };
  issued.set(command.operation_id, structuredClone(reply));
  return reply;
}
const request = async (path: string, options?: RequestInit) => {
  calls.push({
    path,
    method: options?.method || "GET",
    body: typeof options?.body === "string" ? options.body : undefined,
  });
  if (mode === "assurance") {
    mode = "normal";
    throw {
      code: "ASSURANCE_REQUIRED",
      reason: "FRESH_AUTHENTICATION_REQUIRED",
    };
  }
  if (mode === "authority") {
    mode = "normal";
    throw { code: "RESOURCE_UNAVAILABLE" };
  }
  if (mode === "expired") {
    mode = "normal";
    throw { code: "IDEMPOTENCY_EXPIRED" };
  }
  if (mode === "wrong-history" && !options?.method) {
    mode = "normal";
    return {
      object_id: OLD,
      items: [
        {
          revision_id: OLD,
          revision_number: 1,
          saved_at: "2026-10-05T07:00:00Z",
        },
      ],
      next_cursor: null,
    };
  }
  if (!options?.method)
    return {
      object_id: PLAN,
      items: [
        {
          revision_id: OLD,
          revision_number: 1,
          saved_at: "2026-10-05T07:00:00Z",
        },
      ],
      next_cursor: null,
    };
  const reply = await makeReply(path, String(options.body));
  if (mode === "lost") {
    mode = "normal";
    throw new Error("Synthetic response lost after issuance.");
  }
  if (mode === "delay") {
    mode = "normal";
    await new Promise<void>((resolve) => {
      delayed = resolve;
    });
  }
  return reply;
};
function Fixture() {
  const [state, setState] = useState<State>({
    canExport: true,
    hasUnsavedChanges: false,
    hasConflictingMutation: false,
    principalId: "synthetic-author",
    sessionIdentity: "synthetic-identity",
    currentRevision: REV,
  });
  (window as any).fixture = {
    patch: (v: Partial<State>) => setState((s) => ({ ...s, ...v })),
    mode: (v: string) => {
      mode = v;
    },
    calls: () => structuredClone(calls),
    pending: () => parentPending,
    release: () => {
      delayed?.();
      delayed = null;
    },
    tamperReceipt: () => {
      for (const reply of issued.values())
        reply.receipt.object_id = crypto.randomUUID();
    },
    issued: () => structuredClone([...issued.values()]),
    selectors: { PLAN, REV, OLD },
  };
  return (
    <main className="ai-enablement">
      <h1>Temporary synthetic internal-copy fixture</h1>
      <p>
        This in-memory request fixture does not qualify a backend or
        authorisation policy.
      </p>
      <h2>AI workspace</h2>
      <h3>Opened saved AI plan</h3>
      <AIPlanPortability
        base="/v1/tenants/synthetic/"
        objectId={PLAN}
        planTitle="Synthetic saved plan"
        {...state}
        request={request}
        explain={(cause) =>
          cause instanceof Error ? cause.message : "Request unavailable"
        }
        onMutationStateChange={(v) => {
          parentPending = v;
        }}
      />
    </main>
  );
}
createRoot(document.getElementById("root")!).render(<Fixture />);
