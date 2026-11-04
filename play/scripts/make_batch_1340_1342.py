#!/usr/bin/env python3
"""Phase 2 batch 18: bp1340, bp1341, bp1342 (15 questions), single-line.

bp1342 needs ln Keq for its ΔG°' question and, like bp1334, never supplies it, so one
sentence adds the three natural logs. Nothing else changes.
"""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BP = os.path.join(ROOT, "bank", "BP.json")
REC = os.path.join(ROOT, "json", "phase2", "repairs_pending.json")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1340_1342.json")

ANCHOR = "The investigators used R = 8.314 J/(mol\u00b7K) and expected values of \u0394G\u00b0\u2032 to be consistent with literature compilations."
ADDED = ANCHOR + " They also tabulated the natural logarithms of the three equilibrium constants: ln 652 = 6.48, ln 1.93 = 0.657 and ln 0.0545 = -2.91."


def nums(obj):
    return sorted(re.findall(r"\d+(?:\.\d+)?", json.dumps(obj, ensure_ascii=False)))


def repair_bp1342():
    data = json.load(open(BP, encoding="utf-8"))
    by = {p["id"]: p for p in data["passages"]}
    p = by["bp1342"]
    before = list(p["text"])
    if any("ln 652 = 6.48" in t for t in before):
        print("bp1342 passage already supplies ln values; no new record")
        return
    hit = [i for i, t in enumerate(before) if ANCHOR in t]
    assert len(hit) == 1, hit
    i = hit[0]
    after = list(before)
    after[i] = before[i].replace(ANCHOR, ADDED)
    assert after[i] == before[i].replace(ANCHOR, ADDED)
    assert all(after[j] == before[j] for j in range(len(before)) if j != i)
    table_nums = {n for t in p.get("tbl") or [] for n in nums(t)}
    new_nums = set(nums(after)) - set(nums(before))
    assert new_nums <= {"6.48", "0.657", "2.91"} | table_nums, (new_nums, table_nums)
    p["text"] = after
    rec = json.load(open(REC, encoding="utf-8")) if os.path.exists(REC) else {}
    rec.setdefault("bp1342", []).append({
        "field": "text",
        "why": ("the \u0394G\u00b0\u2032 question (Keq = 652, 310 K) needs ln Keq, which the passage "
                "never supplied; one sentence adds the three natural logs so the answer is read, "
                "not computed on a calculator"),
        "before": before,
        "after": after,
    })
    with open(BP, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    json.dump(rec, open(REC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("bp1342 passage repaired; added sentence only, digits preserved")


E = {
 "bp1340_0": {"ox": [
  "Correct. The 60 µM inhibitor column of Table 1 at [S] = 200 µM reads 34.3 µmol/min, against 80 in the no-inhibitor column at the same substrate level.",
  "Incorrect. 80 µmol/min is the no-inhibitor column at [S] = 200 µM, the uninhibited rate rather than the inhibited one.",
  "Incorrect. 53.3 µmol/min is the inhibitor column at [S] = 400 µM, one row below the row asked about.",
  "Incorrect. 20 µmol/min is the inhibitor column at [S] = 100 µM, a lower substrate level."]},
 "bp1340_1": {"ox": [
  "Incorrect. A 60-minute run changes how far substrate is consumed, not whether high substrate can outcompete the inhibitor, and the passage's velocities come from the first 60 seconds.",
  "Incorrect. A lower temperature slows both columns and cannot show whether substrate competes for the active site.",
  "Correct. A competitive inhibitor raises Km,app but leaves Vmax intact, so saturating [S] restores the uninhibited plateau; noncompetitive inhibition lowers it at every [S], and Table 1's rising inhibited/control ratio is the difference the experiment would separate.",
  "Incorrect. Varying enzyme concentration at one [S] tests whether velocity scales with enzyme, not where the inhibitor binds; Table 1 varies substrate, which is the informative axis here."]},
 "bp1340_2": {"ox": [
  "Correct. Control reaches half its plateau at 100 µM (60 against a 120 plateau) while the inhibited column reaches that same half-plateau near 500 µM, between 53.3 at 400 and 73.8 at 800, so Km,app/Km = 5 and Ki = 60/4 = 15 µM.",
  "Incorrect. 300 µM is 60 x 5, multiplying [I] by the ratio instead of dividing by the excess above 1.",
  "Incorrect. 12 µM is 60/5, using the whole Km,app/Km ratio and dropping the 1 in Km,app = Km(1 + [I]/Ki).",
  "Incorrect. 240 µM is 60 x 4, inverting the division: the excess factor 4 belongs in the denominator."]},
 "bp1340_3": {"ox": [
  "Incorrect. This is consistent: the inhibited/control ratio climbs from 5.7/24 = 0.24 at 25 µM to 73.8/106.7 = 0.69 at 800 µM, so inhibition weakens as substrate rises.",
  "Incorrect. This is consistent: a competitive inhibitor binds the free enzyme, which is why that ratio rises with [S] in Table 1.",
  "Incorrect. This is consistent: the inhibited column needs about 500 µM to reach half-plateau where control needs 100 µM, the raised Km that competition produces.",
  "Correct. At 800 µM the inhibited rate is 73.8 against 106.7 for control and still climbing toward the same plateau, so a lower Vmax at saturating [S] is exactly the behaviour competition excludes."]},
 "bp1340_4": {"ox": [
  "Incorrect. Covalent binding is not required; the inhibited column of Table 1 rises with [S] from 0.24 to 0.69 of control, which is reversible displacement rather than inactivation.",
  "Incorrect. Lowering turnover at saturating substrate is noncompetitive behaviour and would leave the inhibited column below 106.7 at every high-[S] row.",
  "Correct. Occupying the same site as pyruvate is what makes a structural analog competitive, and Table 1's ratio rising toward the control plateau is reversible competition for that site.",
  "Incorrect. Competitive inhibitors bind the free enzyme in preference to the enzyme-substrate complex, as the ratio rising from 0.24 at 25 µM to 0.69 at 800 µM shows."]},
 "bp1341_0": {"ox": [
  "Correct. The Hypotensol row of Table 1 reads 125 ± 8 mmHg at 8 weeks, the lowest mean in the table.",
  "Incorrect. 132 mmHg is the Hypotensol value at 4 weeks, one column before the 8-week reading.",
  "Incorrect. 144 mmHg is the placebo group at 8 weeks, not the Hypotensol group.",
  "Incorrect. 148 mmHg is the Hypotensol baseline, before any treatment effect."]},
 "bp1341_1": {"ox": [
  "Incorrect. Randomization balances the two groups of 60 but leaves participants and investigators aware of who received what, so it does not hide expectations.",
  "Correct. The passage describes the trial as double-blind, so neither participants nor investigators know the assignment and expectations cannot bias the reported SBP.",
  "Incorrect. A paired t-test compares each group's own baseline with its follow-up, as Table 1's 148 to 125 change shows; it conceals nothing.",
  "Incorrect. A 5-minute seated rest standardizes the measurement but does not mask which treatment the participant received."]},
 "bp1341_2": {"ox": [
  "Incorrect. 10% is near 16/148 = 10.8%, the reduction at 4 weeks rather than at 8 weeks.",
  "Correct. 148 - 125 = 23 mmHg, and 23/148 = 15.5%, the fall from baseline to week 8 in the Hypotensol row.",
  "Incorrect. 20% is near 30/148 = 20.3%, which would need a 30 mmHg fall; Table 1 shows 23 mmHg from 148 to 125.",
  "Incorrect. 25% would need a 37 mmHg fall, but the Hypotensol row falls only from 148 to 125."]},
 "bp1341_3": {"ox": [
  "Incorrect. The passage assigns paired t-tests to the within-group comparison, each group against its own baseline in Table 1.",
  "Correct. The passage states that independent t-tests were used between groups at each time point, which is the Hypotensol-versus-placebo comparison.",
  "Incorrect. A chi-square test handles counts of categories, and the outcome here is the continuous mean SBP in mmHg reported in Table 1.",
  "Incorrect. No correlation between two variables is described in the passage."]},
 "bp1341_4": {"ox": [
  "Incorrect. The placebo row reads 147 at baseline, 145 at 4 weeks and 144 at 8 weeks, so its mean fell rather than rose.",
  "Correct. 147 - 144 = 3 mmHg for placebo against 148 - 125 = 23 mmHg for Hypotensol, a comparison the table supports directly.",
  "Incorrect. At 4 weeks placebo fell 2 mmHg (147 to 145) while Hypotensol fell 16 mmHg (148 to 132).",
  "Incorrect. The placebo 8-week mean of 144 mmHg is higher, not lower, than the Hypotensol 8-week mean of 125 mmHg."]},
 "bp1342_0": {"ox": [
  "Correct. Reaction B has Q = 1.93 against Keq = 1.93, so Q/Keq = 1, while reaction A (6.52/652 = 0.01) and reaction C (5.45/0.0545 = 100) sit far from 1.",
  "Incorrect. Reaction C has Q = 5.45 against Keq = 0.0545, so Q/Keq = 100, the furthest of the three from equilibrium.",
  "Incorrect. Reaction A has Q = 6.52 against Keq = 652, so Q/Keq = 0.01, a hundred-fold below 1.",
  "Incorrect. Table 1 contains a reaction whose Q equals Keq (1.93 for both), so not all three are far from equilibrium."]},
 "bp1342_1": {"ox": [
  "Incorrect. Doubling enzyme speeds the approach but cannot change the final ratio, so it tests catalysis rather than the Keq values in Table 1.",
  "Correct. A true equilibrium ratio is the same whether the vessel starts from reactants or from products, so matching ratios from both directions confirms Table 1's Keq.",
  "Incorrect. A single time-point ratio cannot distinguish equilibrium from a slow approach, and the passage says each vessel was allowed to reach equilibrium before HPLC quantification.",
  "Incorrect. Cooling below the passage's 37 C slows the approach and would leave the ratio further from equilibrium."]},
 "bp1342_2": {"ox": [
  "Incorrect. 16.7 kJ/mol drops the minus sign, but \u0394G\u00b0\u2032 = -RT ln Keq is negative whenever Keq exceeds 1, as 652 does.",
  "Incorrect. -7.3 kJ/mol comes from the base-10 logarithm (2.814) instead of the natural log: 2.577 x 2.814 = 7.25, whereas the supplied ln 652 = 6.48 gives 16.7.",
  "Incorrect. -38.5 kJ/mol does not follow from the 652 cell: 2.577 x 6.48 is 16.7, not 38.5.",
  "Correct. \u0394G\u00b0\u2032 = -RT ln Keq = -(0.008314 x 310) x 6.48 = -2.577 x 6.48 = -16.7 kJ/mol, using the ln 652 the passage supplies."]},
 "bp1342_3": {"ox": [
  "Incorrect. This is correct: Keq fixes \u0394G\u00b0\u2032 but says nothing about activation energy, so the 652 and 1.93 values in Table 1 cannot set a rate.",
  "Correct. A negative \u0394G\u00b0\u2032 fixes direction, not speed: reaction A with Keq = 652 is favourable yet still needed its enzyme to run at a measurable rate, which makes 'always proceeds rapidly' the incorrect statement.",
  "Incorrect. This is correct: with \u0394G = \u0394G\u00b0\u2032 + RT ln Q, a small enough Q drives a positive \u0394G\u00b0\u2032 reaction forward, as reaction A's Q of 6.52 against Keq 652 illustrates.",
  "Incorrect. This is correct: the actual \u0394G adds RT ln Q to \u0394G\u00b0\u2032, which is why the passage compares Q with Keq row by row."]},
 "bp1342_4": {"ox": [
  "Correct. Coupling to a strongly exergonic step such as ATP hydrolysis (about -30.5 kJ/mol) makes the summed \u0394G negative even when the coupled step has a positive \u0394G\u00b0\u2032, and reaction A of Table 1 is such an ATP-driven step.",
  "Incorrect. Removing catalyst cannot help: enzymes change rate, not \u0394G\u00b0\u2032, and the 652 and 1.93 values in Table 1 would be unaffected.",
  "Incorrect. More enzyme speeds the reaction but leaves \u0394G\u00b0\u2032 untouched, since catalysis cannot change the 1.93 or 652 values in Table 1.",
  "Incorrect. Raising temperature shifts \u0394G\u00b0\u2032 only slightly and cannot make Keq equal 1 for a reaction whose Keq is 652 or 1.93."]},
}


def main():
    repair_bp1342()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(E, ensure_ascii=False, separators=(",", ":")))
    print("wrote", OUT, len(E), "entries")


if __name__ == "__main__":
    main()
