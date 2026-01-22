# Week 6 Final (Winner)

winner_run_id: lora_v1_deberta_normtrain
parent_model: lora_v1_microsoft-deberta-v3-base_u0_20260118_153344 (Week 4 final checkpoint baseline)

train_time_toggles:
- normalize_train: true
- normalize_drop_mn: false
- aug_adv2_prob: 0.0
- aug_rewrite_prob: 0.0
- aug_seed: 42

eval_protocol:
- script: scripts/eval_week6_grid.py
- splits: val, test_main, test_jbb, test_main_unicode, test_jbb_unicode, test_main_adv2, test_jbb_adv2, test_main_rewrite, test_jbb_rewrite
- normalize_infer: off
- threshold: val_threshold from run config.json

decision_commit: ed47a08f4289ab367978225f5d9fc467371b9e7e

rationale:
Meets clean/unicode constraints with minimal recall loss, improves transfer without recall collapse.
Adv2-train reduces FPR but collapses JBB adv2 recall; norm-train is the safest operating-point transfer.
