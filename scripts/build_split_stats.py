from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Tuple


def _load_predictions(path: Path) -> Tuple[int, int]:
    total = 0
    pos = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            total += 1
            if int(row.get("label", 0)) == 1:
                pos += 1
    return total, pos


def _load_auprc(path: Path) -> float | None:
    if not path.exists():
        return None
    metrics = json.loads(path.read_text(encoding="utf-8"))
    val = metrics.get("auprc")
    return float(val) if val is not None else None


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Build split stats table (pos_rate + AUPRC lift).")
    ap.add_argument("--run_dir", required=True, help="Path to run directory.")
    ap.add_argument("--splits", default="", help="Comma-separated split names.")
    ap.add_argument("--out", required=True, help="Output markdown table path.")
    ap.add_argument("--use_norm", action="store_true", help="Use *_norm predictions/metrics.")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir)
    splits = [s.strip() for s in args.splits.split(",") if s.strip()]
    if not splits:
        raise SystemExit("Provide --splits.")

    suffix = "_norm" if args.use_norm else ""
    rows: List[List[str]] = []
    for split in splits:
        pred_path = run_dir / f"predictions_{split}{suffix}.jsonl"
        metrics_path = run_dir / f"final_metrics_{split}{suffix}.json"
        if not pred_path.exists():
            print(f"Missing predictions: {pred_path}")
            continue
        total, pos = _load_predictions(pred_path)
        pos_rate = pos / total if total else 0.0
        auprc = _load_auprc(metrics_path)
        auprc_lift = auprc - pos_rate if auprc is not None else None
        rows.append(
            [
                split,
                f"{pos_rate:.4f}",
                f"{pos_rate:.4f}",
                f"{auprc_lift:.4f}" if auprc_lift is not None else "-",
            ]
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| split | pos_rate | auprc_baseline | auprc_lift |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
