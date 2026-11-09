---
id: "doc-dc46eeea53e1"
title: "Kickoff 直播间 模块 PRD · kickoff-live"
date: "2026-05-29T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "监控告警", "CDN", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/prd/modules/kickoff-live.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/prd/modules/kickoff-live.md"
sourceSha256: "6069ce4dcfb8f3a36384a6ac83e1fb13f9e06ccb0b83a11091213b2c699350e6"
sourceSystem: "project-doc"
---

# Kickoff 直播间 模块 PRD · kickoff-live

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605290000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Kickoff%20%E7%9B%B4%E6%92%AD%E9%97%B4%20%E6%A8%A1%E5%9D%97%20PRD%20%C2%B7%20kickoff-live-02.md)

> 整理日期：2026-05-29 00:00｜日期依据：正文日期

模块：`kickoff-live`
端：Web
Owner：`@kickoff/frontend` + `@kickoff/backend`
状态：已确认
对应原型页面：`#page-live`

## 1. 模块目标

直播间是用户消费的**核心场景**，是 GMV 的主战场。目标：

1. **沉浸观赛**：高清视频流 + 比分浮层 + 实时数据，让用户专注于比赛
2. **社交互动**：弹幕 + 进场特效 + 打赏，强化"夜场氛围"
3. **竞猜转化**：浮动竞猜活动卡 + 全部活动弹窗，把观赛流量转为押注流量
4. **无等级特权**：旧原型里的等级弹幕、等级进场、等级排序、等级上限已下线，不作为实现依据

## 2. 用户角色

| 角色 | 说明 |
| --- | --- |
| 已登录观众 | 可看视频、发弹幕、打赏、押注 |
| 未登录观众 | 仅可观看视频，所有互动 CTA 跳登录页 |
| 主播 | 不在本模块；v1 主播仅用 OBS 推流，**不使用任何 web 端**；房间监控由"房间管理员"在后台完成（见 kickoff-admin §直播间管理） |

## 3. 需求列表

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| LIVE-001 | 视频播放器（拉流 / 暂停 / 刷新 / 全屏 / 静音 / 音量） | P0 | 已确认 | 拉流稳定，控制按钮齐全 |
| LIVE-002 | 比分浮层（顶部主播信息 + 底部比分） | P0 | 已确认 | **仅显示比分 + 阶段**；控球/射门/角球/黄牌等实时数据 v1 砍掉（团队无第三方体育数据 API 接入能力） |
| LIVE-003 | 弹幕浮层（视频上飘动） | P0 | 已确认 | 位置/大小/不透明度可调 |
| LIVE-004 | 弹幕列表（右侧滚动 + 滑动暂停） | P0 | 已确认 | 不展示等级徽章，不按等级着色 |
| LIVE-016 | 线路列表 + 选择上报接口（v0.3.1） | P0 | 已确认 | `GET /api/v1/live/lines?room_id={id}` + `POST /api/v1/live/lines/select` |
| LIVE-017 | 弹幕 rank_badge 实时计算 | P0 | 已取消 | 等级特权已下线，不按旧原型实现 |
| LIVE-005 | 弹幕发送（统一字数上限，无等级门槛） | P0 | 已确认 | 所有登录用户均可发；统一 100 字；统一默认颜色 |
| LIVE-006 | 进场提示（无等级特效） | P1 | 已确认 | 不按等级区分，不做 L6 全平台广播 |
| LIVE-007 | 打赏 modal（选金额 → 确认 → toast） | P0 | 已确认 | v0.3：预设 10/100/500/1000/5000/10000 💎；不再单次 1 💎 连击模式 |
| LIVE-008 | 浮动竞猜活动卡（视频右下角，主推 1 张） | P0 | 已确认 | 显示奖池、参与人数、倒计时、3 选项 |
| LIVE-009 | "查看全部活动" 弹窗 | P0 | 已确认 | 列出所有进行中活动 |
| LIVE-010 | 押注弹窗（点选项 → 输入金额） | P0 | 已确认 | 余额不足 → "前往充值" |
| LIVE-011 | 弹幕设置 popover（位置/大小/不透明度） | P1 | 已确认 | 海量全屏 / 全屏 / 半屏 / 上方 |
| LIVE-012 | 房间被关闭/下播 → 友好兜底 | P0 | 已确认 | 显示"主播已下播" + 推荐其他直播 |
| LIVE-013 | 线路选择（替换原"清晰度切换"） | P0 | 已确认 | 5 条线路（自动 + 线路 1-5）+ 实时延迟(ms) + 流畅度灯（4 档：流畅/良好/较慢/卡顿） |
| LIVE-014 | PIP 画中画（小窗悬浮） | P1 | 已确认 | 点小窗按钮 → 视频缩为 360×203 浮窗，可拖拽 + 跨页面持续播放；占位提示替代原位 |
| LIVE-015 | 复制直播间链接（分享） | P0 | 已确认 | 顶部分享按钮 → `navigator.clipboard` 复制 `room_url?ref={uid}` → 屏幕居中弹"链接已复制到剪贴板"toast |

