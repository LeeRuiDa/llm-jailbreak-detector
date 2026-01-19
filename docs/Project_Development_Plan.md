# Project Development Plan (v1)

## Goal
Build a low-false-positive (≤1% FPR) detector for jailbreak & prompt injection inputs.

## Milestones
- Dataset v1 + baselines
- LoRA classifier pipeline
- Adversarial evaluation + ablations
- Final software package + thesis

## Risks & Mitigations
- Data quality/labels: add validation + manual spot checks
- Limited GPU: keep a "lightweight mode" (smaller backbone)
- False positives: focus evaluation on strict operating point (TPR@1%FPR)

## Weekly cadence
- Weekly progress report to supervisor
- 1 guidance record entry per week
