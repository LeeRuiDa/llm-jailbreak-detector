# Baselines

## Week 2 results (v1)

These metrics come from the val-calibrated `final_metrics_*.json` artifacts in `runs/`.

| detector | unicode | split | auroc | auprc | tpr@1%fpr | asr |
| --- | --- | --- | --- | --- | --- | --- |
| rules_v0 | False | test_main | 0.5024 | 0.9111 | 0.0064 | 0.9936 |
| rules_v0 | True | test_main | 0.5024 | 0.9111 | 0.0064 | 0.9936 |
| rules_v0 | False | test_jbb | 0.5000 | 0.5025 | 0.0000 | 1.0000 |
| rules_v0 | True | test_jbb | 0.5000 | 0.5025 | 0.0000 | 1.0000 |
| lora | False | test_main | 0.9935 | 0.9993 | 0.9809 | 0.0191 |
| lora | True | test_main | 0.9935 | 0.9993 | 0.9777 | 0.0223 |
| lora | False | test_jbb | 0.8137 | 0.8354 | 0.9192 | 0.0808 |
| lora | True | test_jbb | 0.8089 | 0.8310 | 0.9293 | 0.0707 |

Sources:
- `runs/rules_test_main_u0/final_metrics.json`
- `runs/rules_test_main_u1/final_metrics.json`
- `runs/rules_test_jbb_u0/final_metrics.json`
- `runs/rules_test_jbb_u1/final_metrics.json`
- `runs/lora_v1_u0_20260110_182247/final_metrics_test_main.json`
- `runs/lora_v1_u1_20260110_192051/final_metrics_test_main.json`
- `runs/lora_v1_u0_20260110_182247/final_metrics_test_jbb.json`
- `runs/lora_v1_u1_20260110_192051/final_metrics_test_jbb.json`

## How to reproduce

Rules baseline (val calibration then test evaluation):
```bash
python scripts/run_rules_baseline.py --data data/v1/val.jsonl --out_dir runs/rules_val_u0
python scripts/run_rules_baseline.py --data data/v1/val.jsonl --out_dir runs/rules_val_u1 --use_unicode_preprocess
python scripts/run_rules_baseline.py --data data/v1/test_main.jsonl --out_dir runs/rules_test_main_u0
python scripts/run_rules_baseline.py --data data/v1/test_main.jsonl --out_dir runs/rules_test_main_u1 --use_unicode_preprocess
python scripts/run_rules_baseline.py --data data/v1_holdout/test_jbb.jsonl --out_dir runs/rules_test_jbb_u0
python scripts/run_rules_baseline.py --data data/v1_holdout/test_jbb.jsonl --out_dir runs/rules_test_jbb_u1 --use_unicode_preprocess

python scripts/eval_with_val_threshold.py --val_predictions runs/rules_val_u0/predictions.jsonl --test_predictions runs/rules_test_main_u0/predictions.jsonl --out runs/rules_test_main_u0/final_metrics.json
python scripts/eval_with_val_threshold.py --val_predictions runs/rules_val_u1/predictions.jsonl --test_predictions runs/rules_test_main_u1/predictions.jsonl --out runs/rules_test_main_u1/final_metrics.json
python scripts/eval_with_val_threshold.py --val_predictions runs/rules_val_u0/predictions.jsonl --test_predictions runs/rules_test_jbb_u0/predictions.jsonl --out runs/rules_test_jbb_u0/final_metrics.json
python scripts/eval_with_val_threshold.py --val_predictions runs/rules_val_u1/predictions.jsonl --test_predictions runs/rules_test_jbb_u1/predictions.jsonl --out runs/rules_test_jbb_u1/final_metrics.json
```

LoRA baseline (run the notebook twice with USE_UNICODE off/on):
- `Untitled-2_fixed_eval.ipynb`

Optional: rebuild the combined table:
```bash
python scripts/build_results_table.py --runs_dir runs --out runs/results_table.md
```
