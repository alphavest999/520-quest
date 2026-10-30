#!/usr/bin/env node
// Replace the old Qbank size in Mastery Sheet content.
// Usage: node scripts/updateSheetCounts.js sheets/3A.json [more.json ...]
// Works on plain (free) sheet files: {"id", "title", "html"}.
// The 27 sealed sheets (*.enc.json) are AES-encrypted; run this on their DECRYPTED json (needs the content key
// held by the owner), then re-seal them. Until then the app shows a "Now 5,904 Qbank" badge next to the old number.
const fs = require("fs");
const OLD = /5,180(?:[ -]question)?(?: Qbank)?/g, NEW = "5,904-question Qbank (80% passage)";
for (const f of process.argv.slice(2)) {
  const d = JSON.parse(fs.readFileSync(f, "utf8"));
  if (typeof d.html !== "string") { console.log(f + ": no html field (sealed?), skipped"); continue; }
  const n = (d.html.match(OLD) || []).length;
  if (!n) { console.log(f + ": nothing to change"); continue; }
  d.html = d.html.replace(OLD, NEW); fs.writeFileSync(f, JSON.stringify(d)); console.log(f + ": replaced " + n);
}
