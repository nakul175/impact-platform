"use strict";

const $ = (id) => document.getElementById(id);
const fmt = (value, zone = "Asia/Kolkata") =>
  value
    ? new Intl.DateTimeFormat("en-IN", {
        timeZone: zone,
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      }).format(new Date(value))
    : "Unestimated";
const label = (value) =>
  value
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/^./, (c) => c.toUpperCase());
let current = null;
let paused = false;
let fetching = false;
let receivedAt = 0;
let lastAnnouncement = "";
let lastStreamSignature = "";
let lastBacklogSignature = "";

function node(tag, text, className) {
  const value = document.createElement(tag);
  if (text !== undefined) value.textContent = text;
  if (className) value.className = className;
  return value;
}

function detail(title, children) {
  const container = node("details");
  container.append(node("summary", title), ...children);
  return container;
}

function etaText(stream) {
  if (stream.status === "COMPLETE") return "Completed for this bounded slice";
  if (stream.eta.confidence === "UNESTIMATED") return "ETA not yet estimated";
  return `${fmt(stream.eta.earliest)} – ${fmt(stream.eta.latest)} IST`;
}

function renderStreams() {
  if (!current) return;
  const filter = $("filter").value;
  const signature = JSON.stringify([
    current.streams,
    filter,
    Math.floor(Date.now() / 60000),
  ]);
  if (signature === lastStreamSignature) return;
  // Do not remove a focused control or close the user's expanded record each poll.
  if ($("streams").contains(document.activeElement)) return;
  const expanded = new Set(
    [
      ...$("streams").querySelectorAll("article[data-stream] details[open]"),
    ].map(
      (item) =>
        `${item.closest("article").dataset.stream}:${item.querySelector("summary").textContent}`,
    ),
  );
  const streams = current.streams.filter(
    (item) =>
      filter === "all" ||
      (filter === "active"
        ? !["QUEUED", "COMPLETE", "BLOCKED"].includes(item.status)
        : item.status === filter),
  );
  const fragment = document.createDocumentFragment();
  for (const stream of streams) {
    const card = node("article", undefined, "stream");
    card.dataset.stream = stream.id;
    const top = node("div", undefined, "stream-top");
    top.append(
      node("h3", stream.title),
      node(
        "span",
        label(stream.status),
        `status ${stream.status.toLowerCase()}`,
      ),
    );
    const eta = node("div", undefined, "eta");
    eta.append(
      node("strong", etaText(stream)),
      node(
        "p",
        `${label(stream.eta.confidence)} confidence · ${stream.eta.basis}`,
      ),
    );
    const next = node("p", undefined, "next");
    next.append(
      node("span", "Next: "),
      document.createTextNode(stream.next_step),
    );
    card.append(
      top,
      node("p", `${stream.domain} · ${stream.owner}`, "owner"),
      node("p", stream.summary, "stream-copy"),
      eta,
      next,
      node("p", `Source updated ${fmt(stream.updated_at)} IST`, "source-time"),
    );
    if (
      Date.now() - new Date(stream.updated_at).getTime() > 15 * 60 * 1000 &&
      stream.status !== "COMPLETE"
    )
      card.append(
        node(
          "p",
          "No source update in 15 minutes. This state may be stale.",
          "stale",
        ),
      );
    if (
      stream.eta.latest &&
      Date.now() > new Date(stream.eta.latest).getTime() &&
      stream.status !== "COMPLETE"
    )
      card.append(
        node(
          "p",
          "The forecast window has passed. A revised estimate is needed.",
          "stale",
        ),
      );
    if (stream.blockers.length) {
      const blockers = node("ul", undefined, "blocked-list");
      stream.blockers.forEach((item) => blockers.append(node("li", item)));
      card.append(blockers);
    }
    if (stream.delivered.length) {
      const list = node("ul");
      stream.delivered.forEach((item) => list.append(node("li", item)));
      card.append(
        detail(
          `${stream.delivered.length} recorded deliverable${stream.delivered.length === 1 ? "" : "s"}`,
          [list],
        ),
      );
    }
    if (stream.evidence.length) {
      const list = node("ul", undefined, "evidence-list");
      for (const evidence of stream.evidence) {
        const item = node("li", undefined, "evidence-item");
        item.append(
          node("strong", `${evidence.title} · ${evidence.result}`),
          node("p", evidence.scope),
          node("span", evidence.path, "evidence-path"),
          node(
            "span",
            `Recorded ${fmt(evidence.recorded_at)} IST`,
            "source-time",
          ),
        );
        list.append(item);
      }
      card.append(
        detail(
          `${stream.evidence.length} supporting evidence record${stream.evidence.length === 1 ? "" : "s"}`,
          [list],
        ),
      );
    }
    if (stream.history.length) {
      const list = node("ol", undefined, "history-list");
      stream.history
        .slice()
        .reverse()
        .forEach((item) =>
          list.append(
            node(
              "li",
              `${fmt(item.at)} IST · ${label(item.status)} · ${item.summary}`,
            ),
          ),
        );
      card.append(detail("Recorded update history", [list]));
    }
    fragment.append(card);
  }
  if (!streams.length)
    fragment.append(node("p", "No workstreams match this view.", "empty"));
  $("streams").replaceChildren(fragment);
  for (const item of $("streams").querySelectorAll(
    "article[data-stream] details",
  ))
    item.open = expanded.has(
      `${item.closest("article").dataset.stream}:${item.querySelector("summary").textContent}`,
    );
  lastStreamSignature = signature;
}

