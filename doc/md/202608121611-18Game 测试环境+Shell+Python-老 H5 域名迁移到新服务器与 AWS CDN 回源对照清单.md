---
id: "doc-505dcc5a5d75"
title: "老 H5 域名迁移到新服务器与 AWS CDN 回源对照清单"
date: "2026-08-12T16:11:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "CDN", "DNS", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1611-%E3%80%90%E8%BF%81%E7%A7%BB%2B%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95%E3%80%91%E8%80%81H5%E5%9F%9F%E5%90%8D%E8%BF%81%E7%A7%BB%E5%88%B0%E6%96%B0%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8EAWS-CDN%E5%9B%9E%E6%BA%90%E5%AF%B9%E7%85%A7%E6%B8%85%E5%8D%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1611-【迁移+验证记录】老H5域名迁移到新服务器与AWS-CDN回源对照清单.md"
sourceSha256: "24ee5e0543ee11b06101e8e7b4d1e763ad0e886a351e34f96b806380f1325cb3"
sourceSystem: "project-doc"
---

# 老 H5 域名迁移到新服务器与 AWS CDN 回源对照清单

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608121611-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E8%80%81%20H5%20%E5%9F%9F%E5%90%8D%E8%BF%81%E7%A7%BB%E5%88%B0%E6%96%B0%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8E%20AWS%20CDN%20%E5%9B%9E%E6%BA%90%E5%AF%B9%E7%85%A7%E6%B8%85%E5%8D%95.md)

> 整理日期：2026-08-12 16:11｜日期依据：文件名日期

环境标签：线上环境 / 游点涩 / H5 / 域名迁移 / AWS CDN / nginx

时间：2026-08-12 16:11（Asia/Manila）

## 任务来源

用户要求：

- 把 `线上环境-游点涩-h5-发版`（宝塔 16.208.5.147）里老的 H5 域名和 SSL 证书，逐个迁移到 `线上环境-游点涩-新h5-发版`（16.208.38.88）的纯 H5 conf。
- 迁移一个测试一个：用 hosts 加 IP（本任务用 `--resolve` 等价模拟）验证访问情况、接口、静态资源，结果发群。
- 全部完成后汇总列表，供运维参考在 AWS CDN 里逐个对照修改域名回源。
- 每步操作都发群通知（上线群 + 运维群），最后合并提交本地代码。

## 迁移说明

### 数据源（宝塔 16.208.5.147）

- H5 站点 = 反代 `203.0.113.1:3003`（线上 H5 容器）的站点：
  - `new.youdianse.com.conf`：约 73 个域名（大 H5 站点）
  - `h5.youdianse.com.conf`、`h5.youdianse-main.xyz.conf`（含 h5-001）、`h5.yodianse.com.conf`
- 证书：`*.youdianse.com` 通配（覆盖 youdianse.com 系）、`*.youdianse-main.xyz` 通配、`h5.yodianse.com` 证书副本；其余大量域名在宝塔无独立证书（TLS 由 AWS CDN 承担）。

### 目标（新服务器 16.208.38.88）

- 纯 H5 conf：`30-youdianse-prod-h5.conf`，`server_name` 已扩展为 84 个主机名（3 个 yds-pc-h5 + 81 个老 H5 域名）。
- 证书：复制 `*.youdianse.com` 通配到 `live/youdianse.com/`、`*.youdianse-main.xyz` 到 `live/h5.youdianse-main.xyz/`、`h5.yodianse.com` 到 `live/h5.yodianse.com/`；其余域名 `live/<主机名>` 软链到 `live/youdianse.com`（占位证书，用于直连功能测试；对外 TLS 由 AWS CDN 提供）。
- `nginx -t` 通过并 reload。

## 迁移与验证结果（84 个主机全部通过）

模拟访问方式（等价 hosts 加 IP）：

```bash
curl -sk --resolve <域名>:443:16.208.38.88 https://<域名>/
```

| 域名 | 页面 | 版本 JSON | 静态资源 |
| --- | --- | --- | --- |
（见下方完整清单，全部 `200` / `915a0d3` / `200`）

完整清单：

| 域名 | 页面 | 版本 JSON | 静态资源 |
| --- | --- | --- | --- |
___TABLE___

## AWS CDN 回源对照修改建议

- 上述 84 个主机名全部可回源到 `16.208.38.88`（H5 应用在容器 3003，由 nginx 按 Host 反代）。
- 迁移后老域名对外 TLS 仍由 AWS CDN 终止；CDN 回源如走 HTTPS，需确认回源验证方式（新服务器上非 youdianse 域名当前为占位证书，建议 CDN 回源用 HTTP 或跳过证书校验，或后续按域名补正式证书）。
- `pc.youdianse.com` 未迁入 H5 conf（属 PC 域名，宝塔当前也反代到 H5 容器，如需保持一致可另行加入 PC conf 或按业务确认）。
- `d38owkgqvg83bq.cloudfront.net` 未迁移（静态资源域，非页面入口）。

## 注意事项

- 证书续期：`*.youdianse.com` / `*.youdianse-main.xyz` 目前是从宝塔复制的副本，建议后续在 AWS CDN 回源切换后，对新服务器上用 certbot 重新签发或建立续期任务，并把新域名加入 `youdianse-prod-h5pc-ssl-renew.sh` 的 `DOMAINS`。
- 宝塔老 H5 站点在 AWS CDN 回源全部切换完成前保留，避免切换期间访问中断。
- 后续新增 H5 域名：DNS `h5.域名 A 16.208.38.88` → 在 `30-youdianse-prod-h5.conf` 的 `server_name` 追加 → 保证 `live/<主机名>/` 证书 → `nginx -t && reload`。

## 群通知

每步已同步发送 `18GAME_ 上线群（正式環境）` 与 `18game运维`：步骤 1 方案、步骤 2 盘点清单、步骤 3 测试结果（3 批）、最终汇总与文档。
