// Closed JSON-only internal-self copy contract. Download the original UTF-8
// string only after current-authority replay and immutable receipt verification.
export const MAX_COPY_BYTES = 1_048_576;
export const COPY_SCHEMA = "nonprofit-ai-plan-export-v1";
// Build 0.39.0 (US-DC-04): a copy whose archived guidance is edition v2 (listings with commercial
// disclosures) is package v2; v1 keeps the shape published before. Each package admits only its
// own guidance editions (null: no archive).
export const COPY_SCHEMA_V2 = "nonprofit-ai-plan-export-v2";
export const COPY_SCHEMAS: Record<string, readonly (string | null)[]> = {
  [COPY_SCHEMA]: ["nonprofit-ai-guidance-v1", null],
  [COPY_SCHEMA_V2]: ["nonprofit-ai-guidance-v2"],
};
export const COPY_RENDERER = "nonprofit-ai-plan-json-v1";
export type CopyManifest = {
  plan_id: string;
  revision_id: string;
  title: string;
  saved_at: string;
  generated_at: string;
  schema: string;
  renderer: string;
  filename: string;
  media_type: "application/json";
  content_sha256: string;
  size_bytes: number;
  replay_expires_at: string;
  guidance_status: "COMPLETE" | "PARTIAL" | "UNAVAILABLE";
};
export type CopyReceipt = {
  object_id: string;
  revision_id: string;
  business_state: "Issued";
  operation_id: string;
  correlation_id: string;
  saved_at: string;
  content_sha256: string;
  byte_count: number;
  replay_until: string;
};
export type CopyReply = {
  content: string;
  manifest: CopyManifest;
  receipt: CopyReceipt;
};
export type CopyCommand = {
  operation_id: string;
  data: {
    format: "JSON";
    restriction: "INTERNAL_SELF";
    acknowledged: true;
  };
};
export type CopyIntent = {
  context: string;
  revision: string;
  path: string;
  body: string;
  operationId: string;
  action: "PREPARE" | "DOWNLOAD";
  // This remains with an uncertain download command, so exact retry cannot
  // forget the previously verified immutable copy after a transport failure.
  expectedManifest?: CopyManifest;
  expectedReceipt?: CopyReceipt;
};
export type CopyAdapter = {
  path(base: string, plan: string, revision: string): string;
  command(operationId: string): CopyCommand;
  decode(value: unknown): CopyReply;
};

