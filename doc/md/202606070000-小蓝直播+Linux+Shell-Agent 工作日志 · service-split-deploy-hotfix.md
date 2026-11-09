---
id: "doc-28414bcb1d2e"
title: "Agent 工作日志 · service-split-deploy-hotfix"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "Go", "Nginx", "监控告警", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-service-split-deploy-hotfix.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-service-split-deploy-hotfix.md"
sourceSha256: "4870787da70fd6149bc553bcb9a70a4fbbd01ae40beaf5ade813ba15938f4a91"
sourceSystem: "project-doc"
---

# Agent 工作日志 · service-split-deploy-hotfix

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606070000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BLinux%2BShell-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20service-split-deploy-hotfix.md)

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：服务拆分后 dev 部署权限与 nginx 反代热修

## 输入资料

- 需求 ID：LIVE-003、LIVE-012、ADM-908、ADM-912
- 运维文档：`infra/deploy/README.md`、`infra/deploy/runner-bootstrap.md`
- 部署脚本：`infra/deploy/deploy.sh`

## 问题

最新 `dev` 提交 `5168ab3` 的 `go-build` 和 `admin-ui-build` 成功，但 `deploy-dev`
失败在第 8 步重启 systemd 服务。根因是部署机 `/etc/sudoers.d/kickoff-deploy`
缺少 `kickoff-ws` 和 `kickoff-worker` 的 NOPASSWD restart / journal 权限。

服务重试成功后又暴露一个公网反代问题：`kickoff-ws` 已启动，但
`api-dev` 的 nginx `/ws/` 仍转发到 API 进程 8080，导致 public WS 返回 404。

## 处理

1. 在部署机补齐 `kickoff` 用户 sudoers：
   `kickoff-ws`、`kickoff-worker` restart 和 journal 权限。
2. retry GitLab `deploy-dev` job，重试 job `2520` 成功。
3. 在部署机 nginx 中新增 `api-dev /ws/ -> 203.0.113.1:8082`。
4. 给 `admin-dev /api/` 补 WebSocket upgrade 头，支撑
   `/api/v1/admin/ws/rooms/{id}/danmaku`。
5. 仓库同步更新 `deploy.sh` fail-fast sudo、runner-bootstrap sudoers 示例和部署 README。

## 验证

| 项目 | 结果 |
| --- | --- |
| GitLab deploy-dev retry job | `2520 success` |
| `kickoff-api` | active，公网 `/healthz` 200，`/readyz` 200 |
| `kickoff-admin` | active，后台 API 正常返回 401/200 |
| `kickoff-ws` | active，公网 `/ws/v1/client` 101 |
| `kickoff-worker` | active，任务日志正常 tick |
| 旧房间 WS | `/ws/v1/live/{room_id}` 101，并收到 `live.viewer.count.updated` |
| 后台监控 WS 新路径 | `/api/v1/admin/ws/rooms/{id}/danmaku` 无 token 返回 401 |
| Admin / H5 首页 | `admin-dev` 200，`web-dev` 200 |

## 风险

- 本次线上 nginx 变更是运行时配置热修，仓库已补文档口径；如果后续把 nginx
  配置纳入 IaC，应把 `/ws/` 和 admin `/api/` upgrade 规则固化进去。
