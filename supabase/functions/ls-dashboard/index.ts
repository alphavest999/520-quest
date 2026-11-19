// 520 Quest operations dashboard: reads Lemon Squeezy sales for the owner's dashboard.
// Single file, so it can be pasted into Supabase > Edge Functions > "Via Editor" with no CLI.
//
// Who can call it: only a signed-in account with profiles.is_admin = true. The Lemon Squeezy API key
// lives in the Edge Function secret LS_API_KEY and never reaches the browser.
// Read-only: it only lists subscriptions and subscription invoices. It does not touch the payment webhook.
//
// Secrets it uses: LS_API_KEY (you add it), plus LS_VARIANT_MONTHLY / LS_VARIANT_SIXMONTH / LS_VARIANT_YEARLY
// and LS_MODE (already set for the lemon-webhook function). SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
// are provided by Supabase automatically.

const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "authorization, apikey, content-type, x-client-info",
  "access-control-allow-methods": "POST, GET, OPTIONS",
};
const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { ...CORS, "content-type": "application/json" } });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  const url = Deno.env.get("SUPABASE_URL"), svc = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY"), ls = Deno.env.get("LS_API_KEY");
  if (!url || !svc) return json(500, { ok: false, error: "Supabase env missing" });

  // 1. Who is calling? Must be a signed-in admin.
  const auth = req.headers.get("authorization") || "";
  const who = await fetch(`${url}/auth/v1/user`, { headers: { apikey: svc, authorization: auth } });
  if (!who.ok) return json(401, { ok: false, error: "sign in first" });
  const user = await who.json();
  const prof = await fetch(`${url}/rest/v1/profiles?id=eq.${encodeURIComponent(user.id)}&select=is_admin`, {
    headers: { apikey: svc, authorization: `Bearer ${svc}` },
  });
  const rows = prof.ok ? await prof.json() : [];
  if (!rows[0] || rows[0].is_admin !== true) return json(403, { ok: false, error: "admins only" });
  if (!ls) return json(500, { ok: false, error: "LS_API_KEY is not set" });

  // 2. Read every page of a Lemon Squeezy list.
  async function all(path: string) {
    const out: any[] = [];
    let next: string | null = `https://api.lemonsqueezy.com/v1/${path}`;
    for (let i = 0; next && i < 50; i++) {
      const r = await fetch(next, { headers: { accept: "application/vnd.api+json", authorization: `Bearer ${ls}` } });
      if (!r.ok) throw new Error(`Lemon Squeezy ${path.split("?")[0]} answered ${r.status}`);
      const b = await r.json();
      out.push(...(b.data || []));
      next = b.links && b.links.next ? b.links.next : null;
    }
    return out;
  }

  const mode = (Deno.env.get("LS_MODE") || "live").toLowerCase();
  const keep = (a: any) => mode === "both" || (mode === "test") === !!a.test_mode;
  const plans: Record<string, string> = {};
  for (const [k, p] of [["LS_VARIANT_MONTHLY", "monthly"], ["LS_VARIANT_SIXMONTH", "sixmonth"], ["LS_VARIANT_YEARLY", "yearly"]]) {
    for (const id of (Deno.env.get(k) || "").split(",").map((s) => s.trim()).filter(Boolean)) plans[id] = p;
  }

  try {
    const [subs, invs] = await Promise.all([
      all("subscriptions?page[size]=100"),
      all("subscription-invoices?page[size]=100"),
    ]);
    const subPlan: Record<string, string> = {};
    const subscriptions = subs.map((s) => s.attributes && ({ id: String(s.id), ...s.attributes })).filter((a) => a && keep(a)).map((a) => {
      const plan = plans[String(a.variant_id)] || "monthly";
      subPlan[a.id] = plan;
      return { email: (a.user_email || "").toLowerCase(), plan, status: a.status, created: a.created_at, endsAt: a.ends_at, renewsAt: a.renews_at };
    });
    const payments = invs.map((s) => s.attributes).filter((a) => a && keep(a) && ["paid", "refunded", "partial_refund"].includes(a.status)).map((a) => ({
      email: (a.user_email || "").toLowerCase(),
      date: a.created_at,
      amount: Math.round((Number(a.total || 0) - Number(a.refunded_amount || 0))) / 100,
      plan: subPlan[String(a.subscription_id)] || "monthly",
      reason: a.billing_reason,
      status: a.status,
    }));
    return json(200, { ok: true, mode, subscriptions, payments });
  } catch (e) {
    return json(502, { ok: false, error: String((e as Error).message || e) });
  }
});
