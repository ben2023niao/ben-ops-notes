---
id: "doc-0c60cbefa7ae"
title: "2026-10-03 香港 jili/panda 重启循环根因修复 + 全厂家容器监控完善"
date: "2026-10-03T17:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Linux", "Shell", "Python", "Docker", "监控告警", "自动化", "安全运维"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-10-03-1720-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%2B%E6%95%85%E9%9A%9C%E5%A4%84%E7%90%86%E3%80%91%E9%A6%99%E6%B8%AFjili-panda%E5%B4%A9%E6%BA%83%E6%A0%B9%E5%9B%A0%E4%BF%AE%E5%A4%8D%E4%B8%8E%E5%AE%B9%E5%99%A8%E7%9B%91%E6%8E%A7%E5%AE%8C%E5%96%84.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-10-03-1720-【架构改造+故障处理】香港jili-panda崩溃根因修复与容器监控完善.md"
sourceSha256: "e23dfce200d7c4e4b41491d189640e0a6f39d33f89c93f4d9128a30f288162d3"
sourceSystem: "project-doc"
---

# 2026-10-03 香港 jili/panda 重启循环根因修复 + 全厂家容器监控完善

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-10-03-1720-【架构改造+故障处理】香港jili-panda崩溃根因修复与容器监控完善.md`

> 整理日期：2026-10-03 17:20｜日期依据：文件名日期

## 一、本轮需求与背景

```text
用户：香港全部游戏厂家已启动（对比巴西：多一个 jili、少一个 tada）；参考巴西再确认/完善
      critical_restart_watch.py 每分钟一次的全厂家容器状态监控。
另附昨天监控的实际报警：3 条告警（01 的 api/pg/tada_ws 消失、02 的 pg 重建）后用满调试期配额进入静默。
本轮按流程发群：步骤 1-2/3 message_id 7614（另有汇总）。
```

## 二、香港容器现状（监控清单已对齐）

```text
两台（203.0.113.1 / 203.0.113.1）各 9 个业务容器 + beszel-agent，镜像统一 20261003-ben：
  api(9090) pg(9091) jili(9093) tada_ws(8765) ppk(9098) pp(9099) playson(9020) panda(9018) g759(9019)
与巴西的差异：香港是 jili（复用 tada 镜像，/app/tada）+ tada_ws，没有巴西的 tada(9096) —— 脚本 VENDORS 已按此配置。
容器名：game-service-<厂家>-prod（tada_ws 兼容下划线/连字符两种写法）。
```

## 三、线上故障：jili / panda 一直在重启循环

```text
现象（10-03 17:0x，两台一致）：
  game-service-jili-prod    status=restarting  restarts=16（01）/ 15（02）
  game-service-panda-prod   status=restarting  restarts=14（01）/ 15（02）
日志：
  File "/app/tada/jili.py", line 733, in <module>
    import risk_control_entry -> from configs import is_top_new_configs
  ImportError: cannot import name 'is_top_new_configs' from 'configs' (/app/tada/configs.py)
  （panda 同型：/app/panda/configs.py）

根因：start.sh 第 97-99 行会把**宿主机的 conf/configs-<厂家>.py 挂载成容器内的 configs.py**：
    config_file="-v /data/server-runtime/conf/configs-$v.py:/app/$appdir/configs.py"
  而 10-02 那次 rsync 全量同步把 conf/configs-*.py 一并覆盖成了旧版，其中
  configs-jili.py（95 行）/ configs-panda.py（42 行）**没有** is_top_new_configs；
  新镜像 20261003-ben 里的 /app/tada|panda/configs.py（101 / 47 行）是有这个函数的 ——
  宿主机文件把镜像里正确的覆盖掉了，导致 import 失败、启动即崩。

影响面核查（宿主机文件 vs 镜像）：
  api 92 行/0 函数  ⇄ 镜像 92/0   一致
  pg 175/1          ⇄ 镜像 175/1  一致
  pp 96/1           ⇄ 镜像 96/1   一致
  jili 95/0         ⇄ 镜像 101/1  **不一致（旧）**
  panda 42/0        ⇄ 镜像 47/1   **不一致（旧）**
  ppk / playson / g759 宿主机没有对应文件 → 不挂载、直接用镜像  → 正常
```

### 修复（已执行，两台）

```text
1. 从镜像里取出正确的配置覆盖宿主机文件：
     docker run --rm --entrypoint sh <game-service-tada:20261003-ben>  -c "cat /app/tada/configs.py"  > conf/configs-jili.py
     docker run --rm --entrypoint sh <game-service-panda:20261003-ben> -c "cat /app/panda/configs.py" > conf/configs-panda.py
   原文件备份：/root/conf-configs-backup-20261003/（两台都有）
