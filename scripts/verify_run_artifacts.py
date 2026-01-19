from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
from sklearn.metrics import roc_auc_score


def _fmt_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).isoformat()


def _iter_predictions(path: Path) -> Iterable[Tuple[int, float]]:
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no} in {path}: {e}") from e
            if "label" not in row or "score" not in row:
                raise ValueError(f"Missing label/score on line {line_no} in {path}")
            yield int(row["label"]), float(row["score"])


def _sanity_stats(y_true: np.ndarray, y_score: np.ndarray) -> None:
    pos = y_true == 1
    neg = y_true == 0
    pos_mean = float(y_score[pos].mean()) if pos.any() else float("nan")
    neg_mean = float(y_score[neg].mean()) if neg.any() else float("nan")
    if len(np.unique(y_true)) > 1:
        auc = float(roc_auc_score(y_true, y_score))
        print(
            f"auc={auc:.4f} mean(score|y=1)={pos_mean:.4f} "
            f"mean(score|y=0)={neg_mean:.4f}"
        )
        if auc < 0.5:
            inv_auc = float(roc_auc_score(y_true, 1.0 - y_score))
            print(f"warning: auc < 0.5 (inv auc={inv_auc:.4f})")
    else:
        print(
            f"mean(score|y=1)={pos_mean:.4f} mean(score|y=0)={neg_mean:.4f} "
            "(AUC undefined: single class)"
        )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True)
    ap.add_argument(
        "--predictions",
        help="Optional path to a predictions JSONL file (e.g., predictions_val.jsonl).",
    )
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        raise SystemExit(f"Run dir not found: {run_dir}")

    pred_path = Path(args.predictions) if args.predictions else run_dir / "predictions.jsonl"
    if not pred_path.exists():
        candidates = sorted(run_dir.glob("predictions_*.jsonl"))
        if not candidates:
            raise SystemExit(f"Missing predictions.jsonl in {run_dir}")
        if len(candidates) == 1:
            pred_path = candidates[0]
        else:
            options = "\n".join(f"- {p.name}" for p in candidates)
            raise SystemExit(
                "Multiple predictions files found. Pass --predictions:\n" + options
            )

    metrics_path = run_dir / "final_metrics.json"
    if pred_path.name.startswith("predictions_") and pred_path.name.endswith(".jsonl"):
        split = pred_path.name[len("predictions_") : -len(".jsonl")]
        split_metrics = run_dir / f"final_metrics_{split}.json"
        if split_metrics.exists():
            metrics_path = split_metrics

    print(f"{pred_path.name} mtime: {_fmt_mtime(pred_path)}")
    if metrics_path.exists():
        print(f"{metrics_path.name} mtime: {_fmt_mtime(metrics_path)}")
    else:
        print(f"{metrics_path.name} not found.")

    rows = list(_iter_predictions(pred_path))
    if not rows:
        print("predictions.jsonl is empty.")
        return

    y_true = np.array([r[0] for r in rows], dtype=int)
    y_score = np.array([r[1] for r in rows], dtype=float)
    _sanity_stats(y_true, y_score)


if __name__ == "__main__":
    main()
