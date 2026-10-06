import { useEffect, useId, useState } from "react";
import {
  applyPracticeStarter,
  currentPracticeStarter,
  previewPracticeStarter,
  type PracticeWorksheet,
  type StarterGuide,
  type StarterPreview,
  worksheetFingerprint,
} from "./AIPracticeStarterModel";

type Props = {
  context: string;
  guide: StarterGuide;
  templateId: string;
  value: PracticeWorksheet | null;
  canManage: boolean;
  mutationBlocked?: boolean;
  onChange(value: PracticeWorksheet): void;
};

export function AIPracticeStarter({
  context,
  guide,
  templateId,
  value,
  canManage,
  mutationBlocked = false,
  onChange,
}: Props) {
  const id = useId();
  const [preview, setPreview] = useState<StarterPreview | null>(null);
  const [notice, setNotice] = useState<{
    text: string;
    fingerprint: string;
  } | null>(null);
  const source = {
    context,
    canManage: canManage && !mutationBlocked,
    guide,
    templateId,
    value,
  };
  const candidate = previewPracticeStarter(source);
  const visible = currentPracticeStarter(source, preview) ? preview : null;
  const fingerprint = worksheetFingerprint(value);

  useEffect(() => {
    setPreview(null);
  }, [context, guide.content_version, templateId, fingerprint, canManage]);

  useEffect(() => {
    setNotice(null);
  }, [context, guide.content_version, templateId, canManage]);

  useEffect(() => {
    setNotice((current) =>
      current?.fingerprint === fingerprint ? current : null,
    );
  }, [fingerprint]);

  function useBrief() {
    if (!visible) return;
    const changed = applyPracticeStarter(source, visible);
    if (!changed) return;
    onChange(changed);
    setPreview(null);
    setNotice({
      fingerprint: worksheetFingerprint(changed),
      text: "The invented brief is in your local worksheet. Your draft and review notes were kept, and self-checks were reset. Save the adoption plan to keep this change.",
    });
  }

  return (
    <section aria-labelledby={id + "-heading"} className="ai-notice">
      <h5 id={id + "-heading"}>A guided first practice</h5>
      <ol>
        <li>Prepare an invented brief, or use the example for this task.</li>
        <li>Write your own draft. Use only the facts supplied in the brief.</li>
        <li>
          Record review notes, then check each statement against the brief.
        </li>
      </ol>
      <p>
        This is manual practice. Using an example does not complete a lesson or
        a self-check, and does not send text to an AI service.
      </p>
      <button
        type="button"
        className="secondary"
        disabled={!candidate}
        onClick={() => {
          setPreview(candidate);
          setNotice(null);
        }}
      >
        Preview the invented brief for this task
      </button>
      {visible && (
        <div role="group" aria-label="Invented brief starter preview">
          <h6>{visible.title}</h6>
          <p>{visible.brief}</p>
          <p className="muted">
            Current task guidance edition {visible.contentVersion}. This preview
            changes no worksheet or saved plan.
          </p>
          {visible.hasExistingWork && (
            <p>
              Your worksheet already contains work. Replacing the brief keeps
              your draft and review notes exactly as entered and clears all
              self-checks. Review that preserved work against the new brief.
            </p>
          )}
          {canManage ? (
            <button
              type="button"
              className="secondary"
              disabled={mutationBlocked}
              onClick={useBrief}
            >
              {visible.hasExistingWork
                ? "Replace only my brief and reset self-checks"
                : "Use this invented brief in my worksheet"}
            </button>
          ) : (
            <p>
              You can study this example. Plan management permission is needed
              to change the shared worksheet.
            </p>
          )}
          {mutationBlocked && (
            <p>
              Wait for the pending saved-plan action before changing the brief.
            </p>
          )}
          <button
            type="button"
            className="secondary"
            onClick={() => setPreview(null)}
          >
            Keep my worksheet unchanged
          </button>
        </div>
      )}
      {notice?.fingerprint === fingerprint && (
        <p role="status">{notice.text}</p>
      )}
    </section>
  );
}
