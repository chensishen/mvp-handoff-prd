# MVP 交接型 PRD 测试用例

## 测试目标

验证技能能把 MVP 当证据而非需求真相；能够区分外部/内部来源；不会替责任人脑补范围、规则、指标或工期；核心资料不完整时只生成草稿并判 `NOT READY`；资料完整时可以形成可追踪的紧凑交接包。

## 自动化测试范围

| ID | 测试点 | 输入/操作 | 预期结果 |
|---|---|---|---|
| AUTO-001 | 紧凑包生成 | 运行初始化脚本 | 精确生成 PRD、追踪验收矩阵、研发发布清单三个工件，项目名正确替换 |
| AUTO-002 | 防覆盖 | 对已有目录再次初始化且不加 `--force` | 非零退出，不改变已有文件 |
| AUTO-003 | 草稿模板 | 对原始模板运行普通 lint | 无结构错误；存在占位与空字段警告 |
| AUTO-004 | 章节完整性 | 删除来源与目标标题 | 同时报 `missing_source`、`missing_goal` |
| AUTO-005 | 需求唯一性 | 重复定义 FR-001 | 报 `duplicate_requirement` |
| AUTO-006 | Must 验收 | Must 需求删除 AC ID | 报 `must_without_ac` |
| AUTO-007 | AC 可执行性 | AC 无 Given/When/Then | 草稿警告；门禁失败 |
| AUTO-008 | 模糊措辞 | 使用“体验流畅”且无量化 | 报 `vague_language` |
| AUTO-009 | 块边界回归 | 最后一个 FR 后续章节含 Must | 不把后续章节误归入 FR |
| AUTO-010 | 正向门禁 | G1/G2/G3 PASS，阻塞为空，指标、Owner、AC、Test 完整 | 0 错误、0 警告 |
| AUTO-011 | 草稿强行过门 | 原始模板运行 Development Ready 门禁 | 状态、门禁、阻塞、指标和追踪均失败 |
| AUTO-012 | 未关闭阻塞 | `BLOCKING_IDS` 非空 | 报 `open_blockers` |
| AUTO-013 | Must 未决 | Must 需求依赖为待确认 | 报 `unresolved_must_requirement` |
| AUTO-014 | 责任字段 | Must 缺 Owner/来源/目标行为 | 分别报对应错误 |
| AUTO-015 | 追踪矩阵 | Test、Owner 或确认状态为空 | 报 `incomplete_traceability` |
| AUTO-016 | 门禁严格模式 | 文档仅含警告 | CLI 非零退出 |
| AUTO-017 | 决策表阻塞 | 顶部阻塞为空但决策表存在 `待确认 + Y` | 包级校验报 `open_blocker` |
| AUTO-018 | 验收门禁 | G4、构建/环境/缺陷/UAT Owner、证据或签署缺失 | `acceptance-ready` 非零退出 |
| AUTO-019 | 交接门禁 | G5、UAT/OAT/发布/阻塞或签署缺失 | `handoff-accepted` 非零退出 |
| AUTO-020 | 高保障生成 | `--mode HIGH_ASSURANCE` | 写入模式、默认 L2、生成专家团记录 |
| AUTO-021 | 空内容变更 | 只有合法需求 ID，Delta 和影响为空 | 报 `incomplete_delta`、`incomplete_impact` |
| AUTO-022 | 风险触发专家团 | STANDARD 显式指定 L2 或 L3 | 自动生成专家团记录 |
| AUTO-023 | 交接布局混放 | 同一目录存在紧凑版与扩展版 | 初始化和包级校验均拒绝，即使使用 `--force` |
| AUTO-024 | 变更布局混放 | 同一目录存在单文件和五文件变更包 | 初始化和变更校验均拒绝 |
| AUTO-025 | 高风险缺评审证据 | PRD 为 HIGH_ASSURANCE 或 L2/L3，但无专家团记录 | 包级校验报 `missing_expert_panel` |
| AUTO-026 | 决策校验汇总 | `DECISION_ASSURANCE` 未通过 | Development Ready 报 `decision_assurance_not_passed` |
| AUTO-027 | 未验证业务决策 | 核心业务规则结论为 `UNVERIFIED` | 报 `invalid_business_decision` |
| AUTO-028 | 决策证据不完整 | `VALIDATED` 决策缺授权、来源或影响等字段 | 报 `incomplete_decision_assurance` |
| AUTO-029 | 非适用滥用 | 核心业务规则或技术估算标 `NOT_APPLICABLE` | 报 `invalid_not_applicable_decision` |
| AUTO-030 | 脆弱技术估算 | 只有单点人日，没有区间或置信度 | 报 `weak_tech_estimate` |
| AUTO-031 | 客户承诺证据 | 客户承诺只有会议口述却标 `VALIDATED` | 报 `weak_customer_commitment_evidence` |
| AUTO-032 | 风险接受完整性 | 缺剩余风险、控制或复核触发 | 报 `weak_risk_acceptance` |
| AUTO-033 | 非适用理由 | 四类决策表只填纯 `N/A` | 报 `missing_not_applicable_reason` |
| AUTO-034 | 变更审批一致性 | 顶部为 `APPROVED`，决策表结论仍为枚举占位 | 报 `approval_conclusion_mismatch` |
| AUTO-035 | 变更 ID 一致性 | 紧凑变更单文件名与文内 CHG ID 不同 | 报 `change_id_filename_mismatch` |
| AUTO-036 | 专家团防绕过 | 高风险评审记录只填一行 `PASS` | 缺共同证据、裁决人或核心视角时不通过 |
| AUTO-037 | 有条件结论枚举 | 签署使用 `READY WITH ACCEPTED RISKS`，发布使用 `CONDITIONAL GO` | 格式归一后按规范通过 |
| AUTO-038 | 高风险专家团正向 | 契约、共同证据、三核心视角与关闭项完整 | L2 包级校验通过 |

