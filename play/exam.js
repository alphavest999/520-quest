/* Timed exam mode: FL01-FL10 (4 sections) and Mini01-Mini10 (1 section). Runs inside #view-exam of index.html. */
(() => {
  const SEC = { CP: { name: "Chem/Phys", min: 95 }, CARS: { name: "CARS", min: 90 }, BB: { name: "Bio/Biochem", min: 95 }, PS: { name: "Psych/Soc", min: 95 } };
  const FL_ORDER = ["CP", "CARS", "BB", "PS"];
  const BREAKS = [{ min: 10, label: "10-minute break" }, { min: 30, label: "30-minute lunch break" }, { min: 10, label: "10-minute break" }];
  const FREE = "Mini01";
  const pad = n => String(n).padStart(2, "0");
  const fmt = s => { s = Math.max(0, Math.ceil(s)); const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60); return (h ? h + ":" + pad(m) : pad(m)) + ":" + pad(s % 60); };
  const num = id => +(id.match(/(\d+)$/) || [0, 0])[1];
  const cap = t => t ? t.charAt(0).toUpperCase() + t.slice(1) : t;
  const scaled = pct => pct <= .25 ? 118 : Math.min(132, Math.round(118 + 14 * Math.pow((pct - .25) / .75, .85)));
  const root = () => document.getElementById("view-exam");

  /* ---------- catalog from the loaded bank ---------- */
  let CAT_X = null;
  function catalog() {
    if (CAT_X) return CAT_X;
    const ids = new Set();
    PASSAGES.forEach(p => { const m = p.id.match(/^((?:FL|Mini)\d+)_/); if (m) ids.add(m[1]); });
    const list = [...ids].sort((a, b) => (a[0] === b[0] ? num(a) - num(b) : a[0] === "F" ? -1 : 1)).map(id => {
      const secs = [...new Set(PASSAGES.filter(p => p.id.startsWith(id + "_")).map(p => p.s))];
      const order = id.startsWith("FL") ? FL_ORDER.filter(s => secs.includes(s)) : secs;
      const sections = order.map(s => { const it = items(id, s); return { s, n: it.length, min: SEC[s].min }; });
      return { id, full: id.startsWith("FL"), sections, n: sections.reduce((a, s) => a + s.n, 0) };
    });
    return (CAT_X = list);
  }
  const ITEMS = {};
  function items(exam, sec) {
    const k = exam + "|" + sec; if (ITEMS[k]) return ITEMS[k];
    const ps = PASSAGES.filter(p => p.id.startsWith(exam + "_" + sec + "_P")).sort((a, b) => num(a.id) - num(b.id));
    const ds = QUESTIONS.filter(q => q.id.startsWith(exam + "_" + sec + "_D")).sort((a, b) => num(a.id) - num(b.id));
    const out = []; let used = 0;
    ps.forEach((p, i) => {
      p.qs.forEach(q => out.push({ q, p }));
      const upto = ps.length ? Math.floor((i + 1) * ds.length / ps.length) : 0;
      while (used < upto) out.push({ q: ds[used++], p: null });
    });
    while (used < ds.length) out.push({ q: ds[used++], p: null });
    return (ITEMS[k] = out);
  }

  /* ---------- state ---------- */
  const X = () => S.exam;
  const secOf = () => X().secs[X().si];
  const meta = id => catalog().find(c => c.id === id);
  const left = sec => sec.t0 ? sec.rem - (Date.now() - sec.t0) / 1000 : sec.rem;
  const canTake = id => S.pro || id === FREE;
  let tick = null;
  function stopTick() { clearInterval(tick); tick = null; }
  function persistTime() { const s = X() && X().phase === "run" && !X().paused ? secOf() : null; if (s) { s.rem = left(s); s.t0 = Date.now(); } save(); }
  function setExamingClass() { document.body.classList.toggle("examing", !!(X() && X().phase === "run" && !X().paused && !root().hidden)); }

  function newExam(id) {
    const m = meta(id);
    S.exam = { id, si: 0, phase: "intro", paused: false, started: Date.now(),
      secs: m.sections.map(s => ({ s: s.s, i: 0, rem: s.min * 60, t0: null, ans: {}, flag: {}, str: {}, done: false, used: 0 })) };
    S.examHist = S.examHist || [];
    save();
  }

  /* ---------- hub ---------- */
  function hub() {
    stopTick(); setExamingClass();
    const cat = catalog(), hist = S.examHist || [], best = id => hist.filter(h => h.id === id).reduce((b, h) => Math.max(b, h.total), 0);
    const active = X() && X().phase !== "done" ? X() : null;
    const card = c => {
      const open = canTake(c.id), b = best(c.id), run = active && active.id === c.id;
      const mins = c.sections.reduce((a, s) => a + s.min, 0), t = mins >= 120 ? Math.floor(mins / 60) + "h" + (mins % 60 ? pad(mins % 60) : "") : mins + " min";
      const label = c.full ? "Full-length " + num(c.id) : "Mini " + num(c.id) + " · " + SEC[c.sections[0].s].name;
      return `<div class="panel xcard"><div class="row" style="justify-content:space-between;flex-wrap:nowrap"><h3 style="margin:0">${esc(label)}</h3>${open ? "" : '<span class="tag sec">Plans</span>'}</div>
        <p class="small muted" style="margin:4px 0 8px">${c.n} questions · ${c.sections.length === 1 ? t : "4 sections · " + t + " testing time"}${b ? " · best " + b : ""}</p>
        <div class="row"><button class="btn primary small" data-xstart="${c.id}">${run ? "Resume" : open ? "Start" : "Unlock"}</button>${run ? `<button class="btn ghost small" data-xdrop="${c.id}">Discard attempt</button>` : ""}</div></div>`;
    };
    const fl = cat.filter(c => c.full), mn = cat.filter(c => !c.full);
    root().innerHTML = `<h2 class="title">Timed exams</h2><p class="sub">Sit a section under real timing: countdown, pause, flag, end-of-section review and a scaled score estimate. Full-lengths run Chem/Phys, CARS, Bio/Biochem, Psych/Soc with breaks. Mini exams are one section.</p>
      ${S.pro ? "" : `<div class="probanner" style="margin-bottom:14px"><p><b>PLANS</b> Mini 1 is free. Plans unlock all 10 full-lengths and the other 9 minis.</p><button class="btn small pro" data-pro>See plans</button></div>`}
      <h3 class="xh">Full-length exams</h3><div class="xgrid">${fl.map(card).join("")}</div>
      <h3 class="xh">Mini exams</h3><div class="xgrid">${mn.map(card).join("")}</div>
      <p class="small muted" style="margin-top:14px">Scaled scores are estimates: the AAMC does not publish conversion tables, so each section maps percent correct to 118-132 on a typical curve.</p>`;
  }

  /* ---------- sections ---------- */
  function introView() {
    const e = X(), s = secOf(), m = meta(e.id), n = items(e.id, s.s).length;
    const last = e.si === e.secs.length - 1;
    root().innerHTML = `<div class="xwrap"><span class="eyebrow">${esc(e.id)} · Section ${e.si + 1} of ${e.secs.length}</span><h2 class="title">${SEC[s.s].name}</h2>
      <div class="panel"><p style="margin:0"><b>${n} questions</b> · <b>${SEC[s.s].min} minutes</b></p>
      <ul class="small" style="margin:10px 0 0;padding-left:18px"><li>The timer starts when you press Begin and counts down.</li><li>Pause stops the clock and hides the questions.</li><li>Flag questions to revisit, strike out options, and use the navigator to jump around.</li><li>No answers are shown until the exam is finished. When you end a section you cannot return to it.</li></ul></div>
      <div class="row" style="margin-top:14px"><button class="btn primary" data-xbegin>Begin section</button><button class="btn ghost" data-xexit>Exit</button></div></div>`;
  }
  function begin() {
    const e = X(), s = secOf(); e.phase = "run"; e.paused = false; s.t0 = Date.now(); save();
    runView(); startTick();
  }
  function startTick() {
    stopTick(); let n = 0;
    tick = setInterval(() => {
      const e = X(); if (!e || e.phase !== "run" || e.paused) return stopTick();
      const s = secOf(), r = left(s), el = document.getElementById("xTimer");
      if (el) { el.textContent = fmt(r); el.classList.toggle("warn", r <= 300); el.classList.toggle("hot", r <= 60); }
      if (++n % 5 === 0) persistTime();
      if (r <= 0) { toast("Time is up for this section."); endSection(true); }
    }, 1000);
  }

  function qView(it, i, total, s) {
    const q = it.q, id = q.id, a = s.ans[id], st = s.str[id] || [], p = it.p;
    const firstOfP = p && (i === 0 || items(X().id, s.s)[i - 1].p !== p);
    const pass = p ? `<details class="xpass" ${firstOfP ? "open" : ""}><summary>Passage${p.title ? "" : ""} (tap to ${firstOfP ? "collapse" : "expand"})</summary>
      <div class="passage">${p.text.map(t => `<p>${esc(t)}</p>`).join("")}</div>${(p.tbl ? [].concat(p.tbl) : []).map(t => tableHTML(t)).join("")}${graphHTML(p.graph)}</details>` : "";
    const opts = q.o.map((o, k) => `<div class="xopt ${a === k ? "sel" : ""} ${st.includes(k) ? "struck" : ""}"><button class="xpick" data-xpick="${k}"><b>${"ABCD"[k]}</b><span>${o[0]}</span></button><button class="xstrike" data-xstrike="${k}" aria-label="Strike out option ${"ABCD"[k]}" title="Strike out">✕</button></div>`).join("");
    return `${pass}<div class="panel"><h3 class="xq">${q.q}</h3>${tableHTML(q.vt, "vt")}<div class="xopts">${opts}</div></div>`;
  }
  function runView() {
    const e = X(), s = secOf(), it = items(e.id, s.s), n = it.length, i = Math.min(s.i, n - 1), cur = it[i];
    const flagged = !!s.flag[cur.q.id], r = left(s);
    const ans = Object.keys(s.ans).length;
    root().innerHTML = `<div class="xbar"><div class="xtimer ${r <= 300 ? "warn" : ""} ${r <= 60 ? "hot" : ""}" id="xTimer" aria-live="off">${fmt(r)}</div>
      <div class="xmeta"><b>${SEC[s.s].name}</b><span class="small muted">Q ${i + 1} of ${n} · ${ans} answered</span></div>
      <div class="xbtns"><button class="btn small ghost" data-xflag aria-pressed="${flagged}" title="Flag for review">${flagged ? "⚑ Flagged" : "⚐ Flag"}</button><button class="btn small ghost" data-xnav>☰</button><button class="btn small ghost" data-xpause>❚❚ Pause</button></div></div>
      <div class="xbody" id="xBody">${qView(cur, i, n, s)}</div>
      <div class="xfoot"><button class="btn" data-xprev ${i === 0 ? "disabled" : ""}>← Previous</button>${i === n - 1 ? `<button class="btn primary" data-xend>End section</button>` : `<button class="btn primary" data-xnext>Next →</button>`}</div>`;
    setExamingClass();
    root().scrollTop = 0;
  }
  function goto(i) { const s = secOf(); s.i = i; save(); runView(); }
  function pauseView() {
    const e = X(); e.paused = true; const s = secOf(); s.rem = left(s); s.t0 = null; save(); stopTick();
    root().innerHTML = `<div class="xwrap xcenter"><span class="eyebrow">Paused</span><h2 class="title">Time is stopped</h2><p class="sub">${fmt(s.rem)} left in ${SEC[s.s].name}. Questions are hidden while paused.</p>
      <div class="row" style="justify-content:center"><button class="btn primary" data-xresume>Resume</button><button class="btn ghost" data-xexit>Save and exit</button></div></div>`;
  }
  function resume() { const e = X(), s = secOf(); e.paused = false; s.t0 = Date.now(); save(); runView(); startTick(); }
  function navView() {
    const e = X(), s = secOf(), it = items(e.id, s.s), cur = s.i;
    const cell = (x, i) => { const id = x.q.id, st = s.ans[id] !== undefined ? "ans" : "un"; return `<button class="xcell ${st} ${s.flag[id] ? "flag" : ""} ${i === cur ? "cur" : ""}" data-xgo="${i}">${i + 1}${s.flag[id] ? "<i>⚑</i>" : ""}</button>`; };
    const un = it.filter(x => s.ans[x.q.id] === undefined).length, fl = it.filter(x => s.flag[x.q.id]).length;
    root().innerHTML = `<div class="xwrap"><div class="row" style="justify-content:space-between"><h2 class="title" style="margin:0">Navigator</h2><span class="xtimer sm" id="xTimer">${fmt(left(s))}</span></div>
      <p class="small muted">${un} unanswered · ${fl} flagged. Tap a number to jump.</p><div class="xgridn">${it.map(cell).join("")}</div>
      <div class="row" style="margin-top:14px"><button class="btn" data-xback>Back to question ${cur + 1}</button><button class="btn ghost" data-xgounans ${un ? "" : "disabled"}>First unanswered</button><button class="btn primary" data-xend>End section</button></div></div>`;
  }
  function endConfirm() {
    const e = X(), s = secOf(), it = items(e.id, s.s), un = it.filter(x => s.ans[x.q.id] === undefined).length, fl = it.filter(x => s.flag[x.q.id]).length;
    const last = e.si === e.secs.length - 1;
    root().innerHTML = `<div class="xwrap xcenter"><span class="eyebrow">End ${SEC[s.s].name}?</span><h2 class="title">${un ? un + " unanswered" : "All questions answered"}</h2>
      <p class="sub">${fl ? fl + " flagged. " : ""}${fmt(left(s))} left. After you end the section you can't come back to it.${un ? " Unanswered questions score zero." : ""}</p>
      <div class="row" style="justify-content:center"><button class="btn" data-xback>Keep working</button><button class="btn primary" data-xconfirm>End section</button></div></div>`;
  }
  function score(e) {
    return e.secs.map(s => { const it = items(e.id, s.s), raw = it.filter(x => s.ans[x.q.id] === x.q.a).length;
      return { sec: s.s, raw, n: it.length, scaled: scaled(raw / it.length), used: s.used }; });
  }
  function endSection(timeUp) {
    const e = X(), s = secOf(); stopTick();
    s.rem = Math.max(0, left(s)); s.t0 = null; s.done = true; s.used = Math.round(SEC[s.s].min * 60 - s.rem);
    const last = e.si >= e.secs.length - 1;
    if (last) { finish(); return; }
    e.phase = "break"; e.brk = { rem: BREAKS[e.si].min * 60, t0: Date.now() }; save(); breakView();
  }
  function breakView() {
    const e = X(), b = e.brk, nxt = e.secs[e.si + 1];
    setExamingClass();
    const upd = () => { const el = document.getElementById("xBrk"); const r = b.rem - (Date.now() - b.t0) / 1000; if (el) el.textContent = fmt(r); if (r <= 0) nextSection(); };
    root().innerHTML = `<div class="xwrap xcenter"><span class="eyebrow">Section ${e.si + 1} complete</span><h2 class="title">${BREAKS[e.si].label}</h2>
      <div class="xtimer big" id="xBrk">${fmt(b.rem)}</div><p class="sub">Next: ${SEC[nxt.s].name} (${SEC[nxt.s].min} minutes). The break is optional.</p>
      <div class="row" style="justify-content:center"><button class="btn primary" data-xnext-sec>Start next section now</button></div></div>`;
    stopTick(); tick = setInterval(upd, 1000);
  }
  function nextSection() { stopTick(); const e = X(); e.si++; e.phase = "intro"; e.brk = null; save(); introView(); setExamingClass(); }
  function finish() {
    const e = X(); e.phase = "done"; e.res = score(e); const total = e.res.reduce((a, r) => a + r.scaled, 0);
    e.total = e.secs.length === 4 ? total : e.res[0].scaled;
    S.examHist = S.examHist || []; S.examHist.push({ id: e.id, date: Date.now(), res: e.res, total: e.total });
    if (e.secs.length === 4) { S.fl = S.fl || []; S.fl.push({ label: e.id, score: total }); }
    save(); setExamingClass(); resultsView();
  }

  /* ---------- results + review ---------- */
  function resultsView() {
    stopTick(); setExamingClass();
    const e = X(), full = e.secs.length === 4, tot = e.res.reduce((a, r) => a + r.raw, 0), N = e.res.reduce((a, r) => a + r.n, 0);
    const bySheet = {};
    e.secs.forEach(s => items(e.id, s.s).forEach(x => { const c = x.q.sh || (x.p && x.p.c) || x.q.c || "CARS", b = bySheet[c] = bySheet[c] || { r: 0, n: 0 }; b.n++; if (s.ans[x.q.id] === x.q.a) b.r++; }));
    const sheets = Object.entries(bySheet).sort((a, b) => a[1].r / a[1].n - b[1].r / b[1].n);
    root().innerHTML = `<div class="xwrap"><span class="eyebrow">${esc(e.id)} complete</span><h2 class="title">${full ? "Estimated score " + e.total : "Section score " + e.total}</h2>
      <p class="sub">${tot} of ${N} correct (${Math.round(tot / N * 100)}%)${full ? " · scale 472-528" : " · scale 118-132"}. This is an estimate; the AAMC does not publish conversion tables.</p>
      <div class="panel"><table class="xres"><thead><tr><th>Section</th><th>Correct</th><th>Scaled</th><th>Time</th></tr></thead><tbody>${e.res.map(r => `<tr><td>${SEC[r.sec].name}</td><td>${r.raw}/${r.n}</td><td><b>${r.scaled}</b></td><td>${fmt(r.used)}</td></tr>`).join("")}</tbody></table></div>
      <div class="panel"><h3>Weakest categories</h3><p class="small muted" style="margin-top:0">Lowest percent correct first.</p>${sheets.slice(0, 6).map(([c, b]) => `<div class="row" style="justify-content:space-between;flex-wrap:nowrap"><span>${esc(c)}</span><span class="small muted">${b.r}/${b.n}</span></div>`).join("")}</div>
      <div class="row"><button class="btn primary" data-xreview>Review answers</button><button class="btn ghost" data-xhub>Back to exams</button></div></div>`;
  }
  let rv = { si: 0, f: "all", q: null };
  function reviewView() {
    stopTick(); const e = X(), s = e.secs[rv.si], it = items(e.id, s.s);
    const st = x => s.ans[x.q.id] === undefined ? "un" : s.ans[x.q.id] === x.q.a ? "ok" : "bad";
    const show = (x, i) => rv.f === "all" || (rv.f === "bad" && st(x) === "bad") || (rv.f === "un" && st(x) === "un") || (rv.f === "flag" && s.flag[x.q.id]);
    const tabs = e.secs.map((x, i) => `<button class="chipbtn" aria-pressed="${i === rv.si}" data-xrsec="${i}">${SEC[x.s].name}</button>`).join("");
    const fil = [["all", "All"], ["bad", "Incorrect"], ["un", "Unanswered"], ["flag", "Flagged"]].map(([k, l]) => `<button class="chipbtn" aria-pressed="${rv.f === k}" data-xrf="${k}">${l}</button>`).join("");
    const body = rv.q !== null ? reviewQ(it[rv.q], rv.q, s, it.length) : `<div class="xgridn">${it.map((x, i) => show(x, i) ? `<button class="xcell ${st(x)} ${s.flag[x.q.id] ? "flag" : ""}" data-xrq="${i}">${i + 1}${s.flag[x.q.id] ? "<i>⚑</i>" : ""}</button>` : "").join("")}</div>`;
    root().innerHTML = `<div class="xwrap"><div class="row" style="justify-content:space-between"><h2 class="title" style="margin:0">Review ${esc(e.id)}</h2><button class="btn small ghost" data-xresults>Scores</button></div>
      <div class="filters" style="margin:8px 0">${tabs}</div>${rv.q === null ? `<div class="filters" style="margin:0 0 8px">${fil}</div><p class="small muted">Green: correct. Red: incorrect. Grey: unanswered.</p>` : ""}${body}</div>`;
    root().scrollTop = 0;
  }
  function reviewQ(x, i, s, n) {
    const q = x.q, a = s.ans[q.id], p = x.p;
    const pass = p ? `<details class="xpass"><summary>Passage (tap to expand)</summary><div class="passage">${p.text.map(t => `<p>${esc(t)}</p>`).join("")}</div>${(p.tbl ? [].concat(p.tbl) : []).map(t => tableHTML(t)).join("")}${graphHTML(p.graph)}</details>` : "";
    const opts = q.o.map((o, k) => `<div class="xrev ${k === q.a ? "right" : a === k ? "wrong" : ""}"><b>${"ABCD"[k]}</b><div><span>${o[0]}</span>${k === q.a ? '<div class="xtag good">Correct answer</div>' : a === k ? '<div class="xtag bad">Your answer</div>' : ""}<p class="small muted xwhy">${cap(o[1] || "")}</p></div></div>`).join("");
    return `<div class="row" style="justify-content:space-between"><button class="btn small ghost" data-xrback>← All questions</button><span class="small muted">Q ${i + 1} of ${n}${s.flag[q.id] ? " · ⚑ flagged" : ""}</span></div>
      ${pass}<div class="panel"><h3 class="xq">${q.q}</h3>${tableHTML(q.vt, "vt")}${a === undefined ? '<p class="small" style="color:var(--bad)">Unanswered</p>' : ""}<div class="xopts">${opts}</div>
      <p class="small" style="margin-top:10px">${q.x || ""}</p>${q.av ? '<p class="small muted">✓ Calculation recomputed during QA.</p>' : ""}</div>
      <div class="row"><button class="btn" data-xrprev ${i === 0 ? "disabled" : ""}>← Previous</button><button class="btn primary" data-xrnext ${i === n - 1 ? "disabled" : ""}>Next →</button></div>`;
  }

  /* ---------- events ---------- */
  function resumeExam() {
    const e = X(); setExamingClass();
    if (e.phase === "intro") return introView();
    if (e.phase === "break") return breakView();
    if (e.phase === "done") return resultsView();
    if (e.phase === "run") { const s = secOf(); if (!e.paused) { s.rem = left(s); s.t0 = null; e.paused = true; save(); } return pauseView(); }
  }
  function ready(fn) { (typeof bankReady !== "undefined" ? bankReady : Promise.resolve()).then(fn, fn); }
  function open() {
    ready(() => {
      if (X() && X().phase !== "done") { /* active attempt: show hub so the user can resume or discard */ }
      hub();
    });
  }
  function onClick(ev) {
    const t = ev.target, g = sel => t.closest(sel);
    let b;
    if ((b = g("[data-xstart]"))) {
      const id = b.dataset.xstart; if (!canTake(id)) return showPro();
      if (X() && X().id === id && X().phase !== "done") return resumeExam();
      if (X() && X().phase !== "done" && !confirm("Start " + id + "? Your unfinished " + X().id + " attempt will be discarded.")) return;
      newExam(id); return introView();
    }
    if ((b = g("[data-xdrop]"))) { if (confirm("Discard your unfinished attempt?")) { S.exam = null; save(); hub(); } return; }
    if (g("[data-xbegin]")) return begin();
    if (g("[data-xexit]")) { const e = X(); if (e && e.phase === "run" && !e.paused) { const s = secOf(); s.rem = left(s); s.t0 = null; e.paused = true; } save(); stopTick(); return hub(); }
    if (g("[data-xhub]")) { return hub(); }
    if (g("[data-xpause]")) return pauseView();
    if (g("[data-xresume]")) return resume();
    if (g("[data-xprev]")) return goto(Math.max(0, secOf().i - 1));
    if (g("[data-xnext]")) return goto(secOf().i + 1);
    if ((b = g("[data-xpick]"))) { const s = secOf(), q = items(X().id, s.s)[s.i].q, k = +b.dataset.xpick; if (s.ans[q.id] === k) delete s.ans[q.id]; else s.ans[q.id] = k; save(); return runView(); }
    if ((b = g("[data-xstrike]"))) { const s = secOf(), id = items(X().id, s.s)[s.i].q.id, k = +b.dataset.xstrike, a = s.str[id] = s.str[id] || []; const j = a.indexOf(k); if (j < 0) a.push(k); else a.splice(j, 1); save(); const y = root().scrollTop; runView(); root().scrollTop = y; return; }
    if (g("[data-xflag]")) { const s = secOf(), id = items(X().id, s.s)[s.i].q.id; if (s.flag[id]) delete s.flag[id]; else s.flag[id] = 1; save(); const y = root().scrollTop; runView(); root().scrollTop = y; return; }
    if (g("[data-xnav]")) return navView();
    if ((b = g("[data-xgo]"))) return goto(+b.dataset.xgo);
    if (g("[data-xgounans]")) { const s = secOf(), it = items(X().id, s.s), i = it.findIndex(x => s.ans[x.q.id] === undefined); return goto(i < 0 ? s.i : i); }
    if (g("[data-xback]")) return runView();
    if (g("[data-xend]")) return endConfirm();
    if (g("[data-xconfirm]")) return endSection(false);
    if (g("[data-xnext-sec]")) return nextSection();
    if (g("[data-xreview]")) { rv = { si: 0, f: "all", q: null }; return reviewView(); }
    if (g("[data-xresults]")) return resultsView();
    if ((b = g("[data-xrsec]"))) { rv = { si: +b.dataset.xrsec, f: rv.f, q: null }; return reviewView(); }
    if ((b = g("[data-xrf]"))) { rv.f = b.dataset.xrf; rv.q = null; return reviewView(); }
    if ((b = g("[data-xrq]"))) { rv.q = +b.dataset.xrq; return reviewView(); }
    if (g("[data-xrback]")) { rv.q = null; return reviewView(); }
    if (g("[data-xrprev]")) { rv.q = Math.max(0, rv.q - 1); return reviewView(); }
    if (g("[data-xrnext]")) { rv.q += 1; return reviewView(); }
  }
  const css = document.createElement("style");
  css.textContent = `
.examing .hud, .examing .tabs { display: none; }
.tabs.six { grid-template-columns: repeat(6, 1fr); }
.xh { font: 700 15px/1 var(--display); letter-spacing: .08em; text-transform: uppercase; color: var(--volt); margin: 18px 0 10px; }
.xgrid { display: grid; gap: 10px; }
.xcard h3 { font: 700 17px/1.2 var(--display); }
.xwrap { display: grid; gap: 12px; align-content: start; }
.xcenter { text-align: center; padding-top: 18vh; }
.xbar { position: sticky; top: -14px; z-index: 5; display: flex; align-items: center; gap: 8px; background: var(--ink); padding: 8px 0 10px; border-bottom: 1px solid var(--line); margin-bottom: 10px; flex-wrap: wrap; }
.xmeta { display: grid; line-height: 1.25; flex: 1; min-width: 90px; }
.xbtns { display: flex; gap: 6px; }
.xtimer { font: 700 24px/1 var(--display); letter-spacing: .04em; color: var(--text); background: var(--panel-2); border: 1px solid var(--line); border-radius: 12px; padding: 8px 12px; min-width: 96px; text-align: center; }
.xtimer.sm { font-size: 16px; padding: 6px 10px; min-width: 0; } .xtimer.big { font-size: 44px; display: inline-block; margin: 8px auto; padding: 14px 22px; }
.xtimer.warn { color: var(--heat); border-color: var(--heat); } .xtimer.hot { color: var(--bad); border-color: var(--bad); }
.xpass { margin-bottom: 10px; background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 10px 14px; }
.xpass summary { font: 700 13px/1 var(--display); letter-spacing: .08em; text-transform: uppercase; color: var(--volt); cursor: pointer; padding: 4px 0; }
.xpass[open] summary { margin-bottom: 8px; }
.xq { font-size: 17px; line-height: 1.45; margin: 0 0 12px; }
.xopts { display: grid; gap: 8px; }
.xopt { display: flex; gap: 6px; align-items: stretch; }
.xpick { flex: 1; display: flex; gap: 10px; align-items: flex-start; text-align: left; background: var(--panel-2); border: 1px solid var(--line); border-radius: 12px; padding: 12px; }
.xpick b { flex: none; width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center; background: var(--ink); font: 700 13px/1 var(--display); }
.xopt.sel .xpick { border-color: var(--volt); background: rgba(250,204,21,.12); } .xopt.sel .xpick b { background: var(--volt); color: var(--volt-ink); }
.xopt.struck .xpick span { text-decoration: line-through; opacity: .45; }
.xstrike { flex: none; width: 38px; border: 1px solid var(--line); background: transparent; border-radius: 12px; color: var(--muted); }
.xopt.struck .xstrike { color: var(--bad); border-color: var(--bad); }
.xfoot { position: sticky; bottom: -24px; display: flex; justify-content: space-between; gap: 10px; background: var(--ink); padding: 10px 0 4px; margin-top: 12px; border-top: 1px solid var(--line); }
.xgridn { display: grid; grid-template-columns: repeat(auto-fill, minmax(46px, 1fr)); gap: 8px; }
.xcell { position: relative; height: 44px; border-radius: 10px; border: 1px solid var(--line); background: transparent; font: 700 14px/1 var(--display); color: var(--text); }
.xcell.ans { background: var(--panel-2); border-color: var(--cool); } .xcell.cur { outline: 2px solid var(--volt); }
.xcell.ok { background: rgba(74,222,128,.18); border-color: var(--good); } .xcell.bad { background: rgba(251,113,133,.18); border-color: var(--bad); } .xcell.un { color: var(--muted); }
.xcell i { position: absolute; top: 1px; right: 4px; font-style: normal; font-size: 10px; color: var(--volt); }
.xres { width: 100%; border-collapse: collapse; font-size: 14px; } .xres th, .xres td { text-align: left; padding: 6px 4px; border-bottom: 1px solid var(--line); }
.xrev { display: flex; gap: 10px; padding: 10px; border-radius: 12px; border: 1px solid var(--line); }
.xrev > b { flex: none; width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center; background: var(--ink); font: 700 13px/1 var(--display); }
.xrev.right { border-color: var(--good); background: rgba(74,222,128,.1); } .xrev.wrong { border-color: var(--bad); background: rgba(251,113,133,.1); }
.xtag { font: 700 11px/1 var(--display); letter-spacing: .08em; text-transform: uppercase; margin-top: 4px; } .xtag.good { color: var(--good); } .xtag.bad { color: var(--bad); }
.xwhy { margin: 6px 0 0; }
`;
  document.head.appendChild(css);
  document.addEventListener("click", ev => { const r = root(); if (r && !r.hidden && r.contains(ev.target)) onClick(ev); });
  window.renderExam = open;
  window.ExamUI = { open, scaled, items, catalog };
  // A reload while running leaves the exam paused with the time it had.
  if (S.exam && S.exam.phase === "run" && !S.exam.paused) { const s = S.exam.secs[S.exam.si]; s.rem = Math.max(0, s.rem); s.t0 = null; S.exam.paused = true; save(); }
})();
