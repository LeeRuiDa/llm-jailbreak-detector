# Truncation Overflow Summary

- tokenizer_path: `C:/Users/LENOVO/Desktop/Capstone Project/llm-guardrail-capstone-starter/runs/week7_norm_only/lora_adapter`
- tokenizer_family: `microsoft/deberta-v3-base`
- max_length: `256`

| split | total examples | examples with token length > 256 | percentage > 256 | p95 token length |
| --- | ---: | ---: | ---: | ---: |
| val | 6106 | 1244 | 20.3734 | 685 |
| test_main | 35230 | 15443 | 43.8348 | 581 |
| test_jbb | 197 | 0 | 0.0000 | 31 |
| test_main_adv2 | 35230 | 29373 | 83.3750 | 1185 |
