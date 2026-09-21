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
4. 确定交付模式：`QUICK` 用于低风险小改动，`STANDARD` 用于一般生产项目，`HIGH_ASSURANCE` 用于客户合同、敏感数据、资金/医疗/强监管或高恢复风险场景。模式决定文档与评审深度，不取消证据、范围、验收和责任人。
5. 若资料含客户数据、密钥、个人信息或未公开商业信息，先脱敏；不要在输出中复述凭据。

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

目标主流程由具名的产品/业务负责人提出或确认。AI 可以把已确认主流程拆成用户操作、系统响应、页面/状态变化与数据副作用，但不得悄然优化、改道或新建核心业务链路。未确认的替代方案只能进入决策日志。

在成文前执行四个写作检查点：`信息归集（只分类、不补全） → 主流程拆解（不改方案） → 漏洞排查（只提问题、不代决策） → 规格编译`。详细停止条件见 [references/staged-authoring.md](references/staged-authoring.md)。

### 4. 编写可实现规格

使用稳定 ID：`OBJ` 目标、`FR` 功能、`BR` 业务规则、`NFR` 非功能、`API` 接口、`DATA` 数据、`SEC` 安全、`OBS` 可观测性、`OPS` 发布运维、`AC` 验收。

每条需求至少包含：来源/理由、MVP 现状、目标行为、优先级、前置与依赖、异常/边界、验收标准、状态。要求应原子、明确、必要、可行、可验证；避免“体验良好”“尽量快”“支持常见情况”等措辞。

验收标准优先使用 Given/When/Then 或等价的前置条件—动作—结果结构，并覆盖：正常、空值、边界、异常、权限、并发/重复、超时/重试、降级/恢复。每个 Must 需求必须至少映射一条验收标准。

按需补充 API 契约、数据字典/迁移、权限矩阵、状态机、埋点、性能与容量、可用性、兼容性、可访问性、安全、监控告警、灰度与回滚。详细写法见 [references/writing-standard.md](references/writing-standard.md)。

同时为 C 岗位编译“实施上下文”：精确代码路径、已有模式、不得破坏的契约、启动/构建/测试命令、任务边界与依赖、每个切片的权威验证命令。不能用 README 推测、无法复现的命令或无证据的代码约定填充。

### 5. 预审与决策

先只列问题和风险，不替需求方做业务决定。待确认项必须有：`ID、问题、影响、建议选项（如有）、决策人、截止日、是否阻塞`。

对客户承诺、核心业务规则、技术估算和风险接受执行“授权 → 证据 → 一致性 → 可行性 → 影响 → 剩余风险 → 有效期”校验。AI 可以用原始材料和代码证据指出越权、冲突、不可执行条件或不合理假设，但不能把自己的判断变成授权。结论只使用 `VALIDATED / NOT_APPLICABLE / UNVERIFIED / INVALID`；任何无法证明的事实保持 `UNVERIFIED`。详细规则见 [references/decision-assurance.md](references/decision-assurance.md)。

普通项目至少完成产品、技术、QA 三视角检查；当用户要求“专家团”，或项目属于 L2/L3、跨系统、合同边界复杂、核心规则争议大时，采用独立首轮评审：各专家先只看共同证据包，分别提交带证据的发现，协调人去重并仅回传分歧，再进行一轮复核。不得以多数票决定客户承诺、业务范围、安全例外或技术工期；这些事项仍由具名责任人裁决。详细编排与停止条件见 [references/expert-panel.md](references/expert-panel.md)，记录使用 [assets/专家团评审记录模板.md](assets/专家团评审记录模板.md)。

以下情况不得宣称 PRD 已可开发：核心流程或核心规则未决；关键业务决策校验不是 PASS；Must 项没有验收标准；权限/数据/接口边界不清；重大安全、合规或迁移风险无人承接；MVP 基线无法验证且会改变估算。

### 6. 形成交接包并过门

默认只生成三个长期维护对象，信息完整但不按阶段重复拆文件：

1. `01-交接型PRD.md`：来源证据、MVP 审计、目标与范围、流程规则、功能/NFR、风险、决策和发布要求。
2. `02-需求追踪与验收矩阵.csv`：来源 → 目标 → GAP → 需求 → AC → Test → Task → 验收证据。
3. `03-研发实施与发布清单.md`：代码上下文、实施切片、UAT/OAT、上线检查和三方签署。

文件数不是质量门槛；证据、差距、规格、测试和责任链是否闭合才是。运行 `python3 <技能目录>/scripts/init_handoff_package.py <输出目录> --project <项目名> --mode STANDARD` 生成紧凑交接包；`--mode QUICK / STANDARD / HIGH_ASSURANCE` 会写入实际交付模式，`HIGH_ASSURANCE` 自动增加专家团记录并默认 L2；显式指定 L2/L3 也会生成专家团记录。只有组织要求分别归档、文件由不同 Owner 独立签署或工具权限必须隔离时，才加 `--expanded` 生成旧式八文件布局。

除 HIGH_ASSURANCE、L2/L3 外的其他触发条件需要专家团时加 `--expert-panel`，紧凑布局额外生成 `04-专家团评审记录.md`。专家团记录是评审证据，不替代正文与正式签署。紧凑版与扩展版必须使用不同目录；`--force` 只覆盖同布局同名文件，不负责删除另一布局的旧工件。

`03-研发实施与发布清单.md` 不只是勾选表，还必须包含 C 岗可复现的代码导航、环境说明、实施切片、依赖图和验证命令。使用“新鲜上下文的非原作者”至少复现一次启动和核心验证命令。

对已批准基线的后续变更，不重写整份 PRD；运行 `python3 <技能目录>/scripts/init_change_package.py <输出目录> --change-id CHG-001 --title <变更标题>` 生成一份增量变更单，按“提案 → 需求 Delta → 影响 → 任务 → 决策/生效”管理。仅在这些部分由不同角色分权维护时加 `--expanded`。详细见 [references/change-control.md](references/change-control.md)。

依次检查 `基线可信 → 范围已定 → 可进入开发 → 可进入验收 → 交接完成`。门禁定义见 [references/review-gates.md](references/review-gates.md)。研发估算与技术方案应由实际实施者确认，不代替 C 岗位承诺工期。

## 输出规则

- 先给结论、阻塞项和建议下一步，再给正文。
- 事实附来源；代码证据尽量给文件和行号；观察附版本/时间/环境。
- 不删除待确认项来制造“完整”；所有未决项进入统一日志。
- 文档中的日期用绝对日期，版本可追溯，变更必须记录影响的需求 ID。
- 草稿运行 `python3 <技能目录>/scripts/validate_prd.py <PRD.md>`。单文档的 `--gate development-ready` 只做候选结构预检，不能凭自填 PASS 宣称就绪。包级门禁依次运行 `validate_package.py <目录> --gate development-ready / acceptance-ready / handoff-accepted`；正式签署只保存在研发实施与发布清单，避免 PRD 与清单双重签署。HIGH_ASSURANCE 或 L2/L3 缺专家团记录、目录混放两种布局、任何校验错误或未关闭阻塞都禁止过门。

权威参考和采用理由见 [references/knowledge-base.md](references/knowledge-base.md)。

GitHub 同类项目的对比、采用与不采用项见 [references/github-benchmark.md](references/github-benchmark.md)。

用户要求参考案例时，读取 [references/casebook.md](references/casebook.md)。案例用于说明方法，不得把案例中的指标、范围或决策复制到新项目。
