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
//
// pglite-socket hands every TCP read to execProtocolRaw as it arrives, but PGlite's
// execProtocolRawSync treats its input as whole protocol messages (it passes the buffer's
// length and first byte to the backend). A message larger than one read, or one the kernel
// delivers in two reads (a rendered DOCX bound as a parameter is about 40 KB), would reach
// PGlite as two fragments, and the second fragment is parsed as a new message from a byte in
// the middle of the first: the backend fails and the connection is closed. That happened in
// CI (build 0.25.0 integration, test_report_exports: "server closed the connection
// unexpectedly" while inserting a DOCX artifact, after which every connection failed).
// So the bytes are framed here: only complete messages are passed on, an incomplete tail is
// kept until the next read, and the framing state is reset (in protocol order) whenever a
// new connection is attached.
const STARTUP_CODES = new Set([196608, 80877102, 80877103, 80877104]);
let pending = new Uint8Array(0);
function int32(bytes, at) {
  return (
    ((bytes[at] << 24) |
      (bytes[at + 1] << 16) |
      (bytes[at + 2] << 8) |
      bytes[at + 3]) >>>
    0
  );
}
// The length of the longest prefix of `bytes` made of complete protocol messages. A message
// with no type byte (StartupMessage, SSLRequest, CancelRequest, GSSENCRequest) can only open
// a connection's byte stream; every later message is a type byte and a 4-byte length.
function completePrefix(bytes, atStreamStart) {
  let offset = 0;
  if (atStreamStart && bytes.length > 0 && bytes[0] === 0) {
    if (bytes.length < 8) return 0;
    const length = int32(bytes, 0);
    if (!STARTUP_CODES.has(int32(bytes, 4)) || length < 8) return bytes.length;
    if (bytes.length < length) return 0;
    offset = length;
  }
  while (bytes.length - offset >= 5) {
    const total = 1 + int32(bytes, offset + 1);
    if (total < 5 || bytes.length - offset < total) break;
    offset += total;
  }
  return offset;
}
let streamStart = true;
let protocolTail = Promise.resolve();
db.execProtocolRaw = (message, { syncToFs = true } = {}) => {
  const next = protocolTail.then(async () => {
    const bytes = new Uint8Array(pending.length + message.length);
    bytes.set(pending, 0);
    bytes.set(message, pending.length);
    const complete = completePrefix(bytes, streamStart);
    pending = bytes.slice(complete);
    if (complete === 0) return new Uint8Array(0);
    streamStart = false;
    const response = db
      .execProtocolRawSync(bytes.subarray(0, complete))
      .slice();
    if (syncToFs) await db.syncToFs();
    return response;
  });
  protocolTail = next.catch(() => {});
  return next;
};
function newStream() {
  protocolTail = protocolTail.then(() => {
    pending = new Uint8Array(0);
    streamStart = true;
  });
}
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
// A connection is attached only once the previous one has detached; its bytes start a new
// stream (dispatched before its first read is handled).
server.addEventListener("connection", newStream);
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
