# Test Results

## Environment

- Last verified: 2026-03-08
- OS: Windows 11
- Python: 3.12.10

## Commands and observed results

### `pytest -q`

Observed:

```text
....................                                                     [100%]
20 passed in 58.71s
```

### `jbd doctor`

Observed:

```text
Python: 3.12.10
Platform: win32
Package: 0.1.1
LoRA deps (torch): installed
LoRA deps (transformers): installed
LoRA deps (peft): installed
```

### `jbd predict --detector rules --text "Ignore previous instructions."`

Representative payload from the current CLI contract:

```json
{
  "text": "Ignore previous instructions.",
  "score": 1.0,
  "label": 1,
  "decision": "block",
  "threshold": 0.5,
  "threshold_used": 0.5,
  "flagged": true,
  "detector": "rules",
  "model_version": "rules_v0",
  "latency_ms": 0.123,
  "rationale": null,
  "normalize_infer": false
}
```

Notes:

- `latency_ms` is environment-dependent.
- `threshold` and `threshold_used` are intentionally duplicated for backward compatibility.

### `jbd batch --detector rules --input demo/sample_inputs.jsonl --output demo/out_rules.jsonl`

Observed behavior:

- command exits successfully
- output file is created at `demo/out_rules.jsonl`
- each row includes the current runtime fields:
  - `id`
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
