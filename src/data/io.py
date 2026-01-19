from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Optional

REQUIRED_FIELDS = {"id", "text", "label", "attack_type", "source", "group_id"}

@dataclass
class Example:
    id: str
    text: str
    label: int  # 0 benign/safe, 1 attack/unsafe
    attack_type: str
    source: str
    group_id: str
    meta: Dict[str, Any]

def load_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no} in {path}: {e}") from e
    return rows

def validate_row(row: Dict[str, Any]) -> None:
    missing = REQUIRED_FIELDS - set(row.keys())
    if missing:
        raise ValueError(f"Missing required fields: {sorted(missing)}")
    if not isinstance(row["id"], str):
        raise ValueError("Field `id` must be a string")
    if not isinstance(row["text"], str):
        raise ValueError("Field `text` must be a string")
    if row["label"] not in (0, 1):
        raise ValueError("Field `label` must be 0 or 1")
    if not isinstance(row["attack_type"], str):
        raise ValueError("Field `attack_type` must be a string")
    if not isinstance(row["source"], str):
        raise ValueError("Field `source` must be a string")
    if not isinstance(row["group_id"], str):
        raise ValueError("Field `group_id` must be a string")

def to_examples(rows: List[Dict[str, Any]]) -> List[Example]:
    out: List[Example] = []
    for row in rows:
        validate_row(row)
        out.append(
            Example(
                id=row["id"],
                text=row["text"],
                label=int(row["label"]),
                attack_type=row["attack_type"],
                source=row["source"],
                group_id=row["group_id"],
                meta=row.get("meta", {}) if isinstance(row.get("meta", {}), dict) else {},
            )
        )
    return out

def load_examples(path: str) -> List[Example]:
    return to_examples(load_jsonl(path))
