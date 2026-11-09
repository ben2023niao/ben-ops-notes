---
id: "doc-616c542f2d70"
title: "Agent 工作日志 · spender-tier-label"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-spender-tier-label.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-spender-tier-label.md"
sourceSha256: "b7f01dd1f5251b70f1f0cc18cb3ec8b292da5359c409564a259788dcf86377ff"
sourceSystem: "project-doc"
---

# Agent 工作日志 · spender-tier-label

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605260000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20spender-tier-label.md)

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：补齐大 R 运营标签，按累计送出打赏钻石计算

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-402, ADM-403, ADM-907
- 设计图：用户提供的 H5 原型与接口截图
- 设计图文件名：`2026.05.23迭代版.html`、`telegram-cloud-photo-size-5-6100591549361098949-y.jpg`
- 视觉要点：旧等级不足弹幕报错已废弃；大 R 仅作为后台运营识别
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`AGENTS.md`
- AI/工具控制文件：`AGENTS.md`
- 项目 Overlay：Kickoff（小蓝看夜场）
- 其他：前序等级特权下线日志 `docs/agents/logs/2026-05-26-disable-level-privileges.md`

## 本次目标

1. 将大 R 从“等级”口径改为按累计送出打赏钻石计算的后台运营标签。
2. 后台用户列表和详情返回并展示 `spender_tier`、`total_tip_diamond`。
3. 更新 OpenAPI、contracts、PRD 和 Agent 规则，防止后续按旧原型恢复等级特权。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/user.go` | 后台用户列表/详情聚合 `live_tips` 的累计送出钻石并计算 `spender_tier` |
| `services/go-app/internal/service/admin/spender_tier_test.go` | 新增阈值单元测试 |
| `services/go-app/internal/dto/admin_modules.go` | `AdminUserItem` 新增 `spender_tier`、`total_tip_diamond` |
| `apps/admin/src/api/index.ts` | 后台 API client 类型新增运营标签字段 |
| `apps/admin/src/views/users/UserListView.vue` | 用户列表展示运营标签和累计打赏钻石 |
| `apps/admin/src/views/users/UserDetailView.vue` | 用户详情展示运营标签和累计打赏钻石 |
| `apps/admin/src/views/rooms/RoomDetailView.vue` | 房间实时观众表预留同口径运营标签字段 |
| `docs/api/openapi.yaml` | 后台用户列表/详情契约改为 `AdminManagedUser` 并新增字段说明 |
| `packages/contracts/openapi/v1.yaml` | 同步发布契约 |
| `docs/prd/modules/kickoff-admin.md` | ADM-402/403/907 补齐大 R 运营标签口径 |
| `docs/frontend-integration.md` | 补充前端联调口径：发弹幕不需要等级，大 R 使用 `spender_tier` |
| `AGENTS.md` | 新增规则：大 R 是送钻石运营标签，不是等级特权 |

## 核心决策

1. `spender_tier` 阈值以累计送出打赏钻石为口径：`NORMAL`、`R1`、`R2`、`R3`、`WHALE`。
2. 该字段只在后台管理面用于运营识别，不进入 C 端权限判断。
3. 不新增表，不复用历史 `level` 字段，避免把旧等级系统带回业务逻辑。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目资产 + Agent 规则 |
| 哪些内容可复用到下一个项目 | “消费识别标签不等于用户等级权益”的边界 |
| 哪些内容只属于当前项目 | `spender_tier` 阈值与后台展示字段 |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 可作为多 Agent 口径约束 |
| 是否涉及 Scale Profile：mvp / growth / scale / enterprise | mvp |
| 是否影响项目 Overlay：project.config.json / docs/project | 不影响 |
| 是否增加了自动校验或 CI 门禁 | 增加 Go 单元测试 |
| 是否降低了 Agent 偷懒空间 | 是，AGENTS 明确禁止把大 R 当等级特权 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-402, ADM-403, ADM-907 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`AdminUserItem` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 不适用，本次已更新契约 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不新增表，复用 `live_tips` 聚合 |
| 是否影响数据表 / migration / 索引 | 不影响 |
| 是否使用表设计模板 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不新增资金变动，只读聚合，不涉及账本和审计 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 结构化证据 | `docs/qa/architecture-capability-evidence.json` |
| 是否只是 CRUD | 不是，包含后台运营派生字段 |
| 涉及能力 | 统计 / 权限安全 |
| 不适用项及原因 | 不新增异步、缓存、搜索、推荐 |
| 当前 MVP 边界 | 后台实时查询聚合，后续数据量增长后可改为离线统计表 |
| 未来迁移成本 | 低，字段契约稳定，计算来源可替换 |
| 升级触发指标 | 用户量或打赏流水导致用户列表聚合查询变慢 |
| 高风险触发项 | 用户数据 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 不影响部署入口 |
| 回滚 | 回滚本次代码和契约变更即可 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 可通过后台用户列表接口错误率观察聚合查询异常 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 大 R 标签不参与 C 端权限、弹幕、押注、颜色、进场或排序 |
| 红队质疑 | 实时聚合 `live_tips` 在大数据量下可能慢，后续需统计表或缓存 |
| 合入判断 | 当前 MVP 可接受 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现后台大 R 运营标签和契约文档，提交验证证据 |
| 完成裁决 | 待 Reviewer / Owner / QA / CI / Release Manager 裁决 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `cd services/go-app && go test ./internal/service/admin -run TestSpenderTier -count=1` | 通过 |
| `cd services/go-app && go test ./...` | 通过 |
| `npm run build --workspace apps/admin` | 通过；仅有 Vite chunk size 提示 |
| `npm run check:openapi && npm run check:contract` | 通过 |
