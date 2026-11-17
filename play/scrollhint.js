// "More below" hint: a small chevron floats at the bottom of whatever is scrolling on screen
// (Qbank card, mastery sheet, pop-up sheet, Me page, checklist, exam ...) while there is still
// content under the fold. Tap it to scroll down. It fades away once you are near the bottom.
(() => {
  const css = `
#sh { position: fixed; z-index: 250; left: 50%; bottom: 16px; transform: translate(-50%, 6px); display: grid; place-items: center;
  width: 38px; height: 38px; padding: 0; border-radius: 999px; border: 1px solid rgba(30,58,138,.18); cursor: pointer;
  background: rgba(255,255,255,.72); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); color: #1e3a8a;
  box-shadow: 0 4px 14px rgba(15,23,42,.14); opacity: 0; pointer-events: none; transition: opacity .25s ease, transform .25s ease, background .2s; }
#sh.on { opacity: .8; pointer-events: auto; transform: translate(-50%, 0); }
#sh.on:hover, #sh:focus-visible { opacity: 1; background: #fff; outline: none; box-shadow: 0 6px 18px rgba(15,23,42,.2); }
#sh svg { width: 18px; height: 18px; animation: shbob 1.8s ease-in-out infinite; }
@keyframes shbob { 0%, 100% { transform: translateY(-1px); } 50% { transform: translateY(2px); } }
@media (prefers-reduced-motion: reduce) { #sh svg { animation: none; } #sh { transition: opacity .2s; } }
@media print { #sh { display: none !important; } }`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);

  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const NEAR = 40;   // px left to scroll that still counts as "at the bottom"
  let hint, box = null, queued = false;

  function build() {
    hint = document.createElement("button");
    hint.id = "sh"; hint.type = "button"; hint.tabIndex = -1;
    hint.setAttribute("aria-label", "Scroll down for more");
    hint.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>`;
    hint.addEventListener("click", () => { if (box) box.scrollBy({ top: Math.round(box.clientHeight * .8), behavior: reduce ? "auto" : "smooth" }); });
    document.body.appendChild(hint);
  }

  const docScroller = () => document.scrollingElement || document.documentElement;
  const viewRect = el => el === docScroller() ? { bottom: innerHeight, left: 0, width: innerWidth } : el.getBoundingClientRect();
  function scrolls(el) {
    if (el.scrollHeight - el.clientHeight < 4) return false;
    if (el === docScroller()) return getComputedStyle(document.body).overflowY !== "hidden";
    const o = getComputedStyle(el).overflowY; return o === "auto" || o === "scroll";
  }
  // The scroller behind the middle of the screen (an open pop-up sheet wins over the page under it).
  // Small inner boxes, like a long passage panel, are skipped for the page-sized one around them.
  function findBox() {
    const pts = document.elementsFromPoint ? document.elementsFromPoint(innerWidth / 2, innerHeight * .55) : [];
    const start = pts.find(p => p !== hint && !hint.contains(p));
    for (let el = start; el && el !== document.documentElement; el = el.parentElement) {
      if (el.id === "fz") return null;   // full-screen figure viewer
      if (el !== document.body && scrolls(el) && el.clientHeight >= innerHeight * .3) return el;
    }
    const d = docScroller(); return scrolls(d) ? d : null;
  }

  function update() {
    queued = false;
    if (!hint) { if (!document.body) return; build(); }
    box = findBox();
    const on = !!box && box.scrollHeight - box.scrollTop - box.clientHeight > NEAR;
    if (on) {
      const r = viewRect(box), bottom = Math.min(r.bottom, innerHeight);
      const x = Math.round(r.left + r.width / 2) + "px", y = Math.round(innerHeight - bottom + 14) + "px";
      if (hint.style.left !== x) hint.style.left = x;
      if (hint.style.bottom !== y) hint.style.bottom = y;
    }
    hint.classList.toggle("on", on);
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