2. 容器本来就带 --restart=always，文件换掉后崩溃循环自己重启即生效，无需手工重建
3. 结果：两台 jili / panda 均 Up 且端口在监听，01/02 各 9 个厂家容器全部 running

关联：这次和 10-02「conf 被同步覆盖」是同一根因链 —— 当天只按用户要求恢复了 conf/domains，
      conf/configs-*.py 当时标注为遗留项，今天由 jili/panda 崩溃暴露出来并已修复。
```

## 四、监控脚本完善（v2）

```text
针对昨天「一次发版就用光调试期 3 条配额」的问题，本版新增：
  1. 发版窗口抑制：检测到 rsync/start.sh/stop.sh 时（及结束后 DBQP_MONITOR_RELEASE_GRACE=600s 内），
     容器的「消失 / 重建 / 重启」合并成一条「发版窗口提示」，同一窗口只发一条，
     且**不消耗调试期告警配额**
  2. 窗口结束后仍未恢复 → 自动补一条告警（不会被窗口吞掉，用 suppressed 标记跟踪）
  3. 重启循环识别：status=restarting 明确标注「重启循环，通常是启动即崩」并附
     **容器最近 3 行日志**（今天 jili/panda 的 ImportError 就是这样一眼看出来的）
  4. 静默自动复位选项 DBQP_MONITOR_AUTO_RESET_HOURS（默认关闭，调试期可设 6 → 6 小时后自动恢复告警）
  5. 宿主根盘阈值（默认 85%）、日志 4MB 轮转、心跳按真实统计输出
  6. 保留：SSH 重试 + 连续 2 轮失败才报、持续告警冷却 30 分钟、--baseline、静默文件、--reset-alerts
  7. 修 bug：告警计数/静默标记原先写在状态落盘之后导致静默不生效，改为最后统一落盘

桩数据自测（不真发群）：
  场景 1 发版窗口内 running → restarting：只出「发版窗口提示」，状态标记 suppressed，告警数为 0 ✅
  场景 2 窗口过期后仍 restarting：补发告警，正文含「状态=restarting」+「最近日志：…readonly database…」✅
```

## 五、部署与验证

```text
脚本：docker/deploy/hongkong/critical_restart_watch.py → prod-01 /opt/dbqp-scripts/
凭据：/opt/dbqp-hk-ops/container-watch.env（600；PROJECT_NAME=香港项目、
      DBQP_WATCH_HOSTS=203.0.113.1,203.0.113.1、DBQP_MONITOR_MAX_ALERTS=3）
定时：systemd dbqp-container-watch.service + .timer（*:0/1，active）

验证：
  · --show：2 台 × 9 厂家 = 18 个容器逐条打印，全部 running、端口监听
    （jili restarts=16/15、panda restarts=14/15 是本次崩溃循环累积，基线后不再误报）
  · --reset-alerts：调试期配额清零、解除静默
  · --baseline：重新铺底 18 个容器（不发告警）
  · --dry-run：alerts=0
  · timer：active，每分钟执行一次
```

## 六、日常使用

```bash
set -a; . /opt/dbqp-hk-ops/container-watch.env; set +a
python3 /opt/dbqp-scripts/critical_restart_watch.py --show            # 快照
python3 /opt/dbqp-scripts/critical_restart_watch.py --baseline        # 重铺基线（不发告警）
python3 /opt/dbqp-scripts/critical_restart_watch.py --reset-alerts    # 解除调试期静默
touch /opt/dbqp-hk-ops/container-monitor-quiet                        # 临时静音（删除即恢复）
systemctl status dbqp-container-watch.timer; tail -f /var/log/dbqp-hk-restart-watch.log
```

## 七、遗留与建议

```text
1. 任何一次全量同步（rsync /data/server-runtime）都必须带 --exclude 'conf' 或至少
   --exclude 'conf/domains' --exclude 'conf/configs-*.py'：今天这两个崩溃就是 conf 被覆盖导致的。
   建议把 conf/configs-*.py 也纳入 /opt/dbqp-hk-ops 安全副本 + restore_hk_domains.sh 一起恢复。
2. 发版流程建议加一步：发布后自动比对「宿主机 conf/configs-<厂家>.py」与「镜像内 configs.py」，
   不一致就报警（本次故障靠看容器日志才发现）。
3. 调试期告警上限 3 条：如果希望发版窗口不影响配额，本版已实现（发版窗口内不计入）。
```

## 八、关联

```text
docker/deploy/hongkong/critical_restart_watch.py（本版脚本）
docker/doc/2026-10-02-1645-【架构改造】香港全厂家容器状态监控上线（参考巴西）.md（上一版）
docker/doc/2026-10-02-1615-【故障处理】香港0102配置被同步覆盖与一键恢复防复发.md（conf 被覆盖根因）
master/docker/scripts/critical_restart_watch.py（巴西参考版）
```
