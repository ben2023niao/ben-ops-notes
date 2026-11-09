---
id: "doc-c9f65db9dbaa"
title: "【问题排查】iOS「在 iTunes 中打开」无反应（plist 无法下载）根因与修复"
date: "2026-09-30T19:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Go", "Docker", "Nginx", "监控告警", "自动化"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-30-1900-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91iOS%20plist%20%E6%97%A0%E6%B3%95%E4%B8%8B%E8%BD%BD%E6%A0%B9%E5%9B%A0%E4%B8%8E%E4%BF%AE%E5%A4%8D-UA%E7%9C%9F%E5%AE%9E%E6%80%A7%E8%A7%84%E5%88%99%E8%AF%AF%E6%8B%A6Apple%E5%AE%A2%E6%88%B7%E7%AB%AF.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-30-1900-【问题排查】iOS plist 无法下载根因与修复-UA真实性规则误拦Apple客户端.md"
sourceSha256: "824ed59fc16d36ac8082062de84aa9791168de8cbeaff63827319b9fb573c446"
sourceSystem: "project-doc"
---

# 【问题排查】iOS「在 iTunes 中打开」无反应（plist 无法下载）根因与修复

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609301900-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BPython-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91iOS%E3%80%8C%E5%9C%A8%20iTunes%20%E4%B8%AD%E6%89%93%E5%BC%80%E3%80%8D%E6%97%A0%E5%8F%8D%E5%BA%94%EF%BC%88plist%20%E6%97%A0%E6%B3%95%E4%B8%8B%E8%BD%BD%EF%BC%89%E6%A0%B9%E5%9B%A0%E4%B8%8E%E4%BF%AE%E5%A4%8D.md)

> 整理日期：2026-09-30 19:00｜日期依据：文件名日期

- 日期：2026-09-30 19:00（北京时间）
- 环境：游点涩线上（www.youdianse.com / h5.game-app543.com）
- 等级：线上业务影响（iOS 安装分发链路不可用）
- 处置：网关 + 宝塔源站 UA 清单与路径规则放行 Apple 客户端；已生效并验证

## 一、结论（先看这里）

不是回调地址写错，也不是 plist 内容或域名解析问题，是**我们自己的「UA 真实性」防护规则误伤了 iOS 系统客户端**。

`itms-services://?action=download-manifest&url=...` 被点击后，真正去抓取 plist 的是系统 App Store 客户端
（UA = `com.apple.appstored` / `MacAppStore` / `itunesstored`），它不是浏览器、也不属于我们登记过的原生 App 前缀，
于是被 UA 规则判成「非完整真实客户端」直接 `444`（不回包）；CloudFront 对空响应统一包装成 `502`，
前端表现就是「点了没反应」。

## 二、现象与影响

- iPhone 点击「在 iTunes 中打开」无反应；`/api/v1/appVersionManifest/index?channel=official` 对 iOS 客户端返回 502。
- ipa 包本身可直接下载，测试环境可正常下载，只有线上 www.youdianse.com 不行 —— 差异在域名走的入口链路。
- 影响面：仅 iOS / macOS 的 plist 安装分发链路；浏览器访问、Android 渠道、支付回调、SDK / 合作方接口均不受影响。
- 该问题不是被授权安全测试，也不存在安全敞口，属于防护规则漏放行。

## 三、排查过程（证据）

### 3.1 网关日志：同一路径、同一时间窗，只有 UA 不同

网关 `16.208.38.88` `/var/log/nginx/access.log`，09-30 10:50~10:55：

```text
"GET /api/v1/appVersionManifest/index?channel=official" 444
  UA: com.apple.appstored/1.0 iOS/27.2 model/iPhone18,4 hwp/t8150 build/24B5089g (6; dt:362) AMS/1
"GET /api/v1/appVersionManifest/index?channel=official" 444
  UA: MacAppStore/3.0 MacAppStore/3.0 (Macintosh; OS X 26.5; 25F71) AppleWebKit/1624.2.5.11.4 AMS/1 (dt:1)
"GET /api/v1/appVersionManifest/index?channel=official" 200 1774
  UA: Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) ... Version/18.0 Mobile/15E148 Safari/604.1
```