## 4. 业务规则

### 4.1 视频与拉流（v0.3 改为"线路选择"模式）

1. **拉流**：进入直播间立即播放（autoplay 失败则提示用户点击）。
2. **线路选择**（替换原"清晰度切换"）：
   - 默认"自动"：客户端根据延迟探测选最优线路
   - 提供 5 条手动线路：线路 1（华东曲沃）/ 线路 2（华南）/ 线路 3（华北）/ 线路 4（海外）/ 线路 5（备用 CDN）
   - 每条线路实时显示：**延迟（ms）+ 流畅度灯**（4 档：流畅 ≤ 30 / 良好 ≤ 80 / 较慢 ≤ 200 / 卡顿 > 200）
   - 客户端每 10s 探测一次延迟（HEAD 请求边缘节点）
   - 用户手选后写入 localStorage，下次进任何房间记忆该选择
3. **画中画 PIP**：用户点小窗按钮 → 视频转为 360×203 浮窗，z-index 高于 SPA；可拖拽 + 跨 tab 持续播放；原位置显示占位卡（"视频已转为小窗 · 点击恢复"）。
4. **下播**：主播下播 → 推流停止 → 服务端推 WS 关播事件 → 前端切到兜底页（PIP 同步关闭）。
5. **分辨率**：v0.3 不再向用户暴露 1080p / 720p / 480p 三档选择，分辨率由所选线路在 CDN 侧决定（一条线路一档分辨率）。

### 4.1.1 比分浮层（v1 仅比分）

> **v1 砍掉**：控球率、射门、射正、角球、黄牌、越位等比赛实时数据卡。原型评审版含 4 项数据卡（控球/射门/角球/黄牌），v1 因无第三方体育数据 API 接入能力**统一删除**，仅保留比分。

1. 浮层显示：
   - 顶部：主播头像 + 名称 + 房间标题 + LIVE 徽章 + 观看人数
   - 底部：比分（运营手动维护）+ 进行阶段（未开赛/进行中/已结束/HT/FT）
2. 比分来源：**运营在后台"比赛比分快速录入"页面手动改**（见 `kickoff-admin.md §赛事 & 赔率管理` 子模块）
3. 比分刷新：客户端 30s 轮询 + 后台改动后推 WS `match.score.updated` 事件
4. 阶段切换：运营在后台手动切（未开赛 / 进行中 / 已结束）；驱动 UI 状态 + 竞猜状态
5. 观看人数统计：观众订阅直播间 WS 时实时同步 `current_online`，在线观众包含登录用户和游客连接；本场 `cumulative_views` 按进房人次累计，`unique_visitors` 按 session + user 去重（游客不计独立用户）；下播时当前在线清零，历史累计和峰值保留。

### 4.2 弹幕（v0.3 去除等级字数限制）

1. **字数上限**：所有登录用户统一 100 字；不再按 L0/L1/L6 等级限制发送。
2. **颜色**：统一默认颜色；前端不得按用户等级强制渲染颜色或特效。
3. **频率限制**：同用户 < 3s 一条弹幕；触发 → 红框提示。
4. **审核**：弹幕过敏感词词库（运营维护）；命中 → 不广播 + 记录；累计 ≥ 10 次 → 禁言 24h。
5. **弹幕来源**：所有弹幕走 WebSocket 推送；进入房间拉取最近 50 条历史；新弹幕实时推送。
6. **滑动暂停**：用户鼠标在弹幕列表上滚动时，列表暂停自动下滚。

