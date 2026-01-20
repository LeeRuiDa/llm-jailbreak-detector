from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple


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


def _threshold_for_fpr(neg_scores: List[float], target_fpr: float) -> float:
    if not neg_scores:
        raise ValueError("No negative samples to calibrate on.")
    neg_sorted = sorted(neg_scores)
    n = len(neg_sorted)
    target_fpr = min(max(target_fpr, 0.0), 1.0)
    idx = max(0, min(n - 1, math.ceil((1.0 - target_fpr) * n) - 1))
    return float(neg_sorted[idx])


def _actual_fpr(neg_scores: List[float], threshold: float) -> float:
    if not neg_scores:
        return 0.0
    return float(sum(1 for s in neg_scores if s >= threshold) / len(neg_scores))


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Calibrate thresholds to target FPR on negatives.")
    ap.add_argument("--pred_path", required=True, help="Predictions JSONL with label/score.")
    ap.add_argument("--targets", default="0.01,0.05", help="Comma-separated target FPRs.")
    ap.add_argument("--out_dir", default="reports/week5/thresholds", help="Output directory.")
    ap.add_argument("--out_prefix", default="threshold_adv2", help="Output filename prefix.")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    pred_path = Path(args.pred_path)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    y_true, y_score = _load_predictions(pred_path)
    neg_scores = [s for y, s in zip(y_true, y_score) if y == 0]
    pos_scores = [s for y, s in zip(y_true, y_score) if y == 1]
    pos_rate = len(pos_scores) / len(y_true) if y_true else 0.0

    targets = [float(t.strip()) for t in args.targets.split(",") if t.strip()]
    normalize_infer = pred_path.name.endswith("_norm.jsonl")

    for target in targets:
        threshold = _threshold_for_fpr(neg_scores, target)
        actual_fpr = _actual_fpr(neg_scores, threshold)
        suffix = f"fpr{int(round(target * 100))}"
        out_path = out_dir / f"{args.out_prefix}_{suffix}.json"
        payload: Dict[str, object] = {
            "source_predictions": str(pred_path),
            "target_fpr": target,
            "threshold": threshold,
            "actual_fpr": actual_fpr,
            "n_neg": len(neg_scores),
            "n_pos": len(pos_scores),
            "pos_rate": pos_rate,
            "normalize_infer": normalize_infer,
        }
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
