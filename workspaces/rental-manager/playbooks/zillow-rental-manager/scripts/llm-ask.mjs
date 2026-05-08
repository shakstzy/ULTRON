// llm-ask.mjs — single LLM-call helper for the playbook.
//
// Adithya's stated preference: claude for writing tasks, gemini only for
// visual. We try claude -p --model sonnet first; if it fails (auth lapse,
// transient error), we fall back to cloud-llm's ask_text (gemini-first
// internally with claude-sonnet last-resort). This keeps the cron alive
// even when claude CLI auth has expired.
//
// All drafts include the engine name so the user can audit the mix
// post-hoc. If the eventual ratio shifts heavily to gemini, that's a
// signal to refresh claude auth.

import { spawnSync } from 'node:child_process';

const CLOUD_LLM_DIR = '/Users/shakstzy/ULTRON/_shell/skills/cloud-llm';

function tryClaudeCli(prompt, { timeoutMs }) {
  const r = spawnSync('claude', ['-p', '--model', 'sonnet'], {
    input: prompt,
    encoding: 'utf8',
    timeout: timeoutMs,
    maxBuffer: 16 * 1024 * 1024
  });
  if (r.status !== 0 || !r.stdout) {
    const detail = (r.stderr || r.error?.message || `exit=${r.status}`).slice(0, 500);
    return { ok: false, error: `claude-cli: ${detail}` };
  }
  return { ok: true, engine: 'claude-sonnet', text: r.stdout.trim() };
}

function tryCloudLlm(prompt, { timeoutMs }) {
  // cloud-llm is a Python module. Shell out via python3 -c.
  const py = `
import sys, json
sys.path.insert(0, "${CLOUD_LLM_DIR}")
from client import ask_text, CloudLLMUnreachable
try:
    res = ask_text(${JSON.stringify(prompt)})
    sys.stdout.write(json.dumps({"ok": True, "engine": res["engine"], "account": res.get("account"), "text": res["output"]}))
except CloudLLMUnreachable as e:
    sys.stdout.write(json.dumps({"ok": False, "error": "cloud-llm-unreachable: " + str(e)}))
except Exception as e:
    sys.stdout.write(json.dumps({"ok": False, "error": "cloud-llm: " + str(e)}))
`;
  const r = spawnSync('python3', ['-c', py], {
    encoding: 'utf8',
    timeout: timeoutMs,
    maxBuffer: 16 * 1024 * 1024
  });
  if (r.status !== 0) {
    return { ok: false, error: `python3 exit=${r.status}: ${(r.stderr || '').slice(0, 300)}` };
  }
  try {
    const out = JSON.parse(r.stdout || '{}');
    if (out.ok) return { ok: true, engine: out.engine, text: out.text, account: out.account };
    return { ok: false, error: out.error || 'cloud-llm unknown error' };
  } catch (e) {
    return { ok: false, error: `cloud-llm bad json: ${(r.stdout || '').slice(0, 200)}` };
  }
}

/**
 * Ask the LLM. Tries claude CLI first, falls back to cloud-llm (gemini Pro
 * cycling, claude-sonnet last-resort). Throws on total failure.
 *
 * @param {string} prompt
 * @param {object} [opts]
 * @param {number} [opts.timeoutMs=180000]
 * @returns {{engine: string, text: string, account?: string, fallback_used: boolean}}
 */
export function llmAsk(prompt, { timeoutMs = 180_000 } = {}) {
  const claudeResult = tryClaudeCli(prompt, { timeoutMs });
  if (claudeResult.ok) {
    return { engine: claudeResult.engine, text: claudeResult.text, fallback_used: false };
  }
  // Claude failed. Log + fall through.
  const claudeError = claudeResult.error;
  const cloudResult = tryCloudLlm(prompt, { timeoutMs });
  if (cloudResult.ok) {
    return {
      engine: cloudResult.engine,
      text: cloudResult.text,
      account: cloudResult.account,
      fallback_used: true,
      claude_error: claudeError
    };
  }
  // Both paths down — halt loud.
  throw new Error(`llm-ask: claude failed (${claudeError}); cloud-llm failed (${cloudResult.error})`);
}
