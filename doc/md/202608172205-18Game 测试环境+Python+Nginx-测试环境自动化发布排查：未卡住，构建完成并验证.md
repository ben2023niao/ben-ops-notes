---
id: "doc-d65206553f52"
title: "测试环境自动化发布排查：未卡住，构建完成并验证"
date: "2026-08-17T22:05:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Nginx", "Redis", "自动化", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-17_2205-%E3%80%90%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E8%87%AA%E5%8A%A8%E5%8C%96%E5%8F%91%E5%B8%83%E6%9C%AA%E5%8D%A1%E4%BD%8F-%E6%9E%84%E5%BB%BA%E5%AE%8C%E6%88%90%E9%AA%8C%E8%AF%81.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-17_2205-【排查记录】测试环境自动化发布未卡住-构建完成验证.md"
sourceSha256: "c140bc0ef6601b143051b74d194fee7c9b2f8c56a9e5616fe3b798bb464281e4"
sourceSystem: "project-doc"
---

# 测试环境自动化发布排查：未卡住，构建完成并验证

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608172205-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BPython%2BNginx-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E8%87%AA%E5%8A%A8%E5%8C%96%E5%8F%91%E5%B8%83%E6%8E%92%E6%9F%A5%EF%BC%9A%E6%9C%AA%E5%8D%A1%E4%BD%8F%EF%BC%8C%E6%9E%84%E5%BB%BA%E5%AE%8C%E6%88%90%E5%B9%B6%E9%AA%8C%E8%AF%81.md)

> 整理日期：2026-08-17 22:05｜日期依据：文件名日期

环境标签：测试环境 / CICD / 自动发布 / 38.92.8.34

时间：2026-08-17 22:05（Asia/Manila）

## 背景

后端 dev 推送包含「会员规则大小限制」修复的代码后（诸葛亮：“35就提交了，是不是自动发布卡住了”），排查测试环境自动化发布状态。

## 排查结论

- **自动发布未卡住**。21:35:53 GitLab webhook 正常触发 `/auto-deploy/youdianse`，目标 `a3fb5d07`；构建耗时约 9 分钟（composer install 约 6.5 分钟 + 1.16GB 镜像导出），21:44:19 发布完成 `SUCCESS`。
- 服务器业务代码已同步：`src/youdianse-php` HEAD = `a3fb5d07ce8d`（= origin/dev）。
- 容器已切换：web/nginx/cron 全部 running，镜像 `youdianse-php:dev-a3fb5d07ce8d`，dirty=false。
- 健康检查：HTTP 200 / Session writable / Redis 1ms / Mongo 0ms。

## 新代码验证（防复发治本项已上线）

- `app/Repositories/Backend/VipRuleRepository.php` 新增 `MAX_CONTENT_BYTES = 65536`（64KB），`save()` 超限抛错：`规则内容过大，请勿粘贴带图片的文档，图片请用编辑器上传`。
- 内容改为独立集合 `vip_growth_rule` 存储，保存时删除旧 `config.vip_growth_rule` 并清 `SYSTEM_CONFIG` 缓存，不再把富文本塞进统一配置缓存。
- 当前 Mongo `config.vip_growth_rule` 已不存在，Redis `18game_system_config` = 7,073 字节。

## 稳态验证（发布后）

| 检查项 | 结果 |
| --- | --- |
| admin /api/v1/modules/home | 200，0.14s |
| h5 /api/v1/system/info | 200，0.26s |
| h5 /api/v1/game/lists | 200，0.17s |
| H5 首页 | 200，0.42s |
| Redis 配置缓存 | 7,073 字节 |
| slow_api（21:44 后） | 0 条 |

说明：21:44-21:59 的少量 3-4s FPM 慢日志为容器重启后各接口冷缓存重建，当前稳态已恢复。

## 通知与提交

- 每步已发 `18game运维` 群（步骤 1-2）。
- 本地 Git 已提交（不 Push），commit 信息见提交结果通知。
