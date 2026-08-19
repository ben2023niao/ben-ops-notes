---
id: "doc-9e1eb5218332"
title: "【问题排查】线上环境游戏登录失败排查记录：新网关 nginx 连接打满"
date: "2026-08-20T02:53:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "监控告警", "CDN", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0253-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E6%B8%B8%E6%88%8F%E7%99%BB%E5%BD%95%E5%A4%B1%E8%B4%A5%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95-%E6%96%B0%E7%BD%91%E5%85%B3nginx%E8%BF%9E%E6%8E%A5%E6%89%93%E6%BB%A1.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0253-【问题排查】线上环境游戏登录失败排查记录-新网关nginx连接打满.md"
sourceSha256: "fdfb7fb94579a44ff2a82a817739c18fe6dc978e99e383de1be421000346dc0c"
sourceSystem: "project-doc"
---

# 【问题排查】线上环境游戏登录失败排查记录：新网关 nginx 连接打满

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0253-【问题排查】线上环境游戏登录失败排查记录-新网关nginx连接打满.md`

> 整理日期：2026-08-20 02:53｜日期依据：文件名日期

文档日期：2026-08-20 02:53
环境：游点涩线上环境（main 分支）
分类：问题排查
标签：线上环境、游戏登录、SDK、新网关 nginx、worker_connections、CloudFront

## 现象

```text
平台官网/H5 注册、登录正常；平台内部分游戏退出账号后无法再次登录/注册，
登录页报“网络连接失败”；受影响游戏选服、支付同步异常；
部分游戏正常（异世界物语、星界大战等），部分受影响（蜜桃、欲女梦工厂、淫欲斗罗、tong 等）；
注册与充值订单仍在发起（间歇性成功）。
开始时间：08-20 01:00 左右（北京时间），用户集中反馈。
```

## 排查过程（只读，未修改线上代码/配置）

### 1. 后端平台侧（203.0.113.1）

```text
后台 200、CICD 200；web/nginx/cron 正常（Up 12h）
api_response 08-20 登录接口 22699 条全部 status:"y"，无失败
后端 nginx 01:00-02:10 状态：200=983078，404=2660，499=990，无 5xx
结论：平台后端登录接口正常。
```

### 2. 宝塔侧（16.208.5.147）

```text
公网 admin/cicd/h5.18h.game 全部 200；站点日志窗口内无异常
结论：宝塔入口正常。
```

### 3. 新网关 nginx（16.208.38.88 / ip-172-31-27-233）——根因

```text
背景：18game H5/PC 统一网关，8/12 上线，承载 h5.18h.game、h5.youdianse-main.xyz、
      pc.youdianse-main.xyz、new.youdianse.com 等大量域名（CloudFront CDN 回源到该机）
nginx 配置：worker_processes auto（8 worker）× worker_connections 768 ≈ 6144 连接上限
/api 代理：proxy_pass https://203.0.113.1（宝塔内网），无 upstream keepalive，
           每个请求新建 TLS 连接（proxy_ssl_server_name on）

错误日志（/var/log/nginx/error.log）：
08-20 01:00:05 CST 起大量：
  [alert] 768 worker_connections are not enough while connecting to upstream
  request: "POST /api/sdk/system/gameTrack ...", upstream: "https://203.0.113.1:443/api/..."
  客户端多为 CloudFront 边缘 IP（52.46.x / 3.172.x）
累计：469 条；08-19 18:00 CST 起已零星出现（248），01:00 达 141，最新 02:39 CST（仍在持续）

访问日志窗口（19/Aug 17:00-17:59 UTC=08-20 01:00-01:59 CST）：
  总请求 277 万；200=2771714，404=2857，499=2162，500=2
  /api/sdk/Login 窗口内：200=16569，499=41（间歇性失败）

次因：$ssl_server_name 为空时证书路径 /etc/letsencrypt/live//fullchain.pem 不存在，
      导致 SSL 握手失败（02:32-02:39 CST 仍在报），同样表现为“网络连接失败”。
```

## 根因结论

```text
1. 新网关 nginx worker_connections=768 连接池打满，无法连接上游宝塔，
   导致游戏 SDK 的 /api 请求间歇性失败（能连上就成功，连不上就“网络连接失败”）。
2. /api 代理未配置 upstream keepalive，每个请求新建 TLS 连接，连接开销大，
   在 CloudFront 高并发回源下极易打满。
3. 与 IP 黑名单无关（黑名单已清空仍复现）；与平台后端无关（接口全 200）；
   平台官网直连宝塔正常，游戏走 CloudFront -> 新网关 -> 宝塔链路，卡在新网关。
```

## 处置建议（需运维授权后执行，本次未改线上）

```text
1) 立即缓解：worker_connections 768 -> 4096（8 worker ≈ 3.2 万连接），nginx -t 后 reload。
2) 结构优化：/api 代理改 upstream + keepalive（proxy_http_version 1.1 + Connection ""），
   复用与宝塔的 TLS 连接，大幅降低连接开销。
3) 修复次因：未知/空 $ssl_server_name 时给默认证书或直接 444，避免 SSL 握手失败刷错误。
4) 监控：error.log 出现 "worker_connections are not enough" 立即告警；
   开启 stub_status 观察连接数。
5) 验证：改后模拟多游戏登录/选服/支付，观察 499/502 消失、错误日志归零。
```

## 通知记录

```text
步骤 1 仓库状态与文档/workbench 就绪   message_id 9946
步骤 2 线上健康基线核验                message_id 9947
步骤 3 故障窗口日志分析（根因）        message_id 9948
步骤 4 结论与处置建议                  message_id 9949
最终总结                              见群内后续消息
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据、.env 敏感值。
