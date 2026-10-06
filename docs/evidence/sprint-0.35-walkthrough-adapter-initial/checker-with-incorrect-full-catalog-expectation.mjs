import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import {
  fictionalWalkthroughRequest as request,
  WALKTHROUGH_BASE as base,
} from "../../apps/web/src/AIFictionalWalkthroughAdapter.ts";

const repo = new URL("../../", import.meta.url);
const files = [
  "apps/web/src/AIFictionalWalkthroughAdapter.ts",
  "apps/web/src/walkthrough-guidance.json",
  "apps/api/impact_api/ai_enablement_catalog.py",
  "apps/api/impact_api/ai_learning_content.py",
  "apps/api/impact_api/ai_task_practice.py",
  "tools/browser/ai-walkthrough-adapter-check.mjs",
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
const before = hashes();
const started = new Date().toISOString();
const results = [];
const check = async (name, run) => {
  await run();
  results.push({ name, status: "passed" });
};

await check(
  "Bundled guidance exactly matches the current public source projection",
  async () => {
    const loaded = spawnSync(
      process.env.PYTHON || ".venv/bin/python",
      [
        "-c",
        "import json,sys;sys.path.insert(0,'apps/api');from impact_api.ai_enablement_catalog import catalog;from impact_api.ai_task_practice import task_templates;c=catalog();print(json.dumps({'catalog':{k:c[k] for k in ['content_version','learning_paths','procurement_criteria']},'practice':task_templates()}))",
      ],
      { cwd: fileURLToPath(repo), encoding: "utf8" },
    );
    assert.equal(loaded.status, 0, "Registered pure public guidance must load");
    const source = JSON.parse(loaded.stdout);
    assert.deepEqual(
      await request(base + "ai-enablement/catalog"),
      source.catalog,
    );
    assert.deepEqual(
      await request(base + "ai-enablement/task-templates"),
      source.practice,
    );
  },
);

await check("Both public guides return isolated clones", async () => {
  const first = await request(base + "ai-enablement/task-templates");
  assert(first.templates.length > 0);
  const original = first.templates[0].example_brief;
  first.templates[0].example_brief = "caller mutation";
  assert.equal(
    (await request(base + "ai-enablement/task-templates")).templates[0]
      .example_brief,
    original,
  );
  const catalog = await request(base + "ai-enablement/catalog");
  assert(catalog.learning_paths.length > 0);
  const catalogOriginal = structuredClone(catalog);
  catalog.learning_paths.length = 0;
  assert.deepEqual(
    await request(base + "ai-enablement/catalog"),
    catalogOriginal,
  );
});
await check(
  "Only the two exact bundled guide routes are available",
  async () => {
    for (const path of [
      "/auth/me",
      "/v1/tenants/example/ai-enablement/catalog",
      base + "ai-enablement/plans",
      base + "ai-enablement/advisory",
      base + "ai-enablement/human-advice",
      base + "ai-enablement/task-templates?extra=1",
      "https://example.org",
      base + "../catalog",
    ])
      await assert.rejects(request(path), /unavailable/);
  },
);
await check("Mutation methods and HEAD refuse without a fallback", async () => {
  for (const method of ["POST", "PUT", "PATCH", "DELETE", "HEAD"])
    await assert.rejects(
      request(base + "ai-enablement/task-templates", { method, body: "{}" }),
      /cannot save/,
    );
});
await check(
  "Bodies and caller authentication context refuse on GET",
  async () => {
    for (const options of [
      { body: "{}" },
      { headers: { Authorization: "fictional" } },
      { credentials: "include" },
    ])
      await assert.rejects(
        request(base + "ai-enablement/catalog", options),
        /cannot save/,
      );
  },
);
await check("Cancelled local guide requests return AbortError", async () => {
  const controller = new AbortController();
  controller.abort();
  await assert.rejects(
    request(base + "ai-enablement/catalog", { signal: controller.signal }),
    { name: "AbortError" },
  );
});
await check(
  "Adapter source contains no ambient network or storage access",
  () => {
    const raw = readFileSync(
      new URL("apps/web/src/AIFictionalWalkthroughAdapter.ts", repo),
      "utf8",
    );
    assert(
      !/\b(fetch|XMLHttpRequest|WebSocket|sendBeacon|localStorage|sessionStorage|indexedDB|cookie)\s*[.(=]/.test(
        raw,
      ),
    );
  },
);
const after = hashes();
assert.deepEqual(after, before);
writeFileSync(
  new URL("docs/evidence/sprint-0.35-walkthrough-adapter-tests.json", repo),
  JSON.stringify(
    {
      started_at: started,
      recorded_at: new Date().toISOString(),
      scope:
        "Registered pure checks of the actual clone-only bundled walkthrough adapter. Browser network/storage traps are qualified separately; no API, authentication, database, onboarding or authority acceptance.",
      results,
      qualified_sources: before,
      current_sources: after,
      sources_unchanged: true,
    },
    null,
    2,
  ) + "\n",
);
console.log(`${results.length} registered walkthrough adapter groups passed`);
