---
id: "doc-e4eea6432e4d"
title: "Kickoff H5 端 模块 PRD"
date: "2026-05-23T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/kickoff-h5.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/kickoff-h5.md"
sourceSha256: "f22e5c3ab70ec6ffb5d543cac2ec184440482e6e615aff511778058f6e395a80"
sourceSystem: "project-doc"
---

# Kickoff H5 端 模块 PRD

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/kickoff-h5.md`

> 整理日期：2026-05-23 00:00｜日期依据：正文日期

模块：`kickoff-h5`
端：H5（移动端浏览器）
Owner：`@kickoff/frontend`
状态：已确认（v0.3：4 pane + 3 种直播模式 + 3 广告位 + 字证图 + 编辑信息 + 未登录 gate）
对应原型页面：`#page-h5`（含 4 pane `#h5-app` + 剧场式直播间 `theater-*` + 横屏 overlay `.landscape-room` + 沉浸式 `#h5-vert-frame`）

> **v0.3 变更（2026-05-23 对齐原型 v4.45）**：
> 1. **5 pane → 4 pane**：删除"设置"pane（v4.26 退出登录入口移除后，设置 pane 无内容）；保留 `直播 / 赛程 / 竞猜 / 我的`。
> 2. **直播间 3 种模式**（v3.54-v3.57）：默认**剧场式**（16:9 视频 + 下方聊天 + 右侧广告 + 竞猜卡）；点扩展可进**横屏 16:9**；可选**沉浸式 9:16**（v3.54）。
> 3. **4 种广告位**（v4.32-v4.41）：
>    - A **吸底广告位**（live tab，全宽顶满，可关闭）
>    - B **固定角标广告位**（schedule tab，右下不动）
>    - C **浮动气泡广告位**（predict tab，RAF 弹墙运动）
>    - D **TopBar 横向滚动广告位**（v4.40，剧场式直播间顶部 marquee 文字滚动）
> 4. **个人信息编辑 modal**（v4.17 / v4.20）：点头像 → 弹 modal → 相册上传头像 + 用户名修改。
> 5. **保存账号信息字证图**（v3.84）：me-header"保存信息"chip → canvas 渲染 PNG。
> 6. **我的 tab 未登录 gate**（v4.15）：游客访问 me tab → 显示"请先登录"引导，资产区访问策略验证。
> 7. **TG 客服走中转页**：客服按钮跳 `#page-telegram`，再跳真 Telegram。
>
> **v0.3.1 增补（2026-05-24 原型 vs PRD 对照后补齐）**：
> 8. **等级特权下线**：旧原型里的弹幕等级徽章 / L5+ 标识 / L6 广播不交付，H5 不按等级做权限、颜色、特效或排序。
> 9. **实时比赛数据条**（H5-016 升级）：剧场式视频底部 marquee 显示完整数据（比分 + 控球率 + 射门 + 角球 + 黄牌 + 越位 + 比赛阶段 + 分辨率/码率）。
> 10. **剧场式竞猜卡收/展**（H5-011 增补）：竞猜卡可收起到右侧 mini 卡；点 mini 展开还原。
> 11. **充值记录状态机 + 5 通道**（H5-009 增补）：状态枚举 + 微信/支付宝/银联/USDT/e-CNY 通道展示。
> 12. **线路选择 modal**（H5-017 增补）：自动 + 5 条线路，含 ping + 阶梯色 + 推荐标签。
> 13. **充值费率展示**（H5-010 增补）：modal 内三行明细（充值金额 / 平台手续费 5% / 实际入账）+ USDT 专用行（应转账数量）。

## 1. 模块目标

H5 是 Web 端的**移动端镜像**，承担：

1. **移动端可用性**：在没有原生 App 的情况下，提供完整的移动端体验
2. **流量入口**：分享、外链、社交导流的落地承接
3. **三态直播体验**：剧场式（默认）/ 横屏 / 沉浸式 三种模式覆盖看球 / 推流 / 短视频流三种场景

H5 端**简化兜底**，不追求 Web 端全部功能，但**所有核心闭环（看-押-充-提）必须完整可走通**。

## 2. 用户角色

| 角色 | 说明 |
| --- | --- |
| 移动端用户 | 通过手机浏览器访问；可登录、押注、充值、提现 |
| 已登录 Web 用户 | 选择从 Web 切换到 H5；session 共用 |

