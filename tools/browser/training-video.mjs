// training-video: a silent, captioned walkthrough of the product for a non-engineer audience,
// recorded from the real user interface of a running development instance (make dev or
// scripts/run.py dev --ephemeral) with synthetic fixture data. Part 1 sets up an organisation the
// way docs/current/DEPLOYMENT-GUIDE.md §4.1 describes it (three people: an operator, a second
// operator and the organisation's owner); part 2 runs the measurement cycle in the fixture
// workspace (entry, independent approval, calculation, period close, dashboard, report, PDF)
// with short looks at forms, imports, evidence and People & access.
//
// One browser context records one page into a WebM; the script converts it to MP4 with ffmpeg
// and writes chapters.json beside it. See docs/TRAINING-VIDEO.md for how to run it.
//
//   IMPACT_BASE_URL        the running instance (default http://127.0.0.1:8000)
//   IMPACT_TEST_LOCAL      its run directory with passwords.json, config.json and the signing
//                          keys (default .local/dev)
//   TRAINING_VIDEO_DIR     output directory (default .local/training-video)
//   TRAINING_VIDEO_PACE    1 = human pace (default); 0.2 for a quick selector check
//   TRAINING_VIDEO_SCENES  all (default) or a comma list of intro,part1,part2,outro
//   TRAINING_VIDEO_UNIQUE  1 adds a suffix to every name the film creates, for repeated runs
//                          against one instance (the final take runs on a fresh instance)
//   TRAINING_VIDEO_AUDIO_DIR  clips.json and WAV clips from `narrate.py synth`; with it the
//                          captions are held for their spoken length and timeline.json is written
//                          for `narrate.py mix` (without it the film is paced for reading only)
//   TRAINING_VIDEO_CRF     x264 quality (default 23; higher is smaller)
//   TRAINING_VIDEO_RESET_LOGIN_LIMIT  0 leaves the development sign-in counters alone (see
//                          resetSignInLimit below; the film signs people in about twenty times)
//   FFMPEG                 the ffmpeg binary (default: ffmpeg on PATH)
//
// Everything the film creates is synthetic: the two colleagues' addresses end in example.org,
// the organisation and programmes are invented, and the one-time passwords are shown on screen
// exactly as the product shows them to the operator who created them.
import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";

const root = process.cwd();
const base = (process.env.IMPACT_BASE_URL || "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);
const local = process.env.IMPACT_TEST_LOCAL || path.join(root, ".local/dev");
const outDir = path.resolve(
  process.env.TRAINING_VIDEO_DIR || path.join(root, ".local/training-video"),
);
const pace = Number(process.env.TRAINING_VIDEO_PACE || "1");
const suffix =
  process.env.TRAINING_VIDEO_UNIQUE === "1"
    ? " " + Date.now().toString().slice(-5)
    : "";
const tag = suffix.trim();
const scenes = new Set((process.env.TRAINING_VIDEO_SCENES || "all").split(","));
const want = (name) => scenes.has("all") || scenes.has(name);
const ffmpeg = process.env.FFMPEG || "ffmpeg";
// Voice-over (tools/browser/narrate.py): narration.json pairs every caption and card with its
// spoken text; TRAINING_VIDEO_AUDIO_DIR holds the synthesized clips and their durations
// (clips.json). With clips present a caption stays on screen until its clip would have been
// spoken (clip length + 0.8 s) before the next action, and every caption, card and chapter is
// logged with its time in timeline.json so that narrate.py mix can place the clips.
const narration = JSON.parse(
  await fs.readFile(path.join(root, "tools/browser/narration.json"), "utf8"),
);
const audioDir = process.env.TRAINING_VIDEO_AUDIO_DIR || "";
const clipSeconds = audioDir
  ? JSON.parse(await fs.readFile(path.join(audioDir, "clips.json"), "utf8"))
      .clips
  : {};
const narrated = new Map(
  narration.map((line) => [
    line.kind + ":" + line.screen,
    { id: line.id, seconds: clipSeconds[line.id]?.seconds || 0 },
  ]),
);
const timeline = [];
function narrate(kind, screen, at) {
  const line = narrated.get(kind + ":" + screen);
  timeline.push({ kind, id: line?.id || null, screen, t: at });
  if (!line && kind !== "chapter")
    console.warn("no narration line for " + kind + ": " + screen);
  return line?.seconds || 0;
}

const fixture = JSON.parse(
  await fs.readFile(
    path.join(root, "specification/fixtures/api-fixture.json"),
    "utf8",
  ),
);
const records = Object.fromEntries(
  JSON.parse(
    await fs.readFile(
      path.join(root, "specification/fixtures/records.json"),
      "utf8",
    ),
  ).map((r) => [r.key, r]),
);
const tenant = fixture.tenant_a;
const passwords = JSON.parse(
  await fs.readFile(path.join(local, "passwords.json"), "utf8"),
);
const config = JSON.parse(
  await fs.readFile(path.join(local, "config.json"), "utf8"),
);

// ---------------------------------------------------------------------------------------------
// The API as a fixture actor, for preparing part 2 (the film shows the user interface only).
// Development bearer tokens are minted like scripts/run.py mints them: RS256 with the run's
// private key and the kid of its public key (impact_api.keyring.rsa_key_id).
const privateKey = crypto.createPrivateKey(
  await fs.readFile(path.join(local, "private.pem")),
);
const kid =
  "rs-" +
  crypto
    .createHash("sha256")
    .update(
      crypto
        .createPublicKey(await fs.readFile(path.join(local, "public.pem")))
        .export({ type: "spki", format: "der" }),
    )
    .digest("hex")
    .slice(0, 16);
const b64url = (value) =>
  Buffer.from(JSON.stringify(value)).toString("base64url");
const tokens = new Map();
function token(actor) {
  const cached = tokens.get(actor);
  if (cached && cached.until > Date.now()) return cached.value;
  const now = Math.floor(Date.now() / 1000);
  const input =
    b64url({ alg: "RS256", typ: "JWT", kid }) +
    "." +
    b64url({
      iss: config.issuer,
      sub: fixture.actors[actor].identity_id,
      aud: config.audience,
      azp: config.client_id,
      iat: now,
      exp: now + 900,
      auth_time: now,
    });
  const value =
    input +
    "." +
    crypto
      .sign("RSA-SHA256", Buffer.from(input), privateKey)
      .toString("base64url");
  tokens.set(actor, { value, until: Date.now() + 120000 });
  return value;
}
async function api(actor, route, data, method = "POST", revision) {
  const url = route.startsWith("/")
    ? base + route
    : base + "/v1/tenants/" + tenant + "/" + route;
  const response = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + token(actor),
    },
    body:
      method === "GET"
        ? undefined
        : JSON.stringify({
            operation_id: crypto.randomUUID(),
            ...(revision ? { expected_revision: revision } : {}),
            data,
          }),
  });
  const text = await response.text();
  if (!response.ok)
    throw new Error(
      method + " " + route + " -> " + response.status + " " + text,
    );
  return text ? JSON.parse(text) : null;
}
const read = (route, actor = "author") => api(actor, route, null, "GET");
let template;
async function approveCandidate(candidateId, reason) {
  const workflow = (await read("workflows?limit=100", "reviewer")).items.find(
    (w) =>
      w.lifecycle_state === "InReview" && w.data.candidate_id === candidateId,
  );
  if (!workflow) throw new Error("no open review for " + candidateId);
  return api(
    "reviewer",
    "workflows/" + workflow.object_id + "/actions/approve",
    { candidate_revision: workflow.data.candidate_revision, reason },
    "POST",
    workflow.revision_id,
  );
}
async function submitAndApprove(route, id, reason) {
  const row = await read(route + "/" + id);
  await api(
    "author",
    route + "/" + id + "/actions/submit",
    { workflow_version: template.revision_id },
    "POST",
    row.revision_id,
  );
  await approveCandidate(id, reason);
  return read(route + "/" + id);
}
async function act(route, id, verb, data = {}, actor = "author") {
  const row = await read(route + "/" + id, actor);
  return api(
    actor,
    route + "/" + id + "/actions/" + verb,
    data,
    "POST",
    row.revision_id,
  );
}

