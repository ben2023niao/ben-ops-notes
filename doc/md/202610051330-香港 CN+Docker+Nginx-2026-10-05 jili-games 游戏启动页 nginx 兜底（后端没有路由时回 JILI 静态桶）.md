---
id: "doc-f33839c73b9d"
title: "2026-10-05 jili-games 游戏启动页 nginx 兜底（后端没有路由时回 JILI 静态桶）"
date: "2026-10-05T13:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "Nginx", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-10-05-1330-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AFjili-games%E6%B8%B8%E6%88%8F%E5%90%AF%E5%8A%A8%E9%A1%B5nginx%E5%85%9C%E5%BA%95%EF%BC%88%E5%90%8E%E7%AB%AF%E6%97%A0%E8%B7%AF%E7%94%B1%E5%9B%9EJILI%E9%9D%99%E6%80%81%E6%A1%B6%EF%BC%89.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-10-05-1330-【架构改造】香港jili-games游戏启动页nginx兜底（后端无路由回JILI静态桶）.md"
sourceSha256: "f7f8ea1893c3eed3f6096d85f551a525f9ff4ba412542f47fe0b873a9ee97ae4"
sourceSystem: "project-doc"
---

# 2026-10-05 jili-games 游戏启动页 nginx 兜底（后端没有路由时回 JILI 静态桶）

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-10-05-1330-【架构改造】香港jili-games游戏启动页nginx兜底（后端无路由回JILI静态桶）.md`

> 整理日期：2026-10-05 13:30｜日期依据：文件名日期

## 一、需求

```text
开发给的地址（在**动态**域名上）：
  https://jili-games.m4q7z1.shop/lj500/
  https://jili-games.m4q7z1.shop/lj500/index.html
运维侧确认：这个由 nginx 来处理（不是后端路由）。
本轮按要求不通知飞机群。
```

## 二、定位

```text
1) 现状：这两条地址都由 **jili 后端**（Sanic，容器 9093）返回 404（14B 纯文本）；
   在 06 链路（CF）上表现相同 —— 说明后端确实没有这个路由。
2) 但页面本身是存在的，在 **JILI 静态桶**里：
     dbqp-s3-jili-static1/lj500/index.html -> 200 / 97,383B   ← lj500 在这里
     dbqp-s3-jili-static /ifff/index.html  -> 200 / 34,238B   ← ifff 页在这里
   对照：PG 的游戏入口是后端自带路由（pg-games.<域>/65/index.html -> 200），
        JILI 没有对应路由，所以要在 nginx 侧做兜底。
3) 巴西没有 jili（只有 tada-statics*），仓库里巴西的 vhost 备份是空文件，
   因此按「后端 404 → 回 JILI 自己的静态桶」这个口径实现。
```

## 三、实现（standby nginx，两个新域名的 jili-games server 块）

```nginx
    recursive_error_pages on;          # 关键：允许 error_page 链式跳转（nginx 默认 off）

    # 只匹配「单段路径 + 可选 index.html」，避免影响 /webservice、/sso-login.api 等接口的 404 语义
    location ~ ^/[A-Za-z0-9_-]+(/index\.html)?/?$ {
        include snippets/dbqp-hk-standby-proxy.conf;
        proxy_pass http://dbqp_hk_standby_jili;     # 先走后端
        proxy_intercept_errors on;
        error_page 404 = @jili_page_static1;        # 后端没这个路由才兜底
    }

    location @jili_page_static1 {                   # 第 1 跳：JILI 静态桶 1
        internal;
        resolver 169.254.169.254 8.8.8.8 valid=300s ipv6=off;
        rewrite ^(.+)/$ $1/index.html break;         # /lj500/ -> /lj500/index.html
        proxy_ssl_server_name on;
        proxy_ssl_name dbqp-s3-jili-static1.s3.ap-northeast-3.amazonaws.com;
        proxy_set_header Host dbqp-s3-jili-static1.s3.ap-northeast-3.amazonaws.com;
        proxy_intercept_errors on;
        error_page 403 404 = @jili_page_static0;     # S3 缺对象返回 403，一并拦截
        proxy_pass https://dbqp-s3-jili-static1.s3.ap-northeast-3.amazonaws.com;
    }

    location @jili_page_static0 {                   # 第 2 跳：JILI 主静态桶
        internal;
        resolver 169.254.169.254 8.8.8.8 valid=300s ipv6=off;
        rewrite ^(.+)/$ $1/index.html break;
        proxy_ssl_server_name on;
        proxy_ssl_name dbqp-s3-jili-static.s3.ap-northeast-3.amazonaws.com;
        proxy_set_header Host dbqp-s3-jili-static.s3.ap-northeast-3.amazonaws.com;
        proxy_pass https://dbqp-s3-jili-static.s3.ap-northeast-3.amazonaws.com;
    }
```

```text
踩坑：只写 error_page 链是没用的 —— nginx 默认 `recursive_error_pages off`，
      第二跳（static1 403 → static）不会触发，最终返回 nginx 自带的 403 页面。
      加上 `recursive_error_pages on;` 后链式兜底才生效。
备份：/etc/nginx/sites-available/dbqp-hk-standby.conf.bak-20261005-jilipage
```

## 四、验证（源站 + 经 EdgeOne）

| 请求 | 结果 |
| --- | --- |
| `jili-games.m4q7z1.shop/lj500/` | **200 / 97,383B**（= jili-static1 桶里的文件） |
| `jili-games.m4q7z1.shop/lj500/index.html` | **200 / 97,383B** |
| `jili-games.k8x2v9.shop/lj500/`、`/lj500/index.html` | **200 / 97,383B** |
| `jili-games.<域>/ifff/`、`/ifff/index.html` | **200 / 34,238B**（走第 2 跳，从 jili-static 桶取） |
| `jili-games.<域>/health` | 200 / 105B（后端，未受影响） |
| `jili-games.<域>/webservice/nope` | 404 / 14B（**仍是后端 404，语义未变**） |
| 经 EdgeOne 公网：`/lj500/`、`/ifff/` | 200（97,383B / 34,238B，text/html） |

```text
EdgeOne 侧动态域名规则是「不缓存」，所以之前后端 404 不会留下边缘缓存，无需清缓存。
```

## 五、影响面与回滚

```text
影响面：只影响 jili-games.<新域名> 上「单段路径 / <game>/ 或 <game>/index.html」且后端返回 404 的请求；
        接口路径（多段，如 /webservice/xxx、/sso-login.api）与 WebSocket（/lifeservice/ws2、/ws2）完全不受影响；
        06/07 的 jili-games 未改动（如需同口径，同一段配置复制过去即可）。
回滚：cp /etc/nginx/sites-available/dbqp-hk-standby.conf.bak-20261005-jilipage \
        /etc/nginx/sites-available/dbqp-hk-standby.conf && nginx -t && systemctl reload nginx
```

## 六、关联

```text
docker/deploy/hongkong/nginx-standby.conf（本轮的 jili-games 兜底）
docker/doc/2026-10-05-1230-【架构改造】香港nginx的jili静态改为走自己的大阪桶（对齐香港Worker）.md
docker/doc/2026-10-05-1310-【运维】跨域职责划分-动态归开发静态归运维（撤销动态CORS兜底）.md
```
