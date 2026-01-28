# Figures & Tables Plan

Locked eval pack is the source of truth for quantitative results. All result figures/tables in this plan reference files under `reports/week7/locked_eval_pack/week7_norm_only/`.

## Formatting policy
- 300 DPI minimum
- Consistent widths (e.g., 12–14 cm)
- PNG for plots; SVG/PDF allowed for diagrams if the thesis template supports them
- Consistent font size in plots

Canonical diagram location: docs/figures/ (Thesis includes images from docs/figures/).

Table renumbering note: locked pack Table A/B/C/D are cited as Table 4.1/4.2/5.1/4.3 in the thesis.

## Summary checklist (by chapter)
- Chapter 1: Figure 1.1
- Chapter 2: Table 2.1
- Chapter 3: Figure 3.1, Figure 3.2, Table 3.1
- Chapter 4: Figure 4.1, Figure 4.2, Figure 4.3, Table 4.1, Table 4.2, Table 4.3
- Chapter 5: Figure 5.1, Figure 5.2 (optional), Table 5.1
- Chapter 6: Figure 6.1, Table 6.1
- Chapter 7: Optional Table 7.1 (if included)
- Chapter 8: Appendix references (non-figure/table links)

## Scanned assets (locked eval pack + docs)
- Locked-pack tables: reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_A_clean_unicode.md; reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_B_adv2_rewrite.md; reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_C_threshold_transfer.md; reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_D_ablation_effects.md
- Locked-pack figures: reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_main_adv2.png; reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_main_rewrite.png; reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_jbb_adv2.png; reports/week7/locked_eval_pack/week7_norm_only/figures/hist_week7_norm_only_test_main_adv2.png; reports/week7/locked_eval_pack/week7_norm_only/figures/hist_week7_norm_only_test_jbb_adv2.png
- Locked-pack error cases: reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fn.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fp.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_rewrite_fn.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_rewrite_fp.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fn.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fp.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_rewrite_fn.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_rewrite_fp.md
- Thesis sources: thesis/03_method.md; thesis/04_experiments.md; thesis/05_robustness.md; thesis/06_limitations.md
- Architecture/interface sources: docs/HLD.md; docs/MODULE_INTERFACES.md

## Detailed entries by chapter

### Chapter 1 (Ch1.1–1.6)
Figure 1.1 — System context diagram (Prompt/context -> detector -> allow/block -> LLM)
Placement: Chapter 1.3
Source path(s): docs/figures/ch1_system_context.mmd (to create); docs/figures/ch1_system_context.png (to create)
What it demonstrates: The end-to-end guardrail context, showing where the detector sits between user input and the target LLM and how decisions route to allow/block.
Generation: Needs generation — create a Mermaid diagram at docs/figures/ch1_system_context.mmd and export with `mmdc -i docs/figures/ch1_system_context.mmd -o docs/figures/ch1_system_context.png`.
Install: `npm install -g @mermaid-js/mermaid-cli`
Note: `mmdc` must be on PATH.

### Chapter 2 (Ch2.1–2.4)
Table 2.1 — Threat taxonomy vs defenses vs weaknesses
Placement: Chapter 2.2
Source path(s): thesis/03_method.md; thesis/05_robustness.md; thesis/06_limitations.md
What it demonstrates: A concise mapping from threat types (unicode, adv2, rewrite) to the defenses evaluated (normalization, augmentation, fixed thresholding) and the observed weaknesses/limits described in the thesis text.
Generation: Needs generation — manually author the table in the Chapter 2 manuscript using the sources above (no script).

### Chapter 3 (Ch3.1–3.6)
Figure 3.1 — Pipeline diagram (Input -> Normalization -> Detector -> Decision -> Output)
Placement: Chapter 3.2
Source path(s): docs/HLD.md (Mermaid source); docs/figures/ch3_pipeline.mmd (to create); docs/figures/ch3_pipeline.png (to create)
What it demonstrates: The operational pipeline of the detector, aligned with the method description and implementation components.
Generation: Needs generation — copy the Mermaid flowchart from docs/HLD.md into docs/figures/ch3_pipeline.mmd and export with `mmdc -i docs/figures/ch3_pipeline.mmd -o docs/figures/ch3_pipeline.png`.
Install: `npm install -g @mermaid-js/mermaid-cli`
Note: `mmdc` must be on PATH.

