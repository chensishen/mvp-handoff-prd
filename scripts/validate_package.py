#!/usr/bin/env python3
"""Validate cross-artifact integrity for an MVP handoff package."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import re
import sys
from pathlib import Path


COMPACT_FILES = {
    "prd": "01-交接型PRD.md",
    "trace": "02-需求追踪与验收矩阵.csv",
    "handoff": "03-研发实施与发布清单.md",
}

EXPANDED_FILES = {
    "sources": "00-资料与证据台账.md",
    "audit": "01-MVP现状审计.md",
    "gaps": "02-现状目标差距与技术债.md",
    "prd": "03-目标PRD.md",
    "trace": "04-需求追踪与测试矩阵.csv",
    "decisions": "05-待确认决策与变更日志.md",
    "tests": "06-UAT与OAT验收.md",
    "handoff": "07-研发交接与发布清单.md",
}


def select_layout(package: Path) -> tuple[str, dict[str, str]]:
    """Select one unambiguous layout while keeping existing eight-file packages valid."""
    has_compact = any((package / name).exists() for name in COMPACT_FILES.values())
    has_expanded = any((package / name).exists() for name in EXPANDED_FILES.values())
    if has_compact and has_expanded:
        raise ValueError("compact and expanded artifacts coexist")
    if has_compact:
        return "compact", COMPACT_FILES
    return "expanded", EXPANDED_FILES


def load_prd_validator(skill_dir: Path):
    path = skill_dir / "scripts" / "validate_prd.py"
    spec = importlib.util.spec_from_file_location("handoff_validate_prd", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def ids(text: str, prefix: str) -> set[str]:
    return set(re.findall(rf"\b{re.escape(prefix)}-[A-Z0-9-]+\b", text, re.IGNORECASE))


def normalized(row: dict[str, str], *names: str) -> str:
    for key, value in row.items():
        key_norm = (key or "").replace("_", "").replace(" ", "").lower()
        if any(name.replace("_", "").replace(" ", "").lower() in key_norm for name in names):
            return (value or "").strip()
    return ""


def normalized_enum(value: str) -> str:
    return re.sub(r"[\s-]+", "_", value.strip().upper())


def has_gate_signoff(handoff: str, gate: str) -> bool:
    accepted_by_gate = {
        "development ready": {"PASS", "READY", "APPROVED", "READY_WITH_ACCEPTED_RISKS", "PASS_WITH_ACCEPTED_RISKS", "通过"},
        "acceptance ready": {"PASS", "READY", "APPROVED", "ACCEPTED", "READY_WITH_ACCEPTED_RISKS", "PASS_WITH_ACCEPTED_RISKS", "通过", "接受"},
        "handoff accepted": {"PASS", "APPROVED", "ACCEPTED", "PASS_WITH_ACCEPTED_RISKS", "ACCEPTED_WITH_ACCEPTED_RISKS", "通过", "接受"},
    }
    accepted = accepted_by_gate[gate.lower()]
    for line in handoff.splitlines():
        if gate.lower() not in line.lower() or not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if (
            len(cells) >= 7
            and normalized_enum(cells[1]) in accepted
            and all(cells[index] and cells[index].upper() not in {"TBD", "N/A", "NONE", "-"} for index in (3, 4, 5))
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[6])
        ):
            return True
    return False


def has_open_blocker(text: str) -> bool:
    """Read decision tables by column name instead of relying on column order."""
    header: list[str] | None = None
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            header = None
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if "是否阻塞" in cells:
            header = cells
            continue
        if not header or len(cells) != len(header) or all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        blocker = cells[header.index("是否阻塞")].upper()
        state_index = next((header.index(name) for name in ("审批状态", "决策/待确认", "状态") if name in header), None)
        state = cells[state_index] if state_index is not None else ""
        if blocker in {"Y", "YES", "是"} and re.search(r"待审批|待确认|未决|草稿|PROPOSED|PENDING", state, re.IGNORECASE):
            return True
    return False


HANDOFF_FIELD = re.compile(
    r"^(G4_ACCEPTANCE_READY|G5_HANDOFF_ACCEPTED|BUILD_ID|TEST_ENV_ID|BLOCKING_DEFECT_IDS|UAT_OWNER|UAT_STATUS|OAT_STATUS|RELEASE_STATUS|HANDOFF_BLOCKING_IDS)\s*:\s*(.*?)\s*$",
    re.MULTILINE,
)


def handoff_fields(text: str) -> dict[str, str]:
    return {match.group(1): match.group(2).strip() for match in HANDOFF_FIELD.finditer(text)}


def unresolved_value(value: str) -> bool:
    return not value or value.upper() in {"TBD", "NOT_EVALUATED", "NONE", "N/A"}


def table_value(text: str, label: str) -> str:
    match = re.search(rf"\|\s*{re.escape(label)}\s*\|\s*([^|]*)\|", text)
    return match.group(1).strip() if match else ""


def bullet_value(text: str, label: str) -> str:
    match = re.search(rf"^-\s*{re.escape(label)}\s*[：:]\s*(.*?)\s*$", text, re.MULTILINE)
    return match.group(1).strip().strip("`") if match else ""


def validate_expert_panel(panel: str) -> list[str]:
    problems: list[str] = []
    for label in ("评审 ID / 日期", "共同证据包版本", "MVP Commit / Build / 环境", "评审范围 / 明确排除", "业务裁决人", "技术裁决人"):
        if unresolved_value(table_value(panel, label)):
            problems.append(f"panel_missing_contract_field: {label}")

    expert_rows: dict[str, list[str]] = {}
    for line in panel.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] in {"EXP-01", "EXP-02", "EXP-03"}:
            expert_rows[cells[0]] = cells
    for expert_id in ("EXP-01", "EXP-02", "EXP-03"):
        row = expert_rows.get(expert_id, [])
        if len(row) < 8 or normalized_enum(row[6]) not in {"完成", "COMPLETE", "COMPLETED"}:
            problems.append(f"panel_core_expert_incomplete: {expert_id} Round 1 未完成")

    conclusion = normalized_enum(bullet_value(panel, "结论"))
    if conclusion not in {"PASS", "PASS_WITH_ACCEPTED_RISKS"}:
        problems.append("panel_not_closed: 专家团记录存在但没有通过结论")
    for label in ("未关闭 P0", "缺席核心视角", "未裁决分歧"):
        value = normalized_enum(bullet_value(panel, label))
        if value not in {"NONE", "无", "[]"}:
            problems.append(f"panel_open_item: {label} 必须为 NONE/无/[]")
    if conclusion == "PASS_WITH_ACCEPTED_RISKS":
        accepted_risks = bullet_value(panel, "已接受 P1 风险及 Owner/期限")
        if unresolved_value(accepted_risks) or not re.search(r"\d{4}-\d{2}-\d{2}", accepted_risks):
            problems.append("panel_accepted_risk_incomplete: 有条件通过必须写明 P1 风险、Owner 和 YYYY-MM-DD 期限")
    if re.search(r"\|[^\n]*\bP0(?:\s+Blocker)?\b[^\n]*\|\s*(?:Y|YES|是)\s*\|", panel, re.IGNORECASE):
        problems.append("panel_p0_open: 专家团记录仍含 P0 阻塞")
    return problems


def validate(package: Path, gate: str = "development-ready") -> list[str]:
    problems: list[str] = []
    try:
        layout, files = select_layout(package)
    except ValueError:
        return ["ambiguous_layout: 紧凑版与扩展版工件不能混放在同一目录"]
    paths = {key: package / name for key, name in files.items()}
    for key, path in paths.items():
        if not path.is_file():
            problems.append(f"missing_artifact: {files[key]}")
    if problems:
        return problems

    texts = {key: path.read_text(encoding="utf-8-sig") for key, path in paths.items() if path.suffix == ".md"}
    validator = load_prd_validator(package.parent if (package.parent / "scripts" / "validate_prd.py").is_file() else Path(__file__).resolve().parent.parent)
    findings = validator.lint(texts["prd"], "development-ready", paths["trace"])
    problems.extend(f"prd_{item.severity}:{item.code}: {item.message}" for item in findings)

    if not has_gate_signoff(texts["handoff"], "Development Ready"):
        problems.append("missing_gate_signoff: Development Ready 需产品/业务、C 技术、QA 具名签署与日期")

    with paths["trace"].open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    source_text = texts["prd"] if layout == "compact" else texts["sources"] + texts["prd"]
    audit_text = texts["prd"] if layout == "compact" else texts["audit"] + texts["prd"]
    gap_text = texts["prd"] if layout == "compact" else texts["gaps"] + texts["prd"]
    decision_text = texts["prd"] if layout == "compact" else texts["decisions"] + texts["prd"]
    trace_text = paths["trace"].read_text(encoding="utf-8-sig")
    test_text = trace_text + texts["prd"] if layout == "compact" else texts["tests"]
    registry = {
        "SRC": ids(source_text, "SRC"),
        "OBJ": ids(texts["prd"], "OBJ"),
        "FR": ids(texts["prd"], "FR"),
        "GAP": ids(gap_text, "GAP"),
        "EVD": ids(audit_text, "EVD"),
        "AC": ids(texts["prd"], "AC"),
        "TEST": ids(test_text, "TEST"),
        "CHG": ids(decision_text, "CHG"),
        "TASK": ids(texts["handoff"] + texts["prd"], "TASK"),
    }
    seen: set[tuple[str, str, str]] = set()
    for number, row in enumerate(rows, start=2):
        values = {
            "SRC": normalized(row, "来源ID", "sourceid"),
            "OBJ": normalized(row, "目标ID", "objectiveid"),
            "FR": normalized(row, "需求ID", "requirementid", "reqid"),
            "GAP": normalized(row, "GAPID"),
            "EVD": normalized(row, "MVP证据ID", "evidenceid"),
            "AC": normalized(row, "ACID", "验收标准"),
            "TEST": normalized(row, "TestID", "测试ID"),
            "CHG": normalized(row, "变更ID", "changeid"),
            "TASK": normalized(row, "TASKID", "任务ID"),
        }
        key = (values["FR"], values["AC"], values["TEST"])
        if key in seen:
            problems.append(f"duplicate_trace_row:{number}: {key}")
        seen.add(key)
        for kind, value in values.items():
            if value and value not in registry[kind]:
                problems.append(f"broken_reference:{number}: {value} 未在对应工件中定义")
        if values["FR"] and values["AC"] and not values["AC"].upper().startswith(f"AC-{values['FR'].upper()}-"):
            problems.append(f"wrong_ac_owner:{number}: {values['AC']} 不属于 {values['FR']}")

    decisions = texts["prd"] if layout == "compact" else texts["decisions"]
    if has_open_blocker(decisions):
        problems.append("open_blocker: 决策日志仍有未关闭阻塞项")

    fields = handoff_fields(texts["handoff"])
    if gate in {"acceptance-ready", "handoff-accepted"}:
        if fields.get("G4_ACCEPTANCE_READY", "").upper() != "PASS":
            problems.append("gate_not_passed: G4_ACCEPTANCE_READY 必须为 PASS")
        for name in ("BUILD_ID", "TEST_ENV_ID", "UAT_OWNER"):
            if unresolved_value(fields.get(name, "")):
                problems.append(f"missing_acceptance_field: {name}")
        if fields.get("BLOCKING_DEFECT_IDS", "").upper() not in {"NONE", "无", "[]"}:
            problems.append("open_defects: BLOCKING_DEFECT_IDS 必须为空")
        if not has_gate_signoff(texts["handoff"], "Acceptance Ready"):
            problems.append("missing_gate_signoff: Acceptance Ready 需三方具名签署与日期")
        for number, row in enumerate(rows, start=2):
            if normalized(row, "优先级").upper() in {"MUST", "P0", "必须"} and not normalized(row, "验收证据"):
                problems.append(f"missing_acceptance_evidence:{number}: Must 需求缺验收证据")

    if gate == "handoff-accepted":
        if fields.get("G5_HANDOFF_ACCEPTED", "").upper() != "PASS":
            problems.append("gate_not_passed: G5_HANDOFF_ACCEPTED 必须为 PASS")
        if fields.get("HANDOFF_BLOCKING_IDS", "").upper() not in {"NONE", "无", "[]"}:
            problems.append("open_handoff_blockers: HANDOFF_BLOCKING_IDS 必须为空")
        if fields.get("UAT_STATUS", "").upper() != "ACCEPTED":
            problems.append("uat_not_accepted: UAT_STATUS 必须为 ACCEPTED")
        if fields.get("OAT_STATUS", "").upper() != "PASS":
            problems.append("oat_not_passed: OAT_STATUS 必须为 PASS")
        if normalized_enum(fields.get("RELEASE_STATUS", "")) not in {"GO", "CONDITIONAL_GO"}:
            problems.append("release_not_ready: RELEASE_STATUS 必须为 GO 或 CONDITIONAL_GO")
        if not has_gate_signoff(texts["handoff"], "Handoff Accepted"):
            problems.append("missing_gate_signoff: Handoff Accepted 需三方具名签署与日期")

    prd_fields = validator.gate_fields(texts["prd"])
    panel_required = (
        prd_fields.get("DELIVERY_MODE", "").upper() == "HIGH_ASSURANCE"
        or prd_fields.get("RISK_LEVEL", "").upper() in {"L2", "L3"}
    )
    panel_path = package / ("04-专家团评审记录.md" if layout == "compact" else "08-专家团评审记录.md")
    if panel_required and not panel_path.is_file():
        problems.append("missing_expert_panel: HIGH_ASSURANCE 或 L2/L3 必须包含专家团评审记录")
    if panel_path.is_file():
        panel = panel_path.read_text(encoding="utf-8-sig")
        problems.extend(validate_expert_panel(panel))

    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("--gate", choices=("development-ready", "acceptance-ready", "handoff-accepted"), default="development-ready")
    args = parser.parse_args()
    problems = validate(args.package_dir.resolve(), args.gate)
    for problem in problems:
        print(f"ERROR {problem}")
    print(f"Summary: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
