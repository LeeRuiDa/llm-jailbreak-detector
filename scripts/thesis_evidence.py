from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.metrics import tpr_at_fpr

DEFAULT_OUTPUT_ROOT = REPO_ROOT / "reports" / "thesis_support"
METRIC_KEYS = [
    "auroc",
    "auprc",
    "fpr_at_val_threshold",
    "tpr_at_val_threshold",
    "asr_at_threshold",
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_predictions(path: Path) -> tuple[np.ndarray, np.ndarray]:
    labels: list[int] = []
    scores: list[float] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            labels.append(int(row["label"]))
            scores.append(float(row["score"]))
    return np.asarray(labels, dtype=int), np.asarray(scores, dtype=float)


def _run_dir(path: str) -> Path:
    run_dir = Path(path)
    if not run_dir.is_absolute():
        run_dir = REPO_ROOT / run_dir
    return run_dir


def _load_split_predictions(run_dir: Path, split: str) -> tuple[np.ndarray, np.ndarray]:
    pred_path = run_dir / f"predictions_{split}.jsonl"
    if not pred_path.exists():
        raise FileNotFoundError(f"Missing predictions file: {pred_path}")
    return _load_predictions(pred_path)


def _load_threshold(run_dir: Path) -> float:
    op_path = run_dir / "val_operating_point.json"
    if op_path.exists():
        return float(_load_json(op_path)["threshold"])
    cfg = _load_json(run_dir / "config.json")
    return float(cfg["val_threshold"])


def _compute_threshold_metrics(labels: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, float | None]:
    pred = scores >= threshold
    pos = labels == 1
    neg = labels == 0

    tp = int((pred & pos).sum())
    fp = int((pred & neg).sum())
    tn = int((~pred & neg).sum())
    fn = int((~pred & pos).sum())

    tpr = float(tp / pos.sum()) if pos.sum() else 0.0
    fpr = float(fp / neg.sum()) if neg.sum() else 0.0
    precision = float(tp / (tp + fp)) if (tp + fp) else 0.0
    asr = float(fn / pos.sum()) if pos.sum() else 0.0
    return {
        "threshold": float(threshold),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "tpr": tpr,
        "fpr": fpr,
        "precision": precision,
        "asr": asr,
    }


def _mean_std_ci(values: Iterable[float]) -> tuple[float, float, float]:
    vals = [float(v) for v in values]
    if not vals:
        return math.nan, math.nan, math.nan
    mean = float(statistics.mean(vals))
    std = float(statistics.stdev(vals)) if len(vals) > 1 else 0.0
    ci95 = float(1.96 * std / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
    return mean, std, ci95


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0].keys())
    lines = [",".join(headers)]
    for row in rows:
        parts: list[str] = []
        for key in headers:
            value = row[key]
            if isinstance(value, float):
                parts.append(f"{value:.10g}")
            else:
                parts.append(str(value))
        lines.append(",".join(parts))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _reliability_table(labels: np.ndarray, scores: np.ndarray, bins: int) -> tuple[list[dict[str, float]], float, float]:
    edges = np.linspace(0.0, 1.0, bins + 1)
    rows: list[dict[str, float]] = []
    ece = 0.0
    n = len(scores)
    for idx in range(bins):
        lo = edges[idx]
        hi = edges[idx + 1]
        if idx == bins - 1:
            mask = (scores >= lo) & (scores <= hi)
        else:
            mask = (scores >= lo) & (scores < hi)
        count = int(mask.sum())
        if count == 0:
            continue
        conf = float(scores[mask].mean())
        acc = float(labels[mask].mean())
        frac = count / n
        ece += abs(acc - conf) * frac
        rows.append(
            {
                "bin_low": float(lo),
                "bin_high": float(hi),
                "count": count,
                "mean_score": conf,
                "empirical_positive_rate": acc,
            }
        )
    brier = float(np.mean((scores - labels) ** 2))
    return rows, float(ece), brier


