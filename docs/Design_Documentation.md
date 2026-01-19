# Design Documentation (v1)

## High-level architecture
Data -> (raw / unicode-processed) -> detector -> scores -> evaluation -> reports

## Modules
- data.io: load/validate schema
- preprocess.unicode: normalize + flag suspicious characters
- baselines.rules: heuristic detector
- eval.metrics: metrics (AUROC/AUPRC/TPR@FPR/ASR)
- scripts/run_*: runnable entry points
