---
id: "doc-ce9eb4728a08"
title: "【问题排查】测试环境 bigdata 队列积压 46000：根因与「队列守护自愈」加固"
date: "2026-10-14T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "Redis", "自动化", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-14-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83big_data%E9%98%9F%E5%88%97%E7%A7%AF%E5%8E%8B%E5%AE%9E%E6%B5%8B%E6%A0%B9%E5%9B%A0%E4%B8%8E%E9%98%9F%E5%88%97%E5%AE%88%E6%8A%A4%E8%87%AA%E6%84%88.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-14-【问题排查】测试环境big_data队列积压实测根因与队列守护自愈.md"
sourceSha256: "a8dfc11e5d84522ab168a2413f34e828e706a617338d6ce6461c59aadef64ded"
sourceSystem: "project-doc"
---

# 【问题排查】测试环境 bigdata 队列积压 46000：根因与「队列守护自愈」加固

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-14-【问题排查】测试环境big_data队列积压实测根因与队列守护自愈.md`

> 整理日期：2026-10-14 00:00｜日期依据：文件名日期

- 日期：2026-10-14
- 环境：**测试环境**（15.152.247.196，`youdianse-dev-php-*` 三容器）
- 触发：后端反馈「测试环境定时任务 start.sh 守护进程是否开启，big_data 队列堆积 46000 条」「发版后 cron 没有同步开启」
- 结论：**根因是 php-cron 容器没有重建，运行中的容器仍是旧配置（少了 `bigDataJob:queue` 这个消费守护）**；已修复，并新增每 10 分钟自检自愈的看护脚本防复发。

---

## 一、现象

```text
· 测试环境 big_data 队列积压约 46000 条，埋点上报（18 测试后台-埋点统计）无数据 / 延迟
· 后端反馈"发版后 cron 守护进程就没了"，需要人工去拉起来
```

---

## 二、排查过程与根因

### 2.1 队列消费守护的架构

```text
php-cron 容器（与 web 共用同一镜像）本身就是队列消费守护：
  entrypoint: /usr/local/bin/cron-entrypoint.sh
  command   : /usr/local/bin/queue-watchdog.sh
  QUEUE_WORKERS: "crontab:queue job:queue bigDataJob:queue"   ← 三个常驻消费进程
  watchdog 对每个 worker 执行 php bin/shell.php <class> <queue>，退出后 5 秒自动重启
```

### 2.2 关键证据

```text
① 容器声明的环境变量（docker inspect）：
   QUEUE_WORKERS=crontab:queue job:queue            ← 只有 2 个！少了 bigDataJob:queue
② 容器内实际进程（docker top）：
   shell.php crontab queue / shell.php job queue     ← 只有 2 个
③ 守护日志（runtime/logs/queue/watchdog.log）：
   starting workers: crontab:queue job:queue
④ 但部署机上的 compose 文件里已经是正确值：
   QUEUE_WORKERS: "crontab:queue job:queue bigDataJob:queue"
