# Thesis Support Analyses

This folder stores follow-up analyses for the frozen `week7_norm_only` run. The goal is to strengthen the thesis argument without changing the locked Week 7 evidence pack.

## Completed analyses

### 1. Calibration curves and ECE

Source: `reports/thesis_support/calibration/week7_norm_only/`

Key results:

- `val`: `ECE = 0.0065`, `Brier = 0.0133`
- `test_main`: `ECE = 0.0087`, `Brier = 0.0107`
- `test_jbb`: `ECE = 0.3227`, `Brier = 0.3042`
- `test_main_adv2`: `ECE = 0.0536`, `Brier = 0.0587`
- `test_jbb_adv2`: `ECE = 0.4316`, `Brier = 0.4350`

Interpretation:

- Calibration is strong on `val` and `test_main`.
- Calibration degrades sharply on `test_jbb`.
- Calibration is severely broken on `test_jbb_adv2`.
- This supports the thesis claim that high ranking quality does not imply trustworthy thresholded probabilities under shift.

### 2. Threshold-stability sweep

Source: `reports/thesis_support/threshold_sweep/week7_norm_only/`

Sweep settings:

- center threshold: `tau = 0.734039`
- radius: `+-0.12`
- summary deltas reported at `-0.05`, `-0.02`, `0`, `+0.02`, `+0.05`

Key results:

- `test_main` FPR changes only from `0.0324` at `tau - 0.05` to `0.0308` at `tau + 0.05`.
- `test_jbb` FPR remains extreme, changing only from `0.6224` to `0.5714`.
- `test_main_adv2` FPR remains extreme, changing only from `0.6498` to `0.6273`.
- `test_jbb_adv2` FPR remains extreme, changing only from `0.8469` to `0.8367`.

Interpretation:

- The main-distribution operating point is fairly stable locally.
- Under shifted benign distributions, the failure is not fixed by small threshold adjustments.
- This strengthens the thesis argument from "one bad threshold" to "threshold transfer is structurally unstable under shift."

### 3. Benign-heavy calibration sensitivity

Source: `reports/thesis_support/benign_heavy/week7_norm_only/`

Attack prevalence values evaluated on resampled validation negatives:

- `0.495251` (original validation balance)
- `0.20`
- `0.10`
- `0.05`

Key results:

- Mean calibrated threshold rises from `0.7340` at the original validation balance to:
  - `0.7383` at attack prevalence `0.20`
  - `0.7832` at attack prevalence `0.10`
  - `0.8075` at attack prevalence `0.05`
- `test_main` FPR improves only modestly:
  - `0.0311` -> `0.0305` -> `0.0300`
- `test_jbb` FPR improves only modestly:
  - `0.5816` -> `0.5765` -> `0.5653`
- `test_main_adv2` FPR improves, but remains unusable:
  - `0.6403` -> `0.6286` -> `0.6207`
- `test_jbb_adv2` FPR improves, but remains unusable:
  - `0.8469` -> `0.8367` -> `0.8204`
- Higher thresholds trade away some recall:
  - `test_main` TPR drops from `0.9869` to `0.9844`
  - `test_jbb_adv2` TPR drops from `0.8990` to `0.8677`

Interpretation:

- Benign-heavy calibration helps slightly, especially on `adv2`.
- It does not rescue the detector under strong distribution shift.
- This supports the thesis position that calibration priors matter, but the dominant problem is shifted score distributions, not only threshold choice.

### 4. Multi-seed reruns

Source: `reports/thesis_support/multiseed/`

Executed seeds:

- `41`
- `42`
- `43`

Run directories:

- `runs/week7_norm_only_ms_seed41`
- `runs/week7_norm_only_ms_seed42`
- `runs/week7_norm_only_ms_seed43`

Summary source:

- `reports/thesis_support/multiseed/multiseed_summary.csv`
- `reports/thesis_support/multiseed/multiseed_summary.json`

Key results:

- Clean ranking is stable across seeds:
  - `test_main AUROC = 0.99581 +- 0.00042`
  - `test_main AUPRC = 0.99955 +- 0.00005`
- Main-distribution thresholded recall remains high:
  - `test_main TPR@tau = 0.99246 +- 0.00546`
- Main-distribution benign FPR is less stable than the single frozen run suggested:
  - `test_main FPR@tau = 0.04025 +- 0.00890`
- Shifted operating-point behavior is substantially seed-sensitive:
  - `test_jbb FPR@tau = 0.60884 +- 0.10272`
  - `test_main_adv2 FPR@tau = 0.61032 +- 0.18823`
  - `test_jbb_adv2 FPR@tau = 0.69048 +- 0.41290`
  - `test_jbb_adv2 TPR@tau = 0.74411 +- 0.34879`
- The per-seed validation thresholds differ materially even though all satisfy the same validation FPR target:
  - seed `41`: `tau = 0.5199`
  - seed `42`: `tau = 0.7450`
  - seed `43`: `tau = 0.6042`

Interpretation:

- The detector family is stable in threshold-free ranking terms on the main distribution.
- The transferred operating point is not stable across random seeds under shifted evaluation conditions.
- This strengthens the thesis claim: deployment risk comes from threshold-transfer instability, not only from one unlucky frozen run.
- These reruns should be reported as follow-up evidence rather than silently replacing the locked `week7_norm_only` winner.`r`n- They were executed under the current repo code path recorded in the rerun configs (`git_commit = 54b50486...`), while the frozen Week 7 winner was recorded under an earlier commit (`git_commit = 91ae94e3...`).

## Supporting scripts

- `scripts/thesis_evidence.py`
- `scripts/render_thesis_eval_figures.py`

