import { useState } from "react";
import { AILearningLesson } from "./AILearningLesson";
import { AIToolComparison, type PublicToolSolution } from "./AIToolComparison";
import {
  AIProcurementBriefFields,
  type ProcurementBrief,
} from "./AIProcurementBrief";
import { AITaskPractice, type TaskPractice } from "./AITaskPractice";
import {
  fictionalWalkthroughRequest,
  WALKTHROUGH_BASE,
} from "./AIFictionalWalkthroughAdapter";
import guidance from "./walkthrough-guidance.json" with { type: "json" };
import "./styles.css";
import "./ai-enablement.css";
import "./ai-planning-tools.css";
import "./ai-walkthrough.css";

const tabs = [
  ["start", "Choose a first use"],
  ["learning", "Build team skills"],
  ["practice", "Try a manual task"],
  ["tools", "Compare invented tools"],
  ["procurement", "Prepare questions"],
] as const;
type Tab = (typeof tabs)[number][0];
const initialProcurement: ProcurementBrief = {
  requirements:
    "Fictional example: three volunteer roles practise drafting a composting-workshop invitation. A person reviews every claim before any real use.",
  data_boundary:
    "Invented text only. No participant records, contact details, passwords or confidential material.",
  budget_notes:
    "Invented quote examples are for learning only. Ask each actual supplier for all pilot, review, support and exit costs before any decision.",
  vendor_questions:
    "What information is retained?\nCan a person review and correct every draft?\nHow is accessible output checked?\nWhat is the full cost and exit process?\nWhat happens when source information is missing?",
};
const tools: PublicToolSolution[] = [
  {
    id: "fictional-draft-lantern",
    name: "Example A · Draft Lantern",
    provider: "Invented provider A",
    category: "WRITING",
    use_case_ids: ["communications"],
    description: "A fictional drafting option, not an available supplier.",
    deployment: "Invented browser option",
    commercial_model:
      "Invented quote: 80 example units each month; setup unknown",
    nonprofit_offer: "Not supplied in this invented scenario",
    api_available: "Not supplied",
    source_urls: [],
    verification_notes: [
      "All attributes are fictional, unverified and noncommercial.",
    ],
    data_review_questions: [
      "What is retained?",
      "Who can review drafts?",
      "How would the organisation leave?",
    ],
    commercial_disclosure: {
      status: "NONE_KNOWN",
      relationship_types: [],
      statement:
        "Invented example: this provider does not exist, so no commercial relationship with it exists.",
      declared_on: "2026-10-09",
    },
  },
  {
    id: "fictional-public-notebook",
    name: "Example B · Public Notebook",
    provider: "Invented provider B",
    category: "WRITING",
    use_case_ids: ["communications"],
    description: "A second invented option for asking the same questions.",
    deployment: "Invented locally run option",
    commercial_model:
      "Invented quote: 200 example units for setup; support unknown",
    nonprofit_offer: "Not supplied in this invented scenario",
    api_available: "Not supplied",
    source_urls: [],
    verification_notes: [
      "All attributes are fictional, unverified and noncommercial.",
    ],
    data_review_questions: [
      "Who maintains it?",
      "What review time is needed?",
      "How are outputs checked?",
    ],
    commercial_disclosure: {
      status: "NONE_KNOWN",
      relationship_types: [],
      statement:
        "Invented example: this provider does not exist, so no commercial relationship with it exists.",
      declared_on: "2026-10-09",
    },
  },
];

