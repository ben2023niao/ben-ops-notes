---
id: "doc-3b24dca96220"
title: "2026-09-09 故障复盘：18game 网关 nginx 连接异常（workerconnections are not enough）"
date: "2026-09-09T14:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "Nginx", "Redis", "监控告警", "自动化"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-09_1440-%E3%80%90%E6%95%85%E9%9A%9C%E5%A4%8D%E7%9B%98%E3%80%9118game%E7%BD%91%E5%85%B3nginx%E8%BF%9E%E6%8E%A5%E5%BC%82%E5%B8%B8%E8%AF%A6%E7%BB%86%E6%A0%B9%E5%9B%A0%E4%B8%8E%E8%B4%A3%E4%BB%BB%E5%88%92%E5%88%86.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-09_1440-【故障复盘】18game网关nginx连接异常详细根因与责任划分.md"
sourceSha256: "6cc13f72c60bf583dff52294ebce6f6daf2b18d4036757ae3b3e34112b0add14"
sourceSystem: "project-doc"
---

# 2026-09-09 故障复盘：18game 网关 nginx 连接异常（workerconnections are not enough）

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-09_1440-【故障复盘】18game网关nginx连接异常详细根因与责任划分.md`

> 整理日期：2026-09-09 14:40｜日期依据：文件名日期

环境标签：线上 / 网关 / nginx / Node SSR / 后端发布

时间：2026-09-09 14:40（北京时间，Asia/Manila = UTC+8）

结论一句话：**本次不是单纯 nginx 参数问题，而是“首页 SSR 高并发 → Node/PHP 接口超时 → CloudFront/客户端重试 → 网关连接与 socket 堆积”的级联故障；最近一次线上后端发布（main-616c296，14:10 北京）与故障起点（14:18 北京）强相关，责任需按“后端发布复核 / 前端 SSR 架构 / 运维容量与告警”三方落实。**

---

## 1. 故障现象与处理时间线（北京时间）

| 时间（北京） | 事件 |
| --- | --- |
| 14:10:56 | @melo_sre 通过 CICD 发布后端 main `616c296da9cd`（发布日志：`游点涩-后端-运维-@melo_sre-...-main-616c296da9cd-20260909-141056.log.txt`） |
| 14:11:33~50 | 后端镜像构建并重建 web/nginx/cron，健康检查 SUCCESS（HTTP 200 / Session / Redis / Mongo） |
| 14:18~14:20 | 第一轮故障窗口：网关/SSR 超载，约 33.6 万请求、以 `GET /`（SSR 首页）为主 |
| 14:30 前后 | 第二轮更严重：负载 21→51，H5/PC 公网 000，`worker_connections` 告警持续增长 |
| 14:34 | 运维应急处理：nginx 容量加固 + 优雅 reload；重启 PC SSR 集群打破超时/重启环路 |
| 14:40 | 恢复：负载约 1.56~2.5，H5/PC `version.json` 与首页 200（0.1~0.8s），告警增量 0，PC worker 稳定 5 分钟以上 |

告警总量：`409656` 条 `4096 worker_connections are not enough`（截至 14:34 应急处理时不再增长）。

---

## 2. 故障窗口的流量与状态证据（14:18-14:20，UTC 06:18-06:20）

- 3 分钟窗口共约 `336,380` 条访问。
- 状态码分布：
  - `200`：30,577
  - `500`：135,804（SSR/Node 返回错误页）
  - `499`：161,407（客户端等不及断开）
  - `502`：3,939
  - `504`：4,443
- 请求几乎全部集中在 `GET /`（SSR 首页），来源 IP 高度分散（CloudFront 边缘 64.252.x/3.172.x/52.46.x + 大量公网 IP），不像单 IP 授权安全测试，更像“大量用户/边缘同时回源 + 5xx 重试”的突发。
- 同一时间 Node SSR 日志（PC）：
  - `[fetch] 请求失败 /modules/home fetch failed | cause: ETIMEDOUT | target: https://www.youdianse.com/api/v1`
  - `[c-request-view] SSR 请求失败 /modules/home [TimeoutError]`
  - H5 同步出现 `/system/info` 请求失败并“使用空配置降级”。
