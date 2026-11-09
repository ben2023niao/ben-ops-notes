---
id: "doc-d2ea00ef0d7c"
title: "dnsmonitor 项目 AI 接手开发 Prompt"
date: "2026-10-27T22:54:15+08:00"
dateSource: "文件创建/修改时间"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "DNS", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/dns_monitor/doc/prompt.md"
sourcePath: "~/Desktop/18game_devops/devops/python/dns_monitor/doc/prompt.md"
sourceSha256: "ccb43a099c7abb2c80af6fb835acbd344ea45c040df8abc44e7a7346e7f9ee0b"
sourceSystem: "project-doc"
---

# dnsmonitor 项目 AI 接手开发 Prompt

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610272254-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-dnsmonitor%20%E9%A1%B9%E7%9B%AE%20AI%20%E6%8E%A5%E6%89%8B%E5%BC%80%E5%8F%91%20Prompt.md)

> 整理日期：2026-10-27 22:54｜日期依据：文件创建/修改时间

你正在接手 `devops/python/dns_monitor` 项目。这个项目是一个 Flask + Docker 的 DNS 污染与 SNI 阻断检测 API 服务，主要用于批量检测域名在不同 DNS 服务商下的解析结果，并尝试判断是否存在 DNS 污染、链路风险验证、私有地址解析、SNI 阻断或端口封锁。

## 0. 关联文档

- 仓库总入口：`.github/copilot-prompt-instructions.md`
- Python 项目总索引：`devops/python/doc/prompt.md`
- 可视化版本：`devops/python/dns_monitor_pywebio/doc/prompt.md`
- 服务器上下文：`devops/ai_context/doc/prompt.md`
- 运维导航站入口：`devops/work.youdianse.com/doc/prompt.md`

这个项目是 API 版；如果用户要页面交互体验，优先看 `dns_monitor_pywebio`。如果要把检测入口放给人工使用，再检查导航站是否需要同步入口。

## 1. 项目定位

- 项目目录：`devops/python/dns_monitor`
- 服务类型：HTTP API
- Web 框架：Flask
- DNS 库：dnspython
- 容器端口：`59000`
- 默认容器名：`dns_monitor`
- 默认镜像名：`dns_monitor:latest`
- 核心服务文件：`dns_monitor/app.py`
- 一键部署脚本：`deploy_dns_monitor.sh`

## 2. 当前目录结构

```text
dns_monitor/
├── README.md
├── HELP.md
├── deploy_dns_monitor.sh
├── 18game-dns/
│   └── 18game-dns.sh
├── dns_monitor/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   ├── full_domains_result.json
│   └── small_domains_result.json
└── doc/
    └── prompt.md
```

## 3. 核心能力

`dns_monitor/app.py` 提供 `POST /dns_check`。

请求体：

```json
{
  "domains": ["example.com", "google.com"]
}
```

返回值是列表，每条记录包含：

- `域名`
- `服务商`
- `DNS地址`
- `IP`
- `DNS状态`
- `备注`
- `SNI检测`

检测逻辑：

1. 先用海外基准 DNS 查询域名 A 记录。
2. 再用多个 DNS 服务商查询同一域名。
3. 对比解析结果。
4. 命中内置拦截 IP 则标记为链路风险验证。
5. 解析到私有地址则标记为私有地址。
6. 国内外解析结果不同则标记为解析差异。
7. 对解析到的 IP 尝试 TCP 443 + TLS SNI 握手。
8. 根据握手结果判断正常、阻断、超时或跳过。

## 4. 关键文件说明

### `dns_monitor/app.py`

这是实际 Flask 服务文件。核心对象：

- `app = Flask(__name__)`
- `BANNED_IPS_MAP`
- `dns_servers`
- `get_detailed_status()`
- `check_sni_blocking()`
- `query_domains()`
- `dns_check()`

如果只改检测逻辑，优先改这里。

### `dns_monitor/requirements.txt`

当前依赖：

```text
flask
dnspython
```

### `dns_monitor/Dockerfile`

