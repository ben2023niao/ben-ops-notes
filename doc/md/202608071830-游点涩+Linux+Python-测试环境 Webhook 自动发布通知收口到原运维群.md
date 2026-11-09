---
id: "doc-3b6288c4abc1"
title: "测试环境 Webhook 自动发布通知收口到原运维群"
date: "2026-08-07T18:30:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Python", "Docker", "监控告警", "自动化", "CDN", "安全运维"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-07-1830-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83Webhook%E8%87%AA%E5%8A%A8%E5%8F%91%E5%B8%83%E9%80%9A%E7%9F%A5%E6%94%B6%E5%8F%A3%E5%88%B0%E5%8E%9F%E8%BF%90%E7%BB%B4%E7%BE%A4.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-07-1830-【运维记录】测试环境Webhook自动发布通知收口到原运维群.md"
sourceSha256: "db6230516f67a276f953d15d47c2663a45908483b69d697f1037834dd2157fdf"
sourceSystem: "project-doc"
---

# 测试环境 Webhook 自动发布通知收口到原运维群

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608071830-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BPython-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%20Webhook%20%E8%87%AA%E5%8A%A8%E5%8F%91%E5%B8%83%E9%80%9A%E7%9F%A5%E6%94%B6%E5%8F%A3%E5%88%B0%E5%8E%9F%E8%BF%90%E7%BB%B4%E7%BE%A4.md)

> 整理日期：2026-08-07 18:30｜日期依据：文件名日期

环境标签：测试环境

时间：2026-08-07 18:30

2026-08-11 更新：收口范围从 Webhook 自动发布扩大到全部发布类通知（人工发布 + Webhook 自动发布 + 发布会话内运行配置同步），配置名升级为 `TG_PUBLISH_CHAT_IDS`（旧名 `TG_WEBHOOK_CHAT_IDS` 兼容）。详见 `docs/2026-08-11-1830-【运维记录】测试环境发布通知收口到原运维群.md`。

## 背景

用户要求：

```text
测试环境 自动化发布 就不要通知到 18game运维 这个飞机群了。
```

并要求：读取 doc 历史文档；使用 workbench；每步操作发群通知；操作完成后先验证再汇总文档；汇总和文档发群里；最后合并提交本地代码。

## 现状核验（2026-08-07 只读）

```text
测试服务器：youdianse-test / 38.92.8.34
外层运维仓库 HEAD：f1c03c7（origin/dev 领先 1 个提交 a93aba4，env/.env.dev 新增 log_path）
CICD Web：运行中，18090 HTTP 200；3003/3004/8088/18090 均在监听
secrets.env 键：YOUDIANSE_PUBLISH_PASSWORD / YOUDIANSE_WEBHOOK_TOKEN / TG_BOT_TOKEN / TG_CHAT_ID / YOUDIANSE_HEALTH_TG_CHAT_ID / TG_EXTRA_CHAT_IDS
原运维监控报警群：TG_CHAT_ID 与 YOUDIANSE_HEALTH_TG_CHAT_ID 为同一 chat_id
18game运维 群：TG_EXTRA_CHAT_IDS
config 解析结果：3 个目标 = 原群 + 无效 “[]” + 18game运维
生产日志：每次发送“成功 2 个群、失败 1 个群”，失败目标即无效 “[]”
```

无效 “[]” 来源：`settings.json` 的 `telegram.chat_ids: []` 被 `str()` 转成字符串 `"[]"`，被当作一个真实群目标发送，Telegram 返回 HTTP 400。

## 改动

### 1. 代码（本地仓库 dev）

```text
cicd-web/config.py
  - 修复空列表解析：settings.json 的 chat_ids: [] / extra_chat_ids: [] 不再产生无效目标 “[]”。
  - 新增 TG_WEBHOOK_CHAT_IDS：优先读 secrets.env 的 TG_WEBHOOK_CHAT_IDS，其次 settings.json 的 telegram.webhook_chat_ids；未配置时回退全量群列表。
cicd-web/telegram.py
  - 新增 Webhook 专用群覆盖 set/clear，解析群列表时优先返回专用群。
  - 异步队列项快照发送时的群列表，避免任务结束时覆盖被提前清理的竞态。
cicd-web/webhook.py
  - Webhook 自动发布触发即启用专用群覆盖，后台任务 finally 清理；
    发布占用、发布结果、详细部署日志文件只发专用群。
cicd-web/config/settings.json
  - telegram 增加 webhook_chat_ids: []。
```

### 2. 测试服务器运行密钥（只写服务器本地，不提交 Git）

```text
路径：/opt/docker-youdianse-php/cicd-web/runtime/secrets.env
新增：TG_WEBHOOK_CHAT_IDS=<原运维监控报警群 chat_id>
```

### 3. 文档与 workbench

```text
新增：docs/2026-08-07-1830-【运维记录】测试环境Webhook自动发布通知收口到原运维群.md
更新：workbench/CURRENT_TASK.md / CURRENT_STATE.md / DECISIONS.md / ACTIVE_TASKS.md
更新：README.md 运行密钥维护说明
```

## 验证

```text
1. 本地：python3 -m py_compile 通过；config 解析 TG_CHAT_IDS=2（无 “[]”）、TG_WEBHOOK_CHAT_IDS=1；override 设置/清理行为通过。
2. 测试服务器（2026-08-07 18:35 实测）：外层 HEAD=eef1fe0；重启后 CICD Web 新 PID 3051907，18090 HTTP 200。
3. 群解析：TG_CHAT_IDS=2（原运维监控报警群 + 18game运维，sha256 已核对去重），TG_WEBHOOK_CHAT_IDS=1（仅原运维监控报警群）；settings.json 空列表不再产生 “[]” 目标。
4. 测试发送：Webhook 专用群覆盖下发送成功 1 个群；全量群发送成功 2 个群、失败 0（修复前为成功 2 失败 1）。
5. 端点检查：/auto-deploy 使用错误 token 返回 401，未触发真实发布。
6. 步骤通知：步骤 8/9 群通知发送成功 2 群、失败 0，印证 “[]” 无效目标已消除。
```

## 通知规则变化

```text
Webhook 自动发布（自动发布占用、发布结果、详细部署日志）：只发原运维监控报警群。
人工发布、文档/步骤通知、健康告警：保持现有已配置群（原运维监控报警群 + 18game运维）。
```

## 安全要求

```text
不输出、不记录、不提交 Telegram token/chat_id、SSH 密码、发布密码、私钥和带凭据仓库 URL。
TG_WEBHOOK_CHAT_IDS 只写测试服务器 secrets.env。
```

## 遗留说明

```text
测试服务器 env/.env.dev 存在本地删除 [cdn.tencent.test-img] 段的运行态改动（已有备份
env.env.dev.bak_before_remove_test_img_cdn_20260806_181959），本次保留不动，未纳入提交。
```
