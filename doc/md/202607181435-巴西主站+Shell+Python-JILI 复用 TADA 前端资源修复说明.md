---
id: "doc-6a95e647ce05"
title: "JILI 复用 TADA 前端资源修复说明"
date: "2026-07-18T14:35:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "Nginx", "CDN", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-18-1435-%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91JILI%E5%A4%8D%E7%94%A8TADA%E5%89%8D%E7%AB%AF%E8%B5%84%E6%BA%90%E4%BF%AE%E5%A4%8D%E8%AF%B4%E6%98%8E.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-18-1435-【修复Bug+架构改造】JILI复用TADA前端资源修复说明.md"
sourceSha256: "808c1f334c7cebccfad19c4e6e117a8c8689609d98cff9586ad93d51cbc7976a"
sourceSystem: "project-doc"
---

# JILI 复用 TADA 前端资源修复说明

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-18-1435-【修复Bug+架构改造】JILI复用TADA前端资源修复说明.md`

> 整理日期：2026-07-18 14:35｜日期依据：文件名日期

## 问题

访问 `jili-static.hkcloudplay05.com/fg/` 时，CloudFront 返回 HTTP 403，响应来自私有 S3，错误码为 `AccessDenied`。

只读检查确认：

- `dbqp-gcs-tada-statics/fg/` 存在并返回 HTTP 200。
- `fg/` 是一个带 HTML 内容的尾斜杠对象；常规 rclone 会把这类对象视为目录标记，因此同步工具需要单独识别和上传。
- JILI CloudFront 当前读取独立的 `/jili-static*` S3 前缀，其中没有最新的 `/fg/` 页面。
- TADA 对外域名在 CN 环境未启用，不能让 platform-api 直接返回 `tada-statics*` 域名。

## 修复模型

JILI 保留自己的对外域名和动态端口：

| 类型 | 对外名称 | 实际目标 |
| --- | --- | --- |
| 默认静态 | `jili-static*` | S3 `/tada-statics`；nginx 兜底到 `dbqp-gcs-tada-statics` |
| 特殊组 1 | `jili-static1*` | S3 `/tada-statics1`；nginx 兜底到 `dbqp-gcs-tada-statics1` |
| 特殊组 2 | `jili-static2*` | S3 `/tada-statics2`；nginx 兜底到 `dbqp-gcs-tada-statics2` |
| 动态/API | `jili-games*` / `jili-api` | 两台后端 TCP 9093 |

这样 JILI 与 TADA 只有动态后端端口不同，前端对象只维护一份。

## 上线顺序

先备份三个 JILI CloudFront 分配配置，再依次执行：

```bash
python3 docker/deploy/hongkong/sync_gcs_to_s3.py tada-statics
python3 docker/deploy/hongkong/sync_gcs_to_s3.py tada-statics1
python3 docker/deploy/hongkong/sync_gcs_to_s3.py tada-statics2

python3 docker/deploy/hongkong/create_cloudfront_static_distributions.py jili-static
python3 docker/deploy/hongkong/create_cloudfront_static_distributions.py jili-static1
python3 docker/deploy/hongkong/create_cloudfront_static_distributions.py jili-static2
```

CloudFront 工具会先允许对应 JILI 分配读取共享 S3 前缀，再更新 OriginPath；仅在源路径发生变化时创建全路径失效请求。

同步工具会扫描 GCS 顶层目录标记，把其中非空的尾斜杠对象显式写入 S3，并只对发生变化的入口路径创建 CloudFront 失效请求，确保 `/fg/` HTML 本身与其下级资源同时存在。

如需更新 nginx 兜底配置，安装仓库中的 `nginx-dbqp.conf` 后先执行：

```bash
nginx -t
```

测试通过后再 reload，不能跳过语法检查。

## 验证

等待三个 CloudFront 分配均为 `Deployed` 后执行：

```bash
python3 docker/deploy/hongkong/validate_cloudfront_static.py
curl -fsS -o /dev/null -w '%{http_code} %{content_type}\n' https://jili-static.hkcloudplay05.com/fg/
```

预期 `/fg/` 返回 HTTP 200 和 HTML，不再出现 S3 `AccessDenied`。验证地址不需要携带登录 Token。

## 2026-07-18 现场验证记录

本轮先修复 `jili-static.hkcloudplay05.com/fg/` 入口 403：

- `jili-static` CloudFront `E2KICAEYOWJ24E` 已读 `/tada-statics`。
- `jili-static1` CloudFront `EIKLXE4BT0I05` 已读 `/tada-statics1`。
- `jili-static2` CloudFront `E38M63JF95BKAL` 已读 `/tada-statics2`。
- S3 已补齐 `tada-statics/fg/`，大小 `34742` bytes，`Content-Type: text/html; charset=utf-8`。
- 公开验证 `https://jili-static.hkcloudplay05.com/fg/` 返回 HTTP 200。

随后复查浏览器截图中的深层 403：

```text
jili-static.hkcloudplay04.com/astarte2/3.6/web-mobile/assets/jiliMain/index.9330c.js
```

结论：

