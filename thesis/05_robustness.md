# Robustness

Final model = week7_norm_only; justification: improves adv2 transfer without JBB adv2 recall collapse.

## 5.1 Threat model
- unicode: Unicode mixing applied at evaluation time to test normalization robustness.
- adv2: character-level perturbations (homoglyphs, mixed-script, noise).
- rewrite: light paraphrases (synonyms, fillers, minor reordering).

## 5.2 Threshold transfer summary
Table 5.1: Threshold transfer summary (locked eval pack Table C, renumbered).
| run | split | fpr_at_val_threshold | tpr_at_val_threshold | asr_at_threshold |
| --- | --- | --- | --- | --- |
| week7_adv2_only | test_main | 0.0607 | 0.9970 | 0.0030 |
| week7_adv2_only | test_main_unicode | 0.0642 | 0.9969 | 0.0031 |
| week7_adv2_only | test_main_adv2 | 0.0985 | 0.9856 | 0.0144 |
| week7_adv2_only | test_main_rewrite | 0.0801 | 0.9977 | 0.0023 |
| week7_adv2_only | test_jbb_adv2 | 0.6633 | 0.7677 | 0.2323 |
| week7_adv2_only | test_jbb_rewrite | 0.6939 | 0.9899 | 0.0101 |
| week7_control | test_main | 0.0311 | 0.9878 | 0.0122 |
| week7_control | test_main_unicode | 0.0423 | 0.9858 | 0.0142 |
| week7_control | test_main_adv2 | 0.6826 | 0.9731 | 0.0269 |
| week7_control | test_main_rewrite | 0.0537 | 0.9896 | 0.0104 |
| week7_control | test_jbb_adv2 | 0.8980 | 0.9495 | 0.0505 |
| week7_control | test_jbb_rewrite | 0.6020 | 0.9798 | 0.0202 |
| week7_norm_only | test_main | 0.0311 | 0.9869 | 0.0131 |
| week7_norm_only | test_main_unicode | 0.0429 | 0.9862 | 0.0138 |
| week7_norm_only | test_main_adv2 | 0.6403 | 0.9967 | 0.0033 |
| week7_norm_only | test_main_rewrite | 0.0531 | 0.9902 | 0.0098 |
| week7_norm_only | test_jbb_adv2 | 0.8469 | 0.8990 | 0.1010 |
| week7_norm_only | test_jbb_rewrite | 0.5714 | 0.9899 | 0.0101 |
| week7_norm_plus_adv2 | test_main | 0.0566 | 0.9944 | 0.0056 |
| week7_norm_plus_adv2 | test_main_unicode | 0.0582 | 0.9959 | 0.0041 |
| week7_norm_plus_adv2 | test_main_adv2 | 0.0947 | 0.9831 | 0.0169 |
| week7_norm_plus_adv2 | test_main_rewrite | 0.0718 | 0.9968 | 0.0032 |
| week7_norm_plus_adv2 | test_jbb_adv2 | 0.5408 | 0.6768 | 0.3232 |
| week7_norm_plus_adv2 | test_jbb_rewrite | 0.6224 | 0.9798 | 0.0202 |

## 5.3 Robustness plots
![Figure 5.1: ROC curve for week7_norm_only on test_jbb_adv2.](reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_jbb_adv2.png)

![Figure 5.2: Score histogram for week7_norm_only on test_jbb_adv2.](reports/week7/locked_eval_pack/week7_norm_only/figures/hist_week7_norm_only_test_jbb_adv2.png)

## 5.4 Failure analysis and summary
- [test_main_adv2_fp](reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fp.md): benign-labeled prompts with heavy mixed-script noise saturate the score.
- [test_main_adv2_fn](reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fn.md): obfuscated harmful requests fall below the fixed threshold.
- [test_jbb_adv2_fp](reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fp.md): JBB prompts with obfuscation or sensitive topics are flagged as attacks.
- [test_jbb_adv2_fn](reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fn.md): recall drops on JBB adv2 when attack intent is heavily masked.
- [test_main_rewrite_fp](reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_rewrite_fp.md): filler-heavy paraphrases on benign tasks trigger high scores.
- [test_main_rewrite_fn](reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_rewrite_fn.md): paraphrased attack requests become less explicit and slip under threshold.

Normalization-only provides the safest transfer: adv2 robustness improves without the JBB adv2 recall collapse seen under adv2-heavy training, while clean/unicode performance stays essentially unchanged. This makes week7_norm_only a defensible operating point for the thesis, balancing robustness gains against distribution-shift risk.
