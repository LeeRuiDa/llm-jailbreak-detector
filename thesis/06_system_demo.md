# System Demonstration

## 6.1 Overview
This chapter summarizes the system components and the CLI usage contract.

## 6.2 Component diagram
![Figure 6.1: Component diagram for CLI, core prediction stack, detectors, and evaluation scripts.](docs/figures/ch6_component_diagram.png)

## 6.3 System walkthrough
High-level walkthrough of the CLI and prediction flow.

## 6.4 CLI contract
Table 6.1: CLI contract (command -> input -> output).
| Command | Input | Output |
| --- | --- | --- |
| `jbd predict` | `--text`, `--detector rules|lora`, optional `--run_dir`, `--threshold` or `val`, optional `--normalize`, `--drop-mn` | JSON fields: `id` (optional), `text`, `score`, `threshold`, `flagged`, `detector`, `normalize_infer` |
| `jbd batch` | `--input` (jsonl or txt), `--output` (jsonl), `--detector rules|lora`, optional `--run_dir`, `--threshold` or `val`, optional `--normalize`, `--drop-mn` | JSONL with fields: `id` (optional), `text`, `score`, `threshold`, `flagged`, `detector`, `normalize_infer` |
| `jbd normalize` | `--text`, optional `--drop-mn` | Normalized text |

## 6.5 Reproducibility notes
Command settings and run artifacts are logged for repeatable evaluation.
