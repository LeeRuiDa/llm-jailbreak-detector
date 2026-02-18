#!/usr/bin/env bash
set -euo pipefail

render() {
  local input="$1"
  local output="$2"
  if command -v npx >/dev/null 2>&1; then
    if npx -y -p @mermaid-js/mermaid-cli mmdc -i "$input" -o "$output"; then
      return 0
    fi
    echo "npx render failed for $input; trying global mmdc fallback..."
  fi
  if command -v mmdc >/dev/null 2>&1; then
    mmdc -i "$input" -o "$output"
    return 0
  fi
  echo "Mermaid render failed: install Node.js (for npx) or global mmdc."
  return 1
}

render docs/figures/ch1_system_context.mmd docs/figures/ch1_system_context.png
render docs/figures/ch3_pipeline.mmd docs/figures/ch3_pipeline.png
render docs/figures/ch3_eval_protocol.mmd docs/figures/ch3_eval_protocol.png
render docs/figures/ch6_component_diagram.mmd docs/figures/ch6_component_diagram.png