- 网关 nginx error log 同步出现大量：
  - `worker_connections are not enough while connecting to upstream`
  - `upstream timed out ... upstream: "https://203.0.113.1:443/api/v1/..."`（线上宝塔前端→后端 203.0.113.1:8088）
- 连接状态峰值（网关）：`FIN-WAIT-2 ≈ 22,875`、`TIME-WAIT ≈ 18,000+`、`CLOSE-WAIT ≈ 1,326`；TCP `ListenOverflows ≈ 218 万`、SYN Cookie 大量触发 → accept 队列被塞满。

---

## 3. 详细根因链

### 3.1 表层直接原因（为什么报 worker_connections 不足）

网关 8 个 nginx worker 原配置 `worker_connections 4096`，即每个 worker 最多同时 4096 条连接（含客户端 + 上游）。故障窗口内 Node SSR 每个首页请求会同时占用“客户端连接 + 到 Node 的上游连接 + 到后端 API 的连接”，高并发下单 worker 连接数瞬间触顶，nginx 无法再向上游建立连接：

```text
client -> nginx(worker_connections 4096 打满) -> upstream(203.0.113.1:3003/3004 或 203.0.113.1:443) 建立失败
```

### 3.2 中间层：Node SSR 自身被打满

- PC 容器 `youdianse_prod_pc_main_18game_pc_client_3004`（bbafe4a）8 个 PM2 cluster worker 全部 CPU 80-100%，容器 CPU 一度约 650-658%。
- PM2 出现“每 2 分钟整组重启、单个 worker 重启 4-6 次”的循环：worker 起来 → 收到 SSR 首页 → 内部 API fetch 超时/失败 → 产生 500 错误页 → 高内存/高 CPU → 重启。
- H5 容器同样 8 个 worker；两台前端共 16 个 Node worker 挤在网关主机 8 vCPU 上，CPU 争抢进一步放大。

### 3.3 放大机制 A：SSR 内部 API 走公网 CloudFront 回环

PC/H5 SSR 渲染首页时内部 `fetch` 的目标是：

```text
https://www.youdianse.com/api/v1/modules/home （公网 CloudFront）
```

CloudFront 会回源到线上网关/宝塔；网关拥堵时该 fetch 会 ETIMEDOUT 或拿到 CloudFront 502。于是：

```text
大量用户 GET /
  -> Node SSR 渲染首页
    -> SSR fetch 公网 www API（经 CloudFront 又回到同一网关）
      -> 网关已拥堵 -> fetch 超时/502
        -> Node 返回 500 错误页
          -> 客户端/边缘看到 5xx 后重试
            -> 产生更多 GET / -> 自放大
```

### 3.4 放大机制 B：socket 堆积 + accept 队列溢出

故障窗口大量 FIN-WAIT-2 / CLOSE_WAIT / TIME-WAIT 堆积（合计 4 万+），`ListenOverflows` 高达约 218 万，即使 nginx worker 没到 4096 上限，新连接也可能进不了 accept 队列，表现就是公网“打不开/000/超时”。

### 3.5 为什么与“最近后端发布”相关

- 最近一次线上后端变更：`14:10:56`（北京）发布 `main-616c296da9cd`，`14:11:50` 容器重建完成；故障首轮 `14:18` 开始，间隔约 7 分钟。
- 后端/宝塔/DB 当前实测均健康（负载 0.03/0.39，容器 0 个 5xx，接口 200/数 ms），说明故障已不在后端本身。
- 但该 git id 并非 09-09 才首次上线：CICD 目录还有 09-08 18:10、21:27 的相同 `616c296da9cd` 发布日志；网关 error log 在 09-09 02:16（北京）前后也已有同类 `worker_connections` 告警。因此不能把责任简单全推给“今天这次发布”，但“按最近变更排查”的第一步仍是核对 616c296 相对上一版的行为差异。
- 目前未能直接拉到 616c296 的 commit diff（GitLab 凭据 401/远端 main 已不再包含该 SHA 对象），需要由有仓库权限的后端直接核对/回复。

---

## 4. 责任划分（建议）

### 4.1 后端 / 开发（波特、Alex 等）

