from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Dict, Iterable, Iterator, List, Optional

WHITESPACE_RE = re.compile(r"\s+")


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def normalize_for_hash(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text.strip()).lower()


def make_id(source: str, payload: str) -> str:
    return sha256_str(f"{source}|{payload}")


def make_group_id(source: str, group_payload: str) -> str:
    return sha256_str(f"{source}|{group_payload}")


def format_text(prompt: str, context: Optional[str]) -> str:
    ctx = context or ""
    return f"[PROMPT]\n{prompt}\n[CONTEXT]\n{ctx}"


def iter_jsonl(path: str) -> Iterator[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no} in {path}: {e}") from e


def read_jsonl(path: str) -> List[Dict]:
    return list(iter_jsonl(path))


def write_jsonl(path: str, rows: Iterable[Dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
