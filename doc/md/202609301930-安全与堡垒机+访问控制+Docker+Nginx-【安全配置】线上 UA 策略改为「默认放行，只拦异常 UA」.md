---
id: "doc-a7aa9256af92"
title: "【安全配置】线上 UA 策略改为「默认放行，只拦异常 UA」"
date: "2026-09-30T19:30:00"
categories: ["安全与堡垒机", "访问控制"]
tags: ["安全与堡垒机", "访问控制", "Docker", "Nginx", "Apache", "PHP", "SQL注入", "漏洞"]
source: "03-安全运营与应急/03-安全配置与访问控制/游点涩-网关与白名单/2026-09-30-1930-【安全配置】线上UA策略改为默认放行-只拦异常UA.md"
---

# 【安全配置】线上 UA 策略改为「默认放行，只拦异常 UA」

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609301930-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%2BDocker%2BNginx-%E3%80%90%E5%AE%89%E5%85%A8%E9%85%8D%E7%BD%AE%E3%80%91%E7%BA%BF%E4%B8%8A%20UA%20%E7%AD%96%E7%95%A5%E6%94%B9%E4%B8%BA%E3%80%8C%E9%BB%98%E8%AE%A4%E6%94%BE%E8%A1%8C%EF%BC%8C%E5%8F%AA%E6%8B%A6%E5%BC%82%E5%B8%B8%20UA%E3%80%8D.md)

> 来源：本地项目文档 `game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-30-1930-【安全配置】线上UA策略改为默认放行-只拦异常UA.md`
> 整理：2026-11-09。仅复制到知识库，未改动原项目文件；敏感凭据已脱敏。

- 日期：2026-09-30 19:30（北京时间）
- 生效范围：网关 203.0.113.1 + 宝塔源站 203.0.113.1（后端该 map 只作用于登录 location）
- 前置改动：同日 19:20 已把白名单扩到「真实客户端 + 全部搜索引擎爬虫」，本次进一步改为黑名单策略

## 一、为什么改成黑名单

原来的规则是**白名单制**：`default 0`，UA 不在名单里就返回 444。这个思路在这一天里连续误伤了 6 类正常流量：

| 时间 | 被误伤的对象 | 后果 |

| --- | --- | --- |

| 上午 | iOS plist 抓取（`com.apple.appstored` / `MacAppStore`） | iPhone「在 iTunes 中打开」无反应，对外表现为 502 |

| 上午 | 1game auth 服务器（`python-requests`）调 `checkTokenV2` | 玩家 token 校验失败，登录报错 |

| 上午 | 支付方回调（`Go-http-client`） | 几百单回调被拦成 502，订单积压 |

| 下午 | 自动化测试机（`python-requests`） | 127 条用例 106 条失败，误判为业务故障 |

| 19:20 | 全部搜索引擎爬虫 | Google/百度/Bing 等一个都进不来，站点无法被收录 |

| 19:20 | 华为/荣耀/鸿蒙浏览器、Safari 系统进程 | 40 分钟 3,700+ 次真实访问被静默 444 |

根因不是名单不够长，而是**「默认拒绝」这个方向本身**：互联网上真实客户端形态无穷无尽（新机型、新浏览器、
系统进程、IoT、TV、合作方 SDK），任何白名单都会持续漏。相反，「异常 UA」是一个有限且稳定的集合。

## 二、新策略

```nginx
map $http_user_agent $yds_ua_real {
    default 1;                     # ← 默认放行
    ""                            0;   # 空 UA
    "~*^$"                        0;   # 空 UA
    "~*^-$"                       0;   # 缺失 UA
    "~*^Mozilla/[45]\.0 *$"       0;   # 极简伪造 UA（登录刷量 99.8% 用的就是这个）
    "~*^Mozilla *$"               0;
    "~*^curl" / "^Wget" / "^wget" 0;   # 命令行工具
    "~*^python-requests" / "^python-urllib" / "^Python-urllib" / "^aiohttp" / "^Scrapy" / "^scrapy" / "^httpie" 0;
    "~*sqlmap|nikto|nmap|masscan|zgrab|nuclei|wpscan|gobuster|dirbuster|dirsearch|feroxbuster|
        ffuf|wfuzz|hydra|metasploit|acunetix|netsparker|nessus|qualys|openvas|zmeu|whatweb|w3af|
        Censys|InternetMeasurement" 0;   # 漏洞扫描 / 攻击工具
}
```

