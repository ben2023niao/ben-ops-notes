---
id: "doc-918cfff89533"
title: "【运维记录】运维组新增成员 @fyb99：值班表排班 + 各类通知 @ 名单更新"
date: "2026-10-10T13:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "Nginx", "监控告警", "自动化", "DNS"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-10_1330-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E8%BF%90%E7%BB%B4%E7%BB%84%E6%96%B0%E5%A2%9E%E6%88%90%E5%91%98fyb99-%E5%80%BC%E7%8F%AD%E8%A1%A8%E4%B8%8E%E9%80%9A%E7%9F%A5%E5%90%8D%E5%8D%95%E6%9B%B4%E6%96%B0.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-10_1330-【运维记录】运维组新增成员fyb99-值班表与通知名单更新.md"
sourceSha256: "2e817a3866495f2c6138d91592c2de4208cd95a77f3e819df24f9454bf9eca3f"
sourceSystem: "project-doc"
---

# 【运维记录】运维组新增成员 @fyb99：值班表排班 + 各类通知 @ 名单更新

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610101330-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E8%BF%90%E7%BB%B4%E7%BB%84%E6%96%B0%E5%A2%9E%E6%88%90%E5%91%98%20%40fyb99%EF%BC%9A%E5%80%BC%E7%8F%AD%E8%A1%A8%E6%8E%92%E7%8F%AD%20%2B%20%E5%90%84%E7%B1%BB%E9%80%9A%E7%9F%A5%20%40%20%E5%90%8D%E5%8D%95%E6%9B%B4%E6%96%B0.md)

> 整理日期：2026-10-10 13:30｜日期依据：文件名日期

- 日期：2026-10-10 13:30（北京）
- 需求：运维组加新人 @fyb99；值班表增加其排班（14:00-22:00、大小周）；分组分到 Jett + Melo 的一组；各类通知的 @ 名单都加上 @fyb99
- 范围：ben-bot 值班表与通知、线上/测试环境运维脚本、CICD 通知名单

## 一、值班表改动

### 1.1 分组（`weekend_duty.json` / `duty_status.py` 默认配置）

```json
"group1": {"name": "一组", "members": ["@jett_yunwei", "@melo_sre", "@fyb99"],
           "shift": "early", "desc": "Jett + Melo + fyb99"}
```

- 一组沿用**早班 14:00-22:00**（与需求一致：下午 2 点到晚上 10 点）
- 大小周规则不变：大周周六一组、周日二组；小周仅周日一组（轮换）
- 二组（Kermit + Davie，晚班 17:00-01:00）不变

### 1.2 ben-bot 成员常量（`duty_schedule.py`）

```text
NEW_MEMBERS += "@fyb99"           # 新员工归类
SHORT_NAMES["@fyb99"] = "fyb99"
BUTTON_CODES["@fyb99"] = "F"      # 值班面板按钮位
```

### 1.3 实测排班结果（本地与容器内一致）

```text
2026-10-17 周六 组=group1 值班=['@jett_yunwei', '@melo_sre', '@fyb99']
2026-10-18 周日 组=group2 值班=['@Kermit0824', '@Daviea2']
2026-10-25 周日 组=group1 值班=['@jett_yunwei', '@melo_sre', '@fyb99']
```

## 二、通知 @ 名单改动

统一在 `@jett_yunwei` 之后插入 `@fyb99`（幂等，已在名单里的不会重复加）：

```text
旧： @Ben_Bird @jett_yunwei @Kermit0824 @melo_sre @Daviea2
新： @Ben_Bird @jett_yunwei @fyb99 @Kermit0824 @melo_sre @Daviea2
```

| 仓库 | 文件 |
| --- | --- |
| 18game_devops | ben-bot `app/benbot/constants.py`（OPS_USERNAMES 权限名单） |
| 18game_devops | `devops/php/public/dns_check.php`、`devops/php/public/boce_check_api.php` |
| 18game_devops | `devops/python/s3-manager-app-apk/{s3-manager-18gane-prod,18gane-test,xcp-prod}/app.py` |
| docker-youdianse-php | `ops/production/scripts/`：server-health-alert、health-hourly-summary、nginx-gateway-alert、app-log-hourly-rotate、gateway-cert-alert、disk-auto-clean |
| docker-youdianse-php | `ops/test/scripts/`：server-health-alert、health-hourly-summary |
| docker-youdianse-php | `cicd-web/config/settings.json`（`ops_mentions`） |

共修改 **18 个文件**（18game_devops 9 个、docker-youdianse-php 9 个）。

> 未改动项：`cicd-web/config/settings.json` 的 `publish.operators`（发布权限名单）——
> 这属于**权限授予**而非通知，需 Ben 确认后再加（最小权限原则）。另
> `文档与联系人/文档日常发布监控/.benbot.json` 是 UI 提示文案（"优先找 @jett_yunwei"），非通知名单，暂不改。

## 三、下发与生效

