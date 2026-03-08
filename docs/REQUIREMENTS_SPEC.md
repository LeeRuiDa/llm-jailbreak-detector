# Requirements Specification

This file is the runtime-focused requirements summary used by the repo and demo materials. The school-facing attachment is `docs/Requirements_Specification.md`.

## Scope
- local CLI detector with an offline rules baseline
- optional LoRA detector from local run artifacts
- reproducible Week 7 evaluation and locked-pack reporting

## Functional requirements
- `jbd predict` accepts one `--text` input and returns structured JSON.
- `jbd batch` accepts `.jsonl` or `.txt` input and writes `.jsonl` output.
- `jbd normalize` exposes the normalization transform used by the runtime.
- `jbd doctor` reports environment and optional LoRA dependency status.
- LoRA mode supports `--run_dir` and `--threshold val` for local inference.

## Non-functional requirements
- low-FPR calibration target of about 1% on validation
- deterministic scoring for fixed inputs and artifacts
- rules mode works offline without model downloads
- evaluation artifacts persist config, threshold, metrics, and environment metadata
- runtime is demo-safe on Windows or Linux with Python 3.11+ in CI

## Runtime input and output schema
Input JSONL:
- `text` (required)
- `id` (optional)

Output JSON for `predict` and JSONL rows for `batch`:
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

## Out of scope
- hosted safety API comparisons
- web UI or hosted service deployment
- live training during the exam demo
- any claim that unsupported CLI switches are part of the shipped runtime