# Threshold Transfer Analysis

val_threshold: 0.759439

| split | fpr_at_val_threshold | tpr_at_val_threshold | asr_at_threshold |
| --- | --- | --- | --- |
| val | 0.0091 | 0.9686 | 0.0314 |
| test_main | 0.0308 | 0.9898 | 0.0102 |
| test_main_unicode | 0.0410 | 0.9888 | 0.0112 |
| test_jbb | 0.6429 | 0.9798 | 0.0202 |
| test_jbb_unicode | 0.6837 | 0.9798 | 0.0202 |

Interpretation:
- The val threshold transfers cleanly to test_main with low FPR and near-ceiling TPR.
- test_main_unicode remains strong with only a small FPR increase vs clean.
- JBB splits show a large FPR jump at the same threshold, suggesting distribution shift.
- Despite higher FPR on JBB, TPR remains high and ASR stays low.
- Week 5 should prioritize calibration or split-specific operating points for JBB-style data.
