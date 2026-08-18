---
id: "doc-cb4d9d656026"
title: "线上前端携带用户真实 IP：后端 realip 信任修复与 SSR 遗留"
date: "2026-08-18T16:48:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Docker", "Nginx", "CDN", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-18_1648-%E3%80%90%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E5%89%8D%E7%AB%AF%E6%90%BA%E5%B8%A6%E7%94%A8%E6%88%B7%E7%9C%9F%E5%AE%9EIP-%E5%90%8E%E7%AB%AFrealip%E4%BF%A1%E4%BB%BB%E4%B8%8ESSR%E9%81%97%E7%95%99.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-18_1648-【修复记录】线上前端携带用户真实IP-后端realip信任与SSR遗留.md"
sourceSha256: "832693f7e5ca93b684cfe87fb70958ee1fceac5cdf353b25dae0a7331f3c073d"
sourceSystem: "project-doc"
---

# 线上前端携带用户真实 IP：后端 realip 信任修复与 SSR 遗留

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-18_1648-【修复记录】线上前端携带用户真实IP-后端realip信任与SSR遗留.md`

> 整理日期：2026-08-18 16:48｜日期依据：文件名日期

环境标签：线上环境 / 前端 / 用户IP / nginx realip / SSR

时间：2026-08-18 16:48（Asia/Manila）

## 背景

后端反馈：前端服务器发起的内网请求接口没有携带用户真实 IP，接口拿到的都是内网地址。要求宝塔老前端和新的 nginx 服务器（16.208.38.88）都要处理。

## 链路与根因

- 新服务器：用户 → 16.208.38.88（unified conf `/api` 反代，已带 X-Real-IP / X-Forwarded-For）→ 宝塔内网 203.0.113.1 → 后端 203.0.113.1:8088。
- 宝塔老前端：用户 → CloudFront → 宝塔（extension `00-youdianse-fixed-reverse-proxy.conf` 的 `/api` 反代，已带 X-Forwarded-For）→ 后端。
- 两端前端 nginx 其实都已透传 XFF；根因是**后端 nginx（203.0.113.1:8088，容器 youdianse-main-php-nginx）全站无 `set_real_ip_from` / `real_ip_header`**，PHP 的 REMOTE_ADDR 一直是内网对端 IP（203.0.113.1 / 203.0.113.1）。

## 处理（后端 16.209.16.108）

1. 备份 `/opt/docker-youdianse-php/nginx/default.conf` → `default.conf.bak.realip-20260818_0000`。
2. nginx `server` 块增加：
   - `set_real_ip_from`：203.0.113.1/16、203.0.113.1/8、100.64.0.0/10、138.252.248.139、CloudFront 官方 211 段（从 ip-ranges.json 生成）；
   - `real_ip_header X-Forwarded-For;`
   - `real_ip_recursive on;`
3. `nginx -t` 通过并 reload；验证后用临时 access_log 抓包确认（已移除 debug 日志，realip 保留）。

## 验证

- 公网直连 `h5.yds-pc-h5-01.cc`（新服务器链路）：后端 nginx 解析 REMOTE_ADDR = 请求者真实公网 IP（实测 112.207.100.18）。
- 宝塔老前端 CloudFront 链路：用户请求解析为真实 IP（如 223.88.200.119、IPv6 等）。
- 应用 api_request 日志现在记录真实用户 IP。

## 遗留（需前端配合）

- Nuxt SSR 页面渲染时，容器直接请求 `https://www.youdianse.com/api`（经 CloudFront），未把浏览器请求的用户 IP 透传；构建产物中 `useRequestHeaders` 只转发了 `user-agent`，导致 SSR 类请求后端仍显示服务器出口 IP（16.208.38.88）。
- 精确改法（H5 与 PC 前端仓库同一个文件 `utils/fetch.ts`）：在 `$fetch.create({ headers: {...} })` 中加一行：

  ```ts
  headers: {
    'Content-Type': 'text/plain',
    'deviceType': 'web',
    ...(import.meta.server ? useRequestHeaders(['x-forwarded-for', 'x-real-ip']) : {}),
  },
  ```

- `useRequestHeaders` 为 Nuxt 内置组合式函数，服务端自动取当前请求 header，无需额外依赖/写 node 逻辑。改完提交前端 main 分支，宝塔老 H5/PC 与 16.208.38.88 新 H5/PC 重新发版后彻底解决。
- 已同步通知 `18GAME_ 上线群（正式環境）`。

## 全链路验证结果（2026-08-18 17:10 更新）

用本机真实公网 IP（112.207.100.18）实测：

| 链路 | 后端记录 IP | 状态 |
| --- | --- | --- |
| 浏览器直连 h5.yds-pc-h5-01.cc/api | 112.207.100.18（真实公网 IP） | ✅ 已修复 |
| 请求 H5 页面触发 Nuxt SSR（新服务器） | 16.208.38.88（服务器出口） | ❌ 未修复 |
| 宝塔老前端 www.youdianse.com 页面 SSR | 服务器出口 IP（如 3.1.244.240） | ❌ 未修复 |

原因：线上 H5/PC 容器仍是旧构建（`b1fc14f` / `cbaacc2`），前端仓库尚未提交/发版 SSR 透传改动（构建产物中 `x-forwarded-for` 仅出现在 Nuxt 框架 h3 内部，非前端 fetch 透传）。

结论：浏览器直连链路已彻底解决；SSR 链路需前端按上述 `utils/fetch.ts` 改法提交 main 并发版（宝塔老 H5/PC + 新服务器 H5/PC）后复核。

## 通知与提交

- 每步已发 `18GAME_ 上线群（正式環境）`（步骤 1-3）。
- 本地 Git 已提交（不 Push），commit 信息见提交结果通知。