// ---------------------------------------------------------------------------------------------
// Names the film uses. Every address ends in example.org; every name is invented.
const orgName = "Clean Water Trust" + suffix;
const emailOf = (name) => name + (tag ? "+" + tag : "") + "@example.org";
// Repeated runs against one instance (TRAINING_VIDEO_UNIQUE=1) keep the people distinguishable.
const second = {
  email: emailOf("second.operator"),
  first: "Second",
  last: "Operator" + suffix,
};
const ownerPerson = {
  email: emailOf("org.owner"),
  first: "Organisation",
  last: "Owner" + suffix,
};
const waterProgramme = "Clean Water Access 2026" + suffix;
const fieldProgramme = "Field Collection 2026" + suffix;
const siteKey = (n) => "CWA" + (tag ? "-" + tag : "") + "-SITE-0" + n;
const reportHeading = "Clean water - third quarter 2026" + suffix;

// What preparing part 2 through the API leaves behind for the browser scenes.
const prepared = {};
async function prepare() {
  template = (await read("workflow-templates")).items[0];
  const calendar = (await read("reporting-calendars")).items[0];
  const geography = (await read("geographies")).items[0];
  const period = await read("periods/" + records.period.object_id);
  prepared.period = period;
  prepared.reportTemplate = (await read("report-templates")).items.find((r) =>
    ["Approved", "Active"].includes(r.lifecycle_state),
  );
  // Programme 1: a pooled-ratio indicator, three planned sites, two of them already approved.
  const programme = await api("author", "programmes", {
    code: "CWA",
    title: waterProgramme,
    programme_type: "Health",
    starts_at: "2026-01-01T00:00:00Z",
    ends_at: "2027-01-01T00:00:00Z",
    reporting_calendar_id: calendar.object_id,
    geography_id: geography.object_id,
  });
  let definition = await api("author", "indicator-definitions", {
    code: "SWH" + (tag ? "-" + tag : ""),
    name: "Households with safe drinking water" + suffix,
    measurement_type: "PERCENTAGE",
    unit: "percent",
    population: "Households visited by the field team during the quarter",
    inclusion: "Households visited at least once in the quarter",
    exclusion: "Repeat visits to the same household",
    method: "Share of visited households whose main water source is safe",
    source_mode: "MANUAL",
    time_semantic: "FLOW",
    combination_rule: "POOLED_RATIO",
    numerator_meaning: "Households with safe drinking water",
    denominator_meaning: "Households visited",
    display_decimals: 2,
  });
  definition = await submitAndApprove(
    "indicator-definitions",
    definition.object_id,
    "Definition reviewed for the training walkthrough",
  );
  prepared.definitionName = definition.data.name;
  let indicator = await api("author", "indicator-instances", {
    programme_id: programme.object_id,
    definition_version: definition.revision_id,
    local_applicability: "Pilot districts" + suffix,
    collector_id: fixture.actors.author.principal_id,
    reviewer_id: fixture.actors.reviewer.principal_id,
  });
  prepared.indicator = indicator.object_id;
  prepared.indicatorLabel = "Pilot districts" + suffix;
  const plan = await api("author", "collection-plans", {
    title: "Quarterly site returns" + suffix,
    indicator_id: indicator.object_id,
    period_id: period.object_id,
    obligations: [1, 2, 3].map((n) => ({
      label: "Site " + n,
      source_namespace: "MANUAL",
      source_key: siteKey(n),
      due_at: "2026-10-01T00:00:00Z",
    })),
  });
  await submitAndApprove(
    "collection-plans",
    plan.object_id,
    "Plan reviewed for the training walkthrough",
  );
  await act("indicator-instances", indicator.object_id, "activate");
  for (const verb of ["ready", "activate"])
    await act("programmes", programme.object_id, verb);
  prepared.programme = programme.object_id;
  for (const [n, numerator, denominator, value] of [
    [1, "50", "100", "50"],
    [2, "1", "10", "10"],
  ]) {
    const row = await api("author", "observations", {
      source_namespace: "MANUAL",
      source_key: siteKey(n),
      indicator_id: indicator.object_id,
      event_at: "2026-08-20T09:00:00Z",
      captured_at: "2026-08-20T10:00:00Z",
      capture_zone: "UTC",
      value_state: "PRESENT",
      value,
      numerator,
      denominator,
      source_version: "1",
      dimension_values: {},
    });
    await submitAndApprove(
      "observations",
      row.object_id,
      "Checked against the site return",
    );
  }
  // An approved results framework and a quarterly target, so the planning tab has content.
  const owner = fixture.actors.author.principal_id;
  const ids = [0, 1, 2, 3].map(() => crypto.randomUUID());
  const levels = ["IMPACT", "OUTCOME", "OUTPUT", "ACTIVITY"];
  const titles = [
    "Healthier households in the pilot districts",
    "Households use safe drinking water",
    "Water points repaired and tested",
    "Quarterly site visits and water tests",
  ];
  const nodes = levels.map((level, i) => ({
    node_id: ids[i],
    node_type: level,
    title: titles[i],
    definition: "The intended " + level.toLowerCase() + " of the programme.",
    parent_node_id: i ? ids[i - 1] : null,
    owner_id: owner,
    indicator_ids: level === "OUTPUT" ? [indicator.object_id] : [],
  }));
  const framework = await api("author", "frameworks", {
    programme_id: programme.object_id,
    version_label: "Baseline 2026",
    nodes,
    relationships: [],
    effective_from: "2026-01-01T00:00:00Z",
    exceptions: nodes
      .filter((n) => ["IMPACT", "OUTCOME"].includes(n.node_type))
      .map((n) => ({
        object_id: n.node_id,
        rule: "UNMEASURED_RESULT",
        reason:
          "Measured by the end-line evaluation, outside routine monitoring.",
        review_date: "2026-12-31",
      })),
  });
  await submitAndApprove(
    "frameworks",
    framework.object_id,
    "Framework reviewed for the training walkthrough",
  );
  const target = await api("author", "targets", {
    indicator_id: indicator.object_id,
    period_id: period.object_id,
    target_kind: "VALUE",
    value_state: "PRESENT",
    value: "55",
    direction: "HIGHER",
    target_basis: "ORIGINAL",
  });
  await submitAndApprove(
    "targets",
    target.object_id,
    "Target reviewed for the training walkthrough",
  );
  // Programme 2: a household count collected through a published web form and spreadsheets.
  const field = await api("author", "programmes", {
    code: "FLD",
    title: fieldProgramme,
    programme_type: "Health",
    starts_at: "2026-01-01T00:00:00Z",
    ends_at: "2027-01-01T00:00:00Z",
    reporting_calendar_id: calendar.object_id,
    geography_id: geography.object_id,
  });
  let count = await api("author", "indicator-definitions", {
    code: "HHV" + (tag ? "-" + tag : ""),
    name: "Households visited" + suffix,
    measurement_type: "COUNT",
    unit: "households",
    population: "Households in the programme villages",
    inclusion: "Households visited by a field officer",
    exclusion: "Duplicate visits",
    method: "Count of visit records",
    source_mode: "MANUAL",
    time_semantic: "FLOW",
    combination_rule: "SUM",
    display_decimals: 0,
  });
  count = await submitAndApprove(
    "indicator-definitions",
    count.object_id,
    "Definition reviewed for the training walkthrough",
  );
  const visits = await api("author", "indicator-instances", {
    programme_id: field.object_id,
    definition_version: count.revision_id,
    local_applicability: "Village visits" + suffix,
    collector_id: fixture.actors.author.principal_id,
    reviewer_id: fixture.actors.reviewer.principal_id,
  });
  prepared.visitsLabel = "Village visits" + suffix;
  const unit = "VILLAGE-07";
  const fieldPlan = await api("author", "collection-plans", {
    title: "Village visit returns" + suffix,
    indicator_id: visits.object_id,
    period_id: period.object_id,
    obligations: [
      {
        label: unit,
        source_namespace: "FORM",
        source_key: unit + "/" + visits.object_id,
        due_at: "2026-10-01T00:00:00Z",
      },
    ],
  });
  await submitAndApprove(
    "collection-plans",
    fieldPlan.object_id,
    "Plan reviewed for the training walkthrough",
  );
  await act("indicator-instances", visits.object_id, "activate");
  for (const verb of ["ready", "activate"])
    await act("programmes", field.object_id, verb);
  const form = await api("author", "forms", {
    code: "HV" + (tag ? "-" + tag : ""),
    title: "Household visit" + suffix,
    programme_id: field.object_id,
    fields: [
      {
        field_id: crypto.randomUUID(),
        stable_code: "consent",
        position: 0,
        field_type: "BOOLEAN",
        label: "Consent given",
        required: true,
      },
      {
        field_id: crypto.randomUUID(),
        stable_code: "households",
        position: 1,
        field_type: "INTEGER",
        label: "Households reached",
        required: false,
        minimum: "0",
        maximum: "1000",
        indicator_id: visits.object_id,
        value_role: "VALUE",
        relevant_when: { field_code: "consent", equals: "true" },
      },
    ],
    logic: [],
    translation_versions: [],
    compatibility_policy: "LOCK_PUBLISHED",
  });
  const approvedForm = await submitAndApprove(
    "forms",
    form.object_id,
    "Form reviewed for the training walkthrough",
  );
  await api(
    "reviewer",
    "forms/" + form.object_id + "/actions/publish",
    { approved_candidate_revision: approvedForm.revision_id },
    "POST",
    approvedForm.revision_id,
  );
  prepared.formTitle = "Household visit" + suffix;
  prepared.formUnit = unit;
  // One batch already committed (so a repeated village is a duplicate), one batch previewed
  // with an accepted, a quarantined and a duplicate row for the film to open.
  const mapping = {
    unit_column: "village",
    columns: [
      {
        column: "households",
        indicator_id: visits.object_id,
        value_role: "VALUE",
        unit: "households",
      },
    ],
  };
  const prefix = "D" + (tag ? tag : "");
  const earlier = await api("author", "imports", {
    format: "CSV",
    file_name: "village-returns-august.csv",
    content: `village,households\n${prefix}-01,14\n${prefix}-02,9\n`,
    programme_id: field.object_id,
    period_id: period.object_id,
    mode: "APPEND",
    atomic: true,
    mapping,
  });
  await act("imports", earlier.object_id, "preview");
  const staged = await read("imports/" + earlier.object_id);
  await api(
    "author",
    "imports/" + earlier.object_id + "/actions/commit",
    {
      preview_hash: staged.data.preview.preview_hash,
      workflow_version: template.revision_id,
    },
    "POST",
    staged.revision_id,
  );
  const batch = await api("author", "imports", {
    format: "CSV",
    file_name: "village-returns-september.csv",
    content:
      `village,households,remarks\n` +
      `${prefix}-01,15,already reported in August\n` +
      `${prefix}-05,abc,not a number\n` +
      `${prefix}-06,9,ordinary\n` +
      `${prefix}-07,11,ordinary\n`,
    programme_id: field.object_id,
    period_id: period.object_id,
    mode: "APPEND",
    atomic: false,
    mapping,
  });
  await act("imports", batch.object_id, "preview");
  prepared.batchFile = "village-returns-september.csv";
  prepared.fieldProgramme = field.object_id;
}

