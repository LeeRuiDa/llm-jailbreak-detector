# Evidence for Chapter 3 Method

## Task and schema
- Canonical loader schema requires `id`, `text`, `label`, `attack_type`, `source`, `group_id`, with optional `meta`. Evidence: `src/data/io.py`, `docs/data_schema.md`.
- `label=1` is the attack class used for training and evaluation. Evidence: `src/data/io.py`, `scripts/train_lora.py`.

## Prompt/context representation
- Ingestion assembles prompt and optional context into one `text` payload using `[PROMPT]` / `[CONTEXT]`. Evidence: `scripts/dataset_utils.py`, `scripts/ingest_bipia.py`, `scripts/ingest_jailbreakdb.py`.
- Explicit escaping of delimiter-like marker lines is not enforced in code. Evidence: `scripts/dataset_utils.py`, `docs/TRACEABILITY_MATRIX.md`.

## Locked split counts
Authoritative Week 7 counts are in `reports/week7/locked_eval_pack/week7_norm_only/DATA_STATS.md`:
- `train`: 201,276 total; 14,859 benign; 186,417 attack
- `val`: 6,106 total; 3,082 benign; 3,024 attack
- `test_main`: 35,230 total; 3,147 benign; 32,083 attack
- `test_jbb`: 197 total; 98 benign; 99 attack

## Detectors and preprocessing
- Rules baseline: `src/baselines/rules.py`, `src/llm_jailbreak_detector/rules_detector.py`.
- LoRA detector: `src/llm_jailbreak_detector/lora_detector.py` with local artifacts only.
- Final Week 7 normalization policy: `normalize_train=true`, `normalize_infer=false`, `unicode_preprocess=false`. Evidence: `runs/week7_norm_only/config.json`, `reports/week7/locked_eval_pack/week7_norm_only/RUN_CONFIG_SNAPSHOT.md`.

## Operating point and artifacts
- Threshold is calibrated on `val` with target FPR 1% and transferred unchanged. Evidence: `src/eval/metrics.py`, `scripts/train_lora.py`, `reports/week7/locked_eval_pack/week7_norm_only/README.md`.
- With 3,082 benign validation examples, the minimum FPR step is about `1/3082 ~= 0.0324%`. Evidence: `reports/week7/locked_eval_pack/week7_norm_only/DATA_STATS.md`, `thesis/03_method.md`.
- Training selects the best checkpoint by validation `tpr_at_fpr` with AUROC tie-break and saves `best_metrics.json`. Evidence: `scripts/train_lora.py`.
- Evaluation records sidecar metadata in `evaluation_manifest.json` rather than mutating `config.json`. Evidence: `scripts/eval_lora_from_run.py`.

## Locked protocol
- Final run: `week7_norm_only`.
- Locked pack contents: tables, figures, error cases, environment summary, run snapshot, aggregate data stats. Evidence: `reports/week7/locked_eval_pack/week7_norm_only/README.md`.