- 复核 `main-616c296da9cd` 相对上一发布版本的 diff，重点：
  - `/api/v1/modules/home`、`/api/v1/system/info`、`/api/v1/tracking/*` 是否新增慢查询/大循环/缓存失效/超时逻辑；
  - 是否有配置（环境变量、Redis key、CDN/域名）导致接口响应异常；
  - 回复该版本在 09-08 18:10/21:27 发布后是否已知问题。
- 结论确认是回归：给修复提交或明确同意回滚到上一业务版本；结论与时间请直接回本群。

### 4.2 前端（H5/PC）

- 首页/核心页 SSR 的 API 调用应避免公网 CloudFront 自环，建议：
  - SSR 内网直连（如 `http://203.0.113.1:8088` 或网关内网域名）；
  - fetch 增加超时、失败快速降级（先渲染可缓存内容），不要等 10s+；
  - 对 5xx 不要无脑重试。
- 本次 PC `bbafe4a` 与上一版 `96ad5e4` 的 diff 仅新增 `/sdk` 模块（10 个文件、2434 行），未改动首页 SSR 核心；前端代码责任较小，但 SSR 架构责任需认领。

### 4.3 运维（本群执行）

- 本次已完成应急：
  - nginx `worker_connections 4096 → 8192`；
  - `worker_rlimit_nofile 16384 → 65535`；
  - 开启 `multi_accept on`；
  - 备份：`/root/.codex-backup/nginx-gw-workerconn-20260909_063444/nginx.conf.bak`（UTC 命名，即北京 14:34）；
  - 优雅 reload nginx；重启 PC SSR 集群打破环路。
- 后续需做（另立任务）：
  - PC/H5 Node 实例数与网关 8 vCPU 的容量规划（当前各 8 worker 共 16 个易互相争抢）；
  - SSR API 内网化改造推进与验收；
  - 增加“PM2 重启次数/Node CPU/首页 QPS/worker_connections 告警数”细粒度告警；
  - 将网关 nginx.conf 变更与发布手册同步到仓库，避免只在服务器改。

### 4.4 监控/值班

- 本次从告警到恢复链路有效，但缺“请求突发与 Node/PM2 异常”关联告警，导致表象是 nginx 连接不足、实际是 SSR 自放大。补告警后应能更早区分“是流量型还是代码型”。

---

## 5. 当前状态与验证

- 公网：
  - `https://h5.yds-pc-h5-01.cc/version.json` → 200（约 0.1~0.7s）
  - `https://pc.yds-pc-h5-01.cc/version.json` → 200（约 0.1~0.35s）
  - H5/PC 首页 → 200
  - `POST https://www.youdianse.com/api/v1/modules/home` → 200（约 0.4s）
- 网关：`worker_connections` 告警增量 0（409656 条为存量）；负载约 1.5~2.5；PC PM2 稳定 5 分钟以上。
- 后端：宝塔网关机与后端容器负载正常、接口直连 200。

---

## 6. 回滚点与备注

- nginx 配置备份：`/root/.codex-backup/nginx-gw-workerconn-20260909_063444/nginx.conf.bak`；回滚：恢复文件 → `nginx -t` → reload。
- 后端若需回滚：用 CICD 选择上一业务版本重新发布（需后端确认上一版本号）。
- 本记录不含 token/密码/私钥/完整连接串等敏感信息。

---

## 7. 二次彻底核验（2026-09-09 14:47 北京）

### 7.1 核验结果

- 告警：`/var/log/nginx/error.log` 总量保持在 `409656` 不再增长；最近一条 `worker_connections are not enough` 时间 `14:30:17`（北京），即 14:34 加固处理后零新增。
- 60 秒观察窗口：负载 1.83→1.90，稳定；无新增告警。
- PC SSR：8 个 PM2 worker 自 14:34 重启后 uptime≥12 分钟，未再出现“2 分钟整组重启”循环，CPU 0%。
- H5 SSR：worker 连续运行 4-5 天，无异常重启。
- 公网三轮：`h5/pc.yds-pc-h5-01.cc/version.json` 全部 200（0.009~0.096s）；`POST https://www.youdianse.com/api/v1/modules/home` 200（0.012s）。
- 后端/宝塔/DB 链路实测正常。

