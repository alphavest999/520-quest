// Renders the Lemon Squeezy product images (4:3, 1652x1240, LS's recommended size)
// in the same look as the 520quest.com landing page.
// Run from the repo root:  node tools/lemonsqueezy/render.js
// Output: images/lemonsqueezy/*.png
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '../..');
const OUT = path.join(ROOT, 'images/lemonsqueezy');
const W = 1652, H = 1240;
const img = p => 'file://' + path.join(ROOT, 'images', p);

const CSS = `
:root { --bg:#070f22; --text:#f5f7fb; --muted:#a3b0cc; --dim:#6f7fa3; --pink:#ec4899; --pink-2:#f472b6; --good:#4ade80;
  --grad: linear-gradient(100deg,#f472b6 0%,#ec4899 35%,#a78bfa 70%,#67e8f9 100%);
  --display:"Chakra Petch",sans-serif; --body:"Figtree",sans-serif; }
* { box-sizing:border-box; margin:0; }
body { width:${W}px; height:${H}px; overflow:hidden; background:var(--bg); color:var(--text); font-family:var(--body); -webkit-font-smoothing:antialiased; }
.slide { position:relative; width:100%; height:100%; isolation:isolate; overflow:hidden; padding:96px 104px; }
.bg { position:absolute; inset:0; z-index:-2; background:radial-gradient(60% 60% at 75% 40%, rgb(236 72 153 / .22), transparent 70%), radial-gradient(50% 50% at 90% 85%, rgb(103 232 249 / .14), transparent 70%), var(--bg); }
.bg img { width:100%; height:100%; object-fit:cover; object-position:70% center; opacity:.7; }
.slide::after { content:""; position:absolute; inset:0; z-index:-1; background:linear-gradient(90deg, var(--bg) 22%, rgb(7 15 34 / .55) 55%, transparent 85%), linear-gradient(0deg, var(--bg), transparent 35%); }
.logo { display:flex; align-items:center; gap:16px; font:700 34px/1 var(--display); letter-spacing:.02em; }
.logo i { width:60px; height:60px; border-radius:18px; background:linear-gradient(135deg,#f472b6,#db2777); display:grid; place-items:center; font:700 20px/1 var(--display); font-style:normal; box-shadow:0 8px 28px -6px rgb(236 72 153 / .8); }
.grad { background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
.eyebrow { display:inline-flex; align-items:center; gap:14px; font:700 22px/1 var(--display); letter-spacing:.22em; text-transform:uppercase; color:var(--pink-2); }
.eyebrow::before { content:""; width:34px; height:3px; background:currentColor; border-radius:2px; }
h1 { font:700 104px/1 var(--display); letter-spacing:-.01em; }
h2 { font:700 84px/1.04 var(--display); letter-spacing:-.01em; }
.lede { font-size:31px; line-height:1.45; color:var(--muted); }
.copy { position:absolute; left:104px; top:96px; bottom:96px; width:820px; display:flex; flex-direction:column; justify-content:center; gap:36px; }
.copy > .logo { position:absolute; top:0; }
.foot { position:absolute; bottom:0; }
.price { display:flex; align-items:baseline; gap:16px; }
.price b { font:700 136px/1 var(--display); }
.price span { font-size:36px; color:var(--muted); font-weight:600; }
.pill { align-self:flex-start; padding:12px 22px; border-radius:999px; background:linear-gradient(135deg,#f472b6,#ec4899 60%,#db2777); font:800 24px/1 var(--body); color:#fff; box-shadow:0 10px 40px -10px rgb(236 72 153 / .7); }
.pill.ghost { background:rgb(255 255 255 / .08); border:1px solid rgb(255 255 255 / .18); box-shadow:none; color:var(--text); }
.checks { display:grid; grid-template-columns:1fr 1fr; gap:16px 30px; font-size:27px; color:var(--text); font-weight:600; }
.checks span::before { content:"✓"; color:var(--good); font-weight:800; margin-right:12px; }
.foot { font-size:24px; color:var(--dim); }
.phone { position:absolute; width:400px; aspect-ratio:585/1266; border-radius:60px; padding:13px; background:linear-gradient(160deg,#2a3555,#0d1428 40%,#1b2440); box-shadow:0 0 0 1px rgb(255 255 255 / .12), 0 60px 120px -30px rgb(0 0 0 / .85), 0 40px 100px -40px rgb(236 72 153 / .6); }
.phone img { width:100%; height:100%; object-fit:cover; object-position:top; border-radius:48px; background:#fff; }
.phone::before { content:""; position:absolute; top:24px; left:50%; translate:-50% 0; width:118px; height:32px; border-radius:20px; background:#05080f; z-index:2; }
`;

