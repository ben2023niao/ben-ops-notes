---
id: "doc-65061b72e7b0"
title: "测试环境后端 Webhook 自动部署失效与 CICD 密钥加载修复"
date: "2026-10-20T21:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "安全运维"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-20-2100-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%90%8E%E7%AB%AFWebhook%E8%87%AA%E5%8A%A8%E9%83%A8%E7%BD%B2%E5%A4%B1%E6%95%88%E4%B8%8ECICD%E5%AF%86%E9%92%A5%E5%8A%A0%E8%BD%BD%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-20-2100-【问题排查】测试环境后端Webhook自动部署失效与CICD密钥加载修复.md"
sourceSha256: "53e05961126bffc5146509e10949a144e95e7dcee2b43ad83f32abeb20c4f4e2"
sourceSystem: "project-doc"
---

# 测试环境后端 Webhook 自动部署失效与 CICD 密钥加载修复

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610202100-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%90%8E%E7%AB%AF%20Webhook%20%E8%87%AA%E5%8A%A8%E9%83%A8%E7%BD%B2%E5%A4%B1%E6%95%88%E4%B8%8E%20CICD%20%E5%AF%86%E9%92%A5%E5%8A%A0%E8%BD%BD%E4%BF%AE%E5%A4%8D.md)

> 整理日期：2026-10-20 21:00｜日期依据：文件名日期

## 一、现象

- 2026-10-20 20:49（北京时间）业务仓库 `dev` 分支已有新提交 `1379cc5d9670`，但测试环境没有自动发布。
- 测试后端手动发布后已到 `dev/1379cc5d9670`，说明业务代码和构建链路本身正常。
- 测试机 CICD 页面 `http://203.0.113.1:18090/` 返回 200，但 `/auto-deploy` 使用运行密钥探测返回 401。
- 最近一条成功的 Webhook 自动发布日志是 `2026-10-20 08:43 UTC`，之后没有新的 Webhook 日志。

## 二、根因

测试环境配置发布事故恢复期间，CICD 被直接以下面的形式重新启动：

```text
python3 /opt/docker-youdianse-php/cicd-web.py
```

这次启动没有经过 `cicd-web.sh start`，因此没有加载 root 专属的：

```text
/opt/docker-youdianse-php/cicd-web/runtime/secrets.env
```

进程中的 `YOUDIANSE_WEBHOOK_TOKEN` 为空，`config.py` 最终得到空的 webhook token，GitLab 的 Push Hook 请求返回 401。GitLab 侧并非没有事件，而是投递没有得到可用 token。

## 三、永久修复

修改 `cicd-web/config.py`：

- 在配置模块加载时统一读取 `cicd-web/runtime/secrets.env`；
- 已存在的环境变量优先，保留临时覆盖能力；
- 文件不存在或当前用户无权读取时不影响 CICD 启动；
- 不打印、不写入日志任何密钥值。

这样无论使用标准启动脚本还是直接执行 Python，Webhook token、Telegram token 和多群参数都能被正确加载。`cicd-web.sh start/restart` 仍保留原有的 `secrets.env` 加载逻辑，作为双保险。

该修复没有修改以下配置发布关键路径：

- `sync_runtime_config_no_build()` 的配置仓库同步逻辑；
- `cleanup_created_containers()` 的 Created 容器清理逻辑；
- 业务容器 `web/nginx/cron` 的发布顺序和健康检查。

## 四、现场恢复与验证

1. 使用标准脚本重启测试 CICD：

   ```bash
   cd /opt/docker-youdianse-php
   sudo ./cicd-web.sh restart
   ```

2. 验证页面和 Webhook：

   ```bash
   curl -sS -o /dev/null -w '%{http_code}\n' http://203.0.113.1:18090/
   ```

   预期：`200`。

   使用运行密钥请求一个非 `dev` 分支，做无副作用探测：

   ```bash
   curl -sS -X POST \
     -H 'Content-Type: application/json' \
     -d '{"ref":"refs/heads/nonexistent-branch"}' \
     "http://203.0.113.1:18090/auto-deploy/<YOUDIANSE_WEBHOOK_TOKEN>"
   ```

   预期：HTTP 200，响应 `status=ignored`，不会触发业务发布。

3. 验证最新业务版本：

   ```bash
   docker compose --profile cron ps
   ```

   实测结果：`web/nginx/cron` 均为 `running`，镜像为
   `youdianse-php:dev-1379cc5d9670`，业务仓库 `dev` HEAD 为
   `1379cc5d9670`，白名单文件 84 行，包含 `n4bs.wqdyapi.top`，健康检查为 SUCCESS。

## 五、后续操作

- 今后测试环境重启 CICD 统一使用 `sudo ./cicd-web.sh restart`；
- GitLab Push Hook 仍是 `dev` 自动发布入口；
- 若再次发现 `/auto-deploy` 返回 401，先检查 CICD 进程是否由标准脚本启动，以及 `secrets.env` 权限是否为 root 可读；
- 不要直接在群里或文档中粘贴 webhook token、Telegram token、SSH 私钥或发布密码。
