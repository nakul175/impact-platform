import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";
import {
  applyProcurementPreview,
  currentProcurementPreview,
  prepareProcurementText,
  previewProcurement,
} from "../../apps/web/src/AIProcurementPreviewModel.ts";

const repo = fileURLToPath(new URL("../../", import.meta.url));
// Private preparation points this only at the frozen local source tree. A
// registered run defaults to its own checkout; no HTTP or provider is involved.
const inputsRoot = process.env.IMPACT_PROCUREMENT_CHECK_INPUT_ROOT || repo;
const evidence =
  process.env.IMPACT_PROCUREMENT_CHECK_REPORT ||
  resolve(
    repo,
    "docs/evidence/sprint-0.36-procurement-preview-model-tests.json",
  );
const inputPaths = [
  "apps/api/impact_api/ai_enablement_catalog.py",
  "apps/api/impact_api/ai_solutions_catalog.py",
  "apps/api/impact_api/ai_learning_content.py",
];
function digest(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}
function fingerprints() {
  return {
    "apps/web/src/AIProcurementPreviewModel.ts": digest(
      resolve(repo, "apps/web/src/AIProcurementPreviewModel.ts"),
    ),
    "tools/browser/ai-procurement-preview-model-check.mjs": digest(
      fileURLToPath(import.meta.url),
    ),
    ...Object.fromEntries(
      inputPaths.map((path) => [path, digest(resolve(inputsRoot, path))]),
    ),
  };
}
const before = fingerprints();
const published = JSON.parse(
  execFileSync(
    resolve(inputsRoot, ".venv/bin/python"),
    [
      "-c",
      [
        "import json",
        "from impact_api.ai_enablement_catalog import catalog, validate_profile",
        "from impact_api.ai_solutions_catalog import solutions_catalog",
        "profile = dict(sector='HEALTH', team_size=4, goal='Improve invented messages Café 🧭\\nKeep review human', data_readiness='BASIC', ai_experience='EXPERIMENTING', sensitive_data=False)",
        "validate_profile(profile)",
        "print(json.dumps(dict(catalog=catalog(), solutions=solutions_catalog(), profile=profile), ensure_ascii=False))",
      ].join("\n"),
    ],
    {
      cwd: inputsRoot,
      env: {
        PYTHONPATH: resolve(inputsRoot, "apps/api"),
        PYTHONDONTWRITEBYTECODE: "1",
        PYTHONHASHSEED: "0",
      },
      encoding: "utf8",
      timeout: 15000,
      maxBuffer: 1024 * 1024,
    },
  ),
);
const selectedIds = ["chatgpt_business", "claude_team"];
const empty = () => ({
  requirements: "",
  data_boundary: "",
  budget_notes: "",
  vendor_questions: "",
});
function source() {
  const selected = selectedIds.map((id) => {
    const row = published.solutions.solutions.find((item) => item.id === id);
    assert(
      row,
      "The published selected tool must exist; never invent a replacement",
    );
    return structuredClone(row);
  });
  return {
    context: {
      base: "/v1/tenants/invented/",
      principalId: "invented-editor",
      sessionIdentity: "invented-session",
    },
    head: { object_id: "invented-plan", revision_id: "invented-revision" },
    profile: structuredClone(published.profile),
    catalog: structuredClone(published.catalog),
    solutionsVersion: published.solutions.content_version,
    solutionIds: [...selectedIds],
    selected,
    selectedSourceKey: JSON.stringify(selected),
    value: empty(),
    planKey: JSON.stringify({
      title: "Invented work",
      profile: published.profile,
      procurement: empty(),
    }),
    planGeneration: 0,
    interactionGeneration: 0,
    canManage: true,
    mutationBlocked: false,
  };
}

// Independent pinned expected product copy. These are not calculated with the
// model or a duplicate fill algorithm. Source changes require deliberate review.
const nonSensitiveBoundary =
  "Use synthetic or approved non-sensitive material in the pilot. Do not send participant identities, confidential records or credentials. Confirm retention, deletion and permissions before wider use.";