## 3. 需求列表

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| H5-001 | 4 pane 主框架（直播 / 赛程 / 竞猜 / 我的） | P0 | 已确认 | 底部 tab 切换；v0.3 已删除"设置"pane |
| H5-002 | 直播 pane - Banner 轮播（5 张赛事卡） | P0 | 已确认 | 倒计时/比分/即将开始三态 |
| H5-003 | 直播 pane - 正在直播列表 | P0 | 已确认 | 主题房卡片 |
| H5-004 | 直播 pane - 热门竞猜（最多 4 条） | P0 | 已确认 | 主-平-客 三档赔率 |
| H5-005 | 赛程 pane - 按天分组（同 Web） | P0 | 已确认 | LIVE / VS / 已结束 三态 |
| H5-006 | 竞猜 pane - 一级 tab（列表 / 我的 / 规则） | P0 | 已确认 | tab 切换 |
| H5-007 | 竞猜 pane - 二级状态 tab（进行中/未开始/待开奖/已开奖） | P0 | 已确认 | 同 Web 4 状态 |
| H5-008 | 我的 pane - 资金钱包卡（2 项简化） | P0 | 已确认 | 钻石主余额 / 累计充值；提现弹窗另取 RMB 可提现 |
| H5-009 | 我的 pane - 资金记录（充值/提现 tab） | P0 | 已确认 | 简化版列表 |
| H5-010 | 我的 pane - 充值/提现按钮（唤起 modal） | P0 | 已确认 | 跳 modal 化页面 |
| H5-011 | 剧场式直播间（默认模式） | P0 | 已确认 | 16:9 视频 + 下方聊天 + 右侧广告 + 竞猜卡 |
| H5-012 | 横屏直播间（手动切换） | P0 | 已确认 | 点扩展按钮 → 容器旋转 90° + landscape-room overlay 接管 |
| H5-013 | 沉浸式直播间（`#h5-vert-frame`，可选） | P1 | 已确认 | 9:16 全屏视频 + 多层 scrim + 玻璃浮层 |
| H5-014 | 打赏 modal + toast（同 Web 流程） | P0 | 已确认 | 6 档金额 → 确认 → toast "{username} 打赏了 N 💎" |
| H5-015 | 顶部主播信息（头像/名称/观看数/分享） | P0 | 已确认 | 三种直播模式均显示 |
| H5-016 | 比分条（LIVE 时间/双方/比分） | P0 | 已确认 | 三种直播模式均显示 |
| H5-017 | 底部输入栏（弹幕/线路/打赏） | P0 | 已确认 | 3 控件（v0.3 去除 HD 切换，改线路；去送花） |
| H5-018 | 直播间内广告卡片（剧场式右侧） | P1 | 已确认 | 可关闭 |
| H5-019 | 直播 tab 吸底广告位 A | P1 | 已确认 | 全宽顶满；右上 × 关闭；本会话内不再展示 |
| H5-020 | 赛程 tab 角标广告位 B | P1 | 已确认 | 固定右下；不动；右上 × 关闭 |
| H5-021 | 竞猜 tab 浮动气泡广告位 C | P1 | 已确认 | RAF 弹墙运动（60 px/s）；右上 × 关闭 |
| H5-021b | 剧场式 TopBar 滚动广告位 D（v0.3.1） | P1 | 已确认 | 剧场式 live-room 顶部横向 marquee；左滚 30 px/s；不可关闭（运营硬投放） |
| H5-026 | 弹幕 rank_badge 等级徽章 | P0 | 已取消 | 等级特权已下线；不要按旧原型实现 |
| H5-027 | 剧场式竞猜卡收/展（v0.3.1） | P1 | 已确认 | 卡头 ⌃ 收起到右侧 mini；mini ⌄ 展开还原 |
| H5-028 | 线路选择 modal（v0.3.1，对接 LIVE—016） | P0 | 已确认 | 自动 + 5 线路；ping + 阶梯色（smooth/ok/slow/bad）+ "推荐"标签 |
| H5-029 | 充值费率分解展示（v0.3.1） | P0 | 已确认 | modal 三行明细 + USDT 专用行（应转账 USDT 数量） |
| H5-030 | 页脚联系信息 | P0 | 已确认 | 页面页脚展示客服邮箱、商务合作邮箱、主域名；数据来自 `GET /api/v1/config/system` 的 `site.support_email`、`site.business_email`、`site.primary_domain` |
| H5-022 | 我的 tab - 点头像唤起"编辑信息" modal | P0 | 已确认 | 改头像（相册上传）+ 用户名 |
| H5-023 | 我的 tab - "保存信息" chip → 字证图 PNG | P0 | 已确认 | canvas 渲染同登录模块字证图规格（详见 kickoff-auth.md §4.5） |
| H5-024 | 我的 tab - 游客 gate | P0 | 已确认 | 未登录显示"请先登录"引导，访问策略验证资产区 |
| H5-025 | 我的 tab - TG 客服 chip → 跳 `#page-telegram` 中转页 | P0 | 已确认 | 中转页样式仿 t.me 落地页 |

