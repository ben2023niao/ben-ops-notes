---
id: "doc-ee04bfc28b25"
title: "测试环境备案域名迁移到新 Nginx 服务器收口"
date: "2026-07-30T21:18:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "监控告警", "自动化", "CDN", "DNS", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-2118-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8D%E8%BF%81%E7%A7%BB%E5%88%B0%E6%96%B0Nginx%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%94%B6%E5%8F%A3.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-2118-【运维记录】测试环境备案域名迁移到新Nginx服务器收口.md"
sourceSha256: "ef8b207011ed57ed7f99ed1da7b948cba623e960b3476bad2f0ef11b3f6490e7"
sourceSystem: "project-doc"
---

# 测试环境备案域名迁移到新 Nginx 服务器收口

> 来源文件：`~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-2118-【运维记录】测试环境备案域名迁移到新Nginx服务器收口.md`

> 整理日期：2026-07-30 21:18｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-30 21:18

## 背景

用户确认测试环境备案域名已迁移到新服务器：

```text
服务器：162.211.181.13
hostname：youdianse-test-cdn-proxy
角色：EdgeOne / 腾讯 CDN HTTP 回源服务器、备案域名前端反向代理 Nginx
Nginx 配置：/etc/nginx/conf.d/youdianse-test-record-domains.conf
```

本文用于把旧文档统一改成迁移后的链路，避免后续 AI 或运维继续按旧测试服务器入口理解备案域名。

## 迁移后总链路

```text
公网用户
  -> EdgeOne / 腾讯 CDN，HTTPS 终止
  -> HTTP 回源 162.211.181.13:80
  -> youdianse-test-cdn-proxy 本机 Nginx
     -> H5 页面：38.92.8.34:3003
     -> PC 页面：38.92.8.34:3004
     -> API 路径：38.92.8.34:8088
     -> H5 静态资源：AWS S3 H5 静态桶
     -> PC 静态资源：AWS S3 PC 静态桶
     -> uploads 图片：CloudFront uploads，token/t 放行，裸链固定图
```

旧测试服务器 `38.92.8.34` 当前仍是业务服务源站，不是要下线的机器：

```text
H5 容器：youdianse_test_18game_h5_client_3003
PC 容器：youdianse_pc_dev_18game_pc_client_3004
后端 API：youdianse-dev-php-nginx / youdianse-dev-php-web
```

## 新 Nginx 域名配置

| 域名 | 入口类型 | Nginx 规则 | 上游 |
| --- | --- | --- | --- |
| `test-h5.hbabaxb.cn` | H5 页面 | `/` 到 H5，`/(api|channel|customer)` 到 API | `38.92.8.34:3003` / `38.92.8.34:8088` |
| `test-h5.hbazuua.cn` | H5 页面 | `/` 到 H5，`/(api|channel|customer)` 到 API | `38.92.8.34:3003` / `38.92.8.34:8088` |
| `test-pc.hbabaxb.cn` | PC 页面 | `/` 到 PC，`/(api|channel|customer)` 到 API | `38.92.8.34:3004` / `38.92.8.34:8088` |
| `test-pc.hbazuua.cn` | PC 页面 | `/` 到 PC，`/(api|channel|customer)` 到 API | `38.92.8.34:3004` / `38.92.8.34:8088` |
| `test-h5-s3.hbabaxb.cn` | H5 静态资源 | `/` 到 H5 S3 桶 | `18game-nuxt-static-test-h5.s3.ap-southeast-1.amazonaws.com` |
| `test-pc-s3.hbabaxb.cn` | PC 静态资源 | `/` 到 PC S3 桶 | `18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com` |
| `test-img.hbabaxb.cn` | uploads 图片 | `/uploads/` 校验 `token/t`；无效请求返回固定图 | `d1rct3ku9n07y3.cloudfront.net` |
| `test-img.hbazuua.cn` | uploads 图片 | `/uploads/` 校验 `token/t`；无效请求返回固定图 | `d1rct3ku9n07y3.cloudfront.net` |

日志位置：

```text
/var/log/nginx/test-h5.record.access.log
/var/log/nginx/test-pc.record.access.log
/var/log/nginx/test-h5-s3.record.access.log
/var/log/nginx/test-pc-s3.record.access.log
/var/log/nginx/test-img.record.access.log
```

## HTTPS 与回源

