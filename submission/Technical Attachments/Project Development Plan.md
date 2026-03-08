# Project Development Plan

## Objective
Deliver a graduation-ready capstone project that demonstrates an offline-capable jailbreak and prompt-injection detector, a reproducible ML pipeline, a locked evaluation pack for thesis reporting, and a stable CLI demo that examiners can run locally.

## Planned milestones and actual outcome

| Phase | Planned output | Actual evidence | Status |
| --- | --- | --- | --- |
| Week 4 | Establish baseline dataset flow and first detector | `WEEK4_FINAL.md`, `reports/week4/` | Completed |
| Week 5 | Robustness analysis and threshold-calibration experiments | `reports/week5/`, threshold reports, perturbation results | Completed |
| Week 6 | Decide the final experiment direction and candidate model | `reports/week6/WEEK6_FINAL.md`, `reports/week6/week6_experiment_plan.md` | Completed |
| Week 7 | Freeze final run, build locked pack, and finalize thesis evidence | `reports/week7/locked_eval_pack/week7_norm_only/`, `reports/week7/WEEK7_FINAL.md` | Completed |
| Week 8+ | Package runnable software, thesis chapters, and submission artifacts | `README.md`, `demo/`, `submission/`, thesis chapters, technical attachments | In progress during final submission pass |

## Work breakdown

### Product and software work
- Build an installable CLI package with `predict`, `batch`, `normalize`, and `doctor` commands.
- Maintain a deterministic rules baseline that always runs offline.
- Support optional LoRA inference from local run artifacts.
- Provide a safe demo path that does not depend on external APIs or hidden services.

### ML and evaluation work
- Define a canonical JSONL schema and split grid.
- Train and evaluate a LoRA classifier under a fixed low-FPR operating point.
- Generate unicode, adv2, and rewrite stress splits.
- Freeze the Week 7 locked evaluation pack for thesis reporting.

### Thesis and submission work
- Keep thesis chapters aligned to the locked pack and the actual runtime surface.
- Package school-required technical attachments: Project Development Plan, Requirements Specification, Design Documentation, Testing Documentation, and User Manual.
- Provide a submission-ready evidence manifest and an examiner-facing demo workflow.

## Success criteria
- Software installs locally with `pip install -e .` and exposes the `jbd` entrypoint.
- `pytest -q` and CLI smoke checks pass in the submission environment.
- The thesis cites a single final run (`week7_norm_only`) and uses only locked-pack counts and metrics.
- The project clearly states its claim boundary: reproducible research prototype, not production-ready guardrail.
- Submission bundle contains the required technical attachments with school-facing names.

## Key risks and mitigations

| Risk | Why it matters | Mitigation actually used |
| --- | --- | --- |
| Dataset leakage or duplicate families across splits | Inflates measured generalization | `group_id` checks and dataset validation in `scripts/validate_dataset.py` |
| Threshold instability at very low FPR | Can make demo and thesis claims unreliable | calibrate on `val`, freeze `val_threshold`, report transfer failures explicitly |
| Missing local ML artifacts during defense | Could break the live demo | rules-only path remains the guaranteed demo surface |
| Proposal overreach versus runnable evidence | Committee can reject incomplete deliverables | explicit scope narrowing and proposal-alignment matrix in `submission/Evidence/` |
| Thesis and repo drift | Defense risk if chapters overclaim runtime features | this final pass synchronizes thesis chapters, manuals, and traceability docs to the actual code |

## Final deliverables
- Installable software package: `src/llm_jailbreak_detector/`, `pyproject.toml`, `demo/`
- Locked evaluation evidence: `reports/week7/locked_eval_pack/week7_norm_only/`
- Thesis chapters and bibliography: `thesis/`, `thesis ready chapters/`, `thesis/references.bib`
- Technical attachments: `docs/Project_Development_Plan.md`, `docs/Requirements_Specification.md`, `docs/Design_Documentation.md`, `docs/Testing_Documentation.md`, `docs/User_Manual.md`
- School-facing bundle: `submission/`

## Completion state at submission pass
The engineering pass is complete enough for a portfolio-grade repo. The remaining priority work in this final pass is academic correctness: unify split counts to the locked pack, remove unsupported runtime claims, narrow the external-guardrail comparison claim honestly, and package the submission artifacts in one obvious location.