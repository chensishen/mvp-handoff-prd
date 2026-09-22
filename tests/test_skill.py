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
CHANGE_INITIALIZER_PATH = SKILL_DIR / "scripts" / "init_change_package.py"
CHANGE_VALIDATOR_PATH = SKILL_DIR / "scripts" / "validate_change_package.py"
PACKAGE_VALIDATOR_PATH = SKILL_DIR / "scripts" / "validate_package.py"


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
        DELIVERY_MODE: STANDARD
        RISK_LEVEL: L1
        BASELINE_ID: commit-abc123
        G1_BASELINE: PASS
        G2_SCOPE: PASS
        G3_DEVELOPMENT_READY: PASS
        MAIN_FLOW_STATUS: APPROVED
        MAIN_FLOW_OWNER: 李四
        DECISION_ASSURANCE: PASS
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

        | DA-ID | 类型 | 决策/承诺对象 | 授权决策人 | 授权与来源证据 | 一致性/约束检查 | 可行性/估算证据 | 影响需求/验收/成本/工期 | 剩余风险/控制 | 有效期/复核触发 | 校验结论 |
        |---|---|---|---|---|---|---|---|---|---|---|
        | DA-001 | CUSTOMER_COMMITMENT | N/A：内部项目无客户承诺 | N/A：由内部 Sponsor 管理 | N/A：无合同或客户承诺 | N/A：无外部承诺约束 | N/A：不适用客户交付估算 | N/A：不影响外部验收 | N/A：无客户承诺风险 | N/A：若转为外部项目则复核 | NOT_APPLICABLE |
        | DA-002 | CORE_BUSINESS_RULE | 主持人提交音频后获得转写 | 李四（业务 Owner） | SRC-001 / DEC-001 | 与已批准主流程、权限和数据规则一致 | 真实转写接口 PoC EVD-001 已验证 | FR-001 / AC-FR-001-01 / 采购成本已确认 | 服务超时；允许重试并记录失败 | 来源或主流程变更时复核 | VALIDATED |
        | DA-003 | TECH_ESTIMATE | FR-001 开发估算 | 王五（C 技术负责人） | EST-001 / 基线 commit-abc123 | 范围与 GAP-001、依赖和保护边界一致 | 3–5 人日，置信度中；含接口联调假设 | FR-001 / TEST-001 / 采购依赖 | 第三方沙箱不稳定；预留联调缓冲 | 接口契约或基线变化时重估 | VALIDATED |
        | DA-004 | RISK_ACCEPTANCE | N/A：当前无请求接受的剩余风险 | N/A：没有风险接受事项 | N/A：风险均有控制且未申请例外 | N/A：没有豁免安全或合规约束 | N/A：不影响当前估算 | N/A：没有例外影响验收 | N/A：不存在待接受的剩余风险 | N/A：出现例外申请时复核 | NOT_APPLICABLE |
        """
    ).strip() + "\n"


def with_chinese_status_footer(document: str) -> str:
    old_fields = document[document.index("PRD_STATUS:"):document.index("## 0. 文档控制")]
    footer = "\n## 20. 状态与门禁摘要\n\n| 字段 | 当前值 |\n|---|---|\n"
    for label, key in VALIDATOR.GATE_LABELS.items():
        footer += f"| {label} | {VALIDATOR.gate_fields(document)[key]} |\n"
    return document.replace(old_fields, "") + footer


def write_trace(path: Path, *, test_id: str = "TEST-001", owner: str = "王五", status: str = "已确认", evidence: str = "") -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["来源ID", "目标ID", "需求ID", "GAP_ID", "MVP证据ID", "优先级", "AC_ID", "Test_ID", "验收证据", "状态", "Owner"])
        writer.writerow(["SRC-001", "OBJ-001", "FR-001", "GAP-001", "EVD-001", "Must", "AC-FR-001-01", test_id, evidence, status, owner])


def codes(findings) -> set[str]:
    return {item.code for item in findings}


def write_valid_package(package: Path) -> None:
    package.mkdir(parents=True)
    prd = "SRC-001\nEVD-001\nGAP-001\n" + valid_prd() + "\n| Development Ready | PASS | NONE | 张三/王五/赵六 | 2026-09-20 |\n"
    (package / "01-交接型PRD.md").write_text(prd, encoding="utf-8")
    write_trace(package / "02-需求追踪与验收矩阵.csv")
    (package / "03-研发实施与发布清单.md").write_text(
        "G4_ACCEPTANCE_READY: NOT_EVALUATED\nG5_HANDOFF_ACCEPTED: NOT_EVALUATED\n"
        "BUILD_ID: TBD\nTEST_ENV_ID: TBD\nBLOCKING_DEFECT_IDS: TBD\nUAT_OWNER: TBD\n"
        "UAT_STATUS: NOT_EVALUATED\nOAT_STATUS: NOT_EVALUATED\nRELEASE_STATUS: NOT_EVALUATED\nHANDOFF_BLOCKING_IDS: TBD\n"
        "| Development Ready | PASS | NONE | 张三 | 王五 | 赵六 | 2026-09-20 |\n",
        encoding="utf-8",
    )


def write_valid_expanded_package(package: Path) -> None:
    package.mkdir(parents=True)
    (package / "00-资料与证据台账.md").write_text("SRC-001\nEVD-001\n", encoding="utf-8")
    (package / "01-MVP现状审计.md").write_text("EVD-001\n", encoding="utf-8")
    (package / "02-现状目标差距与技术债.md").write_text("GAP-001\n", encoding="utf-8")
    prd = valid_prd() + "\n| Development Ready | PASS | NONE | 张三/王五/赵六 | 2026-09-20 |\n"
    (package / "03-目标PRD.md").write_text(prd, encoding="utf-8")
    write_trace(package / "04-需求追踪与测试矩阵.csv")
    (package / "05-待确认决策与变更日志.md").write_text("DEC-001 已关闭\n", encoding="utf-8")
    (package / "06-UAT与OAT验收.md").write_text("TEST-001\n", encoding="utf-8")
    (package / "07-研发交接与发布清单.md").write_text(
        "G4_ACCEPTANCE_READY: NOT_EVALUATED\nG5_HANDOFF_ACCEPTED: NOT_EVALUATED\n"
        "BUILD_ID: TBD\nTEST_ENV_ID: TBD\nBLOCKING_DEFECT_IDS: TBD\nUAT_OWNER: TBD\n"
        "UAT_STATUS: NOT_EVALUATED\nOAT_STATUS: NOT_EVALUATED\nRELEASE_STATUS: NOT_EVALUATED\nHANDOFF_BLOCKING_IDS: TBD\n"
        "| Development Ready | PASS | NONE | 张三 | 王五 | 赵六 | 2026-09-20 |\n",
        encoding="utf-8",
    )


class PackageInitializerTests(unittest.TestCase):
    def test_generates_compact_three_artifacts_and_replaces_project_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "handoff"
            result = subprocess.run(
                [sys.executable, str(INITIALIZER_PATH), str(output), "--project", "测试项目"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = {"01-交接型PRD.md", "02-需求追踪与验收矩阵.csv", "03-研发实施与发布清单.md"}
            self.assertEqual({path.name for path in output.iterdir()}, expected)
            self.assertIn("# 测试项目", (output / "01-交接型PRD.md").read_text(encoding="utf-8"))

    def test_expanded_flag_keeps_legacy_eight_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "handoff"
            result = subprocess.run(
                [sys.executable, str(INITIALIZER_PATH), str(output), "--project", "兼容项目", "--expanded"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(list(output.iterdir())), 8)
            self.assertTrue((output / "03-目标PRD.md").is_file())

    def test_refuses_to_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "handoff"
            first = subprocess.run([sys.executable, str(INITIALIZER_PATH), str(output), "--project", "A"], capture_output=True)
            second = subprocess.run([sys.executable, str(INITIALIZER_PATH), str(output), "--project", "B"], capture_output=True)
            self.assertEqual(first.returncode, 0)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("# A", (output / "01-交接型PRD.md").read_text(encoding="utf-8"))

    def test_expert_panel_flag_adds_review_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "handoff"
            result = subprocess.run(
                [sys.executable, str(INITIALIZER_PATH), str(output), "--project", "评审项目", "--expert-panel"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            panel = output / "04-专家团评审记录.md"
            self.assertTrue(panel.is_file())
            self.assertIn("# 评审项目 专家团评审记录", panel.read_text(encoding="utf-8"))

    def test_high_assurance_sets_mode_risk_and_panel(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "handoff"
            result = subprocess.run(
                [sys.executable, str(INITIALIZER_PATH), str(output), "--project", "高保障项目", "--mode", "HIGH_ASSURANCE"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            prd = (output / "01-交接型PRD.md").read_text(encoding="utf-8")
            self.assertIn("| 交付模式 | HIGH_ASSURANCE |", prd)
            self.assertIn("| 风险等级 | L2 |", prd)
            self.assertTrue(prd.rstrip().endswith("| 阻塞项编号 | TBD |"))
            self.assertNotIn("DELIVERY_MODE:", prd)
            self.assertTrue((output / "04-专家团评审记录.md").is_file())

    def test_l2_or_l3_risk_always_adds_expert_panel(self):
        for risk_level in ("L2", "L3"):
            with self.subTest(risk_level=risk_level), tempfile.TemporaryDirectory() as temp_dir:
                output = Path(temp_dir) / "handoff"
                result = subprocess.run(
                    [sys.executable, str(INITIALIZER_PATH), str(output), "--project", "风险项目", "--risk-level", risk_level],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((output / "04-专家团评审记录.md").is_file())

    def test_refuses_mixed_handoff_layout_even_with_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "handoff"
            subprocess.run(
                [sys.executable, str(INITIALIZER_PATH), str(output), "--project", "扩展", "--expanded"],
                capture_output=True,
                check=True,
            )
            result = subprocess.run(
                [sys.executable, str(INITIALIZER_PATH), str(output), "--project", "紧凑", "--force"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("other layout", result.stderr)

    def test_generates_incremental_change_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "change"
            result = subprocess.run(
                [sys.executable, str(CHANGE_INITIALIZER_PATH), str(output), "--change-id", "CHG-007", "--title", "调整客户验收口径"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({path.name for path in output.iterdir()}, {"CHG-007.md"})
            self.assertIn("CHG-007", (output / "CHG-007.md").read_text(encoding="utf-8"))

    def test_expanded_change_flag_keeps_legacy_five_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "change"
            result = subprocess.run(
                [sys.executable, str(CHANGE_INITIALIZER_PATH), str(output), "--change-id", "CHG-009", "--title", "分权变更", "--expanded"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({path.name for path in output.iterdir()}, {"proposal.md", "requirements.md", "impact.md", "tasks.md", "decision.md"})

    def test_refuses_mixed_change_layout_even_with_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "change"
            subprocess.run(
                [sys.executable, str(CHANGE_INITIALIZER_PATH), str(output), "--change-id", "CHG-012", "--title", "紧凑"],
                capture_output=True,
                check=True,
            )
            result = subprocess.run(
                [sys.executable, str(CHANGE_INITIALIZER_PATH), str(output), "--change-id", "CHG-012", "--title", "扩展", "--expanded", "--force"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("other layout", result.stderr)
            (output / "proposal.md").write_text("CHG-012\n", encoding="utf-8")
            validation = subprocess.run(
                [sys.executable, str(CHANGE_VALIDATOR_PATH), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn("ambiguous_layout", validation.stdout)

    def test_empty_change_package_fails_validation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "change"
            subprocess.run(
                [sys.executable, str(CHANGE_INITIALIZER_PATH), str(output), "--change-id", "CHG-008", "--title", "空变更"],
                capture_output=True,
                check=True,
            )
            result = subprocess.run(
                [sys.executable, str(CHANGE_VALIDATOR_PATH), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("empty_delta", result.stdout)

    def test_change_id_without_content_still_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "change"
            subprocess.run(
                [sys.executable, str(CHANGE_INITIALIZER_PATH), str(output), "--change-id", "CHG-010", "--title", "空内容"],
                capture_output=True,
                check=True,
            )
            change = output / "CHG-010.md"
            change.write_text(change.read_text(encoding="utf-8").replace("<REQ-ID>", "FR-001"), encoding="utf-8")
            result = subprocess.run([sys.executable, str(CHANGE_VALIDATOR_PATH), str(output)], text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("incomplete_delta", result.stdout)
            self.assertIn("incomplete_impact", result.stdout)

    def test_complete_approved_change_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "change"
            output.mkdir()
            (output / "CHG-011.md").write_text(
                textwrap.dedent(
                    """
                    # CHG-011 调整审批规则变更单
                    CHANGE_STATUS: APPROVED
                    BASELINE_ID: release-2026-09

                    ## 1. 提案
                    已确认来源 SRC-001。

                    ## 2. 需求 Delta
                    | 类型 | 需求ID | 变更前 | 变更后/新要求 | 原因/来源 | 受影响 AC/Test | Owner |
                    |---|---|---|---|---|---|---|
                    | MODIFIED | FR-001 | 直接提交 | 经理审批后提交 | SRC-001 | AC-FR-001-01 / TEST-001 | 李四 |

                    ## 3. 影响评估
                    | 维度 | 影响或 N/A + 理由 | 证据/估算人 | 控制与 Owner |
                    |---|---|---|---|
                    | 范围/用户/流程 | 增加经理审批节点 | SRC-001 | 产品张三 |
                    | 技术方案/工期 | 增加状态和接口 | 王五 | C 技术王五 |
                    | 商务/费用/合同 | N/A，无外部合同 | 张三 | 张三 |
                    | API/数据/迁移 | 新增审批状态 | 王五 | 王五 |
                    | 安全/隐私/合规 | N/A，不新增数据 | 赵六 | 赵六 |
                    | 测试/UAT/验收 | 增加审批分支 | 赵六 | 赵六 |
                    | 发布/运维/回滚 | 使用功能开关 | 王五 | 王五 |

                    ## 4. 实施任务
                    | TASK-ID | 关联需求 | 边界/保护边界 | Depends | Owner | 验证命令 | 状态 |
                    |---|---|---|---|---|---|---|
                    | TASK-011 | FR-001 | 审批模块；不改认证 | NONE | 王五 | pytest tests/test_approval.py | READY |

                    ## 5. 决策与生效
                    | 项目 | 内容 |
                    |---|---|
                    | 结论 | APPROVED |
                    | 业务/客户授权人 | 张三 |
                    | C 技术估算确认人 | 王五 |
                    | QA/验收影响确认人 | 赵六 |
                    | 决策日期/证据 | 2026-09-20 / DEC-011 |
                    """
                ).strip() + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(CHANGE_VALIDATOR_PATH), str(output), "--gate", "approved"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            change = output / "CHG-011.md"
            change.write_text(change.read_text(encoding="utf-8").replace("BASELINE_ID: release-2026-09\n", ""), encoding="utf-8")
            missing_baseline = subprocess.run(
                [sys.executable, str(CHANGE_VALIDATOR_PATH), str(output), "--gate", "approved"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(missing_baseline.returncode, 0)
            self.assertIn("missing_baseline", missing_baseline.stdout)

    def test_approved_change_requires_matching_decision_conclusion(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "change"
            output.mkdir()
            document = textwrap.dedent(
                """
                # CHG-012 变更单
                CHANGE_STATUS: APPROVED
                BASELINE_ID: release-1
                ## 1. 提案
                来源 SRC-001。
                ## 2. 需求 Delta
                | 类型 | 需求ID | 变更前 | 变更后/新要求 | 原因/来源 | 受影响 AC/Test | Owner |
                |---|---|---|---|---|---|---|
                | MODIFIED | FR-001 | A | B | SRC-001 | AC-FR-001-01 | 李四 |
                ## 3. 影响评估
                | 维度 | 影响或 N/A + 理由 | 证据/估算人 | 控制与 Owner |
                |---|---|---|---|
                | 1 | 有影响 | 甲 | 甲 |
                | 2 | 有影响 | 甲 | 甲 |
                | 3 | 有影响 | 甲 | 甲 |
                | 4 | 有影响 | 甲 | 甲 |
                | 5 | 有影响 | 甲 | 甲 |
                | 6 | 有影响 | 甲 | 甲 |
                | 7 | 有影响 | 甲 | 甲 |
                ## 4. 实施任务
                | TASK-ID | 关联需求 | 边界/保护边界 | Depends | Owner | 验证命令 | 状态 |
                |---|---|---|---|---|---|---|
                | TASK-012 | FR-001 | A；不改B | NONE | 李四 | pytest | READY |
                ## 5. 决策与生效
                | 项目 | 内容 |
                |---|---|
                | 结论 | APPROVED / REJECTED / WITHDRAWN |
                | 业务/客户授权人 | 张三 |
                | C 技术估算确认人 | 李四 |
                | QA/验收影响确认人 | 王五 |
                | 决策日期/证据 | 2026-09-21 / DEC-012 |
                """
            ).strip() + "\n"
            (output / "CHG-012.md").write_text(document, encoding="utf-8")
            result = subprocess.run([sys.executable, str(CHANGE_VALIDATOR_PATH), str(output), "--gate", "approved"], text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("approval_conclusion_mismatch", result.stdout)

    def test_compact_change_id_must_match_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "change"
            subprocess.run([sys.executable, str(CHANGE_INITIALIZER_PATH), str(output), "--change-id", "CHG-013", "--title", "测试"], check=True, capture_output=True)
            source = output / "CHG-013.md"
            source.rename(output / "CHG-099.md")
            result = subprocess.run([sys.executable, str(CHANGE_VALIDATOR_PATH), str(output)], text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("change_id_filename_mismatch", result.stdout)


class StructuralLintTests(unittest.TestCase):
    def test_bundled_template_is_a_valid_draft_without_fill_in_warnings(self):
        template = (SKILL_DIR / "assets" / "交接型PRD模板.md").read_text(encoding="utf-8")
        findings = VALIDATOR.lint(template)
        self.assertEqual(findings, [])

    def test_generated_scaffold_has_no_fill_in_warnings_but_edited_draft_does(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "handoff"
            subprocess.run(
                [sys.executable, str(INITIALIZER_PATH), str(output), "--project", "真实项目", "--mode", "HIGH_ASSURANCE"],
                check=True,
                capture_output=True,
            )
            prd = (output / "01-交接型PRD.md").read_text(encoding="utf-8")
            self.assertEqual(VALIDATOR.lint(prd), [])
            edited = prd.replace("- 目标行为：", "- 目标行为：待确认", 1)
            self.assertIn("missing_target_behavior", codes(VALIDATOR.lint(edited)))
            self.assertIn("unresolved_semantics", codes(VALIDATOR.lint(edited)))

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

    def test_chinese_status_footer_passes_same_gate_as_legacy_fields(self):
        document = with_chinese_status_footer(valid_prd())
        self.assertNotIn("PRD_STATUS:", document)
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            self.assertEqual(VALIDATOR.lint(document, "development-ready", trace), [])
            blocked = document.replace("| G1 基线可信 | PASS |", "| G1 基线可信 | FAIL |")
            self.assertIn("gate_not_passed", codes(VALIDATOR.lint(blocked, "development-ready", trace)))

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

    def test_unapproved_or_unowned_main_flow_fails_gate(self):
        document = valid_prd().replace("MAIN_FLOW_STATUS: APPROVED", "MAIN_FLOW_STATUS: NOT_EVALUATED").replace("MAIN_FLOW_OWNER: 李四", "MAIN_FLOW_OWNER: TBD")
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            result_codes = codes(VALIDATOR.lint(document, "development-ready", trace))
            self.assertTrue({"main_flow_not_approved", "missing_main_flow_owner"}.issubset(result_codes))

    def test_decision_assurance_summary_is_required(self):
        document = valid_prd().replace("DECISION_ASSURANCE: PASS", "DECISION_ASSURANCE: NOT_EVALUATED")
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            self.assertIn("decision_assurance_not_passed", codes(VALIDATOR.lint(document, "development-ready", trace)))

    def test_unverified_business_decision_blocks_gate(self):
        document = valid_prd().replace(
            "| DA-002 | CORE_BUSINESS_RULE | 主持人提交音频后获得转写 | 李四（业务 Owner） | SRC-001 / DEC-001 | 与已批准主流程、权限和数据规则一致 | 真实转写接口 PoC EVD-001 已验证 | FR-001 / AC-FR-001-01 / 采购成本已确认 | 服务超时；允许重试并记录失败 | 来源或主流程变更时复核 | VALIDATED |",
            "| DA-002 | CORE_BUSINESS_RULE | 主持人提交音频后获得转写 | 李四（业务 Owner） | SRC-001 / DEC-001 | 与已批准主流程、权限和数据规则一致 | 真实转写接口 PoC EVD-001 已验证 | FR-001 / AC-FR-001-01 / 采购成本已确认 | 服务超时；允许重试并记录失败 | 来源或主流程变更时复核 | UNVERIFIED |",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            self.assertIn("invalid_business_decision", codes(VALIDATOR.lint(document, "development-ready", trace)))

    def test_validated_decision_requires_complete_evidence(self):
        document = valid_prd().replace("| SRC-001 / DEC-001 | 与已批准主流程", "|  | 与已批准主流程")
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            self.assertIn("incomplete_decision_assurance", codes(VALIDATOR.lint(document, "development-ready", trace)))

    def test_core_rule_cannot_be_not_applicable(self):
        document = valid_prd().replace(
            "| DA-002 | CORE_BUSINESS_RULE | 主持人提交音频后获得转写 | 李四（业务 Owner） | SRC-001 / DEC-001 | 与已批准主流程、权限和数据规则一致 | 真实转写接口 PoC EVD-001 已验证 | FR-001 / AC-FR-001-01 / 采购成本已确认 | 服务超时；允许重试并记录失败 | 来源或主流程变更时复核 | VALIDATED |",
            "| DA-002 | CORE_BUSINESS_RULE | N/A：无核心规则 | N/A：无授权人 | N/A：无来源 | N/A：无约束 | N/A：无可行性证据 | N/A：无影响 | N/A：无风险 | N/A：无复核 | NOT_APPLICABLE |",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            self.assertIn("invalid_not_applicable_decision", codes(VALIDATOR.lint(document, "development-ready", trace)))

    def test_technical_estimate_requires_range_or_confidence(self):
        document = valid_prd().replace("3–5 人日，置信度中；含接口联调假设", "5 人日")
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            self.assertIn("weak_tech_estimate", codes(VALIDATOR.lint(document, "development-ready", trace)))

    def test_customer_commitment_requires_formal_evidence(self):
        document = valid_prd().replace(
            "| DA-001 | CUSTOMER_COMMITMENT | N/A：内部项目无客户承诺 | N/A：由内部 Sponsor 管理 | N/A：无合同或客户承诺 | N/A：无外部承诺约束 | N/A：不适用客户交付估算 | N/A：不影响外部验收 | N/A：无客户承诺风险 | N/A：若转为外部项目则复核 | NOT_APPLICABLE |",
            "| DA-001 | CUSTOMER_COMMITMENT | 9 月交付 | 客户代表甲 | 会议口述 | 与范围一致 | 已评估可行 | FR-001 / AC-FR-001-01 | 剩余延迟风险；每周复核 | 2026-09-30 复核 | VALIDATED |",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            self.assertIn("weak_customer_commitment_evidence", codes(VALIDATOR.lint(document, "development-ready", trace)))

    def test_risk_acceptance_requires_residual_risk_controls_and_trigger(self):
        document = valid_prd().replace(
            "| DA-004 | RISK_ACCEPTANCE | N/A：当前无请求接受的剩余风险 | N/A：没有风险接受事项 | N/A：风险均有控制且未申请例外 | N/A：没有豁免安全或合规约束 | N/A：不影响当前估算 | N/A：没有例外影响验收 | N/A：不存在待接受的剩余风险 | N/A：出现例外申请时复核 | NOT_APPLICABLE |",
            "| DA-004 | RISK_ACCEPTANCE | 接受延迟风险 | 业务 Owner | DEC-004 | 不违反强制约束 | 可延迟上线 | FR-001 / AC-FR-001-01 | 已知风险 | 后续再看 | VALIDATED |",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            self.assertIn("weak_risk_acceptance", codes(VALIDATOR.lint(document, "development-ready", trace)))

    def test_not_applicable_requires_reason(self):
        document = valid_prd().replace("N/A：内部项目无客户承诺", "N/A").replace("N/A：由内部 Sponsor 管理", "N/A").replace("N/A：无合同或客户承诺", "N/A").replace("N/A：无外部承诺约束", "N/A").replace("N/A：不适用客户交付估算", "N/A").replace("N/A：不影响外部验收", "N/A").replace("N/A：无客户承诺风险", "N/A").replace("N/A：若转为外部项目则复核", "N/A")
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            self.assertIn("missing_not_applicable_reason", codes(VALIDATOR.lint(document, "development-ready", trace)))

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

    def test_fake_ac_reference_fails_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            trace = Path(temp_dir) / "trace.csv"
            write_trace(trace)
            text = trace.read_text(encoding="utf-8").replace("AC-FR-001-01", "AC-FR-001-99")
            trace.write_text(text, encoding="utf-8")
            result_codes = codes(VALIDATOR.lint(valid_prd(), "development-ready", trace))
            self.assertTrue({"broken_ac_reference", "incomplete_traceability"}.issubset(result_codes))

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


class CrossArtifactPackageTests(unittest.TestCase):
    def test_complete_cross_artifact_package_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "package"
            write_valid_package(package)
            result = subprocess.run(
                [sys.executable, str(PACKAGE_VALIDATOR_PATH), str(package)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_mixed_handoff_layout_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "package"
            write_valid_package(package)
            (package / "03-目标PRD.md").write_text(valid_prd(), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(PACKAGE_VALIDATOR_PATH), str(package)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ambiguous_layout", result.stdout)

    def test_high_risk_package_requires_expert_panel(self):
        for old, new in (("RISK_LEVEL: L1", "RISK_LEVEL: L2"), ("DELIVERY_MODE: STANDARD", "DELIVERY_MODE: HIGH_ASSURANCE")):
            with self.subTest(new=new), tempfile.TemporaryDirectory() as temp_dir:
                package = Path(temp_dir) / "package"
                write_valid_package(package)
                prd = package / "01-交接型PRD.md"
                prd.write_text(prd.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(PACKAGE_VALIDATOR_PATH), str(package)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("missing_expert_panel", result.stdout)

    def test_chinese_footer_high_risk_package_requires_expert_panel(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "package"
            write_valid_package(package)
            prd = package / "01-交接型PRD.md"
            document = with_chinese_status_footer(prd.read_text(encoding="utf-8"))
            prd.write_text(document.replace("| 风险等级 | L1 |", "| 风险等级 | L2 |"), encoding="utf-8")
            result = subprocess.run([sys.executable, str(PACKAGE_VALIDATOR_PATH), str(package)], text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing_expert_panel", result.stdout)

    def test_expert_panel_cannot_pass_with_only_a_conclusion(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "package"
            write_valid_package(package)
            prd = package / "01-交接型PRD.md"
            prd.write_text(prd.read_text(encoding="utf-8").replace("RISK_LEVEL: L1", "RISK_LEVEL: L2"), encoding="utf-8")
            (package / "04-专家团评审记录.md").write_text("# 评审\n- 结论：PASS\n", encoding="utf-8")
            result = subprocess.run([sys.executable, str(PACKAGE_VALIDATOR_PATH), str(package)], text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("panel_missing_contract_field", result.stdout)
            self.assertIn("panel_core_expert_incomplete", result.stdout)

    def test_complete_high_risk_expert_panel_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "package"
            write_valid_package(package)
            prd = package / "01-交接型PRD.md"
            prd.write_text(prd.read_text(encoding="utf-8").replace("RISK_LEVEL: L1", "RISK_LEVEL: L2"), encoding="utf-8")
            panel = textwrap.dedent(
                """
                # 专家团评审记录
                | 项目 | 内容 |
                |---|---|
                | 评审 ID / 日期 | REV-001 / 2026-09-21 |
                | 共同证据包版本 | baseline-001 |
                | MVP Commit / Build / 环境 | abc123 / build-1 / staging |
                | 评审范围 / 明确排除 | FR-001 / 不含后续候选 |
                | 业务裁决人 | 张三 |
                | 技术裁决人 | 王五 |

                | Expert ID | 视角 | 专长 | 独立/项目内 | 利益冲突 | 无法覆盖领域 | Round 1 | Round 2 |
                |---|---|---|---|---|---|---|---|
                | EXP-01 | 产品/业务 | 业务 | 项目内 | 无 | 无 | 完成 | 无需 |
                | EXP-02 | C 技术 | 架构 | 项目内 | 无 | 无 | 完成 | 无需 |
                | EXP-03 | QA/验收 | 测试 | 项目内 | 无 | 无 | 完成 | 无需 |

                - 未关闭 P0：NONE
                - 已接受 P1 风险及 Owner/期限：NONE
                - 缺席核心视角：NONE
                - 未裁决分歧：NONE
                - 结论：PASS
                """
            ).strip() + "\n"
            (package / "04-专家团评审记录.md").write_text(panel, encoding="utf-8")
            result = subprocess.run([sys.executable, str(PACKAGE_VALIDATOR_PATH), str(package)], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_documented_conditional_enums_are_accepted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "package"
            write_valid_package(package)
            write_trace(package / "02-需求追踪与验收矩阵.csv", evidence="report://TEST-001")
            handoff = package / "03-研发实施与发布清单.md"
            text = handoff.read_text(encoding="utf-8")
            for old, new in {
                "G4_ACCEPTANCE_READY: NOT_EVALUATED": "G4_ACCEPTANCE_READY: PASS",
                "G5_HANDOFF_ACCEPTED: NOT_EVALUATED": "G5_HANDOFF_ACCEPTED: PASS",
                "BUILD_ID: TBD": "BUILD_ID: build-123",
                "TEST_ENV_ID: TBD": "TEST_ENV_ID: staging-1",
                "BLOCKING_DEFECT_IDS: TBD": "BLOCKING_DEFECT_IDS: NONE",
                "UAT_OWNER: TBD": "UAT_OWNER: 赵六",
                "UAT_STATUS: NOT_EVALUATED": "UAT_STATUS: ACCEPTED",
                "OAT_STATUS: NOT_EVALUATED": "OAT_STATUS: PASS",
                "RELEASE_STATUS: NOT_EVALUATED": "RELEASE_STATUS: CONDITIONAL GO",
                "HANDOFF_BLOCKING_IDS: TBD": "HANDOFF_BLOCKING_IDS: NONE",
            }.items():
                text = text.replace(old, new)
            text += "| Acceptance Ready | READY WITH ACCEPTED RISKS | RISK-1 | 张三 | 王五 | 赵六 | 2026-09-21 |\n"
            text += "| Handoff Accepted | PASS WITH ACCEPTED RISKS | RISK-1 | 张三 | 王五 | 赵六 | 2026-09-22 |\n"
            handoff.write_text(text, encoding="utf-8")
            result = subprocess.run([sys.executable, str(PACKAGE_VALIDATOR_PATH), str(package), "--gate", "handoff-accepted"], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_role_signoff_blocks_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "package"
            write_valid_package(package)
            handoff = package / "03-研发实施与发布清单.md"
            handoff.write_text(handoff.read_text(encoding="utf-8").replace("| 赵六 | 2026", "|  | 2026"), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(PACKAGE_VALIDATOR_PATH), str(package)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing_gate_signoff", result.stdout)

    def test_open_blocker_table_blocks_even_if_header_ids_say_none(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "package"
            write_valid_package(package)
            prd = package / "01-交接型PRD.md"
            prd.write_text(
                prd.read_text(encoding="utf-8")
                + "\n| ID | 问题/冲突 | 影响需求 | 选项 | 决策/待确认 | 决策人 | 截止日 | 是否阻塞 | 依据 |\n"
                + "|---|---|---|---|---|---|---|---|---|\n"
                + "| DEC-009 | 核心规则 | FR-001 | A/B | 待确认 | 张三 | 2026-09-30 | Y | SRC-001 |\n",
                encoding="utf-8",
            )
            result = subprocess.run([sys.executable, str(PACKAGE_VALIDATOR_PATH), str(package)], text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("open_blocker", result.stdout)

    def test_acceptance_and_handoff_gates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "package"
            write_valid_package(package)
            write_trace(package / "02-需求追踪与验收矩阵.csv", evidence="report://TEST-001")
            handoff = package / "03-研发实施与发布清单.md"
            text = handoff.read_text(encoding="utf-8")
            replacements = {
                "G4_ACCEPTANCE_READY: NOT_EVALUATED": "G4_ACCEPTANCE_READY: PASS",
                "G5_HANDOFF_ACCEPTED: NOT_EVALUATED": "G5_HANDOFF_ACCEPTED: PASS",
                "BUILD_ID: TBD": "BUILD_ID: build-123",
                "TEST_ENV_ID: TBD": "TEST_ENV_ID: staging-1",
                "BLOCKING_DEFECT_IDS: TBD": "BLOCKING_DEFECT_IDS: NONE",
                "UAT_OWNER: TBD": "UAT_OWNER: 赵六",
                "UAT_STATUS: NOT_EVALUATED": "UAT_STATUS: ACCEPTED",
                "OAT_STATUS: NOT_EVALUATED": "OAT_STATUS: PASS",
                "RELEASE_STATUS: NOT_EVALUATED": "RELEASE_STATUS: GO",
                "HANDOFF_BLOCKING_IDS: TBD": "HANDOFF_BLOCKING_IDS: NONE",
            }
            for old, new in replacements.items():
                text = text.replace(old, new)
            text += "| Acceptance Ready | PASS | NONE | 张三 | 王五 | 赵六 | 2026-09-21 |\n"
            text += "| Handoff Accepted | PASS | NONE | 张三 | 王五 | 赵六 | 2026-09-22 |\n"
            handoff.write_text(text, encoding="utf-8")
            for gate in ("acceptance-ready", "handoff-accepted"):
                result = subprocess.run([sys.executable, str(PACKAGE_VALIDATOR_PATH), str(package), "--gate", gate], text=True, capture_output=True, check=False)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_legacy_expanded_package_still_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "package"
            write_valid_expanded_package(package)
            result = subprocess.run(
                [sys.executable, str(PACKAGE_VALIDATOR_PATH), str(package)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
