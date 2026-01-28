# Rules baseline (fixed threshold = 0.5; no val threshold transfer)

| run | split | auroc | auprc | val_threshold | fpr_at_val_threshold | tpr_at_val_threshold | asr_at_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rules_baseline | test_main | 0.5024 | 0.9111 | 0.5000 | 0.0016 | 0.0064 | 0.9936 |
| rules_baseline | test_main_unicode | 0.5009 | 0.9108 | 0.5000 | 0.0010 | 0.0028 | 0.9972 |
| rules_baseline | test_main_adv2 | 0.5007 | 0.9108 | 0.5000 | 0.0000 | 0.0015 | 0.9985 |
| rules_baseline | test_jbb_adv2 | 0.5000 | 0.5025 | 0.5000 | 0.0000 | 0.0000 | 1.0000 |
| rules_baseline | test_main_rewrite | 0.5021 | 0.9110 | 0.5000 | 0.0016 | 0.0057 | 0.9943 |
