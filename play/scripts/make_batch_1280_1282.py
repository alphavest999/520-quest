#!/usr/bin/env python3
"""Hand-authored Phase 2 batch 5: bp1280, bp1281, bp1282 (15 questions), single-line."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1280_1282.json")

E = {
 "bp1280_0": {"ox": [
  "Correct. The Week 12 column reads 148 (placebo), 135 (low-dose) and 120 mmHg (high-dose), so the high-dose group's week-12 mean is 120 mmHg, the lowest of the three.",
  "Incorrect. 135 mmHg is the low-dose group's week-12 value (149 to 135), not the high-dose group's.",
  "Incorrect. 148 mmHg is the placebo group's week-12 value (150 to 148).",
  "Incorrect. 150 mmHg is the placebo group's baseline reading, not a week-12 value."]},
 "bp1280_1": {"ox": [
  "Correct. The passage states that 120 participants were randomized into three groups and that the design was double-blind and placebo-controlled, which is a randomized controlled trial.",
  "Incorrect. An observational cohort follows patients without assigning treatment; in the passage participants are randomized to placebo, 10 mg or 20 mg.",
  "Incorrect. A case-control study groups people by an outcome that already occurred; here the groups were assigned before the 12 weeks of SBP readings.",
  "Incorrect. A cross-sectional study measures a single time point; the passage measures SBP weekly over 12 weeks."]},
 "bp1280_2": {"ox": [
  "Correct. The high-dose row falls from 151 to 120 mmHg, a 31 mmHg drop, and 31 / 151 × 100 = 20.5%, which rounds to 20%.",
  "Incorrect. 31 / 120 × 100 = 25.8%, about 25%, which divides by the week-12 value instead of the 151 mmHg baseline.",
  "Incorrect. 30% would need a fall of about 45 mmHg on the 151 mmHg baseline; the high-dose fall is 31 mmHg.",
  "Incorrect. 35% would need a fall of about 53 mmHg on 151; the table shows 151 falling only to 120 mmHg."]},
 "bp1280_3": {"ox": [
  "Incorrect. The placebo baseline is 150 mmHg, one mmHg below the high-dose baseline.",
  "Incorrect. The low-dose baseline is 149 mmHg, the lowest of the three baselines.",
  "Correct. The baseline column reads 150 (placebo), 149 (low-dose) and 151 mmHg (high-dose), so the high-dose group starts highest.",
  "Incorrect. The baselines are not equal: 150, 149 and 151 mmHg in the table."]},
 "bp1280_4": {"ox": [
  "Incorrect. A placebo effect would appear in the placebo arm, which fell only 2 mmHg (150 to 148); it cannot explain the 31 mmHg fall at 20 mg.",
  "Correct. The reductions grow with dose: 2 mmHg (placebo), 14 mmHg (low-dose, 149 to 135) and 31 mmHg (high-dose, 151 to 120), which is a dose-response relationship.",
  "Incorrect. Confounding bias is a threat to a study's design, not a pattern in its results; the passage's randomization addresses it, and the graded falls track dose.",
  "Incorrect. The Hawthorne effect concerns behaviour changing when people are observed; the passage measures no such behaviour, and the reductions follow dose."]},
 "bp1281_0": {"ox": [
  "Incorrect. 120 AU is the ROS intensity in the 0 µM control row, not the 50 µM row.",
  "Incorrect. 110 AU is the 10 µM value, one row above the 50 µM row in the table.",
  "Correct. The 48-hour table lists 80 AU of ROS intensity for the 50 µM concentration, alongside 85% viability.",
  "Incorrect. 60 AU is the 100 µM value, the lowest ROS intensity in the table."]},
 "bp1281_1": {"ox": [
  "Incorrect. A single 50 µM concentration cannot show how ROS changes with dose; a dose-response needs several concentrations compared under the same conditions.",
  "Correct. Exposing cells to 0, 10, 50 and 100 µM for the same 48 hours and measuring ROS and viability at one time point is the design that isolates concentration.",
  "Incorrect. Two concentrations (0 and 100 µM) give only one comparison, and reading at 24 hours leaves the 48-hour table values unused.",
  "Incorrect. One concentration at 12 hours cannot show how ROS varies with concentration; it gives a single point."]},
 "bp1281_2": {"ox": [
  "Incorrect. 5.3% is 5 / 95; the viability drop at 100 µM is 25 points (95 to 70), not 5.",
  "Incorrect. 7.9% matches no viability drop in the table; from 95% the falls are 3 points (10 µM), 10 points (50 µM) and 25 points (100 µM).",
  "Correct. Viability falls from 95% at 0 µM to 70% at 100 µM, a 25-point drop, and 25 / 95 × 100 = 26.3%.",
  "Incorrect. 15.8% is (95 - 80) / 95, the drop at 50 µM, not the drop at 100 µM."]},
 "bp1281_3": {"ox": [
  "Incorrect. This is supported: ROS intensity falls 120, 110, 80 and 60 AU as concentration rises through 0, 10, 50 and 100 µM.",
  "Incorrect. This is supported: viability falls 95, 92, 85 and 70% across the same four concentrations.",
  "Incorrect. This is supported: among the treated rows, 10 µM has the highest ROS at 110 AU, against 80 and 60 AU.",
  "Correct. The control row has the highest viability in the table (95%), not the lowest, so \"the control group has the lowest cell viability\" is not supported."]},
 "bp1281_4": {"ox": [
  "Correct. At 100 µM, ROS falls from 120 to 60 AU, a 50% drop, while viability falls from 95% to 70%, so the lower ROS did not bring higher viability.",
  "Incorrect. Both values fall: ROS from 120 to 60 AU and viability from 95% to 70%.",
  "Incorrect. ROS decreases rather than rises (120 to 60 AU), so the table does not show a pro-oxidant effect.",
  "Incorrect. Both values change substantially: ROS by 60 AU and viability by 25 percentage points."]},
 "bp1282_0": {"ox": [
  "Correct. The 0-hour row reads 100% viability at 0 µM drug, the highest value in the viability column (100, 85, 70, 55%).",
  "Incorrect. The 24-hour row reads 85% viability, below the 100% at 0 hours; longer exposure lowered it.",
  "Incorrect. The 48-hour row reads 70% viability, below the 100% at 0 hours; it is not the highest value.",
  "Incorrect. The 72-hour value is 55%, the lowest in the table rather than the highest."]},
 "bp1282_1": {"ox": [
  "Incorrect. Adding 96- and 120-hour points under the same stepwise schedule keeps concentration and time rising together, so the confound remains.",
  "Correct. Holding 0, 15, 25 or 35 µM constant in separate wells and reading all of them at one time point removes exposure time, leaving concentration as the difference.",
  "Incorrect. Doubling plating density to 2×10^5 cells per well changes growth conditions but does not separate the rising concentration from the rising exposure time.",
  "Incorrect. A second assay may improve measurement validity, but the table's concentration and time still rise together, so the confound remains."]},
 "bp1282_2": {"ox": [
  "Incorrect. 10 µM is not the mean of the 15 µM and 25 µM rows; (15 + 25) / 2 = 20 µM.",
  "Incorrect. 15 µM is only the 24-hour concentration, one of the two values being averaged.",
  "Correct. The table lists 15 µM at 24 hours and 25 µM at 48 hours, so the mean is (15 + 25) / 2 = 20 µM.",
  "Incorrect. 25 µM is only the 48-hour concentration, not the mean of the two."]},
 "bp1282_3": {"ox": [
  "Incorrect. This is true: viability goes 100, 85, 70 and 55% as concentration rises 0, 15, 25 and 35 µM.",
  "Incorrect. This is true: 55% at 72 hours is the lowest value in the table.",
  "Incorrect. This is true: the 48-hour row lists 25 µM with 70% viability in the table.",
  "Correct. At 0 hours the drug concentration is 0 µM and viability is 100% of the untreated control, not 85%; 85% is the 24-hour value."]},
 "bp1282_4": {"ox": [
  "Incorrect. Pharmacokinetics describes how the body handles a drug (absorption, distribution, clearance), none of which this table measures.",
  "Correct. The table relates drug concentration and exposure time to a cellular response, viability falling 100, 85, 70 and 55%, which is a pharmacodynamic effect.",
  "Incorrect. Clinical trial phases concern testing in humans; these are cultured cells, and the passage describes no trial phase.",
  "Incorrect. Molecular genetics concerns inheritance and gene expression; the passage measures viability, not genetic effects."]},
}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(E, ensure_ascii=False, separators=(",", ":")))
    print("wrote", OUT, len(E), "entries")


if __name__ == "__main__":
    main()
