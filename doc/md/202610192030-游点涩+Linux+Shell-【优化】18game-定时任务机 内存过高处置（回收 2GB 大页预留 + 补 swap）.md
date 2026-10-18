---
id: "doc-845d57d9f350"
title: "【优化】18game-定时任务机 内存过高处置（回收 2GB 大页预留 + 补 swap）"
date: "2026-10-19T20:30:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Docker", "MySQL", "监控告警", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-2030-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E5%AE%9A%E6%97%B6%E4%BB%BB%E5%8A%A1%E6%9C%BA%E5%86%85%E5%AD%98%E8%BF%87%E9%AB%98%E5%A4%84%E7%BD%AE%EF%BC%882GB%E5%A4%A7%E9%A1%B5%E9%A2%84%E7%95%99%E5%9B%9E%E6%94%B6%2B%E5%8A%A0swap%EF%BC%89.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-2030-【优化】定时任务机内存过高处置（2GB大页预留回收+加swap）.md"
sourceSha256: "65d88a84caef873249ad8d376328b5d9a6b97bca0faed01164ae70d9b8440e2d"
sourceSystem: "project-doc"
---

# 【优化】18game-定时任务机 内存过高处置（回收 2GB 大页预留 + 补 swap）

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-2030-【优化】定时任务机内存过高处置（2GB大页预留回收+加swap）.md`

> 整理日期：2026-10-19 20:30｜日期依据：文件名日期

- 时间：2026-10-19 20:20 ~ 20:35（北京时间）
- 主机：18game-定时任务机-Spug调度-16.208.32.40（ip-172-31-20-69，2 vCPU / 3.6 GB）
- 现象：内存长期贴顶，告警频繁

## 一、处置前

```
Mem:  total 3785 MB   used 3276 MB   free 114 MB   buff/cache 393 MB   available 267 MB
Swap: 0
进程 RSS 合计仅 1321 MB（131 个进程）
容器：spug 556 MB、spug-db 298 MB（均未设内存上限）
历史上 OOM 记录：14 次（dmesg 中 "Out of memory: Killed"）
```

RSS 合计 1.3 GB，但 used 3.3 GB —— **有约 1.8 GB 内存去向不明**。

## 二、根因：2 GB 大页被预留且无人使用

```
$ sysctl vm.nr_hugepages
vm.nr_hugepages = 1067
$ grep Huge /proc/meminfo
HugePages_Total: 1067     # 1067 × 2MB ≈ 2.1 GB
HugePages_Free:  1067     # 全部闲置
```

- 无任何进程使用大页（`/proc/*/smaps` 中无 HugePages_ 记录）
- 内核启动参数里**没有** hugepages（`/proc/cmdline`），说明是运行时被设的
- 线索：`/root/incident-kworker-20261010-121027/kworker`（10-10 挖矿/内存马事件的取证样本）中包含 `nr_hugepages` 字符串，**疑似该事件遗留**；系统内未发现会重复设置大页的 cron/systemd

## 三、处置

```bash
# 1) 回收大页并持久化
sysctl -w vm.nr_hugepages=0
cat > /etc/sysctl.d/99-youdianse-disable-hugepages.conf <<'EOF'
vm.nr_hugepages = 0
EOF

# 2) 增加 2G swap（原机无 swap）
fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
echo "/swapfile none swap sw 0 0" >> /etc/fstab
```

## 四、结果

| 指标 | 处置前 | 处置后 |
| --- | ---: | ---: |
| used | 3,276 MB | **1,134 MB** |
| available | 267 MB | **2,409 MB** |
| swap | 0 | 2,047 MB |
| HugePages_Total | 1067 | 0 |

服务验证：`spug` / `spug-db` 容器均 Up，`http://203.0.113.1:80` 返回 200，调度/worker/monitor 进程正常。

## 五、是否需要扩容 / 迁移

**当前不需要。** 释放后可用内存 2.4 GB，Spug 全家桶实际占用约 0.9 GB，余量充足。

若后续作业量增长仍需迁移，候选：

| 主机 | 内存 | 当前可用 | 说明 |
| --- | ---: | ---: | --- |
| 监控机 52.79.252.255 | 7.7 GB | 5.6 GB | 同 VPC、已有 Docker，最适合承接 Spug |
| 后端 16.209.16.108 | 31 GB | 27 GB | 资源最充裕，但与业务同机，迁移需评估影响 |

迁移注意：Spug 有内置 MySQL（spug-db 容器）+ 主机密钥，迁移需停服、导出库、同步 `docker` 数据卷与 `/root/.ssh`，并在新机验证定时任务能正常 SSH 到目标机；建议在低峰窗口做。

## 六、遗留事项

- `/root/incident-kworker-20261010-121027/` 是 10-10 事件的取证样本（含木马二进制），建议确认取证完成后归档到离线存储，避免被误执行
- 该机未设容器内存上限；若后续再出现内存紧张，可给 `spug`/`spug-db` 设 `--memory` 限制（需重启容器）
