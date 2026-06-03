---
id: "doc-6ecf7cdeff18"
title: "Kickoff 运营后台（Admin Portal） 模块 PRD · kickoff-admin"
date: "2026-06-04T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Redis", "监控告警", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/kickoff-admin.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/kickoff-admin.md"
sourceSha256: "6f8b2716f3589181c3bbc4f2d10c7cc00894cd5d2137bdf8cc848ad7f0890436"
sourceSystem: "project-doc"
---

# Kickoff 运营后台（Admin Portal） 模块 PRD · kickoff-admin

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/kickoff-admin.md`

> 整理日期：2026-06-04 00:00｜日期依据：正文日期

模块：`kickoff-admin`
端：Web（桌面端）
Owner：`@kickoff/admin` + `@kickoff/backend`
状态：已确认
对应原型页面：`#page-admin`

## 1. 模块目标

运营后台是 Kickoff 的**控制中枢**，让运营、房间管理员、风控、财务在赛期窗口内高效处置一切异常。当前后台覆盖从看板到审核的核心运营场景：

1. 总览：数据看板（GMV / 在线主播 / 活跃用户 / 押注笔数 + 7 日 GMV 走势 + 事件流 + 实时在线 + 时段分布）
2. 业务：赛事 & 赔率管理（含比赛比分快速录入） / 主播管理 / **直播间管理（新模块）** / 用户管理 / 订单中心
3. 财务 & 合规：通道对账 / 内容审核

> **v0.5 变更（2026-06-04）**：
> - 竞猜功能已下线，依赖竞猜押注规则的"风控告警"模块同步下线。
> - 财务管理不再展示"押注订单"菜单；保留充值、提现、支付回调、支付通道等资金运营入口。
> - 后台不再展示风控告警菜单，不再暴露 `/api/v1/admin/risk/*` 接口。
> - `risk_admin` 角色保留用于用户冻结、解冻、重置密码等敏感操作授权，不代表恢复告警中心。

> **v0.6 上线安全变更（2026-06-09）**：
> - 后台登录页不展示开发账号、默认密码、角色快捷填充等上线前辅助信息。
> - 后台登录必须先获取图形验证码，提交账号、密码、验证码 ID 与验证码文本；验证码 2 分钟过期且一次性消费。

> **v0.2 变更（2026-05-22）**：
> - 新增"直播间管理"模块（承接原"主播端"职能）
> - 赛事 & 赔率管理 v1 必上（修订原 PRD 的"v2 占位"）
> - 内容审核 v1 必上（同上）
> - "主播管理"简化为"签约信息 + 推流凭据 + 关联房间"

## 2. 用户角色

| 角色 | 权限范围 |
| --- | --- |
| 超级管理员（super） | 全部模块；创建主播 / 创建房间 / 分配房间管理员 / 资金审批 |
| 运营管理员（ops） | 看板 + 主播 + 用户 + 订单（只读） + 内容审核 + 赛事赔率 |
| **房间管理员（room_admin）** | **仅被分配的房间**：监控弹幕 / 看实时观众 / 改房间标题 / 切关联比赛 / 查看推流凭据 / 强制关播；多个房间可同时分配（多对多） |
| 财务管理员（finance） | 订单 + 对账 + 提现审核 |
| 风控管理员（risk） | 用户冻结 / 解冻 / 重置密码等敏感操作审查；风控告警中心已下线 |
| 内容审核员（moderator） | 内容审核（举报 / 弹幕违规 / 敏感词词库 / 房间封禁） |

后台所有用户独立账号体系，不复用 C 端 `user` 表。
房间管理员可以同时管理多个房间（**多对多关系**，通过 `admin_room_assignments` 表关联），首版 UI 仅提供基本"分配/取消分配"操作，复杂排班 v2 再做。

## 3. 需求列表

### 3.1 通用框架

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| ADM-001 | 侧边栏导航（总览 / 业务 / 财务合规） | P0 | 已确认 | 不再展示风控告警入口，徽章显示待处理数 |
| ADM-002 | 顶部条（标题 + 面包屑 + ENV 标签 + 全局搜索 + 通知 + 时间） | P0 | 已确认 | PROD 红色标签醒目；通知未读小红点 |
| ADM-003 | 后台账号系统 + RBAC | P0 | 已确认 | 超管可新增/启用/禁用后台管理员账号；5 种角色权限隔离；登录页不展示开发账号，登录需图形验证码 |
| ADM-004 | 后台操作审计（所有写操作） | P0 | 已确认 | 谁、何时、对什么、做了什么 全记录 |
| ADM-005 | 侧栏折叠 | P1 | 已确认 | 收起后只显示 icon |
| ADM-006 | 基础配置（C 端页脚联系信息） | P0 | 已确认 | 系统配置 / 基础维护 `home.support_email`、`home.business_email`、`home.primary_domain`；C 端通过 `GET /api/v1/config/system` 的 `site` 节点展示客服邮箱、商务合作、主域名 |
| ADM-930 | 数据初始化 / 2026 世界杯默认数据导入 | P0 | 已确认 | super_admin 可上传 2026 世界杯赛程 Excel，先预览清理表和导入摘要，再输入确认短语执行；支持只重导世界杯默认数据、上线前全量清测试数据两种范围；执行写审计 |