const logo = `<div class="logo"><i>520</i>520 Quest</div>`;
const ALL = ['5,904 questions', '830 science passages', '100 CARS passages', '33 Mastery Sheets', '150 mnemonics', '20 full and mini exams'];

const plans = [
  { file: 'plan-monthly', name: 'Monthly', price: '$14.99', per: '/ month', tag: 'Cancel anytime', ghost: true,
    lede: 'Full access for your final push, as long as you need it.' },
  { file: 'plan-6-months', name: '6 Months', price: '$44.99', per: 'every 6 months', tag: 'Just $7.50 a month · save 50%',
    lede: 'A full MCAT prep season, from diagnostic to test day.' },
  { file: 'plan-yearly', name: 'Yearly', price: '$59.99', per: '/ year', tag: 'Best value · $5 a month · save 67%',
    lede: 'A whole year of practice for the price of four months.' },
];

const phones = (a, b, c) => `
  <div class="phone" style="right:350px; top:270px; width:330px; rotate:-8deg; opacity:.85">${a ? `<img src="${img('app/' + a)}">` : ''}</div>
  <div class="phone" style="right:30px; top:310px; width:310px; rotate:7deg; opacity:.75">${c ? `<img src="${img('app/' + c)}">` : ''}</div>
  <div class="phone" style="right:150px; top:120px; width:450px; z-index:3">${b ? `<img src="${img('app/' + b)}">` : ''}</div>`;

function planSlide(p) {
  return `<div class="slide"><div class="bg"><img src="${img('hero-bg.webp')}"></div>
  <div class="copy">${logo}
    <span class="eyebrow" >${p.name} plan</span>
    <div class="price"><b>${p.price}</b><span>${p.per}</span></div>
    <span class="pill${p.ghost ? ' ghost' : ''}">${p.tag}</span>
    <p class="lede">${p.lede} <b style="color:var(--text)">Unlocks everything:</b></p>
    <div class="checks">${ALL.map(x => `<span>${x}</span>`).join('')}</div>
    <p class="foot">Works on any phone or computer · 520quest.com</p>
  </div>${phones('map.webp', 'answers.webp', 'course.webp')}</div>`;
}

const features = [
  { file: 'feature-1-explanations', eyebrow: 'Answer and learn', title: 'Every choice <span class="grad">explained.</span>',
    lede: 'See why the right answer is right and why each wrong one is wrong, right after you answer. Tag how you missed it so the app knows what to fix.',
    shots: ['question.webp', 'answers.webp', 'explain.webp'] },
  { file: 'feature-2-plan', eyebrow: 'Your plan', title: 'Practice where your <span class="grad">points leak.</span>',
    lede: 'A timed diagnostic finds your weakest areas, then the Skill map and your daily plan keep you working on them.',
    shots: ['me.webp', 'map.webp', 'welcome.webp'] },
  { file: 'feature-3-course', eyebrow: 'Course and exams', title: 'Review it. <span class="grad">Test it.</span>',
    lede: '33 Mastery Sheets, the Memorization Checklist, 150 mnemonics, timed full-length exams and boss battles.',
    shots: ['course.webp', 'exams.webp', 'boss.webp'] },
];

function featureSlide(f) {
  return `<div class="slide"><div class="bg"><img src="${img('cta-bg.webp')}"></div>
  <div class="copy" style="width:700px">${logo}
    <span class="eyebrow" >${f.eyebrow}</span>
    <h2>${f.title}</h2>
    <p class="lede">${f.lede}</p>
    <p class="foot">Included in every paid plan · 520quest.com</p>
  </div>${phones(f.shots[0], f.shots[1], f.shots[2])}</div>`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const head = `<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=Figtree:wght@400;600;800&display=swap"><style>${CSS}</style>`;
  const jobs = [...plans.map(p => [p.file, planSlide(p)]), ...features.map(f => [f.file, featureSlide(f)])];
  for (const [file, body] of jobs) {
    const tmp = path.join(OUT, '.tmp.html');
    fs.writeFileSync(tmp, head + body);
    await page.goto('file://' + tmp, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(OUT, file + '.png') });
    fs.unlinkSync(tmp);
    console.log('wrote', file + '.png');
  }
  await browser.close();
})();
