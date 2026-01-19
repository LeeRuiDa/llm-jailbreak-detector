from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Set

from dataset_utils import iter_jsonl

REQUIRED_FIELDS = {"id", "text", "label", "attack_type", "source", "group_id"}


def _load(path: str) -> List[Dict]:
    return list(iter_jsonl(path))


def _validate_rows(rows: Iterable[Dict], path: str) -> Counter:
    counts = Counter()
    seen_ids: Set[str] = set()
    dup_ids = 0
    for row in rows:
        missing = REQUIRED_FIELDS - set(row.keys())
        if missing:
            counts["missing_fields"] += 1
        if row.get("label") not in (0, 1):
            counts["invalid_label"] += 1
        ex_id = row.get("id")
        if ex_id in seen_ids:
            dup_ids += 1
        else:
            seen_ids.add(ex_id)
        counts[f"label:{row.get('label')}"] += 1
        counts[f"attack_type:{row.get('attack_type')}"] += 1
    if dup_ids:
        counts["duplicate_ids"] = dup_ids
    return counts


def _group_ids(rows: Iterable[Dict]) -> Set[str]:
    return {row.get("group_id") for row in rows if row.get("group_id")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="data/v1/train.jsonl")
    ap.add_argument("--val", default="data/v1/val.jsonl")
    ap.add_argument("--test_main", default="data/v1/test_main.jsonl")
    ap.add_argument("--test_jbb", default="data/v1_holdout/test_jbb.jsonl")
    args = ap.parse_args()

    splits = {
        "train": _load(args.train),
        "val": _load(args.val),
        "test_main": _load(args.test_main),
        "test_jbb": _load(args.test_jbb),
    }

    report = {}
    for name, rows in splits.items():
        report[name] = _validate_rows(rows, name)

    train_groups = _group_ids(splits["train"])
    val_groups = _group_ids(splits["val"])
    test_groups = _group_ids(splits["test_main"])

    overlap_train_val = train_groups & val_groups
    overlap_train_test = train_groups & test_groups
    overlap_val_test = val_groups & test_groups

    if overlap_train_val or overlap_train_test or overlap_val_test:
        print("Group overlap detected:")
        print(f"train∩val: {len(overlap_train_val)}")
        print(f"train∩test_main: {len(overlap_train_test)}")
        print(f"val∩test_main: {len(overlap_val_test)}")
    else:
        print("No group_id overlap across train/val/test_main.")

    val_benign = report["val"].get("label:0", 0)
    if val_benign < 1000:
        print(f"Warning: val benign count {val_benign} < 1000 (1% FPR may be unstable).")

    print(json.dumps({k: dict(v) for k, v in report.items()}, indent=2))


if __name__ == "__main__":
    main()
