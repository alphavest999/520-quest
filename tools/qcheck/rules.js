// The rules check_bank.js applies to one question. Errors block a merge; "tells" (giveaways) only block when new.
const NUM = /[-−+]?\d[\d,]*(?:\.\d+)?/;
const UNIT = /(?:^|[\s\d])(%|°C|°|K|J|kJ|kJ\/mol|J\/mol|cal|kcal|eV|W|kW|V|mV|A|mA|Ω|C|N|Pa|kPa|atm|mmHg|torr|Torr|bar|L|mL|µL|μL|m|cm|mm|nm|µm|μm|km|s|ms|µs|min|h|hr|g|kg|mg|µg|μg|ng|mol|mmol|µmol|μmol|M|mM|µM|μM|nM|Hz|kHz|dB|T|D|m\/s|m\/s²|m²|m³|cm³|L\/min|mL\/min|g\/mol|g\/L|mg\/mL|J\/K|bpm|beats\/min|kb|bp|kDa|Da)(?=$|[\s.,;)\/·²³])/;
const plain = s => String(s || "").replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
const norm = s => plain(s).replace(/[−–]/g, "-").replace(/\s+/g, "").replace(/[.,;:!?]+$/, "");
const isNumeric = t => NUM.test(t) && plain(t).replace(/[-−+\d.,\s%×^⁻⁰¹²³⁴⁵⁶⁷⁸⁹()\/]/g, "").length <= 12;
const unitOf = t => { const m = plain(t).match(UNIT); return m ? m[1] : ""; };
const isCorrect = s => /^\s*Correct\b/i.test(plain(s));

// Returns { errors: [msg], tells: [msg] } for one question. ex = rich explanation entry (or undefined).
function checkQuestion(q, ex, { strictFeedback }) {
  const errors = [], tells = [];
  if (!plain(q.q) || plain(q.q).length < 8) errors.push("question stem is missing or too short");
  if (!Array.isArray(q.o) || q.o.length !== 4) { errors.push(`needs exactly 4 choices (has ${Array.isArray(q.o) ? q.o.length : 0})`); return { errors, tells }; }
  q.o.forEach((o, i) => { if (!Array.isArray(o) || !plain(o[0])) errors.push(`choice ${"ABCD"[i]} is empty`); });
  if (!Number.isInteger(q.a) || q.a < 0 || q.a > 3) { errors.push(`answer key "${q.a}" is not 0-3`); return { errors, tells }; }
  const txt = q.o.map(o => plain(o[0])), fb = q.o.map(o => plain(o[1]));
  const dup = txt.map(norm).filter((t, i, a) => t && a.indexOf(t) !== i);
  if (dup.length) errors.push(`duplicate choices: "${txt[txt.map(norm).indexOf(dup[0])]}"`);
  // Exactly one right answer: no wrong choice may be explained as "Correct", and (bank files) the key must be.
  const corr = fb.map(isCorrect);
  corr.forEach((c, i) => { if (c && i !== q.a) errors.push(`choice ${"ABCD"[i]} is explained as "Correct" but the key is ${"ABCD"[q.a]} (two right answers or a wrong key)`); });
  if (strictFeedback && !corr[q.a]) errors.push(`the key ${"ABCD"[q.a]} is not explained as "Correct" (wrong key?)`);
  if (ex && Array.isArray(ex.ox)) {
    if (ex.ox.length !== 4) errors.push(`full explanation has ${ex.ox.length} choice notes, needs 4`);
    else ex.ox.forEach((s, i) => {
      if (i === q.a && !isCorrect(s)) errors.push(`full explanation for the key ${"ABCD"[i]} doesn't start "Correct" (wrong key?)`);
      if (i !== q.a && isCorrect(s)) errors.push(`full explanation calls ${"ABCD"[i]} "Correct" but the key is ${"ABCD"[q.a]}`);
    });
  }
  if (strictFeedback ? !plain(q.x) || plain(q.x).length < 40 : !plain(q.x) && !(ex && Array.isArray(ex.ox)) && !fb.every(Boolean)) errors.push("no explanation (or a stub under 40 characters)");
  if (!fb.every(Boolean) && !(ex && Array.isArray(ex.ox))) errors.push("a choice has no reason why it's right or wrong");
  // Giveaways.
  const nums = txt.map(isNumeric);
  if (nums.every(Boolean)) {
    const u = txt.map(unitOf), ku = u[q.a];
    if (ku && u.filter(x => x === ku).length === 1 && u.filter(Boolean).length >= 2 && !plain(q.q).includes(ku)) tells.push(`unit tell: only the key uses "${ku}"`);
    if (ku && u.filter(Boolean).length === 1) tells.push(`unit tell: only the key has a unit ("${ku}")`);
    if (!ku && u.filter(Boolean).length === 3) tells.push("unit tell: the key is the only choice without a unit");
  } else {
    const len = txt.map(t => t.length), others = len.filter((_, i) => i !== q.a), mx = Math.max(...others), mn = Math.min(...others);
    if (len[q.a] > mx * 1.5 && len[q.a] - mx >= 25) tells.push(`length tell: the key is much longer than every other choice (${len[q.a]} vs ≤${mx} chars)`);
    if (len[q.a] * 1.8 < mn && mn - len[q.a] >= 25) tells.push(`length tell: the key is much shorter than every other choice (${len[q.a]} vs ≥${mn} chars)`);
  }
  if (/\b(all|none) of the above\b/i.test(txt.join(" | "))) tells.push('uses "all/none of the above"');
  return { errors, tells, longest: nums.every(Boolean) ? null : txt.every((t, i) => i === q.a || t.length < txt[q.a].length) };
}
// A passage question (or its explanation) that points at a table, figure or paragraph the passage doesn't have.
function checkRefs(q, p, ex) {
  if (!p) return [];
  // The stem, the choices and the explanation all have to point at things this passage really has.
  const exTxt = ex ? JSON.stringify(ex, (k, v) => (k === "fig" || k === "graph" || k === "tb" ? undefined : v)) : "";
  const out = [], stem = plain(q.q) + " " + q.o.map(o => plain(o[0])).join(" ") + " " + plain(exTxt);
  const ptxt = (p.text || []).map(plain).join(" ") + " " + JSON.stringify(p.tbl || "") + JSON.stringify(p.graph || "") + JSON.stringify(p.fig || "") + JSON.stringify(p.figs || "");
  for (const m of stem.matchAll(/\b(Table|Figure)\s+(\d+)/g)) if (!new RegExp(`\\b${m[1]}\\s+${m[2]}\\b`).test(ptxt)) out.push(`refers to ${m[1]} ${m[2]}, which the passage doesn't have`);
  for (const m of stem.matchAll(/\bparagraph\s+(\d+)\b/gi)) if (+m[1] > (p.text || []).length) out.push(`refers to paragraph ${m[1]}, but the passage has ${(p.text || []).length}`);
  return out;
}
module.exports = { checkQuestion, checkRefs, plain, norm };
