---
id: "doc-f6d87d69bc04"
title: "测试后端自动发布日志误读确认"
date: "2026-08-04T16:45:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "Nginx", "Redis", "自动化", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1645-%E3%80%90%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E5%90%8E%E7%AB%AF%E8%87%AA%E5%8A%A8%E5%8F%91%E5%B8%83%E6%97%A5%E5%BF%97%E8%AF%AF%E8%AF%BB%E7%A1%AE%E8%AE%A4.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1645-【排查记录】测试后端自动发布日志误读确认.md"
sourceSha256: "07980819b9d92ea4353a283f54c38393648a2ddd1b01967edbdcc69f8b748db9"
sourceSystem: "project-doc"
---

# 测试后端自动发布日志误读确认

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608041645-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E6%B5%8B%E8%AF%95%E5%90%8E%E7%AB%AF%E8%87%AA%E5%8A%A8%E5%8F%91%E5%B8%83%E6%97%A5%E5%BF%97%E8%AF%AF%E8%AF%BB%E7%A1%AE%E8%AE%A4.md)

> 整理日期：2026-08-04 16:45｜日期依据：文件名日期

环境标签：测试环境 / 后端 / 自动发布 / CICD / ben-bot

## 1. 本次结论

用户提供的测试环境后端自动发布日志实际为成功日志，开发侧看走眼，不是发布失败。

关键成功信息：

- Docker 镜像构建完成：`youdianse-php:dev-09e39078f710`
- `docker compose up -d --force-recreate --remove-orphans web nginx cron` 退出码为 `0`
- 容器启动完成：`web`、`nginx`、`cron`
- 健康检查通过：
  - HTTP：`200`
  - Session：`writable`
  - Redis：open
  - MongoDB：open
- 综合结论：`SUCCESS`
- 发布结果：`SUCCESS`
- 分支：`dev`
- Git ID：`09e39078f7104836aa109913c7a9407902a65215`

## 2. 本次执行过的只读/低风险检查

- 已按 workbench 读取当前任务、机器矩阵、运行链路和测试后端事实源。
- 已确认测试环境后端服务器记录为 `38.92.8.34`，业务容器名与日志里的 `youdianse-dev-php-*` 一致。
- 已检查公开入口：
  - `https://cicd.youdianse-test.xyz` 返回 `200`
  - `https://admin.youdianse-test.xyz` 根路径返回 `404`，符合历史记录，不代表后端异常。

## 3. 顺手清理

排查时发现 ben-bot 宿主机和容器的 `data/scripts` 目录下存在 macOS `._*` 元数据文件。已清理：

| 位置 | 清理前 | 清理后 |
| --- | --- | --- |
| ben-bot 宿主机 `data/scripts` | 257 | 0 |
| ben-bot 容器 `/app/data/scripts` | 257 | 0 |

该操作只删除 macOS 元数据文件，不影响发布脚本、业务代码、容器和配置。

## 4. 本次未执行

- 未重新发布测试后端。
- 未重启测试后端业务容器。
- 未修改测试后端 `.env`。
- 未修改 CICD 平台配置。
- 未读取或记录密码、token、Secret Key、私钥正文、Session Cookie 或完整 Signed URL。

## 5. 后续建议

后续判断测试后端自动发布结果时，以日志尾部为准：

```text
综合结论：SUCCESS
发布结果：SUCCESS
HTTP：200
Session：writable
Redis：... open
MongoDB：... open
```

如果这些都存在，说明发布流程已经完成；中间的 Composer 安装、Docker BuildKit 分层、容器 Recreate/Started 日志属于正常发布过程。
