// Draft via the cloud-llm skill (gemini cycle, claude -p fallback). Routing
// drafting through cloud-llm spreads load across Adithya's Workspace AI Ultra
// account first, only burning his Claude Max weekly cap when gemini is
// exhausted. On Bumble, the man almost never sends the opener
// (women-message-first + Opening Moves). Default intent is `reply`.

import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { loadVoice } from "./voice-loader.mjs";
import { lintDraft } from "./voice-lint.mjs";

const CLOUD_LLM_DIR = "/Users/shakstzy/ULTRON/_shell/skills/cloud-llm";

class CloudLLMUnreachable extends Error {}

// Shells out to ULTRON's cloud-llm Python client. Returns { engine, account, output }.
function askText(prompt) {
  const wrapper = `
import sys, json
sys.path.insert(0, "${CLOUD_LLM_DIR}")
from client import ask_text, CloudLLMUnreachable
prompt = sys.stdin.read()
try:
    result = ask_text(prompt)
    print(json.dumps(result))
except CloudLLMUnreachable as e:
    print(json.dumps({"_unreachable": str(e)}))
    sys.exit(2)
`;
  return new Promise((resolveP, rejectP) => {
    const p = spawn("python3", ["-c", wrapper]);
    p.stdin.write(prompt);
    p.stdin.end();
    let out = "", err = "";
    p.stdout.on("data", d => out += d);
    p.stderr.on("data", d => err += d);
    p.on("close", code => {
      const trimmed = out.trim();
      try {
        const r = JSON.parse(trimmed);
        if (r._unreachable) return rejectP(new CloudLLMUnreachable(r._unreachable));
        if (code !== 0) return rejectP(new Error(`ask_text exit ${code}: ${err.trim() || trimmed}`));
        return resolveP(r);
      } catch (e) {
        return rejectP(new Error(`bad JSON from ask_text (exit=${code}): ${e.message}: ${trimmed.slice(0, 300)}; stderr=${err.slice(0, 300)}`));
      }
    });
  });
}

const SYSTEM = `You are drafting a single Bumble message in Adithya's voice.

Bumble context: in hetero matches, the woman either sends the first message OR sets an "Opening Move" prompt that Adithya can answer. Adithya almost never sends a cold opener. The intent is one of: reply (she sent something substantive), opening_move_response (she has an Opening Move set, no message yet), reengage (silence > 5 days, side-channel hint says she's still active elsewhere).

Output: the literal message text only. No quotes, no preamble, no explanation, no emoji unless the voice profile calls for it.

Hard constraints (rejection if violated): no em dashes, max 3 sentences, max 1 exclamation, no looks compliments, no "how was your day" variants, no formal greetings, no AI-tells.`;

function formatBasicsLifestyle(obj) {
  if (!obj || Object.keys(obj).length === 0) return "?";
  return Object.entries(obj).map(([k, v]) => `${k}=${v}`).join(", ");
}

function formatProfileDiff(diff) {
  if (!diff) return null;
  const lines = [];
  for (const [k, v] of Object.entries(diff.added || {})) lines.push(`  she ADDED ${k}: ${JSON.stringify(v)}`);
  for (const [k, { from, to }] of Object.entries(diff.changed || {})) lines.push(`  she CHANGED ${k}: was ${JSON.stringify(from)}, now ${JSON.stringify(to)}`);
  for (const [k, v] of Object.entries(diff.removed || {})) lines.push(`  she REMOVED ${k}: ${JSON.stringify(v)}`);
  return lines.length ? lines.join("\n") : null;
}

function formatPrompts(prompts) {
  if (!Array.isArray(prompts) || prompts.length === 0) return "?";
  return prompts.map(p => `    Q: ${p.q}\n    A: ${p.a}`).join("\n");
}

function formatVisual(visual) {
  if (!visual || !String(visual).trim()) return null;
  // Strip the HTML provenance comment that visualize.mjs prepends.
  return String(visual).replace(/<!--[\s\S]*?-->/g, "").trim();
}

function buildPrompt({ context, intent, voice }) {
  const diffBlock = formatProfileDiff(context.profile_diff);
  const visualBlock = formatVisual(context.visual);
  const lines = [
    SYSTEM, "",
    "## Voice profile and skills", voice, "",
    "## Now draft for this match",
    `intent: ${intent}`,
    "",
    "match profile:",
    `  name: ${context.name || "?"}`,
    `  age: ${context.age ?? "?"}`,
    `  height: ${context.height || "?"}`,
    `  bio: ${context.bio || "?"}`,
    `  looking_for: ${context.looking_for || "?"}`,
    `  opening_move: ${context.opening_move || "?"}`,
    `  jobs: ${(context.jobs || []).join(", ") || "?"}`,
    `  schools: ${(context.schools || []).join(", ") || "?"}`,
    `  lives_in: ${context.lives_in || "?"}`,
    `  hometown: ${context.hometown || "?"}`,
    `  lifestyle_badges: ${(context.lifestyle_badges || []).join(", ") || "?"}`,
    `  interests: ${(context.interests || []).join(", ") || "?"}`,
    `  basics: ${formatBasicsLifestyle(context.basics)}`,
    `  lifestyle: ${formatBasicsLifestyle(context.lifestyle)}`,
    `  prompts:`,
    `${formatPrompts(context.prompts)}`,
    "",
  ];
  if (visualBlock) {
    lines.push("visual signal from her photos (NON-FACIAL — settings, props, vibe, activities):");
    lines.push(visualBlock);
    lines.push("Use these signals to anchor the message on something specific and observable (a place, a prop, an activity, a notable_signal). NEVER reference how she looks, her body, or her face.");
    lines.push("");
  }
  if (diffBlock) {
    lines.push("PROFILE CHANGES SINCE LAST SCRAPE (recent edits she made):");
    lines.push(diffBlock);
    lines.push("If a change is recent and interesting, you MAY anchor the message on it. Don't force it.");
    lines.push("");
  }
  lines.push(
    "thread so far (oldest first; empty if no messages yet):",
    (context.thread || []).map(m => `  ${m.direction === "out" ? "you" : "her"}: ${m.text}`).join("\n") || "  (empty)",
    "",
    "side-channel signal:",
    `  ${context.imessage_summary || "(none)"}`,
    "",
    "Write the next message now. Just the message text, nothing else.",
  );
  return lines.join("\n");
}

export async function draftMessage({ context, intent }) {
  const voice = await loadVoice();
  const prompt = buildPrompt({ context, intent, voice });
  const draftId = randomUUID();

  const result = await askText(prompt);
  const text = String(result.output || "").trim().replace(/^["']|["']$/g, "");
  const lint = lintDraft(text);
  return { draftId, text, lint, intent, engine: result.engine, account: result.account };
}