const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const keys = [
  "plan_id",
  "revision_id",
  "title",
  "saved_at",
  "generated_at",
  "schema",
  "renderer",
  "filename",
  "media_type",
  "content_sha256",
  "size_bytes",
  "replay_expires_at",
  "guidance_status",
] as const;
const receiptKeys = [
  "object_id",
  "revision_id",
  "business_state",
  "operation_id",
  "correlation_id",
  "saved_at",
  "content_sha256",
  "byte_count",
  "replay_until",
] as const;
function record(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value))
    throw new Error("The copy response could not be verified.");
  return value as Record<string, unknown>;
}
function exactKeys(value: Record<string, unknown>, allowed: readonly string[]) {
  if (
    Object.keys(value).length !== allowed.length ||
    Object.keys(value).some((key) => !allowed.includes(key))
  )
    throw new Error("The copy response has unsupported fields.");
}
function text(value: unknown, maximum: number): string {
  if (typeof value !== "string" || !value || value.length > maximum)
    throw new Error("The copy metadata could not be verified.");
  return value;
}
function instant(value: unknown): string {
  const result = text(value, 48);
  if (!/^\d{4}-\d\d-\d\dT/.test(result) || !Number.isFinite(Date.parse(result)))
    throw new Error("The copy timestamp could not be verified.");
  return result;
}
export const planCopyAdapter: CopyAdapter = {
  path(base, plan, revision) {
    if (!uuid.test(plan) || !uuid.test(revision))
      throw new Error("Choose an authorised saved revision.");
    return `${base}ai-enablement/plans/${plan}/revisions/${revision}/exports`;
  },
  command(operationId) {
    return {
      operation_id: operationId,
      data: {
        format: "JSON",
        restriction: "INTERNAL_SELF",
        acknowledged: true,
      },
    };
  },
  decode(value) {
    const response = record(value);
    exactKeys(response, ["content", "manifest", "receipt"]);
    const source = record(response.manifest);
    exactKeys(source, keys);
    const manifest: CopyManifest = {
      plan_id: text(source.plan_id, 36),
      revision_id: text(source.revision_id, 36),
      title: text(source.title, 150),
      saved_at: instant(source.saved_at),
      generated_at: instant(source.generated_at),
      schema: text(source.schema, 100),
      renderer: text(source.renderer, 100),
      filename: text(source.filename, 120),
      media_type: "application/json",
      content_sha256: text(source.content_sha256, 64),
      size_bytes: Number(source.size_bytes),
      replay_expires_at: instant(source.replay_expires_at),
      guidance_status:
        source.guidance_status as CopyManifest["guidance_status"],
    };
    if (
      !uuid.test(manifest.plan_id) ||
      !uuid.test(manifest.revision_id) ||
      source.media_type !== "application/json" ||
      !Object.hasOwn(COPY_SCHEMAS, manifest.schema) ||
      manifest.renderer !== COPY_RENDERER ||
      !/^[a-f0-9]{64}$/.test(manifest.content_sha256) ||
      !/^impact-ai-plan-[a-f0-9-]+\.json$/.test(manifest.filename) ||
      typeof source.size_bytes !== "number" ||
      !Number.isSafeInteger(manifest.size_bytes) ||
      manifest.size_bytes < 2 ||
      manifest.size_bytes > MAX_COPY_BYTES ||
      !["COMPLETE", "PARTIAL", "UNAVAILABLE"].includes(
        manifest.guidance_status,
      ) ||
      Date.parse(manifest.replay_expires_at) <=
        Date.parse(manifest.generated_at)
    )
      throw new Error("The copy metadata could not be verified.");
    if (
      typeof response.content !== "string" ||
      response.content.length > MAX_COPY_BYTES
    )
      throw new Error("The copy exceeds the supported size.");
    const parsed = JSON.parse(response.content);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed))
      throw new Error("The issued copy is not a JSON package.");
    // The package label must be the document's own and match its archived guidance edition.
    const guidance = parsed.guidance;
    if (
      parsed.schema_version !== manifest.schema ||
      !guidance ||
      typeof guidance !== "object" ||
      Array.isArray(guidance) ||
      guidance.status !== manifest.guidance_status ||
      !COPY_SCHEMAS[manifest.schema].includes(
        guidance.snapshot_schema_version ?? null,
      )
    )
      throw new Error("The issued copy does not match its package edition.");
    const receiptSource = record(response.receipt);
    exactKeys(receiptSource, receiptKeys);
    const receipt: CopyReceipt = {
      object_id: text(receiptSource.object_id, 36),
      revision_id: text(receiptSource.revision_id, 36),
      business_state: "Issued",
      operation_id: text(receiptSource.operation_id, 36),
      correlation_id: text(receiptSource.correlation_id, 36),
      saved_at: instant(receiptSource.saved_at),
      content_sha256: text(receiptSource.content_sha256, 64),
      byte_count: Number(receiptSource.byte_count),
      replay_until: instant(receiptSource.replay_until),
    };
    if (
      ![
        receipt.object_id,
        receipt.revision_id,
        receipt.operation_id,
        receipt.correlation_id,
      ].every((id) => uuid.test(id)) ||
      receiptSource.business_state !== "Issued" ||
      receipt.content_sha256 !== manifest.content_sha256 ||
      typeof receiptSource.byte_count !== "number" ||
      receipt.byte_count !== manifest.size_bytes ||
      Date.parse(receipt.saved_at) !== Date.parse(manifest.generated_at) ||
      Date.parse(receipt.replay_until) !==
        Date.parse(manifest.replay_expires_at)
    )
      throw new Error("The copy receipt could not be verified.");
    return { content: response.content, manifest, receipt };
  },
};

export async function verifyCopy(
  reply: CopyReply,
  plan: string,
  revision: string,
  previous?: CopyManifest,
  operationId?: string,
  previousReceipt?: CopyReceipt,
): Promise<Uint8Array> {
  if (
    reply.manifest.plan_id !== plan ||
    reply.manifest.revision_id !== revision
  )
    throw new Error("The copy does not match the chosen saved revision.");
  if (operationId && reply.receipt.operation_id !== operationId)
    throw new Error("The copy receipt does not match this exact request.");
  const bytes = new TextEncoder().encode(reply.content);
  if (
    bytes.byteLength !== reply.manifest.size_bytes ||
    bytes.byteLength > MAX_COPY_BYTES
  )
    throw new Error("The issued copy has an unexpected byte count.");
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  const hex = [...new Uint8Array(digest)]
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
  if (hex !== reply.manifest.content_sha256)
    throw new Error("The issued copy digest could not be verified.");
  if (previous && JSON.stringify(previous) !== JSON.stringify(reply.manifest))
    throw new Error("The exact issued copy changed during replay.");
  if (
    previousReceipt &&
    JSON.stringify(previousReceipt) !== JSON.stringify(reply.receipt)
  )
    throw new Error("The immutable issuance receipt changed during replay.");
  return bytes;
}
