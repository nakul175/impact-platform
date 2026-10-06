import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/src/styles.css";
import "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/src/ai-enablement.css";
import { AIAdoptionWorkspace } from "./AIAdoptionWorkspace";

import type { Catalog, Profile } from "./AIEnablement";
const clone = <T,>(value: T): T => structuredClone(value);
const profile: Profile = {
  sector: "GENERAL",
  team_size: 5,
  goal: "",
  data_readiness: "BASIC",
  ai_experience: "EXPERIMENTING",
  sensitive_data: false,
};
const catalog: Catalog = {
  content_version: "invented-catalog-v1",
  advisory_available: false,
  journey: [],
  use_cases: [],
  learning_paths: [
    {
      id: "foundation",
      title: "Invented foundation",
      steps: [],
      lessons: [
        {
          key: "known-lesson",
          title: "Invented lesson",
          lesson: "Invented reading",
          exercise: "Invented exercise",
          check: {
            question: "Human review?",
            options: ["Yes", "No"],
            answer: 0,
            explanation: "Invented test",
          },
        },
      ],
    },
  ],
  procurement_criteria: [
    {
      id: "boundary",
      title: "Data boundary",
      questions: ["What is retained?", "How is data deleted?"],
    },
  ],
  marketplace_status: {
    status: "DRAFT",
    explanation: "Synthetic fixture only",
  },
};
const solutions = {
  content_version: "invented-solutions-v1",
  checked_on: "2026-10-05",
  explanation: "Synthetic fixture",
  solutions: ["first", "second"].map((id, index) => ({
    id,
    name: index === 0 ? "First Café" : "Second supplied tool",
    provider: "Invented",
    category: "GENERAL_ASSISTANT",
    use_case_ids: [],
    description: "Invented fixture",
    deployment: "Hosted",
    commercial_model: "Verify",
    nonprofit_offer: "Verify",
    api_available: "Verify",
    source_urls: [],
    verification_notes: [],
    data_review_questions: [
      index === 0 ? "Who can access it?" : "What can be exported?",
    ],
  })),
  comparison_criteria: [],
};
const savedProfile: Profile = {
  ...profile,
  goal: "Saved canonical Café goal",
  team_size: 12,
};
const seed = {
  object_id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
  revision_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  business_state: "Draft",
  data: {
    title: "Private procurement source",
    profile: savedProfile,
    solution_ids: ["first", "second"],
    learning_completed: ["known-lesson"],
    procurement: {
      requirements: "Own Café\nrequirements",
      data_boundary: "Own approved boundary notes",
      budget_notes: "Own budget notes",
      vendor_questions: "Own supplier questions",
    },
    pilot: {
      success_measure: "Existing manual pilot criterion",
      completed_actions: ["DEFINE_GOAL"],
    },
    planning: {
      cost_comparison: null,
      pilot_evaluation: null,
      task_practice: {
        template_id: "invented-task",
        brief: "Existing invented brief",
        draft: "Own exact learner Café\ndraft",
        review_notes: "Own exact review notes",
        checked_steps: ["own-step"],
      },
    },
    content_versions: {
      catalog: catalog.content_version,
      solutions: solutions.content_version,
    },
  },
};

let row = clone(seed),
  calls: { path: string; method: string; body?: any }[] = [],
  holdRead = false,
  readHeld = false,
  releaseRead: (() => void) | null = null,
  holdSave = false,
  saveHeld = false,
  releaseSave: (() => void) | null = null;
async function request(path: string, options: RequestInit = {}) {
  const method = options.method || "GET",
    body = options.body ? JSON.parse(String(options.body)) : undefined;
  calls.push({ path, method, ...(body ? { body } : {}) });
  if (path.endsWith("/solutions")) return clone(solutions);
  if (path.includes("plans?limit"))
    return { items: [clone(row)], next_cursor: null };
  if (path.includes("/revisions?")) return { items: [], next_cursor: null };
  if (path.endsWith("/plans/" + row.object_id)) {
    if (method === "GET") {
      const captured = clone(row);
      if (holdRead) {
        holdRead = false;
        readHeld = true;
        await new Promise<void>((resolve) => (releaseRead = resolve));
        readHeld = false;
      }
      return captured;
    }
    if (method === "PUT") {
      if (holdSave) {
        holdSave = false;
        saveHeld = true;
        await new Promise<void>((resolve) => (releaseSave = resolve));
        saveHeld = false;
      }
      row = {
        ...row,
        revision_id: crypto.randomUUID(),
        data: { ...body.data, content_versions: row.data.content_versions },
      };
      return {
        object_id: row.object_id,
        revision_id: row.revision_id,
        business_state: "Draft",
      };
    }
  }
  throw {
    code: "RESOURCE_UNAVAILABLE",
    reason: "Synthetic fixture has no response",
  };
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
      <button type="button" onClick={close}>
        Close
      </button>
    </div>
  );
}
function App() {
  const [currentProfile, setProfile] = useState(clone(profile)),
    [canRead, setRead] = useState(true),
    [currentContext, setContext] = useState({
      base: "/v1/tenants/invented/",
      principal: "invented-editor",
      session: "invented-session",
    });
  Object.assign(window, {
    fixture: {
      calls: () => clone(calls),
      row: () => clone(row),
      profile: () => clone(currentProfile),
      patchProfile: (patch: Partial<Profile>) =>
        setProfile((previous) => ({ ...previous, ...patch })),
      holdRead: () => (holdRead = true),
      readHeld: () => readHeld,
      releaseRead: () => {
        releaseRead?.();
        releaseRead = null;
      },
      holdSave: () => (holdSave = true),
      saveHeld: () => saveHeld,
      releaseSave: () => {
        releaseSave?.();
        releaseSave = null;
      },
      canRead: setRead,
      newContext: () => {
        setProfile({ ...profile, goal: "Clean new context brief" });
        setContext({
          base: "/v1/tenants/another-invented/",
          principal: "another-invented-editor",
          session: "another-invented-session",
        });
      },
    },
  });
  return (
    <main className="ai-enablement">
      <h1>Private profile preservation</h1>
      <p>
        Actual candidate React source with synthetic in-memory requests. No real
        API or authority proof.
      </p>
      <label>
        AI goal
        <textarea
          aria-label="AI goal"
          value={currentProfile.goal}
          onChange={(event) =>
            setProfile((previous) => ({
              ...previous,
              goal: event.target.value,
            }))
          }
        />
      </label>
      <label>
        Team size
        <input
          aria-label="Team size"
          type="number"
          value={currentProfile.team_size}
          onChange={(event) =>
            setProfile((previous) => ({
              ...previous,
              team_size: Number(event.target.value),
            }))
          }
        />
      </label>
      <AIAdoptionWorkspace
        base={currentContext.base}
        principalId={currentContext.principal}
        sessionIdentity={currentContext.session}
        request={request}
        explain={(error) => String((error as any).reason || error)}
        capabilities={
          canRead
            ? ["ai.enablement.read", "ai.enablement.manage"]
            : ["ai.enablement.manage"]
        }
        profile={currentProfile}
        catalog={catalog}
        onLoadProfile={setProfile}
        Dialog={Dialog}
      />
    </main>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
