---
id: "doc-4cb5446a492a"
title: "dnsmonitorpywebio 项目 AI 接手开发 Prompt"
date: "2026-10-27T22:54:15+08:00"
dateSource: "文件创建/修改时间"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "CDN", "DNS", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/dns_monitor_pywebio/doc/prompt.md"
sourcePath: "~/Desktop/18game_devops/devops/python/dns_monitor_pywebio/doc/prompt.md"
sourceSha256: "d045a43c9ec97e1cc0bef7110675040873932c7cd0680ebdab8423963ec3195e"
sourceSystem: "project-doc"
---

# dnsmonitorpywebio 项目 AI 接手开发 Prompt

> 来源文件：`~/Desktop/18game_devops/devops/python/dns_monitor_pywebio/doc/prompt.md`

> 整理日期：2026-10-27 22:54｜日期依据：文件创建/修改时间

你正在接手 `devops/python/dns_monitor_pywebio` 项目。这个项目是 DNS 污染 + SNI 阻断检测工具的可视化版本，基于 PyWebIO 提供浏览器页面，让用户可以输入域名、选择 DNS 服务商、编辑拦截 IP 库、调整超时并查看检测结果。

## 0. 关联文档

- 仓库总入口：`.github/copilot-prompt-instructions.md`
- Python 项目总索引：`devops/python/doc/prompt.md`
- API 版本：`devops/python/dns_monitor/doc/prompt.md`
- 服务器上下文：`devops/ai_context/doc/prompt.md`
- 运维导航站入口：`devops/work.youdianse.com/doc/prompt.md`

这个项目是 Web UI 版；如果用户要接口化调用或给其他系统集成，优先看 `dns_monitor`。如果页面部署给团队使用，通常还要同步导航站入口和服务器上下文。

## 1. 项目定位

- 项目目录：`devops/python/dns_monitor_pywebio`
- 服务类型：Web UI
- UI 框架：PyWebIO
- DNS 库：dnspython
- 容器端口：`59999`
- 默认容器名：`dns_monitor_pywebio`
- 默认镜像名：`dns_monitor_pywebio:latest`
- 核心文件：`dns_monitor/app.py`
- 一键部署：`deploy_dns_monitor.sh`
- Compose：`docker-compose.yml`

## 2. 当前结构

```text
dns_monitor_pywebio/
├── Dockerfile
├── docker-compose.yml
├── deploy_dns_monitor.sh
├── README.md
├── HELP.md
├── dns_monitor/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── full_domains_result.json
│   └── small_domains_result.json
└── doc/
    └── prompt.md
```

## 3. 核心功能

页面支持：

- 一行一个输入待检测域名。
- 勾选内置 DNS 服务商。
- 填写自定义 DNS，格式为 `名称=IP`。
- 编辑拦截 IP 库，格式为 `IP=备注`。
- 设置海外基准 DNS。
- 设置 DNS 超时和 TCP 超时。
- 一键执行检测。
- 检测期间锁定输入，显示进度条和实时日志。
- 输出统计摘要、结果表格和 JSON 结果。
- 额外尝试抓取 HTTPS 首页 `<title>`。

## 4. 核心代码地图

### `dns_monitor/app.py`

关键常量：

- `APP_PORT`
- `BANNED_IPS_MAP`
- `DEFAULT_DNS_SERVERS`
- `DEFAULT_DOMAINS`
- `FORM_FIELD_NAMES`

关键函数：

- `get_detailed_status()`：判断 IP 对应的 DNS 状态。
- `check_sni_blocking()`：TCP 443 + TLS SNI 握手检测。
- `fetch_page_title()`：尝试获取 HTTPS 页面标题。
- `parse_domains()`：解析域名输入。
- `parse_custom_dns()`：解析自定义 DNS。
- `parse_banned_ips()`：解析拦截 IP 库。
- `build_dns_server_map()`：合并内置和自定义 DNS。
- `query_domains()`：核心检测循环。
- `render_summary()`：摘要统计。
- `render_results()`：结果表格和 JSON。
- `render_progress_status()`：进度摘要。
- `set_form_locked()`：检测时锁定输入控件。
- `run_detection()`：按钮触发的主流程。
- `fill_demo_data()`：填充示例。
- `clear_results()`：清空结果。
- `main()`：PyWebIO 页面入口。

