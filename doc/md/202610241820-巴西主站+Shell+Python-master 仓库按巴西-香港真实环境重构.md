---
id: "doc-57a6fe2988c5"
title: "master 仓库按巴西/香港真实环境重构"
date: "2026-10-24T18:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "Nginx", "监控告警", "自动化", "CDN"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-10-24-1820-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91master%E4%BB%93%E5%BA%93%E6%8C%89%E5%B7%B4%E8%A5%BF%E9%A6%99%E6%B8%AF%E7%9C%9F%E5%AE%9E%E7%8E%AF%E5%A2%83%E9%87%8D%E6%9E%84.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-10-24-1820-【运维】master仓库按巴西香港真实环境重构.md"
sourceSha256: "874f9c9950fe489616c68192f41aec211818190a857d05585a961e67251ba703"
sourceSystem: "project-doc"
---

# master 仓库按巴西/香港真实环境重构

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-10-24-1820-【运维】master仓库按巴西香港真实环境重构.md`

> 整理日期：2026-10-24 18:20｜日期依据：文件名日期

时间：北京 2026-10-24 18:20 ｜ 巴西圣保罗 2026-10-24 07:20

## 目标

- 移除顶层 `docker/` 目录，把其中全部文件迁出。
- 根据 `运维发布页.html` 和线上真实服务器，重新规范项目目录。
- 同时覆盖巴西、香港和公共层。
- 从 `origin/cn` 补充香港配置、工具和历史。
- 完整保留历史文档，提供开发和 AI 快速索引。

## Git 基线

```text
本地分支：master
本地基线：8590f52d
origin/master：8fcefd60
origin/master..本地：本地领先，远端没有新提交
origin/cn：5c3b3de6a5beef52aa9c8f152366e9650503610f
```

03 打包机工作区仍位于业务提交 `336e2fde`，且存在未提交域名配置；该工作区没有被
合并到本地运维 `master`。

## 线上真实目录核验

### 巴西

```text
01/02：/data/server-runtime
03：/data/pgserver
03 香港配置源：/data/server-runtime-hk
03 registry：192.0.2.1:5000
```

03 是代码打包与镜像分发机，不是普通业务发布目标。

### 香港

```text
01/02：/data/server-runtime
Nginx：/etc/nginx/sites-available/bizops-hongkong.conf
Nginx snippets：/etc/nginx/snippets/bizops-hongkong-*.conf
镜像来源：192.0.2.20:5000
```

### 厂商差异

```text
巴西：api pg vendor_a vendor_a_ws ppk pp vendor_c vendor_d g759
香港：api pg vendor_b vendor_a_ws ppk pp vendor_c vendor_d g759
```

香港没有 vendor_a HTTP 主服务；vendor_b 复用 vendor_a 镜像。

## 新目录结构

```text
.
├── build/
├── docs/
│   ├── guides/
│   └── history/
├── infrastructure/
│   ├── brazil/
│   ├── hongkong/
│   └── shared/
├── scripts/
├── workbench/
├── 运维发布页.html
└── 静态资源缓存清理笔记.html
```

迁移规则：

```text
docker/scripts/             -> scripts/
docker/doc/                 -> docs/history/
docker/workbench/           -> workbench/
docker/线上服务器信息/       -> infrastructure/
docker/Dockerfile           -> build/Dockerfile
```

## 实时快照

已从服务器直接导出并校验：

```text
巴西 01 域名配置 10 个
香港 01 域名配置 10 个
香港 Nginx 配置 3 个
巴西运行时脚本 7 个
香港运行时脚本 2 个
```

快照文件均附带 `SHA256SUMS`，并与线上重新计算结果逐字节一致。

## 香港 cn 补充

从 `origin/cn@5c3b3de6` 导入：

```text
域名配置 7 个
Cloudflare / AWS / CloudFront / S3 工具与说明 12 个
历史文档 19 个
```

线上配置明显比 `cn` 新：

- 活跃核心静态域名使用 `m4q7z1.shop`、`k8x2v9.shop`；
- 存在 `hkcloudplay06.com`、`hkcloudplay07.com` 扩展配置；
- vendor_b 增加 `vendor_b-static3-aws` 至 `vendor_b-static5-aws`；
- PG 增加 `pg6-static`、`pg7-static`；
- 线上有 `fc.json`、`jdb.json`、`vendor_a.json` 配置，但不代表对应业务已全部启用。

差异详见 `infrastructure/hongkong/domains/DIFF.md`。

## Worker 变更保护

当前线上 Worker 已经被开发手工改为 `FACTORY_CONFIG` 结构：

```text
SHA256：
d3c90b51d3cde911d7c9ac7c1c17b745a0ad84375725092abc88a1986cd4f265

宝塔备份：
/root/bizops-cf-backups/20261024-094228-worker-manual

仓库备份：
scripts/worker-js-cdn-代码备份/【线上在用】worker.js
scripts/worker-js-cdn-代码备份/【历史备份】2026-10-24-094228-开发手工变更-FACTORY_CONFIG.js
```

新增 `scripts/cf_worker_backup.py`。以后 Worker 操作前必须先拉取、备份、比较 SHA256，
不能用仓库旧文件直接覆盖线上。

## 文档保留

- 原 `docker/doc/` 的 219 个文档全部保留。
- 香港 master 历史移入 `docs/history/hongkong/live/`。
- 香港 cn 历史移入 `docs/history/hongkong/cn/`。
- 新增 `docs/history/INDEX.md`。
- 新增项目规范与运行/发布规范。

## 验证

```text
Python 脚本编译：通过
Shell 语法：通过
全部实时 JSON：通过
快照 SHA256：通过
Markdown 当前文档链接：通过
HTML 桌面/手机布局：通过
HTML JavaScript 运行：无错误
Telegram 通知通道：监控报警群可发送
```

## 群通知

```text
步骤 1 基线核查：message_id=513
步骤 3 目录与香港补充完成：message_id=514
步骤 4 文档与验证完成：message_id=515
```
