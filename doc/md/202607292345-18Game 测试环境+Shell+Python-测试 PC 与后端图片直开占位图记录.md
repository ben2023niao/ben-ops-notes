---
id: "doc-ff5d4c2ac866"
title: "测试 PC 与后端图片直开占位图记录"
date: "2026-07-29T23:45:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "自动化", "CDN", "安全运维", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2345-%E3%80%90%E5%AE%89%E5%85%A8%E4%BC%98%E5%8C%96%2B%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E6%B5%8B%E8%AF%95PC%E9%9D%99%E6%80%81%E5%9B%BE%E7%89%87%E7%9B%B4%E5%BC%80Token%E9%97%A8%E6%A7%9B%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2345-【安全优化+网络调整】测试PC静态图片直开Token门槛记录.md"
sourceSha256: "e8a953bf6a107e5b121cde2b5cf154f38d690a9af6a41cd470ff6569bd203030"
sourceSystem: "project-doc"
---

# 测试 PC 与后端图片直开占位图记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2345-【安全优化+网络调整】测试PC静态图片直开Token门槛记录.md`

> 整理日期：2026-07-29 23:45｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-29 23:45
分类：安全优化 / 网络调整 / 测试环境
范围：`test-img.hbabaxb.cn`、`test-pc.hbabaxb.cn`、`pc.youdianse-test.xyz`

## 1. 背景

测试环境存在两类图片直连地址：

```text
后端 uploads 图片:
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp

PC 前端静态图片:
https://test-pc.hbabaxb.cn/images/mine/footer-app-download-icon.webp
```

要求：

- 后端 uploads 带合法 `token/t` 时正常显示原图。
- 后端 uploads 裸链或空 token 直接打开时，不跳转，原 URL 下直接返回固定占位图内容。
- PC 前端静态图片地址栏直接打开时，不跳转，原 URL 下直接返回固定占位图内容。
- 页面内部正常加载图片不能拦截，否则 PC 页面图标会挂。
- 不对当前前端构建产物做加密改造。

## 2. 本次改动

文件：

```text
devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/nginx/pc.youdianse-test.xyz.conf
devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/nginx/test-img.hbabaxb.cn.conf
```

服务器配置：

```text
/www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf
/www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf
```

备份：

```text
/www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf.bak.direct_media_token_20260729_2345
/www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf.bak.require_token_20260729_2337
/www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf.bak.placeholder_redirect_20260729_2358
/www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf.bak.placeholder_allow_20260729_2358
/www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf.bak.internal_placeholder_20260730_0003
/www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf.bak.internal_placeholder_20260730_0003
```

## 3. Nginx 判断逻辑

### 3.1 后端 uploads 图片

作用域名：

```text
test-img.hbabaxb.cn
```

作用路径：

```text
/uploads/
```

规则：

```text
token 为空或 t 为空时，内部返回占位图内容
外部 Referer 非白名单时，内部返回占位图内容
带 token/t 的正常页面图片继续回源 CloudFront
```

关键实现：

```nginx
error_page 418 = @placeholder_image;

location ^~ /uploads/ {
    if ($[敏感内容已脱敏]) {
        return 418;
    }
    if ($arg_t = "") {
        return 418;
    }

    valid_referers none *.hbabaxb.cn *.youdianse-test.xyz;
    if ($invalid_referer) {
        return 418;
    }

    proxy_pass https://d1rct3ku9n07y3.cloudfront.net;
}

location @placeholder_image {
    rewrite ^ /images/mine/footer-app-download-icon.webp break;
    proxy_pass https://test-pc-s3.hbabaxb.cn;
    proxy_set_header Host test-pc-s3.hbabaxb.cn;
}
```

效果：

```text
浏览器地址栏仍然是原 uploads 图片 URL
响应内容是占位图 image/webp
没有 302 Location 跳转
```

### 3.2 PC 前端静态媒体直开

作用域名：

```text
test-pc.hbabaxb.cn
pc.youdianse-test.xyz
```

作用路径：

```text
/images/
/image/
/video/
/videos/
/media/
```

规则：

```text
如果 Sec-Fetch-Dest = document，并且 token 为空，则内部返回占位图内容
如果 token 非空，则允许继续回源
如果是页面内正常图片加载，Sec-Fetch-Dest=image，不拦截
```

Nginx 片段：

```nginx
set $block_direct_media_open 0;
if ($http_sec_fetch_dest = "document") {
    set $block_direct_media_open 1;
}
if ($arg_token != "") {
    set $block_direct_media_open 0;
}
if ($block_direct_media_open = 1) {
    return 418;
}

location @media_placeholder_image {
    rewrite ^ /images/mine/footer-app-download-icon.webp break;
    proxy_pass https://test-pc-s3.hbabaxb.cn;
    proxy_set_header Host test-pc-s3.hbabaxb.cn;
}
```

说明：

- 这是“不跳转占位图”，不是完整 md5 强验签。
- 主要解决浏览器地址栏直接打开原图的问题。
- 如果后续要“随便填 token 也不能打开”，需要再加 Lua/md5 校验，并先确保前端发布生成的 token 统一。

## 4. 验证结果

```text
PC 页面:
https://test-pc.hbabaxb.cn/
=> 200 text/html

地址栏直开，无 敏感凭据：[已脱敏]
=> 200 image/webp，URL 不变，返回占位图内容

地址栏直开，空 敏感凭据：[已脱敏]
=> 200 image/webp，URL 不变，返回占位图内容

地址栏直开，非空 敏感凭据：[已脱敏]
=> 200 image/webp

页面内图片加载:
Sec-Fetch-Dest=image
=> 200 image/webp
```

后端 uploads 补充验证：

```text
签名原图:
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp?敏感凭据：[已脱敏]
=> 200 image/webp，返回原图内容，size=138492

裸原图:
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp
=> 200 image/webp，URL 不变，返回占位图内容，size=13716

空 敏感凭据：[已脱敏]
=> 200 image/webp，URL 不变，返回占位图内容，size=13716

占位图:
https://test-pc.hbabaxb.cn/images/mine/footer-app-download-icon.webp
=> 200 image/webp，size=13716
```

## 5. 回滚方式

恢复备份：

```bash
cp /www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf.bak.direct_media_token_20260729_2345 \
   /www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf
cp /www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf.bak.require_token_20260729_2337 \
   /www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf
nginx -t
nginx -s reload
```

回滚后：

- `test-img.hbabaxb.cn/uploads/...` 裸链会恢复为 403 或上一版策略。
- `test-pc.hbabaxb.cn/images/...` 地址栏直开会恢复为上一版策略。
- 页面内图片加载不受影响。
