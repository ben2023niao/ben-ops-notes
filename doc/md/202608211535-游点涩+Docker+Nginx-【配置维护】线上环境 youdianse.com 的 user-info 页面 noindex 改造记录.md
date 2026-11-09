---
id: "doc-77d4459c6336"
title: "【配置维护】线上环境 youdianse.com 的 user-info 页面 noindex 改造记录"
date: "2026-08-21T15:35:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-21-1535-%E3%80%90%E9%85%8D%E7%BD%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83youdianse.com%E7%9A%84user-info%E9%A1%B5%E9%9D%A2noindex%E6%94%B9%E9%80%A0%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-21-1535-【配置维护】线上环境youdianse.com的user-info页面noindex改造记录.md"
sourceSha256: "2c08678791235724472c550afc94f58c0d0fde25eb2b4f1ad8ff3887d5e6e1d2"
sourceSystem: "project-doc"
---

# 【配置维护】线上环境 youdianse.com 的 user-info 页面 noindex 改造记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608211535-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BDocker%2BNginx-%E3%80%90%E9%85%8D%E7%BD%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20youdianse.com%20%E7%9A%84%20user-info%20%E9%A1%B5%E9%9D%A2%20noindex%20%E6%94%B9%E9%80%A0%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-21 15:35｜日期依据：文件名日期

文档日期：2026-08-21 15:35
环境：游点涩线上环境（main 分支）
分类：配置维护 / SEO异常验证
标签：线上环境、nginx、user-info、noindex、nofollow、X-Robots-Tag

## 背景

需求：youdianse.com 域名下 `user-info` 页面不需要被搜索引擎收录，需改为
noindex,nofollow。`post-detail` 页面暂不处理（等待决策）。
此前 SEO异常验证 策略为：仅 *.youdianse.com（根域+子域）index,follow；其余域名
noindex,nofollow（按域名 map 实现）。

## 实现

```text
网关 nginx（16.208.38.88）：
/etc/nginx/conf.d/20-youdianse-prod-unified.conf 的 location / 中新增：

    if ($request_uri ~* "^/user-info") {
        set $robots_meta_repl '<meta name="robots" content="noindex, nofollow">';
        set $robots_x_tag "noindex, nofollow";
    }

覆盖按域名 map 得到的 index,follow；meta（sub_filter）与 X-Robots-Tag
响应头同步生效。
原配置备份：20-youdianse-prod-unified.conf.bak.20260821-userinfo
```

## 验证

```text
URL                                 X-Robots-Tag        HTML meta
/                                   index, follow       index, follow
/user-info                          noindex, nofollow   noindex, nofollow
/user-info/abc123                   noindex, nofollow   -
/post-detail/123                    index, follow       -（暂不处理）
nginx -t 通过，reload 生效。
```

## 后续

```text
1. post-detail 页面是否 noindex 待决策，决策后按同样方式追加规则；
2. 新页面路由若需 noindex，按此模式扩展 if 匹配。
```

## 通知记录

```text
步骤 1：user-info noindex 需求分析（nginx 按路径覆盖方案）
步骤 2：配置修改生效并验证 X-Robots-Tag
步骤 3：HTML meta 与响应头双验证通过
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据。