结论：运行层已恢复并连续稳定（约 15 分钟零新增告警）。彻底根治还需补两项代码层闭环：后端复核 `616c296da9cd` diff；前端 SSR 内部 API 内网直连与超时/快速降级。

### 7.2 本次解决故障实际修改点

1. `/etc/nginx/nginx.conf`（16.208.38.88 网关）：
   - `worker_connections 4096 → 8192`：单 worker 可同时挂连接数翻倍，避免突发时秒级拒绝建上游连接；
   - `worker_rlimit_nofile 16384 → 65535`：同步提高 fd 上限，避免“连接数提升但 fd 不够”；
   - 开启 `multi_accept on`：一次事件循环多收连接，降低 accept 队列堆积。
2. `systemctl reload nginx`：无中断替换 worker，清理 FIN-WAIT-2/CLOSE-WAIT 等存量 socket，重置单 worker 连接计数。
3. 重启 PC SSR 集群（`docker exec youdianse_prod_pc_main_18game_pc_client_3004 pm2 restart all`）：清空卡在“内部 API 超时→500→客户端重试”循环中的进程与请求，新 worker 起来后 API 链路已恢复。

补充说明：只 reload nginx 不能恢复（Node 仍在满转）；只重启 SSR 不扩容也容易再次被连接告警授权安全测试，本次是两项组合才稳定。

---

## 8. 为什么“升级后端后”会突然爆发（2026-09-09 14:52 北京补充）

### 8.1 已核对 616c296d 相对上一正式版 a321bb24 的代码差异

- 范围：93 个文件，+76 / -589；
- 主要内容：
  - 大量定时任务/Job 去重删冗余（-589 行）；
  - 多表查询上限从 `99999999 / 99999` 收敛到 `9999`（消息、游戏预约、渠道扣量、热帖、SDK 配置等）；
  - `CdnService` 新增 `ql-prod-apk1.ql-boss.com`、`ql-prod-apk.ql-boss.com` 两个域名。
- 结论：本次代码本身以“性能优化/减负”为主，没有能直接制造约 33 万首页 `GET /` 的逻辑。

### 8.2 更合理的因果解释：发布动作 + 架构脆弱点

1. 发布 = `14:10:56` 开始、`14:11:50` 重建完成；重建时旧 web/nginx/cron 被强杀，进行中的 API 请求断连，PHP/Redis/Mongo 冷启动、opcache 重新预热。
2. 冷启动窗口内首页 SSR 的后端 fetch 只要慢/失败，Node 就超时返回 500；而 SSR 没有超时/熔断/快速降级，内部 fetch 还走公网 `https://www.youdianse.com/api/v1`（CloudFront 回源又回到同一网关）。
3. 出现 500 后浏览器/CloudFront 自动重试 → 更多 SSR → 更多 500 → PC 8 worker 满载并每约 2 分钟整组重启 → nginx/accept 队列被授权安全测试 → `worker_connections are not enough`。
4. 佐证：
   - 后端 14:11:50 健康检查 SUCCESS，其后接口/Redis/Mongo 一直正常；纯代码回归通常表现为持续 500/慢，而不是 7 分钟后才暴发；
   - 同一 616c296 于 09-08 发布过，09-09 02:16（北京）同类告警仅 871 条，说明并非“每次发布必爆”。

结论：应理解为“发布重建的脆弱窗口 + SSR 无保护 + CloudFront 公网回环”的放大效应；后端 616c296 diff 仍需复核并回群确认。

---

## 9. 复发处理记录（2026-09-09 14:48-15:00 北京）

### 9.1 复发现象

- 14:48-14:51：SSL Monitor 报 25+ 老 H5 域名“源站连续不可达”；H5/PC 公网 000。
- 现场与首轮不同：Node CPU 不高，而是 nginx worker 100%（sys≈97.7%）；`CLOSE-WAIT≈3.4 万`（约 2.8 万指向 203.0.113.1:3004/3003）、`FIN-WAIT-2≈2.8 万`；nginx error 出现 `connect() to 203.0.113.1:3004 failed (99)`；首页 SSR QPS 峰值约 940-1200。

### 9.2 新定位的根因级缺陷