- `9330c` 和 `70ff4` 旧 hash 文件在 `dbqp-gcs-tada-statics`、`dbqp-gcs-tada-statics1`、`dbqp-gcs-tada-statics2` 三个源桶均不存在。
- 当前 `https://jili-static.hkcloudplay04.com/pp/` 入口不再引用 `astarte2`、`9330c`、`70ff4` 或 `jiliMain`。
- 当前 `pp` 入口实际引用的关键文件验证通过：
  - `pp/`：HTTP 200。
  - `pp/src/import-map.a7842.json`：HTTP 200。
  - `pp/src/settings.163a4.json`：HTTP 200。
  - `pp/cocos-js/cc.921f1.js`：HTTP 200。
- 当前 `fg` 入口实际引用的关键文件验证通过：
  - `fg/`：HTTP 200。
  - `fg/src/settings.00a8c.json`：HTTP 200。

截图中的 `9330c` / `70ff4` 请求判断为旧入口或浏览器站点缓存残留。已对 `jili-static`、`jili-static1`、`jili-static2` 三个 CloudFront 分配提交并完成 `/*` 全量失效。测试复现时建议使用无痕窗口，或清理 `jili-static.hkcloudplay04.com` 的站点缓存后重新进入。

同步工具已修正：GCS 顶层尾斜杠 HTML 对象会显式同步到 S3；校验时会扣除这类入口对象，避免 S3 比普通 rclone 源统计多出 marker 后误判失败。

## 2026-07-18 14:35 二次 403 复核

用户再次反馈 `jili-static.hkcloudplay04.com/pp/` 进入后 DevTools 中大量资源 403，截图中的典型 URL 为：

```text
https://jili-static.hkcloudplay04.com/astarte2/3.6/web-mobile/assets/jiliMain/config.9330c.json
https://jili-static.hkcloudplay04.com/astarte2/3.6/web-mobile/assets/jiliMain/index.9330c.js
https://jili-static.hkcloudplay04.com/astarte2/3.6/web-mobile/assets/jiliMain/config.70ff4.json
https://jili-static.hkcloudplay04.com/astarte2/3.6/web-mobile/assets/jiliMain/index.70ff4.js
```

复核结果：

- `https://jili-static.hkcloudplay04.com/pp/?apiId=10585` 返回 HTTP 200。
- 上述 4 个深层资源返回 HTTP 403，响应来自 Amazon S3。
- AWS S3 私有桶 `dbqp-h5-hk-517506432530` 中，`tada-statics`、`tada-statics1`、`tada-statics2` 三个前缀均不存在上述 4 个对象。
- GCS 源端 `dbqp-gcs-tada-statics`、`dbqp-gcs-tada-statics1`、`dbqp-gcs-tada-statics2` 均不存在上述 4 个对象。
- 进一步检查当前香港配置内所有同步源桶：
  - `dbqp-gcs-pg-static`
  - `dbqp-gcs-pg3-static`
  - `dbqp-gcs-pg4-static`
  - `dbqp-gcs-pg5-static`
  - `dbqp-gcs-pp-static`
  - `dbqp-gcs-ppk-static`
  - `dbqp-gcs-panda-static`
  - `dbqp-gcs-tada-statics`
  - `dbqp-gcs-tada-statics1`
  - `dbqp-gcs-tada-statics2`

  均不存在 `astarte2/3.6/web-mobile/assets/jiliMain/*9330c*` 或 `*70ff4*` 文件。

已执行安全刷新：

```text
jili-static CloudFront: E2KICAEYOWJ24E
Invalidation: I5V6CM0KJC6IANVBBH6GUNRRXB
Status: Completed
Path: /*
```

刷新后复测：

```text
https://jili-static.hkcloudplay04.com/pp/?apiId=10585
HTTP 200

https://jili-static.hkcloudplay04.com/astarte2/3.6/web-mobile/assets/jiliMain/config.9330c.json
HTTP 403

https://jili-static.hkcloudplay04.com/astarte2/3.6/web-mobile/assets/jiliMain/index.9330c.js
HTTP 403

https://jili-static.hkcloudplay04.com/astarte2/3.6/web-mobile/assets/jiliMain/config.70ff4.json
HTTP 403

https://jili-static.hkcloudplay04.com/astarte2/3.6/web-mobile/assets/jiliMain/index.70ff4.js
HTTP 403
```

结论：

这批 403 不是 AWS 同步漏资源，也不是 CloudFront OriginPath 配错。`jili-static` 当前 OriginPath 确认为 `/tada-statics`，符合“JILI 复用 TADA 前端资源”的配置。403 的根因是当前测试链路或旧缓存引用了源端不存在的 JILI 线上版本资源。需要开发补齐对应资源，或调整入口/版本引用到源端真实存在的资源。

## 回滚

如果共享源路径导致异常，使用上线前保存的 CloudFront 配置和对应 ETag，将三个分配恢复到原 OriginPath：

```text
jili-static  -> /jili-static
jili-static1 -> /jili-static1
jili-static2 -> /jili-static2
```

恢复后分别创建 `/*` 失效请求，并等待状态回到 `Deployed`。共享的 `/tada-statics*` S3 对象是增量复制结果，不需要删除；Google 源桶也不得删除。
