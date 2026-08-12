---
id: "doc-e2b492b49ddb"
title: "线上 H5+PC 新域名接入（yds-pc-h5-01/02/03.cc）"
date: "2026-08-12T15:36:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1536-%E3%80%90%E9%85%8D%E7%BD%AE%E9%83%A8%E7%BD%B2%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8AH5%2BPC%E6%96%B0%E5%9F%9F%E5%90%8D%E6%8E%A5%E5%85%A5.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1536-【配置部署+运维记录】线上H5+PC新域名接入.md"
sourceSha256: "8a2b3533a9a2e85eedf6df97d8921f58b61400f91c39996193baa71aa7d06bf5"
sourceSystem: "project-doc"
---

# 线上 H5+PC 新域名接入（yds-pc-h5-01/02/03.cc）

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1536-【配置部署+运维记录】线上H5+PC新域名接入.md`

> 整理日期：2026-08-12 15:36｜日期依据：文件名日期

环境标签：线上环境 / 游点涩 / H5 / PC / nginx / SSL / ben-bot

时间：2026-08-12 15:36（Asia/Manila）

## 任务来源

用户要求：

- 读取 `doc` 历史文档，使用 `workbench`，每步操作都发群通知（本任务同步通知 `18GAME_ 上线群（正式環境）` 与 `18game运维`）。
- 新开 AWS 服务器 `16.208.38.88`（与线上后端同内网），参考 线上环境 H5 发版 / 线上前置 H5 / PC 发版，制作 `线上环境-游点涩-h5+pc-发版` 入口。
- 3 个域名 `yds-pc-h5-01/02/03.cc`（`*` 与 `@` A 到 16.208.38.88）搭建正式线上 PC + H5：`www.域名`/根域名按设备跳转 `h5.域名`/`pc.域名`。
- 最终域名必须全 HTTPS；新服务器制作 SSL 证书，并写自动化更新/到期检查脚本部署到服务器。
- 后续追加：把组合入口拆分为 `线上环境-游点涩-新h5-发版`、`线上环境-游点涩-新pc-发版` 两个按钮，分别选择对应 git id 发布。
- 操作完成后先验证，再汇总文档，发群并合并提交本地代码。

## 本轮读取依据

- `AGENTS.md`、`workbench/`（START_HERE / ACTIVE_TASKS / MACHINE_ACCESS_MATRIX / PROJECT_RUNTIME_CHAINS / NOTIFICATION_TARGETS / CURRENT_STATE / CURRENT_TASK）、`devops/ai_context/servers.yml`
- 参考入口：`线上环境-游点涩-h5-发版`、`线上前置-游点涩-h5-发版`、`线上前置-游点涩-pc-发版`、`线上前置-游点涩-前端配置/nginx/youdianse-preprod-frontends.conf`
- 群聊天记录（产品/陈总/运维关于 PC 上线与域名跳转方案）

## 群通知

按用户最新要求，本任务每步通知发送到两个群：

- `18GAME_ 上线群（正式環境）`（`-1003762262155`）
- `18game运维`（`-4929911895`）

已通知步骤：1 上下文与只读核验、2 实施计划、3 仓库产物、4 服务器初始化与证书、5 发布（含 PC 静态修正）、6 拆分入口。最终汇总与文档见发送记录。

## 服务器与域名

| 项目 | 值 |
| --- | --- |
| 服务器 | `16.208.38.88`（hostname `ip-172-31-27-233`，Ubuntu 22.04，8C/20G/49G，AWS，与线上后端同 VPC） |
| 登录 | `ubuntu`，SSH key：`线上环境-游点涩-h5-发版/id_rsa`，sudo 免密 |
| 域名 | `yds-pc-h5-01.cc`、`yds-pc-h5-02.cc`、`yds-pc-h5-03.cc`；根域/www/pc/h5 均 A 到 `16.208.38.88` |

## 访问规则（nginx，一个域名一个 conf）

- `www.域名` 与根域名：按设备 UA（PC 浏览器 / 手机浏览器）301 跳转：
  - PC → `https://pc.域名/`
  - 手机 → `https://h5.域名/`
- `pc.域名`：反代 PC 容器 `203.0.113.1:3004`
- `h5.域名`：反代 H5 容器 `203.0.113.1:3003`
- `/api|/channel|/customer` 代理线上 `www.youdianse.com`；`/uploads` 代理线上 CloudFront；`sw.js`/旧 workbox/`/images/aside` 兜底。

