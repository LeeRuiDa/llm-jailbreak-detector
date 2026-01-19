from __future__ import annotations

import re
import unicodedata

ZERO_WIDTH_CHARS = {
    "\u200b",  # ZWSP
    "\u200c",  # ZWNJ
    "\u200d",  # ZWJ
    "\ufeff",  # BOM
}

WHITESPACE_RE = re.compile(r"\s+")

FULLWIDTH_OFFSET = 0xFEE0
FULLWIDTH_START = 0xFF01
FULLWIDTH_END = 0xFF5E
FULLWIDTH_SPACE = 0x3000

CONFUSABLES = {
    "\u0430": "a",  # Cyrillic a
    "\u0435": "e",  # Cyrillic e
    "\u043e": "o",  # Cyrillic o
    "\u0440": "p",  # Cyrillic p
    "\u0441": "c",  # Cyrillic c
    "\u0445": "x",  # Cyrillic x
    "\u0443": "y",  # Cyrillic y
    "\u0456": "i",  # Cyrillic i
}


def _map_fullwidth(text: str) -> str:
    out = []
    for ch in text:
        code = ord(ch)
        if code == FULLWIDTH_SPACE:
            out.append(" ")
        elif FULLWIDTH_START <= code <= FULLWIDTH_END:
            out.append(chr(code - FULLWIDTH_OFFSET))
        else:
            out.append(ch)
    return "".join(out)


def _map_confusables(text: str) -> str:
    if not text:
        return text
    return "".join(CONFUSABLES.get(ch, ch) for ch in text)


def normalize_text(
    text: str,
    *,
    nfkc: bool = True,
    strip_zw: bool = True,
    collapse_ws: bool = True,
) -> str:
    """Normalize Unicode to reduce obfuscation used in jailbreaks/prompt injection.

    Applies NFKC, strips zero-width characters, maps common confusables, and
    collapses whitespace to make adversarial formatting less effective.
    """
    out = text
    if nfkc:
        out = unicodedata.normalize("NFKC", out)
    out = _map_fullwidth(out)
    out = _map_confusables(out)
    if strip_zw:
        out = "".join(ch for ch in out if ch not in ZERO_WIDTH_CHARS)
    if collapse_ws:
        out = WHITESPACE_RE.sub(" ", out).strip()
    return out
