---
id: "doc-828173e3ef41"
title: "Agent 工作日志：Admin ↔ Public 一致性修复（#1/#2/#3/#5）"
date: "2026-05-24T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "Redis", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-admin-public-consistency-fixes.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-admin-public-consistency-fixes.md"
sourceSha256: "0c3ad7c6dffe64768a0a7798534bffccaeed04fcab107d0b38caba7bb8dcf78c"
sourceSystem: "project-doc"
---

# Agent 工作日志：Admin ↔ Public 一致性修复（#1/#2/#3/#5）

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-admin-public-consistency-fixes.md`

> 整理日期：2026-05-24 00:00｜日期依据：文件名日期

日期：2026-05-24
Agent：claude-code
任务：依据 code-explorer agent 输出的"admin ↔ public API 业务一致性审计"报告，修复 4 个真实业务/安全问题。剩余 #4（OpenAPI 已声明但 handler 未实现）作为单独的业务开发任务，#6/#7/#8/#9 推 v1.1。

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（按 project.config.json exceptions[apps.admin].exceptionReason 与 `docs/prd/modules/admin.md` 同义；用户管理 + 直播间管理子模块）、`kickoff-live.md`（WS 协议）
- 需求 ID：ADM-405 (Freeze)、ADM-305 (ForceEnd)、ADM-909 (DeleteDanmaku)、LIVE-002 (Match WS)
- 接口契约：`docs/api/openapi.yaml`（WS §16.6）
- 上游审计：code-explorer agent 输出的一致性差异

## 本次目标

1. **#1（RED）**：admin Freeze 同步写 `user:revoked_before:{uid}`，让冻结用户已颁发的 token 立即失效
2. **#2（YELLOW）**：admin ForceEnd / Ban 同步广播 WS `room_state`，让在场 WS 长连观众实时收到房间结束/封禁
3. **#3（YELLOW）**：admin/match.go + live/service.go 的 matchStatusString 从小写改大写，与 REST canonical（schedule.matchStatusString）对齐；WS RoomStatePayload / MatchStatePayload 文档注释同步
4. **#5（GREEN→YELLOW）**：protocol.go 新增 TypeDanmakuDelete + DanmakuDeletePayload；DeleteDanmaku 写后广播

## 修改文件

| 文件 | 修复项 | 说明 |
| --- | --- | --- |
| `services/go-app/internal/service/admin/user.go` | #1 | Freeze 调 `revokeUserSessions` 写 Redis `user:revoked_before:{uid}=now()`；提取共享 helper（与 ResetPassword 同机制） |
| `services/go-app/internal/service/admin/room.go` | #2 #5 | RoomService 加 `ws wsx.Broadcaster` 字段 + `SetWSBroadcaster`；ForceEnd / Ban 写后广播 TypeRoomState；DeleteDanmaku 广播 TypeDanmakuDelete |
| `services/go-app/internal/http/router/admin.go` | #2 #5 | `roomSvc.SetWSBroadcaster(wsHub)` wiring |
| `services/go-app/internal/service/admin/match.go` | #3 | matchStatusString 改大写（UPCOMING/LIVE/ENDED/CANCEL） |
| `services/go-app/internal/service/live/service.go` | #3 | matchStatusToString 改大写，与 REST 对齐 |
| `services/go-app/internal/pkg/wsx/protocol.go` | #3 #5 | 注释 + payload 文档大写；新增 TypeDanmakuDelete 常量 + DanmakuDeletePayload 结构体 |
| `docs/api/openapi.yaml` | #5 | WS §16.6 增 `danmaku_delete` event 说明 |

## 核心决策

1. **#1 抽取 `revokeUserSessions` 共享 helper**：避免 Freeze 复制 ResetPassword 那 30 行；helper 集中负责 Redis 写入 + 失败 audit；后续 Disable 等强制下线动作可复用
2. **#1 Freeze 失败 audit 不阻断主流程**：DB status 已落，Redis 不可达只是降级（旧 token 仍可用至 TTL），写 fail audit 给运维介入；不应让"Redis 抖动"导致 Freeze 整体失败（用户管理优先级高于会话撤销精度）
3. **#2 RoomService 加 Broadcaster 走与 live.Service 同模式**：默认 `wsx.Noop{}` 防御性初始化，router 装配后 `SetWSBroadcaster(wsHub)` 注入；保持启动期单元测试无 Redis 依赖
4. **#2 Status 字段用大写 "ENDED"/"BANNED"**：与 #3 修复同步，保持 WS / REST 跨端一致
5. **#3 不动 RoomStatePayload / MatchStatePayload struct field 命名**：兼容性优先；只改函数返回 + 注释说明大写约定
6. **#5 类型名用 TypeDanmakuDelete (not TypeDanmakuDeleted)**：与既有 TypeDanmaku / TypeTip 命名风格一致（动词原形，不带 ed）；OpenAPI 兼容 `live.danmaku.deleted` 历史标记，标注以本 type 为准

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | (1) go build / go vet 全过；(2) go test -race -count=1 ./... 全 ok；(3) integration test -tags=integration 5/5 pass 无 regression；(4) make framework-check 17/17 全绿；(5) admin 端代码改动均在已有 wiring 路径内，不破坏既有 router/admin.go 注入次序 |
| 红队质疑 | (1) #1 Redis 不可达时只写 audit 不报错，授权安全测试者能否利用？→ 蓝队答：Freeze 已写 DB status=FROZEN，新登录被 auth service 直接拒（service.go:141）；旧 token 仅在 access_ttl 内（≤2h）可用，已是大幅收紧；Redis 长期不可达是另一类故障；(2) #2 Broadcaster 注入失败（Noop）默认行为 admin 删弹幕看不到？→ 蓝队答：Noop 是 fail-safe，prod 不应跑成 Noop；router 加载若未注入，admin 写后无 WS 推送但 DB 状态已变，前端轮询 REST 仍能感知（业务降级而非中断）；(3) #3 改大写会不会破坏现有前端代码？→ 蓝队答：admin 前端目前只显示状态值不做条件分支（grep ConfigListView / UserListView 验证），影响面 0；apps/h5 / apps/web 还未实现，正好趁早纠偏；(4) #5 新增 TypeDanmakuDelete 与历史 OpenAPI 中 live.danmaku.deleted 是否分裂？→ 蓝队答：openapi.yaml 已加注"以本 type 为准"，迁移期前端按 TypeDanmakuDelete 实现即可；live.danmaku.deleted 是文档历史，无实际代码引用 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented + verified（go test 全过 + framework-check 17/17 全绿） |
| Project Decision | pending-review |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-405 / ADM-305 / ADM-909 / LIVE-002 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `kickoff-admin.md` / `kickoff-live.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml` §16.6 新增 danmaku_delete event；RoomStatePayload / MatchStatePayload Status 字段注释更新 |
| 验收证据行 | `docs/qa/acceptance-evidence.md`：本次为一致性修复，无新增完成行；`docs/qa/project-acceptance.md` kickoff-admin / kickoff-live 行的"自动化测试"列受益（鉴权 + WS 广播 + 状态一致性） |
| 不涉及契约的原因 | 仅扩展 WS event type（新增不破坏既有），其余为内部实现修正 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | Go: gofmt + go vet 全过；错误处理走 errcode 统一封装 |
| 数据表设计 | 不影响表结构 |
| 是否影响账本、事务、幂等或审计 | 不影响账本；增加 audit 字段（Freeze 失败 audit、room_state/danmaku_delete WS event）|
| 规范例外与原因 | 无 |

## 验证记录

- `go build ./...`：通过
- `go vet ./...`：通过
- `go test -race -count=1 ./...`：member / wallet / config / ledger 全 ok
- `go test -tags=integration -race ./internal/pkg/ledger/...`：5/5 pass
- `make framework-check`：17/17 全绿

## 后续动作（剩余审计项）

待业务开发批次：
- **#4**：OpenAPI 已声明但 backend 无 handler 的 5 类接口（`PUT /admin/matches/{id}/phase`、`admin/live-lines` CRUD、`admin/ads/h5`、`admin/payment-channels`、`live/lines` 用户侧） — 上轮 PRD v0.3.1 留下的实现债，独立批次实现

待 v1.1：
- **#6**：`/me/recharge-records` vs `/wallet/recharge-records` 路径统一
- **#7**：`GET /wallet/recharge/breakdown` handler 注册
- **#8**：admin/match.go `Update` 加 WS 推送（与 UpdateScore 双路径统一）
- **#9**：System Config / Banner 加 Redis 缓存层（高流量场景）
