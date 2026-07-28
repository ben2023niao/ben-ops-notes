---
id: "doc-984b7aa5477f"
title: "hbazuua.cn 腾讯 DNSPod 接管与解析补齐记录"
date: "2026-07-29T17:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "自动化", "CDN", "DNS"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1740-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%2B%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91hbazuua.cn%E8%85%BE%E8%AE%AFDNSPod%E6%8E%A5%E7%AE%A1%E4%B8%8E%E8%A7%A3%E6%9E%90%E8%A1%A5%E9%BD%90%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1740-【网络调整+架构改造】hbazuua.cn腾讯DNSPod接管与解析补齐记录.md"
sourceSha256: "e63c7b44d5f4be40e8823b2e59e701b96d93d8b03d5bd441f796cfb33f018858"
sourceSystem: "project-doc"
---

# hbazuua.cn 腾讯 DNSPod 接管与解析补齐记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1740-【网络调整+架构改造】hbazuua.cn腾讯DNSPod接管与解析补齐记录.md`

> 整理日期：2026-07-29 17:40｜日期依据：文件名日期

环境标签：测试+线上环境

## 1. 文档信息

- 日期：2026-07-29
- 分类：网络调整、架构改造、发布保障
- 域名：`hbazuua.cn`
- 范围：Gname 注册商、腾讯云 DNSPod 权威解析、腾讯 EdgeOne CNAME、证书验证记录、API 补解析、访问验证
- 原则：本文只记录公开解析和验证信息，不记录腾讯云密钥、Telegram Token、账号密码或私钥内容。

## 2. 背景

`hbazuua.cn` 是备案域名替换中的包下载/客户端入口域名，当前主要使用 `package.hbazuua.cn`。

为了后续通过腾讯云 API 管理解析，采取“注册商不转移、DNS 托管切腾讯云 DNSPod”的方案：

- Gname 继续作为域名注册商。
- 腾讯 DNSPod 接管权威解析。
- EdgeOne/CDN 继续负责加速和证书。
- 后续解析新增、修改、删除统一走腾讯云 DNSPod 控制台或 API。

## 3. NS 状态

验证命令：

```bash
dig NS hbazuua.cn +short
dig @8.8.8.8 NS hbazuua.cn +short
```

结果：

```text
a.dnspod.com.
b.dnspod.com.
c.dnspod.com.
```

结论：

- `hbazuua.cn` 的 NS 已经生效到腾讯 DNSPod。
- DNSPod 初始只有默认 NS 记录，缺少业务解析，需要 API 补齐。

## 4. DNSPod API 补齐记录

按 Gname 当前记录，通过腾讯云 DNSPod API 创建 3 条记录。API 调用使用机器人服务器本地容器环境变量中的腾讯云凭证，未输出或记录密钥。

| 主机记录 | 类型 | 记录值 | TTL | 用途 |
| --- | --- | --- | --- | --- |
| `_dnsauth.package` | CNAME | `package.hbazuua.cn.eoacme2.com` | 600 | `package` 域名 EdgeOne 证书验证 |
| `package` | CNAME | `package.hbazuua.cn.eo.dnse4.com` | 600 | 客户端包/下载入口 EdgeOne 域名 |
| `edgeonereclaim` | TXT | `reclaim-kckk0mmzys69mhtthnkscj2vvzeumoei` | 600 | EdgeOne 站点归属验证 |

## 5. 验证结果

权威 DNSPod 验证：

```bash
dig @a.dnspod.com NS hbazuua.cn +short
dig @a.dnspod.com package.hbazuua.cn CNAME +short
dig @a.dnspod.com _dnsauth.package.hbazuua.cn CNAME +short
dig @a.dnspod.com edgeonereclaim.hbazuua.cn TXT +short
```

结果：

```text
NS: a.dnspod.com. / b.dnspod.com. / c.dnspod.com.
package: package.hbazuua.cn.eo.dnse4.com.
_dnsauth.package: package.hbazuua.cn.eoacme2.com.
edgeonereclaim: reclaim-kckk0mmzys69mhtthnkscj2vvzeumoei
```

公共 DNS 抽查：

```bash
dig @8.8.8.8 package.hbazuua.cn CNAME +short
dig @1.1.1.1 package.hbazuua.cn CNAME +short
```

结果均返回：

```text
package.hbazuua.cn.eo.dnse4.com.
```

访问抽查：

| 方式 | 结果 |
| --- | --- |
| 解析 `package.hbazuua.cn` A 记录 | 已返回 EdgeOne 边缘 IP |
| 指定 EdgeOne IP 访问 `https://package.hbazuua.cn/` | `HTTP/2 200` |

说明：

- 本机系统 resolver 曾短暂返回 `Could not resolve host`。
- `dig`、Google DNS、Cloudflare DNS 和指定 EdgeOne IP 访问均已正常。
- 判断为本机系统解析缓存未刷新，不是 DNSPod 记录缺失。

## 6. 飞机群通知

已通知群：稳定备案域名 + 腾讯云原厂。

通知节点：

- `hbazuua.cn` DNSPod 缺少业务记录，准备按最小范围补记录。
- 按 Gname 当前记录补齐 3 条解析。
- 权威 DNS、公共 DNS 和访问链路验证结果。

消息记录：

| 消息 ID | 内容 |
| --- | --- |
| `54007` | `hbazuua.cn` 准备通过 DNSPod API 补记录 |
| `54012` | `hbazuua.cn` DNSPod API 补 3 条记录完成并验证 |

## 7. 后续维护

- `hbazuua.cn` 后续解析统一在腾讯 DNSPod 维护。
- Gname 只保留注册商管理，不再维护解析记录。
- 当前该域名只记录 `package` 相关解析，不复制 `hbabaxb.cn` 的 H5/PC/S3 业务记录。
- 新增包下载或客户端相关子域名时，先在 EdgeOne 创建域名，再补 DNSPod CNAME 和证书验证记录。
- 若本地短时间内查不到记录，优先用 `dig @a.dnspod.com` 和公共 DNS 验证，区分权威记录缺失与本地缓存。
