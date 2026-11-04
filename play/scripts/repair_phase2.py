#!/usr/bin/env python3
"""Minimal source repairs for Phase 2 passages, with a before/after record.

Usage: python3 play/scripts/repair_phase2.py bp1262 [more ids]
Only repairs that are objectively verifiable are applied: a table stored as
stringified columns/rows is rebuilt as real header/row lists. The record is kept in
play/json/phase2/repairs_pending.json until the v59 merge writes it to held_back.json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bp_phase2 import norm_table

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BP = os.path.join(ROOT, "bank", "BP.json")
REC = os.path.join(ROOT, "json", "phase2", "repairs_pending.json")


def main():
    ids = sys.argv[1:]
    if not ids:
        print("give one or more passage ids")
        return 1
    data = json.load(open(BP, encoding="utf-8"))
    by = {p["id"]: p for p in data["passages"]}
    rec = json.load(open(REC)) if os.path.exists(REC) else {}
    changed = 0
    for pid in ids:
        p = by.get(pid)
        if not p:
            print(pid, "not found")
            continue
        fixed = []
        for t in p.get("tbl") or []:
            h = t.get("h")
            if isinstance(h, list) and h and h[0] in ("columns", "rows"):
                n = norm_table(t)
                if n:
                    fixed.append({"before": t, "after": n})
        if not fixed:
            print(pid, "no structural repair needed")
            continue
        p["tbl"] = [f["after"] for f in fixed]
        for f in fixed:
            rec.setdefault(pid, []).append({
                "field": "tbl",
                "why": "table was stored as stringified columns/rows, so it could not render or be read",
                "before": f["before"],
                "after": f["after"],
            })
        changed += 1
        print(pid, "rebuilt", len(fixed), "table(s)")
    if changed:
        with open(BP, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        json.dump(rec, open(REC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("repaired", changed, "passage(s); record:", REC)
    return 0


if __name__ == "__main__":
    sys.exit(main())
