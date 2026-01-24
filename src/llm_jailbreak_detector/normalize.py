from __future__ import annotations

from preprocess.normalize import normalize_text as _normalize_text


def normalize_text(text: str, drop_mn: bool = False) -> str:
    """Normalize text with NFKC + format stripping; optionally drop Mn."""
    return _normalize_text(text, remove_cf=True, remove_mn=drop_mn)
