from __future__ import annotations

import os
import re
import sys
from pathlib import Path


PLAN_PATH = Path("thesis/FIGURES_TABLES_PLAN.md")


def extract_paths(text: str) -> list[str]:
    patterns = [
        r"docs/figures/[A-Za-z0-9_\-./]+",
        r"reports/week7/locked_eval_pack/[A-Za-z0-9_\-./]+",
        r"thesis/[A-Za-z0-9_\-./]+\.md",
        r"docs/[A-Za-z0-9_\-./]+\.md",
    ]
    results: list[str] = []
    for pattern in patterns:
        results.extend(re.findall(pattern, text))
    return sorted(set(results))


def main() -> int:
    if not PLAN_PATH.exists():
        print(f"Missing plan file: {PLAN_PATH}")
        return 1

    text = PLAN_PATH.read_text(encoding="utf-8")
    paths = extract_paths(text)

    allow_missing_mermaid = os.environ.get("THESIS_ALLOW_MISSING_MERMAID_PNG") == "1"

    missing: list[str] = []
    deferred: list[tuple[str, str]] = []
    for rel_path in paths:
        path = Path(rel_path)
        if path.exists():
            continue

        if rel_path.startswith("reports/week7/locked_eval_pack/"):
            missing.append(rel_path)
            continue

        if (
            allow_missing_mermaid
            and rel_path.startswith("docs/figures/")
            and rel_path.endswith(".png")
        ):
            mmd_path = path.with_suffix(".mmd")
            if mmd_path.exists():
                deferred.append((rel_path, str(mmd_path)))
                continue

        missing.append(rel_path)

    if deferred:
        for png_path, mmd_path in deferred:
            print(
                f"DEFERRED: missing {png_path}, found {mmd_path} (render later with mmdc)"
            )

    if missing:
        print("Missing files:")
        for rel_path in missing:
            print(f"- {rel_path}")

    print(
        "Summary: "
        f"{len(paths)} referenced, "
        f"{len(deferred)} deferred, "
        f"{len(missing)} missing"
    )
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
