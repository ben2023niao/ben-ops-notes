---
id: "doc-0bdbdef0f7b7"
title: "Agent 工作日志 · room-program-force-restart-contract"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "自动化", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-room-program-force-restart-contract.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-room-program-force-restart-contract.md"
sourceSha256: "45fc83aff771a44b7ab83ac3d81a84910873b50fb974b13322f3f5e56fd3a5ee"
sourceSystem: "project-doc"
---

# Agent 工作日志 · room-program-force-restart-contract

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E8%87%AA%E5%8A%A8%E5%8C%96-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20room-program-force-restart-contract.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：修复节目流强制重建未生效

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（admin 门禁兼容引用：`docs/prd/modules/admin.md`）
- 需求 ID：LIVE-101
- 接口/契约：`POST /api/v1/admin/rooms/{id}/prepare-live`，`docs/api/admin-api.md`，`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户反馈切换 LSJ 直播源后，直播源预览可看，但刷新、开播准备、强制重建均未替换 ZEGO 赛事流，页面仍显示旧 `MIXED_STREAM_READY`。

## 本次目标

1. 修复后台“强制重建”请求字段与后端契约不一致的问题。
2. 后端兼容旧字段，避免旧前端包或缓存继续失效。
3. 明确 FAILED 节目流可由普通开播准备重试，READY/MIXED 状态必须强制重建。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/api/modules/room.ts` | `prepareLive` 请求体改为发送后端契约字段 `force_restart`。 |
| `apps/admin/src/locales/langs/zh-CN/room.json` | 修正节目流提示文案，说明切换 LSJ 源后需强制重建。 |
| `services/go-app/internal/dto/admin_modules.go` | `AdminRoomPrepareLiveRequest` 增加 `force` 兼容字段。 |
| `services/go-app/internal/dto/admin_modules_test.go` | 增加 `force_restart` 与旧 `force` 字段解码测试。 |
| `services/go-app/internal/http/adminapi/program.go` | 后端 handler 使用 `force_restart || force`。 |
| `services/go-app/internal/service/liveprogram/service.go` | 抽出已有节目流替换判断；FAILED 允许普通准备重试，READY/MIXED 需强制重建。 |
| `services/go-app/internal/service/liveprogram/service_test.go` | 增加节目流替换规则测试。 |

## 核心决策

1. 契约字段以 OpenAPI 已定义的 `force_restart` 为准。
2. 后端临时兼容 `force`，防止旧后台静态资源或缓存导致强制重建继续无效。
3. `MIXED_STREAM_READY` 是房间节目流会话状态，表示已经回填混流 ID；不是 ZEGO 赛事流本身的状态。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`；门禁兼容引用 `docs/prd/modules/admin.md` |
| OpenAPI / Event / DTO | OpenAPI 已有 `force_restart`，本次代码对齐契约并兼容旧字段 |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；沿用已有 prepare-live 审计 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否 |
| 涉及能力 | 第三方直播源、ZEGO 云播放器节目流状态一致性 |
| 当前 MVP 边界 | 不新增 ZEGO 删除云播放器接口；通过结束旧节目会话并创建新云播放器实现重建 |
| 高风险触发项 | 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要同时部署 go-app 和 admin 静态包 |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不新增指标 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 修复了强制重建按钮传参错误，后端兼容旧字段，降低缓存导致的复现概率。 |
| 红队质疑 | 切换 LSJ 源后若旧节目流仍是 READY/MIXED，需要运营点击强制重建；普通开播准备不会覆盖健康节目流。 |
| 合入判断 | 可合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/dto ./internal/service/liveprogram ./internal/http/adminapi` | 通过 |
| `go test ./...` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 不涉及，本次只修复后台按钮请求字段和提示文案 |
| 设计图尺寸 | 不涉及 |
| 目标视口 | 后台桌面 1440x900 |
| 页面截图 | 不涉及布局变更；screenshot 未生成，原因是只改请求字段与一行提示文案，已用 typecheck/build 验证 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 375x812 手机视口不适用：后台桌面运营页，本次无布局变更 |
| 桌面/平板视口 | 桌面 1440x900，字段与文案变更由 typecheck/build 验证 |
| 响应式验收 | 不适用：未改布局、尺寸或组件结构 |
| API 接口路径 | `POST /api/v1/admin/rooms/{id}/prepare-live` |
| SEO异常验证/分享/下载渠道 | 不涉及 SEO异常验证，不改 title/description/分享/下载渠道 |
| 后台权限与审计 | 沿用已有后台房间权限与 prepare-live 审计；ownerService: `services/go-app` |
| 合入判断 | 可合入 |

## 风险与待办

1. 后续可接入 ZEGO 云播放器停止/删除能力，强制重建时主动回收旧 player。
2. 部署后需要在房间详情点“强制重建”，确认赛事流 ID 和云播放器 ID 变化。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 前端强制重建字段必须是 `force_restart`。
2. 后端暂时兼容 `force`，不要在新代码继续使用旧字段。
3. `MIXED_STREAM_READY` 表示混流已回填，不代表 LSJ 赛事源已自动替换。
