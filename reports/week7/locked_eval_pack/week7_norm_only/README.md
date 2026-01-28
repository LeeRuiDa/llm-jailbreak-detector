# Week 7 Locked Eval Pack (Final)

This directory contains the Week 7 final, locked evaluation outputs for the thesis. It captures the agreed protocol and aggregate results without exposing raw data, prompts, or model checkpoints.

## Directory map
- `tables/`: results tables (A–D), long metrics, rules baseline table, and other aggregate summaries.
- `figures/`: ROC curves and score histograms used in the thesis.
- `error_cases/`: false-positive/false-negative example lists (aggregated case files).
- `ENV.txt`: environment snapshot from the evaluation environment.
- `DATA_STATS.md` / `DATA_STATS.json`: aggregate-only dataset statistics (counts and class balance).

## Protocol summary
- `normalize_infer` is OFF for all locked evaluations.
- `val_threshold` is chosen on the validation split and applied unchanged to all test splits.
- Metrics reported: AUROC, AUPRC, FPR@val_threshold, TPR@val_threshold, ASR@threshold.

## Final selection
- Winner: `week7_norm_only` (see `WEEK7_FINAL.md` in this directory).

## Reproduction pointers
- `scripts/eval_week7_grid.py`
- `scripts/lock_week7_eval_pack.py`
- `scripts/prep_thesis_ingredients.ps1` / `scripts/prep_thesis_ingredients.sh`

## Not committed
- Raw datasets under `data/`
- Run directories under `runs/`
- Model weights or prediction dumps

## Optional artifacts
- Confusion-matrix counts at the operating threshold are optional and may be generated locally if run artifacts are available. They are not included by default.
