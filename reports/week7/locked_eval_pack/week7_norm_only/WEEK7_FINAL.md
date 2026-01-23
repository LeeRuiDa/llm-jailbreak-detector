# Week 7 Final (Ablations)

winner_run_id: week7_norm_only

factors:
- normalize_train: true
- aug_adv2_prob: 0.0
- aug_rewrite_prob: 0.0
- aug_seed: 42

eval_protocol:
- script: scripts/eval_week7_grid.py
- splits: val, test_main, test_jbb, test_main_unicode, test_jbb_unicode, test_main_adv2, test_jbb_adv2, test_main_rewrite, test_jbb_rewrite
- normalize_infer: off
- threshold: val_threshold from config.json

decision_commit: 91ae94e334944206ad7104ad010739c8a6671f16

rationale:
- Table D: adv2-only reduces adv2 mean FPR by -0.4094 but drops adv2 mean TPR by -0.0847.
- Table D: norm+adv2 reduces adv2 mean FPR by -0.4725 with TPR -0.1313.
- Table D: norm-only improves adv2 mean FPR by -0.0466 with minimal TPR loss (-0.0135) and clean/unicode deltas near zero.
- Table C: JBB adv2 TPR collapses for adv2-only (0.7677) and norm+adv2 (0.6768) vs control (0.9495).