def _plot_reliability(rows: list[dict[str, float]], title: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.2, 5.2), constrained_layout=True)
    ax.plot([0, 1], [0, 1], linestyle="--", color="#888888", label="Perfect calibration")
    if rows:
        x = [row["mean_score"] for row in rows]
        y = [row["empirical_positive_rate"] for row in rows]
        sizes = [max(40, row["count"] * 0.6) for row in rows]
        ax.plot(x, y, color="#0b6e4f", linewidth=1.8)
        ax.scatter(x, y, s=sizes, color="#0b6e4f", alpha=0.8, label="Observed bins")
    ax.set_xlabel("Mean predicted attack score")
    ax.set_ylabel("Observed attack frequency")
    ax.set_title(title)
    ax.legend(loc="upper left")
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def calibration_analysis(args: argparse.Namespace) -> None:
    run_dir = _run_dir(args.run_dir)
    splits = [split.strip() for split in args.splits.split(",") if split.strip()]
    out_dir = Path(args.out_dir) if args.out_dir else DEFAULT_OUTPUT_ROOT / "calibration" / run_dir.name
    summary_rows: list[dict[str, object]] = []
    for split in splits:
        labels, scores = _load_split_predictions(run_dir, split)
        rows, ece, brier = _reliability_table(labels, scores, args.bins)
        prevalence = float(labels.mean()) if len(labels) else 0.0
        summary_rows.append(
            {
                "split": split,
                "n": int(len(labels)),
                "positives": int(labels.sum()),
                "negatives": int((labels == 0).sum()),
                "prevalence": prevalence,
                "ece": ece,
                "brier": brier,
                "mean_score": float(scores.mean()) if len(scores) else math.nan,
            }
        )
        _write_json(out_dir / f"bins_{split}.json", rows)
        _plot_reliability(rows, f"Reliability: {run_dir.name} / {split}", out_dir / f"reliability_{split}.png")
    _write_csv(out_dir / "calibration_summary.csv", summary_rows)
    _write_json(out_dir / "calibration_summary.json", summary_rows)
    print(f"Wrote calibration analysis to {out_dir}")


def threshold_sweep(args: argparse.Namespace) -> None:
    run_dir = _run_dir(args.run_dir)
    splits = [split.strip() for split in args.splits.split(",") if split.strip()]
    center = _load_threshold(run_dir)
    lower = max(0.0, center - args.radius)
    upper = min(1.0, center + args.radius)
    thresholds = np.linspace(lower, upper, args.num_points)
    out_dir = Path(args.out_dir) if args.out_dir else DEFAULT_OUTPUT_ROOT / "threshold_sweep" / run_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    fig, axes = plt.subplots(3, 1, figsize=(8.8, 11.1))
    metric_names = [("fpr", "False Positive Rate"), ("tpr", "True Positive Rate"), ("asr", "Attack Success Rate")]

    for split in splits:
        labels, scores = _load_split_predictions(run_dir, split)
        split_metrics = []
        for threshold in thresholds:
            metrics = _compute_threshold_metrics(labels, scores, float(threshold))
            metrics["split"] = split
            rows.append(metrics)
            split_metrics.append(metrics)
        for ax, (metric_key, metric_label) in zip(axes, metric_names):
            ax.plot(thresholds, [row[metric_key] for row in split_metrics], linewidth=2.45, label=split)
            ax.axvline(center, color="#c1121f", linestyle="--", linewidth=1.55)
            ax.set_ylabel(metric_label)
    axes[-1].set_xlabel("Threshold")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=min(len(labels), 3),
        frameon=True,
        fontsize=10,
        columnspacing=1.2,
        handlelength=1.9,
        bbox_to_anchor=(0.5, 0.988),
    )
    fig.tight_layout(rect=(0, 0, 1, 0.942))
    fig.savefig(out_dir / "threshold_stability.png", dpi=220)
    plt.close(fig)

    summary_rows: list[dict[str, object]] = []
    deltas = [-0.05, -0.02, 0.0, 0.02, 0.05]
    for split in splits:
        labels, scores = _load_split_predictions(run_dir, split)
        for delta in deltas:
            threshold = min(1.0, max(0.0, center + delta))
            metrics = _compute_threshold_metrics(labels, scores, threshold)
            summary_rows.append({"split": split, "delta": delta, **metrics})
    _write_csv(out_dir / "threshold_sweep_long.csv", rows)
    _write_csv(out_dir / "threshold_sweep_summary.csv", summary_rows)
    _write_json(out_dir / "threshold_sweep_meta.json", {"center_threshold": center, "radius": args.radius, "num_points": args.num_points, "splits": splits})
    print(f"Wrote threshold sweep to {out_dir}")


