#!/usr/bin/env python3
"""Hand-authored Phase 2 batch 19: bp1344, bp1345, bp1347 (15 questions), single-line."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "json", "phase2", "batch_1344_1347.json")

E = {
 "bp1344_0": {"ox": [
  "Incorrect. The change keeps growing past the low dose, from -7 mmHg at 10 mg to -12 at 20 mg and -15 at 40 mg, so it does not level off there.",
  "Correct. The change grows from -7 to -12 to -15 mmHg, but the gain per mg falls: 5 mmHg over the first 10 mg step against 3 mmHg over the last 20 mg step.",
  "Incorrect. No significance tests appear in the passage or Table 1, and every active dose beat placebo's -2 mmHg.",
  "Incorrect. The active rows differ, -7, -12 and -15 mmHg, so the reductions are not similar across doses."]},
 "bp1344_1": {"ox": [
  "Correct. Random assignment of 20 participants to each of the four groups balances known and unknown confounders, which is what lets the change column be attributed to Hypertensol.",
  "Incorrect. A 12-week period sets how long the effect is followed but does not make the groups comparable at baseline.",
  "Incorrect. A 5-minute seated rest standardizes each reading but does not equalize the groups.",
  "Incorrect. Three centres widen the sample but add site-to-site variation rather than controlling it, and Table 1's 20 participants per group is unchanged by recruiting sites."]},
 "bp1344_2": {"ox": [
  "Correct. -15 - (-2) = 13 mmHg, the high-dose change set against the placebo change in Table 1.",
  "Incorrect. 15 mmHg is the high-dose change alone, before the -2 mmHg placebo fall is subtracted.",
  "Incorrect. 17 mmHg adds the placebo decline (15 + 2) instead of subtracting it.",
  "Incorrect. 12 mmHg is the medium-dose change, not the high dose against placebo."]},
 "bp1344_3": {"ox": [
  "Incorrect. This is supported: the high-dose change of -15 mmHg is the largest in Table 1.",
  "Incorrect. This is supported: the placebo row falls from 148 to 146 mmHg, a change of -2.",
  "Correct. The passage says diastolic BP was collected but reports no diastolic result anywhere in Table 1, so a fall in all three active groups is unsupported.",
  "Incorrect. This is supported: the passage states patients were treated for 12 weeks before SBP was reassessed."]},
 "bp1344_4": {"ox": [
  "Correct. 15 - 12 = 3 mmHg extra over the 20 mg step from 20 mg to 40 mg, so 3/20 = 0.15 mmHg per mg.",
  "Incorrect. 0.5 mmHg per mg is the low-to-medium interval, a 5 mmHg difference over 10 mg.",
  "Incorrect. 0.3 divides the 3 mmHg increment by 10 mg rather than by the actual 20 mg interval.",
  "Incorrect. 0.38 divides the whole 15 mmHg high-dose change by 40 mg instead of using the increment between doses."]},
 "bp1345_0": {"ox": [
  "Incorrect. The 10 mg row reads 5.0 mmHg with SD 3.2, the smallest reduction in Table 1.",
  "Incorrect. The 20 mg row reads 8.5 mmHg, below the 30 mg value of 12.0.",
  "Correct. The 30 mg row reads 12.0 mmHg with SD 4.0, the largest mean reduction, above the 40 mg row's 10.5.",
  "Incorrect. The 40 mg row reads 10.5 mmHg with SD 5.5, a smaller mean than the 30 mg row despite the higher dose."]},
 "bp1345_1": {"ox": [
  "Correct. The passage describes the trial as double-blind, so investigators recording blood pressure do not know each participant's dose and their expectations cannot bias the reading.",
  "Incorrect. A baseline reading allows the change in Table 1 to be calculated but reveals nothing about which of the four doses was assigned.",
  "Incorrect. Four dose groups permit the 5.0 to 12.0 mmHg comparison in Table 1 but do not conceal assignment from the observer.",
  "Incorrect. A 4-week period sets duration and does nothing about observer expectations."]},
 "bp1345_2": {"ox": [
  "Correct. SE = 4/7.07 = 0.566 mmHg, with 7.07 x 7.07 = 50, so the 95% interval is 12 ± 1.96 x 0.566 = 12 ± 1.11, or 10.9 to 13.1 mmHg.",
  "Incorrect. 11.4 to 12.6 spans about ±0.57 mmHg, one standard error, which is roughly a 68% interval.",
  "Incorrect. 10 to 14 spans ±2 mmHg, wider than the ±1.11 that 1.96 standard errors give.",
  "Incorrect. 9 to 15 spans ±3 mmHg, far wider than ±1.11 and close to the SD of 4 itself."]},
 "bp1345_3": {"ox": [
  "Incorrect. This is supported: 12.0 mmHg at 30 mg is the largest reduction in Table 1.",
  "Incorrect. This is supported: 5.0 mmHg at 10 mg is the smallest reduction in Table 1.",
  "Incorrect. This is supported: the 40 mg SD of 5.5 is the largest in Table 1.",
  "Correct. The 10 mg row reads a 5.0 mmHg reduction with SD 3.2, so that group did respond; 'no reduction' contradicts the table."]},
 "bp1345_4": {"ox": [
  "Incorrect. Pharmacokinetics covers absorption, distribution, metabolism and excretion, not how a given dose becomes an effect, which is what the 5.0 to 12.0 mmHg rise in Table 1 shows.",
  "Correct. A dose-response curve of 5.0, 8.5, 12.0 and 10.5 mmHg is a pharmacodynamic relationship: how the drug's concentration at its target changes the response.",
  "Incorrect. Toxicology concerns adverse effects, and the passage reports only SBP reductions and SDs in Table 1.",
  "Incorrect. Trial phases describe stages of drug development, not the shape of the dose-response relation in Table 1."]},
 "bp1347_0": {"ox": [
  "Incorrect. 75% would mean a quarter lost in 60 minutes, a linear guess; Table 1 falls 100 to 50 at 30 min and to 25 at 60 min, halving every 30 minutes.",
  "Incorrect. 50% is the 30-minute row, one half-life, not the 60-minute row.",
  "Correct. The 60-minute row of Table 1 reads 25%, two half-lives after the 100% starting value (100 to 50 to 25).",
  "Incorrect. 12.5% is the 90-minute row of Table 1, three half-lives after the 100% starting value."]},
 "bp1347_1": {"ox": [
  "Incorrect. Cycloheximide inhibits translation elongation, as the passage states, so it lowers rather than raises new protein production.",
  "Correct. The passage states cycloheximide blocks translation elongation, so no new IκBα is made and the fall from the 100% band at time 0 reflects decay of the existing pool.",
  "Incorrect. It does not speed degradation; the halving to 50% at 30 minutes in Table 1 is the protein's own turnover.",
  "Incorrect. Detection comes from the antibody the passage describes after SDS-PAGE, not from cycloheximide."]},
 "bp1347_2": {"ox": [
  "Incorrect. 1.562% is six half-lives, 100 x (1/2)^6, one more than 150 minutes allows.",
  "Correct. 150 minutes is five 30-minute half-lives, so 100 x (1/2)^5 = 3.125%, continuing the halving from 100 to 50 to 25 to 12.5 in Table 1.",
  "Incorrect. 6.25% is four half-lives, the value 120 minutes would give.",
  "Incorrect. 96.875% is the fraction lost, 1 - 0.03125, not the fraction remaining."]},
 "bp1347_3": {"ox": [
  "Incorrect. This is correct: t½ = ln 2/k is the relation for first-order decay.",
  "Correct. First-order decay has t½ = ln 2/k, which contains no starting amount, so the constant 30-minute halving from 100 to 50 to 25% in Table 1 would not slow with more protein; this statement is the incorrect one.",
  "Incorrect. This is correct: independence from starting concentration is what makes first-order decay exponential, as the constant ratio between Table 1's rows shows.",
  "Incorrect. This is correct: first-order rate is proportional to the amount remaining, which is why each 30 minutes removes half."]},
 "bp1347_4": {"ox": [
  "Incorrect. Phosphorylation by glycolytic kinases does not target proteins for secretion, and the decay in Table 1 is intracellular.",
  "Correct. Polyubiquitin tagging sends short-lived regulators to the proteasome, which is the route the passage tests when it asks whether proteasome inhibition would stabilize IκBα.",
  "Incorrect. Glycosylation in the Golgi does not prevent degradation, and the 30-minute half-life in Table 1 is far faster than Golgi processing.",
  "Incorrect. Lysosomes degrade bulk material, not the ribosome, and the passage's stabilization question is about the proteasome."]},
}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(E, ensure_ascii=False, separators=(",", ":")))
    print("wrote", OUT, len(E), "entries")


if __name__ == "__main__":
    main()
