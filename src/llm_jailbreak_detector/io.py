from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Iterator


def iter_jsonl(path: str | Path) -> Iterator[dict]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def iter_text_lines(path: str | Path) -> Iterator[dict]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle):
            text = line.rstrip("\n")
            if not text:
                continue
            yield {"id": str(idx), "text": text}


def iter_input_records(path: str | Path) -> Iterator[dict]:
    path = Path(path)
    if path.suffix.lower() == ".jsonl":
        for obj in iter_jsonl(path):
            if "text" not in obj:
                raise ValueError("JSONL records must include a 'text' field")
            yield obj
    else:
        yield from iter_text_lines(path)


def write_jsonl(path: str | Path, rows: Iterable[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            payload = json.dumps(row, ensure_ascii=True)
            handle.write(payload + "\n")