// ---------------------------------------------------------------------------------------------
// Browser, recording and the visual helpers (caption bar, cursor, outlines, cards).
await fs.mkdir(outDir, { recursive: true });
const rawDir = path.join(outDir, "raw");
await fs.rm(rawDir, { recursive: true, force: true });
await fs.mkdir(rawDir, { recursive: true });
const browserDir = path.join(root, ".local/browser");
const browser = await chromium.launch({
  executablePath: path.join(browserDir, "chromium"),
  headless: true,
  args: [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--no-zygote",
  ],
  env: {
    ...process.env,
    LD_LIBRARY_PATH: browserDir + ":" + path.join(browserDir, "lib"),
    FONTCONFIG_PATH: browserDir,
  },
});
const context = await browser.newContext({
  viewport: { width: 1280, height: 720 },
  recordVideo: { dir: rawDir, size: { width: 1280, height: 720 } },
  acceptDownloads: true,
  locale: "en-GB",
  timezoneId: "Asia/Kolkata",
});
// The overlay lives in every document: a caption bar at the bottom, a visible cursor that
// follows the real mouse events, and a ripple on each click. Styles go through the CSSOM
// (style.setProperty), which the application's content-security policy allows; inline style
// attributes would be refused.
await context.addInitScript(() => {
  const set = (el, props) => {
    for (const [k, v] of Object.entries(props))
      el.style.setProperty(k, v, "important");
  };
  // The application's dialogs are native <dialog> elements shown with showModal(), which puts
  // them in the browser's top layer above any z-index. The caption bar and the cursor are
  // manual popovers, which also live in the top layer, re-raised whenever a dialog opens so
  // that they stay above it (the last element to enter the top layer is drawn on top).
  function raise() {
    for (const id of ["tv-caption", "tv-cursor"]) {
      const el = document.getElementById(id);
      if (!el || !el.isConnected) continue;
      try {
        if (el.matches(":popover-open")) el.hidePopover();
        el.showPopover();
      } catch {
        /* popovers unavailable: the elements stay ordinary fixed layers */
      }
    }
  }
  function ensure() {
    if (!document.body || location.protocol === "about:") return;
    let created = false;
    if (!document.getElementById("tv-caption")) {
      const bar = document.createElement("div");
      bar.id = "tv-caption";
      bar.setAttribute("popover", "manual");
      set(bar, {
        position: "fixed",
        inset: "auto 0 0 0",
        margin: "0",
        border: "0",
        width: "auto",
        height: "auto",
        "max-width": "none",
        "max-height": "none",
        overflow: "visible",
        "z-index": "2147483646",
        background: "rgba(17, 29, 25, 0.9)",
        color: "#ffffff",
        font: "500 23px/1.35 'Open Sans', system-ui, sans-serif",
        padding: "14px 36px 16px",
        "min-height": "70px",
        "box-sizing": "border-box",
        "pointer-events": "none",
        visibility: "hidden",
        "text-shadow": "0 1px 1px rgba(0,0,0,0.5)",
      });
      document.body.appendChild(bar);
      created = true;
    }
    if (!document.getElementById("tv-cursor")) {
      const cursor = document.createElement("div");
      cursor.id = "tv-cursor";
      cursor.setAttribute("popover", "manual");
      set(cursor, {
        position: "fixed",
        inset: "0 auto auto 0",
        margin: "0",
        padding: "0",
        width: "22px",
        height: "22px",
        "max-width": "none",
        "max-height": "none",
        overflow: "visible",
        "border-radius": "50%",
        background: "rgba(232, 160, 48, 0.55)",
        border: "2px solid #1d2b26",
        "box-shadow": "0 0 0 2px rgba(255,255,255,0.85)",
        "z-index": "2147483647",
        "pointer-events": "none",
        visibility: "hidden",
        transform: "translate(-100px, -100px)",
        "box-sizing": "border-box",
      });
      document.body.appendChild(cursor);
      created = true;
    }
    if (created) {
      raise();
      new MutationObserver((records) => {
        for (const r of records) {
          const target = r.target;
          if (
            (r.type === "attributes" &&
              target.tagName === "DIALOG" &&
              target.open) ||
            (r.type === "childList" &&
              [...r.addedNodes].some(
                (n) =>
                  n.nodeType === 1 &&
                  (n.tagName === "DIALOG" || n.querySelector?.("dialog")),
              ))
          )
            return raise();
        }
      }).observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["open"],
        subtree: true,
        childList: true,
      });
    }
  }
  window.__caption = (text) => {
    ensure();
    const bar = document.getElementById("tv-caption");
    if (!bar) return;
    bar.textContent = text;
    set(bar, { visibility: text ? "visible" : "hidden" });
    raise();
  };
  window.addEventListener(
    "mousemove",
    (e) => {
      ensure();
      const cursor = document.getElementById("tv-cursor");
      if (!cursor) return;
      set(cursor, {
        transform: `translate(${e.clientX - 11}px, ${e.clientY - 11}px)`,
        visibility: "visible",
      });
    },
    true,
  );
  window.addEventListener(
    "mousedown",
    (e) => {
      ensure();
      if (!document.body || location.protocol === "about:") return;
      const ripple = document.createElement("div");
      ripple.setAttribute("popover", "manual");
      set(ripple, {
        position: "fixed",
        inset: e.clientY - 4 + "px auto auto " + (e.clientX - 4) + "px",
        margin: "0",
        padding: "0",
        width: "8px",
        height: "8px",
        "border-radius": "50%",
        border: "3px solid rgba(232, 160, 48, 0.95)",
        background: "transparent",
        "z-index": "2147483647",
        "pointer-events": "none",
        opacity: "0.9",
        transform: "scale(1)",
        transition: "transform 420ms ease-out, opacity 420ms ease-out",
      });
      document.body.appendChild(ripple);
      try {
        ripple.showPopover();
      } catch {
        /* drawn as an ordinary fixed layer */
      }
      requestAnimationFrame(() =>
        requestAnimationFrame(() =>
          set(ripple, { transform: "scale(7)", opacity: "0" }),
        ),
      );
      setTimeout(() => ripple.remove(), 500);
    },
    true,
  );
  if (document.readyState !== "loading") ensure();
  else document.addEventListener("DOMContentLoaded", ensure);
});
// Part 2's configuration is created before the recording starts, so the film has no dead time.
if (want("part2")) {
  console.log("preparing part 2 through the API");
  await prepare();
}
const page = await context.newPage();
page.setDefaultTimeout(30000);
const started = Date.now();
const chapters = [];
const pageErrors = [];
page.on("pageerror", (e) => pageErrors.push(e.message));

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const hold = (ms) => sleep(Math.max(0, ms * pace));
const CAPTION_MIN = 4000;
let captionAt = 0;
let captionText = "";
// A caption stays at least CAPTION_MIN before the next replaces it, and the viewer gets a moment
// to start reading before the next action.
async function caption(text, settle = 1100) {
  const remaining = captionAt + CAPTION_MIN * pace - Date.now();
  if (remaining > 0) await sleep(remaining);
  captionText = text;
  await page.evaluate((t) => window.__caption && window.__caption(t), text);
  captionAt = Date.now();
  const spoken = narrate("caption", text, captionAt - started);
  await hold(Math.max(settle, spoken ? spoken * 1000 + 800 : 0));
}
// Re-apply the current caption after a navigation replaced the document.
async function restoreCaption() {
  await page.evaluate(
    (t) => window.__caption && window.__caption(t),
    captionText,
  );
}
function chapter(title) {
  const at = Date.now() - started;
  chapters.push({ title, at });
  timeline.push({ kind: "chapter", id: null, screen: title, t: at });
  console.log("chapter " + format(at) + " " + title);
}
function format(ms) {
  const s = Math.round(ms / 1000);
  return (
    String(Math.floor(s / 60)).padStart(2, "0") +
    ":" +
    String(s % 60).padStart(2, "0")
  );
}
let mouse = { x: 640, y: 400 };
async function moveTo(x, y, steps = 18) {
  const from = { ...mouse };
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    const eased = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    await page.mouse.move(
      from.x + (x - from.x) * eased,
      from.y + (y - from.y) * eased,
    );
    await sleep(Math.max(3, 11 * pace));
  }
  mouse = { x, y };
}
async function nudge() {
  await page.mouse.move(mouse.x + 1, mouse.y + 1);
  await page.mouse.move(mouse.x, mouse.y);
}
const outlineOn = (el) => {
  el.style.setProperty("outline", "3px solid #e8a030", "important");
  el.style.setProperty("outline-offset", "2px", "important");
};
const outlineOff = (el) => {
  el.style.removeProperty("outline");
  el.style.removeProperty("outline-offset");
};
async function wheel(dy) {
  const steps = Math.max(1, Math.round(Math.abs(dy) / 90));
  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, dy / steps);
    await sleep(Math.max(8, 45 * pace));
  }
  await hold(250);
}
// Bring the element into the part of the viewport above the caption bar, scrolling the
// container under the pointer (so a dialog scrolls when the target is inside one).
async function bringIntoView(locator) {
  const target = locator.first();
  await target.waitFor({ state: "visible" });
  await target.scrollIntoViewIfNeeded();
  let box = await target.boundingBox();
  if (!box) return box;
  const bottomLimit = 720 - 92;
  if (box.y + box.height > bottomLimit || box.y < 70) {
    await moveTo(
      box.x + Math.min(box.width / 2, 200),
      Math.min(Math.max(box.y + box.height / 2, 80), 640),
      10,
    );
    const dy =
      box.y + box.height > bottomLimit
        ? box.y + box.height - bottomLimit + 60
        : box.y - 150;
    await wheel(dy);
    box = await target.boundingBox();
  }
  return box;
}
async function focusOn(locator, dwell = 350) {
  const box = await bringIntoView(locator);
  const dx = Math.min(box.width / 2, 200);
  await moveTo(box.x + dx, box.y + box.height / 2);
  await locator.first().evaluate(outlineOn);
  await hold(dwell);
  return { dx, dy: box.height / 2 };
}
async function clearOutline(locator) {
  await locator
    .first()
    .evaluate(outlineOff)
    .catch(() => {});
}
async function humanClick(locator, settle = 400) {
  const position = await focusOn(locator);
  const el = locator.first();
  await el.click({ position: { x: position.dx, y: position.dy } });
  setTimeout(() => clearOutline(locator), 500 * pace);
  await hold(settle);
}
async function humanType(locator, text) {
  await humanClick(locator, 120);
  await locator
    .first()
    .pressSequentially(text, { delay: Math.max(2, 32 * pace) });
  await hold(300);
}
// Values a person would paste or pick (dates, identifiers, passwords): filled in one go.
async function humanFill(locator, text) {
  await humanClick(locator, 120);
  await locator.first().fill(text);
  await hold(400);
}
async function humanSelect(locator, option) {
  await focusOn(locator);
  await locator.first().selectOption(option);
  setTimeout(() => clearOutline(locator), 500 * pace);
  await hold(600);
}
// Choose the option whose text matches `pattern` (selectOption itself takes exact labels only).
async function selectByText(locator, pattern) {
  const value = await locator
    .first()
    .evaluate(
      (select, source) =>
        [...select.options].find((o) => new RegExp(source).test(o.textContent))
          ?.value,
      pattern.source,
    );
  if (!value) throw new Error("no option matches " + pattern);
  await humanSelect(locator, value);
}
async function look(locator, dwell = 1800) {
  await bringIntoView(locator);
  await locator.first().evaluate(outlineOn);
  await hold(dwell);
  await clearOutline(locator);
}
async function scrollMain(dy) {
  await moveTo(760, 420, 10);
  await wheel(dy);
}
async function card(
  title,
  lines,
  { kicker = "", dwell = 5500, size = 54 } = {},
) {
  await page.goto("about:blank");
  await page.evaluate(
    ({ title, lines, kicker, size }) => {
      const set = (el, props) => {
        for (const [k, v] of Object.entries(props)) el.style.setProperty(k, v);
      };
      document.title = title;
      document.body.textContent = "";
      set(document.documentElement, { background: "#f4f0e6", height: "100%" });
      set(document.body, {
        margin: "0",
        height: "100vh",
        display: "flex",
        "align-items": "center",
        "justify-content": "center",
        background: "#f4f0e6",
        color: "#1d3a30",
        "font-family": "'Open Sans', system-ui, sans-serif",
      });
      const box = document.createElement("div");
      set(box, {
        "max-width": "980px",
        padding: "0 56px",
        "box-sizing": "border-box",
      });
      if (kicker) {
        const k = document.createElement("div");
        k.textContent = kicker;
        set(k, {
          "font-size": "19px",
          "letter-spacing": "0.18em",
          "text-transform": "uppercase",
          color: "#b5731f",
          "margin-bottom": "18px",
          "font-weight": "600",
        });
        box.appendChild(k);
      }
      const h = document.createElement("h1");
      h.textContent = title;
      set(h, {
        font: `600 ${size}px/1.15 Caladea, Georgia, 'DejaVu Serif', serif`,
        margin: "0 0 26px",
        color: "#1d3a30",
      });
      box.appendChild(h);
      for (const line of lines) {
        const p = document.createElement("p");
        p.textContent = line;
        set(p, {
          font: "400 27px/1.45 'Open Sans', system-ui, sans-serif",
          margin: "0 0 16px",
        });
        box.appendChild(p);
      }
      const rule = document.createElement("div");
      set(rule, {
        width: "72px",
        height: "4px",
        background: "#b5731f",
        "margin-top": "30px",
        "border-radius": "2px",
      });
      box.appendChild(rule);
      document.body.appendChild(box);
    },
    { title, lines, kicker, size },
  );
  captionText = "";
  captionAt = 0;
  const spoken = narrate("card", title, Date.now() - started);
  await hold(Math.max(dwell, spoken ? spoken * 1000 + 1000 : 0));
}
async function openApp() {
  await page.goto(base);
  await page.getByRole("heading", { name: "Welcome back" }).waitFor();
  await nudge();
}
const landing = () =>
  page
    .getByRole("heading", {
      // Since build 0.27.0 a member without any capability (the owner before initial access is
      // applied) lands on the access gate's waiting page instead of a refused portfolio.
      name: /^(Programme portfolio|People & access|No active workspace|Join the workspace|Tenant lifecycle|Your administrator access is being set up|Your access is being set up)$/,
    })
    .and(page.locator("h1"));
