---
id: "doc-f6015db0cb82"
title: "【运维】入口机 nginx CPU 偏高排查 + 浏览器巡检迁移到 03"
date: "2026-09-18T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "Docker", "Nginx", "监控告警", "自动化"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-18-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91%E5%85%A5%E5%8F%A3%E6%9C%BAnginx-CPU%E5%81%8F%E9%AB%98%E6%8E%92%E6%9F%A5-%E6%B5%8F%E8%A7%88%E5%99%A8%E5%B7%A1%E6%A3%80%E8%BF%81%E7%A7%BB%E5%88%B003.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-18-【运维】入口机nginx-CPU偏高排查-浏览器巡检迁移到03.md"
sourceSha256: "cadd7eb1f43b4569cfe857639645174cf7e3e8ea1bd9b2554e6af19b5fa5c2a4"
sourceSystem: "project-doc"
---

# 【运维】入口机 nginx CPU 偏高排查 + 浏览器巡检迁移到 03

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609180000-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BLinux%2BShell-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91%E5%85%A5%E5%8F%A3%E6%9C%BA%20nginx%20CPU%20%E5%81%8F%E9%AB%98%E6%8E%92%E6%9F%A5%20%2B%20%E6%B5%8F%E8%A7%88%E5%99%A8%E5%B7%A1%E6%A3%80%E8%BF%81%E7%A7%BB%E5%88%B0%2003.md)

> 整理日期：2026-09-18 00:00｜日期依据：文件名日期

时间：2026-09-18
对象机器：`bizops-saopaulo-nginx-standby-01`（192.0.2.13 / 192.0.2.1）——**线上真正入口**，非常重要
告警现象：beszel 反复报 CPU 高于阈值（1 分钟均值 84.13% / 74.58% / 82.99% / 75.33%）
结论：**入口机上每小时错峰跑的 Playwright 浏览器巡检（game_availability_monitor）吃 CPU**；
　　　已把 7 条浏览器巡检迁到 03，入口机 CPU 回落到平均 0.2%。
全程只读排查 + 迁移，未影响线上用户；未通知飞机群。

---

## 一、排查过程（只读）

### 1. 机器规格与当时状态

```text
4 vCPU / 7.9 GB 内存（内存不是瓶颈：available 7.0 GB）
排查时 load 0.00、CPU 98.5% idle —— 说明不是持续高负载，而是【间歇性尖峰】
```

### 2. 这台机器上的定时任务

```text
*/2 * * * *  container_health_monitor.py     # SSH 到 01/02/03 看容器状态（轻）
*/2 * * * *  entry_health_monitor.py         # 公网 HTTPS 探活（轻）
 0/8/16/24/32/40/48 * * * *  game_availability_monitor.py --vendor X   # 【浏览器巡检】7 个厂家错峰
56 * * * *  pg67_games_watch.py              # 纯 HTTP 检查（轻）
```

`game_availability_monitor.py` 会调用 `post_deploy_browser_smoke.py`（202KB 的 Playwright 脚本），
真正做的是：打开 H5 大厅 → 点游戏卡片 → 等游戏 shell 加载 → 试玩一次。

### 3. 采样定位（每 5 秒记录整体 CPU + TOP 进程）

| 时间（UTC） | 当时跑的巡检 | 采到的 CPU | TOP 进程 |
| --- | --- | --- | --- |
| 10:40:09 ~ 10:40:14 | vendor_d（:40 分） | **42% ~ 43%** | chrome-headless |
| 10:48:07 ~ 10:48:17 | g759（:48 分） | **35% → 71% → 89%** | chrome-headless |

```text
采样期内出现的 TOP 进程：containerd(基线) / chrome-headless(浏览器巡检时) / python3(驱动脚本)
→ 结论明确：CPU 尖峰 = Playwright 的 chromium 在软件渲染模式跑游戏（没有 GPU，全靠 CPU）
  4 vCPU 的机器上很容易被 2~3 个核的浏览器顶到 80%+，正好对上 beszel 的 75~84% 告警
```

## 二、迁移方案与实施

### 思路

```text
浏览器巡检属于"重活"，不该跑在流量入口机上；03（bizops-saopaulo-sanic-prod-03）是空闲机器，
已有 docker，把巡检放进容器跑，既不占入口机 CPU，也不污染 03 的系统环境。
入口机只保留轻量检查（container_health / entry_health / pg67_games_watch）。
```

### 03 上的落地结构

```text
/opt/bizops-scripts/game-monitor/
├── docker/scripts/game_availability_monitor.py     # 从入口机拷贝的最新版（8308B）
├── docker/scripts/post_deploy_browser_smoke.py     # 最新版（202202B，ROOT_DIR = /opt/bizops-scripts/game-monitor）
├── docker/scripts/pg67_games_watch.py              # 备用（当前仍在入口机跑，未迁）
└── run_game_monitor.sh                             # 执行包装：在 bizops-browser-test 容器里跑单个厂家

镜像：bizops-browser-test:latest（在 03 上用 /opt/bizops-browser-test/Dockerfile 重建，自带 Playwright+Chromium）
状态：/var/tmp/bizops-game-availability-<vendor>.json（已从入口机同步过来，保证告警计数连续）
日志：/var/log/bizops-game-availability.log、/var/log/bizops-game-availability-cron.log
凭据：--env-file /opt/benbot-runtime.env（TG token 等）
```

`run_game_monitor.sh` 核心（完整见仓库 `docker/scripts/run_game_monitor_on_03.sh`）：

