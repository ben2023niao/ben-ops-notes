---
id: "doc-623a7592652b"
title: "测试环境 albwhite 本地维护与发布覆盖修复记录"
date: "2026-07-30T16:14:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Redis", "自动化", "安全运维"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-1614-%E3%80%90%E4%BF%AE%E5%A4%8DBug%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83alb_white%E6%9C%AC%E5%9C%B0%E7%BB%B4%E6%8A%A4%E4%B8%8E%E5%8F%91%E5%B8%83%E8%A6%86%E7%9B%96%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-1614-【修复Bug】测试环境alb_white本地维护与发布覆盖修复记录.md"
sourceSha256: "63c7f8fb9bea4f27d7ae9f2538f0e3483b8bd48e4217cb6a8ead66dd1be97948"
sourceSystem: "project-doc"
---

# 测试环境 albwhite 本地维护与发布覆盖修复记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607301614-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%20albwhite%20%E6%9C%AC%E5%9C%B0%E7%BB%B4%E6%8A%A4%E4%B8%8E%E5%8F%91%E5%B8%83%E8%A6%86%E7%9B%96%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-30 16:14｜日期依据：文件名日期

环境标签：测试环境

文档日期：2026-07-30 16:14
环境：游点涩测试环境（dev 分支）
分类：修复Bug

## 背景

测试环境后端发布失败，CICD 页面提示：

```text
业务代码存在本地未提交修改，默认拒绝发布。
M alb_white.txt
```

研发反馈曾在测试服务器手工执行 `docker cp`，把 `alb_white.txt` 和 `alb_white_secret.txt` 复制进容器，并修正容器内权限。重新发布后，容器里的 `alb_white.txt` 又被覆盖。

本次需要新增的测试环境白名单内容：

```text
# ===== 桃色西遊 =====
stgpf.xy-game.com
```

## 根因

`docker cp` 只修改当前容器文件。测试环境重新发布时会重建 PHP 镜像和容器，镜像里的业务代码文件会重新进入容器，因此手工复制进去的内容会被覆盖。

同时，`alb_white.txt` 在业务仓库里是已跟踪文件；如果直接在测试服务器业务目录修改它，业务仓库会变成 dirty，网页发布会按保护策略拒绝继续发布。

## 修复策略

这两个 txt 明确改为测试服务器本地运行文件，不再提交业务代码仓库。业务仓库里即使存在同名文件，测试环境运行也不以仓库版本为准。

```text
cicd-web/runtime/app-local-files/alb_white.txt
cicd-web/runtime/app-local-files/alb_white_secret.txt
```

发布流程改造：

1. 发布前检查服务器本地源目录。
2. 如果业务目录里只有这两个受保护 txt 出现 dirty，先迁移到服务器本地源目录，再恢复业务 Git 工作区。
3. 拉取或切换业务代码后，只确认服务器本地源文件存在，不再依赖业务仓库里的本地改动。
4. 容器重建后，把服务器本地源文件覆盖到 web/cron 容器内同名路径。
5. 容器内文件统一修正为 `root:www-data 0640`。
6. 健康检查成功后，再刷新 runtime 备份。

## 改动范围

运维仓库：

```text
cicd-web/config/settings.json
cicd-web/config.py
cicd-web/core.py
docs/2026-07-22-0910-【优化】测试环境业务本地密钥文件发布保护.md
docs/2026-07-30-1614-【修复Bug】测试环境alb_white本地维护与发布覆盖修复记录.md
README.md
ops/test/README.md
workbench/CURRENT_STATE.md
workbench/CURRENT_TASK.md
```

业务仓库：

```text
不提交业务仓库。
不把 alb_white.txt 和 alb_white_secret.txt 的测试环境本地新增内容作为业务代码变更发布。
```

## 服务器维护方法

以后测试环境需要新增白名单时，只维护测试服务器本地源文件：

```bash
cd /opt/docker-youdianse-php
install -d -m 700 cicd-web/runtime/app-local-files
printf '\n# ===== 桃色西遊 =====\nstgpf.xy-game.com\n' >> cicd-web/runtime/app-local-files/alb_white.txt
chmod 0600 cicd-web/runtime/app-local-files/alb_white.txt
```

注意：

- 不要把 `alb_white_secret.txt` 内容写入文档、聊天、Git 或普通日志。
- 不要在业务仓库里提交这两个 txt 的测试环境本地内容。
- 不要只用 `docker cp` 改容器；容器重建后仍会丢失。

## 验证项

本地验证：

```bash
python3 -m py_compile cicd-web.py cicd-web/core.py cicd-web/config.py cicd-web/telegram.py cicd-web/command.py
```

结果：

```text
通过。
```

服务器验证：

```bash
test -f /opt/docker-youdianse-php/cicd-web/runtime/app-local-files/alb_white.txt
test -f /opt/docker-youdianse-php/cicd-web/runtime/app-local-files/alb_white_secret.txt
git -C /opt/docker-youdianse-php/src/youdianse-php status --short
docker exec youdianse-dev-php-web grep -n 'stgpf.xy-game.com' /var/www/html/youdianse-php/alb_white.txt
docker exec youdianse-dev-php-web stat -c '%U:%G %a %n' /var/www/html/youdianse-php/alb_white.txt /var/www/html/youdianse-php/alb_white_secret.txt
```

结果：

```text
运维仓库提交：cdfa030 修复测试环境本地保护文件发布覆盖
测试服务器运维仓库：/opt/docker-youdianse-php -> cdfa030
业务仓库：/opt/docker-youdianse-php/src/youdianse-php -> dev，clean
业务 git id：6f0518ea1a1bb56e8f3e1a31fc2c46e8de77ab3f
镜像 tag：dev-6f0518ea1a1b
发布日志：cicd-web/logs/游点涩-后端-Webhook-自动发布-youdianse-test-38.92.8.34-dev-latest-20260730-162145.log.txt
发布结果：SUCCESS
HTTP：后台 200，CICD 200
Session：writable
Redis：open
MongoDB：open
Dirty：false
```

容器复查：

```text
web 容器 alb_white.txt：包含 # ===== 桃色西遊 ===== 和 stgpf.xy-game.com
cron 容器 alb_white.txt：包含 # ===== 桃色西遊 ===== 和 stgpf.xy-game.com
web 容器权限：alb_white.txt root:www-data 640；alb_white_secret.txt root:www-data 640
cron 容器权限：alb_white.txt root:www-data 640；alb_white_secret.txt root:www-data 640
```

过程异常和处置：

```text
首次重启 CICD Web 时进程匹配过宽导致 SSH 会话断开；复查原进程仍在，HTTP 200，未造成服务中断。
随后使用精确 PID 重启。
自动发布首次触发返回 401；原因是重启 CICD Web 时未加载 runtime/secrets.env。
随后带 secrets.env 重启 CICD Web，自动发布恢复正常。
```

## 回滚

如发布器改造异常：

1. 回滚运维仓库本次提交。
2. 重新拉取运维仓库到测试服务器。
3. 重启 CICD Web。
4. 使用发布前的 `cicd-web/runtime/app-local-file-backups/` 备份文件恢复。

## 结论

本次修复后，`alb_white.txt` 和 `alb_white_secret.txt` 在测试环境按服务器本地运行文件维护。发布流程会自动把本地源文件同步进容器，业务仓库保持 clean，避免再次出现“本地未提交修改导致发布失败”或“发布后 docker cp 内容被覆盖”的问题。
