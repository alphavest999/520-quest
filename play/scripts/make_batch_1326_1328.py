#!/usr/bin/env python3
"""Hand-authored Phase 2 batch 14: bp1326, bp1327, bp1328 (15 questions), single-line."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1326_1328.json")

E = {
 "bp1326_0": {"ox": [
  "Incorrect. The Control row reads 68.4 mm, the highest mean VAS in Table 1, so it cannot be the lowest.",
  "Incorrect. The Low Dose row reads 55.2 mm, above the 42.7 and 31.1 mm of the two higher-dose rows.",
  "Incorrect. The Medium Dose row reads 42.7 mm, below Control and Low Dose but still above the 31.1 mm of the High Dose row.",
  "Correct. The High Dose row reads 31.1 mm against 68.4, 55.2 and 42.7 mm in Table 1, the lowest of the four week-12 means."]},
 "bp1326_1": {"ox": [
  "Incorrect. A crossover gives every patient all four doses, so carry-over between treatments cannot be separated from a dose effect without washout evidence the passage never describes.",
  "Correct. The passage assigns 120 patients to placebo, 10 mg, 20 mg and 40 mg groups and reads each patient once at week 12, which is a parallel-group randomized controlled trial across four dose levels.",
  "Incorrect. A case-control design groups people by an outcome that has already occurred; here the dose was assigned before the week-12 VAS reading.",
  "Incorrect. An observational cohort assigns no treatment, yet the passage states that patients were assigned to one of four groups."]},
 "bp1326_2": {"ox": [
  "Correct. (68.4 - 31.1)/68.4 = 37.3/68.4 = 54.5%, the drop from the Control mean to the High Dose mean expressed as a share of the Control mean.",
  "Incorrect. 45.3% is near the remaining fraction 31.1/68.4 = 45.5%, the pain still present after treatment rather than the reduction.",
  "Incorrect. 62.1% is near the Medium Dose mean as a share of Control, 42.7/68.4 = 62.4%, which compares a different pair of rows.",
  "Incorrect. 48.6% does not follow from Table 1: the only reduction measured from the Control row is 37.3/68.4 = 54.5%."]},
 "bp1326_3": {"ox": [
  "Incorrect. This is true: the High Dose mean of 31.1 mm is the lowest week-12 value in Table 1.",
  "Incorrect. This is true: 37.3/68.4 = 54.5%, which is more than half of the Control mean.",
  "Correct. The Low Dose mean is 55.2 mm and the Medium Dose mean is 42.7 mm, so the low-dose group is higher, not lower, which makes this the false statement.",
  "Incorrect. This is true: the High Dose SD of 8.9 is the smallest of the four SD cells in Table 1 (12.3, 10.8, 9.5, 8.9)."]},
 "bp1326_4": {"ox": [
  "Correct. 55.2 - 31.1 = 24.1 mm across the three 10 mg steps from 10 mg to 40 mg, and 24.1/3 = 8.0 mm per 10 mg.",
  "Incorrect. 12.5 mm is the single fall from 10 mg to 20 mg (55.2 - 42.7), one interval rather than an average over the full 30 mg span.",
  "Incorrect. 11.6 mm is the fall from 20 mg to 40 mg (42.7 - 31.1), which spans 20 mg, so it is not a per-10 mg figure.",
  "Incorrect. 24.1 mm is the whole fall from 10 mg to 40 mg; dividing it by the three 10 mg steps gives 8.0 mm."]},
 "bp1327_0": {"ox": [
  "Incorrect. The means span 39.7 to 45.2 min, a 5.5 min spread, so they are not nearly identical.",
  "Incorrect. Carbohydrate is 42.8 min and placebo is 45.2 min, so the carbohydrate mean is shorter, not longer.",
  "Correct. Table 1 reads 45.2 (placebo), 42.8 (carbohydrate), 43.5 (protein) and 39.7 min (combined), so every supplement row is below placebo and 39.7 min is the lowest row.",
  "Incorrect. The placebo row at 45.2 min, not the protein row at 43.5 min, is the longest mean time."]},
 "bp1327_1": {"ox": [
  "Incorrect. The 12-week duration affects how long an effect is followed but says nothing about whether the groups were comparable before treatment began.",
  "Correct. The passage states that 80 participants were randomly assigned to the four groups, which is what lets the between-group differences be attributed to the supplements rather than to pre-existing differences.",
  "Incorrect. The 40-km time trial is the outcome measure; a suitable outcome measure does not by itself make the comparison valid.",
  "Incorrect. Table 1's means and SDs summarise the four rows but do not control confounding the way random assignment of the 80 participants does."]},
 "bp1327_2": {"ox": [
  "Incorrect. 5.0% is close to the placebo-to-carbohydrate gap as a share of placebo, (45.2 - 42.8)/45.2 = 5.3%, a between-group figure rather than Group D's own change.",
  "Incorrect. 8.3% is close to the protein-to-combined gap over placebo, (43.5 - 39.7)/45.2 = 8.4%, again a between-group difference.",
  "Correct. The passage reports that Group D showed a 12.5% reduction in completion time compared with its own baseline, and Table 1's 39.7 min is that group's end-of-study mean.",
  "Incorrect. 15.7% exceeds every change the data support; the widest gap between two group means is (45.2 - 39.7)/45.2 = 12.2%."]},
 "bp1327_3": {"ox": [
  "Incorrect. This is supported: the combined group's 39.7 min is the lowest mean in Table 1.",
  "Incorrect. This is supported: the passage states that Group A increased by 2.1% from baseline.",
  "Incorrect. This is supported: carbohydrate at 42.8 min and protein at 43.5 min are both below placebo's 45.2 min.",
  "Correct. Protein alone finished in 43.5 min against 39.7 min for the combined supplement, so protein was slower, not faster, and this is the statement the data do not support."]},
 "bp1327_4": {"ox": [
  "Incorrect. 1.7 min is placebo minus protein (45.2 - 43.5), a different pair of rows.",
  "Incorrect. 3.1 min is carbohydrate minus combined (42.8 - 39.7), not placebo minus combined.",
  "Correct. 45.2 - 39.7 = 5.5 min, the difference between the placebo mean and the combined-supplement mean in Table 1.",
  "Incorrect. 6.5 min is not the difference of any two means in Table 1; the largest such gap is 5.5 min."]},
 "bp1328_0": {"ox": [
  "Incorrect. The untreated row shows Ct 25 for SOD2, higher than the treated 22, and a higher Ct means the threshold came later with less template.",
  "Incorrect. The two SOD2 Ct values are 25 and 22, not equal, so the starting amounts differ even though both reference Ct values are 18.",
  "Correct. The treated row shows SOD2 Ct 22 against 25 untreated, and with the reference gene at 18 in both rows the treated cells crossed threshold three cycles sooner, meaning more starting SOD2 template.",
  "Incorrect. Both primer pairs have efficiency near 100% and each row uses the same target and reference, so the Ct difference alone gives the direction without a standard curve."]},
 "bp1328_1": {"ox": [
  "Incorrect. Raising the annealing temperature changes specificity, but the passage describes no reaction that omits reverse transcriptase, so RNA-derived cDNA and genomic DNA still cannot be told apart.",
  "Correct. A no-reverse-transcriptase control omits the enzyme that makes cDNA, so any product appearing in that reaction must come from genomic DNA rather than the RNA the passage extracted and DNase treated.",
  "Incorrect. Doubling the template in the reaction changes signal strength but cannot reveal whether that template is cDNA or genomic DNA, which is what the passage's DNase step is meant to exclude.",
  "Incorrect. A no-primer reaction tests for primer-independent signal rather than DNA contamination, since the passage has primers present in every amplifying reaction."]},
 "bp1328_2": {"ox": [
  "Incorrect. 3 is the Ct difference itself (25 - 22), not the fold change; at 100% efficiency each cycle doubles the product, so the factor is 2 raised to that difference.",
  "Correct. \u0394Ct is 25 - 18 = 7 untreated and 22 - 18 = 4 treated, so \u0394\u0394Ct = 4 - 7 = -3 and the fold change is 2^3 = 8.",
  "Incorrect. 16-fold would need a \u0394\u0394Ct of 4, which is the treated \u0394Ct itself rather than the difference between the two \u0394Ct values.",
  "Incorrect. 0.125-fold is 2^-3, the reciprocal; since the treated Ct is lower, SOD2 rose, so the factor is above 1."]},
 "bp1328_3": {"ox": [
  "Incorrect. This is true: with 100% efficiency the product doubles each cycle, so one Ct apart is a two-fold difference.",
  "Correct. Ct 22 in treated cells against 25 in untreated cells means the treated cells held more template, so a higher Ct marks a lower starting amount, making this the incorrect statement.",
  "Incorrect. This is true: both rows show reference Ct 18, and dividing by the reference corrects for how much RNA entered each reaction.",
  "Incorrect. This is true: Table 1's treated Ct of 22 crosses threshold earlier than the untreated 25, and earlier crossing means more target at the start."]},
 "bp1328_4": {"ox": [
  "Incorrect. Introns lie within the coding region and bear on splicing; the passage ties the Ct change to transcription, so intron number does not locate a factor-binding site.",
  "Incorrect. The poly-A tail is added to the finished mRNA and affects its processing and stability; the passage instead names the promoter region as the place to look next.",
  "Correct. Transcription factors bind promoter and enhancer elements upstream of the transcription start site, which is why the passage's group planned to examine that region after the Ct change.",
  "Incorrect. A tRNA anticodon pairs with mRNA codons during translation, a step downstream of the transcription that the passage's Ct values measure."]},
}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(E, ensure_ascii=False, separators=(",", ":")))
    print("wrote", OUT, len(E), "entries")


if __name__ == "__main__":
    main()
