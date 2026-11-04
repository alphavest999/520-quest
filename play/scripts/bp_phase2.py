#!/usr/bin/env python3
"""Shared helpers for the Phase 2 bp* rich explanations (passages 201-400).

Source of truth: play/bank/BP.json. Every sentence written into an ox item must be
traceable to the passage text, a table cell, or the question's own rationale.
"""
import ast
import json
import re

SUP = str.maketrans({"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
                     "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-", "⁺": "+"})
DASH = {"\u2011": "-", "\u2013": "-", "\u2014": "-", "\u2212": "-", "\u202f": " ",
        "\xa0": " ", "\u2009": " ", "\u200b": ""}
LETTERS = "ABCD"


def clean(s):
    s = str(s)
    for k, v in DASH.items():
        s = s.replace(k, v)
    return s.translate(SUP)


def num(s):
    """Parse the first number in a string, handling 5.2×10⁶ and −22."""
    t = clean(s).replace(",", "").replace("−", "-")
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*[×x]\s*10\s*\^?\s*(-?\d+)", t)
    if m:
        return float(m.group(1)) * (10 ** int(m.group(2)))
    m = re.search(r"-?\d+(?:\.\d+)?", t)
    return float(m.group()) if m else None


def fmt(v):
    if v is None:
        return "?"
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return ("%.3f" % v).rstrip("0").rstrip(".")


# ---------------------------------------------------------------- tables
def _lit(s):
    try:
        v = ast.literal_eval(str(s))
        return v if isinstance(v, list) else None
    except Exception:
        return None


def norm_table(t):
    """Return {'h': [...], 'r': [[...]]} or None. Repairs the three broken table layouts:
       A. h == ['columns','rows'], r == [[str(cols), str(rows)]]
       B. a proper header, but r rows are single cells holding stringified lists (transposed)
       C. already well formed."""
    if not isinstance(t, dict):
        return None
    h, r = t.get("h"), t.get("r")
    if not isinstance(h, list) or not isinstance(r, list):
        return None
    # A: header replaced by a two-label placeholder; parse every cell for list literals
    if h and isinstance(h[0], str) and h[0] in ("columns", "rows"):
        lists = []
        for row in r:
            for c in (row if isinstance(row, list) else [row]):
                v = _lit(c)
                if isinstance(v, list):
                    lists.append(v)
        if len(lists) >= 2 and all(isinstance(x, str) for x in lists[0]) \
                and all(isinstance(x, list) for x in lists[1]):
            cols, rows = lists[0], lists[1]
            return {"h": [clean(c) for c in cols],
                    "r": [[clean(c) for c in row] for row in rows]}
        return None
    if not all(isinstance(x, str) for x in h):
        return None
    if all(isinstance(row, list) and len(row) == len(h) for row in r) and r:
        return {"h": [clean(x) for x in h], "r": [[clean(c) for c in row] for row in r]}
    # B0: one physical row whose cells are each a stringified column (fully transposed)
    if len(r) == 1 and isinstance(r[0], list) and len(r[0]) == len(h):
        cols = [_lit(c) for c in r[0]]
        if all(isinstance(x, list) for x in cols) and len({len(x) for x in cols}) == 1:
            m = len(cols[0])
            rows = [[cols[ci][ri] for ci in range(len(h))] for ri in range(m)]
            return {"h": [clean(x) for x in h], "r": [[clean(c) for c in row] for row in rows]}
    # B: transposed table - each "row" is one cell containing a column's values
    lists = [_lit(row[0]) for row in r if isinstance(row, list) and len(row) == 1]
    if len(lists) == len(r) and lists and all(isinstance(x, list) for x in lists) \
            and len(lists) == len(h) and len({len(x) for x in lists}) == 1:
        m = len(lists[0])
        rows = [[lists[ci][ri] for ci in range(len(h))] for ri in range(m)]
        return {"h": [clean(x) for x in h], "r": [[clean(c) for c in row] for row in rows]}
    return None


def tables(passage):
    out = []
    for t in passage.get("tbl") or []:
        n = norm_table(t)
        if n:
            out.append(n)
    return out


def table_label(passage, idx=0):
    return "Table %d" % (idx + 1)


# ---------------------------------------------------------------- rationale
def split_trap(x):
    m = re.search(r"\bTrap:\s*(.*)$", x, re.I | re.S)
    if m:
        return x[:m.start()].strip(), m.group(1).strip()
    return x.strip(), ""


def letter_reasons(body):
    """Parse 'Correct: C) ... Why the others are wrong: A) ... B) ...' into {letter: text}."""
    out = {}
    for m in re.finditer(r"(?:\b([A-D]))\)\s*(.+?)(?=\s+\b[A-D]\)\s|\s*$)", body, re.S):
        out[m.group(1)] = m.group(2).strip(" .")
    if len(out) < 3:
        out = {}
    return out


def parse_rationale(q):
    body, trap = split_trap(q.get("x", ""))
    key_letter = LETTERS[q["a"]]
    body = re.sub(r"^Correct:\s*[A-D]\)\s*", "", body).strip()
    reasons = letter_reasons(body)
    if reasons and key_letter not in reasons:
        # the letter map did not include the key: keep only if it covers all
        reasons = {}
    return {"body": body, "trap": trap, "reasons": reasons}


