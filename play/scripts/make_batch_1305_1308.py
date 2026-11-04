#!/usr/bin/env python3
"""Hand-authored Phase 2 batch 10: bp1305, bp1307, bp1308 (15 questions), single-line."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1305_1308.json")

E = {
 "bp1305_0": {"ox": [
  "Incorrect. Heart rate recovery is 17 bpm/min with the supplement against 15 with placebo, so it did change; the statement that it was unaffected is wrong.",
  "Correct. Distance rises from 2950 to 3200 m (+250 m, 8.5%), heart rate recovery from 15 to 17 bpm/min (+2, 13.3%), and lactate is 4.2 versus 4.3 mmol/L, which the passage calls no significant difference.",
  "Incorrect. Lactate is 4.2 mmol/L with the supplement and 4.3 with placebo, a 0.1 difference the passage reports as not significant, so a lactate decrease is not supported.",
  "Incorrect. Both distance (3200 versus 2950 m) and heart rate recovery (17 versus 15 bpm/min) improved with the supplement."]},
 "bp1305_1": {"ox": [
  "Correct. In a crossover each cyclist receives both supplement and placebo in random order with a washout, so each acts as their own control and between-subject variability cannot obscure the table's 3200 versus 2950 m gap.",
  "Incorrect. A cohort of cyclists who choose the supplement invites selection bias, because those who take it may differ from those who do not; the passage assigns the supplement at random.",
  "Incorrect. A case-control study groups cyclists by whether endurance improved, so it cannot assign the supplement before the table's cardiovascular measures are taken.",
  "Incorrect. Qualitative interviews record perceptions, not the cardiovascular measurements in Table 1 that would be needed to test mediation."]},
 "bp1305_2": {"ox": [
  "Incorrect. 2 / 17 × 100 = 11.8%, which divides by the supplement value instead of the placebo reference of 15 bpm/min.",
  "Incorrect. 12.5% would need a denominator of 16; the table gives 15 bpm/min for placebo, so 2 / 15 = 13.3%.",
  "Incorrect. 9.4% matches no pair: 2 / 15 = 13.3% and 2 / 17 = 11.8% are the two percentages available.",
  "Correct. Heart rate recovery is 17 bpm/min with the supplement and 15 with placebo, so (17 - 15) / 15 × 100 = 13.3%."]},
 "bp1305_3": {"ox": [
  "Correct. Lactate is 4.2 mmol/L with the supplement and 4.3 with placebo, and the passage states the difference was not significant, so a significant lactate reduction is not supported.",
  "Incorrect. This is supported: 3200 - 2950 = 250 m greater mean distance in the supplement group.",
  "Incorrect. This is supported: 17 - 15 = 2 bpm/min higher heart rate recovery with the supplement.",
  "Incorrect. This is supported: the passage states 80 participants were divided equally into two groups, so 40 each."]},
 "bp1305_4": {"ox": [
  "Incorrect. 250 / 3200 × 100 = 7.8%, which divides the 250 m gain by the supplement mean instead of the placebo reference.",
  "Correct. The supplement group covers 3200 m against 2950 m for placebo, so (3200 - 2950) / 2950 × 100 = 250 / 2950 × 100 = 8.5%.",
  "Incorrect. 12.5% would need a denominator of 2000 m; the placebo mean in the table is 2950 m.",
  "Incorrect. 15.5% would need a denominator near 1613 m; the table's placebo mean is 2950 m."]},
 "bp1307_0": {"ox": [
  "Incorrect. The placebo row reads a 5 mmHg change from baseline, the smallest reduction in the table.",
  "Correct. The change column reads 5 mmHg (placebo), 16 mmHg (Drug A) and 12 mmHg (Drug B), so Drug A has the greatest mean reduction.",
  "Incorrect. Drug B falls 12 mmHg (147 to 135), which is less than Drug A's 16 mmHg (146 to 130).",
  "Incorrect. All three groups fall, by 5, 16 and 12 mmHg, so the reduction is not absent."]},
 "bp1307_1": {"ox": [
  "Incorrect. A cross-sectional study measures one time point; the passage measures SBP at baseline and after 4 weeks of assigned treatment.",
  "Incorrect. A case-control study groups people by an outcome that already occurred; the passage assigns treatment before the 4-week SBP change in the table is measured.",
  "Correct. The passage describes random assignment to placebo, Drug A or Drug B with double blinding, which is the design that balances confounders.",
  "Incorrect. A cohort study follows people without random assignment; the passage assigns the treatment at random."]},
 "bp1307_2": {"ox": [
  "Incorrect. 8% of the 146 mmHg baseline is 11.7 mmHg; the Drug A fall is 16 mmHg.",
  "Incorrect. 10% of 146 mmHg is 14.6 mmHg; the table shows a 16 mmHg fall.",
  "Correct. Drug A falls from 146 to 130 mmHg, a 16 mmHg drop, and 16 / 146 × 100 = 10.96%, which rounds to 11%.",
  "Incorrect. 12% is close to 16 / 130 = 12.3%, which divides by the week-4 value instead of the 146 mmHg baseline."]},
 "bp1307_3": {"ox": [
  "Incorrect. This is supported: Drug A falls 16 mmHg against 12 mmHg for Drug B.",
  "Incorrect. This is supported: Drug B falls 12 mmHg against 5 mmHg for placebo.",
  "Incorrect. This is supported: the within-group p-values are 0.001 for Drug A and 0.003 for Drug B.",
  "Correct. The passage reports a mild headache in 5% of Drug A participants and no serious events in any group, so it does not show adverse events were more common with placebo."]},
 "bp1307_4": {"ox": [
  "Correct. p = 0.08 is above the 0.05 threshold, so the 5 mmHg placebo change is not statistically significant and chance cannot be excluded.",
  "Incorrect. A p-value is the probability of data this extreme if the null hypothesis is true, not the probability that the placebo lowers blood pressure; the table's p = 0.08 says only that the 5 mmHg change is not significant.",
  "Incorrect. p = 0.08 fails to show significance; it does not prove the placebo has no effect.",
  "Incorrect. The placebo change is 5 mmHg and the Drug A change is 16 mmHg, so the placebo reduction is smaller."]},
 "bp1308_0": {"ox": [
  "Incorrect. 0.9 µmol/L is the control-versus-experimental gap on day 3, not a rise within the experimental group.",
  "Correct. Experimental MDA falls from 4.1 µmol/L on day 0 to 2.1 µmol/L on day 7, a decrease of 4.1 - 2.1 = 2.0 µmol/L.",
  "Incorrect. The experimental mean falls from 4.1 to 2.1 µmol/L, so it did not remain unchanged.",
  "Incorrect. 0.1 µmol/L is the day-0 control-versus-experimental gap, not the change within the experimental group."]},
 "bp1308_1": {"ox": [
  "Incorrect. A higher dose of the antioxidant is another active arm; it does not supply the no-antioxidant comparison behind Table 1's MDA values.",
  "Incorrect. Antioxidant without the diet removes the diet itself; the passage's intervention is the supplement added to a standard diet.",
  "Correct. The passage's control group receives the standard diet without the antioxidant, which is what allows differences in MDA to be attributed to the supplement.",
  "Incorrect. A placebo pill is irrelevant because the passage's intervention is dietary supplementation, not an oral medication."]},
 "bp1308_2": {"ox": [
  "Correct. Experimental MDA falls from 4.1 to 2.1 µmol/L, a 2.0 µmol/L drop, and 2.0 / 4.1 × 100 = 48.8%.",
  "Incorrect. 50% would need a fall of 2.05 µmol/L on the 4.1 baseline; the table shows a fall of 2.0.",
  "Incorrect. 60% would need a fall of 2.46 µmol/L; the experimental mean falls 2.0 µmol/L by day 7.",
  "Incorrect. 70% would need a fall of 2.87 µmol/L; the observed fall is 2.0 µmol/L."]},
 "bp1308_3": {"ox": [
  "Incorrect. This is supported: on day 3 the experimental mean is 3.0 µmol/L against 3.9 for control.",
  "Correct. The study used mice and measured a biomarker only (Table 1's MDA values), so clinical benefit in humans with age-related diseases is not supported by the data.",
  "Incorrect. This is supported: the control mean drifts only from 4.0 to 3.6 µmol/L over 14 days.",
  "Incorrect. This is supported: the experimental means are 4.1, 3.0, 2.1, 1.8 and 1.5 µmol/L, a steady fall."]},
 "bp1308_4": {"ox": [
  "Incorrect. Only Table 1's MDA biomarker was measured in mice, so the study cannot show that antioxidants cure all age-related diseases.",
  "Correct. In adult mice a 0.5% dietary antioxidant lowered plasma MDA, a lipid peroxidation marker, from 4.1 to 1.5 µmol/L over 14 days, but aging and disease outcomes were not measured.",
  "Incorrect. The passage tested diet against an MDA biomarker, not aging outcomes, so it cannot prove diet has no impact on aging.",
  "Incorrect. The passage did not measure aging outcomes, so Table 1 cannot show that oxidative stress is irrelevant to aging."]},
}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(E, ensure_ascii=False, separators=(",", ":")))
    print("wrote", OUT, len(E), "entries")


if __name__ == "__main__":
    main()
