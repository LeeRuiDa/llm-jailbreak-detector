# Week 7 Report Draft

## 1. Objective (Week 7)
Prove which training-time factors matter by isolating normalization and adv2 augmentation in a 2x2 ablation.

## 2. What changed from Week 6
- Week 6: train-time robustness ablations, winner selected.
- Week 7: controlled ablation to attribute gains to normalization vs adv2 augmentation.

## 3. Factors under test
- normalize_train (Unicode normalization + Cf removal during training)
- adv2 augmentation (prob=0.25)

## 4. Ablation grid (fixed)
- control: normalize_train=false, adv2_prob=0.0
- norm_only: normalize_train=true, adv2_prob=0.0
- adv2_only: normalize_train=false, adv2_prob=0.25
- norm_plus_adv2: normalize_train=true, adv2_prob=0.25

## 5. Evaluation protocol
- Splits: val, test_main, test_jbb, test_main_unicode, test_jbb_unicode, test_main_adv2, test_jbb_adv2, test_main_rewrite, test_jbb_rewrite.
- Use val_threshold from run config (score orientation locked).
- Metrics: AUROC, AUPRC, FPR@val_threshold, TPR@val_threshold, ASR@threshold.
- Inference normalization: OFF for all runs.

## 6. Tables
- Table A: clean + unicode
- Table B: adv2 + rewrite
- Table C: threshold transfer
- Table D: ablation effects (delta vs control by group)

## 7. Key findings (draft)
- Normalization-only improves robustness without harming clean/unicode: mean FPR drops on unicode (-0.0252) and rewrite (-0.0156) with near-flat TPR, while clean shifts are negligible (Table D).
- Adv2 augmentation sharply reduces adv2 FPR (control 0.7903 -> 0.3809 / 0.3178) but comes with large adv2 recall loss on JBB (Table C), making it unsuitable under the recall constraint.
- Normalization-only yields modest adv2 FPR gains (0.7903 -> 0.7436) with smaller recall loss (0.9613 -> 0.9478), the best balance among ablations.
- Clean/unicode FPR increases under adv2-only and norm+adv2, indicating a trade-off that does not generalize across splits.

## 8. Model selection
Final run: week7_norm_only.
Rationale: preserves clean/unicode operating-point behavior while improving adv2 transfer without the large JBB adv2 recall collapse observed in adv2-only and norm+adv2.

## 9. Error analysis
- Review top FP/FN for adv2 and rewrite in reports/week7/error_cases/week7_norm_only/ (especially test_main_adv2_* and test_jbb_adv2_*).
- Adv2 FPs: mixed-script noise still triggers high scores; Adv2 FNs: obfuscation that dilutes attack tokens.
- Rewrite FNs: paraphrases that soften direct harm cues.

## 10. Threats to validity
- Synthetic transforms may not capture real-world adversaries.
- Dataset shift between main and JBB splits.
- A single val threshold assumes stable calibration across shifts.

## 11. Next steps
- Incorporate representative error cases into robustness section and final thesis narrative.
- If needed, tune adv2_prob or add a lighter adversarial mix to reduce JBB adv2 false positives without recall collapse.
