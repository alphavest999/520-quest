/* 520 Quest accounts: email-code sign-in, progress sync, device limits, and paid content.
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
    S.admin = isAdminEmail(user.email); if (S.admin) { S.pro = true; try{ save(); }catch(e){} }
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
// Owner admin: profiles.is_admin, set only from the Supabase dashboard (supabase/003_admin.sql). It unlocks everything a plan does.
const isAdmin = () => !!(ACCT.profile && ACCT.profile.is_admin);
const isPaid = () => !!(ACCT.profile && (ACCT.profile.plan !== "free" || ACCT.profile.is_admin));
const planName = p => (p && p.is_admin ? "Admin" : PLAN_NAME[(p || {}).plan] || "Free");
const ADMIN_EMAILS = ["alphavest99@gmail.com"];
const isAdminEmail = (email) => ADMIN_EMAILS.includes((email||"").toLowerCase());
const fullAccess = () => isPaid() || !!S.admin; // every plan unlocks all sheets and mnemonics; so does the owner admin flag
function applyPlan() {
  if (isPaid() && !S.pro) { S.pro = true; S.proBy = "account"; save(); toast(isAdmin() ? "<b>Admin access</b> is on: everything is unlocked." : `<b>${esc(PLAN_NAME[ACCT.profile.plan])}</b> is active on this device.`); }
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
  if (typeof window.onContentKey === "function") window.onContentKey(); // paid passages + full explanations
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
window.acctUnseal = box => unseal(box);
// After a checkout succeeds, the webhook sets the plan a moment later: check the profile every 3 s for up to 90 s.
let planWatch = null;
window.acctWatchPlan = () => {
  if (ACCT.state !== "in") { toast("<b>Payment received.</b> Sign in with the same email in the Me tab to unlock your plan."); return; }
  clearInterval(planWatch); let n = 0;
  toast("<b>Payment received.</b> Activating your plan…", 6000);
  planWatch = setInterval(async () => {
    try {
      const sb = await sbLoad(), p = await sb.from("profiles").select("*").eq("id", ACCT.user.id).single();
      if (!p.error && p.data && p.data.plan !== "free") { clearInterval(planWatch); ACCT.profile = p.data;
    S.admin = isAdminEmail(ACCT.user.email); if (S.admin) { S.pro = true; try{ save(); }catch(e){} } applyPlan(); await loadKey(); refreshViews(); return; }
    } catch (e) {}
    if (++n >= 30) { clearInterval(planWatch); toast("Your plan is taking longer than usual. Reopen the app in a minute, or contact support."); }
  }, 3000);
};
window.openSealed = id => fetch("sheets/" + encodeURIComponent(id) + ".enc.json").then(r=>{if(!r.ok) throw 0; return r.json();}).then(unseal).catch(()=> fetch("sheets/" + encodeURIComponent(id) + ".json").then(r=>r.json()));

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
      note.innerHTML = `Your ${esc(planName(ACCT.profile))} plan works on <b>${lim} device${lim === 1 ? "" : "s"}</b>. Devices unused for 90 days drop off on their own.${ACCT.state === "blocked" ? " Remove one to use 520 Quest here." : ""}`;
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
  if (ACCT.state === "out") return `<div class="panel"><h3>Account</h3><p class="small">Sign in to save your progress, use 520 Quest on up to 3 devices and keep your progress in sync.</p><div class="row"><button class="btn primary small" data-acin>Sign in with email</button><button class="btn small exitred" data-exit>Exit</button></div></div>`;
  const p = ACCT.profile || {}, email = (ACCT.user && ACCT.user.email) || "";
  return `<div class="panel"><div class="row" style="justify-content:space-between;flex-wrap:nowrap"><h3>Account</h3><span class="tag sec">${esc(planName(p))}</span></div>
    <p class="small" style="overflow-wrap:anywhere">${esc(email)}</p>
    ${ACCT.state === "blocked" ? `<p class="small" style="color:var(--bad)">This device isn't syncing: your account is already on ${ACCT.limit} device${ACCT.limit === 1 ? "" : "s"}.</p>` : `<p class="small muted">${ACCT.synced ? "Progress saved to your account " + new Date(ACCT.synced).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }) + "." : "Progress saves to your account after each question."}${fullAccess() ? " All Mastery Sheets and mnemonics are unlocked." : ""}</p>`}
    <div class="row"><button class="btn small" data-acdevices>Manage devices</button><button class="btn small ghost" data-acout>Sign out</button><button class="btn small exitred" data-exit>Exit without signing out</button></div></div>${isAdmin() ? adminPanelHTML() : ""}`;
};
/* ---------- owner admin tools (only for an account with is_admin) ---------- */
function adminPanelHTML() {
  const lv = S.lv.level;
  return `<div class="panel"><div class="row" style="justify-content:space-between;flex-wrap:nowrap"><h3>Admin tools</h3><span class="tag sec">Owner</span></div>
    <p class="small muted">Unlimited questions, bosses, full-lengths, minis, Mastery Sheets, mnemonics and Anki export are on. These buttons change this account's own level, to preview each tier.</p>
    <p class="small">Jump to level</p><div class="row">${[1, 2, 3, 4, 5].map(n => `<button class="btn small${n === lv ? " primary" : ""}" data-adlevel="${n}">${n}. ${esc(tierName(n))}</button>`).join("")}</div>
    <div class="row" style="margin-top:8px">${lv < 5 ? `<button class="btn small" data-adgate>Fight Gatekeeper ${lv + 1} now</button>` : ""}<button class="btn small" data-adbosses>Reset today's boss count</button></div>
    <p class="small" style="margin-top:12px">Real percent correct per question, from students' first tries.</p><div class="row"><button class="btn small" data-adqstats>Question stats</button><button class="btn small" data-adqreports>Reported questions</button><button class="btn small" data-admcat>Real MCAT results</button></div></div>`;
}
document.addEventListener("click", e => {
  if (!isAdmin()) return;
  const lvBtn = e.target.closest("[data-adlevel]"), t = e.target;
  if (lvBtn) { const n = +lvBtn.dataset.adlevel; S.lv.level = n; S.lv.qual = n; S.lv.pending = 0; save(); renderAll(); return toast(`Level set to ${n}: ${esc(tierName(n))}.`); }
  if (t.closest("[data-adgate]")) { if (S.lv.level >= 5) return; S.lv.pending = S.lv.level + 1; save(); go("boss"); return startBoss(gateBoss()); }
  if (t.closest("[data-adbosses]")) { S.today.bosses = 0; save(); refreshViews(); return toast("Today's boss count is reset."); }
});
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
});

