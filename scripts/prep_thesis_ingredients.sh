#!/usr/bin/env bash
set -euo pipefail

python scripts/build_data_stats.py
python scripts/build_rules_baseline_table.py

echo "Outputs written to reports/week7/locked_eval_pack/week7_norm_only/"
