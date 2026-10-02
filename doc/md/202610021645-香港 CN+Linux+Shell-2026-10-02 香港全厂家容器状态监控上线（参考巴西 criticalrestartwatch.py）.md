---
id: "doc-c79814920cd6"
title: "2026-10-02 香港全厂家容器状态监控上线（参考巴西 criticalrestartwatch.py）"
date: "2026-10-02T16:45:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Linux", "Shell", "Python", "Docker", "监控告警", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-10-02-1645-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AF%E5%85%A8%E5%8E%82%E5%AE%B6%E5%AE%B9%E5%99%A8%E7%8A%B6%E6%80%81%E7%9B%91%E6%8E%A7%E4%B8%8A%E7%BA%BF%EF%BC%88%E5%8F%82%E8%80%83%E5%B7%B4%E8%A5%BF%EF%BC%89.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-10-02-1645-【架构改造】香港全厂家容器状态监控上线（参考巴西）.md"
sourceSha256: "10670e35f9738106abab78df6ba72868d2979be9200b5d04238194814651df20"
sourceSystem: "project-doc"
---

# 2026-10-02 香港全厂家容器状态监控上线（参考巴西 criticalrestartwatch.py）

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-10-02-1645-【架构改造】香港全厂家容器状态监控上线（参考巴西）.md`

> 整理日期：2026-10-02 16:45｜日期依据：文件名日期

## 一、需求

```text
用户：参考巴西项目，香港项目也加上「全部厂家、全部游戏容器」的状态监控，
      定时任务每分钟一次 critical_restart_watch.py，并完善这个脚本。
补充口径（本轮澄清）：
  · 香港目前没上线、处于调试阶段 → 报警 3 条后先静默（只记录日志）
  · 巴西是上线运营的 → 需要时时刻刻报警、不设上限
本轮按流程发飞机群通知（开始 7600 / 部署完成 7607）。
```

## 二、巴西版对照

```text
巴西脚本：master/docker/scripts/critical_restart_watch.py（454 行）
  · 跑在入口机 34.151.249.53 的 crontab，每分钟一次
  · 监控 203.0.113.1 / 203.0.113.1 各 9 个厂家容器：api pg tada tada_ws ppk pp playson panda g759
  · 判定：RestartCount 增加 / 容器 ID 变化 / 状态非 running / 容器缺失；
    另加宿主内存阈值预警、发版动作提示；状态文件 + 每小时心跳；告警带双时区与 @ 提及
巴西今日文档：2026-10-02-1820 / 1830（关键容器严禁重启监控、18 个容器状态监控升级）
```

## 三、香港版适配

```text
文件：docker/deploy/hongkong/critical_restart_watch.py（部署在 prod-01：/opt/dbqp-scripts/）
运行位置：prod-01（34.92.83.132）——这台有 TG 机器人凭据与 sshpass，且能 SSH 到两台后端
监控对象：203.0.113.1 / 203.0.113.1 × 9 个厂家 = 18 个容器
  api(9090) pg(9091) jili(9093) tada_ws(8765) ppk(9098) pp(9099) playson(9020) panda(9018) g759(9019)
  （香港没有 tada(9096) 容器，用 jili 代替；tada_ws 容器名两台可能下划线/连字符，两种都认）
默认值：PROJECT_NAME=香港项目、DBQP_WATCH_HOSTS=203.0.113.1,203.0.113.1、
      状态 /var/tmp/dbqp-hk-restart-watch.json、日志 /var/log/dbqp-hk-restart-watch.log
时区：告警正文用「北京 / 香港」双时间
```

## 四、本版对巴西脚本的完善

```text
1. 告警上限静默（按你的口径拆分）
     DBQP_MONITOR_MAX_ALERTS：**默认 0 = 不限**（生产口径，巴西用这个）
     香港调试期在 env 里显式设为 3 → 发满 3 条后自动进入静默，并发一条「已进入静默」提示；
     静默后告警/恢复都只写日志；--reset-alerts 可清零计数并解除静默
2. --baseline：只写基线、不发告警（容器整批未启动时铺底，避免首次巡检刷屏）
3. 静默文件开关：存在 /opt/dbqp-hk-ops/container-monitor-quiet 时只记录不发群（应急静音）
4. 持续性告警冷却：缺失/不在运行/内存/磁盘类问题每 DBQP_MONITOR_REALERT_SECONDS（默认 1800s）
   才重发一次；一次性事件（重启次数+1、容器被重建）只报一次，不会误发「已恢复」
