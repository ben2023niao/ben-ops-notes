---
id: "doc-a1004ae1364a"
title: "线上前置 H5/PC 发版按钮授权前端组"
date: "2026-08-07T20:56:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Python", "自动化", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-07_2056-%E3%80%90%E6%9D%83%E9%99%90%E6%8E%88%E6%9D%83%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E5%89%8D%E7%BD%AEH5-PC%E5%8F%91%E7%89%88%E6%8C%89%E9%92%AE%E6%8E%88%E6%9D%83%E5%89%8D%E7%AB%AF%E7%BB%84.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-07_2056-【权限授权+运维记录】线上前置H5-PC发版按钮授权前端组.md"
sourceSha256: "2f8ec52f23aedd9d472ac5566cf283eeb9b005714f0631c0de1e909974e697ec"
sourceSystem: "project-doc"
---

# 线上前置 H5/PC 发版按钮授权前端组

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-07_2056-【权限授权+运维记录】线上前置H5-PC发版按钮授权前端组.md`

> 整理日期：2026-08-07 20:56｜日期依据：文件名日期

环境标签：通用 / ben-bot / 权限 / 前端 / 线上前置 / 游点涩

时间：2026-08-07 20:56（Asia/Manila）

## 任务来源

用户要求：

- 读取 `doc` 历史文档，使用 `workbench`。
- 每步操作都发群通知。
- 把 `线上前置-游点涩-h5-发版`、`线上前置-游点涩-pc-发版` 两个发布按钮权限授权给前端组。
- 新增前端成员 `@kimtomf77`。
- 操作完成后先验证，再汇总文档，并把汇总和文档发群里。
- 最后合并提交本地代码。

说明：线上前置前端对接线上后台接口，是不对外的前端入口，用于前端开发发布测试使用。

## 本轮读取依据

按 workbench 入口读取：

- `AGENTS.md`
- `workbench/START_HERE.md`
- `workbench/ACTIVE_TASKS.md`
- `workbench/PROJECT_INDEX.md`
- `workbench/MACHINE_ACCESS_MATRIX.md`
- `workbench/PROJECT_RUNTIME_CHAINS.md`
- `workbench/NOTIFICATION_TARGETS.md`
- `workbench/projects/18game_devops/CURRENT_STATE.md`
- `workbench/projects/18game_devops/CURRENT_TASK.md`
- `devops/ai_context/servers.yml`

重点参考历史文档：

- `devops/python/ben-bot/doc/2026-07-31_1430-【优化+运维记录】ben-bot运维权限确认与重启记录.md`
- `devops/python/ben-bot/doc/2026-07-14_1503-【运维记录】新运维联系方式与发布权限更新.md`
- `devops/python/ben-bot/doc/2026-08-06_1952-【配置部署+机器人优化】yiyi0620证书与ben-bot前端发版展示收尾.md`

## 群通知

本轮每个明确步骤均已发送到：

- `18game运维`（`-4929911895`）
- `18GAME_ 上线群（正式環境）`（`-1003762262155`）

通知标题沿用线上规则：`【线上环境｜步骤 N 完成】`。

已通知步骤：

1. 恢复上下文并确认任务范围。
2. 权限代码修改完成（constants.py / permissions.py）。
3. 本地静态验证通过。
4. 运行机同步、备份、容器重建完成。
5. 容器内权限验证通过。

通知内容未包含密码、token、Secret Key、私钥正文、Session Cookie、完整 Signed URL、数据库连接串或 `.env` 原文。

## 变更内容

### 1. 前端用户组

文件：`devops/python/ben-bot/app/benbot/constants.py`

`FRONTEND_USERNAMES` 新增：

```text
kimtomf77
```

### 2. 前端角色按钮权限

文件：`devops/python/ben-bot/app/benbot/permissions.py`

`ROLE_ALLOWED_PATHS["frontend"]` 新增：

```text
线上前置-游点涩-h5-发版
线上前置-游点涩-pc-发版
```

`_build_role_capabilities()` 的前端能力文案同步新增：

```text
游点涩H5线上前置发版
游点涩PC线上前置发版
```

## 权限效果

前端角色（含 `@kimtomf77`）现在可以：

- 操作 `线上前置-游点涩-h5-发版`：发布到日本线上前置服务器 `138.252.248.139:38927`，页面入口 `https://h5.yiyi0620.com`，H5 分支 `main`，静态资源走 preprod H5 AWS S3 桶。
- 操作 `线上前置-游点涩-pc-发版`：发布到日本线上前置服务器 `138.252.248.139:38927`，页面入口 `https://pc.yiyi0620.com`，PC 分支 `dev`，静态资源走 preprod PC AWS S3 桶。
- 原有测试环境 H5/PC 发版权限不变。

