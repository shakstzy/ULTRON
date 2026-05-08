// Per-person markdown writer for LinkedIn deposits.
//
// Writes to RAW_DIR (workspaces/<ws>/raw/linkedin/<slug>-linkedin.md) using the
// ULTRON workspace raw ingest standard:
//   source / workspace / ingested_at / ingest_version / content_hash /
//   provider_modified_at  (header)
//   then LinkedIn-specific fields, plus an `entity:` wikilink up to the
//   _global/entities/people/<slug>.md stub for graphify route-resolution.
//
// Body sections:
//   ## Profile snapshot   — innerText of LinkedIn <main> (overwritten on re-pull)
//   ## Threads            — append-only event log, dedup'd on (day, direction, text)
//
// Cross-source dedup: BEFORE writing, we read the target file's frontmatter; if
// `redirect_to:` is present we swap the slug to canonical and write THERE
// instead. This is what makes `/alias` durable — future ingests honor the
// merge automatically rather than re-creating the duplicate.
//
// Provides:
//   upsertPerson({ slug, frontmatter, profileSnapshot, threadEvent })
//   upsertGlobalPersonStub({ slug, name, linkedinPublicId, linkedinUrl })
//     -> creates a thin _global/entities/people/<slug>.md stub if absent.
//        Idempotent first-write-wins; never modifies an existing stub
//        (contacts-sync owns the stub when it has one).

import { promises as fs } from "node:fs";
import { join, dirname } from "node:path";
import { createHash } from "node:crypto";
import lockfile from "proper-lockfile";
import { RAW_DIR, WORKSPACE, ULTRON_ROOT } from "./paths.mjs";
import { rawFilename } from "./slug.mjs";

const FRONTMATTER_RE = /^---\n([\s\S]*?)\n---\n?/;
const INGEST_VERSION = 1;

const GLOBAL_PEOPLE_DIR = join(ULTRON_ROOT, "_global/entities/people");

async function ensureRawDir() {
  await fs.mkdir(RAW_DIR, { recursive: true });
}

function parseFrontmatter(text) {
  const m = text.match(FRONTMATTER_RE);
  if (!m) return { frontmatter: {}, body: text };
  const frontmatter = parseYamlFlat(m[1]);
  const body = text.slice(m[0].length);
  return { frontmatter, body };
}

// Tiny YAML-flat parser. Handles only `key: value`, `key: "string"`, `key: [a, b]`. No nesting.
// We control the writer for raw deposits so this is safe. For nested global-stub YAML
// (written by contacts-sync), we only check for redirect_to and never round-trip.
function parseYamlFlat(yaml) {
  const out = {};
  for (const line of yaml.split("\n")) {
    const m = line.match(/^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$/);
    if (!m) continue;
    const key = m[1];
    let val = m[2].trim();
    if (val.startsWith("[") && val.endsWith("]")) {
      val = val.slice(1, -1)
        .split(",")
        .map((s) => s.trim().replace(/^"(.*)"$/, "$1"))
        .filter(Boolean);
    } else if (val.startsWith('"') && val.endsWith('"')) {
      val = val.slice(1, -1);
    } else if (val === "true") val = true;
    else if (val === "false") val = false;
    else if (val === "null" || val === "") val = null;
    out[key] = val;
  }
  return out;
}

