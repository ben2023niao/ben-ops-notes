---
id: "doc-22863a845284"
title: "Beszel 告警汉化上线与日志保留期调整"
date: "2026-10-20T09:10:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "Go", "Docker", "Nginx", "监控告警"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-10-20-0910-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91Beszel%E5%91%8A%E8%AD%A6%E6%B1%89%E5%8C%96%E4%B8%8A%E7%BA%BF%E4%B8%8E%E6%97%A5%E5%BF%97%E4%BF%9D%E7%95%99%E6%9C%9F%E8%B0%83%E6%95%B4.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-10-20-0910-【运维】Beszel告警汉化上线与日志保留期调整.md"
sourceSha256: "70cb49f5e63b5527b05eefa65fba54f1ecf867a3619bf8642c4aa36a5a417079"
sourceSystem: "project-doc"
---

# Beszel 告警汉化上线与日志保留期调整

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-10-20-0910-【运维】Beszel告警汉化上线与日志保留期调整.md`

> 整理日期：2026-10-20 09:10｜日期依据：文件名日期

时间：2026-10-20 09:10（北京）｜2026-10-19 22:10（巴西圣保罗）
范围：东京监控机 `34.146.121.225`；巴西 01/02、香港 01/02 后端

## 一、Beszel 告警汉化（已上线）

### 1.1 线上版本与接入方式

- Hub：`http://34.146.121.225:8090/`，容器名 `beszel`，数据卷 `beszel_data`。
- 线上版本：**v0.18.7**（`henrygd/beszel`，2026-10-20 之前是英文原版）。
- 访问方式：东京 22 端口没有系统 sshd，2222 是 **GitLab 容器**的 SSH（只认 GitLab 账号的 key），
  所以常规 SSH 进不去；本次走 GCP 串口控制台用 root 密码登录。
  `gcloud compute connect-to-serial-port dbqp-tokyo-gitlab-cicd-01 --zone=asia-northeast1-a --port=1`

### 1.2 改了哪些文案

只改 `internal/alerts/*.go` 的展示文案，不动采集、阈值判断和存储：

| 场景 | 原文 | 现文 |
| --- | --- | --- |
| 阈值告警标题 | `xxx disk usage above threshold` | `xxx 磁盘使用率 超过阈值` |
| 阈值恢复标题 | `xxx cpu below threshold` | `xxx CPU 低于阈值` |
| 告警正文 | `Disk usage averaged 70.01% for the previous 1 minute.` | `磁盘 root 使用率 最近 5 分钟平均 70.01%。` |
| 磁盘明细 | `Usage of root` | `磁盘 root 使用率` |
| 在线状态 | `Connection to xxx is down` | `xxx 连接状态 断开` |
| SMART | `SMART failure on xxx: sda` | `xxx 的磁盘 sda SMART 状态：failure` |
| 测试告警 | `Test Alert` / `This is a notification from Beszel.` | `测试告警` / `这是来自监控系统（Beszel）的测试通知。` |
| 链接文字 | `View xxx` | `查看 xxx` |

所有 Telegram 告警正文统一追加：

```text
@运维 @Ben_Bird @benb6879
```

### 1.3 顺手修掉的问题

- `APP_URL` 原来是 `http://localhost:8090`，告警里的链接点不开；已改为
  `http://34.146.121.225:8090`。
- 磁盘正文原来只写 `root 使用率`，已改为 `磁盘 root 使用率`。

### 1.4 构建与部署

```bash
# 源码
git clone --depth 1 --branch v0.18.7 https://github.com/henrygd/beszel.git /root/beszel-src
cd /root/beszel-src
python3 /path/to/patch_v0.18.7.py .
docker build -f Dockerfile.zh -t beszel-zh:0.18.7 .

# 部署（保留原数据卷）
docker stop beszel && docker rm beszel
docker run -d --name beszel --restart unless-stopped \
  -p 8090:8090 -v beszel_data:/beszel_data \
  -e APP_URL=http://34.146.121.225:8090 \
  beszel-zh:0.18.7
```

