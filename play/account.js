/* 520 Quest accounts: email-code sign-in, progress sync, device limits, paid content and 1v1 duels.
   Runs after the main app script and shares its globals (S, save, sheet, toast, go, ...).
   The server is Supabase; see supabase/001_core.sql for the tables and functions. */
const SB_URL = CONFIG.supabaseUrl, SB_KEY = CONFIG.supabaseKey;
const SB_LIB = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js";
const SB_STORE = SB_URL ? "sb-" + new URL(SB_URL).hostname.split(".")[0] + "-auth-token" : "";
const CK_STORE = "quest520.ck", DEV_STORE = "quest520.dev";
const PLAN_NAME = { free: "Free", monthly: "Monthly", sixmonth: "6 Months", yearly: "Yearly" };
const ACCT = { state: SB_URL ? "out" : "off", sb: null, user: null, profile: null, key: null, limit: 0, synced: 0, loading: null };
const lsGet = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
const lsSet = (k, v) => { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) {} };
const b64bytes = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));

function deviceId() {
  let id = lsGet(DEV_STORE);
  if (!id) { id = (crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2)); lsSet(DEV_STORE, id); }
  return id;
}
function deviceInfo() {
  const ua = navigator.userAgent, touch = navigator.maxTouchPoints > 1;
  const ipad = /iPad/.test(ua) || (/Macintosh/.test(ua) && touch);
  const os = ipad ? "iPad" : /iPhone/.test(ua) ? "iPhone" : /Android/.test(ua) ? (/Mobile/.test(ua) ? "Android phone" : "Android tablet") : /Mac/.test(ua) ? "Mac" : /Windows/.test(ua) ? "Windows PC" : /CrOS/.test(ua) ? "Chromebook" : /Linux/.test(ua) ? "Linux" : "Computer";
  const br = /Edg\//.test(ua) ? "Edge" : /CriOS|Chrome\//.test(ua) ? "Chrome" : /FxiOS|Firefox\//.test(ua) ? "Firefox" : /Safari\//.test(ua) ? "Safari" : "";
  const kind = ipad || /Android tablet/.test(os) ? "tablet" : /iPhone|Android phone/.test(os) ? "mobile" : "desktop";
  return { label: (os + (br ? " · " + br : "") + (installed() ? " app" : "")).slice(0, 80), kind };
}

/* ---------- client ---------- */
function sbLoad() {
  if (ACCT.sb) return Promise.resolve(ACCT.sb);
  if (!SB_URL) return Promise.reject(new Error("off"));
  if (ACCT.loading) return ACCT.loading;
  ACCT.loading = new Promise((res, rej) => {
    const make = () => {
      ACCT.sb = window.supabase.createClient(SB_URL, SB_KEY, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false, storageKey: SB_STORE } });
      ACCT.sb.auth.onAuthStateChange((ev, session) => {
        if (ev === "SIGNED_OUT") signedOut();
        else if (session && session.user && (!ACCT.user || ACCT.user.id !== session.user.id)) signedIn(session.user);
      });
      res(ACCT.sb);
    };
    if (window.supabase && window.supabase.createClient) return make();
    const s = document.createElement("script"); s.src = SB_LIB; s.async = true;
    s.onload = make; s.onerror = () => { ACCT.loading = null; rej(new Error("load")); };
    document.head.appendChild(s);
  });
  return ACCT.loading;
}
function rpc(name, args) {
  return sbLoad().then(sb => sb.rpc(name, args || {})).then(r => { if (r.error) throw r.error; return r.data; });
}
const errText = e => String((e && (e.message || e.error_description)) || e || "");