// The development sign-in counts every attempt, successful or not, against the account and the
// network (ten per five minutes); the film signs people in about twenty times from one browser,
// so the counters of the local instance are cleared before each sign-in (a test-instance
// affordance only: the staging sign-in is Keycloak's, which locks only after wrong passwords).
const identityDsn = config.identity_dsn;
function resetSignInLimit() {
  if (process.env.TRAINING_VIDEO_RESET_LOGIN_LIMIT === "0" || !identityDsn)
    return;
  const result = spawnSync(
    path.join(root, ".venv/bin/python"),
    [
      "-c",
      "import psycopg,sys\n" +
        "with psycopg.connect(sys.argv[1], prepare_threshold=None) as c:\n" +
        "    c.execute('DELETE FROM impact.login_attempt')\n",
      identityDsn,
    ],
    { stdio: ["ignore", "ignore", "pipe"], encoding: "utf8" },
  );
  if (result.status !== 0)
    console.error(
      "sign-in limit not reset: " + (result.stderr || "").slice(-400),
    );
}
async function signIn(username, password, who) {
  await page.getByRole("heading", { name: "Welcome back" }).waitFor();
  resetSignInLimit();
  if (who) await caption(who, 1200);
  await humanType(page.getByLabel("Username", { exact: true }), username);
  await humanFill(page.getByLabel("Password", { exact: true }), password);
  await humanClick(
    page.getByRole("button", { name: "Sign in →", exact: true }),
    200,
  );
  await landing().waitFor();
  await hold(500);
}
async function signOut() {
  // The console's sub-pages (recovery contacts, initial access) have no sign-out of their own.
  const back = button("Back to tenant lifecycle");
  if (await back.count()) await humanClick(back, 300);
  await humanClick(
    page.getByRole("button", { name: "Sign out", exact: true }).first(),
    200,
  );
  await page.getByRole("heading", { name: "Welcome back" }).waitFor();
  // The single-page application keeps the "console open" flag across a sign-out in the same
  // tab (the next person would land in the Tenant lifecycle console); a fresh load gives each
  // person the start page the click-path describes.
  await page.reload();
  await page.getByRole("heading", { name: "Welcome back" }).waitFor();
  await restoreCaption();
  await nudge();
  await hold(400);
}
const button = (name) => page.getByRole("button", { name, exact: true });
const label = (name) => page.getByLabel(name, { exact: true });
const dialog = () => page.getByRole("dialog");
async function navTo(name) {
  await humanClick(
    page
      .getByRole("navigation", { name: "Main navigation" })
      .getByRole("button", { name, exact: true }),
    700,
  );
}
async function closeDialog() {
  await humanClick(button("Close dialog"), 400);
  await dialog().waitFor({ state: "hidden" });
}
async function console_(section) {
  await humanClick(button("Tenant lifecycle"), 600);
  await page
    .getByRole("heading", { name: "Tenant lifecycle", exact: true })
    .waitFor();
  if (section) {
    await humanClick(button(section), 600);
    await page.getByRole("heading", { name: section, exact: true }).waitFor();
  }
}
// The POST whose path ends with `suffix`, caused by `click`; its receipt names the workflow.
async function receipt(click, suffix) {
  const pending = page.waitForResponse(
    (r) =>
      r.request().method() === "POST" &&
      new URL(r.url()).pathname.endsWith(suffix),
  );
  await click();
  const response = await pending;
  if (!response.ok()) throw new Error(suffix + " " + (await response.text()));
  return response.json();
}
// Workspace members with several workspaces (the administrator after part 1) land in the first
// one; the measurement scenes play in the fixture workspace.
async function ensureWorkspace(tenantId) {
  const select = page.getByLabel("Workspace", { exact: true });
  if (!(await select.count())) return;
  if ((await select.inputValue()) === tenantId) return;
  await humanSelect(select, tenantId);
  await landing().waitFor();
  await hold(600);
}
// Lists load 50 records at a time, oldest first: page on until `entry` is present.
async function loadUntil(entry) {
  const more = button("Load more");
  await entry.first().or(more).first().waitFor();
  for (let i = 0; i < 40 && !(await entry.count()); i++) {
    if (!(await more.count())) break;
    const loaded = page.waitForResponse(
      (r) => r.request().method() === "GET" && r.url().includes("cursor="),
    );
    await more.click();
    await (await loaded).finished();
  }
  await entry.first().waitFor();
  return entry.first();
}
async function reviewAndApprove(workflowId, text) {
  await navTo("Review queue");
  await caption(
    text || "The review queue lists what is waiting for a decision.",
    1200,
  );
  await humanClick(
    await loadUntil(
      page
        .locator("tr")
        .filter({ hasText: workflowId.slice(0, 8) })
        .getByRole("button")
        .first(),
    ),
  );
  await humanClick(button("Review submission"));
  await dialog().getByLabel("Decision reason", { exact: true }).waitFor();
}
async function decide(reason) {
  await humanType(label("Decision reason"), reason);
  await humanClick(button("Approve"));
  await dialog().waitFor({ state: "hidden" });
}
// The console's change forms: a reason, then the confirm button; "Change saved." follows.
// Since build 0.27.0 the tenant change form is a dialog beside its card; the recovery-contact
// and initial-access forms are still regions at the foot of their pages.
const changeRegion = (name) => page.getByRole("region", { name, exact: true });
async function confirmIn(form, buttonName, reason) {
  await humanType(form.getByLabel("Reason", { exact: true }), reason);
  await humanClick(form.getByRole("button", { name: buttonName, exact: true }));
  await page.getByRole("status").filter({ hasText: "Change saved." }).waitFor();
}
const confirmTenant = (reason) =>
  confirmIn(dialog(), "Confirm tenant change", reason);