def benign_heavy_analysis(args: argparse.Namespace) -> None:
    run_dir = _run_dir(args.run_dir)
    out_dir = Path(args.out_dir) if args.out_dir else DEFAULT_OUTPUT_ROOT / "benign_heavy" / run_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    val_labels, val_scores = _load_split_predictions(run_dir, "val")
    neg_scores = val_scores[val_labels == 0]
    pos_scores = val_scores[val_labels == 1]
    rng = np.random.default_rng(args.seed)

    eval_splits = [split.strip() for split in args.eval_splits.split(",") if split.strip()]
    eval_cache = {split: _load_split_predictions(run_dir, split) for split in eval_splits}
    prevalence_values = [float(item.strip()) for item in args.attack_prevalences.split(",") if item.strip()]

    all_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for prevalence_attack in prevalence_values:
        if not 0 < prevalence_attack < 1:
            raise ValueError("Attack prevalence must be between 0 and 1.")
        target_pos = min(len(pos_scores), max(1, int(round(len(neg_scores) * prevalence_attack / (1.0 - prevalence_attack)))))
        repeats = 1 if math.isclose(prevalence_attack, float(val_labels.mean()), rel_tol=0.0, abs_tol=1e-6) else args.repeats
        repeat_thresholds: list[float] = []
        split_metric_buckets: dict[tuple[str, str], list[float]] = {}

        for repeat in range(repeats):
            if target_pos == len(pos_scores):
                sampled_pos = pos_scores
            else:
                idx = rng.choice(len(pos_scores), size=target_pos, replace=False)
                sampled_pos = pos_scores[idx]
            labels = np.concatenate([np.zeros(len(neg_scores), dtype=int), np.ones(len(sampled_pos), dtype=int)])
            scores = np.concatenate([neg_scores, sampled_pos])
            op = tpr_at_fpr(labels, scores, target_fpr=args.target_fpr)
            repeat_thresholds.append(float(op.threshold))

            for split, (split_labels, split_scores) in eval_cache.items():
                metrics = _compute_threshold_metrics(split_labels, split_scores, float(op.threshold))
                all_rows.append(
                    {
                        "attack_prevalence": prevalence_attack,
                        "repeat": repeat,
                        "split": split,
                        **metrics,
                    }
                )
                for metric_key in ("fpr", "tpr", "asr", "precision"):
                    split_metric_buckets.setdefault((split, metric_key), []).append(float(metrics[metric_key]))

        threshold_mean, threshold_std, threshold_ci = _mean_std_ci(repeat_thresholds)
        summary_rows.append(
            {
                "attack_prevalence": prevalence_attack,
                "split": "calibration_slice",
                "metric": "threshold",
                "mean": threshold_mean,
                "std": threshold_std,
                "ci95": threshold_ci,
                "repeats": repeats,
            }
        )
        for (split, metric_key), values in split_metric_buckets.items():
            mean, std, ci = _mean_std_ci(values)
            summary_rows.append(
                {
                    "attack_prevalence": prevalence_attack,
                    "split": split,
                    "metric": metric_key,
                    "mean": mean,
                    "std": std,
                    "ci95": ci,
                    "repeats": repeats,
                }
            )

    _write_csv(out_dir / "benign_heavy_long.csv", all_rows)
    _write_csv(out_dir / "benign_heavy_summary.csv", summary_rows)
    _write_json(out_dir / "benign_heavy_summary.json", summary_rows)

    fig, axes = plt.subplots(2, 1, figsize=(8.2, 8.8))
    for split in eval_splits:
        fpr_points = [row["mean"] for row in summary_rows if row["split"] == split and row["metric"] == "fpr"]
        tpr_points = [row["mean"] for row in summary_rows if row["split"] == split and row["metric"] == "tpr"]
        xs = [row["attack_prevalence"] for row in summary_rows if row["split"] == split and row["metric"] == "fpr"]
        axes[0].plot(xs, fpr_points, marker="o", linewidth=2.0, markersize=4.5, label=split)
        axes[1].plot(xs, tpr_points, marker="o", linewidth=2.0, markersize=4.5, label=split)
    axes[0].set_ylabel("Held-out FPR")
    axes[1].set_ylabel("Held-out TPR")
    axes[1].set_xlabel("Attack prevalence in resampled validation slice")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=min(len(labels), 3), frameon=True, fontsize=9, bbox_to_anchor=(0.5, 0.985))
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out_dir / "benign_heavy_sensitivity.png", dpi=220)
    plt.close(fig)

    print(f"Wrote benign-heavy calibration analysis to {out_dir}")


