# MVP 交接型 PRD Skill

`mvp-handoff-prd` 是一个面向 Codex 的 Brownfield 需求交接 Skill：审计已有 MVP、原型、Demo 或未完成代码，再生成 C 技术岗可估算、可实施，QA 可验证，需求方可签收的 PRD 交接包。

> 核心原则：MVP 是“现状证据”，不是“需求真相”。已实现的行为、个人推测和行业惯例都不能自动升格为已批准需求。

## 核心能力

- 区分外部客户需求、内部项目需求及其最终决策权。
- 将资料分为已确认、MVP 观察、合理推断、待确认和冲突，保留来源与证据。
- 逆向审计页面、流程、权限、API、数据、测试、部署与技术债。
- 建立 `来源 → 目标 → GAP → 需求 → AC → Test → Task → 验收证据` 追踪链。
- 校验客户承诺、核心业务规则、技术估算和风险接受是否授权合法、有据、一致且可执行。
- 通过 Development Ready、Acceptance Ready 和 Handoff Accepted 门禁阻止“表面完整”的 PRD 进入开发或发布。
- 为 L2/L3 或 HIGH_ASSURANCE 项目增加产品、技术、QA 独立首轮评审，但不用多数票代替授权人裁决。

## 适用边界

适用于：

- 已有可运行或可静态审计的 MVP、Demo、脚手架或部分仓库。
- 提出人已做了原型或项目框架，现需交给 C 技术岗补全为生产版。
- 需要把原始需求、当前实现、目标规格、实施任务和验收证据连成可审计链路。

不适用于：

- 完全没有 MVP 的创意阶段 PRD。
- 只需修复明确代码缺陷、不涉及需求交接的任务。
- 用 AI 替客户、业务 Owner、技术负责人或风险 Owner 作出授权决策。

## 快速开始

### 1. 安装

```bash
git clone https://github.com/chensishen/mvp-handoff-prd.git ~/.codex/skills/mvp-handoff-prd
```

如果目标目录已存在，请先确认其中是否有未保存的修改。

### 2. 在 Codex 中调用

```text
$mvp-handoff-prd 审计这个 MVP，并生成可交给技术岗继续完成的 PRD 交接包。
```

建议同时提供：

- 需求原文、会议记录、合同/SOW 或立项材料。
- MVP 入口、代码仓库、Commit/Build、设计稿和测试账号。
- API、数据、部署方式、第三方依赖与已知缺陷。
- 业务决策人、客户授权人、C 技术负责人和验收人。

### 3. 直接初始化交接包

```bash
python3 scripts/init_handoff_package.py ./handoff \
  --project "项目名" \
  --mode STANDARD
```

内置脚本需要 Python 3.9 或更高版本，运行时无第三方依赖。

## 默认交付物

默认只生成三个长期维护对象，避免同一需求、风险和验收状态在多个文件里重复维护：

| 文件 | 用途 |
|---|---|
| `01-交接型PRD.md` | 来源证据、MVP 现状、目标范围、流程规则、需求/NFR、决策与发布要求 |
| `02-需求追踪与验收矩阵.csv` | 来源、需求、AC、Test、Task 和验收证据的双向追踪 |
| `03-研发实施与发布清单.md` | 代码上下文、实施切片、验证命令、UAT/OAT、上线检查和三方签署 |

只有在独立归档、权限隔离或分别签署时，才使用 `--expanded` 生成兼容的八文件布局。两种布局不能混放在同一目录。

PRD 的状态与 G1–G3 门禁摘要采用文末中文字段表，不占用文档开头；旧版英文键值字段仍可由校验器读取。

## 交付模式

| 模式 | 适用场景 | 额外要求 |
|---|---|---|
| `QUICK` | 低风险小改动 | 可裁剪细节，不取消证据、范围、AC 和 Owner |
| `STANDARD` | 一般生产项目 | 默认模式，要求产品、技术、QA 三视角复核 |
| `HIGH_ASSURANCE` | 合同、敏感数据、资金、医疗、强监管或高恢复风险 | 默认 L2，自动增加专家团评审记录 |

显式指定 `--risk-level L2` 或 `L3` 也会生成专家团记录。其他情况需要专家团时使用 `--expert-panel`。

## 校验与门禁

校验 PRD 草稿：

```bash
python3 scripts/validate_prd.py ./handoff/01-交接型PRD.md
```

原样初始化的空白 PRD 不会产生“待填写”预警；编辑后，未填的 Owner、来源、目标行为等仍会提示。开发门禁始终检查全部缺项，不因模板身份放行。

候选 Development Ready 结构预检：

```bash
python3 scripts/validate_prd.py ./handoff/01-交接型PRD.md \
  --gate development-ready \
  --traceability ./handoff/02-需求追踪与验收矩阵.csv
```

正式门禁必须校验完整包，并由产品/业务、C 技术和 QA/验收人具名确认：

```bash
python3 scripts/validate_package.py ./handoff --gate development-ready
python3 scripts/validate_package.py ./handoff --gate acceptance-ready
python3 scripts/validate_package.py ./handoff --gate handoff-accepted
```

单文档中自行填写 `PASS` 不能替代包级交叉校验和正式签署。

## 已批准基线的变更

基线批准后不重写整份 PRD，默认生成一份增量变更单：

```bash
python3 scripts/init_change_package.py ./changes/CHG-001 \
  --change-id CHG-001 \
  --title "变更标题"

python3 scripts/validate_change_package.py ./changes/CHG-001 --gate approved
```

仅当提案、需求 Delta、影响、任务和审批必须由不同角色分权维护时，才为变更包使用 `--expanded`。

## 开发校验

Skill 运行时无第三方 Python 依赖。`PyYAML` 仅用于开发期的官方 Skill 结构校验：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
.venv/bin/python /path/to/skill-creator/scripts/quick_validate.py .
```

当前自动化回归覆盖初始化、草稿 lint、三级门禁、业务决策、专家团、布局冲突与增量变更校验。详细结果见 [tests/test-report.md](tests/test-report.md)。

## 项目导航

- [SKILL.md](SKILL.md)：Skill 入口与核心执行规则。
- [references/workflow.md](references/workflow.md)：外部/内部双入口及六阶段流程。
- [references/review-gates.md](references/review-gates.md)：G1–G5 门禁与阻塞条件。
- [references/decision-assurance.md](references/decision-assurance.md)：四类关键业务决策的有效性校验。
- [references/expert-panel.md](references/expert-panel.md)：专家团独立评审与裁决机制。
- [references/change-control.md](references/change-control.md)：已批准基线的增量变更流程。
- [references/github-benchmark.md](references/github-benchmark.md)：GitHub 同类项目的取舍记录。

## 责任边界

Skill 可以揭示冲突、越权、不可执行条件和无依据假设，但不代替人对客户承诺、核心规则、技术工期、合规豁免和风险接受作出最终授权。缺少原始证据时，正确结论是 `UNVERIFIED` 或 `NOT READY`，而不是补全一份看起来完整的 PRD。
