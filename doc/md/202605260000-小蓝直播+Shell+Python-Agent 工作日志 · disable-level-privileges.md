---
id: "doc-cecd4ee58e9a"
title: "Agent 工作日志 · disable-level-privileges"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "自动化", "CDN", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-disable-level-privileges.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-disable-level-privileges.md"
sourceSha256: "6f611d5875e1576345545e0418c5da9190da38b406bd313ca73612b52d8b12b9"
sourceSystem: "project-doc"
---

# Agent 工作日志 · disable-level-privileges

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-disable-level-privileges.md`

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：下线等级特权逻辑，修复低等级用户无法发送弹幕

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-predict.md`、`docs/prd/modules/kickoff-h5.md`、`docs/prd/modules/kickoff-member.md`、`docs/prd/modules/kickoff-home.md`、`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-005、LIVE-006、LIVE-017、PRED-016、H5-026、HOME-010、MEM-002、MEM-008、ADM-402、ADM-907、ADM-908
- 设计图：用户提供的接口截图
- 设计图文件名：telegram-cloud-photo-size-5-6100591549361098949-y.jpg
- 设计图尺寸：830 x 484
- 视觉要点：接口返回 `30004` / `等级不足，无法发送弹幕`，与当前产品口径冲突
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/frontend-integration.md`
- AI/工具控制文件：`AGENTS.md`
- 项目 Overlay：不涉及
- 其他：遵守 `AGENTS.md` §14，不修改 `apps/web/**`

## 本次目标

1. 写入项目规则：等级特权已下线，不再按旧 H5 原型恢复等级门槛或等级特效。
2. 修复服务端发弹幕因 `user.level` 为 0 返回等级不足的问题。
3. 去除代码中的等级特权行为，包括弹幕颜色、进场特效、竞猜等级限额、等级配置接口、用户等级展示字段和后台等级配置管理。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `AGENTS.md` | 新增“产品口径：等级特权已下线”，明确发弹幕不需要等级 |
| `services/go-app/internal/service/live/service.go` | 删除发弹幕等级门槛，弹幕颜色统一为默认色 |
| `services/go-app/internal/service/live/service_test.go` | 增加 L0 用户可发送弹幕测试，更新默认色断言 |
| `services/go-app/internal/service/predict/service.go` | 删除投注单次/单日等级限额逻辑 |
| `services/go-app/internal/http/public/level.go` | 删除公开等级配置接口实现 |
| `services/go-app/internal/dto/level.go` | 删除等级配置响应 DTO |
| `services/go-app/internal/http/router/public.go` | 下线 `GET /api/v1/level/config` |
| `services/go-app/internal/http/router/admin.go` | 下线后台 `level-config` 管理路由 |
| `services/go-app/internal/http/adminapi/system_dashboard.go` | 删除后台等级配置 handler |
| `services/go-app/internal/service/admin/system.go` | 删除后台等级配置读写逻辑 |
| `services/go-app/internal/dto/auth.go` | 用户响应不再包含 `level` / `level_name` |
| `services/go-app/internal/dto/member.go` | 个人中心不再包含 `level_name` / `level_progress` |
| `services/go-app/internal/pkg/wsx/protocol.go` | 弹幕和进场 WS payload 不再携带用户等级 |
| `apps/admin/src/api/index.ts` | 后台 API client 移除等级配置与用户等级字段 |
| `apps/admin/src/views/users/UserListView.vue` | 用户列表移除等级列 |
| `apps/admin/src/views/users/UserDetailView.vue` | 用户详情移除等级展示 |
| `apps/admin/src/views/rooms/RoomDetailView.vue` | 房间观众列表移除 VIP/等级口径 |
| `docs/prd/modules/kickoff-live.md` | 更新直播间 PRD：弹幕、进场、rank_badge 不再按等级实现 |
| `docs/prd/modules/kickoff-predict.md` | 更新竞猜 PRD：投注限额不再按等级区分 |
| `docs/prd/modules/kickoff-h5.md` | 更新 H5 PRD：等级徽章、L5+ 标识、L6 广播不交付 |
| `docs/prd/modules/kickoff-home.md` | 首页等级特权入口改为不交付 |
| `docs/prd/modules/kickoff-member.md` | 个人中心升级进度和等级弹窗改为不交付 |
| `docs/prd/modules/kickoff-admin.md` | 后台观众/弹幕/用户管理去掉等级特权口径 |
| `docs/prd/product-prd.md` | 产品总 PRD 明确 C 端用户等级体系已下线 |
| `docs/api/openapi.yaml` | 更新接口契约描述，移除等级特权口径 |
| `packages/contracts/openapi/v1.yaml` | 同步前端可读契约 |

