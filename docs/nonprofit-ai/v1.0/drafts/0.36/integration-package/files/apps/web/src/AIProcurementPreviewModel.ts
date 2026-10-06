export type ProcurementDraft = {
  requirements: string;
  data_boundary: string;
  budget_notes: string;
  vendor_questions: string;
};
export type ProcurementProfile = {
  sector: string;
  team_size: number;
  goal: string;
  data_readiness: string;
  ai_experience: string;
  sensitive_data: boolean;
};
export type ProcurementPreviewSource = {
  context: { base: string; principalId: string; sessionIdentity: string };
  head: { object_id: string; revision_id: string } | null;
  profile: ProcurementProfile;
  catalog: {
    content_version: string;
    procurement_criteria: { id: string; title: string; questions: string[] }[];
  };
  solutionsVersion: string | null;
  solutionIds: string[];
  selected: { id: string; name: string; data_review_questions: string[] }[];
  selectedSourceKey: string;
  value: ProcurementDraft;
  planKey: string;
  planGeneration: number;
  interactionGeneration: number;
  canManage: boolean;
  mutationBlocked: boolean;
};
export type ProcurementPreview = {
  binding: string;
  before: ProcurementDraft;
  proposed: ProcurementDraft;
  hasExistingWork: boolean;
};

const limits = {
  requirements: 2000,
  data_boundary: 2000,
  budget_notes: 500,
  vendor_questions: 2000,
};
function usable(source: ProcurementPreviewSource): boolean {
  return Boolean(
    source.context.base &&
      source.context.principalId &&
      source.context.sessionIdentity &&
      typeof source.profile.goal === "string" &&
      source.profile.goal.trim() &&
      typeof source.profile.team_size === "number" &&
      Number.isFinite(source.profile.team_size) &&
      typeof source.profile.sensitive_data === "boolean" &&
      Number.isSafeInteger(source.planGeneration) &&
      source.planGeneration >= 0 &&
      Number.isSafeInteger(source.interactionGeneration) &&
      source.interactionGeneration >= 0 &&
      source.planKey &&
      source.selectedSourceKey &&
      source.catalog.content_version &&
      Object.entries(limits).every(([key, limit]) => {
        const value = source.value[key as keyof ProcurementDraft];
        return typeof value === "string" && value.length <= limit;
      }) &&
      Array.isArray(source.catalog.procurement_criteria) &&
      source.catalog.procurement_criteria.every(
        (row) =>
          Array.isArray(row.questions) &&
          row.questions.every((question) => typeof question === "string"),
      ) &&
      Array.isArray(source.selected) &&
      source.selected.every(
        (row) =>
          typeof row.name === "string" &&
          Array.isArray(row.data_review_questions) &&
          row.data_review_questions.every(
            (question) => typeof question === "string",
          ),
      ),
  );
}

// These four strings are the existing Workspace fill text, including its exact
// ordering, fallback supplier wording and UTF-16 slice boundaries.
export function prepareProcurementText(
  source: ProcurementPreviewSource,
): ProcurementDraft {
  const supplierNames =
    source.selected.map((solution) => solution.name).join(", ") ||
    "a supplier to be selected";
  return {
    requirements: (
      "Pilot goal: " +
      source.profile.goal +
      "\nTeam: " +
      source.profile.team_size +
      " people.\nShortlist: " +
      supplierNames +
      ".\nRequire human review of every output and a documented exit/export process."
    ).slice(0, 2000),
    data_boundary: source.profile.sensitive_data
      ? "The intended work involves sensitive information. Begin with synthetic material only. An authorised data steward must approve a specific data boundary, access controls, retention and supplier processing terms before any real data is used."
      : "Use synthetic or approved non-sensitive material in the pilot. Do not send participant identities, confidential records or credentials. Confirm retention, deletion and permissions before wider use.",
    budget_notes:
      "Request the total cost of the bounded pilot, including seats, API usage, onboarding, support, taxes and exit costs. Confirm any nonprofit eligibility and renewal conditions directly with the supplier.",
    vendor_questions: [
      ...source.catalog.procurement_criteria.flatMap(
        (criterion) => criterion.questions,
      ),
      ...source.selected.flatMap((solution) => solution.data_review_questions),
    ]
      .join("\n")
      .slice(0, 2000),
  };
}

export function procurementSourceFingerprint(
  source: ProcurementPreviewSource,
): string {
  return JSON.stringify([
    source.context,
    source.head,
    source.profile,
    source.catalog,
    source.solutionsVersion,
    source.solutionIds,
    source.selected,
    source.selectedSourceKey,
    source.value,
    source.planKey,
    source.planGeneration,
    source.interactionGeneration,
    source.canManage,
    source.mutationBlocked,
  ]);
}

export function previewProcurement(
  source: ProcurementPreviewSource,
): ProcurementPreview | null {
  if (!source.canManage || source.mutationBlocked || !usable(source))
    return null;
  return {
    binding: procurementSourceFingerprint(source),
    before: { ...source.value },
    proposed: prepareProcurementText(source),
    hasExistingWork: Object.values(source.value).some(
      (value) => value.length > 0,
    ),
  };
}

export function currentProcurementPreview(
  source: ProcurementPreviewSource,
  preview: ProcurementPreview | null,
): boolean {
  if (!preview) return false;
  const current = previewProcurement(source);
  return Boolean(
    current &&
      current.binding === preview.binding &&
      JSON.stringify(current.proposed) === JSON.stringify(preview.proposed) &&
      JSON.stringify(current.before) === JSON.stringify(preview.before),
  );
}

export function applyProcurementPreview(
  source: ProcurementPreviewSource,
  preview: ProcurementPreview,
): ProcurementDraft | null {
  if (!currentProcurementPreview(source, preview)) return null;
  return prepareProcurementText(source);
}
