---
id: "doc-eab6c55b2c90"
title: "Kickoff（小蓝看夜场） · 产品总览 PRD"
date: "2026-05-21T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Redis", "监控告警", "CDN", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/prd/product-prd.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/prd/product-prd.md"
sourceSha256: "cb8356a527c6cff4570f7908938992123031945a2c96460762bcb5e6127fb99d"
sourceSystem: "project-doc"
---

# Kickoff（小蓝看夜场） · 产品总览 PRD

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605210000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BRedis%2B%E7%9B%91%E6%8E%A7%E5%91%8A%E8%AD%A6-Kickoff%EF%BC%88%E5%B0%8F%E8%93%9D%E7%9C%8B%E5%A4%9C%E5%9C%BA%EF%BC%89%20%C2%B7%20%E4%BA%A7%E5%93%81%E6%80%BB%E8%A7%88%20PRD.md)

> 整理日期：2026-05-21 00:00｜日期依据：正文日期

版本：v0.1（基线，对齐 `2026.05.21评审版.html` v2.32）
日期：2026-05-22
Owner：`@kickoff/product`
状态：已确认（基线版，等待迭代细化）

---

## 1. 产品概述

### 1.1 项目背景

2026 FIFA 世界杯将于 6 月在北美三国揭幕，**32 天赛期、64 场比赛、累计 50 亿全球观众**——这是 4 年一次、对内容平台最大的流量增量窗口。

我们瞄准的是一个被传统体育平台忽视的细分市场：**亚太华人男同群体**。他们是体育消费的高粘性人群，但没有专属空间——想看球缺同好、想欢呼要在异性恋直男圈伪装自己。世界杯赛期会把这种痛点集中放大。

团队已运营成熟男同视频内容业务，拥有验证过的内容生产能力、产品矩阵、用户运营经验。我们将在**30 天内**把这些能力重组为一个世界杯专题平台，在赛事窗口期集中变现。赛事结束后，平台将转型或为现有产品矩阵导流——**世界杯不是终点，是启动战役**。

### 1.2 产品定位

Kickoff 是一个为**亚太华人男同**打造的**世界杯主题直播社交平台**。在 32 天的赛期内，用「**主播陪看 + 即时竞猜 + 身份认同**」三个核心场景，服务"想看球、想欢呼、想找到一群同好"的群体。

**商业模型：不做主播经济，做"夜场经济"** — 平台是夜店，主播是员工，用户是来度过精彩夜晚的客人。

### 1.3 Slogan

> **为你解说，陪你一夜**
> — 独属于男同胞的世界杯 —

### 1.4 品牌内涵

- 对球场，Kickoff 是**开球**的第一脚
- 对项目，Kickoff 是**启动**的第一步
- 对用户，Kickoff 是今晚不再一个人看球的那一刻——**直接开干**

---

## 2. 产品目标（赛季窗口 32 天）

| 维度 | 指标 | 目标值 |
| --- | --- | --- |
| 注册 | 累计注册用户 | ≥ 50,000 |
| 活跃 | DAU 峰值（决赛日） | ≥ 8,000 |
| 付费 | 付费用户数 | ≥ 12,000 |
| 付费 | 付费率 | ≥ 25% |
| GMV | 赛期总 GMV | ≥ 800 万 RMB |
| GMV | 高净值（L4+）用户贡献占比 | ≥ 70% |
| 主播 | 在线主播峰值 | ≥ 50 名 |
| 主播 | 平均开播时长（凌晨档） | ≥ 2.5 小时 |
| 风控 | 风控告警平均响应 | ≤ 15 分钟 |
| 风控 | 资金对账差异率 | ≤ 0.05% |

**北极星指标**：决赛日（2026-07-19）单日 GMV ≥ ¥150,000。

---

## 3. 用户角色

| 角色 | 说明 | 端 |
| --- | --- | --- |
| **C 端用户（球迷/夜场客人）** | 18+ 男性，亚太华人，世界杯期间晚间观球需求；不做等级特权 | Web / H5 |
| **主播（员工）** | 与平台签约的内容生产者，按班次开播（主推凌晨档）；按等级 S/A/B/C/未评级 | Streamer Portal（桌面端） |
| **运营管理员（OP）** | 平台日常运营、赛事配置、主播管理、内容审核、风控处置 | Admin Portal |
| **财务管理员** | 提现审核、对账、退款处置 | Admin Portal（订单中心 + 对账模块） |
| **风控管理员** | 告警处置、规则维护、账户冻结/解冻 | Admin Portal（风控告警模块） |

