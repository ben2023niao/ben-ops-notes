---
id: "doc-40b8da799d80"
title: "Beszel 巡检与针对性维护"
date: "2026-10-25T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Shell", "Docker", "监控告警", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8825%E6%97%A5-Beszel%E5%B7%A1%E6%A3%80%E4%B8%8E%E7%BB%B4%E6%8A%A4/2026%E5%B9%B410%E6%9C%8825%E6%97%A5-Beszel%E5%B7%A1%E6%A3%80%E4%B8%8E%E7%BB%B4%E6%8A%A4.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月25日-Beszel巡检与维护/2026年10月25日-Beszel巡检与维护.md"
sourceSha256: "8bb40d0d2760f91ac87cfb4b8ae93e409300cc5fc41afc6b13ab9ae6a85d05f3"
sourceSystem: "project-doc"
---

# Beszel 巡检与针对性维护

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610250000-%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E4%B8%8E%E8%87%AA%E5%8A%A8%E5%8C%96%2BBKL%20UAT%2BShell-Beszel%20%E5%B7%A1%E6%A3%80%E4%B8%8E%E9%92%88%E5%AF%B9%E6%80%A7%E7%BB%B4%E6%8A%A4.md)

> 整理日期：2026-10-25 00:00｜日期依据：文件名日期

日期：2026-10-25
执行人：Ben（运维）
版本：v1

## 巡检范围

登录 Beszel，逐台读取 7 台服务器：UAT 5 台 + SRS 韩国/新加坡。

## 当前状态（维护后）

| 系统 | CPU | 内存 | 磁盘 | 状态 |
| --- | --- | --- | --- | --- |
| 堡垒机 | 8.0% | 65.5% | 23.8% | up |
| middleware | 25.0% | 43.0% | 76.1% | up |
| manager | 8.4% | 45.2% | 41.2% | up |
| worker01 | 12.1% | 44.2% | 44.0% | up |
| worker02 | 15.3% | 34.6% | 52.3% | up |
| SRS 韩国 | 3.1% | 69.3% | 18.6% | up |
| SRS 新加坡 | 1.4% | 6.7% | 12.3% | up |

## 内存分析

- middleware：48G 总内存，used 20.8G，available 27.3G，swap 1.3G。
- manager/worker：32G，used 12~13G，available 18~20G，swap 约 1~2M。
- 堡垒机内存约 65%，SRS 韩国约 69%，SRS 新加坡约 7%。
- 没有 OOM、没有内存持续上涨；middleware swap 1.3G 属轻微，不因此重启。

## 异常分析

- Swarm 应用全部 2/2：chili-game、chili-pay、middle-station 没有副本缺失。
- 没有新的 restart loop / unhealthy 任务。
- manager/worker01 CPU 短时高，top 中是多个 Java 业务进程 70%~80%，属于当前业务负载，不是重启风暴。
- middleware Disk 80 告警仍在 triggered，但当前磁盘已从 85.5% 降到 76% 左右，等 10 分钟恢复窗口后应 resolved。

## 维护操作

### middleware

- Docker unused images：先 prune 7 天前镜像回收 1.44G，仍 87%；再执行 `docker image prune -a -f`，回收 **9.809G**。
- 当前磁盘约 76%，active images 不动；旧回滚镜像可从 Harbor 重拉。
- 没有删除 Jenkins 备份、Harbor 数据、业务容器。

### worker01/02

- 修复 xxl-job 保留逻辑：之前 `cutoff` 使用 `<`，2 天实际保留了 3 个自然日。
- 改为 `<= cutoff`，只保留今天和昨天；清理 2026-10-23 日志。
- worker01/02 磁盘：53%/62% → 约 44%/52%。
- 每日 03:15 的 cleanup cron 仍保留 2 天。

## 验证

- 7 台 Beszel 全部 `status=up`。
- Swarm 所有应用 `2/2`。
- 内存无压力，swap 无异常增长。
- 业务容器未重启。
- `make check` 通过。

## 后续

- middleware 剩余空间主要是 Jenkins 主 workspace 11G、Harbor 8.5G、备份 7.8G；不硬删。
- xxl-job 仍约 14~15G/天，开发需检查任务频率、失败重试、`logretentiondays`。
- 观察 middleware Disk 告警恢复和 worker 日志 cron。

## 提交

- 主提交：`5961778`
- 文档收尾提交：见 `git log -1`
- 远端：`root/devops` main
