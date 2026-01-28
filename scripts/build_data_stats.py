from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "reports" / "week7" / "week7_ablation_spec.json"
EVAL_GRID_PATH = REPO_ROOT / "scripts" / "eval_week7_grid.py"
OUT_DIR = REPO_ROOT / "reports" / "week7" / "locked_eval_pack" / "week7_norm_only"


def _load_spec_datasets(path: Path) -> List[Tuple[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    datasets = data.get("dataset", {})
    ordered = ["train", "val", "test_main", "test_jbb"]
    out: List[Tuple[str, str]] = []
    for key in ordered:
        rel = datasets.get(key)
        if rel:
            out.append((key, rel))
    return out


def _parse_eval_grid_datasets(path: Path) -> List[Tuple[str, str]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r'\("(?P<split>[^"]+)",\s*"(?P<path>[^"]+)"\)')
    return [(m.group("split"), m.group("path")) for m in pattern.finditer(text)]


def _iter_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_no} in {path}") from exc


def _count_labels(path: Path) -> Dict[str, float]:
    total = 0
    n_attack = 0
    n_benign = 0
    for row in _iter_jsonl(path):
        if "label" not in row:
            raise ValueError(f"Missing label in {path}")
        label = int(row["label"])
        if label not in (0, 1):
            raise ValueError(f"Invalid label {label} in {path}")
        total += 1
        if label == 1:
            n_attack += 1
        else:
            n_benign += 1
    attack_rate = (n_attack / total) if total else 0.0
    return {
        "total_rows": total,
        "n_attack": n_attack,
        "n_benign": n_benign,
        "attack_rate": round(attack_rate, 6),
    }


def main() -> None:
    if not SPEC_PATH.exists():
        raise FileNotFoundError(f"Missing spec: {SPEC_PATH}")

    splits: Dict[str, str] = {}
    for split, rel_path in _load_spec_datasets(SPEC_PATH):
        splits[split] = rel_path

    # Include robustness splits from the locked eval grid if present.
    for split, rel_path in _parse_eval_grid_datasets(EVAL_GRID_PATH):
        if split not in splits:
            splits[split] = rel_path

    stats: Dict[str, Dict[str, float]] = {}
    for split, rel_path in splits.items():
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        stats[split] = _count_labels(path)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "DATA_STATS.json"
    md_path = OUT_DIR / "DATA_STATS.md"

    json_path.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Dataset statistics (aggregate only)",
        "",
        "All statistics are computed by streaming JSONL rows and counting labels. "
        "No raw prompts or ids are stored in this report.",
        "",
        "| split | total | attack | benign | attack_rate |",
        "| --- | --- | --- | --- | --- |",
    ]
    for split in sorted(stats.keys()):
        row = stats[split]
        lines.append(
            "| "
            + " | ".join(
                [
                    split,
                    str(row["total_rows"]),
                    str(row["n_attack"]),
                    str(row["n_benign"]),
                    f"{row['attack_rate']:.6f}",
                ]
            )
            + " |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")


if __name__ == "__main__":
    main()
