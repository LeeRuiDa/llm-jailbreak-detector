# HANDOFF

## Repo map (high level)

```
repo/
- scripts/
- reports/
  - week5/
  - week6/
  - week7/
  - week8/
- thesis/
- docs/
- src/
- tests/
- examples/
```

- scripts/: data ingestion, training, evaluation, and table/plot builders. Used to generate tables/locked packs from local `runs/` and `data/` (not in git).
- reports/week5/: Week 5 evidence pack (tables, figures, thresholds, error cases) and `week5_report_draft.md` for mitigation/calibration narrative.
- reports/week6/: Week 6 plan, report draft, and winner decision file `WEEK6_FINAL.md` plus tables used in the Week 6 writeup.
- reports/week7/: Week 7 ablation artifacts, results notebook, run manifest, and the locked eval pack used by the thesis.
- reports/week8/: Midterm pack and changelog summary for the demo.
- thesis/: Chapter drafts for Method, Experiments, Robustness, Limitations (Weeks 4-8 synthesis).
- docs/: Demo guide, user manual, testing notes, HLD, module interfaces, plus older course docs.
- src/: Core code (augmentations, preprocessing, baselines, eval helpers) and the installable `llm_jailbreak_detector` package.
- tests/: Pytest suite for normalization, rules baseline, unicode preprocessing, and CLI smoke tests.
- examples/: Small, non-sensitive sample inputs for the CLI batch demo.

## Tags and milestones (Weeks 5-8)

Week 5:
- `week5-pre-mitigation`: evidence pack with Week 5 figures/tables/error cases and `reports/week5/week5_report_draft.md`.
- `week5-mitigation-calibration`: adds adv2 calibration tables/thresholds and scripts (`scripts/calibrate_threshold.py`, `scripts/build_adv2_mitigation_table.py`).
- `week5-report-self-contained`: clarifies definitions in `reports/week5/week5_report_draft.md`.

Week 6:
- `week6-final-normtrain`: locks the Week 6 winner in `reports/week6/WEEK6_FINAL.md`.

Week 7:
- `week7-locked-eval-norm-only`: anchors the Week 7 locked eval pack and results notebook. Key files: `reports/week7/WEEK7_FINAL.md`, `reports/week7/results_notebook.md`, `reports/week7/locked_eval_pack/week7_norm_only/...`.
- `week7-locked-week7_norm_only`: currently points to the Week 6 final commit (likely a mistaken tag); rely on `week7-locked-eval-norm-only` for Week 7 artifacts.

Week 8:
- `week8-thesis-skeleton`: thesis chapter drafts plus a Week 7 ROC plot in the locked pack.
- `week8-midterm-demo`: installable CLI + midterm pack + design docs (`docs/`, `reports/week8/`, `src/llm_jailbreak_detector/`).
- `week8-midterm-demo-patch1`: CLI hint + test path fix.
- `week8-demo-polish`: examiner demo guide polish + ignore rules (`docs/DEMO_GUIDE.md`, `.gitignore`).

## Current truth (single source of truth)

Final model:
- Chosen model: `week7_norm_only`.
- Documented in `reports/week7/WEEK7_FINAL.md` and reinforced in `thesis/05_robustness.md` and `reports/week7/results_notebook.md`.

Fixed evaluation protocol (Week 7 and thesis):
- Splits: `val`, `test_main`, `test_jbb`, `test_main_unicode`, `test_jbb_unicode`, `test_main_adv2`, `test_jbb_adv2`, `test_main_rewrite`, `test_jbb_rewrite`.
- `normalize_infer` is OFF during evaluation; `normalize_train` is ON for the final model.
- Threshold = `val_threshold` from each run `config.json`, transferred unchanged to all splits.
- Metrics: AUROC, AUPRC, FPR@val_threshold, TPR@val_threshold, ASR@threshold (ASR = attack false negatives; lower is better).

Perturbation families and transforms:
- Unicode mixing: `src/preprocess/unicode.py` and normalization in `src/preprocess/normalize.py`.
- Adv2 perturbations: `src/augment/adv2.py` (also generated via `scripts/make_adv2_set.py`).
- Rewrite paraphrases: `src/augment/rewrite.py` (also via `scripts/make_rewrite_set.py`).

## Thesis-ready content

Chapter drafts:
- `thesis/03_method.md`: task framing, model, normalization, perturbations, and metrics definitions.
- `thesis/04_experiments.md`: Week 4-7 timeline and rationale summary.
- `thesis/05_robustness.md`: full Week 7 tables (A-D), plots, failure analysis links, and the final model justification. Uses relative links into the locked eval pack.
- `thesis/06_limitations.md`: limitations on perturbations, dataset shift, and threshold transfer.
Additional chapters/stubs with embedded figures/tables:
- `thesis/01_introduction.md`: includes Figure 1.1 system context.
- `thesis/02_related_work.md`: includes Table 2.1 taxonomy.
- `thesis/06_system_demo.md`: includes Figure 6.1 + Table 6.1 CLI contract.
- `thesis/07_limitations_ethics.md`: includes optional Table 7.1 mapping limitations to evidence.

