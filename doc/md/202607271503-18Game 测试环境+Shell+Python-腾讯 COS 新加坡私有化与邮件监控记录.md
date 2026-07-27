---
id: "doc-a6244700569f"
title: "腾讯 COS 新加坡私有化与邮件监控记录"
date: "2026-07-27T15:03:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "监控告警", "自动化", "CDN", "DNS"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-27_1503-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%2B%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E8%85%BE%E8%AE%AFCOS%E6%96%B0%E5%8A%A0%E5%9D%A1%E7%A7%81%E6%9C%89%E5%8C%96%E4%B8%8E%E9%82%AE%E4%BB%B6%E7%9B%91%E6%8E%A7.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-27_1503-【架构改造+网络调整】腾讯COS新加坡私有化与邮件监控.md"
sourceSha256: "c769ca4277be592aab28feee08b06d14b6427bdfe1cf2fd05bd45d74d565e282"
sourceSystem: "project-doc"
---

# 腾讯 COS 新加坡私有化与邮件监控记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-27_1503-【架构改造+网络调整】腾讯COS新加坡私有化与邮件监控.md`

> 整理日期：2026-07-27 15:03｜日期依据：文件名日期

环境标签：测试+线上环境

## 1. 文档信息

- 日期：2026-07-27
- 范围：游点涩 H5/PC 测试静态资源、测试 uploads、线上 S3 首次同步、Gname 解析通知、腾讯短信权限检查、ben-bot 邮件监控与同步按钮
- 原则：本文只记录可公开运维信息，不记录云密钥、服务器密码、Telegram Token、群 ID、邮箱密码等敏感内容。

## 2. COS 当前状态

| 用途 | 原广州桶 | 新加坡桶 | 区域 | 公网直连 |
| --- | --- | --- | --- | --- |
| 测试 H5 静态资源 | `18game-nuxt-static-test-h5-1450169938` 已清理 | `18game-nuxt-static-test-h5-sg-1450169938` | `ap-singapore` | 私有，直连返回 403 |
| 测试 PC 静态资源 | `18game-nuxt-static-test-pc-1450169938` 已清理 | `18game-nuxt-static-test-pc-sg-1450169938` | `ap-singapore` | 私有，直连返回 403 |
| 测试业务 uploads | `18game-storage-dev-uploads-1450169938` 已清理 | `18game-storage-dev-uploads-sg-1450169938` | `ap-singapore` | 私有，直连返回 403 |
| 线上业务资源 | AWS `18game-prod` | `18game-storage-prod-uploads-sg-1450169938` | `ap-singapore` | 私有，直连返回 403 |

已完成：

- H5 静态资源从广州桶同步到新加坡桶。
- PC 静态资源从广州桶同步到新加坡桶。
- 测试后端 uploads 从 AWS 源桶同步到腾讯新加坡 uploads 桶。
- 新加坡桶 ACL 已设置为私有，验证公网直连为 403，签名访问可读。
- `test-s3.hbabaxb.cn` 已创建 EdgeOne 加速配置，并修正为 S3-compatible 私有源站。
- `test-s3.hbabaxb.cn` 已部署 EdgeOne 免费证书，正常 HTTPS 访问验证通过。
- 已通知 `稳定备案域名+腾讯云原厂` 群：Gname 需要添加 `test-s3` CNAME 到 EdgeOne 分配的 CNAME。
- H5/PC 测试发版脚本的腾讯 COS 默认目标已调整为新加坡静态桶，避免后续发版继续写广州桶。
- 2026-07-28 已按确认清理 3 个广州旧桶，复查均为不存在或不可访问。
- 2026-07-28 晚间发现测试 H5/PC 页面发布产物仍写入旧广州 COS 原始域名，广州桶清理后导致 `_nuxt` 静态资源 404/CORS；已将测试 H5/PC 机器人发版环境统一改为 `NUXT_PUBLIC_CDN_URL=https://test-s3.hbabaxb.cn`，并把发版阶段的 COS 同步目标切到 `18game-storage-dev-uploads-sg-1450169938`，确保页面引用的 `_nuxt` 文件可通过 CDN 域名访问，COS 原始域名继续私有不可直连。
- 2026-07-28 复查发现项目内置 `.env` 已有 `NUXT_PUBLIC_CDN_URL` 时，旧发布脚本不会覆盖，导致页面仍可引用 AWS S3；已改为只要机器人发布环境指定静态 CDN，就强制覆盖该键，避免 H5/PC 发版后继续走 AWS 静态域名。
- 2026-07-28 按最新要求拆分测试前端静态资源：H5 改用 `test-h5-s3.hbabaxb.cn` + `18game-nuxt-static-test-h5-sg-1450169938`，PC 改用 `test-pc-s3.hbabaxb.cn` + `18game-nuxt-static-test-pc-sg-1450169938`；后端 uploads 和客户端包继续使用现有 AWS 老 S3，不切腾讯。
- 2026-07-28 已创建 `test-h5-s3.hbabaxb.cn`、`test-pc-s3.hbabaxb.cn` EdgeOne 域名，主 CNAME 已生效；HTTPS 免费证书文件验证失败，需先在 Gname 添加 `_dnsauth` CNAME 后再发版切换页面资源。
- 2026-07-28 Gname 补充 `_dnsauth.test-h5-s3`、`_dnsauth.test-pc-s3` 后，EdgeOne 免费证书验证通过并完成显式绑定；随后重发 H5 `8f7eed7`、PC `857966e`，构建产物分别双推 AWS 前端桶和腾讯新加坡私有前端桶。

