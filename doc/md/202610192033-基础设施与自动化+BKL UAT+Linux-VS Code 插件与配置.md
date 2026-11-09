---
id: "doc-82ddc365cfaf"
title: "VS Code 插件与配置"
date: "2026-10-19T20:33:32+08:00"
dateSource: "文件创建/修改时间"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Linux", "Shell", "Python", "Docker", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/workbench-kit-%E9%80%9A%E7%94%A8AI%E5%B7%A5%E4%BD%9C%E5%8F%B0/docs/05-VSCode%E6%8F%92%E4%BB%B6%E4%B8%8E%E9%85%8D%E7%BD%AE.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/workbench-kit-通用AI工作台/docs/05-VSCode插件与配置.md"
sourceSha256: "d7cbc182d3699740aaeae1b42a511557baf0f58f04333d306a9444056253f866"
sourceSystem: "project-doc"
---

# VS Code 插件与配置

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610192033-%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E4%B8%8E%E8%87%AA%E5%8A%A8%E5%8C%96%2BBKL%20UAT%2BLinux-VS%20Code%20%E6%8F%92%E4%BB%B6%E4%B8%8E%E9%85%8D%E7%BD%AE.md)

> 整理日期：2026-10-19 20:33｜日期依据：文件创建/修改时间

目标：让 VS Code 成为 Workbench 的操作台，而不是插件仓库。
插件按「必装 / 推荐 / 可选」分三档，先装必装，跑顺了再加。

## 1. 工作区怎么开

推荐直接打开项目根目录：

```bash
code /path/to/your-project
```

如果项目分多个仓库，用多根工作区：

```bash
code --add /path/to/project-a --add /path/to/project-b
```

保存为 `project.code-workspace`，放到项目外层，不要提交到业务仓库。

## 2. 必装插件

| 插件 | 扩展 ID | 作用 |
| --- | --- | --- |
| GitLens | `eamodio.gitlens` | 看每行是谁改的、提交历史、分支对比 |
| Git Graph | `mhutchie.git-graph` | 图形化看提交树、切分支、cherry-pick |
| Markdown All in One | `yzhang.markdown-all-in-one` | 目录、列表、快捷键、预览 |
| Markdown Preview Mermaid | `bierner.markdown-mermaid` | 预览架构图、流程图 |
| YAML | `redhat.vscode-yaml` | YAML 校验、Schema 提示 |
| Docker | `ms-azuretools.vscode-docker` | 看容器、镜像、compose、日志 |
| Remote - SSH | `ms-vscode-remote.remote-ssh` | 直接编辑服务器文件、开远程终端 |
| Python | `ms-python.python` | Python 运行、调试、环境选择 |
| Pylance | `ms-python.vscode-pylance` | 类型提示、跳转、补全 |
| EditorConfig | `editorconfig.editorconfig` | 统一缩进、换行、编码 |

这 10 个覆盖 80% 的日常：代码、Git、Markdown、YAML、Docker、远程服务器。

## 3. 推荐插件

| 插件 | 扩展 ID | 作用 |
| --- | --- | --- |
| Error Lens | `usernamehw.errorlens` | 错误直接显示在行尾 |
| Todo Tree | `gruntfuggly.todo-tree` | 汇总 TODO / FIXME |
| ShellCheck | `timonwong.shellcheck` | Shell 脚本静态检查 |
| markdownlint | `DavidAnson.vscode-markdownlint` | Markdown 格式检查 |
| REST Client | `humao.rest-client` | 在编辑器里发 HTTP 请求，测 API |
| Dev Containers | `ms-vscode-remote.remote-containers` | 用容器做开发环境 |

## 4. AI 插件怎么选

不要同时开多个“会自动改文件”的 Agent，容易互相覆盖。
选一个主力，其他只做问答。

### 4.1 GitHub Copilot

| 项 | 说明 |
| --- | --- |
| 扩展 | `github.copilot`、`github.copilot-chat` |
| 优点 | 安装即用，补全最强，和 VS Code 集成好 |
| 缺点 | 付费，企业网络可能受限 |
| 适合 | 日常写代码、补全、解释代码 |

配置：登录 GitHub 账号即可，不需要自己填 API Key。

### 4.2 Continue

| 项 | 说明 |
| --- | --- |
| 扩展 | `continue.continue` |
| 优点 | 开源，可接 OpenAI / DeepSeek / Anthropic / 本地 Ollama |
| 缺点 | 需要自己配模型和 Key |
| 适合 | 想统一接多家模型、或走内网模型 |

配置思路：

1. 安装扩展
2. 打开 Continue 侧边栏 → Settings
3. 选择 Provider（OpenAI Compatible / Anthropic / Ollama）
4. 填 Base URL、Model、API Key
5. Key 用环境变量或插件密钥存储，不要写进仓库

