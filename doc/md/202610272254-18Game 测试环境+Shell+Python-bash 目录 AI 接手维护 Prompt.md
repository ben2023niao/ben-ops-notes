---
id: "doc-25db45ac3e5c"
title: "bash 目录 AI 接手维护 Prompt"
date: "2026-10-27T22:54:14+08:00"
dateSource: "文件创建/修改时间"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "监控告警", "自动化", "CDN", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/bash/doc/prompt.md"
sourcePath: "~/Desktop/18game_devops/devops/bash/doc/prompt.md"
sourceSha256: "a4c8d76acea2b02228b77fcd3659127c05fdc778ab21e28adb3dcb95c32754ac"
sourceSystem: "project-doc"
---

# bash 目录 AI 接手维护 Prompt

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610272254-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-bash%20%E7%9B%AE%E5%BD%95%20AI%20%E6%8E%A5%E6%89%8B%E7%BB%B4%E6%8A%A4%20Prompt.md)

> 整理日期：2026-10-27 22:54｜日期依据：文件创建/修改时间

你正在接手 `devops/bash` 目录。这里收集的是运维 Shell/Python 辅助脚本，覆盖 AWS 成本统计、Codex 用量报账、历史 CI/CD、Mongo 备份、Glances 部署、后端更新等任务。这个目录不是单一项目，而是一组偏临时和半自动化的运维脚本集合。

## 0. 关联文档

- 仓库总入口：`.github/copilot-prompt-instructions.md`
- 服务器上下文：`devops/ai_context/doc/prompt.md`
- Python 多项目索引：`devops/python/doc/prompt.md`
- PHP 工具站：`devops/php/doc/prompt.md`
- 周报生成：`work-运维部工作进度-周报/doc/prompt.md`

如果 Bash 脚本会被 ben-bot、PHP 页面、服务器 crontab 或周报流程引用，改动前要同步确认对应项目文档和真实运行路径，避免只改仓库副本却没有影响线上脚本。

## 1. 目录定位

- 目录路径：`devops/bash`
- 主要类型：Shell 脚本、Python 脚本、说明文档、少量截图素材
- 运行场景：本机、服务器、AWS CloudShell
- 维护重点：先判断脚本运行环境，再修改

当前实际可见子目录包括：

- `Codex用量报账`
- `aws-cloudshell`

工作区里可能存在一些历史脚本的删除状态，例如 `18game-cicd`、Mongo、Glances、CDN 等路径。不要擅自恢复或删除这些状态，除非用户明确要求。

## 2. 已知子项目

### `Codex用量报账`

文件：

- `README.md`
- `codex_usage_report.sh`

用途：

- 生成 Codex 月度用量报账材料。
- 默认是演示报表，带 `SIMULATED / NOT FOR REIMBURSEMENT` 标识。
- `--real` 模式会调用本机 `cusage codex monthly`，如果不存在会提示安装。

常用命令：

```bash
./devops/bash/Codex用量报账/codex_usage_report.sh --since 20260601 --until 20260630
./devops/bash/Codex用量报账/codex_usage_report.sh --real --since 20260601 --until 20260630
```

维护注意：

- 不要把演示报表伪装成真实报销证据。
- 如果改报表格式，保留 demo 标记。
- 日期格式是 `YYYYMMDD`。

### `aws-cloudshell`

文件类型：

- AWS 成本统计 Python 脚本
- AWS 成本统计 Shell 脚本
- S3 打标签脚本
- 使用说明
- 截图示例

用途：

- 在 AWS CloudShell 里统计 S3、EC2、CloudFront 成本。
- 部分 Python 脚本会把结果发送到 Telegram。
- S3 成本按桶分组依赖 Cost Allocation Tag，需要先给桶打 `Name` 标签并在 Billing 中激活。

典型任务：

- S3 存储桶成本统计
- EC2 实例成本统计
- CloudFront 分发成本统计
- 给 S3 bucket 写入 Name 标签

