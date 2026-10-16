import { test } from "node:test";
import assert from "node:assert/strict";
import {
  sections,
  freshDemo,
  saveDemo,
  advanceDemo,
} from "../../apps/web/src/PublicSandboxModel.ts";

test("fresh workspaces and sections do not share mutable records", () => {
  const a = freshDemo(),
    b = freshDemo();
  a.programmes[0].history.push("local");
  assert.equal(b.programmes[0].history.length, 1);
  assert.equal(new Set(sections.map(([id]) => id)).size, 20);
  const edited = saveDemo(
    a,
    "programmes",
    "New title",
    "Invented",
    a.programmes[0].id,
  );
  assert.equal(a.programmes[0].title, "Community learning");
  assert.deepEqual(edited.observations, a.observations);
});
test("review is explicitly simulated and edits invalidate its state", () => {
  const a = freshDemo(),
    id = a.programmes[0].id;
  const submitted = advanceDemo(a, "programmes", id);
  const reviewed = advanceDemo(submitted, "programmes", id);
  assert.equal(a.programmes[0].status, "Draft");
  assert.equal(reviewed.programmes[0].status, "Reviewed (simulation)");
  assert.throws(() => advanceDemo(reviewed, "programmes", id));
  const edited = saveDemo(reviewed, "programmes", "Changed", "New draft", id);
  assert.equal(edited.programmes[0].status, "Draft");
  assert.equal(edited.programmes[0].history.length, 4);
});
test("invalid drafts and stale IDs cannot change the workspace", () => {
  const a = freshDemo();
  for (const title of ["", "   ", "a".repeat(121)])
    assert.throws(() => saveDemo(a, "programmes", title, ""));
  assert.throws(() => saveDemo(a, "programmes", "Title", "a".repeat(2001)));
  assert.throws(() => saveDemo(a, "programmes", "Title", "", "missing"));
  assert.throws(() => advanceDemo(a, "programmes", "missing"));
  assert.equal(a.programmes.length, 1);
});
test("bounded records and fresh reset discard every edit", () => {
  let a = freshDemo();
  for (let i = 0; i < 49; i++)
    a = saveDemo(a, "programmes", `Example ${i}`, "");
  assert.equal(new Set(a.programmes.map((r) => r.id)).size, 50);
  assert.throws(() => saveDemo(a, "programmes", "Too many", ""));
  assert.equal(freshDemo().programmes.length, 1);
});
