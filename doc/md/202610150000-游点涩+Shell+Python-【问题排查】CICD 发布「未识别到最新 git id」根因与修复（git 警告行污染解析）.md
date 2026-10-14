---
id: "doc-61cf1e78a040"
title: "【问题排查】CICD 发布「未识别到最新 git id」根因与修复（git 警告行污染解析）"
date: "2026-10-15T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Docker", "监控告警", "自动化", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-15-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91CICD%E5%8F%91%E5%B8%83%E6%9C%AA%E8%AF%86%E5%88%AB%E6%9C%80%E6%96%B0gitid-%E8%AD%A6%E5%91%8A%E8%A1%8C%E6%B1%A1%E6%9F%93%E8%A7%A3%E6%9E%90.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-15-【问题排查】CICD发布未识别最新gitid-警告行污染解析.md"
sourceSha256: "512a95495f0da937387234dd4053c16466445f2bfbb3eedb46bde13468465807"
sourceSystem: "project-doc"
---

# 【问题排查】CICD 发布「未识别到最新 git id」根因与修复（git 警告行污染解析）

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-15-【问题排查】CICD发布未识别最新gitid-警告行污染解析.md`

> 整理日期：2026-10-15 00:00｜日期依据：文件名日期

- 日期：2026-10-15
- 环境：**线上环境** CICD Web（`https://cicd.youdianse-main.xyz/`，宿主机 16.209.16.108）
- 触发：Davie 发布后端时卡在「第二步：选择部署 git id」，页面显示 `后端业务 git id：warning:`，开发给的提交 `6e46c0cc3f77bc81d43e50e94d9e60aab19768af` 没有被识别
- 结论：**远端仓库完全正常**（`main` 的头就是 `6e46c0cc3f77…`）；是 CICD 解析 `git ls-remote` 输出时**把 git 的告警行当成了 git id**

---

## 一、现象

```text
· 发布流程第二步：「正在选择 youdianse-php main 分支最近 5 个提交。」后没有下文
· 发布日志文件名带 warning：游点涩-后端-运维[邮箱已脱敏]
· 日志里：后端业务 git id：warning:  ← 明显不是 40 位 SHA
· 发布锁（publish-lock.json）停在第二步，active=true
```

---

## 二、根因（已 100% 复现）

### 2.1 直接原因：git 先打印一行 warning，解析取了第一段

在生产宿主机上执行 CICD 实际调用的命令：

```bash
$ git -C /opt/docker-youdianse-php/src/youdianse-php ls-remote origin refs/heads/main
warning: redirecting to https://18game.18git.com/php/youdianse-php.git/
6e46c0cc3f77bc81d43e50e94d9e60aab19768af    refs/heads/main
```

而 `cicd-web/core.py` 里（修复前，第 767 行）：

```python
    if result.code == 0 and result.output:
        return result.output.split()[0], "远端分支"     # ← 取第一段
```

`run_cmd()`（`command.py`）用的是 `stderr=subprocess.STDOUT`，**stderr 被合并进 stdout**，
于是 `output.split()[0]` 拿到的是 `warning:` —— 这就是日志里那个 `warning:` 的来历。
git id 非法 → 第二步无法继续 → 发布卡住并留下 warning 日志 + 发布锁。

### 2.2 为什么会出现这行 warning

该仓库的 `origin` 地址形如 `https://18game.18git.com/php/youdianse-php`（不带 `.git`），
GitLab 会把它 **301 重定向**到 `.../php/youdianse-php.git/`，git 于是打印
`warning: redirecting to ...`。**这本身无害**，只是被脆弱的解析放大了。

### 2.3 排除项（确认与仓库/开发无关）

```text
· 远端 main 的头 = 6e46c0cc3f77bc81d43e50e94d9e60aab19768af ← 正是开发给的提交
· 最近 5 个提交正常：6e46c0cc / 252e5faa / ad7cb029 / 2c49a9c0 / b211823f（渠道包相关）
```

---

## 三、修复（`cicd-web/core.py`）

新增两个工具函数，并把三处解析全部改为「按内容取 SHA」：

```python
def extract_sha(text: str) -> str:
    """从可能混有 stderr 告警的输出里提取第一个 40 位十六进制 SHA。"""
    match = re.search(r"\b[0-9a-f]{40}\b", text or "")
    return match.group(0) if match else ""

def parse_ls_remote_sha(output: str, branch: str) -> str:
    """从 `git ls-remote <remote> refs/heads/<branch>` 输出里精确取该分支的 SHA。"""
    want = f"refs/heads/{branch}"
    for line in (output or "").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == want and re.fullmatch(r"[0-9a-f]{40}", parts[0]):
            return parts[0]
    ...  # 兜底：任何 "<40位sha>\trefs/..." 也接受
```

