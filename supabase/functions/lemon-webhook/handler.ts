import { decide, parseConfig, verifySignature } from "./logic.ts";

const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

// Takes the environment and fetch as arguments so it can be tested without Deno.
export async function handleRequest(
  req: Request, env: Record<string, string | undefined>, fetchFn: typeof fetch,
): Promise<Response> {
  if (req.method !== "POST") return json(405, { ok: false, error: "POST only" });
  const secret = env.LS_WEBHOOK_SECRET;
  if (!secret) return json(500, { ok: false, error: "LS_WEBHOOK_SECRET is not set" });

  const raw = await req.text();
  if (!(await verifySignature(raw, req.headers.get("x-signature"), secret))) return json(401, { ok: false, error: "bad signature" });

  let body: unknown;
  try { body = JSON.parse(raw); } catch { return json(400, { ok: false, error: "bad json" }); }

  const cfg = parseConfig(env);
  if (!Object.keys(cfg.variants).length) return json(500, { ok: false, error: "no LS_VARIANT_* set" });
  const d = await decide(body, cfg);
  if (d.kind === "ignore") return json(200, { ok: true, ignored: d.reason }); // 2xx so Lemon Squeezy does not retry

  const url = env.SUPABASE_URL, key = env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) return json(500, { ok: false, error: "Supabase env missing" });
  const r = await fetchFn(`${url}/rest/v1/rpc/apply_payment`, {
    method: "POST",
    headers: { apikey: key, authorization: `Bearer ${key}`, "content-type": "application/json" },
    body: JSON.stringify({
      p_event_key: d.eventKey, p_event_name: d.eventName, p_user: d.userId, p_email: d.email, p_plan: d.plan,
      p_event_time: d.eventTime, p_subscription: d.subscriptionId, p_test: d.test,
    }),
  });
  if (!r.ok) return json(500, { ok: false, error: "database rejected the update" }); // non-2xx makes Lemon Squeezy retry
  const outcome = await r.json();
  return json(200, { ok: true, outcome, plan: d.plan });
}