## 4. 业务规则

### 4.1 与 Web 共用

1. **共用账号体系**：H5 token 与 Web token 互通；同设备登录共用 session。
2. **共用资金体系**：钱包、押注、订单数据共用。
3. **共用 API**：所有业务 API 与 Web 共用，仅前端展现不同。

### 4.2 4 个 Pane（v0.3 删除"设置"）

| Pane | 用途 | 内容 |
| --- | --- | --- |
| 直播 | 首页发现 | Banner 轮播 + 正在直播 + 热门竞猜 + 吸底广告位 A |
| 赛程 | 全部比赛 | 按天分组（v1 仅日期视图，不上阶段视图）+ 角标广告位 B |
| 竞猜 | 押注中心 | 一级 tab + 二级状态 tab + 浮动气泡广告位 C |
| 我的 | 个人中心 | 钱包卡（2 项）+ 资金记录 + TG 客服 + 编辑信息 + 保存字证图 |

> 原"设置"pane v0.3 删除：退出登录入口已移除（v4.26），密码修改 / 找回不再提供（详见 [`kickoff-auth.md`](kickoff-auth.md) §4.4），无其他必需内容。

### 4.3 直播间 3 种模式

| 模式 | 触发 | 布局 | 默认 |
| --- | --- | --- | --- |
| 剧场式 | 点直播 pane 房间卡 → 默认进入 | 16:9 视频（上）+ 主播 chip + 比分条 + 聊天列表 + 竞猜卡 + 输入栏 | ✓ |
| 横屏 | 剧场式点"扩展" / 输入栏旋转图标 | 容器旋转 90°（852×393）+ `.landscape-room` overlay 接管：视频全屏 + 玻璃顶栏 + 聊天 overlay + 竞猜卡缩 mini | |
| 沉浸式 | （v0.3 可选；目前 `#h5-vert-frame` 默认隐藏，需手动开启） | 9:16 全屏视频 + scrim + 玻璃浮层 + 弹幕飘动 + 浮动竞猜卡 | |

### 4.4 四种广告位（v0.3.1 新增 D）

| 广告位 | 位置 | 触发 | 关闭行为 | 数据来源 |
| --- | --- | --- | --- | --- |
| 首页 Hero 广告 | H5 首页顶部运营 banner | 进入 H5 首页展示 | 不可关闭；为空时回退赛事 Hero | `GET /api/v1/ads/slots/h5_home_hero/creatives` |
| 首页信息流广告 | H5 首页直播列表附近 | 首页直播区展示 | 右上 ×；本会话不再显示 | `GET /api/v1/ads/slots/h5_home_live_feed/creatives` |
| A 吸底 | live tab，全宽顶满（贴底 tabbar 上方） | 进入 live tab 自动展示 | 右上 ×；本会话不再显示 | `GET /api/v1/ads/slots/h5_sticky/creatives` |
| B 角标 | schedule tab，右下不动（距底 130px 右 14px） | 进入 schedule tab 自动展示 | 右上 ×；本会话不再显示 | `GET /api/v1/ads/slots/h5_corner/creatives` |
| C 气泡 | predict tab，自由弹墙（RAF 60px/s 线性 + 弹墙反弹） | 进入 predict tab 自动展示并启动 RAF | 右上 ×；停止 RAF | `GET /api/v1/ads/slots/h5_bubble/creatives` |
| D TopBar | 剧场式 live-room 顶部 marquee（左滚 30 px/s） | 进入 live-room 自动展示 | 不可关闭（硬投放）；离开 live-room 自动隐藏 | `GET /api/v1/ads/slots/h5_theater_topbar/creatives` |

