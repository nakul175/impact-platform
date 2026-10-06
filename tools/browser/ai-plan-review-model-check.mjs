import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import {
  captureReviewSnapshot,
  reviewVisible,
  captureCanonicalRead,
  canonicalReadVisible,
} from "../../apps/web/src/AIPlanReviewModel.ts";
const context = {
  base: "/v1/tenants/synthetic/",
  principalId: "synthetic-principal",
  sessionIdentity: "synthetic-human",
};
function plan() {
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

const repo = new URL("../../", import.meta.url);
const evidence = new URL(
  "docs/evidence/sprint-0.35-saved-review-model-tests.json",
  repo,
);
const files = [
  "apps/web/src/AIPlanReviewModel.ts",
  "tools/browser/ai-plan-review-model-check.mjs",
  "apps/api/impact_api/ai_plan_public_export_schema_v1.json",
];
const hashes = () =>
  Object.fromEntries(
    files.map((file) => [
      file,
      createHash("sha256")
        .update(readFileSync(new URL(file, repo)))
        .digest("hex"),
    ]),
  );
const before = hashes(),
  results = [];
const area = (row, id) =>
  captureReviewSnapshot(row, context)?.areas.find((area) => area.id === id);
const check = (name, fn) =>
  test(name, () => {
    fn();
    results.push({ name, status: "passed" });
  });

check(
  "Canonical read validity stays distinct from unavailable public interpretation",
  () => {
    const source = plan();
    source.data.profile.goal = 123;
    const marker = captureCanonicalRead(source, context);
    assert.equal(captureReviewSnapshot(source, context), null);
    assert.equal(
      canonicalReadVisible(marker, context, marker.head, true, false, false),
      true,
    );
    assert.equal(
      canonicalReadVisible(marker, context, marker.head, true, false, true),
      false,
    );
    assert.equal(
      captureCanonicalRead(
        {
          object_id: source.object_id,
          revision_id: source.revision_id,
          business_state: "Draft",
        },
        context,
      ),
      null,
    );
  },
);
check("Review binds only the exact successful public saved selectors", () => {
  const source = plan(),
    snapshot = captureReviewSnapshot(source, context);
  assert.equal(snapshot.title, source.data.title);
  assert.deepEqual(snapshot.head, {
    object_id: source.object_id,
    revision_id: source.revision_id,
  });
  assert.equal(
    reviewVisible(snapshot, context, snapshot.head, true, false, false),
    true,
  );
  source.data.title = "Local later edit";
  source.revision_id = "33333333-3333-4333-8333-333333333333";
  assert.notEqual(snapshot.title, source.data.title);
  assert.notEqual(snapshot.head.revision_id, source.revision_id);
});
check(
  "Actor, tenant/base and exposed identity changes immediately hide the old review",
  () => {
    const snapshot = captureReviewSnapshot(plan(), context);
    for (const key of ["base", "principalId", "sessionIdentity"])
      assert.equal(
        reviewVisible(
          snapshot,
          { ...context, [key]: "changed" },
          snapshot.head,
          true,
          false,
          false,
        ),
        false,
      );
  },
);
check("Different plan or revision cannot reuse a prior saved review", () => {
  const snapshot = captureReviewSnapshot(plan(), context);
  for (const key of ["object_id", "revision_id"])
    assert.equal(
      reviewVisible(
        snapshot,
        context,
        { ...snapshot.head, [key]: "changed" },
        true,
        false,
        false,
      ),
      false,
    );
});
check(
  "Lost read authority, unavailable canonical source and dirty draft deny display",
  () => {
    const snapshot = captureReviewSnapshot(plan(), context);
    assert.equal(
      reviewVisible(snapshot, context, snapshot.head, false, false, false),
      false,
    );
    assert.equal(
      reviewVisible(snapshot, context, snapshot.head, true, true, false),
      false,
    );
    assert.equal(
      reviewVisible(snapshot, context, snapshot.head, true, false, true),
      false,
    );
    assert.equal(
      reviewVisible(null, context, snapshot.head, true, false, false),
      false,
    );
    assert.equal(
      reviewVisible(snapshot, context, null, true, false, false),
      false,
    );
  },
);
check("A receipt without canonical data cannot establish the review", () => {
  const source = plan();
  assert.equal(
    captureReviewSnapshot(
      {
        object_id: source.object_id,
        revision_id: source.revision_id,
        business_state: "Draft",
      },
      context,
    ),
    null,
  );
});
check(
  "Malformed base plan shape or selectors never become recorded preparation",
  () => {
    for (const edit of [
      (p) => (p.business_state = "Approved"),
      (p) => (p.object_id = "raw-unbounded-selector"),
      (p) => (p.data.profile.team_size = 0),
      (p) => (p.data.solution_ids = ["same", "same"]),
      (p) => (p.data.pilot.completed_actions = ["AWARD_APPROVED"]),
      (p) => (p.data.title = "x".repeat(151)),
    ]) {
      const p = plan();
      edit(p);
      assert.equal(captureReviewSnapshot(p, context), null);
    }
  },
);
check(
  "Explicit zero is a recorded entered cost, with no total-cost approval",
  () => {
    const procurement = area(plan(), "procurement");
    assert.equal(procurement.basis, "INPUTS_RECORDED");
    assert.match(
      procurement.notes.join(" "),
      /do not approve.*total cost of ownership/,
    );
  },
);
check("Null amount remains a follow-up without inferred complete cost", () => {
  const p = plan();
  p.data.planning.cost_comparison.offers[0].lines[0].unit_amount = null;
  const a = area(p, "procurement");
  assert.equal(a.basis, "FOLLOW_UP");
  assert.match(a.notes.join(" "), /unknown amount.*no complete total/);
});
check(
  "Missing required cost line identity, label or category is uninterpretable",
  () => {
    for (const key of ["id", "label", "category"]) {
      const p = plan();
      delete p.data.planning.cost_comparison.offers[0].lines[0][key];
      assert.equal(area(p, "procurement").basis, "INTERPRETATION_UNKNOWN");
    }
  },
);
check(
  "Invalid known cost enum, identifier or decimal remains uninterpretable",
  () => {
    for (const [key, value] of [
      ["id", "Not allowed"],
      ["category", "GUARANTEED_TOTAL"],
      ["quantity", "1e2"],
      ["unit_amount", "-1"],
      ["cadence", "FOREVER"],
    ]) {
      const p = plan();
      p.data.planning.cost_comparison.offers[0].lines[0][key] = value;
      assert.equal(area(p, "procurement").basis, "INTERPRETATION_UNKNOWN");
    }
  },
);
check(
  "Duplicate offer or within-offer line identities are uninterpretable",
  () => {
    for (const kind of ["offers", "lines"]) {
      const p = plan(),
        cost = p.data.planning.cost_comparison;
      if (kind === "offers") cost.offers.push(structuredClone(cost.offers[0]));
      else cost.offers[0].lines.push(structuredClone(cost.offers[0].lines[0]));
      assert.equal(area(p, "procurement").basis, "INTERPRETATION_UNKNOWN");
    }
  },
);
check("Blank procurement fields produce concrete review actions", () => {
  const p = plan();
  p.data.procurement.requirements = "";
  p.data.procurement.data_boundary = " ";
  assert.equal(area(p, "brief").basis, "FOLLOW_UP");
  assert.match(
    area(p, "procurement").notes.join(" "),
    /what.*must do.*permitted and prohibited/,
  );
});
check(
  "Legacy absent planning remains missing follow-up without invented measurements",
  () => {
    const p = plan();
    delete p.data.planning;
    assert.equal(area(p, "practice").basis, "FOLLOW_UP");
    assert.equal(area(p, "pilot").basis, "FOLLOW_UP");
    assert.match(area(p, "pilot").notes.join(" "), /not recorded/);
  },
);
check(
  "Malformed or incomplete planning object remains interpretation unavailable",
  () => {
    for (const value of [null, [], "unknown", {}]) {
      const p = plan();
      p.data.planning = value;
      for (const id of ["practice", "pilot", "procurement"])
        assert.equal(area(p, id).basis, "INTERPRETATION_UNKNOWN");
    }
  },
);
check(
  "Saved worksheet inputs do not certify competence or interpret retired learning keys",
  () => {
    const a = area(plan(), "practice");
    assert.match(
      a.notes.join(" "),
      /stored self-reported learning.*older or unavailable.*not.*competency.*not assessed competence/,
    );
  },
);
check(
  "Blank practice review notes remain follow-up even if steps are ticked",
  () => {
    const p = plan();
    p.data.planning.task_practice.review_notes = "";
    const a = area(p, "practice");
    assert.equal(a.basis, "FOLLOW_UP");
    assert.match(a.notes.join(" "), /blank/);
  },
);
check(
  "Pilot incomparable flag prevents a recorded comparable-observation label",
  () => {
    const p = plan();
    p.data.planning.pilot_evaluation.comparable = false;
    const a = area(p, "pilot");
    assert.equal(a.basis, "FOLLOW_UP");
    assert.match(a.notes.join(" "), /not comparable/);
  },
);
check(
  "Comparable self-entered pilot does not claim calculated improvement or official impact",
  () => {
    const a = area(plan(), "pilot");
    assert.equal(a.basis, "INPUTS_RECORDED");
    assert.match(
      a.notes.join(" "),
      /No improvement or causal conclusion is calculated.*do not establish.*official impact/,
    );
  },
);
check("Edition strings alone never assert archive completeness", () => {
  const a = area(plan(), "guidance");
  assert.match(a.notes.join(" "), /alone do not prove.*available/);
  const p = plan();
  delete p.data.content_versions;
  assert.equal(area(p, "guidance").basis, "INTERPRETATION_UNKNOWN");
});
check(
  "Additional private/future metadata produces byte-identical review output",
  () => {
    const p = plan(),
      expected = captureReviewSnapshot(p, context);
    p.data.impact_reference = {
      programme_id: "PRIVATE-SENTINEL",
      reference_exists: true,
    };
    p.data.human_advice_count = 123;
    p.advice_problem = "PRIVATE-SENTINEL";
    p.data.planning.cost_comparison.secret_provider_credentials =
      "PRIVATE-SENTINEL";
    assert.deepEqual(captureReviewSnapshot(p, context), expected);
    assert.doesNotMatch(
      JSON.stringify(expected),
      /PRIVATE-SENTINEL|impact_reference|human_advice/,
    );
  },
);
check(
  "Source public payload stays untouched and raw notes are not retained",
  () => {
    const p = plan();
    p.data.procurement.vendor_questions = "PUBLIC-RAW-NOTE-SENTINEL";
    const before = structuredClone(p);
    const s = captureReviewSnapshot(p, context);
    assert.deepEqual(p, before);
    assert.doesNotMatch(JSON.stringify(s), /PUBLIC-RAW-NOTE-SENTINEL/);
  },
);
process.on("exit", () => {
  writeFileSync(
    evidence,
    JSON.stringify(
      {
        scope:
          "Registered saved-review pure public snapshot checks only; no actual UI/API/database authority or accepted requirement evidence",
        results,
        source_fingerprints: before,
        current_sources: hashes(),
        sources_unchanged: JSON.stringify(before) === JSON.stringify(hashes()),
      },
      null,
      2,
    ) + "\n",
  );
});
