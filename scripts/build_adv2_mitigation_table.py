from __future__ import annotations

import argparse
import json
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


def _compute_metrics(y_true: List[int], y_score: List[float], threshold: float) -> Dict[str, float]:
    pos = [y == 1 for y in y_true]
    neg = [y == 0 for y in y_true]
    pred_attack = [s >= threshold for s in y_score]
    tp = sum(p and a for p, a in zip(pred_attack, pos))
    fp = sum(p and n for p, n in zip(pred_attack, neg))
    fn = sum((not p) and a for p, a in zip(pred_attack, pos))
    pos_count = sum(pos)
    neg_count = sum(neg)
    tpr = tp / pos_count if pos_count else 0.0
    fpr = fp / neg_count if neg_count else 0.0
    asr = fn / pos_count if pos_count else 0.0
    return {"fpr": fpr, "tpr": tpr, "asr": asr}


def _load_threshold(path: Path) -> float:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return float(payload["threshold"])


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Build adv2 mitigation table (A/B/C thresholds).")
    ap.add_argument("--run_dir", required=True, help="Path to run directory.")
    ap.add_argument("--thresholds_dir", required=True, help="Directory with threshold JSON files.")
    ap.add_argument("--out", required=True, help="Output markdown table.")
    ap.add_argument("--splits", default="test_main_adv2,test_jbb_adv2", help="Comma-separated splits.")
    ap.add_argument("--prefix", default="threshold_adv2", help="Prefix for non-norm thresholds.")
    ap.add_argument("--prefix_norm", default="threshold_adv2_norm", help="Prefix for norm thresholds.")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir)
    thresholds_dir = Path(args.thresholds_dir)
    splits = [s.strip() for s in args.splits.split(",") if s.strip()]

    cfg_path = run_dir / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    val_threshold = float(cfg.get("val_threshold"))

    thresholds = {
        False: {
            "adv2_fpr1": _load_threshold(thresholds_dir / f"{args.prefix}_fpr1.json"),
            "adv2_fpr5": _load_threshold(thresholds_dir / f"{args.prefix}_fpr5.json"),
        },
        True: {
            "adv2_fpr1": _load_threshold(thresholds_dir / f"{args.prefix_norm}_fpr1.json"),
            "adv2_fpr5": _load_threshold(thresholds_dir / f"{args.prefix_norm}_fpr5.json"),
        },
    }

    rows: List[List[str]] = []
    for split in splits:
        for normalize in (False, True):
            suffix = "_norm" if normalize else ""
            pred_path = run_dir / f"predictions_{split}{suffix}.jsonl"
            if not pred_path.exists():
                print(f"Missing predictions: {pred_path}")
                continue
            y_true, y_score = _load_predictions(pred_path)
            for label, threshold in [
                ("val", val_threshold),
                ("adv2_fpr1", thresholds[normalize]["adv2_fpr1"]),
                ("adv2_fpr5", thresholds[normalize]["adv2_fpr5"]),
            ]:
                metrics = _compute_metrics(y_true, y_score, threshold)
                rows.append(
                    [
                        split,
                        "true" if normalize else "false",
                        label,
                        f"{threshold:.4f}",
                        f"{metrics['fpr']:.4f}",
                        f"{metrics['tpr']:.4f}",
                        f"{metrics['asr']:.4f}",
                    ]
                )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| split | normalize_infer | threshold_source | threshold | fpr | tpr | asr |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
