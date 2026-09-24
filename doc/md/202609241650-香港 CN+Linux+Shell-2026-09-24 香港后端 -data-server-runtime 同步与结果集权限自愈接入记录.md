---
id: "doc-9a3085842f22"
title: "2026-09-24 香港后端 /data/server-runtime 同步与结果集权限自愈接入记录"
date: "2026-09-24T16:50:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Linux", "Shell", "Docker", "监控告警", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-09-24-1650-%E3%80%90%E6%95%B0%E6%8D%AE%E7%BB%B4%E6%8A%A4%2B%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AF%E5%90%8E%E7%AB%AF%E7%BB%93%E6%9E%9C%E9%9B%86server-runtime%E5%90%8C%E6%AD%A5%E4%B8%8E%E6%9D%83%E9%99%90%E8%87%AA%E6%84%88%E6%8E%A5%E5%85%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-09-24-1650-【数据维护+架构改造】香港后端结果集server-runtime同步与权限自愈接入记录.md"
sourceSha256: "342bcd906f8cae75c49228b6c903222a8a7416b279c74f57b7996cf1d6efaff7"
sourceSystem: "project-doc"
---

# 2026-09-24 香港后端 /data/server-runtime 同步与结果集权限自愈接入记录

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-09-24-1650-【数据维护+架构改造】香港后端结果集server-runtime同步与权限自愈接入记录.md`

> 整理日期：2026-09-24 16:50｜日期依据：文件名日期

## 一、任务

```text
把巴西打包机 dbqp-saopaulo-sanic-prod-03 的 /data/server-runtime
同步到香港两台后端 /data/server-runtime：
  先 dbqp-hongkong-sanic-prod-01（跨公网直连巴西）
  再由 prod-01 走香港内网推送 dbqp-hongkong-sanic-prod-02
参考命令（用户提供）：
  rsync -avP --delete -e "ssh -o ServerAliveInterval=15 -o ServerAliveCountMax=3" \
    --exclude 'logs' --exclude '*.db-shm' --exclude '*.db-wal' \
    root@203.0.113.1:/data/server-runtime /data/
额外要求：
  1) 同步过程挂后台一次性任务（本地离开也能继续），每 10 分钟把网速/进度条发飞机群
  2) 同步完成后参考巴西 01/02，加上定时任务监控结果集权限
```

流程：前置核验 → 执行 → 验证 → 文档 → 本地提交；本轮不发送「每步」通知，只按用户要求发同步进度。

## 二、前置核验

```text
git：本地 cn 领先 origin/cn 77，工作区干净
数据源：巴西 prod-03 /data/server-runtime 实测 152.1 GiB（du -sb = 163,297,197,003）
  目录：version.json / stop.sh / server_configs / md5sum.txt / conf /
        game_result_datas / logs / share.so / xxxxxx.mmdb
连通：香港 prod-01 -> 34.39.180.82:22（prod-03 公网）可达，同一 root 密码可登录
  香港内网 prod-01(203.0.113.1) <-> prod-02(203.0.113.1) 已互通
磁盘：香港两台 / 485G，剩余 482G，容纳 152G 结果集无压力
权限目标（从巴西 prod-01 复刻）：game_result_datas 与 logs 需要 uid:gid = 1000:1000
  （容器内业务进程 appuser uid 1000 要写 SQLite 的 .db/-wal/-shm）
```

## 三、执行内容

### 3.1 同步任务（后台一次性 systemd 任务）

```text
脚本：/root/hk-runtime-sync.sh（prod-01）
任务：systemd-run --unit=hk-runtime-sync --collect --no-block /bin/bash /root/hk-runtime-sync.sh
  一次性 unit，跑完自动 collect；与 SSH 会话解耦，本地下线不影响
阶段：
  STAGE1  prod-03(34.39.180.82) -> prod-01   rsync -a --partial --info=progress2 --stats
          --exclude logs --exclude '*.db-shm' --exclude '*.db-wal' --delete
  STAGE2  prod-01 -> prod-02(203.0.113.1)     同样的参数（走香港内网），仅当 STAGE1 rc=0
日志：/root/hk-runtime-sync.log（上一轮日志归档为 .log.prev）
凭据：/root/.rsync-pass（600，root；sshpass 使用，明文不入库）
```

说明：相比用户给的 `-avP`，改用 `-a --partial --info=progress2`，多出「总体进度 + 网速 +
剩余时间」一行，作为进度上报的数据源；`--delete` 与排除项保持与参考命令一致。

### 3.2 每 10 分钟进度上报（飞机群）

```text
脚本：/opt/dbqp-scripts/notify_runtime_sync.py（仓库 docker/deploy/hongkong/notify_runtime_sync.py）
定时：systemd 单元 hk-runtime-sync-notify.timer（OnBootSec=3min / OnUnitActiveSec=10min）
凭据：/opt/benbot-runtime.env（从巴西 prod-01 复制，600；含 TG_BOT_TOKEN /
     BEN_BOT_MONITOR_CHAT_ID，明文不入库）