| 位置 | 动作 | 生效方式 |
| --- | --- | --- |
| 监控机 52.79.252.255 | 9 个文件单文件同步（备份 `/root/duty-update-20261010-132032/`）；php 应用副本 2 个文件（备份 `/root/php-app-update-20261010-052040/`） | 文件即时生效 |
| 监控机 ben-bot | 重建并重启机器人（`build_and_run_ben_bot.sh`） | app 层改动需重建镜像才生效（启动通知已发 7 个群） |
| 线上后端 16.209.16.108 | 7 个文件单文件同步（备份 `/root/duty-update-20261010-132040/`） | 脚本即时生效；CICD 重启后加载新名单 |
| 线上后端 CICD | `systemctl restart cicd-web` | 已 active，18090 → 200 |
| 测试环境 15.152.247.196 | 3 个文件就地替换（备份 `/tmp/*.bak-20261010-052226`） | 脚本即时生效 |
| 测试环境 CICD | `./cicd-web.sh restart` | 启动成功，18090 → 200 |

## 四、验证

```text
· JSON / Python / PHP 语法：本地与线上校验全部通过（php -l 在 php-server 容器内执行）
· 值班表：本地 module 与容器内 JSON 均为 一组=['@jett_yunwei','@melo_sre','@fyb99']，早班 14:00-22:00
· 权限名单：容器内 constants.OPS_USERNAMES 已含 fyb99
· 部署副本：监控机 10 个文件、后端 7 个文件、测试机 3 个文件均已含 @fyb99
· 服务健康：ben-bot 容器 Up；CICD（线上/测试）18090 均 200
```

## 五、回滚

```bash
# 监控机（9 个文件 + php 2 个）
sudo cp -a /root/duty-update-20261010-132032/f<i>.orig     <对应目标>   # 或按需逐个还原
sudo cp -a /root/php-app-update-20261010-052040/<文件>.orig /opt/18game_devops/devops/php/public/<文件>
# 线上后端（7 个文件）
sudo cp -a /root/duty-update-20261010-132040/<文件>.orig   /opt/docker-youdianse-php/<相对路径>
sudo systemctl restart cicd-web
# 测试环境（3 个文件）
sudo cp -a /tmp/<文件>.bak-20261010-052226 <对应目标>
cd /opt/docker-youdianse-php && sudo ./cicd-web.sh restart
# ben-bot：还原仓库文件后重新执行 build_and_run_ben_bot.sh
```

## 六、待确认

1. 是否给 @fyb99 开通**发布权限**（`cicd-web/config/settings.json` 的 `publish.operators` 增加 `运维-@fyb99`）——属权限变更，等确认
2. 一组现在 3 人（Jett/Melo/fyb99），周末值班会显示 3 人；如需改为「组内轮换 2 人」，说一声即可调整

## 七、补充修复：月历排班漏显示 fyb99（2026-10-10 追加）

### 7.1 现象

用户反馈机器人输出的「加班 · 周末值班」里，一组仍只显示 `Jett、Melo`（10-02/10-04/10-06 国庆、10-17/10-25/10-31 周末），
而补班出勤那行已经带上了 fyb99。

### 7.2 根因

排班取人只取组内**前两位**，第三人被丢弃：

```python
# 修复前（duty_schedule.py:252 / duty_status.py:179）
early = [members[0]] if members else []
late = [members[1]] if len(members) > 1 else []
```

一处修好不够，**两个文件都有这段**：`data/scripts/运维值班表/duty_schedule.py`（月历/周排班渲染）
与 `app/benbot/duty_status.py`（值班状态通知）。本次两处一起改。

### 7.3 修复规则

```python
# 组内第 1、3… 位走早班（14:00-22:00）；第 2、4… 位走晚班（17:00-01:00）
early = members[0::2]
late = members[1::2]
```

对当前数据的结果：一组 = Jett（早）+ Melo（晚）+ **fyb99（早，14:00-22:00，与需求一致）**；二组不变。

### 7.4 修复后实测（本地与容器内一致）

```text
10-02 星期五（节日·国庆节）：一组 Jett、fyb99、Melo、Ben（14:00-22:00｜2倍日薪）
10-04 星期日（节日·国庆节）：一组 Jett、fyb99、Melo、Ben（14:00-22:00｜1:1 调休）
10-06 星期二（节日·国庆节）：一组 Jett、fyb99、Melo、Ben（14:00-22:00｜1:1 调休）
10-17 星期六（大周）：一组 Jett、fyb99、Melo（14:00-22:00 / 17:00-01:00）
10-25 星期日（小周）：一组 Jett、fyb99、Melo（14:00-22:00 / 17:00-01:00）
10-31 星期六（大周）：一组 Jett、fyb99、Melo（14:00-22:00 / 17:00-01:00）
10-10 星期六：补班出勤（Ben、Jett、Kermit、Melo、Davie、fyb99）
11-01 星期日（大周）：二组 Kermit、Davie
```

### 7.5 下发与回滚

```text
· 监控机：duty_schedule.py / duty_status.py 已同步（备份 /root/duty-fix-20261010-053412/）
· ben-bot：已重建重启（app 层改动需重建），容器内复测排班正确
· 回滚：还原上述备份后重跑 build_and_run_ben_bot.sh
```
