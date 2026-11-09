---
id: "doc-aee4017287f0"
title: "线上前置 H5/PC 切 yiyi0620 与 AWS S3 记录"
date: "2026-08-06T19:19:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_1919-%E3%80%90%E9%85%8D%E7%BD%AE%E9%83%A8%E7%BD%B2%2B%E9%98%BB%E5%A1%9E%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E5%89%8D%E7%BD%AEH5-PC%E5%88%87yiyi0620%E4%B8%8EAWS-S3.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_1919-【配置部署+阻塞记录】线上前置H5-PC切yiyi0620与AWS-S3.md"
sourceSha256: "34502d698acae0a062eb9fb50fd936c47161e15537de402bf243a9ae3f464c31"
sourceSystem: "project-doc"
---

# 线上前置 H5/PC 切 yiyi0620 与 AWS S3 记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608061919-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-%E7%BA%BF%E4%B8%8A%E5%89%8D%E7%BD%AE%20H5-PC%20%E5%88%87%20yiyi0620%20%E4%B8%8E%20AWS%20S3%20%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-06 19:19｜日期依据：文件名日期

环境标签：线上前置 / 游点涩 / H5 / PC / AWS S3 / JP 服务器

## 目标

- 页面入口切到 `https://h5.yiyi0620.com`、`https://pc.yiyi0620.com`。
- H5、PC 打包产物分别使用独立 AWS S3 桶作为 `NUXT_PUBLIC_CDN_URL`。
- 图片、视频等后台返回资源使用线上后台 AWS 资源域。
- 砍掉旧备案域名静态资源链路和签名加密链路。
- 部署到日本服务器并为两个二级域名制作 SSL 证书。

## 已读取上下文

- `AGENTS.md`
- `workbench/START_HERE.md`
- `workbench/ACTIVE_TASKS.md`
- `workbench/PROJECT_INDEX.md`
- `workbench/MACHINE_ACCESS_MATRIX.md`
- `workbench/PROJECT_RUNTIME_CHAINS.md`
- `workbench/NOTIFICATION_TARGETS.md`
- `workbench/projects/18game_devops/CURRENT_STATE.md`
- `workbench/projects/18game_devops/CURRENT_TASK.md`
- `devops/ai_context/servers.yml`
- 历史文档：
  - `2026-08-04_2012-【运维记录+链路改造】线上前置日本服务器替换与备案域名COS直连关系.md`
  - `2026-08-04_1635-【运维记录+配置部署】线上前置PC-H5网站与腾讯CDN域名配置.md`
  - `2026-08-04_1702-【运维规划+链路改造】备案域名前端静态资源COS绑定域名直连关系.md`
  - `2026-08-06_1800-【架构调整+回退】测试H5-PC静态资源恢复AWS老S3.md`
  - `2026-08-06_1837-【配置调整+域名回退】测试H5-PC页面入口切回youdianse-test子域.md`

## 通知目标

- `18game运维`
- `18GAME_ 上线群（正式環境）`

本任务每个明确步骤均已通过 ben-bot 运行容器发群通知；本机默认 Telegram 通道返回 `chat not found`，未伪造通知。

## 变更内容

- 修改线上前置 H5 发布入口默认值：
  - 页面域名：`https://h5.yiyi0620.com`
  - 静态资源：`https://18game-nuxt-static-preprod-h5.s3.ap-southeast-1.amazonaws.com`
  - S3 桶：`18game-nuxt-static-preprod-h5`
  - COS 同步：关闭
  - 腾讯 CDN/EdgeOne 刷新：关闭
  - 静态资源签名鉴权：关闭
- 修改线上前置 PC 发布入口默认值：
  - 页面域名：`https://pc.yiyi0620.com`
  - 静态资源：`https://18game-nuxt-static-preprod-pc.s3.ap-southeast-1.amazonaws.com`
  - S3 桶：`18game-nuxt-static-preprod-pc`
  - COS 同步：关闭
  - 腾讯 CDN/EdgeOne 刷新：关闭
  - 静态资源签名鉴权：关闭
- 修复 PC 共用发布入口变量映射，补齐 `BUILD_COMMAND`、`BUILD_ENV_FILE`、SSH 目标、静态删除开关和腾讯签名开关等 PC 前缀变量到共用引擎的映射。
- 新建并配置两个 AWS S3 桶，沿用现有测试桶的公开读和 CORS 姿态。
- 部署 JP Nginx 配置：
  - `h5.yiyi0620.com` 代理到 H5 容器。
  - `pc.yiyi0620.com` 代理到 PC 容器。
  - 图片/视频兼容路径代理到线上后台 AWS CloudFront：`d391me9s8n5j5s.cloudfront.net`。
  - H5/PC favicon/PWA 静态兼容路径回源各自 AWS S3 桶。
- 禁用旧备案域名 COS 代理：
  - 禁用 `/etc/nginx/conf.d/30-youdianse-static-cos-proxy.conf`
  - 删除旧备案域名 certbot 证书记录

## 发布结果

| 项目 | 版本 | 容器 | 端口 | 状态 |
| --- | --- | --- | --- | --- |
| H5 | `87f1652` | `youdianse_preprod_h5_main_18game_h5_client_3003` | `3003` | Up |
| PC | `041764b` | `youdianse_preprod_pc_dev_18game_pc_client_3004` | `3004` | Up |

