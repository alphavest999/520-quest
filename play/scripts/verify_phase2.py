#!/usr/bin/env python3
"""Independent verifier for Phase 2 rich explanations (play/json/phase2/batch_*.json).

Runs per batch of 15 questions and flags:
  two-defensible   numeric choices within 0.5% of each other, or an ox that concedes
                   another choice is also correct/true
  needs-outside    wording that appeals to knowledge outside the passage
  needs-calculator roots, logs, or a calculator
  structural-slip  table stored as text, paragraph breaks inside a passage string,
                   duplicated key text, rationale leakage ("Why the others are wrong")
Usage: python3 play/scripts/verify_phase2.py [--quiet]
Exit code 1 when any failure is found.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bp_phase2 import candidates, clean, num, norm_table, tables

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BATCH = os.path.join(ROOT, "json", "phase2")
BP = os.path.join(ROOT, "bank", "BP.json")
L = "ABCD"
BANNED = [
    (r"textbook|in general|literature value|known that|standard value|outside the passage|"
     r"outside knowledge|from memory|normally|as we know", "needs-outside"),
    (r"use a calculator|calculator|log10|\bfourth root\b", "needs-calculator"),
    (r"also correct|also true|both are correct|either could|equally defensible", "two-defensible"),
    (r"Why the others are wrong|Correct: Correct|^Correct:", "structural-slip"),
]


def main():
    quiet = "--quiet" in sys.argv
    data = json.load(open(BP, encoding="utf-8"))
    P = {p["id"]: p for p in data["passages"]}
    files = sorted(glob.glob(os.path.join(BATCH, "batch_*.json")))
    if not files:
        print("no batch files")
        return 1
    fail, total = [], 0
    per_batch = []
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        bfail = 0
        for key, ent in d.items():
            total += 1
            pid, qi = key.rsplit("_", 1)
            pg = P.get(pid)
            if not pg or int(qi) >= len(pg["qs"]):
                fail.append((key, "structural-slip", "no matching BP question"))
                bfail += 1
                continue
            if pg.get("s") != "BB" or not (1261 <= int(pid[2:]) <= 1618):
                fail.append((key, "structural-slip", "outside Phase 2 scope (BB, bp1261-bp1618)"))
                bfail += 1
                continue
            q = pg["qs"][int(qi)]
            ox = ent.get("ox")
            if not isinstance(ox, list) or len(ox) != len(q["o"]):
                fail.append((key, "structural-slip", "ox must have one entry per option"))
                bfail += 1
                continue
            a = q["a"]
            if not ox[a].startswith("Correct."):
                fail.append((key, "structural-slip", "key entry does not start Correct."))
                bfail += 1
            for j, s in enumerate(ox):
                if j != a and not s.startswith("Incorrect."):
                    fail.append((key, "structural-slip", "non-key entry %d not marked Incorrect." % j))
                    bfail += 1
                if not 70 <= len(s) <= 520:
                    fail.append((key, "structural-slip", "entry %d length %d" % (j, len(s))))
                    bfail += 1
                for pat, tag in BANNED:
                    if re.search(pat, s, re.I):
                        fail.append((key, tag, "entry %d: /%s/" % (j, pat)))
                        bfail += 1
                if not re.search(r"\d|table|passage|reads|column|row", s, re.I):
                    fail.append((key, "structural-slip", "entry %d has no source anchor" % j))
                    bfail += 1
            if len({clean(s) for s in ox}) != len(ox):
                fail.append((key, "structural-slip", "duplicate ox text"))
                bfail += 1
            # negative stems: the non-key choices are true and must be affirmed
            if re.search(r"not supported|except|incorrect|false|not true", q["q"], re.I):
                for j, s in enumerate(ox):
                    if j != a and re.search(r"^(no statement|nothing in the passage|the passage's own account "
                                            r"does not support)", s.split(". ", 1)[-1], re.I):
                        fail.append((key, "two-defensible", "negative stem but choice %d is denied" % j))
                        bfail += 1
            # numeric choices too close to separate without over-precision
            vals = []
            for j, o in enumerate(q["o"]):
                t = clean(o[0]).strip()
                # only pure quantities can be "too close to separate"; prose with a day
                # number ("by day 7") is not a numeric choice
                if re.fullmatch(r"[-+]?\d+(?:\.\d+)?\s*(?:%|mmHg|mg|mL|ms|min|h|days?|weeks?)?\s*", t):
                    v = num(t)
                    if v is not None and "%" not in t:
                        vals.append((j, v))
            # values that each sit in a distinct labelled cell are separable by row/column,
            # so closeness alone is not a two-defensible defect there
            cells = set()
            for tb in tables(pg):
                for row in tb["r"]:
                    for c in row[1:]:
                        v = num(c)
                        if v is not None:
                            cells.add(round(v, 6))
            for i in range(len(vals)):
                for k in range(i + 1, len(vals)):
                    if abs(vals[i][1] - vals[k][1]) <= max(0.005, abs(vals[i][1]) * 0.005):
                        if round(vals[i][1], 6) in cells and round(vals[k][1], 6) in cells \
                                and round(vals[i][1], 6) != round(vals[k][1], 6):
                            continue
                        fail.append((key, "two-defensible", "choices %s and %s differ by <0.5%%"
                                     % (L[vals[i][0]], L[vals[k][0]])))
                        bfail += 1
            # key arithmetic must be reproducible from the table
            if re.search(r"closest (option|answer|choice)|provided options|illustrative|rounded for", q["x"], re.I):
                fail.append((key, "needs-calculator", "key relies on a hedge (closest/illustrative)"))
                bfail += 1
            tl = tables(pg)
            if pg.get("tbl") and not tl:
                fail.append((key, "structural-slip", "table stored as text, not rows/cells"))
                bfail += 1
            if any("\n\n" in t for t in pg["text"]):
                fail.append((key, "structural-slip", "paragraph break inside a passage string"))
                bfail += 1
        per_batch.append((os.path.basename(f), len(d), bfail))
    print("checked %d entries in %d batches" % (total, len(files)))
    if not quiet:
        for b, n, e in per_batch:
            print("  %-22s %2d entries  %2d flag(s)" % (b, n, e))
    if fail:
        kinds = {}
        for _, tag, _ in fail:
            kinds[tag] = kinds.get(tag, 0) + 1
        print("\n%d flag(s) across %d categor(ies): %s" % (len(fail), len(kinds), kinds))
        for k, tag, msg in fail[:40]:
            print("  %s [%s] %s" % (k, tag, msg))
        return 1
    print("\nAll Phase 2 checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
