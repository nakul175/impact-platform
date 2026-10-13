import React, { useState } from "react";

type Suggestion = {
  suggestion_id: string;
  viewpoint: string;
  excerpt: string;
  suggested_codes: string[];
  theme: string;
  translation_text: string | null;
  translation_status: "NOT_REQUESTED" | "MACHINE_UNREVIEWED";
};
type Run = { run_id: string; suggestions: Suggestion[] };
type Props = {
  base: string;
  policyVersion: number | null;
  canUse: boolean;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
};

const sha256 = async (value: string) => {
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(value),
  );
  return [...new Uint8Array(digest)]
    .map((item) => item.toString(16).padStart(2, "0"))
    .join("");
};

function ReviewCard({
  base,
  suggestion,
  request,
  explain,
}: {
  base: string;
  suggestion: Suggestion;
  request: Props["request"];
  explain: Props["explain"];
}) {
  const [codes, setCodes] = useState(suggestion.suggested_codes.join(", "));
  const [theme, setTheme] = useState(suggestion.theme);
  const [translation, setTranslation] = useState(
    suggestion.translation_text ?? "",
  );
  const [translationReviewed, setTranslationReviewed] = useState(false);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const review = async (disposition: "ACCEPTED" | "REJECTED") => {
    setError("");
    try {
      await request(
        base +
          `ai-enablement/qualitative-suggestions/${suggestion.suggestion_id}/actions/review`,
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            disposition,
            final_codes:
              disposition === "ACCEPTED"
                ? codes
                    .split(",")
                    .map((item) => item.trim())
                    .filter(Boolean)
                : [],
            final_theme: disposition === "ACCEPTED" ? theme : null,
            final_translation: translation || null,
            translation_reviewed: translationReviewed,
          }),
        },
      );
      setResult(disposition);
    } catch (caught) {
      setError(explain(caught));
    }
  };
  return (
    <article className="ai-result-card">
      <h4>{suggestion.viewpoint}</h4>
      <blockquote>{suggestion.excerpt}</blockquote>
      <label>
        Final code IDs
        <input
          value={codes}
          disabled={Boolean(result)}
          onChange={(event) => setCodes(event.target.value)}
        />
      </label>
      <label>
        Final theme
        <input
          value={theme}
          disabled={Boolean(result)}
          onChange={(event) => setTheme(event.target.value)}
        />
      </label>
      {suggestion.translation_text && (
        <>
          <label>
            Translation
            <textarea
              value={translation}
              disabled={Boolean(result)}
              onChange={(event) => setTranslation(event.target.value)}
            />
          </label>
          <label>
            <input
              type="checkbox"
              checked={translationReviewed}
              disabled={Boolean(result)}
              onChange={(event) => setTranslationReviewed(event.target.checked)}
            />
            I reviewed this machine translation
          </label>
        </>
      )}
      <div className="actions">
        <button
          type="button"
          disabled={Boolean(result)}
          onClick={() => review("ACCEPTED")}
        >
          Accept edited suggestion
        </button>
        <button
          type="button"
          disabled={Boolean(result)}
          onClick={() => review("REJECTED")}
        >
          Reject
        </button>
      </div>
      {error && <p role="alert">{error}</p>}
      {result && <p role="status">Review saved: {result}</p>}
    </article>
  );
}

export function AIQualitativeAssistance({
  base,
  policyVersion,
  canUse,
  request,
  explain,
}: Props) {
  const [form, setForm] = useState({
    codebook_id: "",
    codebook_revision_id: "",
    source_object_id: "",
    source_revision_id: "",
    source_language: "en",
    speaker_reference: "",
    viewpoint: "",
    excerpt: "",
    start_character: "0",
    codes: "",
    theme: "",
    translation_language: "",
    translation_text: "",
  });
  const [run, setRun] = useState<Run | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const update = (name: keyof typeof form, value: string) =>
    setForm((current) => ({ ...current, [name]: value }));
  if (!canUse) return null;
  return (
    <section aria-labelledby="ai-qualitative-assistance">
      <h3 id="ai-qualitative-assistance">Qualitative assistance</h3>
      <p className="muted">
        Suggestions stay tied to an exact source excerpt and approved codebook.
        Every viewpoint is reviewed separately; machine translation remains
        labelled until a person confirms it.
      </p>
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          setBusy(true);
          setError("");
          try {
            const start = Number(form.start_character);
            const result = await request(
              base + "ai-enablement/qualitative-runs",
              {
                method: "POST",
                body: JSON.stringify({
                  operation_id: crypto.randomUUID(),
                  codebook_id: form.codebook_id,
                  codebook_revision_id: form.codebook_revision_id,
                  sources: [
                    {
                      object_id: form.source_object_id,
                      revision_id: form.source_revision_id,
                      language: form.source_language,
                    },
                  ],
                  candidates: [
                    {
                      source_revision_id: form.source_revision_id,
                      viewpoint: form.viewpoint,
                      start_character: start,
                      end_character: start + form.excerpt.length,
                      excerpt: form.excerpt,
                      excerpt_sha256: await sha256(form.excerpt),
                      speaker_reference: form.speaker_reference || null,
                      suggested_codes: form.codes
                        .split(",")
                        .map((item) => item.trim())
                        .filter(Boolean),
                      theme: form.theme,
                      translation_language: form.translation_language || null,
                      translation_text: form.translation_text || null,
                    },
                  ],
                  policy_version: policyVersion,
                  language: "en",
                }),
              },
            );
            setRun(result);
          } catch (caught) {
            setError(explain(caught));
          } finally {
            setBusy(false);
          }
        }}
      >
        {[
          ["codebook_id", "Approved codebook ID"],
          ["codebook_revision_id", "Codebook revision ID"],
          ["source_object_id", "Evidence ID"],
          ["source_revision_id", "Evidence revision ID"],
          ["source_language", "Source language"],
          ["speaker_reference", "Source speaker reference (optional)"],
          ["viewpoint", "Viewpoint label"],
          ["start_character", "Excerpt start character"],
          ["codes", "Suggested code IDs, comma separated"],
          ["theme", "Suggested theme"],
          ["translation_language", "Translation language (optional)"],
        ].map(([name, label]) => (
          <label key={name}>
            {label}
            <input
              required={
                !name.startsWith("translation_") && name !== "speaker_reference"
              }
              value={form[name as keyof typeof form]}
              onChange={(event) =>
                update(name as keyof typeof form, event.target.value)
              }
            />
          </label>
        ))}
        <label>
          Exact source excerpt
          <textarea
            required
            value={form.excerpt}
            onChange={(event) => update("excerpt", event.target.value)}
          />
        </label>
        <label>
          Machine translation (optional)
          <textarea
            value={form.translation_text}
            onChange={(event) => update("translation_text", event.target.value)}
          />
        </label>
        <button disabled={busy || policyVersion === null}>
          {busy ? "Preparing…" : "Prepare suggestions"}
        </button>
      </form>
      {error && <p role="alert">{error}</p>}
      {run?.suggestions.map((suggestion) => (
        <ReviewCard
          key={suggestion.suggestion_id}
          base={base}
          suggestion={suggestion}
          request={request}
          explain={explain}
        />
      ))}
    </section>
  );
}
