# Scope Narrowing Note: External Guardrail Comparison

## Original proposal expectation
The approved proposal named comparison against existing guardrails such as Llama Guard 2, Prompt Guard, ProtectAI-style detectors, and a rules baseline.

## Submission-time check performed
During the final submission pass, the local environment was checked for a reproducible local integration path for those proposal-named systems.

Observed constraints:
- repository search across `src/`, `scripts/`, `docs/`, `reports/`, `thesis/`, and `thesis ready chapters/` found no runnable local integration or benchmark harness for Llama Guard, Prompt Guard, or ProtectAI
- local Hugging Face cache inspection found no matching cached guardrail models
- local Python site-packages inspection found no matching package directories for those proposal-named systems
- hosted API comparison was rejected because it would violate the project's offline-first, examiner-reproducible framing

## Final decision
The final submission narrows the proposal from an external-guardrail bakeoff to an offline reproducible detector study.

What is still delivered:
- canonical dataset/preprocessing pipeline
- offline rules baseline
- learned LoRA detector
- locked robustness evaluation pack
- runnable local software and technical attachments

What is not claimed as delivered:
- a reproducible benchmark against Llama Guard 2, Prompt Guard, or ProtectAI in the submission environment

## Thesis wording requirement
The thesis must state this narrowing explicitly and must not imply that the external comparison was completed.