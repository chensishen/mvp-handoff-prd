#!/usr/bin/env python3
"""Create a compact MVP-to-PRD handoff package from bundled templates."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


COMPACT_FILES = [
    ("交接型PRD模板.md", "01-交接型PRD.md"),
    ("需求追踪矩阵.csv", "02-需求追踪与验收矩阵.csv"),
    ("交接检查清单.md", "03-研发实施与发布清单.md"),
]

EXPANDED_FILES = [
    ("资料与证据台账模板.md", "00-资料与证据台账.md"),
    ("MVP审计模板.md", "01-MVP现状审计.md"),
    ("交接型PRD模板.md", "03-目标PRD.md"),
    ("需求追踪矩阵.csv", "04-需求追踪与测试矩阵.csv"),
    ("决策变更日志模板.md", "05-待确认决策与变更日志.md"),
    ("测试与验收模板.md", "06-UAT与OAT验收.md"),
    ("交接检查清单.md", "07-研发交接与发布清单.md"),
]

COMPACT_OUTPUTS = {name for _, name in COMPACT_FILES} | {"04-专家团评审记录.md"}
EXPANDED_OUTPUTS = {name for _, name in EXPANDED_FILES} | {
    "02-现状目标差距与技术债.md",
    "08-专家团评审记录.md",
}

GAP_TEMPLATE = """# <项目名称> 现状目标差距与技术债

## 1. 差距总览

| GAP-ID | 关联需求 | MVP 当前行为与证据 | 目标行为 | 处置 | 优先级 | 工程差距 | 风险 | Owner | 验收方式 |
|---|---|---|---|---|---|---|---|---|---|
| GAP-001 | FR-001 |  |  | 保留/补全/重构/重写/新增/移除/延期/待定 | Must |  |  |  |  |

## 2. 技术债

| DEBT-ID | 代码/环境证据 | 原因 | 影响 | 概率/等级 | 处置 | 临时控制 | Owner | 版本/日期 | 验收方法 | 风险接受人 |
|---|---|---|---|---|---|---|---|---|---|---|

## 3. 复用/重构/重写裁决

| 模块 | 结论 | 依据 | 替代方案 | 影响需求 | 批准人 | 日期 |
|---|---|---|---|---|---|---|
"""


def replace_project(path: Path, project: str) -> None:
    if path.suffix.lower() != ".md":
        return
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("<项目名称>", project), encoding="utf-8")


def set_prd_mode(path: Path, mode: str, risk_level: str) -> None:
    if "PRD" not in path.name:
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace("DELIVERY_MODE: STANDARD", f"DELIVERY_MODE: {mode}")
    text = text.replace("RISK_LEVEL: L1", f"RISK_LEVEL: {risk_level}")
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--project", required=True, help="Project name used in headings")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated files")
    parser.add_argument("--expert-panel", action="store_true", help="Also create an expert-panel review record")
    parser.add_argument("--mode", choices=("QUICK", "STANDARD", "HIGH_ASSURANCE"), default="STANDARD")
    parser.add_argument("--risk-level", choices=("L0", "L1", "L2", "L3"))
    parser.add_argument(
        "--expanded",
        action="store_true",
        help="Create the legacy eight-file layout when separate document ownership is required",
    )
    args = parser.parse_args()
    risk_level = args.risk_level or ("L2" if args.mode == "HIGH_ASSURANCE" else "L1")

    assets = Path(__file__).resolve().parent.parent / "assets"
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    files = EXPANDED_FILES if args.expanded else COMPACT_FILES
    targets = [out / name for _, name in files]
    if args.expanded:
        targets.append(out / "02-现状目标差距与技术债.md")
    include_panel = args.expert_panel or args.mode == "HIGH_ASSURANCE" or risk_level in {"L2", "L3"}
    if include_panel:
        targets.append(out / ("08-专家团评审记录.md" if args.expanded else "04-专家团评审记录.md"))
    alternate_outputs = COMPACT_OUTPUTS if args.expanded else EXPANDED_OUTPUTS
    conflicting = sorted(path.name for path in out.iterdir() if path.is_file() and path.name in alternate_outputs)
    if conflicting:
        parser.error(
            "output directory contains artifacts from the other layout; use a clean directory or move them first: "
            + ", ".join(conflicting)
        )
    existing = [str(path) for path in targets if path.exists()]
    if existing and not args.force:
        parser.error("refusing to overwrite existing files: " + ", ".join(existing))

    for source_name, target_name in files:
        target = out / target_name
        shutil.copyfile(assets / source_name, target)
        replace_project(target, args.project)
        set_prd_mode(target, args.mode, risk_level)

    if args.expanded:
        gap = out / "02-现状目标差距与技术债.md"
        gap.write_text(GAP_TEMPLATE.replace("<项目名称>", args.project), encoding="utf-8")

    if include_panel:
        panel = out / ("08-专家团评审记录.md" if args.expanded else "04-专家团评审记录.md")
        shutil.copyfile(assets / "专家团评审记录模板.md", panel)
        replace_project(panel, args.project)

    print(f"Created MVP handoff package at {out}")
    for path in targets:
        print(path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