### 3.1' 客服接待

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| SUPPORT-001 | 客服接待 | P0 | 已确认 | C 端可登录/匿名创建客服会话并发送文本/图片；后台客服接待列表每 5 秒刷新；OPEN 会话超过 5 分钟没有任何新消息自动关闭并追加系统消息，后续用户/客服发消息可重新打开 |

### 3.2 数据看板（① Dashboard）

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| ADM-101 | 4 大 KPI 卡（今日 GMV / 在线主播 / 活跃用户 / 今日押注） | P0 | 已确认 | 实时；同/环比 |
| ADM-102 | 近 7 日 GMV 走势图（折线 + 面积） | P0 | 已确认 | 单位万元；每日 24:00 统计 |
| ADM-103 | 近 24 小时事件流（warn/ok/info 三色） | P0 | 已确认 | 订单失败、关键操作、系统提示 |
| ADM-104 | TOP 主播表（按今日 GMV） | P0 | 已确认 | 主播 / 时长 / 观看 / GMV |

### 3.3 赛事 & 赔率管理（② Match - **v1 必上**）

> v0.2 修订：原 PRD 标记 v2 占位，v0.2 改为 v1 必上（实际运营依赖此模块录入比分 + 创建竞猜活动 + 触发结算）。

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| ADM-201 | 赛事 CRUD | P0 | 已确认 | 64 场预录入 / 单场编辑 / 状态切换 |
| ADM-202 | **比赛比分快速录入** | P0 | 已确认 | 进行中比赛列表 + 双方比分 +/- 按钮 + 状态切换；手机端友好 |
| ADM-203 | 录入比赛结果 + MVP（已结束后） | P0 | 已确认 | 最终比分锁定 + MVP 选填 |
| ADM-204 | 进球事件录入 | P0 | 已确认 | 时间 + 球队 + 球员 + 比分变化（运营观看比赛随手录入） |
| ADM-211 | 创建竞猜活动 | P0 | 已确认 | 关联比赛 + 市场类型 + 选项 + 初始赔率 + 展示直播间 + 开盘/封盘时间 |
| ADM-212 | 编辑活动（赔率/选项） | P0 | 已确认 | 锁盘前可改，锁盘后只能退单 |
| ADM-213 | 手动锁盘 / 解盘 | P0 | 已确认 | 锁盘后禁押注；写审计 |
| ADM-214 | 手动触发结算 | P0 | 已确认 | 输入结果选项 → worker-settle 批处理 |
| ADM-215 | 退单（活动级） | P1 | 已确认 | 全部押注用户钻石回退 + 审计 |
| ADM-216 | 人工干预日志 | P0 | 已确认 | 所有赔率修改 / 锁盘 / 退单 完整审计 |

### 3.3' 直播间管理（③' LiveRoom - **新模块 v0.2**）

