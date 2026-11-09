---
id: "doc-dcf9cddb0582"
title: "测试图片默认图与广告缓存旧签名修复记录 · 【修复Bug+安全优化】测试图片默认图与广告缓存旧签名修复记录"
date: "2026-07-30T18:50:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "Nginx", "CDN", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_1850-%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E5%AE%89%E5%85%A8%E4%BC%98%E5%8C%96%E3%80%91%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87%E9%BB%98%E8%AE%A4%E5%9B%BE%E4%B8%8E%E5%B9%BF%E5%91%8A%E7%BC%93%E5%AD%98%E6%97%A7%E7%AD%BE%E5%90%8D%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_1850-【修复Bug+安全优化】测试图片默认图与广告缓存旧签名修复记录.md"
sourceSha256: "ede7aa00d9310cc25ffef5b3245617594d8f8c9ce0691433b0ebcf43bdcdb367"
sourceSystem: "project-doc"
---

# 测试图片默认图与广告缓存旧签名修复记录 · 【修复Bug+安全优化】测试图片默认图与广告缓存旧签名修复记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607301850-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87%E9%BB%98%E8%AE%A4%E5%9B%BE%E4%B8%8E%E5%B9%BF%E5%91%8A%E7%BC%93%E5%AD%98%E6%97%A7%E7%AD%BE%E5%90%8D%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95%20%C2%B7%20%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E5%AE%89%E5%85%A8%E4%BC%98%E5%8C%96%E3%80%91%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87%E9%BB%98%E8%AE%A4%E5%9B%BE%E4%B8%8E%E5%B9%BF%E5%91%8A%E7%BC%93%E5%AD%98%E6%97%A7%E7%AD%BE%E5%90%8D%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-30 18:50｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-30 18:50

## 问题现象

测试环境页面图片大量显示默认占位图。

用户截图里可以看到：

```text
https://test-img.hbabaxb.cn/uploads/...webp?sign=...&t=...
```

请求状态是 `200`，但响应内容大小是 `13716`，这是默认占位图，不是原图。

## 当前正确规则

测试后端 uploads 图片防盗刷当前规则：

```text
正常页面图片：必须带 token/t
旧 sign/t：按无效签名处理，返回默认占位图
裸图或空 token：返回默认占位图
```

Nginx `test-img` 规则只认：

```text
$arg_token
$arg_t
```

不认：

```text
$arg_sign
```

## 排查结论

本次不是 S3/COS 问题，也不是 Nginx 域名反代问题。

只读核验结果：

```text
/opt/docker-youdianse-php 外层仓库：dev 与 origin/dev 一致
/opt/docker-youdianse-php/src/youdianse-php 内层仓库：dev 与 origin/dev 一致
CommonService.php md5：8540833c544f95e297c333ff1bf01a9f
后端 commit：cbd772ff
```

env 非敏感字段确认：

```ini
[cdn.tencent.test-img.hbabaxb.cn]
domain=test-img.hbabaxb.cn
path_prefix=/uploads/
ttl=2592000
[敏感内容已脱敏]
time_param=t
key_file=

[cdn.tencent.test-img.hbazuua.cn]
domain=test-img.hbazuua.cn
path_prefix=/uploads/
ttl=2592000
[敏感内容已脱敏]
time_param=t
key_file=
```

容器挂载确认：

```text
/opt/docker-youdianse-php/env/.env.dev -> /var/www/html/youdianse-php/.env
```

最终定位：

- H5 页面 SSR 图片已经全部是 `token/t`。
- PC 游戏页大部分图片已经是 `token/t`。
- PC 顶部推荐/广告 banner 仍残留旧 `sign/t`。
- 根因是后端广告缓存中还保存了旧签名 URL。

## 处理动作

### 1. 刷新广告缓存

在测试后端 PHP 容器里临时执行：

```php
require 'vendor/autoload.php';
$app = new App\CliApplication();
$app->initDispatcher();
$app->initUrl();
$result = App\Services\Common\AdvService::refreshCache();
var_dump($result);
```

结果：

```text
bool(true)
```

说明广告缓存已重新经过 `CommonService::getCdnUrl()` 生成 `token/t`。

### 2. 重启测试后端容器

执行：

```bash
cd /opt/docker-youdianse-php
docker compose restart web nginx
docker restart youdianse-dev-php-cron
```

目的：

- 刷新 PHP-FPM/opcache。
- 让 web、nginx、cron 都处于同一套最新代码和配置状态。

## 验证结果

外网抓取正常入口，不加调试参数：

```text
https://h5.youdianse-test.xyz/
test-img：97 条
token：97
sign：0
裸链：0

https://pc.youdianse-test.xyz/game?page=4
test-img：31 条
token：31
sign：0
裸链：0

https://test-pc.hbabaxb.cn/game?page=4
test-img：31 条
token：31
sign：0
裸链：0
```

抽样图片验证：

```text
带 token/t 图片：
HTTP/2 200
Content-Type: image/webp
size=48438
返回原图

旧 sign/t 图片：
HTTP/2 200
Content-Type: image/webp
size=13716
返回默认占位图
```

## 影响说明

对 H5：

- 服务端返回已经是 `token/t`。
- 未发现 `sign/t` 和裸链。

对 PC：

- 游戏页顶部广告旧 `sign/t` 已通过广告缓存刷新修复。
- 当前 PC 游戏页图片全部恢复为 `token/t`。

对上传：

- 未修改上传逻辑。
- 后台上传仍走原 AWS S3。

对 AWS：

- 未修改 AWS S3 和 CloudFront。
- AWS 老链路仍作为未命中腾讯配置时的原样返回路径。

## 如果浏览器仍显示默认图

服务端当前已恢复。

如果个别本地浏览器仍看到默认图，优先排查：

- 浏览器缓存。
- Service Worker 缓存。
- DevTools 是否勾选 Disable cache。
- 是否还停留在旧页面状态，未重新拉取 SSR/API 数据。

建议操作：

```text
Chrome DevTools -> Application -> Service Workers -> Unregister
Chrome DevTools -> Application -> Storage -> Clear site data
然后强刷页面
```

## 后续注意

- 后端代码和 env 更新后，如页面仍有旧图片签名，优先检查业务缓存。
- 广告位尤其容易缓存旧 URL，重点看 `AdvService::refreshCache()`。
- 不要先怀疑 S3/COS 同步，因为本次图片能返回默认图，说明域名和反代链路是通的。
- `sign/t` 是旧签名参数；当前标准是 `token/t`。

## 飞机群通知

已通知群：

```text
稳定备案域名+腾讯云原厂
```

通知摘要：

- 根因是广告缓存残留旧 `sign/t`。
- 已刷新广告缓存。
- 已重启测试后端 web/nginx/cron。
- H5/PC/test-pc 均验证 `token` 全量恢复、`sign` 为 0、裸链为 0。
