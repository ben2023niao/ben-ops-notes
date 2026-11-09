---
id: "doc-050dc5931807"
title: "【优化 + 安全】CC 守卫：误封 CloudFront 回源 IP 修复 + 群通知文案改版"
date: "2026-10-13T16:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Nginx", "监控告警", "自动化", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-13_1620-%E3%80%90%E4%BC%98%E5%8C%96%2B%E5%AE%89%E5%85%A8%E3%80%91CC%E5%AE%88%E5%8D%AB%E8%AF%AF%E5%B0%81CloudFront%E5%9B%9E%E6%BA%90IP%E4%BF%AE%E5%A4%8D%E4%B8%8E%E7%BE%A4%E9%80%9A%E7%9F%A5%E6%96%87%E6%A1%88%E6%94%B9%E7%89%88.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-13_1620-【优化+安全】CC守卫误封CloudFront回源IP修复与群通知文案改版.md"
sourceSha256: "452299925880a93b89cc3bd64175bb98b9cf16ef3e5337c8e82e8ea2e0fd38b7"
sourceSystem: "project-doc"
---

# 【优化 + 安全】CC 守卫：误封 CloudFront 回源 IP 修复 + 群通知文案改版

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610131620-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-%E3%80%90%E4%BC%98%E5%8C%96%20%2B%20%E5%AE%89%E5%85%A8%E3%80%91CC%20%E5%AE%88%E5%8D%AB%EF%BC%9A%E8%AF%AF%E5%B0%81%20CloudFront%20%E5%9B%9E%E6%BA%90%20IP%20%E4%BF%AE%E5%A4%8D%20%2B%20%E7%BE%A4%E9%80%9A%E7%9F%A5%E6%96%87%E6%A1%88%E6%94%B9%E7%89%88.md)

> 整理日期：2026-10-13 16:20｜日期依据：文件名日期

- 日期：2026-10-13 16:20（北京）
- 范围：`devops/scripts/cc_guard/`（网关 CC 守卫、国家级拉黑、容器 CPU 看护）
- 触发：10-13 群里连续多条「CC 守卫告警（login_bruteforce）」+ 1 条「容器 CPU 看护」；用户反馈通知"有效内容太少、太啰嗦"，要求继续优化

---

## 一、历史运行结果总结（CC 守卫）

| 项目 | 现状 |
| --- | --- |
| 运行方式 | 监控机 52.79.252.255，ubuntu crontab 每 10 秒一轮（`flock` 串行），日志 `state/guard.log`、`state/cron.log` |
| 识别来源 | 网关并发连接、网关/源站 `/api` 刷量、后端「登录失败按 IP」、自有监控 UA |
| 处置 | 按地区：常规刷量国内/港澳台只观察、海外临时封禁（10 分钟起、重复翻倍、上限 2 小时）；登录撞库国内也在更高阈值（60 次/10 分钟）封禁；必要时国家级临时拉黑 |
| 生效位置 | 网关 nginx XFF 清单（444）+ 宝塔源站清单（444）+ 宝塔 iptables + 限流 |
| 通知 | `serious`（故障类）即时发两群；`temp_block/api_flood/observe` 累计为 30 分钟摘要发两群 |
| 本次之前状态 | 守卫健康、磁盘 40%、load 1.5~5；`blocked=2`（**异常，见第三节**）、`xff 3`、temp 0 |

长期观察结论：**授权安全测试面在持续变化**（换路径、换 UA、绕 CDN 打源站/旁站、低速率撞库、0day 挖矿），
守卫的识别规则需要持续迭代；同时**误拦正常流量**才是最大的业务风险（历史已发生 5 次以上：支付回调、
1game 鉴权、SDK 接口、自动化测试机、iOS plist、搜索引擎爬虫、手机浏览器）。

---

## 二、本次触发的告警（现象）

1. 10-13 02:58~05:20 之间：连续多条 `【CC 守卫告警】触发：login_bruteforce=1`（load 1.5~4.3）。
2. 30 分钟摘要 2 条：`223.114.4.28｜CN｜60 次｜封 30 分钟`、`2402:1980:e238:3e59::1｜MY｜22 次｜封 30 分钟`。
3. 16:04 后端容器 `youdianse-main-php-web` CPU 805%（阈值 500%）→ 自动触发 CC 守卫处置（成功）。

**结论：授权安全测试已被正常处置，但通知本身有问题**（第三节 1、2 条）。

---

## 三、排查发现的问题

