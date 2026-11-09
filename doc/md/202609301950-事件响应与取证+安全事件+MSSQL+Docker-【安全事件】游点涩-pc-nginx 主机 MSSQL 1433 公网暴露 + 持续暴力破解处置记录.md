---
id: "doc-829f9a0726c2"
title: "【安全事件】游点涩-pc-nginx 主机 MSSQL 1433 公网暴露 + 持续暴力破解处置记录"
date: "2026-09-30T19:50:00"
categories: ["事件响应与取证", "安全事件"]
tags: ["事件响应与取证", "安全事件", "MSSQL", "Docker", "Nginx", "PHP", "SQL注入", "漏洞"]
source: "03-安全运营与应急/01-安全事件与取证/游点涩-主机与注入事件/2026-09-30-1950-【安全事件】pc-nginx主机MSSQL1433公网暴露与暴力破解处置记录.md"
---

# 【安全事件】游点涩-pc-nginx 主机 MSSQL 1433 公网暴露 + 持续暴力破解处置记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609301950-%E4%BA%8B%E4%BB%B6%E5%93%8D%E5%BA%94%E4%B8%8E%E5%8F%96%E8%AF%81%2B%E5%AE%89%E5%85%A8%E4%BA%8B%E4%BB%B6%2BMSSQL%2BDocker-%E3%80%90%E5%AE%89%E5%85%A8%E4%BA%8B%E4%BB%B6%E3%80%91%E6%B8%B8%E7%82%B9%E6%B6%A9-pc-nginx%20%E4%B8%BB%E6%9C%BA%20MSSQL%201433%20%E5%85%AC%E7%BD%91%E6%9A%B4%E9%9C%B2%20%2B%20%E6%8C%81%E7%BB%AD%E6%9A%B4%E5%8A%9B%E7%A0%B4%E8%A7%A3%E5%A4%84%E7%BD%AE%E8%AE%B0%E5%BD%95.md)

> 来源：本地项目文档 `game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-30-1950-【安全事件】pc-nginx主机MSSQL1433公网暴露与暴力破解处置记录.md`
> 整理：2026-11-09。仅复制到知识库，未改动原项目文件；敏感凭据已脱敏。

- 文档日期：2026-09-30 19:50（北京）/ 11:50（UTC）
- 主机：`游点涩-pc-nginx` = **203.0.113.1**（18game H5/PC 统一网关，内网 203.0.113.1）
- 分类：安全事件（E4 · 生产环境外部暴露 + 持续暴力破解）
- 发现方式：本轮「清理垃圾日志」时发现 `/var/log/syslog` 被 MSSQL 登录失败刷到 2.5G，顺线追出

## 一、发现经过

```text
起因：清理该机垃圾日志时，/var/log/syslog 已达 2498M，且最后 2 万行里 99% 是同一条：
  sqlservr[864]: Logon Error: 18456, Severity: 14, State: 8.
  sqlservr[864]: Login failed for user 'sa'. Reason: Password did not match ... [CLIENT: x.x.x.x]
```

## 二、事实（VERIFIED）

- `sqlservr` 监听 **`203.0.113.1:1433` 与 `[::]:1433`**（对公网全开）
- syslog 中 `Login failed for user 'sa'` 累计 **7,957,782 条**（统计窗口：Sep 27 07:07 起，
  约 2.6M 次/天、平均约 30 次/秒）
- 攻击源 TOP（按失败次数）：

| 来源 IP | 失败次数 |

| --- | --- |

| `203.0.113.1`（HostHatch） | 7,933,721（99.7%） |

| `203.0.113.1` | 13,336 |

| `203.0.113.1` | 4,031 |

| `203.0.113.1` | 3,856 |

| `203.0.113.1` / `203.0.113.1` / `203.0.113.1` / `203.0.113.1` | 数百 |

