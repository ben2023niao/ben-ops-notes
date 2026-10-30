---
id: "doc-a7184b43a8eb"
title: "Codex 当前模型说明与 MacBook 本地 AI 部署笔记"
date: "2026-10-31T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Shell", "Python", "Docker", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8831%E6%97%A5-Codex%E6%A8%A1%E5%9E%8B%E8%AF%B4%E6%98%8E%E4%B8%8EMac%E6%9C%AC%E5%9C%B0AI%E9%83%A8%E7%BD%B2/2026%E5%B9%B410%E6%9C%8831%E6%97%A5-Codex%E6%A8%A1%E5%9E%8B%E8%AF%B4%E6%98%8E%E4%B8%8EMac%E6%9C%AC%E5%9C%B0AI%E9%83%A8%E7%BD%B2.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月31日-Codex模型说明与Mac本地AI部署/2026年10月31日-Codex模型说明与Mac本地AI部署.md"
sourceSha256: "44f2122b7c2b5cdf6cc2928705678964af9d1d04f07ebd446447ad1b6369a3fb"
sourceSystem: "project-doc"
---

# Codex 当前模型说明与 MacBook 本地 AI 部署笔记

> 来源文件：`~/Projects/work/ops/devops/devops-bkl/doc/2026年10月31日-Codex模型说明与Mac本地AI部署/2026年10月31日-Codex模型说明与Mac本地AI部署.md`

> 整理日期：2026-10-31 00:00｜日期依据：文件名日期

日期：2026-10-31
设备：MacBook Air（Apple M5，24GB 统一内存）
用途：说明当前工作 AI 的实际模型与运行方式，并提供可在本机实施的离线/本地模型部署步骤。

## 结论

当前 Codex 工作会话不是在本机离线推理。根据本机 `~/.codex/config.toml`、`~/.codex/models.json`、当前会话记录和 `codex doctor` 的输出：

- 客户端：Codex CLI `0.164.0-alpha.11.1`，由 VS Code ChatGPT/Codex 扩展提供；ChatGPT 桌面应用版本为 `26.1021.31345`。
- 模型名称：`DeepSeek-Flash`。
- 模型标识：`deepseek-flash`。
- 模型提供方：自定义 provider `deepseek`。
- 接口：`https://api.deepseek.com/`，协议为 OpenAI 兼容的 `responses`。
- 推理强度：`high`。
- 模型目录最大上下文：`1,048,576` tokens。
- 当前会话有效上下文：`996,147` tokens，约为最大窗口的 95%。
- 输入能力：文本、图片。
- 其他能力：并行工具调用；模型目录给出的可用推理级别为 `low`、`high`、`max`。
- 当前配置关闭了 Codex 内置 web search。
- 当前 provider 不要求 OpenAI 登录，使用 API Key 方式认证。

这里的“当前工作 AI”指本机 Codex 配置实际调用的模型，不代表本机已经下载或运行了该模型的权重。DeepSeek-Flash 的推理仍通过远端 API 完成。

## 官方模型背景

截至 2026-10-31，OpenAI 官方模型页列出的 Work/Codex 推荐模型包括：

- **Astra**：面向最复杂、需要持续推理与判断的端到端工作。
- **GPT-6.1 Sol**：接近 Astra，适合长期、重复的代码/应用/文档工作，默认上下文 500,000 tokens。
- **GPT-6.1 Terra**：速度更快，适合日常写作、图像理解、电脑操作。
- **GPT-6 Luna**：适合高吞吐、边界清晰、可重复的提取、转换和聚焦编码任务。

