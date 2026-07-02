---
id: "doc-2482ec29911e"
title: "后台系统统计报表说明 · stats_report"
date: "2026-07-03T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/src/youdianse-php/doc/stats_report.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/src/youdianse-php/doc/stats_report.md"
sourceSha256: "1f66233ee85269cb76950f7bb2d0f45970bdd127d85d1ff2217b8fa19bbe37c1"
sourceSystem: "project-doc"
---

# 后台系统统计报表说明 · stats_report

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/src/youdianse-php/doc/stats_report.md`

> 整理日期：2026-07-03 00:00｜日期依据：正文日期

> 统计汇总时间：2026-07-03
> 覆盖范围：后台（`/admin1866`）系统管理菜单下所有统计报表页面。
> 定时任务统一由 `app/Tasks/` 目录下的 Task 类驱动，入口脚本为 `bin/shell.php`，详见 `crontab.md`。

---

## 目录

### 一、平台层统计

| # | 报表名称 | 页面路由 | 落库表 / 数据来源 |
|---|----------|----------|------------------|
| 1 | [平台总览](#1-平台总览) | `/platformOverview/home` | `report_platform_daily_total_log` + 实时聚合 |
| 2 | [系统主页](#2-系统主页) | `/system/home` | `report_total_day_log` + `user_charge` + `account_detail`（实时） |
| 3 | [平台日报统计](#3-平台日报统计) | `/system/platformDailyStat` | `report_platform_daily_total_log`（total模式）/ `report_device_type_day_log`（device模式） |
| 4 | [平台注册留存统计](#4-平台注册留存统计) | `/system/platformRetention` | `report_platform_daily_total_log`（total模式）/ `report_platform_retention_daily_log`（dim模式） |
| 5 | [系统报表日志](#5-系统报表日志) | `/system/reportTotalDayLog` | `report_total_day_log` |

### 二、转化漏斗

| # | 报表名称 | 页面路由 | 落库表 / 数据来源 |
|---|----------|----------|------------------|
| 6 | [转化漏斗](#6-转化漏斗) | `/funnelStat/list` | `page_visit_log` / `user_download` / `user` / `user_charge` / `user_spend` 等 |

### 三、渠道统计

| # | 报表名称 | 页面路由 | 落库表 / 数据来源 |
|---|----------|----------|------------------|
| 7 | [渠道统计（V1）](#7-渠道统计v1) | `/system/channel` | `report_channel_day_log` |
| 8 | [渠道统计V2](#8-渠道统计v2) | `/system/channelV2` | `report_channel_day_log_v2` |
| 9 | [渠道注册留存](#9-渠道注册留存) | `/system/channelRetention` | `report_channel_retention_daily_log` |
| 10 | [渠道注册LTV](#10-渠道注册ltv) | `/system/channelLtv` | `report_channel_ltv_daily_log` |

### 四、游戏统计

| # | 报表名称 | 页面路由 | 落库表 / 数据来源 |
|---|----------|----------|------------------|
| 11 | [游戏统计](#11-游戏统计) | `/system/game` | `report_game_day_log` |
| 12 | [网络游戏统计](#12-网络游戏统计) | `/system/networkGame` | `report_game_network_day_log` |
| 13 | [游戏渠道统计](#13-游戏渠道统计) | `/system/gameChannel` | `report_game_channel_day_log` |
| 14 | [游戏注册留存](#14-游戏注册留存) | `/system/gameRetention` | `report_game_retention_daily_log` |
| 15 | [游戏注册LTV](#15-游戏注册ltv) | `/system/gameLtv` | `report_game_ltv_daily_log` |
| 16 | [单机游戏统计](#16-单机游戏统计) | `/system/singleGame` | `report_single_game_day_log` |

### 五、套餐 / AB测试统计

| # | 报表名称 | 页面路由 | 落库表 / 数据来源 |
|---|----------|----------|------------------|
| 17 | [套餐统计](#17-套餐统计) | `/system/combo` | `report_combo_total_day_log` |
| 18 | [AB测试统计](#18-ab测试统计) | `/system/abLog` | `report_ab_day_log` |

### 六、用户行为 / 活跃统计

| # | 报表名称 | 页面路由 | 落库表 / 数据来源 |
|---|----------|----------|------------------|
| 19 | [留存统计（DAU）](#19-留存统计dau) | `/system/dau` | `report_dau_log` |
| 20 | [小时统计](#20-小时统计) | `/system/hour` | `report_hour_log` |
| 21 | [活跃列表](#21-活跃列表) | `/system/appLog` | `app_log` |
| 22 | [游戏下载列表](#22-游戏下载列表) | `/system/gameDownload` | `user_download` |
| 23 | [特权会员游戏下载](#23-特权会员游戏下载) | `/system/gameVipDownload` | `user_vip_download` |
| 24 | [游戏预约统计](#24-游戏预约统计) | `/system/gameReserve` | `game_reserve` |

### 七、内容统计

| # | 报表名称 | 页面路由 | 落库表 / 数据来源 |
|---|----------|----------|------------------|
| 25 | [视频统计](#25-视频统计) | `/system/movie` | `report_movie_log` |
| 26 | [漫画统计](#26-漫画统计) | `/system/comics` | `report_comics_log` |
| 27 | [广告统计](#27-广告统计) | `/system/adv` | `report_adv_log` |

### 八、AI统计

| # | 报表名称 | 页面路由 | 落库表 / 数据来源 |
|---|----------|----------|------------------|
| 28 | [老司机AI汇总统计](#28-老司机ai汇总统计) | `/system/reportAiTotal` | `UserLsjAiService` 日统计 |

### 九、埋点 / 行为统计

| # | 报表名称 | 页面路由 | 落库表 / 数据来源 |
|---|----------|----------|------------------|
| 29 | [活动埋点统计](#29-活动埋点统计) | `/trackingStat/list` | `tracking_stat`（`tracking_type≠99`） |
| 30 | [游戏推广埋点统计](#30-游戏推广埋点统计) | `/trackingGameStat/list` | `tracking_stat`（`tracking_type=99`） |
| 31 | [页面访问统计](#31-页面访问统计) | `/pageVisitStat/list` | `page_visit_stat` |
| 32 | [页面访问日志明细](#32-页面访问日志明细) | `/pageVisitStat/pageVisitLog` | `page_visit_log` |
| 33 | [未登录游戏下载统计](#33-未登录游戏下载统计) | `/gameDownloadStat/list` | `game_download_stat` |
| 34 | [商品点击统计](#34-商品点击统计) | `/productClickStat/list` | `product_click_stat` |

### 十、平台币统计

| # | 报表名称 | 页面路由 | 落库表 / 数据来源 |
|---|----------|----------|------------------|
| 35 | [平台币总览](#35-平台币总览) | `/coinOverview/list` | `report_coin_overview_day_log` |
| 36 | [平台币原因结构](#36-平台币原因结构) | `/coinReason/list` | `report_coin_reason_day_log` |
| 37 | [平台币消耗去向](#37-平台币消耗去向) | `/coinDestination/list` | `report_coin_destination_day_log` |
| 38 | [平台币余额快照](#38-平台币余额快照) | `/coinBalance/list` | `report_coin_balance_day_log` |

### 十一、支付统计

| # | 报表名称 | 页面路由 | 落库表 / 数据来源 |
|---|----------|----------|------------------|
| 39 | [支付通道日统计](#39-支付通道日统计) | `/paymentOrder/stat` | `payment_channel_daily_statistics` |

---

## 通用机制说明

### 重跑（resetData）

后台统计报表支持对指定日期触发重跑，入口：`/system/resetData`
参数：`reset_type`（对应报表类型）、`end_time`（目标日期）、`reset_data=1`
内部通过 `QueueService` 分发对应离线 Job 重建当日数据。

### 导出 Excel（excelAction）

统一入口：`/system/excel`，传 `type` 参数路由到对应方法，`pageSize` 扩展至 `100000` 条。

### 定时任务

所有统计 Job 均在 `app/Tasks/` 下定义，`bin/shell.php` 为 CLI 入口，cron 调度见 `crontab.md`。

---

## 1. 平台总览

**路由**：`/platformOverview/home`
**控制器**：`PlatformOverviewController::homeAction`
**数据仓库**：`PlatformOverviewRepository`
**主数据表**：`report_platform_daily_total_log`（离线日报） + 实时聚合源表

### 数据来源表

| 表名 | 数据层级 | 说明 |
|------|----------|------|
| `report_platform_daily_total_log` | 离线汇总表 | 昨日及历史日报主表，定时任务写入 |
| `report_device_type_day_log` | 离线汇总表 | 今日实时聚合源表（按设备类型分组） |

#### 计算来源表（ETL 实际读取，`PlatformDailyStatJob` → `ReportDeviceTypeDayLogService::collectStatistics`）

| 表名 | 贡献指标 |
|------|----------|
| `app_log` | `platform_active_account`/`game_active_account`等活跃指标 |
| `user` | `platform_new_account`（注册）、`website_register_account`/`sdk_register_account` |
| `user_download` | `download_request_num`（下载请求数） |
| `user_charge` | `charge_account_num`/`charge_amount`、`total_order_num`/`valid_order_num`（充值/订单） |
| `user_spend` | `spend_account_num`/`spend_amount`（消费/投诉扣款） |
| `page_visit_stat` | `platform_uv`（平台访客UV） |

#### `report_platform_daily_total_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{date}` 的md5值 |
| `date` | 日期 |
| `platform_uv` | 平台访客UV |
| `platform_new_account` | 平台新增账号 |
| `website_register_account` | 网站注册账号 |
| `sdk_register_account` | SDK注册账号 |
| `platform_summary_active_account` | 平台汇总活跃账号 |
| `platform_active_account` | 平台活跃账号 |
| `game_active_account` | 游戏活跃账号 |
| `download_request_num` | 下载请求数 |
| `total_order_num` | 总下单数 |
| `valid_order_num` | 有效订单数 |
| `charge_account_num` | 充值账号数 |
| `charge_amount` | 充值金额 |
| `spend_account_num` | 消费账号数 |
| `spend_amount` | 消费金额 |
| `complaint_deduct_order_num` | 投诉扣款订单数 |
| `complaint_deduct_amount` | 投诉扣款金额 |
| `d2`~`d7`,`d14`,`d30` | D2~D30留存账号数（在平台站内登录成功） |
| `created_at` / `updated_at` | 创建/更新时间 |

#### `report_device_type_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{date}_{device_type_new}` 的md5值 |
| `date` | 日期 |
| `device_type_new` | 设备类型 |
| `platform_uv`~`spend_amount`、`complaint_deduct_order_num`、`complaint_deduct_amount` | 同 `report_platform_daily_total_log`，按设备类型分组统计 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

展示平台核心运营指标的「今天 / 过去7天 / 过去30天」三个时间维度。每个维度展示当期值、对比值、波动率（`+/-`方向箭头）。

| 时间区块 | 当期区间 | 对比区间 |
|----------|----------|----------|
| 今天 | 当日（实时） | 昨日全天（离线表） |
| 过去7天 | [昨天-6天, 昨天] | [昨天-13天, 昨天-7天] |
| 过去30天 | [昨天-29天, 昨天] | [昨天-59天, 昨天-30天] |

> 今日数据由 `ReportDeviceTypeDayLogService::getTotalStatistics()` 实时聚合源表计算，昨天及更早使用离线日报表。

### 统计指标（共 11 个）

| 字段 | 指标名称 | 类型 | 口径说明 |
|------|----------|------|----------|
| `platform_uv` | 平台访客UV | 整数 | 当期平台访问去重用户数（含游客） |
| `platform_new_account` | 平台新增账号 | 整数 | 当期新注册账号数 |
| `platform_summary_active_account` | 平台汇总活跃账号 | 整数 | 平台活跃 + 游戏活跃的并集去重 |
| `platform_active_account` | 平台活跃账号 | 整数 | 当期有平台侧行为的登录账号数 |
| `game_active_account` | 游戏活跃账号 | 整数 | 当期有游戏内行为的账号数 |
| `download_request_num` | 下载请求数 | 整数 | 当期发起游戏下载请求的次数 |
| `charge_account_num` | 充值账号数 | 整数 | 当期成功充值的去重账号数 |
| `charge_amount` | 充值金额 | 金额（元，保留2位） | 当期成功充值的总金额（人民币） |
| `spend_account_num` | 消费账号数 | 整数 | 当期有消费行为的去重账号数 |
| `spend_amount` | 消费金额（元） | 金额（元，保留2位） | 统计表存 G 点，展示时 ÷10 换算为人民币（10 G点 = 1元） |
| — | 订单成功率 | 百分比 | `valid_order_num / total_order_num × 100%` |

### 波动率计算

```
波动率 = (当前值 - 对比值) / 对比值
```
- 对比值为 0 时展示「`-`」；
- 无离线行（当日/区间无数据）时各指标展示「`-`」。

---

## 2. 系统主页

**路由**：`/system/home`
**控制器**：`SystemController::homeAction`
**数据仓库**：`ReportRepository::getNewReportData`
**主数据表**：`report_total_day_log`（今日/历史）、`user_charge`、`account_detail`（实时聚合）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_total_day_log` | 离线全平台日报，近30天趋势图数据来源 |
| `user_charge` | 充值订单表，实时聚合累计充值/付费指标 |
| `account_detail` | 平台币流水明细，实时聚合累计消耗/赠送/充值G点 |

