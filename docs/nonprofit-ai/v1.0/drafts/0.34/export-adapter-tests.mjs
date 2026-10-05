import assert from "node:assert/strict";
import { createHash, webcrypto } from "node:crypto";
import { test } from "node:test";
import {
  provisionalCopyAdapter as adapter,
  verifyCopy,
  COPY_SCHEMA,
  COPY_RENDERER,
} from "./adapter-output/export-adapter.js";
if (!globalThis.crypto)
  Object.defineProperty(globalThis, "crypto", { value: webcrypto });
const PLAN = "11111111-1111-4111-8111-111111111111";
const REV = "22222222-2222-4222-8222-222222222222";
const OP = "33333333-3333-4333-8333-333333333333";
const AUDIT = "44444444-4444-4444-8444-444444444444";
const AUDIT_REV = "55555555-5555-4555-8555-555555555555";
const CORR = "66666666-6666-4666-8666-666666666666";
function response(
  content = '{\n  "title": "Café — समुदाय",\n  "record_status": "Draft"\n}\n',
) {
  const digest = createHash("sha256").update(content, "utf8").digest("hex");
  const size = Buffer.byteLength(content, "utf8");
  return {
    content,
    manifest: {
      plan_id: PLAN,
      revision_id: REV,
      title: "Café — समुदाय",
      saved_at: "2026-10-05T09:00:00Z",
      generated_at: "2026-10-05T11:00:00Z",
      schema: COPY_SCHEMA,
      renderer: COPY_RENDERER,
      filename: `impact-ai-plan-${PLAN}.json`,
      media_type: "application/json",
      content_sha256: digest,
      size_bytes: size,
      replay_expires_at: "2026-10-12T11:00:00Z",
      guidance_status: "PARTIAL",
    },
    receipt: {
      object_id: AUDIT,
      revision_id: AUDIT_REV,
      business_state: "Issued",
      operation_id: OP,
      correlation_id: CORR,
      saved_at: "2026-10-05T11:00:00Z",
      content_sha256: digest,
      byte_count: size,
      replay_until: "2026-10-12T11:00:00Z",
    },
  };
}
test("exact command and saved-revision path contain only the closed internal-self intent", () => {
  assert.deepEqual(adapter.command(OP), {
    operation_id: OP,
    data: { format: "JSON", restriction: "INTERNAL_SELF", acknowledged: true },
  });
  assert.equal(
    adapter.path("/v1/tenants/example/", PLAN, REV),
    `/v1/tenants/example/ai-enablement/plans/${PLAN}/revisions/${REV}/exports`,
  );
  assert.throws(() => adapter.path("/", "../another", REV));
});
test("Unicode UTF-8 bytes and original formatting are preserved exactly", async () => {
  const raw = response();
  const reply = adapter.decode(raw);
  const bytes = await verifyCopy(reply, PLAN, REV, undefined, OP);
  assert.equal(new TextDecoder().decode(bytes), raw.content);
  assert.equal(bytes.byteLength, Buffer.byteLength(raw.content));
  assert.notEqual(bytes.byteLength, raw.content.length);
});
for (const [name, mutate] of [
  ["response extras", (r) => (r.private_reference = "hidden")],
  ["manifest extras", (r) => (r.manifest.advice_case_id = AUDIT)],
  ["receipt extras", (r) => (r.receipt.natural_id = AUDIT)],
  ["missing guidance status", (r) => delete r.manifest.guidance_status],
  ["unknown guidance status", (r) => (r.manifest.guidance_status = "CURRENT")],
  ["unknown renderer", (r) => (r.manifest.renderer = "future-provider-export")],
  ["path filename", (r) => (r.manifest.filename = "../impact-ai-plan.json")],
  [
    "receipt digest mismatch",
    (r) => (r.receipt.content_sha256 = "0".repeat(64)),
  ],
  ["receipt byte mismatch", (r) => r.receipt.byte_count++],
  [
    "issuance timestamp mismatch",
    (r) => (r.receipt.saved_at = "2026-10-05T12:00:00Z"),
  ],
  [
    "expiry timestamp mismatch",
    (r) => (r.receipt.replay_until = "2026-10-12T12:00:00Z"),
  ],
  [
    "expired-before-generation manifest",
    (r) => (r.manifest.replay_expires_at = "2026-10-04T11:00:00Z"),
  ],
  ["invalid receipt selector", (r) => (r.receipt.object_id = "not-an-id")],
  [
    "string byte count",
    (r) => (r.receipt.byte_count = String(r.receipt.byte_count)),
  ],
  ["oversized manifest", (r) => (r.manifest.size_bytes = 1048577)],
])
  test(`closed decoder refuses ${name}`, () => {
    const raw = response();
    mutate(raw);
    assert.throws(() => adapter.decode(raw));
  });
test("content corruption fails byte/digest verification without reserialization", async () => {
  const raw = response();
  raw.content = raw.content.replace("Draft", "Closed");
  await assert.rejects(
    verifyCopy(adapter.decode(raw), PLAN, REV, undefined, OP),
  );
});
test("wrong plan, revision and operation are refused", async () => {
  const reply = adapter.decode(response());
  await assert.rejects(verifyCopy(reply, AUDIT, REV, undefined, OP));
  await assert.rejects(verifyCopy(reply, PLAN, AUDIT_REV, undefined, OP));
  await assert.rejects(verifyCopy(reply, PLAN, REV, undefined, CORR));
});
test("replay pins exact manifest and issuance receipt after lost-response retry", async () => {
  const prior = adapter.decode(response());
  const raw = response();
  raw.receipt.object_id = CORR;
  const next = adapter.decode(raw);
  await assert.rejects(
    verifyCopy(next, PLAN, REV, prior.manifest, OP, prior.receipt),
  );
  await verifyCopy(prior, PLAN, REV, prior.manifest, OP, prior.receipt);
});
test("even valid reissued bytes with the same operation cannot replace a pinned copy", async () => {
  const prior = adapter.decode(response());
  const next = adapter.decode(
    response('{"title":"A different exact package"}\n'),
  );
  await assert.rejects(
    verifyCopy(next, PLAN, REV, prior.manifest, OP, prior.receipt),
  );
});
