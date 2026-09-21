# GitHub 同类项目对比与采用决策

> 调研快照：2026-09-20。Star 只用于表示社区关注度，不作为方法正确性证据。采用时仍以本技能的业务场景、证据质量和交付风险为准。

| 项目 | 可参考部分 | 本技能采用 | 不直接采用 |
|---|---|---|---|
| [GitHub Spec Kit](https://github.com/github/spec-kit) | 规格、计划、任务、实现、收敛；现有项目入口 | 阶段工件、澄清/一致性检查、收敛门禁 | 不用单一功能规格取代客户授权和 MVP 证据审计 |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | Brownfield 友好的 proposal/spec/design/tasks 变更目录 | 增量变更包、Delta 需求、生效与归档 | 不以灵活工作流取消合同/安全/验收门禁 |
| [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | 按工作复杂度选择规划深度，支持现有代码库和专业视角 | QUICK / STANDARD / HIGH_ASSURANCE 风险适配 | 不默认启动全部角色，避免重复内容与责任稀释 |
| [PRP](https://github.com/Wirasm/prp) | PRD + 代码库上下文 + 执行手册；精确路径与验证命令 | 在研发交接中增加代码导航、现有模式、切片与验证契约 | 不把实施手册当成客户/业务验收契约 |
| [Agent OS](https://github.com/buildermethods/agent-os) | 从代码库提取并按任务注入规范 | 已存在实现模式必须有代码证据 | 不把现有代码习惯自动提升为业务需求 |
| [cc-sdd](https://github.com/gotalab/cc-sdd) | 边界优先、任务依赖、独立审查、TDD 和失败诊断 | 实施切片的边界/依赖、非原作者复现与独立复核 | 不让开发阶段工作流倒推或覆盖需求来源 |
| [Doorstop](https://github.com/doorstop-dev/doorstop) | Git 内的独立需求项、链接、追踪校验与发布 | 稳定 ID、双向追踪、孤立/断链检查 | 不强制小项目采用完整建模工具 |
| [AI Dev Tasks](https://github.com/snarktank/ai-dev-tasks) | PRD → 任务 → 逐项实现的简单心智模型 | 保留简明的任务切片与逐项验证 | 不采用仅靠 3–5 个澄清问题就生成生产 PRD 的深度 |
| [MetaGPT](https://github.com/FoundationAgents/MetaGPT) / [ChatDev](https://github.com/OpenBMB/ChatDev) / [CrewAI](https://github.com/crewAIInc/crewAI) | 角色化 SOP、通用多代理编排、人工介入 | 专家团的视角分离与可配置编排 | 不用代理共识或多数票代替客户、业务、技术和风险授权 |

## 系统定位

本技能不是通用“一句话生成软件公司”框架。它的不可替代部分是：已有 MVP 的可复现取证、需求来源与决策权分离、演示到生产的差距、可签署的验收契约与跨工件追踪。外部项目的优势是承诺边界，内部项目的优势是 Sponsor 与长期运营归属，两者都不应被代码生成流程稀释。
