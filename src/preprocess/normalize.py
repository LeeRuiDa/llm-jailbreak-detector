from __future__ import annotations

import unicodedata


def normalize_text(text: str, *, remove_cf: bool = True, remove_mn: bool = False) -> str:
    """Normalize text for inference.

    Applies NFKC, strips category Cf (format), and optionally strips Mn
    (nonspacing marks) to reduce obfuscation.
    """
    out = unicodedata.normalize("NFKC", text)
    if not (remove_cf or remove_mn):
        return out
    cleaned = []
    for ch in out:
        cat = unicodedata.category(ch)
        if remove_cf and cat == "Cf":
            continue
        if remove_mn and cat == "Mn":
            continue
        cleaned.append(ch)
    return "".join(cleaned)
