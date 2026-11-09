---
id: "doc-cbfdbdfb7b60"
title: "18game 项目 AI 接手开发 Prompt"
date: "2026-02-24T00:00:00+08:00"
dateSource: "正文日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/18game/doc/prompt.md"
sourcePath: "~/Desktop/18game_devops/devops/python/18game/doc/prompt.md"
sourceSha256: "daee41e0402354b3649ce4e8b1a0818cbd4b02f2766e9d5d802218661d495cdb"
sourceSystem: "project-doc"
---

# 18game 项目 AI 接手开发 Prompt

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202602240000-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-18game%20%E9%A1%B9%E7%9B%AE%20AI%20%E6%8E%A5%E6%89%8B%E5%BC%80%E5%8F%91%20Prompt.md)

> 整理日期：2026-02-24 00:00｜日期依据：正文日期

你正在接手 `devops/python/18game` 项目。这个目录是一个很小的 Python 工具项目，目前主要脚本是 `sim_user.py`，用于模拟用户从不同地区、运营商和客户端访问线路测速入口，并把模拟测速结果提交到目标接口。

## 0. 关联文档

- 仓库总入口：`.github/copilot-prompt-instructions.md`
- Python 项目总索引：`devops/python/doc/prompt.md`
- 服务器上下文：`devops/ai_context/doc/prompt.md`
- 运维周报：`work-运维部工作进度-周报/doc/prompt.md`

这是独立的小工具项目。除非用户明确要求，不要把这里的测速模拟逻辑接入 ben-bot、导航站或线上发布链路；如果运行结果要写周报，只提炼为运维事项，不要把接口细节和敏感参数展开。

## 1. 项目定位

- 项目目录：`devops/python/18game`
- 当前核心脚本：`sim_user.py`
- 附带素材：`photo_2026-02-24_04-32-47.jpg`
- 运行方式：直接用 Python 执行脚本
- 主要依赖：`requests`

这个项目当前不像 Web 服务，也没有 Dockerfile、README、requirements.txt。它更像一次性或临时运维模拟工具，用来向指定接口批量提交线路测速数据。

## 2. 当前脚本行为

`sim_user.py` 做的事情：

1. 定义目标接口 `TARGET_URL`。
2. 维护一组待测速域名 `DOMAINS`。
3. 维护一组地区、运营商和 IP 前缀配置 `LOCATIONS_CONFIG`。
4. 每轮随机选择一个地区和运营商。
5. 根据对应 IP 前缀生成伪造客户端 IP。
6. 给所有域名随机生成耗时，模拟测速结果。
7. 选出最快域名作为 `fastest`。
8. 通过 POST 请求提交：
   - `fastest`
   - `times`
   - `location`
   - `isp`
9. 请求头里设置：
   - `User-Agent`
   - `Referer`
   - `X-Forwarded-For`
   - `Client-IP`
10. 默认执行 20 轮，每轮之间随机等待 0.5 到 3 秒。

## 3. 重要配置点

修改时优先看这些变量：

```python
TARGET_URL = "..."
DOMAINS = [...]
LOCATIONS_CONFIG = [...]
TOTAL_ROUNDS = 20
```

注意：

- `TARGET_URL` 是外部接口地址，改动前确认目标服务仍然接收同样表单字段。
- `DOMAINS` 中的域名会被随机排序耗时并上报。
- `LOCATIONS_CONFIG` 当前用的是伪造 IP 前缀，不是真实代理请求。
- 脚本只是设置 HTTP 头，不会真正从对应地区发起请求。

## 4. 运行方式

建议先创建虚拟环境：

```bash
cd devops/python/18game
python3 -m venv .venv
. .venv/bin/activate
pip install requests
python3 sim_user.py
```

如果只是临时运行，也可以：

```bash
python3 -m pip install requests
python3 devops/python/18game/sim_user.py
```

## 5. 建议补齐的工程化文件

当前项目缺少：

- `README.md`
- `requirements.txt`
- 参数化配置
- 日志文件
- dry-run 模式
- 错误重试策略

如果后续要长期维护，建议先补：

```text
18game/
├── README.md
├── requirements.txt
├── sim_user.py
└── doc/prompt.md
```

`requirements.txt` 可以先写：

```text
requests
```

## 6. 二次开发建议

如果用户要求“批量模拟更多地区”：

- 只改 `LOCATIONS_CONFIG`。
- 每个地区配置格式为：

```python
("地区名", "运营商", ["IP前缀1", "IP前缀2"])
```

如果用户要求“增加域名”：

- 只改 `DOMAINS`。
- 保持域名不要带协议头。
- 上报时脚本会把最快域名拼成 `https://<domain>`。

如果用户要求“减少频率/避免太快”：

- 调整 `TOTAL_ROUNDS`。
- 调整 `time.sleep(random.uniform(...))` 的范围。

如果用户要求“真实地区访问”：

- 当前脚本做不到。
- 需要接入代理池或云函数节点。
- 不要误导用户说 `X-Forwarded-For` 等于真实地区访问。

## 7. 安全和合规边界

- 不要把这个脚本改成授权安全测试、压测或绕过风控工具。
- 不要把轮次数和并发调得过高。
- 不要在没有确认目标系统归属的情况下对第三方地址运行。
- 不要伪造敏感身份信息。
- 如果改成代理模式，不要提交代理账号密码。

## 8. 验证清单

修改后至少验证：

```bash
python3 -m py_compile devops/python/18game/sim_user.py
python3 devops/python/18game/sim_user.py
```

观察输出：

- 是否能打印每轮地区、运营商、伪装 IP。
- 是否能打印最快线路。
- 请求失败时是否有清晰错误。
- 是否不会无限循环。

## 9. 给后续 AI 的第一步

当你接到这个项目的修改需求时：

1. 先读 `sim_user.py`。
2. 确认用户要改的是接口、域名、地区、轮数还是请求字段。
3. 优先小范围修改常量。
4. 如果要长期化，再补 `requirements.txt` 和 CLI 参数。
5. 不要引入复杂框架，除非用户明确要做 Web 面板或定时任务。
