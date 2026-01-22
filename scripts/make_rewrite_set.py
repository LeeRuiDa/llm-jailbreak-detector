from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.augment.rewrite import apply_rewrite


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Create rewrite (word-level) dataset.")
    ap.add_argument("--in", dest="input_path", required=True, help="Input JSONL path.")
    ap.add_argument("--out", dest="output_path", required=True, help="Output JSONL path.")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--syn_prob", type=float, default=0.15)
    ap.add_argument("--filler_prob", type=float, default=0.08)
    ap.add_argument("--swap_prob", type=float, default=0.15)
    ap.add_argument("--id_suffix", default="::rewrite1")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    in_path = Path(args.input_path)
    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    syn_total = 0
    filler_total = 0
    swap_total = 0

    with in_path.open("r", encoding="utf-8") as src, out_path.open("w", encoding="utf-8") as dst:
        for line in src:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            total += 1

            original_text = row.get("text", "")
            rewritten, counts = apply_rewrite(
                original_text,
                rng,
                syn_prob=args.syn_prob,
                filler_prob=args.filler_prob,
                swap_prob=args.swap_prob,
            )
            row["text"] = rewritten
            row_id = row.get("id", "")
            row["id"] = f"{row_id}{args.id_suffix}"

            meta = row.get("meta")
            if not isinstance(meta, dict):
                meta = {}
            meta["rewrite"] = {
                "syn_prob": args.syn_prob,
                "filler_prob": args.filler_prob,
                "swap_prob": args.swap_prob,
                "counts": counts,
            }
            row["meta"] = meta

            syn_total += counts.get("synonym", 0)
            filler_total += counts.get("filler", 0)
            swap_total += counts.get("swap", 0)

            dst.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote rewrite dataset: {out_path}")
    print(f"rows={total} synonyms={syn_total} fillers={filler_total} swaps={swap_total}")


if __name__ == "__main__":
    main()
