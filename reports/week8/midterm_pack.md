# Mid-Term Pack (Week 8)

## Overview
This mid-term pack summarizes progress through Week 7, the current final model choice, and the core evidence artifacts for robustness and threshold transfer. It also captures the immediate next steps and risk posture ahead of the final thesis write-up and demonstration phase.

## What's done (Weeks 1-7)
- Week 1: established baseline rules detector and unified data schema.
- Week 2: built preprocessing utilities and evaluation scaffolding.
- Week 3: integrated LoRA fine-tuning pipeline and metrics logging.
- Week 4: locked backbone selection (microsoft/deberta-v3-base) and frozen baseline results.
- Week 5: evaluated robustness on unicode/adv2, analyzed operating-point transfer.
- Week 6: ran train-time robustness ablations and rewrite perturbations.
- Week 7: completed 2x2 ablation (normalize_train x adv2) and selected final model.

## Final model: week7_norm_only
The week7_norm_only configuration provides the safest transfer behavior: it improves robustness on adv2 without the sharp JBB adv2 recall collapse seen under adv2-heavy training, while keeping clean/unicode operating-point behavior essentially unchanged. This balance makes it the most defensible operating point for the thesis and demo, given the distribution-shift risks observed across JBB and synthetic perturbations.

## Key metrics

Week 7 Table C (threshold transfer):

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

Week 7 Table D (ablation effects):

| run | group | mean_auroc | mean_auprc | mean_fpr | mean_tpr | mean_asr | delta_fpr_vs_control | delta_tpr_vs_control | delta_asr_vs_control |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| week7_adv2_only | clean | 0.9452 | 0.9468 | 0.3773 | 0.9935 | 0.0065 | 0.0658 | 0.0097 | -0.0097 |
| week7_adv2_only | unicode | 0.9163 | 0.9157 | 0.4096 | 0.9985 | 0.0015 | 0.0365 | 0.0207 | -0.0207 |
| week7_adv2_only | adv2 | 0.8124 | 0.8334 | 0.3809 | 0.8766 | 0.1234 | -0.4094 | -0.0847 | 0.0847 |
| week7_adv2_only | rewrite | 0.9391 | 0.9454 | 0.3870 | 0.9938 | 0.0062 | 0.0591 | 0.0091 | -0.0091 |
| week7_control | clean | 0.9519 | 0.9514 | 0.3115 | 0.9838 | 0.0162 | 0.0000 | 0.0000 | 0.0000 |
| week7_control | unicode | 0.9404 | 0.9397 | 0.3732 | 0.9778 | 0.0222 | 0.0000 | 0.0000 | 0.0000 |
| week7_control | adv2 | 0.6277 | 0.7553 | 0.7903 | 0.9613 | 0.0387 | 0.0000 | 0.0000 | 0.0000 |
| week7_control | rewrite | 0.9463 | 0.9450 | 0.3279 | 0.9847 | 0.0153 | 0.0000 | 0.0000 | 0.0000 |
| week7_norm_only | clean | 0.9424 | 0.9371 | 0.3064 | 0.9834 | 0.0166 | -0.0051 | -0.0004 | 0.0004 |
| week7_norm_only | unicode | 0.9381 | 0.9349 | 0.3480 | 0.9830 | 0.0170 | -0.0252 | 0.0052 | -0.0052 |
| week7_norm_only | adv2 | 0.6726 | 0.7908 | 0.7436 | 0.9478 | 0.0522 | -0.0466 | -0.0135 | 0.0135 |
| week7_norm_only | rewrite | 0.9449 | 0.9479 | 0.3122 | 0.9900 | 0.0100 | -0.0156 | 0.0053 | -0.0053 |
| week7_norm_plus_adv2 | clean | 0.9473 | 0.9471 | 0.3344 | 0.9871 | 0.0129 | 0.0229 | 0.0033 | -0.0033 |
| week7_norm_plus_adv2 | unicode | 0.9406 | 0.9368 | 0.3658 | 0.9828 | 0.0172 | -0.0074 | 0.0050 | -0.0050 |
| week7_norm_plus_adv2 | adv2 | 0.8081 | 0.8243 | 0.3178 | 0.8300 | 0.1700 | -0.4725 | -0.1313 | 0.1313 |
| week7_norm_plus_adv2 | rewrite | 0.9330 | 0.9345 | 0.3471 | 0.9883 | 0.0117 | 0.0193 | 0.0036 | -0.0036 |

Key plots (paths):
- reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_main_adv2.png
- reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_jbb_adv2.png
- reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_main_rewrite.png

## What's next (Weeks 9+ roadmap)
- Finalize thesis chapters (methods, experiments, robustness, limitations).
- Package and document the demo CLI, plus examiner quickstart materials.
- Add targeted error-case reviews and clarify failure modes for JBB + adv2.
- Optional: calibrate alternative thresholds for documented operational trade-offs.

## Risks/limitations + mitigations
- Dataset shift (main vs JBB): report separate operating points and highlight transfer gaps; avoid over-claiming generalization.
- Synthetic perturbations (adv2/rewrite): cross-check against clean/unicode splits and include error-case discussion.
- Threshold transfer: document val-threshold transfer failures and provide calibrated alternatives where needed.