共 **40 条拦截规则**，除此之外一律放行。规则三处同源：网关、宝塔源站、仓库 `nginx/main.conf`。

### 与上一版的区别

- 上一版（19:20）是「白名单 + 放行搜索引擎爬虫」，仍属默认拒绝；
- 本版是**默认放行 + 黑名单**，搜索引擎爬虫、新机型浏览器、合作方 SDK（`Go-http-client`、
  `Apache-HttpClient`）、自测工具（`PostmanRuntime`）、爬虫库（`libwww-perl`）、以及**前所未见的 UA** 全部放行。

## 三、防护能力没有因此下降

UA 过滤本来就不是主要防线，真正的防线是下面三层，全部保持原样：

1. **IP 层**：CC 守卫（10 秒一轮）自动识别刷量源 → 网关/源站 Nginx 清单 + iptables 封禁；
   自有 IP、合作方服务器、自动化测试机永久白名单。
2. **限流层**：网关 `/api` 50r/s、宝塔源站 30r/s、登录接口 5r/s（burst 20）、后端 10r/s 兜底；
   国家级临时拉黑（海外）只作用于登录接口，CN/HK/MO/TW 不参与。
3. **路径层**：支付、`/api/sdk/*`、`/customer`、`/channel`、应用版本清单等路径整体豁免拦截。

实测确认：`python-requests`、极简伪造 UA `Mozilla/5.0` 打登录接口依旧被 444（对外 502）；
真实浏览器登录 200；业务页面、支付回调不受影响。

> 提醒：默认放行后，攻击者伪造浏览器 UA 就能穿过 UA 这一层（原本也可以），
> 因此防刷完全依赖限流 + IP 封禁 + CC 守卫，三者必须保持开启。

## 四、验证（逐 UA 探测，直连网关 `/healthz`）

| 预期放行 | 结果 | | 预期拦截 | 结果 |

| --- | --- | --- | --- | --- |

| Googlebot / Baiduspider / PetalBot | 200 | | 空 UA | 444 |

| Safari 系统进程 NetworkingExtension | 200 | | 极简伪造 `Mozilla/5.0` / `Mozilla/4.0` | 444 |

| 荣耀/华为浏览器（嵌套括号 UA） | 200 | | `curl` / `Wget` | 444 |

| 安卓 Flutter App | 200 | | `python-requests` | 444 |

| `Go-http-client` / `Apache-HttpClient` | 200 | | `sqlmap` | 444 |

| `PostmanRuntime` / `libwww-perl` | 200 | | `nikto` | 444 |

| 前所未见的新客户端 UA | 200 | | `nuclei` | 444 |

| iOS 第三方 App（CFNetwork） | 200 | | | |

21 个用例全部符合预期。经 CloudFront 端到端复测：首页 200、Googlebot 200、Baiduspider 200、
支付回调 200；`python-requests` / 伪造 UA 打登录接口依旧被拦（502），真实浏览器登录 200。

## 五、部署与回滚

| 层 | 文件 | 状态 |

| --- | --- | --- |

| 网关 203.0.113.1 | `/etc/nginx/conf.d/10-youdianse-prod-maps.conf` | 已改 + `nginx -t` 通过 + reload |

| 宝塔源站 203.0.113.1 | `/www/server/panel/vhost/nginx/00-abuse-guard-http.conf` | 已改 + `nginx -t` 通过 + reload |

| 后端 203.0.113.1 | `nginx/main.conf` | 仓库同步（该层只作用于登录 location） |

回滚（回上一版白名单/爬虫放行版）：还原 `*.bak.uabl-20260930-111642`（网关）/
`*.bak.uabl-20260930-191642`（源站）→ `nginx -t` → `nginx -s reload`；
再上一版为 `*.bak.uav2-20260930-*`。

## 六、后续建议

1. 黑名单要定期复核：出现新型扫描器/攻击工具 UA 时补进名单（攻击者有成本才会换 UA，频次远低于白名单漏放行）。
2. 若某类合作方客户端开始被限流影响，优先用「路径级豁免」而不是加 UA 白名单。
3. 网关仍未设置 `worker_shutdown_timeout`，reload 后旧 worker 会短暂沿用旧规则，建议补上 `5s`。

## 七、涉及文件

- `ops/production/scripts/gateway-ua-authenticity.conf`
- `ops/production/scripts/baota-www-abuse-guard-http.conf`
- `nginx/main.conf`
