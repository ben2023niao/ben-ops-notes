---
id: "doc-2bdd986d16d6"
title: "Kickoff 个人中心 模块 PRD"
date: "2026-05-23T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "CDN", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/kickoff-member.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/kickoff-member.md"
sourceSha256: "700766804f94efd2a9aaffddad85025b7240b81a18f79583363194a26264f6c3"
sourceSystem: "project-doc"
---

# Kickoff 个人中心 模块 PRD

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/kickoff-member.md`

> 整理日期：2026-05-23 00:00｜日期依据：正文日期

模块：`kickoff-member`
端：Web / H5
Owner：`@kickoff/backend` + `@kickoff/frontend`
状态：已确认（v0.3：钱包卡 2 项 + 编辑信息 + 字证图 + TG 客服 + 去退出登录）
对应原型页面：`#page-member`

> **v0.3 变更（2026-05-23 对齐原型 v4.45）**：
> 1. **钱包卡收敛口径**：v0.3 H5 个人中心主余额按**钻石钱包**展示；`GET /api/v1/me/profile.wallet` 只暴露 `diamond_balance / diamond_frozen / diamond_withdrawable`，不暴露 RMB 余额 / 冻结 / 可提现。卡片里的累计充值使用 `cumulative_recharge_rmb`；提现弹窗里的 RMB 可提现、限额和冻结原因统一走 `GET /api/v1/wallet/withdraw/info`。
> 2. **MEM-010 退出登录废弃**（v4.26）：原型 demo 阶段移除退出登录按钮，正式上线版退出入口建议放在设置页（v2 交付）。
> 3. **客服入口不分级**（v3.69）：原 5 档客服通道废弃，统一跳 `#page-telegram` 中转页 → 真 Telegram。
> 4. **新增账户状态字段**：`正常 / 冻结`；冻结时禁止提现 + 显示客服联系方式。
> 5. **新增"编辑个人信息" modal**（v4.17 / v4.20）：点头像 → 弹 modal → 改头像（相册上传）+ 改用户名。
> 6. **注册账号 vs 用户名拆分**（v4.21）：UID 只读 + 注册账号只读 + 用户名可改；首版用户名 = 注册账号。
> 7. **新增"保存账号信息" chip**（v3.84）：me-header 旁 chip → 弹字证图 modal → 下载 PNG（与 [`kickoff-auth.md`](kickoff-auth.md) §4.5 同规格）。

## 1. 模块目标

个人中心是用户的"账户管理 + 价值感知"主页，承担：

1. **资产展示**：钻石主余额 + 累计充值（v0.3 简化为 2 段式）；提现弹窗单独展示 RMB 可提现额
2. **资产展示收敛**：不展示等级、升级进度或等级权益入口
3. **资金追溯**：充值记录 + 提现记录，让用户随时核查资金流水
4. **押注回顾**：竞猜概览（总场数/胜率/累计收益）+ 三态明细（进行中/待开奖/已开奖）
5. **等级特权下线**：不交付等级特权弹窗，不按旧原型展示 L0-L6 权益
6. **账号自管理**：编辑头像 / 用户名、保存账号字证图、联系 TG 客服

## 2. 用户角色

| 角色 | 说明 |
| --- | --- |
| 已登录用户 | 完整资产 + 流水 + 押注 |
| 未登录用户 | 不可访问，直接跳登录 |

