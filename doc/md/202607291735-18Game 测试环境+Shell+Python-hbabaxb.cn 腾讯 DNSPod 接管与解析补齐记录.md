---
id: "doc-e72c7197709a"
title: "hbabaxb.cn 腾讯 DNSPod 接管与解析补齐记录"
date: "2026-07-29T17:35:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "自动化", "CDN", "DNS", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1735-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%2B%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91hbabaxb.cn%E8%85%BE%E8%AE%AFDNSPod%E6%8E%A5%E7%AE%A1%E4%B8%8E%E8%A7%A3%E6%9E%90%E8%A1%A5%E9%BD%90%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1735-【网络调整+架构改造】hbabaxb.cn腾讯DNSPod接管与解析补齐记录.md"
sourceSha256: "2352491a28c63fe91395d92b4a1f01037696392462fc903e9700a7838201da58"
sourceSystem: "project-doc"
---

# hbabaxb.cn 腾讯 DNSPod 接管与解析补齐记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1735-【网络调整+架构改造】hbabaxb.cn腾讯DNSPod接管与解析补齐记录.md`

> 整理日期：2026-07-29 17:35｜日期依据：文件名日期

环境标签：测试+线上环境

## 1. 文档信息

- 日期：2026-07-29
- 分类：网络调整、架构改造、发布保障
- 域名：`hbabaxb.cn`
- 范围：Gname 注册商、腾讯云 DNSPod 权威解析、腾讯 EdgeOne CNAME、证书验证记录、API 补解析、访问验证
- 原则：本文只记录公开解析和验证信息，不记录腾讯云密钥、Telegram Token、账号密码或私钥内容。

## 2. 背景

`hbabaxb.cn` 原解析维护在 Gname。为了后续可以通过腾讯云 API 自动管理解析记录，采取“注册商不转移、DNS 托管切腾讯云 DNSPod”的方案：

- Gname 继续作为域名注册商。
- 腾讯 DNSPod 接管权威解析。
- EdgeOne/CDN 仍使用腾讯云已有加速域名和 CNAME。
- 后续解析新增、修改、删除统一走腾讯云 DNSPod 控制台或 API。

## 3. NS 切换

切换目标：

| 类型 | 值 |
| --- | --- |
| 权威 DNS | DNSPod |
| NS 1 | `a.dnspod.com.` |
| NS 2 | `b.dnspod.com.` |
| NS 3 | `c.dnspod.com.` |

验证记录：

```bash
dig @8.8.8.8 NS hbabaxb.cn +short
```

公共 DNS 已返回：

```text
a.dnspod.com.
b.dnspod.com.
c.dnspod.com.
```

说明：

- 本地路由器 DNS 曾短暂返回旧 NS：`a.share-dns.com.`、`b.share-dns.net.`。
- 该现象属于递归 DNS 缓存传播，不代表 DNSPod 未接管。
- 需要以 DNSPod 权威查询和主流公共 DNS 查询作为判断依据。

## 4. DNSPod API 补齐记录

通过腾讯云 DNSPod API 创建 15 条记录。API 调用使用机器人服务器本地容器环境变量中的腾讯云凭证，未输出或记录密钥。

