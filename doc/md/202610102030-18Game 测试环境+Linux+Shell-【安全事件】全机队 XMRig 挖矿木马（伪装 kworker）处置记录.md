---
id: "doc-b7fc3378576c"
title: "【安全事件】全机队 XMRig 挖矿木马（伪装 kworker）处置记录"
date: "2026-10-10T20:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "Nginx", "MySQL", "Redis"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-10_2030-%E3%80%90%E5%AE%89%E5%85%A8%E4%BA%8B%E4%BB%B6%E3%80%91%E5%85%A8%E6%9C%BA%E9%98%9FXMRig%E6%8C%96%E7%9F%BF%E6%9C%A8%E9%A9%AC%E5%A4%84%E7%BD%AE%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-10_2030-【安全事件】全机队XMRig挖矿木马处置记录.md"
sourceSha256: "c5c780d67386ed2fab35c462b5b13bc399c3bc4c927a7eb7835bb40a423205b0"
sourceSystem: "project-doc"
---

# 【安全事件】全机队 XMRig 挖矿木马（伪装 kworker）处置记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610102030-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-%E3%80%90%E5%AE%89%E5%85%A8%E4%BA%8B%E4%BB%B6%E3%80%91%E5%85%A8%E6%9C%BA%E9%98%9F%20XMRig%20%E6%8C%96%E7%9F%BF%E6%9C%A8%E9%A9%AC%EF%BC%88%E4%BC%AA%E8%A3%85%20kworker%EF%BC%89%E5%A4%84%E7%BD%AE%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-10-10 20:30｜日期依据：文件名日期

- 日期：2026-10-10 20:30（北京）
- 触发：测试服务器内存告警（70.1% used，连续多次）→ 排查发现挖矿木马 → 全机队排查
- 结论：**11 台机器被植入伪装成内核线程的 XMRig 门罗币挖矿程序**，已在全部可访问主机上完成清除、取证与矿池封堵；
  另有 5 台机器无法通过现有通道核验（见第三节），**业务未受影响，但需尽快做凭据轮换与深层溯源**

## 一、发现过程

```text
1) 测试服务器 15.152.247.196 报「内存 70%（5.3G/7.6G）连续 3 次」
2) 上机排查内存构成，发现可疑进程：
     PID 1651544  RSS 2.1GB  ./kworker --config=./c   ← 用户态进程伪装成内核线程
   （真内核线程形如 [kworker/...]，RSS 为 0；该进程工作目录 /var/local/kworker）
3) 进一步发现：systemd 服务 kworker.service（root 运行）+ 启动脚本 kworker.sh
4) 顺藤摸瓜扩线排查全机队 → 5 台生产/监控机 + 4 台测试/前置机同样中招
```

## 二、木马详情

```text
目录：/var/local/kworker/（权限 0777，属主 root）
  ├─ kworker          8.3MB 挖矿主程序（md5 8f4fff0ded94f1141768220906abfbb8）
  ├─ kworker.sh       启动脚本：ulimit -n 65535; ./kworker --config=./c
  ├─ c                配置（md5 d996b98bdecd52d08d67acb38cbfa268）
  │    pools: url=pool.supportxmr.com:3333  algo=rx/0（RandomX 门罗币）
  │           user=42vkCsUbH8ZUcesyHgUN6JKBczb8VHafVaNykbamX5KxCRWsGLxSkJiDSes273w8i7QpyeHxZJpg5TQHeoVSJbNBSLYS1zP
  │           pass=supportxmr888888   donate-level=1
  ├─ k                运行日志
  └─ cert.pem / cert_key.pem  自签 localhost 证书（配套组件用）

持久化：/etc/systemd/system/kworker.service
  Type=simple  User=root  WorkingDirectory=/var/local/kworker
  ExecStart=/var/local/kworker/kworker.sh  Restart=on-failure  RestartSec=10
  WantedBy=multi-user.target
```

处置时每台机器上的该进程都显示出同样的行为：向 `pool.supportxmr.com:3333` 建立连接挖矿，
内存占用在内存较小的机器上达 2.1~2.4GB（正是测试机 70% 内存告警的直接原因）。

## 三、影响面（全量巡检结果）

### 3.1 已确认感染并处置完成（11 台，均为 root 权限植入）

| # | 主机 | 角色 | 挖矿进程 RSS | 处置后内存(总-可用) |
| --- | --- | --- | --- | --- |
| 1 | 15.152.247.196 | 测试环境-前后端 | 2.1GB | 70.4% → **43.4%** |
| 2 | 52.79.252.255 | 监控/ben-bot 部署机 | 2.4GB | → 26% |
| 3 | 13.208.101.121 | 线上前端 H5 | 2.1GB | → 33% |
| 4 | 16.208.38.88 | 线上网关（H5/PC 统一入口） | 6.5MB | → 43% |
| 5 | 16.209.16.108 | 线上后端（PHP/发布） | 7.0MB | → 13% |
| 6 | 16.208.5.147 | 线上宝塔源站 | 8.3MB | → 19% |
| 7 | 15.152.6.51 | 测试环境数据库（Mongo/Redis） | — | 已清除 |
| 8 | 16.208.32.40 | 生产定时任务机（Spug） | — | 内存吃紧（3.3G/3.8G） |
| 9 | 138.252.248.139 | JP 前置/备用回源 | — | → 17G 可用 |
| 10 | 103.207.68.124 | 旧测试任务机 | — | 3.9G/7.8G（已释放） |
| 11 | 15.152.160.250 | 测试 Spug（18game-spug） | — | 1.1G/3.7G（已释放） |

### 3.2 无法核验（5 台，需用其它通道确认）

