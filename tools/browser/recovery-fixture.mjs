import assert from "node:assert/strict";

export async function approveRecoveryContact(base, fixture, tenant) {
  async function command(actor, path, data, revision) {
    const response = await fetch(base + path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + process.env[fixture.actors[actor].token_env],
      },
      body: JSON.stringify({
        operation_id: crypto.randomUUID(),
        expected_revision: revision,
        data,
      }),
    });
    const result = await response.json();
    assert.equal(response.status, 200, JSON.stringify(result));
    return result;
  }
  let row = await command(
    "author",
    `/v1/platform/tenants/${tenant.tenant_id}/recovery-contacts`,
    {
      nominee_identity_id: fixture.actors.partner.identity_id,
      expected_contact_revision: tenant.recovery_contact.revision_id,
      expires_at: new Date(Date.now() + 60 * 86400000).toISOString(),
      reason: "Synthetic browser recovery contact",
    },
    tenant.revision_id,
  );
  const path = `/v1/platform/recovery-contacts/${row.contact_id}/actions/`;
  row = await command(
    "partner",
    path + "verify",
    { reason: "Confirm registered identity" },
    row.revision_id,
  );
  return command(
    "admin",
    path + "approve",
    { reason: "Independent review" },
    row.revision_id,
  );
}
