# Requirements Specification (v1)

## Functional requirements
- Ingest prompt + optional retrieved context
- Produce risk score in [0,1] and a decision at a chosen threshold
- Support multiple detector backends (rules baseline, ML model)

## Non-functional requirements
- Must support evaluation at ≤1% false-positive rate
- Reproducible runs: save config + metrics + predictions
- Clear user instructions (install & run)

## Evaluation requirements
- Report AUROC, AUPRC, TPR@1%FPR, ASR
