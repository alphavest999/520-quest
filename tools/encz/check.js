// CI: every compressed sealed file (.encz) must have been built from the .enc.json that ships next to it.
// A mismatch means the bank was resealed without running tools/encz/build.js, so paid players would get old content.
const fs = require("fs"), path = require("path");
const B = path.join(__dirname, "..", "..", "play", "bank"), ix = JSON.parse(fs.readFileSync(path.join(B, "index.json"), "utf8"));
let bad = 0;
for (const f of ix.sealed || []) {
  const z = (ix.z || {})[f];
  if (!z) { console.log(`::warning::${f} has no compressed copy; players download the full file. Run tools/encz/build.js.`); continue; }
  const iv = JSON.parse(fs.readFileSync(path.join(B, f), "utf8")).iv;
  if (z.src !== iv || !fs.existsSync(path.join(B, z.f))) { console.log(`::error::${z.f} is stale or missing for ${f}. Run: CONTENT_KEY_FILE=... node tools/encz/build.js`); bad++; }
}
for (const f of Object.keys(ix.z || {})) if (!(ix.sealed || []).includes(f)) { console.log(`::error::index.json z lists ${f}, which is not sealed any more.`); bad++; }
console.log(bad ? `${bad} stale compressed file(s).` : "Compressed sealed files match their sources.");
process.exit(bad ? 1 : 0);
