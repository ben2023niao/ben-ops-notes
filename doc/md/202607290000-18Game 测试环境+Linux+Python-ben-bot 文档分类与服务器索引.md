---
id: "doc-f65812a61332"
title: "ben-bot 文档分类与服务器索引"
date: "2026-07-29T00:00:00+08:00"
dateSource: "正文日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Python", "Nginx", "监控告警", "自动化", "CDN", "DNS"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91ben-bot%E6%96%87%E6%A1%A3%E5%88%86%E7%B1%BB%E4%B8%8E%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%B4%A2%E5%BC%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/【运维记录】ben-bot文档分类与服务器索引.md"
sourceSha256: "c70979bad83bc5c6e8e7deabed8e25631fa7da6253ed3edeca92525f4dd90729"
sourceSystem: "project-doc"
---

# ben-bot 文档分类与服务器索引

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607290000-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BPython-ben-bot%20%E6%96%87%E6%A1%A3%E5%88%86%E7%B1%BB%E4%B8%8E%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%B4%A2%E5%BC%95.md)

> 整理日期：2026-07-29 00:00｜日期依据：正文日期

环境标签：通用

## 1. 文档用途

本文件用于快速定位 ben-bot、游点涩测试发版、S3/COS/CDN 和飞机群通知相关文档。

原则：

- 公开文档只写服务器用途、IP、用户、路径、桶名、域名、流程和验证结果。
- 密码、Token、私钥内容、云密钥、群敏感配置只写入本机私密文档。
- 私密文档目录 `devops/python/ben-bot/doc/private/` 已加入 `.gitignore`，不提交 Git。

## 2. 命名分类

| 分类 | 适用内容 | 示例 |
| --- | --- | --- |
| 【优化】 | 发布进度框、通知体验、定时任务、日志降噪 | `2026-07-29_1755-【优化】测试前端发布完成通知补备案域名记录.md` |
| 【架构改造】 | 新服务器、新桶、新 CDN、新 webhook、新发布链路 | `2026-07-27_1503-【架构改造+网络调整】游点涩S3拆分与发版操作记录.md` |
| 【问题排查】 | CORS、404、静态资源缺失、机器人运行位置、发布失败 | `2026-07-22_1503-【架构改造】游点涩PC测试环境发布改造.md` |
| 【网络调整】 | 域名、CNAME、EdgeOne、CDN、证书、源站 | `2026-07-27_1503-【架构改造+网络调整】腾讯COS新加坡私有化与邮件监控.md` |
| 【运维记录】 | 服务器索引、值班、交接、机器人菜单、联系信息 | 本文件 |

推荐命名：

```text
YYYY-MM-DD_HHMM-【分类】项目或问题简述.md
YYYY-MM-DD_HHMM-【分类1+分类2】项目或问题简述.md
```

## 3. 当前服务器索引

| 服务器 | 用途 | 登录身份 | 关键路径 | 备注 |
| --- | --- | --- | --- | --- |
| `52.79.252.255` | ben-bot 机器人真实运行服务器 | `ubuntu` + SSH key | `/opt/telegram/18game_devops/devops/python/ben-bot` | 运行 `ben-bot` 容器；机器人部署、菜单、webhook 和飞机群通知都以此为准 |
| `38.92.8.34` | 游点涩测试 H5/PC 宝塔发布目标 | `root` + 私密凭据 | `/www/wwwroot/18game_h5_client`、`/www/wwwroot/18game_pc_client` | 只负责前端构建、容器启动、Nginx/宝塔访问，不长期运行机器人 |

注意：

- 机器人真实运行机是 `52.79.252.255`。
- `38.92.8.34` 是测试发布目标，不是 ben-bot 主运行机。
- 服务器私密连接细节见本机 `devops/python/ben-bot/doc/private/服务器登录信息.local.md`。

## 4. 当前测试前端资源索引