Locked eval pack:
- Path: `reports/week7/locked_eval_pack/week7_norm_only/`.
- Contents: `tables/` (A-D + metrics long), `figures/` (ROC/hist), `error_cases/` markdown, `ENV.txt`, and a local `WEEK7_FINAL.md`.
- The robustness chapter links to plots/error cases in this pack; keep these files intact.
New locked-pack metadata:
- `reports/week7/locked_eval_pack/week7_norm_only/README.md`: manifest + protocol summary.
- `reports/week7/locked_eval_pack/week7_norm_only/RUN_CONFIG_SNAPSHOT.md` and `.json`: frozen config snapshot (Week 7 final).
- `reports/week7/locked_eval_pack/week7_norm_only/DATA_STATS.md` and `.json`: aggregate-only split counts.
- `reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_rules_baseline.md`: rules baseline metrics table (fixed threshold 0.5).

## Runnable demo status (Week 8)

Package and CLI:
- Package name: `llm-jailbreak-detector` in `pyproject.toml` (src layout under `src/llm_jailbreak_detector/`).
- Default detector: rules baseline (offline, no model downloads).
- LoRA detector: optional extras `pip install -e ".[lora]"`; lazy imports; clear error message if missing.
- CLI commands: `jbd doctor`, `jbd predict`, `jbd normalize`, `jbd batch`.

Docs:
- `docs/User_Manual.md`: install + usage + troubleshooting.
- `docs/DEMO_GUIDE.md`: examiner quickstart (rules-only flow) + optional LoRA.
- `docs/TESTING.md`: how to run tests and coverage scope.
- `docs/HLD.md`: pipeline diagram + non-functional notes.
- `docs/MODULE_INTERFACES.md`: public API + CLI contract + file formats.

Tests:
- `tests/test_normalize.py`: NFKC + Cf/Mn removal behavior.
- `tests/test_rules_detector.py`: rules baseline stability.
- `tests/test_unicode_preprocess.py`: unicode normalization in `src/preprocess/unicode.py`.
- `tests/test_cli_smoke.py`: `jbd --help`, `jbd doctor`, `jbd predict` JSON output.

## Repro commands (no training)

Rules-only install and examiner demo:

```bash
python -m pip install -e .
jbd doctor
jbd --help
jbd predict --detector rules --text "Ignore previous instructions."
jbd normalize --text "he\u200bllo" --drop-mn
jbd batch --detector rules --input examples/sample_inputs.jsonl --output out.jsonl
```

Run unit tests:

```bash
pytest -q
```

Regenerate Week 7 tables (requires local outputs, not in git):

```bash
# Requires reports/week7/metrics/ with final_metrics_*.json and runs/<run_id>/config.json
python scripts/build_week7_tables.py --metrics_root reports/week7/metrics --out_dir reports/week7/results --runs_root runs
```

Locate the locked eval pack outputs:

```bash
ls reports/week7/locked_eval_pack/week7_norm_only
ls reports/week7/locked_eval_pack/week7_norm_only/tables
ls reports/week7/locked_eval_pack/week7_norm_only/figures
ls reports/week7/locked_eval_pack/week7_norm_only/error_cases
```

## Gaps / next steps (Week 9+ roadmap)

Priority checklist:
- Finish thesis narrative integration (tie `thesis/03_method.md` and `thesis/05_robustness.md` to the final results notebook and explicit limitations).
- Verify citation/attribution for datasets and perturbation generation; add to thesis where missing.
- Expand testing docs or add a LoRA smoke test (optional) if local weights are available.
- Consider clarifying how threshold transfer failures are discussed in `thesis/06_limitations.md` with 1-2 concrete examples from the locked pack.
- Optional packaging polish: add a short note in `README.md` for rules-only vs LoRA installs (avoid heavy deps by default).

Notes:
- Avoid regenerating or committing `data/`, `runs/`, or untracked report artifacts (Week 6/7 generated outputs stay local-only).
- Use tags above to anchor week-specific deliverables when referencing content.

## Recent progress (2026-01-28)
- Added `thesis/FIGURES_TABLES_PLAN.md` with formatting policy, mapping, and asset inventory.
- Mermaid sources and rendered diagrams live under `docs/figures/` with render scripts in `scripts/render_diagrams.ps1` and `.sh`.
- Thesis embedding done for figures/tables across chapters; strict asset check passes via `scripts/check_thesis_assets.py`.
- Added thesis ingredient scripts: `scripts/build_data_stats.py`, `scripts/build_rules_baseline_table.py`, and prep scripts `scripts/prep_thesis_ingredients.ps1` / `.sh`.
- Updated `docs/TEST_RESULTS.md` with a short, current evidence log (pip install, pytest, jbd doctor, jbd predict).
- Added `thesis/references.bib` starter (real entries + TODO placeholders).