# ---------------------------------------------------------------- numbers
def candidates(tbl, limit=400):
    """Every cell and every simple within-row / cross-row difference, percent, ratio."""
    out = []
    h, rows = tbl["h"], tbl["r"]
    for row in rows:
        label = row[0]
        vals = []
        for ci in range(1, len(row)):
            v = num(row[ci])
            if v is not None:
                vals.append((h[ci] if ci < len(h) else "column %d" % ci, v, ci))
        for name, v, _ in vals:
            out.append({"v": v, "kind": "cell", "desc": "%s row, %s = %s" % (label, name, fmt(v))})
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                n1, v1, _ = vals[i]
                n2, v2, _ = vals[j]
                out.append({"v": v2 - v1, "kind": "diff",
                            "desc": "%s row: %s %s minus %s %s" % (label, n2, fmt(v2), n1, fmt(v1))})
                if v1:
                    out.append({"v": (v2 - v1) / v1 * 100, "kind": "pct",
                                "desc": "%s row: (%s - %s) / %s x 100" % (label, fmt(v2), fmt(v1), fmt(v1))})
                if v2:
                    out.append({"v": (v2 - v1) / v2 * 100, "kind": "pct_end",
                                "desc": "%s row: (%s - %s) / %s x 100, dividing by the later value"
                                        % (label, fmt(v2), fmt(v1), fmt(v2))})
                if v1:
                    out.append({"v": v2 / v1, "kind": "ratio",
                                "desc": "%s row: %s / %s" % (label, fmt(v2), fmt(v1))})
    for ci in range(1, len(h)):
        vals = [(row[0], num(row[ci]) if ci < len(row) else None) for row in rows]
        vals = [(lbl, v) for lbl, v in vals if v is not None]
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                l1, v1 = vals[i]
                l2, v2 = vals[j]
                out.append({"v": v2 - v1, "kind": "rowdiff",
                            "desc": "%s minus %s in the %s column" % (l2, l1, h[ci])})
                if v1:
                    out.append({"v": (v2 - v1) / v1 * 100, "kind": "rowpct",
                                "desc": "(%s %s - %s %s) / %s x 100" % (h[ci], fmt(v2), h[ci], fmt(v1), fmt(v1))})
                if v1 and v2:
                    out.append({"v": (v2 - v1) / v2 * 100, "kind": "rowpct_end",
                                "desc": "(%s %s - %s %s) / %s x 100, dividing by %s"
                                        % (h[ci], fmt(v2), h[ci], fmt(v1), fmt(v2), fmt(v2))})
    return out[:limit]


def close(a, b):
    if a is None or b is None:
        return False
    return abs(a - b) <= max(0.05, abs(b) * 0.012)


def best_candidate(opts, cands, kinds=None):
    """Match an option's number to a table-derived value. Sign is flexible because
    a 'reduction of 10.7%' option is the same quantity as a change of -10.7%."""
    v = num(opts)
    if v is None:
        return None
    pool = [c for c in cands if not kinds or c["kind"] in kinds]
    hit = [c for c in pool if close(v, c["v"])]
    if not hit:
        hit = [c for c in pool if close(v, -c["v"])]
    if not hit:
        return None
    return min(hit, key=lambda c: (abs(abs(c["v"]) - abs(v)), 0 if c["kind"] == "cell" else 1))


def pct_text(opts):
    return "%" in str(opts)


# ---------------------------------------------------------------- text
STOP = set("""a an the of in on for to and or with from by as is are was were be been
being that this these those it its their they them than then which what when how why
following best describes most likely according table figure passage researchers study
group groups value values mean data show shows shown statement statements among between
each per at into over under more less highest lowest greater smaller larger""".split())


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", clean(text).strip())
    return [p.strip() for p in parts if len(p.strip()) > 25]


def keywords(s):
    words = re.findall(r"[A-Za-z][A-Za-z\-]{3,}", clean(s))
    return {w.lower() for w in words if w.lower() not in STOP}


def best_sentence(passage_text, target, avoid=""):
    tg = keywords(target)
    if not tg:
        return ""
    best, score = "", 0.0
    for s in sentences(passage_text):
        sk = keywords(s)
        sc = len(tg & sk) / (len(tg) ** 0.5 + 1)
        if avoid and s == avoid:
            sc *= 0.5
        if sc > score:
            best, score = s, sc
    return best if score >= 0.55 else ""


def quote(s, n=190):
    s = clean(s).strip().rstrip(".")
    if len(s) > n:
        cut = s[:n].rsplit(" ", 1)[0]
        return cut + " ..."
    return s


def table_walk(tbl, limit=6):
    """Row-by-row values, for trend/average questions."""
    h, rows = tbl["h"], tbl["r"]
    bits = []
    for row in rows[:limit]:
        vals = [clean(c) for c in row]
        if len(vals) >= 2:
            bits.append("%s: %s" % (vals[0], ", ".join(vals[1:3])))
    return "; ".join(bits)