- 处置前 `ss -tn` 显示 `203.0.113.1` 对本机 1433 保持 **59 条 ESTABLISHED** 连接（高频重试）
- 注：`203.0.113.1` **与本机 nginx 攻击源黑名单里的那个 IP 是同一个**
  （见 `10-youdianse-prod-maps.conf` 的 `~*203.0.113.1 1`），
  即该来源同时打 80/443（已被 nginx 444）和 1433（此前无任何防护）
- 附带影响：MSSQL 常驻 **3.4G 内存**（该机最大内存占用进程）、
  `/var/opt/mssql/log/errorlog` 被刷到 **1.7G**

## 三、处置（2026-09-30 11:38~11:45 UTC）

1. **本机防火墙止血**（仅放行 VPC/内网，其余 DROP）：

```
iptables -I INPUT 1 -p tcp --dport 1433 -s 203.0.113.1/16 -j ACCEPT
iptables -I INPUT 2 -p tcp --dport 1433 -j DROP
```

2. **断开存量连接**：`ss -K dst 203.0.113.1` 连续执行 3 轮 → 外部连接归零
3. **持久化**：新增 `/usr/local/sbin/youdianse-mssql-1433-guard.sh`（幂等，重复执行不会加重复规则），
   root crontab 增加 `@reboot /usr/local/sbin/youdianse-mssql-1433-guard.sh`
   （本机没有 netfilter-persistent，重启后靠这条恢复）

## 四、验证

```text
· 外部连接：ss -tn | grep :1433 | grep -v 203.0.113.1 → 0 条
· 攻击是否停止：连续 10 秒 syslog 新增 "Login failed" = 0 条（处置前约 30 条/秒）
· 规则生效：iptables -S INPUT 可见 ACCEPT(203.0.113.1/16) + DROP 两条
· 业务无影响：nginx active、H5(3003)/PC(3004)/healthz 全部 200、公网首页 200
```

## 五、遗留风险与建议（待决策）

1. **AWS 安全组大概率仍对 203.0.113.1/0 放行 1433** —— 本次只是本机 iptables 兜底。
   建议在安全组直接把 1433 收口到 VPC 网段（或删除该入站规则），否则任何一次
   系统重装/规则丢失都会重新暴露。
2. **MSSQL 疑似无人使用**：处置期间本机无任何正常客户端连接（只有暴力破解与 203.0.113.1 少量）。
   若确认业务不需要，建议停用/卸载 —— 可同时回收 3.4G 内存与 1.7G errorlog
   （该机此前「内存使用率偏高」的主要占用之一就是它）。
3. `sa` 账号若曾使用弱口令，建议改密/禁用；MSSQL 未用时直接停服务最彻底。
4. `/var/opt/mssql/log/errorlog` 1.7G 未处理：MSSQL 持有文件句柄，安全做法是
   `EXEC sp_cycle_errorlog`（需有效凭据）或随服务停用一并处理，**不建议直接 truncate**。

## 六、回滚

```text
· 删除 iptables 两条规则：iptables -D INPUT -p tcp --dport 1433 -s 203.0.113.1/16 -j ACCEPT
                          iptables -D INPUT -p tcp --dport 1433 -j DROP
· 移除 root crontab 中 `@reboot /usr/local/sbin/youdianse-mssql-1433-guard.sh` 一行
· 删除 /usr/local/sbin/youdianse-mssql-1433-guard.sh（如需彻底撤销）
```

## 七、安全与敏感内容

本记录不含 token、密钥、私钥正文；攻击源 IP 与统计口径属安全事件证据，可记录。

## 八、追查：这个 MSSQL 是干什么的？（2026-09-30 12:10 UTC 补充）

### 8.1 结论：是**标准的"装完没人用"组件**，不是业务依赖

- 安装时间：**2026-06-10 21:49 UTC**（`/var/log/dpkg.log`：`install mssql-server:16.0.4255.1-8`），
  与 `/opt/mssql`、`/var/opt/mssql` 目录创建时间完全一致 —— 即**服务器初始装机时就一并装上了**
- 版本：SQL Server 2022（16.0.4255.1），`mssql-tools18` 同装；`mssql.conf` 为默认（仅 EULA + sqlagent）
- **没有任何用户数据库**：`/var/opt/mssql/data` 只有 `master/model/msdb/tempdb` 系列系统库
  （`master.mdf` 的修改时间只是被暴力破解的登录尝试刷出来的），从未建过业务库
