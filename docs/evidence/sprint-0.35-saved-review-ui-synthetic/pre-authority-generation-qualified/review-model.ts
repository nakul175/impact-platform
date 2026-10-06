/** Read-only review of exact public saved inputs. No requests, totals or decisions. */
export type ReviewTab =
  | "tools"
  | "learning"
  | "practice"
  | "procurement"
  | "pilot";
export type ReviewContext = {
  base: string;
  principalId: string;
  sessionIdentity: string;
};
export type ReviewHead = { object_id: string; revision_id: string };
export type ReviewArea = {
  id: string;
  title: string;
  basis: "INPUTS_RECORDED" | "FOLLOW_UP" | "INTERPRETATION_UNKNOWN";
  notes: string[];
  actions: { id: string; text: string; tab?: ReviewTab }[];
};
export type CanonicalReadMarker = {
  context: ReviewContext;
  head: ReviewHead;
};
export type ReviewSnapshot = CanonicalReadMarker & {
  title: string;
  areas: ReviewArea[];
};

type RecordValue = Record<string, unknown>;
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const decimal = /^(?:0|[1-9][0-9]{0,25})(?:\.[0-9]{1,12})?$/;
const costId = /^[a-z][a-z0-9_-]{0,63}$/;
const costCategories = new Set([
  "SETUP",
  "SUBSCRIPTION",
  "USAGE",
  "INTEGRATION",
  "TRAINING",
  "REVIEW",
  "SUPPORT",
  "EXIT",
  "OTHER",
]);
const pilotActions = new Set([
  "DEFINE_GOAL",
  "SYNTHETIC_TRIAL",
  "HUMAN_REVIEW",
  "TRAIN_STAFF",
  "REVIEW_OUTCOME",
]);
const object = (value: unknown): RecordValue | null =>
  value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as RecordValue)
    : null;
const text = (
  value: unknown,
  maximum: number,
  required = false,
): value is string =>
  typeof value === "string" &&
  value.length <= maximum &&
  (!required || value.trim().length > 0);
const integer = (
  value: unknown,
  lower: number,
  upper: number,
): value is number =>
  Number.isSafeInteger(value) &&
  Number(value) >= lower &&
  Number(value) <= upper;
function ids(
  value: unknown,
  maximum: number,
  length: number,
): value is string[] {
  return (
    Array.isArray(value) &&
    value.length <= maximum &&
    value.every((id) => text(id, length, true)) &&
    new Set(value).size === value.length
  );
}
function contextValid(value: ReviewContext) {
  return (
    !!value &&
    text(value.base, 300, true) &&
    text(value.principalId, 100, true) &&
    text(value.sessionIdentity, 512, true)
  );
}
function sameContext(left: ReviewContext, right: ReviewContext) {
  return (
    contextValid(left) &&
    contextValid(right) &&
    left.base === right.base &&
    left.principalId === right.principalId &&
    left.sessionIdentity === right.sessionIdentity
  );
}
export function canonicalReadVisible(
  marker: CanonicalReadMarker | null,
  current: ReviewContext,
  head: ReviewHead | null,
  canRead: boolean,
  canonicalUnavailable: boolean,
  hasUnsavedChanges: boolean,
) {
  return (
    !!marker &&
    canRead &&
    !canonicalUnavailable &&
    !hasUnsavedChanges &&
    !!head &&
    sameContext(marker.context, current) &&
    marker.head.object_id === head.object_id &&
    marker.head.revision_id === head.revision_id
  );
}
export const reviewVisible = canonicalReadVisible;

/** Establish only from a successful current-authorised canonical GET, never a
 * directory item, write receipt or captured draft. Public-field interpretation
 * may remain unavailable while this exact read marker is valid.
 */
