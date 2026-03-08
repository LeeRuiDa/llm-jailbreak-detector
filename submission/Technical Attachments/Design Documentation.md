# Design Documentation

## 1. System overview
The project is organized as a CLI-first detection system with a frozen evaluation/reporting pipeline. The runtime surface is intentionally narrow so examiners can install and run the software locally without hidden services.

## 2. High-level architecture

```text
Input text or JSONL/TXT batch
  -> CLI (`jbd`)
  -> Predictor
  -> optional normalization
  -> detector backend (`rules` or `lora`)
  -> score + threshold decision
  -> JSON/JSONL output

Training/evaluation side
  -> canonical JSONL datasets
  -> train_lora.py
  -> run_dir artifacts
  -> eval_week7_grid.py / build_week7_tables.py
  -> locked evaluation pack
```

## 3. Module map

| Layer | Responsibility | Key files |
| --- | --- | --- |
| CLI/runtime | Parse commands, run detectors, emit outputs | `src/llm_jailbreak_detector/cli.py`, `src/llm_jailbreak_detector/predict.py` |
| Rules baseline | Always-available regex detector | `src/baselines/rules.py`, `src/llm_jailbreak_detector/rules_detector.py` |
| LoRA inference | Load local artifacts and produce attack probability | `src/llm_jailbreak_detector/lora_detector.py` |
| Input/output | Read JSONL/TXT and write JSONL | `src/llm_jailbreak_detector/io.py` |
| Normalization | NFKC + `Cf` removal + optional `Mn` removal | `src/llm_jailbreak_detector/normalize.py`, `src/preprocess/normalize.py` |
| Dataset layer | Validate canonical schema and prevent leakage | `src/data/io.py`, `scripts/validate_dataset.py`, `scripts/dataset_utils.py` |
| Training | Fine-tune LoRA classifier and persist run artifacts | `scripts/train_lora.py` |
| Evaluation/reporting | Produce split metrics, tables, plots, and locked pack | `scripts/eval_lora_from_run.py`, `scripts/eval_week7_grid.py`, `scripts/build_week7_tables.py`, `scripts/lock_week7_eval_pack.py` |

## 4. Data flow

### 4.1 Runtime path
1. User calls `jbd predict` or `jbd batch`.
2. Input is read as plain text or from JSONL/TXT.
3. Optional normalization is applied at inference if requested.
4. `Predictor` resolves detector backend and threshold policy.
5. Detector returns a score.
6. CLI converts the score into `label`, `decision`, `flagged`, `threshold_used`, and metadata.
7. Output is printed or written to JSONL.

### 4.2 ML pipeline path
1. Ingestion scripts convert source datasets into canonical JSONL records.
2. Dataset validation checks required fields, duplicate IDs, and `group_id` overlap.
3. `scripts/train_lora.py` trains a run and records config, hashes, metrics, and the validation operating point.
4. Best-checkpoint selection is based on validation `tpr_at_fpr` with AUROC tie-break.
5. `scripts/eval_lora_from_run.py` evaluates splits and writes `evaluation_manifest.json` without mutating the frozen training config.
6. Week 7 scripts collect metrics into a locked evidence pack used by the thesis.

## 5. Configuration loading
- Rules mode uses a fixed threshold of `0.5` unless explicitly overridden.
- LoRA mode requires `run_dir/config.json` and `run_dir/lora_adapter/`.
- `Predictor` resolves `threshold=None` to the saved LoRA threshold for learned runs.
- The final thesis run is `runs/week7_norm_only`.

## 6. Design decisions and trade-offs
- CLI-first rather than web-service-first: lower operational risk for grading.
- Rules default rather than LoRA default: guarantees an offline runnable baseline.
- Locked-pack reporting rather than raw-data release: balances reproducibility against dataset and safety constraints.
- Honest claim boundary rather than hidden recalibration: the system preserves validation-threshold transfer even when it fails under shift.

## 7. Known limitations in the design
- canonical `[PROMPT]` / `[CONTEXT]` formatting exists, but explicit escaping of delimiter-like marker lines is not implemented
- no ensemble runtime is shipped; the user selects either rules or LoRA per invocation
- no built-in redaction mode is implemented in the CLI
- external guardrail benchmarking is narrowed in the final submission because no runnable local artifacts were available