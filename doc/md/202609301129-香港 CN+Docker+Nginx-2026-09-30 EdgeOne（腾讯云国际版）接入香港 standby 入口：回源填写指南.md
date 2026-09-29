---
id: "doc-4deaf9777225"
title: "2026-09-30 EdgeOne（腾讯云国际版）接入香港 standby 入口：回源填写指南"
date: "2026-09-30T11:29:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "Nginx", "CDN", "DNS", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-09-30-1129-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91EdgeOne%E6%8E%A5%E5%85%A5%E9%A6%99%E6%B8%AFstandby%E5%85%A5%E5%8F%A3%E5%9B%9E%E6%BA%90%E5%A1%AB%E5%86%99%E6%8C%87%E5%8D%97.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-09-30-1129-【架构改造】EdgeOne接入香港standby入口回源填写指南.md"
sourceSha256: "b444b890ed10a9aa777ccb7760e3bb5399444da6629054fcdfeeb0335015c32e"
sourceSystem: "project-doc"
---

# 2026-09-30 EdgeOne（腾讯云国际版）接入香港 standby 入口：回源填写指南

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-09-30-1129-【架构改造】EdgeOne接入香港standby入口回源填写指南.md`

> 整理日期：2026-09-30 11:29｜日期依据：文件名日期

## 一、一句话结论

```text
源站填「新那台」standby 入口：公网 34.150.1.185（内网 203.0.113.1，dbqp-hongkong-nginx-standby-01）。
回源协议用 HTTP（80），回源 Host 必须填一个香港 nginx 认得的域名；
加速区域只能选「全球（不含中国大陆）」（域名未备案，选大陆节点会被卡）。
老入口 34.92.13.108 这次的测试不要用（它承载老域名 01-05 现网业务）。
```

## 二、EdgeOne「添加站点」逐步填写

| 步骤 | 填什么 | 说明 |
| --- | --- | --- |
| 加速区域 | **全球（不含中国大陆）** | 域名未做 ICP 备案，选「中国大陆」或「全球」会要求备案号；免备案路线就是这条 |
| 接入模式 | **CNAME 接入**（推荐） | 不动现有 NS，去现有 DNS 加一条 CNAME 指向 EdgeOne 给的 `*.eo.dnse1.com`；DNS 主导权留在自己手里，方便以后做多 CDN 竞速/回切。想用 EdgeOne 做智能分线路再考虑 NS 接入 |
| 源站类型 / 地址 | `34.150.1.185`（standby 公网 IP） | 就是承载 hkcloudplay06/07 的那台；内网 203.0.113.1 |
| 回源协议 / 端口 | **HTTP / 80** | 源站 nginx 443 是**自签证书**（CN=hkcloudplay06.com，SAN 里没有测试域名），EdgeOne 回源 HTTPS 会证书校验失败。后面换可信证书再改 HTTPS 443 |
| 回源 Host | 填 nginx 已配置的域名，如 `pg-games.hkcloudplay06.com` / `pg-static.hkcloudplay06.com` | nginx 按 `server_name` 分站，Host 对不上会落默认站（80 返回 404） |
| 缓存 | 先「不缓存」测通，再按后缀（js/css/png/jpg/woff/json…）开 7 天 | 动态 API 与 WebSocket 一律不缓存 |
| 证书 | 用 EdgeOne 免费证书（自动签发） | 只覆盖加速域名，与源站证书无关 |

## 三、实测证据（2026-09-30，只读核验）

```text
外部直连 standby：
  http://34.150.1.185/healthz                                 -> 200（80 端口公网可达）
  http://34.150.1.185/            （Host=默认）                -> 404 "dbqp hong kong standby"
  http://34.150.1.185/health      （Host=pg-games.hkcloudplay06.com）-> 200（Host 对得上就通）
  http://34.150.1.185/health      （Host=m4q7z1.shop）          -> 404（未知域名落默认站）
  https://34.150.1.185/health     （Host=m4q7z1.shop）          -> 200 ← 见下方「坑」

源站证书（standby nginx 443）：
  subject=CN=hkcloudplay06.com  issuer=CN=hkcloudplay06.com（自签，10 年）
  SAN: *.hkcloudplay06.com / *.hkcloudplay07.com / *.hk-socket.com / IP 203.0.113.1
  说明：公网看到的 Let's Encrypt 证书是 Cloudflare 边缘的，不是源站的。

nginx upstream（两台自建后端，least_conn + failover）：
  platform_api 203.0.113.1:9090 / 203.0.113.1:9090
  pg 9091、jili 9093、pp 9099、ppk 9098、panda 9018、g759 9019、playson 9020、tada_ws2 8765
```

## 四、两个坑（必须知道）

```text
1. 443 未知 Host 会「看起来能通」：nginx 443 没有 default_server，未匹配的 SNI 落到第一个
   server 块（= pg-games 的 upstream），所以 `Host: 任意域名` 打 443 都可能返回 200 ——
   实际是打到了 PG 后端。用 HTTP 80 回源就不会有这种误判（未知 Host 明确 404）。
2. 回源 Host 填错 = 落到默认站：新域名（如 m4q7z1.shop）如果想直接用自己域名做回源 Host，
   必须先在 standby nginx 上给它加一个 server 块；否则 80 一律 404。
   加速域名为新域名但回源 Host 用现成域名（如 pg-games.hkcloudplay06.com）是最快的验证方式。
```

## 五、新域名要加 nginx 站点时的模板（需要时再加，本周未执行）

```nginx
# /etc/nginx/sites-available/dbqp-hk-standby.conf 内新增
server {
    include snippets/dbqp-hk-standby-tls.conf;   # 80 + 443 + 自签证书
    server_name m4q7z1.shop;

    location = /healthz { default_type text/plain; return 200 "ok\n"; }

    location / {
        include snippets/dbqp-hk-standby-proxy.conf;
        proxy_pass http://dbqp_hk_standby_pg;     # 按用途换成 platform_api/jili/… 的 upstream
    }
}

# 注意：自签证书 SAN 需要补上该域名，或改用可信证书；否则只能 HTTP 回源
```

## 六、关联

```text
docker/doc/2026-09-29-1808-【架构改造】香港项目大陆加速多CDN渠道免备案优先沟通口径与前置条件.md
docker/deploy/hongkong/nginx-standby.conf（仓库内站点配置源）
docker/workbench/CURRENT_STATE.md「环境」「当前动态端口」
```
