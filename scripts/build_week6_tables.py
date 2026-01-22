from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple


CLEAN_UNICODE_SPLITS = [
    "val",
    "test_main",
    "test_jbb",
    "test_main_unicode",
    "test_jbb_unicode",
]

STRESS_SPLITS = [
    "test_main_adv2",
    "test_jbb_adv2",
    "test_main_rewrite",
    "test_jbb_rewrite",
]

THRESHOLD_TRANSFER_SPLITS = [
    "test_main",
    "test_main_unicode",
    "test_main_adv2",
    "test_main_rewrite",
    "test_jbb_adv2",
    "test_jbb_rewrite",
]


def _load_metrics(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_metrics(metrics_root: Path) -> Dict[str, Dict[str, Dict]]:
    runs: Dict[str, Dict[str, Dict]] = {}
    for path in metrics_root.rglob("final_metrics_*.json"):
        run_name = path.parent.name
        split = path.stem[len("final_metrics_") :]
        runs.setdefault(run_name, {})[split] = _load_metrics(path)
    return runs


def _fmt(val: object) -> str:
    if val is None:
        return "-"
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val)


def _write_table(out_path: Path, rows: List[List[str]]) -> None:
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
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mean(values: List[float]) -> float | None:
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Build Week 6 summary tables.")
    ap.add_argument("--metrics_root", default="reports/week6/metrics")
    ap.add_argument("--out_dir", default="reports/week6/tables")
    ap.add_argument(
        "--ablation_runs",
        default="",
        help="Comma-separated run names for ablation summary (optional).",
    )
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    metrics_root = Path(args.metrics_root)
    out_dir = Path(args.out_dir)

    runs = _collect_metrics(metrics_root)
    if not runs:
        raise SystemExit(f"No metrics found under {metrics_root}")

    ablation_runs = [r.strip() for r in args.ablation_runs.split(",") if r.strip()]
    run_list = ablation_runs or sorted(runs.keys())

    rows_a: List[List[str]] = []
    rows_b: List[List[str]] = []
    for run_name, splits in runs.items():
        for split in CLEAN_UNICODE_SPLITS:
            metrics = splits.get(split)
            if not metrics:
                continue
            rows_a.append(
                [
                    run_name,
                    split,
                    _fmt(metrics.get("auroc")),
                    _fmt(metrics.get("auprc")),
                    _fmt(metrics.get("val_threshold", metrics.get("threshold"))),
                    _fmt(metrics.get("fpr_at_val_threshold", metrics.get("fpr_actual"))),
                    _fmt(metrics.get("tpr_at_val_threshold", metrics.get("tpr_at_fpr"))),
                    _fmt(metrics.get("asr_at_threshold")),
                ]
            )
        for split in STRESS_SPLITS:
            metrics = splits.get(split)
            if not metrics:
                continue
            rows_b.append(
                [
                    run_name,
                    split,
                    _fmt(metrics.get("auroc")),
                    _fmt(metrics.get("auprc")),
                    _fmt(metrics.get("val_threshold", metrics.get("threshold"))),
                    _fmt(metrics.get("fpr_at_val_threshold", metrics.get("fpr_actual"))),
                    _fmt(metrics.get("tpr_at_val_threshold", metrics.get("tpr_at_fpr"))),
                    _fmt(metrics.get("asr_at_threshold")),
                ]
            )

    _write_table(out_dir / "week6_table_A_clean_unicode.md", rows_a)
    _write_table(out_dir / "week6_table_B_adv2_rewrite.md", rows_b)

    rows_c: List[List[str]] = []
    for run_name in run_list:
        splits = runs.get(run_name, {})
        for split in THRESHOLD_TRANSFER_SPLITS:
            metrics = splits.get(split)
            if not metrics:
                continue
            rows_c.append(
                [
                    run_name,
                    split,
                    _fmt(metrics.get("fpr_at_val_threshold", metrics.get("fpr_actual"))),
                    _fmt(metrics.get("tpr_at_val_threshold", metrics.get("tpr_at_fpr"))),
                    _fmt(metrics.get("asr_at_threshold")),
                ]
            )

    out_c = out_dir / "week6_table_C_threshold_transfer.md"
    header_c = ["run", "split", "fpr_at_val_threshold", "tpr_at_val_threshold", "asr_at_threshold"]
    lines_c = [
        "| " + " | ".join(header_c) + " |",
        "| " + " | ".join(["---"] * len(header_c)) + " |",
    ]
    for row in rows_c:
        lines_c.append("| " + " | ".join(row) + " |")
    out_c.write_text("\n".join(lines_c) + "\n", encoding="utf-8")

    summary_rows: List[List[str]] = []
    for run_name in run_list:
        splits = runs.get(run_name, {})
        aurocs = [_mean([splits.get(s, {}).get("auroc") for s in STRESS_SPLITS])]
        auprcs = [_mean([splits.get(s, {}).get("auprc") for s in STRESS_SPLITS])]
        fprs = [_mean([splits.get(s, {}).get("fpr_at_val_threshold") for s in STRESS_SPLITS])]
        tprs = [_mean([splits.get(s, {}).get("tpr_at_val_threshold") for s in STRESS_SPLITS])]
        asrs = [_mean([splits.get(s, {}).get("asr_at_threshold") for s in STRESS_SPLITS])]
        summary_rows.append(
            [
                run_name,
                _fmt(aurocs[0]),
                _fmt(auprcs[0]),
                _fmt(fprs[0]),
                _fmt(tprs[0]),
                _fmt(asrs[0]),
            ]
        )

    summary_path = out_dir / "week6_ablation_summary.md"
    header = ["run", "mean_auroc", "mean_auprc", "mean_fpr", "mean_tpr", "mean_asr"]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for row in summary_rows:
        lines.append("| " + " | ".join(row) + " |")
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote: {out_dir / 'week6_table_A_clean_unicode.md'}")
    print(f"Wrote: {out_dir / 'week6_table_B_adv2_rewrite.md'}")
    print(f"Wrote: {summary_path}")


if __name__ == "__main__":
    main()
