#!/usr/bin/env node
// 520 Quest question-bank check. Runs on every pull request (.github/workflows/qcheck.yml) and locally:
//   node tools/qcheck/check_bank.js                       plain files only
//   CONTENT_KEY_FILE=path/to/content.key node tools/qcheck/check_bank.js   also the sealed (paid) files
//   ... --update-baseline                                 accept today's giveaway list as the new baseline
// Errors (wrong key, two right answers, duplicate choices, missing explanation, broken table/figure refs, missing
// figure files, explanations left behind by archived questions, figures borrowed from another passage, passages
// sharing a title or (near-)identical text,
// free copy that disagrees with the sealed copy) always fail. Giveaways (length/unit tells) fail only when
// they are new, i.e. not in tools/qcheck/baseline.json, which holds the ones the QA council already accepted.
const fs = require("fs"), path = require("path");
const { load, loadInline, keyFrom } = require("./load.js");
const { checkQuestion, checkRefs, norm } = require("./rules.js");
const { checkFigures } = require("./figs.js");
const { checkPassages } = require("./dupes.js");
const ROOT = path.resolve(__dirname, "../.."), BANK = path.join(ROOT, "play/bank"), BASE = path.join(__dirname, "baseline.json");
const key = keyFrom(process.env);
const L = load(BANK, key);
const all = loadInline(path.join(ROOT, "play/index.html")).concat(L.qs);
const errors = [], tells = [], sec = {};
const add = (list, r, msg) => list.push(`${r.id} (${r.file}): ${msg}`);
// Free copies (BP.json, CARS.json, FL.json, MN.json) must match their sealed twins exactly.
const twins = {};
for (const r of all) {
  const sealed = /\.enc\.json$/.test(r.file), group = r.file.replace(".enc", "");
  const tw = (twins[group] = twins[group] || {}), side = sealed ? "s" : "p";
  if (tw[r.id] && tw[r.id][side]) add(errors, r, `duplicate question id (also in ${tw[r.id][side].file})`);
  (tw[r.id] = tw[r.id] || {})[side] = r;
}
for (const g of Object.values(twins)) for (const t of Object.values(g)) if (t.p && t.s) {
  const a = t.p.q, b = t.s.q;
  if (a.a !== b.a) add(errors, t.p, `free copy has key ${"ABCD"[a.a]} but the sealed copy has ${"ABCD"[b.a]}`);
  else if (norm(a.q) !== norm(b.q) || a.o.some((o, i) => norm(o[0]) !== norm((b.o[i] || [])[0]))) add(errors, t.p, "free copy's question or choices differ from the sealed copy");
}
const seenTell = new Set();
for (const r of all) {
  const res = checkQuestion(r.q, L.ex[r.id], { strictFeedback: r.file !== "index.html" });
  res.errors.forEach(m => add(errors, r, m));
  checkRefs(r.q, r.p, L.ex[r.id]).forEach(m => add(errors, r, m));
  if (/\.enc\.json$/.test(r.file) || !twins[r.file.replace(".enc", "")][r.id].s) { // count each question once, sealed copy preferred
    res.tells.forEach(m => { const k = `${r.id}: ${m.split(":")[0]}`; if (!seenTell.has(k)) { seenTell.add(k); tells.push({ k, msg: `${r.id} (${r.file}): ${m}` }); } });
    if (res.longest !== null) { const s = r.q.s || (r.p && r.p.s) || "CARS"; const x = (sec[s] = sec[s] || [0, 0]); x[1]++; if (res.longest) x[0]++; }
  }
}
// Figures: missing files, explanations of archived questions, figures borrowed across passages.
let base = { rates: {}, tells: [] }; try { base = JSON.parse(fs.readFileSync(BASE, "utf8")); } catch (e) {}
const figs = checkFigures(all, L.ex, path.join(ROOT, "play/fig"), base.figShared || {}, !!key);
errors.push(...figs.errors);
// Passages: each needs its own title and its own text.
errors.push(...checkPassages(all).errors);
// Section-wide longest-answer rate (how often the key is the longest choice; ~25% is neutral). Only judged when the
// sealed bank is readable, because the free sample alone is too small. A PR fails if it pushes a section more than
// 1.5 points further from 25% than the baseline.
const rates = {}; for (const [s, [k, n]] of Object.entries(sec)) rates[s] = +(100 * k / n).toFixed(1);
if (key) for (const [s, r] of Object.entries(rates)) {
  const b = base.rates[s]; if (b == null || sec[s][1] < 200) continue;
  if (Math.abs(r - 25) > Math.abs(b - 25) + 1.5) errors.push(`${s}: the key is now the longest choice in ${r}% of questions (was ${b}%). New answer choices are giving the key away by length.`);
}
if (process.argv.includes("--update-baseline")) {
  if (!key) { console.error("Set CONTENT_KEY or CONTENT_KEY_FILE so the baseline covers the sealed files too."); process.exit(2); }
  base = { rates, tells: tells.map(t => t.k).sort(), figShared: figs.shared };
  fs.writeFileSync(BASE, JSON.stringify(base, null, 1) + "\n");
  console.log(`baseline.json now accepts ${tells.length} known giveaways, ${Object.keys(figs.shared).length} shared figures and today's section rates.`);
}
const known = new Set(base.tells), fresh = tells.filter(t => !known.has(t.k));

const out = [];
out.push(`## Question bank check`);
out.push(`Checked ${all.length.toLocaleString("en-US")} questions in ${L.files.length + 1} files.` + (L.skipped.length ? ` **Sealed files skipped** (${L.skipped.length}): add the CONTENT_KEY secret to check paid content.` : " Sealed (paid) files included."));
if (key) out.push(`How often the key is the longest choice: ` + Object.entries(rates).map(([s, r]) => `${s} ${r}%` + (base.rates[s] != null ? ` (baseline ${base.rates[s]}%)` : "")).join(", ") + ". About 25% is neutral.");
out.push("", `### Errors (${errors.length})`, ...(errors.length ? errors.slice(0, 200).map(e => "- " + e) : ["None."]));
out.push("", `### New giveaways (${fresh.length})`, ...(fresh.length ? fresh.slice(0, 200).map(t => "- " + t.msg) : ["None."]));
out.push("", `Known giveaways already accepted in baseline.json: ${tells.length - fresh.length}.`);
const text = out.join("\n");
console.log(text);
if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, text + "\n");
if (process.env.GITHUB_ACTIONS) [...errors, ...fresh.map(t => t.msg)].slice(0, 50).forEach(m => console.log(`::error title=Question bank::${m.replace(/\n/g, " ")}`));
process.exit(errors.length || fresh.length ? 1 : 0);
