---
id: "doc-569981c4d824"
title: "【架构改造】关键容器「严禁重启」监控上线（api / pp / pg）"
date: "2026-10-02T18:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "Docker", "监控告警", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-10-02-1820-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E5%85%B3%E9%94%AE%E5%AE%B9%E5%99%A8api-pp-pg%E4%B8%A5%E7%A6%81%E9%87%8D%E5%90%AF%E7%9B%91%E6%8E%A7%E4%B8%8A%E7%BA%BF%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-10-02-1820-【架构改造】关键容器api-pp-pg严禁重启监控上线记录.md"
sourceSha256: "9842281e62b0f33e40d024473b453a69e2e82c4a4a2087485ce34c6f9640f546"
sourceSystem: "project-doc"
---

# 【架构改造】关键容器「严禁重启」监控上线（api / pp / pg）

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-10-02-1820-【架构改造】关键容器api-pp-pg严禁重启监控上线记录.md`

> 整理日期：2026-10-02 18:20｜日期依据：文件名日期

时间：2026-10-02 18:20（北京）/ 10:20（UTC）
对象机器：后台 01 `203.0.113.1`、后台 02 `203.0.113.1`（被监控方）
　　　　　备用入口机 `34.151.249.53`（跑定时任务）
需求：
　　· 开发（Ben C++）：「巴西线上的厂商不能重启了哈」「除了今天更的几个厂商，都不能重启。重启会有问题」
　　　「一定不能重启哈」，最后拍定**先不改配置、只做监控**（「算了，监控到起」）
　　· 运维：担心「容器如果压力太多有概率重启容器」（start.sh 里是 `--restart=always`）
结论：新增专用监控 `critical_restart_watch.py`，**每分钟**盯 01/02 上今天更新的
　　　`game-service-api-prod / pp-prod / pg-prod` 共 6 个容器，任何重启/重建/掉线/内存告急
　　　立刻发飞机群。**不改容器、不改重启策略**（开发明确先不动）。

---

## 一、上线前的现状基线（2026-10-02 实测）

```text
prod-01（203.0.113.1）                 prod-02（203.0.113.1）
  api-prod  running restarts=0 id=f7e9752db6b2   api-prod  running restarts=0 id=587ad9c4e1ab
  pp-prod   running restarts=0 id=b668823fcaf5   pp-prod   running restarts=0 id=8e050e9694f8
  pg-prod   running restarts=0 id=87d09e8bbf28   pg-prod   running restarts=0 id=4479ab6189fb

共同点：RestartPolicy = always（start.sh 里 docker run --restart=always）
        容器内存上限 = **未限制**（HostConfig.Memory=0）
        宿主机：32 GB，实测可用约 23 GB
```

```text
为什么「没有内存上限」反而要注意：
  容器 limit 不设，就不会因为容器配额被 OOM；
  真正会触发重启的是**宿主机内存耗尽**时内核 OOM 杀掉容器进程 →
  docker 的 --restart=always 立刻把它拉起来 = 一次重启。
所以监控里额外加了「宿主机可用内存低于阈值就提前预警」，在重启发生前先喊人。
```

## 二、监控设计

```text
脚本：docker/scripts/critical_restart_watch.py
部署：入口机 /opt/pgserver/docker/scripts/critical_restart_watch.py（0755）
频率：每分钟（入口机 crontab）
对象：01/02 × { game-service-api-prod, game-service-pp-prod, game-service-pg-prod }

判定（命中任意一条立即报警，不等多次采样）：
  1) RestartCount 比上次多        → 容器被 Docker 重启过（最关键的信号）
  2) 容器 ID 变了                 → 容器被删掉重建（start.sh 的 stop+rm+run 会这样）
  3) State.Status != running      → 当前不在运行（exited/restarting/dead/created/paused）
  4) 容器查不到                    → 容器缺失
  5) 宿主机可用内存 < 3000 MB     → OOM 前置预警（可用 DBQP_HOST_MEM_MIN_MB 调阈值）

抑制与恢复：
  · 同一状态的重复采样不会重复发（状态文件里记 alerted 标记）
  · 「重启次数+1」「容器被重建」是一次性事件，不会在下一轮误发「已恢复」
  · 「容器缺失 / 不在 running / 内存告急」是持续状态，恢复时补一条「已恢复」通知

采一次只要一次 SSH（同一条命令里顺带读 /proc/meminfo），开销很小。
```

## 三、报警长这样

```text
【DBQP 巴西项目｜关键容器重启监控｜报警】@运维 @Ben_Bird @benb6879
时间：北京 2026-10-02 18:21:00 ｜ 巴西圣保罗 2026-10-02 07:21:00
⚠️ 开发 2026-10-02 明确要求：今天更新的 api / pp / pg **千万不能重启**。
- game-service-api-prod（203.0.113.1 / 01）id=f7e9752db6b2 status=running restarts=0 策略=always
  → **发生重启**（restarts 0 → 1）
  started=2026-10-02T09:15:03.123456789Z
  OOMKilled=false ExitCode=0 RestartPolicy=always

