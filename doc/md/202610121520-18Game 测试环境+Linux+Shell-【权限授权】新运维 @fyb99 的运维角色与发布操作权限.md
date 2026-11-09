---
id: "doc-a0dfa1df006b"
title: "【权限授权】新运维 @fyb99 的运维角色与发布操作权限"
date: "2026-10-12T15:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "自动化", "安全运维", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-12_1520-%E3%80%90%E6%9D%83%E9%99%90%E6%8E%88%E6%9D%83%E3%80%91%E6%96%B0%E8%BF%90%E7%BB%B4fyb99%E5%8F%91%E5%B8%83%E4%B8%8E%E8%BF%90%E7%BB%B4%E8%A7%92%E8%89%B2%E6%9D%83%E9%99%90.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-12_1520-【权限授权】新运维fyb99发布与运维角色权限.md"
sourceSha256: "9e0e30c6cc3a6f763391a92cf6c61166ae771accd0e96e5bb31184ae10cb54b6"
sourceSystem: "project-doc"
---

# 【权限授权】新运维 @fyb99 的运维角色与发布操作权限

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610121520-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-%E3%80%90%E6%9D%83%E9%99%90%E6%8E%88%E6%9D%83%E3%80%91%E6%96%B0%E8%BF%90%E7%BB%B4%20%40fyb99%20%E7%9A%84%E8%BF%90%E7%BB%B4%E8%A7%92%E8%89%B2%E4%B8%8E%E5%8F%91%E5%B8%83%E6%93%8D%E4%BD%9C%E6%9D%83%E9%99%90.md)

> 整理日期：2026-10-12 15:20｜日期依据：文件名日期

- 日期：2026-10-12 15:20（北京）
- 需求：给新运维 @fyb99 加上**发布操作权限**（分配到**运维角色**）
- 结论：机器人（ben-bot）侧**上一轮已生效**（本轮复核），CICD 发布操作人名单本轮补齐

## 一、权限模型（两处，缺一不可）

| 位置 | 作用 | 名单来源 |
| --- | --- | --- |
| ben-bot（Telegram 机器人） | 决定角色：ops 角色 = 全部权限（各发布入口、`/sh`、上传下载、脱敏配置查看等） | `devops/python/ben-bot/app/benbot/constants.py` 的 `OPS_USERNAMES`；`permissions.py::get_user_role()` 按用户名匹配 |
| CICD Web（发布页） | 决定发布时可选/可归属的「操作人」（发布 UI 下拉与归属记录） | `cicd-web/config/settings.json` → `publish.operators` |

> 说明：CICD Web 的实际门禁是**发布口令**；`publish.operators` 是操作人名单（谁可以以自己名义发起发布、发布记录归属谁）。

## 二、变更内容

```text
1) ben-bot 角色（18game_devops，2026-10-10 已提交并重建生效）
   constants.py → OPS_USERNAMES 增加 "fyb99"
2) CICD 发布操作人（docker-youdianse-php，本轮新增）
   cicd-web/config/settings.json → publish.operators 增加 "运维-@fyb99"
   生产 16.209.16.108：operators 11 → 12 人
   测试 15.152.247.196：operators 11 → 12 人
```

## 三、部署与生效

| 位置 | 动作 | 生效方式 |
| --- | --- | --- |
| 生产后端 16.209.16.108 | 覆盖 `cicd-web/config/settings.json` | `systemctl restart cicd-web`（已 active，18090 → 200） |
| 测试环境 15.152.247.196 | 就地更新同名文件 | `./cicd-web.sh restart`（已成功，18090 → 200） |
| ben-bot 52.79.252.255 | 上一轮已重建镜像 | 本轮复核容器内角色 |

备份：

```text
· 生产：/root/cicd-settings.bak.20261012-151920.json
· 测试：/tmp/cicd-settings.bak.20261012-071932.json
```

## 四、验证

```text
1) 机器人侧（容器内实测）：
     get_user_role(username="fyb99") → ops
     get_role_capability_text("ops") → 全部权限。
     "fyb99" in OPS_USERS → True
2) 生产 CICD：
     operators 含 fyb99 = True，共 12 人
     venv 内加载校验：config.PUBLISH_OPERATOR_OPTIONS → ['运维-@fyb99']
     服务：active，18090 → 200
3) 测试 CICD：operators 共 12 人（第 6 位为 运维-@fyb99），服务重启成功，18090 → 200
4) 仓库文件：docker-youdianse-php/cicd-web/config/settings.json 已含 运维-@fyb99（JSON 校验通过）
```

## 五、回滚

```bash
# 生产
sudo cp -a /root/cicd-settings.bak.20261012-151920.json /opt/docker-youdianse-php/cicd-web/config/settings.json
sudo systemctl restart cicd-web
# 测试
sudo cp -a /tmp/cicd-settings.bak.20261012-071932.json /opt/docker-youdianse-php/cicd-web/config/settings.json
cd /opt/docker-youdianse-php && sudo ./cicd-web.sh restart
# 机器人角色（如需撤销）
#   constants.py 的 OPS_USERNAMES 去掉 "fyb99" 后重跑 build_and_run_ben_bot.sh
```

## 六、待确认（其它系统是否也要开权限）

以下系统与「发布/运维角色」相关，但**不在本次改动范围**，如需要请明确：

```text
· Spug 定时任务平台账号（生产 16.208.32.40 / 测试 15.152.160.250）
· 宝塔面板账号（16.208.5.147）
· AWS 控制台 / IAM 账号
· 服务器 SSH 账号（如需直连，建议走跳板机而非单独发密钥）
```
