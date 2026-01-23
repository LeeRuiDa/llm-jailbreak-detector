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
        raise FileNotFoundError(f"Missing metrics: {src}")
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


def _collect_metrics(metrics_root: Path) -> Dict[str, Dict[str, Dict]]:
    runs: Dict[str, Dict[str, Dict]] = {}
    for path in metrics_root.rglob("final_metrics_*.json"):
        run_name = path.parent.name
        split = path.stem[len("final_metrics_") :]
        runs.setdefault(run_name, {})[split] = json.loads(path.read_text(encoding="utf-8"))
    return runs


def _write_long_tables(metrics_root: Path, out_md: Path, out_csv: Path) -> None:
    runs = _collect_metrics(metrics_root)
    rows: List[List[str]] = []
    for run_name in sorted(runs.keys()):
        splits = runs[run_name]
        for split in sorted(splits.keys()):
            metrics = splits[split]
            rows.append(
                [
                    run_name,
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

    header = [
        "run",
        "split",
        "auroc",
        "auprc",
        "val_threshold",
        "fpr_at_val_threshold",
        "tpr_at_val_threshold",
        "asr_at_threshold",
    ]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    csv_lines = [",".join(header)]
    for row in rows:
        csv_lines.append(",".join(row))
    out_csv.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")


def _load_run_manifest(path: Path) -> List[Dict]:
    if not path.exists():
        raise FileNotFoundError(f"Run manifest not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise TypeError("run_manifest.json must contain a list")
    return data


def _resolve_run_list(run_dirs_arg: str, manifest_path: Path) -> List[Tuple[str, Path]]:
    runs: List[Tuple[str, Path]] = []
    if run_dirs_arg:
        for item in run_dirs_arg.split(","):
            item = item.strip()
            if not item:
                continue
            run_path = Path(item)
            if not run_path.is_absolute():
                run_path = REPO_ROOT / run_path
            runs.append((run_path.name, run_path))
        return runs

    manifest = _load_run_manifest(manifest_path)
    for entry in manifest:
        if isinstance(entry, str):
            run_id = entry
            run_dir = REPO_ROOT / "runs" / run_id
        elif isinstance(entry, dict):
            run_id = str(entry.get("run_id") or entry.get("name") or "").strip()
            if not run_id:
                raise ValueError("Manifest entry missing run_id")
            run_dir = entry.get("run_dir")
            if run_dir:
                run_dir = Path(run_dir)
                if not run_dir.is_absolute():
                    run_dir = REPO_ROOT / run_dir
            else:
                run_dir = REPO_ROOT / "runs" / run_id
        else:
            raise TypeError("Invalid entry in run_manifest.json")
        runs.append((run_id, Path(run_dir)))
    return runs


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Evaluate Week 7 locked grid for one or more runs.")
    ap.add_argument("--run_manifest", default=str(REPO_ROOT / "reports" / "week7" / "run_manifest.json"))
    ap.add_argument("--run_dirs", default="", help="Comma-separated run directories (optional)")
    ap.add_argument("--out_dir", default=str(REPO_ROOT / "reports" / "week7"))
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    metrics_root = out_dir / "metrics"

    runs = _resolve_run_list(args.run_dirs, Path(args.run_manifest))
    if not runs:
        raise SystemExit("No runs provided for evaluation")

    splits_run: List[str] = []
    for split, rel_path in DATASETS:
        data_path = REPO_ROOT / rel_path
        if not data_path.exists():
            raise FileNotFoundError(f"Missing dataset: {data_path}")
        splits_run.append(split)

    for run_id, run_dir in runs:
        if not run_dir.exists():
            raise FileNotFoundError(f"Run dir not found: {run_dir}")

        metrics_dir = metrics_root / run_id
        errors_dir = out_dir / "error_cases" / run_id
        figures_dir = out_dir / "figures" / run_id
        table_path = out_dir / f"{run_id}_metrics.md"

        for split, rel_path in DATASETS:
            data_path = REPO_ROOT / rel_path
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

    results_dir = out_dir / "results"
    _write_long_tables(
        metrics_root,
        results_dir / "week7_metrics_long.md",
        results_dir / "week7_metrics_long.csv",
    )
    print(f"Wrote combined metrics to {results_dir}")


if __name__ == "__main__":
    main()
