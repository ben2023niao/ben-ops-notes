---
id: "doc-e738bc7f83eb"
title: "测试后端 uploads 图片 EdgeOne 反代与防盗刷落地记录"
date: "2026-07-29T21:55:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "自动化", "CDN", "DNS", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2155-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%2B%E5%AE%89%E5%85%A8%E4%BC%98%E5%8C%96%E3%80%91%E6%B5%8B%E8%AF%95%E5%90%8E%E7%AB%AFuploads%E5%9B%BE%E7%89%87EdgeOne%E5%8F%8D%E4%BB%A3%E4%B8%8E%E9%98%B2%E7%9B%97%E5%88%B7%E8%90%BD%E5%9C%B0%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2155-【网络调整+安全优化】测试后端uploads图片EdgeOne反代与防盗刷落地记录.md"
sourceSha256: "37ac00d3434d2f0fc872cc3e258a7391488a499c82f9127256daf9b297de23f1"
sourceSystem: "project-doc"
---

# 测试后端 uploads 图片 EdgeOne 反代与防盗刷落地记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2155-【网络调整+安全优化】测试后端uploads图片EdgeOne反代与防盗刷落地记录.md`

> 整理日期：2026-07-29 21:55｜日期依据：文件名日期

环境标签：测试环境

## 1. 背景

测试 PC 前端静态资源曾尝试加 token 鉴权，但前端页面域名和测试域名变化频繁，容易引入 CORS、524、相对路径和缓存兼容问题。

最终调整方向：

- 前端打包资源不再加密，H5/PC 的 `_nuxt`、JS、CSS、前端图片继续按现有 S3/COS 静态资源链路发布。
- 后端 uploads 图片才是主要盗刷风险点，单独新建腾讯 EdgeOne 反代域名做防盗刷。
- 不改后台上传逻辑，上传仍继续写 AWS S3。
- 只把后端展示域名从 AWS CloudFront 切到腾讯 EdgeOne 域名。

## 2. 本次范围

测试环境：

```text
页面入口:
- https://pc.youdianse-test.xyz
- https://test-pc.hbabaxb.cn

后端 uploads 原展示域名:
- https://d1rct3ku9n07y3.cloudfront.net

后端 uploads 新展示域名:
- https://test-img.hbabaxb.cn
```

不改动：

- 前端打包静态资源鉴权。
- 测试 H5 当前页面资源链路。
- 后台上传 AWS S3 逻辑。
- APK/App 客户端包链路。
- 线上环境。

## 3. EdgeOne 与 DNS

新增 EdgeOne 加速域名：

```text
test-img.hbabaxb.cn
```

DNSPod 解析：

```text
主机记录: test-img
记录类型: CNAME
记录值: test-img.hbabaxb.cn.eo.dnse4.com
TTL: 600
RecordId: 66127418
```

当前反代链路：

```text
浏览器
-> test-img.hbabaxb.cn
-> 腾讯 EdgeOne
-> 测试源站 Nginx 38.92.8.34:80
-> AWS CloudFront d1rct3ku9n07y3.cloudfront.net
-> AWS S3 uploads 对象
```

说明：

- 最初 EdgeOne 直接回源 CloudFront 时，需要设置回源 Host 为 `d1rct3ku9n07y3.cloudfront.net`，否则 CloudFront 返回 403。
- 为了实现 Referer 防盗刷并避免 EdgeOne 缓存绕过，最终改为 EdgeOne 回源测试 Nginx，由 Nginx 做 Referer 白名单判断和 no-store 响应头。

## 4. 测试源站 Nginx

本地配置文件：

```text
devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/nginx/test-img.hbabaxb.cn.conf
```

服务器配置文件：

```text
/www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf
```

关键策略：

```text
只允许 /uploads/*
允许 Referer / 空 Referer:
- none
- *.hbabaxb.cn
- *.youdianse-test.xyz

非本站 Referer:
- 返回 403

缓存控制:
- Cache-Control: private, no-store, max-age=0
- Vary: Referer
```

这样处理的原因：

- 如果 EdgeOne 缓存了允许 Referer 的 200 图片，再被无 Referer 请求命中同一缓存，会绕过源站 Referer 校验。
- 源站统一返回 no-store 后，EdgeOne 不缓存该反代图片，Referer 判断每次回到 Nginx 执行。

## 5. 后端配置变更

后端配置项：

```text
Mongo config.code = cdn_image
```

