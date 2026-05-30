---
id: "doc-843daf03deb9"
title: "Agent 工作日志：LIVE-101 D 阶段 smoke + 修两个落库 bug"
date: "2026-05-31T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "MySQL", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-streamer-d-smoke.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-streamer-d-smoke.md"
sourceSha256: "c8b51e596dc23161589910c76151b38bed13e4b67add86b463ac3e9b31fa0457"
sourceSystem: "project-doc"
---

# Agent 工作日志：LIVE-101 D 阶段 smoke + 修两个落库 bug

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-streamer-d-smoke.md`

> 整理日期：2026-05-31 00:00｜日期依据：文件名日期

日期:2026-05-31
Agent:siggod / go-app
任务:三端联调 smoke + 修 live_chat_messages 列名错配

## 输入资料

- D1 commit:`133f6da feat(streamer): 主播端鉴权 5 接口 + 独立 JWT subject`
- D2 commit:`cd20297 feat(streamer): 开播/下播/改房间 + Zego webhook 兜底`
- D3 commit:`c33a454 feat(streamer): 弹幕敏感词缓存 + 主播 init_password 自动生成`

## 本次目标

1. 全流程 curl smoke:admin → create streamer → approve → login → 改房间 → start live → 弹幕命中三动作 → stop live → change password → 旧密码失效
2. 修发现的两个 bug(都是 D3 模型层未对齐 B 段 migration 实际列名)

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `internal/model/live.go` | LiveChatMessage 列名修正:Severity/Action/Words/Handled → violation_severity/violation_action/violation_words/violation_handled(B 段 migration 实际列名,D3 model 写错为短名) |
| `internal/service/live/service.go` | 未命中时 wordsJSON 写 "[]"(violation_words 是 MySQL JSON 列,空字符串触发 invalid JSON) |

## 核心决策

1. **列名以 DB 为准,不改 schema**:DB 列已落 violation_ 前缀(B 段 commit b6ca5f5 已定),改 model 比改 migration 影响面小
2. **JSON 列空值用 `[]` 而非 NULL**:violation_words 设了 NOT NULL?(看 DDL 是 NULL allowed,但 GORM 写 "" 时 MySQL JSON 验证报错);统一 `[]` 占位语义明确,也方便后台 SQL 直接 JSON_LENGTH 判空

## smoke 步骤 + 实测结果

| 步骤 | 命令 | 结果 |
| --- | --- | --- |
| 1. admin 登录 | `POST /admin/auth/login kickoff_admin/Admin1234!` | 拿 token |
| 2. admin 创主播 | `POST /admin/streamers` | 返 `[敏感内容已脱敏] `username=siggod_smoke01` |
| 3. admin 审批 | `POST /admin/streamers/{id}/approve` | OK |
| 4. 主播登录 | `POST /streamer/auth/login siggod_smoke01/HZpd3VNY` | 拿 token,`[敏感内容已脱敏] |
| 5. 主播 me | `GET /streamer/me` | self 信息正确 |
| 6. 主播看房间 | `GET /streamer/me/rooms` | items=[] (尚未关联) |
| 7. DB 改 streamer_id 关联房间 | `UPDATE live_rooms SET streamer_id=...` | 关联成功 |
| 8. 主播改房间 | `PATCH /streamer/rooms/{id}` `{title, tags:[足球,深夜]}` | OK,tags 落库 |
| 9. 主播开播 | `POST /streamer/rooms/{id}/start` | 返 zego_app_id/token/server,stream_no=rm_room1_1780221761 |
| 10. 主播再开播 | 同上 | 409 `房间已在直播中` ✅ |
| 11. 刷 Zego token | `POST /streamer/rooms/{id}/refresh-zego-token` | OK |
| 12. 弹幕-正常 | `POST /live/room/{id}/danmaku "今天比赛真精彩"` | code=0,violation_flag=0 |
| 13. 弹幕-BLOCK | "加我赌博群" | 20001 `内容含违禁词,请修改后再发` ✅ 不落库 |
| 14. 弹幕-MASK | "草啊太精彩" | code=0,DB 落库 `*啊太精彩`,violation_flag=1 action=2 words=["草"] |
| 15. 弹幕-ALERT | "看广告免费送金币" | code=0,DB 原文落库,violation_flag=1 action=4 words=["广告"] |
| 16. 主播下播 | `POST /streamer/rooms/{id}/stop` | OK,room→ENDED(3),session→ENDED(2) duration_sec=319 |
| 17. 主播改密 | `POST /streamer/auth/change-password` 旧→新 | OK |
| 18. 用新密码登录 | login | OK,[敏感内容已脱敏] |
| 19. 用旧密码登录 | login | 30001 `账号或密码错误` ✅ |

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器,还是项目资产 | 项目资产 + bug fix |
| 哪些内容可复用到下一个项目 | 列名对齐前 grep migration 实际列名的检查清单 |
| 哪些内容只属于当前项目 | violation_* 列定义 |
| 是否影响数据表 / migration / 索引 | 否(model 列名修正,不改 schema) |
| 是否使用表设计模板 | n/a |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 无 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否使用表设计模板 | n/a |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否,直播 + 内容审核全链路 |
| 涉及能力 | 已覆盖鉴权 / 状态机 / 内容审核 / 缓存 / Webhook |
| 高风险触发项 | 直播状态 + 主播账号 |
| 能力门禁结论 | smoke 通过,允许合入 |

## 验证记录

| 命令 | 结果 |
| --- | --- |
| `go build ./...` | 通过 |
| `go vet ./...` | 通过 |
| `go test -race -count=1 ./internal/service/live/...` | 通过 |
| 上表 19 步 curl smoke | 全通过 |

## 风险与待办

1. Zego webhook 实际回调未在 smoke 跑(ZegoCloud Console 未配置 dev 公网回调),靠单测覆盖兜底
2. forbidden_words 后台 CRUD 接口仍未做(本期仅手动 INSERT 测试),v1.x 内补
3. `live_chat_messages` 月分表的 violation 列名前缀(`violation_*`)与 model 字段名(短名)曾错配,后续加新月份分表时确保 DDL 模板与 model 一起更新

## 交接说明

下一位 Agent / 工程师需要知道:

1. 启动 api 必须带 `APP_ZEGO_APP_ID` + 32 字节 `APP_ZEGO_SERVER_SECRET`,否则直播相关接口降级 503(`ErrFeatureClosed`)
2. forbidden_words 改完等 ≤5min 自动 reload,或重启 api 立刻生效;启动 log 会打 `forbidden_words reloaded count=N`
3. 月份分表 (`live_chat_messages_YYYYMM`) 必须由 cron 提前建,缺月份会让弹幕 INSERT 返 500;本地 dev 缺 202607,生产前 cron 须就位
