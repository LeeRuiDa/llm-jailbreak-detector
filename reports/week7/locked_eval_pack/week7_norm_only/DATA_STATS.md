# Dataset statistics (aggregate only)

All statistics are computed by streaming JSONL rows and counting labels. No raw prompts or ids are stored in this report.

| split | total | attack | benign | attack_rate |
| --- | --- | --- | --- | --- |
| test_jbb | 197 | 99 | 98 | 0.502538 |
| test_jbb_adv2 | 197 | 99 | 98 | 0.502538 |
| test_jbb_rewrite | 197 | 99 | 98 | 0.502538 |
| test_jbb_unicode | 197 | 99 | 98 | 0.502538 |
| test_main | 35230 | 32083 | 3147 | 0.910673 |
| test_main_adv2 | 35230 | 32083 | 3147 | 0.910673 |
| test_main_rewrite | 35230 | 32083 | 3147 | 0.910673 |
| test_main_unicode | 35230 | 32083 | 3147 | 0.910673 |
| train | 201276 | 186417 | 14859 | 0.926176 |
| val | 6106 | 3024 | 3082 | 0.495251 |