- nginx 通过 `203.0.113.1:3003/3004` 访问 Node，实际每请求经过 Docker `docker-proxy` 用户态转发；docker-proxy 单点在高并发下 CPU 340%+、连接失败。
- nginx 配置里虽然定义了 `upstream ... keepalive`，但 `proxy_pass http://$h5pc_target` 是变量转发，**没有使用该 keepalive 组**，等于每请求新建/关闭 TCP，socket 清理跟不上即雪崩。
- 多次 reload 后旧 worker 因存量 keepalive 不退出，继续用旧配置（203.0.113.1）并烧 CPU；未设 `worker_shutdown_timeout` 导致 reload 清不掉。

### 9.3 已执行修复

1. nginx 上游由 `203.0.113.1:3003/3004` 改为直连容器桥接 IP：H5=`203.0.113.1:3003`，PC=`203.0.113.1:3004`（备份 `/root/.codex-backup/nginx-h5pc-direct-20260909_065350/`）。
2. `nginx.conf` 增加 `worker_shutdown_timeout 5s`（备份 `/root/.codex-backup/nginx.conf.bak.20260909_0656*`），强制旧 worker 退出。
3. 首页 SSR 临时全局限流：`limit_req_zone $request_uri zone=ssr_root:20m rate=300r/s` + `burst=100 nodelay`（备份 `/root/.codex-backup/nginx-ssr-limit-20260909_065543/`）。
4. 仓库模板 `线上环境-游点涩-新前端配置/nginx/10-youdianse-prod-maps.conf`、`20-youdianse-prod-unified.conf` 已整体同步为服务器现行版本（含直连 IP、限流、域名/证书 map/API keepalive）。

### 9.4 是否授权安全测试

限流生效后首页 SSR QPS 由峰值约 940 降至约 2；观察到的请求多为 CloudFront 边缘 + 正常浏览器 UA（含 GPTBot、DomainSecurityMonitor 等少量爬虫）。判断主要不是持续 抗压能力测试，而是“5xx → CDN/客户端重试 → SSR → 5xx”的自放大；保留限流观察，如需 WAF/CC 防护另立项。

### 9.5 待确认

- 备用 nginx 主机 IP（若有）：到目标机后按该机实际容器 IP 同步配置，不能照抄 172.17.0.x。
- 是否回滚后端到上一正式版 `a321bb24`（旧镜像仍在 16.209.16.108）；当前证据不建议仅因时间相关性回滚，最终由团队决定。

---

## 10. OOM 与 CC 授权安全测试确认（2026-09-09 15:07-15:15 北京）

### 10.1 现象

- 长观察第 6 轮（07:06 UTC / 15:06 北京）首页 SSR 再次突增；随后 nginx 全部 worker 被系统 OOM 杀死（`Result: oom-kill`，8 个 worker RSS 各约 2.2-2.3GB）。
- 15:05-15:08 共约 **127.6 万次 `GET /`（≈7000 r/s）**。
- 来源为大量机房/IDC IP（176.222.x、89.163.x、213.32.x、159.195.x 等，单 IP 3 分钟 4800-6300 次），非 CloudFront 边缘 IP；UA 伪装多种旧版 Chrome。
- 结论：**存在分布式 CC 授权安全测试**（此前判断的“自放大”低估了授权安全测试成分；两者可能叠加）。

### 10.2 已追加保护（15:14-15:16 北京）

1. `limit_req_status 429` + `limit_req_log_level notice`（拒绝请求不再刷 error log）。
2. `limit_conn_zone $binary_remote_addr zone=perip_ssr:10m` + `limit_conn perip_ssr 50`（单 IP 并发 SSR 上限）。
3. `http2_max_concurrent_streams 32`（限制单 HTTP/2 连接并发流）。
4. `client_header_timeout/client_body_timeout 10s`（加速清理慢连接/慢速授权安全测试）。
5. 429/503 响应不再写入 access.log（`map $status $log_ssr` + `if=`），降低日志写入压力。
6. nginx 已恢复并 reload；当前 worker RSS 10-15MB，公网 200。

备份：`/root/.codex-backup/nginx-protect-20260909_071406/`、`/root/.codex-backup/nginx-cc-20260909_0714*/`

