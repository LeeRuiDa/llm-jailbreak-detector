from __future__ import annotations

from llm_jailbreak_detector.normalize import normalize_text


def test_nfkc_and_cf_removed() -> None:
    raw = "\uff21\u200b"
    assert normalize_text(raw) == "A"


def test_drop_mn_removes_mark() -> None:
    raw = "x\u0327"
    assert normalize_text(raw, drop_mn=False) == "x\u0327"
    assert normalize_text(raw, drop_mn=True) == "x"