浏览器 UA 200、系统客户端 UA 444 —— 直接指向 UA 真实性规则。

### 3.2 分层复现（只改 UA，其余完全相同）

| 测试位置 | UA | 修复前 |
| --- | --- | --- |
| `https://www.youdianse.com/...`（经 CloudFront） | `com.apple.appstored/1.0 ...` | 502 |
| `https://www.youdianse.com/...`（经 CloudFront） | `MacAppStore/3.0 ...` | 502 |
| `https://www.youdianse.com/...`（经 CloudFront） | iPhone Safari | 200 |
| 宝塔源站 `16.208.5.147` 直连（Host: www.youdianse.com） | `com.apple.appstored/1.0 ...` | 连接被断开（444） |

说明网关与宝塔源站**两层都在拦**，只修一层仍会被下一层 444。

## 四、根因

2026-09-30 为对抗「授权安全测试者在接口之间切换做 CC」上线了通用「UA 真实性」拦截：凡是 UA 不像完整真实客户端的请求
（`$yds_ua_real = 0`）直接 444。当时的白名单只覆盖：

- 完整浏览器 UA（`Mozilla/5.0 (平台信息) ... 引擎标识`）
- 原生 App / SDK 固定前缀（`Dart`、`okhttp`、`Dalvik`、`UnityPlayer`、`BestHTTP`、`UnityWebRequest`、`node`）
- 自有拨测监控（`DomainSecurityMonitor`）、ACME 校验（`Let's Encrypt`）
- 合作方 / 服务端接口路径（`/customer`、`/channel`、`/sdk`、`/api/sdk/`）、支付路径、自有 IP、三方白名单

**没有覆盖 Apple 系统客户端**，而 plist 抓取恰恰由它们发起，于是被一棍子打死。

## 五、处置

### 5.1 改动清单

三层同步，全部是「放行」方向：

| 层 | 主机 / 文件 | 改动 |
| --- | --- | --- |
| 网关 | `16.208.38.88` `/etc/nginx/conf.d/10-youdianse-prod-maps.conf` | `$yds_ua_real` 增加 `com.apple.appstored` / `MacAppStore` / `AppStore/` / `itunesstored` / `iTunes/` |
| 网关 | `16.208.38.88` `/etc/nginx/conf.d/20-youdianse-prod-unified.conf` | server 级新增路径级豁免：`if ($request_uri ~* "^/api/(v1/)?appVersionManifest(/|$)") { set $yds_gw_all_block 0; }` |
| 宝塔源站 | `16.208.5.147` `/www/server/panel/vhost/nginx/00-abuse-guard-http.conf` | 同上 UA 清单同步补齐 |
| 宝塔源站 | `16.208.5.147` `extension/new.youdianse.com/01-abuse-guard.conf` | server 级路径豁免 `set $yds_all_block 0` |
| 宝塔源站 | `16.208.5.147` `extension/new.youdianse.com/00-youdianse-fixed-reverse-proxy.conf` | `/api` location 路径豁免 `set $yds_api_block 0` |
| 宝塔源站 | `16.208.5.147` `allvhost/40-allvhost-guard.conf` | 全站 vhost 路径豁免 `set $yds_allvhost_block 0` |
| 后端 | `16.209.16.108` 容器 `youdianse-main-php-nginx` | **无需现场变更**：容器内 `$yds_ua_real` 只作用于登录 location，不拦该路径；仓库 `nginx/main.conf` 同步补齐保持三层一致 |

### 5.2 设计取舍（为什么不干脆整条路径全放行）

路径级豁免**只跳过「UA 真实性判断」**，IP 黑名单与限流（网关 50r/s、源站 30r/s）继续生效。
这样既解决系统客户端被误伤，又不会把该路径变成授权安全测试者可随意刷的开口子 —— 与「支付回调整体免限制」那种
（连黑名单都跳过）的处理刻意区分开，因为支付是钱的事、而这是分发清单。

另外为什么要加路径级豁免：同类「UA 规则误伤」这个月已经发生 5 次（1game token 校验、支付回调、
`/api/sdk/*`、自动化测试机、以及本次 Apple 客户端），每次都是靠人工发现。
iOS 后续版本若更换 UA 前缀，只靠 UA 清单还会再复发；路径级豁免把这条链路的不确定性一次性消掉。

