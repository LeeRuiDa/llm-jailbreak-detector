from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]


DATASETS: List[Tuple[str, str]] = [
    ("val", "data/v1/val.jsonl"),
    ("test_main", "data/v1/test_main.jsonl"),
    ("test_jbb", "data/v1_holdout/test_jbb.jsonl"),
    ("test_main_unicode", "data/v1_adv/test_main_unicode.jsonl"),
    ("test_jbb_unicode", "data/v1_adv/test_jbb_unicode.jsonl"),
    ("test_main_adv2", "data/v1_adv2/test_main_adv2.jsonl"),
    ("test_jbb_adv2", "data/v1_adv2/test_jbb_adv2.jsonl"),
    ("test_main_rewrite", "data/v1_rewrite/test_main_rewrite.jsonl"),
    ("test_jbb_rewrite", "data/v1_rewrite/test_jbb_rewrite.jsonl"),
]


def _run(cmd: List[str]) -> None:
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def _copy_metrics(run_dir: Path, metrics_dir: Path, split: str) -> None:
    src = run_dir / f"final_metrics_{split}.json"
    if not src.exists():
        print(f"Missing metrics: {src}")
        return
    metrics_dir.mkdir(parents=True, exist_ok=True)
    dst = metrics_dir / src.name
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def _write_metrics_table(metrics_dir: Path, out_path: Path, splits: List[str]) -> None:
    rows: List[List[str]] = []
    for split in splits:
        path = metrics_dir / f"final_metrics_{split}.json"
        if not path.exists():
            continue
        metrics = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            [
                split,
                f"{metrics.get('auroc', 0):.4f}" if metrics.get("auroc") is not None else "-",
                f"{metrics.get('auprc', 0):.4f}" if metrics.get("auprc") is not None else "-",
                f"{metrics.get('val_threshold', metrics.get('threshold', 0)):.4f}"
                if metrics.get("val_threshold", metrics.get("threshold")) is not None
                else "-",
                f"{metrics.get('fpr_at_val_threshold', metrics.get('fpr_actual', 0)):.4f}"
                if metrics.get("fpr_at_val_threshold", metrics.get("fpr_actual")) is not None
                else "-",
                f"{metrics.get('tpr_at_val_threshold', metrics.get('tpr_at_fpr', 0)):.4f}"
                if metrics.get("tpr_at_val_threshold", metrics.get("tpr_at_fpr")) is not None
                else "-",
                f"{metrics.get('asr_at_threshold', 0):.4f}"
                if metrics.get("asr_at_threshold") is not None
                else "-",
            ]
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| split | auroc | auprc | val_threshold | fpr_at_val_threshold | tpr_at_val_threshold | asr_at_threshold |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Evaluate Week 6 grid for a run.")
    ap.add_argument("--run_dir", required=True, help="Path to run directory.")
    ap.add_argument("--out_dir", required=True, help="Output root (e.g., reports/week6).")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir)
    out_dir = Path(args.out_dir)
    run_name = run_dir.name

    metrics_dir = out_dir / "metrics" / run_name
    errors_dir = out_dir / "error_cases" / run_name
    figures_dir = out_dir / "figures" / run_name
    table_path = out_dir / "tables" / f"{run_name}_metrics.md"

    splits_run: List[str] = []
    for split, rel_path in DATASETS:
        data_path = REPO_ROOT / rel_path
        if not data_path.exists():
            print(f"Skipping missing dataset: {data_path}")
            continue
        _run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "eval_lora_from_run.py"),
                "--run_dir",
                str(run_dir),
                "--data",
                str(data_path),
                "--split_name",
                split,
            ]
        )
        _copy_metrics(run_dir, metrics_dir, split)
        splits_run.append(split)

    if splits_run:
        plotter = REPO_ROOT / "scripts" / "plot_predictions.py"
        if plotter.exists():
            _run(
                [
                    sys.executable,
                    str(plotter),
                    "--run_dir",
                    str(run_dir),
                    "--splits",
                    ",".join(splits_run),
                    "--out_dir",
                    str(figures_dir),
                ]
            )
        dumper = REPO_ROOT / "scripts" / "dump_error_cases.py"
        if dumper.exists():
            for split in splits_run:
                _run(
                    [
                        sys.executable,
                        str(dumper),
                        "--run_dir",
                        str(run_dir),
                        "--split",
                        split,
                        "--out_fp",
                        str(errors_dir / f"{split}_fp.md"),
                        "--out_fn",
                        str(errors_dir / f"{split}_fn.md"),
                    ]
                )

    _write_metrics_table(metrics_dir, table_path, splits_run)
    print(f"Wrote metrics table: {table_path}")


if __name__ == "__main__":
    main()
