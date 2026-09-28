import { PGlite } from "@electric-sql/pglite";
import { PGLiteSocketServer } from "@electric-sql/pglite-socket";
import path from "node:path";
import { mkdir } from "node:fs/promises";
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
// This process only serves the database. Migrations and the fixture are applied
// over the wire by scripts/migrate.py, the single migration runner, exactly as on
// native PostgreSQL; nothing here interprets migration files.
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
