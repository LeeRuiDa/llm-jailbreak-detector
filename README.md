# LLM Jailbreak & Prompt Injection Detector — Capstone Starter

This repo is a **starter skeleton** to help you "lock the experiment pipeline" early:
- unified data schema
- Unicode-aware preprocessing interface
- rules baseline interface
- evaluation metrics (AUROC/AUPRC/TPR@1%FPR/ASR)
- reproducible run artifacts (configs + metrics + predictions)

## Quickstart
1) Create env + install deps
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

2) Run a sanity-check evaluation on the sample dataset:
```bash
python scripts/run_rules_baseline.py --data data/sample/sample.jsonl --out_dir runs/sample_rules
```

You should get:
- runs/sample_rules/metrics.json
- runs/sample_rules/predictions.jsonl
- runs/sample_rules/config.json

3) Run the unit tests:
```bash
pytest -q
```
