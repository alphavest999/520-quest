#!/usr/bin/env python3
"""Hand-authored Phase 2 batch 12: bp1318, bp1319, bp1320 (15 questions), single-line."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1318_1320.json")

E = {
 "bp1318_0": {"ox": [
  "Incorrect. Bifidobacterium rose rather than fell: the passage reports a 25 % increase in relative abundance, and Table 1 shows 12.5 % for the probiotic row against 10.2 % for placebo.",
  "Correct. The passage reports a 15 % reduction in Proteobacteria, and Table 1 lists 25.5 % in the probiotic row against 29.8 % in the placebo row, so this is the taxon that fell by week 12.",
  "Incorrect. Table 1 has no Firmicutes row and the passage names no Firmicutes figure, so the 15 % decrease it reports cannot refer to this group.",
  "Incorrect. Actinobacteria appear neither in Table 1 nor in the passage text, so no relative abundance change is reported for that group."]},
 "bp1318_1": {"ox": [
  "Correct. The passage states that 120 participants were randomized to probiotic or placebo for 12 weeks, which is a randomized placebo-controlled comparison between the two arms.",
  "Incorrect. A placebo arm is a comparison group, so the design is not single-arm; Table 1 reports the placebo row beside the probiotic row at week 12.",
  "Incorrect. A crossover gives every participant both treatments; here each participant was assigned one of the two for the full 12 weeks.",
  "Incorrect. The placebo arm that received no probiotic is the control group, and its p-value of 0.45 appears in Table 1's placebo row."]},
 "bp1318_2": {"ox": [
  "Incorrect. 1.4 is the absolute gap between 4.9 and 3.5 mg/L, not a percentage; as a share of the placebo value that gap is 28.6 %.",
  "Correct. (4.9 − 3.5) / 4.9 × 100 = 1.4 / 4.9 × 100 = 28.6 %, comparing the week-12 CRP values in the two rows of Table 1.",
  "Incorrect. 30 % is the probiotic group's fall from its own baseline, which the passage reports; it is not a comparison against the placebo row.",
  "Incorrect. 40 % comes from dividing 1.4 by the probiotic value 3.5, but the comparison uses the placebo row as its reference."]},
 "bp1318_3": {"ox": [
  "Incorrect. This is supported: the passage reports a 25 % increase in Bifidobacterium, and Table 1 shows 12.5 % against 10.2 % for placebo.",
  "Incorrect. This is supported: the passage reports a 15 % reduction in Proteobacteria, and Table 1 shows 25.5 % against 29.8 % for placebo.",
  "Incorrect. This is supported: the passage reports a 30 % decrease in serum CRP, and Table 1 shows 3.5 against 4.9 mg/L for placebo.",
  "Correct. The passage lists IL-6 as measured but reports no IL-6 value, so a claimed increase has no figure in Table 1 or in the text behind it."]},
 "bp1318_4": {"ox": [
  "Correct. A p-value of 0.45 in the placebo row sits above the 0.05 cutoff, so no statistically significant change was detected there, unlike the probiotic row's p < 0.01.",
  "Incorrect. A p-value is the probability of data this extreme if the null were true, not the probability that the null hypothesis itself is true; the 0.45 in Table 1 is evidence, not that probability.",
  "Incorrect. The placebo row's p-value describes evidence, not magnitude; a 45 % change would be a size of effect, and no such change is listed in Table 1.",
  "Incorrect. The placebo row carries no information about the probiotic arm, whose own p-value is < 0.01 in Table 1."]},
 "bp1319_0": {"ox": [
  "Incorrect. 450 nm gives 21.6 µmol CO₂ m⁻² s⁻¹, which Table 1 places below the 24.9 measured at 650 nm.",
  "Incorrect. 9.2 µmol CO₂ m⁻² s⁻¹ at 550 nm is the lowest rate in Table 1, not the highest.",
  "Correct. Table 1 lists 24.9 µmol CO₂ m⁻² s⁻¹ at 650 nm, above 21.6 at 450 nm, 12.4 at 700 nm and 9.2 at 550 nm.",
  "Incorrect. 12.4 µmol CO₂ m⁻² s⁻¹ at 700 nm is about half the 24.9 at 650 nm, so it is not the maximum."]},
 "bp1319_1": {"ox": [
  "Correct. The passage states that all four LEDs were run at the same photon flux; if flux varied, a rate difference could reflect the amount of light rather than its wavelength.",
  "Incorrect. Chlorophyll-a is measured after growth (10.9 to 12.5 µg mL⁻¹ in Table 1), so it is a response rather than a variable to hold fixed.",
  "Incorrect. Wavelength is the variable deliberately changed across the four rows of Table 1 (450, 550, 650 and 700 nm).",
  "Incorrect. Photosynthetic rate is the outcome measured in Table 1, so it necessarily differs between treatments."]},
 "bp1319_2": {"ox": [
  "Incorrect. 63.1 % divides the 15.7 increase by the final value 24.9 instead of by the starting value 9.2.",
  "Correct. (24.9 − 9.2) / 9.2 × 100 = 15.7 / 9.2 × 100 = 170.7 %, using the 550 nm and 650 nm rows of Table 1.",
  "Incorrect. 270.7 % is 24.9 / 9.2 expressed as a percent, which is the ratio of the two rates rather than the increase over the starting rate.",
  "Incorrect. 90.0 % matches no ratio in Table 1; the two rates are 9.2 and 24.9, and their increase is 170.7 %."]},
 "bp1319_3": {"ox": [
  "Incorrect. This is accurate: Table 1's highest chlorophyll-a value, 12.5 µg mL⁻¹, is the 650 nm row.",
  "Incorrect. This is accurate: 12.4 at 700 nm is lower than the 21.6 at 450 nm in Table 1.",
  "Correct. The rate does not rise steadily with wavelength: it drops from 21.6 at 450 nm to 9.2 at 550 nm, peaks at 24.9 at 650 nm, then falls to 12.4 at 700 nm.",
  "Incorrect. This is accurate: 9.2 at 550 nm is lower than 21.6 at 450 nm in Table 1."]},
 "bp1319_4": {"ox": [
  "Incorrect. Photoperiodism concerns day length as a timing cue, while the passage varies wavelength at fixed photon flux and has no day-length treatment.",
  "Correct. Table 1 holds photon flux constant and varies wavelength, so the rates 21.6, 9.2, 24.9 and 12.4 show photosynthesis depending on light quality.",
  "Incorrect. Stomatal conductance is not measured; the passage reports CO₂ uptake with no stomatal data in Table 1.",
  "Incorrect. No carbon fixation pathway is measured; the passage reports only CO₂ uptake and chlorophyll-a in Table 1."]},
 "bp1320_0": {"ox": [
  "Incorrect. ROS falls rather than rises: Table 1 gives 1000, 800, 600 and 400 RFU as Antiox-1 goes from 0 to 20 µM.",
  "Correct. Table 1's mean ROS column reads 1000, 800, 600 and 400 RFU at 0, 5, 10 and 20 µM, a fall of 200 RFU at each step.",
  "Incorrect. The values are not equal: 1000, 800, 600 and 400 RFU differ across the four concentration rows of Table 1.",
  "Incorrect. There is no rise at any step; each 5 µM increment lowers mean ROS by 200 RFU (1000 → 800 → 600 → 400)."]},
 "bp1320_1": {"ox": [
  "Correct. The 0 µM row (1000 RFU at 24 h) is untreated cells carried through the same incubation, so any fall below it can be attributed to the compound.",
  "Incorrect. A single 20 µM condition offers no untreated reference, so its 400 RFU cannot be separated from the 24-hour incubation.",
  "Incorrect. One measurement in treated cells gives a value but no baseline row, so a change across the Table 1 concentration series cannot be assessed.",
  "Incorrect. The reference sample is needed to express SOD2 as fold change; it does not establish whether ROS fell because of the compound."]},
 "bp1320_2": {"ox": [
  "Incorrect. 30 % is below the 40 % reduction already present at 10 µM (600 RFU), so a 15 µM point cannot sit lower than that.",
  "Correct. Interpolating halfway between 600 RFU at 10 µM and 400 RFU at 20 µM gives 500 RFU, and (1000 − 500) / 1000 × 100 = 50 %.",
  "Incorrect. 70 % exceeds the 60 % reduction at 20 µM (400 RFU), which no lower concentration can surpass.",
  "Incorrect. 90 % would need 100 RFU, but the lowest value in Table 1 is 400 RFU at 20 µM."]},
 "bp1320_3": {"ox": [
  "Incorrect. This is supported: SOD2 fold change climbs from 1.2 at 0 µM to 3.0 at 20 µM in Table 1.",
  "Incorrect. This is supported: mean ROS falls from 1000 to 400 RFU as concentration rises in Table 1.",
  "Correct. Table 1 holds ROS readings and SOD2 mRNA only, with no assay of chemical scavenging, so the compound neutralizing ROS directly is not shown.",
  "Incorrect. This is supported: SOD2 is an antioxidant enzyme and its mRNA rises from 1.2-fold to 3.0-fold across the rows of Table 1."]},
 "bp1320_4": {"ox": [
  "Correct. Table 1 shows SOD2 mRNA rising 1.2 → 1.8 → 2.4 → 3.0 fold while mean ROS falls 1000 → 800 → 600 → 400 RFU, the pattern the proposal predicts.",
  "Incorrect. ROS did not rise: the column runs 1000, 800, 600 and 400 RFU, falling as concentration increases in Table 1.",
  "Incorrect. SOD2 mRNA rose rather than fell, going from 1.2-fold at 0 µM to 3.0-fold at 20 µM in Table 1.",
  "Incorrect. The SOD2 values are not equal; they are 1.2, 1.8, 2.4 and 3.0 fold across the four rows of Table 1."]},
}

if __name__ == "__main__":
    json.dump(E, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("wrote %s: %d entries" % (OUT, len(E)))
    assert len(E) == 15, len(E)
    for k, v in E.items():
        assert len(v["ox"]) == 4, k
