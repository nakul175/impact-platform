// Live identity-provider browser check (v0.15): sign in through Keycloak's own pages with a
// password and a TOTP code, reach the workspace, sign out and confirm the provider session ended.
// Run with: scripts/run.py idp-browser --idp keycloak
import { chromium } from "playwright-core";
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
const root = process.cwd(),
  local = process.env.IMPACT_TEST_LOCAL,
  base = process.env.IMPACT_BASE_URL,
  idpFile = process.env.IMPACT_IDP_FILE;
if (!local || !base || !idpFile)
  throw Error("Use scripts/run.py idp-browser --idp keycloak");
const idp = JSON.parse(await fs.readFile(idpFile, "utf8"));
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
const results = [],
  errors = [],
  pages = [];
const used = new Set();
// RFC 6238 (HMAC-SHA1, 30 s, 6 digits) over the UTF-8 bytes of Keycloak's stored secret; never
// submits the same step twice, because the realm refuses code reuse.
async function totp(secret) {
  for (;;) {
    const now = Math.floor(Date.now() / 30000);
    const step = [now, now + 1].find((s) => !used.has(s));
    if (step !== undefined) {
      used.add(step);
      const counter = Buffer.alloc(8);
      counter.writeBigUInt64BE(BigInt(step));
      const mac = crypto
        .createHmac("sha1", Buffer.from(secret, "utf8"))
        .update(counter)
        .digest();
      const offset = mac[mac.length - 1] & 15;
      return String((mac.readUInt32BE(offset) & 0x7fffffff) % 1000000).padStart(
        6,
        "0",
      );
    }
    await new Promise((r) => setTimeout(r, 30000 - (Date.now() % 30000) + 500));
  }
}
async function test(label, fn) {
  await fn();
  results.push({ name: label, status: "passed" });
  console.log("PASS " + label);
}
try {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
  });
  const page = await context.newPage();
  pages.push(page);
  page.setDefaultTimeout(20000);
  page.on("pageerror", (e) => errors.push(e.message));
  const owner = idp.users.owner;
  await test("Sign-in goes through the provider with a TOTP step", async () => {
    await page.goto(base);
    await page
      .getByRole("link", { name: "Continue with your organisation →" })
      .click();
    await page.waitForURL((u) => u.toString().startsWith(idp.base_url));
    await page.locator("#username").fill(owner.username);
    await page.locator("#password").fill(owner.password);
    await page.locator("#kc-login").click();
    await page.locator("#otp").fill(await totp(owner.totp_secret));
    await page.locator("#kc-login").click();
    await page.waitForURL((u) => u.toString().startsWith(base));
    await page.getByRole("button", { name: "Sign out" }).first().waitFor();
    const me = await page.evaluate(async () =>
      (await fetch("/auth/me")).json(),
    );
    assert.ok(me.identity_id);
  });
  await test("Sign-out ends the platform and the provider session", async () => {
    await page.getByRole("button", { name: "Sign out" }).first().click();
    await page.waitForURL((u) => u.toString() === base + "/");
    await page
      .getByRole("link", { name: "Continue with your organisation →" })
      .waitFor();
    const status = await page.evaluate(
      async () => (await fetch("/auth/me")).status,
    );
    assert.equal(status, 401);
    // A new sign-in asks the provider for credentials again.
    await page
      .getByRole("link", { name: "Continue with your organisation →" })
      .click();
    await page.waitForURL((u) => u.toString().startsWith(idp.base_url));
    await page.locator("#username").waitFor();
  });
  assert.deepEqual(errors, []);
  await fs.writeFile(
    "docs/evidence/idp-browser-tests.json",
    JSON.stringify(
      {
        engine: "Chromium",
        identity_provider: "Keycloak " + idp.keycloak_version,
        results,
        uncaughtErrors: errors,
      },
      null,
      2,
    ),
  );
} catch (e) {
  for (let i = 0; i < pages.length; i++)
    await pages[i].screenshot({
      path: path.join(local, `idp-${i}-failure.png`),
      fullPage: true,
    });
  throw e;
} finally {
  await browser.close();
}