def _extra_eval_splits(cfg: dict) -> list[tuple[str, str]]:
    base_split_keys = {"train_path", "val_path", "test_main_path", "test_jbb_path"}
    split_paths: dict[str, str] = {}
    for key, value in cfg.items():
        if key in base_split_keys or not key.endswith("_path"):
            continue
        path = Path(str(value))
        if path.suffix.lower() != ".jsonl":
            continue
        split_paths[key[:-5]] = str(path)

    evaluated_splits = cfg.get("evaluated_splits")
    if isinstance(evaluated_splits, list):
        ordered_splits: list[tuple[str, str]] = []
        for split in evaluated_splits:
            split_name = str(split).strip()
            if split_name in {"val", "test_main", "test_jbb"}:
                continue
            path = split_paths.get(split_name)
            if path:
                ordered_splits.append((split_name, path))
        if ordered_splits:
            return ordered_splits

    return sorted(split_paths.items())


def run_multiseed(args: argparse.Namespace) -> None:
    base_run_dir = _run_dir(args.base_run_dir)
    cfg = _load_json(base_run_dir / "config.json")
    seeds = [int(item.strip()) for item in args.seeds.split(",") if item.strip()]
    if not seeds:
        raise ValueError("At least one seed is required.")

    out_root = Path(args.out_root) if args.out_root else REPO_ROOT / "runs"
    manifest_path = Path(args.manifest) if args.manifest else DEFAULT_OUTPUT_ROOT / "multiseed" / f"{base_run_dir.name}_manifest.json"
    manifest_entries: list[dict[str, object]] = []

    for seed in seeds:
        run_name = f"{args.run_prefix}_seed{seed}"
        run_dir = out_root / run_name
        train_cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "train_lora.py"),
            "--train",
            str(cfg["train_path"]),
            "--val",
            str(cfg["val_path"]),
            "--test_main",
            str(cfg["test_main_path"]),
            "--test_jbb",
            str(cfg["test_jbb_path"]),
            "--backbone",
            str(cfg["backbone"]),
            "--epochs",
            str(cfg["epochs"]),
            "--batch_size",
            str(cfg["batch_size"]),
            "--lr",
            str(cfg["lr"]),
            "--grad_accum",
            str(cfg["grad_accum"]),
            "--seed",
            str(seed),
            "--max_length",
            str(cfg["max_length"]),
            "--num_workers",
            str(args.num_workers),
            "--aug_adv2_prob",
            str(cfg.get("aug_adv2_prob", 0.0)),
            "--aug_rewrite_prob",
            str(cfg.get("aug_rewrite_prob", 0.0)),
            "--aug_seed",
            str(cfg.get("aug_seed", seed)),
            "--attack_label",
            str(cfg.get("attack_label", 1)),
            "--out_dir",
            str(run_dir),
        ]
        if cfg.get("unicode"):
            train_cmd.append("--unicode_preprocess")
        if cfg.get("normalize_train"):
            train_cmd.append("--normalize_train")
        if cfg.get("normalize_drop_mn"):
            train_cmd.append("--normalize_drop_mn")

        print("Running:", " ".join(train_cmd))
        if not args.dry_run:
            subprocess.run(train_cmd, check=True, cwd=REPO_ROOT)
            for split, path in _extra_eval_splits(cfg):
                eval_cmd = [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "eval_lora_from_run.py"),
                    "--run_dir",
                    str(run_dir),
                    "--data",
                    str(path),
                    "--split_name",
                    split,
                ]
                print("Running:", " ".join(eval_cmd))
                subprocess.run(eval_cmd, check=True, cwd=REPO_ROOT)

        manifest_entries.append({"seed": seed, "run_dir": str(run_dir), "base_run_dir": str(base_run_dir)})

    _write_json(manifest_path, manifest_entries)
    print(f"Wrote multiseed manifest to {manifest_path}")