### 4.3 进场提示

1. 进场提示不按等级区分；需要展示时仅使用普通房间内提示。
2. 不做 L4/L5 全屏动画，也不做 L6 全平台广播。

### 4.4 打赏（v0.3 改为 modal 选金额模式）

1. **触发**：用户点视频下方"打赏"按钮 → 弹出打赏 modal。
2. **金额选择**：预设 6 档 `10 / 100 / 500 / 1000 / 5000 / 10000` 💎；默认选中 `100`。
3. **确认**：点"立即打赏"→ 扣钻 → 关 modal → 顶部弹出 toast"{username} 打赏了 N 💎"。
4. **不再有连击**：原"1 次 = 1 钻石 + 3s 内连击合并"逻辑废弃（v3.75 / v3.99）。
5. **结算**：打赏完成立即扣减钻石；普通用户打赏实时累加主播侧 GMV。运营账号送礼照常在 C 端和主播端展示，并进入实时礼物榜和众筹解锁进度，打上 `is_operator_tip` 快照；礼物本身价值保留在 `rmb_equiv`，但主播结算字段 `settlement_rmb_equiv/settlement_diamond_amount` 为 0，不计入真实 GMV、主播收益和奖励。
6. **房间内广播**：所有用户都能看到打赏 toast；toast 显示 2.4s 后淡出。
7. **打赏排行**：本场 TOP 10 打赏者（用户）记录，供主播下播后查看；用户侧不展示。
8. **余额不足**：modal 内"立即打赏"按钮置灰，提示"余额不足 · 前往充值"，点击跳充值 modal。
9. **H5 与 Web 同流程**：H5 端也是 modal + toast，不再用 H5 特有的弹珠飘动动画（v3.75 已对齐）。

### 4.5 浮动竞猜活动卡

1. **位置**：视频右下角浮动卡片，仅展示 1 个"主推活动"。
2. **主推规则**：仅"竞猜进行中" 状态；按奖池倒序取第 1 个。
3. **倒计时**：实时跳动；倒计时结束 → 卡片消失或切到下一活动。
4. **点击选项**：唤起押注弹窗；余额不足 → 跳充值。
5. **无进行中活动**：不显示卡片（不留位）。
6. **查看全部活动**：点击 → 弹窗显示所有"进行中"活动列表。

### 4.6 押注弹窗

1. **输入范围**：100 - 50,000 💎（以全局配置和活动配置为准）。
2. **快捷金额**：500 / 1,000 / 5,000 / 最大（取活动上限 vs 余额的最小值）。
3. **校验**：余额 ≥ 金额；不超活动/全局上限；不超活动剩余封盘时间（封盘瞬间禁止下单）。
4. **下单**：携带幂等键 → 后端事务（扣钻石、写订单、更新奖池） → 成功提示。
5. **失败**：余额不足 → "前往充值"按钮；已封盘 → "活动已结束"；其他 → 通用错误。

### 4.7 复制直播间链接（分享）

1. **入口**：视频画面右上角分享按钮（剧场式 / 横屏 / 沉浸式三种模式都有）。
2. **链接格式**：`https://xiaolan-kanqiu.app/room/{room_id}?ref={uid}`；`ref` 用于推广归因（v1 仅写日志，不付分销奖励）。
3. **复制实现**：优先 `navigator.clipboard.writeText`；不支持时 fallback `textarea + execCommand('copy')`。
4. **反馈**：成功 → 屏幕**居中**（v4.43）弹"链接已复制到剪贴板"toast 2.2s 自动消失；失败 → 红色 toast"复制失败，请手动复制"。
5. **未登录用户**：仍可分享（`ref` 字段省略）。

### 4.8 画中画 PIP（v0.3 新增）

