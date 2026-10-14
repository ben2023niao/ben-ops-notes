---
id: "doc-f3c3328121b7"
title: "UAT 部署架构摘要（提取自 视讯项目UAT部署.xmind）"
date: "2026-10-15T15:10:56+08:00"
dateSource: "文件创建/修改时间"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Docker", "Nginx", "MySQL", "Redis", "自动化", "源码与配置"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8815%E6%97%A5-%E5%8E%9F%E5%A7%8B%E8%B5%84%E6%96%99/UAT%E6%9E%B6%E6%9E%84%E6%91%98%E8%A6%81.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月15日-原始资料/UAT架构摘要.md"
sourceSha256: "c85cabf23d03bba08a9b38762e48abdf37d41095160639b4bf276dac5fe03e1f"
sourceSystem: "project-doc"
---

# UAT 部署架构摘要（提取自 视讯项目UAT部署.xmind）

> 来源文件：`~/Projects/work/ops/devops/devops-bkl/doc/2026年10月15日-原始资料/UAT架构摘要.md`

> 整理日期：2026-10-15 15:10｜日期依据：文件创建/修改时间

原文为脑图，这里提取文字部分；架构图（逻辑架构、物理架构）为图片，见原文件。

## 整体方案

1. 应用服务：Docker Swarm（Docker Stack）部署，模拟生产环境高可用。
2. 中间件服务：独立 Docker Compose 部署，降低服务器资源占用。
3. 运维支撑服务：GitLab、Nexus、Harbor、Jenkins、ELK、SRS，与 dev / test 环境共享。

## 部署说明（物理架构）

1. 中间件节点：部署中间件 Docker Compose 和前端项目静态文件。
2. 后端服务集群节点：部署后端应用服务，按项目工程划分 Docker Stack。
3. 后端服务通过节点 IP 访问中间件服务和运维支持服务。
4. UAT 环境服务器部署在运维支撑服务器同一局域网。

## 逻辑架构组件

| 层次 | 组件 |
| --- | --- |
| 反向代理 | Nginx |
| 前端应用 | game-admin-panel、game-agent-panel、middle-station-admin-panel、middle-station-merchant-panel、pay-admin-panel、pay-merchant-panel |
| 后端服务 | game-backend（gateway / auth / admin / agent / dealer）、middle-station-backend（gateway / auth / openapi / queue / scheduler）、pay-backend（gateway / auth / admin / merchant / merchant-open） |
| 中间件 | MySQL、Redis、RabbitMQ、RocketMQ、Nacos、MinIO、xxl-job admin |
| 运维支撑 | GitLab、Nexus、Harbor、Jenkins、ELK、SRS |

## 配置注意事项（原文）

**节点配置**

1. 自动清理无用 Docker 镜像：`0 3 * * * /usr/bin/docker image prune -f`
2. 限制 Docker 容器日志大小（`/etc/docker/daemon.json`）：`insecure-registries`（dev 的 Harbor）、`log-opts` max-size 100m / max-file 3

**后端服务配置**：Swarm `deploy` 副本数 2、`start-first` 滚动更新、失败回滚、健康检查重试等（原文为 compose 片段）。

**Jenkins 配置**：前端页面发布到中间件节点；后端 `docker stack deploy --with-registry-auth --force-redeploy`。

## 资源规划

- 中间件节点：1 个，8C24G + SSD 256G
- 后端服务集群：3 个（1 Manager + 2 Worker），8C32G + SSD 256G
