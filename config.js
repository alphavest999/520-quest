/* ===== Site settings. Paste your Gumroad product link here once it exists. ===== */
window.SITE = {
  // Lemon Squeezy checkout link (Share > Checkout link). When set, it replaces Gumroad
  // and opens as a pop-up on this page. e.g. "https://520quest.lemonsqueezy.com/buy/xxxx"
  lemonUrl: "https://unprocrastinate.lemonsqueezy.com/checkout/buy/8edb3384-9e65-4fbf-9b08-4fdce2f022d8",
  gumroadUrl: "https://alphavest.gumroad.com/l/520quest",          // e.g. "https://yourname.gumroad.com/l/520quest"
  price: "$39"
};
/* =============================================================================== */
const SITE_ROOT = document.currentScript.src.replace(/config\.js.*$/, "");
// Checkout link with the pop-up look: dark, pink Pay button, no extra product text.
SITE.buyUrl = SITE.lemonUrl
  ? SITE.lemonUrl + (SITE.lemonUrl.includes("?") ? "&" : "?") + "embed=1&dark=1&media=0&desc=0&button_color=%23fb7185"
  : SITE.gumroadUrl ? SITE.gumroadUrl + "?wanted=true" : "";
// Warm up the connection to the checkout so it opens faster.
if (SITE.buyUrl) {
  const l = document.createElement("link"); l.rel = "preconnect"; l.href = new URL(SITE.buyUrl).origin; document.head.appendChild(l);
}
if (SITE.lemonUrl) {
  const s = document.createElement("script"); s.src = "https://assets.lemonsqueezy.com/lemon.js"; s.defer = true;
  s.onload = () => window.createLemonSqueezy && window.createLemonSqueezy();
  document.head.appendChild(s);
}
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-price]").forEach(el => el.textContent = SITE.price);
  document.querySelectorAll("[data-buy]").forEach(a => {
    if (SITE.buyUrl) { a.href = SITE.buyUrl; if (SITE.lemonUrl) a.classList.add("lemonsqueezy-button"); }
    else { a.href = SITE_ROOT + "play/"; a.textContent = "Pro opens soon. Play free now"; }
  });
  window.createLemonSqueezy && window.createLemonSqueezy();
});