/* ---------- question stats: the real percent of students who get each question right ---------- */
// Works signed in or not. Only a random device id, the question id, the option picked and right/wrong are sent
// (supabase/004_question_stats.sql); the server counts only each device's first answer to a question.
const QS_STORE = "quest520.qs", QR_STORE = "quest520.qr", QR_MIN = 30;
let qsList = null, qsTimer = null, qsBusy = false, qsOff = false, QRATE = null;
const qsSave = () => lsSet(QS_STORE, qsList.length ? JSON.stringify(qsList) : null);
function logAnswer(id, k, ok) {
  if (!SB_URL || !id || /^g_/.test(id)) return; // generated drill questions change every time, so they aren't tracked
  if (!qsList) { try { qsList = JSON.parse(lsGet(QS_STORE) || "[]"); } catch (e) { qsList = []; } }
  qsList.push({ q: String(id), k: k >= 0 && k <= 3 ? k : null, ok: !!ok });
  if (qsList.length > 500) qsList.splice(0, qsList.length - 500);
  qsSave(); clearTimeout(qsTimer);
  if (qsList.length >= 10) flushAnswers(); else qsTimer = setTimeout(flushAnswers, 30000);
}
function flushAnswers(leaving) {
  if (!qsList || !qsList.length || qsBusy || qsOff || !navigator.onLine) return;
  const batch = qsList.slice(0, 50); qsBusy = true; clearTimeout(qsTimer);
  fetch(SB_URL + "/rest/v1/rpc/record_answers", { method: "POST", keepalive: !!leaving, headers: { apikey: SB_KEY, "Content-Type": "application/json" }, body: JSON.stringify({ p_dev: deviceId(), p_items: batch }) })
    .then(r => { qsBusy = false; if (r.status === 404) { qsOff = true; return; } if (!r.ok) return; qsList.splice(0, batch.length); qsSave(); if (qsList.length) flushAnswers(); })
    .catch(() => { qsBusy = false; });
}
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") flushAnswers(true); });
window.addEventListener("online", () => flushAnswers());
// Percent correct for questions with 30+ answers, fetched at most twice a day.
function loadRates() {
  if (QRATE || !SB_URL) return;
  let c = null; try { c = JSON.parse(lsGet(QR_STORE) || "null"); } catch (e) {}
  QRATE = (c && c.d) || {};
  if (c && Date.now() - c.t < 12 * 3600000) return;
  fetch(SB_URL + "/rest/v1/rpc/question_rates", { method: "POST", headers: { apikey: SB_KEY, "Content-Type": "application/json" }, body: "{}" })
    .then(r => r.ok ? r.json() : null).then(d => { if (d && typeof d === "object") { QRATE = d; lsSet(QR_STORE, JSON.stringify({ t: Date.now(), d })); } }).catch(() => {});
}
function rateHTML(id) {
  loadRates();
  const r = QRATE && QRATE[id]; if (!r || r[0] < QR_MIN) return "";
  return `<p class="small muted qrate">${r[1]}% of 520 Quest students got this right (${r[0].toLocaleString()} first tries).</p>`;
}
setTimeout(loadRates, 3000);