> v0.2 新增。承接原 PRD"主播端"职能。主播仅用 OBS 推流，所有 web 端职能由"房间管理员"在此模块承担。
> 后台房间详情不是另做一套 C 端直播间，而是复用同一批房间、弹幕、观众、打赏和会话数据，提供 admin API + admin 权限 + 审计约束下的控场面板。

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| ADM-901 | 直播间列表 | P0 | 已确认 | 列：房间 ID / 关联主播 / 关联比赛 / 状态（LIVE/PREPARING/ENDED）/ 首页 Banner 推荐 / 分配的管理员 / 推流码状态 / 操作 |
| ADM-902 | 创建直播间（手动 / 关联主播） | P0 | 已确认 | 超管创建房间 → 选主播 → 生成推流码 → 房间为"PREPARING" |
| ADM-903 | 关联/切换房间归属主播 | P0 | 已确认 | 一房间一主播；切换写审计 |
| ADM-904 | 房间详情（含控场面板） | P0 | 已确认 | 一屏看完：标题 / 比赛 / 主播 / 实时观众 / 弹幕滚动 / 推流凭据 / 控场操作 |
| ADM-905 | 改房间标题 | P0 | 已确认 | 房间管理员 + 超管可改；写审计 |
| ADM-906 | 切换关联比赛 | P0 | 已确认 | 切换前需弹窗确认（影响竞猜活动展示） |
| ADM-907 | 实时观众列表 | P0 | 已确认 | 公共直播 WS 登记登录观众和游客连接到 Redis 在线集合；后台每 5s 刷新，在线人数包含游客；登录用户返回用户、进入时间、累计打赏钻石和 `spender_tier` 运营标签，游客以“游客”占位展示；不按等级标记 |
| ADM-908 | 实时弹幕监控 | P0 | 已确认 | `GET /admin/rooms/{id}/danmaku` 拉最近弹幕，`/ws/v1/admin/rooms/{id}/danmaku` 实时订阅；仅房间授权管理员可连；不按等级置顶 |
| ADM-909 | 删除弹幕 + 禁言用户（房间级） | P0 | 已确认 | 后台弹幕表可直接删除 / 禁言；删除推全房间并写审计；禁言写房间级禁言表和审计 |
| ADM-910 | 查看推流凭据（脱敏 + 一次性展示） | P0 | 已确认 | 默认掩码；点击"查看完整"→ 二次确认 + 短暂展示 + 审计 |
| ADM-911 | 轮换推流凭据 | P0 | 已确认 | 一键轮换；旧码立即失效；写审计 |
| ADM-912 | 强制关播 | P0 | 已确认 | 立即关闭推流 + WS 通知观众 + 写审计 |
| ADM-913 | 联系主播（展示 TG / 电话 + 复制按钮） | P0 | 已确认 | 联系方式存 streamers 表；展示需 admin role 权限 + 审计 |
| ADM-914 | 房间封禁 / 解封 | P0 | 已确认 | 封禁后该房间不可推流；超管权限 |
| ADM-915 | 分配 / 取消分配房间管理员 | P0 | 已确认 | 超管在房间详情添加/移除房间管理员；多对多 |
| ADM-916 | 我管理的房间（房间管理员视角） | P0 | 已确认 | room_admin 角色登录后首页直接显示其负责的房间卡 |
| ADM-917 | 房间会话历史 | P1 | 已确认 | 列出该房间历次开播 session + 统计 |
| ADM-918 | 房间维度统计（GMV / 观看 / 弹幕 / 打赏） | P0 | 已确认 | 当日 + 累计 |
| ADM-920 | LSJ 资源管理 | P0 | 已确认 | 独立菜单只读查询 LSJ 上游赛事和线路；支持类型、状态、画质、关键词筛选和 m3u8 预览；赛事 LSJ 绑定选择器支持按画质筛选并选择对应线路 |

### 3.4 主播管理（④ Streamers - 简化）

> v0.2 简化：主播无 web 端，"主播管理"只管签约信息、关联房间、联系方式、状态、推流凭据。

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| ADM-301 | 主播列表 | P0 | 已确认 | 列：ID / 真实姓名 / 显示名 / 等级（S/A/B/C/未评级） / 状态 / 关联房间 / 累计 GMV / 联系方式（脱敏） |
| ADM-302 | 状态筛选（在班 / 休息 / 封禁 / 待审） | P0 | 已确认 | chip 切换 |
| ADM-303 | 新增主播签约 | P0 | 已确认 | 表单：姓名 / 显示名 / 等级 / 签约赛季 / TG / 电话；保存后**不自动创建房间**（房间手动建） |
| ADM-304 | 主播详情 | P0 | 已确认 | 签约信息 + 关联的房间列表 + 累计 GMV + 历次开播 session + 审计 |
| ADM-306 | 封禁/解封主播 | P0 | 已确认 | 封禁后所有关联房间不可推流 |
| ADM-308 | 主播待审通过/驳回（签约审核） | P0 | 已确认 | 通过 → 转"在班" |
| ADM-309 | 导出主播 CSV | P1 | 已确认 | 全量字段导出 |
| ADM-310 | 编辑主播信息（含 TG/电话） | P0 | 已确认 | TG / 电话 / 显示名 / 头像可改；登录账号只读展示并可复制，不允许编辑；重置密码生成一次性临时密码并写审计 |

> v0.2 已废弃：ADM-305（强制下播）—— 改为房间维度的 ADM-912；ADM-307（设备冲突恢复）—— 改为基于 stream_key 自动；原 ADM-301 的"授权码 / 最后操作"列在主播表上移除。

