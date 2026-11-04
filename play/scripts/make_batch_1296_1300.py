#!/usr/bin/env python3
"""Hand-authored Phase 2 batch 8: bp1296, bp1299, bp1300 (15 questions), single-line."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1296_1300.json")

E = {
 "bp1296_0": {"ox": [
  "Correct. SOD2 Ct is 22 in treated cells and 25 in untreated cells, with the reference gene at 19 in both, so the treated sample reaches threshold three cycles earlier and has more starting template.",
  "Incorrect. The reference gene reads Ct 19 in both conditions, so the comparison is already normalized; ranking the starting amounts needs no standard curve.",
  "Incorrect. The untreated Ct of 25 is higher than the treated Ct of 22, which means less SOD2 template, not more.",
  "Incorrect. The two Ct values differ by three cycles (25 versus 22), so the starting amounts are not equal."]},
 "bp1296_1": {"ox": [
  "Correct. Without reverse transcriptase no cDNA is made, so any product must come from genomic DNA; a no-RT control therefore tests exactly the DNA contamination the passage's DNase step targets.",
  "Incorrect. A no-primer control tests primer-independent signal, not whether the signal comes from DNA; the passage's DNase step targets DNA.",
  "Incorrect. Doubling the template tests linearity and sensitivity, not whether the product is DNA-derived; the passage's DNase treatment is the step aimed at DNA.",
  "Incorrect. Raising the annealing temperature changes primer specificity, not the source of the template, and the passage holds amplification efficiency near 100%."]},
 "bp1296_2": {"ox": [
  "Correct. ΔCt untreated = 25 - 19 = 6 and ΔCt treated = 22 - 19 = 3, so ΔΔCt = 3 - 6 = -3 and the fold change is 2 raised to 3, which is 8-fold.",
  "Incorrect. 16-fold would need a 4-cycle ΔΔCt; the table shows a 3-cycle difference (25 versus 22).",
  "Incorrect. 0.125 is 2 raised to -3, which reverses the sign of ΔΔCt and reports a decrease instead of an increase.",
  "Incorrect. 3 is the difference in Ct cycles, not a fold change; each cycle doubles the product."]},
 "bp1296_3": {"ox": [
  "Incorrect. This is true: the reference gene reads Ct 19 in both conditions, which is what normalizes for input RNA.",
  "Incorrect. This is true: at 100% efficiency the product doubles each cycle, so one Ct is a two-fold difference.",
  "Incorrect. This is true: the treated sample reaches threshold at Ct 22 versus 25 untreated, so a lower Ct means more template.",
  "Correct. A higher Ct means the threshold is crossed later, which indicates less starting template; the untreated 25 therefore has less SOD2, not more."]},
 "bp1296_4": {"ox": [
  "Incorrect. tRNA anticodons act during translation, downstream of the transcriptional response the Table 1 Ct data reflect.",
  "Incorrect. Introns concern transcript processing; the Ct differences in Table 1 reflect transcription, not splicing.",
  "Incorrect. The poly-A tail is added during mRNA processing after transcription; Table 1 measures transcript abundance, not tail length.",
  "Correct. Promoter and enhancer sequences upstream of the transcription start site carry transcription-factor binding sites, the region that controls the transcript levels in Table 1."]},
 "bp1299_0": {"ox": [
  "Incorrect. The treatment mean falls at every time point, from 258 to 210, 180, 160 and 150 mg/dL.",
  "Incorrect. The decline continues after day 30: 210 to 180 to 160 to 150 mg/dL, so it does not stay constant.",
  "Correct. The decrements are 48 mg/dL (days 0-30), 30 (30-60), 20 (60-90) and 10 (90-120), so the fall is steepest first and slows progressively.",
  "Incorrect. The treatment mean falls from 258 to 150 mg/dL, so it did not remain unchanged."]},
 "bp1299_1": {"ox": [
  "Incorrect. Time points in the treatment group alone cannot separate the drug from the passage of time; the control also falls, 260 to 240 mg/dL.",
  "Incorrect. The p-values in the table (0.003 to 1e-06) quantify chance, not the time trend, and they provide no comparison group.",
  "Correct. The placebo group follows the same 120-day time course (260 to 240 mg/dL), so the between-group difference at each time point isolates the drug.",
  "Incorrect. Enrolling adults with hypertriglyceridemia defines the population but supplies no comparison for the 120-day time course in the table."]},
 "bp1299_2": {"ox": [
  "Correct. The treatment mean falls from 258 to 150 mg/dL, a 108 mg/dL drop, and 108 / 258 × 100 = 41.9%.",
  "Incorrect. 48.5% would be a 125 mg/dL fall on the 258 mg/dL baseline; the table shows 108 mg/dL.",
  "Incorrect. 54.3% would need a 140 mg/dL fall; the treatment mean falls 108 mg/dL.",
  "Incorrect. 60.2% would need a 155 mg/dL fall on 258; the observed fall is 108 mg/dL."]},
 "bp1299_3": {"ox": [
  "Incorrect. This is supported: the p-values are 0.003, 0.0001, 2e-05 and 1e-06, all below 0.05.",
  "Incorrect. This is supported: the control mean falls from 260 to 240 mg/dL over 120 days.",
  "Correct. The table has no hepatic lipase column, so a causal link between the triglyceride fall and hepatic lipase activity is not shown by these data.",
  "Incorrect. This is supported: the treatment mean falls 108 mg/dL while the control falls 20 mg/dL."]},
 "bp1299_4": {"ox": [
  "Incorrect. 78 is 258 - 180, the treatment group's own change from baseline, not the group difference at day 60.",
  "Incorrect. 80 is 260 - 180, which uses the baseline control value instead of the day-60 control mean of 250.",
  "Correct. At day 60 the control mean is 250 mg/dL and the treatment mean is 180 mg/dL, so the difference is 250 - 180 = 70 mg/dL.",
  "Incorrect. 30 is 210 - 180, the treatment group's change between day 30 and day 60."]},
 "bp1300_0": {"ox": [
  "Incorrect. 34.3 µmol/min is the inhibited velocity at 800 µM, not at 400 µM.",
  "Incorrect. 40 µmol/min is the uninhibited velocity at 400 µM, from the no-inhibitor column.",
  "Correct. The 400 µM row lists 24 µmol/min in the 120 µM inhibitor column.",
  "Incorrect. 15 µmol/min is the inhibited velocity at 200 µM, one row above the 400 µM row in the table."]},
 "bp1300_1": {"ox": [
  "Correct. Competitive inhibition raises apparent Km but leaves Vmax unchanged, so at very high substrate the inhibited rate should approach the uninhibited plateau (43.6 versus 53.3 µmol/min at 1600 µM and still rising).",
  "Incorrect. Varying enzyme concentration at one substrate level tests proportionality to enzyme, not whether substrate outcompetes the inhibitor at the table's 1600 µM row.",
  "Incorrect. A longer incubation tests stability and linearity over time, not the inhibition mechanism seen in the table.",
  "Incorrect. A lower temperature slows both reactions and does not distinguish competitive from noncompetitive inhibition of the table's velocities."]},
 "bp1300_2": {"ox": [
  "Incorrect. 40 µM is 120 / 3, which divides by the Km ratio instead of by the ratio minus one.",
  "Incorrect. 240 µM is 120 × 2, multiplying by the ratio instead of dividing.",
  "Incorrect. 360 µM is 120 × 3, which also multiplies rather than divides.",
  "Correct. The rates converge as [S] rises (53.3 versus 43.6 µmol/min at 1600 µM), so Vmax is unchanged and Km,app / Km = 3; then [I] / Ki = 2 and Ki = 120 / 2 = 60 µM."]},
 "bp1300_3": {"ox": [
  "Correct. Competitive inhibition leaves Vmax unchanged, so a lower Vmax at saturating [S] contradicts it; the table's rates converge as substrate rises (53.3 versus 43.6 µmol/min at 1600 µM).",
  "Incorrect. A larger apparent Km is expected: half-maximal velocity shifts to a higher [S] with inhibitor, as the table's 400 µM rates show (30 without, 24 with).",
  "Incorrect. Binding free enzyme in preference to the enzyme-substrate complex is the definition of competitive inhibition, consistent with the table's converging rates.",
  "Incorrect. Weaker inhibition at higher [S] is expected, and the table shows the gap narrowing from 12 versus 4.6 to 53.3 versus 43.6 µmol/min."]},
 "bp1300_4": {"ox": [
  "Incorrect. Competitive inhibitors do not lower the turnover number at saturating substrate; Vmax is unchanged, as the converging rates at 1600 µM show.",
  "Incorrect. Covalent binding is not required; these drugs bind reversibly and can be outcompeted, as the converging rates at 1600 µM show.",
  "Incorrect. Binding only the enzyme-substrate complex describes uncompetitive inhibition, which the table's unchanged Vmax rules out.",
  "Correct. Competition requires occupying the same active site as the substrate, which is why a structural analog can fit there and be outcompeted at high [S], as the table shows."]},
}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(E, ensure_ascii=False, separators=(",", ":")))
    print("wrote", OUT, len(E), "entries")


if __name__ == "__main__":
    main()
