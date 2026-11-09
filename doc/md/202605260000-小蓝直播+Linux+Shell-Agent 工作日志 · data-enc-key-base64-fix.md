---
id: "doc-8dbe65d78542"
title: "Agent 工作日志 · data-enc-key-base64-fix"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "Go", "监控告警", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-data-enc-key-base64-fix.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-data-enc-key-base64-fix.md"
sourceSha256: "4b03ca168cd4f640e7cf1f4c6fccd7356b9e1d32c676bbbda0306ef6c6f9aff5"
sourceSystem: "project-doc"
---

# Agent 工作日志 · data-enc-key-base64-fix

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605260000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BLinux%2BShell-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20data-enc-key-base64-fix.md)

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：修复 APP_DATA_ENC_KEY base64 配置后 stream_key 加密未配置

## 输入资料

- PRD：不涉及业务需求变更
- 需求 ID：OPS-001
- 团队可读文档：`infra/deploy/README.md`、`docs/operations/secrets-management.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：线上 `kickoff-admin` 创建直播间提示 `stream_key 加密未配置`

## 本次目标

1. 确认线上 env 是否已注入到 systemd 进程。
2. 定位 base64 密钥与 Go AES key 长度判断不一致的问题。
3. 让 `APP_DATA_ENC_KEY` 同时支持 raw 32 字节和 base64 编码的 32 字节。
4. 让部署脚本自动同步 systemd unit，避免 unit 模板变更不生效。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/pkg/cryptox/aes.go` | 新增 `ParseAES256Key`，兼容 raw/base64 AES-256 key |
| `services/go-app/internal/pkg/cryptox/aes_test.go` | 覆盖 raw、标准 base64、无 padding base64 和非法长度 |
| `services/go-app/internal/http/router/admin.go` | admin 服务装配使用 `ParseAES256Key` |
| `services/go-app/internal/http/router/public.go` | public 服务装配使用 `ParseAES256Key` 并保留无效 key 告警 |
| `infra/deploy/deploy.sh` | deploy 时同步 systemd unit 到 `/etc/systemd/system/` |

## 核心决策

1. 保留 raw 32 字节兼容性，同时支持 `openssl rand -base64 32` 生成的配置格式。
2. 不在日志或文档中记录真实 secret，只检查变量名和长度。
3. systemd unit 模板改动必须由 deploy 自动安装，不能依赖一次性 bootstrap。

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要重新 deploy，让新二进制和新版 unit 安装到服务器 |
| 回滚 | 可回滚到上一 commit；但 base64 key 会再次失效，除非改成 raw 32 字节 |
| 密钥 | 不需要轮换；现有 base64 key 可继续使用 |
| 备份恢复 | 不涉及 |
| 观测 | public router 对无效 enc key 继续输出告警 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 已确认线上进程存在 `APP_DATA_ENC_KEY` / `APP_DATA_HMAC_KEY`，失败根因是 base64 字符串长度不等于 32。 |
| 红队质疑 | 如果只修服务器 env 而不修代码，下一次按文档生成 base64 key 仍会复发；因此必须补解析函数和测试。 |
| 合入判断 | 允许合入；修复范围集中在配置解析和部署同步，无真实 secret 入库或入 git。 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented |
| Project Decision | pending-review |
| 项目级完成依据 | `docs/qa/project-acceptance.md` |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/pkg/cryptox ./internal/http/router` | 通过 |
| `docs/qa/acceptance-evidence.md` | 本次不涉及业务验收记录变更 |