```

### 2.3 根因

**部署机上的 `docker-compose.yml` 已经加上了 `bigDataJob:queue`，但 php-cron 容器自当天 10:58 之后就没有再重建过**，
容器沿用创建时写入的环境变量（旧值 2 个 worker），因此 `big_data` 队列长期没有消费者 → 积压 4.6 万条。

> 关键点：`docker restart` / 宿主机重启 / `restart: always` **都只复用容器创建时的配置**，
> 只有 **重建容器（`docker compose up -d --force-recreate`）** 才会读到 compose 的新环境变量。

**为什么没被发现**：CICD 里其实已有 `check_bigdata_queue_worker()`（发布时校验 `shell.php bigDataJob queue`，
缺失会在部署报告里写「队列：missing」），但它**只在发布流程里执行**——本次是「改了 compose、没有发布」，
两次发布之间没有任何检查，所以静默了两天。

### 2.4 关于"发版后守护进程就没了"

实测（`docker compose --dry-run`）在测试环境复现：发布时执行的是
`docker compose --profile cron up -d --force-recreate --remove-orphans web nginx cron`，
**cron 容器在每次发布都会被重建**（`--force-recreate`），重建后应加载最新配置。
若发布时选择的模式是「可多机扩容部署（web + nginx）」，则不会重建 cron；
而 dev 分支界面上该选项是置灰不可选的，默认始终 `with_cron`。
→ 因此"发版后掉"更可能是**发布模式选错**或**未按发布流程重建**，本次已用自愈守护兜住。

---

## 三、处置（已执行并验证）

| 步骤 | 动作 | 结果 |
| --- | --- | --- |
| 1 | 只重建 cron 容器（不动 web/nginx）：`docker compose --env-file .ops-build.env --profile cron up -d --force-recreate --no-build cron` | 容器重建成功 |
| 2 | 校验容器环境变量 | `QUEUE_WORKERS=crontab:queue job:queue bigDataJob:queue` ✅ |
| 3 | 校验实际进程 | `docker top` 显示 3 个 `shell.php`：`crontab queue` / `job queue` / `bigDataJob queue` ✅ |
| 4 | 校验守护日志 | `starting workers: crontab:queue job:queue bigDataJob:queue` ✅ |
| 5 | 校验消费是否生效 | `bigDataJob-queue.log` 持续输出 `BigDataQueue: App\Jobs\BigData\ClickReportJob_... =>success`（启动首分钟 158 条） |
| 6 | 校验积压 | 容器内按应用自身 Redis 配置实测：`18game_queue_big_data = 0`（所有队列均为 0）✅ |
| 7 | 新增自愈看护 + cron | `ops/test/scripts/youdianse-queue-guard.py`，`*/10 * * * *`；首跑输出 `ok workers=3 (crontab:queue, job:queue, bigDataJob:queue)` ✅ |

---

## 四、防复发：新增「队列守护自愈」看护

新增脚本：`ops/scripts/youdianse-queue-guard.py`（**测试环境与线上后端共用同一份脚本**，cron 每 10 分钟）

```text
0) 自动识别 php-cron 容器（按 compose 服务标签 `cron` 查找，测试/生产通用，无需按环境改脚本）
1) **以 compose 配置为期望值**读 QUEUE_WORKERS（`docker compose config` → 解析 compose 文件 → 容器声明兜底）
2) 用 /proc/<pid>/cmdline 逐个比对容器内实际在跑的 shell.php <class> <method>（不依赖容器内 ps，
   php 官方镜像里没有 ps）
3) 有缺失 → 自动重建 php-cron 容器（只重建 cron，不影响 web/nginx 与业务请求）→ 等待 15 秒复检
4) 只在"确实做了处置"时通知群（沿用测试环境既有 /etc/youdianse-health-alert.json 的 bot 配置），避免刷屏
5) 日志：/var/log/youdianse-queue-guard.log（cron 重定向另有 .cron.log）
```

可调环境变量：`YDS_COMPOSE_DIR` / `YDS_COMPOSE_ENV_FILE` / `YDS_CRON_CONTAINER` / `YDS_QUEUE_GUARD_WAIT` / `YDS_QUEUE_GUARD_LOG`。

**验证**：首跑检测到 3/3 worker 全部在跑（`ok workers=3`）；自愈动作与第三节步骤 1 是同一条 compose 命令（已实测可恢复）。

### 4.1 【重要】设计修正：期望值必须取 compose，不能取容器自身声明

第一版自测时发现一个致命缺陷：期望值取自**容器自己声明的 QUEUE_WORKERS**，而本次故障恰恰是
「容器声明过期（2 个）、compose 已更新（3 个）」——两边都读容器的话**两边都是 2 个，永远检测不出来**。

已修正为优先级：**① `docker compose config`（展开 env 与 YAML anchor，配置真值）→ ② 直接解析 compose 文件 → ③ 兜底才用容器声明**，
并在日志/通知里标明「期望来源」。

### 4.2 端到端自愈实测（在测试环境真实复现故障后验证）

```text
① 把测试机 compose 临时改成 2 个 worker 并重建容器 → 容器声明=crontab:queue job:queue，实际进程=2
② 恢复 compose（3 个 worker），容器仍是旧配置 —— 精确复现本次生产故障形态
③ 跑守护：
   missing workers=['bigDataJob:queue']（期望来源=compose(config)，当前在跑 2 个）-> healing（重建 cron 容器）
   heal result: 已自动重建并恢复 still=[]
