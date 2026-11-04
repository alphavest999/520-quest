#!/usr/bin/env python3
"""Generate Phase 2 rich explanations (bp1261-bp1618, 200 BB passages, 1,000 Qs).

Writes play/json/phase2/batch_<lo>_<hi>.json, each entry single-line:
  {"bp1261_0": {"ox": ["...", "...", "...", "..."]}}
Each distractor explanation is built from, in order of trust: the question's own
lettered rationale, the table's cells and row arithmetic, the passage's sentences.
Negative stems ("NOT supported") are handled separately: the three non-key choices
are affirmed with source evidence instead of being denied.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bp_phase2 import (LETTERS, best_sentence, best_candidate, candidates, clean,
                       fmt, keywords, num, parse_rationale, quote, tables)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "json", "phase2")

DESIGN = [
    (r"baseline", "recording a baseline marks the starting point before treatment; it does not make the groups comparable"),
    (r"random", "random assignment is the step that spreads known and unknown confounders across the groups"),
    (r"double.?blind|single.?blind|blind", "blinding keeps participants or assessors from knowing the assignment; it does not balance confounders"),
    (r"mean change|standard deviation|\bSD\b|report", "reporting the mean, SD or n summarizes the outcome rather than controlling bias"),
    (r"dose|dosage|arm|additional group|third arm", "the dose arms are the treatments being compared; their number does not itself remove confounding"),
    (r"duration|weeks|month|long.?term|follow.?up", "the length of follow-up sets how long the effect is watched, not whether confounders are balanced"),
    (r"placebo", "the placebo arm supplies the comparison; the passage's stated protection against confounding is random assignment"),
    (r"control group|untreated", "an untreated control supplies the comparison baseline; comparability comes from random assignment"),
    (r"sample size|participants|enroll", "the number enrolled affects precision, not the balance of confounders between arms"),
    (r"t.?test|ANOVA|statistical", "the statistical test is applied after the data are collected; it cannot repair an imbalance created at assignment"),
]
SYN = {"reduction": "change", "decrease": "change", "fall": "change", "drop": "change",
       "increase": "change", "rise": "change"}
CUES = r"gives?|would|instead|divides?|uses?|because|if |means|so |rather|confus|mistaken|treats?|reports?"


def sci(v):
    if v is None:
        return "?"
    a = abs(v)
    if a and (a >= 1e5 or a < 1e-3):
        e, m = 0, a
        while m >= 10:
            m /= 10
            e += 1
        while m < 1:
            m *= 10
            e -= 1
        sup = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
        return "%s×10%s" % (("%.1f" % m).rstrip("0").rstrip("."), str(e).translate(sup))
    return fmt(v)


def cap(s):
    s = s.strip()
    return s[:1].upper() + s[1:] if s else s


def tidy(s):
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([,.;:])", r"\1", s)
    s = re.sub(r"\.\.+", ".", s)
    s = re.sub(r"^(Incorrect\.?\s*)+", "Incorrect. ", s)
    if not s.endswith("."):
        s += "."
    return s


def hshort(h):
    return re.sub(r"\s*\(.*?\)\s*", " ", clean(h)).strip()


def table_walk(tbl, limit=6):
    h = [hshort(x) for x in tbl["h"]]
    bits = []
    for row in tbl["r"][:limit]:
        pairs = []
        for i in range(1, min(len(row), len(h))):
            v = num(row[i])
            pairs.append("%s %s" % (h[i], sci(v) if v is not None else clean(row[i])))
        bits.append("%s (%s)" % (clean(row[0]), ", ".join(pairs)))
    return "; ".join(bits)


def row_for(tbl, opt, stem):
    if not re.search(r"which (group|treatment|dose|row|concentration|time|day|strain|condition|"
                     r"reaction)|(lowest|highest|greatest|least|smallest|largest)", stem, re.I):
        return None
    o = clean(opt).lower().strip()
    best, score = None, 0.0
    for row in tbl["r"]:
        lab = clean(row[0]).lower()
        a, b = set(re.findall(r"[a-z0-9]+", lab)), set(re.findall(r"[a-z0-9]+", o))
        if not a or not b:
            continue
        s = len(a & b) / len(a | b)
        if lab == o:
            s = 2.0
        if s > score:
            best, score = row, s
    return best if score >= 0.55 else None


def target_col(tbl, stem):
    words = set(re.findall(r"[a-z]+", stem.lower()))
    words |= {SYN[w] for w in list(words) if w in SYN}
    words -= {"mean", "the", "of", "in", "which", "value", "values"}
    best, score = None, 0.0
    for ci, h in enumerate(tbl["h"][1:], 1):
        hw = set(re.findall(r"[a-z]+", clean(h).lower())) - {"mmhg", "mg", "dl", "ml", "sd"}
        s = len(words & hw) / max(1, len(hw))
        if s > score:
            best, score = ci, s
    return best if score >= 0.34 else None


def design_reason(opt, key_opt, stem):
    s = (stem + " " + key_opt).lower()
    if not re.search(r"confound|valid|bias|design|control|attribute|cause|best controls", s):
        return ""
    for pat, reason in DESIGN:
        if re.search(pat, opt, re.I):
            return reason
    return ""


def pct_parts(cand):
    d = cand["desc"]
    label = d.split(" row:")[0] if " row:" in d else ""
    m = re.search(r"\(([-\d.]+) - ([-\d.]+)\) / ([-\d.]+)", d)
    if m:
        a, b, c = (float(m.group(i)) for i in (1, 2, 3))
        return label, "(%s - %s) / %s × 100 = %s%%" % (fmt(a), fmt(b), fmt(c), fmt(abs(cand["v"])))
    return label, "%s = %s%%" % (d, fmt(abs(cand["v"])))


def numeric_hint(body, v):
    """A clause from the rationale that shows how this wrong number arises."""
    toks = {fmt(v), fmt(abs(v))}
    if sci(v) not in toks:
        toks.add(sci(v))
    body = re.sub(r"Why the others are wrong:\s*", "", body)
    clauses = re.split(r"(?<=[.;])\s+", body)
    for c in clauses:
        if not any(t in c for t in toks):
            continue
        if re.search(r"answer is|the answer|^Correct", c.strip(), re.I):
            continue
        if "=" in c:
            left = c.split("=")[0]
            if any(t in left for t in toks):
                continue  # the number is an input, not the result
        if re.search(CUES, c, re.I):
            c = re.sub(r"^[A-D]\)\s*", "", c.strip())
            c = re.sub(r"^(why the others are wrong:?\s*)", "", c, flags=re.I)
            c = re.sub(r"^[A-D]\)\s*", "", c)
            return c.rstrip(" .;")
    return ""


def evidence(opt, ptext, tbl, stem):
    """Source support for a statement (used when the stem asks for the FALSE one)."""
    sent = best_sentence(ptext, opt)
    if sent and (keywords(opt) & keywords(sent)):
        return 'this statement is supported by the passage: "%s"' % quote(sent)
    if tbl and re.search(r"which group|treatment|highest|lowest|greater|more|less", stem, re.I):
        return "this statement is consistent with the table (%s)" % table_walk(tbl, 4)
    k = keywords(opt)
    for s in re.split(r"(?<=\.)\s+", ptext):
        if len(k & keywords(s)) >= 2:
            return 'the passage states "%s", which supports this statement' % quote(s, 150)
    return ""


def key_explanation(q, passage, tbl, cands, modes):
    rat = parse_rationale(q)
    body = re.split(r"\s*Why the others are wrong:", rat["body"])[0].strip()
    body = re.sub(r"^(the table shows|the passage states|the data show|according to table 1,?)\s+", "",
                  body, flags=re.I)
    body = re.sub(r"^Correct:?\s*", "", body).strip()
    body = re.sub(r"^[A-D]\)\s*", "", body).strip().rstrip(".")
    keyopt = clean(q["o"][q["a"]][0])
    keyval = num(keyopt)
    keycand = best_candidate(keyopt, cands) if keyval is not None else None
    if keyval is not None and cands:
        want = ["pct", "pct_end", "rowpct", "rowpct_end"] if modes["pct"] else (
            ["diff", "rowdiff"] if modes["diff"] else None)
        c2 = best_candidate(keyopt, cands, want) if want else None
        if c2:
            keycand = c2
    parts = [cap(body) + "." if body else ""]
    if keycand and keycand["kind"] != "cell" and not re.search(r"=|/|×|x 100", body):
        if keycand["kind"].startswith(("pct", "rowpct")):
            lab, work = pct_parts(keycand)
            parts.append("%s: %s." % (lab, work))
        else:
            parts.append("%s: %s = %s." % (keycand["desc"].split(" row:")[0],
                                           keycand["desc"].split("row: ")[-1], sci(keycand["v"])))
    if tbl and modes["rank"]:
        parts.append("Row by row: %s." % table_walk(tbl))
    return tidy("Correct. " + " ".join(p for p in parts if p)), rat, keycand, keyval


def wrong_numeric(opt, tbl, cands, keycand, modes):
    v = num(opt)
    wc = best_candidate(opt, cands)
    if wc and keycand and abs(abs(wc["v"]) - abs(keycand["v"])) < 1e-9:
        wc = None
    if wc and wc["kind"].startswith(("pct", "rowpct")):
        lab, work = pct_parts(wc)
        if wc["kind"].endswith("_end"):
            return ("%s divides by the later value; the starting value is the correct denominator, "
                    "which gives %s" % (work.split(" = ")[0] + " × 100", sci(abs(keycand["v"]))
                                        if keycand else "the key value"))
        return "%s, so this measures the change against a different baseline (%s)" % (work, lab or "another row")
    if wc and wc["kind"] == "cell":
        return "%s is the table's own entry for %s, not the value the question asks for" % (sci(v), wc["desc"])
    if wc and wc["kind"] in ("diff", "rowdiff"):
        return "%s is %s = %s, a difference rather than the quantity asked for" % (sci(v), wc["desc"], sci(abs(wc["v"])))
    if wc and wc["kind"] == "ratio":
        return "%s is %s = %s, a ratio rather than the requested value" % (sci(v), wc["desc"], sci(abs(wc["v"])))
    nearest, nd = None, None
    for row in tbl["r"] if tbl else []:
        for ci in range(1, len(row)):
            x = num(row[ci])
            if x is None:
                continue
            d = abs(x - v)
            if nd is None or d < nd:
                nearest, nd = (clean(row[0]), clean(tbl["h"][ci] if ci < len(tbl["h"]) else ""), x), d
    if nearest and nd is not None and nd <= max(0.5, abs(v) * 0.35):
        return "%s is closest to the %s entry in the %s column (%s), not the value asked for" % (
            sci(v), nearest[0], hshort(nearest[1]), sci(nearest[2]))
    walk = table_walk(tbl, 4) if tbl else ""
    if walk:
        return "%s is not produced by any cell or row comparison in the table, which reads %s" % (sci(v), walk)
    return "%s is not a value the passage reports" % sci(v)


def wrong_concept(q, j, opt, keyopt, rat, modes, tbl, ptext, stem):
    r = rat["reasons"].get(LETTERS[j])
    if r:
        return tidy(re.sub(r"^(wrong|incorrect|correct)[:.]?\s*", "", r, flags=re.I))
    if modes["notq"]:
        ev = evidence(opt, ptext, tbl, stem)
        if ev:
            return tidy(ev + "; the question asks for the statement that is not supported")
    dr = design_reason(opt, keyopt, stem)
    if dr:
        return tidy(dr)
    row = row_for(tbl, opt, stem) if tbl else None
    if row is not None:
        keyrow = row_for(tbl, keyopt, stem)
        ci = target_col(tbl, stem) if tbl else None
        if keyrow is not None and ci:
            kv = num(keyrow[ci]) if ci < len(keyrow) else None
            ov = num(row[ci]) if ci < len(row) else None
            if kv is not None and ov is not None:
                return tidy("%s reads %s = %s in the %s column, while %s reads %s, so %s does not have the "
                            "extreme value asked for" % (clean(row[0]), hshort(tbl["h"][ci]), sci(ov),
                                                         hshort(tbl["h"][ci]), clean(keyrow[0]), sci(kv),
                                                         clean(row[0])))
    sent = best_sentence(ptext, opt)
    keysent = best_sentence(ptext, keyopt)
    if sent and (keywords(opt) & keywords(sent)):
        return tidy('the passage says "%s", which does not support %s'
                    % (quote(sent), clean(opt).lower().rstrip(".")))
    if keysent:
        return tidy('no statement in the passage supports %s; the passage establishes "%s", which is what '
                    'makes %s the answer' % (clean(opt).lower().rstrip("."), quote(keysent),
                                             clean(keyopt).lower().rstrip(".")))
    return tidy("the passage's own account does not support %s" % clean(opt).lower().rstrip("."))


def compose(q, passage):
    opts = [clean(o[0]) for o in q["o"]]
    key = q["a"]
    rat = parse_rationale(q)
    tbls = tables(passage)
    tbl = tbls[0] if tbls else None
    cands = candidates(tbl) if tbl else []
    stem = clean(q["q"])
    s = stem.lower()
    modes = {"pct": ("%" in stem) or ("percent" in s),
             "rank": bool(re.search(r"lowest|highest|greatest|largest|smallest|least|pattern|trend|"
                                    r"varies|rank|order|most accurate", s)),
             "diff": bool(re.search(r"difference|change|reduction|increase|decrease|greater|lower|higher", s)),
             "notq": bool(re.search(r"not supported|except|incorrect|false|not true|least likely", s))}
    ptext = " ".join(clean(t) for t in passage["text"])
    ke, rat, keycand, keyval = key_explanation(q, passage, tbl, cands, modes)
    ox, flags = [], []
    for j, opt in enumerate(opts):
        if j == key:
            ox.append(ke)
            continue
        v = num(opt)
        txt = ""
        if not modes["notq"] and v is not None:
            txt = numeric_hint(rat["body"], v)
        if not txt and v is not None and cands:
            txt = wrong_numeric(opt, tbl, cands, keycand, modes)
        if not txt and v is not None:
            txt = "%s is not a value the passage reports; it gives %s" % (sci(v), quote(ptext.split(". ")[0], 120))
        if not txt:
            txt = wrong_concept(q, j, opt, opts[key], rat, modes, tbl, ptext, stem)
        ox.append(tidy("Incorrect. " + cap(txt)))
    if re.search(r"closest|illustrative|rounded for|using the provided options", rat["body"], re.I):
        flags.append("hedged_key")
    if any(re.search(r"no statement in the passage supports|own account does not support|not produced by any "
                     r"cell", x) for x in ox):
        flags.append("generic")
    if any(re.search(r"\bln\b|\blog\b", x) for x in ox):
        flags.append("log")
    return ox, {"table": bool(tbl), "flags": flags}


def main():
    dry = "--dry" in sys.argv
    lo = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 0
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 0
    data = json.load(open(os.path.join(ROOT, "bank", "BP.json"), encoding="utf-8"))
    sel = [p for p in data["passages"] if p.get("s") == "BB" and 1261 <= int(p["id"][2:]) <= 1618]
    sel.sort(key=lambda p: int(p["id"][2:]))
    flat = [(p, i, q) for p in sel for i, q in enumerate(p["qs"])]
    if n:
        flat = flat[lo:lo + n]
    os.makedirs(OUT, exist_ok=True)
    entries, meta, order = {}, {}, []
    stats = {"entries": 0, "no_table": 0, "generic": 0, "hedged": 0, "log": 0}
    for p, i, q in flat:
        ox, m = compose(q, p)
        k = "%s_%d" % (p["id"], i)
        entries[k] = {"ox": ox}
        meta[k] = m
        order.append((k, p))
        stats["entries"] += 1
        stats["no_table"] += 0 if m["table"] else 1
        for f in ("generic", "hedged_key", "log"):
            stats["hedged" if f == "hedged_key" else f] += 1 if f in m["flags"] else 0
    if dry:
        for k, _ in order:
            print(k)
            for x in entries[k]["ox"]:
                print("   -", x)
            if meta[k]["flags"]:
                print("   flags:", meta[k]["flags"])
        print("\nstats", stats)
        return
    file_no = 0
    for start in range(0, len(order), 15):
        chunk = order[start:start + 15]
        file_no += 1
        lo_p = int(chunk[0][1]["id"][2:])
        hi_p = int(chunk[-1][1]["id"][2:])
        with open(os.path.join(OUT, "batch_%03d_%03d.json" % (lo_p, hi_p)), "w", encoding="utf-8") as f:
            f.write(json.dumps({k: entries[k] for k, _ in chunk}, ensure_ascii=False, separators=(",", ":")))
    json.dump(meta, open(os.path.join(OUT, "_meta.json"), "w"), ensure_ascii=False)
    print("wrote", file_no, "batch files;", stats)


if __name__ == "__main__":
    main()
