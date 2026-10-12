/* ===== Site settings. Paste your Gumroad product link here once it exists. ===== */
window.SITE = {
  gumroadUrl: "https://alphavest.gumroad.com/l/520quest",          // e.g. "https://yourname.gumroad.com/l/520quest"
  price: "$39"
};
/* =============================================================================== */
const SITE_ROOT = document.currentScript.src.replace(/config\.js.*$/, "");
// Warm up the connection to Gumroad so checkout opens faster.
if (SITE.gumroadUrl) {
  for (const h of ["https://alphavest.gumroad.com", "https://gumroad.com", "https://assets.gumroad.com"]) {
    const l = document.createElement("link"); l.rel = "preconnect"; l.href = h; document.head.appendChild(l);
  }
}
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-price]").forEach(el => el.textContent = SITE.price);
  document.querySelectorAll("[data-buy]").forEach(a => {
    // ?wanted=true goes straight to Gumroad's payment form (one click, fastest)
    if (SITE.gumroadUrl) a.href = SITE.gumroadUrl + "?wanted=true";
    else { a.href = SITE_ROOT + "play/"; a.textContent = "Pro opens soon. Play free now"; }
  });
});