目标群：监控报警群（-5203304347），与巴西告警同群
```

消息样例（实测，message_id=7422）：

```text
【香港后端结果集同步｜进度】
阶段：① 巴西 prod-03 → 香港 prod-01（跨公网）
进度：758.3MB / 152.1GB　0.5%
　　　░░░░░░░░░░░░░░░░░░░░
瞬时速度：6.61 MB/s
预计剩余：6:25:30
日志：/root/hk-runtime-sync.log
时间：2026-09-24 08:50:16 UTC
```

同步结束后脚本会自动发最后一条并 disable 通知 timer（避免继续刷群）。

### 3.3 结果集权限自愈（参考巴西 01/02）

从巴西 prod-01 复刻到香港 prod-01 与 prod-02：

```text
脚本：/opt/dbqp-scripts/fix_result_perms.sh（11,758 字节，与巴西一致）
单元：/etc/systemd/system/dbqp-result-perms.{service,timer}
  每 2 分钟检查一次（OnBootSec=2min / OnUnitActiveSec=2min）
目标：/data/server-runtime/game_result_datas、/data/server-runtime/logs
  异常时 chown -R 1000:1000 + chmod -R u+rwX，并发飞机群告警（10 分钟限流）
日志：/var/log/dbqp-result-perms.log
```

为什么必须做：巴西 2026-09-24 线上事故就是 `rsync -a`（隐含 -o -g -p）把源端
`root:root` 覆盖到 01/02，容器内 appuser(uid1000) 无法写 SQLite，表现为
「所有厂家都下不了注 / attempt to write a readonly database」。本脚本既是修复也是自愈。

实测：香港 prod-01 首次运行即修复 `game_result_datas` 16/16 个条目（root:root → 1000:1000）：

```text
[2026-09-24 08:47:23+0000] 已修复权限 /data/server-runtime/game_result_datas :
  修复前异常 16/16 个条目，修复后剩余 0（属主 1000:1000）
```

### 3.4 通知文案与进度口径修正（2026-09-24 16:58 追加）

用户反馈两点：结果集告警要**标识香港项目**；并且群消息尾部多出一段「只有标签、没有内容」
的重复模板。本轮一起修掉：

```text
1) 标题加项目标识（只改香港两台，巴西保持原样）
   香港：`【DBQP 香港项目｜结果集权限告警】@运维 @Ben_Bird @benb6879`
2) 修 printf 参数个数 bug（这就是「空模板段」的根因）
   alert_text 在「修复后剩余 = 0」时不追加告警行，但 printf 仍多传了一个参数；
   bash 内置 printf 在参数多于占位符时会复用格式串再渲染一遍，于是群里多出一段空模板。
   改为按占位符数量分支传参（left≠0 / left=0 两种写法）。已发模拟演练验证（message_id 7424）。
3) 同步命令加 --chown=1000:1000（从源头消掉刷屏）
   自愈日志显示 rsync -a 每落盘新文件都会带 root:root，自愈每 2 分钟修一次并告警；
   已在 /root/hk-runtime-sync.sh 的 RSYNC_OPTS 加 --chown=1000:1000，自愈任务保留作兜底。
   重启后实测 /data/server-runtime/game_result_datas 属主直接就是 ubuntu:ubuntu。
4) 进度口径改为「本地已落盘大小」（du -sb）
   rsync 重启后会话计数从 0 开始，会让百分比回退、均速虚高（曾出现 446 MB/s、ETA 26 秒）；
   改为本地落盘字节为分子，均速与 ETA 自算。实测消息（message_id 7427/7428）：
     进度：6.2GB / 152.1GB　4.1%　██░░░░…
     瞬时速度：6.53 MB/s　近 1 分钟均速：6.52 MB/s
     预计剩余：约 6 小时 21 分（按均速估算）
```

### 3.5 公网同步完成后的收尾校验（2026-09-24 22:00 追加）

用户要求：公网同步（prod-03 → prod-01）完成后再同步一次做校验，然后由 prod-01 走内网同步 prod-02。

```text
脚本：/root/hk-runtime-sync-finalize.sh（prod-01）
任务：systemd-run --unit=hk-runtime-sync-finalize（一次性，已挂起）
日志：/root/hk-runtime-sync-finalize.log
流程：
  1) 轮询等待主任务 hk-runtime-sync 结束（每 60s）
  2) STEP1  prod-03 → prod-01 二次 rsync（校验补漏，参数与主任务一致，含 --delete/--chown/排除项）
  3) STEP2  prod-01 → prod-02 内网 rsync（203.0.113.1）
  4) CHECK1/CHECK2 用 `rsync -n -i --delete` 统计差异条目数
     （prod-03↔prod-01 / prod-01↔prod-02，0 表示完全一致）
  5) 完成后往监控报警群发一条「同步完成校验」：
     二次同步返回码、两条差异条目数、两台体积、日志路径
```

### 3.6 执行结果（2026-09-24 23:35 完成）

```text
主任务 hk-runtime-sync：
  STAGE1 done rc=0 size=147G    （15:19:19Z，巴西 prod-03 -> prod-01 跨公网）
  STAGE2 done rc=0              （15:30:56Z，prod-01 -> prod-02 香港内网 203.0.113.1）
  SYNC END rc1=0 rc2=0