const confirmContact = (reason) =>
  confirmIn(
    changeRegion("Recovery contact change"),
    "Confirm recovery contact change",
    reason,
  );
const confirmAccess = (reason) =>
  confirmIn(
    changeRegion("Initial access change"),
    "Confirm initial access change",
    reason,
  );
const inDays = (days) =>
  new Date(Date.now() + days * 86400000).toISOString().slice(0, 16);
const orgCard = () => page.getByRole("article", { name: orgName, exact: true });
const contactCard = () =>
  page.getByRole("article", {
    name: new RegExp(
      "^" +
        orgName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") +
        " recovery contact ",
    ),
  });
const accessCard = () =>
  page.getByRole("article", { name: orgName + " initial access", exact: true });

// ---------------------------------------------------------------------------------------------
async function intro() {
  chapter("Impact Platform — how it works");
  await card(
    "Impact Platform — how it works",
    [
      "A walkthrough in two parts: 1. Setting up an organisation. 2. The measurement cycle.",
      "All data shown is synthetic test data on a local test instance.",
    ],
    { kicker: "Training walkthrough", dwell: 6500 },
  );
  await card(
    "One rule explains most of the steps",
    [
      "Nobody can approve their own work.",
      "Every approval — of an organisation, a data entry, a report — is made by a different person. That is what makes the numbers trustworthy.",
    ],
    { kicker: "Before we start", dwell: 7500, size: 50 },
  );
}

