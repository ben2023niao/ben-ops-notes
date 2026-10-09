---
id: "doc-dce4e0f6c57d"
title: "【安全加固】封禁登录撞库来源 + CC 守卫新增「登录失败按 IP 封禁」"
date: "2026-10-09T18:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Nginx", "监控告警", "CDN", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-09_1800-%E3%80%90%E5%AE%89%E5%85%A8%E5%8A%A0%E5%9B%BA%E3%80%91%E5%B0%81%E7%A6%81%E7%99%BB%E5%BD%95%E6%92%9E%E5%BA%93IP%E4%B8%8ECC%E5%AE%88%E5%8D%AB%E6%96%B0%E5%A2%9E%E4%BD%8E%E9%80%9F%E7%8E%87%E6%92%9E%E5%BA%93%E8%AF%86%E5%88%AB.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-09_1800-【安全加固】封禁登录撞库IP与CC守卫新增低速率撞库识别.md"
sourceSha256: "e10c04752f6c0cacc4f41415f666ccbeba1a76b2996dff917fb50f717ca3a000"
sourceSystem: "project-doc"
---

# 【安全加固】封禁登录撞库来源 + CC 守卫新增「登录失败按 IP 封禁」

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-09_1800-【安全加固】封禁登录撞库IP与CC守卫新增低速率撞库识别.md`

> 整理日期：2026-10-09 18:00｜日期依据：文件名日期

- 日期：2026-10-09 18:00（北京）
- 背景：当日发现登录接口撞库（来源 `3.1.244.240`，约 2,663 次/小时）。授权安全测试者换成完整 Chrome UA 穿过 UA 规则、速率又低于 /api 泛刷量阈值(500)，**原有规则完全没识别**
- 需求：①封禁该 IP；②给 CC 守卫增加「按 IP 失败次数封禁」的低速率撞库规则；**改造前先备份，便于回滚**

## 一、改动 1：封禁 `3.1.244.240`

写入守卫的**静态拦截清单**（守卫每轮会把它合并写入网关，不会被动态清单冲掉）：

```text
/opt/telegram/18game_devops/devops/scripts/cc_guard/state/static_block_ips.txt
  167.104.164.116
  15.168.8.171
  3.1.244.240   # 2026-10-09 登录接口撞库（约 2663 次/小时，换 UA 绕过，速率低于 /api 泛刷量阈值）