`backend_branch_git_id()` 的三条路径（远端 ls-remote / 本地 origin 缓存 / 本地 HEAD 兜底）全部改用上面两个函数，
不再有 `output.split()[0]` 这种写法。

**单测（用真实输出）**：

```text
含 warning 的真实输出 -> 6e46c0cc3f77bc81d43e50e94d9e60aab19768af   ✅
旧逻辑 split()[0]     -> warning:                                   ← 事故原因
空输出 / fatal        -> ''（走后续兜底，不会把错误信息当 git id）    ✅
```

---

## 四、线上处置与验证（生产 16.209.16.108）

| 步骤 | 动作 | 结果 |
| --- | --- | --- |
| 1 | 备份并部署修复版 `cicd-web/core.py` | 备份 `core.py.bak.gitidfix-20261015-135700` |
| 2 | 服务端语法校验 | `py_compile` 通过 |
| 3 | 释放卡住的发布锁（TTL 默认 6 小时，等不到自动释放） | 删除 `runtime/publish-lock.json`，备份到 `/tmp/publish-lock.bak-20261015-135700.json` |
| 4 | 重启 `cicd-web` | `active`；18090 → **200** |
| 5 | 直接调用校验 | `backend_branch_git_id("main")` → **`6e46c0cc3f77bc81d43e50e94d9e60aab19768af`**（来源：远端分支）✅ |
| 6 | 最近 5 个提交 | 正确列出（头部队列为开发提交）✅ |

**现在可以直接重试发布**（Davie 再次点发布即可，页面会正常列出最近 5 个提交）。

---

## 五、处理过程中的一次误操作（如实记录，避免重犯）

最初我把**生产的 `core.py` 整体复制到测试环境**，导致测试环境 CICD 起不来：

```text
ImportError: cannot import name 'ADMIN_LOGIN_PATH' from 'config'
```

原因：**测试与生产的 cicd-web 代码版本不同**（测试机仓库检出停在 `45d04aa`），
生产版 core.py 依赖的 config 项在测试版里还没有。

- 处置：立即用备份回滚测试环境 `core.py` → 重启 → 18090 恢复 **200**；测试环境未留下修复（保持原版本，避免二次分叉）。
- 教训：**跨环境只做"最小改动"，不要整文件覆盖**；改完必须立刻验证服务端口。
- 测试环境该缺陷属**潜伏**（它的 origin 地址不触发重定向，所以不会打印 warning）；
  等测试机 `git pull` 到含修复的提交后即自动修好。

---

## 六、影响与后续建议

1. **发布锁 TTL 默认 6 小时**（`defaults.publish_lock_ttl_seconds=21600`）——发布异常中断后，
   运维要等 6 小时才能再发。建议调小（如 600~1800 秒），或在页面提供「强制释放发布锁」按钮。
2. **统一两环境 cicd-web 版本**：测试机 `/opt/docker-youdianse-php` 落后于远端，
   建议 `git pull` 同步（注意该机还有 `docker-compose.yml`、`cicd-web/config/settings.json`、
   `ops/test/install-health-monitor.sh` 三处本地改动，同步前确认归属）。
3. **根治 redirect 告警（可选）**：把仓库 `origin` 地址补成带 `.git` 的形式，
   或在调用前加 `git -c advice.detachedHead=false` / 统一用 `git ls-remote <url>.git`，让输出保持干净。
4. 排查同类隐患：任何「命令输出直接 `split()[0]` / 取首行」的解析，都可能被 stderr 告警污染
   （本次已全仓检查，仅此一处）。

---

## 七、回滚

```bash
# 生产（16.209.16.108）
cd /opt/docker-youdianse-php
sudo cp -a cicd-web/core.py.bak.gitidfix-20261015-135700 cicd-web/core.py
sudo systemctl restart cicd-web && systemctl is-active cicd-web

# 测试（15.152.247.196）—— 若需回滚（当前已是原版本）
cd /opt/docker-youdianse-php
sudo cp -a cicd-web/core.py.bak.gitidfix-20261015-055722 cicd-web/core.py
sudo ./cicd-web.sh restart
```
