---
id: "doc-097f98716ec0"
title: "Agent 工作日志 · admin-datepicker-ms-regression"
date: "2026-06-04T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-admin-datepicker-ms-regression.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-admin-datepicker-ms-regression.md"
sourceSha256: "d5caa91d4ed9d26006138a4910854142cae6b334e9a9f3efdd53a5abc67b67ac"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-datepicker-ms-regression

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20admin-datepicker-ms-regression.md)

> 整理日期：2026-06-04 00:00｜日期依据：文件名日期

日期：2026-06-04
Agent：Codex
任务：修复后台日期控件毫秒时间戳回显为 1784 年的问题

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-201
- 设计图：用户提供后台直播间 Banner 推荐表单截图
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 定位 Banner 推荐开始/结束时间重新打开后显示 1784 年的问题。
2. 修复 DatePicker 回显毫秒时间戳的类型转换。
3. 检查其它后台 DatePicker 是否有同类 `_at_ms` 字符串回显。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/rooms/list.vue` | Banner 推荐表单回显开始/结束时间时保留 number 毫秒值，不再转字符串。 |
| `apps/admin/src/views/matches/list.vue` | 赛事开赛时间自动填充和编辑回显保留 number 毫秒值。 |

## 核心决策

1. Element Plus DatePicker 使用 `valueFormat: 'x'` 时，表单值应按毫秒时间戳 number/string 输出；回显时传入纯数字毫秒值最稳定。
2. 后端接口继续使用 UnixMs，不改契约。
3. 不新增全局日期包装组件，先修实际错误来源，避免扩大影响面。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-201 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不变；仍使用 `*_at_ms` UnixMs。 |
| 不涉及契约的原因 | 仅前端表单回显类型修复。 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 影响 admin 前端构建产物。 |
| 回滚 | 回滚本次前端改动即可。 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 修复了毫秒时间戳字符串被日期控件按日期字符串解析的问题。 |
| 红队质疑 | 未跑真实浏览器登录流，仍需在 dev 环境按用户步骤复测一次。 |
| 合入判断 | 可进入评审；建议补真实页面复测。 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / partially-verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `rg "String\\([^)]*_at_ms..." apps/admin/src` | 未发现剩余 `_at_ms` 字符串回显问题；仅剩修复后的 helper 命中。 |
| `node -e ...2026-06-04T20:57:13+07:00...` | 确认目标时间毫秒值对应 `2026-06-04 20:57:13`。 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 用户提供 Banner 推荐表单截图 |
| 页面截图 | 未生成 |
| UI 视觉证据 manifest | 未更新 |
| 真实手机视口 | 不适用 |
| 桌面/平板视口 | 未跑真实浏览器 |
| 响应式验收 | 不涉及 |
| API 接口路径 | `POST /api/v1/admin/rooms/{id}/home-banner` |
| 后台权限与审计 | 沿用既有 super_admin 路由和后端审计 |
| 合入判断 | 待真实环境复测 |

## 风险与待办

1. 需要在已登录 admin dev 环境按用户步骤复测一次。
2. 若其它页面未来回显 UnixMs，必须传 number，不要传毫秒字符串。
3. 可后续沉淀共享 `unixMsDatePickerValue` helper，减少重复。

## 交接说明

1. 问题不是后端时间值错误，是前端 DatePicker 回显传入了毫秒字符串。
2. `1780581433000` 对应 `2026-06-04 20:57:13`，不能作为日期字符串传给控件。
3. Banner 推荐表单和赛事表单已改为 number 回显。