export function captureCanonicalRead(
  value: unknown,
  context: ReviewContext,
): CanonicalReadMarker | null {
  const row = object(value);
  if (
    !contextValid(context) ||
    !row ||
    !object(row.data) ||
    row.business_state !== "Draft" ||
    !text(row.object_id, 36, true) ||
    !uuid.test(row.object_id) ||
    !text(row.revision_id, 36, true) ||
    !uuid.test(row.revision_id)
  )
    return null;
  return {
    context: {
      base: context.base,
      principalId: context.principalId,
      sessionIdentity: context.sessionIdentity,
    },
    head: { object_id: row.object_id, revision_id: row.revision_id },
  };
}
function costState(
  value: unknown,
): "MISSING" | "RECORDED" | "UNKNOWN_AMOUNT" | "UNKNOWN" {
  if (value === null || value === undefined) return "MISSING";
  const cost = object(value);
  if (
    !cost ||
    !text(cost.currency, 3, true) ||
    !/^[A-Z]{3}$/.test(cost.currency) ||
    !integer(cost.period_months, 1, 60) ||
    !Array.isArray(cost.offers) ||
    cost.offers.length < 1 ||
    cost.offers.length > 4
  )
    return "UNKNOWN";
  let unknown = false;
  const offerIds = new Set<string>();
  for (const candidate of cost.offers) {
    const offer = object(candidate);
    if (
      !offer ||
      !text(offer.id, 64, true) ||
      !costId.test(offer.id) ||
      offerIds.has(offer.id) ||
      !text(offer.name, 150, true) ||
      !Array.isArray(offer.lines) ||
      offer.lines.length < 1 ||
      offer.lines.length > 20
    )
      return "UNKNOWN";
    offerIds.add(offer.id);
    const lineIds = new Set<string>();
    for (const candidateLine of offer.lines) {
      const line = object(candidateLine);
      if (
        !line ||
        !text(line.id, 64, true) ||
        !costId.test(line.id) ||
        lineIds.has(line.id) ||
        !costCategories.has(String(line.category)) ||
        !text(line.label, 150, true) ||
        !text(line.quantity, 39, true) ||
        !decimal.test(line.quantity) ||
        !["ONE_OFF", "MONTHLY"].includes(String(line.cadence))
      )
        return "UNKNOWN";
      lineIds.add(line.id);
      if (line.unit_amount === null) unknown = true;
      else if (
        !text(line.unit_amount, 39, true) ||
        !decimal.test(line.unit_amount)
      )
        return "UNKNOWN";
    }
  }
  return unknown ? "UNKNOWN_AMOUNT" : "RECORDED";
}
function sampleValid(value: unknown) {
  const sample = object(value);
  return (
    !!sample &&
    integer(sample.sample_size, 1, 10000) &&
    integer(sample.factual_corrections, 0, 1000000) &&
    [sample.total_drafting_minutes, sample.total_review_minutes].every(
      (value) => text(value, 39, true) && decimal.test(value),
    )
  );
}
function pilotState(
  value: unknown,
): "MISSING" | "RECORDED" | "NOT_COMPARABLE" | "UNKNOWN" {
  if (value === null || value === undefined) return "MISSING";
  const pilot = object(value);
  if (
    !pilot ||
    !text(pilot.task_label, 150, true) ||
    !text(pilot.notes, 1000) ||
    typeof pilot.comparable !== "boolean" ||
    !sampleValid(pilot.baseline) ||
    !sampleValid(pilot.pilot)
  )
    return "UNKNOWN";
  return pilot.comparable ? "RECORDED" : "NOT_COMPARABLE";
}
function practiceState(
  value: unknown,
): "MISSING" | "RECORDED" | "INCOMPLETE" | "UNKNOWN" {
  if (value === null || value === undefined) return "MISSING";
  const practice = object(value);
  if (
    !practice ||
    !text(practice.template_id, 64, true) ||
    ![practice.brief, practice.draft, practice.review_notes].every((value) =>
      text(value, 2500),
    ) ||
    !ids(practice.checked_steps, 10, 64)
  )
    return "UNKNOWN";
  return [practice.brief, practice.draft, practice.review_notes].every(
    (value) => String(value).trim().length > 0,
  )
    ? "RECORDED"
    : "INCOMPLETE";
}

/** Call only after a successful current-authority canonical saved-plan read.
 * Select known public fields only. Additional private/future keys neither enter
 * the snapshot nor change visible output; no private linkage existence inference.
 */
