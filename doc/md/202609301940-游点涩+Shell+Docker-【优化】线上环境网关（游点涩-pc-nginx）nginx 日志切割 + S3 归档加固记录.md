---
id: "doc-c00162d7ac1e"
title: "【优化】线上环境网关（游点涩-pc-nginx）nginx 日志切割 + S3 归档加固记录"
date: "2026-09-30T19:40:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "监控告警", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-30-1940-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E7%BD%91%E5%85%B3pc-nginx%E6%97%A5%E5%BF%97%E5%88%87%E5%89%B2%E4%B8%8ES3%E5%BD%92%E6%A1%A3%E5%8A%A0%E5%9B%BA%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-30-1940-【优化】线上环境网关pc-nginx日志切割与S3归档加固记录.md"
sourceSha256: "6606203610ada12c76f339999a4134e9d3be928088a15f3c5f328c45780faa49"
sourceSystem: "project-doc"
---

# 【优化】线上环境网关（游点涩-pc-nginx）nginx 日志切割 + S3 归档加固记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609301940-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BDocker-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E7%BD%91%E5%85%B3%EF%BC%88%E6%B8%B8%E7%82%B9%E6%B6%A9-pc-nginx%EF%BC%89nginx%20%E6%97%A5%E5%BF%97%E5%88%87%E5%89%B2%20%2B%20S3%20%E5%BD%92%E6%A1%A3%E5%8A%A0%E5%9B%BA%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-09-30 19:40｜日期依据：文件名日期

- 文档日期：2026-09-30 19:40（北京）/ 11:40（UTC）
- 目标机：`游点涩-pc-nginx` = **16.208.38.88**（18game H5/PC 统一网关，Beszel 面板名即 `游点涩-pc-nginx`）
- 分类：优化 + 稳定性加固（P2）
- 关联：`2026-09-26-0227`（日志打满根盘导致 SSL Monitor 连环告警）、`2026-09-26-1053`（S3 归档与 75% 看门狗改造）

## 一、背景与现象（起点状态，VERIFIED）

- 根盘 `/dev/root` 49G，已用 34G（70%）；`/var/log/nginx` 合计 4.7G
- `access.log` 4.1G（09-30 00:00 轮转后新建，到 11:23 已长到 4.1G）、`access.log.2.gz` 528M、`access.log.1.gz` 55M
- 网关 logrotate（`/etc/logrotate.d/nginx`）：`daily + maxsize 2G + rotate 3 + compress`
- 网关 root crontab 只有 `*/10` 磁盘看门狗与 `7 * * * *` 页缓存回收，**没有任何 logrotate 定时任务**
- S3 归档链路在 ben-bot 宿主机：`/usr/local/bin/youdianse-nginx-log-archive.sh`，
  桶 `youdianse-prod-gateway-logs`、前缀 `nginx/`、cron `5 */6 * * *`，取 `-mtime +0` 的 `.gz` 上传后删本地

## 二、根因

1. **maxsize 形同虚设**：logrotate 的 `maxsize` 只有在「logrotate 自己被运行时」才判断。
   本机没有 logrotate cron，只有系统 `logrotate.timer`（daily，00:00 UTC）→ 一天只判断一次
   → 单日 `access.log` 能涨到 8~9G（实测约 360MB/小时）。这与 09-26 打满 49G 根盘是同一机理。
2. **归档滞后**：归档脚本只取「24 小时前」的 `.gz`，而当前大文件没被及时切割，
   导致「当前日志」长期是几 GB 的裸文件，S3 里只有零散旧件。
3. **本地留存与轮转次数矛盾**（09-26 老问题）：`rotate 3` 时轮转件可能在归档脚本取走前
   就被 logrotate 自己删掉，等于「未归档即删除」。

## 三、处置

### 3.1 立即清理存量（2026-09-30 11:27~11:29 UTC）

1. 先把现存 `.gz` 全部归档（`ARCHIVE_MIN_AGE_MINUTES=0` 立即模式）：
   `access.log.1.gz`(55M)、`access.log.2.gz`(528M)、`error.log.1/2.gz` → S3 http=200 → 删本地
2. 网关强制轮转 4.1G 当前日志：`logrotate -f /etc/logrotate.d/nginx`
   → `access.log` 4263M 变成 `access.log.1.gz` 329M（压缩比约 13:1），`nginx -s reopen` 服务不中断
3. 新的 329M gz 再次归档到 S3 并删本地

结果：`/var/log/nginx` 4.7G → **15M**；根盘 34G(70%) → **29G(60%)**，可用 15G → 20G。

### 3.2 轮转加固：size 触发 + 高频检查（网关 16.208.38.88）

- `/etc/logrotate.d/nginx`（备份 `/root/logrotate-nginx-backup-20260930-*`）：
  `maxsize 2G → 1G`、`rotate 3 → 16`、保持 `compress`（轮转即压缩，不留下未压缩滞留）
- 新增 root crontab：`*/15 * * * * /usr/sbin/logrotate /etc/logrotate.d/nginx`
  → 单文件超 1G 最迟 15 分钟内被切割压缩，`access.log` 不再出现 GB 级裸文件
  → `rotate 16` 保证 24 小时内的轮转件（约 8~9 个）不会被 logrotate 提前删掉

