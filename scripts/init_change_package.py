#!/usr/bin/env python3
"""Create a compact incremental PRD change record."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


EXPANDED_FILES = ("proposal.md", "requirements.md", "impact.md", "tasks.md", "decision.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--change-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--expanded", action="store_true", help="Create the legacy five-file change package")
    args = parser.parse_args()

    change_id = args.change_id.strip().upper()
    if not re.fullmatch(r"CHG-\d{3,}", change_id):
        parser.error("--change-id must match CHG-001")

    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    targets = [out / name for name in EXPANDED_FILES] if args.expanded else [out / f"{change_id}.md"]
    conflicting = (
        sorted(path.name for path in out.glob("CHG-*.md"))
        if args.expanded
        else sorted(name for name in EXPANDED_FILES if (out / name).is_file())
    )
    if conflicting:
        parser.error(
            "output directory contains artifacts from the other layout; use a clean directory or move them first: "
            + ", ".join(conflicting)
        )
    existing = [str(path) for path in targets if path.exists()]
    if existing and not args.force:
        parser.error("refusing to overwrite existing files: " + ", ".join(existing))

    for target in targets:
        source = assets_dir / "change-package" / target.name if args.expanded else assets_dir / "变更单模板.md"
        shutil.copyfile(source, target)
        text = target.read_text(encoding="utf-8")
        target.write_text(
            text.replace("<CHANGE_ID>", change_id).replace("<CHANGE_TITLE>", args.title.strip()),
            encoding="utf-8",
        )

    print(f"Created change package {change_id} at {out}")
    for target in targets:
        print(target.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
