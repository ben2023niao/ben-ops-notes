---
id: "doc-68bb399de4d9"
title: "测试图片加密防止检测防盗刷完整汇总说明"
date: "2026-07-29T23:50:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Docker", "Nginx", "自动化", "CDN", "安全运维", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2350-%E3%80%90%E5%AE%89%E5%85%A8%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87%E5%8A%A0%E5%AF%86%E9%98%B2%E6%AD%A2%E6%A3%80%E6%B5%8B%E9%98%B2%E7%9B%97%E5%88%B7%E5%AE%8C%E6%95%B4%E6%B1%87%E6%80%BB%E8%AF%B4%E6%98%8E.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2350-【安全优化+运维记录】测试图片加密防止检测防盗刷完整汇总说明.md"
sourceSha256: "800025983d09c7a7e55c907882255ebe8c41f4a53cf795a98b49f58108fe8755"
sourceSystem: "project-doc"
---

# 测试图片加密防止检测防盗刷完整汇总说明

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2350-【安全优化+运维记录】测试图片加密防止检测防盗刷完整汇总说明.md`

> 整理日期：2026-07-29 23:50｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-29 23:50
分类：安全优化 / 运维记录 / 测试环境
范围：测试 PC、后端 uploads 图片、`test-img.hbabaxb.cn`

## 1. 一句话结论

测试环境 PC 现在已经做了图片加密防止检测防盗刷基础改造：

```text
图片访问增加 token/t 加密参数
原始图片 URL 直接打开不暴露原图
缺参数、空参数或过期后统一降级显示默认占位图
```

```text
正常页面访问：显示原图
带 token/t 的图片地址：有效期内显示原图
裸原始图片 URL：原 URL 不跳转，直接显示默认占位图
token 缺失或为空：原 URL 不跳转，直接显示默认占位图
```

测试入口：

```text
https://test-pc.hbabaxb.cn
```

## 2. 给运营看的说明

别人如果复制后台上传图片的原始链接出去：

```text
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp
```

现在看到的不是原图，而是默认占位图。

正常测试 PC 页面里，图片仍然正常显示。

## 3. 给开发看的说明

后端只改了图片 URL 返回出口，不改上传。

文件：

```text
/var/www/html/youdianse-php/app/Services/Common/CommonService.php
```

核心变更：

```text
getCdnUrl() 返回 URL 前统一经过 signCdnUrlIfNeeded()
signCdnUrlIfNeeded() 只处理配置命中的 host 和 path prefix
```

签名方式按 EdgeOne Method D 兼容格式：

```text
敏感凭据：[已脱敏] + uri_path + timestamp)
t = 当前时间戳
```

说明：

```text
t 不是过期时间，是签名时间
有效期由 ttl / EdgeOne Timeout 控制
AWS CloudFront 绝对 URL 不匹配配置 host，会原样返回
```

不影响：

```text
后台上传逻辑
AWS S3 原始存储
AWS CloudFront 老图片 URL
APK/App 包
前端 _nuxt/js/css 静态资源
线上环境
```

## 4. 后端配置

测试服务器配置文件：

```text
/opt/docker-youdianse-php/env/.env.dev
```

本地配置文件：

```text
/Users/ben/Documents/ben/docker/dev/docker-youdianse-php/env/.env.dev
```

配置段：

```text
[cdn.test_img_auth]
enabled=1
hosts=test-img.hbabaxb.cn
prefixes=/uploads/
ttl=2592000
[敏感内容已脱敏]
time_param=t
key=仅 env 保存，文档不记录明文
key_file=
```

配置含义：

```text
enabled=1：开启后端 URL 加签
hosts：只处理 test-img.hbabaxb.cn
prefixes：只处理 /uploads/
ttl=2592000：有效期 30 天
token_param：签名参数名
time_param：时间参数名
key：签名密钥，只在 env 保存
```

## 5. 给运维看的 Nginx 实现

### 5.1 后端 uploads 图片

域名：

```text
test-img.hbabaxb.cn
```

配置文件：

```text
/www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf
```

实现逻辑：

```text
带 token/t：回源 CloudFront，返回原图
缺 token 或缺 t：内部返回默认占位图
外部 Referer 非白名单：内部返回默认占位图
```

注意：

```text
不是 302 跳转
没有 Location
浏览器地址栏仍是原始图片 URL
Nginx 直接返回占位图文件内容
```

### 5.2 PC 前端静态图片直开

域名：

```text
test-pc.hbabaxb.cn
pc.youdianse-test.xyz
```

配置文件：

```text
/www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf
```

实现逻辑：

```text
页面内正常加载图片：继续正常显示
地址栏直接打开图片：内部返回默认占位图
```

判断依据：

```text
Sec-Fetch-Dest=document 表示浏览器地址栏直接打开
Sec-Fetch-Dest=image 表示页面里作为图片加载
```

### 5.3 Nginx 关键写法

```nginx
error_page 418 = @placeholder_image;

