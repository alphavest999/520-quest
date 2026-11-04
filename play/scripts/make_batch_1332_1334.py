#!/usr/bin/env python3
"""Phase 2 batch 16: bp1332, bp1333, bp1334 (15 questions), single-line.

bp1334 needs ln Keq to answer its ΔG°' question and the passage never supplies it,
so one sentence is added to the passage giving the three natural logs (same minimal
repair used for bp1294). Nothing else in the passage changes.
"""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BP = os.path.join(ROOT, "bank", "BP.json")
REC = os.path.join(ROOT, "json", "phase2", "repairs_pending.json")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1332_1334.json")

ANCHOR = "The investigators used R = 8.314 J/(mol\u00b7K) and expected values of \u0394G\u00b0\u2032 to be consistent with literature compilations."
ADDED = ANCHOR + " They also tabulated the natural logarithms of the three equilibrium constants: ln 652 = 6.48, ln 1.93 = 0.657 and ln 0.0545 = -2.91."


def nums(obj):
    return sorted(re.findall(r"\d+(?:\.\d+)?", json.dumps(obj, ensure_ascii=False)))


def repair_bp1334():
    data = json.load(open(BP, encoding="utf-8"))
    by = {p["id"]: p for p in data["passages"]}
    p = by["bp1334"]
    before = list(p["text"])
    if any("ln 1.93 = 0.657" in t for t in before):
        print("bp1334 passage already supplies ln values; no new record")
        return
    hit = [i for i, t in enumerate(before) if ANCHOR in t]
    assert len(hit) == 1, hit
    i = hit[0]
    after = list(before)
    after[i] = before[i].replace(ANCHOR, ADDED)
    # the repair may only append the logarithm sentence: every other passage string is
    # untouched, and the edited one is the original with the sentence appended
    assert after[i] == before[i].replace(ANCHOR, ADDED)
    assert all(after[j] == before[j] for j in range(len(before)) if j != i)
    # every number the sentence introduces must be either a natural log or a Keq value
    # already in Table 1, so no new quantity enters the passage
    table_nums = {n for t in p.get("tbl") or [] for n in nums(t)}
    new_nums = set(nums(after)) - set(nums(before))
    assert new_nums <= {"6.48", "0.657", "2.91"} | table_nums, (new_nums, table_nums)
    p["text"] = after
    rec = json.load(open(REC, encoding="utf-8")) if os.path.exists(REC) else {}
    rec.setdefault("bp1334", []).append({
        "field": "text",
        "why": ("the \u0394G\u00b0\u2032 question (Keq = 1.93, 310 K) needs ln Keq, which the passage "
                "never supplied; one sentence adds the three natural logs so the answer is read, "
                "not computed on a calculator"),
        "before": before,
        "after": after,
    })
    with open(BP, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    json.dump(rec, open(REC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("bp1334 passage repaired; added sentence only, digits preserved")


E = {
 "bp1332_0": {"ox": [
  "Incorrect. 26.7 \u00b5mol/min is the control column at [S] = 200 \u00b5M, the uninhibited rate rather than the inhibitor value.",
  "Correct. The inhibitor column of Table 1 at [S] = 200 \u00b5M reads 11.4 \u00b5mol/min, against 26.7 in the control column at the same substrate level.",
  "Incorrect. 6.7 \u00b5mol/min is the inhibitor column one row above, at [S] = 100 \u00b5M.",
  "Incorrect. 17.8 \u00b5mol/min is the inhibitor column at [S] = 400 \u00b5M, a higher substrate level than 200 \u00b5M."]},
 "bp1332_1": {"ox": [
  "Incorrect. Running the reaction for 60 minutes changes how far substrate is consumed, not whether high substrate can outcompete the inhibitor, and the passage's velocities come from the first 60 seconds.",
  "Correct. A competitive inhibitor raises Km,app but leaves Vmax intact, so saturating [S] restores the uninhibited plateau; noncompetitive inhibition lowers the plateau at every [S], which is the difference Table 1 lets the experiment separate.",
  "Incorrect. Varying enzyme concentration at one [S] tests whether velocity scales with enzyme, not where the inhibitor binds; Table 1 varies substrate, which is the informative axis here.",
  "Incorrect. A lower temperature slows catalysis in both columns and cannot show whether substrate competes with the inhibitor."]},
 "bp1332_2": {"ox": [
  "Incorrect. 480 \u00b5M is 120 x 4, multiplying the inhibitor concentration by the excess factor instead of dividing by it.",
  "Incorrect. 600 \u00b5M is 120 x 5, applying the whole Km,app/Km ratio to [I] rather than the excess above 1.",
  "Incorrect. 24 \u00b5M is 120/5, setting [I]/Ki equal to Km,app/Km and dropping the 1 in Km,app = Km(1 + [I]/Ki).",
  "Correct. Km,app/Km = 5 means 1 + [I]/Ki = 5, so [I]/Ki = 4 and Ki = 120/4 = 30 \u00b5M; Table 1 fits that, with the inhibited column still climbing (24.6 at 800 \u00b5M) toward the control plateau (35.6)."]},
 "bp1332_3": {"ox": [
  "Correct. The inhibitor column rises to 24.6 \u00b5mol/min at 800 \u00b5M while control reaches 35.6, so at saturating substrate the inhibited rate keeps approaching the same plateau rather than flattening below it; a genuine Vmax drop is what competitive inhibition forbids.",
  "Incorrect. This is consistent: a competitive inhibitor binds the free enzyme, which is why the inhibited/control ratio climbs from 1.9/8 = 0.24 at 25 \u00b5M to 24.6/35.6 = 0.69 at 800 \u00b5M.",
  "Incorrect. This is consistent: the inhibited column reaches half its plateau at a higher [S], reading 6.7 at 100 \u00b5M where control already reads 20.",
  "Incorrect. This is consistent: 1.9/8 = 0.24 at 25 \u00b5M against 24.6/35.6 = 0.69 at 800 \u00b5M, so inhibition weakens as substrate rises."]},
 "bp1332_4": {"ox": [
  "Incorrect. Competitive inhibitors bind the free enzyme in preference to the enzyme-substrate complex, as the rising inhibited/control ratio in Table 1 shows.",
  "Correct. Occupying the same site as oxaloacetate is what makes a structural analog competitive, and Table 1's pattern, with inhibition easing from 1.9/8 = 0.24 of control to 24.6/35.6 = 0.69, is reversible competition for that site.",
  "Incorrect. Lowering turnover at saturating substrate is noncompetitive behaviour and would leave the inhibited column below control's 35.6 at every high-[S] row.",
  "Incorrect. Covalent binding is not required for competition; the inhibited column of Table 1 rises with [S], which shows reversible displacement rather than inactivation."]},
 "bp1333_0": {"ox": [
  "Incorrect. The ratio is 6/24 = 10/40 = 15/60 = 20/80 = 24/96 = 26.7/106.7 = 0.25 at every row, so it does not rise.",
  "Incorrect. The ratio stays at 0.25 rather than falling; a falling ratio would mean substrate overcomes the compound, which Table 1 does not show.",
  "Incorrect. At the lowest [S] of 12.5 \u00b5M the inhibited value is 6 against 24 for control, so it is lower, not higher.",
  "Correct. Dividing the two columns gives 6/24 = 10/40 = 15/60 = 20/80 = 24/96 = 26.7/106.7 = 0.25, a constant quarter at every substrate level."]},
 "bp1333_1": {"ox": [
  "Incorrect. Potency falling as [S] rises is the signature of competitive inhibition, the opposite of the constant 0.25 inhibited/control ratio in Table 1.",
  "Incorrect. Km rising with compound concentration describes competitive inhibition and would confirm competition rather than exclude it, which is not the pattern in Table 1's flat 0.25 ratio.",
  "Correct. If raising [S] to 400 \u00b5M cannot lift the inhibited rate (26.7) toward control (106.7), the compound is not simply competing for the substrate site, which is the point of the test.",
  "Incorrect. The passage already states the compound has no structural resemblance to oxaloacetate, so matching the substrate is not available as a test."]},
 "bp1333_2": {"ox": [
  "Incorrect. 24 \u00b5mol/min is the inhibited velocity at 200 \u00b5M, a single point rather than the plateau the fit approaches.",
  "Incorrect. 480 \u00b5mol/min multiplies the uninhibited Vmax by 4 instead of dividing by the factor.",
  "Correct. The inhibited column is one quarter of control at every row (6/24 = 26.7/106.7 = 0.25), so Vmax,app = 120/4 = 30 \u00b5mol/min.",
  "Incorrect. 116 \u00b5mol/min subtracts 4 from 120; the compound cuts the rate to a quarter, not by 4 units."]},
 "bp1333_3": {"ox": [
  "Incorrect. This is true: equal affinity for free enzyme and enzyme-substrate complex is exactly the pattern Table 1 shows, a constant 0.25 ratio across all six rows.",
  "Correct. Pure noncompetitive inhibition leaves Km unchanged, which is why Table 1's ratio is a constant 0.25; a rising Km would need competition with substrate, and the passage places the compound in a distant hydrophobic pocket.",
  "Incorrect. This is true: a shared x-intercept at -1/Km follows directly from an unchanged Km.",
  "Incorrect. This is true: the inhibited column plateaus near a quarter of control (26.7 against 106.7), an apparent Vmax of 30 against 120."]},
 "bp1333_4": {"ox": [
  "Incorrect. Covalent activation is a different mechanism and would not produce the constant 0.25 ratio across every [S] in Table 1.",
  "Correct. The docking result places the compound in a hydrophobic pocket far from the catalytic residues, and binding at such a regulatory site that lowers capacity reproduces Table 1's noncompetitive pattern.",
  "Incorrect. Substrate-analog competition is ruled out: the passage states the compound has no structural resemblance to oxaloacetate.",
  "Incorrect. Transition-state mimicry at the active site would be overcome by high [S], yet the 400 \u00b5M row still reads 26.7 against 106.7 for control."]},
 "bp1334_0": {"ox": [
  "Incorrect. Table 1 gives Q/Keq of 0.5, 0.01 and 100, so one reaction is within a factor of two of equilibrium.",
  "Incorrect. Reaction C has Q = 5.45 against Keq = 0.0545, so Q/Keq = 100, the furthest from equilibrium of the three.",
  "Correct. Reaction A has Q = 326 against Keq = 652, so Q/Keq = 0.5, closer to 1 than reaction B (0.0193/1.93 = 0.01) or reaction C (5.45/0.0545 = 100).",
  "Incorrect. Reaction B has Q = 0.0193 against Keq = 1.93, so Q/Keq = 0.01, fifty-fold further from 1 than reaction A's 0.5."]},
 "bp1334_1": {"ox": [
  "Incorrect. A single time-point ratio cannot distinguish equilibrium from a slow approach, and the passage says each vessel was allowed to reach equilibrium before HPLC quantification.",
  "Incorrect. Cooling below the passage's 37 C slows the approach and would leave the ratio further from equilibrium, not confirm it.",
  "Correct. A true equilibrium ratio is the same whether the vessel starts from reactants or from products, so matching ratios from both directions is what confirms Table 1's Keq.",
  "Incorrect. Doubling enzyme speeds the approach but cannot change the final ratio, so it tests catalysis rather than the Keq values in Table 1."]},
 "bp1334_2": {"ox": [
  "Incorrect. -3.9 kJ/mol does not follow from the 1.93 cell; with the supplied ln 1.93 = 0.657, 2.577 x 0.657 is 1.7, not 3.9.",
  "Incorrect. 1.7 kJ/mol drops the minus sign, but \u0394G\u00b0\u2032 = -RT ln Keq is negative whenever Keq exceeds 1, as 1.93 does.",
  "Incorrect. -0.7 kJ/mol comes from the base-10 logarithm (0.285) instead of the natural log: 2.577 x 0.285 = 0.73, whereas the supplied ln 1.93 of 0.657 gives 1.7.",
  "Correct. \u0394G\u00b0\u2032 = -RT ln Keq = -(0.008314 x 310) x 0.657 = -2.577 x 0.657 = -1.7 kJ/mol, using the ln 1.93 the passage now supplies."]},
 "bp1334_3": {"ox": [
  "Incorrect. This is correct: with \u0394G = \u0394G\u00b0\u2032 + RT ln Q, a small enough Q makes the second term negative enough to drive a positive \u0394G\u00b0\u2032 reaction forward, as reaction A's Q of 326 against Keq 652 illustrates.",
  "Incorrect. This is correct: Keq fixes \u0394G\u00b0\u2032 but says nothing about activation energy, so the 1.93 and 652 values in Table 1 cannot set a rate.",
  "Incorrect. This is correct: the actual \u0394G adds RT ln Q to \u0394G\u00b0\u2032, so Q matters alongside it, which is why the passage compares Q with Keq row by row.",
  "Correct. A negative \u0394G\u00b0\u2032 fixes direction, not speed: reaction A with Keq = 652 is favourable yet still needed its enzyme to run at a measurable rate, which makes 'always proceeds rapidly' the incorrect statement."]},
 "bp1334_4": {"ox": [
  "Incorrect. Removing catalyst cannot help: enzymes change rate, not \u0394G\u00b0\u2032, and the 652 and 1.93 values in Table 1 would be unaffected.",
  "Correct. Coupling to a strongly exergonic step such as ATP hydrolysis (about -30.5 kJ/mol) makes the summed \u0394G negative even when the coupled step has a positive \u0394G\u00b0\u2032, and reaction A of Table 1 is such an ATP-driven step with Keq = 652.",
  "Incorrect. Raising temperature shifts \u0394G\u00b0\u2032 only slightly and cannot make Keq equal 1 for a reaction whose Keq is 1.93 or 652.",
  "Incorrect. More enzyme speeds the reaction but leaves \u0394G\u00b0\u2032 untouched, since catalysis cannot change the 1.93 or 652 values in Table 1."]},
}


def main():
    repair_bp1334()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(E, ensure_ascii=False, separators=(",", ":")))
    print("wrote", OUT, len(E), "entries")


if __name__ == "__main__":
    main()
