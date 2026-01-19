from __future__ import annotations

import argparse
import hashlib
import random
from typing import Dict, Iterable

from dataset_utils import iter_jsonl, sha256_str, write_jsonl

ZWSP = "\u200b"
FULLWIDTH_OFFSET = 0xFEE0


def _rng_for_id(seed: int, ex_id: str) -> random.Random:
    digest = hashlib.sha256(f"{seed}|{ex_id}".encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def _to_fullwidth(ch: str) -> str:
    code = ord(ch)
    if 0x21 <= code <= 0x7E:
        return chr(code + FULLWIDTH_OFFSET)
    return ch


def _obfuscate_text(
    text: str, rng: random.Random, zwsp_rate: float, fullwidth_rate: float
) -> str:
    out = []
    for ch in text:
        if 0x21 <= ord(ch) <= 0x7E and rng.random() < fullwidth_rate:
            ch = _to_fullwidth(ch)
        out.append(ch)
        if ch not in ("\n", "\r") and rng.random() < zwsp_rate:
            out.append(ZWSP)
    return "".join(out)


def _obfuscate_rows(
    rows: Iterable[Dict],
    seed: int,
    zwsp_rate: float,
    fullwidth_rate: float,
) -> Iterable[Dict]:
    for row in rows:
        ex_id = str(row.get("id", ""))
        rng = _rng_for_id(seed, ex_id)
        text = str(row.get("text", ""))
        obfuscated_text = _obfuscate_text(text, rng, zwsp_rate, fullwidth_rate)

        meta = row.get("meta", {})
        meta = dict(meta) if isinstance(meta, dict) else {}
        meta["orig_id"] = row.get("id")
        meta["orig_group_id"] = row.get("group_id")
        meta["unicode_adv"] = {
            "variant": "uadv1",
            "seed": seed,
            "zwsp_rate": zwsp_rate,
            "fullwidth_rate": fullwidth_rate,
        }

        out_row = dict(row)
        out_row["id"] = f"{ex_id}::uadv1"
        out_row["text"] = obfuscated_text
        out_row["group_id"] = sha256_str(obfuscated_text)
        out_row["meta"] = meta
        yield out_row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_jsonl", required=True)
    ap.add_argument("--output_jsonl", required=True)
    ap.add_argument("--seed", type=int, default=2024)
    ap.add_argument("--zwsp_rate", type=float, default=0.02)
    ap.add_argument("--fullwidth_rate", type=float, default=0.05)
    args = ap.parse_args()

    rows = iter_jsonl(args.input_jsonl)
    obfuscated = _obfuscate_rows(rows, args.seed, args.zwsp_rate, args.fullwidth_rate)
    write_jsonl(args.output_jsonl, obfuscated)
    print(f"Wrote: {args.output_jsonl}")


if __name__ == "__main__":
    main()