/* Admin: questions sorted by real percent correct, with the ones that look broken or too easy flagged. */
function qstatsSheet() {
  sheet(`<div class="eyebrow">Admin</div><h2>Question stats</h2><p class="small muted" id="qsMsg">Loading…</p><div id="qsBody"></div><div class="row"><button class="btn ghost" data-close>Close</button></div>`, async s => {
    flushAnswers();
    let rows;
    try { rows = await rpc("question_stats_admin", { p_min: 1 }); } catch (e) { $("#qsMsg", s).textContent = /function|schema cache|404/i.test(errText(e)) ? "The stats table isn't set up yet. Run supabase/004_question_stats.sql in Supabase first." : "Couldn't load stats: " + errText(e); return; }
    rows = rows || [];
    const MIN = 20, ripe = rows.filter(r => r[1] >= MIN), pct = r => Math.round(r[2] / r[1] * 100);
    const low = ripe.filter(r => pct(r) < 15), high = ripe.filter(r => pct(r) > 95);
    const total = rows.reduce((a, r) => a + r[1], 0);
    const line = r => {
      const q = anyQ(r[0]), wrong = r[3].map((n, k) => [n, k]).filter(([, k]) => !q || k !== q.a).sort((a, b) => b[0] - a[0])[0];
      const top = wrong && wrong[0] ? ` · most-picked${q ? " wrong" : ""}: ${"ABCD"[wrong[1]]} (${Math.round(wrong[0] / r[1] * 100)}%)` : "";
      return `<div class="panel" style="padding:10px"><div class="row" style="justify-content:space-between;flex-wrap:nowrap"><b>${esc(r[0])}</b><span><b>${pct(r)}%</b> <span class="small muted">of ${r[1]}</span></span></div>
        ${q ? `<p class="small" style="margin:4px 0 0">${esc(String(q.q).replace(/<[^>]+>/g, "").slice(0, 140))}</p><p class="small muted" style="margin:2px 0 0">Key: ${"ABCD"[q.a]}${top}</p>` : top ? `<p class="small muted" style="margin:4px 0 0">${top.slice(3)}</p>` : ""}</div>`;
    };
    const block = (title, note, list) => `<h3>${title} (${list.length})</h3><p class="small muted" style="margin-top:0">${note}</p>${list.slice(0, 40).map(line).join("") || '<p class="small muted">None yet.</p>'}`;
    $("#qsMsg", s).textContent = `${rows.length.toLocaleString()} questions answered ${total.toLocaleString()} times (first tries only). Flags need ${MIN}+ answers; ${ripe.length.toLocaleString()} questions have that many.`;
    $("#qsBody", s).innerHTML = block("Check the answer key", "Under 15% right. Often a wrong key, a typo or two right answers. A popular wrong choice is the usual clue.", low)
      + block("Too easy", "Over 95% right. Fine for warm-ups, but they don't train a 520.", high)
      + block("Hardest overall", "Lowest percent correct first.", ripe.filter(r => pct(r) >= 15 && pct(r) <= 95).slice(0, 20));
  });
}
document.addEventListener("click", e => { if (e.target.closest("[data-adqstats]") && isAdmin()) qstatsSheet(); });

