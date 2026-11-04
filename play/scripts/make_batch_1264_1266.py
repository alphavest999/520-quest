#!/usr/bin/env python3
"""Hand-authored Phase 2 batch 2: bp1264-bp1266 (15 questions), single-line output."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1264_1266.json")

E = {
 "bp1264_0": {"ox": [
  "Incorrect. No cell in Table 1 equals 5.2×10⁶; the day-7 row reads 1.1×10⁷ CFU/mL untreated and 4.0×10⁵ CFU/mL treated.",
  "Correct. The day-7 row of Table 1 lists 4.0×10⁵ CFU/mL for the treated group, against 1.1×10⁷ CFU/mL for the untreated group.",
  "Incorrect. 3.4×10⁵ resembles the untreated day-14 count of 3.4×10⁷, which is two orders of magnitude larger and belongs to a different column and day.",
  "Incorrect. No cell equals 8.9×10⁶; the largest treated value is 2.5×10⁶ on day 3, and the day-7 untreated value is 1.1×10⁷."]},
 "bp1264_1": {"ox": [
  "Correct. The passage describes two groups: one receiving 10 µg/mL of the antibiotic and an untreated control, so the control is bacteria given no antibiotic.",
  "Incorrect. The passage never mentions a placebo compound; it describes an untreated control group.",
  "Incorrect. No comparator antibiotic appears in the passage, which tests only the novel antibiotic against no treatment.",
  "Incorrect. Only one concentration, 10 µg/mL, is tested, so no higher-dose control group exists."]},
 "bp1264_2": {"ox": [
  "Incorrect. 15% per day would compound to a much smaller 4-day factor than the 2.75-fold the passage reports (1.1×10⁷ ÷ 4.0×10⁶).",
  "Correct. The counts rise from 4.0×10⁶ on day 3 to 1.1×10⁷ on day 7, a 2.75-fold increase, which the passage states corresponds to about a 29% increase per day.",
  "Incorrect. 35% per day does not match the passage's stated 29% per day for the 2.75-fold rise over the four days from day 3 to day 7.",
  "Incorrect. 45% per day would compound far beyond the 2.75-fold rise (1.1×10⁷ ÷ 4.0×10⁶) that the passage reports across those four days."]},
 "bp1264_3": {"ox": [
  "Incorrect. This statement is supported: the treated count falls from 1.0×10⁶ at day 0 to 4.0×10⁵ by day 7, a reduction.",
  "Incorrect. This statement is supported: the untreated count rises from 1.0×10⁶ at day 0 to 3.4×10⁷ by day 14.",
  "Correct. The treated count falls from 1.0×10⁶ to 4.0×10⁵ by day 7 and to 5.0×10³ by day 14, so \"no effect\" contradicts the table and is the statement not supported.",
  "Incorrect. This statement is supported: on day 7 the treated count is 4.0×10⁵ and the untreated count is 1.1×10⁷."]},
 "bp1264_4": {"ox": [
  "Correct. The treated count starts at 1.0×10⁶ and is 4.0×10⁵ by day 7, below its starting value, while the untreated count rises from 1.0×10⁶ to 1.1×10⁷ over the same days.",
  "Incorrect. The treated count at day 14 is 5.0×10³ CFU/mL, not zero, so the table does not show complete elimination.",
  "Incorrect. The treated count rises from 1.0×10⁶ at day 0 to 2.5×10⁶ at day 3, so it did increase at an early sampling time.",
  "Incorrect. The untreated count rises from 1.0×10⁶ at day 0 to 3.4×10⁷ at day 14, a 34-fold increase, not a constant level."]},
 "bp1265_0": {"ox": [
  "Incorrect. The supplement column falls at every visit, 132, 128, 124 and 120 mmHg; it never increases.",
  "Incorrect. The supplement mean never returns to baseline: 120 mmHg at week 12 is below the 132 mmHg baseline, and each visit is lower than the one before.",
  "Correct. The supplement column reads 132 at baseline, 128 at week 4, 124 at week 8 and 120 at week 12, a progressive 12 mmHg fall to week 12.",
  "Incorrect. The supplement mean changes by 12 mmHg (132 to 120), so it was not unchanged; the nearly flat column is the placebo group (131 to 128)."]},
 "bp1265_1": {"ox": [
  "Incorrect. A cross-sectional survey measures one point in time; the passage measures SBP at baseline, week 4, week 8 and week 12 after assignment.",
  "Correct. The passage describes a randomized, double-blind, placebo-controlled trial with 60 participants per arm, which supports a causal reading of the supplement's effect.",
  "Incorrect. A case-control study selects people by whether they already have an outcome; in the passage participants are assigned to supplement or placebo first and SBP is then followed over 12 weeks.",
  "Incorrect. A cohort study follows participants who chose their exposure; in the passage the intervention was assigned and blinded, not self-selected."]},
 "bp1265_2": {"ox": [
  "Correct. The supplement mean falls from 132 to 120 mmHg, a 12 mmHg drop. Percent reduction = 12 / 132 × 100 = 9.09%, which rounds to 9.1%.",
  "Incorrect. 12 / 132 × 100 = 9.1%; 10.5% would need a baseline near 114 mmHg, and the table's baseline is 132.",
  "Incorrect. 12.0% is the raw 12 mmHg fall with a percent sign attached; 12 mmHg out of 132 mmHg is 9.1%.",
  "Incorrect. 15.4% would need a baseline near 78 mmHg (12 / 78), far below the 132 mmHg the table reports."]},
 "bp1265_3": {"ox": [
  "Incorrect. This is an accurate reading: at week 12 the supplement mean is 120 mmHg and the placebo mean is 128 mmHg.",
  "Incorrect. This is an accurate reading: the placebo change column reads 0, -1, -2 and -3 mmHg, ending at a 3 mmHg fall.",
  "Correct. The supplement group fell 12 mmHg and the placebo group fell 3 mmHg, so only the 9 mmHg excess over placebo can be attributed to the supplement; treating the whole 12 mmHg as the supplement's doing is the misconception.",
  "Incorrect. This is an accurate reading: the passage states that the researchers recorded adverse events and compliance rates."]},
 "bp1265_4": {"ox": [
  "Incorrect. 3 mmHg is the placebo group's own fall (131 to 128), which is the comparison, not the excess.",
  "Correct. The supplement fell 12 mmHg (132 to 120) and the placebo fell 3 mmHg (131 to 128), so the supplement's fall exceeded placebo by 12 - 3 = 9 mmHg.",
  "Incorrect. 12 mmHg is the supplement group's whole fall, which includes the 3 mmHg shared with placebo; the excess is 9 mmHg.",
  "Incorrect. 15 mmHg is 12 + 3, adding the two falls instead of subtracting the placebo fall from the supplement fall."]},
 "bp1266_0": {"ox": [
  "Incorrect. Placebo falls from 150 to 148 mmHg, a 2 mmHg reduction, the smallest in the table.",
  "Incorrect. Low-dose falls from 149 to 140 mmHg, a 9 mmHg reduction, well below the high-dose fall.",
  "Incorrect. Medium-dose falls from 151 to 130 mmHg, a 21 mmHg reduction; the high dose falls further.",
  "Correct. High-dose falls from 152 to 120 mmHg, a 152 - 120 = 32 mmHg reduction, the largest of the four groups (2, 9, 21 and 32 mmHg)."]},
 "bp1266_1": {"ox": [
  "Correct. The placebo group shows the 2 mmHg change that occurs without the drug (150 to 148), so subtracting it isolates the drug's effect.",
  "Incorrect. A high-dose arm shows that the effect grows with dose; it does not measure the non-drug change that the placebo arm captures.",
  "Incorrect. The passage notes a 5-minute seated rest before each reading, which standardizes measurement conditions; it does not estimate how SBP drifts without treatment.",
  "Incorrect. The 4-week follow-up sets when SBP is re-measured, not how much it changes without the drug."]},
 "bp1266_2": {"ox": [
  "Incorrect. 10 mmHg matches no row: the medium-dose baseline is 151 and its week-4 value is 130, a 21 mmHg difference.",
  "Incorrect. 20 mmHg would come from 150 - 130, mixing the placebo baseline with the medium-dose week-4 value.",
  "Correct. The medium-dose row reads 151 mmHg at baseline and 130 mmHg at week 4, so the reduction is 151 - 130 = 21 mmHg.",
  "Incorrect. 25 mmHg would need a week-4 value of 126 mmHg; the table gives 130 for the medium dose."]},
 "bp1266_3": {"ox": [
  "Incorrect. The placebo baseline is 150 mmHg, below the high-dose baseline of 152 mmHg.",
  "Incorrect. The low-dose baseline is 149 mmHg, the lowest of the four baselines.",
  "Incorrect. The medium-dose baseline is 151 mmHg, one mmHg below the high-dose baseline of 152 mmHg.",
  "Correct. The baseline column reads 150 (placebo), 149 (low), 151 (medium) and 152 (high) mmHg, so the high-dose group has the highest baseline pressure."]},
 "bp1266_4": {"ox": [
  "Correct. The reductions are ordered by dose (2, 9, 21 and 32 mmHg), so a test for linear trend or regression of SBP change on dose uses the dose gradient directly.",
  "Incorrect. A paired t-test inside the placebo group compares baseline with week 4 in one arm; it never uses the four dose levels and cannot test a dose trend.",
  "Incorrect. A chi-square test on baseline SBP treats counts in categories and ignores the ordered dose-response in the change column.",
  "Incorrect. Correlating baseline SBP with age uses the baseline column and ignores the dose levels, so it cannot test whether the table's change column rises with dose."]},
}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(E, ensure_ascii=False, separators=(",", ":")))
    print("wrote", OUT, len(E), "entries")


if __name__ == "__main__":
    main()