说明：PC 仓库没有 `scripts.build:prod`，发布引擎按仓库实际脚本降级为 `pnpm build`，资源链路仍为线上前置 AWS S3。

## 备份点

- ben-bot 运行机脚本备份：`/opt/telegram/18game_devops/.codex-backup/preprod-yiyi0620-202608062015`
- JP Nginx 前置配置备份：`/root/.codex-backup/preprod-yiyi0620-nginx-202608062015`
- 旧备案域名 COS 代理配置备份：`/root/.codex-backup/preprod-yiyi0620-cut-old-static-cos-20260806111725`
- H5 误跑/失败半成品目录已移入 JP 服务器备份目录，最终成功版本为 `87f1652`。

## 验证结果

| 验证项 | 结果 |
| --- | --- |
| 本地 Python 编译 | 通过 |
| ben-bot 容器 Python 编译 | 通过 |
| H5 发布 | 成功 |
| PC 发布 | 成功 |
| JP Docker 容器 | H5/PC 均 Up |
| JP Nginx `nginx -t` | 通过 |
| Host Header `h5.yiyi0620.com /healthz` | `200 ok` |
| Host Header `pc.yiyi0620.com /healthz` | `200 ok` |
| Host Header H5 `/` | `HTTP/1.1 200 OK` |
| Host Header PC `/` | `HTTP/1.1 200 OK` |
| Host Header H5 `/version.json` | `short_id=87f1652` |
| Host Header PC `/version.json` | `short_id=041764b` |
| H5 S3 `version.json` | `200 OK` |
| PC S3 `version.json` | `200 OK` |
| H5 页面静态资源域 | 命中 `18game-nuxt-static-preprod-h5.s3.ap-southeast-1.amazonaws.com` |
| PC 页面静态资源域 | 命中 `18game-nuxt-static-preprod-pc.s3.ap-southeast-1.amazonaws.com` |
| active Nginx 旧备案域名计数 | `0` |
| certbot 旧备案域名计数 | `0` |

## 当前阻塞

公开域名仍不可用，证书未能签发。

实测 DNS：

| 域名 | 当前 A 记录 |
| --- | --- |
| `yiyi0620.com` | `38.252.248.24` |
| `h5.yiyi0620.com` | `38.252.248.24` |
| `pc.yiyi0620.com` | `38.252.248.24` |

实测可达性：

- `http://h5.yiyi0620.com/healthz`：公网超时。
- `https://h5.yiyi0620.com/`：公网超时。
- `http://pc.yiyi0620.com/healthz`：公网超时。
- `https://pc.yiyi0620.com/`：公网超时。
- 强制解析到 `138.252.248.139` 后，H5/PC HTTP `/healthz` 均 200。

原因：当前 DNS 指向 `38.252.248.24`，而日本服务器实际可用公网 IP 是：

- `138.252.248.24`
- `138.252.248.139`
- `138.252.248.249`

因此 Let's Encrypt HTTP-01 证书签发无法通过公网校验。需要先把 `yiyi0620.com` 的 `@` 和 `*` A 记录改到实际 JP IP 之一，建议优先使用已有发布 SSH 主机所在机器的可达 IP `138.252.248.139`，或按 DNS 截图意图改为同机实际 IP `138.252.248.24`。DNS 修正后再签发 `h5.yiyi0620.com`、`pc.yiyi0620.com` 证书并复验 HTTPS。

## 后续动作

1. DNS 修正：`@.yiyi0620.com` 与 `*.yiyi0620.com` A 记录从 `38.252.248.24` 改到 `138.252.248.24`、`138.252.248.139` 或 `138.252.248.249` 之一。
2. 等待 DNS 生效后，在 JP 服务器签发 `h5.yiyi0620.com`、`pc.yiyi0620.com` SSL 证书。
3. 切换 Nginx HTTPS server 块，验证：
   - `https://h5.yiyi0620.com/`
   - `https://h5.yiyi0620.com/version.json`
   - `https://pc.yiyi0620.com/`
   - `https://pc.yiyi0620.com/version.json`

## 群通知记录

- 步骤 1：读取 workbench 和任务目标。
- 步骤 2：读取历史 doc 和脚本。
- 步骤 3：DNS/服务器核验，发现 `38.252.248.24` 与实际 JP IP 不一致。
- 步骤 4：本地配置修改和编译验证。
- 步骤 5：ben-bot 同步、重建和 H5/PC 版本查询。
- 步骤 6：JP Nginx 配置部署。
- 步骤 7：H5 首次发布发现 wrapper 环境污染，终止。
- 步骤 8：修复 wrapper 强覆盖并清理半成品。
- 步骤 9：H5 发布发现 Docker buildx 缺失。
- 步骤 10：安装 Docker buildx。
- 步骤 11：H5 发布发现 S3 桶不存在。
- 步骤 12：创建并配置两个独立 AWS S3 桶。
- 步骤 13：H5 发布成功。
- 步骤 14：PC 首次发布前检查发现目标偏差并中断。
- 步骤 15：修复 PC 共用入口变量映射。
- 步骤 16：PC 发布成功。
- 步骤 17：旧备案域名 COS 代理和旧证书记录清理完成。
