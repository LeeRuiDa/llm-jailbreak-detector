from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
from sklearn.metrics import roc_auc_score


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


def _sanity_check(y_true: np.ndarray, y_score: np.ndarray, name: str) -> None:
    pos = y_true == 1
    neg = y_true == 0
    pos_mean = float(y_score[pos].mean()) if pos.any() else float("nan")
    neg_mean = float(y_score[neg].mean()) if neg.any() else float("nan")
    auc = roc_auc_score(y_true, y_score) if len(np.unique(y_true)) > 1 else float("nan")
    print(
        f"[{name}] auc={auc:.4f} mean(score|y=1)={pos_mean:.4f} "
        f"mean(score|y=0)={neg_mean:.4f}"
    )
    if pos.any() and neg.any() and pos_mean < neg_mean:
        print(
            f"[{name}] warning: mean(score|y=1) < mean(score|y=0). "
            "Scores may be inverted."
        )
    if not np.isnan(auc) and auc < 0.5:
        inv_auc = roc_auc_score(y_true, 1.0 - y_score)
        print(f"[{name}] warning: auc < 0.5 (inv auc={inv_auc:.4f}).")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--predictions",
        nargs="+",
        required=True,
        help="One or more predictions.jsonl files.",
    )
    args = ap.parse_args()

    for pred_path in args.predictions:
        path = Path(pred_path)
        rows = list(_iter_predictions(path))
        if not rows:
            print(f"[{path}] no rows found.")
            continue
        y_true = np.array([r[0] for r in rows], dtype=int)
        y_score = np.array([r[1] for r in rows], dtype=float)
        _sanity_check(y_true, y_score, name=str(path))


if __name__ == "__main__":
    main()