/* ---------- sign in / out ---------- */
function signIn(why) {
  if (ACCT.state === "off") return toast("Accounts aren't available yet.");
  if (!navigator.onLine) return toast("Connect to the internet to sign in.");
  sbLoad().catch(() => toast("Couldn't reach the sign-in server. Check your connection and try again."));
  sheet(`<div class="eyebrow">${esc(why || "Account")}</div><h2>Sign in with your email</h2>
    <p class="muted">We'll email you a code. Your progress saves to your account and follows you to your other devices. No password needed.</p>
    <label class="field" for="acEmail">Email<input type="email" id="acEmail" autocomplete="email" inputmode="email" placeholder="you@example.com"></label>
    <div class="row"><button class="btn primary" data-acsend>Email me a code</button><button class="btn ghost" data-close>Not now</button></div><p class="small muted" id="acMsg"></p>`, s => {
    const msg = $("#acMsg", s), input = $("#acEmail", s);
    const send = async () => {
      const email = input.value.trim().toLowerCase();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { msg.textContent = "Enter your email address."; return; }
      msg.textContent = "Sending…";
      try {
        const sb = await sbLoad(), r = await sb.auth.signInWithOtp({ email, options: { shouldCreateUser: true } });
        if (r.error) throw r.error;
        codeStep(s, email);
      } catch (e) {
        msg.textContent = /rate|limit|security purposes/i.test(errText(e)) ? "Too many codes were sent just now. Wait a minute, then try again." : "Couldn't send the code. Check the address and your connection, then try again.";
      }
    };
    $("[data-acsend]", s).addEventListener("click", send);
    input.addEventListener("keydown", e => { if (e.key === "Enter") send(); });
    input.focus();
  });
}
function codeStep(s, email) {
  s.innerHTML = `<div class="eyebrow">Check your email</div><h2>Enter the code</h2><p class="muted">We sent a code to <b>${esc(email)}</b>. It can take a minute; check spam too.</p>
    <label class="field" for="acCode">Code<input type="text" id="acCode" inputmode="numeric" autocomplete="one-time-code" maxlength="10" placeholder="123456"></label>
    <div class="row"><button class="btn primary" data-acverify>Sign in</button><button class="btn ghost" data-close>Cancel</button></div><p class="small muted" id="acMsg"></p>`;
  const msg = $("#acMsg", s), input = $("#acCode", s);
  const verify = async () => {
    const token = input.value.replace(/\D/g, "");
    if (token.length < 6) { msg.textContent = "Enter the code from the email."; return; }
    msg.textContent = "Checking…";
    try {
      const r = await ACCT.sb.auth.verifyOtp({ email, token, type: "email" });
      if (r.error) throw r.error;
      $("#sheetHost").innerHTML = "";
      toast("<b>Signed in.</b> Your progress now saves to your account.");
      if (r.data && r.data.user) signedIn(r.data.user);
    } catch (e) { msg.textContent = /expired/i.test(errText(e)) ? "That code expired. Close this and send a new one." : "That code didn't work. Check it and try again."; }
  };
  $("[data-acverify]", s).addEventListener("click", verify);
  input.addEventListener("keydown", e => { if (e.key === "Enter") verify(); });
  input.focus();
}
async function signedIn(user) {
  ACCT.user = user; ACCT.state = "in";
  try {
    const sb = await sbLoad();
    const dev = deviceInfo(), reg = await rpc("register_device", { p_device_id: deviceId(), p_label: dev.label, p_kind: dev.kind });
    const p = await sb.from("profiles").select("*").eq("id", user.id).single();
    if (p.error) throw p.error;
    ACCT.profile = p.data;
    if (!reg.ok) { ACCT.state = "blocked"; ACCT.limit = reg.limit; refreshViews(); return deviceLimitSheet(); }
    applyPlan();
    await pullProgress();
    await loadKey();
  } catch (e) { console.warn("account", e); }
  refreshViews();
}
function signedOut() {
  ACCT.user = null; ACCT.profile = null; ACCT.state = SB_URL ? "out" : "off"; ACCT.key = null; lsSet(CK_STORE, null);
  if (S.proBy === "account") { S.pro = false; delete S.proBy; save(); }
  refreshViews();
}
function refreshViews() {
  if (!$("#view-me").hidden) renderMe();
  if (!$("#view-boss").hidden && !B && !DU.battle) renderBossLobby();
  if (!$("#view-course").hidden) renderCourse();
  renderHUD();
}

