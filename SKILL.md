---
name: mvp-handoff-prd
description: Audit an existing MVP and turn customer or internal project needs into a source-traceable PRD handoff package that engineering can implement and QA can verify. Use when a prototype, demo, partial repository, or scaffold already exists and must be completed; do not use for idea-stage PRDs with no MVP or for code-only implementation requests.
---

# MVP 交接型 PRD

把 MVP 当作“现状证据”，而不是需求真相。目标是形成一份 C 技术岗位可估算、可开发，测试可验收，需求方可签收的交接包；不得把当前实现、个人推测或行业惯例伪装成已确认需求。

## 开始前

1. 识别来源类型：`外部客户需求` 或 `内部项目需求`。两者同时存在时分别记录来源与最终决策权。
2. 收集资料：需求原文、会议记录、合同/立项材料、MVP 入口与代码、设计稿、接口/数据说明、测试账号、部署方式、已知缺陷。
3. 先建立证据台账。每条信息只允许处于：`已确认`、`MVP观察`、`合理推断`、`待确认`、`冲突`。推断不能进入承诺口径。
4. 若资料含客户数据、密钥、个人信息或未公开商业信息，先脱敏；不要在输出中复述凭据。

需要完整过程或来源差异时，读取 [references/workflow.md](references/workflow.md)。

## 执行流程

### 1. 盘点资料与问题

- 建立来源清单、术语表、角色表、约束表、冲突表和待确认项。
- 对外部需求补充：合同/承诺边界、客户环境、客户验收人、合规与 SLA、变更确认机制。
- 对内部需求补充：战略/OKR 关联、业务 Owner、运营流程、系统依赖、上线后的长期维护归属。
- 发现冲突时并列原文、来源、日期和影响，请决策人裁决；不要自行取舍。

### 2. 逆向审计 MVP

在权限允许的范围内实际检查可运行产品、代码仓库、配置、接口、数据结构、测试和部署。至少输出：

- 当前主流程、页面/模块、角色权限、状态机、接口、数据、第三方依赖；
- 每项状态：`已实现`、`部分实现`、`占位/Mock`、`未实现`、`无法验证`；
- 可复现证据：文件/行号、页面、接口、截图、日志、测试或提交版本；
- 缺陷、技术债、安全/隐私风险、可观测性和部署缺口；
- “演示可用”与“生产可用”的差距。

不要仅根据 UI 存在、接口返回 200、README 描述或一次成功演示判定功能已完成。无法运行或无法访问时，继续做静态审计并把置信度和阻塞项写清楚。

使用 [assets/MVP审计模板.md](assets/MVP审计模板.md)；复杂项目再读取 [references/audit-playbook.md](references/audit-playbook.md)。

### 3. 定义目标与差距

- 写清用户/客户问题、业务目标、成功指标及测量口径。
- 明确 `本期做 / 本期不做 / 后续候选`，并用 `Must / Should / Could / Won't` 标优先级。
- 建立差距表：`当前证据 → 目标状态 → 需新增/修改/保留/移除 → 验证方式`。
- MVP 已实现内容也要重新确认：`保留`、`修改`、`废弃` 或 `待确认`。
- 目标值不能直接照抄 MVP 当前表现；缺乏依据的数字标为待确认。

### 4. 编写可实现规格

使用稳定 ID：`OBJ` 目标、`FR` 功能、`BR` 业务规则、`NFR` 非功能、`API` 接口、`DATA` 数据、`SEC` 安全、`OBS` 可观测性、`OPS` 发布运维、`AC` 验收。

每条需求至少包含：来源/理由、MVP 现状、目标行为、优先级、前置与依赖、异常/边界、验收标准、状态。要求应原子、明确、必要、可行、可验证；避免“体验良好”“尽量快”“支持常见情况”等措辞。

验收标准优先使用 Given/When/Then 或等价的前置条件—动作—结果结构，并覆盖：正常、空值、边界、异常、权限、并发/重复、超时/重试、降级/恢复。每个 Must 需求必须至少映射一条验收标准。

按需补充 API 契约、数据字典/迁移、权限矩阵、状态机、埋点、性能与容量、可用性、兼容性、可访问性、安全、监控告警、灰度与回滚。详细写法见 [references/writing-standard.md](references/writing-standard.md)。

### 5. 预审与决策

先只列问题和风险，不替需求方做业务决定。待确认项必须有：`ID、问题、影响、建议选项（如有）、决策人、截止日、是否阻塞`。

以下情况不得宣称 PRD 已可开发：核心流程或核心规则未决；Must 项没有验收标准；权限/数据/接口边界不清；重大安全、合规或迁移风险无人承接；MVP 基线无法验证且会改变估算。

### 6. 形成交接包并过门

默认生成八类工件；小项目可以合并文件，但不能丢失这些信息：

1. `00-资料与证据台账.md`
2. `01-MVP现状审计.md`
3. `02-现状目标差距与技术债.md`
4. `03-目标PRD.md`
5. `04-需求追踪与测试矩阵.csv`
6. `05-待确认决策与变更日志.md`
7. `06-UAT与OAT验收.md`
8. `07-研发交接与发布清单.md`

可先运行 `python3 <技能目录>/scripts/init_handoff_package.py <输出目录> --project <项目名>` 生成八件套；`<技能目录>` 为本 `SKILL.md` 所在目录。PRD 使用 [assets/交接型PRD模板.md](assets/交接型PRD模板.md)，追踪矩阵使用 [assets/需求追踪矩阵.csv](assets/需求追踪矩阵.csv)，交接门禁使用 [assets/交接检查清单.md](assets/交接检查清单.md)。若只要求单文档，可合并章节，但保留证据、差距、追踪和待决策信息。

依次检查 `基线可信 → 范围已定 → 可进入开发 → 可进入验收 → 交接完成`。门禁定义见 [references/review-gates.md](references/review-gates.md)。研发估算与技术方案应由实际实施者确认，不代替 C 岗位承诺工期。

## 输出规则

- 先给结论、阻塞项和建议下一步，再给正文。
- 事实附来源；代码证据尽量给文件和行号；观察附版本/时间/环境。
- 不删除待确认项来制造“完整”；所有未决项进入统一日志。
- 文档中的日期用绝对日期，版本可追溯，变更必须记录影响的需求 ID。
- 草稿运行 `python3 <技能目录>/scripts/validate_prd.py <PRD.md>`；只有要声明可开发时，才运行 `python3 <技能目录>/scripts/validate_prd.py <PRD.md> --gate development-ready --traceability <追踪矩阵.csv>`。门禁模式下警告也会导致失败。错误必须修复或登记为阻塞，且任何未关闭阻塞都禁止标记 Development Ready。

权威参考和采用理由见 [references/knowledge-base.md](references/knowledge-base.md)。

用户要求参考案例时，读取 [references/casebook.md](references/casebook.md)。案例用于说明方法，不得把案例中的指标、范围或决策复制到新项目。
