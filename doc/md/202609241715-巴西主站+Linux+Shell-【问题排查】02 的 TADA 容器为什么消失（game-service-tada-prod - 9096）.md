---
id: "doc-0bee5104822d"
title: "【问题排查】02 的 TADA 容器为什么消失（game-service-tada-prod / 9096）"
date: "2026-09-24T17:15:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Docker", "Nginx", "监控告警", "自动化", "故障排查"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-09-24-1715-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%9102%E7%9A%84TADA%E5%AE%B9%E5%99%A8%E6%B6%88%E5%A4%B1%E5%8E%9F%E5%9B%A0%E5%AE%9A%E4%BD%8D-%E5%B8%B8%E9%A9%BB%E4%BC%9A%E8%AF%9D%E6%89%8B%E5%8A%A8stop%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-09-24-1715-【问题排查】02的TADA容器消失原因定位-常驻会话手动stop记录.md"
sourceSha256: "eb5de031c789057388983ddb4be2e106c7649319087ad4163817edf90948dcdd"
sourceSystem: "project-doc"
---

# 【问题排查】02 的 TADA 容器为什么消失（game-service-tada-prod / 9096）

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-09-24-1715-【问题排查】02的TADA容器消失原因定位-常驻会话手动stop记录.md`

> 整理日期：2026-09-24 17:15｜日期依据：文件名日期

时间：2026-09-24 17:15（北京时间）/ 09:15（UTC）
对象机器：后台 02 `203.0.113.1`（dbqp-saopaulo-sanic-prod-02）
问题：02 的 `game-service-tada-prod`（TADA 主服务 9096）不见了，nginx 持续报
　　　`connect() failed (111: Connection refused) ... upstream: http://203.0.113.1:9096/`
结论：**不是故障、也不是自动任务，是有人在一个常驻 SSH 会话里手动执行了 `sh stop.sh tada`，
　　　`stop.sh` 会 stop + rm 把容器删掉，之后没有执行对应的 `start.sh`。**
　　　容器在 06:26:27 UTC（北京 14:26:27）被删，06:45 手动启动后恢复。
**本轮不发飞机群通知。**

---

## 一、先看指纹：是「被删除」而不是「崩溃退出」

```text
docker ps -a 全量里没有任何 tada 主服务容器（连 Exited / Restarting 都没有）；
start.sh 起容器时带 --restart=always，正常情况下崩溃会留下 Restarting/Exited 记录。
→ 只有显式 docker rm 才会让容器一点痕迹都不留。
```

`/data/server-runtime/stop.sh` 的实现正好就是 stop + rm：

```bash
stop_container() {
    local container_name="game-service-${v}-prod"
    docker stop "$container_name" >/dev/null 2>&1     # 先 SIGTERM（10 秒超时后强杀）
    docker rm   "$container_name" >/dev/null 2>&1     # 再删除
}
```

## 二、精确到秒的销毁时刻（journald 原始日志）

```text
06:26:27 dockerd: msg="stopping restart-manager" container=ad9aa6af12aa...331f
06:26:37 dockerd: msg="Container failed to exit within 10s of signal 15 - using the force"
                  container=ad9aa6af12aa...331f
06:26:37 systemd: docker-ad9aa6af12aa...331f.scope: Deactivated successfully.
06:26:37 systemd: docker-ad9aa6af12aa...331f.scope: Consumed 42min 25s CPU time
                  over 21h 30.072s wall clock time          ← 容器已连续跑了 21.5 小时
06:26:37 dockerd: received task-delete event from containerd
06:26:37 containerd: cleaning up dead shim / cleaning up after shim disconnected
06:26:38 kernel: docker0: port 3(vethdd086c0) entered disabled state
06:26:38 kernel: vethdd086c0 (unregistering): left promiscuous mode
06:26:38 systemd: var-lib-docker-rootfs-overlayfs-ad9aa6af12aa...331f.mount: Deactivated
```

```text
怎么读这几行：
  · 「signal 15 + 10 秒后 using the force」= 标准 docker stop 行为（先 SIGTERM，超时再 SIGKILL），
    说明是有人下了 docker stop，而不是容器自己崩了；
  · 「task-delete / veth 注销 / overlayfs mount Deactivated」= 容器随后被删除；
  · 容器 ID ad9aa6af12aa... 与 06:14:51 tada 日志里
    「Leader节点: ad9aa6af12aa (PID:32)」完全一致 —— 就是 02 上那个正在带 leader 租约的 tada 实例，
    即 02 当时是 TADA 的 user-sync leader，被停掉后 leader 才切走。
```

## 三、排除「新登录的人干的」：那个时间点没有任何新 SSH 登录

```text
06:20~06:36 之间，02 的 sshd 只有每 2 分钟一次的自动登录：
  06:20:02 / 06:22:02 / 06:24:01 / 06:26:02 / 06:28:02 / 06:30:01 / 06:32:02 / 06:34:02
  全部来自 203.0.113.1 —— 那是入口机上的「DBQP 容器监控」自己（每 2 分钟采集一次）。
除了它，没有其他来源成功登录过 02。
```

所以命令不是通过新连接执行的，而是**早已存在的终端**。

## 四、找到那个终端：一个从 9/18 挂到现在、工作目录就是 /data/server-runtime 的常驻会话

```text
02 上的常驻交互式 shell（2026-09-24 09:00 UTC 实测）：

  PID 700977  父进程 700974（sshd-session: root@pts/0）
  tty     : /dev/pts/0
  启动时间: Fri Sep 18 06:59:53 2026
  已存活  : 5 天 23 小时 49 分
  工作目录: /data/server-runtime        ← 正是执行 start.sh / stop.sh 的目录
  TCP 对端: 60.100.65.172:53068
  /dev/pts/0 最后活动时间: 2026-09-24 06:42:16 UTC（报警之后、重启之前）
```

