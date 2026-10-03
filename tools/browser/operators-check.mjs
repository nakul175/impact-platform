// operators-browser (v0.26a, usable staging): the click-path a non-engineer owner follows without a
// server console. A platform operator nominates a colleague in the Operators panel of the
// tenant-lifecycle console and creates their sign-in, sees the one-time password once, and the
// colleague signs in with it, lands on the plain-language start page and accepts the operator role
// themselves. A workspace administrator then sets up the standard reference data in one click, and
// sees the purpose-bound access section. The development login stands in for the identity provider
// (development account backend); the same operations against Keycloak run in CI's container stack.
import assert from "node:assert/strict";
import { harness, nav, read } from "./qa-harness.mjs";

const { as, test, finish } = await harness("operators-browser");
const email = "operator-" + Date.now() + "@example.test";

await finish(async () => {
  const admin = await as("admin");
  const operators = () => admin.getByRole("region", { name: "Operators" });
  let password = "";

  await test("An operator nominates a colleague and creates their sign-in", async () => {
    await nav(admin, "Tenant lifecycle");
    await admin
      .getByRole("heading", { name: "Tenant lifecycle", exact: true })
      .waitFor();
    await operators()
      .getByRole("button", { name: "Nominate an operator", exact: true })
      .click();
    const form = admin.getByRole("form", { name: "Nominate an operator" });
    await form.getByLabel("Their e-mail address", { exact: true }).fill(email);
    await form.getByRole("button", { name: "Nominate", exact: true }).click();
    await operators()
      .getByRole("status")
      .filter({ hasText: "Nomination recorded" })
      .waitFor();
    const signIn = admin.getByRole("form", { name: "Create a sign-in" });
    assert.equal(
      await signIn.getByLabel("E-mail address", { exact: true }).inputValue(),
      email,
    );
    await signIn.getByLabel("First name", { exact: true }).fill("Second");
    await signIn.getByLabel("Last name", { exact: true }).fill("Operator");
    await signIn
      .getByLabel("Reason", { exact: true })
      .fill("Second operator for independent activation");
    await signIn
      .getByRole("button", { name: "Create sign-in", exact: true })
      .click();
    const credential = admin.getByRole("region", { name: "One-time password" });
    await credential.waitFor();
    password = await credential
      .getByLabel("One-time password", { exact: true })
      .inputValue();
    assert.match(password, /^[a-z2-9]{4}(-[a-z2-9]{4}){4}$/);
    assert.match(await credential.innerText(), /shown only now/);
    await credential
      .getByRole("button", { name: "I have noted it — hide the password" })
      .click();
    await operators().waitFor();
    assert(!(await admin.content()).includes(password));
    assert.match(
      await operators().innerText(),
      /sign-in created by the nominating operator/,
    );
  });

  await test("The colleague signs in, reads the start page and accepts", async () => {
    const colleague = await as(email, 900, password);
    await colleague
      .getByRole("heading", { name: "No active workspace", exact: true })
      .waitFor();
    // The start page loads the nominations after its heading renders ("Checking what is
    // next…"); since build 0.27.0 the status banner's first poll shares PGlite's single
    // connection with that read, so wait for the page to finish loading before reading it.
    await colleague
      .getByText("Checking what is next…", { exact: true })
      .waitFor({ state: "detached" });
    const start = await colleague.locator("main").innerText();
    assert.match(start, /nominated as a platform operator/);
    assert.match(start, /Your identity reference/);
    await colleague
      .getByRole("button", { name: "Tenant lifecycle", exact: true })
      .click();
    const panel = colleague.getByRole("region", { name: "Operators" });
    await panel
      .getByRole("heading", {
        name: "You are nominated as a platform operator",
      })
      .waitFor();
    await panel
      .getByRole("button", { name: "Accept operator role", exact: true })
      .click();
    await panel
      .getByRole("status")
      .filter({ hasText: "You are now a platform operator." })
      .waitFor();
    const directory = await read("/v1/platform/operators", "admin");
    assert(
      directory.operators.some(
        (o) => o.active && o.email_mask.startsWith("op***@"),
      ),
      JSON.stringify(directory.operators),
    );
  });

  await test("Another operator renews the colleague's role, then deactivates it", async () => {
    // v0.27 operator lifecycle: the nominating operator (a different person) renews the new
    // operator's role to a later date, then deactivates it (self-service is refused by the
    // server; qualification/test_operator_lifecycle.py covers it).
    await operators()
      .getByRole("button", { name: "Refresh operators", exact: true })
      .click();
    const row = operators()
      .getByRole("listitem")
      .filter({ hasText: "op***@" })
      .first();
    await row.getByRole("button", { name: "Renew operator role" }).waitFor();
    const before = (
      await read("/v1/platform/operators", "admin")
    ).operators.find((o) => o.email_mask.startsWith("op***@"));
    await row.getByRole("button", { name: "Renew operator role" }).click();
    const renew = admin.getByRole("form", { name: "Renew operator role" });
    const later = new Date(Date.now() + 300 * 86400000)
      .toISOString()
      .slice(0, 10);
    await renew.getByLabel("Operator role until", { exact: true }).fill(later);
    await renew
      .getByLabel("Reason", { exact: true })
      .fill("Renewed for the coming review cycle");
    await renew.getByRole("button", { name: "Renew", exact: true }).click();
    await operators()
      .getByRole("status")
      .filter({ hasText: "Operator role renewed." })
      .waitFor();
    let directory = await read("/v1/platform/operators", "admin");
    const renewed = directory.operators.find(
      (o) => o.identity_id === before.identity_id,
    );
    assert(
      new Date(renewed.expires_at) > new Date(before.expires_at) &&
        renewed.revision_id !== before.revision_id,
      JSON.stringify([before, renewed]),
    );
    assert.equal(directory.changes[0].action, "renew");
    assert.match(await operators().innerText(), /Operator changes/);
    await row.getByRole("button", { name: "Deactivate", exact: true }).click();
    const deactivate = admin.getByRole("form", { name: "Deactivate operator" });
    await deactivate
      .getByLabel("Reason", { exact: true })
      .fill("Left the organisation");
    await deactivate
      .getByRole("button", { name: "Deactivate operator", exact: true })
      .click();
    await operators()
      .getByRole("status")
      .filter({ hasText: "Operator deactivated." })
      .waitFor();
    directory = await read("/v1/platform/operators", "admin");
    const gone = directory.operators.find(
      (o) => o.identity_id === before.identity_id,
    );
    assert.equal(gone.state, "Deactivated");
    assert(!gone.active && directory.changes[0].action === "deactivate");
    assert.match(await row.innerText(), /deactivated since/);
  });

  await test("A workspace administrator sets up the standard reference data", async () => {
    await admin
      .getByRole("button", { name: "Back to workspace", exact: true })
      .click();
    await nav(admin, "People & access");
    const panel = admin.getByRole("region", { name: "Reference data" });
    await panel
      .getByRole("button", {
        name: "Set up the standard reference data",
        exact: true,
      })
      .click();
    await panel
      .getByRole("status")
      .filter({ hasText: "Standard reference data set up" })
      .waitFor();
    await panel
      .getByRole("button", {
        name: "Set up the standard reference data",
        exact: true,
      })
      .click();
    await panel
      .getByRole("alert")
      .filter({ hasText: "already set up" })
      .waitFor();
    const calendars = (await read("reporting-calendars?limit=100", "author"))
      .items;
    assert(
      calendars.some((c) => c.data.title === "Standard quarterly calendar"),
    );
    await admin
      .getByRole("tab", { name: "Purpose-bound access", exact: true })
      .click();
    await admin
      .getByRole("button", {
        name: "Request purpose-bound access",
        exact: true,
      })
      .waitFor();
  });
}, "Operator onboarding and reference data in the browser");
