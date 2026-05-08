// Smoke tests for the template renderer. No live calls.
import { test } from "node:test";
import assert from "node:assert/strict";
import { renderEmail } from "../src/sender/template.mjs";

test("renderEmail substitutes podcast name + host first name", async () => {
  const r = await renderEmail({ podcast_name: "Pushing The Limits", host_name: "Lisa Tamati" });
  assert.match(r.body, /Hi Lisa,/);
  assert.match(r.body, /Pushing The Limits/);
  assert.equal(r.subject, "Interested in Licensing Your Podcast Library?");
  assert.equal(r.fromEmail, "adithya@eclipse.builders");
});

test("renderEmail falls back to 'there' when host_name missing", async () => {
  const r = await renderEmail({ podcast_name: "AI Insights" });
  assert.match(r.body, /Hi there,/);
  assert.match(r.body, /AI Insights/);
});

test("renderEmail strips honorifics from host first name", async () => {
  const r = await renderEmail({ podcast_name: "X", host_name: "Dr. Jane Goodall" });
  assert.match(r.body, /Hi Jane,/);
});

test("renderEmail injects recent-episode line when provided", async () => {
  const r = await renderEmail({
    podcast_name: "Some Show",
    host_name: "Jaeden",
    recent_episode: "How AI Will Change Podcasting",
  });
  assert.match(r.body, /How AI Will Change Podcasting/);
});

test("renderEmail omits recent-episode line when absent", async () => {
  const r = await renderEmail({ podcast_name: "Some Show", host_name: "Jaeden" });
  assert.doesNotMatch(r.body, /caught your recent episode/);
});

test("renderEmail throws when podcast_name missing", async () => {
  await assert.rejects(() => renderEmail({}), /podcast_name is required/);
});