变更内容：

```text
将 cdn_image 中 CloudFront 展示项:
https://d1rct3ku9n07y3.cloudfront.net

替换为:
https://test-img.hbabaxb.cn
```

替换结果：

```text
替换数量: 2
system_config 缓存: 已删除
```

备份文件：

```text
测试后端容器:
/var/www/html/youdianse-php/runtime/logs/cdn_image_backup_20260729_215058.txt
```

保持不变：

- 后台上传仍写 AWS S3。
- 后端客户端包/APK/App 链路不切。
- 腾讯 COS uploads 备用配置不删除。

## 6. 验证结果

DNS：

```text
test-img.hbabaxb.cn CNAME test-img.hbabaxb.cn.eo.dnse4.com
```

样例图片：

```text
https://test-img.hbabaxb.cn/uploads/2026-03-02/809f5e380d5eec76d232b5d5a2ca634d.png
```

CDN 防盗刷验证：

| 场景 | 结果 |
| --- | --- |
| `Referer: https://test-pc.hbabaxb.cn/` | `200 image/webp` |
| 无 Referer | `200 image/webp` |
| `Referer: https://example.com/` | `403 text/html` |
| 再次允许 Referer | `200 image/webp` |

2026-07-29 22:05 修正：

- `pc.youdianse-test.xyz` 页面当前 `Referrer-Policy` 为 `no-referrer`，浏览器正常加载 `test-img` 图片时不会携带 Referer。
- 原先“无 Referer 返回 403”的策略会误伤正常 PC 页面图片，导致页面图片全部 403。
- 已将 Nginx `valid_referers` 调整为 `none *.hbabaxb.cn *.youdianse-test.xyz`，先保证页面恢复。
- 调整后：无 Referer 样例图 `200 image/webp`，`Referer: https://example.com/` 仍为 `403 text/html`。

页面返回验证：

```text
https://test-pc.hbabaxb.cn/
命中 test-img.hbabaxb.cn: 86 处

https://pc.youdianse-test.xyz/
命中 test-img.hbabaxb.cn: 86 处
```

补充验证：

```text
2026-07-29 22:00 从当前本地网络抽测多个 EdgeOne A 记录：
- 测试源站 Nginx 直连: 允许 Referer 200，外部 Referer 403
- 多数 EdgeOne 节点: 允许 Referer 200
- 个别 EdgeOne A 记录: 当前本地网络直连超时
```

判断：

- 后端配置、测试源站 Nginx 和防盗刷策略均已生效。
- 个别 EdgeOne IP 超时更偏向新域名边缘调度/网络可达性差异，需继续观察 DNS 调度和边缘节点状态。

结论：

- 后端展示域名已经生效。
- 测试 PC 备案入口和原 AWS 页面入口均能使用新 uploads 展示域名。
- 带外部 Referer 的热链会被拦截。
- 因 PC 页面本身使用 `no-referrer`，当前必须允许空 Referer；这属于兼容性取舍，不能作为强防盗刷方案。

## 7. 回滚方式

如需回滚：

1. 从备份文件恢复 `cdn_image` 原值。
2. 删除后端缓存 `system_config`。
3. 可选择把 EdgeOne `test-img.hbabaxb.cn` 保留为空闲备用，或暂停该加速域名。

回滚目标：

```text
后端 uploads 展示域名恢复到:
https://d1rct3ku9n07y3.cloudfront.net
```

注意：

- 回滚不需要改上传逻辑。
- 回滚不需要动前端 H5/PC 发布脚本。
- 如果只暂停 EdgeOne 但不回滚 `cdn_image`，前端页面会继续拿到 `test-img.hbabaxb.cn`，可能造成图片不可用。

## 8. 飞机群通知

目标群：

```text
稳定备案域名+腾讯云原厂
```

已按步骤通知：

1. 开始改造测试后台 uploads 图片反代。
2. 确认 `test-img.hbabaxb.cn` 尚未存在。
3. 创建 EdgeOne 加速域名。
4. 创建 DNSPod CNAME。
5. 验证 DNS 和 CloudFront 原图。
6. 修正 EdgeOne 回源 Host。
7. 绑定 EdgeOne 免费证书。
8. 增加测试源站 Nginx Referer 防盗刷。
9. 修复 EdgeOne 缓存绕过问题，增加 no-store。
10. 切换后端 `cdn_image` 展示域名。
11. 验证页面返回和防盗刷结果。