## 部署内容

### 服务器初始化（16.208.38.88）

- 安装 Docker 29.7.2、Docker Compose v5.4.0、Nginx 1.18.0（纯 nginx）、certbot 1.21.0、git。
- `ubuntu` 加入 docker 组。

### SSL 证书与自动续期

- Let's Encrypt HTTP-01，3 个证书（每个 SAN 覆盖 根域/www/pc/h5），到期 `2026-11-10`。
- 自动续期脚本 `/usr/local/bin/youdianse-prod-h5pc-ssl-renew.sh`（certbot renew + 到期检查 + nginx reload + nginx -t），cron 每天 03:10 执行。

### 发布（新服务器容器）

- H5：`main` 分支 `915a0d3` → 容器 `youdianse_prod_h5_main_18game_h5_client_3003`（端口 3003，静态容器内服务），页面 `https://h5.yds-pc-h5-01.cc`。
- PC：`dev` 分支 `5c1d4ba` → 容器 `youdianse_prod_pc_dev_18game_pc_client_3004`（端口 3004，静态生产桶 `18game-nuxt-static-prod-pc`），页面 `https://pc.yds-pc-h5-01.cc`。

### ben-bot 发布入口（拆分）

按用户要求拆分为两个按钮：

- `线上环境-游点涩-新h5-发版`：H5 main，选 git id 发布。
- `线上环境-游点涩-新pc-发版`：PC dev，选 git id 发布。

原组合入口 `线上环境-游点涩-h5+pc-发版` 已下线；nginx 配置归档到 `线上环境-游点涩-新前端配置/nginx/`。

## 过程中的问题与处理

1. PC 发布引擎会把空静态配置回退成测试桶，首次 PC 构建误同步到 `18game-nuxt-static-test-pc`（测试桶）。
2. 处理：新建生产桶 `18game-nuxt-static-prod-pc`（公开读 + CORS），新 PC 入口静态配置改指生产桶并重发 PC；同步把测试 PC 重发到当前 dev `5c1d4ba`（041764b 不在最近 3 条提交，无法回滚），使测试桶与测试 PC 容器保持一致。

## 验证清单

| 项目 | 结果 |
| --- | --- |
| `https://h5.yds-pc-h5-01.cc/` | 200，版本 915a0d3 |
| `https://pc.yds-pc-h5-01.cc/` | 200，版本 5c1d4ba |
| PC 页面静态域 | `18game-nuxt-static-prod-pc.s3.ap-southeast-1.amazonaws.com` |
| PC UA 根域跳转 | 301 → `https://pc.yds-pc-h5-01.cc/` |
| 手机 UA 根域/www 跳转 | 301 → `https://h5.yds-pc-h5-01.cc/` |
| 02/03 域名跳转 | 301 → 对应 pc./h5. 子域 |
| `pc./h5. /healthz` | 200 |
| 证书 | 3 个证书 SAN 覆盖 根域/www/pc/h5，2026-11-10 到期 |
| SSL 续期脚本 | 执行通过（renew + 到期检查 + nginx -t），cron 每天 03:10 |
| 容器 | H5/PC 均 Up |
| 新入口 list_json | 新h5=main 提交、新pc=dev 提交均正确 |
| 双群通知 | 每步已发送上线群与运维群 |

## 结论

- 线上 H5+PC 新域名已在独立服务器 `16.208.38.88` 落地：设备 UA 跳转、pc/h5 反代、全 HTTPS 均已生效。
- SSL 自动续期与到期检查脚本已部署并纳入 cron。
- ben-bot 发布入口已拆分为 `线上环境-游点涩-新h5-发版` / `线上环境-游点涩-新pc-发版`，可分别选择 git id 发布。

## 后续注意

- 新 PC/新 H5 发布走各自按钮；目标均为 `16.208.38.88`，互不影响现有 `www.youdianse.com` 链路。
- 测试 PC 已对齐当前 dev（5c1d4ba）；后续如需恢复历史版本，需重新打包发布对应提交。
- SSL 证书到期前自动续期；如域名增加/更换，需同步更新 nginx conf、证书 SAN 与续期脚本域名列表。