## 3. 需求列表

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| MEM-001 | 用户信息卡（头像 + 用户名 + UID） | P0 | 已确认 | 不展示等级徽章；点头像唤起编辑 modal |
| MEM-002 | 升级进度条（距下一级差额） | P0 | 已取消 | 等级体系已下线，不交付 |
| MEM-003 | 钻石钱包卡（钻石主余额 / 累计充值 + 充值/提现按钮） | P0 | 已确认 | `me/profile.wallet` 只暴露钻石字段；提现 RMB 可提现额由 `/wallet/withdraw/info` 提供；按钮跳对应 modal |
| MEM-004 | 资金记录（充值/提现 2 个 tab） | P0 | 已确认 | 时间/金额/方式/状态/订单号 |
| MEM-005 | 资金记录"查看全部" | P1 | 已确认 | 分页查询全量 |
| MEM-006 | 竞猜概览（竞猜中/已结束/胜率/累计收益 4 项） | P0 | 已确认 | 与押注表统计一致 |
| MEM-007 | 我的竞猜明细（进行中/待开奖/已开奖 3 tab） | P0 | 已确认 | 与 kickoff-predict §4 状态一致 |
| MEM-008 | 等级特权弹窗（七级对比表） | P0 | 已取消 | 等级特权已下线，不交付 |
| MEM-009 | 客服入口（统一跳 TG 中转页） | P0 | 已确认 | v0.3 去等级分级；点击 → `#page-telegram` |
| MEM-011 | 账户状态展示（正常 / 冻结） | P0 | 已确认 | 冻结状态在 me-header 显示红色 chip 提示 |
| MEM-012 | 编辑个人信息 modal（头像 + 用户名） | P0 | 已确认 | 点头像唤起；详见 [`kickoff-h5.md`](kickoff-h5.md) 同名需求 |
| MEM-013 | "保存账号信息" chip → 字证图 PNG | P0 | 已确认 | canvas 渲染同登录模块字证图规格（详见 kickoff-auth.md §4.5） |

> 已废弃：
> - **MEM-010 退出登录**：v0.3 移除（v4.26），正式上线版若需退出建议放设置页（v2 交付）。

## 4. 业务规则

### 4.1 钱包卡数据口径（v0.3 H5 简化为 2 项）

| 字段 | 定义 | 数据来源 |
| --- | --- | --- |
| 可用钻石 | `wallet.diamond_withdrawable`，口径为 `diamond_balance - diamond_frozen` | `GET /api/v1/me/profile` |
| 累计充值 | 用户历史累计成功充值 RMB 总额（不含手续费） | `user_recharge_total.amount_sum` |

> v0.3 删除字段：原"RMB 余额（含冻结）"、"RMB 冻结金额"、"累计消费"。
> - **RMB 可提现 / 冻结 / 限额** 单独在提现页由 `GET /api/v1/wallet/withdraw/info` 返回，不进 `me/profile.wallet`。
> - **冻结钻石**用于押注 / 风控占用，`me/profile.wallet` 可返回 `diamond_frozen` 供卡面或后续明细使用。
> - **累计消费**不再用于等级进度条；如保留底层统计，仅作财务/运营分析。

### 4.2 升级进度条

已取消。个人中心不展示等级、等级名称、升级进度、下一级门槛或等级权益入口。

### 4.3 资金记录

**充值记录字段**：时间、金额、支付方式（微信/支付宝）、状态（已到账/超时失败/退款）、订单号 `RCH<YYYYMMDD><HHMM>`

**提现记录字段**：时间、金额、收款方式（支付宝/银行卡 *末四位）、状态（已到账/处理中/驳回）、订单号 `WDR<YYYYMMDD><HHMM>`

显示规则：

- 默认显示最近 30 天，最多 20 条；超过显示"查看全部"
- 失败/驳回行：金额前缀"—"，状态红色
- 处理中：状态黄色 "⏳ 处理中"

### 4.4 竞猜概览

| 字段 | 计算口径 |
| --- | --- |
| 竞猜中 | `predict_bet` 中 status IN (进行中, 待开奖) 的活动数（去重） |
| 已结束 | status = 已开奖 的活动数（去重） |
| 胜率 | 已开奖 中命中场数 / 已开奖总场数（按活动去重）× 100% |
| 累计收益 | Σ(payout - bet_amount) 跨全部已开奖订单（钻石单位） |

### 4.5 等级特权弹窗

已取消。旧原型中的七级特权对比表、当前等级高亮、升级广播和等级权益说明均不交付。

### 4.6 客服入口（v0.3 简化）

| 范围 | 客服通道 | 入口 |
| --- | --- | --- |
| 全部用户 | Telegram 客服群 / 私聊 | me-header 旁 TG chip → 跳 `#page-telegram` 中转页 → 点 SEND MESSAGE → 跳真 Telegram |

> v0.3 删除原 5 档（L0-L2 工单 / L3 加急 / L4 专属 / L5 VIP / L6 一对一）：原型 v3.69 已统一为 TG 单通道。
> 不再展示等级特权对照表。

### 4.7 账户状态

