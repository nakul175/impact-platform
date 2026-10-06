import guidance from "./walkthrough-guidance.json" with { type: "json" };

export const WALKTHROUGH_BASE = "fictional-walkthrough/";

/** Only bundled public guidance. There is deliberately no network fallback,
 * receipt, saved-plan selector, persistence or real membership context here. */
export async function fictionalWalkthroughRequest(
  path: string,
  options: RequestInit = {},
): Promise<unknown> {
  if (options.signal?.aborted)
    throw new DOMException("Cancelled", "AbortError");
  if (
    (options.method ?? "GET").toUpperCase() !== "GET" ||
    options.body != null ||
    options.headers != null ||
    options.credentials != null
  )
    throw new Error(
      "This fictional walkthrough cannot save, send or connect to an organisation.",
    );
  if (path === WALKTHROUGH_BASE + "ai-enablement/task-templates")
    return structuredClone(guidance.practice);
  if (path === WALKTHROUGH_BASE + "ai-enablement/catalog")
    return structuredClone(guidance.catalog);
  throw new Error(
    "This action is unavailable in the fictional walkthrough. Nothing was sent or saved.",
  );
}
