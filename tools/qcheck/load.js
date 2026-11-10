// Loads every question in play/bank (plain + sealed) into one flat list. Used by check_bank.js.
const fs = require("fs"), path = require("path"), crypto = require("crypto");
function keyFrom(env) {
  const raw = (env.CONTENT_KEY || "").trim() || (env.CONTENT_KEY_FILE && fs.existsSync(env.CONTENT_KEY_FILE) ? fs.readFileSync(env.CONTENT_KEY_FILE, "utf8").trim() : "");
  return raw ? Buffer.from(raw, "base64") : null;
}
function unseal(file, key) {
  const e = JSON.parse(fs.readFileSync(file, "utf8")), ct = Buffer.from(e.ct, "base64");
  const d = crypto.createDecipheriv("aes-256-gcm", key, Buffer.from(e.iv, "base64"));
  d.setAuthTag(ct.subarray(-16));
  return JSON.parse(Buffer.concat([d.update(ct.subarray(0, -16)), d.final()]).toString("utf8"));
}
function load(bankDir, key) {
  const qs = [], passages = [], ex = {}, files = [], skipped = [];
  const read = (rel) => {
    const f = path.join(bankDir, rel);
    if (!fs.existsSync(f)) return null;
    if (/\.enc\.json$/.test(rel)) { if (!key) { skipped.push(rel); return null; } files.push(rel); return unseal(f, key); }
    files.push(rel); return JSON.parse(fs.readFileSync(f, "utf8"));
  };
  const seen = new Set();
  for (const rel of ["BB.json", "CP.json", "PS.json", "DX.json", "CARS.json", "BP.json", "FL.json", "MN.json", "CARS.enc.json", "BP.enc.json", "FL.enc.json", "MN.enc.json"]) {
    const j = read(rel); if (!j) continue;
    (j.questions || []).forEach((q, i) => {
      const id = q.id || `${rel}#${i}`;
      qs.push({ q, id, file: rel, p: null });
    });
    (j.passages || []).forEach(p => {
      passages.push({ p, file: rel });
      (p.qs || []).forEach((q, i) => qs.push({ q, id: q.id || `${p.id}_${i}`, file: rel, p }));
    });
  }
  const exDir = path.join(bankDir, "ex");
  if (fs.existsSync(exDir)) for (const fn of fs.readdirSync(exDir).sort()) {
    if (!/\.json$/.test(fn) || fn === "index.json") continue;
    const j = read("ex/" + fn); if (!j) continue;
    for (const [id, e] of Object.entries(j)) ex[id] = e;
  }
  return { qs, passages, ex, files, skipped };
}
module.exports = { load, keyFrom, unseal };
// The ~130 older questions and CARS passages written straight into play/index.html (ids q1.., p1..).
function loadInline(indexHtml) {
  if (!fs.existsSync(indexHtml)) return [];
  const src = fs.readFileSync(indexHtml, "utf8");
  const a = src.indexOf("const QUESTIONS = [];"), m = src.slice(a).match(/const PASSAGES = \[[\s\S]*?\n\];/);
  if (a < 0 || !m) return [];
  const code = src.slice(a, a + m.index + m[0].length) + "\n;({ QUESTIONS, PASSAGES })";
  let r; try { r = require("vm").runInNewContext(code, {}); } catch (e) { return []; }
  const out = r.QUESTIONS.map(q => ({ q, id: q.id, file: "index.html", p: null }));
  r.PASSAGES.forEach(p => (p.qs || []).forEach((q, i) => out.push({ q, id: p.id + "_" + i, file: "index.html", p })));
  return out;
}
module.exports.loadInline = loadInline;
