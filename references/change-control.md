# 增量变更单

当 PRD 基线已批准后，使用增量变更单，不通过重新生成整份 PRD 覆盖既有决策。此做法借鉴 OpenSpec 的需求 Delta 思路，增加外部客户与内部项目所需的授权、成本、验收和生效控制。

## 默认载体

```text
CHG-001-<slug>/
└── CHG-001.md        # 提案、需求 Delta、影响、任务、决策与生效
```

只有这些章节由不同角色在不同权限域独立维护时，才用 `--expanded` 拆为 `proposal.md / requirements.md / impact.md / tasks.md / decision.md`。拆分不增加门禁，也不代表质量更高。

单文件与五文件布局必须放在不同目录；即使使用 `--force`，初始化器和校验器也拒绝混放，防止旧提案、旧任务或旧审批被误判为当前变更的一部分。

## 状态机

`PROPOSED → IMPACT_ASSESSED → APPROVED / REJECTED → IMPLEMENTED → VERIFIED → EFFECTIVE → ARCHIVED`

- `APPROVED` 前不得把变更当成已承诺范围。
- `IMPLEMENTED` 只表示代码完成，不代表验收通过。
- `EFFECTIVE` 前必须回填 PRD、追踪矩阵、测试、发布和决策日志，并标记生效基线。
- 被拒绝或撤回的变更保留原始提案和结论，不删除历史。

## 变更门禁

1. 来源、提出人、基线 ID 和受影响需求可定位。
2. ADDED / MODIFIED / REMOVED 分类清楚；修改项同时保留前后语义。
3. 范围、费用、工期、验收、数据/迁移、运维与回滚的影响均已评估或写明 N/A 与理由。
4. 外部变更由有权客户/商务代表批准；内部变更由 Sponsor/业务 Owner 批准；技术估算仍由 C 技术负责人确认。
5. 变更生效后，所有受影响 ID 的链接和证据已更新，不留下“文档已改、测试仍指向旧行为”。

校验器不仅检查需求 ID：Delta 必须填写前后语义、原因/来源和 Owner；影响维度必须填写实际影响或 `N/A + 理由`；批准状态还必须有完整 TASK、三方确认和带日期的决策证据。
