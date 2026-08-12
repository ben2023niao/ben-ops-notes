---
id: "doc-276383b219e7"
title: "老 H5 域名 UA 适配（PC/H5）试点"
date: "2026-08-12T17:12:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Nginx", "CDN", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1712-%E3%80%90%E9%85%8D%E7%BD%AE%E9%83%A8%E7%BD%B2%2B%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95%E3%80%91%E8%80%81H5%E5%9F%9F%E5%90%8DUA%E9%80%82%E9%85%8DPC-H5%E8%AF%95%E7%82%B9.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1712-【配置部署+验证记录】老H5域名UA适配PC-H5试点.md"
sourceSha256: "121bb2aa9c82f427c77a0c19c842ccc9a9c810f1452bf1b8fbbccd453a1e3a87"
sourceSystem: "project-doc"
---

# 老 H5 域名 UA 适配（PC/H5）试点

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1712-【配置部署+验证记录】老H5域名UA适配PC-H5试点.md`

> 整理日期：2026-08-12 17:12｜日期依据：文件名日期

环境标签：线上环境 / 游点涩 / nginx / UA 识别 / 反向代理 / 老 H5 域名

时间：2026-08-12 17:12（Asia/Manila）

## 任务来源

用户要求（含群内确认）：

- 老宝塔 H5 域名 `shouyek.com`、`shyssjt.com`、`syyhslzp.com`（AWS CDN 回源已对应改成 01/02/03）。
- 实现：电脑访问 → 反向代理到 PC；手机访问 → 反向代理到 H5；域名 URL 不变、不跳转。
- 先做 3 个试点域名验证，没问题后再逐个推广到其他老域名。
- 每步操作都发群通知（上线群 + 运维群），完成后验证、汇总文档、发群并提交代码。

## 实现

- 新增 `50-youdianse-prod-old-h5-ua-proxy.conf`（16.208.38.88 `/etc/nginx/conf.d/`，后已合并进 `20-youdianse-prod-unified.conf`）：
  - `server_name shouyek.com shyssjt.com syyhslzp.com;`
  - `location /` 内按 `$h5pc_device`（UA 判断）选择后端：
    - 手机（`h5`）→ `203.0.113.1:3003`（H5 容器）
    - 电脑（默认 `pc`）→ `203.0.113.1:3004`（PC 容器）
  - 保留 `/api|/channel|/customer` → `www.youdianse.com`、`/uploads` → CloudFront、`sw.js`/旧 workbox/`/images/aside` 兜底。
- 从 `30-youdianse-prod-h5.conf` 的 `server_name` 移除这 3 个域名（避免与 UA 代理 conf 冲突），其余 81 个 H5 主机不变。
- `nginx -t` 通过并 reload。

## 验证结果（curl --resolve 模拟，均通过）

| 域名 | 电脑 UA | 手机 UA |
| --- | --- | --- |
| shouyek.com | 游点涩 pc（3004），页面 200 | 游点涩 h5（3003），页面 200 |
| shyssjt.com | 游点涩 pc（3004），页面 200 | 游点涩 h5（3003），页面 200 |
| syyhslzp.com | 游点涩 pc（3004），页面 200 | 游点涩 h5（3003），页面 200 |

对照组：`118acs2.com` 仍为纯 H5（两种 UA 均返回 H5 版本 `915a0d3`），未受影响。

## 推广方式

后续把其他老 H5 域名加入 `50-youdianse-prod-old-h5-ua-proxy.conf` 的 `server_name`（并保证 `live/<主机名>/` 证书存在），即可逐个适配 PC/H5。

## 群通知

已同步发送 `18GAME_ 上线群（正式環境）` 与 `18game运维`：步骤 1 方案、步骤 2 部署验证、最终汇总。

## 结论

- 3 个试点老域名已完成 UA 识别反向代理：电脑→PC、手机→H5，域名不变。
- 验证全部通过，可继续按此模式推广到其他老 H5 域名。
