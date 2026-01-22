# Week 6 Experiment Plan

## Goal
Train-time robustness for adv2 and rewrite perturbations with a minimal ablation set.

## Fixed backbone and settings
- Backbone: microsoft/deberta-v3-base
- LoRA config: same as Week 4 final
- Target FPR: 1% for val threshold

## Perturbation families
- Family A: unicode/adv2 (existing)
- Family B: rewrite (new)

## Datasets (evaluation)
- clean: val, test_main, test_jbb
- unicode_adv: test_main_unicode, test_jbb_unicode
- adv2: test_main_adv2, test_jbb_adv2
- rewrite: test_main_rewrite, test_jbb_rewrite

## Ablation runs (no grid explosion)
1) baseline (Week 4 final)
2) +norm-train
3) +adv2-train
4) +both (norm-train + adv2-train)

## Training flags (new)
- --normalize_train (optional)
- --normalize_drop_mn (optional)
- --aug_adv2_prob <0.0-0.5>
- --aug_rewrite_prob <0.0-0.5>
- --aug_seed <int>

## Evaluation pipeline
Use `scripts/eval_week6_grid.py` to generate:
- predictions_*.jsonl, final_metrics_*.json
- plots + error cases
- tables: A (clean/unicode), B (adv2/rewrite), ablation summary

## Reproduce Week 6 tables
```bash
python scripts/eval_week6_grid.py --run_dir runs/<RUN>
python scripts/build_week6_tables.py
```
Outputs:
- reports/week6/week6_table_A_clean_unicode.md
- reports/week6/week6_table_B_adv2_rewrite.md
- reports/week6/week6_table_C_threshold_transfer.md
- reports/week6/week6_ablation_summary.md