| status | 含义 | 用户侧表现 |
| --- | --- | --- |
| `active` | 正常 | 默认状态，无特殊提示 |
| `frozen` | 冻结（违规 / 风控 / 异常充提） | me-header 红色 chip"账户已冻结" + 禁止提现按钮 + 弹窗引导联系客服 |

冻结状态由后台 [`kickoff-admin.md`](kickoff-admin.md) 风控模块设置；用户端只读。

### 4.8 编辑个人信息 modal

1. **触发**：点 me-header 头像。
2. **可改**：
   - **头像**：96px 圆形大预览 + 相机图标 → 调起 `<input type="file" accept="image/*">` → multipart 上传 `file` 到 `POST /api/v1/me/avatar`
   - **用户名**：text input，maxlength 20，允许中英文+数字+常用符号
3. **只读**：
   - **UID**：系统分配，永久
   - **注册账号**：注册时设定，登录凭证，永久
4. **保存**：调用对应接口 → 关 modal → me-header 同步刷新
5. **图片限制**：JPG / PNG / WebP；≤ 5 MB（客户端阻塞）；服务端裁剪 200×200。

### 4.9 保存账号信息字证图

1. **触发**：me-header 旁"保存信息" chip。
2. **行为**：弹 modal → canvas 渲染 PNG → "保存到本地"按钮 → 下载 PNG。
3. **规格**：与 [`kickoff-auth.md`](kickoff-auth.md) §4.5 字证图**完全一致**（760 × 600，LOGO + 产品名 + 账号 + 密码 + 4 警示 + 时间戳）。
4. **安全约束**：
   - 密码必须在内存中可读（刚登录态、refresh 后），否则 chip 灰态 + 提示"请重新登录后再保存"
   - 密码**不调用任何后端接口**取明文（password_hash 永远不解密）
5. **文件名**：`小蓝看夜场-账号信息-YYYYMMDD-HHMM.png`。

### 4.7 数据刷新

1. 进入页面拉取一次。
2. 资金变动 → WS 推送 → 钱包卡 + 资金记录刷新。
3. 押注状态变化（开奖）→ WS 推送 → 概览 + 我的竞猜 tab 刷新。

## 5. 边界与异常

| 场景 | 系统行为 | 提示/状态 |
| --- | --- | --- |
| 用户未消费过 | 累计充值 / 押注统计为 0 | 显示常规空状态 |
| 无充值/提现/押注记录 | 显示空状态 | "暂无记录" |
| 首充 14 天内 | 可提现 = 0 + 提示 | "首充 14 天内不可提现，约 2026-07-24 可申请" |
| 提现处于风控中 | 显示"风控中" | "审核中，预计 24h 内结果" |
| WS 断开 | 降级轮询 | 静默处理 |
| 账户冻结 | 提现按钮置灰 | "账户已冻结，请联系客服 @kickoff_vip" + 跳 TG 中转页 |
| 字证图 chip：密码不在内存 | chip 灰态 | "请重新登录后再保存账号信息" |
| 头像上传超过 5 MB | 阻止 + 提示 | "图片不能超过 5 MB" |
| 头像格式非图片 | 阻止 + 提示 | "请选择 JPG/PNG/WebP 图片" |
| 用户名超过 20 字 / 含特殊字符 | 阻止 + 提示 | "用户名 2-20 字，不允许特殊符号" |

## 6. 权限与风控

1. 需登录。
2. 仅本人可看本人数据；后台管理员通过 Admin Portal 单独查（不复用此接口）。
3. 客户端不展示其他用户的余额。
4. 审计日志：登出 → 写审计；其他动作（充值/提现/押注）由对应模块写。

## 7. 数据对象

| 对象 | Owner | 说明 |
| --- | --- | --- |
| `user` | `services/go-app` | 用户主表 |
| `user_wallet` | `services/go-app` | 钱包（RMB + 钻石） |
| `user_consume_total` | `services/go-app` | 历史累计消费统计；不用于等级权益 |
| `recharge_order` | `services/go-app` | 充值订单 |
| `withdraw_order` | `services/go-app` | 提现订单 |
| `predict_bet` | `services/go-app` | 押注订单（来源 kickoff-predict 模块） |

## 8. API/事件契约

