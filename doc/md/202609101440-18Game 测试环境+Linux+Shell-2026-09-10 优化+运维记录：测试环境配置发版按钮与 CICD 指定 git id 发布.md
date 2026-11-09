---
id: "doc-5d3ecbce238a"
title: "2026-09-10 优化+运维记录：测试环境配置发版按钮与 CICD 指定 git id 发布"
date: "2026-09-10T14:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-10_1440-%E3%80%90%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE%E5%8F%91%E7%89%88%E6%8C%89%E9%92%AE%E4%B8%8ECICD%E6%8C%87%E5%AE%9Agitid%E5%8F%91%E5%B8%83.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-10_1440-【优化+运维记录】测试环境配置发版按钮与CICD指定gitid发布.md"
sourceSha256: "65ebe8f41a45ca6305155e2c269bdddfa8be43d49dbc9bccfe66543f5eac663f"
sourceSystem: "project-doc"
---

# 2026-09-10 优化+运维记录：测试环境配置发版按钮与 CICD 指定 git id 发布

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609101440-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-2026-09-10%20%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%EF%BC%9A%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE%E5%8F%91%E7%89%88%E6%8C%89%E9%92%AE%E4%B8%8E%20CICD%20%E6%8C%87%E5%AE%9A%20git%20id%20%E5%8F%91%E5%B8%83.md)

> 整理日期：2026-09-10 14:40｜日期依据：文件名日期

环境标签：测试环境 / ben-bot / CICD / 配置仓库 / 优化

时间：2026-09-10 14:40（北京时间）

## 1. 目标

- 新增机器人按钮「⚙️🧪⚙️ 测试环境-游点涩-配置-发版」；
- 列出独立配置仓库最近提交，选择配置 git id 后发布到测试环境；
- 配置内容不在群/文档展开；通知 `18game运维` 与 `18GAME_ 上线群（正式環境）`。

## 2. 配置仓库与 CICD

- 配置仓库：`root/docker-youdianse-php-config-dev`（main 单分支）。
- CICD 原有能力：自动跟随 main 同步 env/.env.dev 与 app-local-files/alb_white*.txt。
- 本次新增：按指定 ref（git id）发布。

代码改动（docker-youdianse-php dev=`4664fca`，文档 `f981d16`）：

```text
cicd-web/config_repo.py
  sync_config_repo(logger, force, ref=None)
  ref 非空：fetch 后 checkout --force <ref>；失败则 fetch origin <ref> 后 checkout FETCH_HEAD
  写入 runtime/config-repo.last_commit 与 runtime/config-repo.last_ref
  ref 发布为一次性，不写入分支缓存，后续自动更新仍回 main
cicd-web/core.py
  sync_runtime_config_no_build(..., config_ref=None)
cicd-web/cli.py
  sync-config-repo --ref <git id>
  sync-config --force --ref <git id>（指定 ref 自动 force）
```

## 3. 机器人按钮

新增目录：`data/scripts/测试环境-游点涩-配置-发版/`

- `.benbot.json`：label「⚙️🧪⚙️ 测试环境-游点涩-配置-发版」，运维可见。
- `youdianse_test_config_release.py`
  - `list_json`：读取 live 配置仓库 origin/main 最近 30 个提交；
  - `run <git id> [operator]`：SSH 到 15.152.247.196 执行
    `sync-config-repo --ref` + `sync-config --force --ref`，然后校验
    last_commit/last_ref、env/白名单权限、web/nginx/cron 状态、admin/cicd 入口；
  - 成功/失败发送 Telegram 到 `18GAME_ 上线群（正式環境）` + `18game运维`，不展开配置值。
- `benbot_plugin.py`：复用前端发布提交列表 UI（列出/分页/选择 git id）。

## 4. 验证

| 项目 | 结果 |
| --- | --- |
| 本地脚本 py_compile | 通过 |
| 配置提交列表 | 正常输出（main 最近提交） |
| CICD `sync-config-repo --ref` | live 检出成功，last_ref 写入 |
| CICD `sync-config --force --ref` | web/nginx/cron no-build 重建成功，复查配置一致 |
| 权限 | env=644，alb_white*.txt=600 |
| 入口 | admin 登录页 200，h5 version.json 200，cicd 200 |
| 按钮注册 | 容器内 load_registry 可见新按钮，plugin handle_open/handle_callback 存在 |
| 权限控制 | ops=True；frontend/guest=False |
| 容器内实跑 | 配置发布成功，脚本双群通知成功 |

## 5. 使用方式

群里点「⚙️🧪⚙️ 测试环境-游点涩-配置-发版」→ 选择配置 git id → 自动同步并 no-build 重建测试环境 web/nginx/cron。

等效 CLI（live）：

```bash
cd /opt/docker-youdianse-php
python3 cicd-web.py sync-config-repo --ref <git id>
python3 cicd-web.py sync-config --force --ref <git id>
```

## 6. 安全边界

- 配置仓库 private；配置值不写入群通知、工作台或本文档。
- 密码、token、私钥、连接串均未输出或入库。