/* ---------- question reports: students flag a problem in the app (supabase/005_question_reports.sql) ---------- */
const QREASONS = [["key", "Wrong answer key"], ["typo", "Typo or symbol"], ["unclear", "Unclear wording"], ["fact", "Outdated or wrong fact"], ["figure", "Figure problem"], ["other", "Something else"]];
const qText = q => String((q && q.q) || "").replace(/<[^>]+>/g, "").slice(0, 160);
function reportMail(id, why, note) {
  const q = anyQ(id), body = `Question ID: ${id}\nQuestion: ${qText(q)}\nProblem: ${why}\n\n${note}\n`;
  location.href = `mailto:${CONFIG.supportEmail}?subject=${encodeURIComponent("Problem with question " + id)}&body=${encodeURIComponent(body)}`;
}
function reportSheet(id) {
  let reason = "";
  sheet(`<div class="eyebrow">Report a problem · ${esc(id)}</div><h2>What's wrong with this question?</h2>
    <div class="row" id="qrReasons">${QREASONS.map(([k, l]) => `<button class="chipbtn" data-qr="${k}" aria-pressed="false">${l}</button>`).join("")}</div>
    <textarea id="qrNote" rows="4" maxlength="1000" style="width:100%" placeholder="Optional: what should it say? Which choice is right?"></textarea>
    <p class="small muted" style="margin:0">We read every report and fix the question for everyone. Thank you.</p>
    <div class="row"><button class="btn primary" data-qrsend style="flex:1" disabled>Send report</button><button class="btn" data-close style="flex:1">Cancel</button></div>`, s => {
    $("#qrReasons", s).addEventListener("click", e => {
      const b = e.target.closest("[data-qr]"); if (!b) return;
      reason = b.dataset.qr; s.querySelectorAll("[data-qr]").forEach(x => x.setAttribute("aria-pressed", x === b)); $("[data-qrsend]", s).disabled = false;
    });
    $("[data-qrsend]", s).addEventListener("click", () => {
      const note = $("#qrNote", s).value.trim(), why = (QREASONS.find(r => r[0] === reason) || ["", ""])[1];
      const close = () => { $("#sheetHost").innerHTML = ""; };
      if (!SB_URL || !navigator.onLine) { close(); return reportMail(id, why, note); }
      $("[data-qrsend]", s).disabled = true;
      fetch(SB_URL + "/rest/v1/rpc/report_question", { method: "POST", headers: { apikey: SB_KEY, "Content-Type": "application/json" }, body: JSON.stringify({ p_dev: deviceId(), p_qid: id, p_reason: reason, p_note: note }) })
        .then(r => r.ok ? r.json() : Promise.reject(r.status))
        .then(ok => { if (!ok) throw "refused"; close(); toast("Thanks. Your report was sent, and we'll fix it for everyone."); })
        .catch(() => { close(); reportMail(id, why, note); });
    });
  });
}
document.addEventListener("click", e => { const b = e.target.closest("[data-qreport]"); if (b) reportSheet(b.dataset.qreport); });

/* Admin: open reports grouped by question, most-reported first, with Fixed / Dismiss. */
function reportsSheet() {
  sheet(`<div class="eyebrow">Admin</div><h2>Reported questions</h2><p class="small muted" id="qrMsg">Loading…</p><div id="qrBody" class="stack"></div><div class="row"><button class="btn ghost" data-close>Close</button></div>`, async s => {
    let rows;
    try { rows = await rpc("question_reports_admin", { p_status: "open" }); } catch (e) { $("#qrMsg", s).textContent = /function|schema cache|404/i.test(errText(e)) ? "Reports aren't set up yet. Run supabase/005_question_reports.sql in Supabase first." : "Couldn't load reports: " + errText(e); return; }
    rows = rows || [];
    const by = {}; rows.forEach(r => (by[r[1]] = by[r[1]] || []).push(r));
    const ids = Object.keys(by).sort((a, b) => by[b].length - by[a].length);
    const label = r => (QREASONS.find(x => x[0] === r[2]) || ["", r[2]])[1];
    $("#qrMsg", s).textContent = ids.length ? `${rows.length} open report${rows.length === 1 ? "" : "s"} on ${ids.length} question${ids.length === 1 ? "" : "s"}, most-reported first.` : "No open reports.";
    $("#qrBody", s).innerHTML = ids.map(id => {
      const q = anyQ(id), list = by[id];
      return `<div class="panel" style="padding:10px" data-qrrow="${esc(id)}"><div class="row" style="justify-content:space-between;flex-wrap:nowrap"><b>${esc(id)}</b><span class="small">${list.length} report${list.length === 1 ? "" : "s"}</span></div>
        ${q ? `<p class="small" style="margin:4px 0 0">${esc(qText(q))}</p><p class="small muted" style="margin:2px 0 0">Key: ${"ABCD"[q.a]}</p>` : ""}
        ${list.slice(0, 6).map(r => `<p class="small" style="margin:6px 0 0"><b>${esc(label(r))}</b>${r[3] ? ": " + esc(r[3]) : ""}</p>`).join("")}
        <div class="row" style="margin-top:8px"><button class="btn small" data-qrres="fixed" data-qid="${esc(id)}">Fixed</button><button class="btn small ghost" data-qrres="dismissed" data-qid="${esc(id)}">Dismiss</button></div></div>`;
    }).join("");
    $("#qrBody", s).addEventListener("click", async e => {
      const b = e.target.closest("[data-qrres]"); if (!b) return;
      b.disabled = true;
      try { await rpc("resolve_question_reports", { p_qid: b.dataset.qid, p_status: b.dataset.qrres }); const row = b.closest("[data-qrrow]"); if (row) row.remove(); toast(b.dataset.qrres === "fixed" ? "Marked fixed." : "Dismissed."); }
      catch (err) { b.disabled = false; toast("Couldn't update: " + esc(errText(err))); }
    });
  });
}
document.addEventListener("click", e => { if (e.target.closest("[data-adqreports]") && isAdmin()) reportsSheet(); });