- **没有任何调用方**：四台机器上没有服务、cron、容器、应用配置引用 `1433`/`mssql`
  （唯一命中是新加的加固脚本本身）；容器只有 H5/PC 前端与 beszel-agent
- 连接来源只有两类：`203.0.113.1`（SQL Server 自身/Agent 的内部连接）+ 外部暴力破解
- `bash_history` 无安装痕迹（装机脚本或他人会话执行，已无从追溯）

### 8.2 全机队核查（同一时间点上，四台线上机全都有）

| 主机 | 角色 | MSSQL | 1433 监听 | 用户数据库 | errorlog | 登录失败次数 | 处置 |

| --- | --- | --- | --- | --- | --- | --- | --- |

| 203.0.113.1 | pc-nginx 网关 | active | `203.0.113.1:1433` | 无 | 1.7G | **795 万** | 已封 |

| 203.0.113.1 | 线上后端 | active | `203.0.113.1:1433` | 无 | 36M | 7.2 万 | 已封 |

| 203.0.113.1 | 线上前端 | active | `203.0.113.1:1433` | 无 | 256M | 2.6 万 | 已封 |

| 203.0.113.1 | 宝塔入口 | 未运行/未对外 | `*:1433` | 无（仅系统库） | 20K | 0 | 已封 |

共同点：**都装了、都没用、都没有业务库**。三台监听 `203.0.113.1` 的机器同时在挨打
（后端 5 万次来自 `203.0.113.1`，前端 1.6 万次来自 `203.0.113.1`）。

### 8.3 四台统一加固与验证

- 统一脚本 `/usr/local/sbin/youdianse-mssql-1433-guard.sh`（幂等：按规则序号清理历史/重复规则后再插入），
  四台 root crontab 均加 `@reboot` 恢复
- 现状：每台 INPUT 仅两条 1433 规则（`ACCEPT 203.0.113.1/16` + `DROP`），外部连接 0
- **验证方式与假象排除**：
  - 网关 DROP 计数器 8 秒内 6595 → 7030（+435），说明外部 SYN 正在被丢弃
  - 从 ben-bot 机（AWS 新加坡，VPC 外）测三台 `1433` 全部不可达；
    发 MSSQL 预登录包无任何响应（超时）
  - 注意：从办公网/本机 Python `connect()` 测会**误报"可连"** —— 实测本机连
    1434 / 9999 / 14330 这些确定关闭的端口也报成功，是本机出口网络中间盒造成的假象，
    不能作为"端口还开着"的依据
- AWS 安全组层面仍需收口（本机规则只是兜底，见第五节第 1 条）

### 8.4 业务影响确认（重点）

加固只涉及 `1433`（且保留 VPC 内访问），业务链路实测无影响：

| 验证项 | 结果 |

| --- | --- |

| 公网页面：www / h5.game-app543 / g654321 / baiyingnet / feijuka / onbrp | 全部 200 |

| 应用版本清单 `/api/v1/appVersionManifest/index` | 200（返回合法 plist） |

| 登录接口（真实浏览器 UA） | 200 |

| 支付回调（Go-http-client UA） | 200 |

| 宝塔 → 后端上游 `203.0.113.1:8088`（VPC 内正常链路） | 业务响应（404=应用可达） |

| 后端 `8088` 从本机/公网直连 | 不可达 —— **属既有设计**（该端口本来就只允许 VPC，非本次改动） |

## 九、处置升级：四台统一**停用** MSSQL（观察期）+ 垃圾日志清理（2026-09-30 12:20~12:35 UTC）

### 9.1 用户决策

用户确认：**先停服务观察一段时间**（不卸载），并把垃圾日志清理掉；需确认宝塔不依赖它。

### 9.2 「宝塔是否需要 MSSQL」的核查结论：**不需要**

