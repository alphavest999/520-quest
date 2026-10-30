// Pure webhook logic for Lemon Squeezy subscription events. No Deno or Node APIs beyond Web Crypto, so it runs in both.

export type Plan = "free" | "monthly" | "sixmonth" | "yearly";
export type Mode = "test" | "live" | "both";
export interface Config { variants: Record<string, Plan>; mode: Mode }
export interface Applied {
  kind: "apply"; plan: Plan; userId: string | null; email: string | null;
  subscriptionId: string | null; eventTime: string; eventKey: string; eventName: string; test: boolean;
}
export interface Ignored { kind: "ignore"; reason: string }
export type Decision = Applied | Ignored;

const enc = new TextEncoder();
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
// Events that change what a person is entitled to. Everything else is acknowledged and ignored.
const HANDLED = new Set([
  "subscription_created", "subscription_updated", "subscription_resumed", "subscription_unpaused",
  "subscription_cancelled", "subscription_paused", "subscription_expired",
]);

export function parseConfig(env: Record<string, string | undefined>): Config {
  const variants: Record<string, Plan> = {};
  const add = (id: string | undefined, plan: Plan) => { if (id && id.trim()) variants[id.trim()] = plan; };
  add(env.LS_VARIANT_MONTHLY, "monthly");
  add(env.LS_VARIANT_SIXMONTH, "sixmonth");
  add(env.LS_VARIANT_YEARLY, "yearly");
  const m = (env.LS_MODE || "live").toLowerCase();
  return { variants, mode: m === "test" || m === "both" ? (m as Mode) : "live" };
}

function hexToBytes(hex: string): Uint8Array | null {
  if (!/^[0-9a-f]+$/i.test(hex) || hex.length % 2) return null;
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  return out;
}

// Lemon Squeezy sends hex(HMAC-SHA256(raw body, signing secret)) in the X-Signature header.
export async function verifySignature(raw: string, signature: string | null, secret: string): Promise<boolean> {
  if (!signature || !secret) return false;
  const sig = hexToBytes(signature.trim());
  if (!sig) return false;
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["verify"]);
  return crypto.subtle.verify("HMAC", key, sig, enc.encode(raw)); // constant-time compare
}

async function sha256Hex(s: string): Promise<string> {
  const d = new Uint8Array(await crypto.subtle.digest("SHA-256", enc.encode(s)));
  return [...d].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function decide(body: any, cfg: Config, now: number = Date.now()): Promise<Decision> {
  const name: string | undefined = body?.meta?.event_name;
  if (!name) return { kind: "ignore", reason: "no event name" };
  const test = !!body?.meta?.test_mode;
  if (test && cfg.mode === "live") return { kind: "ignore", reason: "test event while LS_MODE=live" };
  if (!test && cfg.mode === "test") return { kind: "ignore", reason: "live event while LS_MODE=test" };
  if (!HANDLED.has(name)) return { kind: "ignore", reason: `event ${name} is not used` };

  const attrs = body?.data?.attributes;
  const id = body?.data?.id;
  if (!attrs || id == null) return { kind: "ignore", reason: "no subscription data" };
  const planOfVariant = cfg.variants[String(attrs.variant_id)];
  if (!planOfVariant) return { kind: "ignore", reason: `unknown variant ${attrs.variant_id}` };
  const updated: string | undefined = attrs.updated_at;
  if (!updated || Number.isNaN(Date.parse(updated))) return { kind: "ignore", reason: "no updated_at" };

  // Who still gets access. A cancelled subscription keeps access until the period it paid for ends.
  const status: string = String(attrs.status || "");
  let plan: Plan;
  if (name === "subscription_expired" || name === "subscription_paused" || ["expired", "paused", "unpaid"].includes(status)) plan = "free";
  else if (status === "cancelled") {
    const ends = attrs.ends_at ? Date.parse(attrs.ends_at) : NaN;
    plan = !Number.isNaN(ends) && ends <= now ? "free" : planOfVariant;
  } else if (["active", "on_trial", "past_due"].includes(status)) plan = planOfVariant;
  else return { kind: "ignore", reason: `status ${status || "(none)"} not recognised` };

  const rawUser = body?.meta?.custom_data?.user_id;
  const userId = typeof rawUser === "string" && UUID.test(rawUser) ? rawUser.toLowerCase() : null;
  const email = typeof attrs.user_email === "string" && attrs.user_email.trim() ? attrs.user_email.trim().toLowerCase() : null;
  if (!userId && !email) return { kind: "ignore", reason: "no user id or email" };

  return {
    kind: "apply", plan, userId, email, subscriptionId: String(id), eventTime: new Date(updated).toISOString(),
    eventKey: await sha256Hex(`${name}:${id}:${updated}`), eventName: name, test,
  };
}