```text
新服务器当前只监听 80 和 22。
HTTPS 由 EdgeOne / 腾讯 CDN 终止。
EdgeOne / 腾讯 CDN 回源协议应为 HTTP，回源端口为 80。
Host 头保持原请求域名。
不要配置 HTTPS 回源，除非后续给新服务器补 443 证书。
```

## 当前复核结果

新服务器状态：

```text
hostname=youdianse-test-cdn-proxy
nginx=active
docker=active
listen=80,22
```

公网抽样：

```text
test-h5.hbabaxb.cn/game：HTTPS 200，test-img total=133，[敏感内容已脱敏]
test-h5.hbazuua.cn/game：HTTPS 200，test-img total=133，[敏感内容已脱敏]
test-pc.hbazuua.cn/game?page=4：HTTPS 200，test-img total=41，[敏感内容已脱敏]
test-h5-s3.hbabaxb.cn/version.json：HTTPS 200，size=705
test-img.hbazuua.cn 裸链：HTTPS 200，size=13716
```

本次需后续复测的点：

```text
test-pc.hbabaxb.cn：本地 DNS 曾瞬时解析失败，需要后续复测。
test-pc-s3.hbabaxb.cn：本地曾出现一次 SSL_ERROR_SYSCALL，需要后续复测。
test-img.hbabaxb.cn 裸链：本地 EdgeOne 节点曾超时，需要后续从多地复测。
新服务器 access log：本次唯一 probe 标记未命中，需要后续用 no_cache 探测确认 EdgeOne 已稳定回源。
```

## 文档更新范围

已更新：

```text
docs/2026-07-30-1939-【运维记录】测试环境域名与资源链路总览.md
docs/2026-07-30-2050-【运维记录】测试环境备案域名反代服务器配置记录.md
workbench/TEST_ENV_DOMAIN_RELATIONS.md
workbench/TEST_ENV_RECORD_DOMAIN_PROXY_NGINX.md
workbench/PROJECT_RUNTIME_CHAINS.md
workbench/CURRENT_STATE.md
workbench/ACTIVE_TASKS.md
workbench/CURRENT_TASK.md
```

## 后续注意

```text
1. 后续排查备案域名先看 youdianse-test-cdn-proxy。
2. 后续排查业务容器和 API 仍看 38.92.8.34。
3. 切流稳定性确认必须同时看公网状态和新服务器 access log。
4. 清理旧测试服务器备案域名配置前，必须先备份旧配置，并取得用户明确确认。
5. 后续 Telegram 通知默认发到原运维监控报警群和 18game运维 群。
   （2026-08-07 更新：Webhook 自动发布通知只发原运维监控报警群，不再发 18game运维 群；人工发布、文档与步骤通知保持已配置群。）
```

## 2026-07-31 补充：H5 图片域名回源兜底

```text
环境标签：测试环境
新源站：162.211.181.13 / youdianse-test-cdn-proxy
配置：/etc/nginx/conf.d/youdianse-test-record-domains.conf
```

本次补充：

```text
1. 发现新源站 nginx.service 曾为 failed，80 端口未监听；已重新启动并 reload。
2. test-img.* /uploads/ 增加 CloudFront 上游 403/404/500/502/503/504 统一兜底到固定图。
3. PC 静态资源域名补 CORS 响应头；H5 静态资源当前由 S3 桶返回 CORS，公网已验证 Access-Control-Allow-Origin: *。
```

验证：

```text
新源站本机：test-img.hbabaxb.cn 缺失 uploads token/t -> HTTP 200，size=13716
新源站本机：test-img.hbazuua.cn 缺失 uploads token/t -> HTTP 200，size=13716
直连新源站：curl --resolve test-img.*:80:162.211.181.13 -> HTTP 200，size=13716
```

当前仍需腾讯 EdgeOne / CDN 控制台确认：

```text
test-img.hbabaxb.cn、test-img.hbazuua.cn 必须回源到 162.211.181.13:80。
回源协议必须是 HTTP。
回源 Host 保持原请求域名。
修改后清理 test-img.* /uploads/* 相关缓存。
```

原因：

```text
公网 HTTPS test-img 唯一路径仍返回 404/502，且未进入新源站 access log。
说明公网边缘层当前没有稳定命中 162.211.181.13 的 Nginx 规则。
```
