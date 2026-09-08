# Completed Capstone and Final Thesis

The undergraduate capstone is complete. Rida BOUBAKR defended the thesis at Sichuan University, addressed the committee's clarification requests, and graduated. This September 2026 repository update publishes the revised thesis and documents the completed work.

**Thesis:** *Threshold Transfer in Prompt-Layer Jailbreak and Prompt Injection Detection for LLM Applications*

[Read the final thesis (PDF)](../thesis/final_thesis.pdf). The [version guide](../thesis/README.md) identifies the final PDF and distinguishes it from earlier drafts.

## What Was Completed

The study implements a local prompt-layer detector with an offline rules baseline and an optional LoRA-adapted DeBERTa-v3-base classifier. The `jbd` CLI supports single-input prediction, batch scoring, explicit normalization, and environment diagnostics.

The research evaluates whether a decision threshold chosen on validation at a 1% target false-positive rate remains useful when transferred to other prompt distributions. Dataset ingestion, split construction, model training, threshold selection, perturbation evaluation, and the final evidence pack are documented in the thesis.

The selected run remains `week7_norm_only`, with a stored validation threshold of `0.7340390086174011`. The [locked Week 7 pack](../reports/week7/locked_eval_pack/week7_norm_only/) remains the authoritative record of the original result.

## Main Finding

The learned detector ranks attacks well on the main stress split, with AUROC `0.9958`, but the validation threshold does not maintain the intended benign false-positive rate across distributions:

| Split | FPR at the validation threshold |
| --- | ---: |
| Validation | 0.0094 |
| Main stress (`test_main`) | 0.0311 |
| JBB stress (`test_jbb`) | 0.5816 |
| Main stress with adv2 perturbations (`test_main_adv2`) | 0.6403 |

These are the existing thesis results. They show that strong ranking performance and usable decisions at a fixed threshold can diverge. They do not establish the behavior of all prompt-layer detectors or a production guardrail service.

## Defense Revisions

### Chapter 3, Section 3.1.2: Dataset Roles

The clarification after Table 3.1 explains why each source family is included:

- **BIPIA:** indirect prompt injection, including unsafe instructions entering through external context.
- **JailbreakDB:** direct jailbreak examples and benign hard negatives, which test whether security-related discussion can be distinguished from harmful instructions.
- **JailbreakBench:** a separate JBB stress split for examining threshold transfer across source distributions.

Validation is used to choose the threshold. Main stress, JBB stress, and perturbation splits test its transfer. These stress splits were inspected during model selection and therefore remain selection-aware development-evaluation evidence.

### Chapter 4, Section 4.2: Runtime Interpretation

The clarification after Table 4.2 explains the measurement boundary. The benchmark measures repeated CPU calls to the already-loaded `Predictor.predict()` function after warm-up. It excludes model training, first-call initialization, command-line startup, file loading, and full service deployment costs.

The rules backend performs lightweight pattern matching without a transformer. The LoRA backend runs the learned DeBERTa-based detector, with prediction time around 70 ms in the recorded local setting. The values support local reproducibility and availability; they are not production latency claims or evidence that training is lightweight.

The [benchmark script](../scripts/benchmark_thesis_runtime.py) and [original runtime measurements](../thesis_final_tex/runtime_benchmark.json) preserve the measurement procedure and values. Training and runtime timing are separate parts of the project.

Both committee revisions add explanatory text. They do not change the thesis claims, results, tables, figures, or measured values.

## Supplementary Evidence

The final thesis also discusses analyses performed after the official Week 7 result was locked. These remain separate from the selected run and its frozen metrics.

| Analysis | Archived evidence | Interpretation |
| --- | --- | --- |
| Calibration, nearby thresholds, benign-heavy recalibration, and multiple seeds | [Thesis support analyses](../reports/thesis_support/README.md) | Follow-up evidence about confidence and operating-point sensitivity. |
| Inference-time normalization and Unicode preprocessing | [Manual evaluation aggregates](../reports/manual_eval/) | Canonicalization improves some shifted results but does not establish stable low-FPR behavior. |
| Prompt Guard 2 86M comparator | [Aggregate metrics and run configuration](../reports/proposal_recovery/comparators/prompt_guard2_86m/) | One external comparator under validation threshold selection and transfer; not a broad model ranking. |
| Source-assembled benign-only slice | [Summary and category breakdown](../reports/thesis_support/benign_realistic_slice/week7_norm_only/) | 28 false positives among 300 benign examples at the stored threshold; this is not live traffic. |
| Truncation audit | [Overflow summary](../reports/thesis_support/truncation/overflow_summary.md) | About 20.4% of validation, 43.8% of `test_main`, and 83.4% of `test_main_adv2` exceed the 256-token budget. |

The newly published aggregate files are copied from the local research outputs without recalculating their values. Historical run paths in those files are provenance metadata, not portable paths expected to exist after cloning. Raw prompts, prediction dumps, model weights, and the full school submission ZIP are not part of this update.

## Study Boundaries

Training normalization was enabled while normalization in the frozen inference path was disabled. The final thesis treats this mismatch as an internal-validity limitation. A future matched-preprocessing study would need to train, calibrate, and evaluate each configuration consistently.

Other limits include the 256-token input budget, attack-heavy training with an unweighted loss, approximate rewrite labels, selection-aware stress evaluation, and a single official seed. Later reruns and supplementary probes help interpret the result but do not remove these limits.

## Using the Repository

Start with the [README quickstart](../README.md#quickstart) for the offline rules demo. Optional LoRA inference requires a local run directory and the backbone cache. Full training data and model weights are not distributed here.

For the final research narrative, use the [thesis PDF](../thesis/final_thesis.pdf). For the original experiment, inspect the [locked evaluation pack](../reports/week7/locked_eval_pack/week7_norm_only/). Earlier chapter drafts and LaTeX materials remain available as historical development files.