## 3. 域名解析要求

Gname 手动解析建议：

| 主机记录 | 类型 | 记录值 | 用途 |
| --- | --- | --- | --- |
| `test-h5-s3` | CNAME | `test-h5-s3.hbabaxb.cn.eo.dnse4.com` | 测试 H5 前端静态资源 |
| `test-pc-s3` | CNAME | `test-pc-s3.hbabaxb.cn.eo.dnse4.com` | 测试 PC 前端静态资源 |
| `_dnsauth.test-h5-s3` | CNAME | `test-h5-s3.hbabaxb.cn.eoacme2.com` | EdgeOne 免费证书 DNS 验证 |
| `_dnsauth.test-pc-s3` | CNAME | `test-pc-s3.hbabaxb.cn.eoacme2.com` | EdgeOne 免费证书 DNS 验证 |
| `main-s3` | CNAME | `main-s3.hbabaxb.cn.eo.dnse4.com` | 线上后端 uploads/package/app 等 S3 资源 |

要求：

- COS 桶保持私有，不允许公网直连。
- 前端和后端展示域名走 CDN/EdgeOne，不走 COS 原始域名。
- DNS 添加后需验证 CNAME 生效、CDN HTTPS 可访问、COS 原始域名仍不可公开访问。

## 4. 线上 S3 处理状态

已确认线上后端环境当前使用 AWS S3：

| 项 | 当前值 |
| --- | --- |
| AWS 区域 | `ap-northeast-3` |
| AWS Bucket | `18game-prod` |
| 当前展示域名 | AWS CloudFront 域名 |

当前阻塞：

- 线上后端 `.env.prod` 中的 AWS 用户可读取配置，但对 `18game-prod` 执行 `ListBucket` 返回权限不足，不能用于全量迁移。
- 运维 S3 管理账号已验证可列 `18game-prod`，用于本次只读拉取源桶对象。

已完成：

1. 新建线上腾讯 COS 新加坡私有桶 `18game-storage-prod-uploads-sg-1450169938`。
2. 桶 ACL 设置为私有，临时对象公网直连验证返回 403。
3. 创建 EdgeOne 加速域名 `main-s3.hbabaxb.cn`，源站为腾讯新加坡 COS 私有桶，`PrivateAccess=on`。
4. 已通知 Gname 解析 `main-s3` CNAME 到 `main-s3.hbabaxb.cn.eo.dnse4.com`。
5. Gname CNAME 已生效，EdgeOne 免费证书已部署，`https://main-s3.hbabaxb.cn/` 根路径返回 COS 私有桶 403，证书链正常。
6. AWS `18game-prod` 到腾讯新加坡 COS 的全量同步已改用线上后端服务器上的 `rclone` 执行，避免本地链路拉取大文件过慢。
7. 已明确 2026-07-27 本次不修改线上后端 `.env.prod` 展示域名，线上仍继续走现有 AWS CloudFront 域名。
8. 抽样发现 COS 类型源站未保存 `PrivateParameters` 时 CDN 访问对象仍为 403；已改为 EdgeOne S3-compatible 私有源站，补齐 `SignatureVersion=v4`、`Region=ap-singapore` 和本地密钥参数，验证图片 GET 返回 200。

同步记录：

