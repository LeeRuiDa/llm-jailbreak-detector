from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Tuple

from dataset_utils import iter_jsonl, normalize_for_hash, sha256_str, write_jsonl


def _dedup_key(text: str) -> str:
    return sha256_str(normalize_for_hash(text))


def _load(path: str) -> List[Dict]:
    return list(iter_jsonl(path))


def _append_rows(
    rows: Iterable[Dict],
    split: str,
    seen: Dict[str, str],
    kept: Dict[str, List[Dict]],
    dropped: Counter,
    source_priority: str,
) -> None:
    for row in rows:
        text = row.get("text", "")
        if not isinstance(text, str) or not text.strip():
            dropped[f"{split}:missing_text"] += 1
            continue
        key = _dedup_key(text)
        if key in seen:
            dropped[f"{split}:dup"] += 1
            continue
        seen[key] = source_priority
        kept[split].append(row)


def _split_by_group(rows: List[Dict], train_pct: int = 70, val_pct: int = 15) -> Dict[str, List[Dict]]:
    splits = {"train": [], "val": [], "test_main": []}
    for row in rows:
        group_id = str(row.get("group_id", ""))
        bucket = int(sha256_str(group_id)[:8], 16) % 100 if group_id else 0
        if bucket < train_pct:
            splits["train"].append(row)
        elif bucket < train_pct + val_pct:
            splits["val"].append(row)
        else:
            splits["test_main"].append(row)
    return splits


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bipia_train", default="data/processed/bipia_train.jsonl")
    ap.add_argument("--bipia_test", default="data/processed/bipia_test.jsonl")
    ap.add_argument("--jailbreakdb_jsonl", default="data/processed/jailbreakdb.jsonl")
    ap.add_argument("--jailbreak_train", default="data/processed/jailbreakdb_train.jsonl")
    ap.add_argument("--jailbreak_val", default="data/processed/jailbreakdb_val.jsonl")
    ap.add_argument("--jailbreak_test", default="data/processed/jailbreakdb_testmain.jsonl")
    ap.add_argument("--jbb_test", default="data/v1_holdout/test_jbb.jsonl")
    ap.add_argument("--out_train", default="data/v1/train.jsonl")
    ap.add_argument("--out_val", default="data/v1/val.jsonl")
    ap.add_argument("--out_test_main", default="data/v1/test_main.jsonl")
    ap.add_argument("--out_test_jbb", default="data/v1_holdout/test_jbb.jsonl")
    ap.add_argument("--dedup_report", default="data/v1/dedup_report.json")
    ap.add_argument("--manifest", default="data/v1/manifest.json")
    args = ap.parse_args()

    bipia_train = _load(args.bipia_train)
    bipia_test = _load(args.bipia_test)

    if os.path.exists(args.jailbreakdb_jsonl):
        jailbreakdb_rows = _load(args.jailbreakdb_jsonl)
        jailbreak_splits = _split_by_group(jailbreakdb_rows)
    else:
        jailbreak_splits = {
            "train": _load(args.jailbreak_train),
            "val": _load(args.jailbreak_val),
            "test_main": _load(args.jailbreak_test),
        }

    test_main_group_ids = {
        row.get("group_id")
        for row in (bipia_test + jailbreak_splits["test_main"])
        if row.get("group_id")
    }

    bipia_train = [
        row for row in bipia_train if row.get("group_id") not in test_main_group_ids
    ]
    jailbreak_splits["train"] = [
        row
        for row in jailbreak_splits["train"]
        if row.get("group_id") not in test_main_group_ids
    ]
    jailbreak_splits["val"] = [
        row
        for row in jailbreak_splits["val"]
        if row.get("group_id") not in test_main_group_ids
    ]

    seen: Dict[str, str] = {}
    kept: Dict[str, List[Dict]] = defaultdict(list)
    dropped: Counter = Counter()

    # Dedup order: bipia (test, train), jailbreakdb (test, val, train), jbb holdout
    _append_rows(bipia_test, "test_main", seen, kept, dropped, "bipia")
    _append_rows(bipia_train, "train", seen, kept, dropped, "bipia")

    _append_rows(jailbreak_splits["test_main"], "test_main", seen, kept, dropped, "jailbreakdb")
    _append_rows(jailbreak_splits["val"], "val", seen, kept, dropped, "jailbreakdb")
    _append_rows(jailbreak_splits["train"], "train", seen, kept, dropped, "jailbreakdb")

    _append_rows(_load(args.jbb_test), "test_jbb", seen, kept, dropped, "jbb")

    write_jsonl(args.out_train, kept["train"])
    write_jsonl(args.out_val, kept["val"])
    write_jsonl(args.out_test_main, kept["test_main"])
    write_jsonl(args.out_test_jbb, kept["test_jbb"])

    manifest = defaultdict(lambda: defaultdict(Counter))
    for split, rows in kept.items():
        for row in rows:
            source = row.get("source", "unknown")
            attack_type = row.get("attack_type", "unknown")
            label = str(row.get("label", "unknown"))
            manifest[split][source][label] += 1
            manifest[split][source][f"attack_type:{attack_type}"] += 1

    with open(args.dedup_report, "w", encoding="utf-8") as f:
        json.dump({"dropped": dict(dropped)}, f, indent=2)

    with open(args.manifest, "w", encoding="utf-8") as f:
        json.dump(
            {k: {s: dict(v) for s, v in src.items()} for k, src in manifest.items()},
            f,
            indent=2,
        )

    print(f"Wrote: {args.out_train} ({len(kept['train'])})")
    print(f"Wrote: {args.out_val} ({len(kept['val'])})")
    print(f"Wrote: {args.out_test_main} ({len(kept['test_main'])})")
    print(f"Wrote: {args.out_test_jbb} ({len(kept['test_jbb'])})")
    print(f"Wrote: {args.dedup_report}")
    print(f"Wrote: {args.manifest}")


if __name__ == "__main__":
    main()
