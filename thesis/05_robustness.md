# Robustness

The final model is `week7_norm_only`. Its value is not that it solves robustness, but that it exposes a clear and reproducible threshold-transfer story: strong main-distribution ranking, high recall on many shifts, and serious benign false-positive drift under distribution shift.

## 5.1 Threat model and evaluation setting
This chapter keeps the validation-derived threshold fixed at `0.7340` and applies it unchanged to every evaluation split. The authoritative locked-pack counts are:

- `val`: 6,106 total = 3,082 benign + 3,024 attack
- `test_main`: 35,230 total = 3,147 benign + 32,083 attack
- `test_jbb`: 197 total = 98 benign + 99 attack

Unicode, adv2, and rewrite variants preserve the same counts as the corresponding clean split.

## 5.2 Final-model threshold transfer summary

| split | benign | attack | FPR@thr | TPR@thr | ASR@thr |
| --- | ---: | ---: | ---: | ---: | ---: |
| test_main | 3,147 | 32,083 | 0.0311 | 0.9869 | 0.0131 |
| test_main_unicode | 3,147 | 32,083 | 0.0429 | 0.9862 | 0.0138 |
| test_main_adv2 | 3,147 | 32,083 | 0.6403 | 0.9967 | 0.0033 |
| test_main_rewrite | 3,147 | 32,083 | 0.0531 | 0.9902 | 0.0098 |
| test_jbb | 98 | 99 | 0.5816 | 0.9798 | 0.0202 |
| test_jbb_unicode | 98 | 99 | 0.6531 | 0.9798 | 0.0202 |
| test_jbb_adv2 | 98 | 99 | 0.8469 | 0.8990 | 0.1010 |
| test_jbb_rewrite | 98 | 99 | 0.5714 | 0.9899 | 0.0101 |

Interpretation:

- clean `test_main` performance is strong but already above the intended 1% FPR target
- JBB benign traffic is the first major false-positive failure mode
- adv2 is the dominant robustness failure because it destroys operating-point stability
- rewrite is milder, but it does not eliminate the cross-dataset benign shift problem

## 5.3 Family-by-family interpretation

### Unicode
Unicode obfuscation raises false positives more than it harms recall. The main split moves from FPR `0.0311` to `0.0429` with almost no recall loss, while JBB moves from `0.5816` to `0.6531`.

### adv2
adv2 is the decisive failure case. On `test_main_adv2`, TPR remains `0.9967` but FPR explodes to `0.6403`. On `test_jbb_adv2`, both sides degrade: FPR `0.8469`, TPR `0.8990`.

### Rewrite
Rewrite remains comparatively gentle on the main distribution (`FPR=0.0531`, `TPR=0.9902`), but JBB rewrite still shows high benign false-positive rates (`0.5714`).

## 5.4 Small-sample caution on JBB
The JBB splits contain only 98 benign examples, so FPR is quantized: each extra benign false positive changes the reported value by about `1/98 ~= 1.02%`. The JBB numbers are therefore better treated as a stress signal than as a high-precision deployment estimate.

## 5.5 Error analysis anchors
- [test_main_adv2_fp](reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fp.md): benign prompts with heavy mixed-script noise saturate the score.
- [test_main_adv2_fn](reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fn.md): obfuscated harmful requests fall below the fixed threshold.
- [test_jbb_adv2_fp](reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fp.md): benign JBB prompts with obfuscation or safety language are over-flagged.
- [test_jbb_adv2_fn](reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fn.md): recall drops when attack intent is heavily masked.

## 5.6 Thesis claim boundary
The defensible robustness claim is limited:

- supported: `week7_norm_only` is the least harmful option among the tested Week 7 settings
- supported: the locked pack shows clear failure modes under distribution shift
- not supported: a claim that one fixed threshold is robust across unseen jailbreak datasets or noisy channels

![Figure 5.1: ROC curve for week7_norm_only on test_jbb_adv2.](reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_jbb_adv2.png)

![Figure 5.2: Score histogram for week7_norm_only on test_jbb_adv2.](reports/week7/locked_eval_pack/week7_norm_only/figures/hist_week7_norm_only_test_jbb_adv2.png)