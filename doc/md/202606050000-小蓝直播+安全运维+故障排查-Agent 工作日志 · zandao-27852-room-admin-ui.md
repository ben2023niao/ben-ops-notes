---
id: "doc-f3f1feafceb4"
title: "Agent 工作日志 · zandao-27852-room-admin-ui"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-zandao-27852-room-admin-ui.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-zandao-27852-room-admin-ui.md"
sourceSha256: "7155e5c8e53fba1655b2d63c89393182f9967abadb8ce7de3b9ffff8feab5aa0"
sourceSystem: "project-doc"
---

# Agent 工作日志 · zandao-27852-room-admin-ui

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606050000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20zandao-27852-room-admin-ui.md)

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：修复 Zandao Bug 27852，移除当前版本不需要的房管分配 UI

## 输入资料

- Zandao Bug：27852
- 标题：【后台】【直播管理】【直播间管理】【管控】当前版本没有房管功能，页面房管分配功能建议去掉
- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-901
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 直播间管控页不再展示房管分配功能。
2. 页面初始化不再请求房管列表和 room_admin 账号列表。
3. 直播间列表不再展示房管管理员计数列，避免当前版本误导运营。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/rooms/detail.vue` | 移除房管分配区块、分配/移除逻辑和页面初始化请求 |
| `apps/admin/src/views/rooms/list.vue` | 移除管理员计数列 |
| `apps/admin/src/locales/langs/zh-CN/room.json` | 移除房管分配和管理员列文案 |
| `apps/admin/src/locales/langs/en-US/room.json` | 移除房管分配和管理员列文案 |

## 核心决策

1. 当前版本只是隐藏不需要的后台运营功能，保守起见不删除后端接口、DTO 和历史数据结构。
2. 移除页面初始化请求，避免不可见功能继续访问 `/rooms/{id}/admins` 和管理员账号列表。
3. 列表页同步移除管理员计数列，避免入口层仍暗示可配置房管。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-901 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不涉及，未修改接口契约 |
| 不涉及契约的原因 | 后台 UI 隐藏当前版本不用的房管功能；后端接口保留兼容 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不影响 |
| 是否影响账本、事务、幂等或审计 | 不影响资金；移除 UI 后不会触发房管分配写审计 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 是，后台直播间管理页面能力收敛 |
| 涉及能力 | 权限安全：减少当前版本未启用的授权入口 |
| 当前 MVP 边界 | 不删除服务端保留接口，避免影响未来版本或历史兼容 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 仅影响 admin 静态构建产物 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不新增日志指标 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | Zandao Bug 27852 附图 |
| 页面截图 | 未使用浏览器截图，按代码移除对应渲染区块 |
| 响应式验收 | 不涉及新增布局 |
| 公共组件拆分 | 不涉及 |
| API 接口路径 | 移除前端对 `/rooms/{id}/admins` 的管控页调用 |
| 后台权限与审计 | 当前版本不再暴露房管分配入口 |
| 与设计图主要偏差 | 期望去掉房管分配，已移除 |
| 合入判断 | 可合入 |

## 风险与待办

1. 后端房管接口仍保留；如果产品明确永久下线，需要另起任务清理接口、权限、OpenAPI 和数据。
