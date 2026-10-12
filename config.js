/* ===== Site settings. Paste your Gumroad product link here once it exists. ===== */
window.SITE = {
  gumroadUrl: "https://alphavest.gumroad.com/l/520quest",          // e.g. "https://yourname.gumroad.com/l/520quest"
  price: "$39"
};
/* =============================================================================== */
const SITE_ROOT = document.currentScript.src.replace(/config\.js.*$/, "");
// Gumroad's pop-up checkout: buyers stay on this page, and the pop-up only appears
// once it has fully loaded, so there's no white flash. Start loading it right away.
if (SITE.gumroadUrl) {
  for (const h of ["https://gumroad.com", "https://assets.gumroad.com", "https://alphavest.gumroad.com"]) {
    const l = document.createElement("link"); l.rel = "preconnect"; l.href = h; document.head.appendChild(l);
  }
  const s = document.createElement("script"); s.src = "https://gumroad.com/js/gumroad.js"; document.head.appendChild(s);
}
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-price]").forEach(el => el.textContent = SITE.price);
  document.querySelectorAll("[data-buy]").forEach(a => {
    // If the pop-up script can't load, this link still opens the Gumroad page normally.
    if (SITE.gumroadUrl) a.href = SITE.gumroadUrl;
    else { a.href = SITE_ROOT + "play/"; a.textContent = "Pro opens soon. Play free now"; }
  });
});