**广告位通用约束**：
- A/B/C：tab 切换 / 横屏 / 沉浸式 模式下强制隐藏；右上 × 可关闭
- D：仅剧场式 live-room 显示；横屏 / 沉浸式 / 其他 tab 强制隐藏；不提供关闭按钮
- A/B/C 关闭状态用 `dismissed` class 标记，本会话 sessionStorage 持久化
- A/B/C/首页信息流广告卡使用 `title`（≤ 6 字）/ `text_content`（≤ 10 字）/ `image_url` / `link_type` / `link_target`
- D 广告使用 `text_content`（≤ 80 字符，纯文本支持 emoji；前端循环播放）
- 首页 Hero 广告使用 `title` / `image_url` / `link_type` / `link_target`；为空时前端回退到赛事 Hero
- 广告数据统一从 `ad_slots + ad_creatives` 读取；H5 首页 Banner 使用 `GET /api/v1/home/banner`

### 4.5 打赏 toast

1. **触发**：本人打赏成功 / 房间内用户打赏 → 顶部飘 toast（v0.3 与 Web 端 [`kickoff-live.md`](kickoff-live.md) §4.4 同流程），不按等级区分。
2. **内容**：用户头像 + 用户名 + "打赏了 XXX 💎"。
3. **样式**：剧场式 / 沉浸式 顶部居中；横屏 屏幕居中。
4. **时长**：2.4s 后淡出；不可手动关闭。

### 4.6 编辑个人信息 modal（v0.3 新增）

1. **触发**：me-header 头像点击。
2. **内容**：
   - 头像：96px 圆形大预览，右下角相机图标提示，点击 → 调起相册 `<input type="file" accept="image/*">`
   - 用户名输入框：默认填入当前用户名；maxlength 20；不允许特殊字符
   - UID 只读行：显示当前 UID + 锁图标
   - 注册账号只读行：显示当前注册账号 + 锁图标（强调"不可修改"）
3. **保存**：
   - 头像走 `POST /api/v1/me/avatar` 上传（multipart）
   - 用户名走 `PATCH /api/v1/me/username` 更新
   - 关闭 modal + me-header 同步刷新
4. **图片格式**：JPG / PNG / WebP；客户端建议压缩 ≤ 2 MB；服务端裁剪 200×200。

### 4.7 保存账号信息字证图（v0.3 新增）

1. **触发**：me-header 旁"保存信息"chip。
2. **生成**：客户端 `<canvas>` 渲染 PNG（**密码明文不上传**，纯前端读 localStorage 或会话内存）。
3. **规格**：760 × 600 PNG，与 [`kickoff-auth.md`](kickoff-auth.md) §4.5 字证图**完全一致**。
4. **文件名**：`小蓝看夜场-账号信息-YYYYMMDD-HHMM.png`。
5. **安全考虑**：登录态下密码不一定还在内存中（fresh session 没有），此时 chip 应禁用并提示"请重新登录后再保存"。

### 4.8 未登录 gate（v0.3 新增）

1. **触发**：游客（无 token）点 me tab。
2. **行为**：me pane 内容区显示一张引导卡（"请先登录后查看账户信息" + "立即登录" CTA + 锁图标插画），原资产区 / 资金记录 / 编辑入口全部访问策略验证。
3. **CTA**：点击 → 跳 `#page-auth`。
4. **回跳**：登录成功后回到 H5 me tab，gate 自动消失。
5. **其他 tab**：直播 / 赛程 / 竞猜 仍对游客开放（仅观看，互动 CTA 跳登录）。

### 4.9 客服入口

1. me-header 旁 TG 客服 chip → 跳 `#page-telegram` 中转页（同 Web，详见 [`kickoff-auth.md`](kickoff-auth.md) §4.4）。
2. 中转页样式仿 t.me 落地页：浅绿背景 + Telegram 蓝色 LOGO + "SEND MESSAGE" CTA。
3. 用户点 CTA → 跳真 Telegram（生产环境为运营配置的 `https://t.me/{username}`）。

