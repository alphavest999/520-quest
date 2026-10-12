/* ===== Site settings. Paste your Gumroad product link here once it exists. ===== */
window.SITE = {
  gumroadUrl: "https://alphavest.gumroad.com/l/520quest",          // e.g. "https://yourname.gumroad.com/l/520quest"
  price: "$39"
};
/* =============================================================================== */
const SITE_ROOT = document.currentScript.src.replace(/config\.js.*$/, "");
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-price]").forEach(el => el.textContent = SITE.price);
  document.querySelectorAll("[data-buy]").forEach(a => {
    // ?wanted=true skips the Gumroad product page and opens checkout directly
    if (SITE.gumroadUrl) a.href = SITE.gumroadUrl + "?wanted=true";
    else { a.href = SITE_ROOT + "play/"; a.textContent = "Pro opens soon. Play free now"; }
  });
  // Gumroad's overlay opens checkout on top of this page instead of leaving the site.
  // If the script can't load, the links above still go to Gumroad normally.
  if (SITE.gumroadUrl && document.querySelector("[data-buy]")) {
    const s = document.createElement("script");
    s.src = "https://gumroad.com/js/gumroad.js";
    document.body.appendChild(s);
  }
});
