---
id: "doc-8570d7ae98a5"
title: "游点涩前端预发布备用回源服务器初始化"
date: "2026-08-03T22:05:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Python", "Docker", "Nginx", "自动化", "CDN", "DNS"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-03_2205-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%2B%E7%8E%AF%E5%A2%83%E5%88%9D%E5%A7%8B%E5%8C%96%E3%80%91%E6%B8%B8%E7%82%B9%E6%B6%A9%E5%89%8D%E7%AB%AF%E9%A2%84%E5%8F%91%E5%B8%83%E5%A4%87%E7%94%A8%E5%9B%9E%E6%BA%90%E6%9C%8D%E5%8A%A1%E5%99%A8%E5%88%9D%E5%A7%8B%E5%8C%96.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-03_2205-【运维记录+环境初始化】游点涩前端预发布备用回源服务器初始化.md"
sourceSha256: "80ecbdbe84a3e6b5a5f253cc23a5b6faac3e4f92c904bfd86fcfcb86d4dbaca6"
sourceSystem: "project-doc"
---

# 游点涩前端预发布备用回源服务器初始化

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608032205-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BPython-%E6%B8%B8%E7%82%B9%E6%B6%A9%E5%89%8D%E7%AB%AF%E9%A2%84%E5%8F%91%E5%B8%83%E5%A4%87%E7%94%A8%E5%9B%9E%E6%BA%90%E6%9C%8D%E5%8A%A1%E5%99%A8%E5%88%9D%E5%A7%8B%E5%8C%96.md)

> 整理日期：2026-08-03 22:05｜日期依据：文件名日期

环境标签：测试环境 / 线上前置模拟测试 / CDN 备用回源候选

时间：2026-08-03 21:49-22:05

## 需求背景

用户新增服务器 `43.241.16.84:22`，用途为：

- 测试环境前端 PC/H5 调试完成后、部署到线上环境之前的模拟测试机器。
- 本次图片/视频加密上线前，用于跑线上代码容器配合测试。
- 后续作为线上腾讯云 CDN 的备用回源 IP。
- 本次仅部署 Docker 环境和原生 Nginx。

聊天记录补充：服务器规格为 `48-64 / 1T SSD / 50M`，预算归入下月，费用约 `235U`。账号密码只走安全渠道，不写入本文档和 Git。

## 风险与范围

- 风险级别：`C1`，新服务器基础环境初始化。
- 已做：只读核验、Docker/Nginx 基础环境部署、健康检查页配置、本机 Docker build/run 验证、workbench 落档、群通知。
- 未做：未部署业务容器，未接入生产 CDN/DNS，未修改线上域名、证书、IAM、CDN 源站或回源配置。
- 后续将该 IP 接入线上腾讯云 CDN 备用回源属于 `P2`，需要单独审批、变更窗口和回滚方案。

## 通知范围

本次按用户要求，每个明确步骤均同步通知：

- `稳定备案域名+腾讯云原厂`
- `18game运维`
- `18GAME_ 上线群（正式環境）`

通知内容只包含操作总结和非敏感结果，不包含密码、token、私钥、Session Cookie、完整 Signed URL 或 `.env` 明文。

## 服务器只读核验

- IP：`43.241.16.84`
- 主机名：`wanheng`
- 登录用户：`root`
- 系统：`Ubuntu 24.04 LTS`
- Kernel：`6.8.0-31-generic`
- CPU：`48`
- 内存：约 `62GiB`
- Swap：`8.0GiB`
- 根盘：`935G`，已用约 `11G`
- 网卡：`eno1 43.241.16.84/24`
- 初始端口：仅确认 `22` 监听
- 初始 Docker：未运行
- 初始 Nginx：未安装

## 已执行操作

1. 安装基础包：`ca-certificates`、`curl`、`gnupg`、`lsb-release`、`apt-transport-https`。
2. 安装并启用 Docker Engine：`docker.io`。
3. 安装 Docker Compose：`docker-compose-v2`。
4. 安装 Docker Buildx：`docker-buildx`。
5. 安装原生 Nginx：Ubuntu apt 源 `nginx`。
6. 启用并启动服务：
   - `docker`：active / enabled
   - `nginx`：active / enabled
