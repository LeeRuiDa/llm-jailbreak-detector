from __future__ import annotations

import random
from typing import Dict, Tuple


PUNCT_CHARS = [".", ",", "!", "?", ";", ":", "-", "_", "/"]

HOMOGLYPHS = {
    "A": "Α",
    "B": "Β",
    "C": "С",
    "E": "Е",
    "H": "Н",
    "I": "І",
    "J": "Ј",
    "K": "Κ",
    "M": "Μ",
    "N": "Ν",
    "O": "О",
    "P": "Р",
    "S": "Ѕ",
    "T": "Τ",
    "X": "Χ",
    "Y": "Υ",
    "a": "а",
    "c": "с",
    "e": "е",
    "i": "і",
    "o": "о",
    "p": "р",
    "x": "х",
    "y": "у",
}

MIXED_SCRIPT_SAMPLES = [
    "α",
    "β",
    "γ",
    "δ",
    "λ",
    "π",
    "σ",
    "ω",
    "ж",
    "д",
    "я",
    "ш",
]


def apply_adv2(
    text: str,
    rng: random.Random,
    *,
    case_prob: float = 0.2,
    space_prob: float = 0.08,
    punct_prob: float = 0.03,
    zero_width_prob: float = 0.03,
    zero_width_max: int = 2,
    homoglyph_prob: float = 0.06,
    mixed_script_prob: float = 0.02,
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
