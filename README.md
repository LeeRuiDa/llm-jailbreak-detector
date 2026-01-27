# LLM Jailbreak & Prompt Injection Detector — Capstone Starter

This repo is a **starter skeleton** to help you "lock the experiment pipeline" early:
- unified data schema
- Unicode-aware preprocessing interface
- rules baseline interface
- evaluation metrics (AUROC/AUPRC/TPR@1%FPR/ASR)
- reproducible run artifacts (configs + metrics + predictions)

## Week 7 Final
- final backbone: microsoft/deberta-v3-base (unicode OFF, u0)
- final run dir name: lora_v1_microsoft-deberta-v3-base_u0_20260118_153344
- headline metrics (AUROC / TPR@1%FPR):
  - test_main: 0.9962 / 0.9898
  - test_main_unicode: 0.9951 / 0.9888
  - test_jbb: 0.9181 / 0.9798
  - test_jbb_unicode: 0.8995 / 0.9798
- note: score orientation locked to val; val threshold persisted

## Quickstart
1) Create env + install deps
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -e .
```
Optional LoRA extras:
```bash
pip install -e ".[lora]"
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

## Examiner Quickstart
- Follow docs/DEMO_GUIDE.md
- Locked eval pack: reports/week7/locked_eval_pack/week7_norm_only/