从 Python 3.11 slim 构建镜像，复制 `requirements.txt` 和 `app.py`，暴露 `59000`。

### `deploy_dns_monitor.sh`

一键部署脚本。非常重要：这个脚本会用 heredoc 重新生成 `dns_monitor/requirements.txt`、`dns_monitor/app.py` 和 `dns_monitor/Dockerfile`，然后构建并启动容器。

这意味着：

- 如果你只改 `dns_monitor/app.py`，但用户后续运行 `deploy_dns_monitor.sh`，改动可能被脚本覆盖。
- 长期修复必须同步修改 `deploy_dns_monitor.sh` 里的 heredoc 内容。
- 如果要取消覆盖行为，需要先和用户确认。

## 5. 运行方式

一键部署：

```bash
cd devops/python/dns_monitor
bash deploy_dns_monitor.sh
```

手动构建：

```bash
cd devops/python/dns_monitor/dns_monitor
docker build -t dns_monitor:latest .
docker rm -f dns_monitor 2>/dev/null || true
docker run -d --name dns_monitor -p 59000:59000 dns_monitor:latest
```

手动请求：

```bash
curl -s -X POST http://203.0.113.1:59000/dns_check \
  -H "Content-Type: application/json" \
  -d '{"domains": ["example.com", "baidu.com"]}'
```

## 6. 二次开发建议

### 增加 DNS 服务商

改 `dns_servers`：

```python
dns_servers = {
    "阿里云 (AliDNS)": ["223.5.5.5"],
    "腾讯云 (DNSPod)": ["119.29.29.29"],
}
```

注意同步 `deploy_dns_monitor.sh` 中的 heredoc。

### 增加拦截 IP

改 `BANNED_IPS_MAP`：

```python
BANNED_IPS_MAP = {
    "0.0.0.0": "非法占位",
}
```

不要随意把正常公共 DNS IP 加入拦截库，除非有明确证据。

### 调整超时

位置：

- DNS 查询：`resolver.timeout`、`resolver.lifetime`
- TCP 连接：`socket.create_connection(..., timeout=...)`

超时过短会误判，过长会导致批量检测很慢。

### 增加输出字段

返回结果是 dict，直接在 `res.update()` 中添加字段即可。注意前端或调用方可能依赖中文字段名。

## 7. 常见坑

### app.py 改了但部署后没生效

先检查是不是 `deploy_dns_monitor.sh` 又覆盖了 `dns_monitor/app.py`。

### 容器启动失败

检查：

```bash
docker logs dns_monitor
docker ps -a | grep dns_monitor
```

### DNS 查询失败太多

可能原因：

- 当前网络无法访问某些 DNS。
- DNS 服务商对请求做了限制。
- 超时太短。
- 域名本身不存在。

### SNI 结果不稳定

SNI 检测受网络质量、目标 IP 是否支持 443、证书和防火墙影响。不要把单次结果当成绝对结论，建议多次采样。

## 8. 验证清单

本地语法：

```bash
python3 -m py_compile devops/python/dns_monitor/dns_monitor/app.py
```

接口验证：

```bash
curl -s -X POST http://203.0.113.1:59000/dns_check \
  -H "Content-Type: application/json" \
  -d '{"domains": ["example.com"]}'
```

部署验证：

```bash
docker ps | grep dns_monitor
docker logs --tail 50 dns_monitor
```

## 9. 安全边界

- 本项目用于检测域名解析和网络连通，不要改成授权安全测试、扫描内网或高并发压测工具。
- 不要默认内置大规模域名列表导致容器启动后自动猛烈请求。
- 不要把客户域名检测结果随意提交到仓库。
- 如果保存结果，优先保存脱敏报告。

## 10. AI 接手流程

收到需求后：

1. 判断用户要改 API、检测逻辑、部署脚本还是文档。
2. 如果改检测逻辑，同时检查 `dns_monitor/app.py` 和 `deploy_dns_monitor.sh`。
3. 修改后跑 `py_compile`。
4. 如涉及 Docker，构建并 curl 验证。
5. 最终说明是否同步了 deploy 脚本，避免用户部署时丢改动。
