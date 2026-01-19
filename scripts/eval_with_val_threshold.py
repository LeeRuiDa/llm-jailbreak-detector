from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.eval.metrics import tpr_at_fpr


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


def _load_scores(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    rows = list(_iter_predictions(path))
    if not rows:
        raise ValueError(f"No rows in {path}")
    y_true = np.array([r[0] for r in rows], dtype=int)
    y_score = np.array([r[1] for r in rows], dtype=float)
    return y_true, y_score


def _metrics_with_threshold(
    y_true: np.ndarray, y_score: np.ndarray, threshold: float
) -> dict:
    auroc = roc_auc_score(y_true, y_score) if len(np.unique(y_true)) > 1 else None
    auprc = (
        average_precision_score(y_true, y_score)
        if len(np.unique(y_true)) > 1
        else None
    )
    pred_attack = y_score >= threshold
    pos = y_true == 1
    neg = y_true == 0
    tpr = float((pred_attack & pos).sum() / pos.sum()) if pos.sum() else 0.0
    fpr = float((pred_attack & neg).sum() / neg.sum()) if neg.sum() else 0.0
    asr = float((~pred_attack & pos).sum() / pos.sum()) if pos.sum() else 0.0
    return {
        "auroc": auroc,
        "auprc": auprc,
        "tpr_at_fpr": tpr,
        "fpr_actual": fpr,
        "threshold": float(threshold),
        "asr_at_threshold": asr,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--val_predictions", required=True)
    ap.add_argument("--test_predictions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--target_fpr", type=float, default=0.01)
    args = ap.parse_args()

    val_path = Path(args.val_predictions)
    test_path = Path(args.test_predictions)
    out_path = Path(args.out)

    y_true_val, y_score_val = _load_scores(val_path)
    op = tpr_at_fpr(y_true_val, y_score_val, target_fpr=args.target_fpr)

    y_true_test, y_score_test = _load_scores(test_path)
    metrics = _metrics_with_threshold(y_true_test, y_score_test, op.threshold)
    metrics["target_fpr"] = float(args.target_fpr)
    metrics["threshold_source"] = str(val_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Threshold (val): {op.threshold:.6f} fpr={op.fpr:.6f} tpr={op.tpr:.6f}")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
