---
id: "doc-748a84db686e"
title: "2026-10-16 中间件容器启动失败排查（Fatal glibc error： CPU does not support x86-64-v2）"
date: "2026-10-16T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Shell", "Go", "Docker", "MySQL", "Redis", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8816%E6%97%A5-%E4%B8%AD%E9%97%B4%E4%BB%B6%E5%AE%B9%E5%99%A8glibc%E6%8A%A5%E9%94%99%E6%8E%92%E6%9F%A5/2026%E5%B9%B410%E6%9C%8816%E6%97%A5-%E4%B8%AD%E9%97%B4%E4%BB%B6%E5%AE%B9%E5%99%A8glibc%E6%8A%A5%E9%94%99%E6%8E%92%E6%9F%A5.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月16日-中间件容器glibc报错排查/2026年10月16日-中间件容器glibc报错排查.md"
sourceSha256: "774cf468aca09e061475c5a54597f9f382cda682f400266ac359365929792eb7"
sourceSystem: "project-doc"
---

# 2026-10-16 中间件容器启动失败排查（Fatal glibc error： CPU does not support x86-64-v2）

> 来源文件：`~/Projects/work/ops/devops/devops-bkl/doc/2026年10月16日-中间件容器glibc报错排查/2026年10月16日-中间件容器glibc报错排查.md`

> 整理日期：2026-10-16 00:00｜日期依据：文件名日期

| 项 | 内容 |
| --- | --- |
| 日期 | 2026 年 10 月 16 日 |
| 报障 | Bruce：UAT 中间件服务器（43.249.251.11）minio 和 rocketmq-dashboard 反复重启 |
| 结论 | **UAT 虚拟机的 CPU 型号是 2007 年的 Core 2 Duo T7700，缺 popcnt，达不到 x86-64-v2 基线**；新镜像要求 v2 才能跑 |
| 处理 | rocketmq-dashboard 降到 2.0.1；minio 用源码自建静态镜像；**根治要机房改虚拟机 CPU 型号** |

## 一、现象

```
rocketmq-dashboard exited with code 127 (restarting)
rocketmq-dashboard  | Fatal glibc error: CPU does not support x86-64-v2
minio exited with code 127 (restarting)
minio               | Fatal glibc error: CPU does not support x86-64-v2
```

同一台机器上的 mysql、redis、nacos、rabbitmq、rocketmq、xxljob、elk 等容器都正常，只有这两个反复重启。

## 二、排查过程与证据

1. 看 CPU：`grep -m1 "model name" /proc/cpuinfo` → **Intel(R) Core(TM)2 Duo CPU T7700 @ 2.40GHz**（2007 年型号）。
2. 看指令集：`popcnt` **缺失**、`avx/avx2/fma` 缺失 → 不满足 x86-64-v2（v2 基线要求 SSE4.2 + POPCNT）。
3. 对比 5 台 UAT 虚拟机：**CPU 型号与指令集完全一致**（堡垒机、中间件、manager、两个 worker），所以不是"昨晚加内存关机重启"导致的，是一直如此。
4. 排除 Docker 版本：`Docker 29.9.1` 已是最新，glibc 报错发生在容器内部，与 Docker 版本无关（"换 docker-ce" 解决不了）。
5. 为什么 dev/test 能跑：那两个环境在别的宿主机上，CPU 型号更新（有 popcnt）；同样的镜像在那边没问题。
6. 为什么同机其他容器能跑：它们基于较老的系统基线构建（不要求 v2）；出问题的两个镜像是较新基线（RHEL9/UBI9 系 glibc 从构建上就要求 x86-64-v2）。

## 三、根因

**虚拟机 CPU 型号被设置成了很老的兼容型号（Core 2 Duo T7700），缺少 POPCNT 等 x86-64-v2 必需指令。**

近年很多容器镜像基于 RHEL9 / UBI9 或较新的发行版构建，其 glibc 在启动时检测不到 v2 指令会直接 `Fatal glibc error` 退出。这不是应用问题，也不是 Docker 问题，是**虚拟机 CPU 型号**的问题。

## 四、处理

### 1. rocketmq-dashboard（已恢复）

镜像从 `2.1.0` 降到 `2.0.1`（2.0.1 基于 JDK8 的较老基线，不要求 v2）。

```yaml
# /home/chili/docker-compose.yml
image: "apacherocketmq/rocketmq-dashboard:2.0.1"    # 原 2.1.0
```

改完 `docker compose up -d rocketmq-dashboard`，日志显示 Tomcat 正常启动、已连上 nameserver。原文件备份为 `docker-compose.yml.bak-20261016`。

### 2. minio（已恢复，用自建镜像）

官方渠道都断了，没法简单降版本：

- `minio/minio`（Docker Hub）→ 404，仓库已下架
- `dl.min.io` 二进制下载 → 410 Gone
- 镜像站 `pgsty/minio` 全部 tag → 都是同一套新基线，全部要求 v2
- `quay.io/minio/minio` → 401，`bitnami/minio` → not found

解决办法：**用源码编译一个静态二进制镜像**（Go 静态编译，跟 glibc / CPU 指令集无关）。

```dockerfile
# /opt/minio-build/Dockerfile
FROM golang:1.24-alpine AS builder
RUN apk add --no-cache git
WORKDIR /src
ARG MINIO_TAG
RUN git clone --depth 1 --branch ${MINIO_TAG} https://github.com/minio/minio.git . \
    && CGO_ENABLED=0 go build -ldflags "-w -s -X github.com/minio/minio/cmd.Version=${MINIO_TAG} -X github.com/minio/minio/cmd.ReleaseTag=${MINIO_TAG}" -o /out/minio .
FROM scratch
COPY --from=builder /out/minio /minio
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
EXPOSE 9000 9001
ENTRYPOINT ["/minio"]
CMD ["server", "/data"]
```

