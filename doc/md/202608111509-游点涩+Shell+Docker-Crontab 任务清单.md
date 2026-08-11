---
id: "doc-870a7940bab9"
title: "Crontab 任务清单"
date: "2026-08-11T15:09:59+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "监控告警", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/src/youdianse-php/doc/crontab.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/src/youdianse-php/doc/crontab.md"
sourceSha256: "4eb41170cdf84273b436aabe3ba3dd36525c0486ce4e0613df8bfa4cec989b81"
sourceSystem: "project-doc"
---

# Crontab 任务清单

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/src/youdianse-php/doc/crontab.md`

> 整理日期：2026-08-11 15:09｜日期依据：文件创建/修改时间

Shell 公共路径：`/usr/bin/php /var/www/html/18game/18game_php/bin/shell.php`

---

## 系统总览统计

| Cron 表达式 | 模块 | 方法 | 说明 |
|---|---|---|---|
| `0 2 * * *` | total | totalOldDay | 次日重跑，凌晨 2 点（日志 → `/var/log/totalOldDay.log`） |
| `0 * * * *` | total | totalMinute | 每小时整点 |
| `0 4 * * *` | total | totalVipOrCoinOldDay | VIP/金币次日重跑，凌晨 4 点 |
| `0 * * * *` | total | totalVipOrCoinMinute | VIP/金币，每小时整点 |
| `0 */3 * * *` | total | totalAbDay | AB 测试，每 3 小时整点 |

---

## 渠道统计

| Cron 表达式 | 模块 | 方法 | 说明 |
|---|---|---|---|
| `0 1 * * *` | AgentTotalOldDay | agentOldDayTotal | 次日重跑，凌晨 1 点 |
| `0 * * * *` | AgentTotalMinute | agentMinuteTotal | 每小时整点 |
| `0 1 * * *` | channelTotalV2 | channelOldDayTotal | 次日重跑，凌晨 1 点 |
| `0 */2 * * *` | channelTotalV2 | channelMinuteTotal | 每 2 小时整点 |
| `0 6 * * *` | channelTotalV2 | channelRetention | 注册留存，凌晨 6 点 |
| `0 */2 * * *` | channelTotalV2 | channelRetentionMinute | 注册留存，每 2 小时整点 |
| `0 4 * * *` | channelTotalV2 | channelLtv | LTV，凌晨 4 点 |
| `0 */2 * * *` | channelTotalV2 | channelLtvMinute | LTV，每 2 小时整点 |

---

## 金币统计

| Cron 表达式 | 模块 | 方法 | 说明 |
|---|---|---|---|
| `0 1 * * *` | coin | coinOverviewOldDay | 次日重跑，凌晨 1 点 |
| `0 */2 * * *` | coin | coinOverviewMinute | 每 2 小时整点 |

---

## 平台统计

| Cron 表达式 | 模块 | 方法 | 说明 |
|---|---|---|---|
| `0 3 * * *` | platformDailyStat | dailyStat | 平台日报，凌晨 3 点 |
| `0 4 * * *` | platformDailyStat | retention | 平台留存，凌晨 4 点 |
| `0 */2 * * *` | gameTotal | singleGameMinuteTotal | 单款游戏统计，每 2 小时整点 |
| `0 1 * * *` | Crontab | LsjAiDailyStats | 老司机 AI 日统计，凌晨 1 点 |
| `0 * * * *` | HourlyStatsMonitor | monitor | 小时级统计监控，每小时整点 |

---

## 游戏统计

| Cron 表达式 | 模块 | 方法 | 说明 |
|---|---|---|---|
| `0 1 * * *` | GameTotal | gameOldDayTotal | 次日重跑，凌晨 1 点 |
| `0 */2 * * *` | GameTotal | gameMinuteTotal | 每 2 小时整点 |
| `0 5 * * *` | GameTotal | gameOldDayTotalV2 | 网络游戏次日重跑，凌晨 5 点 |
| `0 */2 * * *` | GameTotal | gameMinuteTotalV2 | 网络游戏，每 2 小时整点 |
| `0 6 * * *` | GameTotal | gameRetentionDu | 网络游戏留存，凌晨 6 点 |
| `0 4 * * *` | GameTotal | gameLtv | 网络游戏 LTV，凌晨 4 点 |
| `0 4 * * *` | gameTotal | gameChannelOldDayTotal | 游戏渠道次日重跑，凌晨 4 点 |
| `0 */2 * * *` | gameTotal | gameChannelMinuteTotal | 游戏渠道统计，每 2 小时整点 |

---

## 结算

| Cron 表达式 | 模块 | 方法 | 说明 |
|---|---|---|---|
| `0 0 * * *` | Settlement | create | 结算单创建，每天凌晨 0 点 |

---

## 游戏业务

| Cron 表达式 | 模块 | 方法 | 说明 |
|---|---|---|---|
| `* * * * *` | Crontab | gameNotify | 扣费回调通知，每分钟 |
| `* * * * *` | UserFeedbackStatus | updateUserFeedbackStatus | 客服支持状态关闭，每分钟 |
| `*/30 * * * *` | gameReserve | notify | 预约上线通知检查，每 30 分钟（stderr → 2>&1） |
| `*/30 * * * *` | Crontab | updateGameScore | 更新游戏评分，每 30 分钟 |

---

## 域名

| Cron 表达式 | 模块 | 方法 | 说明 |
|---|---|---|---|
| `0 * * * *` | Crontab | pushDomain | 推送域名，每小时整点 |
| `0 19 * * *` | Crontab | checkDoMain | 检测域名可用性，每天 19 点（日志 → `/var/log/checkDomain.log`） |

---

## 排行榜 / 活动

| Cron 表达式 | 模块 | 方法 | 说明 |
|---|---|---|---|
| `0 0 * * *` | PrizePool | ranking | 奖池彩蛋排行榜快照，每天凌晨 0 点 |
| `0 * * * *` | rank | snapshot | 冲榜活动排行榜快照，每小时整点 |

---

## 社区 / 内容

| Cron 表达式 | 模块 | 方法 | 说明 |
|---|---|---|---|
| `0 4 * * *` | Crontab | preHotPosts | 热帖预热热度值，凌晨 4 点 |
| `0 5 * * *` | UserCommunityTitle | daily | 更新用户头衔，每天 5 点 |

---

## 数据同步

| Cron 表达式 | 模块 | 方法 | 说明 |
|---|---|---|---|
| `0 * * * *` | Crontab | syncChannel | 渠道商数据同步，每小时整点 |
| `0 * * * *` | trackingStat | sync | 埋点统计数据同步，每小时整点 |
| `*/30 * * * *` | Crontab | channelDailyStatistics | 通道日统计（按支付通道），每 30 分钟 |

---

## 一次性脚本（手动执行，不加入 crontab）

| 模块 | 方法 | 说明 |
|---|---|---|
| Crontab | recalculateChannelHistory | 渠道商历史数据修复（用于修复历史数据错误） |
| PrizePool | internalUser | 奖池彩蛋内部账号刷入 |