1. **入口**：视频控制条 PIP 按钮（图标：小矩形右下嵌套小矩形）。
2. **行为**：
   - 视频缩为 360 × 203 浮窗，default 位置：屏幕右下角，距边 20px
   - 浮窗可拖拽（按住整个窗体），不可缩放
   - 浮窗右上角有"关闭"按钮；点击 → 视频回原位
   - PIP 持续期间用户可切换 SPA 页面（赛程 / 我的 等），视频不中断
3. **限制**：
   - 同时只能有 1 个 PIP；切换房间 → 旧 PIP 关闭、新视频在原位开始
   - PIP 与全屏互斥；PIP 时点全屏 → 先关 PIP 再进全屏
4. **占位卡**：原位置显示一张占位卡，含"视频已转为小窗 · 点击恢复"CTA，点击 = 关 PIP。

## 5. 边界与异常

| 场景 | 系统行为 | 提示/状态 |
| --- | --- | --- |
| 拉流失败 | 显示重试按钮 | "网络异常，点击重试" |
| 主播下播 | 切到兜底页 | "主播已下播 · 推荐其他直播 →" |
| 弹幕 WS 断开 | 自动重连（指数退避） | 顶部红条"实时通信断开，重连中..." |
| 钻石余额不足 | 阻止打赏/押注 | 跳充值 |
| 未登录发弹幕 | 跳登录 | "请先登录后发弹幕" |
| 押注金额超活动/全局上限 | 阻止提交 | "押注金额超出限制" |
| 押注封盘瞬间 | 提交失败 | "活动已封盘，无法投注" |
| 用户连续刷弹幕 | 客户端节流 | 红框"发送过于频繁" |
| 命中敏感词 | 不广播 + 记审计 | 仅自己看到"内容审核中" |
| 复制链接 API 不可用 | fallback textarea | 静默使用 execCommand；失败时红 toast |
| PIP 时浏览器禁止跨窗口（iOS Safari） | 显示提示 | "iOS 暂不支持画中画，请使用全屏" |
| 切换线路时切换中 | 视频短暂黑屏 | 显示 loading；2s 内切完成 |

## 6. 权限与风控

1. 进入直播间：登录态可观看视频；未登录可观看但所有互动跳登录。
2. 发弹幕、打赏、押注：必须登录。
3. **审计日志**：打赏（每次）、押注（每次）、被禁言、敏感词命中 → 全部审计。
4. **风控规则**：
   - 弹幕违禁词高频（R-502）：房间 10min 内 ≥ 15 次 → 告警，建议人工巡查
   - 大额打赏（同用户短时累计高额）属技术架构识别的潜在风控缺口，**原型评审版未定义该规则**，待产品决定是否补入 PRD 后再统一登记规则 ID

## 7. 数据对象

| 对象 | Owner | 说明 |
| --- | --- | --- |
| `streamer_room` | `services/go-app` | 直播间表 |
| `live_session` | `services/go-app` | 一次开播会话（含开始时间、结束时间、统计） |
| `danmaku` | `services/go-app` + `services/realtime` | 弹幕表（room_id 哈希分 16 表） |
| `tip_record` | `services/go-app` | 打赏记录（连击算一条） |
| `predict_bet` | `services/go-app` | 押注记录 |
| `room_audit_log` | `services/go-app` | 房间内审计（敏感词、禁言、风控） |
| `forbidden_words` | `services/go-app` | 敏感词词库（运营维护） |

## 8. API/事件契约

