---
id: "doc-cfec51090d01"
title: "【优化】线上环境 nginx 全链路审计与后端 workerconnections 加固记录"
date: "2026-08-20T03:37:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "监控告警", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0337-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83nginx%E5%85%A8%E9%93%BE%E8%B7%AF%E5%AE%A1%E8%AE%A1%E4%B8%8E%E5%90%8E%E7%AB%AFworker_connections%E5%8A%A0%E5%9B%BA%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0337-【优化】线上环境nginx全链路审计与后端worker_connections加固记录.md"
sourceSha256: "cc8aeaaf77e0938c8a561f8dbc306621cef9852b3bc07879f509816e9c0e7cb3"
sourceSystem: "project-doc"
---

# 【优化】线上环境 nginx 全链路审计与后端 workerconnections 加固记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608200337-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BDocker%2BNginx-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20nginx%20%E5%85%A8%E9%93%BE%E8%B7%AF%E5%AE%A1%E8%AE%A1%E4%B8%8E%E5%90%8E%E7%AB%AF%20workerconnections%20%E5%8A%A0%E5%9B%BA%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-20 03:37｜日期依据：文件名日期

文档日期：2026-08-20 03:37
环境：游点涩线上环境（main 分支）
分类：优化
标签：线上环境、nginx、worker_connections、stub_status、连接打满、加固

## 背景

游戏登录故障修复后（网关 worker_connections 4096 + keepalive），Rock 反馈“时好时坏、
一般就是进程或其他被占满”。对 nginx 全链路做审计并加固薄弱环节。

## 全链路审计结果（修复后现状）

```text
新网关（16.208.38.88）：
  worker_connections 4096、worker_rlimit_nofile 16384（已生效）
  修复后错误数 469 无新增；近 3 分钟 15.9 万请求、499 90 条（0.06%）
宝塔（16.208.5.147）：
  worker_connections 51200、worker_rlimit_nofile 51200；错误日志 0 占满类报错
后端 nginx 容器（203.0.113.1:8088）：
  4 worker x 1024（加固前）；自修复后 0 条 worker_connections 报错；CPU 3%
H5/PC 容器（3003/3004）：CPU 19%/35%，内存正常
结论：故障时连接打满已消除，无任何层被占满。
```

## 加固内容

### 1. 后端 nginx 容器 worker_connections 1024 -> 4096

新增 `nginx/main.conf`（仓库内）：

```nginx
worker_processes auto;
worker_rlimit_nofile 16384;
events { worker_connections 4096; multi_accept on; }
```

`docker-compose.yml` nginx 服务新增挂载：

```yaml
- ${YOUDIANSE_RUNTIME_NGINX_MAIN_CONF_FILE:-./nginx/main.conf}:/etc/nginx/nginx.conf:ro
```

后端 nginx 容器已重建生效（web 随依赖短暂重启，cron 未动）。

### 2. 新网关 stub_status 观测

```nginx
location = /nginx_status {
    stub_status;
    allow 203.0.113.1;
    allow 203.0.113.1/16;
    deny all;
    access_log off;
}
```

实时观测：`curl http://203.0.113.1/nginx_status`（Active/Waiting 等）。
配置备份：/root/nginx-stub-20260819-193621.bak。

## 验证结果

```text
后端容器：worker_connections=4096、worker_rlimit_nofile=16384 生效
HTTP：后台 200、CICD 200、登录接口 200
网关：Active 716 / Waiting 604（stub_status 正常返回）
```

## 后续观察

```text
1. 高峰时段观察网关 /nginx_status 与后端 nginx 连接数；
2. 监控 cron（youdianse-nginx-gateway-alert.py）持续告警 worker_connections 不足；
3. 如需更高水位可继续上调 worker_connections / fd。
```

## 修复后复发核查（2026-08-20 04:23 补充）

```text
网关 error.log worker_connections 错误 469 条时间分布：
  08-19 17:19 CST（09:19Z）330 条（首现）
  08-20 01:00:00-01:00:06 CST（17:00Z）139 条（玩家反馈起点，6 秒窗口）
  最后一条 08-20 01:00:06 CST
02:57 CST（修复 reload）后至今：0 条；
后端监控 cron（每 5 分钟）运行约 1.5 小时全部 delta=0；
当前 stub_status：Active 545 / Waiting 435。
结论：1 点后打满仅发生在 01:00:00-01:00:06 秒级窗口，修复后无复发。
```

## 通知记录

```text
步骤 1 nginx 全链路审计（当前健康）   message_id 9970
步骤 2 nginx 链加固完成               message_id 9971
核查（修复后无复发）                  message_id 9990
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据、.env 敏感值。
