---
id: "doc-ba9f4af0ea48"
title: "Agent 工作日志 · lsj-hls-probe-before-zego"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "自动化", "CDN", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-hls-probe-before-zego.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-hls-probe-before-zego.md"
sourceSha256: "00ece35292251adb6846aa895db7a54cff308c1bf35af19f13a279ffad6cf7f7"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-hls-probe-before-zego

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E8%87%AA%E5%8A%A8%E5%8C%96-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20lsj-hls-probe-before-zego.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：创建 ZEGO 云播放器前校验 LSJ m3u8 可访问性

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：LIVE-101
- 接口/契约：`POST /api/v1/admin/rooms/{id}/prepare-live`
- 团队可读文档：`docs/api/streamer-lsj-zego-cloud-player.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户反馈 ZEGO `DescribePlayers` 返回 `status=6`，错误为云播放器未开始推流。

## 本次目标

1. 在调用 ZEGO `CreatePlayer` 前，后端先探测 LSJ `main_url` / `backup_url` 是否 HTTP 2xx 且是 HLS playlist。
2. 主线路不可用时自动尝试备用线路作为主推送地址。
3. 主备都不可用时直接返回明确错误，不再创建必然失败的 ZEGO 云播放器。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/liveprogram/service.go` | 新增 HLS URL 探测和主备线路选择，开播准备前置拦截 404/非 HLS 内容。 |
| `services/go-app/internal/service/liveprogram/service_test.go` | 增加主线路 404 切备用、主备都 404 返回明确错误的单测。 |
| `docs/agents/logs/2026-06-03-lsj-hls-probe-before-zego.md` | 记录本次修复与验证。 |

## 核心决策

1. LSJ `play` 返回 m3u8 URL 不代表 CDN 上实际有流，必须再探测 m3u8 内容。
2. ZEGO `status=6` 之前先由后端给出更直接的 `LSJ m3u8 不可访问` 错误。
3. 备用线路可用时直接用备用线路创建云播放器，提升成功率。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | 不新增字段，接口错误更明确 |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否 |
| 涉及能力 | 第三方直播源健康检查、ZEGO 推流前置校验 |
| 当前 MVP 边界 | 使用同步 HTTP GET 探测前 4KB m3u8；暂不递归校验 ts/key |
| 高风险触发项 | 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要部署 go-app 后生效 |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 错误信息会直接包含 HTTP 状态和上游返回摘要 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 能在本服务侧提前拦截 LSJ CDN 404，避免创建失败的 ZEGO player。 |
| 红队质疑 | 本地服务可访问不等于 ZEGO 机房可访问；仍保留后续 `DescribePlayers.Status=4` gate。 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| curl 当前 LSJ 主线路 m3u8 | HTTP 404 `stream not found` |
| curl 当前 LSJ 备用线路 m3u8 | HTTP 404 `stream not found` |
| `go test ./internal/service/liveprogram` | 通过 |
| `go test ./...` | 通过 |

## 风险与待办

1. 如果 m3u8 可访问但 ts/key 对 ZEGO 不可访问，仍会在 `DescribePlayers` 阶段失败。
2. 后续可补更深层 HLS 片段/key 探测和区域可达性诊断。

## 交接说明

下一位 Agent 或工程师需要知道：

1. `status=6` 是 ZEGO 云播放器连接媒体资源失败。
2. 当前用户这条 LSJ 源的主/备 m3u8 从公网测试均为 404 `stream not found`。
3. 部署后再强制重建，如果源仍 404，后台会直接返回 `LSJ m3u8 不可访问`。
