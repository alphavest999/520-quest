// Figure consistency: every figure an explanation shows must exist, belong to a live question, and not be
// borrowed from another passage. Shared figures the QA council already read and accepted are listed in
// baseline.json under "figShared" (figure file -> the passages allowed to use it). Without the content key only the
// missing-file check runs, because most questions and passages are sealed.
const fs = require("fs"), path = require("path");
const IMG = /\.(svg|png|jpe?g|webp|gif)$/i;
function figFiles(o, out = []) {
  if (!o || typeof o !== "object") return out;
  if (typeof o.f === "string" && IMG.test(o.f)) out.push(o.f);
  for (const v of Object.values(o)) figFiles(v, out);
  return out;
}
function checkFigures(all, ex, figDir, allowed = {}, full = true) {
  const errors = [], byId = {}, uses = {};
  for (const r of all) byId[r.id] = r;
  for (const [id, e] of Object.entries(ex)) {
    const r = byId[id];
    if (!r) { if (full) errors.push(`${id} (ex): explanation has no question; it belongs to an archived or renamed question, so delete it or fix the id`); continue; }
    for (const f of figFiles(e)) {
      if (!fs.existsSync(path.join(figDir, f))) errors.push(`${id} (${r.file}): figure fig/${f} doesn't exist, so the image is broken`);
      const owner = r.p ? r.p.id : null;
      (uses[f] = uses[f] || { passages: new Set(), ids: [] }).ids.push(id);
      if (owner) uses[f].passages.add(owner);
    }
  }
  const shared = {};
  for (const [f, u] of Object.entries(uses)) {
    const ps = [...u.passages].sort();
    if (ps.length < 2 || !full) continue;
    shared[f] = ps;
    const ok = new Set(allowed[f] || []), fresh = ps.filter(p => !ok.has(p));
    if (fresh.length) errors.push(`figure fig/${f} is used by ${ps.length} different passages (${ps.join(", ")}). A figure borrowed from another passage often shows the wrong labels or numbers: give ${fresh.join(", ")} its own figure, or, after checking every label matches, accept it with --update-baseline`);
  }
  return { errors, shared };
}
module.exports = { checkFigures, figFiles };