const sensitiveBoundary =
  "The intended work involves sensitive information. Begin with synthetic material only. An authorised data steward must approve a specific data boundary, access controls, retention and supplier processing terms before any real data is used.";
const budgetNotes =
  "Request the total cost of the bounded pilot, including seats, API usage, onboarding, support, taxes and exit costs. Confirm any nonprofit eligibility and renewal conditions directly with the supplier.";
const questions = `Can the provider demonstrate our acceptance tests?
What fails and how is it detected?
What data leaves our environment?
Who can access it, train on it or retain it?
How are deletion and export verified?
What are setup, usage, review, support and exit costs?
What spending controls and alerts are available?
Can intended users operate it in their languages?
Does it work with our accessibility and connectivity needs?
Who owns integration and incidents?
Which milestones require our acceptance before payment?
Can we export data and configuration in usable formats?
What happens if the service or provider closes?
Who approves outputs and consequential decisions?
How are conflicts of interest and provider claims reviewed?
Which exact plan and contract govern our uploads, prompts and generated content?
How are training use, retention, deletion, subprocessors and processing regions handled?
Who can access connected documents, and how are existing permissions enforced?
Can we test with public or synthetic material before any approved sensitive-data pilot?
Which exact plan and contract govern our uploads, prompts and generated content?
How are training use, retention, deletion, subprocessors and processing regions handled?
Who can access connected documents, and how are existing permissions enforced?
Can we test with public or synthetic material before any approved sensitive-data pilot?`;
const expected = {
  requirements:
    "Pilot goal: Improve invented messages Café 🧭\nKeep review human\nTeam: 4 people.\nShortlist: ChatGPT Business, Claude Team.\nRequire human review of every output and a documented exit/export process.",
  data_boundary: nonSensitiveBoundary,
  budget_notes: budgetNotes,
  vendor_questions: questions,
};
const results = [];
function check(name, fn) {
  test(name, () => {
    try {
      fn();
      results.push({ name, status: "passed" });
    } catch (error) {
      results.push({ name, status: "failed", error: String(error) });
      throw error;
    }
  });
}
function changed(s, preview, mutation) {
  assert(
    preview,
    "Control preview must be usable before any negative assertion",
  );
  assert.equal(currentProcurementPreview(s, preview), true);
  const next = structuredClone(s);
  mutation(next);
  assert.equal(currentProcurementPreview(next, preview), false);
  assert.equal(applyProcurementPreview(next, preview), null);
}

