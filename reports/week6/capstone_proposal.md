# Capstone Project Proposal

## Problem statement + motivation
Prompt injection and jailbreaks threaten safe deployment of LLMs; we need a robust detector that generalizes across obfuscation and domain shifts.

## Dataset description
- clean: v1 (val, test_main, test_jbb)
- unicode_adv: v1_adv (test_main_unicode, test_jbb_unicode)
- adv2: v1_adv2 (stronger obfuscation)
- rewrite: v1_rewrite (word-level paraphrase)

## Method
- Baseline: rules-based detector
- Model: LoRA fine-tuned transformer (microsoft/deberta-v3-base)
- Robustness: train-time normalization + augmentation (adv2, rewrite)

## Metrics
- AUROC, AUPRC
- Operating point: FPR@val_threshold, TPR@val_threshold
- ASR@threshold: fraction of attacks not flagged (false negatives); lower is better

## Week-by-week plan
- Week 4: final backbone + baseline performance locked
- Week 5: robustness evaluation (adv2), calibration + mitigation analysis
- Week 6: train-time robustness + rewrite perturbation family
- Next: finalize ablations, calibrations, and thesis-ready reporting

## Completed
- Reproducible evaluation grid (clean/unicode/adv2/rewrite)
- Two perturbation families (unicode/adv2 + rewrite)
- Train-time robustness ablations (norm-train / adv2-train / both)
- Thesis evidence pack (tables + plots + error cases)

## Next (Week 7 / finalization)
- Pick final model (Week 6 winner)
- Run a locked eval pack + tag
- Write thesis chapters (method, experiments, robustness, limitations)

## Outputs
- Ablations: with vs without Unicode preprocessing; with vs without adversarial augmentation
- Results notebook: tables + plots for thesis reuse

## Risks + mitigation
- Distribution shift (JBB / adv2): use train-time augmentation and re-evaluate transfer
- Threshold transfer failure: calibrate on validation and report operating-point trade-offs
- Overfitting to perturbations: keep minimal ablations and compare across families
