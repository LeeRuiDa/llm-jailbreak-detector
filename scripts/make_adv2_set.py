from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Dict, Iterable, Tuple


PUNCT_CHARS = [".", ",", "!", "?", ";", ":", "-", "_", "/"]

# Simple homoglyph swaps (Latin -> Cyrillic/Greek lookalikes) to stress mixed scripts.
HOMOGLYPHS = {
    "A": "Α",  # Greek Alpha
    "B": "Β",  # Greek Beta
    "C": "С",  # Cyrillic Es
    "E": "Е",  # Cyrillic Ie
    "H": "Н",  # Cyrillic En
    "I": "І",  # Cyrillic Byelorussian-Ukrainian I
    "J": "Ј",  # Cyrillic Je
    "K": "Κ",  # Greek Kappa
    "M": "Μ",  # Greek Mu
    "N": "Ν",  # Greek Nu
    "O": "О",  # Cyrillic O
    "P": "Р",  # Cyrillic Er
    "S": "Ѕ",  # Cyrillic Dze
    "T": "Τ",  # Greek Tau
    "X": "Χ",  # Greek Chi
    "Y": "Υ",  # Greek Upsilon
    "a": "а",  # Cyrillic a
    "c": "с",  # Cyrillic es
    "e": "е",  # Cyrillic ie
    "i": "і",  # Cyrillic i
    "o": "о",  # Cyrillic o
    "p": "р",  # Cyrillic er
    "x": "х",  # Cyrillic ha
    "y": "у",  # Cyrillic u
}

MIXED_SCRIPT_SAMPLES = [
    "α",  # Greek alpha
    "β",  # Greek beta
    "γ",  # Greek gamma
    "δ",  # Greek delta
    "λ",  # Greek lambda
    "π",  # Greek pi
    "σ",  # Greek sigma
    "ω",  # Greek omega
    "ж",  # Cyrillic zhe
    "д",  # Cyrillic de
    "я",  # Cyrillic ya
    "ш",  # Cyrillic sha
]


def _load_jsonl(path: Path) -> Iterable[Dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _apply_perturbations(
    text: str,
    rng: random.Random,
    case_prob: float,
    space_prob: float,
    punct_prob: float,
    zero_width_prob: float,
    zero_width_max: int,
    homoglyph_prob: float,
    mixed_script_prob: float,
) -> Tuple[str, Dict[str, int]]:
    out = []
    counts = {
        "case_flip": 0,
        "extra_space": 0,
        "punct_insert": 0,
        "zero_width": 0,
        "homoglyph_swap": 0,
        "mixed_script_insert": 0,
    }
    for ch in text:
        if ch.isalpha() and rng.random() < case_prob:
            ch = ch.swapcase()
            counts["case_flip"] += 1
        if ch in HOMOGLYPHS and rng.random() < homoglyph_prob:
            ch = HOMOGLYPHS[ch]
            counts["homoglyph_swap"] += 1
        out.append(ch)

        if ch == " " and rng.random() < space_prob:
            extra = " " * rng.randint(1, 2)
            out.append(extra)
            counts["extra_space"] += len(extra)

        if rng.random() < punct_prob:
            out.append(rng.choice(PUNCT_CHARS))
            counts["punct_insert"] += 1

        if rng.random() < mixed_script_prob:
            out.append(rng.choice(MIXED_SCRIPT_SAMPLES))
            counts["mixed_script_insert"] += 1

        if zero_width_prob > 0 and rng.random() < zero_width_prob:
            inserts = rng.randint(1, max(1, zero_width_max))
            out.append("\u200b" * inserts)
            counts["zero_width"] += inserts

    return "".join(out), counts


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
            perturbed, counts = _apply_perturbations(
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