## 5. 运行方式

脚本方式：

```bash
cd devops/python/dns_monitor_pywebio
bash deploy_dns_monitor.sh
```

Compose 方式：

```bash
cd devops/python/dns_monitor_pywebio
docker compose up -d --build
```

手动 Docker：

```bash
cd devops/python/dns_monitor_pywebio
docker build -t dns_monitor_pywebio:latest .
docker rm -f dns_monitor_pywebio 2>/dev/null || true
docker run -d \
  --name dns_monitor_pywebio \
  --restart unless-stopped \
  -e APP_PORT=59999 \
  -p 59999:59999 \
  dns_monitor_pywebio:latest
```

访问：

```text
http://203.0.113.1:59999
```

## 6. 端口注意事项

- 当前端口是 `59999`。
- 历史需求里可能提过 `99999`，这是非法 TCP 端口。
- TCP 端口范围最大是 `65535`。
- 如果要改端口，需要同步：
  - `Dockerfile` 的 `APP_PORT` 和 `EXPOSE`
  - `docker-compose.yml`
  - `deploy_dns_monitor.sh`

## 7. 二次开发建议

### 增加默认域名

修改 `DEFAULT_DOMAINS`，一行一个域名。不要带协议头。

### 增加默认 DNS 服务商

修改 `DEFAULT_DNS_SERVERS` 和 `build_dns_provider_rows()`，这样勾选项和说明表格都同步。

### 增加检测字段

在 `query_domains()` 的 `result.update()` 添加字段，并同步 `render_results()` 的表头和行数据。

### 调整 UI

优先改 `main()` 中的 PyWebIO 控件，而不是引入前端框架。这个项目的优势是单 Python 文件快速部署。

### 优化性能

当前检测是同步循环。如果域名很多会慢。可考虑：

- 限制输入数量。
- 增加线程池。
- 按域名分批。
- 做可取消任务。

但改并发前必须注意 PyWebIO session 和 UI 更新线程安全。

## 8. 常见坑

### 页面打不开

检查：

```bash
docker ps | grep dns_monitor_pywebio
docker logs --tail 100 dns_monitor_pywebio
```

### 检测时页面卡住

当前检测同步执行，域名和 DNS 服务商越多越慢。先减少域名或调低超时排查。

### SNI 和标题获取大量失败

可能原因：

- IP 不支持 443。
- 目标站点拒绝直连 IP。
- 网络超时。
- 证书或 SNI 行为异常。

不要把页面标题失败等同于 DNS 污染。

### 自定义 DNS 不生效

确认格式是：

```text
Cloudflare=1.1.1.1
OpenDNS=208.67.222.222
```

一行一个，必须有等号。

## 9. 验证清单

语法：

```bash
python3 -m py_compile devops/python/dns_monitor_pywebio/dns_monitor/app.py
```

容器：

```bash
cd devops/python/dns_monitor_pywebio
docker compose up -d --build
docker logs --tail 100 dns_monitor_pywebio
```

页面：

- 打开 `http://203.0.113.1:59999`
- 点击“填充示例”
- 点击“开始检测”
- 确认进度条变化
- 确认摘要、表格和 JSON 输出出现

## 10. 安全边界

- 不要让页面默认执行大规模扫描。
- 不要把内网段或未授权目标作为默认检测列表。
- 不要在结果里输出敏感内部域名，除非用户明确要求。
- 不要引入登录口令时硬编码密码；如需鉴权，用环境变量。

## 11. AI 接手流程

1. 先读 `dns_monitor/app.py`。
2. 判断需求是 UI、检测逻辑、DNS 列表、端口还是部署。
3. 修改后跑 `py_compile`。
4. 如果改端口，同步三个位置。
5. 构建容器并打开页面验证。
6. 回复用户时说明访问地址、容器名和验证结果。