| 项 | 内容 |
| --- | --- |
| 同步服务器 | 线上后端服务器 |
| 源 | AWS S3 `18game-prod`，区域 `ap-northeast-3` |
| 目标 | 腾讯 COS `18game-storage-prod-uploads-sg-1450169938`，区域 `ap-singapore` |
| 工具 | `rclone copy`，S3 到 TencentCOS |
| 规模 | 首次同步最终约 670.139GB、230960 个传输对象 |
| 日志 | `/opt/docker-youdianse-php/runtime/s3-migrate/rclone_prod_to_cos_sg.log.rclone` |
| 状态 | 已完成；2026-07-28 03:36 CST 传输完成，进程已退出 |

说明：

- `rclone copy` 会边扫描边传输，源桶对象很多时，总量会从约 585GB 持续上涨到 670GB。
- 日志中百分比显示 100% 后仍可能继续发现对象，因此 ETA 会反复显示十几到几十秒，不代表进程卡住。
- 2026-07-28 多次检查进程 I/O、CPU 和日志时间戳均在变化；03:36 CST 最终传输完成，临时 rclone 配置文件已删除。

已通过 `main-s3.hbabaxb.cn` GET 验证的样本：

| 对象 | CDN 状态 |
| --- | --- |
| `uploads/2025-09-22/ac5642cad329b203b22fbd6d64837e35_origin.webp` | `200 image/webp` |
| `uploads/2025-09-22/b05aa371e5c0f6b934f7bb830d7edca1_large.webp` | `200 image/webp` |
| `uploads/2025-09-22/b60ad210c8f2e0e97df715e569df4aa5.jpg` | `200 image/jpeg` |
| `uploads/2025-09-22/afda1bab2cdd22b81cf8af39d3e26aad.jpg` | `200 image/jpeg` |
| `uploads/2026-07-24/ff8ec6559ec51dac889bd3efcd38c36f.jpeg` | `200 image/jpeg`，HTTPS 证书校验通过 |
| `uploads/2026-07-23/f35f496f05eccfe678a9cc91af295700.jpg` | `200 image/jpeg`，HTTPS 证书校验通过 |
| `uploads/2026-07-23/ffd4188efba6b67ffa78a489df619ae7.jpg` | `200 image/jpeg`，HTTPS 证书校验通过 |

同对象 COS 原始域名保持 `403 application/xml`，符合私有桶要求。

已通过 `test-s3.hbabaxb.cn` GET 验证的样本：

| 对象 | CDN 状态 |
| --- | --- |
| `uploads/2025-09-10/09f76503dcc97bb5c6985882a3ae141d.jpg` | `200 image/jpeg`，HTTPS 证书校验通过 |
| `uploads/2025-09-10/13a4ba9747fa3cbe4f10c5bf7f2a305e.png` | `200 image/png` |
| `uploads/2025-09-10/7e2e9dc4427a176693a03610c4b2688c.jpg` | `200 image/jpeg` |

`test-s3` 同对象 COS 原始域名保持 `403 application/xml`，符合私有桶要求。

后续步骤：

1. 保持线上后端展示域名不变；`main-s3.hbabaxb.cn` 仅作为本次同步验证和后续切换预备域名。
2. 后续可通过 ben-bot `线上后台-S3同步` 按钮执行增量同步。

## 5. ben-bot S3 同步按钮

已新增两个机器人按钮：

| 按钮 | 脚本 | 动作 |
| --- | --- | --- |
| `测试后台-S3同步` | `测试环境-游点涩后台-s3-同步/sync_test_backend_s3.py` | AWS 测试后台桶增量复制到腾讯新加坡 uploads 桶 |
| `线上后台-S3同步` | `线上环境-游点涩后台-s3-同步/sync_prod_backend_s3.py` | AWS 线上桶 `18game-prod` 增量复制到腾讯新加坡业务资源桶 |

按钮行为：

- 使用 `rclone copy`，只做增量复制，不删除源桶或目标桶对象。
- 执行时按步骤通知机器人已记录的全部飞机群，并 @ 运维人员。
- 云密钥只写在 ben-bot 服务器本地 `.env`，不进入 Git 和文档。
- 线上按钮只做同步，不修改后端 `.env.prod` 或数据库展示域名配置。
- 2026-07-28 已重建 ben-bot，同步按钮日志默认改为低噪声，避免一次同步刷大量逐文件日志。

## 6. 广州旧 COS 清理

已清理对象：

