# Run config snapshot (Week 7 final)

Sources:
- `reports/week7/week7_ablation_spec.json`
- `reports/week7/locked_eval_pack/week7_norm_only/WEEK7_FINAL.md`
- `reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_A_clean_unicode.md` (row: `week7_norm_only` val)

## Model
- Backbone: `microsoft/deberta-v3-base`
- Tokenizer: not specified in sources
- Max length: 256
- LoRA params: not specified in sources

## Training hyperparameters
- Epochs: 3
- Batch size: 16
- Learning rate: 0.0002
- Gradient accumulation: 2
- Seed: 42
- Num workers: 0

## Normalization policy
- normalize_train: true
- normalize_infer: false
- unicode_preprocess: false
- normalize_drop_mn: false

## Augmentation (winner run)
- aug_adv2_prob: 0.0
- aug_rewrite_prob: 0.0
- aug_seed: 42

## Threshold
- val_threshold (week7_norm_only): 0.7340
- Policy: learned on val and transferred unchanged to all test splits

## Protocol
- Script: `scripts/eval_week7_grid.py`
- Splits: val, test_main, test_jbb, test_main_unicode, test_jbb_unicode, test_main_adv2, test_jbb_adv2, test_main_rewrite, test_jbb_rewrite

## Reproducibility notes
- normalize_infer is OFF for locked evaluations
- threshold is fixed from validation for all test splits
