---
id: "doc-2b51481ae28a"
title: "yiyi0620 证书与 ben-bot 前端发版展示收尾"
date: "2026-08-06T19:52:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Python", "Nginx", "自动化", "CDN", "DNS", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_1952-%E3%80%90%E9%85%8D%E7%BD%AE%E9%83%A8%E7%BD%B2%2B%E6%9C%BA%E5%99%A8%E4%BA%BA%E4%BC%98%E5%8C%96%E3%80%91yiyi0620%E8%AF%81%E4%B9%A6%E4%B8%8Eben-bot%E5%89%8D%E7%AB%AF%E5%8F%91%E7%89%88%E5%B1%95%E7%A4%BA%E6%94%B6%E5%B0%BE.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_1952-【配置部署+机器人优化】yiyi0620证书与ben-bot前端发版展示收尾.md"
sourceSha256: "fdfdea3ca657c9bba890dfe4e94fbecb39017a6b5b045fb60fafb1e0e069aba0"
sourceSystem: "project-doc"
---

# yiyi0620 证书与 ben-bot 前端发版展示收尾

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608061952-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BPython-yiyi0620%20%E8%AF%81%E4%B9%A6%E4%B8%8E%20ben-bot%20%E5%89%8D%E7%AB%AF%E5%8F%91%E7%89%88%E5%B1%95%E7%A4%BA%E6%94%B6%E5%B0%BE.md)

> 整理日期：2026-08-06 19:52｜日期依据：文件名日期

环境标签：线上前置 / 线上环境 / 测试环境 / 游点涩 / ben-bot / SSL / AWS S3 / 前端发版

## 1. 任务来源

用户要求：

- 读取 `doc` 里面补资源的文档，使用 workbench，并读取之前操作留下的 doc 文档。
- 每步操作都发群通知。
- DNS 已重新解析，可以制作 SSL 证书。
- ben-bot 里面几个前端发布按钮改成一行一个展示，避免看不见字。
- 各环境前端 H5/PC 发布成功后，都需要输出域名，方便群里点击打开查看。
- 更新 ben-bot 主菜单文案，补充线上前置 H5/PC 入口。
- 线上前置 `h5.yiyi0620.com`、`pc.yiyi0620.com` 使用独立 AWS S3 前端静态资源桶，并继续砍掉之前的备案域名默认链路。

## 2. 本轮读取依据

本轮按 workbench 入口读取：

- `workbench/START_HERE.md`
- `workbench/ACTIVE_TASKS.md`
- `workbench/PROJECT_INDEX.md`
- `workbench/MACHINE_ACCESS_MATRIX.md`
- `workbench/PROJECT_RUNTIME_CHAINS.md`
- `workbench/NOTIFICATION_TARGETS.md`
- `workbench/projects/18game_devops/CURRENT_STATE.md`
- `workbench/projects/18game_devops/CURRENT_TASK.md`
- `devops/ai_context/servers.yml`

重点参考历史文档：

- `devops/python/ben-bot/doc/2026-08-06_1919-【配置部署+阻塞记录】线上前置H5-PC切yiyi0620与AWS-S3.md`
- `devops/python/ben-bot/doc/2026-08-06_1837-【配置调整+域名回退】测试H5-PC页面入口切回youdianse-test子域.md`
- `devops/python/ben-bot/doc/2026-08-06_1800-【架构调整+回退】测试H5-PC静态资源恢复AWS老S3.md`
- `devops/python/ben-bot/doc/2026-08-04_1702-【运维规划+链路改造】备案域名前端静态资源COS绑定域名直连关系.md`
- `devops/python/ben-bot/doc/2026-08-04_2130-【运维规划+域名关系】四个备案域名与H5-PC-S3-IMG链路整理.md`
- `devops/python/ben-bot/doc/2026-08-04_2143-【运维记录+域名补全】hbabaxb-hbazuua前端S3静态资源域名补全.md`

## 3. 群通知

本轮每个明确步骤均已通知：

- `18game运维`
- `18GAME_ 上线群（正式環境）`

通知标题沿用线上规则：`【线上环境｜步骤 N 完成】`。

已通知步骤：

1. 恢复上下文并确认任务范围。
2. 读取 workbench、服务器事实源、历史文档和 bot 代码索引。
3. DNS 与日本服务器只读核验完成。
4. `h5.yiyi0620.com`、`pc.yiyi0620.com` 证书签发完成。
5. 日本服务器 Nginx HTTPS 配置部署并 reload。
6. yiyi0620 H5/PC HTTPS 验证通过。
7. ben-bot 本地代码修改与静态验证完成。
8. ben-bot 同步、重启、容器内验证和最终 HTTPS/S3 复验通过。

通知内容未包含密码、token、私钥、原始 `.env` 或完整敏感配置。

## 4. SSL 与 Nginx 结果

DNS 复验：

- `h5.yiyi0620.com -> 138.252.248.24`
- `pc.yiyi0620.com -> 138.252.248.24`

日本线上前置服务器：

- SSH 入口：`root@138.252.248.139:38927`
- 可用公网 IP：`138.252.248.24`、`138.252.248.139`、`138.252.248.249`
- Nginx：`nginx -t` 通过，已 reload

证书：

| 域名 | 证书 | SAN | 到期时间 |
| --- | --- | --- | --- |
| `h5.yiyi0620.com` | Let's Encrypt | `DNS:h5.yiyi0620.com` | `2026-11-04 10:47:06+00:00` |
| `pc.yiyi0620.com` | Let's Encrypt | `DNS:pc.yiyi0620.com` | `2026-11-04 10:47:14+00:00` |

线上前置页面：