| 需求 ID | 契约 | Owner Service | 状态 |
| --- | --- | --- | --- |
| MEM-001~003/011 | `GET /api/v1/me/profile` 返回 `{uid, account, username, avatar, status, wallet}` | `services/go-app` | 待设计 |
| MEM-004 | `GET /api/v1/me/recharge-records?limit=20` | `services/go-app` | 待设计 |
| MEM-004 | `GET /api/v1/me/withdraw-records?limit=20` | `services/go-app` | 待设计 |
| MEM-005 | `GET /api/v1/me/fund-records?type=recharge|withdraw&page=&size=` | `services/go-app` | 待设计 |
| MEM-006/007 | `GET /api/v1/me/predict-summary` | `services/go-app` | 待设计 |
| MEM-007 | `GET /api/v1/me/predict-bets?status=` | `services/go-app` | 待设计 |
| MEM-008 | 不涉及接口 | `services/go-app` | 已取消 |
| MEM-012 | `POST /api/v1/me/avatar`（multipart `file`） | `services/go-app` | 已实现 |
| MEM-012 | `PATCH /api/v1/me/username` body `{username}` | `services/go-app` | 待设计 |
| MEM-013 | （纯前端 canvas，无后端接口） | `apps/web` + `apps/h5` | 待对齐 |

> `POST /api/v1/auth/logout` v0.3 在本模块不再调用（MEM-010 已废弃）；接口本身保留供未来设置页使用。

## 9. 验收标准

| 需求 ID | 验收标准 |
| --- | --- |
| MEM-001 | 用户名、UID 正确；不展示等级徽章；点头像 → 弹编辑 modal |
| MEM-002 | 不展示升级进度条 |
| MEM-003 | 钱包卡显示钻石主余额和累计充值；提现 modal 展示 RMB 可提现额；按钮跳充值 / 提现 modal |
| MEM-004 | 充值/提现 tab 切换正常；订单号格式正确；失败行金额前缀 "—" |
| MEM-006 | 4 项统计与押注表实际数据一致；累计收益可为负 |
| MEM-007 | 三 tab 数据与 kickoff-predict 模块"我的押注" 一致 |
| MEM-008 | 不展示等级特权弹窗入口 |
| MEM-009 | 点 TG chip → 跳 `#page-telegram` → SEND MESSAGE → 跳真 Telegram |
| MEM-011 | frozen 状态 → me-header 显示红色 chip；提现按钮置灰 |
| MEM-012 | 点头像 → 弹 modal；上传新头像（< 5MB）+ 改用户名 → 保存 → me-header 同步 |
| MEM-013 | 点"保存信息" → 弹 modal → 显示字证图预览 → 点保存下载 PNG |

## 10. 测试要求

1. **单元测试**：胜率统计、用户名长度 / 字符校验、头像格式 / 大小校验
2. **集成测试**：押注/充值变更后接口数据一致性；头像上传 + 用户名修改端到端
3. **前端单测**：字证图 canvas 渲染（含特殊字符密码）
4. **E2E**：登录 → 个人中心 → 编辑头像 + 用户名 → 保存字证图 → 充值 → 押注 → 回个人中心查看累计变化 → 点 TG chip 跳中转页
5. **截图**：完整个人中心、编辑信息 modal、字证图 modal、TG 中转页、冻结状态、各状态空态

## 11. 待确认问题

| 问题 | Owner | 截止时间 | 状态 |
| --- | --- | --- | --- |
| 是否单独展示钻石钱包卡 | `@kickoff/product` | 2026-05-26 | 已确认：v0.3 H5 个人中心展示钻石钱包，RMB 提现信息走提现页接口 |
| 是否展示打赏总额 / 主播打赏排行 | `@kickoff/product` | 2026-05-29 | 待确认 |
| TG 客服 v1 是否自建机器人 + 工单系统（vs 纯人工） | `@kickoff/devops` | 2026-05-29 | 待对齐 |
| 头像上传是否走 CDN（七牛 / 阿里 OSS / 自建） | `@kickoff/devops` | 2026-06-01 | 待对齐 |
| 用户名是否允许 emoji（v0.3 当前禁用） | `@kickoff/product` | 2026-05-29 | 待对齐 |
| 字证图 chip 是否每次登录都强提示一次（保护遗忘用户） | `@kickoff/product` | 2026-06-01 | 待对齐 |
| 退出登录 v2 设置页是否交付（v0.3 已删 me tab 入口） | `@kickoff/product` | 2026-06-15 | 待对齐 |
