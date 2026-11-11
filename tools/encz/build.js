/* Compressed copies of the sealed Qbank files, so paid players download about 4 MB instead of 17 MB on first open.
   For every bank/*.enc.json listed in bank/index.json "sealed", writes bank/<name>.encz:
     12-byte IV, then AES-256-GCM ciphertext + tag of gzip(the same JSON).
   The app fetches the .encz when the browser has DecompressionStream and falls back to the .enc.json otherwise.
   index.json gets z: { "BP.enc.json": { f: "BP.encz", src: <iv of the .enc.json it was made from> } }
   so tools/encz/check.js (CI) catches a reseal that forgot to rebuild these.
   Usage: CONTENT_KEY_FILE=/path/content.key node tools/encz/build.js   (or CONTENT_KEY=<base64>)
   Run it after every seal_bank.js run (seal_bank.js calls it itself). */
const fs = require("fs"), path = require("path"), crypto = require("crypto"), zlib = require("zlib");
const B = path.join(__dirname, "..", "..", "play", "bank");
const k64 = process.env.CONTENT_KEY || (process.env.CONTENT_KEY_FILE && fs.readFileSync(process.env.CONTENT_KEY_FILE, "utf8"));
if (!k64) { console.error("Set CONTENT_KEY_FILE (or CONTENT_KEY)."); process.exit(1); }
const key = Buffer.from(k64.trim(), "base64");
const ix = JSON.parse(fs.readFileSync(path.join(B, "index.json"), "utf8"));
ix.z = {};
for (const f of ix.sealed || []) {
  const box = JSON.parse(fs.readFileSync(path.join(B, f), "utf8")), ct = Buffer.from(box.ct, "base64");
  const d = crypto.createDecipheriv("aes-256-gcm", key, Buffer.from(box.iv, "base64"));
  d.setAuthTag(ct.subarray(ct.length - 16));
  const pt = Buffer.concat([d.update(ct.subarray(0, ct.length - 16)), d.final()]);
  JSON.parse(pt.toString("utf8"));   // must be valid JSON
  const gz = zlib.gzipSync(pt, { level: 9 }), iv = crypto.randomBytes(12), c = crypto.createCipheriv("aes-256-gcm", key, iv);
  const out = Buffer.concat([iv, c.update(gz), c.final(), c.getAuthTag()]), zf = f.replace(/\.enc\.json$/, ".encz");
  fs.writeFileSync(path.join(B, zf), out);
  ix.z[f] = { f: zf, src: box.iv };
  console.log(f, "->", zf, (fs.statSync(path.join(B, f)).size / 1e6).toFixed(1), "MB ->", (out.length / 1e6).toFixed(1), "MB");
}
fs.writeFileSync(path.join(B, "index.json"), JSON.stringify(ix));
