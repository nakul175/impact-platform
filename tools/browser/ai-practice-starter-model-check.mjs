import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { spawnSync } from "node:child_process";
import {
  applyPracticeStarter,
  currentPracticeStarter,
  previewPracticeStarter,
} from "../../apps/web/src/AIPracticeStarterModel.ts";

const root = process.cwd();
const sourceFiles = [
  "apps/web/src/AIPracticeStarterModel.ts",
  "apps/api/impact_api/ai_task_practice.py",
  "tools/browser/ai-practice-starter-model-check.mjs",
];
const hashes = async () =>
  Object.fromEntries(
    await Promise.all(
      sourceFiles.map(async (name) => [
        name,
        createHash("sha256")
          .update(await fs.readFile(path.join(root, name)))
          .digest("hex"),
      ]),
    ),
  );
const before = await hashes(),
  results = [],
  started = new Date().toISOString();
const loaded = spawnSync(
  process.env.PYTHON || ".venv/bin/python",
  [
    "-c",
    "import json,sys;sys.path.insert(0,'apps/api');from impact_api.ai_task_practice import task_templates;print(json.dumps(task_templates()))",
  ],
  { cwd: root, encoding: "utf8" },
);
assert.equal(
  loaded.status,
  0,
  "Current public task templates must load from the registered pure API module",
);
const guide = JSON.parse(loaded.stdout);
const source = (value = null, overrides = {}) => ({
  context: "synthetic-tenant|synthetic-member|saved-plan|saved-revision",
  canManage: true,
  guide,
  templateId: "invitation",
  value,
  ...overrides,
});
const work = () => ({
  template_id: "invitation",
  brief: "Learner's own invented brief\n ",
  draft: "Learner draft with <literal text> and Unicode Ω.",
  review_notes: "Keep these questions.\n",
  checked_steps: ["source_facts", "privacy"],
});
function test(name, run) {
  run();
  results.push({ name, status: "passed" });
}
test("preview changes no learner worksheet and no completion", () => {
  const existing = work(),
    original = structuredClone(existing),
    s = source(existing);
  const p = previewPracticeStarter(s);
  assert(p.hasExistingWork);
  assert.deepEqual(existing, original);
  assert.deepEqual(s.value.checked_steps, original.checked_steps);
});
test("first starter uses exact loaded source and existing five-field shape", () => {
  const s = source(),
    p = previewPracticeStarter(s),
    result = applyPracticeStarter(s, p);
  assert.deepEqual(result, {
    template_id: "invitation",
    brief: guide.templates[0].example_brief,
    draft: "",
    review_notes: "",
    checked_steps: [],
  });
});
test("explicit replacement preserves existing draft and review bytes while clearing checks", () => {
  const original = work(),
    s = source(original),
    result = applyPracticeStarter(s, previewPracticeStarter(s));
  assert.equal(result.brief, guide.templates[0].example_brief);
  assert.equal(result.draft, original.draft);
  assert.equal(result.review_notes, original.review_notes);
  assert.deepEqual(result.checked_steps, []);
  assert.notEqual(result, original);
  assert.deepEqual(original.checked_steps, ["source_facts", "privacy"]);
});
test("read-only study cannot apply a starter", () => {
  const s = source(work(), { canManage: false }),
    p = previewPracticeStarter(s);
  assert(p);
  assert.equal(applyPracticeStarter(s, p), null);
});
test("lost current management or pending-mutation permission blocks existing confirmation", () => {
  const s = source(work()),
    p = previewPracticeStarter(s);
  assert.equal(applyPracticeStarter({ ...s, canManage: false }, p), null);
});
for (const [name, altered] of [
  ["tenant", "other-tenant|synthetic-member|saved-plan|saved-revision"],
  ["principal", "synthetic-tenant|other-member|saved-plan|saved-revision"],
  ["plan", "synthetic-tenant|synthetic-member|other-plan|saved-revision"],
  ["revision", "synthetic-tenant|synthetic-member|saved-plan|other-revision"],
])
  test(`changed ${name} context invalidates preview`, () => {
    const s = source(work()),
      p = previewPracticeStarter(s);
    assert.equal(currentPracticeStarter({ ...s, context: altered }, p), false);
    assert.equal(applyPracticeStarter({ ...s, context: altered }, p), null);
  });
test("changed guidance edition cannot apply previously previewed wording", () => {
  const s = source(work()),
    p = previewPracticeStarter(s);
  assert.equal(
    applyPracticeStarter(
      { ...s, guide: { ...guide, content_version: "new-edition" } },
      p,
    ),
    null,
  );
});
test("changed wording under same edition cannot apply old preview", () => {
  const s = source(work()),
    p = previewPracticeStarter(s),
    next = structuredClone(guide);
  next.templates[0].example_brief += "Changed current source.";
  assert.equal(applyPracticeStarter({ ...s, guide: next }, p), null);
});
test("learner edits made after preview are not overwritten", () => {
  const s = source(work()),
    p = previewPracticeStarter(s);
  for (const field of ["brief", "draft", "review_notes", "checked_steps"]) {
    const value = structuredClone(s.value);
    value[field] = field === "checked_steps" ? [] : "Newer learner text";
    assert.equal(applyPracticeStarter({ ...s, value }, p), null);
  }
});
test("retired mismatched absent or duplicate task refuses without selecting a fallback", () => {
  for (const s of [
    source(work(), { templateId: "retired" }),
    source({ ...work(), template_id: "other-task" }),
    source(work(), { guide: null }),
    source(work(), {
      guide: { ...guide, templates: [...guide.templates, guide.templates[0]] },
    }),
  ])
    assert.equal(previewPracticeStarter(s), null);
});
test("oversized missing and invalid synthetic examples fail without truncation", () => {
  for (const value of ["", " ", "x".repeat(2501), null]) {
    const next = structuredClone(guide);
    next.templates[0].example_brief = value;
    assert.equal(previewPracticeStarter(source(null, { guide: next })), null);
  }
  assert.equal(
    previewPracticeStarter(
      source(null, { guide: { content_version: "version" } }),
    ),
    null,
  );
});
test("a draft-only or whitespace-only worksheet still requires explicit replacement", () => {
  for (const value of [
    { ...work(), brief: "", review_notes: "", checked_steps: [] },
    { ...work(), brief: " ", draft: "", review_notes: "", checked_steps: [] },
  ])
    assert.equal(previewPracticeStarter(source(value)).hasExistingWork, true);
});
test("each existing loaded task gives its own exact example without ID invention", () => {
  for (const task of guide.templates) {
    const s = source(null, { templateId: task.id }),
      p = previewPracticeStarter(s),
      result = applyPracticeStarter(s, p);
    assert.equal(result.template_id, task.id);
    assert.equal(result.brief, task.example_brief);
    assert.equal(result.draft, "");
    assert.equal(result.review_notes, "");
    assert.deepEqual(result.checked_steps, []);
  }
});
const after = await hashes();
assert.deepEqual(after, before);
await fs.writeFile(
  path.join(
    root,
    "docs/evidence/sprint-0.35-practice-starter-model-tests.json",
  ),
  JSON.stringify(
    {
      scope:
        "Registered guided-practice model checks against actual current public task-template module; no HTTP/native database/learner competency or formal acceptance",
      started_at: started,
      finished_at: new Date().toISOString(),
      results,
      qualified_sources: before,
      current_sources: after,
      sources_unchanged: true,
    },
    null,
    2,
  ) + "\n",
);
console.log(
  `${results.length} registered model groups passed; source hashes unchanged.`,
);