### 4.10 H5 特有约束

1. **状态栏适配**：模拟 iOS 状态栏（9:41 + 信号 + 100% + 电池）保持原型一致。
2. **手势**：Banner 左右滑、列表上下滚、底部 tab 切换。
3. **下拉刷新**：直播 pane 和 我的 pane 支持下拉刷新。
4. **键盘弹起**：发弹幕时，输入栏跟随键盘上推（iOS Safari 适配）。
5. **横屏**：仅直播间提供横屏切换；其他 pane 强制竖屏。
6. **PWA**：v1 可不实现；v2 可添加 manifest 让用户"添加到主屏幕"。

### 4.11 选端切换

1. 登录成功后二步式选端 modal（详见 [`kickoff-auth.md`](kickoff-auth.md) §4.9）。
2. 用户在 H5 中切回 Web 端入口 v0.3 不交付（v4.26 退出登录已删，设置 pane 已删）。

### 4.13 弹幕等级徽章（已取消）

弹幕等级徽章、L5+ 标识、L6 广播均已取消。H5 不应读取或渲染 `rank_badge` 作为等级特权。

**协议字段**：不再要求 WS payload 追加 `rank_badge`；若旧客户端收到该字段也应忽略。

### 4.14 实时比赛数据条（v0.3.1 升级 H5-016，v1 最小集）

剧场式直播间视频底部 marquee 文字滚动栏（左滚 40 px/s）。

**v1 字段（最小集）**：

| 段 | 内容 | 字段 | 来源 |
|---|---|---|---|
| 比分 | `1 - 0` | `home_score / away_score` | `GET /api/v1/matches/{id}` + WS `match.score.updated` |
| 对阵 | `法国 vs 阿根廷` | `home_team_name / away_team_name` | match detail 同上 |
| 阶段 | `上半场 45'` / `中场休息` / `下半场 78'` / `加时上半 95'` / `加时下半 115'` / `点球 5-4` | `phase + minute (含补时 +N)` | match detail + WS `match.phase.changed`（v0.3.1 新增事件） |
| 流 | `1080P · 5.4 Mbps` | 客户端本地探测 | 不入接口 |

> **不做（与 [`kickoff-live.md`](kickoff-live.md) §4.1.1 / LIVE—002 对齐）**：控球率 / 射门 / 角球 / 黄牌 / 红牌 / 越位。理由：v1 团队无第三方体育数据 API 接入能力；admin 手动录入工作量大且实时性差。原型 v4.45 marquee 显示这些字段是**视觉占位**，前端实现时按本规则**裁切到仅 4 段**。
>
> v1.1 或 v2 接通第三方赛事 API 后再扩展，届时 PRD 升级。

**比赛阶段枚举**：`pre_match / first_half / half_time / second_half / et_first / et_break / et_second / penalty / finished`（统一 [`kickoff-match-detail.md`](kickoff-match-detail.md) §7 数据对象）

### 4.15 剧场式竞猜卡收/展（v0.3.1 新增 H5-027）

1. **默认态**：竞猜卡完整显示在视频下方（含 head + 3 档赔率按钮 + 总押注额）
2. **收起**：点 head 右上 ⌃ → 卡片消失，右侧广告区下方出现 mini 卡（仅显示 LIVE pill + 对阵 + 剩余时间）
3. **展开**：点 mini ⌄ → 还原完整卡，mini 隐藏
4. **session 持久化**：sessionStorage 记录收/展状态，刷新保留
5. **横屏 / 沉浸式 不受影响**：横屏走 `landscape-room` 浮动卡；沉浸式走 `pc-wrap` 浮动；都无 mini 模式

纯前端交互；**无后端接口变化**。

### 4.16 线路选择 modal（v0.3.1 升级 H5-017）

1. **触发**：直播间输入栏点"线路"按钮
2. **接口**：`GET /api/v1/live/lines?room_id={id}`（[`kickoff-live.md`](kickoff-live.md) §8 LIVE—016）
3. **modal 结构**：
   - 头部：自动（智能切换）— 始终列首，默认选中
   - 列表：服务端返回 N 条线路（v1 默认 5 条），含 `{id, name, latency_ms, recommended}`
   - 每行：线路名 + "推荐" 标签（如有）+ ping 数 + 阶梯色 + 选中 √