```

生效面（均已实测）：

- **网关** `/etc/nginx/conf.d/abuse-blocklist.conf` → `~*3.1.244.240 1;`（命中 XFF 即 444，对 CloudFront 流量的有效层）
- **宝塔源站** iptables → `-A INPUT -s 3.1.244.240/32 -j DROP`（防直连源站）

## 二、改动 2：CC 守卫新增「登录失败按 IP 封禁」

文件：`devops/scripts/cc_guard/youdianse_cc_guard.py`（仓库与线上 md5 一致，改后已同步部署）

### 2.1 为什么用「失败次数」而不是「请求次数」

数据源：后端 API 日志 `runtime/app-logs/api_request-<date>.log`，每条请求含 `ip / url / userId`；登录失败时 `userId` 为 null。用失败次数判定更精确也更安全：

- 实测同一 10 分钟窗口：授权安全测试者失败 **356 次**；国内几个大段 IP（疑似 CGNAT）只有 6~50 次 → 不会误伤
- 纯按请求数封禁会误伤 CGNAT 下的真实用户（宝塔侧此前踩过该坑，故 `CC_BAOTA_AUTO_BLOCK` 默认关闭）

### 2.2 判定与处置

```python
LOGIN_FAIL_ENABLE        = 1        # 开关（0 关闭）
LOGIN_FAIL_WINDOW        = 600      # 统计窗口（秒）
LOGIN_FAIL_MIN           = 20       # 海外源阈值（窗口内失败次数）
LOGIN_FAIL_MIN_CN        = 60       # 国内/港澳台阈值（更高，防 CGNAT 误伤）
LOGIN_FAIL_BLOCK_SECONDS = 1800     # 首次封禁 30 分钟
BACKEND_HOST             = 16.209.16.108（与网关共用同一把登录 key）
```

- 命中后走既有处置链路：临时封禁 → 到期自动放出 → 进观察名单低阈值盯防 → 重复违规时长翻倍（30min → 1h → 2h，上限 2h）
- 巡检摘要里以 `login_bruteforce=N` 体现，来源标注 `后端/登录失败`
- 国内/港澳台**同样封禁**（账号授权安全测试不同于正常浏览），但阈值提高到 60
- 已在静态清单里的 IP 会跳过，不再重复进临时封禁（避免重复告警）
- 远端只回传「IP + 失败次数」聚合结果，不把大段日志拉回本机；读取失败只记 WARN，不中断守卫

## 三、改动前的备份（回滚用）

| 对象 | 备份路径 |
| --- | --- |
| 守卫脚本（线上） | `/opt/telegram/18game_devops/devops/scripts/cc_guard/youdianse_cc_guard.py.bak.loginrule-20261009-155050` |
| 静态拦截清单 | `/root/static_block_ips.bak.20261009-155050` |
| 守卫状态文件 | `/root/guard_state.bak.<时间戳>`（清空 signature 触发重写前备份） |
| 网关拦截清单 | `16.208.38.88:/root/abuse-blocklist.bak.20261009-155103` |
| 网关 iptables | `16.208.38.88:/root/gw-iptables-backup-20261009-155119.rules`（894 行） |
| 宝塔拦截清单 | `16.208.5.147:/root/baota-abuse-blocklist.bak.20261009-235105` |
| 宝塔 iptables | `16.208.5.147:/root/baota-iptables-backup-20261009-235105.rules`（174 行） |

## 四、验证结果

| 验证项 | 方式 | 结果 |
| --- | --- | --- |
| 语法 | 本地与线上 `python3 -m py_compile` | 均通过 |
| 新规则能否识别本次撞库（只读） | 直接调用 `login_fail_suspects()`，默认 10 分钟窗口 | `3.1.244.240 → 356 次`（阈值 20）；1 小时窗口 642 次 |
| 误伤评估 | 同窗口其他 IP 的失败次数 | 国内大段 IP 6~50 次（阈值 60）→ 不触发 |
| 封禁生效（网关） | `curl --resolve 网关 -H "X-Forwarded-For: 3.1.244.240"` | 444（连接被关闭） |
| 封禁生效（源站） | `iptables -S \| grep 3.1.244.240` | `-A INPUT -s 3.1.244.240/32 -j DROP` |
| 守卫稳定性 | 以 ubuntu 身份跑一轮 + 观察日志 | `blocklists rewritten: gateway=True baota=True permanent=3`，15:53 之后无 WARN |

> 操作细节（已修正并记录）：用 `sudo`（root）手工执行守卫时，宝塔 key 为 `root:ubuntu 0640`，
> OpenSSH 会以 `UNPROTECTED PRIVATE KEY FILE` 拒绝使用，导致 `baota=False` 的**假故障**。
> 生产路径是 **ubuntu 用户 crontab（每 10 秒）**，属正常；本次验证已改用 ubuntu 身份执行。

## 五、回滚方式

```bash
# 1) 守卫脚本回滚（cron 下一轮自动生效，无需重启）
sudo cp -a /opt/telegram/18game_devops/devops/scripts/cc_guard/youdianse_cc_guard.py.bak.loginrule-20261009-155050 \
           /opt/telegram/18game_devops/devops/scripts/cc_guard/youdianse_cc_guard.py

# 2) 只关新规则、保留脚本（最轻量）
sudo sed -i 's/CC_LOGIN_FAIL_ENABLE", "1"/CC_LOGIN_FAIL_ENABLE", "0"/' \
  /opt/telegram/18game_devops/devops/scripts/cc_guard/youdianse_cc_guard.py

# 3) 撤销对 3.1.244.240 的封禁
sudo cp -a /root/static_block_ips.bak.20261009-155050 \
           /opt/telegram/18game_devops/devops/scripts/cc_guard/state/static_block_ips.txt
#   再清空 signature 触发清单重写（或等下一轮临时封禁变化）
sudo python3 -c "import json,pathlib;p=pathlib.Path('/opt/telegram/18game_devops/devops/scripts/cc_guard/state/guard_state.json');d=json.loads(p.read_text());d['last_block_signature']='';p.write_text(json.dumps(d,ensure_ascii=False))"
```

## 六、后续建议

1. 观察 1~2 天 `login_bruteforce` 触发情况，按需调整阈值（默认海外 20 / 国内港澳台 60）
2. 账号维度加固：同账号连续失败做锁定/验证码（IP 封禁只是第一层）
3. 若同一云厂商网段持续出现，可评估按网段加严登录路径
4. 把新增规则的触发含义写进值班说明，便于看到 `login_bruteforce=` 时快速判断