补丁脚本与 Dockerfile：`docker/scripts/beszel-zh/`（`patch_v0.18.7.py`、`Dockerfile.zh`）。

### 1.5 验证

- `curl http://localhost:8090/api/health` → `{"message":"API is healthy.","code":200}`
- 11 个系统全部 `up`。
- 二进制里已确认包含 `超过阈值`、`磁盘 %s 使用率`、`@Ben_Bird`。
- 受控测试：把香港 02 的磁盘阈值临时调到 40（实际 41.37%），群里收到
  「香港-后端-02 磁盘使用率 超过阈值 / root 使用率 最近 5 分钟平均 41.37%」，
  随后恢复 85，收到恢复通知。

### 1.6 回滚

旧容器保留为 `beszel-old-20261020`（已停止），镜像 `henrygd/beszel` 仍在本机：

```bash
docker rm -f beszel
docker rename beszel-old-20261020 beszel
docker start beszel
```

数据库备份：`/root/beszel-data.bak-20261020.db`
容器配置备份：`/root/beszel-container-backup-20261020.json`

## 二、监控阈值（已按历史数据调整）

直接在 Hub 的 SQLite（`/var/lib/docker/volumes/beszel_data/_data/data.db`）更新，重启后生效：

| 指标 | 原来 | 现在 | 说明 |
| --- | --- | --- | --- |
| CPU | 80%，1 分钟 | 85%，5 分钟 | 平时 2%~3%，发版有短时尖峰 |
| 内存 | 80%，1 分钟 | 88%，10 分钟 | 巴西 01/02 基线就有 57%~58% |
| 磁盘 | 70%，1 分钟 | 85%，5 分钟 | 香港两台基线 42%，70% 会长期常亮 |
| 负载（8 核） | 10，1 分钟 | 12，5 分钟 | 巴西/香港后端 |
| 负载（4 核） | 10，1 分钟 | 6，5 分钟 | 宝塔、备用入口、东京 |
| 负载（2 核） | 10，1 分钟 | 3，5 分钟 | 香港 nginx、禅道 |
| 温度 | 80%，10 分钟 | 不变 | — |
| 带宽 | 10/30，1 分钟 | 不变 | — |

## 三、日志保留期调整

需求：日志只保留一天。实际按 **48 小时** 保留，原因：

- 每天 15:00（北京）的错误日志打包任务要读「前一天」整天；
- 打包时刻最老的数据约 39 小时前，24 小时会把这部分删掉；
- 48 小时既能覆盖打包窗口，又能把存量清干净。

脚本：`docker/scripts/prune_game_logs.sh` → 各后端 `/usr/local/sbin/prune_game_logs.sh`
定时：`10 9 * * *`（每天 09:10 本地时间）
轮转：巴西两台 `maxage 7` 改为 `maxage 2`；香港两台没有 dbqp 轮转配置，靠每日清理兜底。

清理结果（2026-10-20）：

| 机器 | 清理前 | 清理后 | 释放 |
| --- | --- | --- | --- |
| 巴西 01 | 50% | 40% | 46.7G 日志 |
| 巴西 02 | 48% | 40% | 45.4G 日志 |
| 香港 01 | 69% | 42% | 112.0G 日志 + 38.5G 镜像 |
| 香港 02 | 71% | 42% | 120.3G 日志 + 35.6G 镜像 |

## 四、复核命令

```bash
# Hub 健康
curl -s http://34.146.121.225:8090/api/health

# 容器
docker ps --filter name=^beszel$ --format '{{.Names}} {{.Status}} {{.Image}}'

# 阈值
sqlite3 /var/lib/docker/volumes/beszel_data/_data/data.db \
  "select s.name,a.name,a.value,a.min from alerts a join systems s on s.id=a.system order by s.name;"

# 日志清理（试运行）
DRY_RUN=1 /usr/local/sbin/prune_game_logs.sh
```
