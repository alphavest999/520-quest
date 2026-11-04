#!/usr/bin/env python3
"""Hand-authored Phase 2 batch 1: bp1261-bp1263 (15 questions), single-line output."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1261_1263.json")

E = {
 "bp1261_0": {"ox": [
  "Incorrect. The placebo row reads baseline 148 mmHg and week-4 147 mmHg, a change of -1 mmHg, the smallest drop in the table.",
  "Incorrect. The low-dose row reads 149 mmHg at baseline and 141 at week 4, a change of -8 mmHg, less than the medium and high doses.",
  "Incorrect. The medium-dose row reads 150 mmHg at baseline and 134 at week 4, a change of -16 mmHg; that is the largest only until the high dose is read.",
  "Correct. The Mean Change column reads -1 (placebo), -8 (low), -16 (medium) and -22 (high), so the high-dose group's 22 mmHg fall is the largest. Magnitudes in order: 1 < 8 < 16 < 22 mmHg."]},
 "bp1261_1": {"ox": [
  "Correct. The passage calls the trial \"randomized, double-blind, placebo-controlled\": random assignment is the step that spreads known and unknown confounders across the four arms before treatment starts.",
  "Incorrect. A high-dose arm is one of the four treatments the passage assigns (placebo, low, medium and high dose); adding an arm does not balance confounders between the arms.",
  "Incorrect. Baseline SBP was recorded for all participants (148, 149, 150 and 151 mmHg), so it marks each group's starting point rather than controlling confounding.",
  "Incorrect. Reporting the mean change, as the table does for -1, -8, -16 and -22 mmHg, summarizes the outcome after treatment; it does not prevent a confounder from differing between groups."]},
 "bp1261_2": {"ox": [
  "Correct. The medium-dose row reads baseline 150 mmHg and week-4 134 mmHg, a change of -16 mmHg. Percent reduction = (150 - 134) / 150 × 100 = 16 / 150 × 100 = 10.67%, which rounds to 10.7%.",
  "Incorrect. 16 / 134 × 100 = 11.94%, which divides the 16 mmHg change by the week-4 value instead of the 150 mmHg baseline.",
  "Incorrect. 16.0% is the raw 16 mmHg change with a percent sign attached; 16 mmHg out of a 150 mmHg baseline is 10.7%, not 16%.",
  "Incorrect. 22.0% is the high-dose group's change in mmHg (-22), not a percentage of any baseline."]},
 "bp1261_3": {"ox": [
  "Incorrect. This statement is supported: the Mean Change column falls -1, -8, -16 and -22 mmHg as dose rises from none to low to medium to high, which is a dose-dependent effect.",
  "Incorrect. This statement is supported: -22 mmHg in the high-dose row is the largest magnitude in the Mean Change column.",
  "Correct. The placebo row reads 148 mmHg at baseline and 147 at week 4, a 1 mmHg fall, and the passage never claims clinical significance for it; \"clinically significant decrease\" is therefore not supported by the data presented.",
  "Incorrect. This statement is supported: the baseline column reads 148, 149, 150 and 151 mmHg, a spread of only 3 mmHg across the four groups."]},
 "bp1261_4": {"ox": [
  "Incorrect. A placebo effect would appear as the change in the placebo arm, which was -1 mmHg (148 to 147); it cannot produce the graded pattern across the three dose arms.",
  "Correct. Mean change by group is -1, -8, -16 and -22 mmHg as dose rises from none to low to medium to high, so the size of the fall tracks the dose: a dose-response relationship.",
  "Incorrect. Randomization describes how the trial was run (the passage's \"randomized, double-blind, placebo-controlled\" design), not a pattern in the results; the pattern asked about is the graded change across doses.",
  "Incorrect. Baselines were 148-151 mmHg, a 3 mmHg spread, so baseline differences cannot explain why the change column is graded from -1 to -22 mmHg."]},
 "bp1262_0": {"ox": [
  "Incorrect. Control is the reference group at 520 ms; improvement is measured against it, so it cannot show the greatest improvement relative to itself.",
  "Incorrect. Low intensity reads 485 ms against 520 ms for control, a 35 ms difference, smaller than the 90 ms gap for high intensity.",
  "Incorrect. Medium intensity reads 455 ms against 520 ms for control, a 65 ms difference, which is less than the high-intensity gap of 90 ms.",
  "Correct. Post-test means are 520 (control), 485 (low), 455 (medium) and 430 ms (high); high intensity is 520 - 430 = 90 ms below control, the largest difference in the table."]},
 "bp1262_1": {"ox": [
  "Correct. The design sets three graded intensities (low, medium, high) beside a no-training control, and the means fall 520, 485, 455 and 430 ms across them, which is what allows intensity to be compared step by step.",
  "Incorrect. The repeated-measures ANOVA is an analysis the passage says the researchers plan to run; it does not create the graded training intensities (low, medium, high) that a dose-response comparison needs.",
  "Incorrect. A single 4-week duration and one age range (25-35) hold those factors constant, but neither varies training intensity.",
  "Incorrect. The SDs (45, 40, 35 and 30 ms) describe spread within each group; reporting them does not produce groups at different training intensities."]},
 "bp1262_2": {"ox": [
  "Incorrect. A d of 0.75 would need a spread of about 90 / 0.75 = 120 ms, and the largest spread anywhere in Table 1 is the control SD of 45 ms.",
  "Incorrect. 1.25 would need a spread near 90 / 1.25 = 72 ms, close to adding the two SDs (45 + 30 = 75) instead of pooling them.",
  "Correct. SDpooled = square root of (45 squared + 30 squared) / 2 = square root of (2025 + 900) / 2 = square root of 1462.5, about 38.2 ms. Then d = (520 - 430) / 38.2 = 90 / 38.2, about 2.35.",
  "Incorrect. 3.00 is 90 / 30, dividing the 90 ms difference by the high-intensity SD alone instead of by the pooled SD of about 38.2 ms."]},
 "bp1262_3": {"ox": [
  "Incorrect. This reading is correct: the means fall 520, 485, 455 and 430 ms as intensity rises from control to low to medium to high.",
  "Incorrect. This reading is correct: 520 - 430 = 90 ms separates the high-intensity and control means in Table 1.",
  "Correct. The passage says the researchers \"plan to analyze the data using a repeated-measures ANOVA\"; no ANOVA result is reported, so saying the test showed significant differences misreads a planned analysis as a finding.",
  "Incorrect. This reading is correct: the SD column falls 45, 40, 35 and 30 ms across control, low, medium and high intensity."]},
 "bp1262_4": {"ox": [
  "Correct. The means move in one direction as training goes from none to low to medium to high: 520, 485, 455 and 430 ms. A graded change that follows increasing dose is a dose-response relationship.",
  "Incorrect. A placebo effect would require a group given an inert intervention; the design has a no-training control, and the passage describes no placebo arm.",
  "Incorrect. Regression to the mean concerns extreme baseline scores moving toward average; the passage reports post-test means only and shows a graded fall across four levels of training.",
  "Incorrect. A ceiling effect would flatten scores at the top of the scale, but here each step adds improvement, 520 to 485 to 455 to 430 ms."]},
 "bp1263_0": {"ox": [
  "Incorrect. The control row reads 45.2, the lowest of the four means, not the highest.",
  "Incorrect. The visuospatial row reads 53.7, which is 60.3 - 53.7 = 6.6 below the combined group.",
  "Incorrect. The verbal row reads 52.9, which is 60.3 - 52.9 = 7.4 below the combined group and 0.8 below the visuospatial group.",
  "Correct. Table 1 reads 45.2 (control), 53.7 (visuospatial), 52.9 (verbal) and 60.3 (combined), so the combined group's 60.3 is the highest mean post-intervention score."]},
 "bp1263_1": {"ox": [
  "Incorrect. A cross-sectional study measures groups at a single time point; the passage tests working memory before and after an eight-week program.",
  "Incorrect. A case-control study compares people who already have an outcome with those who do not; the passage instead assigns participants to training arms before measuring the outcome.",
  "Correct. The passage states that participants were \"randomly assigned\" to a no-training control or one of three training programs and then assessed, so the design is a randomized controlled trial.",
  "Incorrect. A prospective cohort follows groups defined by an existing exposure; in the passage the training programs were assigned by the researchers, not chosen by participants."]},
 "bp1263_2": {"ox": [
  "Incorrect. No pair of means in Table 1 differs by 3.6; the pairwise gaps are 0.8 (V vs W), 6.6 (C vs V), 7.4 (C vs W), 7.7 (W vs control), 8.5 (V vs control) and 15.1 (C vs control).",
  "Incorrect. 5.6 matches no pair of means; the combined-minus-visuospatial gap is 60.3 - 53.7 = 6.6, not 5.6.",
  "Correct. Combined (C) reads 60.3 and visuospatial (V) reads 53.7, so the difference is 60.3 - 53.7 = 6.6.",
  "Incorrect. 7.6 is close to 7.4, which is the combined-minus-verbal gap (60.3 - 52.9), not the combined-minus-visuospatial gap."]},
 "bp1263_3": {"ox": [
  "Correct. Table 1 lists post-intervention means and SDs only. Change from before to after needs the pre-intervention scores, which the table does not contain.",
  "Incorrect. This can be determined: 60.3 in the combined row is the highest of the four means (45.2, 53.7, 52.9, 60.3).",
  "Incorrect. This can be determined directly from the table by subtraction: the combined mean 60.3 minus the visuospatial mean 53.7 equals 6.6.",
  "Incorrect. This can be determined: the control mean of 45.2 is below 52.9, 53.7 and 60.3, so it is lower than every trained group's mean."]},
 "bp1263_4": {"ox": [
  "Correct. The hypothesis is that the combined program beats each single program, and Table 1 shows C at 60.3 against V at 53.7 and W at 52.9, so the combined mean exceeds both single-modality means.",
  "Incorrect. V at 53.7 versus W at 52.9 is a 0.8 gap between the two single programs; it says nothing about the combined program.",
  "Incorrect. The control SD of 5.1 is the largest spread in the table, but an SD describes variability inside a group, not which program produced the best score.",
  "Incorrect. Every trained group (53.7, 52.9, 60.3) exceeds control (45.2), which shows training helped at all; it does not show the combined program beat the single-modality programs."]},
}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(E, ensure_ascii=False, separators=(",", ":")))
    print("wrote", OUT, len(E), "entries")


if __name__ == "__main__":
    main()
