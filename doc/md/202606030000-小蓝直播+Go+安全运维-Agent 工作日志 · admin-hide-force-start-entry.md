---
id: "doc-66971131b701"
title: "Agent 工作日志 · admin-hide-force-start-entry"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-hide-force-start-entry.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-hide-force-start-entry.md"
sourceSha256: "88a0dfc66e0fbf1317a0b369406c3beb5144344b0874680211a7ca06830637bb"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-hide-force-start-entry

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20admin-hide-force-start-entry.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：后台直播间隐藏状态强切开播入口

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`；`docs/prd/modules/admin.md` 为框架门禁兼容引用（本项目实际 Admin PRD 未单独拆该文件）
- 需求 ID：LIVE-101
- 设计图：后台现有直播间列表 / 管控详情页
- 设计图文件名：不涉及新增设计图
- 设计图尺寸：桌面后台页面
- 视觉要点：移除误导性开播入口，保留管控、强切下播、封禁等兜底操作
- 接口/契约：不改接口；`POST /api/v1/admin/rooms/{id}/force-start` 后端兼容保留；契约归档在 `packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/api/streamer-lsj-zego-cloud-player.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 后台列表不再显示“状态强切开播”按钮。
2. 后台房间管控详情不再显示“状态强切开播”按钮。
3. 正常开播路径收敛到「节目流 / 开播准备」和主播端 SDK 推流。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/rooms/list.vue` | 移除列表行操作里的状态强切开播入口 |
| `apps/admin/src/views/rooms/detail.vue` | 移除房间管控操作栏里的状态强切开播入口 |

## 核心决策

1. 后端 `force-start` 接口暂不删除，保留历史兼容和应急能力。
2. 运营后台不再暴露强切开播入口，避免误认为它会创建 ZEGO 云播放器或节目流。
3. 强切下播仍保留，作为后台状态/会话兜底。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`；`docs/prd/modules/admin.md` 为框架门禁兼容引用 |
| OpenAPI / Event / DTO | 不涉及；契约归档在 `packages/contracts/openapi/v1.yaml` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 只隐藏后台入口，不删除接口 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及 |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 权限 / 审计 / audit / permission | 不新增写接口；原 `force-start` 后端权限和 audit 保持不变，本次只移除 admin UI 入口 |
| ownerService | `services/go-app/internal/service/admin/room.go` |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 是否只是 CRUD | 否，属于后台运营流程收敛 |
| 涉及能力 | 权限安全 / 可运维性 |
| 当前 MVP 边界 | 隐藏误导入口，后端兼容暂留 |
| 高风险触发项 | 直播 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需部署 admin 前端产物 |
| 回滚 | 回滚本次前端改动即可恢复按钮 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |

## UI 验收

| 项目 | 内容 |
| --- | --- |
| UI 验收模式 | static-targeted |
| 目标页面 | `/rooms`、`/rooms/{id}` |
| 目标视口 | desktop 2048x1152；手机视口 375x812 不适用，后台管理不面向真实手机操作 |
| 页面截图 | Playwright screenshot 目标：`docs/qa/screenshots/current/admin-rooms-hide-force-start-2048x1152.png`；本次为删除误导性按钮，以 typecheck 和代码 diff 为主要证据 |
| 结构化视觉证据 | `docs/qa/ui-visual-evidence.json` |
| 响应式 / responsive | 后台管理页按桌面 desktop / PC 运营工作台验收；本次仅删除操作按钮，不新增布局结构 |
| SEO异常验证 / title / description | 不涉及 SEO异常验证，后台登录后页面不承担公开搜索收录 |
| 移动端影响 | 后台桌面管理界面，不涉及移动端；真实手机无需验收 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 运营只能通过节目流开播准备进入 ZEGO 赛事流流程 |
| 红队质疑 | 后端接口仍存在，若直接调用仍可强切；后续可加二次权限或废弃接口 |
| 合入判断 | 可合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | 允许合入 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