check(
  "Actual current local generators supply the public catalog and valid profile",
  () => {
    assert.equal(published.catalog.content_version, "nonprofit-2026-10-05.3");
    assert.equal(
      published.solutions.content_version,
      "nonprofit-solutions-2026-10-05.1",
    );
    assert.deepEqual(
      published.catalog.procurement_criteria.map((r) => r.id),
      [
        "fitness",
        "data",
        "cost",
        "inclusion",
        "delivery",
        "exit",
        "governance",
      ],
    );
    assert.equal(published.solutions.solutions.length, 8);
  },
);
check(
  "Exact existing four-field text retained for non-sensitive profile",
  () => {
    assert.deepEqual(prepareProcurementText(source()), expected);
  },
);
check(
  "Exact existing sensitive-data boundary retained without other string changes",
  () => {
    const s = source();
    s.profile.sensitive_data = true;
    assert.deepEqual(prepareProcurementText(s), {
      ...expected,
      data_boundary: sensitiveBoundary,
    });
  },
);
check("Exact fallback supplier wording without shortlist", () => {
  const s = source();
  s.solutionIds = [];
  s.selected = [];
  assert.equal(
    prepareProcurementText(s).requirements,
    "Pilot goal: Improve invented messages Café 🧭\nKeep review human\nTeam: 4 people.\nShortlist: a supplier to be selected.\nRequire human review of every output and a documented exit/export process.",
  );
  assert.equal(
    prepareProcurementText(s).vendor_questions,
    questions.split("\n").slice(0, 15).join("\n"),
  );
});
check(
  "Current catalog and supplier question ordering matches a literal expectation",
  () => {
    assert.equal(prepareProcurementText(source()).vendor_questions, questions);
    const s = source();
    s.selected.reverse();
    assert.match(
      prepareProcurementText(s).requirements,
      /Shortlist: Claude Team, ChatGPT Business\./,
    );
  },
);
check(
  "Unicode and newline text is preserved without normalizing existing work",
  () => {
    const s = source();
    s.value.requirements = "Own Cafe\u0301\nrequirements 🧭\r\n";
    const beforeValue = s.value.requirements;
    const p = previewProcurement(s);
    assert(p);
    assert.equal(p.before.requirements, beforeValue);
    assert.equal(p.proposed.requirements, expected.requirements);
    assert.notEqual(p.before.requirements, beforeValue.normalize("NFC"));
  },
);
check(
  "Preview retains all existing fields byte-for-byte without mutating source",
  () => {
    const s = source();
    s.value = {
      requirements: "Own Café\nrequirements",
      data_boundary: "Own boundary",
      budget_notes: "Own budget",
      vendor_questions: "Own questions",
    };
    const exact = JSON.stringify(s),
      p = previewProcurement(s);
    assert(p);
    assert.equal(p.hasExistingWork, true);
    assert.deepEqual(p.before, s.value);
    assert.equal(JSON.stringify(s), exact);
    p.before.requirements = "tampered";
    assert.equal(s.value.requirements, "Own Café\nrequirements");
    assert.equal(applyProcurementPreview(s, p), null);
  },
);
check(
  "Apply returns exactly four fields and a bounded parent merge retains unrelated work",
  () => {
    const s = source(),
      p = previewProcurement(s);
    assert(p);
    const value = applyProcurementPreview(s, p);
    assert(value);
    assert.deepEqual(Object.keys(value).sort(), Object.keys(empty()).sort());
    const plan = {
      title: "Own work",
      planning: {
        task_practice: {
          draft: "Exact learner Café\nwork",
          review_notes: "Exact notes",
        },
      },
      learning_completed: ["foundations:0"],
      pilot: { completed_actions: ["DEFINE_GOAL"] },
      procurement: s.value,
    };
    const merged = { ...plan, procurement: value };
    assert.deepEqual({ ...merged, procurement: plan.procurement }, plan);
    assert.deepEqual(value, expected);
  },
);
check("Empty or whitespace goal refuses new preview", () => {
  for (const goal of ["", " \n \t"]) {
    const s = source();
    s.profile.goal = goal;
    assert.equal(previewProcurement(s), null);
  }
});
check("Current management hint is required for preview and prior apply", () => {
  const s = source(),
    p = previewProcurement(s);
  assert(p);
  s.canManage = false;
  assert.equal(previewProcurement(s), null);
  assert.equal(applyProcurementPreview(s, p), null);
});
check("Pending saved-plan action refuses new preview and prior apply", () => {
  const s = source(),
    p = previewProcurement(s);
  assert(p);
  s.mutationBlocked = true;
  assert.equal(previewProcurement(s), null);
  assert.equal(applyProcurementPreview(s, p), null);
});
for (const key of ["base", "principalId", "sessionIdentity"])
  check("Exact actor/session/context binding: " + key, () => {
    const s = source();
    changed(s, previewProcurement(s), (n) => {
      n.context[key] += "-changed";
    });
  });
for (const key of ["object_id", "revision_id"])
  check("Exact saved-head binding: " + key, () => {
    const s = source();
    changed(s, previewProcurement(s), (n) => {
      n.head[key] += "-changed";
    });
  });
