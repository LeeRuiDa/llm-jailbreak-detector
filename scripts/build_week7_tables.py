from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


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

GROUP_SPLITS = {
    "clean": ["test_main", "test_jbb"],
    "unicode": ["test_main_unicode", "test_jbb_unicode"],
    "adv2": ["test_main_adv2", "test_jbb_adv2"],
    "rewrite": ["test_main_rewrite", "test_jbb_rewrite"],
}


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


def _mean(values: List[float]) -> float | None:
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def _metric_val(metrics: Dict, primary: str, fallback: str | None = None) -> float | None:
    if primary in metrics and metrics.get(primary) is not None:
        return float(metrics.get(primary))
    if fallback and fallback in metrics and metrics.get(fallback) is not None:
        return float(metrics.get(fallback))
    return None


def _write_table(out_path: Path, header: List[str], rows: List[List[str]]) -> None:
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_config(runs_root: Path, run_name: str) -> Dict | None:
    cfg_path = runs_root / run_name / "config.json"
    if not cfg_path.exists():
        return None
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def _find_control_run(runs_root: Path, run_names: List[str], override: str | None) -> str:
    if override:
        return override
    for run_name in run_names:
        cfg = _load_config(runs_root, run_name)
        if not cfg:
            continue
        if not cfg.get("normalize_train") and float(cfg.get("aug_adv2_prob", 0.0)) == 0.0:
            return run_name
    raise RuntimeError("Control run not found. Provide --control_run explicitly.")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Build Week 7 summary tables.")
    ap.add_argument("--metrics_root", default="reports/week7/metrics")
    ap.add_argument("--out_dir", default="reports/week7/results")
    ap.add_argument("--runs_root", default="runs")
    ap.add_argument("--control_run", default="", help="Override control run name")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    metrics_root = Path(args.metrics_root)
    out_dir = Path(args.out_dir)
    runs_root = Path(args.runs_root)

    runs = _collect_metrics(metrics_root)
    if not runs:
        raise SystemExit(f"No metrics found under {metrics_root}")

    run_names = sorted(runs.keys())
    control_run = _find_control_run(runs_root, run_names, args.control_run or None)

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

    header_ab = [
        "run",
        "split",
        "auroc",
        "auprc",
        "val_threshold",
        "fpr_at_val_threshold",
        "tpr_at_val_threshold",
        "asr_at_threshold",
    ]
    _write_table(out_dir / "week7_table_A_clean_unicode.md", header_ab, rows_a)
    _write_table(out_dir / "week7_table_B_adv2_rewrite.md", header_ab, rows_b)

    rows_c: List[List[str]] = []
    for run_name in run_names:
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

    header_c = ["run", "split", "fpr_at_val_threshold", "tpr_at_val_threshold", "asr_at_threshold"]
    _write_table(out_dir / "week7_table_C_threshold_transfer.md", header_c, rows_c)

    control_summaries: Dict[str, Dict[str, float | None]] = {}
    control_splits = runs.get(control_run, {})
    for group, splits in GROUP_SPLITS.items():
        control_summaries[group] = {
            "fpr": _mean([
                _metric_val(control_splits.get(s, {}), "fpr_at_val_threshold", "fpr_actual")
                for s in splits
            ]),
            "tpr": _mean([
                _metric_val(control_splits.get(s, {}), "tpr_at_val_threshold", "tpr_at_fpr")
                for s in splits
            ]),
            "asr": _mean([
                _metric_val(control_splits.get(s, {}), "asr_at_threshold")
                for s in splits
            ]),
        }

    rows_d: List[List[str]] = []
    for run_name in run_names:
        splits = runs.get(run_name, {})
        for group, split_list in GROUP_SPLITS.items():
            auroc = _mean([_metric_val(splits.get(s, {}), "auroc") for s in split_list])
            auprc = _mean([_metric_val(splits.get(s, {}), "auprc") for s in split_list])
            fpr = _mean([
                _metric_val(splits.get(s, {}), "fpr_at_val_threshold", "fpr_actual")
                for s in split_list
            ])
            tpr = _mean([
                _metric_val(splits.get(s, {}), "tpr_at_val_threshold", "tpr_at_fpr")
                for s in split_list
            ])
            asr = _mean([
                _metric_val(splits.get(s, {}), "asr_at_threshold") for s in split_list
            ])

            control_vals = control_summaries.get(group, {})
            control_fpr = control_vals.get("fpr")
            control_tpr = control_vals.get("tpr")
            control_asr = control_vals.get("asr")
            delta_fpr = fpr - control_fpr if fpr is not None and control_fpr is not None else None
            delta_tpr = tpr - control_tpr if tpr is not None and control_tpr is not None else None
            delta_asr = asr - control_asr if asr is not None and control_asr is not None else None

            rows_d.append(
                [
                    run_name,
                    group,
                    _fmt(auroc),
                    _fmt(auprc),
                    _fmt(fpr),
                    _fmt(tpr),
                    _fmt(asr),
                    _fmt(delta_fpr),
                    _fmt(delta_tpr),
                    _fmt(delta_asr),
                ]
            )

    header_d = [
        "run",
        "group",
        "mean_auroc",
        "mean_auprc",
        "mean_fpr",
        "mean_tpr",
        "mean_asr",
        "delta_fpr_vs_control",
        "delta_tpr_vs_control",
        "delta_asr_vs_control",
    ]
    _write_table(out_dir / "week7_table_D_ablation_effects.md", header_d, rows_d)

    print(f"Wrote Week 7 tables to {out_dir}")


if __name__ == "__main__":
    main()
