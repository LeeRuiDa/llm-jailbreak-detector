# Evidence for Chapter 6 System Demonstration

## Runtime surface
- CLI entrypoint: `jbd` via `src/llm_jailbreak_detector/cli.py` and `pyproject.toml`.
- Supported commands: `predict`, `batch`, `normalize`, `doctor`. Evidence: `src/llm_jailbreak_detector/cli.py`, `docs/MODULE_INTERFACES.md`.
- Supported detectors: `rules` and `lora`. Evidence: `src/llm_jailbreak_detector/predict.py`.

## Actual CLI contract
### `predict` / `batch` flags
- single-input mode accepts `--text`, `--detector`, `--run_dir`, `--threshold`, `--normalize`, `--drop-mn`, optional `--id`
- batch mode accepts `--input`, `--output`, plus the same detector, threshold, and normalization flags

### Output fields
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

Evidence: `src/llm_jailbreak_detector/cli.py`, `docs/MODULE_INTERFACES.md`, `tests/test_cli_smoke.py`.

## Explicit non-features
The shipped CLI does not implement the older draft-only privacy switches, hash/truncation output variants, or a surfaced threshold-origin field.

Internal threshold-source metadata exists in `Predictor`, but the CLI payload does not expose it. Evidence: `src/llm_jailbreak_detector/predict.py`, `src/llm_jailbreak_detector/cli.py`.

## Demo-safe evidence
- Rules mode is the primary demo path because it is offline and deterministic. Evidence: `docs/DEMO_GUIDE.md`, `demo/DEMO_SCRIPT.md`.
- CLI smoke tests cover help, doctor, rules predict, rules batch, invalid JSONL, and missing LoRA `run_dir`. Evidence: `tests/test_cli_smoke.py`.
- Chapter 6 should present middleware deployment only as an integration scenario, not as a shipped hosted service. Evidence: no FastAPI/Flask service entrypoint exists in the repo.