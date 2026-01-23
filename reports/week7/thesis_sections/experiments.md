# Experiments

## Splits
- val, test_main, test_jbb
- test_main_unicode, test_jbb_unicode
- test_main_adv2, test_jbb_adv2
- test_main_rewrite, test_jbb_rewrite

## Metrics
- AUROC, AUPRC
- FPR@val_threshold, TPR@val_threshold, ASR@threshold

## Operating point
- Threshold learned from val (target FPR=1%) and reused across all splits
- Score orientation locked via val-derived transform

## Ablation design
- 2x2 factorial: normalize_train (off/on) x adv2 augmentation (off/on)
- All other hyperparameters fixed; rewrite augmentation disabled during training
