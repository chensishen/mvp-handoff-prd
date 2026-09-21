# MVP 交接型 PRD Skill

`mvp-handoff-prd` 是一个面向 Codex 的产品交接 skill。它会审计已有 MVP、原型、Demo 或部分代码，并将外部客户或内部项目需求整理成可追溯、可开发、可测试和可验收的 PRD 交接包。

它还会对客户承诺、核心业务规则、技术估算和风险接受进行证据化有效性校验，识别越权、冲突、不可执行条件和无依据假设；最终业务授权仍由具名责任人承担。

内置脚本需要 Python 3.9 或更高版本。

## 适用场景

- 已有原型、Demo、脚手架或未完成仓库，需要进入正式研发。
- 需要区分已确认需求、MVP 观察、合理推断、待确认项和冲突。
- 需要建立“原始需求 → MVP 现状 → 目标规格 → 测试验收”的追踪关系。
- 需要识别演示可用与生产可用之间的差距。

不适用于完全没有 MVP 的创意阶段 PRD，也不适用于只要求修改代码、无需需求交接的任务。

## 安装

将仓库克隆到 Codex skills 目录：

```bash
git clone https://github.com/chensishen/mvp-handoff-prd.git ~/.codex/skills/mvp-handoff-prd
```

如果目标位置已存在，请先确认其中是否有需要保留的改动。

## 使用

在 Codex 中显式调用：

```text
$mvp-handoff-prd 审计这个 MVP，并生成可交给研发和测试的 PRD 交接包。
```

为了提高交付质量，建议同时提供：

- 原始需求、会议记录、合同或立项材料。
- MVP 入口、代码仓库、设计稿和测试账号。
- 接口、数据、部署方式与已知缺陷。
- 业务决策人、验收人和期望时间。

## 默认交付物

默认采用三文件紧凑布局，避免在多个文档重复维护需求、风险和验收状态：

1. `01-交接型PRD.md`
2. `02-需求追踪与验收矩阵.csv`
3. `03-研发实施与发布清单.md`

可以使用内置脚本初始化交接包：

```bash
python3 scripts/init_handoff_package.py <output-directory> \
  --project <project-name> \
  --mode STANDARD
```

`--mode` 可选 `QUICK / STANDARD / HIGH_ASSURANCE`；高保障模式自动生成专家团记录并默认 `RISK_LEVEL: L2`，也可用 `--risk-level` 明确覆盖。任何显式 L2/L3 风险也会自动生成专家团记录。

只有确有独立归档、权限隔离或分别签署要求时才生成旧式八文件布局：

```bash
python3 scripts/init_handoff_package.py <output-directory> \
  --project <project-name> \
  --expanded
```

复杂、高风险或用户明确要求专家团时，增加独立两轮评审记录：

```bash
python3 scripts/init_handoff_package.py <output-directory> --project <project-name> --expert-panel
```

专家团采用产品、C 技术、QA 三个核心视角，按风险增补安全、运维、数据、合规或客户交付专家；先独立评审，再回传分歧并由具名责任人裁决。

已批准 PRD 基线之后，默认生成一份增量变更单，避免重写整份 PRD 覆盖历史：

```bash
python3 scripts/init_change_package.py <change-directory> \
  --change-id CHG-001 \
  --title <change-title>
```

仅在提案、影响、任务与审批需要分权维护时加 `--expanded` 生成五文件布局。

紧凑版与扩展版不要写入同一目录。初始化器即使使用 `--force` 也会拒绝混放，避免旧工件被误当成当前基线。

## 质量校验

先建立隔离的开发校验环境；PyYAML 只用于官方 Skill 结构校验，不是运行本 Skill 的依赖：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python <skill-creator-directory>/scripts/quick_validate.py .
```

运行 skill 自带测试：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

校验 PRD 草稿：

```bash
python3 scripts/validate_prd.py <PRD.md>
```

单文档候选结构预检：

```bash
python3 scripts/validate_prd.py <PRD.md> \
  --gate development-ready \
  --traceability <traceability-matrix.csv>
```

正式声明可进入开发时，对完整交接包做跨工件校验；该结果仍需产品/业务、C 技术和 QA 具名确认：

```bash
python3 scripts/validate_package.py <handoff-package-directory>
python3 scripts/validate_package.py <handoff-package-directory> --gate acceptance-ready
python3 scripts/validate_package.py <handoff-package-directory> --gate handoff-accepted
```

校验增量变更包：

```bash
python3 scripts/validate_change_package.py <change-directory>
python3 scripts/validate_change_package.py <change-directory> --gate approved
```

## 目录结构

```text
mvp-handoff-prd/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
├── references/
├── scripts/
└── tests/
```

`SKILL.md` 是 skill 入口；`references/` 保存按需读取的详细方法；`assets/` 保存交付模板；`scripts/` 提供确定性初始化和校验能力。

## 核心原则

MVP 是“现状证据”，不是“需求真相”。当前实现、个人推测或行业惯例都不能被伪装成已确认需求。任何未决问题应保留在统一决策日志中，而不是为了让文档看起来完整而被删除。

正式成文前执行 `CP-A 证据冻结 → CP-B 主流程确认 → CP-C 规则决策 → CP-D 规格编译`。AI 可以拆解主流程和排查漏洞，但不能代替产品/业务 Owner 定义核心链路与业务规则。
