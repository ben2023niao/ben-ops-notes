---
id: "doc-6b77d53ebcce"
title: "全部容器 nofile 软限制优化记录"
date: "2026-10-20T18:29:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "监控告警", "自动化", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-10-20-1829-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91%E5%85%A8%E9%83%A8%E5%AE%B9%E5%99%A8nofile%E8%BD%AF%E9%99%90%E5%88%B6%E4%BC%98%E5%8C%96%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-10-20-1829-【运维】全部容器nofile软限制优化记录.md"
sourceSha256: "fda93a20418b6d165f804aaf826e8ca456d845247640c8c32d9c145422d57242"
sourceSystem: "project-doc"
---

# 全部容器 nofile 软限制优化记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610201829-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BDocker-%E5%85%A8%E9%83%A8%E5%AE%B9%E5%99%A8%20nofile%20%E8%BD%AF%E9%99%90%E5%88%B6%E4%BC%98%E5%8C%96%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-10-20 18:29｜日期依据：文件名日期

时间：2026-10-20 18:29（北京）｜2026-10-20 07:29（巴西圣保罗）
起因：vendor_a 容器 soft `nofile` 只有 1024，worker 常驻 1023 个 fd，
      持续报 `[Errno 24] Too many open files`，玩家偶发卡加载。

## 一、永久修复：发布脚本统一加 --ulimit

`/data/server-runtime/start.sh` 里所有厂家共用一段 `docker_args`，
在 `--restart=always` 后面补上：

```text
--ulimit nofile=65535:524288
```

这样以后由发布脚本新建/重建的任何容器都自动带这个限制，不需要人工记得。

覆盖的机器与文件：

| 机器 | 文件 |
| --- | --- |
| 巴西 01 `192.0.2.1` | `/data/server-runtime/start.sh` |
| 巴西 02 `192.0.2.1` | `/data/server-runtime/start.sh` |
| 巴西 03 `192.0.2.1` | `/data/server-runtime/start.sh` |
| 香港 01 `192.0.2.1` | `/data/server-runtime/start.sh`、`/data/start.sh` |
| 香港 02 `192.0.2.1` | `/data/server-runtime/start.sh`、`/data/start.sh` |

每份改前都备份为 `start.sh.bak-<时间戳>`，并用 `bash -n` 做了语法检查。
补丁脚本：`docker/scripts/patch_start_sh_nofile.py`（幂等，已含 `--ulimit` 会跳过）。

## 二、运行中容器：prlimit 直接提升，不重启

Docker 的 ulimit 只能在创建容器时指定，`docker update` 改不了。
为了不重启业务，本次直接对容器内所有进程执行：

```bash
for p in /proc/[0-9]*; do
  pid=${p#/proc/}
  grep -q "docker-" /proc/$pid/cgroup 2>/dev/null || continue
  prlimit --pid $pid --nofile=65535:524288
done
```

结果（每个都是容器内全部进程，含 worker 子进程）：

| 机器 | 已提升进程数 | 漏改 |
| --- | --- | --- |
| 巴西 01 | 66 | 0 |
| 巴西 02 | 66 | 0 |
| 巴西 03 | 73 | 0 |
| 香港 01 | 65 | 0 |
| 香港 02 | 65 | 0 |
| 香港禅道 `192.0.2.12` | 20 | 0 |
| 合计 | 355 | 0 |

香港入口 `192.0.2.14` 只有 beszel-agent 一个容器，原本就是 `524287/524288`，
不需要调整；香港两台游戏后端（`192.0.2.16` / `192.0.2.17`）在上一轮已经
和巴西一起改完（各 65 个进程），发布脚本两个入口都已带 `--ulimit`。

## 三、验证

逐台扫描 `/proc/<pid>/limits`，只统计属于 Docker 容器的进程：

```bash
for p in /proc/[0-9]*; do
  pid=${p#/proc/}
  grep -q "docker-" /proc/$pid/cgroup 2>/dev/null || continue
  awk '/Max open files/{print pid, $4}' pid=$pid /proc/$pid/limits
done | awk '{print $2}' | sort | uniq -c
```

五台结果都是 `65535 524288`，没有低于 65535 的容器进程。

vendor_a 专项：

- prod-01 worker 当前 1023 个 fd，上限已从 1024 提升到 65535；
- prod-02 worker 当前 1021 个 fd，同样 65535。
- 2026-10-20 10:26:41 UTC 之后再没有新的 `Too many open files`。

## 四、仍需开发根治

提升上限只是止血：vendor_a 的 fd 仍在 1000+ 高位，说明句柄还在泄漏。
报错集中在 `/app/vendor_a/data/<game>/GameInfoAck.json`，请开发确认是否
每次请求打开后没有 `close()`（建议用 with / try-finally 或缓存文件句柄）。

## 五、回滚

```bash
# 恢复发布脚本
cp /data/server-runtime/start.sh.bak-<时间戳> /data/server-runtime/start.sh

# 运行中的进程无法自动回退 ulimit，也没有回退的必要；
# 下次重建容器时如果不想要新限制，用备份脚本启动即可。
```
