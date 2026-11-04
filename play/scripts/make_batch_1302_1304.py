#!/usr/bin/env python3
"""Hand-authored Phase 2 batch 9: bp1302, bp1303, bp1304 (15 questions), single-line."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1302_1304.json")

E = {
 "bp1302_0": {"ox": [
  "Incorrect. Reaction A has Q 6.52 against Keq 652, a ratio of 0.01, which is two orders of magnitude from equilibrium.",
  "Correct. Reaction B has Q 3.86 against Keq 1.93, a ratio of 2.0, the closest to 1 of the three (reaction A is 0.01 and reaction C is 100).",
  "Incorrect. Reaction C has Q 5.45 against Keq 0.0545, a ratio of 100, the furthest from equilibrium in the table.",
  "Incorrect. Reaction B is within a factor of two of equilibrium, so not all three are far from it; the table's ratios are 0.01, 2.0 and 100."]},
 "bp1302_1": {"ox": [
  "Incorrect. More enzyme speeds the approach to the table's Keq but does not show the endpoint was reached, and it leaves Keq unchanged.",
  "Correct. Reaching the same products-to-reactants ratio from both the reactant and product sides shows the ratio is path-independent, which is what the table's Keq assumes.",
  "Incorrect. A single product measurement at one time point cannot show that the ratio has stopped changing toward the table's Keq value.",
  "Incorrect. Lowering the temperature changes the table's Keq itself rather than demonstrating that equilibrium was reached."]},
 "bp1302_2": {"ox": [
  "Incorrect. -38.5 kJ/mol matches no RT times log combination here: 2.577 × 6.48 = 16.7 and 2.577 × 2.82 = 7.3.",
  "Incorrect. +16.7 kJ/mol reverses the sign; with Keq 652 above 1 the standard free-energy change must be negative.",
  "Incorrect. -7.3 kJ/mol comes from a base-10 logarithm: 2.577 × 2.82 = 7.3, which is the wrong logarithm.",
  "Correct. The passage gives ln 652 = 6.48 and R × T = 8.314 × 310 / 1000 = 2.577 kJ/mol, so ΔG°′ = -(2.577 × 6.48) = -16.7 kJ/mol."]},
 "bp1302_3": {"ox": [
  "Correct. A negative ΔG°′ states the direction of change, not the speed; the table's Keq says nothing about how fast equilibrium is reached, which depends on activation energy.",
  "Incorrect. This is true: ΔG°′ is tied to the table's Keq, while the rate depends on activation energy and catalysis.",
  "Incorrect. This is true: with a small enough Q the RT ln Q term can outweigh a positive ΔG°′, as the table's Q values show.",
  "Incorrect. This is true: actual ΔG = ΔG°′ + RT ln Q, so the table's Q is part of the value."]},
 "bp1302_4": {"ox": [
  "Correct. Coupling to a strongly exergonic step such as ATP hydrolysis (about -30.5 kJ/mol) makes the overall ΔG negative, which is how cells drive unfavourable reactions.",
  "Incorrect. Removing the catalyst slows the reaction and does not change ΔG°′ or the table's Keq.",
  "Incorrect. Enzymes lower activation energy and speed the reaction, but they leave ΔG°′ unchanged; adding more enzyme cannot make an unfavourable step in the table favourable.",
  "Incorrect. Raising the temperature shifts Keq only slightly and does not set it to 1; the table's Keq values are fixed by the reactions."]},
 "bp1303_0": {"ox": [
  "Incorrect. The NutriBoost row reads 52.8 kcal/day at week 12 against 46.1 kcal/day for placebo, so its RMR is higher, not lower.",
  "Incorrect. The passage states the week-12 difference had p < 0.01, so it was statistically significant.",
  "Correct. Week-12 RMR is 52.8 ± 3.4 kcal/day with NutriBoost and 46.1 ± 3.0 kcal/day with placebo, and the passage reports p < 0.01 for the difference.",
  "Incorrect. The two means differ by 6.7 kcal/day (52.8 versus 46.1), so they are not identical."]},
 "bp1303_1": {"ox": [
  "Incorrect. A cross-sectional study measures one time point; the passage measures RMR weekly over 12 weeks after random assignment.",
  "Correct. The passage describes random assignment to NutriBoost or placebo, a placebo control, and weekly RMR measurements over 12 weeks, which is a randomized controlled trial with repeated measures.",
  "Incorrect. A case-control study groups animals by an outcome that already occurred; the passage assigns the diet first and follows RMR for 12 weeks.",
  "Incorrect. An uncontrolled cohort has no comparison arm; the passage randomizes to NutriBoost or placebo."]},
 "bp1303_2": {"ox": [
  "Correct. Baseline RMR is 45.2 kcal/day and week-12 RMR is 52.8 kcal/day, so the absolute increase is 52.8 - 45.2 = 7.6 kcal/day.",
  "Incorrect. 5.6 kcal/day would need a baseline of 47.2; the NutriBoost baseline is 45.2 kcal/day.",
  "Incorrect. 6.6 kcal/day is close to the week-12 between-group gap (52.8 - 46.1 = 6.7), not the within-group rise from baseline.",
  "Incorrect. 8.6 kcal/day would need a baseline of 44.2; the passage gives 45.2 kcal/day."]},
 "bp1303_3": {"ox": [
  "Incorrect. This is accurate: 52.8 - 45.2 = 7.6 kcal/day for the NutriBoost group.",
  "Incorrect. This is accurate: NutriBoost rats gained 0.8 kg against 1.2 kg for placebo, a smaller gain.",
  "Correct. The study used rats, so concluding causality between NutriBoost and weight loss in humans extends the table's findings beyond the species tested.",
  "Incorrect. This is accurate: the passage reports p < 0.01 for the week-12 RMR difference."]},
 "bp1303_4": {"ox": [
  "Correct. The comparison is between two independent groups of 30 rats each with a continuous outcome (week-12 RMR), which calls for an unpaired two-sample t-test.",
  "Incorrect. A paired t-test needs repeated measurements on the same units; the table's between-group comparison uses separate animals.",
  "Incorrect. A chi-square test compares categorical counts, not means of a continuous measure like the RMR values in the table.",
  "Incorrect. A log-rank test compares time-to-event curves, and the table reports RMR values rather than survival times."]},
 "bp1304_0": {"ox": [
  "Incorrect. The reference gene reads Ct 19 in both conditions, so the comparison is already normalized; ranking starting amounts needs no standard curve.",
  "Correct. Untreated cells reach threshold at Ct 26 for IL6 against Ct 28 in treated cells, with the reference at 19 in both, so untreated cells have more starting template.",
  "Incorrect. The Ct values differ by two cycles (26 versus 28), so the starting amounts are not equal.",
  "Incorrect. Treated cells have the higher Ct (28), which means less IL6 template, not more."]},
 "bp1304_1": {"ox": [
  "Correct. Without reverse transcriptase no cDNA is made, so any product must come from genomic DNA; a no-RT control therefore tests exactly the DNA contamination the passage's DNase step targets.",
  "Incorrect. A no-primer control tests primer-independent signal, not whether the product is DNA-derived; the passage's DNase step targets DNA.",
  "Incorrect. Doubling the template tests linearity and sensitivity, not whether the product is DNA-derived, and the passage holds efficiency near 100%.",
  "Incorrect. Raising the annealing temperature changes primer specificity, not the source of the template in Table 1."]},
 "bp1304_2": {"ox": [
  "Correct. ΔCt untreated = 26 - 19 = 7 and ΔCt treated = 28 - 19 = 9, so ΔΔCt = 9 - 7 = 2 and the fold change is 2 raised to -2, which is 0.25-fold.",
  "Incorrect. 4-fold is 2 raised to +2, which inverts the comparison and reports untreated relative to treated.",
  "Incorrect. 0.5-fold would need a one-cycle ΔΔCt; the table shows a two-cycle difference (26 versus 28).",
  "Incorrect. 2-fold would also need a one-cycle ΔΔCt, and the observed difference is two cycles."]},
 "bp1304_3": {"ox": [
  "Incorrect. This is true: the reference gene reads Ct 19 in both conditions, which is what normalizes for input RNA.",
  "Incorrect. This is true: at 100% efficiency the product doubles each cycle, so one Ct is a two-fold difference.",
  "Correct. A higher Ct means the threshold is crossed later, which indicates less starting template; the treated Ct of 28 therefore has less IL6, not more.",
  "Incorrect. This is true: the untreated sample reaches threshold at Ct 26 versus 28, so a lower Ct means more template."]},
 "bp1304_4": {"ox": [
  "Incorrect. tRNA anticodons act during translation, downstream of the transcriptional response the Table 1 Ct data reflect.",
  "Correct. Promoter and enhancer sequences upstream of the transcription start site carry transcription-factor binding sites, the region that controls the transcript levels in Table 1.",
  "Incorrect. Introns concern transcript processing; the Ct differences in Table 1 reflect transcription, not splicing.",
  "Incorrect. The poly-A tail is added during mRNA processing after transcription; Table 1 measures transcript abundance, not tail length."]},
}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(E, ensure_ascii=False, separators=(",", ":")))
    print("wrote", OUT, len(E), "entries")


if __name__ == "__main__":
    main()
