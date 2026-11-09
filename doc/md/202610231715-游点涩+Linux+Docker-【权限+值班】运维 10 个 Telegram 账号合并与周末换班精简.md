---
id: "doc-d637ed33e2d3"
title: "【权限+值班】运维 10 个 Telegram 账号合并与周末换班精简"
date: "2026-10-23T17:15:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Docker", "监控告警", "自动化", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-23-1715-%E3%80%90%E6%9D%83%E9%99%90%2B%E5%80%BC%E7%8F%AD%E3%80%91%E8%BF%90%E7%BB%B4%E5%8D%81%E8%B4%A6%E5%8F%B7%E5%90%88%E5%B9%B6%E4%B8%8E%E5%91%A8%E6%9C%AB%E6%8D%A2%E7%8F%AD%E7%B2%BE%E7%AE%80.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-23-1715-【权限+值班】运维十账号合并与周末换班精简.md"
sourceSha256: "8e04b66cf8cea056243dfaa186a16f004841f8f414d7b04d9c5101d9334a9407"
sourceSystem: "project-doc"
---

# 【权限+值班】运维 10 个 Telegram 账号合并与周末换班精简

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610231715-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BDocker-%E3%80%90%E6%9D%83%E9%99%90%2B%E5%80%BC%E7%8F%AD%E3%80%91%E8%BF%90%E7%BB%B4%2010%20%E4%B8%AA%20Telegram%20%E8%B4%A6%E5%8F%B7%E5%90%88%E5%B9%B6%E4%B8%8E%E5%91%A8%E6%9C%AB%E6%8D%A2%E7%8F%AD%E7%B2%BE%E7%AE%80.md)

> 整理日期：2026-10-23 17:15｜日期依据：文件名日期

- 时间：2026-10-23 17:15（Asia/Manila）
- 环境：游点涩线上环境
- 范围：ben-bot 运维权限、CICD 发布操作人、运维通知 @ 名单、周末值班
- 运行版本：`ben-bot v1.0.4`

## 一、账号归组

| 人员 | Telegram 账号 |
| --- | --- |
| Ben（组长） | `@Ben_Bird`、`@Ben36812` |
| Kermit | `@Kermit0824`、`@kermitt8773` |
| Jett | `@jett_yunwei` |
| Vesper | `@Vesper0020`、`@Vesper688` |
| Melo | `@melo_sre`、`@melomeloo1009` |
| fyb99 | `@fyb99` |

以上 10 个账号全部加入：

1. ben-bot 的 `OPS_USERNAMES`，角色统一为 `ops`；
2. CICD 发布操作人；
3. CICD、生产告警、测试告警及仓库规则中的 @ 运维名单。

## 二、值班模型

值班按“人”展示和统计，同一人的多个 Telegram 账号保存在同一条成员记录中：

- 一组：Jett / Melo / fyb99
- 二组：Kermit / Vesper
- Ben：组长
- 早班：14:00–22:00
- 晚班：17:00–01:00
- 组内成员按顺序拆分早、晚班，账号只用于通知，不重复计算人员。

大小周规则：

- 大周：周六一组、周日二组；
- 小周：周六无值班，周日按两组轮换；
- 以 2026-10-19 所在小周为锚点自动交替。

## 三、通知规则

### 重启通知

- 启动通知只显示“ben-bot 已启动”；
- 不再拼接值班面板、在岗进度、整周排班或出勤统计；
- 不再启动每分钟刷新值班消息的循环任务。

### 周末换班

只在周末 `17:00` 晚班接班时发送一次：

```text
🔁 周末换班 · 10-25 周日
小周 · 一组
早班 14:00-22:00：Jett、fyb99
晚班 17:00-01:00：Melo
@jett_yunwei @fyb99 @melo_sre @melomeloo1009
```

- 工作日不发送；
- 小周周六没有值班组时也不发送；
- 换班消息末尾 @ 全部 10 个运维账号；
- 发送目标：`18GAME_ 上线群（正式環境）` 和 `18game运维` 两个群。