4. **ping 阶梯色**：
   | 阈值 | 颜色 class | 文案 |
   |---|---|---|
   | < 30 ms | smooth（绿） | 流畅 |
   | 30-60 ms | ok（黄绿） | 良好 |
   | 60-100 ms | slow（橙） | 较慢 |
   | 100-200 ms | bad（红） | 卡顿 |
   | ≥ 200 ms / 超时 | cf（深红） | 不可用 |
5. **选中**：点行 → 客户端切流（HLS / FLV 切 URL）+ POST `/api/v1/live/lines/select` 上报（用于风控统计，不阻塞 UI）

### 4.17 充值记录状态机 + 5 通道展示（v0.3.1 升级 H5-009）

**充值记录列表字段**（API `GET /api/v1/me/recharge-records`）：

```
{ amount_rmb, channel, status, third_party_no, paid_at_ms, created_at_ms }
```

**channel 枚举**（与 [`kickoff-wallet.md`](kickoff-wallet.md) 共享）：
- `wechat` 微信支付
- `alipay` 支付宝
- `union` 银联 / 某支付平台
- `usdt_trc20` USDT (TRC20)
- `usdt_erc20` USDT (ERC20)
- `digitalrmb` 数字人民币 e-CNY

**status 枚举** + 前端展示样式：

| status | 文案 | 颜色 | 描述 |
|---|---|---|---|
| `success` | ✓ 已到账 | 绿 | 钻石已入账 |
| `chain_confirming` | ⛓ 链上确认中 | 蓝 | USDT 专属；区块确认数未达阈值 |
| `paying` | ⏳ 支付中 | 灰 | 已发起未到账 |
| `refunded` | ↩ 已退款 | 灰 | 渠道侧已退（金额前缀 "—"） |
| `timeout` | ✗ 超时取消 | 红 | 30 分钟未支付自动作废 |
| `failed` | ✗ 失败 | 红 | 渠道侧返回失败 |

> 5 通道（USDT 双链算 1 类）的实际落地依赖 [ADR-0010](../../decisions/ADR-0010-payment-channels.md)；v0.3.1 PRD 锁定**展示规则与字段名**，对接顺序由 ops 决定。

### 4.18 充值费率分解展示（v0.3.1 新增 H5-029）

充值 modal 显示费用拆解三行（v0.3 ADR-0011：扣 5% 平台费后 1:1 折算钻石）：

| 行 | 内容示例 | 来源 |
|---|---|---|
| 充值金额 | ¥100.00 | 用户选择金额 |
| 平台手续费(5%) | — ¥5.00 | `amount × system_config.wallet.recharge.platform_fee_rate` |
| 实际入账 | ¥95.00 | `amount - fee` |
| 钻石到账 | 95 💎 | `floor(net)` |

**USDT 专属附加行**（channel 为 usdt_*，v0.3.2 暂不开放；后续启用时补汇率字段）：

| 行 | 内容示例 | 来源 |
|---|---|---|
| 应转账 USDT | 13.19 USDT | `(amount + fee) / system_config.wallet.recharge.usdt_rate_cny` |

**接口**：`GET /api/v1/wallet/recharge/breakdown?amount=100&channel=wechat`（[`kickoff-wallet.md`](kickoff-wallet.md) §8 WALLET—010）；当前返回 `{amount_rmb, fee_rate, fee_rmb, net_rmb, diamond_amount, pay_type}`，USDT 请求返回功能关闭。

**底部文案**：`充值扣 5% 平台手续费 · 实际入账按 RMB:💎 = 1:1 兑换`

### 4.19 v1 简化项（相比 Web 削减）

| Web 模块 | H5 v1 是否交付 |
| --- | --- |
| 赛程 - 阶段视图 / Bracket | 不交付（仅日期视图） |
| 个人中心 - 等级特权弹窗 | 不交付；不要显示等级特权入口 |
| 个人中心 - 我的竞猜详细 4 tab | 走竞猜 pane 的"我的"二级 tab |
| 兑换页 | **v0.3 整体下线**（Web 端也已删除，详见 [`kickoff-wallet.md`](kickoff-wallet.md)） |
| 赛事详情完整三态 | 不交付（v1 H5 只跳直播间或竞猜中心） |
| 全平台名人堂 | 不交付 |
| 退出登录 | v0.3 整体不交付（v4.26 删除） |