| 主机记录 | 类型 | 记录值 | TTL | 用途 |
| --- | --- | --- | --- | --- |
| `_dnsauth.test-pc-s3` | CNAME | `test-pc-s3.hbabaxb.cn.eoacme2.com` | 600 | PC 静态域名证书验证 |
| `_dnsauth.test-h5-s3` | CNAME | `test-h5-s3.hbabaxb.cn.eoacme2.com` | 600 | H5 静态域名证书验证 |
| `test-pc-s3` | CNAME | `test-pc-s3.hbabaxb.cn.eo.dnse4.com` | 600 | 测试 PC 前端静态资源 CDN |
| `test-h5-s3` | CNAME | `test-h5-s3.hbabaxb.cn.eo.dnse4.com` | 600 | 测试 H5 前端静态资源 CDN |
| `main-s3` | CNAME | `main-s3.hbabaxb.cn.eo.dnse4.com` | 600 | 线上后端 S3 资源预备 CDN |
| `test-s3` | CNAME | `test-s3.hbabaxb.cn.eo.dnse4.com` | 600 | 测试后端 S3 资源预备 CDN |
| `_dnsauth.main-h5` | CNAME | `main-h5.hbabaxb.cn.eoacme2.com` | 600 | 线上 H5 证书验证 |
| `_dnsauth.test-h5` | CNAME | `test-h5.hbabaxb.cn.eoacme2.com` | 600 | 测试 H5 证书验证 |
| `_dnsauth.test-pc` | CNAME | `test-pc.hbabaxb.cn.eoacme2.com` | 600 | 测试 PC 证书验证 |
| `_dnsauth.test` | CNAME | `test.hbabaxb.cn.eoacme2.com` | 600 | 测试入口证书验证 |
| `main-h5` | CNAME | `main-h5.hbabaxb.cn.eo.dnse4.com` | 600 | 线上 H5 EdgeOne 入口 |
| `test-h5` | CNAME | `test-h5.hbabaxb.cn.eo.dnse4.com` | 600 | 测试 H5 EdgeOne 入口 |
| `test-pc` | CNAME | `test-pc.hbabaxb.cn.eo.dnse4.com` | 600 | 测试 PC EdgeOne 入口 |
| `test` | CNAME | `test.hbabaxb.cn.eo.dnse4.com` | 600 | 测试聚合入口 |
| `edgeonereclaim` | TXT | `reclaim-b74s3cl4y586malv55pq7jfbq14zjc5c` | 600 | EdgeOne 站点归属验证 |

## 5. 验证结果

权威 DNSPod 验证：

```bash
dig @a.dnspod.com NS hbabaxb.cn +short
dig @a.dnspod.com test-h5-s3.hbabaxb.cn CNAME +short
dig @a.dnspod.com test-pc-s3.hbabaxb.cn CNAME +short
dig @a.dnspod.com edgeonereclaim.hbabaxb.cn TXT +short
```

结果：

```text
NS: a.dnspod.com. / b.dnspod.com. / c.dnspod.com.
test-h5-s3: test-h5-s3.hbabaxb.cn.eo.dnse4.com.
test-pc-s3: test-pc-s3.hbabaxb.cn.eo.dnse4.com.
edgeonereclaim: reclaim-b74s3cl4y586malv55pq7jfbq14zjc5c
```

访问抽查：

| URL | 结果 |
| --- | --- |
| `https://test-h5-s3.hbabaxb.cn/version.txt` | `HTTP/2 200` |
| `https://test-pc-s3.hbabaxb.cn/version.txt` | `HTTP/2 200` |
| `https://test-pc.hbabaxb.cn/` | `HTTP/2 200` |

说明：

- 第一次 PC CDN HEAD 请求曾短暂超时，改用 IPv4 重试正常。
- 判断为边缘节点或递归缓存传播抖动，不是 DNSPod 记录缺失。

## 6. 飞机群通知

已通知群：稳定备案域名 + 腾讯云原厂。

通知节点：

- NS 切换操作步骤。
- NS 切换验证和记录缺失风险。
- DNSPod API 补 15 条记录完成。
- H5/PC 静态 CDN 与 PC 页面访问抽查完成。

消息记录：

| 消息 ID | 内容 |
| --- | --- |
| `53955` | `hbabaxb.cn` 切 DNSPod 托管步骤 |
| `53991` | NS 切换验证和 DNSPod 记录缺失风险 |
| `54003` | DNSPod API 补 15 条记录完成 |
| `54004` | H5/PC 静态 CDN 与 PC 页面访问抽查完成 |

## 7. 后续维护

- `hbabaxb.cn` 后续解析统一在腾讯 DNSPod 维护。
- Gname 只保留注册商管理，不再维护解析记录。
- 新增 EdgeOne 域名后，应同步新增主 CNAME、`_dnsauth` CNAME 和必要的 `edgeonereclaim` TXT。
- 修改解析前先查询 DNSPod 当前记录，避免重复创建或覆盖已有业务记录。
- 若本地短时间内查不到记录，优先用 `dig @a.dnspod.com` 和公共 DNS 验证，区分权威记录缺失与本地缓存。
