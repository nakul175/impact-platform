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
