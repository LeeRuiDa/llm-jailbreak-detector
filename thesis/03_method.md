# Method

## Task and labels
This work treats guardrail detection as a binary classification task over user prompts.
The positive class is attack (harmful or policy-violating request) and the negative class is benign.

## Model
Backbone: DeBERTa v3 base with a LoRA adapter (r=8, alpha=16, dropout=0.05) and a binary classification head.

## Training recipe
All Week 5-7 runs use the same training recipe as the Week 4 baseline (v0.3-week4), with hyperparameters locked.

## Normalization
Training-time normalization applies Unicode NFKC and drops Cf characters.
For the final model (week7_norm_only), normalize_train is enabled while normalize_infer is OFF for all evaluations.

## Perturbations
- unicode_adv: Unicode mixing applied to evaluation splits to test normalization robustness.
- adv2: character-level perturbations (homoglyphs, mixed-script, noise) used for robustness evaluation and optional train-time augmentation.
- rewrite: light paraphrases (synonyms, fillers, minor reordering) used for evaluation; train-time rewrite augmentation is OFF in Week 7.

## Evaluation protocol
- Fixed evaluation grid across val and all test splits.
- Threshold is learned on val (val_threshold in run config.json) and transferred unchanged to every split.
- Metrics reported: AUROC, AUPRC, FPR@val_threshold, TPR@val_threshold, ASR@threshold.

## Terminology + metrics
- FPR@threshold: false positives among benign at the transferred threshold.
- TPR@threshold: true positives among attacks at the transferred threshold.
- ASR@threshold: false negatives on attacks (attack success rate) at the transferred threshold; lower is better.
