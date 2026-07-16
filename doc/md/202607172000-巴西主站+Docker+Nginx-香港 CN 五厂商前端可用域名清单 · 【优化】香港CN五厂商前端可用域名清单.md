---
id: "doc-2e0414788e8c"
title: "香港 CN 五厂商前端可用域名清单 · 【优化】香港CN五厂商前端可用域名清单"
date: "2026-07-17T20:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "Nginx", "CDN", "DNS", "故障排查"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-17-2000-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E9%A6%99%E6%B8%AFCN%E4%BA%94%E5%8E%82%E5%95%86%E5%89%8D%E7%AB%AF%E5%8F%AF%E7%94%A8%E5%9F%9F%E5%90%8D%E6%B8%85%E5%8D%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-17-2000-【优化】香港CN五厂商前端可用域名清单.md"
sourceSha256: "5fb415bb3a5275e20d5319d3eca319513a907ef705e7a44975db858cd7183dd0"
sourceSystem: "project-doc"
---

# 香港 CN 五厂商前端可用域名清单 · 【优化】香港CN五厂商前端可用域名清单

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-17-2000-【优化】香港CN五厂商前端可用域名清单.md`

> 整理日期：2026-07-17 20:00｜日期依据：文件名日期

> 2026-07-18 修正：JILI 保留 `jili-static*` 对外域名，但直接读取 TADA 的共享源资源；JILI 动态后端独立使用 9093。
> 2026-07-18 补充：PG 新增固定 API 域名 `api.hkcloudplay01.com` 至 `api.hkcloudplay05.com`，全部反代到 PG 9091。

## 当前范围

2026-07-17 起，`cn` 环境只启用以下服务：

```text
PG / PP / PPK / PANDA / JILI
platform-api / PG verify
```

静态资源链路为 CloudFront -> 香港私有 S3；动态链路为 CloudFront -> 香港 Nginx -> 两台外部后端。下列精确域名在 Cloudflare 均为 DNS-only CNAME、TTL 60 秒。

## 核心与 API 域名

| 用途 | 域名 | 验收结果 |
| --- | --- | --- |
| platform-api | `api.hkplaycore.com` | 根路径 404，为应用正常响应 |
| platform-api 备用入口 | `games.hkplaycore.com` | 根路径 404，为应用正常响应 |
| PG verify | `verify.hkplaycore.com` | 根路径 200 |
| PG API | `pg-api.hkplaycore.com` | 根路径 200 |
| PG 固定 API 域名 | `api.hkcloudplay01.com` ～ `api.hkcloudplay05.com` | 根路径 200 |
| PP API | `pp-api.hkplaycore.com` | 根路径 403，已到 PP 应用 |
| PPK API | `ppk-api.hkplaycore.com` | 根路径 404，已到 PPK 应用 |
| PANDA API | `panda-api.hkplaycore.com` | 根路径 404，已到 PANDA 应用 |
| JILI API | `jili-api.hkplaycore.com` | `/game-setting/game-info-list` 返回 200 |

## 动态游戏域名

以下每组 `01` 至 `05` 均可用，共 25 个域名：

```text
pg-games.hkcloudplay01.com ～ pg-games.hkcloudplay05.com
pp-games.hkcloudplay01.com ～ pp-games.hkcloudplay05.com
ppk-games.hkcloudplay01.com ～ ppk-games.hkcloudplay05.com
panda-games.hkcloudplay01.com ～ panda-games.hkcloudplay05.com
jili-games.hkcloudplay01.com ～ jili-games.hkcloudplay05.com
```

验收状态：PG 根路径 200；PP 根路径 403；PPK/PANDA 根路径 404；JILI `/game-setting/game-info-list` 返回 200。不同根路径状态是应用自身行为，不是 CDN 或反代故障。

## 静态资源域名

以下 10 个前缀均可搭配 `hkcloudplay01.com` 至 `hkcloudplay05.com`，共 50 个域名：

```text
pg-static
pg3-static
pg4-static
pg5-static
pp-static
ppk-static
panda-static
jili-static
jili-static1
jili-static2
```

组合示例：

```text
pg-static.hkcloudplay01.com ～ pg-static.hkcloudplay05.com
pp-static.hkcloudplay01.com ～ pp-static.hkcloudplay05.com
jili-static1.hkcloudplay01.com ～ jili-static1.hkcloudplay05.com
```

JILI 三组静态资源对应 default、SPECIAL_GAMES_v1、SPECIAL_GAMES_v2。`jili-static*` CloudFront 分配直接读取共享的 `tada-statics*` S3 前缀，nginx 兜底也直接读取 `dbqp-gcs-tada-statics*`；JILI 动态请求使用 `jili-games*` / `jili-api`，由 Nginx 转发至 9093。

## PP 特殊规则

PP 的 5 个静态域名继续支持任意目录下的：

```text
/customizations.info
```

CloudFront Function 返回空文件：HTTP 200、`application/octet-stream`、0 字节，并附带 CORS 响应头。

## 当前验收汇总

| 项目 | 结果 |
| --- | ---: |
| 静态精确 DNS | 50/50 |
| 动态游戏精确 DNS | 25/25 |
| 核心/API 精确 DNS | 13/13 |
| 动态 HTTP 应用验收 | 38/38 |
| 静态 CloudFront 强制解析 | 50/50 |
| Google/AWS 代表文件 SHA-256 | 10/10 |
| 私有 S3 公网直连 | 403 |
| TADA/PLAYSON/Socket 精确 DNS 残留 | 0 |

## 不再提供给前端

以下域名不属于当前 `cn` 范围，精确 DNS 已下线；通过原通配记录到达香港 Nginx 时明确返回 410：

```text
tada-api.hkplaycore.com
tada-games.hkcloudplay01.com ～ tada-games.hkcloudplay05.com
tada-statics.hkcloudplay01.com ～ tada-statics.hkcloudplay05.com
tada-statics1.hkcloudplay01.com ～ tada-statics1.hkcloudplay05.com
tada-statics2.hkcloudplay01.com ～ tada-statics2.hkcloudplay05.com

playson-api.hkplaycore.com
playson-games.hkcloudplay01.com ～ playson-games.hkcloudplay05.com
playson-static.hkcloudplay01.com ～ playson-static.hkcloudplay05.com

socket.hkplaycore.com
```

JDB、G759 也未接入本轮 `cn` 环境。

## 关联文档

- `docker/doc/2026-07-17-1900-【架构改造+网络调整】香港CN五厂商收口与JILI-AWS接入完整记录.md`
- `docker/doc/2026-07-17-1500-【架构改造】香港AWS-S3与CloudFront迁移搭建记录.md`
- `docker/doc/2026-07-17-1700-【网络调整】香港AWS-CloudFront灰度切换与回滚验证记录.md`