export function captureReviewSnapshot(
  value: unknown,
  context: ReviewContext,
): ReviewSnapshot | null {
  const row = object(value),
    data = object(row?.data),
    profile = object(data?.profile),
    procurement = object(data?.procurement),
    pilot = object(data?.pilot);
  if (
    !contextValid(context) ||
    !row ||
    !data ||
    row.business_state !== "Draft" ||
    !text(row.object_id, 36, true) ||
    !uuid.test(row.object_id) ||
    !text(row.revision_id, 36, true) ||
    !uuid.test(row.revision_id) ||
    !text(data.title, 150, true) ||
    !profile ||
    !text(profile.goal, 1000, true) ||
    !integer(profile.team_size, 1, 100000) ||
    !["GENERAL", "EDUCATION", "HEALTH", "LIVELIHOODS", "ENVIRONMENT"].includes(
      String(profile.sector),
    ) ||
    !["NONE", "BASIC", "STRUCTURED"].includes(String(profile.data_readiness)) ||
    !["NONE", "EXPERIMENTING", "REGULAR"].includes(
      String(profile.ai_experience),
    ) ||
    typeof profile.sensitive_data !== "boolean" ||
    !ids(data.solution_ids, 4, 100) ||
    !ids(data.learning_completed, 100, 100) ||
    !procurement ||
    !text(procurement.requirements, 2000) ||
    !text(procurement.data_boundary, 2000) ||
    !text(procurement.budget_notes, 500) ||
    !text(procurement.vendor_questions, 2000) ||
    !pilot ||
    !text(pilot.success_measure, 1000) ||
    !ids(pilot.completed_actions, 5, 100) ||
    !pilot.completed_actions.every((id) => pilotActions.has(id))
  )
    return null;
  const planning = object(data.planning);
  const planningUnknown =
    data.planning !== undefined &&
    (!planning ||
      !["cost_comparison", "pilot_evaluation", "task_practice"].every((key) =>
        Object.hasOwn(planning, key),
      ));
  const cost = planningUnknown
    ? "UNKNOWN"
    : costState(planning?.cost_comparison);
  const practice = planningUnknown
    ? "UNKNOWN"
    : practiceState(planning?.task_practice);
  const outcomes = planningUnknown
    ? "UNKNOWN"
    : pilotState(planning?.pilot_evaluation);
  const versions = object(data.content_versions);
  const knownVersions =
    !!versions &&
    text(versions.catalog, 100, true) &&
    text(versions.solutions, 100, true);
  const gaps: string[] = [];
  if (!procurement.requirements.trim())
    gaps.push("Record what the proposed tool must do.");
  if (!procurement.data_boundary.trim())
    gaps.push(
      "Record permitted and prohibited material in the procurement brief.",
    );
  if (!procurement.budget_notes.trim())
    gaps.push(
      "Record the budget assumptions for review; notes do not authorise spending.",
    );
  if (!procurement.vendor_questions.trim())
    gaps.push("Record the questions your team needs a supplier to answer.");
  if (cost === "MISSING")
    gaps.push("Prepare supplied-cost assumptions if a comparison is needed.");
  if (cost === "UNKNOWN_AMOUNT")
    gaps.push(
      "Review the unknown amount in the entered cost lines; no complete total can be inferred here.",
    );
  if (cost === "UNKNOWN")
    gaps.push("Reopen and review the cost inputs before interpreting them.");
  const practiceNotes =
    practice === "RECORDED"
      ? [
          "A practice brief, draft and review notes are saved. This is a self-recorded worksheet, not assessed competence.",
        ]
      : practice === "MISSING"
        ? ["A practice worksheet is not recorded in this saved plan."]
        : practice === "INCOMPLETE"
          ? [
              "A saved practice worksheet has blank brief, draft or review notes.",
            ]
          : ["The saved practice inputs cannot be interpreted by this view."];
  const outcomeNotes =
    outcomes === "RECORDED"
      ? [
          "Baseline and pilot observations are saved and marked comparable by the author. No improvement or causal conclusion is calculated here.",
        ]
      : outcomes === "NOT_COMPARABLE"
        ? ["Saved baseline and pilot observations are marked not comparable."]
        : outcomes === "MISSING"
          ? [
              "A baseline/pilot observation pair is not recorded in this saved plan.",
            ]
          : [
              "The saved pilot observation inputs cannot be interpreted by this view.",
            ];
  const areas: ReviewArea[] = [
    {
      id: "brief",
      title: "Goal and permitted material",
      basis: procurement.data_boundary.trim() ? "INPUTS_RECORDED" : "FOLLOW_UP",
      notes: [
        "An organisation goal and team profile are saved.",
        profile.sensitive_data
          ? "The saved profile flags sensitive material; this checklist does not authorise its use or disclosure."
          : "The saved profile does not flag sensitive material; the team still needs to agree permitted inputs.",
      ],
      actions: [
        {
          id: "brief-review",
          text: "Review the goal and agreed data boundary with the responsible colleague.",
          tab: "procurement",
        },
      ],
    },
    {
      id: "tools",
      title: "Tool shortlist",
      basis: data.solution_ids.length ? "INPUTS_RECORDED" : "FOLLOW_UP",
      notes: [
        data.solution_ids.length
          ? `${data.solution_ids.length} tool selection${data.solution_ids.length === 1 ? " is" : "s are"} recorded in this saved plan.`
          : "A tool shortlist is not recorded in this saved plan.",
      ],
      actions: [
        {
          id: "tools-review",
          text: "Review the existing source-backed directory and current terms before choosing a tool.",
          tab: "tools",
        },
      ],
    },
    {
      id: "practice",
      title: "Team learning and practice",
      basis:
        practice === "UNKNOWN"
          ? "INTERPRETATION_UNKNOWN"
          : practice === "RECORDED"
            ? "INPUTS_RECORDED"
            : "FOLLOW_UP",
      notes: [
        `${data.learning_completed.length} stored self-reported learning entr${data.learning_completed.length === 1 ? "y" : "ies"}; keys may refer to older or unavailable lessons and are not a per-person competency record.`,
        ...practiceNotes,
      ],
      actions: [
        {
          id: "learning-review",
          text: "Review the existing lessons and stored self-reported progress.",
          tab: "learning",
        },
        {
          id: "practice-review",
          text: "Use the existing guided practice worksheet to review what the team tried.",
          tab: "practice",
        },
      ],
    },
    {
      id: "procurement",
      title: "Procurement preparation",
      basis:
        cost === "UNKNOWN"
          ? "INTERPRETATION_UNKNOWN"
          : gaps.length
            ? "FOLLOW_UP"
            : "INPUTS_RECORDED",
      notes: gaps.length
        ? gaps
        : [
            "The brief and entered cost assumptions are saved. These inputs do not approve a supplier, purchase or total cost of ownership.",
          ],
      actions: [
        {
          id: "procurement-review",
          text: "Review the saved brief and supplied-cost assumptions in the existing procurement section.",
          tab: "procurement",
        },
      ],
    },
    {
      id: "pilot",
      title: "Pilot measure and observations",
      basis:
        outcomes === "UNKNOWN"
          ? "INTERPRETATION_UNKNOWN"
          : pilot.success_measure.trim() && outcomes === "RECORDED"
            ? "INPUTS_RECORDED"
            : "FOLLOW_UP",
      notes: [
        pilot.success_measure.trim()
          ? "A pilot success measure is saved."
          : "Record a pilot success measure before interpreting a trial.",
        ...outcomeNotes,
        "Pilot action ticks are self-recorded planning inputs; they do not establish independent approval or official impact.",
      ],
      actions: [
        {
          id: "pilot-review",
          text: "Review the measure, observations and human review actions in the existing pilot section.",
          tab: "pilot",
        },
      ],
    },
    {
      id: "guidance",
      title: "Guide interpretation",
      basis: knownVersions ? "INPUTS_RECORDED" : "INTERPRETATION_UNKNOWN",
      notes: [
        knownVersions
          ? "Guide edition identifiers are saved. Edition identifiers alone do not prove that every historical component is available."
          : "Guide edition identifiers are missing or cannot be interpreted by this view.",
      ],
      actions: [
        {
          id: "guidance-review",
          text: "Use the existing saved guidance view to review the exact captured editions; unavailable guidance must remain unavailable.",
        },
      ],
    },
  ];
  return {
    context: {
      base: context.base,
      principalId: context.principalId,
      sessionIdentity: context.sessionIdentity,
    },
    head: { object_id: row.object_id, revision_id: row.revision_id },
    title: data.title,
    areas,
  };
}