## 5. 边界与异常

| 场景 | 系统行为 | 提示/状态 |
| --- | --- | --- |
| 不支持视频自动播放（iOS Safari） | 显示大播放按钮 | 点击后播放 |
| 弹幕键盘弹起遮挡 | 输入栏跟随上推 | iOS Safari 测试通过 |
| 移动数据网络弱 | 自动切线路（取延迟最低） | 顶部红条提示"已切换至线路 N" |
| 横屏切换（非直播间） | 强制旋转回竖屏 | 提示"请保持竖屏" |
| 横屏切换（直播间） | 容器旋转 90° + landscape-room 接管 | overlay 自动显示，原 pane 隐藏 |
| 未授权麦/相机 | 不影响普通观看 | 仅打赏/弹幕用音 / 不需要 |
| 切到后台 | 视频暂停（Wake Lock 释放） | 切回前自动恢复 |
| 编辑头像上传 > 5 MB | 阻止 + 提示 | "图片不能超过 5 MB" |
| 编辑头像格式非图片 | 阻止 + 提示 | "请选择 JPG/PNG/WebP 图片" |
| 字证图 canvas 渲染失败 | 降级文本展示 | "无法生成图片，请手动记下：账号 XX 密码 XX" |
| 游客进 me tab | 显示 gate | 引导卡 + "立即登录" CTA |
| 广告位关闭后再次进 tab | 不再展示 | sessionStorage 持久化关闭状态 |

## 6. 权限与风控

- 与 Web 共用；所有需登录 / 风控规则一致。
- 无独立审计；与 Web 共用审计日志。

## 7. 数据对象

与 Web 共用 `ad_slots + ad_creatives`，由运营在后台「广告管理」维护。前端按 `slot_code` 拉取当前生效广告；slot 关闭或无内容时不渲染。

## 8. API/事件契约

H5 端**全部复用 Web API**，前端按移动端适配。

| 区域 | 接口 |
| --- | --- |
| 直播 pane | 同 HOME—002/003/004/005 |
| 赛程 pane | 同 SCHED—001 |
| 竞猜 pane | 同 PRED—008/009 |
| 我的 pane | 同 MEM—001~006、WALLET—001 |
| 直播间（3 种模式共用） | 同 LIVE—001~017 |
| 编辑头像 | `POST /api/v1/me/avatar`（multipart `file`，后端落存储并回写 `avatar_url`） |
| 修改用户名 | `PATCH /api/v1/me/username`（v0.3 ADR-0011） |
| 广告位配置（首页 Hero / 首页信息流 / A/B/C/D） | `GET /api/v1/ads/slots/{slot_code}/creatives` |
| 实时比赛数据 | `GET /api/v1/matches/{id}/realtime`（[`kickoff-match-detail.md`](kickoff-match-detail.md) MATCH—005）+ WS `match.stats_update` 事件 |
| 弹幕 rank_badge | 已取消；基础联调不接入 |
| 线路列表 | `GET /api/v1/live/lines?room_id={id}`（LIVE—016） |
| 线路选择上报 | `POST /api/v1/live/lines/select`（风控统计） |
| 充值费率拆解 | `GET /api/v1/wallet/recharge/breakdown?amount={n}&channel={c}`（WALLET—010） |
| 充值记录（含 status + channel） | `GET /api/v1/me/recharge-records`（schema 见 [`kickoff-wallet.md`](kickoff-wallet.md) §7） |

## 9. 验收标准

