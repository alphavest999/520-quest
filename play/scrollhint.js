// "More below" hint: a small chevron floats at the bottom of whatever is scrolling on screen
// (Qbank card, sheet, Me page, checklist, exam ...) while there is still content under the fold.
// It fades away once you are near the bottom. When a finishing button (the Qbank "Done" buttons,
// or anything marked data-scrollhint) is waiting further down, the chevron grows into a labeled
// pill that scrolls straight to it, and the button glows once when it comes into view.
(() => {
  const TARGETS = "[data-qdone], [data-scrollhint]";
  const css = `
#sh { position: fixed; z-index: 250; left: 50%; bottom: 16px; transform: translate(-50%, 6px); display: inline-flex; align-items: center; gap: 6px;
  min-width: 38px; height: 38px; padding: 0 10px; border-radius: 999px; border: 1px solid rgba(30,58,138,.18); cursor: pointer;
  background: rgba(255,255,255,.72); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); color: #1e3a8a;
  box-shadow: 0 4px 14px rgba(15,23,42,.14); font: 800 14px/1 var(--body, system-ui, sans-serif); justify-content: center;
  opacity: 0; pointer-events: none; transition: opacity .25s ease, transform .25s ease, background .2s; }
#sh.on { opacity: .8; pointer-events: auto; transform: translate(-50%, 0); }
#sh.on:hover, #sh:focus-visible { opacity: 1; background: #fff; outline: none; box-shadow: 0 6px 18px rgba(15,23,42,.2); }
#sh svg { width: 18px; height: 18px; flex: none; animation: shbob 1.8s ease-in-out infinite; }
#sh .shl { display: none; white-space: nowrap; max-width: 62vw; overflow: hidden; text-overflow: ellipsis; }
#sh.pill { padding: 0 16px 0 12px; background: #1e3a8a; color: #fff; border-color: #1e3a8a; opacity: 1; box-shadow: 0 6px 18px rgba(30,58,138,.35); }
#sh.pill:hover, #sh.pill:focus-visible { background: #1e40af; }
#sh.pill .shl { display: inline; }
@keyframes shbob { 0%, 100% { transform: translateY(-1px); } 50% { transform: translateY(2px); } }
.sh-glow { animation: shglow 1.1s ease-out 2; }
@keyframes shglow { 0% { box-shadow: 0 0 0 0 rgba(244,114,182,.75); } 100% { box-shadow: 0 0 0 14px rgba(244,114,182,0); } }
@media (prefers-reduced-motion: reduce) { #sh svg, .sh-glow { animation: none; } #sh { transition: opacity .2s; } }
@media print { #sh { display: none !important; } }`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);

  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const NEAR = 40;   // px left to scroll that still counts as "at the bottom"
  let hint, label, box = null, target = null, queued = false;
  const glowed = new WeakSet();

  function build() {
    hint = document.createElement("button");
    hint.id = "sh"; hint.type = "button"; hint.tabIndex = -1;
    hint.setAttribute("aria-label", "Scroll down for more");
    hint.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg><span class="shl"></span>`;
    label = hint.querySelector(".shl");
    hint.addEventListener("click", () => {
      if (!box) return;
      const b = reduce ? "auto" : "smooth";
      if (target && target.isConnected) {
        const top = target.getBoundingClientRect().top - viewRect(box).top;
        const want = box.scrollTop + top - box.clientHeight / 2 + target.offsetHeight / 2;
        box.scrollTo({ top: Math.max(box.scrollTop, want), behavior: b });
        try { target.focus({ preventScroll: true }); } catch (e) {}
      } else box.scrollBy({ top: Math.round(box.clientHeight * .8), behavior: b });
    });
    document.body.appendChild(hint);
  }

  const docScroller = () => document.scrollingElement || document.documentElement;
  const viewRect = el => el === docScroller() ? { top: 0, bottom: innerHeight, left: 0, width: innerWidth } : el.getBoundingClientRect();
  function scrolls(el) {
    if (el.scrollHeight - el.clientHeight < 4) return false;
    if (el === docScroller()) return getComputedStyle(document.body).overflowY !== "hidden";
    const o = getComputedStyle(el).overflowY; return o === "auto" || o === "scroll";
  }
  // The scroller behind the middle of the screen; small inner boxes (a long passage panel) are skipped
  // in favour of the page-sized one around them, which keeps its own native scrollbar anyway.
  function findBox() {
    const pts = document.elementsFromPoint ? document.elementsFromPoint(innerWidth / 2, innerHeight * .55) : [];
    const start = pts.find(p => p !== hint && !hint.contains(p));
    for (let el = start; el && el !== document.documentElement; el = el.parentElement) {
      if (el.id === "fz") return null;   // full-screen figure viewer
      if (el !== document.body && scrolls(el) && el.clientHeight >= innerHeight * .4) return el;
    }
    const d = docScroller(); return scrolls(d) ? d : null;
  }
  const shown = el => !!el && el.isConnected && !el.hidden && el.getClientRects().length > 0;

  function update() {
    queued = false;
    if (!hint) { if (!document.body) return; build(); }
    box = findBox(); target = null;
    let on = false, pill = false;
    if (box) {
      const r = viewRect(box), bottom = Math.min(r.bottom, innerHeight);
      let inView = false;
      const t = [...box.querySelectorAll(TARGETS)].find(shown);
      if (t) {
        const tr = t.getBoundingClientRect();
        if (tr.top >= bottom - 8) { target = t; pill = true; }
        else if (tr.bottom > Math.max(r.top, 0)) {
          inView = true;
          if (!glowed.has(t)) { glowed.add(t); t.classList.add("sh-glow"); setTimeout(() => t.classList.remove("sh-glow"), 2400); }
        }
      }
      // Hide once the finishing button is on screen, or when there is nothing left below.
      on = pill || (!inView && box.scrollHeight - box.scrollTop - box.clientHeight > NEAR);
      if (on) {
        const x = Math.round(r.left + r.width / 2) + "px", y = Math.round(innerHeight - bottom + 14) + "px";
        if (hint.style.left !== x) hint.style.left = x;
        if (hint.style.bottom !== y) hint.style.bottom = y;
      }
    }
    const txt = pill ? (target.textContent || "Done").trim() : "";
    if (label.textContent !== txt) label.textContent = txt;
    const aria = pill ? `Scroll down to ${txt}` : "Scroll down for more";
    if (hint.getAttribute("aria-label") !== aria) hint.setAttribute("aria-label", aria);
    hint.classList.toggle("on", on);
    hint.classList.toggle("pill", on && pill);
  }
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };

  addEventListener("scroll", queue, { capture: true, passive: true });
  addEventListener("resize", queue);
  addEventListener("load", queue, true);   // images and fonts change heights
  const mo = new MutationObserver(recs => { if (recs.some(m => !hint || !hint.contains(m.target))) queue(); });
  const go = () => { mo.observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ["hidden", "class", "style", "open"] }); queue(); };
  if (document.body) go(); else document.addEventListener("DOMContentLoaded", go);
  setInterval(queue, 1500);   // safety net for layout changes nothing announces
})();