### 10.3 后续

- 保持至少 30 分钟长观察（每 55s 采样负载/错误增量/首页 QPS/公网）。
- 授权安全测试侧建议：源站前加 WAF/CC 防护或把直连域名切到 CloudFront/WAF；与云厂商确认是否可限速。
- 备用 nginx 与回滚决定仍待团队确认。

---

## 11. 授权安全测试路线复盘与进一步处置（2026-09-09 15:20-15:45 北京）

### 11.1 授权安全测试路线（基于日志复盘）

- 授权安全测试目标：`16.208.38.88:80/443`，请求路径几乎全部为 `GET /`，HTTP/2。
- 关键特征：限流日志中 **Host=16.208.38.88（裸 IP）约 206.9 万次**，即授权安全测试者直接打网关 IP，不走域名/CDN，且绕过了 CDN/WAF 层。
- 请求头伪装大量不同版本 Chrome UA（Windows），源 IP 来自大量机房/IDC（单 IP 3 分钟数千次），属于分布式 CC botnet。
- 授权安全测试波次：14:18-14:20 / 14:30 / 14:48-14:51 / 15:05-15:08（北京），波峰 3 分钟 127.6 万次。
- 造成的破坏路径：大量请求经 nginx → Node SSR → Node 超时/500 → 客户端重试 → nginx worker/socket 堆积 → docker-proxy 单点失效 → worker 内存升至 2.2-2.3GB → 系统 OOM 杀 nginx。

### 11.2 已执行封堵与防护（15:23-15:38 北京）

1. iptables 封堵授权安全测试源：843 个“3 分钟 ≥400 次 GET /”的源 IP 加入 INPUT DROP（80/443）；规则与清单备份 `/root/.codex-backup/cc-block-20260909_1526/`。
2. nginx 对 `Host: 16.208.38.88` 直接 `return 444`（验证：Host=IP 立即断开；正常域名 200），从入口丢弃裸 IP 授权安全测试流量。
3. 保留：SSR 全局限流 300r/s、单 IP 并发 50、429/503 不入 access log、HTTP/2 流上限 32、慢连接超时 10s。
4. 仓库模板同步为服务器现行配置。

### 11.3 扩容与备用机核验结果

- 13.208.101.121（游点涩-前端，4C/8G，负载≈0.2，nginx 已装但 inactive）：仅运行老 H5 容器（3003），无 PC 容器；可用于部署/分担 H5，若要分担 PC 需先部署 PC 应用或配置反代，并需 DNS/CDN 分流。
- 16.208.5.147（宝塔 nginx）：无 3003/3004 前端反代，不作为 H5/PC 统一网关。
- ben-bot 容器 AWS 凭证（18game-dev，ap-southeast-1）：无 `ec2:DescribeInstances` 权限，不能创建 EC2；扩 2 台内网 SSR 需生产 AWS 权限/控制台操作。
- 仓库/发布脚本中当前仅 16.208.38.88 为“新 H5/PC”发布与网关目标；若存在第二台备用 PC/H5 网关，需提供 IP 才能同步配置（容器 IP 不能照抄）。

### 11.4 当前状态

- 3 小时长观察 07:22 UTC（15:22 北京）启动，每 55s 采样；封堵后 root SSR QPS 回到 1-2 r/s、nginx 内存约 100MB、err_delta=0、H5/PC 200。

### 11.5 自动化守卫与长观察（15:45 北京起）

- 观察延长到 09-10 03:00 北京时间（19:00 UTC）：`devops/scripts/cc_guard/gateway_observer_until3am.sh` 每 240s 采样，日志 `/tmp/gw_obs_until3am_v2.log`。
- CC 守卫：`devops/scripts/cc_guard/youdianse_cc_guard.py` 部署在 ben-bot 宿主机 cron 每分钟执行；识别首页 SSR QPS>100、worker_connections 增量>200、nginx RSS>1.8GB、nginx 非 active；自动 iptables 封禁高频源 IP（跳过内网/CloudFront 边缘），并向 `18GAME_ 上线群（正式環境）` 与 `18game运维` 报警。
- 首次基线已建立，后续按 60s 差值检测；cron 已写入 ben-bot 主机。