### 4.3 Cline / Roo Code

| 项 | 说明 |
| --- | --- |
| 扩展 | Cline：`saoudrizwan.claude-dev` |
| 优点 | 能读文件、改文件、跑命令，适合长任务 |
| 缺点 | 权限大，必须配合 `AGENTS.md` 和人工确认 |
| 适合 | 有明确 plan 的重构、批量修改、排查 |

使用建议：

- 只在一个干净分支上开
- 先让它读 `AGENTS.md` 和 `workbench/START_HERE.md`
- 要求它先输出 plan，再执行
- 高风险命令必须人工确认
- 每步看 diff，不要一路点同意

### 4.4 OpenAI Codex

Codex 可以在 IDE / 终端里按 `AGENTS.md` 工作。建议：

- 在项目根目录放 `AGENTS.md`
- 先让它跑只读检查
- 要求每步发通知、最后提交 Git
- 用 `workbench/scripts/context_pack.py` 控制上下文

具体安装方式以你账号可用的 Codex 版本为准。

### 4.5 Claude Code / 其他终端 Agent

同样适用：

- 项目根目录放 `AGENTS.md`
- 先读 Workbench
- 先 plan 后执行
- 高风险操作人工确认

## 5. AI 插件对比

| 能力 | Copilot | Continue | Cline | Codex |
| --- | --- | --- | --- | --- |
| 代码补全 | 强 | 中 | 中 | 中 |
| 多模型 | 否 | 强 | 强 | 取决于账号 |
| 自动改文件 | 中 | 弱 | 强 | 强 |
| 自动跑命令 | 弱 | 弱 | 强 | 强 |
| 配置成本 | 低 | 中 | 中 | 中 |
| 适合 Workbench | 中 | 强 | 强 | 强 |

结论：

- 日常补全：Copilot
- 多模型 / 内网模型：Continue
- 长任务自动执行：Cline 或 Codex
- 不要四个一起开

## 6. `.vscode` 配置说明

安装器 `--with-vscode` 会生成：

```text
.vscode/
├── extensions.json   推荐插件
├── settings.json     项目设置
└── tasks.json        快捷任务
```

### extensions.json

团队统一推荐插件。打开项目时 VS Code 会提示安装。

### settings.json

只放项目级设置：

- 排除 `__pycache__`、`dist`、`vendor`
- Git 自动 fetch
- Markdown 自动换行
- YAML 校验
- Python 基础类型检查

不要放个人主题、字体、快捷键。

### tasks.json

已内置：

- `workbench: check`
- `workbench: context`
- `git: status`

运行方式：`Cmd/Ctrl + Shift + P` → `Tasks: Run Task`。

## 7. 推荐设置

```json
{
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.DS_Store": true
  },
  "search.exclude": {
    "**/dist": true,
    "**/vendor": true,
    "**/.git": true
  },
  "git.autofetch": true,
  "git.confirmSync": false,
  "markdown.preview.breaks": true,
  "[markdown]": {
    "editor.wordWrap": "on"
  },
  "yaml.validate": true,
  "python.analysis.typeCheckingMode": "basic",
  "editor.formatOnSave": false
}
```

`editor.formatOnSave` 默认关闭，避免不同格式化插件互相打架。项目有统一格式化工具时再打开。

## 8. 远程服务器

用 Remote - SSH：

1. `Cmd/Ctrl + Shift + P` → `Remote-SSH: Connect to Host`
2. 输入 `user@host`
3. 打开 `/opt/...` 目录
4. 终端直接在服务器上执行

建议：

- 只读排查用普通账号
- 写操作走堡垒机
- 不在远程窗口里保存密码
- 用完断开

## 9. 秘密检查

推荐在本地装 `gitleaks`：

```bash
brew install gitleaks
gitleaks detect --source . --no-git
```

提交前也可以跑：

```bash
gitleaks protect --staged
```

没有 gitleaks 时，至少跑项目自己的 `make check` 或 `workbench/scripts/check.py`。

## 10. 常见问题

| 问题 | 处理 |
| --- | --- |
| 插件太多，VS Code 变慢 | 只留必装 + 一个 AI 插件 |
| AI 改了不该改的文件 | 用 Git diff 审核，开新分支 |
| Remote SSH 连不上 | 检查网络、账号、堡垒机、端口 |
| Markdown 图不显示 | 装 Mermaid 预览插件 |
| YAML 一直报红 | 检查缩进、Schema、`---` 分隔 |
| Python 找不到解释器 | `Cmd/Ctrl + Shift + P` → `Python: Select Interpreter` |