/* ---------- plans ---------- */
const isPaid = () => !!(ACCT.profile && ACCT.profile.plan !== "free");
const fullAccess = () => isPaid() || !!S.admin; // every plan unlocks all sheets and mnemonics; so does the owner admin flag
function applyPlan() {
  if (isPaid() && !S.pro) { S.pro = true; S.proBy = "account"; save(); toast(`<b>${esc(PLAN_NAME[ACCT.profile.plan])}</b> is active on this device.`); }
  else if (!isPaid() && S.proBy === "account") { S.pro = false; delete S.proBy; save(); }
}
/* ---------- paid content: sealed sheets and mnemonics ---------- */
async function loadKey() {
  if (!fullAccess()) { ACCT.key = null; lsSet(CK_STORE, null); return; }
  try { const k = await rpc("get_content_key"); if (k) { lsSet(CK_STORE, k); await useKey(k); } } catch (e) {}
}
async function useKey(k) {
  try { ACCT.key = await crypto.subtle.importKey("raw", b64bytes(k), "AES-GCM", false, ["decrypt"]); } catch (e) { ACCT.key = null; return; }
  unsealMnemonics(); refreshViews();
}
async function unseal(box) {
  const pt = await crypto.subtle.decrypt({ name: "AES-GCM", iv: b64bytes(box.iv) }, ACCT.key, b64bytes(box.ct));
  return JSON.parse(new TextDecoder().decode(pt));
}
function unsealMnemonics() {
  if (!ACCT.key || !CONFIG.flags.MNEMONICS_ENABLED) return;
  mnReady.then(() => fetch("mnem/locked.enc.json")).then(r => r.json()).then(unseal).then(list => {
    const by = Object.fromEntries(list.map(m => [String(m.id), m]));
    (MN || []).forEach(m => { const f = by[String(m.id)]; if (f) { Object.assign(m, f); delete m.locked; } });
    if (!$("#view-course").hidden) renderCourse();
  }).catch(() => {});
}
window.acctHasKey = () => !!ACCT.key;
// After a checkout succeeds, the webhook sets the plan a moment later: check the profile every 3 s for up to 90 s.
let planWatch = null;
window.acctWatchPlan = () => {
  if (ACCT.state !== "in") { toast("<b>Payment received.</b> Sign in with the same email in the Me tab to unlock your plan."); return; }
  clearInterval(planWatch); let n = 0;
  toast("<b>Payment received.</b> Activating your plan…", 6000);
  planWatch = setInterval(async () => {
    try {
      const sb = await sbLoad(), p = await sb.from("profiles").select("*").eq("id", ACCT.user.id).single();
      if (!p.error && p.data && p.data.plan !== "free") { clearInterval(planWatch); ACCT.profile = p.data; applyPlan(); await loadKey(); refreshViews(); return; }
    } catch (e) {}
    if (++n >= 30) { clearInterval(planWatch); toast("Your plan is taking longer than usual. Reopen the app in a minute, or contact support."); }
  }, 3000);
};
window.openSealed = id => fetch("sheets/" + encodeURIComponent(id) + ".enc.json").then(r => { if (!r.ok) throw 0; return r.json(); }).then(unseal);