#### `report_total_day_log` 计算来源表（ETL 实际读取，`TotalOldDayJob`）

| 表名 | 贡献指标 |
|------|----------|
| `app_log` | `total_dau`（当日活跃） |
| `user` | `total_reg`（当日注册，按 `register_date`） |
| `user_download` | `total_download_num`（下载数量） |
| `user_charge` | `total_charge`（充值金额）、`total_spend`（投诉扣款，`complaint_time`+`status=2`）、`total_order`/`total_order_success`、`total_reg_pay_num`/`total_reg_pay_total`、`total_retain_pay_num`/`total_retain_pay_total` |
| `user_spend` | `total_complaint`（消费金额，游戏内/单机购买消费口径，`pay_time`+`status=1`） |

#### `report_total_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{date}` 的md5值 |
| `date` | 日期 |
| `total_dau` | 总日活 |
| `total_reg` | 注册人数 |
| `total_download_num` | 下载数量 |
| `total_charge` | 充值金额 |
| `total_spend` | 消费金额 |
| `total_complaint` | 投诉扣款 |
| `total_reg_pay_num` / `total_reg_pay_total` | 注册付费人数/金额 |
| `total_retain_pay_num` / `total_retain_pay_total` | 留存付费人数/金额 |
| `total_order` / `total_order_success` | 订单数/成功订单数 |
| `created_at` / `updated_at` | 创建/更新时间 |

#### `user_charge` 字段（节选，详见附录 E）

| 字段 | 说明 |
|------|------|
| `user_id` | 用户ID |
| `money` | 订单金额 |
| `real_money` | 扣除费率后的实际到账金额 |
| `status` | 订单状态：-1发起失败 0付款中 1已付款 2投诉 |
| `is_vip` | 是否VIP套餐 |
| `created_at` | 创建时间 |

#### `account_detail` 字段（详见附录 B）

| 字段 | 说明 |
|------|------|
| `user_id` | 用户ID |
| `type` | 流水类型：1充值 2消费 3活动赠送 4积分兑换 5后台操作 6VIP每日领取 8盲盒 9积分兑换G点 |
| `amount` | 变动数值（正=获得，负=消耗） |
| `created_at` | 创建时间 |

### 功能说明

后台系统主页仪表盘，展示平台全量累计指标 + 今日/昨日/近7天/本月/上月的环比数据卡片，同时附带近30天趋势折线图（注册、DAU、充值）。

### 统计指标

| 字段 | 说明 | 口径 |
|------|------|------|
| `user_total` | 累计注册总用户数 | `user` 集合总数 |
| `userdown_total` | 累计游戏下载次数 | `user_download` 集合总数 |
| `total_money` | 累计充值总金额（元） | `user_charge.status=1` 的 `money` 之和 |
| `total_pay_num` | 累计付费用户数 | `user_charge.status=1` 去重 `user_id` 数 |
| `total_order` | 累计订单总数 | `user_charge` 集合总数 |
| `total_order_success` | 累计成功订单数 | `user_charge.status=1` 计数 |
| `total_spend` | 累计消耗平台币 | `account_detail.amount<0` 的绝对值之和（G点） |
| `total_gift` | 累计赠送平台币 | `account_detail.type≠1, amount>0` 之和（G点） |
| `total_charge_gpoint` | 累计充值平台币 | `account_detail.type=1, amount>0` 之和（G点） |
| `total_balance` | 平台币结余 | `charge + gift - spend`（G点） |

#### 时间维度数据（各周期）

每个时间区块（今日 / 昨日 / 7日 / 本月 / 上月）返回：`reg`（注册）、`download_num`（下载）、`order`（订单）、`order_success`（成功订单）、`charge`（充值金额）、`spend`（消耗G点）、`gift`（赠送G点）、`charge_gpoint`（充值G点）、`balance`（结余G点）。

#### 近30天折线图数据（`last30DaysData`）

从 `report_total_day_log` 读取，返回：
- `dates`：近30天日期列表
- `reg`：每日注册数
- `dau`：每日活跃数
- `charge`：每日充值金额

---

## 3. 平台日报统计