if ($[敏感内容已脱敏]) {
    return 418;
}
if ($arg_t = "") {
    return 418;
}

location @placeholder_image {
    rewrite ^ /images/mine/footer-app-download-icon.webp break;
    proxy_pass https://test-pc-s3.hbabaxb.cn;
    proxy_set_header Host test-pc-s3.hbabaxb.cn;
}
```

## 6. 验证结果

测试 PC 页面：

```text
https://test-pc.hbabaxb.cn
=> 200，页面正常
```

签名后端 uploads 原图：

```text
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp?敏感凭据：[已脱敏]
=> 200 image/webp，返回原图
```

裸后端 uploads 原图：

```text
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp
=> 200 image/webp，URL 不变，返回默认占位图
```

空 token 后端 uploads：

```text
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp?敏感凭据：[已脱敏] 200 image/webp，URL 不变，返回默认占位图
```

PC 静态图地址栏直开：

```text
https://test-pc.hbabaxb.cn/images/index-new/main-bg.webp
=> 200 image/webp，URL 不变，返回默认占位图
```

占位图：

```text
https://test-pc.hbabaxb.cn/images/mine/footer-app-download-icon.webp
=> 200 image/webp
```

## 7. 当前边界

当前已经解决：

```text
裸图 URL 直接打开不再暴露原图
图片 URL 增加 token/t 加密访问参数，降低被直接检测和盗刷的风险
空 token 不再暴露原图
原始 URL 不跳转，直接显示默认图
正常页面图片展示不受影响
```

当前还不是完整强验签：

```text
如果随便填一个非空 token，Nginx 第一层规则可能仍放行
后续要做到 token 必须完全正确，需要再启用 Lua/md5 强校验
```

强验签前置条件：

```text
H5/PC 重新发布
确认页面里所有 test-img 图片 URL 都使用当前 env key 生成
再启用 Nginx Lua/md5 或 EdgeOne Token 鉴权
```

## 8. 回滚

后端代码备份：

```text
/var/www/html/youdianse-php/runtime/logs/CommonService.php.bak.test_img_auth.20260729_222605
```

测试后端 env 备份：

```text
/opt/docker-youdianse-php/env/.env.dev.bak.test_img_auth.20260729_223439
/opt/docker-youdianse-php/env/.env.dev.bak.test_img_auth_key.20260729_230110
/opt/docker-youdianse-php/env/.env.dev.bak.test_img_auth_ttl.20260729_231320
```

Nginx 备份：

```text
/www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf.bak.internal_placeholder_20260730_0003
/www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf.bak.internal_placeholder_20260730_0003
```

回滚方式：

```text
恢复对应备份
nginx -t
nginx -s reload
必要时重启测试后端容器 youdianse-dev-php-web
```

## 9. 关联提交与文档

关联提交：

```text
c456f39  后端签名 URL 准备态记录
74c919f  Nginx 内部占位图实现
2a26f2f  大白话说明
```

关联文档：

```text
devops/python/ben-bot/doc/2026-07-29_2320-【安全优化+架构改造】测试后端uploads图片签名URL准备态记录.md
devops/python/ben-bot/doc/2026-07-29_2345-【安全优化+网络调整】测试PC静态图片直开Token门槛记录.md
devops/python/ben-bot/doc/2026-07-29_2346-【运维记录】测试图片防盗刷大白话说明.md
```
