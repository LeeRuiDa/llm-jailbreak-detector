# Week 7 Experiment Plan

## Goal
Isolate which factors matter for robustness: training-time normalization and adv2 augmentation, evaluated on a locked split grid.

## Factors (2x2)
- A: normalize_train (off/on)
- B: adv2 augmentation (off/on, prob=0.25)

## Fixed settings
- Backbone: microsoft/deberta-v3-base
- aug_rewrite_prob: 0.0 (rewrite is evaluation-only in Week 7)
- aug_seed: 42
- normalize_infer: OFF for all evals

## Runs (from spec)
See reports/week7/week7_ablation_spec.json for the 4 core runs.

## Evaluation grid (locked)
Splits: val, test_main, test_jbb, test_main_unicode, test_jbb_unicode, test_main_adv2, test_jbb_adv2, test_main_rewrite, test_jbb_rewrite

## Repro commands
### Train ablations
```bash
python scripts/run_week7_ablations.py --spec reports/week7/week7_ablation_spec.json
```

### Evaluate locked grid
```bash
python scripts/eval_week7_grid.py
```

### Build tables
```bash
python scripts/build_week7_tables.py --metrics_root reports/week7/metrics --out_dir reports/week7/results --runs_root runs
```

### Lock eval pack + tag
```bash
python scripts/lock_week7_eval_pack.py --run_id week7_norm_only --rationale "Norm-only improves adv2 FPR without recall collapse." --overwrite
```
Then tag the commit:
```bash
git tag -a week7-locked-eval-norm-only -m "Week 7 locked eval pack (norm-only)"
```
