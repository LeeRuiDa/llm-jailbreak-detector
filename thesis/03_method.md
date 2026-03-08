# Method

## 3.1 Task and labels
This project treats jailbreak and prompt-injection detection as a binary classification problem over a canonical `text` field. The positive class is `label=1` (attack/unsafe) and the negative class is `label=0` (benign/safe). Auxiliary metadata such as `attack_type` is retained for analysis, but the training and evaluation pipeline uses only the binary label for supervision.

## 3.2 Canonical record schema and text template
The loader contract is the JSONL schema implemented in `src/data/io.py`:

- `id`
- `text`
- `label`
- `attack_type`
- `source`
- `group_id`
- optional `meta`

Prompt and optional context are assembled during ingestion into one `text` payload using a fixed `[PROMPT] ... [CONTEXT] ...` template. The template itself is implemented in `scripts/dataset_utils.py`, but explicit escaping of delimiter-like marker tokens inside raw prompt/context text is not currently enforced. The thesis therefore treats delimiter escaping as a documented limitation, not as an implemented safeguard.

## 3.3 Week 7 locked split counts
The authoritative split counts for the final thesis are the locked-pack counts in `reports/week7/locked_eval_pack/week7_norm_only/DATA_STATS.md`.

| split | total | benign | attack | attack rate |
| --- | ---: | ---: | ---: | ---: |
| train | 201,276 | 14,859 | 186,417 | 0.926176 |
| val | 6,106 | 3,082 | 3,024 | 0.495251 |
| test_main | 35,230 | 3,147 | 32,083 | 0.910673 |
| test_jbb | 197 | 98 | 99 | 0.502538 |
| test_main_unicode | 35,230 | 3,147 | 32,083 | 0.910673 |
| test_jbb_unicode | 197 | 98 | 99 | 0.502538 |
| test_main_adv2 | 35,230 | 3,147 | 32,083 | 0.910673 |
| test_jbb_adv2 | 197 | 98 | 99 | 0.502538 |
| test_main_rewrite | 35,230 | 3,147 | 32,083 | 0.910673 |
| test_jbb_rewrite | 197 | 98 | 99 | 0.502538 |

![Figure 3.1: Detection pipeline from input through normalization, detector, decision, and output.](docs/figures/ch3_pipeline.png)

## 3.4 Detectors and preprocessing
The runtime exposes two detector backends:

- Rules baseline: offline regex detector with binary score `0.0` or `1.0`.
- Optional LoRA classifier: local-artifact Hugging Face sequence classifier using the saved Week 7 run directory.

The final locked Week 7 model is `week7_norm_only`:

- backbone: `microsoft/deberta-v3-base`
- `normalize_train=true`
- `normalize_infer=false`
- `unicode_preprocess=false`
- `normalize_drop_mn=false`
- `val_threshold=0.7340`

## 3.5 Metrics and operating point
Evaluation reports AUROC, AUPRC, FPR at the transferred threshold, TPR at the transferred threshold, and ASR at the transferred threshold.

- FPR: benign examples flagged as attacks
- TPR: attacks correctly flagged
- ASR: attack false-negative rate at the threshold (`1 - TPR`)

The operating point is selected on `val` at target FPR `1%` and then transferred unchanged to every evaluation split. Because the benign validation set contains 3,082 examples, the smallest possible FPR step on validation is `1/3082 ~= 0.0324%`. On `test_jbb`, the benign count is only 98, so each additional benign false positive changes reported FPR by about `1.02%`.

![Figure 3.2: Evaluation protocol with a validation threshold transferred unchanged to all test splits.](docs/figures/ch3_eval_protocol.png)

## 3.6 Locked protocol
Week 7 uses a frozen split grid and a locked reporting bundle:

1. Select `week7_norm_only` as the final run.
2. Calibrate `val_threshold` on `val` only.
3. Apply that threshold unchanged to `test_main`, `test_jbb`, and all unicode/adv2/rewrite variants.
4. Package only aggregate metrics, figures, error cases, config snapshot, environment summary, and data stats into the locked eval pack.

This project therefore supports a strong reproducibility claim about the final reported numbers, but it does not claim blind final-test isolation or production-ready threshold stability under distribution shift.