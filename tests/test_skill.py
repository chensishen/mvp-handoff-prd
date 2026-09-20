from __future__ import annotations

import csv
import importlib.util
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = SKILL_DIR / "scripts" / "validate_prd.py"
INITIALIZER_PATH = SKILL_DIR / "scripts" / "init_handoff_package.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_prd", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def valid_prd() -> str:
    return textwrap.dedent(
        """
        # 会议纪要助手交接型 PRD

        PRD_STATUS: DEVELOPMENT_READY
        G1_BASELINE: PASS
        G2_SCOPE: PASS
        G3_DEVELOPMENT_READY: PASS
        BLOCKING_IDS: NONE

        ## 0. 文档控制
        版本 V1.0；基线 Commit abc123；Owner 张三；日期 2026-09-18。

        ## 1. 来源与目标
        来源为 SRC-001 已批准内部立项，目标用户为会议主持人。

        | OBJ-ID | 业务目标 | 指标 | 基线 | 目标 | 口径/数据源 | 时间窗 | Owner | 状态 |
        |---|---|---|---|---|---|---|---|---|
        | OBJ-001 | 减少整理时间 | 单次整理时长中位数 | 30 分钟 | 10 分钟以内 | 工时系统 | 上线后四周 | 李四 | 已确认 |

        ## 2. MVP 现状基线
        Commit abc123 已在测试环境复现；上传界面已实现，真实转写尚未接入，证据 EVD-001 已归档。

        ## 3. 范围与差距
        本期接入已采购转写服务；GAP-001 已批准按补全处理。

        ## 4. 功能需求

        ### FR-001 上传会议音频并获得转写文本
        - 来源与业务价值：SRC-001；减少人工整理时间
        - MVP 现状与证据：上传界面可用，后端为 Mock；EVD-001
        - 目标行为：主持人上传 MP3 后获得可编辑转写文本
        - 角色/前置条件：已登录主持人，音频小于 100 MB
        - 触发：提交上传
        - 主流程：上传、转写、展示文本
        - 分支/异常/恢复：服务超时后显示失败并允许重试
        - 状态与数据副作用：任务转为成功或失败并记录审计事件
        - 权限：仅创建者可查看
        - 优先级：Must
        - 依赖：已采购转写服务
        - Owner：王五
        - 状态：已确认

        AC-FR-001-01
        Given 已登录主持人和一份有效 MP3
        When 主持人提交上传
        Then 系统创建一个转写任务并显示可编辑文本

        ## 5. 非功能与质量要求
        NFR-001：在测试环境、10 个并发任务下，95% 的 30 分钟音频在 10 分钟内完成。

        ## 6. 测试与验收
        需求追踪矩阵将 FR-001、AC-FR-001-01 与 Test ID TEST-001 对应。

        ## 7. 发布与回滚
        先灰度；错误率连续 10 分钟超过 5% 时回滚应用版本。

        ## 8. 待确认与决策
        当前无开放问题。DEC-001 已确认使用已采购服务，日期 2026-09-18。
        """
    ).strip() + "\n"


def write_trace(path: Path, *, test_id: str = "TEST-001", owner: str = "王五", status: str = "已确认") -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["来源ID", "目标ID", "需求ID", "AC_ID", "Test_ID", "状态", "Owner"])
        writer.writerow(["SRC-001", "OBJ-001", "FR-001", "AC-FR-001-01", test_id, status, owner])


def codes(findings) -> set[str]:
    return {item.code for item in findings}


