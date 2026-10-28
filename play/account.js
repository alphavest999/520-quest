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
    flushDuelLink();
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

/* ---------- 1v1 duels ---------- */
const DU = { list: null, battle: null, cat: "BB" };
const DUEL_N = 10, DUEL_SECS = 60;
const DUEL_CATS = [["BB", "Bio/Biochem"], ["CP", "Chem/Phys"], ["PS", "Psych/Soc"], ["ALL", "Mixed"]];
const duelCatName = c => (DUEL_CATS.find(x => x[0] === c) || [, "Mixed"])[1];
const duelLink = code => (CONFIG.appUrl || location.origin + "/").replace(/\/?$/, "/") + "duel/" + String(code).replace(/\D/g, "");
const duelErr = e => {
  const m = errText(e);
  if (/duel limit/.test(m)) return isPaid() ? "Duel limit reached." : "Free accounts get 3 duels a day in Bio/Biochem. Any plan unlocks unlimited duels in every section.";
  if (/not found/.test(m)) return "No duel has that code. Check the 4 digits.";
  if (/taken/.test(m)) return "Someone already accepted that duel.";
  if (/expired/.test(m)) return "That duel expired. Duels last 24 hours.";
  return "Couldn't reach the duel server. Check your connection and try again.";
};
function pickDuelQs(cat) {
  const pool = QUESTIONS.filter(q => QBYID[q.id] && q.o && q.o.length === 4 && (cat === "ALL" ? q.s !== "CARS" : q.s === cat));
  for (let i = pool.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [pool[i], pool[j]] = [pool[j], pool[i]]; }
  return pool.slice(0, DUEL_N).map(q => q.id);
}
const myDuelSide = d => d.player1_id === ACCT.user.id ? 1 : 2;
function duelView(d) {
  const me = myDuelSide(d), my = d["player" + me + "_score"], opp = d["player" + (3 - me) + "_score"], oppName = d["player" + (3 - me) + "_name"] || (d.mode === "random" ? "a random opponent" : "your friend");
  if (d.status === "completed") {
    const won = d.winner_id === ACCT.user.id, tie = !d.winner_id;
    return { line: `${tie ? "Tie" : won ? "You won" : "You lost"} ${my ?? "–"}–${opp ?? "–"} vs ${esc(oppName)}`, btn: `<button class="btn small" data-duelres="${esc(d.id)}">Results</button>`, done: true };
  }
  if (d.status === "expired") return { line: "Expired: nobody played", btn: "" };
  if (my == null) return { line: `Your turn vs ${esc(oppName)}`, btn: `<button class="btn small primary" data-duelplay="${esc(d.id)}">Play</button>` };
  if (d.mode === "friend" && !d.player2_id) return { line: `You scored ${my}/10. Waiting for a friend to accept <b>${esc(d.invite_code || "")}</b>`, btn: d.invite_code ? `<button class="btn small" data-duelshare="${esc(d.invite_code)}">Invite</button>` : "" };
  if (!d.player2_id) return { line: `You scored ${my}/10. Finding an opponent at your level…`, btn: "" };
  return { line: `You scored ${my}/10. Waiting for ${esc(oppName)} to play`, btn: "" };
}
window.duelPanelHTML = () => {
  if (!CONFIG.flags.DUEL_ENABLED || ACCT.state === "off") return "";
  const crown = (S.crownUntil || 0) > Date.now() ? ` <span title="Duel Crown: you won a duel in the last 24 hours">👑</span>` : "";
  const head = `<div class="panel" id="duelPanel"><h3>⚔️ 1v1 Duels${crown}</h3><p class="small muted">10 questions, 60 seconds each. Play on your own time; your opponent's score stays hidden until you've played. Win +200 XP, tie +100, loss +50.</p>`;
  if (ACCT.state === "out") return head + `<div class="row"><button class="btn primary small" data-acin>Sign in to duel</button></div></div>`;
  if (ACCT.state === "blocked") return head + `<p class="small">Duels need this device on your account.</p><div class="row"><button class="btn small" data-acdevices>Manage devices</button></div></div>`;
  const paid = isPaid(); if (!paid) DU.cat = "BB";
  if (DU.list === null) loadDuels();
  return head + `<label class="field" for="duelCat">Section<select id="duelCat" ${paid ? "" : "disabled"}>${DUEL_CATS.map(([c, n]) => `<option value="${c}" ${DU.cat === c ? "selected" : ""}>${n}</option>`).join("")}</select></label>
    ${paid ? "" : `<p class="small muted" style="margin:0">Free: 3 duels a day in Bio/Biochem. Any plan unlocks every section, unlimited.</p>`}
    <div class="row"><button class="btn primary" data-duelrandom>Random match</button><button class="btn" data-duelfriend>Challenge a friend</button></div>
    <div class="row"><input type="text" id="duelCode" placeholder="DUEL-1234" inputmode="numeric" autocomplete="off" style="flex:1;min-width:0;max-width:180px"><button class="btn small" data-dueljoin>Accept</button></div>
    <div class="stack" id="duelList" style="gap:8px">${duelListHTML()}</div></div>`;
};
function duelListHTML() {
  if (DU.list === null) return `<p class="small muted">Loading your duels…</p>`;
  if (!DU.list.length) return `<p class="small muted">No duels yet. Start one above.</p>`;
  return DU.list.slice(0, 12).map(d => { const v = duelView(d); return `<div class="row" style="justify-content:space-between;flex-wrap:nowrap;gap:10px"><span class="small" style="min-width:0">${v.line} <span class="muted">· ${esc(duelCatName(d.category))}</span></span>${v.btn}</div>`; }).join("");
}
async function loadDuels() {
  DU.list = DU.list || null;
  try { DU.list = await rpc("my_duels") || []; } catch (e) { DU.list = DU.list || []; }
  DU.list.forEach(awardDuel);
  const el = $("#duelList"); if (el) el.innerHTML = duelListHTML();
}
const duelCode = v => { const d = String(v || "").replace(/\D/g, ""); return d.length === 4 ? "DUEL-" + d : ""; };
async function startDuel(kind, code) {
  if (ACCT.state !== "in") return signIn("Duels");
  await bankReady.catch(() => {});
  try {
    let d;
    if (kind === "random") d = await rpc("duel_random", { p_questions: pickDuelQs(DU.cat), p_category: DU.cat });
    else if (kind === "friend") d = await rpc("create_duel", { p_questions: pickDuelQs(DU.cat), p_category: DU.cat });
    else if (kind === "rematch") d = await rpc("create_duel", { p_questions: pickDuelQs(code.cat), p_category: code.cat, p_opponent: code.opp });
    else d = await rpc("join_duel", { p_code: code });
    DU.list = null;
    if (kind === "friend") return duelInvite(d, true);
    duelIntro(d);
  } catch (e) { toast(duelErr(e), 4200); }
}
function duelInvite(d, first) {
  sheet(`<div class="eyebrow">Challenge a friend</div><h2>${esc(d.invite_code)}</h2><p class="muted">Send your friend this link. They have 24 hours to accept. ${first ? "Play your round now or after they accept; nobody sees the other's score until both have played." : ""}</p>
    <div class="row"><button class="btn primary" data-duelshare="${esc(d.invite_code)}">Share invite</button>${first ? `<button class="btn" data-close data-duelplay="${esc(d.id)}">Play my round</button>` : ""}<button class="btn ghost" data-close>Later</button></div>`);
}
function shareInvite(code) {
  const url = duelLink(code), txt = `Your friend challenged you to a MCAT duel - Accept with 100 free Qs`;
  if (navigator.share) navigator.share({ text: txt, url }).catch(() => {}); else copy(txt + " " + url, () => toast("Invite copied. Paste it to your friend."));
}
function duelIntro(d) {
  const me = myDuelSide(d), oppName = d["player" + (3 - me) + "_name"];
  if (d["player" + me + "_score"] != null) { toast("You've already played this duel. Results show when your opponent finishes."); return renderBossLobby(); }
  go("boss");
  $("#view-boss").innerHTML = `<div class="stack"><div class="eyebrow">Duel · ${esc(duelCatName(d.category))}</div><h2 class="title">${oppName ? `${esc(oppName)} vs you` : d.mode === "random" ? "Random match" : "Your challenge"}</h2>
    <p class="muted">${DUEL_N} questions, ${DUEL_SECS} seconds each. Ties go to the faster player. ${d.player2_id || me === 2 ? "" : d.mode === "random" ? "No opponent free right now, so you'll play first and we'll match you with someone at your level." : ""}</p>
    <div class="row"><button class="btn primary" data-duelgo>Start duel</button><button class="btn ghost" data-duelback>Not now</button></div></div>`;
  DU.pending = d;
}
async function duelBattle(d) {
  await bankReady.catch(() => {});
  const qs = (d.questions || []).map(id => QBYID[id]).filter(Boolean);
  if (qs.length < d.questions.length) return toast("This duel's questions are still loading. Try again in a moment.");
  DU.battle = { d, qs, i: 0, answers: [], score: 0, time: 0 };
  duelTurn();
}
function duelTurn() {
  const b = DU.battle; clearInterval(b.tick);
  if (b.i >= b.qs.length) return duelSubmit();
  const q = shuf(b.qs[b.i]); b.start = Date.now();
  $("#view-boss").innerHTML = `<div class="arena"><div class="row" style="justify-content:space-between"><span class="small muted">⚔️ Duel · Question ${b.i + 1} of ${b.qs.length}</span><span class="timer" id="dt">1:00</span></div>
    <div class="row" style="justify-content:space-between"><b>${b.score} right</b><span class="small muted">Opponent's score hidden</span></div>
    <article class="card" style="min-height:0"><div class="card-top"><span class="tag sec">${SECTIONS[q.s].name}</span><span class="tag">${q.c}</span>${diffDots(q.d)}</div><h2 class="stem">${q.q}</h2><div class="opts" id="dopts">${optsHTML(q)}</div><div class="reveal stack" hidden></div></article></div>`;
  const box = $("#dopts");
  const finish = i => {
    if (box.dataset.done) return; box.dataset.done = 1; clearInterval(b.tick);
    const secs = Math.min(DUEL_SECS, Math.round((Date.now() - b.start) / 1000)), ok = i === q.a;
    b.time += secs; b.answers.push(ok ? 1 : 0); if (ok) b.score++;
    $$(".opt", box).forEach((o, j) => { o.disabled = true; if (j === q.a) o.classList.add("right"); else if (j === i) o.classList.add("wrong"); });
    beep(ok ? "good" : "bad");
    const rv = $(".reveal", box.parentNode); rv.hidden = false;
    rv.innerHTML = `<div class="verdict ${ok ? "ok" : "no"}">${i < 0 ? "Time's up" : ok ? "Correct" : "Answer: " + "ABCD"[q.a]}</div><div class="row"><button class="btn primary" id="dnext">${b.i + 1 >= b.qs.length ? "Lock in my score" : "Next question"}</button></div>`;
    $("#dnext").addEventListener("click", () => { b.i++; duelTurn(); });
  };
  box.addEventListener("click", e => { const o = e.target.closest(".opt"); if (o) finish(+o.dataset.i); });
  b.tick = setInterval(() => {
    const left = Math.max(0, DUEL_SECS - Math.floor((Date.now() - b.start) / 1000)), t = $("#dt");
    if (!t) return clearInterval(b.tick);
    t.textContent = Math.floor(left / 60) + ":" + String(left % 60).padStart(2, "0"); t.classList.toggle("low", left <= 10);
    if (left <= 0) finish(-1);
  }, 250);
}
async function duelSubmit() {
  const b = DU.battle;
  $("#view-boss").innerHTML = `<div class="stack"><div class="eyebrow">Duel</div><h2 class="title">${b.score}/${b.qs.length}</h2><p class="muted">Locking in your score…</p></div>`;
  let d;
  for (let k = 0; k < 3 && !d; k++) { try { d = await rpc("submit_duel", { p_id: b.d.id, p_answers: b.answers, p_score: b.score, p_time: b.time }); } catch (e) { await new Promise(r => setTimeout(r, 1500)); } }
  DU.battle = null; DU.list = null;
  if (!d) { $("#view-boss").innerHTML = `<div class="stack"><h2 class="title">Couldn't save your score</h2><p class="muted">Check your connection. Your duel stays open for 24 hours, so you can replay it from the duel list.</p><div class="row"><button class="btn primary" data-duelback>Back to duels</button></div></div>`; return; }
  if (d.status === "completed") return duelResult(d);
  const me = myDuelSide(d), oppName = d["player" + (3 - me) + "_name"];
  $("#view-boss").innerHTML = `<div class="stack"><div class="eyebrow">Score locked in</div><h2 class="title">${b.score}/${b.qs.length} in ${b.time} s</h2>
    <p class="muted">${oppName ? `${esc(oppName)} hasn't played yet.` : d.mode === "random" ? "We're matching you with a player at your level." : "Your friend hasn't accepted yet."} You'll see who won here when they finish. If nobody plays within 24 hours, you win by default.</p>
    <div class="row">${d.mode === "friend" && !d.player2_id && d.invite_code ? `<button class="btn primary" data-duelshare="${esc(d.invite_code)}">Share invite</button>` : ""}<button class="btn" data-duelback>Back to duels</button></div></div>`;
}
function awardDuel(d) {
  if (d.status !== "completed" || !ACCT.user) return;
  S.duelXP = S.duelXP || {}; if (S.duelXP[d.id]) return;
  const won = d.winner_id === ACCT.user.id, tie = !d.winner_id, xp = won ? 200 : tie ? 100 : 50;
  S.duelXP[d.id] = 1;
  if (won) S.crownUntil = Date.now() + DAY;
  addXP(xp);
  save(); toast(`Duel ${won ? "won" : tie ? "tied" : "finished"}: <b>+${xp} XP</b>${won ? " and the 👑 Duel Crown for 24 hours" : ""}`, 3600);
}
function duelResult(d) {
  awardDuel(d);
  const me = myDuelSide(d), my = d["player" + me + "_score"], opp = d["player" + (3 - me) + "_score"], oppName = d["player" + (3 - me) + "_name"] || "Opponent";
  const won = d.winner_id === ACCT.user.id, tie = !d.winner_id, oppId = d["player" + (3 - me) + "_id"];
  if (won && !reduce) confetti();
  go("boss");
  $("#view-boss").innerHTML = `<div class="stack"><div class="eyebrow">Duel result · ${esc(duelCatName(d.category))}</div><h2 class="title">${tie ? "It's a tie" : won ? "👑 You win!" : `${esc(oppName)} wins`}</h2>
    <div class="grid2"><div class="panel stat"><b>${my ?? "–"}</b><span>You${d["player" + me + "_time"] != null ? ", " + d["player" + me + "_time"] + " s" : ""}</span></div><div class="panel stat"><b>${opp ?? "–"}</b><span>${esc(oppName)}${d["player" + (3 - me) + "_time"] != null ? ", " + d["player" + (3 - me) + "_time"] + " s" : ""}</span></div></div>
    <p class="muted">${won ? "+200 XP and the Duel Crown for 24 hours." : tie ? "+100 XP." : "+50 XP for showing up. Rematch?"}</p>
    <div class="row">${oppId ? `<button class="btn primary" data-duelrematch="${esc(oppId)}" data-cat="${esc(d.category)}">Rematch</button>` : ""}<button class="btn" data-duelimg="${esc(d.id)}">Share result</button><button class="btn ghost" data-duelback>Back to duels</button></div></div>`;
  DU.last = d;
}
function duelShareImg(d) {
  const me = myDuelSide(d), my = d["player" + me + "_score"], opp = d["player" + (3 - me) + "_score"], oppName = d["player" + (3 - me) + "_name"] || "my opponent";
  const won = d.winner_id === ACCT.user.id, tie = !d.winner_id;
  const c = document.createElement("canvas"); c.width = 1080; c.height = 1080; const g = c.getContext("2d");
  const grd = g.createLinearGradient(0, 0, 1080, 1080); grd.addColorStop(0, "#11100c"); grd.addColorStop(1, "#29261d"); g.fillStyle = grd; g.fillRect(0, 0, 1080, 1080);
  g.fillStyle = "#facc15"; g.beginPath(); g.arc(120, 120, 46, 0, 7); g.fill(); g.fillStyle = "#1a1500"; g.font = "800 30px sans-serif"; g.textAlign = "center"; g.fillText("520", 120, 131);
  g.textAlign = "left"; g.fillStyle = "#f6f1e3"; g.font = "800 38px sans-serif"; g.fillText("520 Quest", 186, 133);
  g.textAlign = "center"; g.fillStyle = "#facc15"; g.font = "800 64px sans-serif"; g.fillText(tie ? "MCAT DUEL: TIE" : won ? "👑 MCAT DUEL WON" : "MCAT DUEL", 540, 380);
  g.fillStyle = "#f6f1e3"; g.font = "800 220px sans-serif"; g.fillText(`${my}–${opp}`, 540, 640);
  g.font = "600 44px sans-serif"; g.fillText("vs " + String(oppName).slice(0, 24), 540, 740);
  g.fillStyle = "#aaa38f"; g.font = "600 36px sans-serif"; g.fillText("Think you can beat me? 520Quest.com", 540, 980);
  c.toBlob(async blob => {
    const file = new File([blob], "520quest-duel.png", { type: "image/png" }), txt = `I ${tie ? "tied" : won ? "won" : "played"} a 520 Quest MCAT duel ${my}–${opp}. Think you can beat me? 520Quest.com`;
    try {
      if (navigator.canShare && navigator.canShare({ files: [file] })) await navigator.share({ files: [file], text: txt });
      else { const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = file.name; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); }
    } catch (e) {}
  }, "image/png");
}
document.addEventListener("click", e => {
  const t = e.target;
  if (t.closest("[data-duelrandom]")) return startDuel("random");
  if (t.closest("[data-duelfriend]")) return startDuel("friend");
  if (t.closest("[data-dueljoin]")) { const c = duelCode(($("#duelCode") || {}).value); return c ? startDuel("join", c) : toast("Enter the 4-digit duel code."); }
  const sh = t.closest("[data-duelshare]"); if (sh) return shareInvite(sh.dataset.duelshare);
  const pl = t.closest("[data-duelplay]"); if (pl) { const d = (DU.list || []).find(x => x.id === pl.dataset.duelplay) || (DU.pending && DU.pending.id === pl.dataset.duelplay ? DU.pending : null); if (d) { $("#sheetHost").innerHTML = ""; duelIntro(d); } else rpc("my_duels").then(l => { DU.list = l; const x = l.find(y => y.id === pl.dataset.duelplay); if (x) duelIntro(x); }).catch(() => toast(duelErr())); return; }
  if (t.closest("[data-duelgo]")) return DU.pending && duelBattle(DU.pending);
  if (t.closest("[data-duelback]")) { DU.pending = null; DU.list = null; return renderBossLobby(); }
  const rs = t.closest("[data-duelres]"); if (rs) { const d = (DU.list || []).find(x => x.id === rs.dataset.duelres); if (d) duelResult(d); return; }
  const rm = t.closest("[data-duelrematch]"); if (rm) return startDuel("rematch", { opp: rm.dataset.duelrematch, cat: rm.dataset.cat });
  if (t.closest("[data-duelimg]") && DU.last) return duelShareImg(DU.last);
});
document.addEventListener("change", e => { if (e.target.id === "duelCat") DU.cat = e.target.value; });
document.addEventListener("keydown", e => { if (e.target.id === "duelCode" && e.key === "Enter") { const c = duelCode(e.target.value); if (c) startDuel("join", c); } });
// Leaving the Boss tab mid-duel abandons the round; the duel stays open to replay from the list.
$(".tabs").addEventListener("click", () => { if (DU.battle && $("#view-boss").hidden) { clearInterval(DU.battle.tick); DU.battle = null; } });

/* ---------- duel links: 520quest.com/duel/1234 lands on /play/#duel=1234 ---------- */
let duelFromLink = (location.hash.match(/^#duel=(\d{4})$/) || [])[1] || null;
function flushDuelLink() {
  if (!duelFromLink || ACCT.state !== "in") return;
  const c = "DUEL-" + duelFromLink; duelFromLink = null;
  try { history.replaceState(null, "", "#boss"); } catch (e) {}
  startDuel("join", c);
}

/* ---------- start ---------- */
(function initAccount() {
  if (ACCT.state === "off") return;
  const k = lsGet(CK_STORE); if (k) useKey(k);
  if (duelFromLink) {
    go("boss");
    sheet(`<div class="eyebrow">Duel challenge</div><h2>Your friend challenged you to a MCAT duel</h2><p class="muted">10 questions, 60 seconds each. Sign in with your email to accept; new players get 100 free questions too.</p>
      <div class="row"><button class="btn primary" data-close data-acin>Accept the duel</button><button class="btn ghost" data-close>Not now</button></div>`);
  }
  if (lsGet(SB_STORE) || duelFromLink) sbLoad().then(sb => sb.auth.getSession()).then(r => { const u = r.data && r.data.session && r.data.session.user; if (u && (!ACCT.user || ACCT.user.id !== u.id)) signedIn(u); }).catch(() => {});
})();
