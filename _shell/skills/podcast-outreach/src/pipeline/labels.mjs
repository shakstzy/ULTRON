// Gmail label management via gog CLI. Two labels nested under "Podcast/":
//   Podcast/podcast - archived  — every send lands here
//   Podcast/podcast - priority  — replies get promoted here
//
// `ensureLabels` is idempotent. `applyLabel`/`removeLabel`/`relabel` are
// dry-run aware — pass send=false to no-op with a console line.

import { spawn } from "node:child_process";
import { ACCOUNT_EMAIL, LABEL_ARCHIVED, LABEL_PRIORITY } from "../runtime/paths.mjs";
import { audit, dim, info, ok, warn } from "../runtime/logger.mjs";

function gog(args, { input } = {}) {
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
        e.stdout = stdout;
        reject(e);
      }
    });
    if (input) {
      child.stdin.write(input);
      child.stdin.end();
    } else {
      child.stdin.end();
    }
  });
}

export async function listLabels() {
  const { stdout } = await gog(["-a", ACCOUNT_EMAIL, "gmail", "labels", "list", "-j"]);
  let parsed;
  try {
    parsed = JSON.parse(stdout);
  } catch {
    throw new Error(`unable to parse gog gmail labels list output: ${stdout.slice(0, 200)}`);
  }
  const arr = Array.isArray(parsed) ? parsed : (parsed.labels || []);
  return arr;
}

export async function findLabel(name) {
  const labels = await listLabels();
  return labels.find((l) => (l.name || "") === name) || null;
}

async function createLabel(name, { send }) {
  if (!send) {
    info(`[dry-run] would create label: ${name}`);
    await audit("label-create-dry-run", { name });
    return { id: `dry-run-${name}`, name };
  }
  const { stdout } = await gog([
    "-a", ACCOUNT_EMAIL,
    "gmail", "labels", "create",
    "--name", name,
    "-j",
  ]);
  let parsed;
  try {
    parsed = JSON.parse(stdout);
  } catch {
    throw new Error(`unable to parse label-create output: ${stdout.slice(0, 200)}`);
  }
  await audit("label-create", { name, id: parsed.id });
  ok(`created label: ${name} (${parsed.id})`);
  return parsed;
}

export async function ensureLabels({ send } = { send: false }) {
  const desired = [LABEL_ARCHIVED, LABEL_PRIORITY];
  let labels;
  try {
    labels = await listLabels();
  } catch (e) {
    if (e.stderr && /invalid_grant|expired|revoked/i.test(e.stderr)) {
      warn(`gog auth expired for ${ACCOUNT_EMAIL}. Run: gog auth login ${ACCOUNT_EMAIL}`);
    }
    throw e;
  }
  const out = {};
  for (const name of desired) {
    const found = labels.find((l) => (l.name || "") === name);
    if (found) {
      dim(`label exists: ${name} (${found.id})`);
      out[name] = found;
    } else {
      out[name] = await createLabel(name, { send });
      // Re-fetch list so subsequent iterations see the new label
      if (send) labels = await listLabels();
    }
  }
  return out;
}

export async function applyLabelToThread(threadId, labelId, { send } = { send: false }) {
  if (!send) {
    info(`[dry-run] would apply label ${labelId} to thread ${threadId}`);
    return;
  }
  await gog([
    "-a", ACCOUNT_EMAIL,
    "gmail", "threads", "modify",
    threadId,
    "--add-label", labelId,
  ]);
  await audit("label-apply", { threadId, labelId });
}

export async function removeLabelFromThread(threadId, labelId, { send } = { send: false }) {
  if (!send) {
    info(`[dry-run] would remove label ${labelId} from thread ${threadId}`);
    return;
  }
  await gog([
    "-a", ACCOUNT_EMAIL,
    "gmail", "threads", "modify",
    threadId,
    "--remove-label", labelId,
  ]);
  await audit("label-remove", { threadId, labelId });
}

export async function markThreadUnread(threadId, { send } = { send: false }) {
  if (!send) {
    info(`[dry-run] would mark thread ${threadId} unread`);
    return;
  }
  await gog([
    "-a", ACCOUNT_EMAIL,
    "gmail", "threads", "modify",
    threadId,
    "--add-label", "UNREAD",
  ]);
  await audit("mark-unread", { threadId });
}

export { gog };
