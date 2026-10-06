// An ephemeral starter for the existing five-field manual worksheet. It never
// generates a draft, records completion, saves a plan or sends anything onward.
export type PracticeWorksheet = {
  template_id: string;
  brief: string;
  draft: string;
  review_notes: string;
  checked_steps: string[];
};
export type StarterGuide = {
  content_version: string;
  templates: {
    id: string;
    title: string;
    example_brief: string;
  }[];
};
export type StarterSource = {
  context: string;
  canManage: boolean;
  guide: StarterGuide | null;
  templateId: string;
  value: PracticeWorksheet | null;
};
export type StarterPreview = {
  context: string;
  contentVersion: string;
  templateId: string;
  title: string;
  brief: string;
  before: string;
  hasExistingWork: boolean;
};

const TEXT_LIMIT = 2500;
const text = (value: unknown, max: number, required = false): value is string =>
  typeof value === "string" &&
  value.length <= max &&
  (!required || value.trim().length > 0);

function usableValue(value: PracticeWorksheet | null): boolean {
  return (
    value === null ||
    (text(value.template_id, 100, true) &&
      [value.brief, value.draft, value.review_notes].every((item) =>
        text(item, TEXT_LIMIT),
      ) &&
      Array.isArray(value.checked_steps) &&
      value.checked_steps.length <= 10 &&
      value.checked_steps.every((item) => text(item, 100, true)))
  );
}

export function worksheetFingerprint(value: PracticeWorksheet | null): string {
  return JSON.stringify(value);
}

export function previewPracticeStarter(
  source: StarterSource,
): StarterPreview | null {
  if (!source.context || !usableValue(source.value) || !source.guide)
    return null;
  if (
    !text(source.guide.content_version, 100, true) ||
    !Array.isArray(source.guide.templates)
  )
    return null;
  const matches = source.guide.templates.filter(
    (item) => item && typeof item === "object" && item.id === source.templateId,
  );
  if (matches.length !== 1) return null;
  const template = matches[0];
  if (
    !text(template.id, 100, true) ||
    !text(template.title, 200, true) ||
    !text(template.example_brief, TEXT_LIMIT, true) ||
    (source.value !== null && source.value.template_id !== template.id)
  )
    return null;
  return {
    context: source.context,
    contentVersion: source.guide.content_version,
    templateId: template.id,
    title: template.title,
    brief: template.example_brief,
    before: worksheetFingerprint(source.value),
    hasExistingWork: Boolean(
      source.value &&
        (source.value.brief.length ||
          source.value.draft.length ||
          source.value.review_notes.length ||
          source.value.checked_steps.length),
    ),
  };
}

export function currentPracticeStarter(
  source: StarterSource,
  preview: StarterPreview | null,
): boolean {
  if (!preview) return false;
  const current = previewPracticeStarter(source);
  return Boolean(
    current &&
      current.context === preview.context &&
      current.contentVersion === preview.contentVersion &&
      current.templateId === preview.templateId &&
      current.brief === preview.brief &&
      current.before === preview.before,
  );
}

export function applyPracticeStarter(
  source: StarterSource,
  preview: StarterPreview,
): PracticeWorksheet | null {
  if (!source.canManage || !currentPracticeStarter(source, preview))
    return null;
  // Retain the learner's own draft and notes byte-for-byte. Replacing a brief
  // invalidates prior self-checks; nothing ever implies a competency decision.
  return {
    template_id: preview.templateId,
    brief: preview.brief,
    draft: source.value?.draft ?? "",
    review_notes: source.value?.review_notes ?? "",
    checked_steps: [],
  };
}
