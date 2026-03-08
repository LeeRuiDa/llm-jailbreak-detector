# Experiments

## 4.1 Locked-pack source of truth
All thesis numbers in this chapter should be read from the Week 7 locked evaluation pack at `reports/week7/locked_eval_pack/week7_norm_only/`. That pack is the only authoritative source for split counts, frozen metrics, figures, and the selected validation threshold.

## 4.2 Split grid and evaluation framing
The fixed Week 7 grid contains one validation split and two evaluation split families:

| split | total | benign | attack |
| --- | ---: | ---: | ---: |
| train | 201,276 | 14,859 | 186,417 |
| val | 6,106 | 3,082 | 3,024 |
| test_main | 35,230 | 3,147 | 32,083 |
| test_jbb | 197 | 98 | 99 |

Unicode, adv2, and rewrite variants preserve the same sample counts as their corresponding clean split.

The threshold is calibrated on `val` and transferred unchanged to all evaluation splits. Because `test_main` and `test_jbb` were inspected during Week 7 model selection, they should be described as development-evaluation splits rather than blind final-test sets.

## 4.3 Model selection summary
The Week 7 ablation varied two factors:

- `normalize_train` in `{false, true}`
- `aug_adv2_prob` in `{0.0, 0.25}`

The selected final run was `week7_norm_only`, with:

- backbone `microsoft/deberta-v3-base`
- `normalize_train=true`
- `normalize_infer=false`
- no adv2 or rewrite augmentation
- `val_threshold=0.7340`

The rationale for selection is pragmatic rather than absolute: among the tested options, `week7_norm_only` gave the least harmful trade-off between clean performance and perturbation robustness without the severe recall collapse seen under heavier adv2 training on `test_jbb_adv2`.

## 4.4 Main locked-pack results for the selected run

### Clean + Unicode
| split | AUROC | AUPRC | FPR@thr | TPR@thr | ASR@thr |
| --- | ---: | ---: | ---: | ---: | ---: |
| val | 0.9983 | 0.9982 | 0.0094 | 0.9696 | 0.0304 |
| test_main | 0.9958 | 0.9996 | 0.0311 | 0.9869 | 0.0131 |
| test_jbb | 0.8890 | 0.8747 | 0.5816 | 0.9798 | 0.0202 |
| test_main_unicode | 0.9949 | 0.9994 | 0.0429 | 0.9862 | 0.0138 |
| test_jbb_unicode | 0.8814 | 0.8704 | 0.6531 | 0.9798 | 0.0202 |

### adv2 + Rewrite
| split | AUROC | AUPRC | FPR@thr | TPR@thr | ASR@thr |
| --- | ---: | ---: | ---: | ---: | ---: |
| test_main_adv2 | 0.7133 | 0.9523 | 0.6403 | 0.9967 | 0.0033 |
| test_jbb_adv2 | 0.6318 | 0.6294 | 0.8469 | 0.8990 | 0.1010 |
| test_main_rewrite | 0.9942 | 0.9994 | 0.0531 | 0.9902 | 0.0098 |
| test_jbb_rewrite | 0.8956 | 0.8964 | 0.5714 | 0.9899 | 0.0101 |

Key interpretation:

- clean `test_main` ranking is strong, but FPR already rises above the `1%` design target
- JBB shows severe benign-distribution shift even without perturbation
- adv2 is the decisive robustness failure mode because it destroys operating-point stability
- rewrite is less harmful on the main distribution, but it does not solve the JBB false-positive problem

![Figure 4.1: ROC curve for week7_norm_only on test_main_adv2.](reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_main_adv2.png)

![Figure 4.2: ROC curve for week7_norm_only on test_main_rewrite.](reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_main_rewrite.png)

![Figure 4.3: Score histogram for week7_norm_only on test_main_adv2.](reports/week7/locked_eval_pack/week7_norm_only/figures/hist_week7_norm_only_test_main_adv2.png)

## 4.5 Proposal-compliance note on external guardrails
The original proposal promised comparison against existing guardrails such as Llama Guard 2, Prompt Guard, or ProtectAI-style detectors in addition to a rules baseline. The final submission does not provide a reproducible benchmark against those external systems.

That reduction is deliberate and should be stated explicitly. During the submission pass, the local repository, local Python environment, and local Hugging Face cache were checked for runnable local artifacts corresponding to those proposal-named systems. None were available in the submission environment, and a hosted API benchmark would have violated the project's offline-first reproducibility constraint. The final thesis should therefore describe the work as an offline reproducible detector study with a rules baseline and a learned detector, not as a completed external-guardrail bakeoff.

## 4.6 Claim boundary
The strongest defensible experimental claim is:

- `week7_norm_only` provides strong ranking quality on the main project distribution.
- The transferred threshold does not remain stable under distribution shift, especially on JailbreakBench and adv2-style perturbations.
- The Week 7 pack is a reproducible development-evaluation bundle, not a blind final-test report.