| 桶 | 清理前规模 | 复查结果 |
| --- | --- | --- |
| `18game-nuxt-static-test-h5-1450169938` | 约 2355 个对象、45MB | 不存在或不可访问 |
| `18game-nuxt-static-test-pc-1450169938` | 约 4273 个对象、65MB | 不存在或不可访问 |
| `18game-storage-dev-uploads-1450169938` | 约 39148 个对象、9.6GB | 不存在或不可访问 |

清理说明：

- 清理前已确认 H5/PC 发版默认腾讯 COS 目标为新加坡桶。
- 清理过程已按步骤通知全部已记录飞机群。
- 新加坡 COS 桶和 EdgeOne 域名未受影响。

## 7. 腾讯短信权限检查

已完成：

- 腾讯 CAM 子用户已增加 `ReadOnlyAccess`。
- 重新调用短信接口后，不再是权限拒绝，说明只读权限已生效。

当前还缺：

- 短信状态拉取接口需要 `SmsSdkAppId`。
- 本地与已检查环境中暂未找到短信应用 ID，无法继续拉取风控/回执详情。

后续需要：

- 在腾讯云短信控制台确认短信应用 ID。
- 将短信应用 ID 以非代码密钥方式配置到机器人或巡检脚本。
- 有风控、失败回执或异常状态时，发送到全部已记录运维群，并 @ 运维人员。

## 8. 腾讯云通知转发

目标：

- 腾讯云账号内各类消息通知都要转发到机器人已记录的全部飞机群。
- 群通知中需要 @ 运维人员。
- 不只覆盖短信风控，也覆盖费用、备案、COS、CDN、EdgeOne、账号安全等腾讯云消息中心可订阅通知。

当前实现方式：

- `ben-bot` 已新增 IMAP 邮件监控定时任务。
- 腾讯云消息中心需要把各产品通知渠道订阅到指定通知邮箱。
- 该通知邮箱配置到 `ben-bot` 后，新邮件会自动转发到全部已记录群并 @ 运维人员。

腾讯云侧需要配置：

1. 进入腾讯云控制台消息中心。
2. 在订阅管理中，把需要关注的产品通知类型勾选邮件渠道。
3. 在消息接收管理中确认通知邮箱为机器人监控邮箱。
4. 费用、到期、回收、安全、备案、COS、CDN、EdgeOne、短信等通知均应覆盖。

机器人侧状态：

- 代码能力已上线。
- 当前未发现 IMAP 邮箱参数，任务默认关闭。
- 配置 IMAP 后设置 `BEN_BOT_MAIL_MONITOR_ENABLED=1` 即可启用。

## 9. ben-bot 邮件监控

本次新增 `ben-bot` 邮件定时任务能力：

- 默认关闭，避免未配置邮箱时误触发。
- 通过 IMAP 轮询新邮件。
- 首次启用默认只记录当前最新 UID，不转发历史邮件。
- 后续发现新邮件时，自动转发到机器人已记录的全部群，并 @ 运维人员。
- 只转发邮件发件人、时间、主题和内容摘要，不转发邮箱密码或机器人密钥。

配置变量：

| 变量 | 说明 |
| --- | --- |
| `BEN_BOT_MAIL_MONITOR_ENABLED` | `1/true/on` 时启用 |
| `BEN_BOT_MAIL_POLL_INTERVAL` | 轮询间隔，最低 60 秒，默认 180 秒 |
| `BEN_BOT_MAIL_IMAP_HOST` | IMAP 服务器 |
| `BEN_BOT_MAIL_IMAP_PORT` | IMAP SSL 端口，默认 993 |
| `BEN_BOT_MAIL_USERNAME` | 邮箱账号 |
| `BEN_BOT_MAIL_PASSWORD` | 邮箱密码或应用专用密码 |
| `BEN_BOT_MAIL_FOLDER` | 邮箱目录，默认 `INBOX` |
| `BEN_BOT_MAIL_MAX_PER_POLL` | 单次最多转发邮件数，默认 10，最大 30 |
| `BEN_BOT_MAIL_FORWARD_EXISTING` | 是否首次转发历史邮件，默认关闭 |
| `BEN_BOT_MAIL_STATE_PATH` | 状态文件路径，默认在机器人 upload 数据目录 |

启用建议：

