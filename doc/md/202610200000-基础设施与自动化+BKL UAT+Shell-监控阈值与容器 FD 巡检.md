---
id: "doc-e86239e869d7"
title: "监控阈值与容器 FD 巡检"
date: "2026-10-20T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Shell", "Python", "Docker", "Nginx", "MySQL", "Redis", "监控告警"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8820%E6%97%A5-%E7%9B%91%E6%8E%A7%E9%98%88%E5%80%BC%E4%B8%8E%E5%AE%B9%E5%99%A8FD%E5%B7%A1%E6%A3%80/2026%E5%B9%B410%E6%9C%8820%E6%97%A5-%E7%9B%91%E6%8E%A7%E9%98%88%E5%80%BC%E4%B8%8E%E5%AE%B9%E5%99%A8FD%E5%B7%A1%E6%A3%80.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月20日-监控阈值与容器FD巡检/2026年10月20日-监控阈值与容器FD巡检.md"
sourceSha256: "ecd7a2a5e65e6342f1d7a95885b120f0ba33fafb4b2a4912275b6251128aa4e7"
sourceSystem: "project-doc"
---

# 监控阈值与容器 FD 巡检

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610200000-%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E4%B8%8E%E8%87%AA%E5%8A%A8%E5%8C%96%2BBKL%20UAT%2BShell-%E7%9B%91%E6%8E%A7%E9%98%88%E5%80%BC%E4%B8%8E%E5%AE%B9%E5%99%A8%20FD%20%E5%B7%A1%E6%A3%80.md)

> 整理日期：2026-10-20 00:00｜日期依据：文件名日期

日期：2026-10-20
执行人：Ben（运维）
版本：v1

## 需求

1. 监控新加两台 SRS 后，结合监控数据重设全部服务器报警阈值。
2. 参考 `pgserver` 项目的 nofile 优化，检查 UAT 全部容器的文件描述符限制和 FD 使用。
3. 检查代码是否有文件句柄不释放问题。
4. 能解决的直接处理，代码问题给开发明确的修改建议。

## 一、Beszel 资产与基线

Beszel 现有 7 台系统，最近约 5 小时数据：

| 系统 | 规格 | CPU p95 | 内存 p95 | 磁盘 p95 | Load5 峰值 |
| --- | --- | --- | --- | --- | --- |
| UAT-堡垒机 | 4C/8G | 6.4% | 69.5% | 26.4% | 1.06 |
| UAT-middleware | 8C/48G | 17.3% | 38.5% | 68.7% | 8.89 |
| UAT-manager | 8C/32G | 52.5% | 10.1% | 15.3% | 7.15 |
| UAT-worker01 | 8C/32G | 34.9% | 10.9% | 15.4% | 5.62 |
| UAT-worker02 | 8C/32G | 20.2% | 12.9% | 15.0% | 5.58 |
| TEST-SRS 韩国 | 4C/16G | 3.7% | 70.6% | 19.1% | 1.96 |
| TEST-SRS 新加坡 | 8C/16G | 3.0% | 6.9% | 12.1% | 0.38 |

## 二、最终报警阈值

| 系统 | CPU | 内存 | 磁盘 | Load5 | 状态 |
| --- | --- | --- | --- | --- | --- |
| UAT-堡垒机 | 80 | 85 | 80 | 8 | 2 分钟 |
| TEST-SRS 韩国 | 80 | 85 | 80 | 8 | 2 分钟 |
| UAT-middleware | 85 | 80 | 80 | 16 | 2 分钟 |
| UAT-manager | 90 | 80 | 80 | 20 | 2 分钟 |
| UAT-worker01 | 90 | 80 | 80 | 20 | 2 分钟 |
| UAT-worker02 | 90 | 80 | 80 | 20 | 2 分钟 |
| TEST-SRS 新加坡 | 85 | 80 | 80 | 16 | 2 分钟 |

说明：

- 8C 业务节点的 CPU/Load 持续 15 分钟才告警；其他系统 10 分钟；状态 2 分钟。
- 堡垒机和 SRS 韩国内存基线已经约 70%，所以内存阈值单独放宽到 85%。
- 8C 节点 Load5 按 2×核数设 16；4C 节点设 8。
- middleware 磁盘 p95 已 68.7%，仍保留 80% 早告警。
- 原来 6 台缺少 LoadAvg5，本次已补齐；7 台共 35 条告警已核验。

## 三、容器 FD 巡检

范围：5 台 UAT，71 个容器记录（运行中 51 个）。

### 3.1 低 nofile 容器

只有堡垒机 4 个容器是 soft 1024：

| 容器 | 原 soft | 原 hard | 进程数 | FD 峰值 |
| --- | --- | --- | --- | --- |
| gitlab | 1024 | 30000 | 65 | 477 |
| jms_all | 1024 | 10032 | 39 | 160 |
| ben-bot | 1024 | 524288 | 1 | 4 |
| nginx | 1024 | 524288 | 5 | 20 |

处理：

```bash
prlimit --pid <pid> --nofile=65535:524288
```

共对 110 个进程执行，0 失败；处理后在 `gitlab`、`jms_all`、`ben-bot`、`nginx` 全部进程上核对为 soft 65535 / hard 524288。