/* ---------- progress sync ---------- */
let syncTimer = 0;
const PREFS = ["sound", "music", "fanfare", "pro", "proBy"];
async function pullProgress() {
  const r = await ACCT.sb.from("progress").select("state,total").eq("user_id", ACCT.user.id).maybeSingle();
  if (r.error) throw r.error;
  const remote = r.data && r.data.state;
  if (remote && remote.v === 1 && (r.data.total || 0) > (S.total || 0)) {
    const keep = Object.fromEntries(PREFS.filter(k => k in S).map(k => [k, S[k]]));
    S = Object.assign(fresh(), remote, keep); rollDay();
    try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {}
    renderAll();
    toast(`<b>Progress loaded.</b> ${S.total.toLocaleString()} answers from your account.`);
  } else pushProgress();
}
async function pushProgress() {
  clearTimeout(syncTimer); syncTimer = 0;
  if (ACCT.state !== "in" || !navigator.onLine) return;
  const state = Object.assign({}, S); PREFS.forEach(k => delete state[k]);
  const r = await ACCT.sb.from("progress").upsert({ user_id: ACCT.user.id, state, total: S.total || 0, updated_at: new Date().toISOString() });
  if (!r.error) ACCT.synced = Date.now();
  const lvl = S.lv.level, acc = S.total ? Math.round(S.totalCorrect / S.total * 100) : 0, p = ACCT.profile;
  if (p && (p.level !== lvl || p.acc !== acc)) { p.level = lvl; p.acc = acc; ACCT.sb.from("profiles").update({ level: lvl, acc }).eq("id", p.id).then(() => {}); }
}
window.acctSync = () => { if (ACCT.state === "in" && !syncTimer) syncTimer = setTimeout(() => pushProgress().catch(() => {}), 3000); };
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden" && syncTimer) pushProgress().catch(() => {}); });

/* ---------- devices ---------- */
async function devicesSheet() {
  sheet(`<div class="eyebrow">Account</div><h2>Manage devices</h2><p class="muted" id="dvNote">Loading…</p><div class="stack" id="dvList"></div><div class="row"><button class="btn ghost" data-close>Done</button></div>`, async s => {
    const list = $("#dvList", s), note = $("#dvNote", s);
    const draw = async () => {
      const r = await ACCT.sb.from("devices").select("*").order("last_seen", { ascending: false });
      if (r.error) { note.textContent = "Couldn't load your devices. Check your connection."; return; }
      const lim = isPaid() ? 3 : 1, me = deviceId();
      note.innerHTML = `Your ${esc(PLAN_NAME[(ACCT.profile || {}).plan] || "Free")} plan works on <b>${lim} device${lim === 1 ? "" : "s"}</b>. Devices unused for 90 days drop off on their own.${ACCT.state === "blocked" ? " Remove one to use 520 Quest here." : ""}`;
      list.innerHTML = r.data.map(d => `<div class="panel row" style="justify-content:space-between;flex-wrap:nowrap;gap:10px"><div style="min-width:0"><b>${esc(d.label || "Device")}</b>${d.device_id === me ? ' <span class="tag">This device</span>' : ""}<div class="small muted">Last used ${new Date(d.last_seen).toLocaleDateString()}</div></div><button class="btn small ghost" data-dvdel="${esc(d.id)}">Remove</button></div>`).join("") || `<p class="small muted">No devices yet.</p>`;
    };
    list.addEventListener("click", async e => {
      const b = e.target.closest("[data-dvdel]"); if (!b) return;
      b.disabled = true;
      const r = await ACCT.sb.from("devices").delete().eq("id", b.dataset.dvdel);
      if (r.error) { b.disabled = false; return toast("Couldn't remove that device. Try again."); }
      if (ACCT.state === "blocked") { $("#sheetHost").innerHTML = ""; return signedIn(ACCT.user); }
      draw();
    });
    draw();
  });
}
function deviceLimitSheet() {
  sheet(`<div class="eyebrow">Device limit</div><h2>Your account is on ${ACCT.limit} device${ACCT.limit === 1 ? "" : "s"} already</h2>
    <p class="muted">${ACCT.limit === 1 ? "Free accounts sync to 1 device; any paid plan works on 3." : "Your plan works on 3 devices at a time."} Remove an old device to use this one, or keep playing here without syncing.</p>
    <div class="row"><button class="btn primary" data-acdevices>Manage devices</button><button class="btn ghost" data-acout>Sign out here</button></div>`);
}