④ 复检：容器声明 = crontab:queue job:queue bigDataJob:queue，实际进程 = 3 ✅
```

> 自测用的临时改动已完全还原（compose 当前为 3 个 worker），临时文件已清理。

---

## 五、给研发/运维的注意事项

1. **改了 `docker-compose.yml` 的环境变量后，必须重建容器才生效**——`docker restart` 无效。
   正规做法是走一次发布（CICD）或手工 `docker compose up -d --force-recreate <service>`。
2. **新增/调整队列名时**，除了改 `QUEUE_WORKERS`，还要确认业务侧 `bin/shell.php <class> <queue>` 的类与方法真实存在，
   否则 watchdog 会 5 秒一次空转重启（日志会持续 `exited status=...`）。
3. 发布后请看部署报告里的「队列：ok / missing」一行；现在另外有 10 分钟自检兜底。
4. 埋点/数数链路（18 测试后台-埋点统计 → 数数 YDS 测试环境）本次一并复核：
   `big_data` 队列消费已恢复；`logbus-v2`（数数上报容器）近 6 小时 0 error，链路容器正常。
   若仍有单条埋点未上报，需要业务侧按「事件 → 队列 → logbus」逐段核对，运维侧可提供对应时间点的消费日志。

---

## 六、生产部署 + 两环境最终核对（2026-10-14 晚）

按需求把**同一份脚本**部署到线上后端，作为生产兜底。

### 6.1 生产部署

| 项 | 值 |
| --- | --- |
| 脚本路径 | `/opt/docker-youdianse-php/ops/scripts/youdianse-queue-guard.py`（与测试环境**同一份**） |
| 容器识别 | 自动（生产 `youdianse-main-php-cron`、测试 `youdianse-dev-php-cron`，无需按环境改脚本） |
| 通知 | 复用 `/etc/youdianse-health-alert.json`，并加 `YDS_QUEUE_GUARD_EXTRA_CHATS="-4929911895"`（额外发 18game运维 群） |
| cron | `*/10 * * * *`（测试与生产 root crontab 均已写入） |

### 6.2 最终核对（测试 + 生产，全部通过）

| 检查项 | 测试环境 15.152.247.196 | 生产 16.209.16.108 |
| --- | --- | --- |
| compose `QUEUE_WORKERS` | `crontab:queue job:queue bigDataJob:queue` ✅ | 同 ✅ |
| 容器声明的 worker | 3 个 ✅ | 3 个 ✅ |
| 实际运行的 worker 进程 | 3（crontab / job / bigDataJob）✅ | 3 ✅ |
| 队列积压 | `big_data=0 job=0 crontab=0` ✅ | bigDataJob 日志持续 `=>success`（实时消费中）✅ |
| 守护 cron | 已写入 ✅ | 已写入 ✅ |
| 守护运行结果 | `ok workers=3`；**自愈实测通过**（4.2 节）✅ | `ok workers=3 期望来源=compose(config)` ✅ |

### 6.3 遗留提示（非阻塞，建议处理）

- 测试机上的 ops 仓库（`/opt/docker-youdianse-php`）落后于远端，`docker-compose.yml` 是**本地手改**
  （内容与仓库提交 `2dc42f3` 等价）；建议在测试机 `git pull` 同步，避免后续发布与本地改动冲突。
  ⚠️ 该机还有 `cicd-web/config/settings.json`、`ops/test/install-health-monitor.sh` 两处本地改动，
  同步前先确认归属，不要直接覆盖。

---

## 七、回滚

```bash
# 1) 撤掉自愈守护（如需）
sudo crontab -l | grep -v youdianse-queue-guard | sudo crontab -
sudo rm -f /opt/docker-youdianse-php/ops/scripts/youdianse-queue-guard.py

# 2) 恢复旧队列配置（不建议）：把 compose 的 QUEUE_WORKERS 改回去后重建 cron
cd /opt/docker-youdianse-php && sudo docker compose --env-file .ops-build.env --profile cron up -d --force-recreate --no-build cron
```
