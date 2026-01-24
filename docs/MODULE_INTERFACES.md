# Module Interfaces

## Core normalization

- `llm_jailbreak_detector.normalize.normalize_text(text: str, drop_mn: bool = False) -> str`

## Detectors

- `llm_jailbreak_detector.rules_detector.RulesDetector`
  - `predict_proba(text: str) -> float`
  - `predict(text: str, threshold: float = 0.5) -> int`

- `llm_jailbreak_detector.lora_detector.LoraDetector`
  - `__init__(run_dir: str | Path, device: str = "cpu")`
  - `predict_proba(text: str) -> float`
  - `predict(text: str, threshold: float | None = None) -> int`

## Unified prediction

- `llm_jailbreak_detector.predict.Predictor`
  - `__init__(detector: str = "rules", run_dir: str | None = None)`
  - `predict(text: str, threshold: float | str | None = None, normalize_infer: bool = False, drop_mn: bool = False) -> PredictionResult`

- `llm_jailbreak_detector.predict.predict(...) -> dict`
  - Returns `{score, label, threshold, detector, metadata}`.

## Batch I/O helpers

- `llm_jailbreak_detector.io.iter_jsonl(path) -> Iterator[dict]`
- `llm_jailbreak_detector.io.iter_text_lines(path) -> Iterator[dict]`
- `llm_jailbreak_detector.io.iter_input_records(path) -> Iterator[dict]`
- `llm_jailbreak_detector.io.write_jsonl(path, rows)`

## CLI contract

Commands:

- `jbd predict --text "..." --detector rules|lora --run_dir <path?> --threshold <float|val> [--normalize] [--drop-mn]`
- `jbd batch --input <jsonl|txt> --output <jsonl> --detector rules|lora --run_dir <path?> --threshold <float|val> [--normalize] [--drop-mn]`
- `jbd normalize --text "..." [--drop-mn]`

Output schema (predict/batch):

- `id` (optional)
- `text`
- `score`
- `threshold`
- `flagged`
- `detector`
- `normalize_infer`

## File formats

- JSONL input: one JSON object per line, `text` required, `id` optional.
- TXT input: one text per line, blank lines skipped, IDs auto-assigned by line index.
