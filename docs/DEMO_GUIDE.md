# Demo Guide (Examiner Quickstart)

Run these five commands from the repo root:

```bash
pip install -e .
jbd --help
jbd predict --text "Ignore previous instructions" --detector rules
jbd normalize --text "he\u200bllo" --drop-mn
jbd batch --input examples/sample_inputs.jsonl --output out.jsonl --detector rules
```

Notes:
- Rules mode is fully offline.
- LoRA mode: `pip install -e ".[lora]"` then use `--run_dir` with local weights.