1. 先在服务器 `.env` 或安全配置中写入 IMAP 参数。
2. 设置 `BEN_BOT_MAIL_MONITOR_ENABLED=1`。
3. 重建并启动 `ben-bot`。
4. 发一封测试邮件，确认全部群收到通知并 @ 运维人员。

## 10. 测试 H5/PC 构建资源双推

调整结果：

- 测试 H5/PC 发版不再依赖 AWS 桶到腾讯桶的异步同步作为前端发布链路。
- 每次前端 Docker build 完成 Nuxt 构建后，直接把 `.output/public` 同步到 AWS S3 和腾讯新加坡 COS。
- H5 AWS 公开桶：`18game-nuxt-static-test-h5`，区域：`ap-southeast-1`，桶域名：`https://18game-nuxt-static-test-h5.s3.ap-southeast-1.amazonaws.com`。
- H5 腾讯新加坡私有桶：`18game-nuxt-static-test-h5-sg-1450169938`，区域：`ap-singapore`，展示域名：`https://test-h5-s3.hbabaxb.cn`。
- PC AWS 公开桶：`18game-nuxt-static-test-pc`，区域：`ap-southeast-1`，桶域名：`https://18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com`。
- PC 腾讯新加坡私有桶：`18game-nuxt-static-test-pc-sg-1450169938`，区域：`ap-singapore`，展示域名：`https://test-pc-s3.hbabaxb.cn`。
- 发布脚本会强制覆盖项目 `.env` 中已有的 `NUXT_PUBLIC_CDN_URL`，避免旧 AWS/广州 COS 地址残留。
- 镜像结构版本已升级到 `tooling-v13-cdn-override`，同一 Git 版本也会重新构建，确保新 CDN 配置生效。
- 2026-07-28 已再次发布 H5 `8f7eed7`、PC `857966e`，两次发布日志均显示 AWS S3 与腾讯新加坡 COS 同步成功。
- 2026-07-28 已将后续机器人发版配置改为：H5 同步到 H5 新加坡桶并展示 `test-h5-s3.hbabaxb.cn`；PC 同步到 PC 新加坡桶并展示 `test-pc-s3.hbabaxb.cn`。
- 2026-07-28 重新发版完成：H5 `8f7eed7` 同步到 AWS `18game-nuxt-static-test-h5` 与腾讯 `18game-nuxt-static-test-h5-sg-1450169938`；PC `857966e` 同步到 AWS `18game-nuxt-static-test-pc` 与腾讯 `18game-nuxt-static-test-pc-sg-1450169938`。

验证结果：

- H5 `8f7eed7`、PC `857966e` 已重发。
- H5/PC 页面源码均出现 `https://test-s3.hbabaxb.cn/_nuxt/...`。
- 抽样 `_nuxt` CDN URL 返回 `200`。
- 腾讯 COS 原始域名直连返回 `403`，符合私有桶只允许 CDN/EdgeOne 访问的要求。
- 页面源码中仍存在的 CloudFront URL 属于后端业务 uploads 图片引用；本次按要求未切后端展示域名。
- 2026-07-28 拆分域名后复查：H5 页面源码只出现 `https://test-h5-s3.hbabaxb.cn/_nuxt/...`，PC 页面源码只出现 `https://test-pc-s3.hbabaxb.cn/_nuxt/...`，旧 `test-s3.hbabaxb.cn/_nuxt` 计数为 0。
- 抽样 `entry.9fJ8Knpu.css`、`Bt8A_f6i.js`、`entry.BMkDqC2i.css`、`CsdYMsDC.js` 均返回 `200`，并带对应站点来源的 `Access-Control-Allow-Origin`。
- AWS H5/PC 公开桶 `version.txt` 返回 `200`；腾讯 H5/PC 新加坡 COS 原始域名 `version.txt` 返回 `403`，符合私有桶要求。

2026-07-28 F12/CORS 复查：

