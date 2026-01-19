from __future__ import annotations

import argparse
import json
from typing import Dict, Iterable, Optional

from dataset_utils import format_text, make_group_id, make_id, sha256_str, write_jsonl

try:
    from datasets import load_dataset
except ImportError as e:
    raise SystemExit(
        "Missing dependency: datasets. Install with `pip install datasets`."
    ) from e


def _pick_col(columns: Iterable[str], candidates: Iterable[str]) -> Optional[str]:
    cols = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    return None


def _iter_rows(path: str) -> Iterable[Dict]:
    ds = load_dataset("csv", data_files=path, streaming=True)
    for row in ds["train"]:
        yield row


def _row_to_example(row: Dict, label: int, goal_col: str, id_col: Optional[str]) -> Dict:
    goal = str(row.get(goal_col, "") or "")
    if not goal:
        return {}
    text = format_text(goal, "")
    if id_col and row.get(id_col) is not None:
        behavior_id = str(row.get(id_col))
    else:
        behavior_id = sha256_str(goal)
    group_id = make_group_id("jbb", behavior_id)
    ex_id = make_id("jbb", f"{behavior_id}|{label}")
    return {
        "id": ex_id,
        "text": text,
        "label": label,
        "attack_type": "jailbreak_direct" if label == 1 else "benign",
        "source": "jailbreakbench",
        "group_id": group_id,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--harmful_csv",
        default="hf://datasets/JailbreakBench/JBB-Behaviors/data/harmful-behaviors.csv",
    )
    ap.add_argument(
        "--benign_csv",
        default="hf://datasets/JailbreakBench/JBB-Behaviors/data/benign-behaviors.csv",
    )
    ap.add_argument("--out", default="data/v1_holdout/test_jbb.jsonl")
    ap.add_argument("--goal_col")
    ap.add_argument("--id_col")
    args = ap.parse_args()

    rows = []
    for path, label in ((args.harmful_csv, 1), (args.benign_csv, 0)):
        iterator = _iter_rows(path)
        first = next(iterator, None)
        if first is None:
            continue
        columns = list(first.keys())
        goal_col = args.goal_col or _pick_col(columns, ["goal", "Goal", "behavior", "Behavior"])
        if not goal_col:
            raise SystemExit("Could not infer goal column. Use --goal_col.")
        id_col = args.id_col or _pick_col(columns, ["behavior_id", "behavior", "id", "ID"])
        ex = _row_to_example(first, label, goal_col, id_col)
        if ex:
            rows.append(ex)
        for row in iterator:
            ex = _row_to_example(row, label, goal_col, id_col)
            if ex:
                rows.append(ex)

    write_jsonl(args.out, rows)
    print(f"Wrote: {args.out} ({len(rows)})")


if __name__ == "__main__":
    main()