收尾任务 hk-runtime-sync-finalize：
  STEP1（prod-03 -> prod-01 二次同步）rc=0
  STEP2（prod-01 -> prod-02 内网同步）rc=0
  CHECK1 prod-03 vs prod-01 差异条目 = 0
  CHECK2 prod-01 vs prod-02 差异条目 = 0
  FINALIZE END size_prod01=147G size_prod02=147G
进度通知 timer：同步结束后自动停用（hk-runtime-sync-notify.timer = inactive）
```

完成后逐项验证（实测）：

| 验证项 | prod-01 | prod-02 | 源 prod-03 |
| --- | --- | --- | --- |
| `/data/server-runtime` 体积 | 147G | 147G | 153G |
| game_result_datas 条目数 | 742 | 742 | 882 |
| game_result_datas 属主 | ubuntu:ubuntu | ubuntu:ubuntu（0777） | ubuntu:ubuntu |
| `game_result_datas/pg/pg_1.db` md5 | `5db34996b11455dc4106668e3db7f953` | 同上 | 同上 |
| version.json | bx.2026.09.09（一致） | 一致 | 一致 |
| 结果集权限自愈 timer | active + 心跳「权限全部正常」 | active + 心跳「权限全部正常」 | — |

体积/条目比源端少的原因：按用户参考命令排除了 `logs`、`*.db-shm`、`*.db-wal`
（SQLite 每个库常带 shm/wal 附属文件）。`rsync -n -i --delete` 的差异条目为 0，
说明**传输范围内两棵树完全一致**。

## 四、验证与当前状态

| 项目 | 结果 |
| --- | --- |
| 主任务 | `hk-runtime-sync` 已完成（STAGE1 rc=0 / STAGE2 rc=0 / SYNC END rc1=0 rc2=0） |
| 收尾校验 | `hk-runtime-sync-finalize` 已完成（CHECK1=0、CHECK2=0，差异条目为 0） |
| 两台体积 | prod-01 = 147G，prod-02 = 147G（源 153G，差值来自被排除项） |
| 数据一致性 | `pg_1.db` md5 三台一致；version.json 一致 |
| 进度上报 | 同步期间每 10 分钟一条（含阶段/进度条/均速/ETA）；结束后 timer 自动停用 |
| 权限自愈 | 香港两台 timer active，心跳正常，无需修复 |
| 本地依赖 | 无（systemd 托管，SSH 断开不影响） |

查询方法（任何人/任何 AI 都可用）：

```bash
ssh root@34.92.83.132 'tail -c 500 /root/hk-runtime-sync.log | tr "\r" "\n" | tail -3'   # 最新进度行
ssh root@34.92.83.132 'systemctl is-active hk-runtime-sync'                              # 是否还在跑
ssh root@34.92.83.132 'grep -E "STAGE|SYNC END" /root/hk-runtime-sync.log | tail -5'      # 阶段状态
ssh root@34.92.83.132 'tail -3 /var/log/dbqp-result-perms.log'                           # 权限自愈
```

## 五、踩坑记录

```text
1) pkill/pgrep -f 自匹配：命令行里出现同样的模式串，会把执行命令的 shell 自己杀掉
   （表现为命令无输出、rsync 没启动）。改用 pgrep -x / 精确 PID。
2) heredoc 只喂一个 cat：一条命令里写两个 `cat > file <<EOF`，第二个文件会是空的
   （notify 脚本先是 0 字节）。改为每个文件单独一条命令传输。
3) 进度解析单位换算 bug：把 speed 的单位换算（MB/s -> B/s）误加到 bytes 上，
   导致进度显示 389.7TB。已修正为「bytes 原样、scale 只用于 speed」，
   并把百分比改成「已传 / 源总大小」计算（rsync 早期整数百分比一直是 0%）。
4) 香港机原先没有飞机群凭据：从巴西 prod-01 复制 /opt/benbot-runtime.env（600），
   权限告警与进度上报才能发到监控报警群。
```

## 六、待办

```text
1. 同步完成后（STAGE2 rc=0）核对：
   - 两台 du -sh /data/server-runtime 与巴西源接近；
   - game_result_datas / logs 属主保持 1000:1000（自愈日志无新增修复记录）；
   - 抽查 md5sum.txt 与关键 db 文件。
2. 若后续自建后端部署容器，注意同步命令可加 --chown=1000:1000 从源头规避权限问题。
3. 香港机 /root/.rsync-pass 与 /opt/benbot-runtime.env 均为 600 且不入库；
   如不再需要跨机同步，可删除 .rsync-pass。
```

## 七、关联文件

```text
docker/deploy/hongkong/notify_runtime_sync.py   同步进度上报脚本（仓库本源）
docker/doc/2026-09-24-1300-【架构改造】香港两台后端服务器创建与Docker环境部署记录.md
docker/doc/2026-09-24-1400-【架构改造】香港standby入口与新域名hkcloudplay0607接入记录.md
```