### 3.5 用户管理（⑤ Users）

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| ADM-401 | 用户 KPI（注册总数 / 付费用户 / 冻结用户 / 封禁） | P0 | 已确认 | 4 卡 |
| ADM-402 | 用户列表（ID/名/RMB/钻石/累计充值/累计打赏钻石/运营标签/运营账号/注册/最后登录/状态） | P0 | 已确认 | 支持用户号 `user_no` 精确搜索、账号/昵称搜索、状态筛选；运营标签 `spender_tier` 按累计送出真实用户打赏钻石计算，不是等级；可设置/取消运营账号，运营账号加钻和送礼不计入真实充值、GMV、主播收益和奖励；运营账号礼物进入 C 端/主播端展示榜单和众筹解锁进度，在场次对账中单列展示但结算金额为 0 |
| ADM-403 | 用户详情（全维度 + 押注/充值/提现/弹幕历史 + 设备指纹 + 累计打赏钻石/运营标签） | P0 | 已确认 | 单页；大 R 仅用于后台识别，不产生用户特权 |
| ADM-404 | 用户审查（风控中状态下的人工审查） | P0 | 已确认 | 触发 R-204 等资金类风控规则时进入 |
| ADM-405 | 冻结/解冻账户 | P0 | 已确认 | 冻结后无法登录、押注、提现 |
| ADM-406 | 手动调整余额（仅超管/财务，含理由记录） | P0 | 已确认 | 写账本 + 强审计；不生成充值订单；运营账号调账使用 `platform:operations` 对账账户，不进入真实充值 |
| ADM-407 | 解封用户 | P0 | 已确认 | 撤销封禁 |
| ADM-408 | 导出 CSV | P1 | 已确认 | 全量字段导出 |
| ADM-409 | 用户等级门槛配置 | P0 | 已确认 | 后台 CRUD；配置等级编号、名称、达到多少累计充值到账钻石可升级；不产生弹幕、投注、进场、颜色、排序等特权 |
| ADM-410 | 礼物列表管理 | P0 | 已确认 | 后台 CRUD；配置礼物名称、上传礼物图标、钻石价格、上传特效静态图、启用状态和排序；`effect_type` 仅作旧枚举兼容 |

### 3.6 订单中心（⑥ Orders）

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| ADM-501 | 押注订单 tab（订单 / 用户 / 赛事 / 市场选项 / 押注 / 赔率 / 潜在收益 / 状态） | P0 | 已下线 | 当前版本无竞猜功能，财务管理不展示押注订单菜单 |
| ADM-502 | 充值订单 tab（订单 / 用户 / 金额 / 通道 / 三方流水号 / 状态） | P0 | 已确认 | 通道/状态筛选 |
| ADM-503 | 提现审核 tab（订单 / 用户 / 金额 / 收款 / 风控评分 / 提交时间 / 操作） | P0 | 已确认 | 待审/已放/已驳分类 |
| ADM-504 | 单笔放行 / 驳回 | P0 | 已确认 | 写审计；驳回需填理由 |
| ADM-505 | 批量审核 | P1 | 已确认 | 多选 + 批量操作 |
| ADM-506 | 押注订单退单 | P0 | 已下线 | 当前版本无竞猜功能，不展示押注订单退单入口 |
| ADM-507 | 充值订单手动补单 | P0 | 已确认 | 对账后异常订单补单到账 |

### 3.7 风控告警（已下线）

> 竞猜功能已下线，原基于竞猜押注的风控告警中心不再交付。后台保留用户冻结 / 解冻等敏感操作能力，但不提供告警列表、告警详情、规则配置页面和 `/api/v1/admin/risk/*` 接口。

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| ADM-601 | 风控 KPI | P0 | 已下线 | 不再展示 |
| ADM-602 | 活跃告警列表 | P0 | 已下线 | 不再展示 |
| ADM-603 | 告警详情 | P0 | 已下线 | 不再展示 |
| ADM-604 | 告警处置 | P0 | 已下线 | 不再展示 |
| ADM-605 | 风控规则表 | P0 | 已下线 | 不再展示 |
| ADM-606 | 新增规则 | P1 | 已下线 | 不再展示 |

### 3.8 通道对账（⑧ Recon）

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| ADM-701 | 通道选择 + 日期筛选 | P0 | 已确认 | 全部/微信/支付宝 |
| ADM-702 | 对账汇总（系统流水 / 通道流水 / 差异） | P0 | 已确认 | 3 卡，差异 > 0 时红色 |
| ADM-703 | 差异明细（金额不一致 / 单边订单） | P0 | 已确认 | 含订单号、通道流水号 |
| ADM-704 | 差异处理（补单 / 挂账 / 核对） | P0 | 已确认 | 写审计 |
| ADM-705 | 历史对账记录 | P0 | 已确认 | 最近 7 天；按平账状态分 |
| ADM-706 | 手动触发对账 | P1 | 已确认 | 重新跑当日对账 |
| ADM-707 | 导出 Excel | P1 | 已确认 | 完整差异明细 |

### 3.9 内容审核（⑨ Moderation - **v1 必上**）