Figure 3.2 — Evaluation protocol diagram (val threshold -> fixed transfer to all splits)
Placement: Chapter 3.5
Source path(s): thesis/03_method.md; docs/figures/ch3_eval_protocol.mmd (to create); docs/figures/ch3_eval_protocol.png (to create)
What it demonstrates: The evaluation protocol, emphasizing the single validation threshold that is transferred unchanged across all test splits.
Generation: Needs generation — create a Mermaid diagram at docs/figures/ch3_eval_protocol.mmd and export with `mmdc -i docs/figures/ch3_eval_protocol.mmd -o docs/figures/ch3_eval_protocol.png`.
Install: `npm install -g @mermaid-js/mermaid-cli`
Note: `mmdc` must be on PATH.

Table 3.1 — Metrics definitions (AUROC, AUPRC, FPR@threshold, TPR@threshold, ASR@threshold)
Placement: Chapter 3.6
Source path(s): thesis/03_method.md
What it demonstrates: The exact metric definitions used throughout evaluation to ensure consistent interpretation of result tables and plots.
Generation: Needs generation — manually author the table in the Chapter 3 manuscript using thesis/03_method.md (no script).

### Chapter 4 (Ch4.1–4.4)
Table 4.1 — Table A: Clean + Unicode results
Placement: Chapter 4.2
Source path(s): reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_A_clean_unicode.md
What it demonstrates: Baseline and unicode-mixed performance across splits under the locked evaluation grid.
Generation: Already committed (locked eval pack).

Table 4.2 — Table B: Adv2 + Rewrite results
Placement: Chapter 4.3
Source path(s): reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_B_adv2_rewrite.md
What it demonstrates: Robustness outcomes under adv2 and rewrite perturbations across runs and splits.
Generation: Already committed (locked eval pack).

Table 4.3 — Table D: Ablation effects (delta vs control)
Placement: Chapter 4.4
Source path(s): reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_D_ablation_effects.md
What it demonstrates: The isolated effect of normalization and adv2 augmentation relative to the control condition.
Generation: Already committed (locked eval pack).

Figure 4.1 — ROC curve for week7_norm_only on test_main_adv2
Placement: Chapter 4.3
Source path(s): reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_main_adv2.png
What it demonstrates: Classification tradeoffs under adversarial character-level perturbations on the main split.
Generation: Already committed (locked eval pack).

Figure 4.2 — ROC curve for week7_norm_only on test_main_rewrite
Placement: Chapter 4.3
Source path(s): reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_main_rewrite.png
What it demonstrates: Detection behavior under rewrite perturbations on the main split.
Generation: Already committed (locked eval pack).

Figure 4.3 — Score histogram for week7_norm_only on test_main_adv2
Placement: Chapter 4.3
Source path(s): reports/week7/locked_eval_pack/week7_norm_only/figures/hist_week7_norm_only_test_main_adv2.png
What it demonstrates: Score distribution shift for adv2 on the main split, highlighting overlap near the transferred threshold.
Generation: Already committed (locked eval pack).

### Chapter 5 (Ch5.1–5.4)
Table 5.1 — Table C: Threshold transfer summary
Placement: Chapter 5.2
Source path(s): reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_C_threshold_transfer.md
What it demonstrates: How a single validation threshold transfers across perturbation families and splits.
Generation: Already committed (locked eval pack).

Figure 5.1 — ROC curve for week7_norm_only on test_jbb_adv2
Placement: Chapter 5.3
Source path(s): reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_jbb_adv2.png
What it demonstrates: Robustness behavior under adv2 on the JBB split, illustrating distribution shift sensitivity.
Generation: Already committed (locked eval pack).

Figure 5.2 (optional) — Score histogram for week7_norm_only on test_jbb_adv2
Placement: Chapter 5.3
Source path(s): reports/week7/locked_eval_pack/week7_norm_only/figures/hist_week7_norm_only_test_jbb_adv2.png
What it demonstrates: Score distribution shift for adv2 on the JBB split, highlighting overlap near the transferred threshold.
Generation: Already committed (locked eval pack).