- `https://h5.youdianse-test.xyz/` 页面源码中有 87 个 `test-s3.hbabaxb.cn` 前端资源引用。
- `https://pc.youdianse-test.xyz/` 页面源码中有 91 个 `test-s3.hbabaxb.cn` 前端资源引用。
- 抽样 `https://test-s3.hbabaxb.cn/_nuxt/entry.9fJ8Knpu.css`、`https://test-s3.hbabaxb.cn/_nuxt/vendor-el-plus.BLkYWqlr.css`、PC `entry.BMkDqC2i.css` 均返回 `200`。
- 上述响应缺少 `Access-Control-Allow-Origin`，浏览器从 `h5.youdianse-test.xyz` / `pc.youdianse-test.xyz` 跨域加载 `_nuxt` 模块和 CSS 时会显示 `CORS error`。
- 已通知 5 个已记录飞机群：需要在腾讯云 EdgeOne/CDN 为 `test-s3.hbabaxb.cn` 增加响应头。
- 2026-07-28 已改为在腾讯新加坡 COS 桶 `18game-storage-dev-uploads-sg-1450169938` 配置 CORS，并提交 EdgeOne 目录刷新 `https://test-s3.hbabaxb.cn/_nuxt/`，JobId：`3t31l4t0b2fr`。
- 刷新后复查 H5/PC 抽样 CSS/JS 均返回 `200`，且带有对应来源的 `Access-Control-Allow-Origin`，浏览器前端静态资源跨域拦截解除。

腾讯云 COS 当前 CORS 规则：

| Header | 建议值 |
| --- | --- |
| `Access-Control-Allow-Origin` | `https://h5.youdianse-test.xyz`、`https://pc.youdianse-test.xyz` |
| `Access-Control-Allow-Methods` | `GET,HEAD` |
| `Access-Control-Allow-Headers` | `*` |
| `Access-Control-Expose-Headers` | `ETag,Content-Length,Content-Type` |
| `Access-Control-Max-Age` | `86400` |

后续如改 EdgeOne/CDN 侧响应头，可按以下方式兜底：

1. 腾讯云 EdgeOne/CDN 控制台进入 `test-s3.hbabaxb.cn`。
2. 在规则引擎或响应头配置中新增一条匹配规则，路径建议 `/*` 或至少 `/_nuxt/*`。
3. 添加 `Access-Control-Allow-Origin`、`Access-Control-Allow-Methods`、`Access-Control-Allow-Headers`、`Access-Control-Max-Age` 等响应头并保存发布。
4. 刷新 `test-s3.hbabaxb.cn/_nuxt/*` 缓存后复查响应头。
5. 用 `Origin: https://h5.youdianse-test.xyz` 和 `Origin: https://pc.youdianse-test.xyz` 抽样验证。

## 11. 测试资源链路边界和后端资源加速方案

当前四类资源边界：

| 类型 | 上传/构建来源 | 当前源 | 腾讯新加坡侧 | 展示策略 |
| --- | --- | --- | --- | --- |
| H5 前端静态资源 | H5 前端构建 `.output/public` | AWS `18game-nuxt-static-test-h5`，公开桶域名访问 | 腾讯 `18game-nuxt-static-test-h5-sg-1450169938`，私有桶 | 优先走 `https://test-h5-s3.hbabaxb.cn/_nuxt/...` |
| PC 前端静态资源 | PC 前端构建 `.output/public` | AWS `18game-nuxt-static-test-pc`，公开桶域名访问 | 腾讯 `18game-nuxt-static-test-pc-sg-1450169938`，私有桶 | 优先走 `https://test-pc-s3.hbabaxb.cn/_nuxt/...` |
| 后台图片 uploads | 后台上传 | AWS `18game-storage-dev-176528004422`，`AWS_DOMAIN=https://d391me9s8n5j5s.cloudfront.net` | 本次不切换 | 继续由后端接口返回 AWS/CloudFront |
| APK/App 客户端包 | 后台或发布流程上传 | 当前与后端 AWS 老 S3 链路同组，下载 CDN 为 `https://dd3tn75akeg7c.cloudfront.net` | 本次不切换 | 继续使用 AWS 老 S3 / CloudFront |

后端 AWS 资源使用腾讯 CDN 国内加速的建议：

- 不改变后台上传流程，后台继续上传 AWS S3。
- 为后台 uploads 和客户端包分别准备腾讯 CDN/EdgeOne 加速域名，源站指向现有 AWS CloudFront 或 AWS S3。
- CDN 域名仅做反向代理和缓存加速，保留 AWS 为源，避免马上改后台上传代码。
- 前端展示时可在网关、Nginx 或前端 URL 映射层把已知 AWS/CloudFront 域名改写为腾讯 CDN 域名。
- 更稳的长期方案是后端 `cdn_image` / package 域名配置直接返回腾讯 CDN 域名，但需单独灰度验证。
- 前端 `_nuxt` 静态资源和后台 uploads/package 资源不要共用发布逻辑；前端发版只负责构建产物双推，后台资源由同步按钮或 CDN 反代负责。
