---
id: "doc-435a941bab85"
title: "UAT 部署资料摘要"
date: "2026-10-23T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Linux", "Shell", "Python", "Nginx", "MySQL", "Redis", "监控告警"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8823%E6%97%A5-UAT%E9%83%A8%E7%BD%B2%E8%B5%84%E6%96%99%E6%91%98%E8%A6%81/2026%E5%B9%B410%E6%9C%8823%E6%97%A5-UAT%E9%83%A8%E7%BD%B2%E8%B5%84%E6%96%99%E6%91%98%E8%A6%81.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月23日-UAT部署资料摘要/2026年10月23日-UAT部署资料摘要.md"
sourceSha256: "d1f6be93c62630287712a702608af7e15d6de92200e5a3cd4c87400a249d7faa"
sourceSystem: "project-doc"
---

# UAT 部署资料摘要

> 来源文件：`~/Projects/work/ops/devops/devops-bkl/doc/2026年10月23日-UAT部署资料摘要/2026年10月23日-UAT部署资料摘要.md`

> 整理日期：2026-10-23 00:00｜日期依据：文件名日期

日期：2026-10-23
说明：原始 `UAT部署/` 目录含明文密码、Token、Harbor 凭据和 Jenkins 配置，**不纳入 Git**。本文件是去敏后的结构和操作摘要。

## 三遍学习记录

1. 第一遍：盘点 XMind 规划/操作、drawio、服务器清单、compose、nginx、SQL、ELK 模板和发布脚本。
2. 第二遍：对照 Beszel 7 台系统、5 台 UAT 容器、当前磁盘和已知故障。
3. 第三遍：抽取发布、回滚、监控、磁盘、FD、SRS、证书和中间件操作步骤，产出 `bkl-运维手册.html`。

## 规划架构

```text
用户 → 前端静态页 / 应用 nginx
  → Swarm gateway（game 8000 / middle-station 8100 / pay 8200）
  → 后端服务
  → MySQL / Redis / RabbitMQ / RocketMQ / Nacos / MinIO / xxl-job

worker01/02 → IEPL → SRS 203.0.113.1/28

运维支撑：JumpServer / Beszel / GitLab / Harbor / Jenkins / ELK / Prometheus
```

## 真实环境与资料差异

| 项目 | UAT 资料 | 当前真实 |
| --- | --- | --- |
| SRS | 旧规划写 203.0.113.1 | 专线探测目标 203.0.113.1；另有韩国 103.57.202.91、新加坡 206.131.201.11 两台 SRS |
| GitLab | 规划中提到 dev/test 共享 | 实际部署在堡垒机 43.249.251.15，域名 gitlab.evercare.id |
| Swarm | 1 Manager + 2 Worker | 一致：manager .12，worker .13/.14 |
| game healthcheck | 仓库 UAT部署新版 start_period 200s | `/home/stack` 旧副本曾为 30s，部署前必须 diff |
| middleware 磁盘 | — | 2026-10-23 清理后约 77% |

## 服务与入口

### 运维入口

- 堡垒机：https://manage.evercare.id
- 监控：https://beszel.evercare.id
- 工作台：https://work.evercare.id
- GitLab：https://gitlab.evercare.id

### UAT 应用入口

`uat*.dgjcoder.top`，主要包括：

- game：`uat`、`uat-admin`、`uat-agent`、`uat-app`、`uat-dealer`、`uat-web`、`uat-web-comp`、`uat-download`、`uat-download-comp`、`uat-webhook`
- pay：`uat-pay`、`uat-pay-admin`、`uat-pay-merchant`、`uat-pay-agent`、`uat-pay-webhook`
- middle-station：`uat-middle-station-admin`、`uat-middle-station-agency`
- 其他：`uat-oss`、`uat-game-portal`、`uat-web-boot1~3`

## 端口

| 服务 | 端口 |
| --- | --- |
| UAT 应用 nginx | 80 |
| game / middle-station / pay gateway | 8000 / 8100 / 8200 |
| scheduler | 7201 / 7202 / 7203 |
| Jenkins | 8888 / 50000 |
| Harbor | 18888 |
| Kibana / ES / Logstash | 5601 / 9200 / 8686 |
| Prometheus / Grafana / Alertmanager / cAdvisor | 5090 / 5000 / 5093 / 5080 |
| Swarm | 2377 TCP、7946 TCP+UDP、4789 UDP |
| JumpServer | 8081 本机、2222 SSH |
| GitLab | 8929 本机 |

## 资料内容索引

- `视讯项目UAT部署规划.xmind`：整体方案、逻辑/物理架构、节点配置、Swarm 资源规划
- `视讯项目UAT部署操作.xmind`：环境初始化、Harbor/Jenkins/ELK/中间件、Swarm、Portainer、Prometheus 操作
- `视讯项目UAT部署.drawio`：前端、后端 Stack、中间件、运维支撑域关系
- `UAT服务器.docx`：机器规格、IP、旧 SRS 地址和账号要求（含敏感值，不直接复制）
- `部署脚本/中间件/chili`：MySQL 主从、Redis、RabbitMQ、RocketMQ、Nacos、MinIO、xxl-job、nginx
- `部署脚本/中间件/elk`：Elasticsearch、Logstash、Kibana、Kafka
- `部署脚本/中间件/harbor`、`jenkins`、`prometheus`
- `部署脚本/服务集群/stack`：chili-game / chili-pay / middle-station Swarm compose 和发布脚本
- `配置数据/数据库`：nacos、xxl-job 初始化 SQL
- `配置数据/ELK初始化脚本`：索引模板、ILM、GeoIP pipeline

## 相关手册

- [bkl-运维手册.html](../../bkl-运维手册.html)
- [UAT环境部署手册](../2026年10月15日-UAT环境部署手册/UAT环境部署手册-2026年10月15日-v1.md)
- [专线网络质量监控](../2026年10月18日-专线网络质量监控/2026年10月18日-专线网络质量监控.md)
- [监控阈值与容器FD巡检](../2026年10月20日-监控阈值与容器FD巡检/2026年10月20日-监控阈值与容器FD巡检.md)
