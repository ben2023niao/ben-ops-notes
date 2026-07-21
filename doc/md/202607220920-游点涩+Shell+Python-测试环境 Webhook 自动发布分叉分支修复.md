---
id: "doc-edac6ca8caf0"
title: "测试环境 Webhook 自动发布分叉分支修复"
date: "2026-07-22T09:20:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Docker", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-22-0920-%E3%80%90%E4%BF%AE%E5%A4%8DBug%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83Webhook%E8%87%AA%E5%8A%A8%E5%8F%91%E5%B8%83%E5%88%86%E5%8F%89%E5%88%86%E6%94%AF%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-22-0920-【修复Bug】测试环境Webhook自动发布分叉分支修复.md"
sourceSha256: "e4e8e91d3a633460598f60c291e4457ea4aa7fad9759a3989c902ae74c57dfd3"
sourceSystem: "project-doc"
---

# 测试环境 Webhook 自动发布分叉分支修复

> 来源文件：`~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-22-0920-【修复Bug】测试环境Webhook自动发布分叉分支修复.md`

> 整理日期：2026-07-22 09:20｜日期依据：文件名日期

环境标签：测试环境

文档日期：2026-07-22
环境：游点涩测试环境（dev 分支）
分类：修复Bug

## 问题

2026-07-22 21:37 测试环境 Webhook 自动发布失败：

```text
git -C /opt/docker-youdianse-php/src/youdianse-php pull --ff-only origin dev
fatal: Not possible to fast-forward, aborting.
```

测试服务器业务仓库状态：

```text
## dev...origin/dev [ahead 1, behind 15]
```

这表示本地 `dev` 与 `origin/dev` 已分叉。Webhook 自动发布虽然会清理工作区脏文件，但旧逻辑仍执行 `git pull --ff-only origin dev`，分叉分支无法快进，因此发布中断。

## 修复

`cicd-web/core.py` 的 `prepare_business_code()` 增加 Webhook 专用分支：

1. Webhook 自动发布仍先清理本地未提交改动和未跟踪文件。
2. `git fetch origin dev --tags` 后，不再对本地分叉分支执行 `pull --ff-only`。
3. 自动发布直接执行：

```bash
git -C /opt/docker-youdianse-php/src/youdianse-php checkout -B dev origin/dev
```

这样 Webhook 始终以远端 `origin/dev` 为准构建镜像，符合“自动发布只部署 Git 远端提交”的约束。

网页手动发布路径不启用这个强制对齐逻辑，仍保持工作区干净检查和 `pull --ff-only`，避免误覆盖人工排查中的本地分支。

## 验证

```bash
python3 -m py_compile cicd-web.py cicd-web/core.py cicd-web/webhook.py cicd-web/config.py cicd-web/telegram.py cicd-web/command.py
bash -n entrypoint/web-entrypoint.sh entrypoint/cron-entrypoint.sh entrypoint/cron-task-runner.sh entrypoint/queue-watchdog.sh cicd-web.sh
docker compose --profile cron config >/tmp/youdianse-dev-compose-webhook-fix.yml
git diff --check
```

测试服务器发布验证需确认：

- 发布日志出现 `Webhook 自动发布：以远端 origin/dev 为准重建本地 dev 分支`。
- 失败前的分叉状态被修复为业务仓库 `dev...origin/dev` 不再 ahead/behind。
- Webhook 自动发布结果为 `SUCCESS`。
