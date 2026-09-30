// Browser modes start no worker process: a check that needs one runs `python -m impact_api.worker
// --once` against the run's own worker.json (synthetic mail sink in the run directory) and reads
// the sink. The worker gets only its configuration file, never the API's environment.
import { execFileSync } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";

export function runWorkerOnce(local, workerId) {
  const output = execFileSync(
    path.resolve(".venv/bin/python"),
    ["-m", "impact_api.worker", "--once", "--worker-id", workerId],
    {
      env: {
        PATH: process.env.PATH,
        PYTHONPATH: path.resolve("apps/api"),
        IMPACT_WORKER_CONFIG_FILE: path.join(local, "worker.json"),
      },
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    },
  );
  return JSON.parse(output.trim().split("\n").pop());
}

export async function sinkMessages(local) {
  try {
    const text = await fs.readFile(
      path.join(local, "synthetic-mail.jsonl"),
      "utf8",
    );
    return text
      .split("\n")
      .filter(Boolean)
      .map((line) => JSON.parse(line));
  } catch {
    return [];
  }
}
