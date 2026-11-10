// Passage uniqueness: every passage needs its own specific title and its own text. Catches
//  - two different passages with the same title (e.g. a topic name such as "How light and sound interact with matter"
//    reused as the title of 35 passages), or a placeholder title ("<category> · passage") left by a build script;
//  - two passages whose text is the same or nearly the same (shares most of its 8-word runs with another passage).
// A free copy and its sealed twin share an id and count once.
const norm = s => String(s || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
function grams(text, n = 8) {
  const w = norm(text).split(" "), g = new Set();
  for (let i = 0; i + n <= w.length; i++) g.add(w.slice(i, i + n).join(" "));
  return g;
}
function checkPassages(all, { near = 0.5 } = {}) {
  const errors = [], byId = new Map();
  for (const r of all) if (r.p && r.p.id && (!byId.has(r.p.id) || /\.enc\.json$/.test(r.file))) byId.set(r.p.id, r);
  const ps = [...byId.values()], where = r => `${r.p.id} (${r.file})`;
  // Titles
  const titles = new Map();
  for (const r of ps) {
    const t = norm(r.p.title);
    if (!t) { errors.push(`${where(r)}: passage has no title`); continue; }
    if (/ · passage$/i.test(String(r.p.title))) errors.push(`${where(r)}: placeholder title "${r.p.title}". Give the passage a title that names its own content`);
    (titles.get(t) || titles.set(t, []).get(t)).push(r);
  }
  for (const rs of titles.values()) if (rs.length > 1)
    errors.push(`${rs.length} passages share the title "${rs[0].p.title}": ${rs.map(where).join(", ")}. Give each one a title that names its own content`);
  // Text: exact copies, then near copies by shared 8-word runs (runs found in many passages are boilerplate and ignored)
  const G = ps.map(r => grams([].concat(r.p.text || []).join(" "))), seen = new Map(), owners = new Map();
  ps.forEach((r, i) => {
    const t = norm([].concat(r.p.text || []).join(" "));
    if (seen.has(t)) errors.push(`${where(r)}: passage text is identical to ${where(ps[seen.get(t)])}`); else seen.set(t, i);
    for (const g of G[i]) (owners.get(g) || owners.set(g, []).get(g)).push(i);
  });
  const pair = new Map();
  for (const list of owners.values()) if (list.length > 1 && list.length <= 10)
    for (let a = 0; a < list.length; a++) for (let b = a + 1; b < list.length; b++) { const k = list[a] * 1e5 + list[b]; pair.set(k, (pair.get(k) || 0) + 1); }
  for (const [k, c] of pair) {
    const a = Math.floor(k / 1e5), b = k % 1e5, share = c / Math.max(1, Math.min(G[a].size, G[b].size));
    if (share >= near && norm(ps[a].p.text) !== norm(ps[b].p.text)) errors.push(`${where(ps[a])} and ${where(ps[b])}: ${Math.round(100 * share)}% of the shorter passage's text also appears in the other. Rewrite one so each passage is unique`);
  }
  return { errors, count: ps.length };
}
module.exports = { checkPassages };
