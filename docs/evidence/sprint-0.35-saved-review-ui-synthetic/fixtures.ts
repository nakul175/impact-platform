export const context = {
  base: "/v1/tenants/synthetic/",
  principalId: "synthetic-principal",
  sessionIdentity: "synthetic-human",
};
export function plan() {
  return {
    object_id: "11111111-1111-4111-8111-111111111111",
    revision_id: "22222222-2222-4222-8222-222222222222",
    business_state: "Draft",
    data: {
      title: "Synthetic saved team plan — Café समुदाय",
      profile: {
        sector: "GENERAL",
        team_size: 5,
        goal: "Prepare public training material",
        data_readiness: "BASIC",
        ai_experience: "EXPERIMENTING",
        sensitive_data: false,
      },
      solution_ids: ["tool-archived"],
      learning_completed: ["retired-learning-key"],
      procurement: {
        requirements: "A text drafting tool",
        data_boundary: "Synthetic or public material only",
        budget_notes: "Entered estimates require review",
        vendor_questions: "Ask about retention and exit",
      },
      pilot: {
        success_measure:
          "Review corrections and time on a comparable public task",
        completed_actions: ["HUMAN_REVIEW"],
      },
      planning: {
        cost_comparison: {
          currency: "USD",
          period_months: 12,
          offers: [
            {
              id: "offer_a",
              name: "Synthetic offer",
              lines: [
                {
                  id: "subscription",
                  category: "SUBSCRIPTION",
                  label: "Entered subscription",
                  quantity: "1",
                  unit_amount: "0",
                  cadence: "MONTHLY",
                },
              ],
            },
          ],
        },
        task_practice: {
          template_id: "draft-public-note",
          brief: "Synthetic brief",
          draft: "Synthetic output",
          review_notes: "Reviewed by the team",
          checked_steps: ["human-review"],
        },
        pilot_evaluation: {
          task_label: "Public text",
          baseline: {
            sample_size: 2,
            total_drafting_minutes: "20",
            total_review_minutes: "10",
            factual_corrections: 1,
          },
          pilot: {
            sample_size: 2,
            total_drafting_minutes: "10",
            total_review_minutes: "15",
            factual_corrections: 2,
          },
          comparable: true,
          notes: "Synthetic observations only",
        },
      },
      content_versions: {
        catalog: "catalog-archived",
        solutions: "solutions-archived",
      },
    },
  };
}
