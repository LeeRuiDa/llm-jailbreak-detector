# Limitations

- Synthetic transforms (adv2, rewrite) are approximations of real-world attacks.
- Dataset shift between main and JBB splits may confound robustness attribution.
- A single fixed threshold assumes calibration stability across distribution shifts.
- Augmentation may overfit to the specific transform families implemented.
