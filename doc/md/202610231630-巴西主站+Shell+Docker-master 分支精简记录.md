---
id: "doc-d18228ec440e"
title: "master 分支精简记录"
date: "2026-10-23T16:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "监控告警", "自动化", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-10-23-1630-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91master%E5%88%86%E6%94%AF%E7%B2%BE%E7%AE%80%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-10-23-1630-【运维】master分支精简记录.md"
sourceSha256: "81cb3142eb90df6a5e8ca0df7d19bc4de6580f9d1022d18ecc267205c5bd5e49"
sourceSystem: "project-doc"
---

# master 分支精简记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-10-23-1630-【运维】master分支精简记录.md`

> 整理日期：2026-10-23 16:30｜日期依据：文件名日期

时间：2026-10-23 16:30（北京）｜2026-10-23 05:30（巴西圣保罗）
原则：`master` 只保留运维发布链路；业务代码统一在 `ben` 分支。

## 一、清理前的备份

- 本地备份分支：`backup/master-business-20261023`
- 备份点：`cc3533e1`（清理前 master 的最后一个提交）
- `ben` 分支：**未做任何 checkout / pull / push 操作**

## 二、删除的业务内容

| 类型 | 内容 |
| --- | --- |
| 厂家源码 | `tada/`、`pp/`、`pg/`、`g759/`、`ppk/`、`panda/`、`playson/`、`platform-api/` |
| 业务构建产物 | `Dockerfile`、`.dockerignore`、`requirements.txt`、`share.so`、`sitecustomize.py`、`server_configs`、`version.json`、`xxxxxx.mmdb` |
| 结果快照 | `collected/`（15 个 results.json） |
| 非发布工具 | `docker/browser-test/` |
| 系统垃圾 | 根目录与 `docker/` 下的 `.DS_Store` |

共删除 36,000+ 个业务文件。

## 三、保留的运维内容

根目录：

- `README.md`：运维帮助文档（已加分支说明）
- `运维发布页.html`：交互式发布操作台
- `deploy-自动化部署最新版本.py`、`update_pgserver.sh`：兼容老命令的发布入口
- `scripts/`：两个兼容包装脚本
- `.gitignore`

`docker/`：

- `deploy/`：总控发布、单服务发布、服务器内更新脚本
- `services/`：各厂家 `service.env` 与发布配置（deploy 脚本实际读取）
- `scripts/`：监控、日志、CDN、GCS、结果集同步等运维脚本
- `doc/`：全部运维历史文档
- `线上服务器信息/`：服务器、网络、端口、备份信息
- `ben-bot/`：通知机器人源码
- `resource-sync/`：GCS 静态资源同步
- `workbench/`：当前状态与运行链路文档
- `ci/`、`Dockerfile`：发布脚本实际使用的构建/自检文件

## 四、清理结果

| 指标 | 清理前 | 清理后 |
| --- | --- | --- |
| 跟踪文件数 | 36,000+ | **924** |
| 工作区体积（不含 .git） | 约 1.5GB | **约 5.7MB** |
| 业务源码目录 | 8 个 | 0 |

`.git` 历史仍有约 801MB（旧提交保留，未重写历史）。如需彻底缩小仓库，可另建 orphan 分支或重新初始化，这属于独立决策，本次未做。

## 五、验证

- `git status` 干净（`.DS_Store` 不再跟踪）
- `git ls-files` 只剩运维内容
- `docker/deploy/deploy_all_servers.py`、`docker/deploy/update_pgserver.py`、`docker/services/pg/service.env`、`docker/scripts/container_health_monitor.py` 均存在
- `运维发布页.html` 存在
- 备份分支 `backup/master-business-20261023` 指向清理前提交

## 六、提交

本地提交：`592b9c5f chore(master): 清理业务代码，仅保留运维发布链路`
未 push 远端；远端 master 仍保持原状，等确认后再决定是否推送。