**路由**：`/system/platformDailyStat`
**控制器**：`SystemController::platformDailyStatAction`
**数据仓库**：`ReportRepository::getPlatformDailyStat`
**主数据表**：`report_platform_daily_total_log`（total模式）/ `report_device_type_day_log`（device模式）
**定时任务**：`platformDailyStat dailyStat`（每天凌晨3点）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_platform_daily_total_log` | 全平台汇总日报（`mode=total`），字段详见 [平台总览](#1-平台总览) |
| `report_device_type_day_log` | 按设备类型拆分日报（`mode=device`），字段详见 [平台总览](#1-平台总览) |

> 计算来源（`app_log`/`user`/`user_download`/`user_charge`/`user_spend`/`page_visit_stat`）与 [平台总览](#1-平台总览) 完全一致，由同一个 `PlatformDailyStatJob` 写入。

### 功能说明

两种模式通过 `mode` 参数切换：
- `mode=total`（默认）：全平台总汇总，一天一行，第1页末行追加「合计」
- `mode=device`：按设备类型（PC/H5/APP等）拆分，支持 `device_type_new` 筛选，不追加合计行

### 筛选条件

| 参数 | 说明 |
|------|------|
| `start_time` / `end_time` | 日期范围 |
| `mode` | `total`（总汇总）/ `device`（按设备） |
| `device_type_new` | 设备类型（device模式下可选：`pc`/`h5`/`app`等） |

### 展示字段

| 字段 | 说明 | 单位 |
|------|------|------|
| `date` | 统计日期 | — |
| `device_type_name` | 设备类型名称（device模式有值，total模式为`-`） | — |
| `register_num` | 新注册账号数 | 人 |
| `dau_account_num` | 日活账号数 | 人 |
| `charge_account_num` | 充值账号数 | 人 |
| `charge_amount` | 充值金额 | 元 |
| `spend_account_num` | 消费账号数 | 人 |
| `spend_amount` | 消费金额（G点÷10→元） | 元 |
| `download_request_num` | 下载请求数 | 次 |
| `total_order_num` | 总订单数 | 次 |
| `valid_order_num` | 成功订单数 | 次 |
| `complaint_deduct_amount` | 投诉扣款金额 | 元 |
| `order_success_rate` | 订单成功率 = `valid_order_num / total_order_num × 100%` | % |
| `net_charge_amount` | 净充值 = `charge_amount - complaint_deduct_amount` | 元 |
| `updated_at` | 最后更新时间 | — |

---

## 4. 平台注册留存统计

**路由**：`/system/platformRetention`
**控制器**：`SystemController::platformRetentionAction`
**数据仓库**：`ReportRepository::getPlatformRetentionStat`
**主数据表**：`report_platform_daily_total_log`（total模式）/ `report_platform_retention_daily_log`（dim模式）
**定时任务**：`platformDailyStat retention`（每天凌晨4点）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_platform_daily_total_log` | 全平台留存日报（`mode=total`），字段详见 [平台总览](#1-平台总览) |
| `report_platform_retention_daily_log` | 按注册来源×设备类型×渠道拆维度留存日报（`mode=dim`） |

#### 计算来源表（ETL 实际读取，`PlatformRetentionDnJob`）

| 表名 | 贡献指标 |
|------|----------|
| `user` | 圈定当日注册的 cohort 用户（`reg_users`） |
| `app_log` | 按 `register_date`+`date` 匹配判断 cohort 用户次日~30日是否回访（`d2`~`d30`） |

#### `report_platform_retention_daily_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号 |
| `date` | 注册日期（cohort日期） |
| `register_source` | 注册来源（1=网站注册，2=SDK注册） |
| `device_type_new` | 设备大类 |
| `channel_name` | 渠道 |
| `reg_users` | 新增账号 |
| `d2`~`d7`,`d14`,`d30` | D2~D30留存人数 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

两种模式：
- `mode=total`（默认）：全平台按注册日期汇总，末行附带「汇总」行（各dN加权平均，仅计入已跑满的cohort）
- `mode=dim`：按注册来源×设备类型×渠道拆维度，无汇总行

### 筛选条件

| 参数 | 说明 | 适用模式 |
|------|------|---------|
| `start_time` / `end_time` | 注册日期范围 | 两种 |
| `mode` | `total` / `dim` | — |
| `register_source` | 1=网站注册，2=SDK注册 | dim |
| `device_type_new` | 设备类型 | dim |
| `channel_name` | 渠道码 | dim |

### 展示字段

| 字段 | 说明 | 口径 |
|------|------|------|
| `register_date` | 注册日期（cohort日期） | — |
| `new_account_count` | 当日新增账号数 | `platform_new_account`（total）/ `reg_users`（dim） |
| `d2_retention` | D2留存率 | `d2 / new_account_count` |
| `d3_retention` | D3留存率 | `d3 / new_account_count` |
| `d4_retention` | D4留存率 | `d4 / new_account_count` |
| `d5_retention` | D5留存率 | `d5 / new_account_count` |
| `d6_retention` | D6留存率 | `d6 / new_account_count` |
| `d7_retention` | D7留存率 | `d7 / new_account_count` |
| `d14_retention` | D14留存率 | `d14 / new_account_count` |
| `d30_retention` | D30留存率 | `d30 / new_account_count` |
| `register_source_name` | 注册来源（dim模式） | 「网站注册」/「SDK注册」 |
| `device_type_new_name` | 设备类型名称（dim模式） | — |
| `channel_name` | 渠道码（dim模式） | — |
| `updated_at` | 最后更新时间 | — |

> **汇总行口径**（total模式末行）：各dN仅将已跑满该天数的cohort（cohort日期 ≤ 今天-N天）纳入加权平均，分子分母分别求和后相除。

---

## 5. 系统报表日志

**路由**：`/system/reportTotalDayLog`
**控制器**：`SystemController::reportTotalDayLogAction`
**数据仓库**：`ReportRepository::getReportTotalDayLog`
**主数据表**：`report_total_day_log`
**定时任务**：`total totalMinute`（每小时）/ `total totalOldDay`（每天凌晨2点重跑）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_total_day_log` | 全平台每日汇总日报主表，计算来源（`app_log`/`user`/`user_download`/`user_charge`/`user_spend`）详见 [系统主页](#2-系统主页) |

### 功能说明

查看全平台每日汇总日报的原始数据，供核查离线 Job 写入情况使用。

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 统计日期 |
| `total_reg` | 当日新注册用户数 |
| `total_dau` | 当日活跃用户数（DAU） |
| `total_charge` | 当日充值金额（元） |
| `updated_at` | 最后更新时间（`Y-m-d H:i`） |

---

## 6. 转化漏斗

**路由**：`/funnelStat/list`
**控制器**：`FunnelStatController::listAction`（复用 `/trackingStat` 权限节点）
**数据仓库**：`FunnelStatRepository`

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_platform_daily_total_log` / `report_device_type_day_log` | 平台访问UV来源，字段详见 [平台总览](#1-平台总览) |
| `page_visit_log` | 详情页访问UV来源（`page` 字段匹配 game_detail/game_sub_detail/game_id_detail），字段详见 [页面访问日志明细](#32-页面访问日志明细) |
| `user_download` | 下载点击/请求UV来源，字段详见 [游戏下载列表](#22-游戏下载列表) |
| `game_download_stat` | 未登录游客下载点击UV来源，字段详见 [未登录游戏下载统计](#33-未登录游戏下载统计) |
| `user` | 注册账号数来源（渠道/游戏视角），字段详见附录 F |
| `user_charge` | 充值账号数来源（渠道/游戏视角），字段详见附录 E |
| `user_spend` | 单机游戏消费账号数来源 |

#### `user_spend` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `user_id` | 用户ID |
| `channel` | 渠道码 |
| `gameid` | 游戏ID/official |
| `type` | 消费类型：1网络游戏内付 2购买单机游戏 |
| `money` | 订单金额 |
| `status` | 订单状态：-1发起失败 0付款中 1付款成功 |
| `pay_time` | 支付时间 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

支持「平台 / 渠道 / 游戏」三种视角，每种视角呈现不同的漏斗节点链路；页面以 Tab 切换。

### 筛选条件

| 参数 | 类型 | 说明 |
|------|------|------|
| `view` | string | 视角：`platform` / `channel` / `game` |
| `start_date` / `end_date` | string | 日期范围（默认：昨天至今天） |
| `device_type_new` | string | 设备类型筛选（`pc`/`h5`/`app` 等，留空=全部） |
| `detail_source` | string | 详情页来源大类（`home_banner` / `home_recommend` / `search` / `game_list` / `other`，留空=全部） |
| `channel_name` | string | 渠道码（仅渠道/游戏视角生效） |
| `game_id` | string/int | 游戏ID或名称（仅游戏视角生效，支持模糊名称解析） |

### 漏斗节点定义

#### 平台视角（4 个漏斗节点）

| 顺序 | 节点key | 节点名称 | 数据来源 |
|------|---------|----------|----------|
| 1 | `platform_visit_uv` | 平台访问UV | `report_platform_daily_total_log` / `report_device_type_day_log` |
| 2 | `detail_uv` | 详情页访问UV | `page_visit_log`（page IN game_detail/game_sub_detail/game_id_detail） |
| 3 | `download_click_uv` | 下载点击UV | `user_download` + `game_download_stat` |
| 4 | `download_request_uv` | 下载请求UV | `user_download`（按user_id去重） |

#### 渠道视角（6 个漏斗节点）

| 顺序 | 节点key | 节点名称 |
|------|---------|----------|
| 1 | `detail_uv` | 详情页访问UV |
| 2 | `download_click_uv` | 下载点击UV |
| 3 | `download_request_uv` | 下载请求UV |
| 4 | `register_num` | 注册账号数 |
| 5 | `charge_account_num` | 充值账号数 |
| 6 | `spend_account_num` | 消费账号数 |

#### 游戏视角（6 个漏斗节点）

| 顺序 | 节点key | 节点名称 |
|------|---------|----------|
| 1 | `detail_uv` | 详情页访问UV |
| 2 | `download_click_uv` | 下载点击UV |
| 3 | `download_request_uv` | 下载请求UV |
| 4 | `new_account_num` | 新增账号数 |
| 5 | `charge_account_num` | 充值账号数 |
| 6 | `spend_account_num` | 消费账号数 |

### 转化率计算

- **步骤转化率**（`step_rate`）：当节点值 / 上一节点值 × 100%
- **首步转化率**（`first_rate`）：当节点值 / 第一节点值 × 100%
- 分母为 0 时展示「`-`」

---

## 7. 渠道统计（V1）

**路由**：`/system/channel`
**控制器**：`SystemController::channelAction`（权限：`/systemChannel`）
**数据仓库**：`ReportRepository::getChannel`
**主数据表**：`report_channel_day_log`
**定时任务**：`AgentTotalOldDay agentOldDayTotal`（凌晨1点重跑）/ `AgentTotalMinute agentMinuteTotal`（每小时）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_channel_day_log` | 渠道日报离线汇总表 |

#### 计算来源表（ETL 实际读取，`AgentTotalOldDayJob` → `ReportChannelDayLogService`）

| 表名 | 贡献指标 |
|------|----------|
| `app_log`（2025-11-27后）/ `report_game_adv_log`（历史） | `dau`/`next_day_dau`（活跃/次日活跃） |
| `user` | `reg`（注册） |
| `user_download` | `download_num`（下载） |
| `user_charge` | `charge`（充值）、`spend`（投诉扣款，`complaint_time`+`status=2`）、`order`/`order_success`、`new_pay_num`/`first_pay_num`/`first_pay_total`、`reg_pay_num`/`reg_pay_total`、`retain_pay_num`/`retain_pay_total` |
| `user_spend` | `complaint`（消费金额，游戏内/单机购买消费口径） |

#### `report_channel_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{channel_name}_{date}` 的md5值 |
| `date` | 日期 |
| `channel` | 渠道名称 |
| `dau` | 总日活 |
| `next_day_dau` | 次日日活 |
| `reg` | 注册人数 |
| `download_num` | 下载数量 |
| `charge` | 充值金额 |
| `spend` | 消耗平台币 |
| `complaint` | 投诉扣款金额 |
| `reg_pay_num` / `reg_pay_total` | 注册付费人数/金额 |
| `retain_pay_num` / `retain_pay_total` | 留存付费人数/金额 |
| `new_pay_num` / `new_pay_total` | 新增付费人数/金额 |
| `order` / `order_success` | 订单数/成功订单数 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

按渠道×日期维度统计新注册、活跃、充值、消费等核心指标，末行追加合计行。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `code` | 渠道码（精确匹配 `channel` 字段） |
| `start_time` / `end_time` | 日期范围 |

### 展示字段

| 字段 | 说明 | 口径 |
|------|------|------|
| `date` | 统计日期 | — |
| `channel` | 渠道码 | — |
| `reg` | 新注册数 | 当日该渠道新注册账号数 |
| `dau` | 日活跃数 | 当日活跃账号数 |
| `next_day_dau` | 次日DAU | 次日该渠道活跃数 |
| `download_num` | 下载次数 | 当日下载请求数 |
| `charge` | 充值金额（元） | 当日充值总额 |
| `spend` | 消耗平台币（G点） | 当日消耗总额 |
| `complaint` | 投诉金额（元） | 当日投诉扣款 |
| `reg_pay_num` | 新用户首日付费人数 | — |
| `reg_pay_total` | 新用户首日付费金额 | — |
| `retain_pay_num` | 老用户回流付费人数 | — |
| `retain_pay_total` | 老用户回流付费金额 | — |
| `first_pay_num` | 首次付费人数 | — |
| `first_pay_total` | 首次付费金额 | — |
| `new_pay_num` | 当日新增付费人数（DAU维度） | — |
| `total_reg` | 当月累计注册数 | 从注册日起到查询截止日的月内累计 |
| `reg_pay_rate` | 新用户付费率 | `reg_pay_num / reg` |
| `reg_pay_arpu` | 新用户ARPU | `charge / reg` |
| `new_pay_rate` | DAU付费率 | `new_pay_num / dau` |
| `new_pay_arpu` | DAU ARPU | `charge / dau` |

---

## 8. 渠道统计V2

**路由**：`/system/channelV2`
**控制器**：`SystemController::channelV2Action`（权限：`/systemChannelV2`）
**数据仓库**：`ReportRepository::getChannelV2`
**主数据表**：`report_channel_day_log_v2`
**定时任务**：`channelTotalV2 channelOldDayTotal`（凌晨1点重跑）/ `channelTotalV2 channelMinuteTotal`（每2小时）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_channel_day_log_v2` | 渠道日报V2离线汇总表 |

#### 计算来源表（ETL 实际读取，`ChannelTotalOldDayV2Job` → `ReportChannelDayLogV2Service`）

| 表名 | 贡献指标 |
|------|----------|
| `app_log` | `dau_account_num`/`pay_dau_account_num`（活跃/活跃付费账号） |
| `user` | `reg`（注册） |
| `user_download` | `download_num`（下载） |
| `user_charge` | `new_pay_total`/`active_pay_num`/`active_pay_total`、`spend`/`spend_num`（投诉扣款，`complaint_time`+`status=2`）、`charge`/`charge_num`（充值）、`reg_pay_num`/`reg_pay_total`、`retain_pay_num`/`retain_pay_total` |

> 与 [渠道统计（V1）](#7-渠道统计v1) 不同，V2 版本无「消费金额」口径，不读取 `user_spend`。

#### `report_channel_day_log_v2` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{channel}_{date}` 的md5值 |
| `date` | 日期 |
| `channel` | 渠道名称 |
| `reg` | 新增账号 |
| `dau_account_num` | 活跃账号（去重） |
| `pay_dau_account_num` | 活跃付费账号 |
| `new_pay_num` | 当日付费账号 |
| `reg_pay_num` / `reg_pay_total` | 新增付费账号/金额 |
| `new_pay_total` | 活跃付费金额（当日总付费金额） |
| `old_active_num` | 次留人数 |
| `download_num` | 下载数量 |
| `spend_num` / `spend` | 投诉扣款订单数/金额 |
| `created_at` / `updated_at` | 创建/更新时间 |

> 页面展示的 `charge`/`charge_num` 由 `reg_pay_total`、`new_pay_total` 等派生计算。

### 功能说明

渠道统计的升级版本，增加了 DAU 付费口径、活跃付费、消费维度，次留率通过关联次日记录计算。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `code` | 渠道码 |
| `start_time` / `end_time` | 日期范围 |

### 展示字段

| 字段 | 说明 | 口径 |
|------|------|------|
| `date` | 统计日期 | — |
| `channel` | 渠道码 | — |
| `reg` | 新注册数 | — |
| `dau_account_num` | 日活账号数 | — |
| `pay_dau_account_num` | 付费DAU账号数 | — |
| `new_pay_num` | 当日新增付费人数 | — |
| `active_pay_num` | 活跃付费人数 | — |
| `active_pay_total` | 活跃付费金额（元） | — |
| `reg_pay_num` | 注册付费人数 | — |
| `reg_pay_total` | 注册付费金额（元） | — |
| `new_pay_total` | 新增付费金额（元） | — |
| `old_active_num` | 次日回访用户数（用于次留率分子） | — |
| `download_num` | 下载次数 | — |
| `spend_num` | 消费人次 | — |
| `spend` | 消耗平台币（G点） | — |
| `charge_num` | 充值次数 | — |
| `charge` | 充值金额（元） | — |
| `old_active` | **次留率** | 取**次日**记录的 `old_active_num` / 当日 `reg` × 100%（批量关联查询） |
| `reg_pay_rate` | 注册付费率 | `reg_pay_num / reg × 100%` |
| `reg_pay_arpu` | 注册ARPU | `reg_pay_total / reg` |
| `reg_pay_arppu` | 注册ARPPU | `reg_pay_total / reg_pay_num` |
| `dau_pay_rate` | DAU付费率 | `active_pay_num / dau_account_num × 100%` |
| `dau_pay_arpu` | DAU ARPU | `active_pay_total / dau_account_num` |
| `dau_pay_arppu` | DAU ARPPU | `active_pay_total / active_pay_num` |

---

## 9. 渠道注册留存

**路由**：`/system/channelRetention`
**控制器**：`SystemController::channelRetentionAction`（权限：`/systemChannelRetention`）
**数据仓库**：`ReportRepository::getChannelRetent`
**主数据表**：`report_channel_retention_daily_log`
**定时任务**：`channelTotalV2 channelRetention`（凌晨6点）/ `channelTotalV2 channelRetentionMinute`（每2小时）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_channel_retention_daily_log` | 渠道注册留存离线汇总表 |

#### 计算来源表（ETL 实际读取，`ChannelRetentionDnJob`）

| 表名 | 贡献指标 |
|------|----------|
| `user` | `reg_users`（cohort当日注册账号数，按渠道分组） |
| `app_log` | `d1`~`d30`（按 `register_date`+`date` 匹配判断次日~30日回访） |

#### `report_channel_retention_daily_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{date}_{channel}` 的md5值 |
| `date` | 注册日期（cohort日期） |
| `channel` | 渠道码 |
| `reg_users` | 新增账号数 |
| `d1`~`d7`,`d14`,`d30` | D1~D30留存人数 |
| `d1_rate`~`d7_rate`,`d14_rate`,`d30_rate` | D1~D30留存率 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

以渠道×注册日期（cohort）为维度，展示该批注册用户在 D1~D30 的次日留存率。

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 注册日期（cohort日期） |
| `channel` | 渠道码 |
| `reg` | 当日注册人数 |
| `d1` ~ `d30` | D1~D30留存人数（绝对值） |
| `d1_rate` ~ `d30_rate` | D1~D30留存率 = dN / reg × 100% |

---

## 10. 渠道注册LTV

**路由**：`/system/channelLtv`
**控制器**：`SystemController::channelLtvAction`（权限：`/systemChannelLtv`）
**数据仓库**：`ReportRepository::getChannelLtv`
**主数据表**：`report_channel_ltv_daily_log`
**定时任务**：`channelTotalV2 channelLtv`（凌晨4点）/ `channelTotalV2 channelLtvMinute`（每2小时）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_channel_ltv_daily_log` | 渠道注册LTV离线汇总表 |

#### 计算来源表（ETL 实际读取，`ChannelLtvJob`）

| 表名 | 贡献指标 |
|------|----------|
| `user` | `reg_users`（cohort当日注册账号数，按渠道分组） |
| `user_spend` | `d1_amount`~`d30_amount`（累计消费金额，游戏内/单机购买口径，**不是** `user_charge` 充值金额） |

#### `report_channel_ltv_daily_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{date}_{channel}` 的md5值 |
| `date` | 注册日期（cohort日期） |
| `channel` | 渠道码 |
| `reg_users` | 新增账号数 |
| `d1_amount`~`d7_amount`,`d14_amount`,`d30_amount` | D1~D30累计消费金额 |
| `d1`~`d7`,`d14`,`d30` | D1~D30消费LTV（人均） |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

以渠道×注册日期（cohort）为维度，展示注册后 D1~D30 的累计充值金额 / 人均LTV。

### 展示字段

| 字段 | 说明 | 单位 |
|------|------|------|
| `date` | 注册日期（cohort） | — |
| `channel` | 渠道码 | — |
| `reg` | 注册人数 | 人 |
| `d1_amount` ~ `d30_amount` | D1~D30 累计充值金额（原始G点，展示÷10=元） | 元 |
| `d1_ltv` ~ `d30_ltv` | 人均LTV = dN_amount / reg | 元/人 |

---

## 11. 游戏统计

**路由**：`/system/game`
**控制器**：`SystemController::gameAction`（权限：`/systemGame`）
**数据仓库**：`ReportRepository::getGame`
**主数据表**：`report_game_day_log`
**定时任务**：`GameTotal gameOldDayTotal`（凌晨1点重跑）/ `GameTotal gameMinuteTotal`（每2小时）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_game_day_log` | 游戏日报离线汇总表 |

#### 计算来源表（ETL 实际读取，`GameTotalOldDayJob` → `ReportGameDayLogService::getGameStatisticsBatch`）

| 表名 | 贡献指标 |
|------|----------|
| `app_log`（2025-11-27后）/ `report_game_adv_log`（历史） | `dau_account_num`/`pay_dau_account_num`/`old_active_num`/`dau`/`next_day_dau` |
| `user` | `reg`（按 `reg_game`+`register_at` 统计注册） |
| `user_download` | `download_num` |
| `user_charge` | `charge`（充值）、`spend`/`spend_num`（投诉扣款，`complaint_time`+`status=2`）、`order`/`order_success`、`new_pay_num`/`new_pay_total`、`first_pay_num`/`first_pay_total`、`reg_pay_num`/`reg_pay_total`、`retain_pay_num`/`retain_pay_total` |
| `user_spend` | `complaint`（消费金额，即游戏内购买/单机购买消费口径） |

#### `report_game_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{channel_name}_{date}` 的md5值 |
| `date` | 日期 |
| `game_id` | 游戏id |
| `dau_account_num` | 活跃账号 |
| `pay_dau_account_num` | 活跃付费账号 |
| `old_active_num` | 次留数 |
| `dau` / `next_day_dau` | 总日活/次日日活 |
| `reg` | 注册人数 |
| `total_reg` | 当月累计注册人数 |
| `download_num` | 下载数量 |
| `charge` | 充值金额 |
| `spend` / `spend_num` | 投诉扣款金额/订单数 |
| `complaint` | 消费金额 |
| `reg_pay_num` / `reg_pay_total` | 注册付费人数/金额 |
| `retain_pay_num` / `retain_pay_total` | 留存付费人数/金额 |
| `new_pay_num` / `new_pay_total` | 新增付费人数/金额 |
| `order` / `order_success` | 订单数/成功订单数 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

按游戏×日期维度统计注册、DAU、下载、充值、消耗、付费等核心指标。仅展示 `status=1`（上架）的游戏，支持按游戏类型筛选。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `game_id` | 游戏ID或名称（支持模糊名称解析） |
| `game_type` | 游戏类型（`1`=网络游戏，`2`=单机，`-1`=全部） |
| `start_time` / `end_time` | 日期范围 |

### 展示字段

| 字段 | 说明 | 口径 |
|------|------|------|
| `date` | 统计日期 | — |
| `game_id` | 游戏ID（含名称，格式：`游戏名（ID）`） | — |
| `reg` | 新注册用户数 | 当日通过该游戏注册的账号数 |
| `dau` | 日活跃用户数 | — |
| `next_day_dau` | 次日DAU | — |
| `download_num` | 下载次数 | — |
| `charge` | 充值金额（元） | — |
| `spend` | 消耗平台币（G点） | — |
| `complaint` | 投诉金额（元） | — |
| `reg_pay_num` | 新用户首日付费人数 | — |
| `reg_pay_total` | 新用户首日付费金额（元） | — |
| `retain_pay_num` | 老用户回流付费人数 | — |
| `retain_pay_total` | 老用户回流付费金额（元） | — |
| `first_pay_num` | 首次付费人数 | — |
| `first_pay_total` | 首次付费金额（元） | — |
| `new_pay_num` | 当日新增付费人数（DAU维度） | — |
| `total_reg` | **当月累计注册数** | `DB字段total_reg + 当日reg`（DB存的是截至昨天的月内累计） |
| `reg_pay_rate` | 新用户付费率 | `reg_pay_num / reg` |
| `reg_pay_arpu` | 新用户ARPU | `charge / reg` |
| `new_pay_rate` | DAU付费率 | `new_pay_num / dau` |
| `new_pay_arpu` | DAU ARPU | `charge / dau` |

---

## 12. 网络游戏统计

**路由**：`/system/networkGame`
**控制器**：`SystemController::networkGameAction`（权限：`/systemNetworkGame`）
**数据仓库**：`ReportRepository::getNetworkGame`
**主数据表**：`report_game_network_day_log`
**定时任务**：`GameTotal gameOldDayTotalV2`（凌晨5点）/ `GameTotal gameMinuteTotalV2`（每2小时）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_game_network_day_log` | 网络游戏日报离线汇总表 |

#### 计算来源表（ETL 实际读取，`GameTotalOldDayV2Job` → `ReportGameDayLogV2Service`）

| 表名 | 贡献指标 |
|------|----------|
| `app_log`（2025-11-27后）/ `report_game_adv_log`（历史） | `dau_account_num`/`pay_dau_account_num`/`old_active_num`/`dau`/`next_day_dau`，以及 **`reg`（注册，按 `register_date`+`date` 统计，与V1「游戏统计」不同，V2不读取 `user` 表）** |
| `user_download` | `download_num` |
| `user_charge` | `charge`/`charge_num`（充值）、`spend`/`spend_num`（投诉扣款）、`order`/`order_success` |
| `user_spend` | `reg_pay_num`/`reg_pay_total`、`retain_pay_num`/`retain_pay_total`、`new_pay_num`/`new_pay_total`、`first_pay_num`/`first_pay_total`（均为网络游戏内消费口径，`type=1`） |

> 注意：网络游戏统计的付费类指标（注册付费/留存付费/新增付费/首次付费）取自 `user_spend`（游戏内消费），充值/投诉取自 `user_charge`；与 [游戏统计](#11-游戏统计)（V1，付费类指标取自 `user_charge`）的口径不同。

#### `report_game_network_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{channel_name}_{date}` 的md5值 |
| `date` | 日期 |
| `game_id` | 游戏id |
| `dau_account_num` | 活跃账号 |
| `pay_dau_account_num` | 活跃付费账号 |
| `old_active_num` | 次留数 |
| `dau` / `next_day_dau` | 总日活/次日日活 |
| `reg` | 注册人数 |
| `total_reg` | 当月累计注册人数 |
| `download_num` | 下载数量 |
| `charge_num` / `charge` | 充值人数/金额 |
| `spend` / `spend_num` | 投诉扣款金额/订单数 |
| `complaint` | 消费金额 |
| `reg_pay_num` / `reg_pay_total` | 新用户付费人数/金额 |
| `retain_pay_num` / `retain_pay_total` | 留存付费人数/金额 |
| `new_pay_num` / `new_pay_total` | 新增付费人数/金额 |
| `order` / `order_success` | 订单数/成功订单数 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

专门针对**网络游戏**（`game.type=1`）的日报统计，字段覆盖比「游戏统计」更丰富，金额字段以元（÷10 G点）展示。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `game_id` | 游戏ID或名称 |
| `start_time` / `end_time` | 日期范围 |

### 展示字段

| 字段 | 说明 | 单位 |
|------|------|------|
| `date` | 统计日期 | — |
| `game_id` | 游戏ID（含名称） | — |
| `reg` | 新注册数 | 人 |
| `dau_account_num` | 日活账号数 | 人 |
| `pay_dau_account_num` | 付费DAU账号数 | 人 |
| `download_num` | 下载次数 | 次 |
| `charge` | 充值金额 | 元 |
| `charge_num` | 充值次数 | 次 |
| `spend` | 消耗平台币 | G点（原始值） |
| `complaint` | 投诉金额 | 元 |
| `reg_pay_num` | 新用户付费人数 | 人 |
| `reg_pay_total` | 新用户付费金额 | 元 |
| `old_active` | **次留率** | % = 次日活跃回归用户 / 当日reg × 100% |
| `reg_pay_rate` | 注册付费率 | `reg_pay_num / reg × 100%` |
| `reg_pay_arpu` | 注册ARPU | `reg_pay_total / reg` |
| `reg_pay_arppu` | 注册ARPPU | `reg_pay_total / reg_pay_num` |
| `dau_pay_rate` | DAU付费率 | `pay_dau_account_num / dau_account_num × 100%` |
| `dau_pay_arpu` | DAU ARPU | `charge / dau_account_num` |
| `dau_pay_arppu` | DAU ARPPU | `charge / pay_dau_account_num` |

---

## 13. 游戏渠道统计

**路由**：`/system/gameChannel`
**控制器**：`SystemController::gameChannelAction`（权限：`/systemGameChannel`）
**数据仓库**：`ReportRepository::getGameChannel`
**主数据表**：`report_game_channel_day_log`
**定时任务**：`gameTotal gameChannelOldDayTotal`（凌晨4点）/ `gameTotal gameChannelMinuteTotal`（每2小时）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_game_channel_day_log` | 游戏×渠道日报离线汇总表 |

#### 计算来源表（ETL 实际读取，`GameChannelTotalOldDayJob` → `ReportChannelGameDayLogService`）

| 表名 | 贡献指标 |
|------|----------|
| `app_log` | `dau_account_num`/`pay_dau_account_num`/`old_active_num`、`reg`（按游戏×渠道分组） |
| `user_download` | `download_num` |
| `user_charge` | `charge`/`charge_num`（充值）、`spend`/`spend_num`（投诉扣款）、`order`/`order_success` |
| `user_spend` | `reg_pay_num`/`reg_pay_total`、`retain_pay_num`/`retain_pay_total`（网络游戏内消费口径） |

#### `report_game_channel_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{channel_name}_{date}` 的md5值 |
| `date` | 日期 |
| `channel` | 渠道码 |
| `game_id` | 游戏id |
| `dau_account_num` | 活跃账号 |
| `pay_dau_account_num` | 活跃付费账号 |
| `old_active_num` | 次留数 |
| `dau` / `next_day_dau` | 总日活/次日日活 |
| `reg` | 注册人数 |
| `total_reg` | 当月累计注册人数 |
| `download_num` | 下载数量 |
| `charge` / `charge_num` | 充值金额/人数 |
| `spend` / `spend_num` | 投诉扣款金额/订单数 |
| `complaint` | 消费金额 |
| `reg_pay_num` / `reg_pay_total` | 注册付费人数/金额 |
| `retain_pay_num` / `retain_pay_total` | 留存付费人数/金额 |
| `new_pay_num` / `new_pay_total` | 新增付费人数/金额 |
| `order` / `order_success` | 订单数/成功订单数 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

以 **游戏ID × 渠道码** 双维度统计各渠道在每款网络游戏内的运营数据，字段与「网络游戏统计」一致。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `game_id` | 游戏ID或名称 |
| `channel` | 渠道码 |
| `start_time` / `end_time` | 日期范围 |

### 展示字段

与「网络游戏统计」基本一致，额外包含：
- `channel`：渠道码维度

---

## 14. 游戏注册留存

**路由**：`/system/gameRetention`
**控制器**：`SystemController::gameRetentionAction`（权限：`/systemGameRetention`）
**数据仓库**：`ReportRepository::getGameRetent`
**主数据表**：`report_game_retention_daily_log`
**定时任务**：`GameTotal gameRetentionDu`（凌晨6点）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_game_retention_daily_log` | 游戏注册留存离线汇总表 |

#### 计算来源表（ETL 实际读取，`GameRetentionDnJob`）

| 表名 | 贡献指标 |
|------|----------|
| `game` | 圈定统计的游戏范围 |
| `app_log` | `reg_users`/`new_reg_users`（注册基数）、`d1`~`d30`（留存，按 `register_date`+`date` 匹配） |

#### `report_game_retention_daily_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{game_id}_{date}` 的md5值 |
| `date` | 日期 |
| `game_id` | 游戏id |
| `reg_users` | 总注册 |
| `new_reg_users` | 新注册 |
| `d1`~`d7`,`d14`,`d30` | D1~D30留存人数 |
| `d1_rate`~`d7_rate`,`d14_rate`,`d30_rate` | D1~D30留存率 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

以 **游戏ID × 注册日期（cohort）** 为维度，展示注册用户在 D1~D30 的留存率。

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 注册日期（cohort） |
| `game_id` | 游戏ID（含名称） |
| `reg` | 当日注册人数 |
| `d1` ~ `d30` | D1~D30留存人数 |
| `d1_rate` ~ `d30_rate` | D1~D30留存率 = dN / reg × 100% |

---

## 15. 游戏注册LTV

**路由**：`/system/gameLtv`
**控制器**：`SystemController::gameLtvAction`（权限：`/systemGameLtv`）
**数据仓库**：`ReportRepository::getGameLtv`
**主数据表**：`report_game_ltv_daily_log`
**定时任务**：`GameTotal gameLtv`（凌晨4点）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_game_ltv_daily_log` | 游戏注册LTV离线汇总表 |

#### 计算来源表（ETL 实际读取，`GameLtvJob`）

| 表名 | 贡献指标 |
|------|----------|
| `game` | 圈定统计的游戏范围 |
| `app_log` | `reg_users`/`new_reg_users`（注册基数） |
| `user_spend` | `d1_amount`~`d30_amount`（累计消费金额，游戏内消费口径，**不是** `user_charge` 充值金额） |

#### `report_game_ltv_daily_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{date}_{game_id}` 的md5值 |
| `date` | 日期（cohort日期） |
| `game_id` | 游戏id |
| `reg_users` | 总注册 |
| `new_reg_users` | 新注册 |
| `d1_amount`~`d7_amount`,`d14_amount`,`d30_amount` | D1~D30累计充值金额 |
| `d1`~`d7`,`d14`,`d30` | D1~D30人均LTV |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

以 **游戏ID × 注册日期（cohort）** 为维度，展示 D1~D30 累计充值金额及人均LTV。

### 展示字段

| 字段 | 说明 | 单位 |
|------|------|------|
| `date` | 注册日期（cohort） | — |
| `game_id` | 游戏ID（含名称） | — |
| `reg` | 注册人数 | 人 |
| `d1_amount` ~ `d30_amount` | D1~D30 累计充值金额（G点÷10→元） | 元 |
| `d1_ltv` ~ `d30_ltv` | 人均LTV = dN_amount / reg | 元/人 |

---

## 16. 单机游戏统计

**路由**：`/system/singleGame`
**控制器**：`SystemController::singleGameAction`（权限：`/systemSingleGame`）
**数据仓库**：`ReportRepository::getSingleGame`
**主数据表**：`report_single_game_day_log`（仅 `game.type='2'` 单机游戏）
**定时任务**：`gameTotal singleGameMinuteTotal`（每2小时）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_single_game_day_log` | 单机游戏日报离线汇总表 |
| `game` | 关联取游戏名称（`type='2'`），字段详见 [平台币消耗去向](#37-平台币消耗去向) |

#### 计算来源表（ETL 实际读取，`SingleGameTotalOldDayJob` → `ReportSingleGameDayLogService`）

| 表名 | 贡献指标 |
|------|----------|
| `page_visit_log` | `detail_uv`（详情页访问UV，按 `page_params` 关联游戏ID） |
| `user_spend` | `buy_account_num`/`buy_amount`（购买账号数/金额，`type=2` 单机游戏购买） |
| `user_charge` | `complaint_amount`（投诉扣款金额，`complaint_time`+`status=2`） |
| `user_download` | `download_uv`/`download_count` |

#### `report_single_game_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`md5({date}_{game_id})` |
| `date` | 日期 |
| `game_id` | 游戏id |
| `detail_uv` | 详情页访问UV |
| `buy_account_num` | 购买账号数 |
| `buy_amount` | 购买金额 |
| `complaint_amount` | 投诉扣款金额 |
| `net_amount` | 净购买金额 |
| `download_uv` | 下载请求UV |
| `download_count` | 下载请求数 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

统计单机游戏的购买转化漏斗，聚焦从详情页浏览 → 购买 → 投诉的转化链路。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `game_id` | 游戏ID |
| `start_time` / `end_time` | 日期范围 |

### 展示字段

| 字段 | 说明 | 口径 |
|------|------|------|
| `date` | 统计日期 | — |
| `game_name` | 游戏名称（含ID） | 关联 `game.title`，仅取 `type='2'` |
| `detail_uv` | 详情页访问UV | — |
| `buy_account_num` | 购买账号数 | — |
| `buy_amount` | 购买金额（元） | — |
| `complaint_amount` | 投诉金额（元） | — |
| `net_amount` | 净收入 = `buy_amount - complaint_amount` | 元 |
| `download_uv` | 下载UV | — |
| `download_count` | 下载次数 | — |
| `buy_convert_rate` | 购买转化率 | `buy_account_num / detail_uv × 100%` |
| `download_rate` | 下载率 | `download_uv / buy_account_num × 100%` |

---

## 17. 套餐统计

**路由**：`/system/combo`
**控制器**：`SystemController::comboAction`（权限：`/systemCombo`）
**数据仓库**：`ReportRepository::getCombo`
**主数据表**：`report_combo_total_day_log`
**定时任务**：`total totalVipOrCoinOldDay`（凌晨4点重跑）/ `total totalVipOrCoinMinute`（每小时）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_combo_total_day_log` | 套餐日报离线汇总表 |
| `user_group` | VIP套餐配置表（`type=1` 时关联取套餐名称，也是遍历 VIP 套餐的基准表） |
| `user_product` | G点套餐配置表（`type=0` 时关联取套餐名称，也是遍历金币套餐的基准表） |

#### 计算来源表（ETL 实际读取，`VipOrCoinTotalOldDayJob::vipCount`/`productCount`）

| 表名 | 贡献指标 |
|------|----------|
| `user_charge` | `charge`/`true_charge`（充值/实际到账金额）、`total_order`/`total_order_success`、`order_user_count`（按 `product_id`+`is_vip` 分组） |
| `product_click_stat` | `click_count`/`click_user_count`（点击次数/点击人数，按 `product_id`+`type` 分组） |

#### `report_combo_total_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `date` | 日期 |
| `combo_id` | 套餐id |
| `type` | 类型：1会员套餐 2金币套餐 |
| `charge` / `true_charge` | 充值金额/实际充值金额 |
| `total_order` / `total_order_success` | 订单数/成功订单数 |
| `click_count` / `click_user_count` | 点击次数/点击人数 |
| `avg_click_per_user` | 人均点击次数 |
| `order_user_count` | 下单人数 |
| `order_conversion_rate` | 下单转化率(%) |
| `created_at` / `updated_at` | 创建/更新时间 |

#### `user_group` 字段（节选）

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `name` | 名称 |
| `level` | 会员类型：1vip会员 2特权会员 |
| `price` / `old_price` | 价格/原价 |
| `day_num` | 可用天数 |

#### `user_product` 字段（节选）

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `name` | 套餐名称 |
| `type` | 类型：point金币 |
| `num` / `gift_num` | 数量/赠送数量 |
| `price` / `original_price` | 价格/原价（划线价） |

### 功能说明

统计各充值套餐（G点套餐 / VIP套餐）的曝光点击、下单、成功支付指标，评估套餐转化效果。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `combo_id` | 套餐ID |
| `type` | 套餐类型：`0`=G点套餐（金币），`1`=VIP套餐 |
| `start_time` / `end_time` | 日期范围 |

### 展示字段

| 字段 | 说明 | 口径 |
|------|------|------|
| `date` | 统计日期 | — |
| `combo_id` | 套餐ID | — |
| `combo_name` | 套餐名称 | `type=1` 从 `UserGroupModel` 关联，`type=0` 从 `UserProductModel` 关联 |
| `type` | 套餐类型 | 0=G点，1=VIP |
| `click_count` | 点击次数（PV） | — |
| `click_user_count` | 点击用户数（UV） | — |
| `order_user_count` | 下单用户数 | — |
| `total_order` | 下单总次数 | — |
| `total_order_success` | 支付成功次数 | — |
| `charge` | 下单总金额（元） | — |
| `true_charge` | 实际到账金额（元） | — |
| `order_rate` | 订单成功率 | `total_order_success / total_order × 100%` |
| `avg_click_per_user` | 人均点击次数 | `click_count / click_user_count` |
| `order_conversion_rate` | 点击→下单转化率 | `order_user_count / click_user_count × 100%` |
| `unit_price` | 实付客单价 | `true_charge / total_order_success` |
| `buy_unit_price` | 订单客单价 | `charge / total_order_success` |

---

## 18. AB测试统计

**路由**：`/system/abLog`
**控制器**：`SystemController::abLogAction`（权限：`/systemAbLog`）
**数据仓库**：`ReportRepository::getAbLog`
**主数据表**：`report_ab_day_log`
**定时任务**：`total totalAbDay`（每3小时）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_ab_day_log` | AB测试日报离线汇总表 |
| `ab_test_config` | 实验配置表，关联取实验名称等，也是遍历实验的基准表 |
| `user_group` / `user_product` | 商品名称关联（`is_vip=1`/`is_vip=0`），字段详见 [套餐统计](#17-套餐统计) |

#### 计算来源表（ETL 实际读取，`AbTotalOldDayJob` → `ReportAbDayLogService::getAbDataAndDate`/`getTrackingStat`）

| 表名 | 贡献指标 |
|------|----------|
| `user_charge` | `charge`/`total_charge`/`true_charge`（充值金额）、`order`/`order_success`、`total_charge_num`/`true_charge_num`（按 `product_id`+`is_vip`+`user_id_last`奇偶分流过滤） |
| `product_click_stat` | `click_num`/`click_user_num`（点击次数/点击人数） |

#### `report_ab_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号的md5值 |
| `ab_group_type` | AB类型：1套餐 2广告 |
| `ab_config_id` | AB测试配置id |
| `ab_type` | 套餐子类型 |
| `ab_code` | AB测试标识 |
| `ab_odd_even` | 奇偶分流 |
| `is_vip` | 是否VIP商品 |
| `product_id` | 套餐id |
| `click_num` / `click_user_num` | 点击次数/点击人数 |
| `charge` | 充值有效金额 |
| `total_charge` / `total_charge_num` | 总下单金额/总下单人数 |
| `true_charge` / `true_charge_num` | 真实有效金额/真实有效下单人数 |
| `order` / `order_success` | 订单数/成功订单数 |
| `created_at` / `updated_at` | 创建/更新时间 |

#### `ab_test_config` 字段（节选）

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `ab_group_type` | 实验类型：1套餐 2广告 |
| `type` | 套餐类型：0金币 1会员 |
| `title` | 实验标题 |
| `code` | 实验标识（随机生成） |
| `odd_even` | 奇数/偶数分流 |
| `status` | 状态：0草稿 1运行 2暂停 3结束 |

### 功能说明

展示各 AB 测试实验的每日效果数据，支持按实验组类型、奇偶分组、VIP/G点类型、实验编码等多维筛选。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `ab_group_type` | AB组类型：`1`=套餐实验（PRODUCT_GROUP），`2`=广告实验 |
| `ab_odd_even` | 奇偶分组：`1`=奇数用户，`2`=偶数用户 |
| `is_vip` | 套餐类型：`0`=G点，`1`=VIP会员 |
| `ab_type` | 实验类型编码 |
| `ab_code` | 实验代码 |
| `start_time` / `end_time` | 日期范围 |

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 统计日期 |
| `ab_config_id` | AB实验配置ID |
| `ab_title` | 实验名称（关联 `ab_test_config.title`） |
| `ab_group_type` | 实验组类型（1=套餐/2=广告） |
| `ab_odd_even` | 奇偶分组 |
| `is_vip` | 商品类型（0=G点/1=VIP） |
| `product_id` | 商品ID |
| `product_name` | 商品名称（`is_vip=0` 从 `user_product` 关联，`is_vip=1` 从 `user_group` 关联） |
| `ab_type` | 实验类型 |
| `ab_code` | 实验编码 |
| 其他统计字段 | 各指标数据（曝光、点击、转化等，依实验类型不同） |

---

## 19. 留存统计（DAU）

**路由**：`/system/dau`
**控制器**：`SystemController::dauAction`（权限：`/systemDau`）
**数据仓库**：`ReportRepository::getDau`
**主数据表**：`report_dau_log`
**定时任务**：`total totalMinute`（每小时）/ `total totalOldDay`（凌晨2点重跑）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_dau_log` | 全平台日活/留存离线汇总表，由 `ReportServerJob` 写入（非 `TotalOldDayJob`） |

#### 计算来源表（ETL 实际读取，`ReportServerJob`）

| 表名 | 贡献指标 |
|------|----------|
| `user` | `reg`（当日注册，按 `register_date`） |
| `app_log` | `active_1`~`active_30`（按 `register_date`+`date` 匹配统计各日留存活跃数） |

#### `report_dau_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{date}` |
| `reg` | 当日注册总数 |
| `active_1`~`active_7`,`active_15`,`active_30` | 1/2/3/4/5/6/7/15/30日活跃总数（留存） |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

展示全平台每日活跃用户数（DAU）及多日留存趋势。

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 统计日期 |
| `dau` | 当日活跃账号数 |
| `d1` / `d3` / `d7` / `d30` | 各阶段留存人数 |
| `d1_rate` / `d3_rate` / `d7_rate` / `d30_rate` | 各阶段留存率 |

---

## 20. 小时统计

**路由**：`/system/hour`
**控制器**：`SystemController::hourAction`（权限：`/systemHour`）
**数据仓库**：`ReportRepository::getHour`
**主数据表**：`report_hour_log`
**定时任务**：`HourlyStatsMonitor monitor`（每小时整点）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_hour_log` | 小时级统计离线汇总表（`pid=0` 为日级摘要行，其余为小时明细行） |

#### 计算来源表（ETL 实际读取，`ReportHourJob`）

| 表名 | 贡献指标 |
|------|----------|
| `user` | `reg_android`/`reg_ios`/`reg_web`（按 `device_type`+`register_at` 统计） |
| `app_log` | `dau_android`/`dau_ios`/`dau_web`（按 `device_type`+`created_at` 统计） |
| `user_order` | `order`（VIP订单数，取 `user_order` 集合而非 `user_charge`） |
| `user_recharge` | `order_money`/`order_success`（充值订单金额及成功数，取 `user_recharge` 集合） |

> 注意：本报表与「充值统计」类报表口径不同，直接来源于 `user_order`/`user_recharge` 两张独立订单表，而非 `user_charge`。

#### `report_hour_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `dau` / `dau_android` / `dau_ios` / `dau_web` | 总日活/安卓/iOS/Web日活 |
| `reg` / `reg_android` / `reg_ios` / `reg_web` | 总注册/安卓/iOS/Web注册 |
| `order` / `order_success` | 订单数/成功订单数 |
| `order_money` | 订单金额 |
| `tav` | 客单价 |
| `apr` | 日付费率 |
| `payr` | 支付成功率 |
| `arpu` | 用户平均收入 |
| `month` | 年月 |
| `date` | 日期 |
| `date_limit` | 时间范围（小时明细） |
| `pid` | 上级id（`0`=日级摘要行） |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

按小时粒度统计平台关键指标，支持两级展示：日级（`pid=0`）和小时展开（`pid=日期记录ID`）。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `month` | 月份（`YYYY-MM`格式） |
| `pid` | `0`=只看日级摘要行，其他值=展开该日的小时明细 |

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 日期（`pid=0` 时）或 小时时间段（展开时显示 `date_limit`） |
| `dau` | 活跃用户数 |
| `dau_android` | Android活跃数 |
| `dau_web` | Web/H5活跃数 |
| `reg` | 新注册数 |
| `reg_android` | Android注册数 |
| `reg_web` | Web/H5注册数 |
| `order` | 订单数 |
| `order_success` | 成功订单数 |
| `order_money` | 充值金额（元） |
| `tav` | 平台总访问量（TAV） |
| `apr` | 活跃付费率（%） |
| `payr` | 付费率（%） |
| `arpu` | ARPU（元） |
| `haveChild` | 是否有小时明细子记录（`true`/`false`） |

---

## 21. 活跃列表

**路由**：`/system/appLog`
**控制器**：`SystemController::appLogAction`（权限：`/systemAppLog`）
**数据仓库**：`ReportRepository::geAppLog`
**主数据表**：`app_log`（原始应用活跃日志）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `app_log` | 用户应用活跃原始日志（写入方为埋点上报） |

#### `app_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `user_id` | 用户编号 |
| `date` / `month` | 日期/月份 |
| `channel_name` | 渠道 |
| `device_type` / `device_type_new` | 设备类型/设备类型（新兼容报表） |
| `register_date` | 注册日期 |
| `jet_lag` | 从注册之日到该条数据距离天数（0当日，1次日……） |
| `ip` | IP |
| `game_id` | 游戏id |
| `is_pay` | 是否充值过：1是 0否 |
| `is_test` | 是否测试账号：1是 0否 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

查询用户的应用活跃原始日志明细，按用户/时间筛选，用于排查单用户行为。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `user_id` | 用户ID |
| `start_time` / `end_time` | 时间范围 |

---

## 22. 游戏下载列表

**路由**：`/system/gameDownload`
**控制器**：`SystemController::gameDownloadAction`（权限：`/systemGameDownload`）
**数据仓库**：`ReportRepository::getGameDownloadAction`
**主数据表**：`user_download`（用户下载记录）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `user_download` | 已登录用户游戏下载记录表 |

#### `user_download` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `user_id` | 用户id |
| `game_id` | 游戏id |
| `platform` | 平台 |
| `register_at` | 注册时间 |
| `channel_name` | 渠道 |
| `device_type_new` | 设备信息 |
| `created_at` / `update_at` | 创建/修改时间 |

### 功能说明

查询已登录用户的游戏下载明细记录，支持多维筛选。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `user_id` | 用户ID |
| `game_id` | 游戏ID |
| `platform` | 平台类型（`CommonValues::getPlatformOptions()`） |
| `start_time` / `end_time` | 下载时间范围 |

---

## 23. 特权会员游戏下载

**路由**：`/system/gameVipDownload`
**控制器**：`SystemController::gameVipDownloadAction`（权限：`/systemGameVipDownload`）
**数据仓库**：`ReportRepository::getGameVipDownloadAction`
**主数据表**：`user_vip_download`（VIP会员专属下载记录）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `user_vip_download` | 特权VIP用户下载记录表 |

#### `user_vip_download` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `user_id` | 用户id |
| `date` | 日期 |
| `game_id` | 游戏id |
| `platform` | 平台 |
| `download_vip_id` | 特权会员id |
| `register_at` | 注册时间 |
| `channel_name` | 渠道 |
| `created_at` / `update_at` | 创建/修改时间 |

### 功能说明

统计特权会员（VIP）通过会员权益免费下载游戏的明细记录。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `user_id` | 用户ID |
| `game_id` | 游戏ID |
| `platform` | 平台类型 |
| `start_time` / `end_time` | 下载时间范围 |

---

## 24. 游戏预约统计

**路由**：`/system/gameReserve`
**控制器**：`SystemController::gameReserveAction`（权限：`/systemGameReserve`）
**数据仓库**：`GameReserveRepository::getReserveStat`

### 数据来源表

| 表名 | 说明 |
|------|------|
| `game_reserve` | 游戏预约记录表 |
| `game` | 关联取游戏名称，字段详见 [平台币消耗去向](#37-平台币消耗去向) |

#### `game_reserve` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `user_id` | 用户ID |
| `game_id` | 游戏ID |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

展示各游戏的用户预约数量统计，以及预约用户明细（通过 `/system/gameReserveDetail` 查看）。
支持点击具体游戏查看预约用户列表（`GameReserveRepository::getReserveDetail`）。

### 展示字段（汇总）

| 字段 | 说明 |
|------|------|
| `game_id` | 游戏ID |
| `game_name` | 游戏名称 |
| `reserve_count` | 预约总人数 |
| `date_range` | 预约统计日期范围 |

---

## 25. 视频统计

**路由**：`/system/movie`
**控制器**：`SystemController::movieAction`（权限：`/systemMovie`）
**数据仓库**：`ReportRepository::getMovie`
**主数据表**：`report_movie_log`

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_movie_log` | 视频每日点击/点赞/收藏统计表（`movie_id_日期` 为主键），由 `ReportMovieLogService` 累加写入 |
| `movie` | 视频基础信息表，关联取视频名称 |

#### `report_movie_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | `{movie_id}_{date}` |
| `movie_id` | 视频ID |
| `name` | 视频名称 |
| `label` | 统计日期（Y-m-d） |
| `click` | 点击（播放）次数 |
| `love` | 点赞次数 |
| `favorite` | 收藏次数 |
| `buy_num` / `buy_total` | 购买次数/购买金额 |
| `download` | 下载次数 |

### 功能说明

统计平台视频内容的播放、互动等数据，支持按排行类型筛选（`CommonValues::getRankingType()`）。

---

## 26. 漫画统计

**路由**：`/system/comics`
**控制器**：`SystemController::comicsAction`（权限：`/systemComics`）
**数据仓库**：`ReportRepository::getComics`
**主数据表**：`report_comics_log`

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_comics_log` | 漫画每日点击/点赞/收藏统计表（`comics_id_日期` 为主键），由 `ReportComicsLogService` 累加写入 |
| `comics` | 漫画基础信息表，关联取漫画名称 |

#### `report_comics_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | `{comics_id}_{date}` |
| `comics_id` | 漫画ID |
| `name` | 漫画名称 |
| `label` | 统计日期（Y-m-d） |
| `click` | 点击（阅读）次数 |
| `love` | 点赞次数 |
| `favorite` | 收藏次数 |

### 功能说明

统计平台漫画内容的阅读、互动等数据，支持按排行类型筛选（`CommonValues::getRankingType()`）。

---

## 27. 广告统计

**路由**：`/system/adv`
**控制器**：`SystemController::advAction`（权限：`/systemAdv`）
**数据仓库**：`ReportRepository::getAdv`
**主数据表**：`report_adv_log`

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_adv_log` | 广告点击日志表 |

#### `report_adv_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `adv_id` | 广告id |
| `name` | 广告名称 |
| `label` | 日期 |
| `click` | 点击次数 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

统计平台广告位的曝光/点击数据，支持按排行类型筛选（`CommonValues::getRankingType()`）。

---

## 28. 老司机AI汇总统计

**路由**：`/system/reportAiTotal`
**控制器**：`SystemController::reportAiTotalAction`
**数据仓库**：`ReportRepository::getReportAiDayStats`
**数据来源**：`UserLsjAiService::queryDayStats()`
**定时任务**：`Crontab LsjAiDailyStats`（每天凌晨1点）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_lsjai_day` | 离线日汇总表，由 `UserLsjAiService::generateDailyStats()` 按 `date+type` 聚合写入 |
| `user_lsj_ai_log` | 原始进出记录表，聚合的数据源 |

#### `report_lsjai_day` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`{date}` 的md5值 |
| `date` | 日期 |
| `type` | 业务类型（对应 `user_lsj_ai_log.type`） |
| `total_sessions` | 总会话数 |
| `total_in` | 总带入资金（G点） |
| `total_out` | 总带出资金（已换算为G点） |
| `total_diff` | 总差额（`total_in - total_out`） |
| `created_at` / `updated_at` | 创建/更新时间 |

#### `user_lsj_ai_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `user_id` | 用户ID |
| `type` | AI类型：1-ai女友，2-工具人 |
| `enter_time` / `exit_time` | 进入/退出时间 |
| `session_id` | 会话ID |
| `in_amount` | 带入金额（单位G点） |
| `out_amount` | 带出金额（单位CNY） |
| `game_id` | 游戏ID |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

汇总老司机AI功能的每日使用数据，支持按业务类型（`type`参数）筛选。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `type` | 统计类型（`0`=全部，其他值=具体业务类型） |
| `start_time` / `end_time` | 日期范围 |

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 统计日期 |
| `total_sessions` | 总会话数 |
| `total_in` | 总输入（G点转入） |
| `total_out` | 总输出（G点转出） |
| `total_diff` | 净差额（`total_in - total_out`） |

---

## 29. 活动埋点统计

**路由**：`/trackingStat/list`
**控制器**：`TrackingStatController::listAction`
**数据仓库**：`TrackingStatRepository`
**主数据表**：`tracking_stat`（`tracking_type ≠ '99'`）
**定时任务**：`trackingStat sync`（每小时整点，Redis→MongoDB同步）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `tracking_stat` | 埋点统计表，由 Redis 实时计数按小时同步落库 |
| `adv_pos` | 广告位配置表，关联取广告位名称 |

#### `tracking_stat` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 记录ID |
| `date` | 统计日期（Y-m-d） |
| `tracking_type` | 活动类型：1=盲盒 2=奖池 3=冲榜 99=游戏 |
| `position` | 曝光位置（`adv_pos.code`） |
| `game_id` | 关联游戏ID（可选） |
| `exposure_pv` / `exposure_uv` | 曝光PV/UV |
| `click_pv` / `click_uv` | 点击PV/UV |
| `download_pv` / `download_uv` | 下载PV/UV |
| `created_at` / `updated_at` | 创建/更新时间 |

#### `adv_pos` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `name` | 广告位名称 |
| `code` | 广告位标识 |
| `is_disabled` | 是否禁用 |
| `width` / `height` | 宽/高 |

### 功能说明

统计各活动类型在各广告位的曝光/点击数据，支持 PV/UV 两个维度，可导出 Excel。

### 筛选条件

| 参数 | 说明 |
|------|------|
| `start_date` / `end_date` | 日期范围 |
| `tracking_type` | 活动类型（`3` 时前缀匹配） |
| `position` | 广告位 code |

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 统计日期 |
| `tracking_type_name` | 活动类型名称（由 `TrackingService::getActivityTypeName` 映射） |
| `position_name` | 广告位名称（由 `adv_pos.code` → `adv_pos.name` 映射） |
| `exposure_pv` | 曝光PV（展示次数） |
| `exposure_uv` | 曝光UV（展示去重用户数） |
| `click_pv` | 点击PV（点击次数） |
| `click_uv` | 点击UV（点击去重用户数） |
| `pv_click_rate` | PV点击率 = `click_pv / exposure_pv × 100%` |
| `uv_click_rate` | UV点击率 = `click_uv / exposure_uv × 100%` |
| `created_at` / `updated_at` | 创建/更新时间 |

### 其他操作

- **导出 Excel**：`/trackingStat/excel`，最多导出 10 万条
- **手动同步**：`/trackingStat/sync`，将 Redis 实时数据落库

---

## 30. 游戏推广埋点统计

**路由**：`/trackingGameStat/list`
**控制器**：`TrackingGameStatController::listAction`
**数据仓库**：`TrackingGameStatRepository`
**主数据表**：`tracking_stat`（`tracking_type = '99'`）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `tracking_stat` | 埋点统计表（`tracking_type=99`），字段详见 [活动埋点统计](#29-活动埋点统计) |
| `adv_pos` | 广告位配置表，关联取广告位名称 |
| `game` | 关联取游戏名称 |

### 功能说明

专门统计游戏推广位（`tracking_type=99`）的曝光、点击、下载三阶段漏斗数据。

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 统计日期 |
| `position_name` | 广告位名称 |
| `game_id` / `game_name` | 游戏ID/名称 |
| `exposure_pv` | 曝光次数 |
| `click_pv` | 点击次数 |
| `download_pv` | 下载次数 |
| `ctr` | 曝光→点击率 = `click_pv / exposure_pv × 100%` |
| `click_to_download_rate` | 点击→下载率 = `download_pv / click_pv × 100%` |
| `exposure_to_download_rate` | 曝光→下载率 = `download_pv / exposure_pv × 100%` |

---

## 31. 页面访问统计

**路由**：`/pageVisitStat/list`
**控制器**：`PageVisitStatController::listAction`
**数据仓库**：`PageVisitStatRepository`
**主数据表**：`page_visit_stat`

### 数据来源表

| 表名 | 说明 |
|------|------|
| `page_visit_stat` | 页面访问统计表（按日期+页面+渠道+设备+访客类型聚合） |

#### `page_visit_stat` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 记录ID，`{date}_{md5(page\|channel_name\|device_type\|visitor_type)}` |
| `date` | 统计日期（Y-m-d） |
| `page` | 页面标识 |
| `channel_name` | 渠道标识 |
| `device_type_new` | 设备类型 |
| `visitor_type` | 访客类型（user/guest） |
| `pv` / `uv` | 访问PV/UV |
| `created_at` / `updated_at` | 创建/更新时间 |

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 统计日期 |
| `page` / `page_name` | 页面路径/名称 |
| `channel_name` | 渠道码 |
| `device_type_name` | 设备类型名称 |
| `visitor_type_name` | 「登录用户」/「游客」 |
| `pv` | 页面访问次数 |
| `uv` | 页面访问去重用户数 |

---

## 32. 页面访问日志明细

**路由**：`/pageVisitStat/pageVisitLog`
**主数据表**：`page_visit_log`（原始访问日志）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `page_visit_log` | 页面访问原始日志表 |

#### `page_visit_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 记录ID（ObjectId字符串） |
| `user_id` | 用户ID（已登录时有值，游客为0） |
| `guest_id` | 游客ID（`md5(deviceId:ip)`，已登录时为空） |
| `page` | 页面标识 |
| `channel_name` | 渠道标识 |
| `device_type_new` | 设备类型 |
| `ip` | 访问IP |
| `source_url` | 来源地址 |
| `page_params` | 页面访问参数 |
| `source_type` | 来源类型（0站内，1站外） |
| `created_at` | 访问时间 |

### 展示字段

| 字段 | 说明 |
|------|------|
| `guest_id` | 游客标识 |
| `user_id` / `username` | 用户ID/名称 |
| `is_registered_user` | `y`/`n` |
| `page_name` | 页面名称 |
| `channel_name` | 渠道码 |
| `device_type_name` | 设备类型名称 |
| `source_type_name` | 「站内」/「站外」 |
| `source_url` | 来源 URL |
| `created_at_text` | 访问时间（`Y-m-d H:i:s`） |

---

## 33. 未登录游戏下载统计

**路由**：`/gameDownloadStat/list`
**主数据表**：`game_download_stat`

### 数据来源表

| 表名 | 说明 |
|------|------|
| `game_download_stat` | 未登录用户游戏下载统计表（按日期+游戏+渠道聚合） |
| `game` | 关联取游戏名称 |

#### `game_download_stat` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 记录ID（`{date}_{game_id}_{encoded_channel}`；历史老数据无渠道段，为`{date}_{game_id}`） |
| `date` | 统计日期（Y-m-d） |
| `game_id` | 游戏ID |
| `channel` | 渠道码，前端未上报渠道时统一记为 `official`（历史老数据"官方"已回填为 `official`） |
| `download_count` | 下载次数 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 功能说明

统计**未登录用户（游客）**的游戏下载次数，按日期+游戏+渠道维度聚合。同一天同一游戏可能有多条记录（每渠道一条），如需总量需对 `download_count` 求和（见 `FunnelStatRepository::countGameDownloadStat`，已按 `$sum` 聚合，不受渠道拆分影响）。

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 统计日期 |
| `game_id` / `game_title` | 游戏ID/名称 |
| `channel` | 渠道（可筛选，不填=全部） |
| `download_count` | 下载次数 |

---

## 34. 商品点击统计

**路由**：`/productClickStat/list`
**主数据表**：`product_click_stat`

### 数据来源表

| 表名 | 说明 |
|------|------|
| `product_click_stat` | 套餐点击统计表（按日期+用户+套餐当日累计） |
| `user` | 关联取用户名，字段详见附录 F |
| `user_group` / `user_product` | 关联取商品名称（`type=1`/`type=0`），字段详见 [套餐统计](#17-套餐统计) |

#### `product_click_stat` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 记录ID |
| `date` | 统计日期（Y-m-d） |
| `user_id` | 用户ID |
| `user_id_last` | 用户ID最后一位，用于区分奇偶 |
| `type` | 套餐类型（0=金币 1=VIP） |
| `product_id` | 套餐ID |
| `click_num` | 点击次数（当天累计） |
| `created_at` / `updated_at` | 创建/更新时间 |

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 统计日期 |
| `user_id` / `username` | 用户ID/名称 |
| `type_name` | 「金币套餐」/「VIP套餐」 |
| `product_name` | 商品名称 |
| `click_num` | 点击次数 |

---

## 35. 平台币总览

**路由**：`/coinOverview/list`
**落库表**：`report_coin_overview_day_log`
**数据来源**：`account_detail`、`user_charge`
**定时任务**：`coin coinOverviewOldDay`（凌晨1点重跑）/ `coin coinOverviewMinute`（每2小时）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_coin_overview_day_log` | 平台币总览离线日报（落库表） |
| `account_detail` | 平台币流水明细，聚合来源，字段详见附录 B |
| `user_charge` | 充值订单表，`real_money` 聚合为充值购币金额，字段详见附录 E |

> 计算脚本：`CoinOverviewDayJob`（同一个 Job 类内也负责 [平台币原因结构](#36-平台币原因结构)、[平台币消耗去向](#37-平台币消耗去向)、[平台币余额快照](#38-平台币余额快照) 三张表的计算）。

#### `report_coin_overview_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 唯一编号，`md5(date)` |
| `date` | 日期（Y-m-d） |
| `earn_users` | 获得人数（去重账号数） |
| `earn_amount` | 获得平台币总量 |
| `charge_money` | 充值购币金额（人民币，来自 `user_charge.real_money`） |
| `charge_coin` | 充值获得平台币（`type=1`） |
| `gift_coin` | 赠送获得平台币（`type!=1，amount>0`） |
| `spend_users` | 消耗人数（去重账号数） |
| `spend_amount` | 消耗平台币总量 |
| `game_spend` | 游戏内消耗平台币（`type=2`） |
| `plat_spend` | 平台侧消耗平台币（`type!=2，amount<0`） |
| `created_at` / `updated_at` | 创建/更新时间 |

### 展示字段

| 字段 | 描述 | 口径说明 | 单位 |
|------|------|----------|------|
| `date` | 日期 | 统计日期 | — |
| `earn_users` | 获得人数 | 当日 `amount>0` 的去重 `user_id` 数 | 人 |
| `earn_amount` | 获得平台币 | 当日 `amount>0` 的 `amount` 之和 | G点 |
| `charge_money` | 充值购币金额 | 当日 `user_charge.status=1` 的 `real_money` 之和 | 元 |
| `charge_coin` | 充值获得平台币 | 当日 `type=1` 且 `amount>0` 的 `amount` 之和 | G点 |
| `gift_coin` | 赠送获得平台币 | 当日 `type≠1` 且 `amount>0` 的 `amount` 之和 | G点 |
| `spend_users` | 消耗人数 | 当日 `amount<0` 的去重 `user_id` 数 | 人 |
| `spend_amount` | 消耗平台币 | 当日 `amount<0` 的 `\|amount\|` 之和 | G点 |
| `game_spend` | 游戏内消耗平台币 | `type=2` 且 `game_id` 属于网络游戏（`game.type=1`） | G点 |
| `plat_spend` | 平台侧消耗平台币 | 除游戏内消耗外的所有消耗 | G点 |
| `net_change` | 净变动平台币 | `earn_amount - spend_amount`（前端衍生） | G点 |
| `avg_earn` | 人均获得平台币 | `earn_amount / earn_users`（取整） | G点 |
| `avg_spend` | 人均消耗平台币 | `spend_amount / spend_users`（取整） | G点 |
| `charge_ratio` | 充值获得占比 | `charge_coin / earn_amount × 100%`（1位小数） | % |
| `gift_ratio` | 赠送获得占比 | `gift_coin / earn_amount × 100%`（1位小数） | % |

---

## 36. 平台币原因结构

**路由**：`/coinReason/list`
**落库表**：`report_coin_reason_day_log`
**数据来源**：`account_detail`

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_coin_reason_day_log` | 平台币原因结构离线日报（落库表） |
| `account_detail` | 平台币流水明细，按 `type_key` 聚合来源，字段详见附录 B |

#### `report_coin_reason_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | `md5(date_typeKey)` |
| `date` | 日期（Y-m-d） |
| `type_key` | 原因唯一标识，如 `earn_1`/`spend_2_network` 等 |
| `change_type` | 获得/消耗 |
| `reason_class` | 原因大类 |
| `reason` | 具体原因 |
| `user_count` | 账号数（去重） |
| `flow_count` | 流水次数 |
| `amount` | 平台币数量（绝对值） |
| `created_at` / `updated_at` | 创建/更新时间 |

### 原因类型定义

| type_key | 变动类型 | 原因大类 | 原因 | 数据口径 |
|----------|----------|----------|------|----------|
| `earn_1` | 获得 | 购买获得 | 充值到账 | `type=1，amount>0` |
| `earn_3` | 获得 | 活动赠送 | 活动赠送 | `type=3，amount>0` |
| `earn_4` | 获得 | 任务奖励 | 积分兑换 | `type=4，amount>0` |
| `earn_5` | 获得 | 系统补偿 | 系统操作补偿 | `type=5，amount>0` |
| `earn_6` | 获得 | 活动赠送 | VIP每日领取 | `type=6，amount>0` |
| `earn_7` | 获得 | 活动赠送 | 奖池彩蛋 | `type=7，amount>0` |
| `earn_9` | 获得 | 任务奖励 | 积分兑换G点 | `type=9，amount>0` |
| `earn_11` | 获得 | 活动赠送 | AI转入资金 | `type=11，amount>0` |
| `spend_2_network` | 消耗 | 游戏内消费 | 网游礼包购买 | `type=2，amount<0，game_id` 为网络游戏 |
| `spend_2_single` | 消耗 | 平台商品 | 单机游戏购买 | `type=2，amount<0，game_id` 非网络游戏 |
| `spend_5` | 消耗 | 系统扣除 | 系统操作扣除 | `type=5，amount<0` |
| `spend_8` | 消耗 | 活动消耗 | 盲盒活动消耗 | `type=8，amount<0` |
| `spend_10` | 消耗 | 平台消耗 | AI转出资金 | `type=10，amount<0` |

### 展示字段

| 字段 | 描述 | 单位 |
|------|------|------|
| `change_type` | 变动类型 | — |
| `reason_class` | 原因大类 | — |
| `reason` | 原因 | — |
| `user_count` | 账号数（跨天求和） | 人 |
| `flow_count` | 流水次数（跨天求和） | 次 |
| `amount` | 平台币数量（跨天求和） | G点 |
| `ratio` | 占同类比例 = `amount / 同变动类型总额 × 100%` | % |

---

## 37. 平台币消耗去向

**路由**：`/coinDestination/list`
**落库表**：`report_coin_destination_day_log`
**数据来源**：`account_detail`、`game`

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_coin_destination_day_log` | 平台币消耗去向离线日报（落库表） |
| `account_detail` | 平台币流水明细，按 `dest_key` 聚合来源，字段详见附录 B |
| `game` | 关联取网络游戏/单机游戏名称，字段详见下方 |

#### `report_coin_destination_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | `md5(date_destKey)` |
| `date` | 日期（Y-m-d） |
| `dest_key` | 去向唯一标识，如 `game_147`/`single_111`/`activity_blindbox` 等 |
| `dest_type` | 去向类型：游戏/商品/活动/平台 |
| `dest_name` | 去向名称 |
| `user_count` | 消耗人数（去重） |
| `flow_count` | 消耗次数 |
| `amount` | 消耗平台币（绝对值） |
| `created_at` / `updated_at` | 创建/更新时间 |

#### `game` 字段（节选）

| 字段 | 说明 |
|------|------|
| `_id` | 游戏ID |
| `title` | 游戏名称 |
| `type` | 类型：1网络游戏 2单机游戏 3在线小游戏 |
| `status` | 状态：启用1 禁用0 |

### 去向类型定义

| `dest_type` | 口径说明 |
|-------------|----------|
| 网络游戏 | `type=2` 消耗，`game.type=1`，按 `game_id` 分组 |
| 单机游戏 | `type=2` 消耗，非网络游戏，按 `game_id` 分组 |
| 活动 | `type=8` 盲盒，合并为「盲盒活动」 |
| 平台 | `type=10` 按 `note` 区分「AI女友」/「AI工具」；`type=5` 负数合并为「系统操作扣除」 |

### 展示字段

| 字段 | 描述 | 单位 |
|------|------|------|
| `dest_type` | 去向类型 | — |
| `dest_name` | 去向名称 | — |
| `user_count` | 消耗人数（跨天求和） | 人 |
| `flow_count` | 消耗次数（跨天求和） | 次 |
| `amount` | 消耗平台币（跨天求和） | G点 |
| `ratio` | 消耗占比 = `amount / 全部消耗总额 × 100%` | % |
| `avg_spend` | 人均消耗平台币 = `amount / user_count`（取整） | G点 |

> 排序：网络游戏→单机游戏→活动→平台，同类内按 `amount` 降序

---

## 38. 平台币余额快照

**路由**：`/coinBalance/list`
**落库表**：`report_coin_balance_day_log`
**数据来源**：`user.balance`

### 数据来源表

| 表名 | 说明 |
|------|------|
| `report_coin_balance_day_log` | 平台币余额日快照（落库表） |
| `user` | 用户表，`balance` 字段为快照来源，字段详见附录 F |

#### `report_coin_balance_day_log` 字段

| 字段 | 说明 |
|------|------|
| `_id` | `md5(date)` |
| `date` | 日期（Y-m-d） |
| `account_count` | 有币账号数（`balance>0`） |
| `total_balance` | 平台币余额总量 |
| `avg_balance` | 平均余额 |
| `high_1000` / `high_5000` / `high_10000` | 余额≥1000/5000/10000的账号数 |
| `created_at` / `updated_at` | 创建/更新时间 |

### 展示字段

| 字段 | 描述 | 口径说明 | 单位 |
|------|------|----------|------|
| `date` | 日期 | 快照日期 | — |
| `account_count` | 有币账号数 | `balance > 0` 的用户数 | 人 |
| `total_balance` | 平台币余额总量 | `balance > 0` 的 `balance` 之和 | G点 |
| `avg_balance` | 平均余额 | `total_balance / account_count`（取整） | G点 |
| `high_1000` | 高余额账号数(≥1000) | `balance ≥ 1000` 的用户数 | 人 |
| `high_5000` | 高余额账号数(≥5000) | `balance ≥ 5000` 的用户数 | 人 |
| `high_10000` | 高余额账号数(≥10000) | `balance ≥ 10000` 的用户数 | 人 |
| `ratio_1000` | 高余额占比(≥1000) | `high_1000 / account_count × 100%` | % |
| `ratio_5000` | 高余额占比(≥5000) | `high_5000 / account_count × 100%` | % |
| `ratio_10000` | 高余额占比(≥10000) | `high_10000 / account_count × 100%` | % |

> **注意**：余额快照反映 Job 执行时刻的用户余额，**不能按日期回溯历史余额**。

---

## 39. 支付通道日统计

**路由**：`/paymentOrder/stat`
**落库表**：`payment_channel_daily_statistics`
**数据来源**：`user_charge`（`status=1 或 2`）
**定时任务**：`Crontab channelDailyStatistics`（每30分钟）

### 数据来源表

| 表名 | 说明 |
|------|------|
| `payment_channel_daily_statistics` | 支付通道日统计离线汇总表（落库表） |
| `user_charge` | 充值订单表，`status IN (1,2)` 聚合来源，字段详见附录 E |
| `payment_channels` | 支付通道配置表，关联取 `channel_name` |

#### `payment_channel_daily_statistics` 字段

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `payment_id` | 支付通道ID |
| `amount` | 流水金额 |
| `fee` | 手续费 |
| `complaint_amount` | 投诉金额 |
| `rate` | 费率 |
| `date` | 日期 |
| `created_at` / `updated_at` | 创建/更新时间 |

#### `payment_channels` 字段（节选）

| 字段 | 说明 |
|------|------|
| `_id` | 编号 |
| `channel_name` | 通道名称 |
| `type` | 通道类型 |
| `status` / `enable` | 状态/启用状态 |
| `fee_rate` | 费用率 |

### 计算口径

- **流水金额**（`amount`）：按 `pay_time` 归属日期，`status IN (1, 2)` 的 `money` 之和
- **投诉金额**（`complaint_amount`）：`status=2` 时，按 `complaint_time` 归属日期的 `money` 之和
- **手续费**（`fee`）：`money × rate / 100`，按 `pay_time` 归属日期累加

> 投诉订单的 `pay_time` 与 `complaint_time` 可能不同天，流水金额计入支付日期，投诉金额单独计入投诉日期。

### 展示字段

| 字段 | 说明 |
|------|------|
| `date` | 统计日期 |
| `payment_id` | 通道ID |
| `channel_name` | 通道名称（关联 `payment_channel`） |
| `amount` | 流水金额（元） |
| `complaint_amount` | 投诉金额（元） |
| `fee` | 手续费（元） |
| `rate` | 费率（%） |

底部汇总返回 `totalMoney`（流水合计）和 `totalComplaint`（投诉合计）。

---

## 附录 A：平台币单位约定

> 10 G点 = 1 元人民币（`CommonConstKey::G_POINT_PER_RMB = 10`）

| 展示场景 | 单位 |
|----------|------|
| 平台币数量 | G点 |
| 充值购币金额 | 元（人民币） |
| 网络游戏统计金额 | 元（G点 ÷ 10 换算） |
| 渠道注册LTV | 元（G点 ÷ 10 换算） |
| 平台总览「消费金额」 | 元（G点 ÷ 10 换算） |

## 附录 B：源表 account_detail 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `user_id` | int | 用户ID |
| `game_id` | string | 游戏ID / `official`（平台侧） |
| `type` | int | 1充值 2消费 3活动赠送 4积分兑换 5后台操作 6VIP每日领取 7奖池彩蛋 8盲盒 9积分兑换G点 10AI转出 11AI转入 |
| `amount` | double | 平台币变动值（正=获得，负=消耗） |
| `note` | string | 备注（AI 去向分类用） |
| `created_at` | int | Unix 时间戳 |

## 附录 C：重跑说明

| `reset_type` | 作用 | 触发入口 |
|--------------|------|----------|
| `coinOverview` | 重跑指定日期的总览 + 原因结构 + 消耗去向 | `/system/resetData` |
| `coinBalance` | 仅重跑指定日期的余额快照 | `/system/resetData` |
| `channel` | 重跑渠道统计（V1） | `/system/resetData` |
| `channelV2` | 重跑渠道统计（V2）+ 留存 + LTV | `/system/resetData` |
| `game` | 重跑游戏统计（V1） | `/system/resetData` |
| `networkGame` | 重跑网络游戏统计（V2）+ 渠道 + 留存 + LTV | `/system/resetData` |
| `singleGame` | 重跑单机游戏统计 | `/system/resetData` |
| `total` | 重跑全平台日报（report_total_day_log） | `/system/resetData` |
| `platformDailyStat` | 重跑平台日报统计 | `/system/resetData` |

## 附录 D：定时任务速查（来自 crontab.md）

| 任务类别 | Cron 表达式 | 模块 | 方法 |
|----------|-------------|------|------|
| 全平台日报重跑 | `0 2 * * *` | total | totalOldDay |
| 全平台日报滚动 | `0 * * * *` | total | totalMinute |
| VIP/金币重跑 | `0 4 * * *` | total | totalVipOrCoinOldDay |
| VIP/金币滚动 | `0 * * * *` | total | totalVipOrCoinMinute |
| AB测试统计 | `0 */3 * * *` | total | totalAbDay |
| 渠道V1重跑 | `0 1 * * *` | AgentTotalOldDay | agentOldDayTotal |
| 渠道V2重跑 | `0 1 * * *` | channelTotalV2 | channelOldDayTotal |
| 渠道V2滚动 | `0 */2 * * *` | channelTotalV2 | channelMinuteTotal |
| 渠道注册留存 | `0 6 * * *` | channelTotalV2 | channelRetention |
| 渠道LTV | `0 4 * * *` | channelTotalV2 | channelLtv |
| 金币总览重跑 | `0 1 * * *` | coin | coinOverviewOldDay |
| 金币总览滚动 | `0 */2 * * *` | coin | coinOverviewMinute |
| 平台日报 | `0 3 * * *` | platformDailyStat | dailyStat |
| 平台注册留存 | `0 4 * * *` | platformDailyStat | retention |
| 单机游戏统计 | `0 */2 * * *` | gameTotal | singleGameMinuteTotal |
| AI日统计 | `0 1 * * *` | Crontab | LsjAiDailyStats |
| 小时级监控 | `0 * * * *` | HourlyStatsMonitor | monitor |
| 游戏统计重跑 | `0 1 * * *` | GameTotal | gameOldDayTotal |
| 网络游戏重跑 | `0 5 * * *` | GameTotal | gameOldDayTotalV2 |
| 游戏注册留存 | `0 6 * * *` | GameTotal | gameRetentionDu |
| 游戏LTV | `0 4 * * *` | GameTotal | gameLtv |
| 游戏渠道重跑 | `0 4 * * *` | gameTotal | gameChannelOldDayTotal |
| 埋点统计同步 | `0 * * * *` | trackingStat | sync |
| 支付通道统计 | `*/30 * * * *` | Crontab | channelDailyStatistics |

## 附录 E：源表 user_charge 字段说明

> 订单表，用户发起充值订单、充值金币到账，多个报表（[系统主页](#2-系统主页)、[转化漏斗](#6-转化漏斗)、[平台币总览](#35-平台币总览)、[支付通道日统计](#39-支付通道日统计)）以其为充值数据来源。

| 字段 | 类型 | 说明 |
|------|------|------|
| `_id` | int | ID |
| `user_id` | int | 用户ID |
| `channel` | string | 用户渠道码 |
| `reg_time` | int | 用户注册时间 |
| `game_id` | string | 从游戏中发起则登记游戏ID，从平台发起则登记 `official` |
| `order_num` | string | 订单号 |
| `money` | double | 订单金额 |
| `origin_money` | double | 原始订单金额 |
| `is_vip` | int | 是否VIP |
| `product_id` | int | 产品ID，关联 `user_group`（`is_vip=0`）或 `user_product`（`is_vip=1`） |
| `payment_id` | int | 支付通道ID |
| `payment_type` | int | 支付方式：0支付宝 1微信 |
| `rate` | double | 费率 |
| `real_money` | double | 扣除费率后的金额 |
| `status` | int | 状态：-1发起失败 0付款中 1已付款 2投诉 |
| `pay_time` | string | 支付时间 |
| `complaint_time` | string | 投诉时间 |
| `business_type` | int | 业务类型：0金币 1VIP 2充值并消费 |
| `is_test` | int | 是否测试账号：1是 0否 |
| `device_type_new` | string | 设备信息 |
| `created_at` / `updated_at` | int | 创建/更新时间 |

## 附录 F：源表 user 关键字段说明

> 用户主表（完整字段较多，此处仅列报表统计常用字段），供 [转化漏斗](#6-转化漏斗)、[商品点击统计](#34-商品点击统计)、[平台币余额快照](#38-平台币余额快照) 等报表关联使用。

| 字段 | 类型 | 说明 |
|------|------|------|
| `_id` | int | 编号 |
| `nickname` / `username` | string | 昵称/用户名 |
| `account` | string | 唯一账号（统一小写格式化） |
| `channel_name` | string | 渠道 |
| `device_type` | string | 设备类型 |
| `balance` | double | 充值余额（G点） |
| `group_id` | int | 用户组 |
| `first_pay` / `last_pay` | int | 第一次/最后一次充值时间 |
| `pay_total` | int | 累计充值金额 |
| `reg_game` | int | 注册来源游戏id，关联 `game` 表 |
| `status` | int | 状态：启用1 禁用0 |
| `register_at` | int | 注册时间 |
| `register_date` | string | 注册日 |
| `login_num` | int | 登录次数 |
| `login_at` | int | 最后登录时间 |
| `is_disabled` | int | 是否禁用：1是 0否 |
| `is_test` | int | 是否测试账号：1是 0否 |
| `created_at` / `updated_at` | int | 创建/更新时间 |
