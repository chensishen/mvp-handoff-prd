#!/usr/bin/env python3
"""Create an eight-artifact MVP-to-PRD handoff package from bundled templates."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


FILES = [
    ("资料与证据台账模板.md", "00-资料与证据台账.md"),
    ("MVP审计模板.md", "01-MVP现状审计.md"),
    ("交接型PRD模板.md", "03-目标PRD.md"),
    ("需求追踪矩阵.csv", "04-需求追踪与测试矩阵.csv"),
    ("资料与证据台账模板.md", "05-待确认决策与变更日志.md"),
    ("测试与验收模板.md", "06-UAT与OAT验收.md"),
    ("交接检查清单.md", "07-研发交接与发布清单.md"),
]

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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--project", required=True, help="Project name used in headings")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated files")
    args = parser.parse_args()

    assets = Path(__file__).resolve().parent.parent / "assets"
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    targets = [out / name for _, name in FILES] + [out / "02-现状目标差距与技术债.md"]
    existing = [str(path) for path in targets if path.exists()]
    if existing and not args.force:
        parser.error("refusing to overwrite existing files: " + ", ".join(existing))

    for source_name, target_name in FILES:
        target = out / target_name
        shutil.copyfile(assets / source_name, target)
        replace_project(target, args.project)

    gap = out / "02-现状目标差距与技术债.md"
    gap.write_text(GAP_TEMPLATE.replace("<项目名称>", args.project), encoding="utf-8")

    # Replace the generic combined ledger with a focused log for artifact 05.
    log_path = out / "05-待确认决策与变更日志.md"
    log_path.write_text(
        f"# {args.project} 待确认、决策与变更日志\n\n"
        "| ID | 类型 | 问题或旧→新 | 影响需求/测试/发布 | 选项 | 结论 | 决策人 | 截止/日期 | 是否阻塞 | 依据 |\n"
        "|---|---|---|---|---|---|---|---|---|---|\n"
        "| DEC-001 | 待确认/决策/变更 |  |  |  |  |  |  |  |  |\n",
        encoding="utf-8",
    )

    print(f"Created MVP handoff package at {out}")
    for path in targets:
        print(path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
