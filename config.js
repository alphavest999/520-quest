/* ===== Site settings: paste each plan's Lemon Squeezy checkout link once the store is live. ===== */
window.SITE = {
  // Lemon Squeezy checkout links (Product > Share > Checkout link), e.g. "https://520quest.lemonsqueezy.com/buy/xxxx".
  // While a link is empty, its button shows "Opening soon".
  plans: {
    monthly: "https://unprocrastinate.lemonsqueezy.com/checkout/buy/6c302339-a93e-4978-99c6-bc350bae5c98",
    sixmonth: "https://unprocrastinate.lemonsqueezy.com/checkout/buy/063e7227-389c-4f07-adb9-c486684c7781",
    yearly: "https://unprocrastinate.lemonsqueezy.com/checkout/buy/1ddf71d5-9a93-477a-b290-77b480a2cd28"
  }
};
/* ============================================================================================= */
// Checkout opens as a pop-up: dark, pink Pay button, no extra product text.
// No embed=1 here: lemon.js adds it for the pop-up, so a click before lemon.js loads opens the normal full checkout page.
const popup = u => u + (u.includes("?") ? "&" : "?") + "dark=1&media=0&desc=0&button_color=%23fb7185";
if (Object.values(SITE.plans).some(Boolean)) {
  // Warm up connections to the checkout hosts, and swap Lemon Squeezy's wordless loading screen
  // (a pulsing dot on black) for a branded "Opening secure checkout" screen. Same CSS lives in play/index.html.
  ["https://unprocrastinate.lemonsqueezy.com", "https://assets.lemonsqueezy.com", "https://js.stripe.com"].forEach(h => {
    const l = document.createElement("link"); l.rel = "preconnect"; l.href = h; l.crossOrigin = ""; document.head.appendChild(l);
  });
  const st = document.createElement("style");
  st.textContent = `.lemonsqueezy-loader{background:rgba(7,15,34,.97)!important;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
.lemonsqueezy-loader main>div{display:none}
.lemonsqueezy-loader main::before{content:"";width:46px;height:46px;border-radius:50%;border:4px solid rgba(255,255,255,.14);border-top-color:#ec4899;animation:lsq-spin .8s linear infinite}
.lemonsqueezy-loader main::after{content:"🔒 Opening secure checkout…";color:#f5f7fb;font-size:18px;font-weight:700;margin-top:20px}
.lemonsqueezy-loader::after{content:"Payments are handled by Lemon Squeezy, our payment partner. Cards are processed by Stripe and never touch 520 Quest.";position:absolute;left:50%;top:calc(50% + 52px);transform:translateX(-50%);width:min(340px,86vw);text-align:center;color:#a3b0cc;font-size:13.5px;line-height:1.5}
@keyframes lsq-spin{to{transform:rotate(360deg)}}`;
  document.head.appendChild(st);
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