7. 写入默认健康页：
   - Web root：`/var/www/html`
   - Nginx 配置：`/etc/nginx/conf.d/00-frontend-preprod-health.conf`
   - `/`：默认说明页
   - `/healthz`：返回 `ok`
8. 移除 Ubuntu 默认 `sites-enabled/default`，避免默认站点与健康页冲突。
9. 执行 `nginx -t` 并 reload 通过。

## 验证结果

版本：

```text
Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2
Docker Compose version 2.40.3+ds1-0ubuntu1~24.04.1
Docker Buildx 0.30.1
nginx version: nginx/1.24.0 (Ubuntu)
```

服务状态：

```text
docker_active=active docker_enabled=enabled
nginx_active=active nginx_enabled=enabled
```

本机 HTTP：

```text
curl -fsSI http://203.0.113.1/      -> HTTP/1.1 200 OK
curl -fsS  http://203.0.113.1/healthz -> ok
curl -fsSI http://43.241.16.84/   -> HTTP/1.1 200 OK
```

Docker 本地运行能力：

```text
run_output=docker-local-runtime-ok
docker_info=ServerVersion=29.1.3 Driver=overlayfs Cgroup=2
```

说明：公共 Docker Hub 拉取 `hello-world` 时出现网络超时；已改用本地 `scratch` 最小镜像 build/run 验证 Docker 引擎可用。后续业务镜像建议使用私有仓库，或上线前确认镜像源和网络策略。

## 当前阻塞项

外部节点访问 HTTP 80 的表现：

- `nc 43.241.16.84 80`：TCP 可连接。
- `curl http://43.241.16.84/`：外部节点超时，无响应体。
- `curl http://43.241.16.84/healthz`：外部节点超时。
- 服务器系统防火墙：`ufw inactive`。
- `iptables INPUT`：默认 `ACCEPT`。
- Nginx：监听 `0.0.0.0:80` 与 `[::]:80`。
- Nginx access log：没有外部 curl 请求进入记录；本机访问公网 IP 会记录并返回 200。

初步结论：当前不像是服务器 Nginx 配置或系统防火墙问题，更像服务商/机房/上游安全策略对直连 HTTP 80 的放行或 HTTP 响应链路存在限制。该问题解决前，`43.241.16.84` 不能直接作为腾讯云 CDN 备用回源投入使用。

## Workbench 更新

已更新：

- `devops/ai_context/servers.yml`
- `workbench/MACHINE_ACCESS_MATRIX.md`
- `workbench/projects/18game_devops/CURRENT_STATE.md`
- `workbench/ACTIVE_TASKS.md`

新增服务器 ID：

```text
youdianse-frontend-preprod-cdn-origin
```

当前状态：

```text
active_with_http_origin_blocker
```

## 后续建议

1. 找服务商/机房确认 `43.241.16.84` 的 HTTP 80 入站和响应链路是否需要额外放行，或是否禁止直连 IP HTTP。
2. 堡垒机归类建议：`线上前端服务器`，用途备注为“游点涩线上前端 PC/H5 上线前模拟测试机 / 腾讯云 CDN 备用回源候选”。密码不写入 Git，以堡垒机记录为准。
3. 上线前部署 PC/H5 业务容器时，先确认镜像源策略；若不走 Docker Hub，优先使用团队私有镜像仓库。
4. 接入腾讯云 CDN 备用回源前，先完成公网 HTTP/HTTPS 验收，再走 `P2` 变更审批。
5. 图片/视频加密联调时，可先用本机 Docker/Nginx 作为线上代码容器承载环境；正式回源切换需单独记录和回滚方案。

## 回滚说明

如需撤销本次基础环境：

- 停止服务：`systemctl stop nginx docker`
- 取消自启：`systemctl disable nginx docker`
- 移除健康页配置：`/etc/nginx/conf.d/00-frontend-preprod-health.conf`
- 移除 workbench 中 `youdianse-frontend-preprod-cdn-origin` 相关索引

执行回滚前仍需按运维通知规则发群通知并保留结果。
