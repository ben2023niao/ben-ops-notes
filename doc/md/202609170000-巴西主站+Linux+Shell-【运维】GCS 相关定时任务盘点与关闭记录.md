---
id: "doc-135dcbc382ec"
title: "【运维】GCS 相关定时任务盘点与关闭记录"
date: "2026-09-17T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "Docker", "监控告警", "CDN", "DNS"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-17-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91GCS%E7%9B%B8%E5%85%B3%E5%AE%9A%E6%97%B6%E4%BB%BB%E5%8A%A1%E7%9B%98%E7%82%B9%E4%B8%8E%E5%85%B3%E9%97%AD%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-17-【运维】GCS相关定时任务盘点与关闭记录.md"
sourceSha256: "61a69ea3587dfdca38cdd8b9df434fcd31b06ede2b76a6dc652a3f2002761ca5"
sourceSystem: "project-doc"
---

# 【运维】GCS 相关定时任务盘点与关闭记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609170000-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BLinux%2BShell-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91GCS%20%E7%9B%B8%E5%85%B3%E5%AE%9A%E6%97%B6%E4%BB%BB%E5%8A%A1%E7%9B%98%E7%82%B9%E4%B8%8E%E5%85%B3%E9%97%AD%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-09-17 00:00｜日期依据：文件名日期

时间：2026-09-17
范围：宝塔 192.0.2.8、后台 01/02/03、宝塔上的 Docker 容器
目标：找出所有跟 GCS 有关的定时任务并关闭（不通知飞机群）

## 一、结论

宝塔上共有 **4 个 GCS 相关定时任务**，现已全部关闭/删除：

| # | 任务 | 位置 | 周期 | 处理 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 1 | 静态资源同步到 GCS | 宝塔面板计划任务 | 每天 03:10 | **已删除**（2026-09-17 17:25，面板安全日志有记录） | 原本已是"停用"状态 |
| 2 | 游戏结果集备份到 GCS<br>`/root/game_results_gcs_backup.sh` | root crontab | 每天 02:20 | **已注释关闭** | 备份到 gs://bizops-game-results-db-backup |
| 3 | GCS health.json 自动补齐<br>`gcs_health_json_ensure.py --apply` | root crontab | 每 15 分钟 | **已注释关闭** | 会往各桶写 health.json |
| 4 | S3→GCS 同步请求 worker<br>`s3_sync_request_worker.py` | root crontab | 每分钟 | **已注释关闭** | 处理机器人按钮投递的同步请求 |

后台 01/02/03 与容器内**没有** GCS 相关定时任务（见第三节证据）。

回滚方式：关闭的行都带前缀 `#DISABLED-20260917(rollback: remove this prefix) `，
把前缀删掉即恢复；crontab 已备份在宝塔 `/root/crontab.bak-2026-09-17-1727-before-disable-gcs`。

## 二、宝塔 root crontab 现状（关闭后）

```text
*/30 * * * *  cf_static_cname_monitor.py                    # CF DNS 监控（非 GCS）
40 4,10,16,22 * * *  sync_certs_to_standby.sh               # 证书同步（非 GCS）
#DISABLED-20260917 ... 20 2 * * *  game_results_gcs_backup.sh   ← 本次关闭（GCS）
30 8 * * *  cf_billing_daily_summary.py --frequency daily   # CF 计费
35 8 * * 1  cf_billing_daily_summary.py --frequency weekly  # CF 计费
40 8 1 * *  cf_billing_daily_summary.py --frequency monthly # CF 计费
*/10 * * * *  new_game_static_check.py                      # CDN 静态入口检查（不直接碰 GCS）
#DISABLED-20260917 ... */15 * * * *  gcs_health_json_ensure.py  ← 本次关闭（GCS）
#DISABLED-20260917 ... * * * * *  s3_sync_request_worker.py     ← 本次关闭（S3→GCS）
20 2 * * *  /www/server/cron/3ab48c27...                    # Let's Encrypt 续签（非 GCS）
```

验证：`crontab -l | grep -E "gcs|GCS" | grep -v "^#" | wc -l` → **0**（没有启用中的 GCS 任务）。

## 三、其它位置的排查证据

```text
宝塔面板任务（用户面板里那 5 条）：
  · 静态资源同步到GCS           → 已删除（本次）
  · 全部游戏域名增加删除 01:40   → /www/server/cron/all_game_domain_sync + c4df/d528，Cloudflare DNS，非 GCS
  · 续签Let's Encrypt证书 02:20  → /www/server/cron/3ab48c27...（acme_v2.py），非 GCS
  · ip 01:30                    → /www/server/cron/9d46bec0...，非 GCS
  · game_results_data-sync 01:30 → 结果集在服务器之间同步，非 GCS（且为停用）
  （/www/server/cron/ 下 5 个脚本逐个 grep "gs://|gsutil|gcloud storage|storage.googleapis" 命中数均为 0）

后台 01 / 02 / 03：
  · root crontab 只有 daily_error_log_pack.py（03 另有 disk_cleanup.sh），无 GCS
  · /etc/cron.d 只有 e2scrub_all；systemd 定时器 bizops-log-maintenance / bizops-game-log-archive /
    bizops-disk-cleanup 等，grep GCS 关键字命中 0
  · 容器内无 cron 定时任务

宝塔 /root 下还留着一批**未被任何 cron 调度**的 GCS 脚本（历史遗留，仅供参考/备用）：
  cron-gcs-static-sync.sh、bizops_gcs_static_sync.sh、bizops_gcs_static_sync_gsutil.sh、
  bizops_gcs_static_sync_gsutil_fast.sh、git_static_gcs_sync.py、vendor_a3_5_static_gcs_sync.py
  → 已逐个确认"无任何 cron/计划任务引用"，不产生定时行为，本次未删除。

注意：`new_game_static_check.py`（每 10 分钟）只通过 CDN 检查静态入口 HTTP 200，
不直接读写 GCS。如果后续要求"凡是碰静态资源的都关"，把它一起注释即可。
```

## 四、关闭后需要注意的影响

1. **health.json 不再自动补齐**：以后新建/同步桶后，如果缺 health.json，
   需要人工跑一次：`python3 /opt/bizops-scripts/gcs_health_json_ensure.py --apply`。
2. **结果集不再自动备份到 GCS**：需要备份时人工跑：
   `bash /root/game_results_gcs_backup.sh pg pp`（可指定厂家）。
3. **机器人"静态资源同步S3到GCS"按钮不再工作**（因为每分钟的 worker 已关）：
   需要同步时在 03 上跑
   `docker/scripts/s3_gcs_sdk_sync.py --prefix <厂家> --apply --only-missing`。
