---
id: "doc-717201d59c8c"
title: "Workbench 工程化与 GitLab 部署"
date: "2026-10-19T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Shell", "Python", "Docker", "Nginx", "Redis", "CDN", "源码与配置"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8819%E6%97%A5-Workbench%E5%B7%A5%E7%A8%8B%E5%8C%96%E4%B8%8EGitLab/2026%E5%B9%B410%E6%9C%8819%E6%97%A5-Workbench%E5%B7%A5%E7%A8%8B%E5%8C%96%E4%B8%8EGitLab.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月19日-Workbench工程化与GitLab/2026年10月19日-Workbench工程化与GitLab.md"
sourceSha256: "31ec98b2f8a9c731548040c85a13665e12f03a4f8bd6f62504811a587912a589"
sourceSystem: "project-doc"
---

# Workbench 工程化与 GitLab 部署

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610190000-%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E4%B8%8E%E8%87%AA%E5%8A%A8%E5%8C%96%2BBKL%20UAT%2BShell-Workbench%20%E5%B7%A5%E7%A8%8B%E5%8C%96%E4%B8%8E%20GitLab%20%E9%83%A8%E7%BD%B2.md)

> 整理日期：2026-10-19 00:00｜日期依据：文件名日期

日期：2026-10-19
执行人：Ben（运维）
版本：v1

## 需求

1. 参考本地其他项目的 Workbench，给本仓库补工作台。
2. 本地项目工程化、模块化：统一入口、通知脚本、检查与部署命令。
3. 文档结构优化，保留按日期记录。
4. 堡垒机部署 GitLab，域名 `gitlab.evercare.id`，nginx 80/443 反代并加一层访问认证。
5. 本地仓库初始化 Git，项目名 `devops`。
6. 本地目录由 `blkuat` 改名为 `devops`；doc 下任务目录统一为「日期-事项」，主文档与目录同名。

## 执行步骤

1. 确认本地状态：初检时目录不是 Git 仓库，无远端提交。
2. 补 Workbench：任务、项目索引、机器矩阵、运行链路、模板、handoff。
3. 工程化：`scripts/notify.py`、`scripts/check_repo.py`、`scripts/sync.sh`、`Makefile`、模块 README。
4. 清理仓库内明文 token，改为读取 `/etc/blkuat/notify.env`（600）。
5. 文档索引与 README 更新。
6. 部署 GitLab（Docker，本机 8929）。
7. nginx 反代 + Basic 认证 + Let's Encrypt。
8. 本地 Git 初始化、验证、提交。
9. 推送到 `root/devops` main，复核远端分支。

## 关键决策

| 事项 | 决定 |
| --- | --- |
| GitLab 部署机 | 堡垒机 43.249.251.15 |
| 端口 | GitLab 只监听 `203.0.113.1:8929`，对外统一 443 |
| 证书 | Let's Encrypt webroot，复用 nginx 证书目录 |
| 访问控制 | 外层 Basic（ops）+ GitLab 账号 |
| 认证模式 | Cloudflare SSL 必须 Full / Full strict |

## 验证结果

- `make check`：通过（Python 语法、必需文件、工作台入口、明文秘密扫描）。
- 本地 GitLab：`203.0.113.1:8929/users/sign_in` 返回 200。
- 公网入口：带 Basic 认证返回 200，不带认证返回 401。
- 证书：`gitlab.evercare.id` 已签发，到期 2027-01-17，续期脚本每天 03:00 UTC 执行。
- GitLab 服务：nginx / puma / sidekiq / gitaly / postgresql / redis / gitlab-workhorse / gitlab-kas 全部 run。
- 远端分支：`git ls-remote origin` 返回 `fb98c6980e93a43d9c2204d07a53c8653c3d2b18 refs/heads/main`。
- 内存：Puma 改单进程后，堡垒机已用约 5.26G / 7.8G，可用约 2.68G。

## 踩坑与注意事项

- 堡垒机余量约 4.4G，GitLab 较重，需限制 Puma/Sidekiq 并观察内存。
- 外层 Basic 会拦截 git 客户端，需对 `info/refs`、`git-upload-pack`、`git-receive-pack` 放行，由 GitLab 自己认证。
- Puma `worker_processes=1` 会多占一份内存，4C8G 机器改为 0（单进程模式）。
- 修改 gitlab.rb 后 reconfigure 不一定重启 Puma，需要 `gitlab-ctl restart puma`。
- 服务器 cron 用 UTC，22:00（上海）= 14:00 UTC。
- 仓库内不再保留任何 bot token。

## 涉及文件

- `workbench/`
- `scripts/`
- `Makefile`
- `code/gitlab-项目运维代码仓库/`
- `2026年10月19日-Workbench工程化与GitLab.md`、`doc/README.md`

## 后续

- 观察 GitLab 内存一周，必要时扩内存或限制并发。
- 文档从 Google Doc 逐步迁移到 GitLab 仓库。
- 给开发同事开 GitLab 账号，关闭不必要的公开注册。
