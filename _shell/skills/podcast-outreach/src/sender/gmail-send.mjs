// Compose + send via gog. Returns { thread_id, message_id }. On dry-run,
// writes a render-only artifact to ~/.ultron/podcast-outreach/dry-run/<ts>/
// and returns synthetic ids.
//
// We use `gog gmail messages send` with --to/--subject/--body-stdin so the
// body never has to be shell-escaped.

import fs from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";
import { ACCOUNT_EMAIL, DRY_RUN_DIR } from "../runtime/paths.mjs";
import { audit, dim, ok } from "../runtime/logger.mjs";

function ts() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function gogSpawn(args, input) {
  return new Promise((resolve, reject) => {
    const child = spawn("gog", args, { stdio: ["pipe", "pipe", "pipe"] });
    let stdout = "", stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolve({ stdout, stderr, code });
      else {
        const e = new Error(`gog ${args.join(" ")} failed (${code}): ${stderr.trim() || stdout.trim()}`);
        e.code = "GOG_FAIL";
        e.exitCode = code;
        e.stderr = stderr;
        reject(e);
      }
    });
    if (input != null) {
      child.stdin.write(input);
      child.stdin.end();
    } else {
      child.stdin.end();
    }
  });
}

export async function sendEmail({ to, subject, body, send }) {
  if (send) {
    // `gog send` (alias for `gog gmail send`). Body via stdin avoids any shell
    // expansion / argv-length issues on long bodies. `--body-file -` reads stdin.
    const args = [
      "-a", ACCOUNT_EMAIL,
      "send",
      "--to", to,
      "--subject", subject,
      "--body-file", "-",
      "-j",
    ];
    const { stdout } = await gogSpawn(args, body);
    let parsed;
    try {
      parsed = JSON.parse(stdout);
    } catch {
      throw new Error(`unable to parse gog gmail send output: ${stdout.slice(0, 200)}`);
    }
    const out = {
      thread_id: parsed.threadId || parsed.thread_id || parsed.id,
      message_id: parsed.id || parsed.messageId,
    };
    await audit("gmail-send", { to, subject, ...out });
    ok(`sent: ${to} (thread=${out.thread_id})`);
    return out;
  }

  // Dry-run path — write artifact, return synthetic ids.
  const dir = path.join(DRY_RUN_DIR, ts());
  await fs.mkdir(dir, { recursive: true });
  const artifact = {
    to,
    from: ACCOUNT_EMAIL,
    subject,
    body,
    rendered_at: new Date().toISOString(),
  };
  await fs.writeFile(
    path.join(dir, "email.json"),
    JSON.stringify(artifact, null, 2),
    "utf8",
  );
  await fs.writeFile(path.join(dir, "body.txt"), body, "utf8");
  await audit("gmail-send-dry-run", { to, subject, dir });
  dim(`[dry-run] would send to ${to}; rendered → ${dir}`);
  return { thread_id: `dry-run-${ts()}`, message_id: `dry-run-${ts()}` };
}

// Used by reply scanner. Returns array of thread objects with `messages`
// summary (from + date + snippet). Limits to recent windows for speed.
export async function searchThreadsByQuery(query, { limit = 100 } = {}) {
  // `gog gmail search` takes the query as positional args (Gmail query
  // syntax). `--max` controls page size; we pass it explicitly because gog
  // defaults to 10.
  const args = [
    "-a", ACCOUNT_EMAIL,
    "gmail", "search",
    query,
    "--max", String(limit),
    "-j",
  ];
  const { stdout } = await gogSpawn(args);
  let parsed;
  try {
    parsed = JSON.parse(stdout);
  } catch {
    throw new Error(`unable to parse gog gmail search output: ${stdout.slice(0, 200)}`);
  }
  return Array.isArray(parsed) ? parsed : (parsed.threads || []);
}

export async function getThread(threadId) {
  const args = [
    "-a", ACCOUNT_EMAIL,
    "gmail", "thread", "get",
    threadId,
    "-j",
  ];
  const { stdout } = await gogSpawn(args);
  return JSON.parse(stdout);
}

export async function searchSentToEmail(email) {
  return searchThreadsByQuery(`to:${email} from:me`, { limit: 5 });
}