## 核心决策

1. 历史 `level` 字段允许兼容保留，但不得再参与权限、限额、颜色、特效或排序。
2. 发弹幕的服务端限制只保留登录、直播间状态、字数、频控、账户状态等非等级条件。
3. `/level/config` 和后台 `/level-config` 不再作为产品接口提供；历史表/字段仅按已发布 migration 留存，不作为功能入口。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目资产与项目规则 |
| 哪些内容可复用到下一个项目 | “旧原型冲突时以项目 AGENTS 产品口径为准”的规则写法 |
| 哪些内容只属于当前项目 | 小蓝看夜场的等级特权下线口径 |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 可作为多 Agent 约束，防止后续按旧原型回填等级特权 |
| 是否涉及 Scale Profile：mvp / growth / scale / enterprise | mvp |
| 是否影响项目 Overlay：project.config.json / docs/project | 不影响 |
| 是否增加了自动校验或 CI 门禁 | 增加服务层回归测试 |
| 是否降低了 Agent 偷懒空间 | 是，AGENTS 明确禁止按旧原型恢复等级特权 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-005、LIVE-006、LIVE-017、PRED-016、H5-026、HOME-010、MEM-002、MEM-008、ADM-402、ADM-907、ADM-908 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-predict.md`、`docs/prd/modules/kickoff-h5.md`、`docs/prd/modules/kickoff-home.md`、`docs/prd/modules/kickoff-member.md`、`docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` |
| 验收证据行 | `docs/qa/project-acceptance.md`、`docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 涉及契约，已同步 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | `docs/architecture/database-design-standards.md` |
| 是否影响数据表 / migration / 索引 | 不新增 migration；历史 `level` / `level_configs` 字段表按已发布 migration 留存，不再由业务读写为特权 |
| 是否使用表设计模板 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不影响资金账本；竞猜投注仍保留原事务与活动限制 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 结构化证据 | `docs/qa/architecture-capability-evidence.json` |
| 是否只是 CRUD | 否，涉及业务规则收敛 |
| 涉及能力 | 权限安全 / 数据一致性 |
| 不适用项及原因 | 不涉及异步、CDN、搜索、推荐 |
| 当前 MVP 边界 | 去除等级特权，保留基础互动与活动配置限制 |
| 未来迁移成本 | 如未来恢复会员体系，需要重新 PRD、ADR、契约和风控评审 |
| 升级触发指标 | 新增会员权益或等级付费能力 |
| 高风险触发项 | 权限 / 用户数据 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 需要发布 go-app 服务 |
| 回滚 | 回滚本次提交即可恢复旧逻辑，但产品口径不建议回滚 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及新增指标；接口错误率可观测低等级弹幕恢复情况 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 低等级用户发送弹幕已有回归测试；公开/后台等级配置接口已下线；用户响应和 WS payload 不再输出等级特权字段 |
| 红队质疑 | 历史客户端可能继续请求 `/level/config`；产品口径为接口下线，前端需同步删除旧调用 |
| 合入判断 | 可提交 Reviewer 复核 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现并验证发弹幕不再依赖等级，等级特权旧口径已从后端逻辑、后台管理、契约文档中移除 |
| 完成裁决 | 待 Reviewer / Owner / QA / CI / Release Manager 裁决 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `cd services/go-app && go test ./internal/service/live -run TestSendDanmakuAllowsLevelZeroUser -count=1` | 修复前失败，复现 `等级不足，无法发送弹幕` |
| `cd services/go-app && go test ./internal/service/live -run 'TestSendDanmaku|TestListDanmaku' -count=1` | 通过 |
| `cd services/go-app && go test ./...` | 通过 |
| `npm run build --workspace apps/admin` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 前端页面验收

本次未修改 `apps/web/**`、`apps/mobile/**`；已修改允许范围内的 `apps/admin/**`，移除后台用户等级展示和 VIP 观众口径。

## 风险与待办

1. H5/Web 前端仍需删除旧的等级弹窗、等级进场、等级弹幕和 `/level/config` 调用。
2. 线上发布后建议观察弹幕发送接口 30004 / 403 类错误是否下降。
3. 如未来新增会员权益，需要重新走 PRD、ADR、契约和风控评审，不得直接复用旧等级原型。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 不要根据旧 H5 原型恢复 L0/L1/L6 等级门槛、等级颜色或等级广播。
2. 历史 `level` 字段仅为已发布表结构遗留，不再作为权限、特权或展示字段。
3. 本次未修改 H5 实现，若前端仍展示等级特权，需要由前端团队按新契约删除旧调用和旧 UI。