async function part1() {
  chapter("Part 1 — Setting up an organisation");
  await card(
    "Part 1 — Setting up an organisation",
    [
      "Three people take part: Nakul, who runs the platform; a colleague who becomes the second operator; and the colleague who will own the organisation.",
      "Each step is done by the person it belongs to.",
    ],
    { kicker: "Part 1", dwell: 6500, size: 48 },
  );
  await openApp();
  await signIn(
    "admin",
    passwords.admin,
    "Nakul signs in as a platform operator (test account 'admin').",
  );
  await caption(
    "Organisations are set up in the Tenant lifecycle console, linked at the bottom of the left-hand menu.",
    900,
  );
  await console_();
  const operators = page.getByRole("region", { name: "Operators" });
  await caption(
    "Step 1 — add a second operator. Nakul nominates a colleague by e-mail address.",
    600,
  );
  await humanClick(
    operators.getByRole("button", {
      name: "Nominate an operator",
      exact: true,
    }),
  );
  const nominate = page.getByRole("form", { name: "Nominate an operator" });
  await humanType(
    nominate.getByLabel("Their e-mail address", { exact: true }),
    second.email,
  );
  await humanClick(
    nominate.getByRole("button", { name: "Nominate", exact: true }),
  );
  await operators
    .getByRole("status")
    .filter({ hasText: "Nomination recorded" })
    .waitFor();
  await caption(
    "A sign-in form opens straight away. Nakul creates the colleague's sign-in: name and a reason.",
    700,
  );
  let form = page.getByRole("form", { name: "Create a sign-in" });
  await humanType(form.getByLabel("First name", { exact: true }), second.first);
  await humanType(form.getByLabel("Last name", { exact: true }), second.last);
  await humanType(
    form.getByLabel("Reason", { exact: true }),
    "Second operator for independent activation",
  );
  await humanClick(
    form.getByRole("button", { name: "Create sign-in", exact: true }),
  );
  let credential = page.getByRole("region", { name: "One-time password" });
  await credential.waitFor();
  second.password = await credential
    .getByLabel("One-time password", { exact: true })
    .inputValue();
  await caption(
    "The one-time password is shown once and never stored. Nakul passes it on in person or by phone.",
    2500,
  );
  await look(credential.getByLabel("One-time password", { exact: true }), 1200);
  await humanClick(
    credential.getByRole("button", {
      name: "I have noted it — hide the password",
    }),
  );
  await operators.waitFor();
  await caption(
    "Step 2 — a sign-in for the person who will own the organisation. Same form, same one-time password.",
    700,
  );
  await humanClick(
    operators.getByRole("button", {
      name: "Create a sign-in for someone",
      exact: true,
    }),
  );
  form = page.getByRole("form", { name: "Create a sign-in" });
  await humanType(
    form.getByLabel("E-mail address", { exact: true }),
    ownerPerson.email,
  );
  await humanType(
    form.getByLabel("First name", { exact: true }),
    ownerPerson.first,
  );
  await humanType(
    form.getByLabel("Last name", { exact: true }),
    ownerPerson.last,
  );
  await humanType(
    form.getByLabel("Reason", { exact: true }),
    "Will own the new organisation",
  );
  await humanClick(
    form.getByRole("button", { name: "Create sign-in", exact: true }),
  );
  credential = page.getByRole("region", { name: "One-time password" });
  await credential.waitFor();
  ownerPerson.password = await credential
    .getByLabel("One-time password", { exact: true })
    .inputValue();
  await hold(1200);
  await humanClick(
    credential.getByRole("button", {
      name: "I have noted it — hide the password",
    }),
  );
  await operators.waitFor();
  await caption(
    "Both colleagues have a sign-in now. Nakul signs out so that they can take their turns.",
    600,
  );
  await signOut();

  await signIn(
    second.email,
    second.password,
    "The second operator signs in with the one-time password. On the live server they also choose their own password and set up an authenticator app.",
  );
  await caption(
    "The start page says what happens next: they have been nominated as an operator. Only they can accept it.",
    2200,
  );
  await console_();
  const panel = page.getByRole("region", { name: "Operators" });
  await look(
    panel.getByRole("heading", {
      name: "You are nominated as a platform operator",
    }),
    900,
  );
  await humanClick(
    panel.getByRole("button", { name: "Accept operator role", exact: true }),
  );
  await panel
    .getByRole("status")
    .filter({ hasText: "You are now a platform operator." })
    .waitFor();
  await caption(
    "There are now two active operators — two different people.",
    2200,
  );
  await signOut();

  await signIn(
    ownerPerson.email,
    ownerPerson.password,
    "The future owner signs in once, so that the platform knows them. Their start page shows an identity reference.",
  );
  await look(page.getByText("Your identity reference", { exact: false }), 1800);
  await signOut();

  await signIn(
    "admin",
    passwords.admin,
    "Step 3 — Nakul requests the organisation.",
  );
  await console_();
  await humanClick(button("Request tenant"));
  const request = dialog();
  await humanType(
    request.getByLabel("Operating name", { exact: true }),
    orgName,
  );
  await caption(
    "The owner is chosen by name from the people who have signed in — a different person from Nakul.",
    600,
  );
  await selectByText(
    request.getByLabel("Organisation owner", { exact: true }),
    new RegExp("^\\s*" + ownerPerson.first + " " + ownerPerson.last),
  );
  await humanSelect(
    request.getByLabel("Qualified deployment", { exact: true }),
    { index: 1 },
  );
  const qualification = (await read("/v1/platform/tenants", "admin"))
    .qualifications[0];
  await humanType(
    request.getByLabel("Privacy policy reference", { exact: true }),
    qualification.privacy_reference,
  );
  await confirmTenant("New organisation for the clean water programme");
  await look(orgCard().getByText("Requested", { exact: true }), 600);
  await caption(
    "Recorded as 'Requested'. Nakul cannot activate it: the owner must accept, and a different operator must activate.",
    2800,
  );
  await signOut();

  await signIn(
    ownerPerson.email,
    ownerPerson.password,
    "Step 4 — the owner accepts the organisation.",
  );
  await console_();
  await humanClick(
    orgCard().getByRole("button", { name: "Accept ownership", exact: true }),
  );
  await confirmTenant("I accept ownership of this organisation");
  await look(orgCard().getByText("Provisioning", { exact: true }), 600);
  await caption(
    "'Provisioning': accepted, not yet active. Next the owner names a recovery contact — a safety net, not a key. Here it is Nakul.",
    1500,
  );
  await humanClick(button("Recovery contacts"));
  await page
    .getByRole("heading", { name: "Recovery contacts", exact: true })
    .waitFor();
  await humanClick(button("Nominate recovery contact"));
  const nomination = page.getByRole("region", {
    name: "Recovery contact change",
  });
  await humanSelect(nomination.getByLabel("Tenant", { exact: true }), {
    label: orgName,
  });
  await humanFill(
    nomination.getByLabel("Nominated contact identity UUID", { exact: true }),
    fixture.actors.admin.identity_id,
  );
  await humanFill(
    nomination.getByLabel("Contact expiry", { exact: true }),
    inDays(60),
  );
  await confirmContact("Nakul is our recovery contact");
  await caption(
    "The contact must confirm, and another operator must approve — the owner can do neither.",
    2200,
  );
  await signOut();

  await signIn(
    "admin",
    passwords.admin,
    "Nakul confirms that he accepts being the recovery contact.",
  );
  await console_("Recovery contacts");
  await humanClick(
    contactCard().getByRole("button", {
      name: "Verify my recovery contact",
      exact: true,
    }),
  );
  await confirmContact("I confirm I am the recovery contact");
  await look(contactCard().getByText("Verified", { exact: true }).first(), 700);
  await signOut();

  await signIn(
    second.email,
    second.password,
    "Step 5 — the second operator approves the recovery contact and activates the organisation.",
  );
  await console_("Recovery contacts");
  await humanClick(
    contactCard().getByRole("button", {
      name: "Approve recovery contact",
      exact: true,
    }),
  );
  await confirmContact("Independent review of the recovery contact");
  await look(
    contactCard().getByText("Eligible for readiness: Yes.", { exact: true }),
    900,
  );
  await humanClick(button("Back to tenant lifecycle"));
  await page
    .getByRole("heading", { name: "Tenant lifecycle", exact: true })
    .waitFor();
  await caption(
    "Activation is allowed for this operator: neither the requester nor the owner.",
    600,
  );
  await humanClick(
    orgCard().getByRole("button", { name: "Activate tenant", exact: true }),
  );
  await confirmTenant("Readiness checks pass; activating");
  await look(orgCard().getByText("Active", { exact: true }).first(), 600);
  await caption(
    "The organisation is Active. Still nobody can open it: access is granted in the next step.",
    2200,
  );
  await signOut();

  await signIn(
    ownerPerson.email,
    ownerPerson.password,
    "Step 6 — the owner proposes the initial access, naming Nakul as second administrator.",
  );
  await console_("Initial access");
  await humanClick(button("Propose initial access"));
  const proposal = page.getByRole("region", { name: "Initial access change" });
  await humanSelect(proposal.getByLabel("Tenant", { exact: true }), {
    label: orgName,
  });
  await humanFill(
    proposal.getByLabel("Second administrator identity UUID", { exact: true }),
    fixture.actors.admin.identity_id,
  );
  await humanFill(
    proposal.getByLabel("Access expiry", { exact: true }),
    inDays(60),
  );
  await caption(
    "The proposal lists the roles the organisation may give out later. It needs the second administrator's acceptance and an operator's approval.",
    1500,
  );
  await look(proposal.getByRole("group").first(), 1500);
  await confirmAccess("Initial administration for the clean water programme");
  await look(accessCard().getByText("Requested", { exact: true }), 600);
  await signOut();

  await signIn(
    "admin",
    passwords.admin,
    "Nakul accepts the administrator role.",
  );
  await console_("Initial access");
  await humanClick(
    accessCard().getByRole("button", {
      name: "Accept administrator role",
      exact: true,
    }),
  );
  await confirmAccess("I accept the second administrator role");
  await signOut();

  await signIn(
    second.email,
    second.password,
    "The second operator — neither owner nor administrator — approves the initial access.",
  );
  await console_("Initial access");
  await humanClick(
    accessCard().getByRole("button", {
      name: "Approve initial access",
      exact: true,
    }),
  );
  await confirmAccess("Independent review of the initial access");
  await look(accessCard().getByText("Applied", { exact: true }), 700);
  await caption(
    "'Applied': the owner and Nakul can now administer the organisation. Access to programme data is a separate, reviewed request.",
    2800,
  );
  await signOut();

  await signIn(
    ownerPerson.email,
    ownerPerson.password,
    "Step 7 — the owner signs in again. The workspace is there, and the standard reference data is one click.",
  );
  const reference = page.getByRole("region", { name: "Reference data" });
  await look(reference.getByRole("heading", { name: "Reference data" }), 500);
  await humanClick(
    reference.getByRole("button", {
      name: "Set up the standard reference data",
      exact: true,
    }),
  );
  await reference
    .getByRole("status")
    .filter({ hasText: "Standard reference data set up" })
    .waitFor();
  await caption(
    "This adds quarterly reporting periods, an approval workflow, a report template and a geography. The organisation is ready for work.",
    3200,
  );
  await signOut();
}