| 域名 | 验证结果 | 当前版本 |
| --- | --- | --- |
| `https://h5.yiyi0620.com` | `/healthz`、`/`、`/version.json` 均 HTTP/2 200 | `87f1652` |
| `https://pc.yiyi0620.com` | `/healthz`、`/`、`/version.json` 均 HTTP/2 200 | `041764b` |

前端静态资源：

- H5 页面引用：`18game-nuxt-static-preprod-h5.s3.ap-southeast-1.amazonaws.com`
- PC 页面引用：`18game-nuxt-static-preprod-pc.s3.ap-southeast-1.amazonaws.com`

后台图片/视频兼容路径：

- Nginx `images/image/video/videos/media/uploads` 兼容路径走线上后台 AWS CloudFront：`d391me9s8n5j5s.cloudfront.net`
- 旧备案域名 COS 代理不再作为默认链路。

## 5. ben-bot 改动

### 5.1 菜单展示

已更新 `devops/python/ben-bot/app/benbot/home.py`：

- `/start` 功能结构补充：
  - `线上前置-游点涩-h5-发版`
  - `线上前置-游点涩-pc-发版`
- 首页前端发版入口从一排多个改为一行一个。

已更新 5 个前端发版入口 `.benbot.json`：

- `测试环境-游点涩-h5-发版`
- `测试环境-游点涩-pc-发版`
- `线上前置-游点涩-h5-发版`
- `线上前置-游点涩-pc-发版`
- `线上环境-游点涩-h5-发版`

这些入口的 `columns` 均改为 `1`。

说明：当前仓库没有单独的 `线上环境-游点涩-pc-发版` 入口，本轮未凭空新增。

### 5.2 发布成功域名输出

已更新共享测试/线上前置发布引擎：

- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py`

已更新线上 H5 发布引擎：

- `devops/python/ben-bot/data/scripts/线上环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py`

已更新 bot 最终进度消息和日志附件标题：

- `devops/python/ben-bot/app/benbot/executor.py`

发布成功后统一输出：

```text
发布后查看:
页面域名: https://...
版本 JSON: https://.../version.json
版本 TXT: https://.../version.txt
```

测试 H5/PC 额外保留：

```text
测试访问域名: https://test-h5.youdianse-test.xyz
测试访问域名: https://test-pc.youdianse-test.xyz
```

线上前置 H5/PC 发布完成后会输出：

```text
页面域名: https://h5.yiyi0620.com
页面域名: https://pc.yiyi0620.com
```

线上 H5 发布完成后会输出：

```text
页面域名: https://www.youdianse.com
```

## 6. 同步与备份

ben-bot 运行机：

- 机器：`ubuntu@52.79.252.255`
- 仓库路径：`/opt/telegram/18game_devops`
- bot 目录：`/opt/telegram/18game_devops/devops/python/ben-bot`

远程备份目录：

- ben-bot 文件备份：`/opt/telegram/18game_devops/.codex-backup/benbot-menu-domain-output-20260806115018`
- yiyi0620 Nginx 443 配置前备份：`/root/.codex-backup/preprod-yiyi0620-ssl-nginx-20260806114649`
- 旧备案域名 COS 代理禁用备份：`/root/.codex-backup/preprod-yiyi0620-cut-old-static-cos-20260806111725`

ben-bot 已重建并启动：

- 容器：`ben-bot`
- 镜像：`ben-bot:latest`
- 状态：`Up`

## 7. 验证清单

| 项目 | 结果 |
| --- | --- |
| 本地 `py_compile` | 通过 |
| 本地 5 个 `.benbot.json` JSON 校验 | 通过 |
| 容器内 `py_compile` | 通过 |
| 容器内 5 个前端入口 `columns` | 全部为 `1` |
| 容器内首页前端发版按钮 | 5 个按钮均一行一个，`ALL_SINGLE=True` |
| ben-bot 容器日志 | 启动正常，启动通知成功 |
| 日本服务器 `nginx -t` | 通过 |
| `h5.yiyi0620.com` 证书 SAN | `DNS:h5.yiyi0620.com` |
| `pc.yiyi0620.com` 证书 SAN | `DNS:pc.yiyi0620.com` |
| `https://h5.yiyi0620.com/healthz` | HTTP/2 200 |
| `https://pc.yiyi0620.com/healthz` | HTTP/2 200 |
| `https://h5.yiyi0620.com/version.json` | 200，版本 `87f1652` |
| `https://pc.yiyi0620.com/version.json` | 200，版本 `041764b` |
| H5 页面 AWS S3 静态资源 | 命中 `18game-nuxt-static-preprod-h5.s3.ap-southeast-1.amazonaws.com` |
| PC 页面 AWS S3 静态资源 | 命中 `18game-nuxt-static-preprod-pc.s3.ap-southeast-1.amazonaws.com` |

## 8. 当前可点击入口

```text
线上前置 H5:
https://h5.yiyi0620.com

线上前置 PC:
https://pc.yiyi0620.com

测试 H5:
https://test-h5.youdianse-test.xyz

测试 PC:
https://test-pc.youdianse-test.xyz
```

## 9. 结论

本轮收尾完成：

- DNS 阻塞已解除，yiyi0620 H5/PC SSL 证书已签发。
- 日本服务器 Nginx 已开启 H5/PC HTTPS。
- 线上前置 H5/PC 可通过 `https://h5.yiyi0620.com` 与 `https://pc.yiyi0620.com` 正常访问。
- 前端打包静态资源继续使用各自独立 AWS S3 域名。
- 旧备案域名默认链路已砍掉，不再作为线上前置默认入口。
- ben-bot 前端发版按钮已改为一行一个。
- 各前端发布成功后会输出页面域名和版本链接，方便群内直接点击验证。
