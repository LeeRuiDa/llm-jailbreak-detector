# Method

## 3.1 Task and labels
This work treats guardrail detection as a binary classification task over user prompts.
The positive class is attack (harmful or policy-violating request) and the negative class is benign.

## 3.2 Pipeline
![Figure 3.1: Detection pipeline from input through normalization, detector, decision, and output.](docs/figures/ch3_pipeline.png)

## 3.3 Model
Backbone: DeBERTa v3 base with a LoRA adapter (r=8, alpha=16, dropout=0.05) and a binary classification head.

## 3.4 Training recipe
All Week 5-7 runs use the same training recipe as the Week 4 baseline (v0.3-week4), with hyperparameters locked.

## 3.5 Evaluation protocol
- Fixed evaluation grid across val and all test splits.
- Threshold is learned on val (val_threshold in run config.json) and transferred unchanged to every split.
- Metrics reported: AUROC, AUPRC, FPR@val_threshold, TPR@val_threshold, ASR@threshold.

![Figure 3.2: Evaluation protocol with a validation threshold transferred unchanged to all test splits.](docs/figures/ch3_eval_protocol.png)

## 3.6 Terminology + metrics
- FPR@threshold: false positives among benign at the transferred threshold.
- TPR@threshold: true positives among attacks at the transferred threshold.
- ASR@threshold: false negatives on attacks (attack success rate) at the transferred threshold; lower is better.

Table 3.1: Metrics definitions used in all evaluations.
| Metric | Definition |
| --- | --- |
| AUROC | Area under the receiver operating characteristic curve. |
| AUPRC | Area under the precision-recall curve. |
| FPR@threshold | False positives among benign at the transferred threshold. |
| TPR@threshold | True positives among attacks at the transferred threshold. |
| ASR@threshold | False negatives on attacks at the transferred threshold (lower is better). |
