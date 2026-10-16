export const sections = [
  [
    "programmes",
    "Portfolio",
    "Programme",
    "Community learning",
    "Support practical learning in three fictional districts.",
  ],
  [
    "observations",
    "Measurement",
    "Observation",
    "Learning attendance",
    "51 participants attended out of 110 invited.",
  ],
  [
    "configuration",
    "Measurement setup",
    "Indicator",
    "Participation rate",
    "Numerator: participants attending. Denominator: participants invited.",
  ],
  [
    "planning",
    "Results framework",
    "Outcome",
    "More confident community teams",
    "Connect activities, outputs, outcomes and their assumptions.",
  ],
  [
    "dashboards",
    "Dashboards",
    "Dashboard",
    "Programme overview",
    "Attendance, coverage and follow-up in one view.",
  ],
  [
    "forms",
    "Forms",
    "Form",
    "Session feedback",
    "Questions: session date, attendance and a short reflection.",
  ],
  [
    "rounds",
    "Collection rounds",
    "Collection round",
    "October learning round",
    "Collect invented feedback from three fictional sites.",
  ],
  [
    "imports",
    "Imports",
    "Import plan",
    "Attendance spreadsheet",
    "Map date, site, invited and attended columns before importing.",
  ],
  [
    "evidence",
    "Evidence",
    "Evidence note",
    "Facilitator observation",
    "Fictional notes about practice sessions; no attachments or personal data.",
  ],
  [
    "changes",
    "Change requests",
    "Change request",
    "Clarify participation definition",
    "Document the reason and affected measurement scope.",
  ],
  [
    "periods",
    "Period close",
    "Period preview",
    "October reporting period",
    "Reconcile missing observations before a simulated close.",
  ],
  [
    "work",
    "My work",
    "Task",
    "Follow up on feedback",
    "Ask fictional site teams to review the draft questionnaire.",
  ],
  [
    "reviews",
    "Review queue",
    "Review candidate",
    "Participation observation",
    "Demo review states do not represent independent human approval.",
  ],
  [
    "results",
    "Results",
    "Result note",
    "Pooled participation",
    "51 / 110 = 46.36%. This is an invented example, not an official result.",
  ],
  [
    "reports",
    "Reports",
    "Report draft",
    "Learning progress summary",
    "Describe evidence, uncertainty and proposed next steps.",
  ],
  [
    "evaluation",
    "Evaluation & learning",
    "Learning question",
    "Which practice sessions help?",
    "Compare fictional feedback, document uncertainty and plan follow-up.",
  ],
  [
    "finance",
    "Finance",
    "Budget draft",
    "Community learning budget",
    "Invented budget: 1,000 units. Invented expenditure: 620 units.",
  ],
  [
    "ai",
    "AI enablement",
    "AI practice plan",
    "Draft a facilitation checklist",
    "A human checks any suggestion. This demo never calls an AI provider.",
  ],
  [
    "people",
    "People & access",
    "Access proposal",
    "Fictional reviewer role",
    "Describe a proposed responsibility. No identity, grant or access is created.",
  ],
  [
    "settings",
    "Workspace settings",
    "Setting draft",
    "Fictional community workspace",
    "Reporting timezone: Asia/Kolkata. All edits stay inside this browser tab.",
  ],
] as const;
export type SectionId = (typeof sections)[number][0];
export type DemoStatus =
  | "Draft"
  | "Submitted (simulation)"
  | "Reviewed (simulation)";
export type DemoRecord = {
  id: string;
  title: string;
  notes: string;
  status: DemoStatus;
  history: string[];
};
export type DemoState = Record<SectionId, DemoRecord[]>;
export function freshDemo(): DemoState {
  return Object.fromEntries(
    sections.map(([id, , , title, notes]) => [
      id,
      [
        {
          id: `sample-${id}`,
          title,
          notes,
          status: "Draft",
          history: ["Bundled fictional example"],
        },
      ],
    ]),
  ) as DemoState;
}
export function saveDemo(
  state: DemoState,
  section: SectionId,
  title: string,
  notes: string,
  id?: string,
): DemoState {
  if (!title.trim() || title.length > 120 || notes.length > 2000)
    throw new Error(
      "Enter a title (1–120 characters) and notes of at most 2,000 characters.",
    );
  const prior = id ? state[section].find((row) => row.id === id) : undefined;
  if (id && !prior)
    throw new Error("This draft is no longer available. Open it again.");
  if (!prior && state[section].length >= 50)
    throw new Error(
      "This demo allows 50 records per section. Reset the demo to start again.",
    );
  const row: DemoRecord = {
    id: prior?.id ?? crypto.randomUUID(),
    title: title.trim(),
    notes,
    status: "Draft",
    history: [
      ...(prior?.history ?? []),
      prior
        ? "Edited locally; simulation returned to draft"
        : "Created locally",
    ],
  };
  return {
    ...state,
    [section]: prior
      ? state[section].map((r) => (r.id === id ? row : r))
      : [...state[section], row],
  };
}
export function advanceDemo(
  state: DemoState,
  section: SectionId,
  id: string,
): DemoState {
  const prior = state[section].find((r) => r.id === id);
  if (!prior || prior.status === "Reviewed (simulation)")
    throw new Error("This demo record cannot advance further.");
  const status: DemoStatus =
    prior.status === "Draft"
      ? "Submitted (simulation)"
      : "Reviewed (simulation)";
  return {
    ...state,
    [section]: state[section].map((r) =>
      r.id === id
        ? {
            ...r,
            status,
            history: [
              ...r.history,
              status + "; no real submission or approval",
            ],
          }
        : r,
    ),
  };
}