### 3.3 归档加固：改为每小时（ben-bot 宿主机）

- `/usr/local/bin/youdianse-nginx-log-archive.sh`（备份 `/root/nginx-log-archive-backup-20260930-*`）：
  时间过滤 `-mtime +0`（24 小时）→ `-mmin +${ARCHIVE_MIN_AGE_MINUTES:-1440}`（默认仍是 24 小时，分钟级可调）；
  保留「http=200 才删本地」的安全逻辑；新增 `ARCHIVE_MIN_AGE_MINUTES=0` 立即归档模式
- cron：`5 */6 * * *` → `5 * * * *`（每小时一次），轮转件在本地滞留不超过约 1 小时
- 本地稳态占用估算：当前 1G 上限 + 24 小时 gz（约 1G）≈ 2G，远低于此前的 15G

## 四、验证

- 网关：`/var/log/nginx` **15M**（access.log 15M 新文件 + error.log 0M）；nginx `active`；H5(3003)/PC(3004) 容器 Up
- 业务自检（本机）：`healthz` 200、H5 容器 200、PC 容器 200；公网 `www.youdianse.com` 首页 200
- 根盘：29G / 49G（60%），可用 20G
- S3（桶 `youdianse-prod-gateway-logs`、前缀 `nginx/`）确认存在：
  - `access.log.1.gz` 344,262,127B 2026-09-30T11:29:41Z
  - `access.log.2.gz` 553,190,184B 2026-09-30T11:27:53Z
  - `error.log.1.gz` / `error.log.2.gz` 同步上传成功
- cron 原样命令手动执行：`sudo /usr/sbin/logrotate /etc/logrotate.d/nginx` → exit=0，
  干跑显示 `log has already been rotated`（不会重复轮转）

## 五、垃圾日志 / 垃圾文件清理（2026-09-30 11:35~11:50 UTC）

在同一台机器上按「垃圾日志 + 垃圾文件」继续清理，处置对象与结果：

| 对象 | 清理前 | 处置 | 释放 |
| --- | --- | --- | --- |
| Docker 构建缓存 | 13.39G（227 条，可回收 12.33G） | `docker builder prune -af` | **13.39G** |
| 僵尸容器（`youdianse_prod_pc_dev_*`，Exited 6 周） | 47M | `docker container prune -f` | 47M |
| `/var/log/syslog`（MSSQL 暴力破解刷屏） | 2.5G | rsyslog logrotate 轮转 + gzip 存档 | 2.5G → 45M |
| `/var/log/auth.log` 等轮转件 | 35~42M × 多份 | 随同一轮转压缩 | — |
| apt 缓存 | 144M | `apt-get clean` | 144M |
| journal | 4.1G（活跃日志，vacuum 未释放） | 复核，未强删 | 0 |
| `/root/.codex-backup` | 338M（155 个配置回滚点） | **保留**（属回滚材料，非垃圾） | 0 |

**syslog 长期不轮转的根因**：`/etc/logrotate.d/rsyslog` 缺少 `su` 指令，而 `/var/log` 是
`drwxrwxr-x root syslog`（组可写）→ logrotate 全部条目报
`skipping … because parent directory has insecure permissions` 而跳过，日志因此涨到 2.5G。
已补 `su root syslog` + `create 0640 syslog adm`（备份 `/root/rsyslog-logrotate-backup-*`），
轮转后实测 rsyslog 仍能正常写入（`logger -t codex-verify` 验证通过）。

清理后根盘：**11G / 49G（22%）**，可用 38G（起点为 34G / 70%）。

## 六、根盘剩余占用分布（供后续优化）

```
/            11G（清理后）
  /var       约 9G
    /var/lib  ← Docker 镜像（构建缓存已清空）
    /var/log  435M（journal 约 4G 仍在 /var/log/journal）
    /var/opt  1.7G ← mssql errorlog（暴力破解期间刷出来的，待单独处置）
  /usr        1.9G
  /opt        1.3G
```

后续可选：`journalctl --vacuum-size=500M`（active journal，需设 `SystemMaxUse` 才长期生效）、
Docker 镜像清理、mssql errorlog 轮转（见安全事件文档）。

## 七、回滚

- 网关 logrotate：恢复 `/root/logrotate-nginx-backup-20260930-*.conf` → `logrotate -d` 校验
- rsyslog logrotate：恢复 `/root/rsyslog-logrotate-backup-20260930-*.conf`
- 网关 cron：删除 crontab 中 `*/15 * * * * /usr/sbin/logrotate /etc/logrotate.d/nginx` 一行
- 归档脚本：恢复 `/root/nginx-log-archive-backup-20260930-*.sh`，cron 还原为 `5 */6 * * *`

## 八、仓库同步

- `18game_devops/devops/scripts/youdianse-nginx-log-archive.sh`（分钟级阈值 + 立即归档模式）
- `18game_devops/devops/scripts/youdianse-gateway-logrotate.conf`（maxsize 1G / rotate 16 + 演进说明）
- `18game_devops/workbench/ACTIVE_TASKS.md`（TASK-20260930-PCNGINX-LOG-S3）

## 九、安全与敏感内容

本记录不输出 Telegram token/chat_id、AWS 凭证、私钥正文；S3 桶名、路径、阈值、统计口径属基础设施信息。
