---
id: "doc-f4dc50318270"
title: "2026-09-10 优化+运维记录：线上环境配置发版按钮与生产 CICD 指定 git id 发布"
date: "2026-09-10T15:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-10_1520-%E3%80%90%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE%E5%8F%91%E7%89%88%E6%8C%89%E9%92%AE%E4%B8%8E%E7%94%9F%E4%BA%A7CICD%E6%8C%87%E5%AE%9Agitid%E5%8F%91%E5%B8%83.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-10_1520-【优化+运维记录】线上环境配置发版按钮与生产CICD指定gitid发布.md"
sourceSha256: "61423c5cd7a2e2682a53f9e26b9d07fb2f0d3ec68b4251cfcc361c470b2fdf7b"
sourceSystem: "project-doc"
---

# 2026-09-10 优化+运维记录：线上环境配置发版按钮与生产 CICD 指定 git id 发布

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-10_1520-【优化+运维记录】线上环境配置发版按钮与生产CICD指定gitid发布.md`

> 整理日期：2026-09-10 15:20｜日期依据：文件名日期

环境标签：线上环境 / ben-bot / CICD / 配置仓库 / 优化

时间：2026-09-10 15:20（北京时间）

## 1. 目标

- 新增机器人按钮「⚙️🚀⚙️ 线上环境-游点涩-配置-发版」；
- 配置仓库：`root/docker-youdianse-php-config-main`（main 单分支）；
- 选择生产配置 git id 后发布到线上环境；
- 生产禁止自动发布，只能由机器人/运维显式触发；
- 通知 `18GAME_ 上线群（正式環境）` + `18game运维`；配置内容不在群/文档展开。

## 2. 生产 CICD 现状

- 生产 CICD 已完成配置仓库抽离：`docker-youdianse-php` main=01d2a3d 起支持 `config_repo` 同步与 `--ref`。
- live：16.209.16.108 /opt/docker-youdianse-php，`cicd-web.service` active，18090 监听。
- 配置仓库初始提交与当前 last_commit/last_ref：`2ae10c14a405`。
- 生产无自动 sync-config 路径，配置仓库提交后不会自动发布。

## 3. 机器人按钮

新增目录：`data/scripts/线上环境-游点涩-配置-发版/`

- `.benbot.json`：label「⚙️🚀⚙️ 线上环境-游点涩-配置-发版」，仅运维可见。
- `youdianse_prod_config_release.py`
  - `list_json`：读取 live 生产配置仓库 origin/main 最近 30 个提交；
  - `run <git id> [operator]`：SSH 到 16.209.16.108，
    加载 `cicd-web/runtime/secrets.env` 后执行
    `sync-config-repo --ref <id>` + `sync-config --force --ref <id>`；
  - 校验 last_commit/last_ref、文件权限、宿主机/web/cron env sha256 一致、
    web/nginx/cron 容器状态、admin/cicd 入口 200；
  - 成功/失败通知 `18GAME_ 上线群（正式環境）` + `18game运维`。
- `benbot_plugin.py`：复用前端发布提交列表 UI（列出/分页/选择 git id）。

## 4. 验证

| 项目 | 结果 |
| --- | --- |
| 本地 py_compile | 通过 |
| 配置提交列表 | 正常输出（生产配置仓库 main，当前 1 条初始提交） |
| 生产 ref 同步（只写 /opt，不重建） | 检出 2ae10c14a405；last_ref 写入 |
| 内容一致性 | env sha256 前后一致（14e0fa6f…），alb_white* 前后一致 |
| 文件权限 | env/.env.prod=644，alb_white*.txt=600 |
| 容器 | web/nginx/cron 未重启（Up） |
| 按钮注册 | 容器内 load_registry 可见，plugin handle_open/handle_callback 存在 |
| 权限控制 | ops=True；frontend/guest=False |

完整生产发布（no-build 重建 web/nginx/cron + 白名单 docker cp）只在按钮点击时执行；
本次验证未触发生产容器重建。

## 5. 使用方式

群里点「⚙️🚀⚙️ 线上环境-游点涩-配置-发版」→ 选择生产配置 git id → 显式触发
`sync-config-repo --ref` + `sync-config --force --ref`。

等效 CLI（生产 16.209.16.108）：

```bash
cd /opt/docker-youdianse-php
sudo bash -c 'set -a; . cicd-web/runtime/secrets.env; set +a; \
  cicd-web/runtime/venv/bin/python cicd-web.py sync-config --force --ref <配置 git id>'
```

回滚：选择历史配置 git id 再次发布即可；
如需业务镜像回退走正常生产发布流程指定业务 git id。

## 6. 安全边界

- 生产配置仓库 private；配置值不写入群通知、工作台或本文档；
- 密码、token、私钥、连接串均未输出或入库；
- chat_id 只存服务器 runtime/secrets.env（0600）。
