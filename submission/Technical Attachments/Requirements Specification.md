# Requirements Specification

## 1. Purpose and scope
This document defines the final submission requirements for the jailbreak and prompt-injection detector. The system is a local, offline-capable CLI application with an optional ML-backed detector and a frozen Week 7 evidence pack for thesis reporting.

Primary users:
- examiners and graders who need a reproducible demo
- developers who need local scoring for single prompts or JSONL batches
- the thesis author, who needs a traceable link between the paper, runtime, and locked evaluation artifacts

## 2. Functional requirements

| ID | Requirement | Final status |
| --- | --- | --- |
| FR-1 | The system shall score a single input text from the CLI. | Delivered via `jbd predict` |
| FR-2 | The system shall score batch input from `.jsonl` or `.txt`. | Delivered via `jbd batch` |
| FR-3 | The system shall provide a deterministic offline baseline detector. | Delivered via rules mode |
| FR-4 | The system shall support an optional learned detector from local artifacts. | Delivered via LoRA `--run_dir` |
| FR-5 | The system shall provide a normalization utility for inspection and inference hardening. | Delivered via `jbd normalize` and `--normalize` |
| FR-6 | The system shall provide environment diagnostics for demo readiness. | Delivered via `jbd doctor` |
| FR-7 | The evaluation pipeline shall store the validation operating point and final metrics. | Delivered via `runs/*/val_operating_point.json`, `final_metrics_*.json`, and locked pack snapshots |
| FR-8 | The project shall package a frozen evidence bundle for thesis reporting. | Delivered via `reports/week7/locked_eval_pack/week7_norm_only/` |
| FR-9 | The submission shall include a user manual, testing documentation, design documentation, requirements specification, and project development plan. | Delivered in `docs/` and mirrored in `submission/Technical Attachments/` |

## 3. Non-functional requirements

| ID | Requirement | Interpretation |
| --- | --- | --- |
| NFR-1 | Target a low false-positive operating point around 1% FPR. | Evaluation/calibration target, not a deployment guarantee |
| NFR-2 | Default runtime path must work without network access. | Rules mode is the guaranteed offline path |
| NFR-3 | Results should be reproducible from stored config, threshold, and metrics artifacts. | Enforced via run config, locked pack, and evaluation manifests |
| NFR-4 | Runtime behavior should be deterministic for fixed inputs and artifacts. | True except for latency measurement |
| NFR-5 | The project must be runnable on common student hardware. | Rules mode on CPU; LoRA optional |
| NFR-6 | Thesis claims must match the shipped runtime surface. | This submission pass aligns Chapter 6, manuals, and traceability docs to the code |

## 4. Input and output contract

### 4.1 Input formats
Single inference:
- `jbd predict --text <TEXT>`

Batch inference:
- `.jsonl` with required `text` and optional `id`
- `.txt` with one input per line; blank lines skipped; IDs generated from line index

### 4.2 Output schema for `predict` and `batch`
The shipped runtime emits the following fields:
- `text`
- `score`
- `label`
- `decision`
- `threshold`
- `threshold_used`
- `flagged`
- `detector`
- `model_version`
- `latency_ms`
- `rationale`
- `normalize_infer`
- optional `id`

The shipped runtime does not implement the older draft-only privacy switches, hash-or-truncation output variants, or a surfaced threshold-origin field.

## 5. Evaluation requirements
- Use the Week 7 locked-pack split counts from `reports/week7/locked_eval_pack/week7_norm_only/DATA_STATS.md`.
- Use `val` for threshold selection and transfer the resulting threshold unchanged to evaluation splits.
- Report AUROC, AUPRC, FPR at threshold, TPR at threshold, and ASR at threshold.
- Treat `test_main` and `test_jbb` as development-evaluation splits rather than blind final tests if they influenced model selection.
- Keep the final thesis run fixed to `week7_norm_only`.

## 6. Constraints and exclusions
- No hosted API dependency is allowed in the required runtime demo.
- No public CLI/API expansion is allowed unless implemented and tested in the repo.
- Raw datasets and full model checkpoints are not redistributed in the locked pack.
- External-guardrail comparison is not claimed as completed unless runnable local artifacts exist in the submission environment.

## 7. Claim boundary
The final submission may claim:
- reproducible local software
- an offline rules baseline and an optional learned detector
- strong ranking performance on the main project distribution
- explicit evidence of threshold-transfer failure under shift

The final submission may not claim:
- production readiness
- stable low-FPR behavior across unseen jailbreak datasets
- completed external-guardrail benchmarking unless a real comparison artifact exists