| 需求 ID | 契约 | Owner Service | 状态 |
| --- | --- | --- | --- |
| LIVE-001 | `GET /api/v1/live/room/{room_id}` | `services/go-app` | 已实现；返回房间、主播、关联比赛与比分快照 |
| LIVE-001/013 | `GET /api/v1/live/room/{room_id}/play-url` | `services/go-app` | 已实现；返回 `flv_url` / `hls_url` / `expire_at`，当前不按线路返回不同地址 |
| LIVE-001 | `POST /api/v1/live/room/{room_id}/refresh-token` | `services/go-app` | 已实现；需登录 |
| LIVE-002 | `GET /api/v1/match/{match_id}/score`（30s 轮询兜底）+ `WS /ws/v1/match/{match_id}` | `services/go-app` | 已实现；房间详情已内嵌一次性比分快照 |
| LIVE-003/4/5 | `WS /ws/v1/live/{room_id}` 弹幕/进场/系统消息 | `services/go-app` | 已按 OpenAPI §16 envelope/type 对齐 |
| LIVE-005 | `POST /api/v1/live/room/{room_id}/danmaku` + `GET /api/v1/live/room/{room_id}/danmaku` | `services/go-app` | 已实现；历史响应为 `data.items[]`，发送响应为 `data=LiveDanmaku` |
| LIVE-007 | `POST /api/v1/live/room/{room_id}/tip` body 含 `diamond_amount` / `client_combo_seq` | `services/go-app` | 已实现；资金写接口，必须带 `Idempotency-Key` 和设备指纹 |
| LIVE-102 | `GET /api/v1/live/room/{room_id}/crowdfund` | `services/go-app` | 已实现；C 端进房主动拉本场众筹解锁快照，后续增量走 WS |
| LIVE-008 | `GET /api/v1/live/room/{room_id}/activities` | `services/go-app` | 已实现；返回 `main` + `all` |
| LIVE-010 | `POST /api/v1/predict/bet` | `services/go-app` | 已实现；直播间投注弹窗复用竞猜下单接口 |
| LIVE-013 | `GET /api/v1/live/lines?room_id={room_id}` 返回启用线路；`POST /api/v1/live/lines/select` 上报选择 | `services/go-app` | 已实现；当前 `room_id` 预留，全房间共用线路池 |
| LIVE-013 | `HEAD /edge/{line_id}/probe` 客户端延迟探测（CDN 边缘节点） | CDN | 待设计 |
| LIVE-014 | （纯前端，无后端接口） | `apps/web` + `apps/h5` | 待前端接入 |
| LIVE-015 | `POST /api/v1/share/log` body `{room_id, uid}` 用于推广归因日志 | `services/go-app` | P1 待对齐 |
| LIVE-016 | `GET /api/v1/live/lines?room_id={room_id}` 返回 N 条；`POST /api/v1/live/lines/select` body `{room_id, line_id}` 上报选中（风控统计） | `services/go-app` | 已实现；`auto` 为前端虚拟项，不由后端返回 |
| LIVE-017 | `rank_badge` | `services/go-app` | 已取消；客户端如收到历史字段应忽略 |

### 8.1 H5 / Web 直播间联调口径

1. 进入 `/live/{room_id}` 先调 `GET /api/v1/live/room/{room_id}`，SSR 可用；拿到 `match.id` 后再订阅 `/ws/v1/match/{match_id}`。
2. 播放地址只调 `GET /api/v1/live/room/{room_id}/play-url`；当前不会因为线路不同返回不同 URL，线路选择先作为体验和统计上报。
3. 弹幕历史响应是 envelope 包 `data.items[]`，不是 `data[]`；发送弹幕成功响应是单条 `LiveDanmaku`。
4. 打赏请求字段是 `diamond_amount`，不是原型简写的 `amount`；所有资金写接口必须带 `Idempotency-Key`。
5. 房间竞猜卡调用 `GET /api/v1/live/room/{room_id}/activities`，有 `main` 才展示主推卡；没有活动时整个卡片隐藏。
6. 线路列表调用 `GET /api/v1/live/lines?room_id={room_id}`；后端只返回真实线路，前端自行置顶“自动”虚拟项并在选择后上报 `line_id=auto`。
7. 打赏解锁卡进房先调 `GET /api/v1/live/room/{room_id}/crowdfund` 初始化 `cumulative_diamond/stages/achieved/next_stage`；之后继续监听 `live.crowdfund.progress` 与 `live.crowdfund.stage_unlocked` 做增量更新。

### 8.2 WS DanmakuPayload / TipPayload / ViewerJoinPayload 协议

基础 envelope 以 `docs/api/openapi.yaml` §16 为准：`type/msg_id/ts/trace_id/data`。直播间当前已实现：