function renderFrontmatter(fm) {
  const lines = ["---"];
  for (const [k, v] of Object.entries(fm)) {
    if (v === null || v === undefined) continue;
    if (Array.isArray(v)) {
      lines.push(`${k}: [${v.map((x) => JSON.stringify(String(x))).join(", ")}]`);
    } else if (typeof v === "boolean" || typeof v === "number") {
      lines.push(`${k}: ${v}`);
    } else if (typeof v === "string" && /[:#@\s"']|^\d/.test(v)) {
      lines.push(`${k}: ${JSON.stringify(v)}`);
    } else {
      lines.push(`${k}: ${v}`);
    }
  }
  lines.push("---", "");
  return lines.join("\n");
}

function nowISO() { return new Date().toISOString(); }

function sha256Hex(text) {
  return "sha256:" + createHash("sha256").update(text, "utf8").digest("hex");
}

// Resolve a slug against a redirect stub at the would-be target path. If the
// existing file's frontmatter has `redirect_to:` set, we follow the redirect
// (one hop only — chained aliases are flagged but not resolved automatically;
// run `/alias` to compact).
async function resolveCanonicalSlug(slug) {
  const file = join(RAW_DIR, rawFilename(slug));
  let text;
  try {
    text = await fs.readFile(file, "utf8");
  } catch {
    return slug;
  }
  const { frontmatter } = parseFrontmatter(text);
  if (frontmatter.redirect_to && typeof frontmatter.redirect_to === "string") {
    return frontmatter.redirect_to;
  }
  return slug;
}

function mergeFrontmatter(existing, incoming, slug) {
  const merged = { ...existing, ...stripNulls(incoming) };
  // previous_slugs accumulates if slug changed
  const prev = Array.isArray(existing.previous_slugs) ? existing.previous_slugs : [];
  if (existing.slug && existing.slug !== slug && !prev.includes(existing.slug)) {
    merged.previous_slugs = [...prev, existing.slug];
  } else {
    merged.previous_slugs = prev;
  }
  merged.slug = slug;
  merged.first_seen = existing.first_seen ?? incoming.first_seen ?? nowISO();
  merged.last_action_at = nowISO();
  return merged;
}

function stripNulls(obj) {
  return Object.fromEntries(Object.entries(obj).filter(([, v]) => v !== null && v !== undefined && v !== ""));
}

// Apply the standard workspace raw ingest header on top of caller-supplied
// LinkedIn-specific fields. Header is always recomputed at write time.
function applyIngestHeader(fm, slug, providerModifiedAt, body) {
  const ts = nowISO();
  return {
    source: "linkedin",
    workspace: WORKSPACE,
    ingested_at: ts,
    ingest_version: INGEST_VERSION,
    content_hash: sha256Hex(body),
    provider_modified_at: providerModifiedAt ?? ts,
    entity: `[[_global/entities/people/${slug}]]`,
    ...fm,
  };
}

export async function upsertPerson({ slug, frontmatter = {}, profileSnapshot = null, threadEvent = null }) {
  if (!slug) throw new Error("upsertPerson: slug required");

  // Honor redirect stubs left by /alias — write to canonical, not the deprecated slug.
  const canonicalSlug = await resolveCanonicalSlug(slug);

  await ensureRawDir();
  const file = join(RAW_DIR, rawFilename(canonicalSlug));

  // Lock target. proper-lockfile requires the path to exist; touch it first.
  try {
    await fs.access(file);
  } catch {
    await fs.writeFile(file, "", "utf8");
  }
  const release = await lockfile.lock(file, { retries: { retries: 8, minTimeout: 50 } });
  try {
    const existingText = await fs.readFile(file, "utf8");
    const { frontmatter: existingFm, body: existingBody } = existingText
      ? parseFrontmatter(existingText)
      : { frontmatter: {}, body: "" };

    let body = existingBody.trim();
    if (profileSnapshot) {
      body = upsertSection(body, "Profile snapshot", profileSnapshot);
    }
    if (threadEvent) {
      body = appendThreadEvent(body, threadEvent);
    }

    const mergedFm = mergeFrontmatter(existingFm, frontmatter, canonicalSlug);
    const headerFm = applyIngestHeader(mergedFm, canonicalSlug, frontmatter.provider_modified_at, body);

    const finalText = renderFrontmatter(headerFm) + (body ? body + "\n" : "");
    await atomicWrite(file, finalText);
  } finally {
    await release();
  }
  return file;
}

// Thin global person stub creator. First-write-wins and idempotent: if a
// stub already exists at the target path (e.g. contacts-sync wrote one),
// we leave it alone. The caller can still see the existing file by reading
// the returned path.
export async function upsertGlobalPersonStub({ slug, name, linkedinPublicId, linkedinUrl } = {}) {
  if (!slug) throw new Error("upsertGlobalPersonStub: slug required");
  await fs.mkdir(GLOBAL_PEOPLE_DIR, { recursive: true });
  const file = join(GLOBAL_PEOPLE_DIR, `${slug}.md`);
  try {
    await fs.access(file);
    return { file, created: false };
  } catch { /* missing; create below */ }

  const ts = nowISO();
  const title = name || slug;
  const safeTitle = JSON.stringify(title);
  const body =
    `---\n` +
    `source: linkedin\n` +
    `workspace: _global\n` +
    `ingested_at: ${ts}\n` +
    `ingest_version: ${INGEST_VERSION}\n` +
    `content_hash: ${sha256Hex(title)}\n` +
    `provider_modified_at: ${ts}\n` +
    `\n` +
    `title: ${safeTitle}\n` +
    `slug: ${slug}\n` +
    `type: person\n` +
    `canonical_uri: lifeos:_global/entities/people/${slug}\n` +
    `aliases: []\n` +
    `identifiers:\n` +
    `  email: []\n` +
    `  phone: []\n` +
    `  slack: []\n` +
    `  linkedin: [${linkedinPublicId ? JSON.stringify(linkedinPublicId) : ""}]\n` +
    `last_synced: ${ts}\n` +
    `entity_status: provisional\n` +
    `global: true\n` +
    `---\n\n` +
    `# ${title}\n\n` +
    (linkedinUrl ? `LinkedIn: ${linkedinUrl}\n\n` : "") +
    `## Notes\n\n` +
    `_Auto-created from LinkedIn ingest. Promote with \`/promote-entity\` once the relationship matures._\n`;
  await atomicWrite(file, body);
  return { file, created: true };
}

async function atomicWrite(file, text) {
  await fs.mkdir(dirname(file), { recursive: true });
  const tmp = file + ".tmp";
  await fs.writeFile(tmp, text, "utf8");
  await fs.rename(tmp, file);
}

function upsertSection(body, heading, content) {
  const re = new RegExp(`(^|\\n)## ${escapeRegex(heading)}\\n[\\s\\S]*?(?=\\n## |$)`, "");
  const block = `\n## ${heading}\n${content.trim()}\n`;
  if (re.test(body)) return body.replace(re, block);
  return body + block;
}

function appendThreadEvent(body, event) {
  // event = { ts: ISO, direction: "outbound"|"inbound"|"system", text: string }
  // Dedupe: skip if a same-day same-direction same-text line already exists.
  const heading = "## Threads";
  const ts = event.ts ?? nowISO();
  const dayBucket = ts.slice(0, 10); // YYYY-MM-DD
  const cleanText = event.text.replace(/\s+/g, " ").trim();
  const line = `### ${ts} — ${event.direction}: ${cleanText}`;
  if (body.includes(heading)) {
    const re = new RegExp(`(\\n## Threads\\n[\\s\\S]*?)(?=\\n## |$)`, "");
    const match = body.match(re);
    if (match) {
      const block = match[0];
      const dupRe = new RegExp(
        `^### ${escapeRegex(dayBucket)}[^\\n]*\\s+\\u2014\\s+${escapeRegex(event.direction)}:\\s+${escapeRegex(cleanText)}\\s*$`,
        "m"
      );
      if (dupRe.test(block)) return body; // already present, no-op
    }
    return body.replace(re, (m) => m.trimEnd() + "\n" + line);
  }
  return body + `\n${heading}\n${line}\n`;
}

function escapeRegex(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
