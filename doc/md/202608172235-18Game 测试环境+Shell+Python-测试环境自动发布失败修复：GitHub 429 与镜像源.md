---
id: "doc-40ff3ad9a3b9"
title: "测试环境自动发布失败修复：GitHub 429 与镜像源"
date: "2026-08-17T22:35:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "Nginx", "Redis", "自动化", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-17_2235-%E3%80%90%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E8%87%AA%E5%8A%A8%E5%8F%91%E5%B8%83%E5%A4%B1%E8%B4%A5-GitHub429%E4%B8%8E%E9%95%9C%E5%83%8F%E6%BA%90%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-17_2235-【修复记录】测试环境自动发布失败-GitHub429与镜像源修复.md"
sourceSha256: "677fe582f142f5a6900962c6624dff86272a7efbc54db066a468302a501011a4"
sourceSystem: "project-doc"
---

# 测试环境自动发布失败修复：GitHub 429 与镜像源

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-17_2235-【修复记录】测试环境自动发布失败-GitHub429与镜像源修复.md`

> 整理日期：2026-08-17 22:35｜日期依据：文件名日期

环境标签：测试环境 / CICD / 自动发布 / Docker 构建 / 38.92.8.34

时间：2026-08-17 22:35（Asia/Manila）

## 背景

后端 dev 推送 config 保存大小限制（0b3ca19e）后，webhook 自动发布 20 分钟未完成，诸葛亮反馈“部署 20 分钟了没好，之前部署都很快”。

## 根因

- 发布不是卡住，是构建失败：`php-web.Dockerfile` 在容器内从 `https://github.com/phalcon/cphalcon/archive/v4.1.2.zip` 下载 Phalcon 源码，GitHub 对服务器出口 IP 返回 **429 限流**，实际下载到 199 字节错误页，`unzip` 失败 → 构建 `FAILED`（21 分钟主要是下载/重试耗时）。
- 触发原因：本轮构建层缓存失效（pecl/phalcon 层重新执行），需要重新联网下载；此前该层一直命中缓存所以“之前部署都很快”。
- 验证：服务器直接访问 `github.com` / `codeload.github.com` 均 429；`ghfast.top` 镜像可正常下载 10.8MB zip。

## 处理

1. 备份 `php-web.Dockerfile` → `php-web.Dockerfile.bak.gh429-20260817_2230`。
2. 第 37 行 Phalcon 下载源改为 `https://ghfast.top/https://github.com/phalcon/cphalcon/archive/refs/tags/v4.1.2.zip`。
3. 手动触发发布 `0b3ca19e`（CLI `deploy --git-id 0b3ca19e --with-cron`）。

## 发布与验证

- 发布结果：**SUCCESS**；容器切换 `youdianse-php:dev-0b3ca19ed7fa`（web/nginx/cron，dirty=false）；健康检查 HTTP 200 / Redis 1ms / Mongo 0ms。
- 构建耗时约 11 分钟（Phalcon 编译 146s + composer 371.8s + 镜像导出），层缓存恢复后后续发布会快。
- 新代码（0b3ca19e）验证：
  - `ConfigService::MAX_VALUE_BYTES = 65536`；
  - `ConfigRepository` 标量配置 >64KB → `配置内容过大，请勿粘贴带图片的文档`；SEO异常验证 配置 JSON >64KB → `SEO异常验证配置内容过大`；
  - `VipRuleRepository` 复用 `ConfigService::MAX_VALUE_BYTES`。
- 稳态：admin modules/home 0.26s、h5 system/info 0.28s、H5 首页 0.61s；Redis 配置缓存 7,073 字节。

## 遗留

- 测试服务器 `php-web.Dockerfile` 为本地修改（未提交到运维仓库，运维仓库另有 env/.env.dev 未提交改动）；如需长期生效，建议在运维仓库提交该镜像源变更，或把 Phalcon 源码包 vendored 进构建上下文，避免依赖公共镜像源。
- GitHub 429 为 IP 级限流，可能随时间恢复；保留 ghfast.top 镜像作为备用下载源。
- 线上后端若使用同一 Dockerfile，注意同样存在 GitHub 429 风险，建议同步镜像源改造后发布。

## 通知与提交

- 每步已发 `18game运维` 群（步骤 1-2）。
- 本地 Git 已提交（不 Push），commit 信息见提交结果通知。
