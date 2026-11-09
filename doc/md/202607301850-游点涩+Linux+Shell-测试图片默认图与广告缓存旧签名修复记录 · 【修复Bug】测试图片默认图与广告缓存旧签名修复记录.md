---
id: "doc-8fda70467627"
title: "测试图片默认图与广告缓存旧签名修复记录 · 【修复Bug】测试图片默认图与广告缓存旧签名修复记录"
date: "2026-07-30T18:50:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "监控告警", "自动化"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-1850-%E3%80%90%E4%BF%AE%E5%A4%8DBug%E3%80%91%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87%E9%BB%98%E8%AE%A4%E5%9B%BE%E4%B8%8E%E5%B9%BF%E5%91%8A%E7%BC%93%E5%AD%98%E6%97%A7%E7%AD%BE%E5%90%8D%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-1850-【修复Bug】测试图片默认图与广告缓存旧签名修复记录.md"
sourceSha256: "cf611b1dc1a39ed19fb3cd9a707097e44f0fef25a088b28adf08cd35268f5f72"
sourceSystem: "project-doc"
---

# 测试图片默认图与广告缓存旧签名修复记录 · 【修复Bug】测试图片默认图与广告缓存旧签名修复记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607301850-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87%E9%BB%98%E8%AE%A4%E5%9B%BE%E4%B8%8E%E5%B9%BF%E5%91%8A%E7%BC%93%E5%AD%98%E6%97%A7%E7%AD%BE%E5%90%8D%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95%20%C2%B7%20%E3%80%90%E4%BF%AE%E5%A4%8DBug%E3%80%91%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87%E9%BB%98%E8%AE%A4%E5%9B%BE%E4%B8%8E%E5%B9%BF%E5%91%8A%E7%BC%93%E5%AD%98%E6%97%A7%E7%AD%BE%E5%90%8D%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md)

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

## 本次补充优化

### 1. 飞机通知支持多群

发布机器人通知不再只依赖单个 `TG_CHAT_ID`。当前支持自动合并并去重：

```text
TG_CHAT_ID
TG_CHAT_IDS
TG_EXTRA_CHAT_IDS
YOUDIANSE_HEALTH_TG_CHAT_ID
TG_HEALTH_CHAT_ID
```

多个群 ID 可以用逗号、分号、空格或换行分隔。发送日志只记录成功/失败群数量，不输出具体 `chat_id`。

### 2. 腾讯 CDN 鉴权配置支持默认继承

后续同规则图片域名不要再复制整段配置。推荐使用默认段 + 域名列表：

```ini
[cdn.tencent._default]
path_prefix=/uploads/
ttl=2592000
[敏感内容已脱敏]
time_param=t
key=<仅测试服务器 env 保管，不写入文档>
key_file=

[cdn.tencent.test-img]
domains=test-img.hbabaxb.cn,test-img.hbazuua.cn
```

说明：

- CDN 鉴权 key 直接保存在测试服务器本地 `env/.env.dev`，不提交 Git，不写入文档。
- `key_file` 当前留空，不再依赖 Docker 文件挂载。
- 后续新增同规则域名，只追加 `domains` 列表，不复制整段配置。

如果后续确实需要恢复密钥文件方案，可继续使用代码兼容的 `key_file`：

```ini
[cdn.tencent._default]
path_prefix=/uploads/
ttl=2592000
[敏感内容已脱敏]
time_param=t
key_file=/run/youdianse-tencent-cdn-auth.key

[cdn.tencent.test-img]
domains=test-img.hbabaxb.cn,test-img.hbazuua.cn
```

兼容旧写法：

```ini
[cdn.tencent.test-img.hbabaxb.cn]
domain=test-img.hbabaxb.cn
path_prefix=/uploads/
ttl=2592000
[敏感内容已脱敏]
time_param=t
key_file=
```

支持的匹配字段：

```text
domains
hosts
domain
```

字段值支持多个域名，也支持 `*.example.com` 这类通配后缀。后续新增同规则域名时，优先只追加到 `domains` 列表。

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
- 后续新增同规则腾讯图片 CDN 域名时，优先维护 `domains` 列表，不要复制整段配置。
- CDN 鉴权 key、Telegram token/chat_id、SSH 密码、发布密码、私钥都只放服务器本地 env/secrets/runtime，不写进 Git 和文档。

## 2026-07-30 19:13 默认段迁移记录

用户确认后，本次最终按以下方式迁移测试图片 CDN 配置：

```ini
[cdn.tencent._default]
path_prefix=/uploads/
ttl=2592000
[敏感内容已脱敏]
time_param=t
key=<仅测试服务器 env 保管，不写入文档>
key_file=

[cdn.tencent.test-img]
domains=test-img.hbabaxb.cn,test-img.hbazuua.cn
```

