# Data schema (JSONL)

Each line is one example.

Required fields:
- `id` (string)
- `prompt` (string)
- `context` (string; can be empty)
- `label` (int: 0=safe/benign, 1=unsafe/attack)
- `attack_type` (string; e.g. "benign", "jailbreak", "prompt_injection")
- `meta` (object; optional extra metadata)

Recommended `meta` keys:
- `source`: dataset name / url
- `lang`: "en", "zh", ...
- `has_unicode_anomaly`: bool
- `notes`: string
