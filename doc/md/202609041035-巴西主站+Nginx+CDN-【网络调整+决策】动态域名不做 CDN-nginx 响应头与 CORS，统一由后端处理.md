---
id: "doc-60cfa6f89273"
title: "【网络调整+决策】动态域名不做 CDN/nginx 响应头与 CORS，统一由后端处理"
date: "2026-09-04T10:35:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Nginx", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-09-04-1035-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%2B%E5%86%B3%E7%AD%96%E3%80%91%E5%8A%A8%E6%80%81%E5%9F%9F%E5%90%8D%E5%93%8D%E5%BA%94%E5%A4%B4CORS%E5%8F%AA%E7%94%B1%E5%90%8E%E7%AB%AF%E5%A4%84%E7%90%86%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-09-04-1035-【网络调整+决策】动态域名响应头CORS只由后端处理记录.md"
sourceSha256: "a4bddce22295c84324ccca8ea28646e20d3c55189629b717fe42dfdd3d2f3537"
sourceSystem: "project-doc"
---

# 【网络调整+决策】动态域名不做 CDN/nginx 响应头与 CORS，统一由后端处理

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-09-04-1035-【网络调整+决策】动态域名响应头CORS只由后端处理记录.md`

> 整理日期：2026-09-04 10:35｜日期依据：文件名日期

时间：2026-09-04 10:35（Asia/Manila）
项目：DBQP / PGServer master（CDN + nginx）
状态：✅ 完成（CF 0 条动态规则；nginx 动态层 CORS 已清除并验证）

## 一、背景与决策

```text
用户明确：目前域名中“动态的”都不需要做响应头、不需要做跨域，
这些统一由后端代码处理（例：pg/server.py 按 Origin 反射 + credentials）。
要求 CF 与 nginx 都不给动态域名（api.* / *-games.* / verify.*）加响应头/CORS。
```

## 二、CF 核查

```text
扫描 22 个静态 zone 的 http_response_headers_transform 与
http_request_cache_settings entrypoint：
命中“动态域名”的规则 = 0；
现有响应头/缓存规则表达式仅匹配 -static.* 与 tada-statics.*（静态域名）。
```

## 三、nginx 调整（备用机 + 宝塔）

```text
文件：
  /www/server/panel/vhost/nginx/common/all-games-proxy.conf
  verify.pgofficialbx.com.conf（两机对应路径）
移除：
  - 所有 add_header Access-Control-*（origin/methods/headers/max-age）
  - 所有 proxy_hide_header Access-Control-*
  - nginx 对动态请求的 OPTIONS 204 拦截（放给后端处理）
保留：HSTS / Alt-Svc / 代理转发逻辑
备份：*.bak-20260904-nocors / bak-20260904-nocors2（可回滚）
验证：nginx -t 通过 + reload；动态响应头改由后端返回
```

## 四、线上验证

```text
带 Origin 请求 api/pg-games/tada-games /health：
  - 不再出现 nginx “*”
  - 返回后端反射：Access-Control-Allow-Origin=<Origin>、
    Allow-Credentials=true、Allow-Headers=后端白名单
verify.pgofficialbx.com OPTIONS -> 由后端响应 204
```

## 五、飞机群通知 message_id

```text
5133 规则确认开始
（汇总/提交结果见文末回写）
```

## 六、本地提交

```text
（提交号文末回写；master 领先 origin/master，未 Push）
```
