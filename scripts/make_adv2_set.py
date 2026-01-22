from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Dict, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.augment.adv2 import apply_adv2


def _load_jsonl(path: Path) -> Iterable[Dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Create an adv2 dataset with light perturbations.")
    ap.add_argument("--input", required=True, help="Input JSONL path.")
    ap.add_argument("--output", required=True, help="Output JSONL path.")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--case_prob", type=float, default=0.2)
    ap.add_argument("--space_prob", type=float, default=0.08)
    ap.add_argument("--punct_prob", type=float, default=0.03)
    ap.add_argument("--homoglyph_prob", type=float, default=0.06)
    ap.add_argument("--mixed_script_prob", type=float, default=0.02)
    ap.add_argument("--zero_width_prob", type=float, default=0.03)
    ap.add_argument("--zero_width_max", type=int, default=2)
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as out_f:
        for row in _load_jsonl(in_path):
            text = row.get("text", "")
            perturbed, counts = apply_adv2(
                text,
                rng,
                case_prob=args.case_prob,
                space_prob=args.space_prob,
                punct_prob=args.punct_prob,
                zero_width_prob=args.zero_width_prob,
                zero_width_max=args.zero_width_max,
                homoglyph_prob=args.homoglyph_prob,
                mixed_script_prob=args.mixed_script_prob,
            )
            row["text"] = perturbed
            meta = row.get("meta")
            if not isinstance(meta, dict):
                meta = {}
            meta["adv2"] = {
                "case_prob": args.case_prob,
                "space_prob": args.space_prob,
                "punct_prob": args.punct_prob,
                "homoglyph_prob": args.homoglyph_prob,
                "mixed_script_prob": args.mixed_script_prob,
                "zero_width_prob": args.zero_width_prob,
                "counts": counts,
            }
            row["meta"] = meta
            out_f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote adv2 dataset: {out_path}")


if __name__ == "__main__":
    main()