官方模型页：[Models | ChatGPT Learn](https://learn.chatgpt.com/docs/models)

OpenAI 官方当前说明 Codex 可以使用本地 Ollama 或 LM Studio，通过 `--oss` 和 `--local-provider` 选择；未启用 `--oss` 时，当前配置会继续使用上面的远端 DeepSeek provider。

## 本机现状

| 项目 | 当前值 |
| --- | --- |
| 机型 | MacBook Air（Mac17,4） |
| 芯片 | Apple M5 |
| CPU | 10 核：4 个性能核 + 6 个能效核 |
| 架构 | arm64 |
| 统一内存 | 24GB |
| 系统 | macOS 26.6（25G72） |
| 根盘可用空间 | 约 772GB |
| Python | `/usr/bin/python3` 可用 |
| Homebrew | 未安装 |
| Ollama | 未安装 |
| LM Studio | 未安装 |
| 当前 Codex 模型 | `deepseek-flash`，远端 API |

因此当前状态是“Codex 工作流已可运行，但本地模型推理尚未部署”。

## 方案选择

### 推荐：Ollama + gpt-oss:20b

OpenAI 官方本地运行指南说明：

- `gpt-oss-20b` 适合至少 16GB VRAM 或统一内存的消费级设备，并明确适合 Apple Silicon。
- `gpt-oss-120b` 建议至少 60GB VRAM/统一内存，不适合这台 24GB MacBook Air。
- 两个模型默认使用 MXFP4 量化。

本机 24GB 统一内存满足 `gpt-oss:20b` 的最低建议，但实际可用内存还要扣除 macOS、浏览器、VS Code、Docker 等进程，建议首次运行时关闭高内存应用。

官方指南：[How to run gpt-oss locally with Ollama](https://developers.openai.com/cookbook/articles/gpt-oss/run-locally-ollama)

### 备选：LM Studio

如果更偏好图形界面和模型管理，可使用 LM Studio。安装后下载兼容模型、加载模型，并在 Developer/Local Server 页面启动 OpenAI 兼容服务。Codex 通过内置的 `lmstudio` 本地 provider 接入。

## Ollama 部署步骤

### 1. 安装 Ollama

从 Ollama 官方 macOS 安装包安装，放入 `/Applications`。本文不使用未经验证的第三方脚本或镜像。

安装后打开终端验证：

```bash
ollama --version
```

如果终端暂时找不到命令，先重新打开终端；不要重复安装多个版本。

### 2. 下载适合本机的模型

```bash
ollama pull gpt-oss:20b
```

下载完成后确认：

```bash
ollama list
```

预期能看到模型标识 `gpt-oss:20b`。不要拉取 `gpt-oss:120b`，24GB 统一内存不足以舒适运行。

### 3. 先验证独立运行

```bash
ollama run gpt-oss:20b
```

输入一个简单问题，确认能正常生成。可用 `/bye` 或 `Ctrl+D` 退出。此步只验证 Ollama，不涉及 Codex。

### 4. 验证本地 API

Ollama 通常监听 `203.0.113.1:11434`：

```bash
curl -fsS http://203.0.113.1:11434/api/tags
```

只要能返回模型列表，就说明本地 API 可用。不要把 11434 端口暴露到公网或不受信任的局域网。

### 5. 用 Codex 接入 Ollama

官方 Codex CLI 原生支持：

```bash
codex --oss --local-provider ollama -m gpt-oss:20b
```

首次运行可执行：

```bash
codex doctor
```

再让本地模型做一次无副作用测试：

```bash
codex --oss --local-provider ollama -m gpt-oss:20b \
  "只回复 READY，不要修改文件。"
```

如果成功返回 `READY`，说明 Codex → 本地 Ollama → gpt-oss 链路已打通。

### 6. 可选：建立独立本地 profile

不要把本地配置直接写入当前全局 `~/.codex/config.toml`，避免覆盖正在使用的 DeepSeek 配置。可创建独立文件：

```text
~/.codex/local-ollama.config.toml
```

示例见本文目录下的 `附件/local-ollama.config.toml`。

启动：

```bash
codex --profile local-ollama --oss --local-provider ollama
```

用完直接退出；不带 `--oss` 的下一次 Codex 启动仍使用原来的远端 DeepSeek 配置。

## LM Studio 备选步骤

1. 安装并打开 LM Studio。
2. 在模型搜索中下载适合 24GB 内存、4-bit/MXFP4 量化的模型。
3. 加载模型，在 Developer 页启动本地服务器，默认端口通常是 `1234`。
4. 查询模型 ID：

```bash
curl -fsS http://203.0.113.1:1234/v1/models
```

5. 使用返回的模型标识启动 Codex：

```bash
codex --oss --local-provider lmstudio -m "<模型标识>"
```

示例 profile 见 `附件/local-lmstudio.config.toml`。

## 自定义本地网关

如果使用 vLLM、LiteLLM、Hugging Face Responses 代理或其他本地网关，需要遵守 Codex 的当前协议要求：

- 自定义 provider 必须提供 Responses API 兼容接口。
- 官方说明当前 Codex 不支持仅 Chat Completions 的 `wire_api = "chat"`。
- 内置 provider ID `openai`、`ollama`、`lmstudio` 不能作为自定义 provider ID 重复定义。

基本结构：

```toml
model = "<本地模型标识>"
model_provider = "local_proxy"

[model_providers.local_proxy]
name = "Local Responses Proxy"
base_url = "http://203.0.113.1:8000/v1"
wire_api = "responses"
```

如果网关需要鉴权，应通过环境变量名或凭据命令提供，不要把真实 Token 写入仓库或配置示例。

官方配置页：[Advanced Configuration](https://learn.chatgpt.com/docs/config-file/config-advanced#custom-model-providers)

## 24GB MacBook 性能建议

- 优先 `gpt-oss:20b` 的 MXFP4 版本；这是本机最接近官方建议、同时具备代码与工具调用能力的选择。
- 首次运行前关闭不必要的 Chrome 标签、Docker Desktop、视频会议和大项目索引。
- 不要同时运行本地模型和多个大型容器；统一内存会和系统、编辑器、Docker 竞争。
- 本地推理比远端 API 更受功耗、温度和模型加载时间影响；首次加载慢属于正常现象。
- 上下文越长，KV Cache 占用和生成延迟越高。长仓库任务先用较短的上下文范围定位文件，再逐步扩大。
- 若系统明显卡顿、模型被系统终止或频繁转用 swap，立即降低模型规模或减少上下文。
- 磁盘空间目前充足，但仍应为模型、系统更新和本地快照保留数十 GB 空间。

## 安全与回滚

### 安全基线

- Ollama/LM Studio 只监听本机回环地址，不对公网开放。
- 本地模型不代表结果自动可信；代码修改仍要运行测试、检查 diff。
- 使用 `workspace-write` 和 `on-request`，不要为日常开发默认开启无沙箱、无审批模式。
- 不把 API Token、Cookie、私钥或 `.env` 原文放入文档、聊天、模型上下文或 Git。
- 当前 DeepSeek provider 使用 API Key；凭据不要随配置样例分发。建议后续改为环境变量或系统钥匙串注入。
- 当前 `web_search=disabled`；本地模型默认不会联网。确需联网时单独明确开启并复核数据外发范围。

### 回滚

本地部署使用独立 profile 和 `--oss` 参数，不影响现有全局配置。需要回到当前工作模型时：

- 不传 `--oss`；
- 不选择 `local-ollama` / `local-lmstudio` profile；
- 执行 `codex doctor`，确认模型重新显示为 `deepseek-flash · deepseek`。

如需回收模型空间，可先执行 `ollama list` 确认模型名，再按 Ollama 官方方式删除对应本地模型；不要在未确认模型目录的情况下批量删除。

## 验收清单

- `ollama --version` 正常。
- `ollama list` 显示 `gpt-oss:20b`。
- `curl -fsS http://203.0.113.1:11434/api/tags` 返回模型列表。
- `codex doctor` 无 fatal 项。
- `codex --oss --local-provider ollama -m gpt-oss:20b "只回复 READY"` 返回 `READY`。
- 不传 `--oss` 时，`codex doctor` 仍显示当前远端模型 `deepseek-flash`。
- 本地服务端口未暴露到公网。

## 发现的本机配置问题

- `codex doctor` 提示 `preferred_auth_method` 已被当前版本忽略，可从 `~/.codex/config.toml` 删除该旧字段。
- `codex doctor` 提示 `node_repl` 的 MCP 环境变量在非交互诊断中缺失；这只影响该次 MCP 诊断，不等于 Codex 主流程故障。
- 当前模型使用自定义 provider，不需要 OpenAI 登录；不要误把 DeepSeek API Key 当成 OpenAI Key。

## 官方资料来源

- [Codex Models](https://learn.chatgpt.com/docs/models)
- [Codex CLI](https://learn.chatgpt.com/docs/codex/cli)
- [Advanced Configuration / Custom model providers](https://learn.chatgpt.com/docs/config-file/config-advanced#custom-model-providers)
- [How to run gpt-oss locally with Ollama](https://developers.openai.com/cookbook/articles/gpt-oss/run-locally-ollama)

以上官方页面读取日期：2026-10-31。