| 类型 | H5 | PC |
| --- | --- | --- |
| 页面入口 | `https://h5.youdianse-test.xyz` | `https://pc.youdianse-test.xyz` |
| 前端仓库 | `web/youdianse-h5`，`test` 分支 | `web/youdianse-pc`，`dev` 分支 |
| AWS 前端静态桶 | `18game-nuxt-static-test-h5` | `18game-nuxt-static-test-pc` |
| 腾讯新加坡 COS | `18game-nuxt-static-test-h5-sg-1450169938` | `18game-nuxt-static-test-pc-sg-1450169938` |
| 腾讯 CDN/EdgeOne | `https://test-h5-s3.hbabaxb.cn` | `https://test-pc-s3.hbabaxb.cn` |
| 发布容器 | `youdianse_test_18game_h5_client_3003` | `youdianse_pc_dev_18game_pc_client_3004` |

当前策略：

- 前端 H5/PC 构建后同时推 AWS 前端静态桶和腾讯新加坡 COS。
- 页面前端 `_nuxt`、CSS、JS、前端静态图优先走腾讯 CDN/EdgeOne。
- 腾讯 COS 桶保持私有，不允许 COS 原始域名公网直连。
- 每次测试前端发布后刷新腾讯 CDN/EdgeOne 的 `_nuxt/` 和 `images/`。
- 后端 uploads 图片、APK/App 包仍属于后端 AWS S3/CloudFront 链路，不混入前端发版流程。

## 5. 推荐阅读顺序

1. `devops/ai_context/README.md`：当前 AI/运维上下文总览。
2. `devops/ai_context/servers.yml`：服务器、环境变量、桶、CDN、发布策略索引。
3. `devops/python/ben-bot/doc/2026-07-29_1806-【运维记录】测试前端H5-PC备案域名与S3链路索引.md`：测试 H5/PC 备案域名、AWS S3、腾讯 COS、EdgeOne 静态资源链路索引。
4. `devops/python/ben-bot/doc/2026-07-29_1755-【优化】测试前端发布完成通知补备案域名记录.md`：测试 H5/PC 发布完成通知补充备案域名。
5. `devops/python/ben-bot/doc/2026-07-27_1503-【架构改造+网络调整】游点涩S3拆分与发版操作记录.md`：测试前端 S3 拆分、新加坡 COS、EdgeOne 证书和解析过程。
6. `devops/python/ben-bot/doc/2026-07-27_1503-【架构改造+网络调整】腾讯COS新加坡私有化与邮件监控.md`：COS 私有化、后台 S3 同步、腾讯通知邮件转发背景。
7. `devops/python/ben-bot/doc/2026-07-29_1700-【优化+架构改造+问题排查】ben-bot前端Webhook发版与S3双推验证记录.md`：ben-bot webhook、进度框、双推和 CORS 验证记录。
8. `devops/python/ben-bot/doc/2026-07-29_1735-【网络调整+架构改造】hbabaxb.cn腾讯DNSPod接管与解析补齐记录.md`：`hbabaxb.cn` 切 DNSPod、15 条解析补齐和访问验证。
9. `devops/python/ben-bot/doc/2026-07-29_1740-【网络调整+架构改造】hbazuua.cn腾讯DNSPod接管与解析补齐记录.md`：`hbazuua.cn` 切 DNSPod、3 条解析补齐和访问验证。
10. `devops/python/ben-bot/doc/2026-07-29_1730-【优化】测试前端发布通知合并与滚动进度框记录.md`：测试 H5/PC 按钮发布和 webhook 发布的进度通知合并策略。
11. `devops/python/ben-bot/doc/private/服务器登录信息.local.md`：仅本机私密连接信息，不提交。

## 6. 更新规则

- 新增服务器、桶、CDN、域名、webhook 或机器人菜单后，同步更新本文件和 `devops/ai_context/servers.yml`。
- 发生发布故障、CORS、404、缓存或同步问题时，新增日期型问题排查文档，不把细节散落到聊天记录里。
- 每次涉及飞机群通知、机器人菜单、webhook 自动发布的变更，都要记录通知目标群和验证结果。
