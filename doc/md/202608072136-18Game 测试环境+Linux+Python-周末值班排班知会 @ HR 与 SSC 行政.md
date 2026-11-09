---
id: "doc-e6787660efd8"
title: "周末值班排班知会 @ HR 与 SSC 行政"
date: "2026-08-07T21:36:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Python", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-07_2136-%E3%80%90%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E5%91%A8%E6%9C%AB%E5%80%BC%E7%8F%AD%E6%8E%92%E7%8F%AD%E7%9F%A5%E4%BC%9A%40HR%E4%B8%8ESSC%E8%A1%8C%E6%94%BF.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-07_2136-【优化+运维记录】周末值班排班知会@HR与SSC行政.md"
sourceSha256: "8e6cacf5e700f35c68a0b636bc3c112da82afcd8dc0bd91b82b5f17fad88cd13"
sourceSystem: "project-doc"
---

# 周末值班排班知会 @ HR 与 SSC 行政

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608072136-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BPython-%E5%91%A8%E6%9C%AB%E5%80%BC%E7%8F%AD%E6%8E%92%E7%8F%AD%E7%9F%A5%E4%BC%9A%20%40%20HR%20%E4%B8%8E%20SSC%20%E8%A1%8C%E6%94%BF.md)

> 整理日期：2026-08-07 21:36｜日期依据：文件名日期

环境标签：通用 / ben-bot / 运维值班表 / 排班知会

时间：2026-08-07 21:36（Asia/Manila）

## 任务来源

用户要求：

- 读取 `doc` 历史文档，使用 `workbench`，每步操作都发群通知。
- 运维值班表换班通知只在周末通知（沿用）。
- 周末值班的排班信息需要机器人 @ HR `@Mollyprojectx8` 和 SSC 行政 `@Yi_nuo_11`，方便她们知道排班信息。
- 操作完成后先验证，再汇总文档，并把汇总和文档发群里（运维值班相关信息只发 `18GAME_ 上线群（正式環境）`）。
- 最后合并提交本地代码。

## 本轮读取依据

按 workbench 入口读取：

- `AGENTS.md`
- `workbench/START_HERE.md`
- `workbench/ACTIVE_TASKS.md`
- `workbench/NOTIFICATION_TARGETS.md`
- `workbench/projects/18game_devops/CURRENT_STATE.md`
- `workbench/projects/18game_devops/CURRENT_TASK.md`
- `devops/ai_context/servers.yml`

重点参考历史文档：

- `devops/python/ben-bot/doc/2026-08-07_2132-【优化+运维记录】运维值班出勤统计与提醒优化.md`
- `devops/python/ben-bot/doc/2026-08-07_2112-【优化+运维记录】运维值班表仅周末显示通知与值班通知收口上线群.md`

## 群通知

按用户要求，运维值班相关信息统一只通知 `18GAME_ 上线群（正式環境）`（`-1003762262155`）。

已通知步骤（全部发送到该群）：

1. 恢复上下文并确认排班知会方案。
2. 排班知会 @ 实现完成。
3. 本地静态验证通过。
4. 运行机同步、备份、容器重建完成。
5. 容器内验证通过。

通知内容未包含密码、token、Secret Key、私钥正文、Session Cookie、完整 Signed URL、数据库连接串或 `.env` 原文。

## 实现内容

文件：`devops/python/ben-bot/app/benbot/duty_status.py`

新增：

```python
ROSTER_NOTIFY_MENTIONS = ("@Mollyprojectx8", "@Yi_nuo_11")  # HR / SSC 行政：周末排班知会
ROSTER_MENTION_EVENTS = frozenset({"early_remind", "early_start", "handoff_remind", "handoff_start"})
```

`build_duty_event_message()` 在排班知会类事件中自动追加：

```text
📣 排班知会：@Mollyprojectx8 @Yi_nuo_11
```

触发事件（周末值班排班信息沟通时点）：

| 事件 | 时间 | 说明 |
|---|---:|---|
| `early_remind` | 13:30 | 早班前 30 分钟提醒 |
| `early_start` | 14:00 | 早班上班 |
| `handoff_remind` | 16:30 | 换班前 30 分钟提醒 |
| `handoff_start` | 17:00 | 晚班上班、交接开始 |

下班/结束类事件（`handoff_end`、`early_end_after`、`late_end`、`late_end_after`）不重复 @，避免打扰 HR 与 SSC 行政。

## 同步与备份

ben-bot 运行机：

- 机器：`ubuntu@52.79.252.255`
- 仓库路径：`/opt/telegram/18game_devops`

远程备份目录：

```text
/opt/telegram/18game_devops/.codex-backup/benbot-roster-mention-20260807213544
```

已备份 `duty_status.py` 原文件后精确同步新版本；ben-bot 容器已重建并启动。

## 验证清单

| 项目 | 结果 |
| --- | --- |
| 本地 `py_compile` / `git diff --check` | 通过 |
| `early_remind` / `early_start` / `handoff_remind` / `handoff_start` 含 @ 排班知会 | 通过 |
| `handoff_end` / `early_end_after` / `late_end` / `late_end_after` 不重复 @ | 通过 |
| 提醒消息仍含本月出勤统计 | 通过 |
| 容器内断言 | 通过 |
| 容器日志：9 个值班任务注册，启动通知成功 9 失败 0 | 通过 |
| 值班通知仅 `18GAME_ 上线群（正式環境）` | 通过 |

## 结论

- 周末值班排班知会类通知会自动 @ HR `@Mollyprojectx8` 与 SSC 行政 `@Yi_nuo_11`，方便她们了解排班信息。
- 值班信息仍只通知 `18GAME_ 上线群（正式環境）`。

## 后续注意

- 需确认 `@Mollyprojectx8`、`@Yi_nuo_11` 是本群成员，@ 才能触达；若不在群内需要先拉入群。
- 如需在其他事件也 @ 或新增知会对象，维护 `duty_status.py` 的 `ROSTER_NOTIFY_MENTIONS` 与 `ROSTER_MENTION_EVENTS` 即可。
