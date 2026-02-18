# Demo Package

Files:
- `demo/DEMO_SCRIPT.md`: grader-proof live demo script with commands and expected behavior.
- `demo/sample_inputs.jsonl`: mixed benign / hard-negative / obvious / subtle / perturbed prompts.
- `demo/expected_outputs.jsonl`: deterministic expectations for rules-mode scoring.

Quick run:
```bash
pip install -e .
jbd --help
jbd batch --detector rules --input demo/sample_inputs.jsonl --output demo/out_rules.jsonl
```

Notes:
- This package is designed for CLI-first local demonstrations.
- Expected outputs are for `--detector rules` with default threshold (`0.5`).
- `latency_ms` is environment-dependent and is not fixed in expectations.