> v0.2 修订：原 PRD 标记 v2 占位，v0.2 改为 v1 必上（合规底线）。

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| ADM-801 | 用户举报队列（举报内容 + 举报人 + 状态） | P0 | 已确认 | 列表 + 处置 + 反馈给举报人 |
| ADM-802 | 弹幕违规检索（按房间/时间/关键字） | P0 | 已确认 | 命中敏感词词库的弹幕全量可查 |
| ADM-803 | 房间封禁记录 | P0 | 已确认 | 与 ADM-914 房间封禁联动 |
| ADM-804 | AI 巡检结果复审（截图鉴黄） | P1 | 已确认 | 阿里云/腾讯云内容安全 API 触发后人工 review |
| ADM-805 | 人工巡查日志 | P0 | 已确认 | 房间管理员/审核员的处置记录 |
| ADM-806 | 敏感词词库管理（增删改 + 分级） | P0 | 已确认 | 后台 CRUD；1min 推送到 go-ws 缓存 |

## 4. 业务规则

### 4.1 RBAC 模型

```text
admin_user ─有─► admin_role ─有─► admin_permission（resource + action）
```

| 角色 | 资源权限 |
| --- | --- |
| super_admin | * × *；管理员账号管理；分配/取消分配房间管理员 |
| room_admin | 仅被分配房间：监控弹幕、实时观众、推流凭据、强制开播/关播、房间标题和比赛关联 |
| finance_admin | order:*, recon:*, withdraw:approve |
| risk_admin | risk:*, user:freeze, user:read, audit:read |
| cs_admin | user:read, order:read, moderation:read |

### 4.2 审计要求

| 写操作 | 必审计字段 |
| --- | --- |
| 主播封禁/解封 | who, when, target_streamer, reason |
| 主播强制下播 | who, when, target_session, reason |
| 用户冻结/解冻 | who, when, target_user, reason |
| 提现放行/驳回 | who, when, order_no, decision, reason |
| 押注退单 | who, when, activity_id, refund_amount, reason |
| 充值补单 | who, when, order_no, amount, reason |
| 手动调整余额 | who, when, target_user, delta, reason, op_type |
| 用户等级门槛新增/编辑/删除 | who, when, level_id, before, after |
| 礼物新增/编辑/删除 | who, when, gift_id, before, after |
| 风控规则编辑 | who, when, rule_id, before, after |
| 对账差异处置 | who, when, order_no, action |

审计表 `admin_audit_log` 全部强制不可删除、不可修改。

### 4.3 数据可见性

1. 后台所有用户的"敏感字段"（手机号、邮箱、支付宝账号、设备指纹、IP）展示时**默认掩码**（如 `138****1234`）。
2. 点击"查看完整信息"触发**二次确认 + 审计**。
3. 超管之外，其他角色看不到"完整 IP / 设备指纹 / 收款账号"。

### 4.4 数据看板口径

| KPI | 计算口径 |
| --- | --- |
| 今日 GMV | 今日 0:00 至现在的全部派彩 + 充值 + 打赏（不含已退单） |
| 在线主播 | 当前推流中的主播数 |
| 活跃用户 | 今日有过任意行为（登录/观看/弹幕/押注/打赏）的去重用户数 |
| 今日押注 | 今日 0:00 至现在的 `predict_bet` 行数 |
| 近 7 日 GMV 走势 | 每日 24:00 完成统计；按天 |

### 4.5 提现风控自动决策

| 风控评分 | 自动决策 | 后台分类 |
| --- | --- | --- |
| < 30（低） | 自动放行 | "已放行" |
| 30-69（中） | 人工审核 | "待审核" |
| ≥ 70（高） | 自动驳回 + 通知用户 | "已驳回" |

但即使低风险，**单笔 > ¥5,000** 也强制人工审核（无论评分）。

### 4.6 关键功能交互

#### 主播管理 - 强制下播

1. 点击主播行的"下播"→ 二次确认弹窗
2. 确认 → 服务端关闭推流 + 推 WS 给观众 + 房间状态 = ENDED + 审计
3. 操作记录显示在主播详情"操作历史" tab

#### 用户管理 - 冻结账户

1. 选择用户 → 点击"冻结"→ 弹窗填写理由（必填，≥ 10 字）
2. 确认 → 用户 `status` = FROZEN + 推 WS 让用户当前会话强制下线 + 审计
3. 后续用户登录 → 收到"账户已冻结，请联系客服"

#### 订单中心 - 提现放行

1. 点击订单的"放行"→ 二次确认
2. 确认 → 后端：解冻 → 调通道 → 转账成功 → 状态 = 已放行 → 推用户站内信 + 审计
3. 转账失败 → 自动重试 3 次；仍失败 → 状态 = 转账异常 → 告警

