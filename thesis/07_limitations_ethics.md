# Limitations and Ethics

## 7.1 Limitations overview
- Synthetic perturbations (adv2, rewrite, unicode) approximate real-world attacks and may miss unseen tactics.
- Dataset shift between main and JBB splits can confound robustness attribution.
- A single fixed threshold assumes calibration stability across distribution shifts.
- Augmentation can overfit to the specific perturbation families implemented.

## 7.2 Ethical considerations
Model decisions affect access to information; false positives and false negatives must be monitored.

## 7.3 Limitations mapped to evidence (optional)
Table 7.1: Limitations mapped to locked-pack error case evidence.
| Limitation | Evidence (locked-pack error cases) |
| --- | --- |
| Synthetic perturbations may miss unseen tactics | reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fn.md, reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_rewrite_fn.md |
| Dataset shift between main and JBB splits | reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fn.md, reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fp.md |
| Fixed threshold assumes calibration stability | reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fp.md, reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fn.md |
| Augmentation can overfit to perturbation families | reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_rewrite_fp.md, reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fp.md |

## 7.4 Future work
Additional datasets and real-world evaluation are needed to validate robustness.

## 7.5 Summary
Limitations inform conservative deployment and ongoing evaluation.
