---
id: "doc-7f884417c183"
title: "Agent 工作日志 · api-issues-backend-fix"
date: "2026-05-27T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Docker", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-27-api-issues-backend-fix.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-27-api-issues-backend-fix.md"
sourceSha256: "c538e97a7dab30569993e949e952eac87d7664f4afd7ae8a2ef5f6092cd8aca8"
sourceSystem: "project-doc"
---

# Agent 工作日志 · api-issues-backend-fix

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-27-api-issues-backend-fix.md`

> 整理日期：2026-05-27 00:00｜日期依据：文件名日期

日期：2026-05-27
Agent：张小凡
任务：修复 H5 公开 API 第一轮黑盒测试报告（apps/web/docs/test-reports/api-issues.md）中的后端隐患

## 输入资料

- 测试报告：`apps/web/docs/test-reports/api-issues.md`（13 项，P1×4 / P2×9，无 P0）
- 契约源：`packages/contracts/openapi/v1.yaml`（唯一源）
- 相关 PRD：竞猜 ADR-0011（兑换下线、提现直接 5%）、PRD §4.2.4（提现限额 单日 5000 / 单月 50000）

## 本次范围与方向（已与需求方确认）

- B/C 类（Match 系列 shape + stage/status 枚举脱节）：**契约对齐后端**（改 v1.yaml 反向描述后端真实输出，不动 Go DTO）
- ISS-04 提现限额：**统一为 5000 单笔/日**
- D 类（status=UNKNOWN 种子、live_top 广告位、rtmp 播放地址、match_id 空串）：本轮**只改 Go 代码 / 配置 / 契约，不动 dev 种子数据**，列清单交运维
- ISS-05（账号首字符非数字）/ ISS-06（logout 强制 refresh_token）：**本轮不动**，无契约依据 / 涉鉴权语义，待业务确认

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/predict/service.go` | ISS-12：竞猜规则文案删除"钻石需先兑换 RMB（手续费 20%）"已下线措辞，改为提现按平台费率 5% 直接发起 |
| `services/go-app/config/config.{dev,local,docker,example}.yaml`、`config.prod.yaml.example` | ISS-04：`biz.withdraw.max_amount` 50000→5000、`daily_limit` 200000→5000，与 `system_configs(5000)` 及 PRD §4.2.4 对齐（单月 = 5000×10 = 50000） |
| `packages/contracts/openapi/v1.yaml` | ISS-01/02/03/07/08/09/10：契约反向对齐后端真实输出（详见下） |
| `docs/api/openapi.yaml`、`packages/ts-sdk/src/generated/schema.ts` | `make openapi` + `make sdk` 重生产物 |

## 契约改动明细（契约对齐后端）

1. `MatchStatus` 枚举 `[SCHEDULED,LIVE,ENDED,CANCELLED]` → `[UPCOMING,LIVE,ENDED,CANCEL]`（后端 `matchStatusString` 实际取值；同时消除与 `HomeMatch.status` 的不一致）。ISS-02
2. `MatchStage` 枚举大写 `[GROUP,R16,QF,SF,...]` → 小写 DB 值 `[group_stage,round_of_16,quarter,semi,final,third_place]`（后端直出、admin 同枚举写入）。ISS-03
3. 新增 `MatchDetail` schema 映射后端 `dto.MatchDetail`，`/api/v1/match/{match_id}` 的 `data` 由 `Match` 改指 `MatchDetail`。ISS-01
4. `/match/{match_id}/score` inline → `{home_score,away_score,status,updated_at_ms}`。ISS-07
5. `MatchGoal` schema 改为后端 `MatchGoalItem` 字段；`/match/{match_id}/goals` 的 `data` 由数组改为 `{items:[MatchGoal]}`。ISS-08
6. `/match/{match_id}/team-comparison` inline → `{home_team,away_team,home_rank,away_rank}`（HomeTeamBrief），删除 v1 未实现的 home_record/goals/conceded 等字段。ISS-10
7. `/match/{match_id}/predict-summary` 由市场数组改为对象 `{activity_id,total_bet_count,total_bet_amount,hot_option}`。ISS-09
8. `/schedule/days` 删除 `day_label`，`matches` 由 `Match` 改指 `HomeMatch`；`/schedule/timeline` 的 `matches` 同改 `HomeMatch`（后端这些端点返回 `TodayMatchItem` ≈ HomeMatch）。ISS-01/02/03

> 未动 `Match` schema 本体（仍被 schedule/groups、bracket、LiveRoom.match 引用，且这些端点不在本轮 13 项内；阶段视图按 PRD v1 仅日期视图）。

## 未处理（D 类 / 待确认，交运维或业务）

| 编号 | 问题 | 根因 | 建议处理方 |
| --- | --- | --- | --- |
| ISS-02(残留) | `status:"UNKNOWN"` | dev 种子数据 `matches.status` 为非法值（非 1-4） | 运维修种子 |
| ISS-03(残留) | dev 出现 `semi_final` 而非 model 常量 `semi` | dev 种子 stage 值非规范 | 运维修种子 |
| ISS-11 | `live_top` 广告位超枚举、`h5_home_hero`/`h5_home_live_feed` 未配 | dev 广告位种子 | 运维 |
| ISS-13 | play-url 返回 `rtmp://edge2.kickoff.local` 内网占位 | dev SRS 边缘配置占位 | 运维 |
| 轻微 | `hot-predicts`/`predict/activities` 部分 `match_id:""` | 活动种子未关联比赛 | 运维 |
| ISS-05 | 账号首字符非数字未校验 | 契约 pattern 本身允许，规则缺失 | 待业务确认是否加规则 |
| ISS-06 | logout 强制 refresh_token，契约定义无 body | 鉴权语义取舍 | 待业务确认 |

## 验证记录

| 命令 | 结果 |
| --- | --- |
| `make openapi` | swagger-cli validate 通过 |
| `make sdk` | ts-sdk schema.ts 重生成功 |
| `go build ./...` | 通过 |
| `go test ./internal/service/{predict,wallet,schedule}/...` | 全部通过 |
| `./devtools/framework check` | 见下（补本日志后复跑） |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 采用「契约对齐后端」方向：未改 Go DTO，仅改 v1.yaml 反向描述真实输出，故 schedule/predict/wallet 单测保持绿、`go build` 通过；`make openapi` swagger 校验 + `make sdk` 重生均成功；提现限额改为配置值 5000，未触账本/扣费逻辑，withdraw_breakdown 已有 5000 上限用例覆盖。 |
| 红队质疑 | (1) `Match` schema 本体未改，仍被 groups/bracket/LiveRoom.match 引用且与后端不符——已确认这些端点不在本轮 13 项、阶段视图按 PRD v1 不做，LiveRoom.match 后端用独立 `LiveRoomMatchSnapshot`，本轮不扩范围。(2) `status:"UNKNOWN"`、`semi_final`、`live_top`、rtmp 占位、`match_id:""` 是 dev 种子/边缘配置问题，非 Go 代码 bug，按约定列清单交运维，未在代码兜底。(3) ISS-05/06 无契约依据 / 涉鉴权语义，按需求方决定本轮不动。 |
| 合入判断 | 允许合入：改动均为契约/配置/文案，无运行时逻辑变更，风险可控；待 Reviewer 复核契约方向。 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented（契约 + 配置 + 文案；未涉 Go DTO 改动） |
| 风险 | 资金类：仅调提现限额配置值，未改账本/扣费逻辑；withdraw_breakdown 已有 5000 上限测试 |
| Project Decision | pending-review（项目级裁决归口 `docs/qa/project-acceptance.md`，由 Reviewer / QA 给出） |
