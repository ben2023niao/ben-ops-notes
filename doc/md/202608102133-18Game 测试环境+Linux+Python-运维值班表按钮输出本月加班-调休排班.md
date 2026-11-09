---
id: "doc-b491647dcba2"
title: "运维值班表按钮输出本月加班/调休排班"
date: "2026-08-10T21:33:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Python", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-10_2133-%E3%80%90%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E8%BF%90%E7%BB%B4%E5%80%BC%E7%8F%AD%E8%A1%A8%E6%8C%89%E9%92%AE%E8%BE%93%E5%87%BA%E6%9C%AC%E6%9C%88%E5%8A%A0%E7%8F%AD%E8%B0%83%E4%BC%91%E6%8E%92%E7%8F%AD.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-10_2133-【优化+运维记录】运维值班表按钮输出本月加班调休排班.md"
sourceSha256: "d093c3119039aab4d6470b4b3c071f41731d3a0e41615ff572177810e32a7c7d"
sourceSystem: "project-doc"
---

# 运维值班表按钮输出本月加班/调休排班

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608102133-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BPython-%E8%BF%90%E7%BB%B4%E5%80%BC%E7%8F%AD%E8%A1%A8%E6%8C%89%E9%92%AE%E8%BE%93%E5%87%BA%E6%9C%AC%E6%9C%88%E5%8A%A0%E7%8F%AD-%E8%B0%83%E4%BC%91%E6%8E%92%E7%8F%AD.md)

> 整理日期：2026-08-10 21:33｜日期依据：文件名日期

环境标签：通用 / ben-bot / 运维值班表 / 按钮输出

时间：2026-08-10 21:33（Asia/Manila）

## 任务来源

用户要求：

- 读取 `doc` 历史文档，使用 `workbench`，每步操作都发群通知。
- `/start` 点击“运维值班表”按钮后，输出本月完整的每天值班排班表。
- 补充要求：正常上班不输出，只输出调休和加班（周末值班）两类。
- 操作完成后先验证，再汇总文档，并把汇总和文档发群里（值班信息只发 `18GAME_ 上线群（正式環境）`）。
- 最后合并提交本地代码。

## 本轮读取依据

- `AGENTS.md`、`workbench/`、`devops/ai_context/servers.yml`
- 历史值班文档：`2026-08-10_2123-【优化+运维记录】运维值班表大小周分组排班与本月值班表.md`、`2026-08-07_2136-【优化+运维记录】周末值班排班知会@HR与SSC行政.md`

## 实现内容

### `duty_schedule.py`

新增 `build_month_roster(target)`，只输出两类：

- 加班（周末值班）：本月每个值班日，含日期、星期、大小周、值班组、人员与班次时段。
- 调休：本月每个调休日，含日期、星期与人员。

`build_payload()` 增加 `month_roster` 输出。

### `benbot_plugin.py`

- 点击 `/start` 菜单“运维值班表”按钮后，渲染为“本月加班 / 调休排班”完整列表。
- 正常上班日（周一至周五）不输出。
- 不再注册实时进度刷新，避免 60 秒面板覆盖排班表。

## 输出示例（2026 年 08 月）

```text
🖥 运维值班表 · 2026 年 08 月
📆 本月加班 / 调休排班

🧧 加班 · 周末值班
08-02 星期日（小周）：二组 Kermit、Davie（14:00-22:00 / 17:00-01:00）
08-08 星期六（大周）：一组 Jett、Melo（14:00-22:00 / 17:00-01:00）
08-09 星期日（大周）：二组 Kermit、Davie（14:00-22:00 / 17:00-01:00）
08-16 星期日（小周）：一组 Jett、Melo（14:00-22:00 / 17:00-01:00）
08-22 星期六（大周）：一组 Jett、Melo（14:00-22:00 / 17:00-01:00）
08-23 星期日（大周）：二组 Kermit、Davie（14:00-22:00 / 17:00-01:00）
08-30 星期日（小周）：二组 Kermit、Davie（14:00-22:00 / 17:00-01:00）

🌴 调休
08-11（星期二）：Davie
08-12（星期三）：Kermit
08-13（星期四）：Melo
08-14（星期五）：Jett

📋 周一至周五正常上班；周末值班每 1 天产生 1 天调休；实际排班以群内每周确认为准。
```

## 同步与备份

ben-bot 运行机：`ubuntu@52.79.252.255`，仓库 `/opt/telegram/18game_devops`。

远程备份目录：

```text
/opt/telegram/18game_devops/.codex-backup/benbot-month-roster-20260810213200
```

已备份 `duty_schedule.py`、`benbot_plugin.py` 原文件后精确同步新版本；ben-bot 容器已重建并启动。

## 验证清单

| 项目 | 结果 |
| --- | --- |
| 本地 `py_compile` / JSON / `git diff --check` | 通过 |
| payload 加班 7 条、调休 4 条 | 通过 |
| 正常上班日不输出 | 通过 |
| 容器内真实插件 `_build_schedule_message` 输出校验 | 通过 |
| 容器日志：9 个值班任务注册，启动通知成功 10 失败 0 | 通过 |
| 值班信息仅 `18GAME_ 上线群（正式環境）` | 通过 |

## 结论

- `/start` 点击“运维值班表”按钮后输出本月完整“加班 / 调休”排班表。
- 正常上班日不输出，只输出周末值班（加班）与调休，便于快速查看本月安排。

## 后续注意

- 排班调整维护 `weekend_duty.json` 的 `by_date` 与 `rest_by_date`；按钮输出自动刷新。
- 实时进度面板不再覆盖排班表消息；值班事件通知与出勤统计保持原逻辑。