5. SSH 采集重试：失败重试 2 次；连续 2 轮失败才报警（避免网络抖动误报）
6. 端口监听检查（新增）：容器 running 但对应端口没监听 → 直接报「业务不可用」
7. 宿主根盘阈值预警（新增）：DBQP_HOST_DISK_MAX_PCT 默认 85%
8. 告警正文补充 OOMKilled / ExitCode / RestartPolicy / 容器内存 / 运行时长 / 端口
9. 日志按大小轮转（默认 4MB）
10. 心跳文案修正：原先固定写「全部 running」，现在按真实统计输出
    「18 个厂家容器，3 个 running，15 个未运行（已在基线内，不计告警）」
```

## 五、部署与验证

```text
部署（prod-01）
  · /opt/dbqp-scripts/critical_restart_watch.py
  · /opt/dbqp-hk-ops/container-watch.env（600）：从 /opt/benbot-runtime.env 抽出
      TG_BOT_TOKEN / TELEGRAM_API_TOKEN / BEN_BOT_MONITOR_CHAT_ID / PGSERVER_DEPLOY_PASS，
      另加 PROJECT_NAME=香港项目、DBQP_WATCH_HOSTS、DBQP_MONITOR_MAX_ALERTS=3
      （原 env 第 29 行是 `BEN_BOT_HOST_OS`（无 =），systemd EnvironmentFile 不允许，故单独生成）
  · systemd：dbqp-container-watch.service（oneshot）+ dbqp-container-watch.timer
      OnCalendar=*:0/1、AccuracySec=10s，已 enable + active

验证结果
  · --show：监控对象 2 台 × 9 厂家 = 18 个容器，逐条打印状态/重启次数/内存/端口/运行时长
  · --baseline：基线写入 18 个容器，未发送任何告警
  · --dry-run：18 个容器、alerts=0（当前 15 个未运行是既定状态，已在基线内）
  · systemd：timer active、服务 oneshot 正常退出；日志按分钟写入
      [10:27:56] 基线已写入：18 个容器（未发送任何告警）
      [10:29:24] 心跳：18 个厂家容器，3 个 running，15 个未运行（已在基线内，不计告警）
  · 联调自测（独立状态文件 + PROJECT_NAME=香港项目·联调测试 + MAX_ALERTS=1）：
      第 1 轮基线 → 第 2 轮发出 1 条告警并进入静默（meta: sent_alerts=1, silenced=true）
      → 第 3 轮静默只记录（日志出现 SILENCED，未发群）→ 第 4 轮 --reset-alerts 解除（计数归零）
      四步全部符合预期；同时修掉了「告警计数未落盘」的 bug（save_state 改为最后执行）

当前状态：203.0.113.1 上 api / pg / tada_ws 在跑，其余 15 个未运行（用户明确本轮不启动容器），
          已在基线内、不计告警；一旦有容器重启/消失/端口掉线，会按上面规则报警。
```

## 六、日常使用

```bash
# 看当前快照（不发群）
set -a; . /opt/dbqp-hk-ops/container-watch.env; set +a
python3 /opt/dbqp-scripts/critical_restart_watch.py --show

# 只检查不写状态
python3 /opt/dbqp-scripts/critical_restart_watch.py --dry-run

# 解除调试期静默、恢复告警
python3 /opt/dbqp-scripts/critical_restart_watch.py --reset-alerts

# 临时静音（不改配置，只建标记文件）
touch /opt/dbqp-hk-ops/container-monitor-quiet      # 静音；删除即恢复

# 定时任务
systemctl status dbqp-container-watch.timer
journalctl -u dbqp-container-watch.service -n 20
tail -f /var/log/dbqp-hk-restart-watch.log

# 加新厂家：改脚本 VENDORS / VENDOR_PORTS 后重跑 --baseline
```

## 七、关联

```text
docker/deploy/hongkong/critical_restart_watch.py（本脚本）
master/docker/scripts/critical_restart_watch.py（巴西参考版）
master/docker/doc/2026-10-02-1830-【架构改造】全厂家容器状态监控升级-18个容器记录.md
docker/doc/2026-09-24-1540-【优化+问题排查】结果集权限被改坏原因定位与权限自愈监控上线记录.md（HK 已有 timer 惯例）
```
