---
id: "doc-6ac8dcd290a7"
title: "运维值班表仅周末显示通知与值班通知收口上线群"
date: "2026-08-07T21:12:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Python", "自动化", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-07_2112-%E3%80%90%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E8%BF%90%E7%BB%B4%E5%80%BC%E7%8F%AD%E8%A1%A8%E4%BB%85%E5%91%A8%E6%9C%AB%E6%98%BE%E7%A4%BA%E9%80%9A%E7%9F%A5%E4%B8%8E%E5%80%BC%E7%8F%AD%E9%80%9A%E7%9F%A5%E6%94%B6%E5%8F%A3%E4%B8%8A%E7%BA%BF%E7%BE%A4.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-07_2112-【优化+运维记录】运维值班表仅周末显示通知与值班通知收口上线群.md"
sourceSha256: "cb58b4cbb05163c1c72acaf4fa9fccc388d6086cd8d946dbb210ad4d2bfdd427"
sourceSystem: "project-doc"
---

# 运维值班表仅周末显示通知与值班通知收口上线群

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-07_2112-【优化+运维记录】运维值班表仅周末显示通知与值班通知收口上线群.md`

> 整理日期：2026-08-07 21:12｜日期依据：文件名日期

环境标签：通用 / ben-bot / 运维值班表 / 通知收口

时间：2026-08-07 21:12（Asia/Manila）

## 任务来源

用户要求：

- 读取 `doc` 历史文档，使用 `workbench`。
- 每步操作都发群通知。
- 运维值班表只显示和通知星期六、星期天的班次；换班通知只在周末通知。
- 工作日（星期一至星期五）全员上班；周末有值班的人员可安排调休。
- 已确认 2026-08-08（星期六）：`@melo_sre` + `@jett_yunwei`；2026-08-09（星期天）：`@Daviea2` + `@Kermit0824`。
- 运维值班相关信息统一只通知 `18GAME_ 上线群（正式環境）`。
- 操作完成后先验证，再汇总文档，并把汇总和文档发群里。
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

- `devops/python/ben-bot/doc/2026-07-11_1503-【优化+运维记录】运维值班动态通知与进度面板.md`
- `devops/python/ben-bot/doc/2026-07-14_1503-【运维记录】新运维联系方式与发布权限更新.md`

## 群通知

按用户最新要求，运维值班相关信息统一只通知：

- `18GAME_ 上线群（正式環境）`（`-1003762262155`）

已通知步骤（全部发送到该群）：

1. 恢复上下文并确认任务范围（含通知收口到上线群）。
2. 值班配置与代码修改完成。
3. 本地静态验证通过。
4. 运行机同步、备份、容器重建完成。
5. 容器内验证通过。

通知内容未包含密码、token、Secret Key、私钥正文、Session Cookie、完整 Signed URL、数据库连接串或 `.env` 原文。

## 需求与实现

### 1. 只显示和通知星期六、星期天班次

- 值班面板（`duty_status.py`）：
  - 工作日（星期一至星期五）：显示“工作日 · 全员上班”，并预告本周末值班安排，不显示早/晚班进度。
  - 星期六、星期天：显示当天 2 人值班，早班/晚班各 1 人，带实时进度、剩余时间和调休说明。
- 换班事件通知：
  - `early_start` / `handoff_start` / `handoff_end` / `late_end` 只在星期六、星期天触发。
  - 星期天 01:00 的晚班下班事件（归属星期六值班）正常发送；星期一 01:00（归属星期天值班）正常发送；其余工作日事件全部跳过。
- 排班数据（`duty_schedule.py`）：
  - 工作日全员上班；周末按 `weekend_duty.json` 显示两人值班。
  - 图例、规则、提醒文案同步更新为“工作日全员上班 / 周末两人值班（可调休）”。

### 2. 周末值班可安排调休

- `weekend_duty.json` 说明文案：周末值班两人覆盖全天，一人早班打卡、一人晚班打卡；周末值班人员可安排调休，以群内当周确认的实际排班为准。
- 面板和排班规则均展示该说明。

### 3. 值班通知收口到上线群

- 新增 `DUTY_NOTIFY_CHAT_IDS = ("-1003762262155",)`（`duty_status.py`）。
- `main.py` 值班事件广播目标从“启动通知群 + 已知聊天”改为只发送到 `DUTY_NOTIFY_CHAT_IDS`，即 `18GAME_ 上线群（正式環境）`。

## 变更文件

- `devops/python/ben-bot/data/scripts/运维值班表/weekend_duty.json`（新增）：周末班次时段、默认周六/周日人员、按日排班（含 2026-08-08、2026-08-09）。
- `devops/python/ben-bot/app/benbot/duty_status.py`：值班面板、事件文案、事件开关、通知目标。
- `devops/python/ben-bot/app/benbot/main.py`：值班事件只通知上线群；跳过日志文案更新。
- `devops/python/ben-bot/data/scripts/运维值班表/duty_schedule.py`：排班数据与规则/图例/提醒。

## 同步与备份

ben-bot 运行机：

- 机器：`ubuntu@52.79.252.255`
- 仓库路径：`/opt/telegram/18game_devops`
- bot 目录：`/opt/telegram/18game_devops/devops/python/ben-bot`

远程备份目录：

```text
/opt/telegram/18game_devops/.codex-backup/benbot-weekend-duty-20260807211121
```

已备份 `duty_status.py`、`main.py`、`duty_schedule.py` 原文件后精确同步新文件与 `weekend_duty.json`，未覆盖现场无关修改。ben-bot 容器已重建并启动。

## 验证清单

| 项目 | 结果 |
| --- | --- |
| 本地 `py_compile` / JSON / `git diff --check` | 通过 |
| 事件开关：周五 False、周六/周日 True、周一 False | 通过 |
| 事件开关：周一 01:00（周日晚班结束）True | 通过 |
| 工作日面板：工作日全员上班 + 本周末值班预告 | 通过 |
| 周六面板：Melo / Jett（早班/晚班 + 调休说明） | 通过 |
| 周日面板：Davie / Kermit | 通过 |
| 事件文案按实际值班人动态生成 | 通过 |
| `DUTY_NOTIFY_CHAT_IDS` 仅上线群 `-1003762262155` | 通过 |
| 排班 JSON：8/8 `[Melo, Jett]`、8/9 `[Davie, Kermit]`、工作日全员 | 通过 |
| 容器内 `py_compile` / 断言 | 通过 |
| 容器日志：5 个值班任务注册（early/handoff/late/live_refresh） | 通过 |
| 启动通知成功 9 失败 0 | 通过 |

## 结论

- 运维值班表现在只显示和通知星期六、星期天班次；工作日只显示“全员上班”和周末预告。
- 换班通知只在周末发送。
- 周末值班人员可安排调休，文案已展示。
- 8/8（周六）Melo + Jett、8/9（周日）Davie + Kermit 已写入排班配置。
- 运维值班相关信息已收口：只通知 `18GAME_ 上线群（正式環境）`。

## 后续注意

- 每周周末排班在 `data/scripts/运维值班表/weekend_duty.json` 的 `by_date` 维护；未配置日期时使用 `default_saturday` / `default_sunday`。
- 早/晚班时段目前沿用 14:00-22:00 / 17:00-01:00，可在 `weekend_duty.json` 的 `shift` 调整；如团队确认“早上打卡”的具体时间，直接改配置即可。
- 值班事件通知目标固定为 `DUTY_NOTIFY_CHAT_IDS`（上线群）；如后续调整，需同步更新 `workbench/NOTIFICATION_TARGETS.md`。