维护注意：

- CloudShell 通常自带 AWS 凭证和 boto3。
- 不要把 AWS 凭证写进脚本。
- Telegram token/chat id 应使用环境变量或运行时安全注入。
- Cost Explorer 的 Resource-level data 可能需要开启并等待生效。

## 3. 可能存在的历史脚本域

即使当前工作区中部分文件处于删除状态，后续用户仍可能问到这些历史方向：

- `18game-cicd`：18game 前后端、H5、PC、PHP 发布脚本。
- `youdianse-docker-cicd`：游点涩 H5 Docker 发布脚本，后续主线已迁移到 `devops/python/ben-bot/data/scripts/...`。
- `mongo`：Mongo 备份到 Telegram。
- `glances-*`：Glances 监控客户端部署和告警脚本。
- `测试环境后端php代码自动化更新脚本`：测试后端 PHP 更新脚本。

如果用户要求恢复或维护这些历史脚本：

1. 先看 `git status` 和 `git log`。
2. 不要直接 `git checkout --` 恢复所有删除。
3. 只恢复用户明确指定的脚本。
4. 对比当前 ben-bot 是否已有替代实现。

## 4. 安全规则

这个目录很容易接触敏感内容，必须遵守：

- 不读取或输出私钥、token、AWS secret、数据库密码。
- 不把 Telegram Bot Token 写入 prompt 或 README。
- 不把 Mongo 备份内容提交。
- 不把 AWS CloudShell 临时凭证写入文件。
- 不用 `rm -rf`、`docker system prune`、清桶等破坏性命令，除非用户明确要求且目标确认。

敏感扫描建议：

```bash
rg -n "BEGIN .*PRIVATE KEY|AKIA|AWS_SECRET|TG_BOT_TOKEN|TELEGRAM.*TOKEN|password|passwd|mongodb://" devops/bash
```

如果扫到历史明文，不要在回复里粘贴值，只说文件路径和风险。

## 5. 开发规范

Shell 脚本建议：

- 开头使用 `#!/usr/bin/env bash`
- 使用 `set -euo pipefail`
- 参数解析提供 `--help`
- 关键变量集中在顶部
- 对外部命令做存在性检查
- 输出分步骤日志
- 删除、覆盖、重启前明确目标

Python 脚本建议：

- 使用环境变量读取 token/key
- 网络请求设置 timeout
- 对 Telegram 发送失败做异常处理
- 成本统计输出要标注时间区间
- 大消息分段发送

## 6. 验证清单

Shell 语法：

```bash
bash -n devops/bash/Codex用量报账/codex_usage_report.sh
```

Python 语法：

```bash
python3 -m py_compile devops/bash/aws-cloudshell/*.py
```

实际运行前确认：

- 当前目录正确
- 运行环境是本机、服务器还是 CloudShell
- AWS 当前账号是否正确
- 时间区间是否正确
- TG 通知目标是否正确

## 7. 常见坑

### CloudShell 成本为 0

可能原因：

- Cost Explorer 数据延迟。
- Resource-level data 未开启。
- S3 tag 刚激活未等待 24 小时。
- 查询时间范围不对。

### Telegram 发送失败

可能原因：

- token/chat id 错误。
- bot 不在群里。
- 消息太长。
- Markdown/HTML parse_mode 未转义。

### 用户让“提交脚本”

先检查是否有无关删除状态。当前仓库可能有很多 `D` 状态不是本次改动产生，不要一起提交。

## 8. AI 接手流程

1. 先确认用户说的是哪个子目录或脚本。
2. `git status --short --branch` 看工作区。
3. 读对应 README/脚本头部。
4. 判断运行环境。
5. 小范围修改。
6. 跑 `bash -n` 或 `py_compile`。
7. 如果涉及真实云账号或 Telegram，只做 dry-run 或让用户确认。
8. 最终说明修改文件、验证命令和未执行的高风险动作。