```bash
cd /opt/minio-build
sudo docker build --build-arg MINIO_TAG=RELEASE.2025-10-15T17-29-55Z -t minio-uat:RELEASE.2025-10-15T17-29-55Z .
# 改 compose 里的镜像
# image: pgsty/minio:RELEASE.2026-06-18T00-00-00Z  →  minio-uat:RELEASE.2025-10-15T17-29-55Z
sudo docker compose up -d minio
```

## 五、验证结果

| 检查 | 结果 |
| --- | --- |
| 自建 minio 能否在老 CPU 上运行 | ✅ `--version` 正常输出（不再有 glibc 报错，Runtime: go1.24.13） |
| minio 容器状态 | ✅ Up |
| `http://203.0.113.1:9000/minio/health/live` | ✅ 200 |
| `http://203.0.113.1:9000/minio/health/ready` | ✅ 200 |
| 控制台 `203.0.113.1:9090` | ✅ 200 |
| 数据卷 `chili_minio-data` | ✅ 保留未动（挂载点 `/var/lib/docker/volumes/chili_minio-data/_data`，`.minio.sys` 已生成） |
| rocketmq-dashboard | ✅ Up，Tomcat 启动、连上 nameserver |

最终 compose 改动（原文件备份 `/home/chili/docker-compose.yml.bak-20261016*`）：

```diff
- image: "apacherocketmq/rocketmq-dashboard:2.1.0"
+ image: "apacherocketmq/rocketmq-dashboard:2.0.1"

- image: pgsty/minio:RELEASE.2026-06-18T00-00-00Z
+ image: minio-uat:RELEASE.2025-10-15T17-29-55Z
```

已知小差异：自编译的 minio 版本号显示 `DEVELOPMENT.GOGET`（官方镜像是构建时注入版本元数据，我们没带那个参数），功能不受影响；介意的话可以用仓库自带的 Makefile 构建。

## 六、运维操作笔记（发给群里的版本）

【运维笔记 · 容器报 CPU does not support x86-64-v2 怎么处理】

一、先判断（一条命令）

```bash
grep -m1 "model name" /proc/cpuinfo; grep -qw popcnt /proc/cpuinfo && echo "CPU 满足 x86-64-v2" || echo "缺 popcnt → 就是这个原因"
```

二、原因

虚拟机 CPU 型号太老（本次是 Core 2 Duo T7700），而近年基于 RHEL9 / UBI9 等新基线构建的镜像要求 x86-64-v2 指令集，启动时直接 `Fatal glibc error` 退出（exit 127）。**跟 Docker 版本无关**，换 docker-ce 解决不了。

三、两条路

1. **根治（推荐）**：让机房把这几台虚拟机的 CPU 类型改成 `host`（直通宿主机）或 Skylake 及以上型号，需要关机改、改完开机。改完所有新镜像都能直接跑。
2. **临时绕行（不改 CPU）**
   - 能降版本的降版本。例：rocketmq-dashboard `2.1.0 → 2.0.1`（改 `/home/chili/docker-compose.yml` 里的 image，然后 `sudo docker compose up -d rocketmq-dashboard`）。
   - 不能降版本的自建静态镜像。minio 官方渠道已下线，用源码编译（服务器上 `/opt/minio-build/Dockerfile` 已放好）：

```bash
cd /opt/minio-build
sudo docker build --build-arg MINIO_TAG=RELEASE.2025-10-15T17-29-55Z \
  -t minio-uat:RELEASE.2025-10-15T17-29-55Z .
# 把 /home/chili/docker-compose.yml 里 minio 的 image 改成 minio-uat:RELEASE.2025-10-15T17-29-55Z
cd /home/chili && sudo docker compose up -d minio
```

四、验证

```bash
sudo docker ps | grep -E "minio|rocketmq-dashboard"          # 两个都应该是 Up
curl -s -o /dev/null -w "%{http_code}\n" http://203.0.113.1:9000/minio/health/live   # 期望 200
sudo docker logs --tail 5 rocketmq-dashboard | tail -1       # 期望看到 Tomcat started
```

五、注意

- 备份在 `/home/chili/docker-compose.yml.bak-20261016*`；机房改完 CPU 后，这两个服务都可以切回官方镜像。
- 以后任何容器报这个错，都先跑第一节那条命令确认 popcnt 是否缺失。

## 六、遗留与建议

### 1. 根治：机房改虚拟机 CPU 型号（建议尽快）

把这几台 UAT 虚拟机的 CPU 类型改成 **host（直通宿主机）**，或至少改成支持 x86-64-v2 的型号（Skylake-Client 及以上）。HCI 平台一般要在虚拟机关机状态下修改，改完开机。

不改的话，**以后任何基于较新系统基线构建的镜像都会踩同一个坑**（这类镜像越来越多），每遇到一个就得降版本或自己编译，成本会累积。

### 2. 当前绕行的代价

- minio 用的是自建镜像，升级时要在 `/opt/minio-build` 重新编译（改 `MINIO_TAG` 即可），不能直接用官方镜像；
- rocketmq-dashboard 停在 2.0.1，暂时不能用 2.1.0 的新特性；
- CPU 修好之后，两者都可以直接切回官方镜像。

### 3. 排查这类问题的口诀

容器报 `Fatal glibc error: CPU does not support x86-64-v2` 时：

```bash
grep -m1 "model name" /proc/cpuinfo     # 看 CPU 型号，太老就要怀疑
grep -qw popcnt /proc/cpuinfo && echo OK || echo "缺 popcnt（不满足 v2）"
```

缺 popcnt 就是根因，换 Docker 版本、重装系统都没用，要改虚拟机 CPU 型号。