### 3.1 C 端用户等级体系

已下线。旧原型中的 L0-L6、等级弹幕、等级进场、等级排序、等级押注上限、客服等级分层、自定义称号和升级广播均不作为实现依据。

---

## 4. 核心流程

### 4.1 用户完整路径（注册 → 充值 → 观赛 → 互动 → 离开）

```text
打开产品(Web/H5)
   │
   ▼
是否已登录？  ── 否 ──► 登录/注册（手机号 / 邮箱 + 18+ 协议） ──┐
   │                                                        │
   是 ◄────────────────────────────────────────────────────┘
   │
   ▼
进入首页 ── 推荐流：大屏赛事 / 今日赛程 / 正在直播 / 热门竞猜 / 我的竞猜 / 赛程时间线
   │
   ├─► 点击赛事 ──► 赛事详情（未开始：开赛前竞猜 ｜ 进行中：相关直播+事件流 ｜ 已结束：MVP+结算）
   ├─► 点击直播间 ──► 进入直播间（视频+弹幕+浮动竞猜活动卡+打赏）
   ├─► 点击竞猜 ──► 竞猜中心（列表 / 我的押注 / 规则；4 状态：进行/未开始/待开奖/已开奖）
   └─► 点击头像 ──► 个人中心（钱包 / 等级 / 资金记录 / 我的竞猜）
                          │
                          ├─► 充值（微信/支付宝 → 二维码 → 状态轮询 → 到账+赠送钻石）
                          ├─► 提现（仅支付宝 → 风控审核 → 10-30 分钟到账）
                          └─► 兑换（RMB ⇄ 钻石，1 RMB = 10 💎，反向扣 20%）
```

### 4.2 主播完整路径（OBS 推流 + 运营托管）

> **变更说明（2026-05-22）**：原型评审版假设了"主播端 5 步流程 web 推流"，但 v1 改为 OBS 推流；主播**不再使用任何 web 端**，仅通过 OBS 推流。配置/监控/处置工作全部由"房间管理员"在运营后台完成。

```text
[ 主播 ] 收到运营私发的：
   推流地址 rtmp://push.kickoff.tv/live/
   推流码   sk_xxx_yyy（每房间常驻，可后台轮换）
   ↓
[ 主播 ] 在 OBS 填入设置，点"开始推流"
   ↓
[ SRS / 云直播 ] on_publish hook → 业务侧校验 stream_key → 允许 / 拒绝
   ↓
[ 房间管理员 ] 在后台"直播间监控页"看：
   实时观众 / 弹幕 / 房间标题 / 关联比赛 / 处置
   ↓
[ 主播 ] OBS 停止推流 = 下播
   ↓
[ 房间管理员 ] 在后台看本场统计
```

主播侧不需要登录任何系统、不需要设备调试页、不需要"开播/下播"按钮、不需要看实时数据。所有 web 端职能由"房间管理员"承担（详见 §5 直播间管理模块）。

### 4.3 竞猜核心流程（5 大块）

详见 [kickoff-predict 模块 PRD](modules/kickoff-predict.md)，简述：

1. **活动配置**：运营后台创建活动（基础信息 + 选项倍率 + 展示直播间）
2. **基础概念**：仅可用**竞猜币（钻石 💎）** 押注；1 RMB = 10 💎；可用微信/支付宝充值；可提现至支付宝
3. **活动状态**：未开始 / 进行中 / 待开奖 / 已开奖
4. **参与阵地**：首页热门竞猜 + 直播间浮动卡 + 竞猜 tab + 赛事详情
5. **参与查看**：竞猜 tab "我的押注" + 个人中心 "我的竞猜"

### 4.4 关键资金流向

```text
RMB（充值）  ──(1:10)──►  钻石 💎  ──(押注)──►  奖池
                            ▲                  │
                            │                  ▼
                  (反向兑换扣 20%)         开奖派彩 → 钻石
                            │                  │
                            ▼                  ▼
                          RMB         可继续押注 / 反向兑 RMB / 提现
```

---

## 5. 功能模块索引

