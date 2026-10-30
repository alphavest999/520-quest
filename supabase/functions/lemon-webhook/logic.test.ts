// Run with: node --test supabase/functions/lemon-webhook/logic.test.ts   (Node 22.18+ runs TypeScript directly)
import test from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { decide, parseConfig, verifySignature } from "./logic.ts";
import { handleRequest } from "./handler.ts";

const SECRET = "whsec_test_secret";
const ENV = { LS_WEBHOOK_SECRET: SECRET, LS_VARIANT_MONTHLY: "111", LS_VARIANT_SIXMONTH: "222", LS_VARIANT_YEARLY: "333", LS_MODE: "test",
  SUPABASE_URL: "https://x.supabase.co", SUPABASE_SERVICE_ROLE_KEY: "service-key" };
const UID = "3f2b8c1e-6a4d-4e8b-9c1a-2d5e7f903a11";
const sign = (raw: string) => createHmac("sha256", SECRET).update(raw).digest("hex");
const ev = (name: string, attrs: Record<string, unknown> = {}, meta: Record<string, unknown> = {}) => ({
  meta: { event_name: name, test_mode: true, custom_data: { user_id: UID }, ...meta },
  data: { id: "9001", attributes: { variant_id: 111, status: "active", user_email: "Student@Example.org", updated_at: "2026-10-28T12:00:00.000000Z", ends_at: null, ...attrs } },
});
const cfg = parseConfig(ENV);

test("signature: valid, wrong secret, tampered body, junk", async () => {
  const raw = JSON.stringify(ev("subscription_created"));
  assert.equal(await verifySignature(raw, sign(raw), SECRET), true);
  assert.equal(await verifySignature(raw, sign(raw), "other"), false);
  assert.equal(await verifySignature(raw + " ", sign(raw), SECRET), false);
  assert.equal(await verifySignature(raw, "zz", SECRET), false);
  assert.equal(await verifySignature(raw, null, SECRET), false);
});

test("each variant maps to its plan; email is lowercased; user id kept", async () => {
  for (const [variant, plan] of [[111, "monthly"], [222, "sixmonth"], [333, "yearly"]] as const) {
    const d = await decide(ev("subscription_created", { variant_id: variant }), cfg);
    assert.equal(d.kind, "apply");
    if (d.kind === "apply") { assert.equal(d.plan, plan); assert.equal(d.email, "student@example.org"); assert.equal(d.userId, UID); assert.equal(d.subscriptionId, "9001"); assert.equal(d.test, true); }
  }
});

test("lifecycle: cancelled keeps access until ends_at; expired, paused, unpaid revoke", async () => {
  const now = Date.parse("2026-11-01T00:00:00Z");
  const cancelledLater = await decide(ev("subscription_cancelled", { status: "cancelled", ends_at: "2026-12-01T00:00:00Z" }), cfg, now);
  assert.equal(cancelledLater.kind === "apply" && cancelledLater.plan, "monthly");
  const cancelledPast = await decide(ev("subscription_cancelled", { status: "cancelled", ends_at: "2026-10-01T00:00:00Z" }), cfg, now);
  assert.equal(cancelledPast.kind === "apply" && cancelledPast.plan, "free");
  assert.equal((await decide(ev("subscription_expired", { status: "expired" }), cfg) as any).plan, "free");
  assert.equal((await decide(ev("subscription_paused", { status: "paused" }), cfg) as any).plan, "free");
  assert.equal((await decide(ev("subscription_updated", { status: "unpaid" }), cfg) as any).plan, "free");
  assert.equal((await decide(ev("subscription_updated", { status: "past_due" }), cfg) as any).plan, "monthly");
  assert.equal((await decide(ev("subscription_updated", { status: "on_trial" }), cfg) as any).plan, "monthly");
  assert.equal((await decide(ev("subscription_resumed", { status: "active" }), cfg) as any).plan, "monthly");
});

