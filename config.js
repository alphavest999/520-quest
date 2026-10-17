/* ===== Site settings: paste each plan's Lemon Squeezy checkout link once the store is live. ===== */
window.SITE = {
  // Lemon Squeezy checkout links (Product > Share > Checkout link), e.g. "https://520quest.lemonsqueezy.com/buy/xxxx".
  // While a link is empty, its button shows "Opening soon".
  plans: { monthly: "", sixmonth: "", yearly: "" }
};
/* ============================================================================================= */
// Checkout opens as a pop-up: dark, pink Pay button, no extra product text.
const popup = u => u + (u.includes("?") ? "&" : "?") + "embed=1&dark=1&media=0&desc=0&button_color=%23fb7185";
if (Object.values(SITE.plans).some(Boolean)) {
  const s = document.createElement("script"); s.src = "https://assets.lemonsqueezy.com/lemon.js"; s.defer = true;
  s.onload = () => window.createLemonSqueezy && window.createLemonSqueezy();
  document.head.appendChild(s);
}
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-plan]").forEach(a => {
    const u = SITE.plans[a.dataset.plan]; if (!u) return;
    a.href = popup(u); a.classList.add("lemonsqueezy-button"); a.removeAttribute("aria-disabled"); a.removeAttribute("tabindex");
    a.textContent = a.textContent.replace(/\s*·?\s*opening soon/i, "").replace(/^Opening soon$/i, "Choose this plan") || "Choose this plan";
  });
  window.createLemonSqueezy && window.createLemonSqueezy();
});