```text
旁证：/root/.bash_history 最后写入时间是 2026-09-23 09:29，末尾是
      「sh start.sh api 20260923-ben / docker ps」（9/23 那次发版）
      —— 也就是说常驻会话里敲的命令还没落盘（bash 退出时才写历史），
      所以历史文件里查不到今天那条 stop.sh，这属于正常现象，不是没执行过。
```

**同一个人/同一台机器上，01 也有一个一样的常驻会话**（可选一并审计）：

```text
01 203.0.113.1：root@pts/1，启动于 Fri Sep 18 07:37:02，对端同样是 60.100.65.172，仍在线。
```

## 五、排除全部自动任务

| 候选 | 实际行为 | 是否嫌疑 |
| --- | --- | --- |
| `dbqp-log-maintenance`（每小时 :04） | 只跑 logrotate + journalctl vacuum + 日志上传 S3，06:04:00 用时不到 1 秒就结束 | 排除 |
| `dbqp-disk-cleanup`（每天 04:00） | 04:03 跑，日志里只删了**旧镜像**（api/pp/tada 的 20260919-ben），没有删容器 | 排除 |
| `dbqp-game-log-archive`（每小时 :09） | 游戏日志轮转 + 旧日志上 S3 | 排除 |
| 容器/进程崩溃（OOM 等） | `dmesg` 无 OOM 记录；崩溃不会导致容器消失，只会留下 Restarting | 排除 |
| 镜像被清理导致容器停止 | Docker 不会因镜像被删而停掉正在运行的容器；且清理发生在 04:03，与 06:26 无关 | 排除 |
| 其他人/其他机器登录 | 该时段无任何其他成功登录（见第三节） | 排除 |

## 六、时间线还原（UTC）

```text
09-23 08:4x   发版开始：sh stop.sh tada / pp / api（02），随后从打包机 03 rsync 资源
09-23 08:48   监控报警（02 缺 tada/api/pp）—— 正常，属于发版窗口
09-23 09:39   sh start.sh pp/tada/api 20260923-ben，容器起回（tada 此后跑了 21h30m）
09-24 06:26:27 有人在「9/18 起的常驻 pts/0 会话」里执行 sh stop.sh tada
               → docker stop（10 秒后强杀）→ docker rm，容器彻底消失
09-24 06:28/06:30/06:32 监控连续 3 次采样确认缺失 → 06:32 报警（这条报警是对的）
09-24 06:26:38~06:43:23 nginx 持续 Connection refused 到 203.0.113.1:9096（每 12 秒一条），由 01 兜住
09-24 06:42:16 该常驻会话仍在活动
09-24 06:42:05 从 34.146.121.225 新建会话登录 02（人工介入）
09-24 06:45   sh start.sh tada 20260923-ben → 容器 20cdf2c5dabd 起来，9096 恢复
```

```text
故障时长：06:26:27 ~ 06:45:04 UTC，约 18.5 分钟（北京 14:26:27 ~ 14:45:04）。
恢复验证（2026-09-24 09:00 UTC 复查）：
  · 02 上 docker ps：game-service-tada-prod  Up，0.0.0.0:9096->9096/tcp；
  · nginx error log：最后一条 9096 refused 停在 06:43:23，之后不再出现；
  · 容器监控：14:44 那条采样发出「容器恢复：game-service-tada-prod（203.0.113.1 / 02）」，
    14:46 / 14:48 恢复为「OK … 期望容器 20 个」（不再有「缺失中」）。
```

## 七、结论与建议

```text
直接原因：手动 sh stop.sh tada（stop + rm）后没有 start 回来，与 9/23 那次发版是同一套动作，
          区别只在于这次只停了 tada 一个、而且后续的「start.sh」这步漏了。
责任判定：不是监控误报，也不是自动化误伤；监控这次是「准确报出真实缺口」。
```

建议（未执行，待确认）：

```text
1) 发版流程收口：停止/启动/同步三步要么写进同一个脚本一次跑完，
   要么在发版结束前用「期望容器清单」自检一遍（例如 sh start.sh all <tag> 或专用校验脚本）。
   现在「容器监控」已经能在发版进程结束后 6 分钟内报出漏启，可作为兜底。
2) 常驻会话治理：01/02 各有一个从 9/18 挂到现在的 root 常驻会话（对端 60.100.65.172）。
   常驻会话的好处是省事，坏处是命令不落 .bash_history、出了问题很难追溯。
   建议发版改用脚本执行并保留日志，或至少用完退出重连。
3) SSH 加固（顺带发现的独立风险）：02 的公网 IP 正在被扫描爆破，
   06:00~06:10 就有 152.67.9.154 / 2.57.122.53 / 177.10.183.34 / 158.173.89.50 等来源
   大量 Failed password（root、admin、minecraft、ec2-user…）。
   建议把 22 端口收敛到只允许 宝塔 203.0.113.1 与内网 203.0.113.1/24，或加 fail2ban。
```

## 八、相关文件

```text
/data/server-runtime/stop.sh   # 02 上：docker stop + docker rm（本次动作来源）
/data/server-runtime/start.sh  # 02 上：先清理同名容器再 docker run --restart=always
docker/scripts/container_health_monitor.py   # 本次报警就是它发的（03 已退出监控、发版窗口自动静默）
docker/doc/2026-09-24-1445-【优化+问题排查】容器监控只留0102并发版窗口自动静默含02的TADA缺失记录.md
```
