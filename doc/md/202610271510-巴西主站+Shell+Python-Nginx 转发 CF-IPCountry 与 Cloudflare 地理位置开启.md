---
id: "doc-85ef574eadfb"
title: "Nginx 转发 CF-IPCountry 与 Cloudflare 地理位置开启"
date: "2026-10-27T15:10:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Nginx", "自动化", "CDN", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-10-27-1510-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91Nginx%E8%BD%AC%E5%8F%91CF-IPCountry%E4%B8%8ECloudflare%E5%85%A8Zone%E5%9C%B0%E7%90%86%E4%BD%8D%E7%BD%AE%E5%BC%80%E5%90%AF.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-10-27-1510-【运维】Nginx转发CF-IPCountry与Cloudflare全Zone地理位置开启.md"
sourceSha256: "fbe7aa5c23197a812e23e820459ecd3bef478871c39e7cee5e8c8e4ec455c663"
sourceSystem: "project-doc"
---

# Nginx 转发 CF-IPCountry 与 Cloudflare 地理位置开启

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-10-27-1510-【运维】Nginx转发CF-IPCountry与Cloudflare全Zone地理位置开启.md`

> 整理日期：2026-10-27 15:10｜日期依据：文件名日期

时间：北京 2026-10-27 15:10 ｜ 巴西圣保罗 2026-10-27 04:10

## 需求

开发要求在 Nginx 反向代理链中透传：

```nginx
proxy_set_header CF-IPCountry $http_cf_ipcountry;
```

同时将 Cloudflare 全部 zone 的 IP Geolocation 开启。该功能会把访问者国家/地区代码写入
`CF-IPCountry` 请求头。

## 处理范围

### 巴西宝塔

修改文件：

```text
/www/server/panel/vhost/nginx/common/all-games-proxy.conf
/www/server/panel/vhost/nginx/common/tada-proxy.conf
/www/server/panel/vhost/nginx/common/socket-proxy.conf
/www/server/panel/vhost/nginx/common/pg-proxy.conf
/www/server/panel/vhost/nginx/verify.pgofficialbx.com.conf
```

所有 `proxy_set_header X-Real-IP` 代理点后均增加 `CF-IPCountry`：

```text
all-games-proxy.conf：10 处
tada-proxy.conf：3 处
socket-proxy.conf：1 处
pg-proxy.conf：1 处
verify 站点：1 处
```

### 巴西备用入口

修改同名 common 文件及 `/etc/nginx/conf.d/verify.pgofficialbx.com.conf`：

```text
all-games-proxy.conf：10 处
tada-proxy.conf：3 处
socket-proxy.conf：1 处
pg-proxy.conf：1 处
verify 站点：1 处
```

### 香港 Nginx

修改：

```text
/etc/nginx/snippets/dbqp-hongkong-proxy.conf
/etc/nginx/proxy_params
```

动态反向代理现在会透传 `CF-IPCountry`。

## Nginx 验证

巴西宝塔：

```text
nginx: the configuration file /www/server/nginx/conf/nginx.conf syntax is ok
configuration file test is successful
```

巴西备用入口：

```text
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
configuration file test is successful
```

香港 Nginx：

```text
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
configuration file test is successful
```

三处均已平滑 reload，无中断。

最终提交前再次执行只读复核：

```text
巴西宝塔：CF-IPCountry 16/16 个代理点
巴西备用入口：CF-IPCountry 16/16 个代理点
香港 Nginx：CF-IPCountry 2/2 个代理点
合计：34/34 个代理点

