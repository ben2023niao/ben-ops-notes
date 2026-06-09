---
id: "doc-e7b9a10a3668"
title: "Agent 工作日志 · lsj-match-picker-preview"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-lsj-match-picker-preview.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-lsj-match-picker-preview.md"
sourceSha256: "5bd989c3304b4fe4e7da0c3f538f6ad872aec0eec0e58b1bdfb1889d1b2900b2"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-match-picker-preview

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-lsj-match-picker-preview.md`

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

日期：2026-06-10
Agent：Codex
任务：赛事上游源选择弹窗增加预览播放

## 输入资料

- 需求 ID：LIVE-101
- 入口：后台管理 `/matches` 编辑/新建赛事弹窗 → 选择上游源
- 用户反馈：上游资源已能选择，但选择资源前也需要能播放验证

## 数据链路

入口页面：`apps/admin/src/views/matches/list.vue`
API：`GET /api/v1/admin/sports-live` 获取可选资源；`POST /api/v1/admin/sports-live/play` 换取 m3u8
DTO / service：`SportsLiveSourceService.Search/Play`
第三方来源：LSJ 体育 `/sportsLive/*`、LSJ 电影 `/movie/*`、Xinlang VOD
返回字段：复用 `app_name`、`stream_name`、`main_url`、`backup_url`
前端消费：赛事选择弹窗每条线路支持「预览」和「选择」两个动作，预览不写入表单，选择才写入绑定字段

## 根因

「上游资源管理」页已有 HLS 预览播放器，但「赛事列表」的选择上游源弹窗只实现了线路选择按钮，没有调用 `sportsLivePlay` 做播放验证。后端接口和 LSJ 电影源已可返回可播放线路，缺口在后台管理选择弹窗交互。

## 修改范围

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/matches/list.vue` | 引入 `hls.js`，新增上游 m3u8 预览弹窗；线路操作区增加「预览」按钮 |
| `apps/admin/src/locales/langs/zh-CN/matches.json` | 新增预览弹窗中文文案 |
| `apps/admin/src/locales/langs/en-US/matches.json` | 新增预览弹窗英文文案 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 是否影响前端字段 | 不改 API 字段；复用现有后台 `sports-live/play` |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/admin run typecheck` | 通过 |

## 风险与待办

1. HLS 预览受浏览器与上游 m3u8 跨域/防盗链影响；失败时弹窗保留主/备线路 URL 供技术排查。
2. 预览不会自动选择线路，避免误绑定；运营仍需点击「选择」完成绑定。
