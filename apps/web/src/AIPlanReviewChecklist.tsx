import { useState } from "react";
import "./ai-plan-review.css";
import {
  reviewVisible,
  type ReviewContext,
  type ReviewHead,
  type ReviewSnapshot,
  type ReviewTab,
} from "./AIPlanReviewModel";

type Props = {
  snapshot: ReviewSnapshot | null;
  currentContext: ReviewContext;
  openedHead: ReviewHead | null;
  canRead: boolean;
  canonicalUnavailable: boolean;
  hasUnsavedChanges: boolean;
  hasConflictingMutation: boolean;
  onOpenSection(tab: ReviewTab): void;
};
const labels = {
  INPUTS_RECORDED: "Planning inputs recorded",
  FOLLOW_UP: "Follow-up suggested",
  INTERPRETATION_UNKNOWN: "Interpretation unavailable",
};
export function AIPlanReviewChecklist({
  snapshot,
  currentContext,
  openedHead,
  canRead,
  canonicalUnavailable,
  hasUnsavedChanges,
  hasConflictingMutation,
  onOpenSection,
}: Props) {
  const [open, setOpen] = useState(false);
  const visible = reviewVisible(
    snapshot,
    currentContext,
    openedHead,
    canRead,
    canonicalUnavailable,
    hasUnsavedChanges,
  );
  if (!canRead || !openedHead) return null;
  return (
    <section
      className="ai-plan-review ai-guidance-archive"
      aria-label="Review of the opened saved AI plan"
    >
      <h4>Review your saved plan</h4>
      <p>
        Use the recorded planning inputs to discuss the next reviews with your
        team. Learning and pilot ticks remain self-recorded; people make
        competency and spending decisions separately.
      </p>
      {!visible ? (
        <p role="status">
          {hasUnsavedChanges
            ? "Your working draft has local edits. Save or discard them, then deliberately reopen the saved plan to review its exact revision."
            : "Open the saved plan again to review its exact saved revision."}
        </p>
      ) : (
        <>
          <button
            type="button"
            className="secondary"
            onClick={() => setOpen((value) => !value)}
          >
            {open ? "Hide saved-plan review" : "View saved-plan review"}
          </button>
          {open && snapshot && (
            <>
              <p>
                <strong>Saved plan:</strong> {snapshot.title}
              </p>
              <details>
                <summary>Saved revision details</summary>
                <p>
                  Plan {snapshot.head.object_id}. Revision{" "}
                  {snapshot.head.revision_id}.
                </p>
              </details>
              <p>
                This review shows suggested follow-up, not a completion
                percentage, certification, supplier award, procurement approval
                or official AI impact.
              </p>
              <div className="ai-cards">
                {snapshot.areas.map((area) => (
                  <article key={area.id}>
                    <h5>{area.title}</h5>
                    <p>
                      <strong>{labels[area.basis]}</strong>
                    </p>
                    <ul>
                      {area.notes.map((note, index) => (
                        <li key={index}>{note}</li>
                      ))}
                    </ul>
                    <ul>
                      {area.actions.map((action) => (
                        <li key={action.id}>
                          {action.text}
                          {action.tab && (
                            <div className="ai-actions">
                              <button
                                type="button"
                                className="secondary"
                                disabled={hasConflictingMutation}
                                onClick={() => onOpenSection(action.tab!)}
                              >
                                Open{" "}
                                {
                                  {
                                    tools: "tool comparison",
                                    learning: "team learning",
                                    practice: "guided practice",
                                    procurement: "procurement brief",
                                    pilot: "pilot tracker",
                                  }[action.tab]
                                }
                              </button>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </article>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </section>
  );
}