| 模块 | PRD | 需求 ID 前缀 | 端 | Owner | 状态 |
| --- | --- | --- | --- | --- | --- |
| 登录注册 | [`modules/kickoff-auth.md`](modules/kickoff-auth.md) | AUTH | Web/H5 | `@kickoff/frontend` | 已确认 |
| 首页 | [`modules/kickoff-home.md`](modules/kickoff-home.md) | HOME | Web | `@kickoff/frontend` | 已确认 |
| 直播间 | [`modules/kickoff-live.md`](modules/kickoff-live.md) | LIVE | Web | `@kickoff/frontend` + `@kickoff/backend` | 已确认 |
| 赛程 | [`modules/kickoff-schedule.md`](modules/kickoff-schedule.md) | SCHED | Web | `@kickoff/frontend` | 已确认 |
| 赛事详情 | [`modules/kickoff-match-detail.md`](modules/kickoff-match-detail.md) | MATCH | Web | `@kickoff/frontend` | 已确认 |
| 竞猜中心 | [`modules/kickoff-predict.md`](modules/kickoff-predict.md) | PRED | Web/H5 | `@kickoff/backend` | 已确认 |
| 个人中心 | [`modules/kickoff-member.md`](modules/kickoff-member.md) | MEM | Web/H5 | `@kickoff/backend` | 已确认 |
| 钱包（充值/提现/兑换） | [`modules/kickoff-wallet.md`](modules/kickoff-wallet.md) | WALLET | Web/H5 | `@kickoff/backend` | 已确认 |
| 运营后台（含直播间管理） | [`modules/kickoff-admin.md`](modules/kickoff-admin.md) | ADM | Web | `@kickoff/admin` | 已确认 |
| H5 端 | [`modules/kickoff-h5.md`](modules/kickoff-h5.md) | H5 | H5 | `@kickoff/frontend` | 已确认 |

---

## 6. 跨模块业务规则

### 6.1 货币与资金

1. **货币模型双轨**：现金 RMB 钱包 + 钻石 💎 钱包。RMB 用于充值/提现，钻石用于押注/打赏。
2. **兑换比例**：1 RMB = 10 💎（充值时附带充值返赠：1 RMB 充值送 5 💎，本次仅作演示基线，实际比例以运营配置为准）；反向兑换 10 💎 = 0.8 RMB（扣 20% 手续费）。
3. **首充冷却**：首次充值后 **14 天**内不可提现（防套现）。
4. **提现限额**：单日 ≤ 5,000 RMB；单月 ≤ 50,000 RMB；单笔 > 1,000 RMB 或月累计 > 5,000 RMB 需 KYC 实名。
5. **提现通道**：仅支付宝（v1）。手续费 2%（平台），渠道费 0。
6. **充值通道**：微信、支付宝双通道，手续费 0。
7. **押注限额**：单次 100 - 50,000 💎；如需每日上限，只能走全局风控配置，不按等级区分。
8. **资金一致性**：充值、提现、兑换、押注、派彩、打赏均按**强一致**记账；账本表与账户余额表通过事务保证原子性。
9. **押注消费统计**：押注消费的 RMB 等价金额可用于财务/运营统计，不用于等级升级或权益。

### 6.2 权限与风控

1. **18+ 强制**：注册必须勾选"已满 18 周岁"协议；未成年禁用。
2. **押注上限不按等级**：押注限制来自活动配置、全局配置、风控和账户状态。
3. **主播单设备开播**：同一主播账号同一时刻只能在**一台设备**推流；多设备触发风控（R-108）。
4. **异常充提链路**：充值 24h 内提现 ≥ 80% 余额触发反洗钱（R-204）。
5. **单笔大额押注**：单笔押注 ≥ ¥10,000 等值触发财务复核（R-301）。
6. **弹幕违禁词**：10 分钟内房间命中 ≥ 15 次触发内容审核（R-502）。
7. **通道成功率**：15 分钟内支付通道成功率下降 ≥ 5% 触发系统告警（R-604）。
8. **新设备登录**：新设备指纹 + IP 异常触发二次验证（R-101）。
9. **审计日志**：所有资金操作、风控决策、后台敏感操作（封禁/解封/放行/驳回）必须记录审计日志，**不可删除、不可篡改**。

### 6.3 等级与升级

已下线。服务端、后台和前端不得根据历史等级字段提供弹幕、进场、押注、客服、排序或广播特权。

### 6.4 数据一致性等级

| 业务 | 一致性等级 | 说明 |
| --- | --- | --- |
| 钱包余额变动（充值/提现/兑换/押注/派彩/打赏） | 强一致 | DB 事务 + 账本表 |
| 等级累计与升级 | 强一致 | 同事务更新 |
| 直播观众数、弹幕计数 | 最终一致 | Redis 计数器 + 定时落库 |
| 主播 GMV、奖池统计 | 最终一致 | 流式聚合，分钟级延迟 |
| 风控告警触发 | 最终一致 | 异步规则引擎 |
| 对账结果 | 强一致（T+1） | 通道流水拉取 → 系统流水比对 → 差异落库 |

