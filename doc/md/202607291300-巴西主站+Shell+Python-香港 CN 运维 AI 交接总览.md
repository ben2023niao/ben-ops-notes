---
id: "doc-3e397b64ab90"
title: "香港 CN 运维 AI 交接总览"
date: "2026-07-29T13:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN", "DNS"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-07-29-1300-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91某业务公司%E8%BF%90%E7%BB%B4AI%E4%BA%A4%E6%8E%A5%E6%80%BB%E8%A7%88.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-07-29-1300-【运维记录】某业务公司运维AI交接总览.md"
sourceSha256: "6ae5bc230d880932e3b8b1be9c434162ffba7e52ceb7a957a2a3d8f8bfcc2cc4"
sourceSystem: "project-doc"
---

# 香港 CN 运维 AI 交接总览

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-07-29-1300-【运维记录】某业务公司运维AI交接总览.md`

> 整理日期：2026-07-29 13:00｜日期依据：文件名日期

> 新会话优先读取 `docker/workbench/START_HERE.md`。本文件保留为较长背景材料，当前状态、当前任务、机器矩阵、运行链路和跨工具交接模板以后以 `docker/workbench/` 为准。

## 分支职责

`cn` 是香港入口与云资源运维分支，只允许维护：

- 香港 Nginx 配置。
- AWS ACM、S3、CloudFront。
- Cloudflare DNS。
- PG、PP、PPK、vendor_d、vendor_b 域名池。
- 验证、回滚和运维文档。

不要在本分支恢复游戏后端代码、后端 Docker 镜像、服务发布脚本、ben-bot 或巴西宝塔快照。两台后端由其他团队维护，本分支只通过香港 Nginx 反向代理访问。

## 当前架构

| 角色 | 地址/资源 |
| --- | --- |
| 香港 Nginx | `192.0.2.14` |
| 后端 01 | `192.0.2.18` |
| 后端 02 | `192.0.2.19` |
| AWS 区域 | `ap-east-1` |
| 私有 S3 | `bizops-h5-hk-517506432530` |
| 动态 CloudFront | `E3QV4VIGTRVCVD` / `d1n4qfcp941cy6.cloudfront.net` |
| CloudFront OAC | `bizops-hk-static-oac` |

动态端口：platform-api `9090`、PG `9091`、vendor_b `9093`、PP `9099`、PPK `9098`、vendor_d `9018`。

PG 同时提供固定 API 域名 `api.hkcloudplay01.com` 至 `api.hkcloudplay05.com`，链路为 Cloudflare DNS-only CNAME -> 动态 CloudFront -> 香港 Nginx -> PG `9091`。

vendor_b 保留 `vendor_b-static*` 对外域名，但 CloudFront/S3 与 nginx 兜底均直接读取 vendor_a 的 `vendor_a-statics*` 共享源资源；vendor_b 动态服务独立走 9093，vendor_a 9096 不启用。

## 目录入口

- `docker/workbench/START_HERE.md`：新会话轻量入口。
- `docker/workbench/CURRENT_STATE.md`：当前已验证状态。
- `docker/workbench/CURRENT_TASK.md`：当前任务和最后安全点。
- `docker/workbench/handoff/`：给 Claude Code 或其他执行层的 context、plan、manifest、result 模板。
- `docker/deploy/hongkong/nginx-bizops.conf`：香港 Nginx 主配置。
- `docker/deploy/hongkong/bizops-hongkong-tls.conf`：TLS 公共配置。
- `docker/deploy/hongkong/bizops-hongkong-proxy.conf`：反代公共参数。
- `docker/deploy/hongkong/*.py`：AWS、CloudFront、S3、Cloudflare 工具。
- `docker/conf/domains/*.json`：交给 platform-api 使用的香港域名池。
- `docker/ci/check.py`：Python 编译和范围检查。

## 强制规则

1. 新工具只使用 Python；禁止新增 `.sh`/`.bash`。
2. 不修改或发布后端代码，不操作两台外部后端上的部署。
3. AWS/Cloudflare 变更先做只读检查、备份和单 Zone 灰度，再扩大范围。
4. S3 保持私有，只允许带 OAC 的 CloudFront 分配读取。
5. Cloudflare 指向 CloudFront 时使用 DNS-only CNAME，禁止误开橙云形成双层 CDN。
6. 不提交或输出密码、Token、Access Key、Secret、`.env`、`cf.api`。
7. 不删除 Google 源资源和无 DNS 的回滚资源，除非用户明确批准。
8. 每完成一步立即发飞机群，标题使用 `【香港项目｜任务名称｜进度 X/Y】`；写清对象、数量、验证、影响和下一步。

## 标准验证

```bash
python3 docker/ci/check.py
```

线上只读检查：

```bash
cf-api GET /user/tokens/verify
ONLY_ZONE=hkcloudplay01.com cloudflare-aws-cutover status vendor_b-static
validate-cloudfront-static
nginx -t
```

预期静态验收：50/50 域名成功、10/10 代表文件哈希一致、CORS 为 `*`、带 `x-cache`、S3 直连为 `403`。

## 当前安全边界

- AWS 凭证只在香港服务器 AWS CLI profile 中。
- Cloudflare Token 只在香港服务器 root-only 文件中。
- Git 只保存工具、配置和不含凭证的记录。
- 任何备份目录都应为 root-only，并在文档中记录回滚路径但不记录密钥。

## 当前域名范围

核心/API 共 13 个、动态游戏域名 25 个、静态域名 50 个，总计 88 个精确现用域名。完整清单见：

`docker/doc/2026-07-17-2000-【优化】香港CN五厂商前端可用域名清单.md`

## 最近关键记录

- `docker/workbench/START_HERE.md`
- `2026-07-29-1926-【补静态资源】香港vendor_d客户端资源同步验证记录.md`
- `2026-07-29-1238-【补静态资源】香港PG45与PP客户端资源同步验证记录.md`
- `2026-07-17-1900-【架构改造+网络调整】香港CN五厂商收口与vendor_b-AWS接入完整记录.md`
- `2026-07-17-1500-【架构改造】香港AWS-S3与CloudFront迁移搭建记录.md`
- `2026-07-17-1700-【网络调整】香港AWS-CloudFront灰度切换与回滚验证记录.md`
- `2026-07-17-1109-【架构改造】cn分支精简与香港工具Python化记录.md`
