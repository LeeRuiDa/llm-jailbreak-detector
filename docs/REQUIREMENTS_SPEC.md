# Requirements Specification

## Scope

This project delivers an offline-capable jailbreak detector with a CLI and
Python API. The primary user is an examiner or developer who needs to score
single prompts or batches without network access. A rules-based detector is
the default; a LoRA-backed detector is optional and requires local artifacts.

## Functional requirements

- FR-1: Single prediction via `jbd predict` accepts a text string and returns a
  JSON payload with score, threshold, detector, and flag decision.
- FR-2: Batch prediction via `jbd batch` accepts `.jsonl` or `.txt` input and
  writes `.jsonl` output. Optional `id` values are preserved.
- FR-3: Normalization via `jbd normalize` performs NFKC + format character
  stripping, with optional Mn removal (`--drop-mn`).
- FR-4: Offline rules detector runs without network access and without model
  downloads. It is the default detector.
- FR-5: Optional LoRA detector accepts `--run_dir` and `--threshold` for
  local inference when weights are available.
- FR-6: CLI provides `--help` and `doctor` diagnostics for environment checks.

## Non-functional requirements

- NFR-1: Target <= 1% false positive rate (FPR) at the chosen operating point.
  This is a goal used for evaluation and calibration, not a hard guarantee.
- NFR-2: Deterministic results for a given input, threshold, and detector.
- NFR-3: Offline capability for the default rules detector.
- NFR-4: Reproducible evaluation via locked config/threshold artifacts and
  documented command lines.
- NFR-5: Runs on Windows with Python 3.9+.

## Input/output schema (JSONL)

Input JSONL (batch):

- `text` (string, required)
- `id` (string, optional)

Output JSONL (predict/batch):

- `id` (string, optional)
- `text` (string)
- `score` (float, detector score)
- `threshold` (float or string, operating point)
- `flagged` (boolean)
- `detector` (string: rules|lora)
- `normalize_infer` (boolean)

## Out of scope

- Online comparisons against hosted safety APIs (e.g., Llama Guard SaaS).
- Training or fine-tuning workflows for the exam demo.
- Web UI or production-grade service deployment.
- Large-scale dataset ingestion beyond the locked evaluation pack.