check("New-plan versus saved-plan identity invalidates preview", () => {
  const s = source();
  changed(s, previewProcurement(s), (n) => {
    n.head = null;
  });
});
check(
  "Full profile binding includes a field not interpolated into text",
  () => {
    const s = source();
    changed(s, previewProcurement(s), (n) => {
      n.profile.data_readiness = "STRUCTURED";
    });
  },
);
check(
  "Ordered shortlist and unavailable stored selection invalidate preview",
  () => {
    const s = source(),
      p = previewProcurement(s);
    changed(s, p, (n) => {
      n.solutionIds.reverse();
    });
    changed(s, p, (n) => {
      n.solutionIds.push("unavailable-stored-id");
    });
  },
);
check("Full selected directory row and relevant wording stay bound", () => {
  const s = source(),
    p = previewProcurement(s);
  changed(s, p, (n) => {
    n.selectedSourceKey += "changed commercial metadata";
  });
  changed(s, p, (n) => {
    n.selected[0].name = "Changed tool name";
  });
});
check(
  "Criterion identity, label, question content and ordering stay bound",
  () => {
    const s = source(),
      p = previewProcurement(s);
    for (const mutation of [
      (n) => {
        n.catalog.procurement_criteria[0].id = "changed";
      },
      (n) => {
        n.catalog.procurement_criteria[0].title = "Changed label";
      },
      (n) => {
        n.catalog.procurement_criteria[0].questions[0] = "Changed question";
      },
      (n) => {
        n.catalog.procurement_criteria.reverse();
      },
      (n) => {
        n.catalog.procurement_criteria[0].questions.reverse();
      },
    ])
      changed(s, p, mutation);
  },
);
check("Current catalog and solutions editions stay bound", () => {
  const s = source(),
    p = previewProcurement(s);
  changed(s, p, (n) => {
    n.catalog.content_version = "changed-edition";
  });
  changed(s, p, (n) => {
    n.solutionsVersion = "changed-edition";
  });
});
check("Each existing procurement field edit invalidates confirmation", () => {
  for (const key of Object.keys(empty())) {
    const s = source();
    changed(s, previewProcurement(s), (n) => {
      n.value[key] = "Own later edit";
    });
  }
});
check("Whole plan edits outside procurement invalidate confirmation", () => {
  const s = source();
  changed(s, previewProcurement(s), (n) => {
    n.planKey += "changed practice notes";
  });
});
check(
  "Observed edit then undo cannot restore confirmation with parent generation",
  () => {
    const s = source();
    changed(s, previewProcurement(s), (n) => {
      n.planGeneration += 2;
    });
  },
);
check(
  "Observed management loss then return cannot restore confirmation",
  () => {
    const s = source();
    changed(s, previewProcurement(s), (n) => {
      n.interactionGeneration += 2;
    });
  },
);
check("Observed pending save then return cannot restore confirmation", () => {
  const s = source();
  changed(s, previewProcurement(s), (n) => {
    n.interactionGeneration += 2;
  });
});
check("Tampered proposed text or binding cannot be applied", () => {
  for (const mutate of [
    (p) => {
      p.proposed.requirements = "Invented award";
    },
    (p) => {
      p.binding += "tampered";
    },
  ]) {
    const s = source(),
      p = previewProcurement(s);
    assert(p);
    mutate(p);
    assert.equal(applyProcurementPreview(s, p), null);
  }
});
check(
  "Malformed known values, generations and oversize budget refuse preview",
  () => {
    for (const mutation of [
      (s) => {
        s.profile.team_size = NaN;
      },
      (s) => {
        s.planGeneration = -1;
      },
      (s) => {
        s.interactionGeneration = Number.MAX_SAFE_INTEGER + 1;
      },
      (s) => {
        s.value.budget_notes = "x".repeat(501);
      },
    ]) {
      const s = source();
      mutation(s);
      assert.equal(previewProcurement(s), null);
    }
  },
);
check(
  "Each existing field accepts its exact JS length boundary and rejects the next unit",
  () => {
    for (const [key, limit] of [
      ["requirements", 2000],
      ["data_boundary", 2000],
      ["budget_notes", 500],
      ["vendor_questions", 2000],
    ]) {
      for (const length of [limit - 1, limit]) {
        const s = source();
        s.value[key] = "x".repeat(length);
        const p = previewProcurement(s);
        assert(p);
        assert.equal(p.before[key].length, length);
      }
      const s = source();
      s.value[key] = "x".repeat(limit + 1);
      assert.equal(previewProcurement(s), null);
    }
  },
);
check(
  "Existing UTF-16 requirement cap preserves a full pair at the exact boundary",
  () => {
    // Synthetic long directory wording is a helper boundary fixture, not a real
    // published tool or server-valid selection. No production catalog is changed.
    const s = source();
    s.profile.goal = "G";
    const prefix = "Pilot goal: G\nTeam: 4 people.\nShortlist: ";
    s.selected = [
      {
        id: "synthetic-long-name",
        name: "x".repeat(2000 - prefix.length - 2) + "🧭",
        data_review_questions: [],
      },
    ];
    const text = prepareProcurementText(s).requirements;
    assert.equal(text, prefix + "x".repeat(2000 - prefix.length - 2) + "🧭");
    assert.equal(text.length, 2000);
    assert.equal(text.charCodeAt(1998), 0xd83e);
    assert.equal(text.charCodeAt(1999), 0xdded);
  },
);
check(
  "Existing requirement cap retains its split-surrogate behavior without a new claim",
  () => {
    const s = source();
    s.profile.goal = "G";
    const prefix = "Pilot goal: G\nTeam: 4 people.\nShortlist: ";
    s.selected = [
      {
        id: "synthetic-long-name",
        name: "x".repeat(2000 - prefix.length - 1) + "🧭",
        data_review_questions: [],
      },
    ];
    const text = prepareProcurementText(s).requirements;
    assert.equal(
      text,
      prefix + "x".repeat(2000 - prefix.length - 1) + "\ud83e",
    );
    assert.equal(text.length, 2000);
    assert.equal(text.charCodeAt(1999), 0xd83e);
  },
);
check(
  "Existing question cap preserves exact newline and UTF-16 boundary",
  () => {
    const s = source();
    s.catalog.procurement_criteria = [
      {
        id: "synthetic",
        title: "Boundary fixture",
        questions: [
          "Café\n" + "x".repeat(1994) + "🧭",
          "Never visible after boundary",
        ],
      },
    ];
    s.selected = [];
    const text = prepareProcurementText(s).vendor_questions;
    assert.equal(text, "Café\n" + "x".repeat(1994) + "\ud83e");
    assert.equal(text.length, 2000);
    assert.doesNotMatch(text, /Never visible/);
    assert.equal(prepareProcurementText(s).data_boundary, nonSensitiveBoundary);
    assert.equal(prepareProcurementText(s).budget_notes, budgetNotes);
  },
);
check(
  "Existing worksheet whitespace still requires explicit replacement disclosure",
  () => {
    const s = source();
    s.value.vendor_questions = " \n";
    const p = previewProcurement(s);
    assert(p);
    assert.equal(p.hasExistingWork, true);
    assert.equal(p.before.vendor_questions, " \n");
  },
);
check(
  "All model and actual generator source bytes stay unchanged during pure checks",
  () => {
    assert.deepEqual(fingerprints(), before);
  },
);

process.on("exit", () => {
  writeFileSync(
    evidence,
    JSON.stringify(
      {
        recorded_at: new Date().toISOString(),
        scope:
          "Private proposed registered procurement-preview pure-model checks using actual local public catalog generators; no integrated UI/API/current-authority/server-save or accepted requirement claim",
        runtime: {
          node: process.versions.node,
          input_method:
            "local pure Python catalog()/solutions_catalog(), no HTTP or provider",
          model_method: "actual proposed TS module with Node type stripping",
        },
        input_editions: {
          catalog: published.catalog.content_version,
          solutions: published.solutions.content_version,
        },
        generated_public_input_sha256: createHash("sha256")
          .update(JSON.stringify(published))
          .digest("hex"),
        results,
        source_fingerprints: before,
        current_sources: fingerprints(),
        sources_unchanged:
          JSON.stringify(before) === JSON.stringify(fingerprints()),
        limits: [
          "Client hints do not grant server authority",
          "Parent merge and monotonic generation wiring require actual integrated browser qualification",
          "UTF-16 split behavior is existing compatibility, not Unicode correctness or server acceptance",
          "No supplier messaging, purchase, approval, persistence or provider call occurs in these checks",
        ],
      },
      null,
      2,
    ) + "\n",
  );
});