#### 风控告警 - 处置

已下线。用户冻结、解冻、重置密码等敏感操作直接在用户管理内完成并写审计，不再经过告警中心。

#### 对账 - 差异处置

1. "补单"：系统单边订单 → 创建对应的通道流水手工记录 → 重新平账
2. "挂账"：金额不一致或单边 → 标记"已挂账"暂不处理（等通道补流水）
3. "核对"：进入差异详情，人工联系通道核查

## 5. 边界与异常

| 场景 | 系统行为 | 提示/状态 |
| --- | --- | --- |
| 后台用户权限不足 | 模块入口隐藏 | 直接 URL 访问返回 403 |
| 后台用户重复登录 | 顶下旧会话 | 旧会话推到登录页 |
| 强制下播但主播已自然下播 | 幂等 | "主播已下播" |
| 冻结/解冻同一账户竞态 | 后写覆盖 + 审计两条 | 显示最终状态 |
| 对账定时任务失败 | 看板"差异"显示 ?? + 告警 | 运营手动触发 |

## 6. 权限与风控

- 所有后台操作必须有权限 + 审计。
- 后台账号密码必须使用强密码（≥ 12 位含大小写、数字、符号）。
- 后台必须启用 **2FA**（v1 可选 v2 强制）。
- IP 白名单（仅允许公司办公 IP + VPN 段访问）。
- 后台访问日志（不仅写操作，读操作也记录）。

## 7. 数据对象

| 对象 | Owner | 说明 |
| --- | --- | --- |
| `admin_user` | `services/go-app` | 后台用户 |
| `admin_role` | `services/go-app` | 角色 |
| `admin_permission` | `services/go-app` | 权限 |
| `admin_audit_log` | `services/go-app` | 后台审计日志 |
| 其他 | — | 主播 / 用户 / 订单 / 对账 等对象同其他模块 |

## 8. API/事件契约

每个子模块的具体接口分布在对应业务模块的 API 中。Admin 专属接口前缀 `/api/v1/admin/`。

| 子模块 | 主要接口 |
| --- | --- |
| Dashboard | `GET /api/v1/admin/dashboard/kpi`、`GET /admin/dashboard/gmv-7d`、`GET /admin/events/24h`、`GET /admin/streamers/top` |
| 主播 | `GET/POST/PUT /api/v1/admin/streamers`、`POST /admin/streamers/{id}/force-end`、`POST /admin/streamers/{id}/ban` |
| 用户 | `GET /api/v1/admin/users`、`POST /admin/users/{id}/freeze`、`POST /admin/users/{id}/unfreeze`、`POST /admin/users/{id}/balance-adjust` |
| 订单 | 财务菜单仅展示 `GET /admin/orders/recharges`、`GET /admin/orders/withdraws`、`GET /admin/orders/payment-callbacks`、`GET /admin/payment-channels`；押注订单入口已随竞猜下线隐藏 |
| 对账 | `GET /api/v1/admin/recon/summary?date=`、`GET /admin/recon/diff`、`POST /admin/recon/trigger` |
| 审计 | `GET /api/v1/admin/audit-logs?type=` |
| 比赛阶段（v0.3.1，ADM—911） | `PUT /api/v1/admin/matches/{id}/phase` body `{phase, minute, stoppage?}` 由运营手动切换上下半场/加时/点球；写后推 WS `match.phase.changed` |
| 直播线路（v0.3.1，ADM—912） | `GET /api/v1/admin/live-lines`、`POST /api/v1/admin/live-lines`、`PUT /api/v1/admin/live-lines/{id}`、`DELETE /api/v1/admin/live-lines/{id}`、`POST /admin/live-lines/{id}/toggle` 管理 N 条线路 |
| 广告位 A/B/C/D（v0.3.1，ADM—913） | `GET /api/v1/admin/ads/h5`、`PUT /api/v1/admin/ads/h5/{position}` 4 个位置（h5_sticky / h5_corner / h5_bubble / h5_theater_topbar） |
| 支付通道（v0.3.2，ADR-0010，ADM—914） | `GET /api/v1/admin/payment-channels`、`PUT /api/v1/admin/payment-channels/{code}` 4 个当前开放子通道开关 + 费率（alipay / wechat / union / digitalrmb；USDT 暂不上线） |
| 首页赛事 Banner 入口（ADM—901 / HOME—002） | `POST /api/v1/admin/rooms/{id}/home-banner` 设置直播间是否作为该赛事首页 Banner 入口；同一赛事只保留一个入口房间，后设置会替换先前入口；公开端 `GET /api/v1/home/today-matches` 返回赛事和 `live_room_entry` |
| LSJ 资源管理（ADM-920） | `GET /api/v1/admin/sports-live` 查询 LSJ 上游赛事和线路，线路返回 `line_type`、`quality_code`、`quality_label` 用于后台画质筛选和赛事绑定回显；`POST /api/v1/admin/sports-live/play` 获取线路 m3u8 用于后台只读预览，不在该页面绑定赛事 |

