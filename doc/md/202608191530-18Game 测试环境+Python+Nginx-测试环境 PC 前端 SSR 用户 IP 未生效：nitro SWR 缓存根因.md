---
id: "doc-9ecaaf64ac7d"
title: "测试环境 PC 前端 SSR 用户 IP 未生效：nitro SWR 缓存根因"
date: "2026-08-19T15:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Nginx", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-19_1530-%E3%80%90%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95PC%E5%89%8D%E7%AB%AFSSR%E7%94%A8%E6%88%B7IP%E6%9C%AA%E7%94%9F%E6%95%88-nitroSWR%E7%BC%93%E5%AD%98%E6%A0%B9%E5%9B%A0.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-19_1530-【排查记录】测试PC前端SSR用户IP未生效-nitroSWR缓存根因.md"
sourceSha256: "36048db0ae096eb6d99e2f343060f6b8c3ae2d6f40e0392a42313f78d5dc3b76"
sourceSystem: "project-doc"
---

# 测试环境 PC 前端 SSR 用户 IP 未生效：nitro SWR 缓存根因

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608191530-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BPython%2BNginx-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%20PC%20%E5%89%8D%E7%AB%AF%20SSR%20%E7%94%A8%E6%88%B7%20IP%20%E6%9C%AA%E7%94%9F%E6%95%88%EF%BC%9Anitro%20SWR%20%E7%BC%93%E5%AD%98%E6%A0%B9%E5%9B%A0.md)

> 整理日期：2026-08-19 15:30｜日期依据：文件名日期

环境标签：测试环境 / PC 前端 / SSR / 用户IP / nitro SWR

时间：2026-08-19 15:30（Asia/Manila）

## 背景

前端反馈：PC/H5 均发布了 SSR 加用户 IP 的代码，H5 正常，PC 接口仍拿到内网 IP。Ben 要求排查测试环境 PC 前端/后端代码情况。

## 排查过程与证据

1. PC 测试容器（`youdianse_pc_dev_18game_pc_client_3004`）运行构建 `3f948c8`（dev 分支），version.json 确认；构建产物中已包含 `resolveClientIp` + `x-forwarded-for/x-real-ip` 透传代码，与 H5 构建（8bf6650）完全一致。
2. 后端 nginx（admin.youdianse-test.xyz）访问日志：PC SSR 请求来自 203.0.113.1（PC 容器）、UA=node、**未携带任何 X-Forwarded-For**；H5 SSR 请求来自 203.0.113.1（H5 容器）且带了用户 IP（后端 api_request 记录为我的真实公网 IP）。
3. 测试 PC 与 H5 的 nginx vhost 的 `location /` 均设置了 `X-Real-IP $remote_addr` 与 `X-Forwarded-For $proxy_add_x_forwarded_for`，无差异。
4. 决定性对照：请求 PC **404/详情等非 SWR 路由** → SSR 请求后端记录真实用户 IP（112.209.180.138）；请求 PC **首页**（SWR 路由）→ SSR 请求后端记录容器 IP（203.0.113.1）。
5. PC 构建 nitro routeRules：`/`、`/game`、`/message`、`/community` 均配置 `"swr": 300`（含 `cache: { swr: true, maxAge: 300 }`）；H5 构建无 `swr: true`。PC 容器日志有 `[cache] SWR handler error`。

## 根因

PC 前端在 nuxt.config 的 `routeRules` 中对首页/游戏/消息/社区等路由启用了 **nitro SWR（stale-while-revalidate，300s）缓存**。SWR 的渲染与后台重新校验流程脱离了携带用户 IP 的请求上下文，`useRequestHeaders` 取不到 `x-real-ip`，SSR 内部请求未设置 `x-forwarded-for` → 后端记录到的是 PC 容器内网 IP（203.0.113.1）。H5 未启用 SWR，SSR 始终在请求上下文执行，因此正常。

## 处理建议（前端）

1. PC `nuxt.config` 的 `routeRules` 去掉 `swr`（或把需要真实用户 IP 的页面移出 SWR），重新发测试与线上；
2. 或保留 SWR，但把依赖用户 IP 的数据改为客户端请求。

## 影响范围

- 测试环境 PC（本次定位）。
- 线上新 PC（16.208.38.88）为同一前端代码（同样带 SWR routeRules），线上 PC SSR 也存在相同问题（此前验证线上 PC SSR 记录 16.208.38.88），前端去 SWR 后需一并发版。

## 通知与提交

- 根因已发 `18game运维` 与 `18GAME_ 上线群（正式環境）`。
- 本地 Git 已提交（不 Push），commit 信息见提交结果通知。
