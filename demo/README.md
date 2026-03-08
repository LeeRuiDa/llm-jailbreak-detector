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

Claim boundary for the full project:
- the final thesis-selected LoRA run is `runs/week7_norm_only`
- validation FPR is `0.0094`, but `test_main` FPR is `0.0311` and `test_jbb` FPR is `0.5816`
- use the rules-only demo for reliability and describe LoRA results as research findings, not as production-ready moderation