class PackageInitializerTests(unittest.TestCase):
    def test_generates_eight_artifacts_and_replaces_project_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "handoff"
            result = subprocess.run(
                [sys.executable, str(INITIALIZER_PATH), str(output), "--project", "测试项目"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = {f"{index:02d}-{name}" for index, name in enumerate([
                "资料与证据台账.md",
                "MVP现状审计.md",
                "现状目标差距与技术债.md",
                "目标PRD.md",
                "需求追踪与测试矩阵.csv",
                "待确认决策与变更日志.md",
                "UAT与OAT验收.md",
                "研发交接与发布清单.md",
            ])}
            self.assertEqual({path.name for path in output.iterdir()}, expected)
            self.assertIn("# 测试项目", (output / "03-目标PRD.md").read_text(encoding="utf-8"))

    def test_refuses_to_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "handoff"
            first = subprocess.run([sys.executable, str(INITIALIZER_PATH), str(output), "--project", "A"], capture_output=True)
            second = subprocess.run([sys.executable, str(INITIALIZER_PATH), str(output), "--project", "B"], capture_output=True)
            self.assertEqual(first.returncode, 0)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("# A", (output / "03-目标PRD.md").read_text(encoding="utf-8"))


class StructuralLintTests(unittest.TestCase):
    def test_bundled_template_is_a_valid_draft_with_warnings(self):
        template = (SKILL_DIR / "assets" / "交接型PRD模板.md").read_text(encoding="utf-8")
        findings = VALIDATOR.lint(template)
        self.assertFalse([item for item in findings if item.severity == "error"])
        self.assertIn("unresolved_placeholder", codes(findings))

    def test_missing_source_and_goal_are_errors(self):
        document = valid_prd().replace("## 1. 来源与目标", "## 1. 项目背景")
        self.assertTrue({"missing_source", "missing_goal"}.issubset(codes(VALIDATOR.lint(document))))

    def test_duplicate_requirement_is_error(self):
        document = valid_prd() + "\n### FR-001 重复定义\n- 优先级：Should\n"
        self.assertIn("duplicate_requirement", codes(VALIDATOR.lint(document)))

    def test_must_without_ac_is_error(self):
        document = valid_prd().replace("AC-FR-001-01", "验收编号缺失", 1)
        self.assertIn("must_without_ac", codes(VALIDATOR.lint(document)))

    def test_ac_without_given_when_then_is_warning_in_draft(self):
        document = valid_prd().replace("Given 已登录主持人和一份有效 MP3\nWhen 主持人提交上传\nThen 系统创建一个转写任务并显示可编辑文本", "系统应完成转写")
        findings = VALIDATOR.lint(document)
        self.assertIn("ac_not_executable", codes(findings))
        self.assertTrue(any(item.code == "ac_not_executable" and item.severity == "warning" for item in findings))

    def test_vague_language_is_warning(self):
        document = valid_prd().replace("减少人工整理时间", "保证体验流畅", 1)
        self.assertIn("vague_language", codes(VALIDATOR.lint(document)))

    def test_last_requirement_does_not_absorb_later_sections(self):
        document = valid_prd().replace("- 优先级：Must", "- 优先级：Should").replace("AC-FR-001-01", "AC-FR-001-01", 1)
        document = document.replace("## 5. 非功能与质量要求", "## 5. 非功能与质量要求\nMust 是后续章节说明，不是 FR-001 的优先级")
        self.assertNotIn("must_without_ac", codes(VALIDATOR.lint(document)))


class DevelopmentReadyGateTests(unittest.TestCase):
    def test_complete_document_and_traceability_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            findings = VALIDATOR.lint(valid_prd(), "development-ready", trace)
            self.assertEqual(findings, [])

    def test_draft_template_fails_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace, owner="", status="草稿")
            template = (SKILL_DIR / "assets" / "交接型PRD模板.md").read_text(encoding="utf-8")
            result_codes = codes(VALIDATOR.lint(template, "development-ready", trace))
            self.assertTrue({"invalid_prd_status", "gate_not_passed", "open_blockers", "missing_success_metric", "incomplete_traceability"}.issubset(result_codes))

    def test_open_blockers_fail_gate(self):
        document = valid_prd().replace("BLOCKING_IDS: NONE", "BLOCKING_IDS: DEC-001")
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            self.assertIn("open_blockers", codes(VALIDATOR.lint(document, "development-ready", trace)))

    def test_unresolved_must_requirement_fails_gate(self):
        document = valid_prd().replace("- 依赖：已采购转写服务", "- 依赖：待确认")
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            self.assertIn("unresolved_must_requirement", codes(VALIDATOR.lint(document, "development-ready", trace)))

    def test_missing_owner_source_and_target_fail_gate(self):
        document = valid_prd().replace("- Owner：王五", "- Owner：").replace("- 来源与业务价值：SRC-001；减少人工整理时间", "- 来源与业务价值：").replace("- 目标行为：主持人上传 MP3 后获得可编辑转写文本", "- 目标行为：")
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            result_codes = codes(VALIDATOR.lint(document, "development-ready", trace))
            self.assertTrue({"missing_requirement_owner", "missing_requirement_source", "missing_target_behavior"}.issubset(result_codes))

    def test_incomplete_traceability_fails_gate(self):
        for kwargs in ({"test_id": ""}, {"owner": ""}, {"status": "草稿"}):
            with self.subTest(kwargs=kwargs), tempfile.TemporaryDirectory() as temp_dir:
                trace = Path(temp_dir) / "trace.csv"
                write_trace(trace, **kwargs)
                self.assertIn("incomplete_traceability", codes(VALIDATOR.lint(valid_prd(), "development-ready", trace)))

    def test_gate_requires_traceability_file(self):
        self.assertIn("traceability_required", codes(VALIDATOR.lint(valid_prd(), "development-ready", None)))

    def test_cli_gate_treats_warning_as_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            prd = Path(temp_dir) / "prd.md"
            trace = Path(temp_dir) / "trace.csv"
            prd.write_text(valid_prd().replace("减少人工整理时间", "保证体验流畅", 1), encoding="utf-8")
            write_trace(trace)
            result = subprocess.run(
                [sys.executable, str(VALIDATOR_PATH), str(prd), "--gate", "development-ready", "--traceability", str(trace)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("vague_language", result.stdout)


if __name__ == "__main__":
    unittest.main()
