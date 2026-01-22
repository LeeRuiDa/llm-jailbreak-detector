from __future__ import annotations

import random
import re
from typing import Dict, List, Tuple


SYNONYMS = {
    "explain": ["describe", "clarify", "outline"],
    "describe": ["explain", "summarize", "outline"],
    "show": ["demonstrate", "display", "present"],
    "create": ["make", "produce", "craft"],
    "write": ["compose", "draft", "author"],
    "give": ["provide", "offer", "share"],
    "list": ["enumerate", "itemize", "outline"],
    "important": ["key", "notable", "significant"],
    "example": ["instance", "case", "illustration"],
    "quick": ["fast", "brief", "rapid"],
    "simple": ["basic", "plain", "straightforward"],
    "use": ["utilize", "apply", "employ"],
    "help": ["assist", "aid", "support"],
    "detail": ["specific", "particular", "precise"],
    "explaination": ["explanation"],
    "reason": ["rationale", "cause", "basis"],
    "begin": ["start", "initiate"],
    "end": ["finish", "conclude"],
}

FILLERS = [
    "in summary",
    "for clarity",
    "in other words",
    "to be clear",
    "as a reminder",
]

WORD_RE = re.compile(r"^([A-Za-z]+)([^A-Za-z]*)$")
SENTENCE_RE = re.compile(r"([.;:!?])")


def _preserve_case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement.title()
    return replacement


def _rewrite_sentence_order(text: str, rng: random.Random, swap_prob: float) -> str:
    parts = SENTENCE_RE.split(text)
    if len(parts) < 3:
        return text
    segments = []
    for i in range(0, len(parts) - 1, 2):
        seg = parts[i].strip()
        punct = parts[i + 1]
        if seg:
            segments.append(f"{seg}{punct}")
    tail = parts[-1].strip()
    if tail:
        segments.append(tail)
    if len(segments) < 2 or rng.random() >= swap_prob:
        return text
    idx = rng.randrange(0, len(segments) - 1)
    segments[idx], segments[idx + 1] = segments[idx + 1], segments[idx]
    return " ".join(segments)


def _rewrite_tokens(
    text: str,
    rng: random.Random,
    syn_prob: float,
    filler_prob: float,
) -> Tuple[str, Dict[str, int]]:
    tokens = text.split()
    rewritten: List[str] = []
    counts = {"synonym": 0, "filler": 0}
    for token in tokens:
        match = WORD_RE.match(token)
        if match:
            word, punct = match.group(1), match.group(2)
            key = word.lower()
            if key in SYNONYMS and rng.random() < syn_prob:
                replacement = rng.choice(SYNONYMS[key])
                word = _preserve_case(word, replacement)
                counts["synonym"] += 1
            rewritten.append(word + punct)
        else:
            rewritten.append(token)
        if rng.random() < filler_prob:
            rewritten.append(rng.choice(FILLERS))
            counts["filler"] += 1
    return " ".join(rewritten), counts


def apply_rewrite(
    text: str,
    rng: random.Random,
    *,
    syn_prob: float = 0.15,
    filler_prob: float = 0.08,
    swap_prob: float = 0.15,
) -> Tuple[str, Dict[str, int]]:
    swapped = _rewrite_sentence_order(text, rng, swap_prob)
    rewritten, counts = _rewrite_tokens(swapped, rng, syn_prob, filler_prob)
    counts["swap"] = 1 if swapped != text else 0
    return rewritten, counts