### 5.3 执行细节与回滚

- 每处改动前先备份，备份文件：
  `*.bak.appleua-20260930-105811`（网关）、`*.bak.appleua-20260930-185834 / -185844`（宝塔源站）。
- 宝塔 `00-youdianse-fixed-reverse-proxy.conf` 带 `chattr +i` 不可改位，按规范执行
  `chattr -i` → 修改 → `chattr +i` 还原，已确认锁回（`lsattr` 复核）。
- 网关与宝塔均先 `nginx -t` 通过再 `nginx -s reload`，未重启服务、无中断。
- 回滚方式：还原对应 `.bak.appleua-*` → `nginx -t` → `nginx -s reload`。

## 六、验证

### 6.1 修复后同一请求（四类 UA 全通过）

| UA | 结果 |
| --- | --- |
| `com.apple.appstored/1.0 iOS/27.2 ...` | 200，合法 plist（`<plist version="1.0">`、`<key>items</key>`，1762 字节） |
| `MacAppStore/3.0 ... AMS/1` | 200，同上 |
| `itunesstored/1.0 (iPhone; iPhone OS 12_5_7)` | 200，同上 |
| iPhone Safari | 200，同上 |

`h5.game-app543.com` 从网关机（日本）测同样 200。

### 6.2 真实用户前后对比

| 客户来源 IP | 修复前 | 修复后 |
| --- | --- | --- |
| `116.98.248.45`（iPhone18,4 / iOS 27.2） | 10:51 连续 444 | 10:59:42 → **200** |
| `160.30.98.71`（iPhone15,2 / iOS 27.0） | 444 | **200** |
| `23.234.78.74`（macOS 26.6.2 / MacAppStore） | 444 | **200** |
| `180.165.43.242`（iPhone14,7 / iOS 17.6.1） | 444 | **200** |

统计口径：10:59 起该路径 **73 次请求全部 200，零报错**；网关 error.log 中该路径最后一条
`upstream prematurely closed connection` 停在 **10:58:35**（早于源站 reload 的 10:58:40）。

### 6.3 回归（确认防护没有被削弱）

- `python-requests/2.34.2` 打 `/api/v1/Login/account` → 依旧 444（经 CloudFront 表现 502）✅
- 极简伪造 UA `Mozilla/5.0` 打登录 → 依旧 444 ✅
- 真实 Safari UA 打登录 → 200 ✅
- 业务页面：www 首页 200、h5 首页 200 ✅
- 支付回调（`Go-http-client` UA）→ 200，未受影响 ✅

## 七、附带发现（与本次无关，另记）

`h5.game-app543.com` 从 AWS 香港出口访问返回 `000`（浏览器 UA 同样 000），从网关机（日本）访问正常。
属既有的地区性访问差异，与本次 UA 规则改动无关，未在本次处理。

## 八、后续建议

1. **新增入口先过一遍 UA 清单**：任何「服务端 / 系统客户端 / 非浏览器」调用方接入前，
   确认其 UA 是否已被 `$yds_ua_real` 覆盖，否则先加白再上线。
2. **把「路径级 UA 豁免」作为标准动作**：对由固定客户端调用的业务路径（分发清单、回调、鉴权、SDK），
   优先用路径级豁免而不是逐个补 UA 前缀，避免每次客户端升级都要再改一次配置。
3. **误伤监控**：对 444 比例突然升高的路径做日巡检，把「防护误伤」和「真实授权安全测试」分开统计，
   避免下次仍然依赖业务方反馈才发现。

## 九、代码与仓库文件

仓库内同步修改（保持线上与仓库一致）：

- `ops/production/scripts/gateway-ua-authenticity.conf`
- `ops/production/scripts/baota-www-abuse-guard-http.conf`
- `ops/production/scripts/baota-www-abuse-guard-server.conf`
- `ops/production/scripts/baota-allvhost-40-guard.conf`
- `ops/production/scripts/baota-new-youdianse-fixed-reverse-proxy.conf`
- `nginx/main.conf`