### 3.1 【安全·高】网关 iptables 误封 CloudFront 回源 IP（3 个）

- 网关 `16.208.38.88` 的 iptables 里封了 `15.158.222.194`、`15.158.222.234`、`3.172.92.112`，端口 80/443 `DROP`。
- 用 AWS 官方 `ip-ranges.json` 核验：三者都属 **`CLOUDFRONT_ORIGIN_FACING`**（15.158.0.0/16、3.172.64.0/18）——
  即 **CloudFront 回源时使用的源 IP**；而本网关就是 CloudFront 的回源（网关日志里 `15.158.222.x` 每个文件约 2 万条）。
- 封禁来源：守卫的「单 IP 到 80/443 并发 established ≥ 200 就判定可疑」规则——CloudFront 边缘天然会维持大量连接，属**误判**。
- 影响：`blocked=2` 自 **10-11 22:37 UTC（10-12 06:37 北京）** 起持续约 1.5 天；
  实测这 3 个 IP 在各日志文件中**均为 0 命中**（当时不在服务）→ **未造成实际中断**，
  但属高危隐患：CloudFront 随时可能启用这些 IP，一旦启用即回源失败（用户侧 5xx/超时）。

### 3.2 【体验】login_bruteforce 告警刷屏且与摘要重复

- `login_bruteforce=` 没有被归入"处置类"，于是每命中一次就走 `serious` **即时告警**（冷却仅 90 秒），
  同时又计入 30 分钟摘要 → **同一件事发两次、且最短 90 秒一条**。

### 3.3 【文案】摘要窗口标注错误

- 摘要写死 `（北京时间，10 分钟汇总）`，实际 `CC_DIGEST_SECONDS=1800`（30 分钟）→ 与实际不符。
- 即时告警里也写死"见 10 分钟聚合摘要"。

### 3.4 【文案】"北京时间"实际是 UTC

- 摘要/故障告警用 `time.localtime()` 格式化并标注「北京时间」，但监控机是 UTC → 时间整体差 8 小时。

---

## 四、改动（`devops/scripts/cc_guard/`）

### 4.1 CDN 永不封禁（新增）

- 新增 `cdn_never_block_cidrs.txt`：AWS CloudFront 段清单（`CLOUDFRONT_ORIGIN_FACING` + `CLOUDFRONT`，共 **309 条**：IPv4 245 / IPv6 64）。
- 新增 `refresh_cdn_never_block.py`：从 `https://ip-ranges.amazonaws.com/ip-ranges.json` 重新生成该清单。
- `youdianse_cc_guard.py`：新增 `is_cdn_ip()`，并让 `is_skippable()` 一并跳过 CDN 段
  → 覆盖 iptables 封禁、临时封禁、`/api` 刷量判定、登录撞库判定**全部路径**；文件缺失时用兜底段（15.158.0.0/16、3.172.64.0/18）。

### 4.2 通知降噪与文案改版

- `login_bruteforce=`、`auto_country_block=` 归入"处置类"→ **只进 30 分钟摘要**，不再即时刷屏。
- 摘要窗口文案改为按 `DIGEST_SECONDS // 60` 动态生成。
- 新增 `bj_time()` / `human_geo()` / `human_src()`：时间统一**北京时间**；国家码转中文（CN→中国…）；
  运营商取 AS 名可读部分（如 `中国·China Mobile…`）；授权安全测试类型转中文（`后端/登录失败`→`登录撞库`）。
- 摘要拼装抽成 `render_digest()`（可本地单测，无发送副作用）。
- 守卫日志行新增 `login_bruteforce=` 字段。
- `youdianse-container-cpu-watch.py`、`youdianse-country-block.py` 的通知同步精简。

### 4.3 新文案（前后对比）

**摘要（改前 ≈10 行，含 4 行固定样板）**

```text
【线上环境｜刷量处置摘要】02:58~03:28（北京时间，10 分钟汇总）
- 本轮新临时封禁：1 个 IP｜按来源国：CN:1次封禁
- 封禁明细（TOP1）：
   223.114.4.28｜CN｜60次｜封30分钟
- 当前状态：临时封禁中 1 个｜观察名单 1 个｜load 3.03｜nginx active｜磁盘 39%
- 策略：单 IP >500 次触发；国内/港澳台只观察；海外临时封禁（10 分钟起，重复违规翻倍，上限 2 小时）
- 放出后进入 2 小时观察名单（阈值降到 100 次），防止「刚放出又授权安全测试」
- 说明：**仅在有处置动作（封禁/国家级拉黑）时发送本摘要**；无授权安全测试则不发
- 明细日志：/opt/telegram/18game_devops/devops/scripts/cc_guard/state/guard.log
```

