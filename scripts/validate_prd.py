#!/usr/bin/env python3
"""Lint a Markdown PRD and optionally enforce the Development Ready gate."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None


REQUIRED_CONCEPTS = {
    "document_control": ("文档控制",),
    "source": ("来源",),
    "goal": ("目标",),
    "mvp": ("MVP",),
    "current_state": ("现状", "基线"),
    "scope": ("范围",),
    "gap": ("差距",),
    "functional": ("功能需求",),
    "nfr": ("非功能", "质量要求"),
    "test": ("测试",),
    "acceptance": ("验收",),
    "release": ("发布",),
    "rollback": ("回滚",),
    "open_items": ("待确认", "开放问题"),
    "decisions": ("决策",),
}

HEADING = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
AC_ID = re.compile(r"\bAC-(FR-[A-Z0-9-]+)-\d+\b")
VAGUE = re.compile(r"体验良好|体验流畅|响应快|尽量快|安全可靠|稳定可靠|支持常见|兼容主流|实时同步|正常运行")
PLACEHOLDER = re.compile(r"<(?![!/?])[^>\n]+>|\[TODO\]|\bTBD\b|【待确认】")
UNRESOLVED = re.compile(r"待确认|未决|待指定|未提供|无法验证|未知")
GATE_FIELD = re.compile(r"^(PRD_STATUS|G1_BASELINE|G2_SCOPE|G3_DEVELOPMENT_READY|BLOCKING_IDS)\s*:\s*(.*?)\s*$", re.MULTILINE)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def requirement_blocks(text: str) -> list[tuple[str, int, str]]:
    headings = list(HEADING.finditer(text))
    results: list[tuple[str, int, str]] = []
    for index, heading in enumerate(headings):
        title_match = re.match(r"(FR-[A-Z0-9-]+)\b", heading.group(2))
        if not title_match:
            continue
        level = len(heading.group(1))
        end = len(text)
        for later in headings[index + 1 :]:
            if len(later.group(1)) <= level:
                end = later.start()
                break
        results.append((title_match.group(1), heading.start(), text[heading.start():end]))
    return results


def nonempty_field(block: str, names: tuple[str, ...]) -> bool:
    label = "|".join(re.escape(name) for name in names)
    pattern = re.compile(rf"(?:^|\n)[ \t]*[-*]?[ \t]*(?:{label})[ \t]*[:：][ \t]*(.+)", re.IGNORECASE)
    match = pattern.search(block)
    if not match:
        return False
    value = match.group(1).strip()
    return bool(value and not UNRESOLVED.search(value) and value not in {"-", "N/A"})


def lint(text: str, gate: str | None = None, traceability: Path | None = None) -> list[Finding]:
    findings: list[Finding] = []
    headings_text = "\n".join(match.group(2) for match in HEADING.finditer(text))

    for code, alternatives in REQUIRED_CONCEPTS.items():
        if not any(term.lower() in headings_text.lower() for term in alternatives):
            findings.append(Finding("error", f"missing_{code}", f"缺少必需章节/概念：{' / '.join(alternatives)}"))

    blocks = requirement_blocks(text)
    if not blocks:
        findings.append(Finding("error", "no_functional_requirement", "未找到以 FR-xxx 编号的功能需求标题"))

    seen: dict[str, int] = {}
    must_reqs: set[str] = set()
    for req_id, start, block in blocks:
        line = line_number(text, start)
        if req_id in seen:
            findings.append(Finding("error", "duplicate_requirement", f"需求 {req_id} 被重复定义；首次在第 {seen[req_id]} 行", line))
        else:
            seen[req_id] = line

        priority = re.search(r"优先级\s*[:：]\s*(Must|P0|必须)\b", block, re.IGNORECASE)
        is_must = bool(priority)
        if is_must:
            must_reqs.add(req_id)
            ac_match = re.search(rf"\bAC-{re.escape(req_id)}-\d+\b", block)
            if not ac_match:
                findings.append(Finding("error", "must_without_ac", f"Must 需求 {req_id} 没有对应 AC", line))
            else:
                ac_text = block[ac_match.start():]
                missing_gherkin = [word for word in ("Given", "When", "Then") if not re.search(rf"\b{word}\b", ac_text, re.IGNORECASE)]
                if missing_gherkin:
                    findings.append(Finding("error" if gate else "warning", "ac_not_executable", f"{req_id} 的 AC 缺少 {'/'.join(missing_gherkin)}", line))
            if not nonempty_field(block, ("Owner", "负责人")):
                findings.append(Finding("error" if gate else "warning", "missing_requirement_owner", f"Must 需求 {req_id} 缺少明确 Owner", line))
            if not nonempty_field(block, ("来源与业务价值", "来源", "业务价值")):
                findings.append(Finding("error" if gate else "warning", "missing_requirement_source", f"Must 需求 {req_id} 缺少来源/业务价值", line))
            if not nonempty_field(block, ("目标行为",)):
                findings.append(Finding("error" if gate else "warning", "missing_target_behavior", f"Must 需求 {req_id} 缺少目标行为", line))
            if gate and UNRESOLVED.search(block):
                findings.append(Finding("error", "unresolved_must_requirement", f"Must 需求 {req_id} 仍含未决内容", line))

    defined_reqs = set(seen)
    for ac in AC_ID.finditer(text):
        req_id = ac.group(1)
        if req_id not in defined_reqs:
            findings.append(Finding("warning", "orphan_ac", f"{ac.group(0)} 指向未定义的 {req_id}", line_number(text, ac.start())))

    for match in VAGUE.finditer(text):
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        line_end = len(text) if line_end == -1 else line_end
        sentence = text[line_start:line_end]
        quantified = re.search(r"(?:≤|≥|<|>|不超过|不少于|至少|最多)?\s*\d+(?:\.\d+)?\s*(?:ms|毫秒|秒|分钟|小时|天|%|％|并发|次|个|条|MB|GB|KB|TPS|QPS)", sentence, re.IGNORECASE)
        if not quantified and not re.search(r"待确认|N/A|不适用", sentence):
            findings.append(Finding("warning", "vague_language", f"不可测措辞“{match.group(0)}”需要量化或标待确认", line_number(text, match.start())))

    for match in PLACEHOLDER.finditer(text):
        findings.append(Finding("warning", "unresolved_placeholder", f"仍有占位/待确认内容：{match.group(0)}", line_number(text, match.start())))

    for offset, line_text in iter_lines(text):
        if line_text.lstrip().startswith("#"):
            continue
        if re.match(r"^\s*\|\s*(?:ID|[A-Z]+-ID)\b", line_text):
            continue
        match = UNRESOLVED.search(line_text)
        if match and not PLACEHOLDER.search(line_text):
            findings.append(Finding("warning", "unresolved_semantics", f"仍有未决语义：{match.group(0)}", line_number(text, offset)))
        if re.match(r"^\s*[-*]\s+[^:：]+[:：]\s*$", line_text):
            findings.append(Finding("warning", "empty_field", "字段仍为空", line_number(text, offset)))

    if "MVP" in text and not re.search(r"Commit|Build|版本|环境|证据", text, re.IGNORECASE):
        findings.append(Finding("warning", "weak_mvp_baseline", "MVP 章节未见版本、环境或证据字段"))
    if blocks and not re.search(r"需求追踪|追踪矩阵|Test ID|测试矩阵", text, re.IGNORECASE):
        findings.append(Finding("warning", "missing_traceability", "未发现需求—AC—测试追踪说明"))

    if gate == "development-ready":
        enforce_development_gate(text, findings, must_reqs, traceability)
    return findings


def iter_lines(text: str):
    offset = 0
    for line in text.splitlines(keepends=True):
        yield offset, line.rstrip("\r\n")
        offset += len(line)


def enforce_development_gate(text: str, findings: list[Finding], must_reqs: set[str], traceability: Path | None) -> None:
    fields = {match.group(1): match.group(2).strip().upper() for match in GATE_FIELD.finditer(text)}
    status = fields.get("PRD_STATUS")
    if status not in {"DEVELOPMENT_READY", "APPROVED"}:
        findings.append(Finding("error", "invalid_prd_status", "门禁模式要求 PRD_STATUS 为 DEVELOPMENT_READY 或 APPROVED"))
    for name in ("G1_BASELINE", "G2_SCOPE", "G3_DEVELOPMENT_READY"):
        if fields.get(name) != "PASS":
            findings.append(Finding("error", "gate_not_passed", f"{name} 必须为 PASS，当前为 {fields.get(name, 'MISSING')}"))
    blockers = fields.get("BLOCKING_IDS")
    if blockers not in {"NONE", "无", "[]"}:
        findings.append(Finding("error", "open_blockers", f"BLOCKING_IDS 必须为空，当前为 {blockers or 'MISSING'}"))
    if not must_reqs:
        findings.append(Finding("error", "no_committed_scope", "Development Ready 前至少要有一条已确定为 Must/P0 的范围需求"))

    objective_rows = [line for line in text.splitlines() if re.search(r"\|\s*OBJ-(?!ID\b)[A-Z0-9-]+\s*\|", line)]
    if not objective_rows or all("|  |" in row or UNRESOLVED.search(row) for row in objective_rows):
        findings.append(Finding("error", "missing_success_metric", "Development Ready 前必须填写可验证的目标/成功指标及口径"))

    if traceability is None:
        findings.append(Finding("error", "traceability_required", "门禁模式必须通过 --traceability 提供追踪矩阵 CSV"))
    else:
        validate_traceability(traceability, findings, must_reqs)


def validate_traceability(path: Path, findings: list[Finding], must_reqs: set[str]) -> None:
    if not path.is_file():
        findings.append(Finding("error", "traceability_missing", f"追踪矩阵不存在：{path}"))
        return
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, csv.Error) as exc:
        findings.append(Finding("error", "traceability_unreadable", f"无法读取追踪矩阵：{exc}"))
        return
    if not rows:
        findings.append(Finding("error", "traceability_empty", "追踪矩阵没有数据行"))
        return

    def get(row: dict[str, str], *needles: str) -> str:
        for key, value in row.items():
            normalized = (key or "").replace("_", "").lower()
            if any(needle.replace("_", "").lower() in normalized for needle in needles):
                return (value or "").strip()
        return ""

    covered: set[str] = set()
    for row in rows:
        req = get(row, "需求ID", "requirementid", "reqid")
        ac = get(row, "ACID", "验收标准")
        test = get(row, "TestID", "测试ID")
        owner = get(row, "Owner", "负责人")
        status = get(row, "状态", "status")
        ready_status = status.upper() in {"已确认", "CONFIRMED", "READY", "APPROVED"}
        if req in must_reqs and ac and test and owner and ready_status and not UNRESOLVED.search(ac + test + owner):
            covered.add(req)
    for req_id in sorted(must_reqs - covered):
        findings.append(Finding("error", "incomplete_traceability", f"Must 需求 {req_id} 未完整映射 AC 与 Test"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prd", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    parser.add_argument("--gate", choices=("development-ready",), help="Enforce a quality gate; implies strict mode")
    parser.add_argument("--traceability", type=Path, help="CSV traceability matrix used by gate validation")
    args = parser.parse_args()

    text = args.prd.read_text(encoding="utf-8")
    findings = lint(text, args.gate, args.traceability)
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)

    if args.as_json:
        print(json.dumps({"errors": errors, "warnings": warnings, "findings": [asdict(item) for item in findings]}, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            location = f":{item.line}" if item.line else ""
            print(f"{item.severity.upper()} {item.code}{location} {item.message}")
        print(f"Summary: {errors} error(s), {warnings} warning(s)")

    strict = args.strict or bool(args.gate)
    return 1 if errors or (strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
