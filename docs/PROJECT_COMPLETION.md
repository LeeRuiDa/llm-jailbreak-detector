# Project Completion

This capstone is complete. The repository includes the final thesis, detector code, demo, tests, and the locked evaluation evidence used in the final analysis.

## Main Finding

The DeBERTa-v3-base LoRA detector achieved strong ranking performance on the main evaluation sets, but a threshold selected on validation data did not maintain the same false-positive behavior under distribution shift.

| Split | AUROC | FPR at threshold 0.7340 |
|---|---:|---:|
| Validation | 0.9983 | 0.0094 |
| Main test | 0.9958 | 0.0311 |
| JBB stress | 0.8890 | 0.5816 |
| Main adversarial (`adv2`) | 0.7133 | 0.6403 |

This is the key research result: ranking quality and fixed-threshold reliability are related but distinct properties.

## What Was Delivered

- An offline rules baseline and a learned DeBERTa-v3-base LoRA detector.
- A command-line interface for individual and batch predictions.
- Tests, demo material, evaluation reports, and reproducibility evidence.
- The [final thesis](../thesis/final_thesis.pdf).

## Defense Revisions

### Dataset roles

Chapter 3 now explains why the three corpus families are kept separate. BIPIA represents indirect prompt-injection settings; JailbreakDB supplies direct jailbreak material and benign hard negatives; and JailbreakBench remains a separate stress split for evaluating threshold transfer. The added explanation makes clear that validation data selects the threshold, while the main stress, JBB stress, and perturbation splits test it under changed conditions.

### Runtime interpretation

Chapter 4 now clarifies that Table 4.2 reports repeated CPU calls to an already-loaded `Predictor.predict()` function. The values exclude training, first-call initialization, command-line startup, file loading, and service deployment. The rules backend is fast because it is pattern based, while the LoRA backend runs the learned transformer detector. The table therefore supports local reproducibility, not a production latency claim.

## Evidence

| Item | Location |
|---|---|
| Final locked evaluation pack | [`reports/week7/locked_eval_pack/week7_norm_only/`](../reports/week7/locked_eval_pack/week7_norm_only/) |
| Dataset and split statistics | [`DATA_STATS.md`](../reports/week7/locked_eval_pack/week7_norm_only/DATA_STATS.md) |
| Threshold-transfer results | [`week7_table_C_threshold_transfer.md`](../reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_C_threshold_transfer.md) |
| Run configuration | [`RUN_CONFIG_SNAPSHOT.md`](../reports/week7/locked_eval_pack/week7_norm_only/RUN_CONFIG_SNAPSHOT.md) |
| Demo instructions | [`docs/DEMO_GUIDE.md`](DEMO_GUIDE.md) |

## Study Boundaries

- The official run uses one training seed.
- The evaluation is intentionally attack heavy and does not estimate real-world attack prevalence.
- Training used normalized text, while the locked evaluation used raw inference.
- Inputs were truncated to 256 tokens.
- Runtime values are local prediction measurements, not end-to-end deployment measurements.

For methodology, complete results, and interpretation, use the [final thesis](../thesis/final_thesis.pdf) as the authoritative reference.
