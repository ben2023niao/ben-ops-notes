---
id: "doc-ea2d07c34f34"
title: "测试环境 H5/PC 发布后强制清理 CDN 缓存规则"
date: "2026-07-31T16:06:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "自动化", "CDN", "安全运维"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-31-1606-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83H5-PC%E5%8F%91%E5%B8%83%E5%90%8E%E5%BC%BA%E5%88%B6%E6%B8%85%E7%90%86CDN%E7%BC%93%E5%AD%98%E8%A7%84%E5%88%99.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-31-1606-【运维记录】测试环境H5-PC发布后强制清理CDN缓存规则.md"
sourceSha256: "43eeccaa516d626060fe23f21fedde02f533d65c05e1464127eaabaec5818d3e"
sourceSystem: "project-doc"
---

# 测试环境 H5/PC 发布后强制清理 CDN 缓存规则

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607311606-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%20H5-PC%20%E5%8F%91%E5%B8%83%E5%90%8E%E5%BC%BA%E5%88%B6%E6%B8%85%E7%90%86%20CDN%20%E7%BC%93%E5%AD%98%E8%A7%84%E5%88%99.md)

> 整理日期：2026-07-31 16:06｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-31 16:06

## 背景

用户要求：

```text
每次测试环境发布 H5 / PC 的时候都需要清理 CDN 缓存。
继续使用 workbench 留痕。
```

本规则只作用于测试环境，不涉及正式环境。

## 当前能力核验

已只读核验测试服务器 ben-bot 发布脚本：

```text
H5 入口：测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py
PC 入口：测试环境-游点涩-pc-发版/youdianse_test_18game_pc_client.py
PC 发布复用 H5 发布引擎，通过环境变量覆盖 PC 仓库、项目名、端口、静态桶等参数
```

当前不能自动提交 CDN purge 的原因：

```text
测试服务器未安装 tccli、aws、coscmd
测试服务器未安装 tencentcloud/qcloud_cos/boto3 Python 模块
/opt/docker-youdianse-php/cicd-web/runtime/secrets.env 未配置 Tencent/EdgeOne API 凭据字段
ben-bot 的 CDN刷新脚本当前只是人工处理框架，不会实际调用 purge API
```

因此本次先把 CDN 清缓存落为发布流程里的强制人工/控制台步骤。

## 硬规则

```text
1. 每次测试环境 H5 发布后，必须清理 H5 页面域名、备案域名和 H5 静态资源域名缓存。
2. 每次测试环境 PC 发布后，必须清理 PC 页面域名、备案域名和 PC 静态资源域名缓存。
3. 如果发布涉及 uploads 图片、广告图、图片签名、默认图或图片域名异常，同时清理 test-img.* /uploads/。
4. 未完成 CDN 清缓存，不允许发送“发布完成”收口通知。
5. 清缓存失败时，应发“发布已完成但 CDN 清缓存失败/待处理”通知，并记录待处理原因。
```

## H5 清缓存范围

每次 H5 发布后清理：

```text
https://h5.youdianse-test.xyz/
https://test-h5.hbabaxb.cn/
https://test-h5.hbazuua.cn/
https://test-h5-s3.hbabaxb.cn/
https://test-h5-s3.hbabaxb.cn/_nuxt/
```

## PC 清缓存范围

每次 PC 发布后清理：

```text
https://pc.youdianse-test.xyz/
https://test-pc.hbabaxb.cn/
https://test-pc.hbazuua.cn/
https://test-pc-s3.hbabaxb.cn/
https://test-pc-s3.hbabaxb.cn/_nuxt/
```

## 图片相关附加清理范围

如本次发布涉及图片签名、广告位、默认图、uploads 展示异常或图片域名回源问题，同时清理：

```text
https://test-img.hbabaxb.cn/uploads/
https://test-img.hbazuua.cn/uploads/
```

## 操作要求

当前执行方式：

```text
腾讯 EdgeOne / CDN 控制台人工清理
或由已有权限的外部工具提交刷新任务
```

清理方式建议：

```text
优先目录刷新：页面域名根目录、静态资源域名根目录、_nuxt/ 目录
涉及图片时刷新：test-img.* /uploads/ 目录
不建议默认全站清理，除非目录刷新仍无法恢复或确认影响范围很小
```

清理后记录：

```text
清理时间
操作者
清理域名/目录
任务 ID 或控制台截图摘要
验证结果
```

不得记录：

```text
Tencent SecretId / SecretKey
Telegram token / chat_id
SSH 密码
发布密码
带凭据仓库 URL
```

## 发布后验证

H5：

```bash
curl -k -I https://h5.youdianse-test.xyz/
curl -k -I https://test-h5.hbabaxb.cn/
curl -k -I https://test-h5.hbazuua.cn/
curl -k -sS https://h5.youdianse-test.xyz/version.json
curl -k -sS https://test-h5-s3.hbabaxb.cn/version.json
```

PC：

```bash
curl -k -I https://pc.youdianse-test.xyz/
curl -k -I https://test-pc.hbabaxb.cn/
curl -k -I https://test-pc.hbazuua.cn/
curl -k -sS https://pc.youdianse-test.xyz/version.json
curl -k -sS https://test-pc-s3.hbabaxb.cn/version.json
```

图片：

```text
test-img 总数 > 0
token/t 数量 = test-img 总数
sign 数量 = 0
裸链数量 = 0
```

## Telegram 收口通知必须包含

```text
发布项目：H5 或 PC
目标提交：<short_id>
容器/镜像：<container>/<image>
CDN 清缓存：已完成
清理范围：页面域名、备案域名、静态资源域名、必要时 test-img uploads
清理任务：<任务 ID 或控制台记录摘要>
验证结果：入口 200、version 新版本、test-img token/t 正常
```

如果 CDN 清缓存未完成：

```text
不能使用“发布完成”字样。
应使用“发布已完成但 CDN 清缓存待处理”。
必须写清楚待处理域名、原因、负责人和下一步时间。
```

## 后续自动化方向

Tencent EdgeOne 官方 `CreatePurgeTask` 支持缓存清理，`Type` 可使用：

```text
purge_url
purge_prefix
purge_host
purge_all
```

自动化前提：

```text
1. 在安全运行态配置 Tencent EdgeOne API SecretId / SecretKey。
2. 配置对应 ZoneId。
3. 确认 API 权限覆盖测试环境相关站点。
4. 在 H5/PC 共用发布引擎中，发布成功后提交 CreatePurgeTask。
5. 发布日志和 Telegram 只输出任务 ID，不输出密钥。
```

官方参考：

```text
CreatePurgeTask：https://www.tencentcloud.com/document/product/1145/50536
TencentCloud API Signature V3：https://www.tencentcloud.com/document/product/597/35336
```
