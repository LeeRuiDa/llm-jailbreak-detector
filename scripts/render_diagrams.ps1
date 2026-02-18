#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Host "npx not found; will try global mmdc fallback."
}

function Render-Diagram {
    param(
        [string]$InputPath,
        [string]$OutputPath
    )
    $rendered = $false
    if (Get-Command npx -ErrorAction SilentlyContinue) {
        try {
            npx -y -p @mermaid-js/mermaid-cli mmdc -i $InputPath -o $OutputPath
            $rendered = $true
        } catch {
            Write-Host "npx render failed for $InputPath; trying global mmdc fallback."
        }
    }
    if (-not $rendered) {
        if (Get-Command mmdc -ErrorAction SilentlyContinue) {
            mmdc -i $InputPath -o $OutputPath
            $rendered = $true
        }
    }
    if (-not $rendered) {
        throw "Mermaid render failed for $InputPath. Install Node.js (npx) or global mmdc."
    }
}

Render-Diagram -InputPath docs/figures/ch1_system_context.mmd -OutputPath docs/figures/ch1_system_context.png
Render-Diagram -InputPath docs/figures/ch3_pipeline.mmd -OutputPath docs/figures/ch3_pipeline.png
Render-Diagram -InputPath docs/figures/ch3_eval_protocol.mmd -OutputPath docs/figures/ch3_eval_protocol.png
Render-Diagram -InputPath docs/figures/ch6_component_diagram.mmd -OutputPath docs/figures/ch6_component_diagram.png
