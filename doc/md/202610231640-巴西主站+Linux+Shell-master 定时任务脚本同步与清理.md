---
id: "doc-3db7ad02bec6"
title: "master 定时任务脚本同步与清理"
date: "2026-10-23T16:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "Docker", "监控告警", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-10-23-1640-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91master%E5%AE%9A%E6%97%B6%E4%BB%BB%E5%8A%A1%E8%84%9A%E6%9C%AC%E5%90%8C%E6%AD%A5%E4%B8%8E%E6%B8%85%E7%90%86.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-10-23-1640-【运维】master定时任务脚本同步与清理.md"
sourceSha256: "e06637673af799de6bbd23bc7188a773ffdc8911824d5812aa39b6de570fc45d"
sourceSystem: "project-doc"
---

# master 定时任务脚本同步与清理

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-10-23-1640-【运维】master定时任务脚本同步与清理.md`

> 整理日期：2026-10-23 16:40｜日期依据：文件名日期

时间：2026-10-23 16:40（北京）｜2026-10-23 05:40（巴西圣保罗）
范围：按线上服务器实际 cron / systemd timer 清单，同步有效脚本到 master，
      清理 master 中已停用或长期不用的监控脚本。

## 一、线上实际在跑的任务

| 机器 | 任务 | 脚本 / 服务 | 周期 |
| --- | --- | --- | --- |
| 入口机 34.151.249.53 | 容器健康 | `container_health_monitor.py` | 每 2 分钟 |
| 入口机 | 入口探活 | `entry_health_monitor.py` | 每 2 分钟 |
| 入口机 | PG6/PG7 启动链 | `pg67_games_watch.py` | 每小时 :56 |
| 入口机 | 严禁重启监控 | `critical_restart_watch.py` | 每分钟 |
| 入口机 | 磁盘清理 | `disk_cleanup.sh` | 每天 04:00 |
| 巴西 01/02 | 每日错误日志 | `daily_vendor_error_pack.py` | 每天 07:00 UTC |
| 巴西 01/02 | 48h 日志清理 | `prune_game_logs.sh` | 每天 09:10 |
| 巴西 01/02 | 结果集权限自愈 | `fix_result_perms.sh` | 每分钟 |
| 巴西 01/02 | 日志轮转归档 | `dbqp_game_log_archive.py` + logrotate | 每小时 |
| 巴西 01/02 | 磁盘清理 | `disk_cleanup.sh` | 每天 |
| 香港 01 | 容器重启监控 | `critical_restart_watch.py`（香港版） | 每分钟 |
| 香港 01/02 | 每日错误日志 | `daily_vendor_error_pack.py` | 每天 15:00 |
| 香港 01/02 | 48h 日志清理 | `prune_game_logs.sh` | 每天 09:10 |
| 香港 01/02 | 结果集权限自愈 | `fix_result_perms.sh` | 每分钟 |
| 宝塔 35.247.205.6 | 静态 CNAME 巡检 | `cf_static_cname_monitor.py` | 每 30 分钟 |
| 宝塔 | 新游戏静态抽检 | `new_game_static_check.py` | 每 10 分钟 |
| 宝塔 | CF 账单汇总 | `cf_billing_daily_summary.py` | 每天/周/月 |
| 宝塔 | 证书同步 | `sync_certs_to_standby.sh` | 每天 4 次 |

## 二、本次同步

### 1. 新增香港版重启监控

香港 01 线上使用的是独立版本（VENDORS 含 `jili`、不含 `tada`，默认 `PROJECT_NAME=香港项目`，
778 行，比巴西版多告警上限等增强）。

已同步为：

```text
docker/scripts/critical_restart_watch_hk.py
```

香港部署路径仍是 `/opt/dbqp-scripts/critical_restart_watch.py`，不要用巴西版覆盖。

### 2. 合并结果集权限脚本的 printf 修复

香港现网版本修掉了 `printf` 参数多于占位符导致的“格式串复用、群里出现重复空告警”问题。
已把这段 if/else 合并回 master 的 `fix_result_perms.sh`，同时保留 `PROJECT_NAME` 支持：

- 巴西：默认 `巴西项目`
- 香港：unit 里传 `PROJECT_NAME=香港项目`

## 三、从 master 清理的旧脚本

| 脚本 | 原因 |
| --- | --- |
| `game_availability_monitor.py` | 游戏可用性巡检已下线，线上 cron 已注释 |
| `run_game_monitor_on_03.sh` | 上述巡检的 03 启动器，一并停用 |
| `daily_error_log_pack.py` | 已被 `daily_vendor_error_pack.py` 替代 |
| `ff789_games_watch.sh` | 线上 cron/timer 均未引用 |
| `cleanup_server_disk.sh` | 旧磁盘清理，已被 `disk_cleanup.sh` 替代 |

## 四、发现的版本差异（本次未覆盖线上）

1. 入口机的 `disk_cleanup.sh` 还是旧版；master 里是 2026-09-19 的镜像白名单版本，
   更安全，建议下次维护窗口把入口机换成 master 版本。
2. 巴西 03 的 crontab 里仍有一条 `daily_error_log_pack.py`（旧错误日志任务），
   与 01/02 的新任务重复，建议确认后停用。
3. 香港 01/02 的 `fix_result_perms.sh` 仍是硬编码“香港项目”的版本；
   master 已合并修复，后续可下发并在 unit 里设置 `PROJECT_NAME=香港项目`。

## 五、验证

- 所有 Python 脚本 `py_compile` 通过
- 所有 Shell 脚本 `bash -n` 通过
- 线上在跑的 13 个脚本在 master 均有对应文件
- 删除的 5 个脚本在线上 cron/timer 中均无引用
