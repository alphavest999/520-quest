#!/usr/bin/env python3
"""Hand-authored Phase 2 batch 4: bp1277, bp1278, bp1279 (15 questions), single-line."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1277_1279.json")

E = {
 "bp1277_0": {"ox": [
  "Correct. The TC_mean column reads 190 mg/dL for the supplement group and 195 mg/dL for placebo, so the supplement group's mean total cholesterol is 5 mg/dL lower.",
  "Incorrect. LDL_mean is 120 mg/dL with the supplement and 125 mg/dL with placebo, so the supplement group's LDL-C is lower, not higher.",
  "Incorrect. Mean total cholesterol is 190 mg/dL with the supplement and 195 mg/dL with placebo, so the two values differ by 5 mg/dL rather than being identical.",
  "Incorrect. HDL_mean is 55 mg/dL with the supplement and 53 mg/dL with placebo, so the supplement group's HDL-C is higher, not lower."]},
 "bp1277_1": {"ox": [
  "Incorrect. A higher dose of the supplement is another active arm; the passage's design needs an inactive comparison to keep participants and investigators blind, which a higher dose cannot supply.",
  "Incorrect. A no-intervention group shows what happens without treatment, but participants would know they are untreated, so the passage's double-blind condition is lost.",
  "Correct. A placebo identical in appearance to the supplement lets participants and investigators stay blind, which is the control the passage's double-blind design requires.",
  "Incorrect. A different lipid-lowering drug is an active comparator; the passage tests one supplement against placebo, so a second active drug would not isolate its effect."]},
 "bp1277_2": {"ox": [
  "Incorrect. 2 mg/dL is the HDL-C difference (55 - 53), not a difference between LDL-C means.",
  "Correct. LDL_mean is 120 mg/dL for the supplement group and 125 mg/dL for placebo, so the absolute difference is 125 - 120 = 5 mg/dL.",
  "Incorrect. No pair of LDL-C means differs by 10 mg/dL; the two table values are 120 and 125 mg/dL.",
  "Incorrect. 15 is the supplement group's TC_SD, a spread rather than a difference between LDL-C means."]},
 "bp1277_3": {"ox": [
  "Incorrect. This statement is supported: placebo LDL-C 125 minus supplement LDL-C 120 is 5 mg/dL lower.",
  "Incorrect. This statement is supported: supplement HDL-C 55 minus placebo HDL-C 53 is 2 mg/dL higher.",
  "Incorrect. This statement is supported: placebo TC 195 minus supplement TC 190 is 5 mg/dL lower.",
  "Correct. The table reports only means and SDs and the passage only states the study aim; no test statistic or p-value appears, so a statistically significant difference is not supported."]},
 "bp1277_4": {"ox": [
  "Correct. The LDL-C difference is 125 - 120 = 5 mg/dL, and 5 / 125 × 100 = 4.0% of the placebo mean.",
  "Incorrect. 5 / 120 × 100 = 4.2%, which divides by the supplement mean instead of the placebo reference of 125 mg/dL.",
  "Incorrect. 5.0 is the absolute difference in mg/dL with no division by the reference mean, so it is not a percentage.",
  "Incorrect. 8.3% would need 10 / 120; the LDL-C difference in the table is 5 mg/dL, not 10."]},
 "bp1278_0": {"ox": [
  "Correct. Average weight gain is 0.15 kg in the experimental group against 0.12 kg in controls, so the difference is 0.15 - 0.12 = 0.03 kg, an increase.",
  "Incorrect. The experimental group gained more (0.15 versus 0.12 kg), so the direction is an increase, not a decrease.",
  "Incorrect. 0.12 kg is the control group's own average gain, not the difference between the two groups.",
  "Incorrect. 0.12 kg is the control group's gain, and the comparison runs the other way: the experimental group gained 0.03 kg more."]},
 "bp1278_1": {"ox": [
  "Correct. The passage states food intake remained comparable between groups, so eating more does not explain the extra 0.03 kg of gain.",
  "Incorrect. Serum insulin (55 versus 45 µU/mL) is an outcome of the diet, not a measure of how much the animals ate.",
  "Incorrect. Identical baseline weights (0.25 ± 0.02 kg in both groups) rule out an initial weight difference, not a difference in food intake.",
  "Incorrect. The passage says twelve animals were assigned to each group, which describes group size rather than how much food each group consumed."]},
 "bp1278_2": {"ox": [
  "Incorrect. 10 / 45 × 100 = 22.2%; a 12% rise would be about 5.4 µU/mL, not the 10 µU/mL rise in the table.",
  "Correct. Insulin rises from 45 to 55 µU/mL, so (55 - 45) / 45 × 100 = 10 / 45 × 100 = 22.2%, which rounds to 22%.",
  "Incorrect. 33% would require a rise of about 14.9 µU/mL over the control value of 45; the table shows a 10 µU/mL rise.",
  "Incorrect. 50% would require a rise of 22.5 µU/mL over 45; the observed rise is 10 µU/mL."]},
 "bp1278_3": {"ox": [
  "Incorrect. This is accurate: 0.15 - 0.12 = 0.03 kg more gain in the experimental group.",
  "Correct. Only fasting insulin is reported (55 versus 45 µU/mL), with no glucose or tolerance measurement, so improved insulin sensitivity cannot be concluded from the table.",
  "Incorrect. This is accurate: the passage states that food intake remained comparable between the groups.",
  "Incorrect. This is accurate: serum insulin is 55 µU/mL in the experimental group and 45 µU/mL in controls."]},
 "bp1278_4": {"ox": [
  "Correct. Insulin has to be read alongside fasting glucose; without a glucose value, the higher insulin (55 versus 45 µU/mL) cannot be classed as better or worse sensitivity.",
  "Incorrect. Serum sodium is not reported in the passage's table, and it does not bear on how insulin acts at the tissues.",
  "Incorrect. Resting heart rate is not reported in the passage and does not measure insulin action, so it cannot clarify the 55 versus 45 µU/mL insulin values.",
  "Incorrect. Bone length is not reported in the passage and does not measure insulin action; the only insulin measure in Table 1 is the fasting level."]},
 "bp1279_0": {"ox": [
  "Incorrect. Placebo reads a 2 mmHg reduction (140 to 138), the smallest in the table.",
  "Incorrect. Low-dose reads 11 mmHg (141 to 130), well below the high-dose value.",
  "Incorrect. Medium-dose reads 22 mmHg (142 to 120), which is less than the high-dose reduction.",
  "Correct. The Mean Reduction column reads 2, 11, 22 and 30 mmHg for placebo, low, medium and high dose, so the high-dose group's 30 mmHg fall (140 to 110) is the largest."]},
 "bp1279_1": {"ox": [
  "Correct. The passage states the trial was randomized, double-blind and placebo-controlled, with a placebo arm plus three active dose arms.",
  "Incorrect. An observational cohort follows patients who were not assigned a treatment; in the passage participants are assigned to placebo or a dose.",
  "Incorrect. A case-control study groups people by an outcome that already occurred; here the doses were assigned before the 4-week SBP readings.",
  "Incorrect. Open-label means participants know their assignment; the passage states the trial was double-blind."]},
 "bp1279_2": {"ox": [
  "Incorrect. 10% of the 140 mmHg baseline is 14 mmHg, while the high-dose fall in the table is 30 mmHg.",
  "Incorrect. 15% is about 21 mmHg on 140, close to the medium-dose fall of 22 mmHg (22 / 142 = 15.5%), not the high-dose fall.",
  "Incorrect. 20% would be 28 mmHg on 140, and 30 / 150 uses a baseline of 150 that the high-dose row does not have.",
  "Correct. The high-dose row falls from 140 to 110 mmHg, a 30 mmHg drop, and 30 / 140 × 100 = 21.4%."]},
 "bp1279_3": {"ox": [
  "Incorrect. This is supported: the high-dose mean reduction of 30 mmHg is the largest in the table.",
  "Correct. The placebo row falls from 140 to 138 mmHg, a 2 mmHg reduction, so \"no change in SBP\" is not supported by the data.",
  "Incorrect. This is supported: the passage states dizziness and headache were most common in the high-dose group.",
  "Incorrect. This is supported: the passage states the analysis used ANOVA with post-hoc Tukey tests."]},
 "bp1279_4": {"ox": [
  "Correct. High-dose falls 30 mmHg and placebo falls 2 mmHg, so the excess is 30 - 2 = 28 mmHg.",
  "Incorrect. 30 mmHg is the high-dose fall alone and leaves the 2 mmHg placebo response in the total.",
  "Incorrect. 8 mmHg is 30 - 22, the gap between high and medium dose, not between high dose and placebo.",
  "Incorrect. 19 mmHg is 30 - 11, the gap between the high-dose and low-dose reductions in the Mean Reduction column, not the gap against placebo."]},
}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(E, ensure_ascii=False, separators=(",", ":")))
    print("wrote", OUT, len(E), "entries")


if __name__ == "__main__":
    main()