### Chapter 6 (Ch6.1–6.5)
Figure 6.1 — Component diagram (CLI, core library, detectors, eval/scripts)
Placement: Chapter 6.2
Source path(s): docs/HLD.md; docs/figures/ch6_component_diagram.mmd (to create); docs/figures/ch6_component_diagram.png (to create)
What it demonstrates: The implementation-level components and their relationships, grounding the system view in concrete modules.
Generation: Needs generation — create a Mermaid component diagram at docs/figures/ch6_component_diagram.mmd and export with `mmdc -i docs/figures/ch6_component_diagram.mmd -o docs/figures/ch6_component_diagram.png`.
Install: `npm install -g @mermaid-js/mermaid-cli`
Note: `mmdc` must be on PATH.

Table 6.1 — CLI contract (command -> input -> output)
Placement: Chapter 6.4
Source path(s): docs/MODULE_INTERFACES.md
What it demonstrates: The exact command surface and I/O schema for reproducible usage and evaluation.
Generation: Needs generation — manually author the table in the Chapter 6 manuscript using docs/MODULE_INTERFACES.md (no script).

### Chapter 7 (Ch7.1–7.5)
Table 7.1 — Optional limitations-to-evidence mapping
Placement: Chapter 7.3
Source path(s): thesis/06_limitations.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fp.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fn.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fp.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fn.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_rewrite_fp.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_rewrite_fn.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_rewrite_fp.md; reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_rewrite_fn.md
What it demonstrates: A compact mapping from each listed limitation to concrete error-case evidence in the locked pack.
Generation: Needs generation — manually author the table in the Chapter 7 manuscript using the sources above (no script).

### Chapter 8 (Appendices)
Appendix references (non-figure/table links): docs/User_Manual.md; docs/DEMO_GUIDE.md; docs/TESTING.md; docs/HLD.md; docs/MODULE_INTERFACES.md

## Gaps and creation plan (non-locked assets)
Figure 1.1, Figure 3.1, Figure 3.2, Figure 6.1, Table 2.1, Table 3.1, and Table 6.1 require new assets or manual authoring; these are listed above with exact creation paths and commands.
Table 7.1 is optional and should be included only if the Chapter 7 outline calls for explicit evidence mapping.
If Node/npm is unavailable, Mermaid PNG rendering may be deferred. Mermaid .mmd sources + render scripts remain the reproducibility anchor; diagrams can be rendered later using mmdc when available.

## Asset inventory (all referenced paths)
docs/HLD.md
docs/MODULE_INTERFACES.md
docs/User_Manual.md
docs/DEMO_GUIDE.md
docs/TESTING.md
docs/figures/ch1_system_context.mmd
docs/figures/ch1_system_context.png
docs/figures/ch3_pipeline.mmd
docs/figures/ch3_pipeline.png
docs/figures/ch3_eval_protocol.mmd
docs/figures/ch3_eval_protocol.png
docs/figures/ch6_component_diagram.mmd
docs/figures/ch6_component_diagram.png
reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_A_clean_unicode.md
reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_B_adv2_rewrite.md
reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_C_threshold_transfer.md
reports/week7/locked_eval_pack/week7_norm_only/tables/week7_table_D_ablation_effects.md
reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_main_adv2.png
reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_main_rewrite.png
reports/week7/locked_eval_pack/week7_norm_only/figures/roc_week7_norm_only_test_jbb_adv2.png
reports/week7/locked_eval_pack/week7_norm_only/figures/hist_week7_norm_only_test_main_adv2.png
reports/week7/locked_eval_pack/week7_norm_only/figures/hist_week7_norm_only_test_jbb_adv2.png
reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fn.md
reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_adv2_fp.md
reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_rewrite_fn.md
reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_jbb_rewrite_fp.md
reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fn.md
reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_adv2_fp.md
reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_rewrite_fn.md
reports/week7/locked_eval_pack/week7_norm_only/error_cases/test_main_rewrite_fp.md
thesis/03_method.md
thesis/04_experiments.md
thesis/05_robustness.md
thesis/06_limitations.md