| 需求 ID | 验收标准 |
| --- | --- |
| H5-001 | 4 个 tab 切换流畅；当前 tab 高亮；不再有"设置"tab |
| H5-002 | Banner 5 张滑动；指示点同步；自动播放 3s 切一张 |
| H5-005 | 赛程页按天分组；LIVE/VS/已结束三态显示正确 |
| H5-006/7 | 竞猜 pane 一级+二级 tab 联动；进入"我的"显示 4 状态 |
| H5-008 | 钱包卡显示钻石主余额和累计充值；提现弹窗 RMB 可提现额来自 `/api/v1/wallet/withdraw/info`；数据与 Web 一致 |
| H5-011 | 剧场式直播间：视频 16:9 + 聊天 + 竞猜卡 + 输入栏完整 |
| H5-012 | 点扩展 → 容器旋转 + landscape-room overlay 显示；输入栏全宽 |
| H5-013 | 沉浸式（如启用）：9:16 + 弹幕飘动 + 玻璃浮层完整 |
| H5-014 | 打赏 modal 6 档金额；选 100 → 确认 → toast"{username} 打赏了 100 💎"飘 2.4s |
| H5-019 | 进入 live tab → 吸底广告自动展示；点 × → 关闭，本会话不再展示 |
| H5-020 | 进入 schedule tab → 右下角标广告展示；点 × → 关闭 |
| H5-021 | 进入 predict tab → 气泡广告随 RAF 弹墙运动（60 px/s）；点 × → 停止运动并关闭 |
| H5-022 | 点头像 → 弹编辑 modal；上传头像（< 5MB）+ 改用户名 → 保存 → me-header 同步刷新 |
| H5-023 | 点"保存信息" → 弹 modal → 字证图 canvas 渲染 → 下载 PNG |
| H5-024 | 游客点 me tab → 显示登录引导卡；点"立即登录" → 跳 `#page-auth` |
| H5-025 | 点 TG 客服 chip → 跳 `#page-telegram` 中转页 → 点 SEND MESSAGE → 跳真 Telegram |

## 10. 测试要求

1. **设备兼容**：iOS Safari 16+、Android Chrome 110+、微信内置浏览器、QQ 浏览器
2. **分辨率**：375x812（iPhone 13/14）、390x844（iPhone 14 Pro）、412x915（Pixel）、360x800（小屏 Android）
3. **网络**：4G / WiFi / 弱网（200kbps）模拟
4. **手势**：左右滑、上下滚、下拉刷新
5. **键盘**：输入弹幕时输入栏跟随上推
6. **三种直播模式**：剧场式 → 横屏 → 沉浸式 切换流畅；横屏 overlay 接管正确
7. **三个广告位**：A/B/C 在对应 tab 自动展示 + 关闭后本会话不复现
8. **编辑信息**：头像上传 / 用户名修改 端到端流畅
9. **字证图**：canvas 渲染 + 下载 PNG 正确
10. **E2E**：登录（H5 + 字证图保存）→ 看直播 → 切横屏 → 押注 → 充值 → 编辑信息 → 保存字证图
11. **截图**：4 pane + 剧场式 / 横屏 / 沉浸式 直播间 + 各分辨率适配

## 11. 待确认问题

| 问题 | Owner | 截止时间 | 状态 |
| --- | --- | --- | --- |
| 沉浸式直播间是否默认开启（v0.3 原型默认隐藏，需手动启用） | `@kickoff/product` | 2026-05-29 | 待对齐（PRD-vs-原型 dead code 警告） |
| H5 是否需要 PWA（添加到主屏幕） | `@kickoff/product` | 2026-05-29 | 待确认 |
| 微信内置浏览器是否需要特殊适配（如 JSSDK 分享） | `@kickoff/frontend` | 2026-05-29 | 待确认 |
| 四个广告位（A/B/C/D）的运营投放频次、内容审核流程 | `@kickoff/product` | 2026-06-01 | 待对齐 |
| 字证图在 me tab 是否仅"刚登录态"可见（密码在内存中），还是永久可见（重新输密码再生成） | `@kickoff/security` | 2026-05-29 | 待对齐 |
| 头像上传是否走 CDN（七牛 / 阿里 OSS / 自建） | `@kickoff/devops` | 2026-06-01 | 待对齐 |
| **ADR-0010 支付通道最终决策（原型已锁 5 通道 + USDT 双链）** | `@kickoff/devops + product` | 2026-05-29 | **逾期阻塞 — 原型已展示但 ADR 仍是 placeholder** |
| 实时比赛数据条字段是否需要全部由 admin 手动录入，还是接第三方赛事数据 API | `@kickoff/product + devops` | 2026-06-01 | 待对齐 |
| TopBar 广告位 D 是否需要按主播 / 房间维度差异化投放 | `@kickoff/product` | 2026-06-01 | 待对齐 |