（内存预警的样子）
- ⚠️ 宿主机内存告急：203.0.113.1 / 01 可用 1800 MB（阈值 3000 MB）
  → 逼近 OOM，可能被杀进程后由 --restart=always 自动重启容器，请尽快处理
```

## 四、部署与验证

```text
1) 脚本部署：本地与入口机 md5 一致 741382cf18b3ec98370189f697b3a46c
2) 基线：首次运行静默建基线（6 个容器 + 2 条内存记录），实测 rc=0
3) dry-run：`[dry-run] 检查 6 个容器 | alerts=0 recovers=0`（内存充足，正常）
4) 定时任务：入口机 crontab 新增
     * * * * * set -a; . /opt/benbot-runtime.env; set +a; \
       /usr/bin/python3 /opt/pgserver/docker/scripts/critical_restart_watch.py \
       >> /var/log/dbqp-restart-watch.log 2>&1
   加之前备份：/root/crontab.bak-20261002-101832-before-restart-watch
5) cron 生效实测：syslog 里 10:19:01、10:20:01 都有该命令执行记录，
   状态文件 mtime 逐分钟刷新（18:19:02 → 18:20:03）
6) 通道测试：--test-notify 发群成功，接口返回 {"ok":true}（message_id 7595）
7) 逻辑回归（本地假数据，不碰线上容器）10 个场景全过：
   基线静默 / 稳态静默 / restarts 0→1 报警 / 重复采样不重复报 /
   ID 变化报警 / 重复采样不报 / status=exited 报警 / 回 running 发恢复 /
   容器缺失报警 / 容器重新出现报警；
   另加内存：低于阈值报警、持续低不重复、恢复发恢复
```

## 五、运维手册

```bash
# 看当前快照（6 个容器 + 内存），不写状态不发群
/usr/bin/python3 /opt/pgserver/docker/scripts/critical_restart_watch.py --show

# 只检查不落状态不发群
/usr/bin/python3 /opt/pgserver/docker/scripts/critical_restart_watch.py --dry-run

# 验证飞机群通道（发一条“·通道测试”，不采集）
/usr/bin/python3 /opt/pgserver/docker/scripts/critical_restart_watch.py --test-notify

# 看日志 / 状态
tail -20 /var/log/dbqp-restart-watch.log
cat /var/tmp/dbqp-restart-watch.json

# 临时停用 / 恢复（入口机 crontab 里注释那一行即可）
crontab -l | sed 's|^\* \* \* \* \* \(set -a; . /opt/benbot-runtime.env.*critical_restart_watch.*\)|#PAUSED \1|' | crontab -

# 调整内存预警阈值（默认 3000 MB）——在 crontab 那行前面加：
#   DBQP_HOST_MEM_MIN_MB=5000
```

```text
要换监控对象：改脚本里的 WATCH（IP → 容器名列表），保存后重跑一次即可；
旧对象的键留在状态文件里不影响，删掉 /var/tmp/dbqp-restart-watch.json 就重新建基线。
```

## 六、局限与建议（未执行，等开发/运维决定）

```text
1) 本监控只是「事后第一时间知道」，**不能阻止重启**。真要杜绝，需要改配置（开发说先不动）：
   · 把 --restart=always 改成 on-failure 或 no（改 start.sh，需重发版）
   · 或给容器加 --memory 上限，避免宿主内存被吃光导致全局 OOM
2) 宿主机内存阈值 3000 MB 是按 32 GB 机器给的保守值；要更早预警可调到 5000 MB。
3) 现在 01/02 上所有厂商容器都是 --restart=always，其它厂商同样「不能重启」，
   如果以后要把它们也纳入本监控，往 WATCH 里加即可。
```

## 七、相关文件

```text
docker/scripts/critical_restart_watch.py                 # 本次新增
/opt/pgserver/docker/scripts/critical_restart_watch.py    # 入口机部署副本
/var/log/dbqp-restart-watch.log、/var/tmp/dbqp-restart-watch.json
docker/scripts/container_health_monitor.py                # 既有容器监控（2 分钟一轮，覆盖全厂家）
docker/doc/2026-09-24-1445-…容器监控只留0102并发版窗口自动静默….md   # 容器监控上一轮改造
```

---

## 后续（2026-10-02 18:30 更新）

```text
本文这版只盯 api / pp / pg 三个厂家。同日晚些按用户要求升级为「全部厂家」：
监控对象扩到 01/02 × 9 厂家 = 18 个容器，并完善了脚本（信息更全、发版窗口提示、
别名兼容、状态键自动清理等），频率仍是每分钟一次。
详见：docker/doc/2026-10-02-1830-【架构改造】全厂家容器状态监控升级-18个容器记录.md
```