### 8.1 v0.3.1 新增 admin 子模块

#### ADM-911 比赛阶段切换（已加入 §3.3 赛事 & 赔率管理子模块的扩展）

- **目的**：v1 无第三方体育数据源，比赛阶段（上半场 / 中场 / 下半场 / 加时 / 点球 / 完场）由运营手动维护
- **页面**：`比赛详情` → `阶段控制` 区块
- **控件**：
  - 阶段下拉：`pre_match / first_half / half_time / second_half / et_first / et_break / et_second / penalty / finished`
  - minute 数字输入（仅 *_half / et_* 段需要；admin 输入"45'+2'"分别填 45 / 2）
  - stoppage 数字输入（补时，可空）
- **接口**：`PUT /api/v1/admin/matches/{id}/phase`
- **写后副作用**：自动更新 `match.status` 派生字段 + 推 WS `match.phase.changed` 给所有订阅该赛事的客户端
- **权限**：`super_admin` + `match_admin`
- **审计**：`admin.match.phase_update` event；before/after phase 入审计

#### ADM-912 直播线路管理

- **目的**：v0.3 引入 N 条线路（v1 默认 5 条）；运营需要新增 / 下线 / 修改 / 排序线路
- **数据**：`live_lines` 表（待迁移）—`id, name, edge_url, recommended, enabled, sort_order, created_at`
- **页面**：`系统配置 / 直播线路`
- **接口**：
  - `GET /api/v1/admin/live-lines` 列表（含 enabled / recommended / sort_order）
  - `POST /admin/live-lines` 新增
  - `PUT /admin/live-lines/{id}` 改名 / 改 edge_url / 改 recommended / 改 sort_order
  - `POST /admin/live-lines/{id}/toggle` enabled 翻转
  - `DELETE /admin/live-lines/{id}` 软删（不真删；soft delete 后客户端不再列出）
- **客户端读路径**：`GET /api/v1/live/lines?room_id={id}`（[`kickoff-live.md`](kickoff-live.md) LIVE—016）
- **权限**：`super_admin`
- **审计**：所有写操作走 audit；`admin.live_line.{create|update|toggle|delete}`

#### ADM-913 广告位管理（H5 / Web 多广告位）

- **目的**：H5 / Web 所有运营广告位统一在后台管理，前台按 `slot_code` 拉取
- **数据模型**：`ad_slots`（广告位定义）+ `ad_creatives`（广告内容），替代旧 `home_banners`
- **标准广告位**：
  - Web：`home_top` / `home_middle`
  - H5 首页：`h5_home_hero` / `h5_home_live_feed`
  - H5 tab / 直播间：`h5_sticky` / `h5_corner` / `h5_bubble` / `h5_theater_topbar`
- **页面**：后台「广告管理」
- **A/B/C 卡片字段**：`title (≤6 字)` / `icon (SVG / image_url)` / `sub (≤10 字)` / `link_type` / `link_target`
- **D 卡片字段**：`text (≤80 字符)`（只一段纯文本，前端循环 marquee）
- **接口**：
  - `GET /api/v1/admin/ads/slots` / `POST /api/v1/admin/ads/slots` / `PATCH /api/v1/admin/ads/slots/{id}`
  - `GET /api/v1/admin/ads/creatives?slot_id={id}` / `POST /api/v1/admin/ads/creatives` / `PATCH /api/v1/admin/ads/creatives/{id}`
- **权限**：`super_admin` + `cs_admin`（运营改广告）
- **客户端读路径**：首页 Banner 使用 `GET /api/v1/home/banner`；其它广告位使用 `GET /api/v1/ads/slots/{slot_code}/creatives`

#### ADM-914 支付通道开关（ADR-0010）

- **目的**：4 个当前开放充值子通道（支付宝 / 微信 / 银联某支付平台 / 数字人民币）的全局启用 / 停用 + 费率调整；USDT 暂不上线，不在后台入口展示
- **数据**：`system_configs` 表，category=`wallet`：
  - `wallet.recharge.channels.enabled` JSON array：`["wechat", "alipay", ...]`
  - `wallet.recharge.channels.{code}.fee_rate` 单通道费率覆盖（默认全局 0.05）
  - `wallet.recharge.channels.recommended` JSON array：配置哪些通道打"推荐"标签
  - `wallet.recharge.platform_fee_rate` 全局手续费率，测试阶段可设 `0`
  - `wallet.recharge.diamond_rmb_rate` 普通充值比例，默认 `1.00`
  - `wallet.recharge.min_amount` / `wallet.recharge.max_amount` 单笔充值上下限，支持 `0.01`
  - `wallet.recharge.amount_options` 充值预设金额 JSON 字符串数组，例如 `["0.01","1","10","50"]`
  - `wallet.recharge.packages` 精确充值包，例如 `[{"amount_rmb":"0.01","diamond_amount":1}]`
