// Figure viewer: tap any explanation figure, passage graph or checklist figure to open it full screen,
// centered, with drag to pan, pinch / wheel / buttons to zoom, and double-tap to zoom in or reset.
(() => {
  const SEL = "figure img, .pgraph svg";
  const css = `
figure img, .pgraph svg { cursor: zoom-in; }
#fz { position: fixed; inset: 0; z-index: 300; background: rgba(8,10,20,.94); touch-action: none; overscroll-behavior: contain; user-select: none; -webkit-user-select: none; }
#fz[hidden] { display: none; }
#fz .fzstage { position: absolute; inset: 0; overflow: hidden; cursor: grab; }
#fz .fzstage.drag { cursor: grabbing; }
#fz .fzc { position: absolute; left: 0; top: 0; transform-origin: 0 0; background: #fff; border-radius: 8px; box-shadow: 0 10px 40px rgba(0,0,0,.5); will-change: transform; }
#fz .fzc img, #fz .fzc svg { display: block; width: 100%; height: 100%; pointer-events: none; -webkit-user-drag: none; }
#fz .fzbar { position: absolute; left: 50%; bottom: calc(14px + env(safe-area-inset-bottom, 0px)); transform: translateX(-50%); display: flex; gap: 6px; align-items: center; background: rgba(20,24,40,.9); border: 1px solid rgba(255,255,255,.15); border-radius: 999px; padding: 6px; }
#fz button { all: unset; box-sizing: border-box; min-width: 44px; height: 44px; padding: 0 12px; border-radius: 999px; display: grid; place-items: center; color: #fff; font: 700 20px/1 system-ui, sans-serif; cursor: pointer; }
#fz button:hover, #fz button:focus-visible { background: rgba(255,255,255,.14); }
#fz .fzpct { min-width: 54px; text-align: center; color: #cfd3e6; font: 600 13px/1 system-ui, sans-serif; font-variant-numeric: tabular-nums; }
#fz .fzx { position: absolute; top: calc(10px + env(safe-area-inset-top, 0px)); right: 10px; background: rgba(20,24,40,.9); border: 1px solid rgba(255,255,255,.15); }
#fz .fzcap { position: absolute; top: calc(14px + env(safe-area-inset-top, 0px)); left: 14px; right: 70px; color: #cfd3e6; font: 13px/1.35 system-ui, sans-serif; max-height: 3.9em; overflow: hidden; pointer-events: none; }
#fz .fzhint { position: absolute; left: 50%; bottom: calc(76px + env(safe-area-inset-bottom, 0px)); transform: translateX(-50%); color: #cfd3e6; font: 12px/1.3 system-ui, sans-serif; background: rgba(20,24,40,.8); padding: 6px 10px; border-radius: 8px; white-space: nowrap; pointer-events: none; transition: opacity .6s; }`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);

  let root, stage, box, pct, cap, hint, w0 = 0, h0 = 0, s = 1, x = 0, y = 0, lastFocus = null, pushed = false;
  const MAX = 8, MIN = 1;
  const pts = new Map(); let pinch = null, moved = false, lastTap = 0, lastTapXY = [0, 0], downXY = [0, 0], anim = 0;

  function build() {
    root = document.createElement("div"); root.id = "fz"; root.hidden = true;
    root.setAttribute("role", "dialog"); root.setAttribute("aria-modal", "true"); root.setAttribute("aria-label", "Figure viewer");
    root.innerHTML = `<div class="fzstage"><div class="fzc"></div></div><div class="fzcap"></div>
<button class="fzx" data-fz="close" aria-label="Close figure">&#x2715;</button>
<div class="fzhint">Drag to move &middot; pinch or scroll to zoom &middot; double-tap to reset</div>
<div class="fzbar"><button data-fz="out" aria-label="Zoom out">&#x2212;</button><span class="fzpct">100%</span><button data-fz="in" aria-label="Zoom in">+</button><button data-fz="fit" aria-label="Fit to screen" style="font-size:14px">Fit</button></div>`;
    document.body.appendChild(root);
    stage = root.querySelector(".fzstage"); box = root.querySelector(".fzc"); pct = root.querySelector(".fzpct");
    cap = root.querySelector(".fzcap"); hint = root.querySelector(".fzhint");
    root.addEventListener("click", e => {
      const b = e.target.closest("[data-fz]"); if (!b) return;
      const a = b.dataset.fz, r = stage.getBoundingClientRect();
      if (a === "close") close();
      else if (a === "fit") animTo(1, r.width / 2, r.height / 2, true);
      else animTo(s * (a === "in" ? 1.6 : 1 / 1.6), r.width / 2, r.height / 2);
    });
    stage.addEventListener("pointerdown", down);
    stage.addEventListener("pointermove", move);
    stage.addEventListener("pointerup", up);
    stage.addEventListener("pointercancel", up);
    stage.addEventListener("wheel", e => {
      e.preventDefault();
      const r = stage.getBoundingClientRect(), k = Math.exp(-(e.deltaMode ? e.deltaY * 16 : e.deltaY) * 0.0018);
      zoomAt(s * k, e.clientX - r.left, e.clientY - r.top); render();
    }, { passive: false });
    window.addEventListener("resize", () => { if (!root.hidden) { const c = center(); fit(); zoomAt(c.s, 0, 0, c); render(); } });
    document.addEventListener("keydown", e => {
      if (root.hidden) return;
      const r = stage.getBoundingClientRect();
      if (e.key === "Escape") { e.preventDefault(); close(); }
      else if (e.key === "+" || e.key === "=") animTo(s * 1.6, r.width / 2, r.height / 2);
      else if (e.key === "-") animTo(s / 1.6, r.width / 2, r.height / 2);
      else if (e.key === "0") animTo(1, r.width / 2, r.height / 2, true);
      else if (/^Arrow/.test(e.key)) { e.preventDefault(); const d = 60; x += e.key === "ArrowLeft" ? d : e.key === "ArrowRight" ? -d : 0; y += e.key === "ArrowUp" ? d : e.key === "ArrowDown" ? -d : 0; render(); }
    });
    window.addEventListener("popstate", () => { if (!root.hidden) { pushed = false; close(); } });
  }

  // Fit size: the largest box with the figure's aspect ratio that fits the screen with a margin.
  let ar = 1;
  function fit() {
    const r = stage.getBoundingClientRect(), mw = r.width - 24, mh = r.height - 150;
    w0 = Math.min(mw, mh * ar); h0 = w0 / ar;
  }
  // Remembers the point of the figure at the screen center so a resize keeps the same view.
  function center() { const r = stage.getBoundingClientRect(); return { s, fx: (r.width / 2 - x) / (w0 * s), fy: (r.height / 2 - y) / (h0 * s) }; }
  function clamp() {
    const r = stage.getBoundingClientRect(), w = w0 * s, h = h0 * s;
    const top = 60, bot = 80; // room for the caption and the toolbar
    x = w <= r.width ? (r.width - w) / 2 : Math.min(0, Math.max(r.width - w, x));
    const ah = r.height - top - bot;
    y = h <= ah ? top + (ah - h) / 2 : Math.min(top, Math.max(r.height - bot - h, y));
  }
  // Zoom to scale ns keeping screen point (px, py) fixed (or, after a resize, re-center on a remembered point).
  function zoomAt(ns, px, py, c) {
    ns = Math.max(MIN, Math.min(MAX, ns));
    if (c) { const r = stage.getBoundingClientRect(); s = ns; x = r.width / 2 - c.fx * w0 * s; y = r.height / 2 - c.fy * h0 * s; return; }
    x = px - (px - x) * ns / s; y = py - (py - y) * ns / s; s = ns;
  }
  // The figure is re-laid out at its zoomed size (not just scaled) so vector art stays sharp.
  function render() {
    clamp();
    box.style.width = w0 * s + "px"; box.style.height = h0 * s + "px";
    box.style.transform = `translate3d(${x}px,${y}px,0)`;
    pct.textContent = Math.round(s * 100) + "%";
  }
  function animTo(ns, px, py, reset) {
    cancelAnimationFrame(anim);
    const s1 = s, x1 = x, y1 = y;
    zoomAt(ns, px, py); if (reset) { s = 1; } clamp();
    const s2 = s, x2 = x, y2 = y, t0 = performance.now();
    s = s1; x = x1; y = y1;
    const step = t => {
      const k = Math.min(1, (t - t0) / 220), e = 1 - Math.pow(1 - k, 3);
      s = s1 + (s2 - s1) * e; x = x1 + (x2 - x1) * e; y = y1 + (y2 - y1) * e; render();
      if (k < 1) anim = requestAnimationFrame(step);
    };
    anim = requestAnimationFrame(step);
  }

  function local(e) { const r = stage.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; }
  function down(e) {
    cancelAnimationFrame(anim);
    stage.setPointerCapture(e.pointerId);
    pts.set(e.pointerId, local(e));
    if (pts.size === 1) { moved = false; downXY = local(e); stage.classList.add("drag"); }
    if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = { d: Math.hypot(a[0] - b[0], a[1] - b[1]) || 1, m: [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2] }; moved = true; }
    hint.style.opacity = 0;
  }
  function move(e) {
    if (!pts.has(e.pointerId)) return;
    const p = local(e), q = pts.get(e.pointerId);
    pts.set(e.pointerId, p);
    if (pts.size === 1) {
      if (Math.hypot(p[0] - downXY[0], p[1] - downXY[1]) > 6) moved = true;
      x += p[0] - q[0]; y += p[1] - q[1];
    } else if (pts.size === 2 && pinch) {
      const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]) || 1, m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
      x += m[0] - pinch.m[0]; y += m[1] - pinch.m[1];
      zoomAt(s * d / pinch.d, m[0], m[1]);
      pinch = { d, m };
    }
    render();
  }
  function up(e) {
    if (!pts.has(e.pointerId)) return;
    pts.delete(e.pointerId);
    if (pts.size < 2) pinch = null;
    if (pts.size === 1) { downXY = [...pts.values()][0]; return; }
    if (pts.size) return;
    stage.classList.remove("drag");
    if (moved) return;
    // Double-tap / double-click: zoom in on that spot, or back to fit when already zoomed.
    const p = local(e), now = performance.now();
    if (now - lastTap < 320 && Math.hypot(p[0] - lastTapXY[0], p[1] - lastTapXY[1]) < 30) {
      lastTap = 0;
      if (s > 1.05) animTo(1, p[0], p[1], true); else animTo(2.5, p[0], p[1]);
    } else { lastTap = now; lastTapXY = p; }
  }

  function open(el) {
    if (!root) build();
    const r = el.getBoundingClientRect();
    ar = r.width && r.height ? r.width / r.height : (el.naturalWidth / el.naturalHeight) || 1;
    let c;
    if (el.tagName === "IMG") { c = document.createElement("img"); c.src = el.currentSrc || el.src; c.alt = el.alt || ""; c.draggable = false; }
    else { c = el.cloneNode(true); c.removeAttribute("width"); c.removeAttribute("height"); c.removeAttribute("style"); c.setAttribute("preserveAspectRatio", "xMidYMid meet"); }
    box.replaceChildren(c);
    const fig = el.closest("figure"), fc = fig && (fig.querySelector("figcaption") || fig.querySelector(".gcap"));
    cap.textContent = fc ? fc.textContent.trim() : (el.getAttribute("alt") || el.getAttribute("aria-label") || "");
    lastFocus = document.activeElement;
    root.hidden = false; hint.style.opacity = 1;
    document.documentElement.style.overflow = "hidden";
    fit(); s = 1; x = 0; y = 0; render();
    root.querySelector(".fzx").focus({ preventScroll: true });
    try { history.pushState({ fz: 1 }, ""); pushed = true; } catch (_) { pushed = false; }
    setTimeout(() => { hint.style.opacity = 0; }, 3500);
  }
  function close() {
    if (!root || root.hidden) return;
    root.hidden = true; box.replaceChildren(); pts.clear(); pinch = null;
    document.documentElement.style.overflow = "";
    if (pushed) { pushed = false; history.back(); }
    lastFocus && lastFocus.focus && lastFocus.focus({ preventScroll: true });
  }

  document.addEventListener("click", e => {
    const el = e.target.closest(SEL);
    if (!el || (root && root.contains(el)) || e.target.closest("a, button, label")) return;
    e.preventDefault(); e.stopPropagation(); open(el);
  }, true);
  window.openFigure = open;
})();
