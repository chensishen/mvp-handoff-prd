# 知识库与采用原则

> 最近复核：2026-09-20。标准版本变化时重新核对采用规则，不以本页摘要替代权威原文。

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

## 专家团与独立评审

- [RAND: Delphi 方法的应用说明](https://www.rand.org/content/dam/rand/pubs/conf_proceedings/2005/CF170.pdf)：匿名独立作答、迭代和受控反馈可降低权威主导、从众和公开立场固化。本技能采用其“独立首轮 + 受控反馈”思想，但对定性 PRD 评审不强求统计聚合或多轮收敛。
- [NASA Systems Engineering Handbook](https://science.nasa.gov/wp-content/uploads/2023/04/nasa_systems_engineering_handbook_0.pdf)：独立技术评审需有明确职权范围与成功标准。本技能据此要求先定义评审契约、入口材料和门禁结论。
- [NASA Software Peer Reviews and Inspections](https://swehb.nasa.gov/pages/viewpage.action?navigatingVersions=true&pageId=98369550)：同行评审需要适合产品的技术背景、入口条件和成功条件。本技能据此要求专家角色与明确问题匹配，而非按人数凑团。
- [GOV.UK: What each role does in a service team](https://www.gov.uk/service-manual/the-team/what-each-role-does-in-service-team)：数字服务需要跨产品、开发、架构、运维、测试等角色协作，并按规模补充专项能力。本技能采用核心三视角、按风险增补专家的方式。

## 本项目原始资料

- `AI写PRD指南.md`：采用“归集 → 主流程拆解 → 漏洞排查 → 定稿”、不脑补、待确认标记、人工复核、敏感信息脱敏。本技能将其升级为 CP-A–D 可审计检查点，并强制主流程具名 Owner；不采用“没有 MVP 取证就直接进入通用四步法”。
- `PRD怎么写.md`：采用基础信息、需求概述、流程规则、详细功能、非功能、验收、依赖风险的通用骨架。
- 本技能的主要增强：MVP 逆向审计、证据分级、当前—目标差距、外部/内部双入口、需求追踪、UAT/OAT、交接/发布门禁与变更控制。

## GitHub 开源方法参考

- [GitHub Spec Kit](https://github.com/github/spec-kit)：采用规格—计划—任务—实现—收敛的阶段工件思路与现有项目入口；不用其功能规格取代客户授权和 MVP 审计。
- [OpenSpec](https://github.com/Fission-AI/OpenSpec)：采用 proposal/spec/design/tasks 的增量变更与 Brownfield 思路；增加商务、验收、签署和生效控制。
- [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)：采用按复杂度选择规划深度的思路，形成 QUICK / STANDARD / HIGH_ASSURANCE；不默认启动所有角色。
- [PRP](https://github.com/Wirasm/prp) 与 [Agent OS](https://github.com/buildermethods/agent-os)：采用代码库上下文、精确路径、现有模式和可执行验证命令；不把当前代码习惯当成业务需求。
- [cc-sdd](https://github.com/gotalab/cc-sdd)：采用边界/依赖标注、非原作者独立复核与失败诊断。
- [Doorstop](https://github.com/doorstop-dev/doorstop)：采用稳定 ID、断链/孤立项校验和版本化追踪；不强制所有小项目采用完整建模工具。

详细对比与不采用理由见 [github-benchmark.md](github-benchmark.md)。
