/* Superscript fix: the bank writes exponents with Unicode characters (10⁻¹², Ca²⁺). In most fonts ¹ ² ³
   are drawn at a different height and size than ⁰ ⁴-⁹ ⁺ ⁻, so a two-digit exponent like ¹⁵ or ²⁴ looks
   uneven. Every run of these characters on screen is redrawn as one <sup> with ordinary digits, so all
   exponents sit on the same line. Text inside KaTeX, SVG, inputs and code is left alone. */
(function () {
  const MAP = { "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁺": "+", "⁻": "−", "⁼": "=", "⁽": "(", "⁾": ")", "ⁿ": "n" };
  const RUN = /[⁰¹²³⁴-⁹⁺⁻⁼⁽⁾ⁿ]+/g, ANY = /[⁰¹²³⁴-⁹⁺⁻⁼⁽⁾ⁿ]/;
  const SKIP = "SCRIPT,STYLE,TEXTAREA,INPUT,SELECT,OPTION,TITLE,CODE,PRE,svg,math,.katex,[data-nosup]";
  const st = document.createElement("style");
  st.textContent = "sup.usup{font-size:.72em;line-height:0;vertical-align:.45em;font-variant-numeric:lining-nums}";
  document.head.appendChild(st);
  function fixText(n) {
    const t = n.nodeValue; if (!t || !ANY.test(t)) return;
    const p = n.parentElement; if (!p || p.closest(SKIP)) return;
    const f = document.createDocumentFragment(); let last = 0;
    t.replace(RUN, (m, at) => {
      if (at > last) f.appendChild(document.createTextNode(t.slice(last, at)));
      const s = document.createElement("sup"); s.className = "usup"; s.textContent = [...m].map(c => MAP[c]).join("");
      f.appendChild(s); last = at + m.length; return m;
    });
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