**摘要（改后 6 行，一行一条，信息更全）**

```text
【刷量处置】15:47–16:17（北京）｜新封禁 2 · 观察 1
· 223.114.4.28｜中国·China Mobile…｜登录撞库 60 次｜封 30 分钟
· 2402:1980:e238:3e59::1｜马来西亚·DiGi…｜接口刷量 22 次｜封 30 分钟｜重复第 2 次
· 观察未封：1.2.3.4（中国 45 次）
· 国家级拉黑：PH（30 分钟，到期自动解除）
· 现况：封禁中 1 · 观察名单 0 · load 3.03 · nginx active · 磁盘 39%
```

**故障告警（改后；只在真正故障时发两群）**

```text
【CC 守卫·故障】网关 16.208.38.88｜10-13 16:16（北京）
· 网关请求 520 次/秒（正常 1~3）
· Nginx 错误日志 +310 条（单轮）
· 现况：nginx active｜load 4.2｜磁盘 78%
· 处置：新增封禁 3 个（累计 3）
```

**容器 CPU 看护（改后）**

```text
【容器 CPU 看护】后端 youdianse-main-php-web｜10-13 16:04:01（北京）
· 触发：CPU 飙升（阈值 500%）（当前 805%）
· 自动处置：CC 守卫已执行 · 成功（3.8 秒）
```

---

## 五、线上部署与验证

| 项 | 结果 |
| --- | --- |
| 备份 | 三个脚本各自 `*.bak.cdnfix-20261013-081310` / `*.bak.notifyopt-20261013-081643`；`guard_state.json.bak.cdnfix-*` |
| 部署 | 3 个脚本 + `cdn_never_block_cidrs.txt` + `refresh_cdn_never_block.py` 已下发（原子 `mv`；root:root 755/644） |
| 语法 | 本地与线上 `py_compile` 均通过 |
| CDN 判定 | 线上实测 `is_cdn_ip/is_skippable`：`15.158.222.194/.234`、`3.172.92.112` = True；`167.104.164.116`（真实授权安全测试源）= False |
| 解封 | 网关 iptables 删除 3 条 DROP（`removed=1` ×3），`iptables -S` 已无匹配 |
| 状态清理 | `guard_state.json` → `blocked=[]`、`blocked_ips.txt` 清空；等待 40 秒后复查仍为 `[]`（守卫未回写） |
| 新日志字段 | `CHECK ... login_bruteforce=0 blocked=0+xff 3 temp=0 observe=0` 正常输出 |
| 渲染自检 | 本地与线上调用 `render_digest()`，输出与预期一致（6 行） |
| 定时刷新 | ubuntu crontab 新增 `17 4 * * 1 ... refresh_cdn_never_block.py`（每周一刷新 CloudFront 段） |

---

## 六、回滚

```bash
G=52.79.252.255   # 监控机
D=/opt/telegram/18game_devops/devops/scripts/cc_guard
# 脚本回滚（用上面备份标签替换）
sudo cp -a $D/youdianse_cc_guard.py.bak.notifyopt-20261013-081643 $D/youdianse_cc_guard.py
sudo cp -a $D/youdianse-country-block.py.bak.notifyopt-20261013-081643 $D/youdianse-country-block.py
sudo cp -a $D/youdianse-container-cpu-watch.py.bak.notifyopt-20261013-081643 $D/youdianse-container-cpu-watch.py
# 状态回滚
sudo cp -a $D/state/guard_state.json.bak.cdnfix-20261013-081310 $D/state/guard_state.json
# 网关解封如需恢复（不建议）：ssh 16.208.38.88 'sudo iptables -I INPUT -p tcp -s <ip> -m multiport --dports 80,443 -j DROP'
```

---

## 七、待办 / 建议

1. `SKIP_PREFIXES` 里仍有 `3.`、`18.`、`34.`、`47.` 这类**过宽的字符串前缀**（早期应急加的），
   现在已有权威 CloudFront 段清单，建议后续收敛为精确网段（本次未动，避免引入新风险）。
2. 网关 iptables 现存 **851 条** DROP 规则，其中多数不在守卫状态中（历史遗留），建议做一次规则清理（人工确认）。
3. 如需「摘要只发 18game运维、不发上线群」，把 `telegram(digest)` 改成 `telegram(digest, only_ops=True)` 即可。
