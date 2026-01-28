#!/usr/bin/env bash
set -euo pipefail

if ! command -v mmdc >/dev/null 2>&1; then
  echo "npm install -g @mermaid-js/mermaid-cli"
  exit 1
fi

mmdc -i docs/figures/ch1_system_context.mmd -o docs/figures/ch1_system_context.png
mmdc -i docs/figures/ch3_pipeline.mmd -o docs/figures/ch3_pipeline.png
mmdc -i docs/figures/ch3_eval_protocol.mmd -o docs/figures/ch3_eval_protocol.png
mmdc -i docs/figures/ch6_component_diagram.mmd -o docs/figures/ch6_component_diagram.png
