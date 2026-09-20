# MVP 交接型 PRD Skill

`mvp-handoff-prd` 是一个面向 Codex 的产品交接 skill。它会审计已有 MVP、原型、Demo 或部分代码，并将外部客户或内部项目需求整理成可追溯、可开发、可测试和可验收的 PRD 交接包。

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

1. `00-资料与证据台账.md`
2. `01-MVP现状审计.md`
3. `02-现状目标差距与技术债.md`
4. `03-目标PRD.md`
5. `04-需求追踪与测试矩阵.csv`
6. `05-待确认决策与变更日志.md`
7. `06-UAT与OAT验收.md`
8. `07-研发交接与发布清单.md`

可以使用内置脚本初始化交接包：

```bash
python3 scripts/init_handoff_package.py <output-directory> --project <project-name>
```

## 质量校验

运行 skill 自带测试：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

校验 PRD 草稿：

```bash
python3 scripts/validate_prd.py <PRD.md>
```

仅当需要声明 PRD 可进入开发时，运行开发就绪门禁：

```bash
python3 scripts/validate_prd.py <PRD.md> \
  --gate development-ready \
  --traceability <traceability-matrix.csv>
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