### 6.5 接口规范

1. 默认响应结构：
   ```json
   { "code": 0, "message": "ok", "data": {}, "trace_id": "xxx", "timestamp": 0 }
   ```
2. 路径版本：`/api/v1/`
3. 错误码：五位编码
   - `1xxxx` 系统错误（10001 参数错误、10500 服务异常）
   - `2xxxx` 业务错误（20101 余额不足、20102 押注超限、20103 已封盘）
   - `3xxxx` 权限错误（30001 未登录、30002 未实名、30003 未达等级）
4. 资金类写接口（充值/提现/兑换/押注/派彩/打赏）必须带**幂等键**（idempotency-key），重复请求返回首次结果。

---

## 7. 非功能需求

### 7.1 性能 / 容量（QPS 预估）

| 场景 | 峰值 QPS | P99 延迟 | 备注 |
| --- | --- | --- | --- |
| 首页加载（聚合接口） | 2,000 | < 300ms | 缓存+CDN |
| 赛程接口（含 64 场） | 500 | < 200ms | 全量缓存 |
| 直播间进入 | 1,500 | < 500ms | 含拉流地址 |
| 弹幕推送（WebSocket） | 在线 8,000 并发 | < 100ms | 长连接 |
| 押注下单 | 800 | < 500ms | 强一致写 |
| 充值发起 | 300 | < 800ms | 含通道调用 |
| 提现申请 | 50 | < 800ms | 同步风控 |

### 7.2 可用性

- 在线服务 SLA：**99.9%**（赛期窗口期 32 天 < 43 分钟不可用）
- 关键接口（押注、充值、提现、登录）熔断降级方案完备
- 直播推/拉流：依赖第三方 CDN（待选型，见 §9）

### 7.3 数据规模（赛期 32 天）

| 数据 | 规模 |
| --- | --- |
| 用户表 | ~50,000 行 |
| 直播间表 | ~3,000 行（48 主播 × 64 场） |
| 比赛表 | 64 行（写死） |
| 押注订单表 | ~50 万行（按 5,672/日 × 32 估算） |
| 充值订单表 | ~10 万行 |
| 提现订单表 | ~5,000 行 |
| 资金账本表 | ~200 万行（每个资金动作一条） |
| 弹幕记录表 | ~5,000 万行（每场 ~50 万 × 64） |
| 审计日志表 | ~50 万行 |

**分表策略**：弹幕记录表按 `room_id` 哈希分 16 张表；账本表按月分表（赛期跨 2 个月）。其他单表即可。

### 7.4 缓存策略

| 数据 | Key 设计 | TTL | 失效触发 |
| --- | --- | --- | --- |
| 用户基础信息 | `user:profile:{uid}` | 1h | 资料修改 |
| 用户余额 | `user:wallet:{uid}` | 不缓存 | 强一致直读 DB |
| 用户等级 | `user:level:{uid}` | 1h | 升级时主动失效 |
| 赛程全量 | `schedule:all` | 5m | 运营修改 |
| 单场赛事 | `match:{match_id}` | 30s | 运营修改 / 状态变化 |
| 直播间列表 | `live:list` | 10s | 开播/下播 |
| 单直播间 | `live:room:{room_id}` | 30s | 状态变化 |
| 竞猜活动列表 | `predict:active` | 10s | 开盘/封盘/开奖 |
| 在线观众数 | `live:viewers:{room_id}` | 5s | 实时增量 |

**穿透/击穿/雪崩对策**：
- 穿透：空结果缓存 30s + 布隆过滤器（用户 ID / 房间 ID）
- 击穿：热点 key 使用单飞（singleflight）回源
- 雪崩：TTL 随机化（基础 TTL ± 20%）

### 7.5 安全

1. **认证**：JWT（access 2h，refresh 30d），refresh token 单设备绑定
2. **传输**：全站 TLS 1.2+
3. **密码**：Bcrypt cost=12
4. **敏感字段**：身份证、银行卡号 AES-256（KMS 托管密钥）
5. **限流**：滑动窗口，按 IP + UID 双维度
6. **CSRF**：Web 端 SameSite=Strict + 双提交 token
7. **XSS**：弹幕内容 HTML escape；用户输入字段限制字符集
8. **SQL 注入**：全部参数化查询

### 7.6 可观测性