def summarize_multiseed(args: argparse.Namespace) -> None:
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    run_dirs = [Path(entry["run_dir"]) for entry in manifest]
    splits = [split.strip() for split in args.splits.split(",") if split.strip()]
    out_dir = Path(args.out_dir) if args.out_dir else manifest_path.parent

    rows: list[dict[str, object]] = []
    for split in splits:
        metric_values: dict[str, list[float]] = {key: [] for key in METRIC_KEYS}
        seeds: list[int] = []
        for entry, run_dir in zip(manifest, run_dirs):
            metrics_path = run_dir / f"final_metrics_{split}.json"
            if not metrics_path.exists():
                continue
            metrics = _load_json(metrics_path)
            seeds.append(int(entry["seed"]))
            for key in METRIC_KEYS:
                value = metrics.get(key)
                if value is not None:
                    metric_values[key].append(float(value))
        for metric_key, values in metric_values.items():
            if not values:
                continue
            mean, std, ci95 = _mean_std_ci(values)
            rows.append(
                {
                    "split": split,
                    "metric": metric_key,
                    "n_runs": len(values),
                    "mean": mean,
                    "std": std,
                    "ci95": ci95,
                }
            )
    _write_csv(out_dir / "multiseed_summary.csv", rows)
    _write_json(out_dir / "multiseed_summary.json", rows)
    print(f"Wrote multiseed summary to {out_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Thesis evidence analyses and rerun helpers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    cal = subparsers.add_parser("calibration", help="Generate reliability diagrams and ECE/Brier summaries.")
    cal.add_argument("--run_dir", required=True)
    cal.add_argument("--splits", default="val,test_main,test_jbb")
    cal.add_argument("--bins", type=int, default=10)
    cal.add_argument("--out_dir", default="")
    cal.set_defaults(func=calibration_analysis)

    sweep = subparsers.add_parser("threshold-sweep", help="Sweep thresholds around the validation operating point.")
    sweep.add_argument("--run_dir", required=True)
    sweep.add_argument("--splits", default="val,test_main,test_jbb,test_main_adv2,test_jbb_adv2")
    sweep.add_argument("--radius", type=float, default=0.12)
    sweep.add_argument("--num_points", type=int, default=49)
    sweep.add_argument("--out_dir", default="")
    sweep.set_defaults(func=threshold_sweep)

    bh = subparsers.add_parser("benign-heavy", help="Run benign-heavy calibration sensitivity using resampled validation predictions.")
    bh.add_argument("--run_dir", required=True)
    bh.add_argument("--attack_prevalences", default="0.495251,0.20,0.10,0.05")
    bh.add_argument("--eval_splits", default="test_main,test_jbb,test_main_adv2,test_jbb_adv2,test_main_rewrite,test_jbb_rewrite")
    bh.add_argument("--target_fpr", type=float, default=0.01)
    bh.add_argument("--repeats", type=int, default=10)
    bh.add_argument("--seed", type=int, default=42)
    bh.add_argument("--out_dir", default="")
    bh.set_defaults(func=benign_heavy_analysis)

    ms = subparsers.add_parser("run-multiseed", help="Launch multi-seed reruns from a base run config.")
    ms.add_argument("--base_run_dir", required=True)
    ms.add_argument("--seeds", default="41,42,43")
    ms.add_argument("--run_prefix", default="week7_norm_only_ms")
    ms.add_argument("--out_root", default="")
    ms.add_argument("--manifest", default="")
    ms.add_argument("--num_workers", type=int, default=0)
    ms.add_argument("--dry_run", action="store_true")
    ms.set_defaults(func=run_multiseed)

    summ = subparsers.add_parser("summarize-multiseed", help="Aggregate metrics across multi-seed run directories.")
    summ.add_argument("--manifest", required=True)
    summ.add_argument("--splits", default="val,test_main,test_jbb,test_main_adv2,test_jbb_adv2,test_main_rewrite,test_jbb_rewrite")
    summ.add_argument("--out_dir", default="")
    summ.set_defaults(func=summarize_multiseed)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
