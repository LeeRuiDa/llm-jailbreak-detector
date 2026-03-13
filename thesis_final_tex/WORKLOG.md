# Thesis Final TeX Worklog

## Scope of this pass
Built a clean LaTeX thesis package under `thesis_final_tex/` using `thesis ready chapters/` as the primary narrative source, with the locked Week 7 evaluation pack and the shipped runtime as authoritative evidence.

## Chapters converted
- `chapters/00_abstract.tex` from `thesis ready chapters/abstract.txt`
- `chapters/01_introduction.tex` from `01_introduction_thesis_updated.md`
- `chapters/02_related_work.tex` from `02_related_work_thesis_updated_v2.md`
- `chapters/03_method.tex` from `ch3 method.tex.txt` plus locked-pack and runtime cross-checks
- `chapters/04_experiments.tex` from `ch4 exp.tex.txt` plus locked-pack tables
- `chapters/05_robustness.tex` from `ch 5 robustness.tex.txt`
- `chapters/06_system_demo.tex` from `ch6_system_demo_revised_v2.md` aligned to current CLI/runtime
- `chapters/07_limitations_ethics.tex` from `ch7_limitations_ethics_defense_proof.md`
- `chapters/08_conclusion.tex` from `ch 8 conclusion.txt`

## Figures resolved
Copied existing repo figures into `figures/`:
- `ch1_system_context.png`
- `ch3_pipeline.png`
- `ch3_eval_protocol.png`
- `ch6_component_diagram.png`
- `roc_week7_norm_only_test_main_adv2.png`
- `roc_week7_norm_only_test_main_rewrite.png`
- `hist_week7_norm_only_test_main_adv2.png`
- `roc_week7_norm_only_test_jbb_adv2.png`
- `hist_week7_norm_only_test_jbb_adv2.png`

No figures were fabricated.

## Tables converted
Created LaTeX-native tables in `tables/`:
- related-work threat table
- Week 7 split counts
- final model configuration
- evaluation split counts
- clean and Unicode results
- adv2 and rewrite results
- ablation summary
- rules baseline summary
- final-model threshold-transfer summary
- CLI contract table

## Citation and consistency checks
- copied bibliography to `bibliography/references.bib`
- used only active citation keys present in `thesis/references.bib`
- removed stale split counts from the final LaTeX package
- did not reintroduce unsupported runtime features
- kept proposal narrowing explicit
- kept delimiter escaping framed as a limitation, not an implemented safeguard
- Day 10 static pass: no missing citation keys in active `.tex` sources
- Day 10 static pass: no missing `\ref{}` labels in active `.tex` sources
- Day 10 static pass: no missing figure or `\input{}` targets in `thesis_final_tex/`
- Day 10 hostile read: overclaim markers remain only in negative or scope-narrowing statements

## Build status
Compilation was **not executed** because no LaTeX engine (`pdflatex`, `xelatex`, `lualatex`, or `latexmk`) was available on PATH in this environment.

Intended build command:
```bash
cd thesis_final_tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Remaining blockers
- fill title-page placeholders: university, faculty, supervisor, student ID, and programme name
- run a real LaTeX build once a TeX toolchain is installed
- review pagination and line breaks after the first successful compile
- if the institution requires a specific thesis class or formatting template, adapt `main.tex` to that class

## Final checklist
- [x] chapters converted
- [x] figures resolved
- [x] tables converted
- [x] bibliography copied and active keys aligned
- [x] Week 7 counts and metrics aligned to locked pack
- [x] Chapter 6 aligned to current CLI/runtime
- [x] proposal narrowing stated honestly
- [ ] compiled PDF produced

## Final source pass after the PDF review
Applied the remaining thesis-source fixes identified in the post-PDF gap review:
- corrected Chapter 1 and Chapter 4 formatting artifacts caused by literal `r`n text in intermediate edits
- added Chapter 3 dataset provenance and source-composition coverage (`tab3_dataset_sources.tex`)
- added Chapter 3 LoRA formalization, classifier-head mapping, and explicit unweighted-loss / imbalance-handling statement
- added Chapter 5 perturbation-operator formalization for Unicode, adv2, and rewrite
- tightened the evaluation framing so the split grid is explicitly described as a threshold-transfer stress study rather than a benign-heavy production simulation
- narrowed RQ3 wording to match the delivered comparison story (rules baseline vs optional learned detector within the shipped runtime)
- regenerated the Chapter 4 and 5 evaluation plots from frozen `predictions_*.jsonl` files with explicit transferred-threshold markers
- added Chapter 6 requirements and measured runtime evidence tables (`tab6_requirements.tex`, `tab6_runtime_benchmark.tex`)
- recorded an honest runtime benchmark result: rules mode measured successfully on the current CPU-only workspace, while LoRA timing was unavailable because the local backbone cache was absent

## Additional generated artifacts in this pass
- `scripts/render_thesis_eval_figures.py`
- `scripts/benchmark_thesis_runtime.py`
- `thesis_final_tex/runtime_benchmark.json`
- updated threshold-aware figure copies in `thesis_final_tex/figures/`

## Final static checks after the source pass
- no `TODO`, `TBD`, or `todo_` markers remain inside `thesis_final_tex/`
- no stale split-count strings (`29,310`, `68,888`, `1115`, `1/1115`, `0.09%`) remain in active thesis sources
- no unsupported runtime claims (`--redact`, `text_sha256`, `text_truncated`, surfaced `threshold_source`) remain in active thesis sources
- no missing `\input{}` or `\includegraphics{}` targets were detected in `thesis_final_tex/`
- active `\cite{}` keys resolve against `bibliography/references.bib`

## Remaining manual-only items after this pass
- rebuild the PDF from the updated `thesis_final_tex/` sources so the compiled thesis matches the latest fixes
- fill the final title-page metadata you want to ship (title wording if you want to revert it, institution fields, and final submission date)
- review float placement and table density after the rebuilt PDF is rendered
- if your school enforces a thesis class/template, port `main.tex` into that template before final export