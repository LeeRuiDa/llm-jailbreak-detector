import hashlib

import pytest

from src.preprocess.unicode import normalize_text


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("\uff28\uff45\uff4c\uff4c\uff4f", "Hello"),
        ("\uff11\uff12\uff13", "123"),
        ("\uff08test\uff09", "(test)"),
        ("he\u200bllo", "hello"),
        ("\ufeffhello", "hello"),
        ("\ufb01", "fi"),
        ("a\tb\nc  d", "a b c d"),
        ("\u0430\u0435\u043e\u0440\u0441\u0445\u0443\u0456", "aeopcxyi"),
        ("A\u3000B", "A B"),
        ("  padded  ", "padded"),
    ],
)
def test_normalize_text_cases(raw: str, expected: str) -> None:
    assert normalize_text(raw) == expected


def test_normalize_text_preserves_ascii() -> None:
    text = "Hello, world!"
    assert normalize_text(text) == text


def test_strip_zero_width_toggle() -> None:
    raw = "he\u200bllo"
    assert normalize_text(raw, strip_zw=False, collapse_ws=False) == raw


def test_collapse_whitespace_toggle() -> None:
    raw = "a\tb\nc  d"
    assert normalize_text(raw, collapse_ws=False) == raw


def test_stable_hash() -> None:
    raw = "\uff28\uff45\uff4c\uff4c\uff4f"
    first = hashlib.sha256(normalize_text(raw).encode("utf-8")).hexdigest()
    second = hashlib.sha256(normalize_text(raw).encode("utf-8")).hexdigest()
    assert first == second
