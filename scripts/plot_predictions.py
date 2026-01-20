from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score, roc_curve

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_predictions(path: Path) -> Tuple[List[int], List[float]]:
    y_true: List[int] = []
    y_score: List[float] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            y_true.append(int(row["label"]))
            y_score.append(float(row["score"]))
    return y_true, y_score


def _safe_mean(values: List[float]) -> float | None:
    if not values:
        return None
    return float(np.mean(values))


def _write_metrics(path: Path, y_true: List[int], y_score: List[float]) -> None:
    pos_scores = [s for y, s in zip(y_true, y_score) if y == 1]
    neg_scores = [s for y, s in zip(y_true, y_score) if y == 0]
    auroc = None
    auprc = None
    if len(set(y_true)) > 1:
        auroc = float(roc_auc_score(y_true, y_score))
        auprc = float(average_precision_score(y_true, y_score))
    metrics = {
        "auroc": auroc,
        "auprc": auprc,
        "mean_pos_score": _safe_mean(pos_scores),
        "mean_neg_score": _safe_mean(neg_scores),
        "n_pos": len(pos_scores),
        "n_neg": len(neg_scores),
    }
    path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def _plot_roc(y_true: List[int], y_score: List[float], out_path: Path, title: str) -> None:
    plt.figure(figsize=(5, 4))
    if len(set(y_true)) > 1:
        fpr, tpr, _ = roc_curve(y_true, y_score)
        auc = roc_auc_score(y_true, y_score)
        plt.plot(fpr, tpr, label=f"AUROC={auc:.4f}")
        plt.plot([0, 1], [0, 1], linestyle="--", color="gray", label="chance")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.legend(loc="lower right")
    else:
        plt.text(0.5, 0.5, "ROC undefined (single class)", ha="center", va="center")
        plt.axis("off")
    plt.title(title)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def _plot_pr(y_true: List[int], y_score: List[float], out_path: Path, title: str) -> None:
    plt.figure(figsize=(5, 4))
    if len(set(y_true)) > 1:
        precision, recall, _ = precision_recall_curve(y_true, y_score)
        auprc = average_precision_score(y_true, y_score)
        plt.plot(recall, precision, label=f"AUPRC={auprc:.4f}")
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.legend(loc="lower left")
    else:
        plt.text(0.5, 0.5, "PR undefined (single class)", ha="center", va="center")
        plt.axis("off")
    plt.title(title)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def _plot_hist(y_true: List[int], y_score: List[float], out_path: Path, title: str) -> None:
    pos_scores = [s for y, s in zip(y_true, y_score) if y == 1]
    neg_scores = [s for y, s in zip(y_true, y_score) if y == 0]
    plt.figure(figsize=(5, 4))
    bins = 40
    plt.hist(neg_scores, bins=bins, alpha=0.6, label="y=0", color="#4C72B0")
    plt.hist(pos_scores, bins=bins, alpha=0.6, label="y=1", color="#DD8452")
    plt.xlabel("Score")
    plt.ylabel("Count")
    plt.legend(loc="upper right")
    plt.title(title)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def _infer_splits(run_dir: Path) -> List[str]:
    splits = []
    for path in sorted(run_dir.glob("predictions_*.jsonl")):
        name = path.stem[len("predictions_") :]
        if name:
            splits.append(name)
    return splits


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Plot ROC/PR/score histograms from predictions files.")
    ap.add_argument("--run_dir", required=True, help="Path to run directory.")
    ap.add_argument("--splits", default="", help="Comma-separated split names.")
    ap.add_argument("--out_dir", default="", help="Output directory for figures/metrics.")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        raise SystemExit(f"Run dir not found: {run_dir}")

    splits = [s.strip() for s in args.splits.split(",") if s.strip()]
    if not splits:
        splits = _infer_splits(run_dir)
    if not splits:
        raise SystemExit(f"No predictions_*.jsonl found in {run_dir}")

    run_id = run_dir.name
    out_dir = Path(args.out_dir) if args.out_dir else REPO_ROOT / "reports" / "week5" / "figures" / run_id

    for split in splits:
        pred_path = run_dir / f"predictions_{split}.jsonl"
        if not pred_path.exists():
            print(f"Skipping missing predictions file: {pred_path}")
            continue
        y_true, y_score = _load_predictions(pred_path)
        stem = f"{run_id}_{split}"
        _plot_roc(y_true, y_score, out_dir / f"roc_{stem}.png", f"ROC: {split}")
        _plot_pr(y_true, y_score, out_dir / f"pr_{stem}.png", f"PR: {split}")
        _plot_hist(y_true, y_score, out_dir / f"hist_{stem}.png", f"Score Histogram: {split}")
        _write_metrics(out_dir / f"metrics_{stem}.json", y_true, y_score)

    print(f"Wrote figures/metrics to {out_dir}")


if __name__ == "__main__":
    main()