| 主机 | 用途 | 探测结果 |
| --- | --- | --- |
| 101.47.158.5 | 登记在册主机 | 22 与 443 均不通 |
| 38.54.17.130 | 登记在册主机 | SSH 端口通，但现有密钥不可用 |
| 38.92.8.34 | 老测试宝塔（密码认证） | SSH 端口通，但只有密码渠道，无密钥 |
| 43.241.16.84 | 老前置机 | 22 与 443 均不通 |
| 43.160.201.59 | 自动化测试机 | 22 与 443 均不通 |

> 巡检覆盖：`servers.yml` 全部 12 个公网 IP + 会话中已知的其它生产/测试/前置主机，共 16 台；
> 其中 11 台确认感染并已处置，5 台因网络或凭据原因无法核验。

- 各主机植入时间不一（`/var/local/kworker` 目录时间：网关/前端 2024-05-29、宝塔 2024-05-30、
  后端 2026-06-17、监控 2025-12-11、测试 2026-08-25），说明是**长期存在的植入**，而非今日首次授权安全测试。
- 9 台机器的挖矿进程在处置前 ~1.5 小时几乎同时启动（etime 均约 01:24），疑似被统一拉起。

## 四、处置动作（逐台，均已执行）

```text
1) 取证隔离：/var/local/kworker/* + kworker.service + 进程/连接/服务状态 → /root/incident-kworker-<时间戳>/
2) 停用服务：systemctl stop/disable kworker.service
3) 杀进程：pgrep -f "[k]worker --config" 逐个 kill -9（用中括号写法避免误杀自己的会话）
4) 删持久化：rm /etc/systemd/system/kworker.service + daemon-reload；rm -rf /var/local/kworker
5) 封矿池：iptables 封 pool.supportxmr.com 解析出的 IP（INPUT DROP + OUTPUT REJECT）并兜底封 TCP 3333 出站
6) 持久化封堵：6 台写入 /usr/local/sbin/youdianse-miner-pool-block.sh + @reboot；
   测试库无 crontab → 改用 systemd oneshot 单元 youdianse-miner-pool-block.service（已 enable）
```

脚本已归档：`devops/scripts/2026-10-10-kworker-miner/`（`kworker_contain.sh`、`kworker_pool_block.sh`、README）。

## 五、验证

```text
· 11 台复核：挖矿进程 0 个、/var/local/kworker 目录不存在、kworker.service inactive
· 内存恢复：测试机 70.4% → 43.4%（可用 2.34G → 4.3G）；前端/监控各释放约 2GB；Spug 机内存压力明显缓解
· 业务自检：www.youdianse.com 首页 200、g654321.com 200、应用版本清单 200、version.txt 200；
  宝塔本机站点 200、宝塔→后端上游 404（业务响应，链路正常）；线上后端容器 Up；JP 前置 nginx 200；
  测试库 mongod/redis7 active 且端口在听
· 失陷面审计：无其它 systemd 单元引用 /var/local、无额外 UID=0 账户、crontab 无可疑 curl/wget/base64 条目、
  无 /etc/ld.so.preload；Spug 任务清单（56/69/38/68/29/30/33/37/59/48/58/40）均属正常业务，
  未发现授权安全测试者新增的调度任务
```

## 六、未确定项与主要风险

1. **授权安全测试入口尚未确定**：植入时间跨 2024-05 ~ 2026-08，且 9 台机器同源，需专项溯源
   （历史 SSH 认证日志、Web 应用漏洞、Docker/宝塔面板暴露面、共用密钥扩散等）。
2. **root 权限长期失陷 → 凭据必须按“已泄露”处理**（这是本次最重要的待办）：
   SSH 私钥/密码、AWS 访问密钥（后端 `env/.env.prod`、CICD 配置）、数据库口令（Mongo/Redis/MySQL）、
   Spug 凭据、Telegram bot token、CDN/Cloudflare/腾讯云凭据、发布口令。
3. 42xx 台机器上是否还有其它后门/Webshell，本轮只做了常规点位审计，建议做一次完整授权安全测试排查。
4. **5 台无法核验**（101.47.158.5、38.54.17.130、38.92.8.34、43.241.16.84、43.160.201.59）：
   需通过控制台 / SSM / 密码渠道确认；老测试宝塔 38.92.8.34 只有密码认证，是高风险点。
   后续新机器上线应纳入统一巡检（本次巡检脚本已入库可复用）。

## 七、建议动作（按优先级）

```text
P0 凭据轮换：SSH 密钥与所有运维口令、AWS 密钥、数据库口令、Telegram token、CDN/云厂商 API Key、发布口令
P0 收敛暴露面：禁止 SSH 密码登录与 root 直登（改堡垒机/跳板 + 密钥 + 二次验证）；复核安全组，
   仅放行必要端口（本次发现 8088/3003/3004/18090 等业务端口对公网开放）
P1 专项溯源：结合各主机 auth.log/应用日志定位首次授权安全测试路径与时间线
P2 加固检测：增加挖矿特征巡检（异常进程名/矿池域名/3333 等端口外连）、主机层 EDR 或 cron 级巡检；
   本次巡检脚本 `devops/scripts/2026-10-10-kworker-miner/` 可直接复用为定期巡检
P2 评估重装：root 长期失陷的机器建议重建（或至少全量比对系统文件）
```

## 八、附录：证据留存

```text
· 各主机证据：/root/incident-kworker-<时间戳>/（木马文件、服务单元、进程/连接快照、服务状态）
· 封堵脚本与说明：devops/scripts/2026-10-10-kworker-miner/
· 矿池钱包地址、config 关键字段见本文第二节
· 本文档不含任何我方 token、密钥或私钥内容
```
