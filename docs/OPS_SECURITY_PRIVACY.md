# Ops, Security, and Privacy

Scope:
- runtime detector package (`src/llm_jailbreak_detector/*`)
- evaluation/reporting scripts (`scripts/*`)

## Security

### Secret handling
- Runtime CLI does not require API keys for inference.
- No `.env` loader is used by the runtime package.
- LoRA mode loads local artifacts from `run_dir` and local Hugging Face cache only (`local_files_only=True` in `src/llm_jailbreak_detector/lora_detector.py`).

### Dependency pinning
- Dependencies are declared in `pyproject.toml` with version floors.
- A full freeze is captured in locked evaluation artifacts (`reports/week7/locked_eval_pack/week7_norm_only/ENV.txt`).
- Current repo does not ship a strict lockfile (for example `poetry.lock` / `requirements-lock.txt`), so exact environment recreation depends on captured `pip freeze`.

### Injection and misuse surfaces
- Untrusted input text flows into:
  - regex matching in `src/baselines/rules.py`
  - tokenizer/model inference in `src/llm_jailbreak_detector/lora_detector.py`
- The runtime path does not execute user-provided code.
- Operational recommendation:
  - treat all input text as untrusted;
  - enforce file/path allowlists for batch inputs in production wrappers.

### Safe logging
- `jbd predict` prints input text in stdout JSON.
- `jbd batch` writes input text into output JSONL rows.
- Recommendation:
  - do not enable persistent storage of raw prompts unless needed;
  - redact or hash sensitive fields when exporting logs beyond local testing.

## Privacy

### What is stored
- By default:
  - `predict` emits one JSON object to stdout;
  - `batch` writes JSONL only when `--output` is provided.
- Evaluation scripts can write:
  - predictions JSONL
  - metrics JSON
  - error-case markdown snippets

### Retention policy
- Repository runtime has no built-in retention daemon or automatic deletion policy.
- Practical default in this project:
  - no persistent storage unless operator chooses output paths;
  - locked eval pack stores aggregate reports and curated snippets.

### PII handling guidance
- Avoid running real PII in demo/evaluation artifacts.
- If PII cannot be avoided:
  - keep artifacts local;
  - redact prompt text before sharing reports;
  - prefer aggregate metrics over raw prompt dumps.

## Ops and monitoring

### Structured outputs
- Runtime outputs are JSON/JSONL and can be ingested by external monitoring tools.
- Recommended counters:
  - block rate (`decision == "block"`)
  - per-split FPR/TPR/ASR from `final_metrics_*.json`
  - false-positive review queue volume from `error_cases/*.md`

### Alerting
- No built-in alerting framework is implemented.
- Recommended minimal alerting trigger:
  - threshold breach on FPR drift across target splits (for example `test_main` vs validation baseline).

### Version stamping
- LoRA training/evaluation persists:
  - `git_commit`
  - `model_name` / `backbone`
  - `val_threshold`
  - dataset manifest hash
  in `runs/*/config.json`.
- Locked pack includes environment snapshot and run snapshot files:
  - `reports/week7/locked_eval_pack/week7_norm_only/ENV.txt`
  - `reports/week7/locked_eval_pack/week7_norm_only/RUN_CONFIG_SNAPSHOT.md`
