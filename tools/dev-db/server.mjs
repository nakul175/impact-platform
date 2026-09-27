import { PGlite } from "@electric-sql/pglite";
import { PGLiteSocketServer } from "@electric-sql/pglite-socket";
import path from "node:path";
import { mkdir, readdir, readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
const dir = process.env.IMPACT_DEV_DATA || path.resolve(".local/development");
await mkdir(path.dirname(dir), { recursive: true });
// Disposable qualification uses memory storage: filesystem-backed PGlite showed
// intermittent EOF/cached-page inconsistencies in the managed execution filesystem.
const ephemeral = process.env.IMPACT_DEV_EPHEMERAL === "1";
let db = await PGlite.create(ephemeral ? undefined : dir);
if (
  !(await db.query("SELECT 1 FROM pg_database WHERE datname='impact_dev'")).rows
    .length
)
  await db.exec("CREATE DATABASE impact_dev");
const initialData = ephemeral ? await db.dumpDataDir() : undefined;
await db.close();
db = ephemeral
  ? await PGlite.create({ database: "impact_dev", loadDataDir: initialData })
  : await PGlite.create(dir, { database: "impact_dev" });
if (process.env.IMPACT_DEV_BOOTSTRAP === "1") {
  const present = (
    await db.query("SELECT to_regclass('impact.schema_migration') AS present")
  ).rows[0].present;
  const applied = present
    ? (await db.query("SELECT version,sha256 FROM impact.schema_migration"))
        .rows
    : [];
  for (const file of (await readdir("infrastructure/migrations"))
    .filter((x) => x.endsWith(".sql"))
    .sort()) {
    const bytes = await readFile("infrastructure/migrations/" + file),
      version = Number(file.slice(0, 4)),
      sha = createHash("sha256").update(bytes).digest("hex"),
      old = applied.find((x) => x.version === version);
    if (old) {
      if (old.sha256 !== sha)
        throw Error("Migration checksum changed: " + file);
      continue;
    }
    await db.exec(
      "BEGIN;" +
        bytes
          .toString()
          .replace(/^BEGIN;\s*$/m, "")
          .replace(/COMMIT;\s*$/, ""),
    );
    await db.query(
      "INSERT INTO impact.schema_migration(version,sha256) VALUES($1,$2)",
      [version, sha],
    );
    await db.exec("COMMIT");
  }
  if (
    !(await db.query("SELECT 1 FROM impact.tenant_root LIMIT 1")).rows.length
  ) {
    await db.exec("SELECT set_config('impact.allow_fixtures','true',false)");
    await db.exec(await readFile("specification/fixtures/seed.sql", "utf8"));
  }
}
// Unauthenticated development socket: loopback only. Never deploy this service.
// PGlite returns a view into a reused wire-response buffer. Copy it before any
// filesystem await and serialize protocol packets across connection handoffs.
// Socket event callbacks are async but EventEmitter does not await them.
let protocolTail = Promise.resolve();
db.execProtocolRaw = (message, { syncToFs = true } = {}) => {
  const next = protocolTail.then(async () => {
    const response = db.execProtocolRawSync(message).slice();
    if (syncToFs) await db.syncToFs();
    return response;
  });
  protocolTail = next.catch(() => {});
  return next;
};
const server = new PGLiteSocketServer({ db, host: "127.0.0.1", port: 55432 });
await server.start();
console.log(
  JSON.stringify({
    status: "ready",
    engine: "PGlite",
    postgres: (await db.query("SHOW server_version")).rows[0].server_version,
  }),
);
let closing = false;
async function stop() {
  if (closing) return;
  closing = true;
  await server.stop();
  await db.close();
  process.exit(0);
}
process.on("SIGTERM", stop);
process.on("SIGINT", stop);
