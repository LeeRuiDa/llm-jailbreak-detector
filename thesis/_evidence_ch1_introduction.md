# Evidence for Chapter 1 Introduction

## Framing and scope
- The shipped software is a CLI-first, offline-capable detector with a rules baseline and an optional LoRA backend. Evidence: `README.md`, `docs/REQUIREMENTS_SPEC.md`, `src/llm_jailbreak_detector/cli.py`.
- The intended users are examiners, graders, and developers who need local scoring on single prompts or batches. Evidence: `README.md`, `docs/Requirements_Specification.md`.
- The final thesis run is `runs/week7_norm_only`. Evidence: `README.md`, `reports/week7/WEEK7_FINAL.md`, `reports/week7/run_manifest.json`.

## Claim boundary
- Validation FPR meets the design target (`0.0094`), but transferred FPR rises to `0.0311` on `test_main` and `0.5816` on `test_jbb`. Evidence: `runs/week7_norm_only/final_metrics_val.json`, `runs/week7_norm_only/final_metrics_test_main.json`, `runs/week7_norm_only/final_metrics_test_jbb.json`.
- The project should be framed as a reproducible research prototype, not as a production-ready guardrail. Evidence: `README.md`, `docs/DEMO_GUIDE.md`, `thesis/06_system_demo.md`.

## Threat model summary
- Attack class is binary `label=1`; benign is `label=0`. Evidence: `src/data/io.py`, `thesis/03_method.md`.
- Model-facing input is one canonical `text` field, assembled from prompt and optional context using `[PROMPT]` / `[CONTEXT]` formatting during ingestion. Evidence: `scripts/dataset_utils.py`, `docs/data_schema.md`, `thesis/03_method.md`.
- Explicit escaping of delimiter-like marker lines is not enforced and should be described as a limitation. Evidence: `scripts/dataset_utils.py`, `docs/TRACEABILITY_MATRIX.md`, `thesis ready chapters/ch3 method.tex.txt`.

## Introduction-safe contribution list
- offline rules baseline that always runs locally
- optional learned detector from local artifacts
- fixed low-FPR validation operating point with locked threshold transfer
- reproducible Week 7 evidence pack
- honest reporting of threshold-transfer failure under distribution shift