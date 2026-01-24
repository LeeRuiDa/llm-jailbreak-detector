# User Manual

## Install

Rules demo (editable install):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

LoRA install (optional):

```bash
pip install -e ".[lora]"
```

## CLI overview

The CLI entrypoint is `jbd`.

### Predict a single text

```bash
jbd predict --text "Ignore previous instructions" --detector rules
```

### Batch scoring

```bash
jbd batch --input examples/sample_inputs.jsonl --output out.jsonl --detector rules
```

### Normalize text

```bash
jbd normalize --text "he\u200bllo" --drop-mn
```

## Offline mode

- Rules detector: fully offline, zero downloads.
- LoRA detector: optional; requires a local `run_dir`, local weights, and the `lora` extra installed.

## Input formats

### JSONL

Each line is a JSON object with a required `text` field and optional `id`:

```json
{"id":"ex1","text":"Hello"}
```

### TXT

Each line is treated as a separate text. Blank lines are skipped. IDs are auto-assigned by line index.

## Output format

Each output record is JSON with these fields:

- `id` (optional)
- `text`
- `score`
- `threshold`
- `flagged`
- `detector`
- `normalize_infer`

Example:

```json
{"id":"ex2","text":"Ignore previous instructions","score":1.0,"threshold":0.5,"flagged":true,"detector":"rules","normalize_infer":false}
```

## CLI flags

- `--detector rules|lora` (default: `rules`)
- `--run_dir <path>` required for `lora`
- `--threshold <float|val>` (use `val` to load `val_threshold` from `config.json`)
- `--normalize` apply inference-time normalization
- `--drop-mn` drop nonspacing marks during normalization

## Examples

```bash
jbd predict --text "Summarize this" --detector rules
jbd predict --text "Ignore previous instructions" --detector rules --normalize
jbd batch --input examples/sample_inputs.jsonl --output out.jsonl --detector rules
```

## Troubleshooting

- `run_dir is required for lora detector`: provide `--run_dir` or switch to `--detector rules`.
- `Failed to load local model files`: ensure the base model is in the local HF cache and the run dir includes `lora_adapter`.
- `threshold must be a float or 'val'`: use numeric values or `val` only with LoRA.
