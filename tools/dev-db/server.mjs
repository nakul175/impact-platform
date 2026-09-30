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
// IMPACT_DEV_DB_PORT selects the loopback port: 55432 by default (make dev), 0 lets the
// operating system choose a free one (the test and browser runners), so two runners or an
// orphaned server never collide. The one JSON status line below carries the actual port;
// scripts/run.py parses that line and builds every connection string from it.
const requestedPort = Number(process.env.IMPACT_DEV_DB_PORT ?? "55432");
if (
  !Number.isInteger(requestedPort) ||
  requestedPort < 0 ||
  requestedPort > 65535
) {
  console.log(
    JSON.stringify({
      status: "failed",
      error: "IMPACT_DEV_DB_PORT must be an integer from 0 to 65535",
    }),
  );
  process.exit(2);
}
const server = new PGLiteSocketServer({
  db,
  host: "127.0.0.1",
  port: requestedPort,
});
let listeningPort = null;
server.addEventListener("listening", (event) => {
  listeningPort = event.detail?.port ?? null;
});
try {
  await server.start();
} catch (error) {
  console.log(
    JSON.stringify({
      status: "failed",
      error: String(error?.message ?? error),
    }),
  );
  await db.close();
  process.exit(1);
}
console.log(
  JSON.stringify({
    status: "ready",
    port: listeningPort ?? server.port,
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
