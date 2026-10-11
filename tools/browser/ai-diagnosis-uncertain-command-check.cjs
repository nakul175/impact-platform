const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const Module = require("node:module");
const { createRequire } = Module;
const { createHash } = require("node:crypto");
const { execFileSync } = require("node:child_process");
const assert = require("node:assert/strict");

// This observes actual compiled component closures through a declared test-only
// in-memory hooks/request adapter. It is NOT mounted browser, HTTP, database,
// receipt-expiry-clock, provider or production qualification.
const root = process.cwd();
const sourcePath = path.join(root, "apps/web/src/AIDiagnosis.tsx");
const stylePath = path.join(root, "apps/web/src/ai-diagnosis.css");
const requireWeb = createRequire(path.join(root, "apps/web/package.json"));
const React = requireWeb("react");
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
const source = fs.readFileSync(sourcePath);
const work = fs.mkdtempSync(
  path.join(os.tmpdir(), "imprana-diagnosis-adapter-"),
);
fs.writeFileSync(path.join(work, "AIDiagnosis.tsx"), source);
fs.writeFileSync(
  path.join(work, "ai-diagnosis.css"),
  fs.readFileSync(stylePath),
);
fs.writeFileSync(path.join(work, "style.d.ts"), 'declare module "*.css";\n');
fs.symlinkSync(
  path.join(root, "apps/web/node_modules"),
  path.join(work, "node_modules"),
);
const results = [];
let emitted;
function shape(message) {
  return String(message).replace(/Bearer\s+[^\s"']+/g, "Bearer [withheld]");
}

function makeHarness(errorCode) {
  let index = 0;
  const cells = [],
    effects = [],
    calls = [];
  const useState = (initial) => {
    const position = index++;
    if (!cells[position])
      cells[position] = {
        value: typeof initial === "function" ? initial() : initial,
      };
    return [
      cells[position].value,
      (next) => {
        cells[position].value =
          typeof next === "function" ? next(cells[position].value) : next;
      },
    ];
  };
  const useRef = (initial) => {
    const position = index++;
    if (!cells[position]) cells[position] = { current: initial };
    return cells[position];
  };
  const useEffect = (effect) => {
    const position = index++;
    if (!cells[position]) {
      cells[position] = { mounted: true };
      effects.push(effect);
    }
  };
  const useId = () => {
    const position = index++;
    if (!cells[position])
      cells[position] = { value: "qa-diagnosis-" + position };
    return cells[position].value;
  };
  const hooks = { ...React, useState, useRef, useEffect, useId };
  hooks.default = hooks;
  hooks.__esModule = true;
  const candidate = new Module(
    path.join(work, "component-adapter.cjs"),
    module,
  );
  candidate.filename = path.join(work, "component-adapter.cjs");
  candidate.require = (name) =>
    name === "react" ? hooks : name.endsWith(".css") ? {} : requireWeb(name);
  candidate._compile(
    emitted + "\nexports.__adapter = { DiagnosisWorkspace };\n",
    candidate.filename,
  );
  const props = {
    base: "/v1/tenants/11111111-1111-4111-8111-111111111111/",
    principalId: "22222222-2222-4222-8222-222222222222",
    sessionIdentity: "synthetic-adapter-session",
    capabilities: ["ai.diagnosis.read", "ai.diagnosis.manage"],
    canRead: true,
    canManage: true,
    explain: (error) => error.code || error.message,
    request: async (route, options = {}) => {
      if (!options.method) return { items: [], next_cursor: null };
      calls.push({ route, method: options.method, body: options.body });
      throw Object.assign(
        new Error("Synthetic adapter outcome; no HTTP request"),
        { code: errorCode },
      );
    },
  };
  let tree;
  function render() {
    index = 0;
    tree = candidate.exports.__adapter.DiagnosisWorkspace(props);
    for (const effect of effects.splice(0)) effect();
    return tree;
  }
  function nodes() {
    const found = [];
    function visit(value) {
      if (Array.isArray(value)) return value.forEach(visit);
      if (!value || typeof value !== "object" || !value.props) return;
      found.push(value);
      visit(value.props.children);
    }
    visit(tree);
    return found;
  }
  function find(type, match) {
    const found = nodes().filter(
      (node) => node.type === type && match(node.props),
    );
    assert.equal(found.length, 1, "Unique actual component control: " + type);
    return found[0];
  }
  const namedButton = (name) =>
    find("button", (props) => props.children === name);
  const input = () =>
    find("input", (props) => props["aria-label"] === "Diagnosis title");
  const pendingGroup = () =>
    nodes().filter(
      (node) =>
        node.props.role === "group" &&
        node.props["aria-label"] === "Uncertain diagnosis request",
    );
  const flush = async () => {
    await new Promise(setImmediate);
    await new Promise(setImmediate);
    render();
  };
  return { render, input, namedButton, pendingGroup, flush, calls, find };
}
async function test(name, fn) {
  const row = { name, status: "running" };
  try {
    row.observations = await fn();
    row.status = "passed";
  } catch (error) {
    row.status = "failed";
    row.message = shape(error.message);
    process.exitCode = 1;
  }
  results.push(row);
}

(async () => {
  try {
    execFileSync(
      path.join(root, "apps/web/node_modules/.bin/tsc"),
      [
        "--module",
        "commonjs",
        "--target",
        "ES2022",
        "--jsx",
        "react",
        "--esModuleInterop",
        "--strict",
        "--skipLibCheck",
        "--noEmit",
        "false",
        "--lib",
        "ES2022,DOM",
        "--outDir",
        path.join(work, "compiled"),
        path.join(work, "AIDiagnosis.tsx"),
        path.join(work, "style.d.ts"),
      ],
      { cwd: work, encoding: "utf8", timeout: 60000, stdio: "pipe" },
    );
    emitted = fs.readFileSync(
      path.join(work, "compiled/AIDiagnosis.js"),
      "utf8",
    );
    for (const code of ["IDEMPOTENCY_EXPIRED", "CONFLICT_OPERATION"]) {
      await test(
        code + " preserves frozen uncertain create and exact retry",
        async () => {
          const h = makeHarness(code);
          h.render();
          await h.flush();
          h.input().props.onChange({
            target: { value: "Synthetic unknown prior create outcome" },
          });
          h.render();
          h.namedButton("Save diagnosis draft").props.onClick();
          await h.flush();
          assert.equal(h.calls.length, 1);
          assert.equal(h.pendingGroup().length, 1);
          assert.equal(
            h.input().props.value,
            "Synthetic unknown prior create outcome",
          );
          assert.equal(h.input().props.readOnly, true);
          assert.equal(
            h.namedButton("Save diagnosis draft").props.disabled,
            true,
          );
          assert.equal(h.namedButton("New diagnosis").props.disabled, true);
          assert.equal(
            h.find(
              "select",
              (props) => props["aria-label"] === "Saved diagnoses",
            ).props.disabled,
            true,
          );
          const first = h.calls[0];
          h.namedButton("Retry the same request").props.onClick();
          await h.flush();
          assert.equal(h.calls.length, 2);
          assert.deepEqual(h.calls[1], first);
          assert.equal(h.pendingGroup().length, 1);
          assert.equal(h.input().props.readOnly, true);
          assert.equal(
            h.namedButton("Save diagnosis draft").props.disabled,
            true,
          );
          return {
            adapter_error_code: code,
            requests_to_adapter: h.calls.length,
            request_bytes_sha256: hash(first.body),
            operation_id: JSON.parse(first.body).operation_id,
            frozen_pending_after_retry: true,
            new_create_control_disabled: true,
          };
        },
      );
    }
    await test("Known validation refusal releases the refused draft for editing", async () => {
      const h = makeHarness("VALIDATION_FAILED");
      h.render();
      await h.flush();
      h.input().props.onChange({
        target: { value: "Synthetic definitively refused draft" },
      });
      h.render();
      h.namedButton("Save diagnosis draft").props.onClick();
      await h.flush();
      assert.equal(h.calls.length, 1);
      assert.equal(h.pendingGroup().length, 0);
      assert.equal(
        h.input().props.value,
        "Synthetic definitively refused draft",
      );
      assert.equal(h.input().props.readOnly, false);
      assert.equal(h.namedButton("Save diagnosis draft").props.disabled, false);
      return {
        adapter_error_code: "VALIDATION_FAILED",
        pending_after_refusal: false,
        refused_input_preserved: true,
      };
    });
    assert.equal(
      hash(fs.readFileSync(sourcePath)),
      hash(source),
      "Actual component source changed during bounded adapter run",
    );
  } catch (error) {
    process.exitCode = 1;
    results.push({
      name: "Compile/source-pin setup",
      status: "failed",
      message: shape(error.message),
    });
  } finally {
    process.stdout.write(
      JSON.stringify(
        {
          scope:
            "ACTUAL_COMPONENT_CLOSURES_WITH_DECLARED_TEST_ONLY_HOOKS_AND_REQUEST_ADAPTER",
          status: process.exitCode ? "failed" : "passed",
          counts: {
            cases: results.length,
            passed: results.filter((row) => row.status === "passed").length,
            failed: results.filter((row) => row.status === "failed").length,
          },
          source_path: sourcePath,
          source_sha256: hash(source),
          compiled_sha256: emitted ? hash(emitted) : null,
          react_version: React.version,
          results,
          limitations: [
            "No real browser mount, DOM events, React concurrent scheduler, API/DB/server receipt expiry, test clock or production acceptance is claimed.",
            "Synthetic request-adapter errors exercise actual component command handlers and rendered control state; they are not server responses or HTTP qualification.",
            "Actual API expired replay requires an approved test clock or actual elapsed retention period; immutable receipts and audit/history must not be edited to manufacture expiry.",
          ],
        },
        null,
        2,
      ) + "\n",
    );
    fs.rmSync(work, { recursive: true, force: true });
  }
})();
