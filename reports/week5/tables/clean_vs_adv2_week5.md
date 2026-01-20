# Clean vs adv2 (Final Run)

run: lora_v1_microsoft-deberta-v3-base_u0_20260118_153344

| split | auroc | tpr_at_val_threshold | fpr_at_val_threshold | asr_at_threshold |
| --- | --- | --- | --- | --- |
| test_main | 0.9962 | 0.9898 | 0.0308 | 0.0102 |
| test_main_adv2 | 0.6376 | 0.9974 | 0.8081 | 0.0026 |
| test_jbb | 0.9181 | 0.9798 | 0.6429 | 0.0202 |
| test_jbb_adv2 | 0.6240 | 0.9495 | 0.9184 | 0.0505 |