### 3.2 其他容器

- middleware、manager、worker01、worker02 的运行容器基本都是 524288。
- Jenkins 394、MySQL 390、MySQL slave 342、redis-dev 322、RocketMQ broker 313、Nacos 224、middle-station 147~211，均远低于 524288。
- Elasticsearch 669 FD 属于 segment/索引文件，限值 524288。
- jms 有 4 个 deleted FD，mysql/mysql-slave 各 5 个，elasticsearch 4 个；属于少量临时/轮转文件，当前没有持续增长证据。

### 3.3 MySQL 专项

两次巡检间隔不到 2 分钟，MySQL FD 从 205 涨到 390，mysql-slave 从 154 涨到 342。专项检查：

| 项 | MySQL | mysql-slave |
| --- | --- | --- |
| FD 指向 | chili_game 151、chili_pay 78、middle_station 71 | 同左 |
| table_open_cache | 4000 | 4000 |
| Open_tables | 1080 | 715 |
| Connections | 2382 | 80 |
| Threads_connected | 37 | 3 |
| socket FD | 40 | 7 |

结论：增长来自 MySQL 打开的表文件，不是 socket 泄漏；`table_open_cache=4000`，当前 Open_tables 1080/715 在正常范围，不需要调小缓存。后续看 FD 是否长期贴近 4000。

## 四、代码句柄检查

- `ben-bot`：`LiveOutputMessage.log_fp` 是长生命周期日志句柄，`close()` 在 `do_exec` 的 `finally` 中调用；当前 FD 4。
- `net-quality`：`open`/`socket` 全部使用 `with`，`subprocess.run` 自动回收；FD 稳定。
- `issue_cert_wendang.sh`：原 inline Python 使用 `open().read()/write()`，已改成 `Path.read_text/write_text`。
- `middle-station`：各容器 FD 147~224，两次采样无异常增长；没有源码不判断业务代码，但当前没有泄漏证据。

给开发的规则：

1. 文件、socket、数据库连接必须 `with` / `defer` / `try-with-resources` / 连接池。
2. 禁止每次请求打开文件不关闭；大文件优先缓存或流式处理。
3. 新服务上线前观察 FD 趋势，不只看单次绝对值。
4. MySQL/ES 的缓存型 FD 不要误判为泄漏，要结合 Open_tables / segment 增长判断。

## 五、永久配置

已在以下 compose 文件中加入：

```yaml
ulimits:
  nofile:
    soft: 65535
    hard: 524288
```

| 文件 | 服务 |
| --- | --- |
| `code/gitlab-项目运维代码仓库/docker-compose.yml` | gitlab |
| `code/ben-bot-运维机器人/docker/docker-compose.yml` | ben-bot |
| `code/ops-scripts-运维部署脚本/jumpserver/docker-compose.yml` | jms_all |
| `code/ops-scripts-运维部署脚本/nginx/docker-compose.yml` | nginx |

服务器原 compose 已备份为 `*.bak-20261020`；4 个 compose `docker compose config` 校验通过。

注意：`docker restart` 不会更新已有容器的 ulimit；下次重建容器时新配置才生效。当前运行中进程已用 `prlimit` 提升。

## 六、运维脚本

新增：

- `code/ops-scripts-运维部署脚本/fd/audit_containers.sh`：只读巡检 FD 限制、FD 数、deleted FD
- `code/ops-scripts-运维部署脚本/fd/raise_nofile.sh`：对运行中容器执行 prlimit
- `code/ops-scripts-运维部署脚本/fd/README.md`：使用说明

## 七、验证

- Beszel 7 台、35 条告警已通过 API 核验。
- 4 个低 nofile 容器共 110 个进程 prlimit 成功，soft/hard=65535/524288。
- 4 个 compose `docker compose config` 通过。
- 两次 FD 快照 71 个容器记录均可读；MySQL 增长已解释为 table cache。
- `make check` 通过。

## 八、回滚

- 告警旧值：堡垒机 `/tmp/beszel-alerts-before.json`
- compose：恢复对应 `*.bak-20261020`
- 运行中 ulimit 无需回滚；下次重建容器时由 compose 决定

## 九、提交

- 主提交：`7f5cb37`
- 文档收尾提交：见 `git log -1`
- 远端：`root/devops` main

## 十、CPU 告警抖动调整（2026-10-20 晚）

调整后首轮告警出现刷屏。复核 Beszel 1 分钟数据：12:05~12:24 UTC，manager/worker01/worker02 CPU 真实在 80%~99%，同时每分钟都有新的 `chili-pay` 容器启动，单个容器占用 20%~30% CPU；12:24 后负载结束，CPU 回落到 3%~13%。

结论：不是监控误报，是真实批量负载；85%/10 分钟阈值贴着峰值，导致反复穿越。调整：

- manager/worker01/worker02：CPU 90%、持续 15 分钟；Load5 20、持续 15 分钟
- 堡垒机/SRS 韩国：保持 CPU 80%、Load5 8、10 分钟
- middleware/SRS 新加坡：保持 CPU 85%、Load5 16、10 分钟

调整后 API 核验通过，当前没有 triggered 告警。
