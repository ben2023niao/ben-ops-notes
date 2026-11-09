---
id: "doc-f6a1683dcbc0"
title: "测试环境登录加载慢：后端 API 无响应诊断"
date: "2026-08-17T19:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Python", "Docker", "Nginx", "Redis", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-17_1940-%E3%80%90%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%90%8E%E7%AB%AFAPI%E6%97%A0%E5%93%8D%E5%BA%94%E5%AF%BC%E8%87%B4%E7%99%BB%E5%BD%95%E5%8A%A0%E8%BD%BD%E6%85%A2.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-17_1940-【修复记录】测试环境后端API无响应导致登录加载慢.md"
sourceSha256: "921126edd8c5d71bb19bf05413c287fb787ee2be71c4f395b41eacc2a3f7287e"
sourceSystem: "project-doc"
---

# 测试环境登录加载慢：后端 API 无响应诊断

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608171940-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BPython-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E7%99%BB%E5%BD%95%E5%8A%A0%E8%BD%BD%E6%85%A2%EF%BC%9A%E5%90%8E%E7%AB%AF%20API%20%E6%97%A0%E5%93%8D%E5%BA%94%E8%AF%8A%E6%96%AD.md)

> 整理日期：2026-08-17 19:40｜日期依据：文件名日期

环境标签：测试环境 / 登录 / API / 后端容器 / 38.92.8.34

时间：2026-08-17 19:40（Asia/Manila）

## 背景

用户反馈测试环境登录要加载很久，要求优先处理。结合此前巡检（H5 SSR 页面 14-25s）进一步定位。

## 定位过程与证据

### 1. 页面本身正常

| 路径 | 结果 |
| --- | --- |
| https://h5.youdianse-test.xyz/login | 200，0.34s |
| https://pc.youdianse-test.xyz/login | 200，0.35s |
| /register | 200，0.19s |
| /version.json / favicon / robots / sw.js | <0.3s |
| GIF（dd3tn75akeg7c） | 200，0.7s |

### 2. 后端 API 全部超时

| 请求 | 结果 |
| --- | --- |
| POST /api/v1/user/login /login /auth/login /user/register | 000，30s 超时 |
| GET /api/v1/game/lists /modules/home | 000，20s 超时 |
| POST via pc.youdianse-test.xyz | 000，20s 超时 |
| admin.youdianse-test.xyz / api | 000，15s 超时 |
| ssl.youdianse-test.xyz | 000，15s 超时 |

结论：**测试后端 PHP/API 整体无响应**（38.92.8.34 上 /opt/docker-youdianse-php 容器），前端静态与页面正常。登录提交卡在登录接口；H5 首页/详情 SSR 14-25s 也是因为 SSR 等待该挂掉的 API。

### 3. 访问通道

- 测试宝塔 38.92.8.34 为 root 密码登录（安全渠道），本地/容器现有密钥均无法登录，需有权限同事执行重启。

## 处理建议（需 38.92.8.34 root 权限）

```text
ssh root@38.92.8.34
cd /opt/docker-youdianse-php
docker ps          # 确认 youdianse-dev-php-web / nginx / cron 状态
docker logs --tail 50 youdianse-dev-php-web   # 看 php 报错
docker restart youdianse-dev-php-web youdianse-dev-php-nginx   # 视情况
# 验证
curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "{}" \
  https://admin.youdianse-test.xyz/api/v1/modules/home   # 期望 200
```

## 结论

- 登录慢根因 = 测试后端 API 无响应（全部 /api 与 admin 超时），非前端问题。
- 已把诊断与处理命令发 `18game运维` 群，等待有权限同事重启后端容器后复测登录与各接口。

## 最终结论（2026-08-17 20:50 更新）

- 重启只能临时恢复几分钟，随后再次全站 504。最终根因见 `2026-08-17_2050-【修复记录】测试环境登录加载慢-配置缓存3.6MB脏数据根因与修复.md`。
- 一句话根因：`config.vip_growth_rule` 今天 19:11 被误粘贴成 3.6MB 腾讯文档 HTML，撑爆 Redis 配置缓存，每次请求跨网读 3.6MB（网络抖动时单次 GET 90s+），5 个 FPM worker 被占满后全站 API 504。
- 已修复：备份 → 恢复为 771 字节正常富文本 → 删除 Redis 缓存 → 重启 php-web。复测：API 8-12ms、H5 SSR 0.16s、登录页 0.02s，修复后 0 条 slow_api 新日志。
