import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { AIPlanReviewChecklist } from "./AIPlanReviewChecklist";
import { AIAdoptionWorkspace } from "./AIAdoptionWorkspace.fixture";
import { captureReviewSnapshot } from "./review-model";
import { context, plan } from "./fixtures";
import type {
  ReviewContext,
  ReviewHead,
  ReviewSnapshot,
  ReviewTab,
} from "./review-model";
import type { Catalog } from "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/src/AIEnablement";
import "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/src/ai-enablement.css";
import "./ui-fixture.css";
type State = {
  context: ReviewContext;
  head: ReviewHead | null;
  canRead: boolean;
  dirty: boolean;
  mutation: boolean;
  unavailable: boolean;
  mode: "direct" | "workspace";
};
type Fixture = {
  patch(value: Partial<State>): void;
  capture(): void;
  row(value: unknown): void;
  failNext(): void;
  holdNext(): void;
  release(): void;
  calls(): unknown[];
  navigation(): ReviewTab[];
  profileGoal(value: string): void;
};
declare global {
  interface Window {
    fixture: Fixture;
  }
}
let row: any = plan(),
  failure = false,
  hold = false,
  release: (() => void) | null = null;
const calls: { path: string; method: string; body?: string }[] = [],
  navigation: ReviewTab[] = [];
const clone = <T,>(value: T): T => structuredClone(value);
const catalog: Catalog = {
  content_version: "synthetic-catalog",
  advisory_available: false,
  journey: [],
  use_cases: [],
  learning_paths: [],
  procurement_criteria: [],
  marketplace_status: { status: "DRAFT", explanation: "Synthetic fixture" },
};
async function request(path: string, options: RequestInit = {}) {
  calls.push({
    path,
    method: options.method || "GET",
    ...(options.body ? { body: String(options.body) } : {}),
  });
  if (path.endsWith("/solutions"))
    return {
      content_version: "synthetic-solutions",
      checked_on: "2026-10-05",
      explanation: "Synthetic fixture",
      solutions: [],
      comparison_criteria: [],
    };
  if (path.includes("plans?limit"))
    return { items: [clone(row)], next_cursor: null };
  if (options.method === "PUT" || options.method === "POST") {
    const data = JSON.parse(String(options.body)).data;
    row = {
      ...row,
      revision_id: "33333333-3333-4333-8333-333333333333",
      data: {
        ...data,
        content_versions: {
          catalog: "synthetic-catalog",
          solutions: "synthetic-solutions",
        },
      },
    };
    return {
      object_id: row.object_id,
      revision_id: row.revision_id,
      business_state: "Draft",
    };
  }
  if (path.endsWith("/plans/" + row.object_id)) {
    if (hold) {
      hold = false;
      await new Promise<void>((resolve) => {
        release = resolve;
      });
    }
    if (failure) {
      failure = false;
      throw { code: "RESOURCE_UNAVAILABLE", reason: "CURRENT_AUTHORITY" };
    }
    return clone(row);
  }
  throw new Error("Unplanned fixture request");
}
function Dialog({
  title,
  close,
  children,
}: {
  title: string;
  close: () => void;
  children: React.ReactNode;
}) {
  return (
    <div role="dialog" aria-label={title}>
      {children}
      <button onClick={close}>Close</button>
    </div>
  );
}
function App() {
  const [state, setState] = useState<State>({
    context,
    head: { object_id: row.object_id, revision_id: row.revision_id },
    canRead: true,
    dirty: false,
    mutation: false,
    unavailable: false,
    mode: "direct",
  });
  const [snapshot, setSnapshot] = useState<ReviewSnapshot | null>(
    captureReviewSnapshot(row, context),
  );
  const [profile, setProfile] = useState(clone(row.data.profile));
  useEffect(() => {
    if (state.dirty || !state.canRead || state.unavailable) setSnapshot(null);
  }, [state.dirty, state.canRead, state.unavailable]);
  window.fixture = {
    patch: (value) => setState((s) => ({ ...s, ...value })),
    capture: () => setSnapshot(captureReviewSnapshot(row, state.context)),
    row: (value) => {
      row = clone(value);
    },
    failNext: () => {
      failure = true;
    },
    holdNext: () => {
      hold = true;
    },
    release: () => {
      release?.();
      release = null;
    },
    calls: () => clone(calls),
    navigation: () => clone(navigation),
    profileGoal: (value) => setProfile((p: any) => ({ ...p, goal: value })),
  };
  return (
    <main className="ai-enablement">
      <h1>Private saved-plan review prototype</h1>
      <p>
        In-memory request-function fixture. No application API or backend
        authority qualification.
      </p>
      {state.mode === "direct" ? (
        <AIPlanReviewChecklist
          key={
            state.context.base +
            state.context.principalId +
            state.context.sessionIdentity +
            state.head?.object_id
          }
          snapshot={snapshot}
          currentContext={state.context}
          openedHead={state.head}
          canRead={state.canRead}
          canonicalUnavailable={state.unavailable}
          hasUnsavedChanges={state.dirty}
          hasConflictingMutation={state.mutation}
          onOpenSection={(tab) => navigation.push(tab)}
        />
      ) : (
        <AIAdoptionWorkspace
          base={state.context.base}
          principalId={state.context.principalId}
          sessionIdentity={state.context.sessionIdentity}
          request={request}
          explain={() => "Saved source unavailable"}
          capabilities={
            state.canRead ? ["ai.enablement.read", "ai.enablement.manage"] : []
          }
          profile={profile}
          catalog={catalog}
          onLoadProfile={setProfile}
          Dialog={Dialog}
        />
      )}
    </main>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