```json
{
  "type": "live.danmaku.received",
  "msg_id": "2102885196873729",
  "ts": 1779788188037,
  "trace_id": "abc123",
  "data": {
    "user_id": "5678",
    "nickname": "MK_BangkokGold",
    "level": 0,
    "color": "default",
    "content": "押 5000 💎",
    "sent_ts": 1779788188037
  }
}
```

`live.viewer.count.updated` payload 使用 `viewer_count` / `peak_count`；`live.tip.combo` payload 使用 `user_id` / `nickname` / `combo_count` / `diamond_amount`。

`rank_badge` 已取消。服务端不生成该字段，客户端不得按旧原型恢复等级徽章。

## 9. 验收标准

| 需求 ID | 验收标准 |
| --- | --- |
| LIVE-001 | 进入房间立即拉流；视频流稳定 ≥ 99%；控制按钮全部可用 |
| LIVE-002 | 顶部主播信息 + 底部比分浮层永远可见；比分 30s 刷新或运营改动后 WS 实时推送（不再含控球/射门/角球/黄牌等数据卡） |
| LIVE-003 | 弹幕从右往左飘动；用户可调位置/字号/不透明度并立即生效 |
| LIVE-005 | 任意等级用户发出 101 字弹幕被阻止；L6 用户红色特效弹幕正确显示 |
| LIVE-006 | L6 用户进入任意房间，全平台所有直播间收到震撼广播 |
| LIVE-007 | 点打赏按钮 → 弹 modal → 选 500 💎 → 点确认 → 钻石扣减 500 + 顶部 toast 弹出 2.4s |
| LIVE-008 | 主推卡显示当前奖池最大的"进行中"活动；倒计时实时 |
| LIVE-010 | 押注 10,000 → 钻石扣减 10,000；奖池累加；导航 chip 余额同步 |
| LIVE-012 | 主播下播 → 5s 内房间切到兜底页 |
| LIVE-013 | 打开线路选择 → 显示 5 条线路 + 实时延迟 + 流畅度灯；切换后 2s 内重连完成 |
| LIVE-014 | 点 PIP → 视频缩 360×203 浮窗；拖拽流畅；切页面视频不中断；点关闭恢复原位 |
| LIVE-015 | 点分享 → 链接复制成功 → 屏幕居中 toast 2.2s |

## 10. 测试要求

1. **单元测试**：弹幕字数校验、无等级门槛发弹幕、连击合并
2. **集成测试**：押注下单事务（含失败回滚）、打赏事务、敏感词命中
3. **WS 测试**：100 人房间发弹幕 P99 < 100ms；断线重连
4. **E2E**：观看 → 弹幕 → 打赏 → 押注 → 下播
5. **压测**：单房间 5000 人同时在线 + 弹幕 100/s
6. **截图**：进行中房间、连击 banner、押注弹窗、全部活动弹窗、下播兜底

## 11. 待确认问题

| 问题 | Owner | 截止时间 | 状态 |
| --- | --- | --- | --- |
| 拉流 CDN（腾讯云 LVB / 阿里云 / 火山引擎） | `@kickoff/tech` | 2026-05-29 | 待确认 |
| 5 条线路命名（华东/华南/华北/海外/备用 vs 线路 1-5 数字） | `@kickoff/product` | 2026-05-29 | 待对齐 |
| 弹幕是否要做 token 化压缩（节省带宽） | `@kickoff/backend` | 2026-06-01 | 待确认 |
| 是否补入大额打赏风控规则及阈值（原型评审版未定义） | `@kickoff/security` | 2026-05-29 | 待对齐 |
| 打赏对应的钻石→主播分成比例 | `@kickoff/product` | 2026-06-01 | 待确认 |
| 视频鉴黄实时性要求（赛事直播是否真人秀类风险等同） | `@kickoff/security` | 2026-05-29 | 待确认 |
| 分享 `ref` 推广归因是否上分销奖励（v1 仅记日志） | `@kickoff/product` | 2026-06-15 | 待对齐 |
| PIP 在 iOS Safari 降级方案（不支持 vs 走 native PiP API） | `@kickoff/frontend` | 2026-06-01 | 待对齐 |