```bash
docker run --rm --network host --shm-size=1g \
  -v /opt/bizops-scripts/game-monitor:/opt/bizops-scripts/game-monitor \
  -v /var/tmp:/var/tmp -v /var/log:/var/log \
  --env-file /opt/benbot-runtime.env \
  --entrypoint python3 bizops-browser-test:latest \
  /opt/bizops-scripts/game-monitor/docker/scripts/game_availability_monitor.py --vendor "$VENDOR"
```

### crontab 变更

```text
入口机：7 条 game_availability_monitor 全部注释（前缀 #MOVED-TO-03-20260918(rollback: remove prefix) ）
        保留：container_health_monitor、entry_health_monitor、pg67_games_watch、disk_cleanup
03    ：新增 7 条，时间与原来完全一致（:00 pg / :08 vendor_a / :16 pp / :24 popok /
        :32 vendor_c / :40 vendor_d / :48 g759），调用 /opt/bizops-scripts/game-monitor/run_game_monitor.sh
备份  ：入口机 /root/crontab.bak-20260918-1050-before-move-browser-monitor-to-03
        03    /root/crontab.bak-2026-09-18-1050-before-add-browser-monitor
```

## 三、验证结果

```text
① 03 接管成功
   11:00:01 start vendor=pg   → 11:00:22 end  rc=0   「pg: OK fails=0 oks=14 alerted=False」
   11:08:01 start vendor=vendor_a → 11:08:24 end  rc=0   「vendor_a: OK fails=0 oks=12 alerted=False」

② 入口机不再跑浏览器巡检
   /var/log/bizops-game-availability.log 里 11:00 之后新增条目 = 0

③ 入口机 CPU 明显回落
   迁移前：42% / 43% / 71% / 89%（浏览器巡检时）
   迁移后：11:00 起 144 个采样点，平均 0.2%，最大 5%；load average 0.00 / 0.00 / 0.04
```

## 四、顺带发现（同一台机器，另一件事）

```text
入口机上有 84 个 chrome-headless <defunct>（僵尸）进程，父进程是备用机器人容器里的 bot.py
（PID 3855641，/app/app/bot.py），最早来自 9/9、9/11 的运行。

影响：RSS=0、CPU=0 ——【不占 CPU 也不占内存】，只是占进程表项；
      不是这次 CPU 告警的原因（告警是 cron 浏览器巡检造成的，已迁移）。
清理：✅ 已于 2026-09-18 12:29 UTC 执行 docker restart bizops-ben-bot-standby，
      僵尸 84 -> 0，无 chrome/chromium 残留，容器恢复正常（Up），启动通知正常发出。
      根治仍建议在机器人代码里给浏览器子进程加 wait（避免再次堆积）。
```

### 清理操作记录（可复现）

```bash
# 清理前
ssh root@192.0.2.13 'ps -eo stat | grep -c "^Z"'      # 84
ssh root@192.0.2.13 'docker inspect bizops-ben-bot-standby \
  --format "{{.Config.Image}} {{.HostConfig.RestartPolicy.Name}}"'   # bizops-ben-bot:latest / unless-stopped

# 执行清理（重启容器 → 旧进程全部销毁，僵尸随之消失）
ssh root@192.0.2.13 'docker restart bizops-ben-bot-standby'

# 清理后
ssh root@192.0.2.13 'ps -eo stat | grep -c "^Z"'      # 0
ssh root@192.0.2.13 'docker ps --filter name=bizops-ben-bot-standby --format "{{.Status}}"'  # Up
```

```text
为什么可以直接重启：这台机器上的 bizops-ben-bot-standby 是【备用】机器人实例，
线上主实例在宝塔（bizops-ben-bot）。重启期间备用实例短暂不可用，主实例照常服务，
重启后备用实例自动恢复 polling（Entrypoint 里 BEN_BOT_POLL=1 时 exec python /app/app/bot.py）。
本次重启后日志显示正常：机器人启动通知已发送到监控群。
```

## 五、回滚方式

```bash
# 入口机恢复浏览器巡检
cp /root/crontab.bak-20260918-1050-before-move-browser-monitor-to-03 /tmp/ct
crontab /tmp/ct      # 或用 crontab -e 把 #MOVED-TO-03-20260918 前缀删掉

# 03 停掉巡检
crontab -l | grep -v "run_game_monitor.sh" | crontab -
```

## 六、后续建议

```text
1) 入口机只做"流量入口 + 轻量探活"，不要再往上放浏览器/编译/打包类重活。
2) 机器人容器里如果还有浏览器任务（发布预热等），同样建议改到 03 的容器里跑，
   并确保子进程被回收（84 个僵尸就是没回收的证据）。
3) 03 现在同时承担：资源同步容器、浏览器巡检容器；浏览器巡检 1 厂家约 20~25 秒、
   每小时 7 次，压力很小；后续如果加更多浏览器任务，注意给容器加 --cpus 限制。
4) 入口机自身仍是单点，建议后续评估再加一台入口做高可用（与 2026-09-18 双后端容灾分开）。
```

---

## 后续（2026-09-29 更新）

```text
本文迁移到 03 的浏览器巡检（游戏可用性监控），已于 2026-09-29 按用户要求整体停用：
「目前有真人测试挂 VPN 到游戏里面真人测试了」，不再需要这套自动化巡检。
03 上 7 条 hourly cron 已注释（备份 /root/crontab.bak-20260929-141344-before-disable-game-availability），
入口机那 7 条保持注释状态。
详见：docker/doc/2026-09-29-2217-【优化】游戏可用性巡检监控下线记录.md
```
