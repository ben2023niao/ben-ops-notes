---
id: "doc-a1c4e8b7b5d0"
title: "2026-10-08 JILI 进不去：EdgeOne 回源 HTTP → X-Forwarded-Proto 为 http"
date: "2026-10-08T14:25:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "Nginx", "CDN", "DNS", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-10-08-1425-%E3%80%90%E6%95%85%E9%9A%9C%E5%A4%84%E7%90%86%E3%80%91%E8%85%BE%E8%AE%AFEdgeOne%E5%9B%9E%E6%BA%90HTTP%E5%AF%BC%E8%87%B4X-Forwarded-Proto%E4%B8%BAhttp%EF%BC%88JILI%E8%BF%9B%E4%B8%8D%E5%8E%BB%EF%BC%89%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-10-08-1425-【故障处理】腾讯EdgeOne回源HTTP导致X-Forwarded-Proto为http（JILI进不去）修复.md"
sourceSha256: "0950a8e63f273d37a64a28d0e8104b5216e44e0816d8062963fe4d52a15a030b"
sourceSystem: "project-doc"
---

# 2026-10-08 JILI 进不去：EdgeOne 回源 HTTP → X-Forwarded-Proto 为 http

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-10-08-1425-【故障处理】腾讯EdgeOne回源HTTP导致X-Forwarded-Proto为http（JILI进不去）修复.md`

> 整理日期：2026-10-08 14:25｜日期依据：文件名日期

## 一、现象

```text
开发（C++）反馈：「线上吉利进不去了」，要求处理；用户补充：这次是**腾讯云（EdgeOne）那条线**，
并提示两个方向：① 看代码里配置的域名；② 怀疑 nginx 把 https 转发成了 http。
```

## 二、排查

```text
1) 先做整体健康检查（都正常，排除了服务挂掉）：
   · 四套动态域名 /health 全 200：jili-games.m4q7z1.shop / .k8x2v9.shop / .hkcloudplay06.com / .hkcloudplay07.com
   · 静态页与资源 200：jili-static1.<新域名>/lj500/index.html（97,383B）、/commom_v3_1.0.9.js、/lj500/src/*.bundle.js
   · 香港 01/02：9 个业务容器 Up、磁盘 40%、负载 <1；ws 容器日志显示真实客户端消息正常收发
   · nginx 错误日志只有扫描器的 SSL handshake 噪音
2) 配置核对（用户提示①）：线上 conf/domains/jili.json 的 default/v1/v2 用的都是腾讯域名
   （jili-static{,1,2}.m4q7z1.shop / .k8x2v9.shop，DNS 与 nginx 都正常）；
   v3/v4/v5 仍写的是 jili-static{3,4,5}-aws.hkcloudplay0[67].com（CF 侧命名），本机 nginx 没有这些 server_name
   → 命中默认站点返回平台页/404。**这条单独记，等开发确认这几个分组的目标域名**（不属本次 https→http 问题）。
3) 抓包对账（用户提示②，决定性证据）：在 prod-01 上 tcpdump 9093/8765，看后端实际收到的头：

   修复前
     Host: jili-games.m4q7z1.shop        X-Forwarded-Proto: http     ← 腾讯 EdgeOne 链路
     Host: jili-games.hkcloudplay06.com  X-Forwarded-Proto: https    ← Cloudflare 链路

   即：**EdgeOne 回源到本机用的是 HTTP**，而 nginx 片段里写的是
   `proxy_set_header X-Forwarded-Proto $scheme;` → `$scheme` 取的是「边缘→本机」这一跳的协议（http），
   后端据此认为客户端在 http 上 → 生成 http:// 链接 → 浏览器按混合内容/协议不一致拦掉 → 游戏进不去。
   CF 链路回源是 HTTPS，所以只有腾讯线出问题，这也解释了「为什么只有腾讯云这条线进不去」。
```

## 三、修复（两台 nginx 入口）

```text
原则：对外（EdgeOne / Cloudflare / 浏览器）实际都是 HTTPS，边缘→源站那一跳用什么协议不代表客户端协议；
      统一告诉后端 https，和 Cloudflare 链路的行为对齐。

· standby 34.150.1.185（腾讯域名 + 06/07 都在这台）
    /etc/nginx/snippets/dbqp-hk-standby-proxy.conf   X-Forwarded-Proto: $scheme →  https；新增 X-Forwarded-Port 443
    /etc/nginx/snippets/dbqp-hk-standby-ws.conf      X-Forwarded-Proto: $scheme →  https；X-Forwarded-Port: $server_port → 443
· 入口机 34.92.13.108（老域名 01-05）
    /etc/nginx/snippets/dbqp-hongkong-proxy.conf     同上（避免 CF 那条线哪天回源走 HTTP 时重演）
· 只改「告诉后端的协议」，不动任何业务口径（动态 CORS 仍归开发、静态 CORS 仍 ACAO *），静态域名不受影响。
· nginx -t 通过后才 reload。
```

## 四、验证

```text
· 抓包（修复后）：腾讯线 jili-games.m4q7z1.shop 与 CF 线 jili-games.hkcloudplay06.com 的后端请求头均为
  `X-Forwarded-Proto: https` + `X-Forwarded-Port: 443`；ws 升级请求（8765）同样带上 https/443。
· 四套动态域名 /health 全 200；静态资源 200；ws 容器继续正常收发包。
· 请开发在腾讯线重新进一次游戏确认（群里已同步）。
```

## 五、备份与回滚

```text
nginx（两台入口）
  standby：/etc/nginx/sites-available/dbqp-hk-standby.conf.bak-20261008-1419-scheme、
           snippets/dbqp-hk-standby-{proxy,ws}.conf.bak-20261008-1419-scheme、
           /root/nginx-backup-20261008-1419/（配置副本）
  入口机：/etc/nginx/sites-available/dbqp-hongkong.conf.bak-20261008-1419-scheme、
          snippets/dbqp-hongkong-proxy.conf.bak-20261008-1419
  入仓：docker/deploy/hongkong/nginx-backup/nginx-{standby,entry}-etc-nginx-20261008-1419.tgz（已排除 /etc/nginx/ssl）
香港 01/02 后端
  /root/dbqp-backup-20261008-1419/（conf/、start.sh、version.json、server_configs/）+ /root/dbqp-backup-20261008-1419.tgz
  记录 share.so md5（e55895552004c189bd22cb9ba297161d）到 MANIFEST.txt
回滚：把对应 .bak-20261008-1419-scheme 覆盖回原位 → nginx -t → systemctl reload nginx
```

## 六、关联

```text
docker/deploy/hongkong/nginx-standby-proxy.conf、nginx-standby-ws.conf、dbqp-hongkong-proxy.conf（本次修改）
docker/deploy/hongkong/nginx-backup/nginx-{standby,entry}-etc-nginx-20261008-1419.tgz
docker/doc/2026-10-05-1400-【架构改造】香港JILI静态域名按Worker路径映射并补intro-astarte处理.md（同一条腾讯链路的映射改造）
docker/doc/2026-10-05-1310-【运维】跨域职责划分-动态归开发静态归运维（撤销动态CORS兜底）.md（跨域口径，本次未动）
```
