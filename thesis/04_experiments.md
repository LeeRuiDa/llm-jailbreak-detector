# Experiments

## Timeline narrative
- Week 4: establish the final baseline checkpoint (v0.3-week4) used as the training and evaluation reference.
- Week 5: adv2 augmentation breaks threshold transfer; calibration reduces FPR but collapses TPR under distribution shift.
- Week 6: train-time robustness sweeps across two perturbation families; normalize_train is selected under a recall constraint.
- Week 7: 2x2 ablation (normalize_train x adv2 augmentation) isolates causal factors; select week7_norm_only as the final model.
