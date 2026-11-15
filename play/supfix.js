/* Superscript fix: the bank writes exponents with Unicode characters (10⁻¹², Ca²⁺). In most fonts ¹ ² ³
   are drawn at a different height and size than ⁰ ⁴-⁹ ⁺ ⁻, so a two-digit exponent like ¹⁵ or ²⁴ looks
   uneven. Every run of these characters on screen is redrawn as one <sup> with ordinary digits, so all
   exponents sit on the same line. Text inside KaTeX, SVG, inputs and code is left alone. */
(function () {
  const MAP = { "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁺": "+", "⁻": "−", "⁼": "=", "⁽": "(", "⁾": ")", "ⁿ": "n" };
  // Also: plain-text subscripts the bank writes with an underscore (E_K, k_f, ρ_water, ΔS_universe, t_1/2) become
  // <sub class=usub>, and e^0.65 / 10^-3 / 2^(1/2) become <sup>. Ids like x5E_001 or bp12_0 are left alone (a letter or
  // digit right before the base), as are category codes (d_4B), e-mail addresses and URLs. No lookbehind: older Safari.
  const RUN = /[⁰¹²³⁴-⁹⁺⁻⁼⁽⁾ⁿ]+/g, ANY = /[⁰¹²³⁴-⁹⁺⁻⁼⁽⁾ⁿ_^]/;
  const ALL = /([⁰¹²³⁴-⁹⁺⁻⁼⁽⁾ⁿ]+)|(^|[^\w#@.\\$])((?:Δ|δ)?[A-Za-zα-ωΑ-Ω]{1,4}\u0307?°?)_(\{[^}]*\}|1\/2|[A-Za-z0-9₀-₉]+)|(^|[^\w^\\])(e|10|2)\^(-?\d+(?:\.\d+)?|\([^)]{1,12}\))/g;
  const SUBD = { "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9" };
  const SKIP = "SCRIPT,STYLE,TEXTAREA,INPUT,SELECT,OPTION,TITLE,CODE,PRE,svg,math,.katex,[data-nosup]";
  const st = document.createElement("style");
  st.textContent = "sup.usup{font-size:.72em;line-height:0;vertical-align:.45em;font-variant-numeric:lining-nums}sub.usub{font-size:.72em;line-height:0}";
  document.head.appendChild(st);
  function el(tag, cls, txt) { const e = document.createElement(tag); e.className = cls; e.textContent = txt; return e; }
  function fixText(n) {
    const t = n.nodeValue; if (!t || !ANY.test(t)) return;
    const p = n.parentElement; if (!p || p.closest(SKIP)) return;
    const f = document.createDocumentFragment(); let last = 0, hit = false;
    t.replace(ALL, (m, sups, pre, base, sub, pre2, cbase, pow, at) => {
      let parts;
      if (sups) parts = [el("sup", "usup", [...sups].map(c => MAP[c]).join(""))];
      else if (base) {
        if (/^\d+[A-E]$/.test(sub)) return m;   // category code like d_4B
        if (/^[\w.+-]*@/.test(t.slice(at + m.length)) || /:\/\/\S*$/.test(t.slice(0, at + pre.length))) return m;   // e-mail, URL
        const s = sub.replace(/^\{|\}$/g, "").replace(/[₀-₉]/g, c => SUBD[c]);
        parts = [document.createTextNode(pre + base), el("sub", "usub", s)];
      } else parts = [document.createTextNode(pre2 + cbase), el("sup", "usup", pow.replace(/^\((-?[\d.]+)\)$/, "$1").replace(/^-/, "−"))];
      if (at > last) f.appendChild(document.createTextNode(t.slice(last, at)));
      parts.forEach(x => f.appendChild(x)); last = at + m.length; hit = true; return m;
    });
    if (!hit) return;
    if (last < t.length) f.appendChild(document.createTextNode(t.slice(last)));
    n.replaceWith(f);
  }
  function scan(root) {
    if (root.nodeType === 3) return fixText(root);
    if (root.nodeType !== 1 || root.closest(SKIP) || !ANY.test(root.textContent || "")) return;
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT), list = [];
    while (w.nextNode()) if (ANY.test(w.currentNode.nodeValue)) list.push(w.currentNode);
    list.forEach(fixText);
  }
  function start() {
    scan(document.body);
    new MutationObserver(ms => ms.forEach(m => m.type === "characterData" ? fixText(m.target) : m.addedNodes.forEach(scan)))
      .observe(document.body, { childList: true, subtree: true, characterData: true });
  }
  window.supFix = scan;
  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", start) : start();
})();
