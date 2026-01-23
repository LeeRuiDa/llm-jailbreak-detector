# Limitations

- Synthetic perturbations (adv2, rewrite, unicode) approximate real-world attacks and may miss unseen tactics.
- Dataset shift between main and JBB splits can confound robustness attribution.
- A single fixed threshold assumes calibration stability across distribution shifts.
- Augmentation can overfit to the specific perturbation families implemented.