/* ---------- Me tab panel ---------- */
window.acctPanelHTML = () => {
  if (ACCT.state === "off") return "";
  if (ACCT.state === "out") return `<div class="panel"><h3>Account</h3><p class="small">Sign in to save your progress, use 520 Quest on up to 3 devices and play 1v1 duels.</p><div class="row"><button class="btn primary small" data-acin>Sign in with email</button></div></div>`;
  const p = ACCT.profile || {}, email = (ACCT.user && ACCT.user.email) || "";
  return `<div class="panel"><div class="row" style="justify-content:space-between;flex-wrap:nowrap"><h3>Account</h3><span class="tag sec">${esc(PLAN_NAME[p.plan] || "Free")}</span></div>
    <p class="small" style="overflow-wrap:anywhere">${esc(email)}${p.name ? ` · duel name <b>${esc(p.name)}</b>` : ""}</p>
    ${ACCT.state === "blocked" ? `<p class="small" style="color:var(--bad)">This device isn't syncing: your account is already on ${ACCT.limit} device${ACCT.limit === 1 ? "" : "s"}.</p>` : `<p class="small muted">${ACCT.synced ? "Progress saved to your account " + new Date(ACCT.synced).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }) + "." : "Progress saves to your account after each question."}${fullAccess() ? " All Mastery Sheets and mnemonics are unlocked." : ""}</p>`}
    <div class="row"><button class="btn small" data-acdevices>Manage devices</button><button class="btn small" data-acname>Change duel name</button><button class="btn small ghost" data-acout>Sign out</button></div></div>`;
};
async function signOut() {
  if (syncTimer) await pushProgress().catch(() => {});
  $("#sheetHost").innerHTML = "";
  try { await ACCT.sb.auth.signOut(); } catch (e) {}
  signedOut(); toast("Signed out. Your progress stays on this device.");
}
document.addEventListener("click", async e => {
  const t = e.target;
  if (t.closest("[data-acin]")) return signIn();
  if (t.closest("[data-acout]")) return signOut();
  if (t.closest("[data-acdevices]")) return devicesSheet();
  if (t.closest("[data-acname]")) {
    sheet(`<div class="eyebrow">Duels</div><h2>Your duel name</h2><p class="muted">Opponents see this name. Keep it friendly; no email addresses.</p><label class="field" for="acNm">Name<input type="text" id="acNm" maxlength="20" value="${esc((ACCT.profile || {}).name || "")}"></label><div class="row"><button class="btn primary" data-acnmsave>Save</button><button class="btn ghost" data-close>Cancel</button></div>`, s => {
      $("[data-acnmsave]", s).addEventListener("click", async () => {
        const nm = $("#acNm", s).value.replace(/[<>@]/g, "").trim().slice(0, 20);
        if (nm.length < 2) return toast("Use at least 2 characters.");
        const r = await ACCT.sb.from("profiles").update({ name: nm }).eq("id", ACCT.user.id);
        if (r.error) return toast("Couldn't save. Try again.");
        ACCT.profile.name = nm; $("#sheetHost").innerHTML = ""; refreshViews();
      });
    });
  }
});

/* ---------- duel links: 520quest.com/duel/1234 lands on /play/#duel=1234 ---------- */
/* ---------- start ---------- */
(function initAccount() {
  if (ACCT.state === "off") return;
  const k = lsGet(CK_STORE); if (k) useKey(k);
  if (lsGet(SB_STORE)) sbLoad().then(sb => sb.auth.getSession()).then(r => { const u = r.data && r.data.session && r.data.session.user; if (u && (!ACCT.user || ACCT.user.id !== u.id)) signedIn(u); }).catch(() => {});
})();