- 宝塔面板自己的库 `/www/server/panel/data/default.db` 中 **`databases` 表 0 条**（没有任何 SQL Server 库登记）
- 面板/站点配置里对 `mssql|1433|sqlsrv` 的命中全部是**面板自带的字典/模板**：
  `config/weak_pass.txt`、`config/pass1000.txt`（弱口令字典）、`overview_template.json`（UI 模板）、
  `plugin_list.json`（插件目录）、`data/warning/*.json`（漏洞告警库）、`safeCloud` 规则（webshell 检测）
- 站点 PHP 目录命中仅为 PHP 源码自带的 `mssql_*` 函数名与 Zend 头文件
- 停服务后实测：`bt` 面板服务 `active`、面板端口响应、本机 `www`/`h5` 站点 200 —— **面板与站点完全不受影响**
- 结论：宝塔、四个站点、后端 PHP、H5/PC 前端**都不使用 MSSQL**，可以停

### 9.3 停用动作（四台，保留数据、可一条命令恢复）

```
systemctl stop mssql-server      # 服务停止
systemctl disable mssql-server   # 禁止开机自启（观察期内重启也不会自己起来）
恢复方式：systemctl enable --now mssql-server
```

| 主机 | mssql | 开机自启 | 1433 监听 | 内存（用/总） | 磁盘 |

| --- | --- | --- | --- | --- | --- |

| 203.0.113.1 | inactive | disabled | 0 | 6547M / 20522M | 7.9G / 49G（17%） |

| 203.0.113.1 | inactive | disabled | 0 | 1147M / 31159M | 17G / 49G（35%） |

| 203.0.113.1 | inactive | disabled | 0 | 1292M / 7727M | 14G / 49G（28%） |

| 203.0.113.1 | inactive | disabled | 0 | 1214M / 20530M | 15G / 49G（30%） |

**内存回收**：网关 10066M→6829M、后端 2382M→1145M、前端 2249M→1223M、宝塔 2258M→1207M，
四台合计释放约 **6.5G 内存**。1433 已无任何监听（iptables 规则保留作为第二层）。

### 9.4 垃圾日志清理

| 对象 | 清理前 | 清理后 | 说明 |

| --- | --- | --- | --- |

| 网关 `/var/opt/mssql/log` | 2759M | 1M | 先用 `tail -20000` 存样本再删 |

| 后端 `/var/opt/mssql/log` | 1155M | 2M | 同上 |

| 前端 `/var/opt/mssql/log` | 1320M | 1M | 同上 |

| 宝塔 `/var/opt/mssql/log` | 421M | 1M | 同上 |

| 后端 journal | 3.8G | 248M | `journalctl --vacuum-size=200M` |

| 前端 journal | 888M | 208M | 同上 |

| 后端/前端健康告警日志 | 26M×2 / 19M×2 | 0 | 与同源 `.cron.log` 重复，直接清空 |

证据样本保留：四台 `/root/mssql-log-sample-<时间戳>.tar.gz`（各约 1M，含 errorlog 末 2 万行）
与 `/root/mssql-log-cleanup-<时间戳>.txt`（清理前文件清单）。

### 9.5 观察期与回滚

- **观察期**：至确认无影响为止（建议跨一个完整业务日 + 节后首个工作日），期间关注
  后端 API/发布、宝塔面板、CICD、H5/PC 页面与支付回调；当前（停用后即刻）全部 200
- **回滚**（1 条命令，数据未动）：`systemctl enable --now mssql-server`
- 卸载（如观察期确认无问题后再决定）：`apt purge mssql-server mssql-tools18` + 删除
  `/var/opt/mssql`、`/opt/mssql`（**未执行**，等用户决定）

### 9.6 停用后业务验证（全部通过）

```
www.youdianse.com 首页 200 ｜ 应用版本清单(plist) 200 ｜ h5.game-app543.com 200 ｜
g654321.com 200 ｜ feijuka.com 200 ｜ 登录接口 200 ｜ 支付回调 200
宝塔面板 active（端口有响应）｜ 宝塔本机 www / h5 站点 200
```