/* ---------- real MCAT results: students report their real score (supabase/006_mcat_results.sql) ---------- */
// The app saves what it estimated at that moment, so real scores can correct the estimate for everyone later.
const CAL_STORE = "quest520.cal", CAL_MIN = 30;
let CALIB = null;
function loadCalib() {
  if (CALIB || !SB_URL) return;
  let c = null; try { c = JSON.parse(lsGet(CAL_STORE) || "null"); } catch (e) {}
  CALIB = (c && c.d) || {};
  if (c && Date.now() - c.t < 24 * 3600000) return;
  fetch(SB_URL + "/rest/v1/rpc/score_calibration", { method: "POST", headers: { apikey: SB_KEY, "Content-Type": "application/json" }, body: "{}" })
    .then(r => r.ok ? r.json() : null).then(d => { if (d && typeof d === "object") { CALIB = d; lsSet(CAL_STORE, JSON.stringify({ t: Date.now(), d })); } }).catch(() => {});
}
// Shift a section's passage-based estimate by the average real-minus-estimated gap, once 30+ students reported.
function calibOff(sec) {
  loadCalib();
  const c = CALIB && CALIB[sec]; if (!c || c[0] < CAL_MIN) return 0;
  return Math.max(-4, Math.min(4, Math.round(c[1])));
}
function realScorePanelHTML() {
  const r = S.realScore;
  return `<div class="panel"><div class="row" style="justify-content:space-between"><h3 style="margin:0">Took the real MCAT?</h3><button class="btn small" data-realscore>${r ? "Update my score" : "Share my score"}</button></div>
    <p class="small muted" style="margin:6px 0 0">${r ? `You reported ${r.total}${r.month ? " (" + esc(r.month) + ")" : ""}. Thank you.` : "Tell us your real score. It makes the score range more accurate for every student. Only the numbers are sent, never your name or email."}</p></div>`;
}
function realScoreSheet() {
  const r = S.realScore || {}, sec = (k, l) => `<label class="small" style="display:grid;gap:4px">${l}<input type="number" id="rs${k}" min="118" max="132" inputmode="numeric" value="${r[k] || ""}" placeholder="118-132"></label>`;
  sheet(`<div class="eyebrow">Real MCAT score</div><h2>How did you do?</h2>
    <label class="small" style="display:grid;gap:4px">Total score<input type="number" id="rsTotal" min="472" max="528" inputmode="numeric" value="${r.total || ""}" placeholder="472-528"></label>
    <div class="grid2">${sec("CP", "Chem/Phys")}${sec("CARS", "CARS")}${sec("BB", "Bio/Biochem")}${sec("PS", "Psych/Soc")}</div>
    <label class="small" style="display:grid;gap:4px">Month you tested<input type="month" id="rsMonth" value="${esc(r.month || "")}"></label>
    <p class="small muted" style="margin:0">Section scores are optional but help the most.</p>
    <div class="row"><button class="btn primary" data-rssend style="flex:1">Send</button><button class="btn" data-close style="flex:1">Cancel</button></div>`, s => {
    $("[data-rssend]", s).addEventListener("click", () => {
      const num = id => { const v = +$(id, s).value; return v ? Math.round(v) : null; };
      const total = num("#rsTotal"); if (!total || total < 472 || total > 528) return toast("Enter a total between 472 and 528.");
      const secs = {}; let bad = false;
      ["CP", "CARS", "BB", "PS"].forEach(k => { const v = num("#rs" + k); if (v == null) return; if (v < 118 || v > 132) bad = true; else secs[k] = v; });
      if (bad) return toast("Section scores run from 118 to 132.");
      const month = $("#rsMonth", s).value || null, est = {};
      ["CP", "CARS", "BB", "PS"].forEach(k => { const e = estimate(k); if (e) est[k] = e.raw || e.mid; }); // uncorrected, so the correction never feeds on itself
      const exams = (S.examHist || []).length, answered = S.total || 0;
      S.realScore = Object.assign({ total, month, at: Date.now() }, secs); save();
      $("#sheetHost").innerHTML = ""; if (!$("#view-me").hidden) renderMe();
      if (!SB_URL) return toast("Saved on this device.");
      fetch(SB_URL + "/rest/v1/rpc/report_mcat", { method: "POST", headers: { apikey: SB_KEY, "Content-Type": "application/json" },
        body: JSON.stringify({ p_dev: deviceId(), p_total: total, p_secs: secs, p_month: month, p_est: est, p_answered: answered, p_exams: exams }) })
        .then(r => r.ok ? r.json() : Promise.reject(r.status)).then(ok => toast(ok ? "Thank you. Your score helps every student get a truer estimate." : "Saved on this device; the server didn't accept it."))
        .catch(() => toast("Saved on this device. We couldn't reach the server, so it wasn't shared."));
    });
  });
}
document.addEventListener("click", e => { if (e.target.closest("[data-realscore]")) realScoreSheet(); });

