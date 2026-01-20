# Final Model Summary

run: lora_v1_microsoft-deberta-v3-base_u0_20260118_153344

| split | auroc | auprc | val_threshold | fpr_at_val_threshold | tpr_at_val_threshold | asr_at_threshold |
| --- | --- | --- | --- | --- | --- | --- |
| val | 0.9983 | 0.9983 | 0.7594 | 0.0091 | 0.9686 | 0.0314 |
| test_main | 0.9962 | 0.9996 | 0.7594 | 0.0308 | 0.9898 | 0.0102 |
| test_main_unicode | 0.9951 | 0.9995 | 0.7594 | 0.0410 | 0.9888 | 0.0112 |
| test_jbb | 0.9181 | 0.9155 | 0.7594 | 0.6429 | 0.9798 | 0.0202 |
| test_jbb_unicode | 0.8995 | 0.9004 | 0.7594 | 0.6837 | 0.9798 | 0.0202 |
