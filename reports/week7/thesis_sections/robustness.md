# Robustness

## Threshold transfer
- Threshold is fixed from val and transferred to all splits with normalize_infer OFF.
- Normalization-only improves transfer modestly on adv2 (mean adv2 FPR 0.7903 -> 0.7436) with limited TPR loss (0.9613 -> 0.9478).
- Adv2 augmentation drives large adv2 FPR reductions (0.7903 -> 0.3809 / 0.3178) but causes sizable recall drops on JBB adv2 (TPR 0.9495 -> 0.7677 / 0.6768).
- Clean/unicode performance is most stable under normalization-only; adv2 augmentation raises clean/unicode FPRs.

## Failure modes (adv2)
- High-scoring false positives in mixed-script or noisy prompts
- False negatives where obfuscation hides attack intent

## Failure modes (rewrite)
- Paraphrases that reduce explicit harm cues
- Benign-looking lead-ins that dilute attack tokens

## Representative examples
- Adv2 FPs/FNs: `reports/week7/error_cases/week7_norm_only/test_main_adv2_fp.md`, `reports/week7/error_cases/week7_norm_only/test_main_adv2_fn.md`
- JBB adv2 FNs: `reports/week7/error_cases/week7_norm_only/test_jbb_adv2_fn.md`
- Rewrite FPs/FNs: `reports/week7/error_cases/week7_norm_only/test_main_rewrite_fp.md`, `reports/week7/error_cases/week7_norm_only/test_main_rewrite_fn.md`