前端角色仍然不可以：

- 操作 `线上环境-游点涩-h5-发版`（正式线上发版，仅运维可操作）。
- 使用 `/sh`、上传、下载等运维专属功能。

其他角色不受影响：

- 测试/后端/访客：不可访问两个线上前置按钮。
- 运维：仍为全部权限。

## 同步与备份

ben-bot 运行机：

- 机器：`ubuntu@52.79.252.255`
- 仓库路径：`/opt/telegram/18game_devops`
- bot 目录：`/opt/telegram/18game_devops/devops/python/ben-bot`

远程备份目录：

```text
/opt/telegram/18game_devops/.codex-backup/benbot-preprod-frontend-perm-20260807125526
```

已备份 `constants.py`、`permissions.py` 原文件，随后精确同步新文件，未覆盖现场无关修改。

ben-bot 容器已重建并启动：

```text
容器：ben-bot
镜像：ben-bot:latest
状态：Up
```

## 验证清单

| 项目 | 结果 |
| --- | --- |
| 本地 `py_compile` | 通过 |
| 本地两个线上前置 `.benbot.json` JSON 校验 | 通过 |
| 本地 `git diff --check` | 通过 |
| 本地权限断言（前端 5 人可访问两个前置按钮） | 通过 |
| 本地权限断言（测试/后端/访客不可访问前置按钮） | 通过 |
| 本地权限断言（运维仍为全部权限） | 通过 |
| 容器内 `py_compile` | 通过 |
| 容器内权限断言（前端 5 人 pre_h5/pre_pc=True，线上正式 H5=False） | 通过 |
| 容器内权限断言（后端无前置权限、运维全权限） | 通过 |
| 容器内前端能力文案包含“游点涩H5/PC线上前置发版” | 通过 |
| ben-bot 容器日志 | 启动正常，启动通知成功=9 失败=0 |

容器内断言结果：

```text
JoliChang: role=frontend pre_h5=True pre_pc=True prod_h5=False
lhong8: role=frontend pre_h5=True pre_pc=True prod_h5=False
gongz123321: role=frontend pre_h5=True pre_pc=True prod_h5=False
tudou0003: role=frontend pre_h5=True pre_pc=True prod_h5=False
kimtomf77: role=frontend pre_h5=True pre_pc=True prod_h5=False
CONTAINER_ASSERT_OK
```

## 结论

- 前端组已获得 `线上前置-游点涩-h5-发版`、`线上前置-游点涩-pc-发版` 两个发布按钮权限。
- `@kimtomf77` 已加入前端角色，可与其他前端成员一起使用两个线上前置发版按钮。
- 正式线上发版和运维专属能力仍只对运维角色开放。
- 汇总与文档已发送到 `18game运维` 与 `18GAME_ 上线群（正式環境）`。

## 后续注意

- 后续新增前端成员统一维护 `app/benbot/constants.py` 的 `FRONTEND_USERNAMES`。
- 后续新增按钮权限统一维护 `app/benbot/permissions.py` 的 `ROLE_ALLOWED_PATHS`。
- 权限修改后需要在容器内跑 `get_user_role()` 和 `can_access_script_path()` 断言，并确认容器重启日志的启动通知发送成功。
- 本轮目标群沿用历史 ben-bot 权限任务和线上前置任务的口径（`18game运维` + `18GAME_ 上线群（正式環境）`），如用户后续指定其他群，按 `workbench/NOTIFICATION_TARGETS.md` 调整。