export function AIFictionalWalkthrough() {
  const [tab, setTab] = useState<Tab>("start");
  const [worksheet, setWorksheet] = useState<TaskPractice | null>(null);
  const [procurement, setProcurement] = useState<ProcurementBrief>({
    ...initialProcurement,
  });
  const [reset, setReset] = useState(0);
  const [notice, setNotice] = useState("");
  function startOver() {
    setWorksheet(null);
    setProcurement({ ...initialProcurement });
    setReset((n) => n + 1);
    setTab("start");
    setNotice(
      "The local example was reset. No organisation record was changed.",
    );
  }
  return (
    <main className="ai-walkthrough ai-enablement">
      <a className="skip-link" href="#walkthrough-content">
        Skip to walkthrough
      </a>
      <header className="walkthrough-header">
        <p className="walkthrough-eyebrow">
          Tola / Impact Platform · AI enablement
        </p>
        <h1>A first AI pilot, with people in control</h1>
        <p>
          Explore a fictional community organisation’s journey from learning to
          practice and fair supplier questions.
        </p>
      </header>
      <aside
        className="walkthrough-boundary"
        aria-label="Fictional walkthrough boundary"
      >
        <strong>
          Fictional walkthrough · temporary local edits · no persistence
        </strong>
        <p>
          All organisations, tools and quote amounts here are invented. Public
          learning guidance and synthetic task examples come from the platform.
          This page has no sign-in, organisation access, AI connection, saved
          plan, approval or certificate. Nothing is sent or saved; reloading
          clears your edits. Enter invented text only.
        </p>
      </aside>
      <nav className="walkthrough-nav" aria-label="Walkthrough steps">
        {tabs.map(([id, label], index) => (
          <button
            key={id}
            type="button"
            aria-pressed={tab === id}
            onClick={() => {
              setTab(id);
              setNotice("");
            }}
          >
            <span aria-hidden="true">{index + 1}. </span>
            {label}
          </button>
        ))}
      </nav>
      <div className="walkthrough-actions">
        <button type="button" className="secondary" onClick={startOver}>
          Reset this local example
        </button>
        <p>Refresh the page to start over. There is no save or send action.</p>
      </div>
      {notice && (
        <p role="status" className="ai-notice">
          {notice}
        </p>
      )}
      <section
        id="walkthrough-content"
        className="panel walkthrough-content"
        aria-label="Current walkthrough step"
        tabIndex={-1}
      >
        {tab === "start" && (
          <>
            <h2>Choose one useful, bounded first task</h2>
            <p>
              <strong>Invented organisation:</strong> a small community learning
              team wants clearer public workshop invitations. Three fictional
              roles will practise with an invented event brief.
            </p>
            <div className="ai-cards">
              <article>
                <h3>A practical first use</h3>
                <p>
                  Draft a plain-language invitation from facts explicitly
                  supplied in a synthetic brief. A person checks every
                  statement.
                </p>
              </article>
              <article>
                <h3>Keep the data boundary small</h3>
                <p>
                  No participant records, real stories, contact details or
                  credentials. Missing arrangements remain questions, rather
                  than invented promises.
                </p>
              </article>
              <article>
                <h3>Name the decisions people make</h3>
                <p>
                  People choose the task, review the draft and decide whether to
                  run a real pilot. This page makes none of those decisions for
                  an organisation.
                </p>
              </article>
            </div>
            <button type="button" onClick={() => setTab("learning")}>
              Explore the learning guide
            </button>
          </>
        )}
        {tab === "learning" && (
          <>
            <h2>Build team skills before using real data</h2>
            <p>
              Read the platform’s public foundation lessons. Answering a
              practice question is local feedback; it records no completion,
              qualification or team progress.
            </p>
            <div className="ai-cards">
              {guidance.catalog.learning_paths
                .filter((path) => path.id === "foundations")
                .map((path) => (
                  <article key={path.id}>
                    <h3>{path.title}</h3>
                    {path.lessons.map((lesson) => (
                      <AILearningLesson
                        key={reset + lesson.key}
                        lesson={lesson}
                      />
                    ))}
                  </article>
                ))}
            </div>
            <button type="button" onClick={() => setTab("practice")}>
              Try an invented practice brief
            </button>
          </>
        )}
        {tab === "practice" && (
          <>
            <h2>Write and review your own manual draft</h2>
            <p className="ai-notice">
              These fields are temporary local examples. They have no
              organisation membership or saved-plan authority and will clear on
              reload. No AI generates a draft.
            </p>
            <AITaskPractice
              key={reset}
              base={WALKTHROUGH_BASE}
              contextKey={"fictional-local-only|" + reset}
              mutationBlocked={false}
              request={fictionalWalkthroughRequest}
              explain={(e) =>
                e instanceof Error ? e.message : "Example unavailable"
              }
              value={worksheet}
              onChange={setWorksheet}
              canManage={true}
              sourceVersion={null}
              persistenceNotice="Temporary local example: reloading clears this worksheet. This page cannot save an adoption plan."
            />
            <button type="button" onClick={() => setTab("tools")}>
              Compare the invented options
            </button>
          </>
        )}
        {tab === "tools" && (
          <>
            <h2>Ask the same questions of every option</h2>
            <p className="ai-notice">
              Both tools, providers and quote amounts below are invented. They
              are not entries from the real source-backed directory, available
              offers, verified terms, official prices or recommendations.
              Unknown costs prevent a fair total; no winner is selected.
            </p>
            <AIToolComparison selected={tools} />
            <p className="muted">
              On a small screen, scroll the comparison sideways to read both
              invented options.
            </p>
            <p>
              Compare data handling, review work, accessibility, support and
              exit conditions alongside price. A quote alone grants no
              data-sharing permission.
            </p>
            <button type="button" onClick={() => setTab("procurement")}>
              Prepare neutral supplier questions
            </button>
          </>
        )}
        {tab === "procurement" && (
          <>
            <h2>Prepare questions without making a commitment</h2>
            <p>
              Edit this invented brief locally. This page cannot buy, book,
              contact a supplier, share a file or save an organisation record.
            </p>
            <AIProcurementBriefFields
              value={procurement}
              canEdit={true}
              onChange={setProcurement}
            />
            <div className="ai-cards">
              {guidance.catalog.procurement_criteria.map((criterion) => (
                <article key={criterion.id}>
                  <h3>{criterion.title}</h3>
                  <ul>
                    {criterion.questions.map((q) => (
                      <li key={q}>{q}</li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
            <p className="ai-notice">
              A real pilot needs current authorised organisation members, agreed
              responsibilities, a data boundary and independent approvals where
              required. This walkthrough does not create or bypass them.
            </p>
          </>
        )}
      </section>
      <footer>
        <p>
          The authenticated Tola / Impact Platform is the real product. This
          isolated walkthrough demonstrates selected public screens with
          invented examples.
        </p>
      </footer>
    </main>
  );
}