async function part2() {
  chapter("Part 2 — The measurement cycle");
  await card(
    "Part 2 — The measurement cycle",
    [
      "Inside an organisation that is already running: entering data, independent approval, calculation, closing the quarter, the dashboard and the report.",
      "Two people do the day-to-day work: a data author and an independent reviewer.",
    ],
    { kicker: "Part 2", dwell: 6500, size: 48 },
  );
  await openApp();
  await signIn(
    "author",
    passwords.author,
    "The data author signs in (test account 'author').",
  );
  await ensureWorkspace(tenant);
  await caption(
    "The portfolio lists the organisation's programmes. We open the clean water programme.",
    600,
  );
  await humanClick(await loadUntil(button(waterProgramme)));
  await caption(
    "A programme becomes Active only after its indicators and collection plan were reviewed. Its indicator is a measurement contract: once approved, a change is a new version.",
    3200,
  );
  await closeDialog();

  chapter("Entering data");
  await navTo("Measurement");
  await caption(
    "Every quarter each site reports. Two sites have reported already; the author enters the third: 8 of 10 households have safe water.",
    1500,
  );
  await humanClick(
    page.getByRole("button", { name: "Add observation", exact: false }),
  );
  await humanSelect(label("Indicator"), prepared.indicator);
  await humanType(label("Source key"), siteKey(3));
  await humanFill(label("Event date (UTC)"), "2026-09-15");
  await humanType(label("Recorded value"), "80");
  await humanType(label("Numerator"), "8");
  await humanType(label("Denominator"), "10");
  await caption(
    "A blank is never recorded as zero — every value carries an explicit state.",
    1500,
  );
  await humanClick(button("Save draft"));
  await dialog().waitFor({ state: "hidden" });
  await humanClick(await loadUntil(button(siteKey(3))));
  const evidence = page.getByRole("region", { name: "Evidence" });
  await caption(
    "Evidence can be attached to an entry — here a photo of the water point. The file is checked and scanned before it is accepted.",
    1200,
  );
  const attach = page.getByRole("form", { name: "Attach evidence" });
  await bringIntoView(attach.getByLabel("Evidence type"));
  await attach
    .getByLabel("File (PDF, PNG, JPEG, TXT or CSV, at most 25 MB)")
    .setInputFiles({
      name: "water-point-site-3.png",
      mimeType: "image/png",
      buffer: Buffer.concat([
        Buffer.from("89504e470d0a1a0a0000000d49484452", "hex"),
        Buffer.alloc(17),
        Buffer.from("# training walkthrough " + Date.now() + "\n"),
      ]),
    });
  await humanSelect(attach.getByLabel("Evidence type"), "PHOTOGRAPH");
  await humanType(attach.getByLabel("Source"), "Field visit, September 2026");
  await humanType(
    attach.getByLabel("Why it supports this record"),
    "Photo of the repaired water point",
  );
  await humanClick(attach.getByRole("button", { name: "Upload and attach" }));
  await evidence
    .getByRole("status")
    .filter({ hasText: "Evidence attached to this revision." })
    .waitFor();
  await look(evidence.getByRole("listitem").first(), 1200);
  await caption(
    "The author submits the entry for review. From now on it cannot be edited quietly.",
    600,
  );
  await humanClick(button("Submit for review"));
  await humanSelect(label("Review template"), { index: 1 });
  const entryReview = await receipt(
    () => humanClick(button("Submit for review")),
    "/actions/submit",
  );
  await page
    .getByRole("status")
    .filter({ hasText: "Saved successfully" })
    .waitFor();
  await caption(
    "The author also holds a reviewer role — but may not approve their own entry. Only a different person can.",
    2800,
  );
  await signOut();

  chapter("Independent approval and calculation");
  await signIn(
    "reviewer",
    passwords.reviewer,
    "The independent reviewer signs in (test account 'reviewer').",
  );
  await reviewAndApprove(entryReview.object_id);
  await caption(
    "The reviewer sees the exact version that was submitted and can approve it, return it for changes or reject it.",
    1800,
  );
  await decide("Checked against the site return");
  await caption("Approved. Now the quarter's result can be calculated.", 800);
  await navTo("Results");
  await humanClick(
    page.getByRole("button", { name: "Calculate result", exact: false }),
  );
  await humanSelect(label("Indicator"), prepared.indicator);
  await humanSelect(label("Reporting period"), prepared.period.object_id);
  await humanClick(button("Calculate"));
  await dialog().waitFor({ state: "hidden" });
  await humanClick(button("Result · 49.17").last());
  await dialog().getByText("PROVISIONAL", { exact: true }).first().waitFor();
  await caption(
    "59 of 120 households: 49.17 %. Totals are pooled — never an average of percentages. The result stays provisional until the quarter is closed.",
    4200,
  );
  await closeDialog();
  await signOut();

  chapter("Targets and closing the quarter");
  await signIn(
    "author",
    passwords.author,
    "Back as the author: the target for the quarter, then the period close.",
  );
  await navTo("Results framework");
  await humanSelect(label("Programme"), { label: waterProgramme });
  await humanClick(
    page.getByRole("tab", { name: "Targets vs actuals", exact: true }),
  );
  const actuals = page.getByRole("table", { name: "Targets versus actuals" });
  await look(
    actuals.locator("tr").filter({ hasText: prepared.indicatorLabel }),
    700,
  );
  await caption(
    "Targets versus actuals: the quarterly target was 55 %; the actual is 49.17 %, still provisional.",
    2800,
  );
  await navTo("Period close");
  await caption(
    "The quarter has ended. Closing it freezes the official numbers.",
    1200,
  );
  await humanClick(button("Preview period close"));
  // This dialog labels programmes by code and periods as "<code> · <state>": choose by value.
  await humanSelect(
    dialog().getByLabel("Programme", { exact: true }),
    prepared.programme,
  );
  await humanSelect(
    dialog().getByLabel("Reporting period", { exact: true }),
    prepared.period.object_id,
  );
  await humanType(
    label("Governance reason"),
    "Quarter complete; all three sites reported",
  );
  await humanSelect(label("Review policy"), { index: 1 });
  const closeReview = await receipt(
    () => humanClick(button("Submit close preview")),
    "/actions/close",
  );
  await page
    .getByRole("status")
    .filter({ hasText: "Close preview submitted for independent review." })
    .waitFor();
  await caption(
    "Even the close needs a second person: the reviewer approves it.",
    2200,
  );
  await signOut();

  await signIn(
    "reviewer",
    passwords.reviewer,
    "The reviewer approves the period close.",
  );
  await reviewAndApprove(
    closeReview.object_id,
    "The close preview pins every source and result. The reviewer checks it like any other submission.",
  );
  await decide("Sources unchanged since the preview; closing");
  await caption(
    "Closed. The official numbers are frozen in a locked snapshot.",
    800,
  );
  chapter("Dashboard");
  await navTo("Dashboards");
  await humanSelect(label("Dashboard programme"), { label: waterProgramme });
  await humanSelect(label("Dashboard period"), {
    label: prepared.period.data.code,
  });
  const dashCard = page.getByRole("article", {
    name: prepared.definitionName + " · " + prepared.indicatorLabel,
  });
  await dashCard.getByText("49.17", { exact: true }).first().waitFor();
  await look(dashCard, 1500);
  await caption(
    "The dashboard shows the official value from the locked snapshot: 49.17 %, with coverage of the three sites and how fresh the data is. Later corrections create a new version; nothing is overwritten.",
    4500,
  );
  await signOut();

  chapter("Report, form and import");
  await signIn(
    "author",
    passwords.author,
    "The author drafts the quarterly report from the locked snapshot.",
  );
  await navTo("Reports");
  await humanClick(
    page.getByRole("button", { name: "Draft report", exact: false }),
  );
  await humanSelect(label("Approved report template"), { index: 1 });
  const snapshot = (await read("snapshots?limit=100")).items.find(
    (s) =>
      s.data.programme_id === prepared.programme &&
      s.data.period_id === prepared.period.object_id,
  );
  await humanSelect(label("Locked snapshot"), snapshot.object_id);
  await humanType(label("Section heading"), reportHeading);
  const binding =
    prepared.reportTemplate?.data.sections?.[0]?.required_binding_codes?.[0] ||
    "RESULT";
  await humanType(
    label("Narrative"),
    "In the third quarter {{" +
      binding +
      "}} of the visited households had safe drinking water.",
  );
  await humanSelect(label("Result to reference"), { index: 1 });
  await caption(
    "Numbers in the text are placeholders bound to the official result. A typed-in number would be refused.",
    2000,
  );
  await humanClick(button("Save draft"));
  await dialog().waitFor({ state: "hidden" });
  await humanClick(await loadUntil(button(reportHeading)));
  await humanClick(button("Submit frozen package for review"));
  await humanSelect(label("Review template"), { index: 1 });
  const reportReview = await receipt(
    () => humanClick(button("Submit for review")),
    "/actions/submit",
  );
  await dialog().waitFor({ state: "hidden" });
  await caption(
    "The report package goes to the reviewer. Meanwhile, two other ways data comes in.",
    1500,
  );

  await navTo("Forms");
  await humanSelect(label("Programme"), { label: fieldProgramme });
  await caption(
    "Web forms: this published form feeds the household count of a second programme.",
    1200,
  );
  await humanClick(button("Fill in"));
  await dialog().getByText("Version 1", { exact: false }).waitFor();
  await humanType(label("Reporting unit"), prepared.formUnit);
  await humanSelect(label("Consent given"), "true");
  await humanType(label("Households reached"), "12");
  await humanClick(button("Submit response"));
  await dialog().waitFor({ state: "hidden" });
  await caption(
    "The response became a data entry, waiting for the same independent review.",
    2000,
  );

  await navTo("Imports");
  await humanSelect(label("Programme"), { label: fieldProgramme });
  await humanSelect(label("Period"), prepared.period.object_id);
  await humanClick(button(prepared.batchFile));
  const outcomes = page.getByRole("table", { name: "Row outcomes" });
  await look(outcomes, 1000);
  await caption(
    "Spreadsheets are checked row by row: accepted, quarantined (not a number) or duplicate. Nothing is written until the batch is committed.",
    3800,
  );
  await signOut();

  chapter("Approving the report and rendering a PDF");
  await signIn(
    "reviewer",
    passwords.reviewer,
    "The reviewer approves the report package, then asks for a PDF.",
  );
  await reviewAndApprove(
    reportReview.object_id,
    "The report package is reviewed as a whole: template, snapshot and the exact bound result.",
  );
  await decide("Snapshot, template and binding checked");
  await caption(
    "Approved. The reviewer now asks for a PDF of the frozen package.",
    800,
  );
  await navTo("Reports");
  await humanClick(await loadUntil(button(reportHeading)));
  const exportsPanel = page.getByRole("region", { name: "Report exports" });
  await humanClick(
    exportsPanel.getByRole("button", {
      name: "Request PDF report",
      exact: true,
    }),
  );
  const pdfRow = exportsPanel
    .locator("tbody tr")
    .filter({ has: page.getByRole("cell", { name: "PDF", exact: true }) });
  await pdfRow.getByText("Queued", { exact: false }).waitFor();
  await caption(
    "A background worker renders the PDF from the frozen package. The panel updates on its own.",
    1000,
  );
  await pdfRow
    .getByRole("link", { name: "Download PDF", exact: true })
    .waitFor({ timeout: 90000 });
  await look(pdfRow, 1500);
  await caption(
    "Done: the PDF can be downloaded. Sending it to a named recipient is a separate, reviewed publication step.",
    3200,
  );
  await closeDialog();
  await signOut();

  chapter("People & access");
  await signIn(
    "admin",
    passwords.admin,
    "Finally, People & access — where an administrator manages who may do what.",
  );
  await ensureWorkspace(tenant);
  await caption(
    "Members and their roles. A role change is requested by one administrator and approved by another.",
    2800,
  );
  const reference = page.getByRole("region", { name: "Reference data" });
  await look(reference.getByRole("heading", { name: "Reference data" }), 800);
  await caption(
    "Reference data: the reporting calendar, review workflow and report templates.",
    1800,
  );
  await look(page.getByRole("heading", { name: "Audit export" }), 800);
  await caption(
    "Audit export: a sealed record of who did what, for a stated purpose.",
    1800,
  );
  await look(page.getByRole("heading", { name: "Data-subject requests" }), 800);
  await caption(
    "Data-subject requests: access and erasure requests about members — planned, approved by a second person, then executed.",
    3000,
  );
  await signOut();
}

