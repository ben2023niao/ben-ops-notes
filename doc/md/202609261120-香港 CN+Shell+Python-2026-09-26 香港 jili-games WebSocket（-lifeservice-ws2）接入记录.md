---
id: "doc-e7be47679eb6"
title: "2026-09-26 香港 jili-games WebSocket（/lifeservice/ws2）接入记录"
date: "2026-09-26T11:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Shell", "Python", "Docker", "Nginx", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-09-26-1120-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E9%A6%99%E6%B8%AFjili-games%20WebSocket%E6%8E%A5%E5%85%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-09-26-1120-【网络调整】香港jili-games WebSocket接入记录.md"
sourceSha256: "d4186c73955af077d02b52c0391e7e88a785ffbde15e3f953be34f03a7c90e94"
sourceSystem: "project-doc"
---

# 2026-09-26 香港 jili-games WebSocket（/lifeservice/ws2）接入记录

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-09-26-1120-【网络调整】香港jili-games WebSocket接入记录.md`

> 整理日期：2026-09-26 11:20｜日期依据：文件名日期

## 一、需求

```text
Ben(C++)：香港这边配置一下 wss://jili-games.hkcloudplay06.com/lifeservice/ws2
确认口径：
  · 「和 tada 一样就行」——参考巴西 TADA 的 ws 站点写法
  · 端口 8765（与巴西 tada 一致）
  · 「域名映射就行了，启动的都是 tada」——jili 复用 TADA 的 ws 服务，不另起后端
本侧按要求只做 nginx 域名映射（不改造 start.sh/stop.sh、不新增后端端口）。
```

## 二、巴西参考（master 配置）

```text
upstream tada_ws2_backend {   # 203.0.113.1 / 0.4 / 0.11 : 8765
    server ... keepalive 32 ...
}
location ^~ /lifeservice/ws2  -> proxy_pass http://tada_ws2_backend;   # 仅 tada-games.* 可用
location ^~ /ws2              -> proxy_pass http://tada_ws2_backend;
两者都带全套 WebSocket 头：Upgrade/Connection/Host/X-Original-Host/X-Real-IP/
  X-Real-Port/X-Forwarded-*/REMOTE-HOST/X-Vendor-Host，
  proxy_connect_timeout 5s、proxy_read_timeout 3600s、proxy_send_timeout 3600s，
  proxy_next_upstream error timeout http_502/503/504 + tries 2。
线上实测对照：wss://tada-games.xqv9m8.icu/lifeservice/ws2 -> 101 Switching Protocols
```

## 三、香港实现

落在 standby 入口（`dbqp-hongkong-nginx-standby-01`，新域名 06/07 的入口），老入口机未改动。

`docker/deploy/hongkong/nginx-standby.conf` 新增：

```nginx
upstream dbqp_hk_standby_tada_ws2 {           # jili 复用 TADA 的 ws 服务
    least_conn;
    server 203.0.113.1:8765 max_fails=3 fail_timeout=10s;
    server 203.0.113.1:8765 max_fails=3 fail_timeout=10s;
}

server {
    server_name ~^jili-games\.hkcloudplay0[67]\.com$;
    location ^~ /lifeservice/ws2 { include snippets/dbqp-hk-standby-ws.conf; proxy_pass http://dbqp_hk_standby_tada_ws2; }
    location ^~ /ws2             { include snippets/dbqp-hk-standby-ws.conf; proxy_pass http://dbqp_hk_standby_tada_ws2; }
    location /                   { include snippets/dbqp-hk-standby-proxy.conf; proxy_pass http://dbqp_hk_standby_jili; }
}
```

新增公共片段 `docker/deploy/hongkong/nginx-standby-ws.conf`（WebSocket 头 + 长超时），
照抄巴西写法，仅把上游换成香港自建后端内网 IP。

部署：两个文件写入 standby（旧站点配置已备份 `dbqp-hk-standby.conf.bak-YYYYMMDD-HHMM`）→
`nginx -t` 通过 → `systemctl reload nginx`。

## 四、验证（真正的 WebSocket 握手，不用 curl 拼头）

用 Python 标准库 socket/ssl 手工发 Upgrade 请求：

| 探测 | 结果 |
| --- | --- |
| 直连 `203.0.113.1:8765` 的 `/lifeservice/ws2` | **HTTP/1.1 101 Switching Protocols** |
| 直连 `203.0.113.1:8765` 的 `/ws2` | 101 |
| 经 standby nginx（SNI=Host=jili-games.hkcloudplay06.com） | 101 |
| 公网 `wss://jili-games.hkcloudplay06.com/lifeservice/ws2` | **101** |
| 公网 `wss://jili-games.hkcloudplay06.com/ws2` | 101 |
| 公网 `wss://jili-games.hkcloudplay07.com/lifeservice/ws2` 与 `/ws2` | 均 101 |
| 巴西对照 `wss://tada-games.xqv9m8.icu/lifeservice/ws2` | 101（口径一致） |

排查过程备注：

```text
一开始用 curl 加 Upgrade 头测试，得到 200 application/json（11 字节）与偶尔 000 超时，
一度误判为「后端不是 ws 端点」。改用标准 WebSocket 握手脚本后全部 101，
说明是 curl 的握手头不完整（缺标准 Sec-WebSocket-Key 规范/未走 ws 流程）导致的误判。
=> 以后验证 ws 一律用握手脚本或 wscat，不用 curl。
```

## 五、待办与风险

```text
1. 单点风险：8765 的 ws 容器目前只在 prod-02（203.0.113.1）监听，prod-01（203.0.113.1）不可达；
   upstream 已按双后端写，等 prod-01 也起 tada_ws 容器后自动双活。
2. 老域名 jili-games.hkcloudplay01-05.com（老入口机）本轮未配 ws —— 用户本次只要求 06/07；
   如需老域名同样支持，需在老入口机 nginx 加同样的 location（并在确认后端就绪后灰度）。
3. tada-games.* 域名在 cn 仍不启用（cn 只保留 jili 复用 TADA 前端/WS 资源，不开放 TADA 对外域名）。
```

## 六、关联

```text
docker/deploy/hongkong/nginx-standby.conf        standby 站点（新增 jili ws 两个 location + upstream）
docker/deploy/hongkong/nginx-standby-ws.conf     WebSocket 反代公共片段（本次新增）
docker/doc/2026-09-25-1345-【修复Bug】香港g759等厂商端口不可达-GCP防火墙端口范围修复记录.md
master/docker/线上服务器信息/standby-nginx/00.vendor-upstreams.conf   （巴西 tada_ws2_backend 参考）
