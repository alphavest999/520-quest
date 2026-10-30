#!/usr/bin/env python3
"""Verifier for the bp* passage-batch source files (play/json/batch_bp_*.json).

Checks structure, ids, answer keys, banned AI/ELI10 wording, duplicate stems,
answer-letter spread, and the arithmetic written into fm.substitution.
Usage: python3 play/scripts/verify_bp.py [--quiet]
Exit code 1 if any error is found.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "json")
REQ = ["id", "passage_text", "table_data", "stem", "options", "correct",
       "explanation", "memorize", "fm", "correct_rationale_plain", "wrong",
       "sc", "mn", "source"]
FM_KEYS = ["formula", "variables", "values", "substitution", "why", "no_calc"]
BANNED = [
    r"ELI10", r"ELI-10", r"in plain words", r"plain-words", r"\banalogy\b",
    r"second ai", r"not verified against aamc", r"expert review",
    r"ai-generated", r"ai generated", r"\bai\b", r"as an ai",
    r"memorize_for_520",
]
ALLOWED_SOURCE = {"High-yield", "high-yield", ""}

ERR = []


def err(f, i, msg):
    ERR.append(f"{os.path.basename(f)}[{i}] {msg}")


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def check_arith(text):
    """Validate 'expression = value' fragments, including chains like '1 + 2 + 1 = 4'."""
    bad = []
    num = r"-?\d+(?:\.\d+)?"
    op = r"\s*[×x*/÷+\-−]\s*"
    chain = re.compile(rf"({num}(?:{op}{num})+)\s*=\s*({num})")
    for expr, rhs in chain.findall(text):
        total = None
        pending = None
        for tok in re.findall(rf"{num}|[×x*/÷+\-−]", expr):
            if tok in "×x*/÷+-−":
                pending = {"x": "*", "×": "*", "÷": "/", "−": "-"}.get(tok, tok)
                continue
            v = float(tok)
            if total is None:
                total = v
            else:
                if pending == "*":
                    total *= v
                elif pending == "/":
                    total = total / v if v else None
                elif pending == "+":
                    total += v
                else:
                    total -= v
        want = float(rhs)
        if total is None:
            bad.append(f"divide by zero in {expr}")
        elif abs(total - want) > max(0.011, abs(want) * 0.011):
            bad.append(f"{expr} = {rhs} (should be {round(total, 4)})")
    return bad


def main():
    quiet = "--quiet" in sys.argv
    files = sorted(glob.glob(os.path.join(ROOT, "batch_bp_*.json")))
    if not files:
        print("No batch_bp_*.json files found.")
        return 1
    seen_ids, seen_stems, total = {}, {}, 0
    per_file = []
    for f in files:
        base = os.path.basename(f)
        m = re.match(r"batch_bp_(\d{3})_(\d{3})\.json$", base)
        if not m:
            err(f, "-", "filename must look like batch_bp_001_016.json")
            continue
        lo, hi = int(m.group(1)), int(m.group(2))
        expect = hi - lo + 1
        try:
            data = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            err(f, "-", f"invalid JSON: {e}")
            continue
        if not isinstance(data, list):
            err(f, "-", "top level must be a list of questions")
            continue
        if len(data) != expect:
            err(f, "-", f"{len(data)} questions, filename promises {expect}")
        letters = {"A": 0, "B": 0, "C": 0, "D": 0}
        for i, q in enumerate(data, 1):
            total += 1
            tag = q.get("id", "?")
            fname = f
            for k in REQ:
                if k not in q:
                    err(fname, tag, f"missing {k}")
            qid = str(q.get("id", ""))
            if not re.fullmatch(r"bp_\d{3}", qid):
                err(fname, tag, "id must be bp_001 style")
            else:
                n = int(qid[3:])
                if not (lo <= n <= hi):
                    err(fname, tag, f"id outside file range {lo}-{hi}")
                if qid in seen_ids:
                    err(fname, tag, f"duplicate id (also in {seen_ids[qid]})")
                seen_ids[qid] = base
            opts = q.get("options") or {}
            if sorted(opts) != ["A", "B", "C", "D"]:
                err(fname, tag, "options must be exactly A-D")
            vals = [str(v).strip() for v in opts.values()]
            if any(not v for v in vals):
                err(fname, tag, "empty option text")
            if len({norm(v) for v in vals}) != len(vals):
                err(fname, tag, "duplicate option text")
            cor = q.get("correct")
            if cor not in opts:
                err(fname, tag, f"correct {cor!r} not one of the options")
            else:
                letters[cor] += 1
            wrong = q.get("wrong") or {}
            if sorted(wrong) != sorted(k for k in "ABCD" if k != cor):
                err(fname, tag, "wrong must cover exactly the three non-correct letters")
            for k, v in wrong.items():
                if not str(v).strip():
                    err(fname, tag, f"empty wrong[{k}]")
            mem = q.get("memorize")
            if not isinstance(mem, list) or not 2 <= len(mem) <= 4:
                err(fname, tag, "memorize must be a list of 2-4 strings")
            fm = q.get("fm") or {}
            if not isinstance(fm, dict):
                err(fname, tag, "fm must be an object")
            else:
                for k in FM_KEYS:
                    if not str(fm.get(k, "")).strip():
                        err(fname, tag, f"fm.{k} empty")
                for bad in check_arith(str(fm.get("substitution", "")) + " " + str(fm.get("no_calc", ""))):
                    err(fname, tag, f"arithmetic: {bad}")
            stem = str(q.get("stem", ""))
            if len(stem) < 25:
                err(fname, tag, "stem looks too short")
            ns = norm(stem)
            if ns in seen_stems:
                err(fname, tag, f"duplicate stem (also {seen_stems[ns]})")
            seen_stems[ns] = base
            for k in ("passage_text", "explanation", "correct_rationale_plain", "sc", "mn"):
                if not str(q.get(k, "")).strip():
                    err(fname, tag, f"{k} empty")
            src = q.get("source", "")
            if src not in ALLOWED_SOURCE:
                err(fname, tag, f'source must be "High-yield" (got {src!r})')
            blob = json.dumps(q, ensure_ascii=False)
            for b in BANNED:
                if re.search(b, blob, re.I):
                    err(fname, tag, f"banned wording /{b}/")
        if len(data) >= 8:
            for k, v in letters.items():
                if v == 0:
                    err(f, "-", f"no question uses answer {k}")
            top = max(letters.values())
            if top > max(3, len(data) // 3):
                err(f, "-", f"answer letters lopsided: {letters}")
        per_file.append((base, len(data), len(q.get("memorize", [])) if data else 0))
    print(f"checked {total} questions in {len(files)} file(s)")
    for b, n, _ in per_file:
        if not quiet:
            print(f"  {b}: {n} questions")
    if ERR:
        print(f"\n{len(ERR)} problem(s):")
        for e in ERR[:200]:
            print("  " + e)
        return 1
    print("\nAll structural checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
