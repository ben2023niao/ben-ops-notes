---
id: "doc-49e917867982"
title: "【问题排查+修复】nginx X-Real-IP 配置核验与 verify 域名补漏记录"
date: "2026-09-09T12:36:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "Nginx", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-09-09-1236-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%2B%E4%BF%AE%E5%A4%8D%E3%80%91nginx%20X-Real-IP%E9%85%8D%E7%BD%AE%E6%A0%B8%E9%AA%8C%E4%B8%8Everify%E5%9F%9F%E5%90%8D%E8%A1%A5%E6%BC%8F%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-09-09-1236-【问题排查+修复】nginx X-Real-IP配置核验与verify域名补漏记录.md"
sourceSha256: "83b006b3ecdfaf9e8f268f2a1d20636b254a7aa7aa584399e388a698c11fc259"
sourceSystem: "project-doc"
---

# 【问题排查+修复】nginx X-Real-IP 配置核验与 verify 域名补漏记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-09-09-1236-【问题排查+修复】nginx X-Real-IP配置核验与verify域名补漏记录.md`

> 整理日期：2026-09-09 12:36｜日期依据：文件名日期

时间：2026-09-09 12:36（Asia/Manila）
项目：DBQP / PGServer master（巴西宝塔+备用 nginx、香港入口 nginx）
结果：✅ 公共反代均配置 X-Real-IP；verify.pgofficialbx.com 两处缺失已补齐并 reload

## 一、问题

```text
确认 nginx 转发服务器是否配置：
  proxy_set_header X-Real-IP $remote_addr;
```

## 二、核验结果

```text
巴西宝塔（35.247.205.6 / 203.0.113.1）：
  socket/api/game/all-games/tada 等公共反代均配置 X-Real-IP；
  唯一缺失：/www/server/panel/vhost/nginx/verify.pgofficialbx.com.conf。

巴西备用 nginx（34.151.249.53 / 203.0.113.1）：
  公共反代同源配置完整；
  唯一缺失：/etc/nginx/conf.d/verify.pgofficialbx.com.conf。

香港入口 nginx（34.92.13.108 / 203.0.113.1）：
  8 个动态 upstream 全部通过 /etc/nginx/snippets/dbqp-hongkong-proxy.conf
  统一配置 X-Real-IP（8 处 proxy_pass 均带 snippet include）。
```

verify.pgofficialbx.com.conf 之前缺失行：

```text
upstream verify_pgofficialbx_pg 转发 34.39.183.154:9091 /
34.95.230.202:9091（PG 验证域），location / 内只有
Connection/X-Forwarded-Proto/X-Forwarded-For/Host，缺少 X-Real-IP。
```

## 三、修复

```text
1) 仓库新增配置快照：
   docker/线上服务器信息/baota/nginx/panel-vhost-nginx/verify.pgofficialbx.com.conf
   （location / 内补充 proxy_set_header X-Real-IP $remote_addr;）。
2) 宝塔：
   备份 verify.pgofficialbx.com.conf.bak-20260909-before-xrealip，
   覆盖为新配置，nginx -t 通过，nginx -s reload 成功。
3) 备用机：
   备份 verify.pgofficialbx.com.conf.bak-20260909-before-xrealip，
   覆盖为新配置，nginx -t 通过，nginx -s reload 成功。
```

## 四、复验

```text
宝塔 live conf：第 24 行 proxy_set_header X-Real-IP $remote_addr; 存在；
nginx -T 全量 X-Real-IP 计数 26。
备用机 live conf：第 24 行存在；nginx -T 计数 24。
公网 verify.pgofficialbx.com / api.pgofficialbx.com 根路径返回 403
（业务无路由的正常响应，代理链路已可达，无 502/504）。
香港核验保持通过：动态 upstream 8/8 使用含 X-Real-IP 的公共 snippet。
```

## 五、结论

```text
此前群内问题答案：
  - nginx 公共转发配置都有 X-Real-IP；
  - 唯一例外 verify.pgofficialbx.com.conf 已在宝塔与备用机补齐并 reload。
```

## 六、群通知回执

```text
5340 核验发现+修复计划
5341 修复完成+复验
5342 汇总与文档
5343 本地提交结果
```