async function outro() {
  chapter("What you need to start");
  await card(
    "What you need to start",
    [
      "On the live server you need three people: you (operator and second administrator), a second operator, and the organisation's owner.",
      "After that, day-to-day work needs two: one who enters data and one who approves.",
    ],
    { kicker: "In short", dwell: 8000, size: 48 },
  );
  const lead = chapters.length ? Math.max(0, chapters[0].at - 300) : 0;
  const list = chapters.map((c) => format(c.at - lead) + "  " + c.title);
  await card("Chapters", list, { kicker: "Index", dwell: 7000, size: 44 });
}

// ---------------------------------------------------------------------------------------------
let failed = null;
try {
  // A short blank lead, so that the first title card's appearance is a visible transition that
  // narrate.py can measure against the logged time.
  await sleep(1000);
  if (want("intro")) await intro();
  if (want("part1")) await part1();
  if (want("part2")) await part2();
  if (want("outro")) await outro();
} catch (e) {
  failed = e;
  console.error(e.stack || e.message);
  await page
    .screenshot({ path: path.join(outDir, "failure.png"), fullPage: true })
    .catch(() => {});
} finally {
  const video = page.video();
  await context.close();
  await browser.close();
  const recorded = await video.path();
  const webm = path.join(outDir, "raw.webm");
  await fs.rename(recorded, webm);
  // The recording starts a moment before the first card is painted: the MP4 begins 0.3 s before
  // the first chapter and the chapter times are shifted accordingly.
  const trim = chapters.length ? Math.max(0, chapters[0].at / 1000 - 0.3) : 0;
  const index = {};
  for (const c of chapters) index[c.title] = format(c.at - trim * 1000);
  await fs.writeFile(
    path.join(outDir, "chapters.json"),
    JSON.stringify(index, null, 2) + "\n",
  );
  await fs.writeFile(
    path.join(outDir, "timeline.json"),
    JSON.stringify(
      {
        started: new Date(started).toISOString(),
        trimMs: Math.round(trim * 1000),
        pace,
        audioDir,
        entries: timeline,
      },
      null,
      2,
    ) + "\n",
  );
  const mp4 = path.join(outDir, "impact-platform-walkthrough.mp4");
  const conversion = spawnSync(
    ffmpeg,
    [
      "-y",
      "-ss",
      trim.toFixed(2),
      "-i",
      webm,
      "-c:v",
      "libx264",
      "-preset",
      "medium",
      "-crf",
      process.env.TRAINING_VIDEO_CRF || "23",
      "-pix_fmt",
      "yuv420p",
      "-movflags",
      "+faststart",
      "-an",
      mp4,
    ],
    { stdio: ["ignore", "ignore", "pipe"], encoding: "utf8" },
  );
  if (conversion.status !== 0)
    console.error(
      "ffmpeg failed (" +
        conversion.status +
        "): " +
        (conversion.stderr || "").slice(-2000),
    );
  else console.log("wrote " + mp4);
  console.log(
    "recording " + format(Date.now() - started) + " total; chapters:",
  );
  for (const c of chapters)
    console.log("  " + format(c.at - trim * 1000) + "  " + c.title);
  if (pageErrors.length)
    console.log("page errors: " + JSON.stringify(pageErrors));
  if (failed) process.exitCode = 1;
}