test("ignored: other events, unknown variant, bad status, no identity, mode mismatch", async () => {
  assert.equal((await decide(ev("order_created"), cfg)).kind, "ignore");
  assert.equal((await decide(ev("subscription_payment_success"), cfg)).kind, "ignore");
  assert.equal((await decide(ev("subscription_created", { variant_id: 999 }), cfg)).kind, "ignore");
  assert.equal((await decide(ev("subscription_updated", { status: "weird" }), cfg)).kind, "ignore");
  assert.equal((await decide(ev("subscription_created", { user_email: "" }, { custom_data: {} }), cfg)).kind, "ignore");
  assert.equal((await decide(ev("subscription_created", {}, { test_mode: false }), cfg)).kind, "ignore"); // LS_MODE=test ignores live
  assert.equal((await decide(ev("subscription_created"), parseConfig({ ...ENV, LS_MODE: "live" }))).kind, "ignore"); // live ignores test
  assert.equal((await decide(ev("subscription_created"), parseConfig({ ...ENV, LS_MODE: "both" }))).kind, "apply");
  assert.equal((await decide({}, cfg)).kind, "ignore");
});

test("a malformed user id falls back to the email; event key is stable and unique per update", async () => {
  const a = await decide(ev("subscription_created", {}, { custom_data: { user_id: "not-a-uuid" } }), cfg);
  assert.equal(a.kind === "apply" && a.userId, null);
  assert.equal(a.kind === "apply" && a.email, "student@example.org");
  const b = await decide(ev("subscription_created"), cfg), c = await decide(ev("subscription_created"), cfg);
  const d = await decide(ev("subscription_created", { updated_at: "2026-10-28T12:00:01.000000Z" }), cfg);
  assert.equal((b as any).eventKey, (c as any).eventKey);
  assert.notEqual((b as any).eventKey, (d as any).eventKey);
});

test("handler: bad signature 401, wrong method 405, ignored 200, apply calls the database once", async () => {
  const calls: { url: string; init: any }[] = [];
  const fakeFetch = (async (url: string, init: any) => { calls.push({ url, init }); return new Response(JSON.stringify("applied"), { status: 200 }); }) as unknown as typeof fetch;
  const raw = JSON.stringify(ev("subscription_created", { variant_id: 333 }));
  const post = (body: string, sig: string) => new Request("https://f/lemon-webhook", { method: "POST", body, headers: { "x-signature": sig } });

  assert.equal((await handleRequest(new Request("https://f/", { method: "GET" }), ENV, fakeFetch)).status, 405);
  assert.equal((await handleRequest(post(raw, "00".repeat(32)), ENV, fakeFetch)).status, 401);
  assert.equal(calls.length, 0);

  const ign = JSON.stringify(ev("order_created"));
  const r1 = await handleRequest(post(ign, sign(ign)), ENV, fakeFetch);
  assert.equal(r1.status, 200); assert.ok((await r1.json()).ignored); assert.equal(calls.length, 0);

  const r2 = await handleRequest(post(raw, sign(raw)), ENV, fakeFetch);
  assert.equal(r2.status, 200);
  assert.deepEqual(await r2.json(), { ok: true, outcome: "applied", plan: "yearly" });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "https://x.supabase.co/rest/v1/rpc/apply_payment");
  assert.equal(calls[0].init.headers.authorization, "Bearer service-key");
  const sent = JSON.parse(calls[0].init.body);
  assert.equal(sent.p_plan, "yearly"); assert.equal(sent.p_user, UID); assert.equal(sent.p_email, "student@example.org"); assert.equal(sent.p_test, true);
  assert.match(sent.p_event_key, /^[0-9a-f]{64}$/);
});

test("handler: a database failure returns 500 so Lemon Squeezy retries; missing secret returns 500", async () => {
  const failing = (async () => new Response("boom", { status: 500 })) as unknown as typeof fetch;
  const raw = JSON.stringify(ev("subscription_created"));
  const req = () => new Request("https://f/", { method: "POST", body: raw, headers: { "x-signature": sign(raw) } });
  assert.equal((await handleRequest(req(), ENV, failing)).status, 500);
  assert.equal((await handleRequest(req(), { ...ENV, LS_WEBHOOK_SECRET: undefined }, failing)).status, 500);
});