1. **日志**：zap + trace_id；所有资金类、风控类操作 INFO 以上必落
2. **指标**：Prometheus；核心 SLI：QPS、P99 延迟、错误率、资金对账差异
3. **追踪**：Jaeger（OpenTelemetry）；登录、押注、充值、提现全链路串
4. **告警**：核心指标偏离基线 → Telegram bot + 邮件(见 `docs/operations/logging-and-alerting.md`)
5. **业务大盘**：今日 GMV、在线主播、活跃用户、押注笔数（4 KPI 实时）

---

## 8. 需求追踪

需求 ID 总账见：

- 人读版：[`docs/prd/requirements.md`](requirements.md)
- 机读版（validator 输入）：[`docs/prd/requirements.index.json`](requirements.index.json)
- Schema：[`docs/prd/requirements.schema.json`](requirements.schema.json)

需求 ID 命名规则：`<MODULE-PREFIX>-<3 位数字>`，例如 `PRED-001`、`WALLET-003`、`ADM-007`。

---

## 9. 待确认问题

| 问题 | Owner | 截止时间 | 状态 |
| --- | --- | --- | --- |
| 直播推/拉流 CDN 选型（腾讯云 / 阿里云 / 火山引擎） | `@kickoff/tech` | 2026-05-29 | 待确认 |
| 视频鉴黄方案（自研模型 / 第三方阿里云内容安全） | `@kickoff/security` | 2026-05-29 | 待确认 |
| 是否需要 KYC 服务商（提现 > 1000 强制实名） | `@kickoff/security` | 2026-05-25 | 待确认 |
| 短信通道供应商（注册验证码） | `@kickoff/devops` | 2026-05-25 | 待确认 |
| 是否上线 H5 沉浸式直播间（v3.54 设计已存在，是否首版交付） | `@kickoff/product` | 2026-05-25 | 待确认 |
| 反向兑换 20% 手续费是否合规（涉博彩边界） | `@kickoff/security` | 2026-05-29 | 待确认 |
| 主播薪资结算逻辑（按 GMV 分成 / 固定 / 混合） | `@kickoff/product` | 2026-06-01 | 待确认 |
| 国际化支持（赛期主战场华人，是否需简繁双语 + 英语兜底） | `@kickoff/product` | 2026-06-01 | 待确认 |
| 客户端是否提供原生 App（仅 Web + H5 是否足够） | `@kickoff/product` | 2026-06-01 | 待确认 |

---

## 10. 埋点

埋点统一走 `track(event, properties)`，事件命名 `<domain>_<action>_<object>`，全部小写下划线。

| 模块 | 事件 | 属性 | 触发时机 |
| --- | --- | --- | --- |
| 登录 | `auth_login_success` | method (phone/email), is_first | 登录成功 |
| 登录 | `auth_register_success` | method, ref_channel | 注册成功 |
| 首页 | `home_banner_click` | match_id, slide_idx | 大屏 Banner 点击 |
| 首页 | `home_match_click` | match_id, status | 今日赛程卡片点击 |
| 直播间 | `live_room_enter` | room_id, streamer_id, match_id | 进入直播间 |
| 直播间 | `live_tip_send` | room_id, streamer_id, amount, combo | 打赏 |
| 直播间 | `live_danmaku_send` | room_id, length, color | 发弹幕 |
| 竞猜 | `predict_open_modal` | activity_id, source (home/live/predict-tab) | 唤起押注弹窗 |
| 竞猜 | `predict_bet_submit` | activity_id, option, amount, rate | 提交押注 |
| 竞猜 | `predict_bet_success` | bet_id, activity_id, amount | 押注成功 |
| 竞猜 | `predict_payout` | bet_id, result (won/lost), profit | 结算到账 |
| 钱包 | `wallet_recharge_init` | amount, channel | 充值发起 |
| 钱包 | `wallet_recharge_success` | order_no, amount, bonus_diamond | 充值到账 |
| 钱包 | `wallet_withdraw_submit` | amount, channel | 提现申请 |
| 钱包 | `wallet_exchange` | direction (fwd/rev), from_amount, to_amount | 兑换 |
| 等级 | `level_up` | from_level, to_level, broadcast_scope | 升级 |
| 主播 | `streamer_go_live` | streamer_id, room_id, match_id | 开播 |
| 主播 | `streamer_end_live` | streamer_id, room_id, duration_sec, viewers_peak | 下播 |

---

## 11. 版本来源与变更记录

- 原型：`2026.05.21评审版.html`（snapshots/v2.32.html）
- 评审日期：2026-05-21
- 本 PRD 基线版本：v0.1（2026-05-22）
- 后续迭代：建议每周 bump minor，每次有意义改动同步更新本 PRD 与模块 PRD