处理细节：

- 原两个 `test-img` 重复完整段已合并为 `_default` + `domains`。
- 鉴权 key 最终改为直接保存在测试服务器 `env/.env.dev` 的 `key=` 字段，文档和 Git 只保留占位。
- Docker compose 已移除腾讯 CDN key 文件挂载，运行态不再依赖 `/run/youdianse-tencent-cdn-auth.key`。
- 过程中曾尝试 key_file 文件方案；首次挂载到业务 `runtime/` 目录时，入口脚本 `chown runtime` 遇到只读文件导致容器重启，后改到 `/run` 可读，但最终按用户要求改为直接 `key=`。
- 已重建测试 `web/nginx/cron` 容器。

运行态验证：

```text
web/nginx/cron：Up
env key：已设置，未输出明文
test-img.hbabaxb.cn：敏感凭据：[已脱敏] t=1 sign=0
test-img.hbazuua.cn：敏感凭据：[已脱敏] t=1 sign=0
后台入口：https://admin.youdianse-test.xyz/admin1866/login HTTP 200
裸图：HTTP 200 size=13716，返回默认图
签名图：HTTP 200 size=286576，返回原图
```

页面复核：

```text
H5 首页仍存在裸 test-img 链接，样本包含 _large.webp。
PC 游戏列表仍存在裸 test-img 链接，来源于 SSR HTML 游戏卡片 image 输出。
当前 sign 均为 0。
```

当前判断：

- 后端 CDN 默认段配置和 `CommonService` 运行态签名已通过。
- 页面残留裸链不再是 env 配置格式问题。
- 下一步应在 H5/PC 前端仓库检查图片组件/缩略图处理是否丢弃 URL query，或是否使用了后端签名字段之外的原图/缩略图字段。

## 2026-07-30 19:19 workbench 使用要求

用户明确要求：

```text
操作一步飞机群通知一步，workbench 文件夹要用上。
```

后续流程固定为：

```text
1. 每一步操作前确认边界。
2. 操作完成后先更新 workbench 当前任务、安全点和下一步。
3. 再发送 Telegram 步骤完成/失败通知。
4. 然后继续下一步。
```

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
- 本次补充发布机器人多群通知能力，并补充腾讯 CDN 多域名默认配置继承说明。

## 2026-07-30 19:40 提交、推送与 /opt 更新复核

本次按用户要求提交 VS Code 中涉及的 11 个文件：

```text
外层运维仓库：10 个文件
内层业务仓库：1 个文件
```

提交结果：

```text
内层业务仓库：25fd3260cf3d fix: support shared tencent cdn auth config
外层运维仓库：af8a2ad fix: simplify test image cdn auth config
外层 workbench 补充提交：377ca48 docs: update cdn deploy workbench status
```

测试服务器 `/opt/docker-youdianse-php` 更新结果：

```text
外层 HEAD：377ca48bb0ef
内层 HEAD：25fd3260cf3d
外层 git status：clean
内层 git status：clean
```

同步过程注意：

- 首次从 macOS 直接同步文件时产生 `._*` AppleDouble 文件。
- 新增中文文档在服务器工作区出现过 HEAD/index 未对齐导致的未跟踪状态。
- 已改为在测试服务器直接从 `origin/dev` blob 重建目标文件，再用 `git reset --mixed origin/dev` 对齐 HEAD/index。
- 同步副产物已移动到 `cicd-web/runtime/sync-artifact-backups/`，不进入 Git。

服务器最终验证：

```text
Python 编译：通过
JSON 校验：通过
PHP 语法检查：通过
docker compose config：通过
web/nginx/cron：Up
后台入口：https://admin.youdianse-test.xyz/admin1866/login HTTP 200
env key：已设置，未输出明文
test-img.hbabaxb.cn：敏感凭据：[已脱敏] t=1 sign=0
test-img.hbazuua.cn：敏感凭据：[已脱敏] t=1 sign=0
```

测试服务器定时任务复核：

```text
每分钟自动更新：cicd-web-auto-update.py
健康巡检告警：youdianse-server-health-alert.py
小时健康汇总：youdianse-health-hourly-summary.py
应用日志轮转：youdianse-app-log-hourly-rotate.py
```

复核结论：

- 测试服务器 `/opt` 已更新到当前 dev 最新提交。
- 自动更新和巡检相关定时任务存在。
- 后端 CDN 配置改造已提交、推送、部署并验证。
- 页面残留裸链仍归为 H5/PC 前端图片处理链路后续排查项。