/* Admin: real scores next to what the app estimated. */
function mcatAdminSheet() {
  sheet(`<div class="eyebrow">Admin</div><h2>Real MCAT results</h2><p class="small muted" id="mrMsg">Loading…</p><div id="mrBody"></div><div class="row"><button class="btn ghost" data-close>Close</button></div>`, async s => {
    let rows;
    try { rows = await rpc("mcat_results_admin"); } catch (e) { $("#mrMsg", s).textContent = /function|schema cache|404/i.test(errText(e)) ? "Not set up yet. Run supabase/006_mcat_results.sql in Supabase first." : "Couldn't load: " + errText(e); return; }
    rows = rows || [];
    const secs = ["CP", "CARS", "BB", "PS"], idx = { CP: 1, CARS: 2, BB: 3, PS: 4 };
    const gap = k => { const g = rows.filter(r => r[idx[k]] && r[6] && r[6][k]).map(r => r[idx[k]] - r[6][k]); return g.length ? `${k}: ${g.length} · avg gap ${(g.reduce((a, b) => a + b, 0) / g.length).toFixed(1)}` : `${k}: none yet`; };
    $("#mrMsg", s).textContent = `${rows.length} result${rows.length === 1 ? "" : "s"}. Real minus estimated, per section: ${secs.map(gap).join(" · ")}. The app adjusts a section once ${CAL_MIN}+ students with 300+ answers report it.`;
    $("#mrBody", s).innerHTML = rows.slice(0, 100).map(r => `<div class="panel" style="padding:10px"><b>${r[0]}</b> <span class="small muted">${esc(r[5] || "")} · ${r[7]} answered · ${r[8]} exams</span>
      <p class="small" style="margin:4px 0 0">${secs.map(k => `${k} ${r[idx[k]] || "–"}${r[6] && r[6][k] ? " (est " + r[6][k] + ")" : ""}`).join(" · ")}</p></div>`).join("");
  });
}
document.addEventListener("click", e => { if (e.target.closest("[data-admcat]") && isAdmin()) mcatAdminSheet(); });

/* ---------- start ---------- */
(function initAccount() {
  if (ACCT.state === "off") return;
  const k = lsGet(CK_STORE); if (k) useKey(k);
  if (lsGet(SB_STORE)) sbLoad().then(sb => sb.auth.getSession()).then(r => { const u = r.data && r.data.session && r.data.session.user; if (u && (!ACCT.user || ACCT.user.id !== u.id)) signedIn(u); }).catch(() => {});
})();