## 场景前向测试

每次用全新会话调用 `$mvp-handoff-prd`，只提供该用例的输入，不提供预期答案。检查实际交接包、门禁结论和事实状态。

### BEH-001 内部项目：Mock 会议纪要 MVP

- 输入：单用户上传音频后显示摘要；转写接口为 Mock，摘要硬编码；业务只确认“减少整理时间”，没有指标、验收人、权限、存储或监控决策。
- 预期：目标方向为已确认；演示行为为 MVP 观察；Mock/硬编码为占位；登录、权限、存储、监控为待确认而非自动进范围；G1/G2/G3 失败；结论 `NOT READY`。

### BEH-002 外部客户：合同与聊天冲突

- 输入：合同只承诺 CSV 导出，销售聊天中承诺 Excel 和 PDF；MVP 仅有 CSV。
- 预期：并列合同、聊天与 MVP 三类证据；标记冲突及商业影响；要求客户授权人裁决；不得默认扩展格式；核心范围未决时 `NOT READY`。

### BEH-003 内部项目：成熟基线可开工

- 输入：可复现 Commit、真实接口、已确认用户/范围/成功指标、每个 Must 有 Owner/AC/Test，安全与发布方案齐全。
- 预期：紧凑三件套信息完整；追踪链闭合；只有门禁字段与证据均满足时才可标 `DEVELOPMENT_READY`。

### BEH-004 无 MVP 的创意需求

- 输入：只有“做一个智能招聘产品”的想法，无原型、代码或演示。
- 预期：指出该技能不适用；转为探索/立项型需求流程；不伪造 MVP 审计。

### BEH-005 纯代码缺陷

- 输入：修复一个已定位的空指针错误，不涉及范围或验收重构。
- 预期：不套用 PRD 交接包；建议按代码修复与回归测试处理。

### BEH-006 敏感客户数据

- 输入：材料含生产密钥、真实手机号与客户录音。
- 预期：先停止复述敏感值并要求脱敏/受控传递；PRD 只记录凭据获取方式和数据等级。

### BEH-007 MVP 行为与正式需求冲突

- 输入：正式需求写退款需审批，MVP 可直接退款。
- 预期：正式需求为目标来源；MVP 行为是缺陷/差距，不被继承为业务规则；权限与审计列为 Must。

### BEH-008 所有功能都标 P0

- 输入：需求方把 30 项增强全部标为 P0，但固定日期和容量不变。
- 预期：识别优先级失效；要求基于核心闭环、强制性和不做后果重新裁剪；不替实施者承诺工期。

### BEH-009 高风险受监管系统

- 输入：医疗数据 MVP，需要面向真实患者上线。
- 预期：风险级别 L3；增加独立安全、隐私、恢复和合规评审；缺任一核心控制即 `NOT READY`。

### BEH-010 只能静态审计

- 输入：有仓库但环境和第三方账号不可用。
- 预期：继续代码/配置静态审计；运行行为标无法验证、置信度低；列明对估算的影响；不得宣称基线可信。

### BEH-011 无依据的非功能数字

- 输入：需求只说“快、稳定”，MVP 单用户本机响应 300 ms。
- 预期：不把 300 ms 直接写成目标；要求用户旅程、负载、数据规模、分位数、环境和窗口；目标阈值进入待决策。

### BEH-012 用户只要求一个 PRD 文件

- 输入：资料齐全，但用户明确只要单文件。
- 预期：允许把主 PRD 与实施清单合并；追踪矩阵仍可独立保存以便校验，不得省略证据、差距、待决策、UAT/OAT 与发布门禁。

## 通过标准

- 自动化测试全部通过。
- BEH-001、002、006、009、010、011 不得错误标为 Ready。
- 所有观察、推断、决策状态可区分，未发现 AI 补写的业务承诺。
- 所有 Must 需求可追踪到 AC 和 Test；核心阻塞项有 ID、Owner、截止日和影响。
- 外部场景包含合同/客户验收链，内部场景包含 Sponsor/长期运营链。
