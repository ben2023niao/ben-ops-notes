---
id: "doc-803fd823e74f"
title: "Agent 工作日志 · main-image-tag-width"
date: "2026-06-11T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Docker", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-main-image-tag-width.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-main-image-tag-width.md"
sourceSha256: "40ea6dc26d2e57c3cf675a6f3499ec2877c403a4ece2cfd9563f42541475c809"
sourceSystem: "project-doc"
---

# Agent 工作日志 · main-image-tag-width

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606110000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20main-image-tag-width.md)

> 整理日期：2026-06-11 00:00｜日期依据：文件名日期

日期：2026-06-11
Agent：Codex
任务：修复 main 发布脚本镜像 tag 长度不一致

## 输入资料

- PRD：不涉及
- 需求 ID：OPS-DEPLOY
- 接口/契约：不涉及
- 团队可读文档：`infra/deploy/main-business-code-update.md`、`infra/deploy/spug-main-task-template.md`
- 其他：main 服务器 `docker manifest inspect ...:0244a4f` 返回 `no such manifest`

## 本次目标

1. 定位 main 发布时镜像 tag 找不到的真实原因。
2. 修复发布脚本默认 `IMAGE_TAG` 与 GitLab 镜像构建 tag 不一致的问题。
3. 更新运维文档，明确 main 镜像 tag 口径。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `infra/deploy/spug-main-update.sh` | 将部署脚本中的 `git rev-parse --short HEAD` 固定为 `--short=8`，对齐 GitLab `CI_COMMIT_SHORT_SHA` |
| `infra/deploy/main-business-code-update.md` | 补充 main 默认 `IMAGE_TAG` 必须使用 8 位短 SHA |
| `infra/deploy/spug-main-task-template.md` | 补充 Spug 模板中镜像 tag 口径 |

## 核心决策

1. 不要求发布人员手工填写 `IMAGE_TAG`，由脚本默认取 main 当前 8 位短 SHA。
2. `compose pull` 仍然先于 `compose down`，确保镜像不存在时不停止现有业务容器。
3. 本次只改发布链路，不涉及业务代码、数据库和 API 契约。

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 影响 main 发布脚本的默认镜像 tag 计算 |
| 回滚 | 可回滚本次脚本提交；也可临时显式传入 `IMAGE_TAG=<8位短SHA>` |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `sh -n infra/deploy/spug-main-update.sh` | 通过 |
| `git diff --check` | 通过 |

## 前端字段变更

不涉及前端字段变更。

## 风险与待办

1. 需要 main pipeline 成功推送 `kickoff-backend:<8位短SHA>` 和 `kickoff-frontend:<8位短SHA>` 后，服务器再执行发布。
2. GitLab 自动触发 Spug 的权限问题仍需单独处理；当前可走服务器手动执行脚本。
