/* ===== Site settings. Paste your Gumroad product link here once it exists. ===== */
window.SITE = {
  gumroadUrl: "",          // e.g. "https://yourname.gumroad.com/l/520quest"
  price: "$39"
};
/* =============================================================================== */
const SITE_ROOT = document.currentScript.src.replace(/config\.js.*$/, "");
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-price]").forEach(el => el.textContent = SITE.price);
  document.querySelectorAll("[data-buy]").forEach(a => {
    if (SITE.gumroadUrl) { a.href = SITE.gumroadUrl; a.target = "_blank"; a.rel = "noopener"; }
    else { a.href = SITE_ROOT + "play/"; a.textContent = "Pro opens soon. Play free now"; }
  });
});
