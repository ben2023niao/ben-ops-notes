---
id: "doc-523fd9674fcc"
title: "18game 网关 CC 误报与 Meta 高频爬虫处置"
date: "2026-10-23T23:55:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Docker", "Nginx", "监控告警", "自动化", "CDN"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-23-2355-%E3%80%90%E5%AE%89%E5%85%A8%E4%BA%8B%E4%BB%B6%E3%80%9118game%E7%BD%91%E5%85%B3CC%E8%AF%AF%E6%8A%A5%E4%B8%8EMeta%E7%88%AC%E8%99%AB%E9%AB%98%E9%A2%91%E6%8A%93%E5%8F%96%E5%A4%84%E7%BD%AE.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-23-2355-【安全事件】18game网关CC误报与Meta爬虫高频抓取处置.md"
sourceSha256: "d042353ad5c085d357f7537baf99f54c3d95b3f7734f601856348b37593458ef"
sourceSystem: "project-doc"
---

# 18game 网关 CC 误报与 Meta 高频爬虫处置

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-23-2355-【安全事件】18game网关CC误报与Meta爬虫高频抓取处置.md`

> 整理日期：2026-10-23 23:55｜日期依据：文件名日期

- 时间：2026-10-23（北京时间）
- 环境：游点涩/18game 线上
- 网关：16.208.38.88
- 结论：本次没有 抗压能力测试/SYN Flood；明确授权安全测试是已拦截的登录撞库。持续高负载主要来自真实业务流量、
  H5/PC SSR 调用和 Meta 高频爬虫。

## 一、告警为什么看起来像授权安全测试

原告警只要 1 分钟负载超过固定值 15 就标记“疑似 CC/抗压能力测试”。本次 8 核网关 load 在 13–19 之间波动，
但现场指标不支持 抗压能力测试：

- established 约 1,300–2,400，远低于 40,000 阈值；
- SYN_RECV 仅个位数至数十，远低于 3,000 阈值；
- 首页 `GET /` 约 1–4 req/s，远低于 100 req/s 阈值；
- nginx worker 连接错误为 0，内存约 130–160MB；
- 全站请求约 1,000–1,200 req/s，HTTP 200 占 98% 以上。

高负载由 H5 SSR（约 300%–400% CPU）、PC SSR 和大量 API 请求共同造成。把“主机负载高”
直接写成“CC/抗压能力测试”会造成错误定性，也会把 CloudFront 边缘节点误列为授权安全测试源。

## 二、明确授权安全测试：登录撞库扫描

### 黑客画像

- 来源：`3.1.244.240`
- 网络：美国 Amazon AWS，AS16509，BGP 段 `3.0.0.0/15`
- UA：`python-requests/2.32.5`，POST 时伪装 Chrome UA
- 行为：自动化脚本，HEAD 探测和 POST 撞库混合
- 频率：15:30–15:47 UTC 共 2,694 次，约 2.6 req/s
- 结果：全部 HTTP 444，没有进入业务应用

### 授权安全测试目标

| 接口 | 请求数 |
| --- | ---: |
| `/api/v1/LoginNew/account` | 973 |
| `/api/v1/Login/email` | 578 |
| `/api/v1/Login/username` | 573 |
| `/api/v1/Login/account` | 570 |

其余 Python 脚本来源共 1,775 次，全部 444。线上后端 `api_request-2026-10-23.log` 中未找到
`3.1.244.240`，说明请求在网关层已被阻断，没有到达 PHP/MongoDB。

## 三、异常爬虫：Meta External Agent

### 识别结果

- UA：`meta-externalagent/1.1`
- 来源：Meta 自有 IPv6 `2a03:2880::/32`
- 样本客户端 IP：当前日志 1,127 个
- 行为：持续约 94 req/s，约 85% 为 POST；伪装 Chrome/Edge/Firefox UA 前缀
- 路径：`exposureCollect/report`、`User/getUserPostList`、`Tracking/recordPageVisit`、
  `configDict/getConfigDict`、`Lang/list`、`Community/config`、`User/getCommunityInfo`

这不是普通搜索引擎的页面/站点地图抓取。它会执行页面脚本并连带请求大量 API、埋点和社区数据。
来源和 UA 指向真实 Meta 网络，不是随机代理池伪造；问题在于抓取强度和资源消耗不可接受。

### 历史分时（日志归档计数）

| 时间窗口 | Meta 请求数 |
| --- | ---: |
| 10-22 14:30–16:00 | 51,924 |
| 10-22 16:00–17:45 | 48,580 |
| 10-22 17:45–21:30 | 502,072 |
| 10-22 21:30–10-23 00:00 | 798,028 |
| 10-23 00:00–03:00 | 1,406,966（峰值） |
| 10-23 03:00–05:30 | 1,241,960 |
| 10-23 05:30–07:45 | 919,897 |
| 10-23 07:45–09:45 | 800,122 |
| 10-23 09:45–11:30 | 611,940 |
| 10-23 11:30–13:00 | 489,196 |
| 10-23 13:00–14:30 | 474,840 |
| 10-23 14:30–15:30 | 342,426 |

## 四、如何区分真实搜索引擎和恶意爬虫

UA 只是声明，不能作为唯一身份依据。生产判定至少结合以下维度：

1. **官方 IP 段**：Googlebot、Bingbot、Applebot、Meta 都有自己的发布网段；
2. **DNS 一致性**：反查主机名必须落在官方域名，且正向解析回原 IP；
3. **robots/sitemap 行为**：是否读取规则、是否只抓页面、是否遵守频控；
4. **请求范围**：只抓页面还是大量调用 API、埋点、社区和用户资料接口；
5. **请求节奏**：单 ASN/网段/IP 的 QPS、并发、持续时间和峰谷；
6. **业务成本**：是否触发 SSR、数据库查询或不必要的写接口。

判定口径：

- UA 官方 + IP 官方 + FCrDNS 一致 + 行为正常 → 已验证搜索引擎；
- UA 官方但 IP 不在官方段 → 伪造/冒充，直接拦截；
- UA/IP 均为官方但速率和路径明显超限 → 真实爬虫的失控/不受欢迎抓取，单独限流或阻断；
- UA 普通浏览器但来源、节奏、路径呈现自动化特征 → 按恶意机器人处置。

## 五、本次修复

### 守卫与告警

- 只有网络阈值命中才标记 CC/抗压能力测试；单纯主机负载改标“主机高负载”；
- 负载阈值改为 `max(20, CPU核数×3.0)`，8 核机器为 24；
- 新增全站 QPS 阈值 3,000；
- 来源 IP 统一取 XFF 首跳，并排除 AWS 官方 CloudFront 段；
- 修复 access/error 日志轮转造成的负 QPS；
- established 对端字段从本地端改为远端；GET / 候选源改为真实客户端。

### 网关限流

- `perip_ssr` 从 `$binary_remote_addr`（CloudFront 边缘）改为 XFF 首跳真实客户端；
- 单真实客户端 SSR 并发从 50 调整为 200，避免正常 H5 首屏并行加载被误限；
- 配置备份后通过 `nginx -t`，网关受控重启加载。

### 爬虫策略

- `meta-externalagent` 返回 403；
- `facebookexternalhit` 链接预览保持 200；
- Googlebot、Bingbot、Applebot 和普通浏览器不受影响。

## 六、验证结果

- `nginx -t`：通过；
- 正常浏览器访问 `www.youdianse.com`、`h5.18h.game`：200；
- Googlebot UA：200；
- `facebookexternalhit`：200；
- `meta-externalagent`：403（CloudFront 和源站直连均验证）；
- 限流修复后 20 秒采样新增 `perip_ssr` 错误：0；
- 30 秒采样全站 QPS：约 1,170 → 约 1,005；
- 线上后端 API：约 314 QPS；
- 网关 load：约 19 → 约 16；
- H5/PC 容器运行正常，内存充足。

## 七、剩余风险与后续动作

1. 当前约 1,000 QPS 的剩余流量主要来自正常 H5/PC、移动 App 和 Meta 之外的客户端，已是容量问题，
   不应继续用“授权安全测试”方式处理。
2. 前端应把埋点合并上报，减少 `exposureCollect/report`、`tracking/record`、
   `Tracking/recordPageVisit` 的单用户高频调用。
3. ~~CloudFront/源站应继续优化 `_nuxt` 和静态图片缓存，避免重复回源 Nuxt SSR。~~
   已于 2026-10-24 增加网关本地只读代理缓存，整机 CPU 从接近 100% 降至约 45%。
4. 后续接入 Googlebot/Bingbot/Applebot 官方 IP 清单与 FCrDNS 校验，形成统一的“已验证爬虫白名单”。
5. 若业务峰值长期超过当前 8 核网关容量，应按监控数据扩容或拆分 H5/PC SSR 节点。

## 八、代码与配置

- `18game_devops/devops/scripts/cc_guard/attack_alert.py`
- `18game_devops/devops/scripts/cc_guard/youdianse_cc_guard.py`
- `18game_devops/devops/python/ben-bot/data/scripts/线上环境-游点涩-新前端配置/nginx/10-youdianse-prod-maps.conf`
- `18game_devops/devops/python/ben-bot/data/scripts/线上环境-游点涩-新前端配置/nginx/20-youdianse-prod-unified.conf`

线上备份：

- `10-youdianse-prod-maps.conf.bak.ssr-xff-20261023-154240`
- `10-youdianse-prod-maps.conf.bak.meta-crawler-20261023-155104`
- `20-youdianse-prod-unified.conf.bak.ssr-conn200-20261023-154610`
- `20-youdianse-prod-unified.conf.bak.meta-crawler-20261023-155104`