- **页面**：
  - `系统管理 / 系统配置 / 充值规则`：维护全局手续费、钻石比例、充值金额上下限、预设金额和精确充值包
  - `财务管理 / 支付通道`：维护通道启用、推荐和单通道费率
- **表格列**：通道 / 启用 / 费率（%）/ 推荐 / 最近 7 天到账率 / 操作
- **接口**：
  - `GET /api/v1/admin/payment-channels` 返回 4 个当前开放通道状态 + 7d 到账率
  - `PUT /api/v1/admin/payment-channels/{code}` body `{enabled?, fee_rate?, recommended?}`
- **权限**：`super_admin` + `finance_admin`
- **审计**：`admin.payment_channel.update` event

#### ADM-919 协议管理（富文本）

- **目的**：运营在后台维护用户协议 / 隐私政策 / 充值协议等法律文本，标题 + 富文本正文
- **形态**：列表式自由 CRUD —— 每条带自定义 `code`（业务 key，C 端按此引用）+ `title` + 富文本 `content`
- **版本策略**：v1 单条覆盖（不做版本历史；谁在何时改由 `admin_audit_logs` 记录）
- **数据模型**：`protocols` 表（雪花 ID / 软删 / `code` 唯一 / `content` MEDIUMTEXT 存 HTML）
- **页面**：后台「内容管理 / 协议管理」，正文用 tiptap 富文本编辑器（`@vben/plugins/tiptap`）
- **接口**：
  - `GET /api/v1/admin/protocols` / `POST /api/v1/admin/protocols`
  - `PATCH /api/v1/admin/protocols/{id}` / `DELETE /api/v1/admin/protocols/{id}`
- **权限**：`super_admin`（v1 仅登录态校验，未细分角色）
- **审计**：所有写操作走 audit；`admin.protocol.{create|update|delete}`
- **范围外**：v1 不做 C 端公开读接口（前端提需求再加）；不做版本快照

## 9. 验收标准

| 需求 ID | 验收标准 |
| --- | --- |
| ADM-001 | 8 个模块入口可见；徽章数与实际待处理数一致 |
| ADM-003 | 5 种角色登录后只能看到对应模块；越权 URL 返回 403 |
| ADM-101 | 4 大 KPI 数字与对应底表实时一致；变化 1 分钟内反映 |
| ADM-301 | 主播表格筛选/搜索/操作正确；状态徽章准确 |
| ADM-305 | 强制下播 → 主播端推流终止 + 观众端切兜底 |
| ADM-405 | 冻结后用户 5s 内被强制下线 + 后续登录被拒 |
| ADM-503 | 提现审核流程：低风险自动放行 ｜ 中风险待审核 ｜ 高风险驳回 |
| ADM-702 | 7-14 当日差异 ¥100 / 2 笔与底表一致；可点击查看明细 |

## 10. 测试要求

1. **单元测试**：RBAC 权限校验、审计写入、提现风险评分映射
2. **集成测试**：每个 admin 写接口的"鉴权 + 审计"完整性
3. **E2E**：5 种角色各自登录后访问每个模块的 happy path + 越权 case
4. **压测**：看板 KPI 接口 100 QPS 持续 1 分钟
5. **安全测试**：CSRF、XSS、未授权访问、敏感字段返回掩码

## 11. 待确认问题

| 问题 | Owner | 截止时间 | 状态 |
| --- | --- | --- | --- |
| 是否启用 2FA（v1 必填 vs 可选） | `@kickoff/security` | 2026-05-29 | 待确认 |
| 后台是否走 IP 白名单（限办公网 / VPN） | `@kickoff/devops` | 2026-05-29 | 待确认 |
| v1 是否实现赛事 & 赔率管理 vs 占位 | `@kickoff/product` | 2026-05-25 | 已确认 v1 占位 |
| 内容审核 v1 占位 vs 最小可用版（仅举报队列） | `@kickoff/product` | 2026-05-25 | 已确认 v1 占位 |
| 风控规则配置是声明式（DSL）还是写死 | `@kickoff/security` | 2026-06-01 | 待确认 |
| 对账定时任务执行时间（默认每日 02:00） | `@kickoff/devops` | 2026-05-29 | 待确认 |