巴西宝塔、备用入口、香港入口：nginx -t 全部通过
巴西宝塔 5 份配置：本地快照 SHA256 与服务器完全一致
巴西备用入口 5 份配置：本地快照 SHA256 与服务器完全一致
香港 2 份配置：本地快照 SHA256 与服务器完全一致
```

功能抽查：

```text
巴西宝塔：PP / PG / API /health = 200
巴西备用入口：PP / PG / API /health = 200
香港入口：PP /health = 200
香港 api.hkplaycore.com/health = 502
```

香港 502 日志显示其现有 upstream
`18.163.34.9:9090`、`43.198.52.147:9090` 均拒绝连接；该现象在本次 reload 前后均存在，
与新增请求头无关。本次没有修改香港 upstream，也没有重启香港业务容器。

最终复核时，香港 upstream 的 9090、9091、9099 端口仍不可达，因此 PP/PG/API
动态请求会返回 502。Nginx 配置自身通过 `nginx -t`，新增请求头也已加载；502 属于
上游服务可达性问题，不是本次配置语法或 reload 失败。

## 配置备份

```text
infrastructure/brazil/backups/20261027-before-cf-ipcountry/
infrastructure/hongkong/nginx/backups/20261027-before-cf-ipcountry/
```

服务器同名位置也保留了 `.bak-20261027-before-cf-ipcountry`。

## Cloudflare IP Geolocation

Cloudflare Account 共 54 个 zone：

```text
总数：54
成功：54
原本已开启：54
新变更：0
失败：0
```

说明：IP Geolocation 已处于全部开启状态，本次没有关闭或改动其它 Cloudflare 设置。

备份：

```text
/root/dbqp-cf-backups/20261027-070407-ip-geolocation/results.json
```

## 厂家差异说明

上面的 `16 + 16 + 2 = 34` 是 Nginx **代理点数量**，不代表巴西和香港的厂家完全一致。
发布和排障必须以对应环境的真实路由为准：

| 厂家/服务 | 巴西 | 香港 | 说明 |
| --- | --- | --- | --- |
| API、PG、PP、PPK、Playson、Panda、G759 | 有 | 有 | 两边都运行 |
| TADA HTTP | 有 | 无 | 巴西 9096；香港没有该主服务 |
| TADA WS2 | 有 | 容器有 | 两边均有 8765；香港 TADA/Socket 公网 Host 当前 410 |
| Socket | 有 | 公网关闭 | 香港 Nginx 明确返回 410 |
| JILI | 无 | 有 | 香港 9093，复用 TADA 镜像 |

香港 `conf/domains` 中可能保留 `tada.json`、`fc.json`、`jdb.json`，不能据此判断厂家启用。
判断顺序应为：Nginx 路由 -> 运行容器 -> 域名配置。

## 仓库与回归校验

```text
任务开始本地 master：7fe7f6cf
远端 origin/master：8fcefd60（无新提交）
远端 origin/ben：be336fee（本次未修改）

Python 语法：通过
Bash 语法：通过
JSON 有效性：通过
Markdown 实际相对链接：299 份，0 错误
配置 SHA256 清单：3 组，0 错误
HTML 桌面 1280×900：2 个页面通过
HTML 手机 390×844：2 个页面通过
HTML 横向溢出：0
HTML JavaScript / Console 错误：0
git diff --check：通过
```

HTML 回归使用本机 Chrome 无头模式，结果覆盖 `运维发布页.html` 和
`静态资源缓存清理笔记.html`。本次没有修改这两个页面。

## 使用说明

在 Cloudflare 代理的动态请求中，Nginx 会向后端发送：

```text
CF-IPCountry: <ISO 3166-1 alpha-2 国家代码>
```

后端可通过 `CF-IPCountry` 获取 Cloudflare 判定的访问者国家/地区。静态资源由 Worker
直接读取 `request.cf.country`，不经过这层 Nginx。

注意：如果源站可被绕过 Cloudflare 直接访问，客户端可以伪造该请求头；业务侧若把该值
用于安全决策，应同时限制源站只接受 Cloudflare 回源或校验 Cloudflare IP 段。

## 群通知

```text
步骤 1 基线核查：message_id=530
步骤 2 Nginx 与 Cloudflare 执行完成：message_id=533
步骤 3 最终验证与文档汇总：message_id=534
步骤 4 本地 Git 提交结果：message_id=535
补充：巴西/香港厂家差异更正：message_id=536
```
