# 知识库与采用原则

本知识库保存“来源 + 对本技能的决策影响”，不复制大段原文。使用时优先打开最新官方版本，并记录访问日期。

## 需求工程与 PRD

- [ISO/IEC/IEEE 29148:2018 Requirements Engineering](https://www.iso.org/obp/ui/#iso:std:iso-iec-ieee:29148:ed-2:v1:en)：用于要求需求在生命周期内可形成、可管理，并强调良构文本需求及其属性。本技能据此要求原子、明确、可验证和可追踪。
- [ISO/IEC 25010:2023 Product Quality Model](https://www.iso.org/standard/78176.html)：用于系统性检查适用的产品质量特性，而不是随意罗列 NFR。
- [Atlassian PRD Template](https://www.atlassian.com/software/confluence/templates/product-requirements)：提供目标、成功指标、假设、需求选项、支撑材料、开放问题和 Out of Scope 的协作结构。本技能在此基础上增加 MVP 证据基线与目标差距。
- [Atlassian Acceptance Criteria](https://www.atlassian.com/work-management/project-management/acceptance-criteria/)：强调验收条件应预先定义并映射到客观测试。本技能要求 Must 需求至少一条 AC。
- [Atlassian Definition of Ready](https://www.atlassian.com/agile/project-management/definition-of-ready)：用于开发前清晰、价值、可行、可测试及资源/时间共识检查。本技能将其落成 Development Ready 门。
- [Atlassian Definition of Done](https://www.atlassian.com/agile/project-management/definition-of-done)：区分单个需求的 AC 与整个增量的完成标准，并强调交接所需文档。本技能将发布、运维和文档纳入完成门。
- [The Scrum Guide](https://scrumguides.org/download)：产品待办是持续演化的，细化增加描述、顺序与透明度。本技能不把 PRD 当一次性静态文件。
- [Cucumber Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)：用于 Given/When/Then 的可执行规格写法。

## 技术设计、可靠性与发布

- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)：用于把 API 契约做成机器可读、可验证的附件，而不是只写自然语言表格。
- [C4 Model](https://c4model.com/diagrams)：用于最小化表达系统上下文、容器和部署关系；复杂模块再补组件图。
- [Google SRE: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)：SLI 是明确度量，SLO 是其目标范围；测量条件和统计口径必须清楚。本技能禁止无依据的“高可用/低延迟”。
- [Google SRE: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)：支持从用户可感知行为与关键系统信号设计监控，而不是只记录技术日志。
- [Google SRE: Release Engineering](https://sre.google/sre-book/release-engineering/) 与 [Launch Coordination Checklist](https://sre.google/sre-book/launch-checklist/)：强调可重复构建、测试审计轨迹、逐步发布、回滚和上线准备。
- [Martin Fowler: Feature Toggles](https://martinfowler.com/articles/feature-toggles.html)：用于在适当场景分离部署与发布，并要求管理开关生命周期；不是所有项目都必须使用开关。

## 安全、隐私与可访问性

- [OWASP Application Security Verification Standard](https://owasp.org/projects/asvs)：提供可验证的 Web 应用安全控制清单。本技能要求按项目风险选择适用控制，而不是笼统写“保证安全”。
- [NIST SP 800-218 SSDF](https://csrc.nist.gov/pubs/sp/800/218/final)：把安全实践嵌入软件开发生命周期，并提供共同语言。本技能要求安全要求、漏洞处理和供应链风险尽早进入 PRD。
- [W3C WCAG 2 Overview](https://www.w3.org/WAI/standards-guidelines/wcag/) 与 [WCAG 2.2](https://www.w3.org/TR/WCAG22/)：无障碍成功标准可测试，按 A/AA/AAA 分级。本技能要求明确适用级别和验证范围。

## 测试与验收

- [ISTQB Acceptance Testing Syllabus](https://istqb.org/wp-content/uploads/2024/11/ISTQB-CT-AcT_Syllabus_v1.0_2019.pdf)：用于验收标准、追踪、UAT、合同和监管验收的结构化设计。
- [ISTQB CTFL v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)：用于等价类、边界值、决策表、状态迁移和风险测试。

## 本项目原始资料

- `AI写PRD指南.md`：采用“归集 → 主流程拆解 → 漏洞排查 → 定稿”、不脑补、待确认标记、人工复核、敏感信息脱敏。
- `PRD怎么写.md`：采用基础信息、需求概述、流程规则、详细功能、非功能、验收、依赖风险的通用骨架。
- 本技能的主要增强：MVP 逆向审计、证据分级、当前—目标差距、外部/内部双入口、需求追踪、UAT/OAT、交接/发布门禁与变更控制。
