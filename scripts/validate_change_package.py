#!/usr/bin/env python3
"""Validate the structure and optional approval gate of an incremental change package."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPANDED_FILES = ("proposal.md", "requirements.md", "impact.md", "tasks.md", "decision.md")
CHANGE_ID = re.compile(r"\bCHG-\d{3,}\b")
REQ_ID = re.compile(r"^(?:FR|BR|NFR|API|DATA|SEC|OBS|OPS)-[A-Z0-9-]+$")
TASK_ID = re.compile(r"^TASK-[A-Z0-9-]+$")
PLACEHOLDER = re.compile(r"^(?:TBD|N/?A|<[^>]+>|-|\s*)$", re.IGNORECASE)


def cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def meaningful(value: str) -> bool:
    return bool(value and not PLACEHOLDER.fullmatch(value))


def section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not match:
        return ""
    end = re.search(r"^##\s+", text[match.end():], re.MULTILINE)
    return text[match.end(): match.end() + end.start()] if end else text[match.end():]


def data_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        row = cells(line)
        if not row or all(re.fullmatch(r":?-+:?", value) for value in row):
            continue
        rows.append(row)
    return rows[1:] if rows else []


def validate(package: Path, gate: str | None = None) -> list[str]:
    problems: list[str] = []
    compact_paths = sorted(package.glob("CHG-*.md"))
    expanded_paths = [package / name for name in EXPANDED_FILES]
    if compact_paths and any(path.is_file() for path in expanded_paths):
        return ["ambiguous_layout: 紧凑变更单与五文件变更包不能混放在同一目录"]
    compact = len(compact_paths) == 1 and not any((package / name).exists() for name in EXPANDED_FILES)
    paths = compact_paths if compact else [package / name for name in EXPANDED_FILES]
    if not compact and len(compact_paths) > 1:
        problems.append("multiple_compact_changes: 一个目录只允许一个紧凑变更单")
    for path in paths:
        if not path.is_file():
            problems.append(f"missing_artifact: {path.name}")
    if problems:
        return problems

    texts = {path.name: path.read_text(encoding="utf-8-sig") for path in paths}
    identifiers = {match.group(0) for text in texts.values() for match in CHANGE_ID.finditer(text)}
    if len(identifiers) != 1:
        problems.append(f"inconsistent_change_id: found {sorted(identifiers)}")
    elif compact and paths[0].stem not in identifiers:
        problems.append(f"change_id_filename_mismatch: {paths[0].name} 与文档内 {next(iter(identifiers))} 不一致")

    status_values = {
        match.group(1).upper()
        for text in texts.values()
        for match in re.finditer(r"^CHANGE_STATUS:\s*(\S+)\s*$", text, re.MULTILINE | re.IGNORECASE)
    }
    if len(status_values) > 1:
        problems.append(f"inconsistent_change_status: found {sorted(status_values)}")

    compact_name = paths[0].name if compact else None
    requirements = texts[compact_name] if compact_name else texts["requirements.md"]
    if compact:
        delta_rows = [row for row in data_rows(section(requirements, "2. 需求 Delta")) if len(row) >= 7 and REQ_ID.fullmatch(row[1])]
        for row in delta_rows:
            change_type = row[0].upper()
            required_indexes = (3, 4, 6) if change_type == "ADDED" else (2, 3, 4, 6)
            if change_type not in {"ADDED", "MODIFIED", "REMOVED"} or not all(meaningful(row[index]) for index in required_indexes):
                problems.append(f"incomplete_delta: {row[1]} 缺少前后语义、原因/来源或 Owner")
    else:
        delta_rows = []
        for heading, required_indexes in (("ADDED", (1, 2, 3, 4)), ("MODIFIED", (1, 2, 3, 4)), ("REMOVED", (1, 2, 3, 4))):
            for row in data_rows(section(requirements, heading)):
                if row and REQ_ID.fullmatch(row[0]):
                    delta_rows.append(row)
                    if len(row) <= max(required_indexes) or not all(meaningful(row[index]) for index in required_indexes):
                        problems.append(f"incomplete_delta: {row[0]} 的 {heading} 信息不完整")
    if not delta_rows:
        problems.append("empty_delta: 需求 Delta 没有实际变更的需求 ID")

    impact = texts[compact_name] if compact_name else texts["impact.md"]
    impact_body = section(impact, "3. 影响评估") if compact else impact
    impact_rows = [row for row in data_rows(impact_body) if len(row) >= 2]
    if len(impact_rows) < 7 or any(not meaningful(row[1]) for row in impact_rows):
        problems.append("incomplete_impact: 影响维度必须填写影响或 N/A + 理由")

    if gate == "approved":
        proposal = texts[compact_name] if compact_name else texts["proposal.md"]
        decision = texts[compact_name] if compact_name else texts["decision.md"]
        baseline_match = re.search(r"^BASELINE_ID:\s*(.*?)\s*$", proposal, re.MULTILINE | re.IGNORECASE)
        if not baseline_match or not meaningful(baseline_match.group(1)):
            problems.append("missing_baseline: 批准前必须指定 BASELINE_ID")
        if status_values != {"APPROVED"}:
            problems.append("not_approved: CHANGE_STATUS 必须为 APPROVED")
        conclusion = re.search(r"\|\s*结论\s*\|\s*([^|]*)\|", decision)
        if not conclusion or conclusion.group(1).strip().upper() != "APPROVED":
            problems.append("approval_conclusion_mismatch: 决策表结论必须为 APPROVED")
        for label in ("业务/客户授权人", "C 技术估算确认人", "QA/验收影响确认人", "决策日期/证据"):
            match = re.search(rf"\|\s*{re.escape(label)}\s*\|\s*([^|]*)\|", decision)
            if not match or not meaningful(match.group(1)):
                problems.append(f"missing_approval_field: {label}")
        date_match = re.search(r"\|\s*决策日期/证据\s*\|\s*([^|]*)\|", decision)
        if date_match and not re.search(r"\d{4}-\d{2}-\d{2}", date_match.group(1)):
            problems.append("invalid_approval_date: 决策日期/证据必须包含 YYYY-MM-DD")
        tasks = texts[compact_name] if compact_name else texts["tasks.md"]
        task_body = section(tasks, "4. 实施任务") if compact else tasks
        if not any(row and TASK_ID.fullmatch(row[0]) and len(row) >= 7 and all(meaningful(row[index]) for index in (1, 2, 4, 5, 6)) for row in data_rows(task_body)):
            problems.append("missing_implementation_task: APPROVED 变更必须有完整 TASK")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("--gate", choices=("approved",))
    args = parser.parse_args()
    problems = validate(args.package_dir.resolve(), args.gate)
    for problem in problems:
        print(f"ERROR {problem}")
    print(f"Summary: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