## 四、代码与配置

### ben-bot

- `app/benbot/constants.py`
  - `BOT_VERSION = v1.0.4`
  - 4 个账号扩展为 10 个 ops 账号
- `app/benbot/duty_status.py`
  - 精简周末值班模型
  - 仅保留 `weekend_handoff` 事件
  - 同一成员合并多个 Telegram 账号
- `app/benbot/main.py`
  - 启动消息移除值班面板
  - 定时任务只注册周末 17:00 换班
  - 移除每分钟值班消息刷新
- `data/scripts/运维值班表/weekend_duty.json`
  - 6 人、10 账号、两个组、早/晚班
- `data/scripts/运维值班表/duty_schedule.py`
  - 输出精简的周末排班 JSON/文本
- `data/scripts/运维值班表/benbot_plugin.py`
  - 按钮展示同一人的多个账号

### CICD

- `cicd-web/config/settings.json`
  - `publish.operators` 增加全部 10 个运维账号
  - `telegram.ops_mentions` 更新为全部 10 个账号
- 生产、测试 CICD 均已同步并重启，HTTP 200。

### 服务器告警

以下实际运行文件已同步 10 个账号：

- 生产后端：
  - `/etc/youdianse-health-alert.json`
  - `/usr/local/sbin/youdianse-server-health-alert.py`
  - `/usr/local/sbin/youdianse-health-hourly-summary.py`
- 宝塔：
  - `/etc/youdianse-health-alert.json`
  - `/usr/local/sbin/youdianse-server-health-alert.py`
- 测试后端：
  - `/etc/youdianse-health-alert.json`
  - `/usr/local/sbin/youdianse-server-health-alert.py`
  - `/usr/local/sbin/youdianse-health-hourly-summary.py`

## 五、验证结果

1. ben-bot 容器 `ben-bot` 正常运行，版本 `v1.0.4`。
2. 10 个账号逐一执行角色判断，结果全部为 `ops`。
3. 2026-10-25 小周：周六无值班，周日一组早 Jett/fyb99、晚 Melo。
4. 2026-10-31 大周：周六一组；2026-11-01 周日二组。
5. 工作日 17:00 不发送；周末 17:00 才发送。
6. 换班消息约 212 字符，无进度条、无出勤统计。
7. 启动消息实测只有：

```text
🤖 ben-bot 已启动
```

8. 启动日志确认只注册：

```text
值班事件定时通知已注册 events=weekend_handoff
```

9. `tests/test_duty_compact.py` 4 项回归测试通过：
   - 10 个账号权限完整；
   - 小周周日一组；
   - 大周周六一组、周日二组；
   - 启动消息不含值班面板。

## 六、回滚

运行机文件在替换前保留 `.bak.20261023-091245` /
`.bak.20261023-091254` 备份；CICD 与告警配置在更新前均保留
`.bak.20261023-*` 备份。恢复时先停止 ben-bot，还原对应文件，再重建容器。

## 七、安全说明

本文不记录 Telegram Bot Token、CICD 发布口令、SSH 凭据或任何私钥。

## 八、Git 提交

| 仓库 | 提交 | 内容 |
| --- | --- | --- |
| `18game_devops` | `2dc756b` | ben-bot 十账号权限、值班模型、启动通知、周末换班与测试 |
| `docker-youdianse-php` | `1a1b175` | CICD 操作人、所有生效通知模板与本文档 |

## 九、通知记录

| 步骤 | 内容 | 线上群 | 18game 群 |
| --- | --- | --- | --- |
| 1 | 账号归组与本地验证完成 | 13775 | 120487 |
| 2 | ben-bot、CICD、监控配置上线 | 13777 | 120531 |
| 3 | 首版汇总文档 | 13778 | 120533 |
| 4 | 最终版文档 | 13782 | 120568 |