function renderBacklog() {
  const backlog = current.backlog;
  const signature = JSON.stringify(backlog);
  if (signature === lastBacklogSignature) return;
  $("baseline").replaceChildren(
    node(
      "p",
      `Impact core: ${backlog.baseline.impact_requirements} source requirements · ${backlog.baseline.impact_partial} partial · ${backlog.baseline.impact_pending} pending · ${backlog.baseline.impact_accepted} accepted`,
    ),
    node(
      "p",
      `AI extension: ${backlog.baseline.ai_requirements} source feature areas`,
    ),
    node(
      "p",
      `${backlog.domains.length} consolidated scope domains · no overall completion percentage`,
    ),
  );
  const fragment = document.createDocumentFragment();
  for (const domain of backlog.domains) {
    const item = node("article", undefined, "domain");
    item.append(
      node("h3", domain.title),
      node("p", domain.current),
      node("p", `Remaining: ${domain.remaining}`),
      node(
        "p",
        `${domain.impact_requirement_ids.length} impact requirements · ${domain.ai_requirement_ids.length} AI requirements`,
      ),
      node("p", `Sources: ${domain.sources.join("; ")}`, "source-time"),
    );
    fragment.append(item);
  }
  $("backlog").replaceChildren(fragment);
  lastBacklogSignature = signature;
}

function tick() {
  if (!current) return;
  const remaining = new Date(current.sprint.deadline).getTime() - Date.now();
  if (remaining <= 0) $("countdown").textContent = "Window ended";
  else {
    const total = Math.floor(remaining / 1000);
    $("countdown").textContent =
      `${String(Math.floor(total / 3600)).padStart(2, "0")}:${String(Math.floor((total % 3600) / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
  }
  if (paused) {
    $("connection").textContent = "Updates paused · recorded snapshot";
    $("connection").className = "live-indicator warning";
  } else if (Date.now() - receivedAt > 15000) {
    $("connection").textContent = "Connection stale · last known snapshot";
    $("connection").className = "live-indicator warning";
  }
}

function render() {
  const sprint = current.sprint;
  $("summary").textContent = sprint.rollup.summary;
  $("deadline").textContent = `Until ${fmt(sprint.deadline)} IST`;
  $("utc-deadline").textContent =
    `${fmt(sprint.deadline, "UTC")} UTC · sprint ${label(sprint.status)}`;
  $("integrated").textContent = String(sprint.rollup.integrated_increments);
  $("planned").textContent =
    `${sprint.rollup.planned_increments} currently planned bounded increments`;
  $("verified").textContent = String(sprint.rollup.verified_increments);
  $("agents").textContent = String(sprint.rollup.active_agents);
  $("agent-limit").textContent =
    `Up to ${sprint.active_agent_limit} active agents, including integration`;
  $("updated").textContent =
    `Rollup source updated ${fmt(sprint.updated_at)} IST · snapshot read ${fmt(current.served_at)} IST`;
  $("checkpoint").textContent =
    `Next integration checkpoint: ${fmt(sprint.rollup.next_checkpoint)} IST`;
  $("branch").textContent = `Review branch: ${sprint.branch}`;
  $("limits").replaceChildren(...sprint.limits.map((text) => node("li", text)));
  const problems = current.errors.map(
    (item) => `${item.stream_id}: ${item.message}`,
  );
  if (
    Date.now() - new Date(sprint.updated_at).getTime() > 15 * 60 * 1000 &&
    sprint.status === "ACTIVE"
  )
    problems.push(
      "The integration rollup has no update in 15 minutes; individual streams may have newer records.",
    );
  $("notice").hidden = problems.length === 0;
  $("notice").textContent = problems.join(" ");
  renderStreams();
  renderBacklog();
  const announcement = `${sprint.rollup.integrated_increments} integrated, ${sprint.rollup.verified_increments} locally verified. ${current.streams.map((s) => `${s.title}: ${label(s.status)}`).join(". ")}`;
  if (announcement !== lastAnnouncement) {
    $("announce").textContent = announcement;
    lastAnnouncement = announcement;
  }
  tick();
}

async function refresh() {
  if (fetching) return;
  fetching = true;
  try {
    const response = await fetch(`/api/status?t=${Date.now()}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(6000),
    });
    if (!response.ok) throw new Error("source_unavailable");
    const next = await response.json();
    if (!next.sprint || !Array.isArray(next.streams) || !next.backlog)
      throw new Error("invalid_snapshot");
    current = next;
    receivedAt = Date.now();
    $("connection").textContent = "Live · recorded files every 5 seconds";
    $("connection").className = "live-indicator good";
    render();
  } catch {
    $("notice").hidden = false;
    $("notice").textContent = current
      ? "Live update unavailable. Showing the last successfully read snapshot; its source timestamps remain visible."
      : "The tracker cannot read a valid source snapshot yet. Retry with Refresh now.";
    $("connection").textContent =
      "Source unavailable · information may be stale";
    $("connection").className = "live-indicator warning";
  } finally {
    fetching = false;
  }
}

$("refresh").addEventListener("click", refresh);
$("filter").addEventListener("change", renderStreams);
$("pause").addEventListener("click", () => {
  paused = !paused;
  $("pause").setAttribute("aria-pressed", String(paused));
  $("pause").textContent = paused ? "Resume updates" : "Pause updates";
  if (!paused) refresh();
  tick();
});
setInterval(() => {
  if (!paused) refresh();
}, 5000);
setInterval(tick, 1000);
refresh();
