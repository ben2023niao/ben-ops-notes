---
id: "doc-e8f93b825207"
title: "【优化】线上环境游戏登录故障修复：新网关 nginx 连接打满处置记录"
date: "2026-08-20T02:59:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Docker", "Nginx", "监控告警", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0259-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E6%B8%B8%E6%88%8F%E7%99%BB%E5%BD%95%E6%95%85%E9%9A%9C%E4%BF%AE%E5%A4%8D-%E6%96%B0%E7%BD%91%E5%85%B3nginx%E8%BF%9E%E6%8E%A5%E6%89%93%E6%BB%A1%E5%A4%84%E7%BD%AE%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0259-【优化】线上环境游戏登录故障修复-新网关nginx连接打满处置记录.md"
sourceSha256: "059ae0c5bbbc2ed8506a40ec18afe047d90d077f6e93e2e884f3f8ca32c3d3f6"
sourceSystem: "project-doc"
---

# 【优化】线上环境游戏登录故障修复：新网关 nginx 连接打满处置记录

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0259-【优化】线上环境游戏登录故障修复-新网关nginx连接打满处置记录.md`

> 整理日期：2026-08-20 02:59｜日期依据：文件名日期

文档日期：2026-08-20 02:59
环境：游点涩线上环境（main 分支）
分类：优化
标签：线上环境、游戏登录、SDK、新网关 nginx、worker_connections、keepalive、监控告警

## 背景

承接 `docs/2026-08-20-0253-【问题排查】线上环境游戏登录失败排查记录-新网关nginx连接打满.md`：
根因为 18game H5/PC 统一网关 nginx（16.208.38.88 / ip-172-31-27-233）
`worker_connections=768` 连接池打满，无法连接上游宝塔，游戏 SDK /api 请求间歇性失败。
用户已授权实施修复（worker_connections 扩容、keepalive、证书兜底、监控告警）。

## 修复内容（已执行）

### 1. worker_connections 扩容（/etc/nginx/nginx.conf）

```text
worker_connections 768 -> 4096
新增 worker_rlimit_nofile 16384;
8 worker x 4096 ≈ 3.2 万并发连接上限
```

### 2. /api 上游 keepalive（conf.d/10-youdianse-prod-maps.conf）

```nginx
upstream youdianse_api_upstream {
    server 203.0.113.1:443;
    keepalive 128;
}
```

`conf.d/20-youdianse-prod-unified.conf` 的 /api location：

```nginx
proxy_pass https://youdianse_api_upstream;
proxy_http_version 1.1;
proxy_set_header Connection "";
```

效果：与宝塔的 TLS 连接复用，不再每请求新建连接（修复前 TCP TIME_WAIT 高达 19832）。

### 3. 证书兜底（10-youdianse-prod-maps.conf + 20-unified）

```nginx
map $ssl_server_name $youdianse_cert_dir {
    default /etc/letsencrypt/live/www.youdianse.com;
}
ssl_certificate $youdianse_cert_dir/fullchain.pem;
ssl_certificate_key $youdianse_cert_dir/privkey.pem;
```

效果：$ssl_server_name 为空/未匹配时回退默认证书，消除
`cannot load certificate /etc/letsencrypt/live//fullchain.pem` SSL 握手失败。

### 4. 监控告警（后端服务器）

新增 `ops/production/scripts/youdianse-nginx-gateway-alert.py`：

- 每 5 分钟 SSH 到网关（专用 ed25519 密钥，公钥已加入网关 ubuntu authorized_keys），
  统计 error.log 中 `worker_connections are not enough` 增量；
- 新增即发送 Telegram 告警到 18GAME_ 上线群（正式環境），含新增条数与最近错误；
- 首次运行只初始化标记，不误报历史存量；
- 后端 root crontab 已安装：`*/5 * * * *` flock 防重入。

## 备份与回滚

```text
网关配置备份：/root/nginx-fix-20260819-185654/
  （nginx.conf、10-youdianse-prod-maps.conf、20-youdianse-prod-unified.conf）
后端 crontab 备份：/root/crontab.before-youdianse-nginx-alert.20260820-025910
回滚：恢复备份文件后 nginx -t && nginx -s reload；移除监控 cron 行。
```

## 验证结果

```text
nginx -t：通过；reload：优雅生效（主进程 PID 不变）
压测：100 并发登录请求（h5.18h.game/api/sdk/Login/quickAccount）全部 200
公网：h5.18h.game / h5.youdianse-main.xyz / www.youdianse.com 全部 200
错误日志：worker_connections 计数 469 无新增（reload 后 0 新错误）
SSL 兜底：https://16.208.38.88/ 返回 200（IP SNI 走默认证书）
监控：脚本 root 运行 delta=0，cron 已安装
```

## 通知记录

```text
步骤 1 复验与修复方案确认        message_id 9953
步骤 5 修复验证通过（已授权执行） message_id 9954
最终总结                        见群内后续消息
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据、.env 敏感值；监控 SSH 密钥公钥仅用于网关巡检。
